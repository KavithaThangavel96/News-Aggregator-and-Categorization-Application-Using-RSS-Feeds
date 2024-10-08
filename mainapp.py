import pandas as pd
import feedparser
import mysql.connector
from datetime import datetime
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from celery import Celery
import logging

# Initialize Celery
app = Celery('mainapp', broker='redis://localhost:6379/0')  # Use Redis as the message broker

# Set up logging
logging.basicConfig(level=logging.INFO)

@app.task(bind=True)
def process_rss_feed(self, rss_url):
    conn = None  # Initialize conn to None to avoid UnboundLocalError
    try:
        logging.info(f"Processing RSS feed from URL: {rss_url}")
        feed = feedparser.parse(rss_url)
        entries = []

        # Check if feed has entries
        if not feed.entries:
            logging.warning("No entries found in the RSS feed.")
            self.update_state(state='FAILURE', meta={'error': 'No entries found in the feed'})
            return

        for entry in feed.entries:
            content = entry.get('summary') or entry.get('description') or 'No content available'
            published = entry.get('published') or entry.get('updated') or 'Unknown'
            
            # Convert the published date to a standard format if possible
            try:
                published_date = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %z')
            except (ValueError, TypeError):
                published_date = None  # Set to None if the date is not in a recognized format

            entries.append({
                'title': entry.title,
                'content': content,
                'published': published_date,
                'link': entry.link,
                'source': entry.get('source', 'Unknown')
            })
        
        df = pd.DataFrame(entries)

        # SQL connection
        conn = mysql.connector.connect(host="localhost", user="", password="", database="NEWS_RSS")
        cursor = conn.cursor()

        # Create table if it does not exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS news_articles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            content TEXT,
            published DATETIME,
            link VARCHAR(255),
            source VARCHAR(255),
            target VARCHAR(255)
        )''')

        # Insert data
        for _, row in df.iterrows():
            cursor.execute('''INSERT INTO news_articles (title, content, published, link, source)
                              VALUES (%s, %s, %s, %s, %s)''',
                           (row['title'], row['content'], row['published'], row['link'], row['source']))

        conn.commit()
        logging.info(f"Inserted {len(df)} articles into the database.")

        # Download the VADER lexicon
        nltk.download('vader_lexicon', quiet=True)

        # Initialize the SentimentIntensityAnalyzer
        sia = SentimentIntensityAnalyzer()

        # Function to classify sentiment
        def classify_sentiment(text):
            scores = sia.polarity_scores(text)
            if scores['compound'] >= 0.05:
                return 'positive'
            elif scores['compound'] <= -0.05:
                return 'negative'
            else:
                return 'neutral'

        # Apply the function to create a new column for sentiment classification
        df['target'] = df['title'].apply(classify_sentiment)

        # Update the target column in the database
        update_query = '''UPDATE news_articles SET target = %s WHERE id = %s;'''

        for index, row in df.iterrows():
            target = row['target']
            record_id = index + 1  # Adjust for 1-based ID
            cursor.execute(update_query, (target, record_id))

        conn.commit()
        logging.info("Updated target sentiments in the database.")

    except mysql.connector.Error as err:
        logging.error(f"Database error: {err}")
        self.update_state(state='FAILURE', meta={'error': str(err)})
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        self.update_state(state='FAILURE', meta={'error': str(e)})
    finally:
        if conn:  # Check if conn was successfully created
            conn.close()
        logging.info("Database connection closed.")
