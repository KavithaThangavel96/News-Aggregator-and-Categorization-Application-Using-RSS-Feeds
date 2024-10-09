# News-Aggregator-and-Categorization-Application-Using-RSS-Feeds
## Objective: 
Develop a robust application that systematically collects news articles from various RSS feeds, stores the articles in a structured database, and categorizes each 
article into predefined categories based on its content. The application will leverage Feedparser for fetching articles, Mysql connector for database interaction with MySQL, 
Celery for managing the task queue, and Natural Language Processing (using NLTK) for text classification, enabling users to easily access and navigate news content tailored to their interests.

## Feed Parser and Data Extraction:
* Create a script that reads the provided list of RSS feeds.
* Parse each feed and extract relevant information from each news article,
including title, content, publication date, and source URL.
* Ensure handling of duplicate articles from the same feed.
## Database Storage:
* Design a database schema to store the extracted news article data.
* Implement logic to store new articles in the database without duplicates.
## Task Queue and News Processing:
* Set up a Celery queue to manage asynchronous processing of new articles.
* Configure the parser script to send extracted articles to the queue upon arrival.
* Create a Celery worker that consumes articles from the queue and performs
## further processing:
* Category classification:
  Utilize NLTK to classify each article into the provided categories.
* Update the database with the assigned category for each article.
## Streamlit Application
* Develop a user-friendly Streamlit application to migrate the categorized news articles to sql database.
## Logging and Error Handling:
* Implement proper logging throughout the application to track events and potential
errors.
* Handle parsing errors and network connectivity issues gracefully
