#!/usr/bin/env python
# coding: utf-8

# # Import Libraries

# In[2]:


import dlt, json, os, time, requests, tempfile

import pandas as pd
import undetected_chromedriver as uc

from datetime import datetime, timedelta, timezone
from dlt.common import pendulum
from dlt.destinations import filesystem
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.auth import BearerTokenAuth
from dlt.sources.helpers.rest_client.paginators import JSONLinkPaginator
from pytz import utc
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager

# local imports
from scrappers import reddit_scrapper, cryptopanic_api_scrapper



# Define your resource
@dlt.resource(name="crypto_prices", write_disposition="merge", primary_key="timestamp")
def fetch_prices():
    #define the restful client
    client = RESTClient(
        base_url="https://api.coingecko.com/api/v3",
        auth=BearerTokenAuth(token=dlt.secrets['crypto_api_key']['coingecko_token'])
    )

    #define some endpoint params
    crypto_headers = dlt.config['cryptoheaders']

    #check if incremental or initial load
    initial_load = crypto_headers['initial_load']
    if(initial_load is True):
        loading_days = 89
    else:
        loading_days = int(crypto_headers['days'])

    #define the coin id for endpoint parsing
    coin_id = crypto_headers['coin_id']

    #parse the params
    params = {
        "vs_currency": crypto_headers['vs_currency'],
        "days": loading_days
    }
    
    #make request to the endpoint
    response = client.get(f'/coins/{coin_id}/market_chart', params=params)
    print(response)

    #if successful
    if response.status_code==200:
        #print logs
        print(f"Fetching last {params['days']} days of prices for {coin_id} is successful!")
        #parse data
        data = json.loads(str(response.content, 'utf-8'))
        #yield data
        for i in range(len(data["prices"])):
            yield {
                "timestamp": datetime.utcfromtimestamp(data["prices"][i][0] / 1000).replace(tzinfo=utc),
                "price": data["prices"][i][1],
                "market_cap": data["market_caps"][i][1],
                "volume": data["total_volumes"][i][1],
                "asset": coin_id.upper(),
                "ingested_at": datetime.utcnow().replace(tzinfo=utc)
            }
    else:
        print(f"Fetching last {params['days']} days of prices for {coin_id} is not successful due to error {response.status_code}!")


# DLT resource for reddit scrapper
@dlt.resource(write_disposition="append", primary_key="comment_id", name="crypto_sentiments")
def extract_reddit_comments():
    yield from reddit_scrapper_instance.get_comments()


# DLT resource for cryptopanic API scrapper
@dlt.resource(write_disposition="append", primary_key="comment_id", name="cryptopanic_sentiments")
def extract_cryptopanic_comments():
    yield from cryptopanic_api_scrapper_instance.yield_comments()



if __name__ == "__main__":

    # # Step 1: Define the DLT pipeline for extraction of crypto prices.
    pipeline = dlt.pipeline(
        pipeline_name="crypto_sentiment_pipeline",
        destination='filesystem',
        dataset_name="crypto_data"
    )

    # # Step 2: Run the pipeline with the resource function
    load_info = pipeline.run(fetch_prices(), loader_file_format="parquet")

    # # Step 3: Define the days to extract
    days_extracted = int(dlt.config['cryptoheaders']['days'])


    # Step 4: Instantiate the Reddit scraper
    reddit_scrapper_instance = reddit_scrapper(headless=False, days_extracted=days_extracted)
    
    # Step 5: Extract posts
    reddit_scrapper_instance.get_posts()

    # Step 6: Wait for 5 seconds
    time.sleep(5)

    # Step 7: Create the DLT pipeline for extraction of reddit comments.
    pipeline = dlt.pipeline(
        pipeline_name="crypto_sentiment_pipeline",
        destination="filesystem",
        dataset_name="crypto_sentiments"
    )

    # Step 8: Run pipeline for extracting the reddit comments
    load_info = pipeline.run(extract_reddit_comments, loader_file_format="parquet")
    
    # Step 9: Close the browser after scraping
    reddit_scrapper_instance.close()

    # Step 10: Instantiate the Cryptopanic API scraper
    cryptopanic_api_scrapper_instance = cryptopanic_api_scrapper(headless=False, days_extracted=days_extracted)

    # Step 11: Extract the crypto posts
    cryptopanic_api_scrapper_instance.fetch_cryptopanic_feed()

    # Step 12: Extract the crypto comments
    cryptopanic_api_scrapper_instance.get_comments()

    # Step 12: Create the DLT pipeline for extraction of cryptopanic comments.
    pipeline = dlt.pipeline(
        pipeline_name="crypto_sentiment_pipeline",
        destination="filesystem",
        dataset_name="crypto_sentiments"
    )

    # Step 13: Run pipeline for extracting the cryptopanic API comments
    load_info = pipeline.run(extract_cryptopanic_comments, loader_file_format="parquet")
    print(load_info)

