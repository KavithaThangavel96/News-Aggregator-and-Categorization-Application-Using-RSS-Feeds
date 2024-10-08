# app.py
import streamlit as slt
from mainapp import process_rss_feed

# Streamlit UI
feed_url = slt.text_input('Enter feed URL:')
if slt.button('Process Feed'):
    # Call the Celery task asynchronously
    task = process_rss_feed.delay(feed_url)
    slt.success("successfull migrated to database!")
    