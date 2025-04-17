    #!/usr/bin/env python
# coding: utf-8

import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import lit, udf, col
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pyspark.sql.types import StringType, FloatType, StructType, StructField
import argparse



def init():
    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("Crypto Data Transformation") \
        .getOrCreate()

    # Set temporary GCS bucket for BigQuery export
    bucket = "zoomcamp_project_v1"
    spark.conf.set('temporaryGcsBucket', bucket)

    return spark


def read_parquet_files(spark, path):
    # Read parquet files from the specified path
    df = spark.read.parquet(path)
    return df


def parse_arguments():
    parser = argparse.ArgumentParser(description="Crypto Data Transformation Script")
    parser.add_argument('--crypto_prices_path', type=str, required=True, help="Path to the crypto prices parquet files")
    parser.add_argument('--reddit_sentiments_path', type=str, required=True, help="Path to the Reddit sentiments parquet files")
    parser.add_argument('--cryptopanic_sentiments_path', type=str, required=True, help="Path to the Cryptopanic sentiments parquet files")
    parser.add_argument('--bigquery_dataset_output', type=str, required=True, help="Bigquery dataset output name")
    return parser.parse_args()


def read_and_transform_sentiments(spark, sentiments_path, social_media):
    # Define a set of columns to select
    columns_selected = ["post_id", "post_title", "post_timestamp", "comment_id", "comment_text", "comment_date", "social_media"]

    # Read data from GCS path and perform relevant transformations.
    df = spark.read.parquet(f"{sentiments_path}/")\
                      .withColumn('social_media', lit(f'{social_media}')) \
                      .dropDuplicates(['post_timestamp', 'post_title', 'comment_text', 'comment_date']) \
                      .filter("comment_text != '' ").filter("post_title != '' ")\
                      .select(columns_selected)
    return df


# Define a UDF to apply VADER sentiment analysis
def get_sentiment(text):
    # Initialize VADER Sentiment Analyzer
    analyzer = SentimentIntensityAnalyzer()

    if not text or len(text.strip()) == 0:
        return ("NEUTRAL", 0.0)
    score = analyzer.polarity_scores(text)['compound']
    if score > 0.05:
        return ("POSITIVE", score)
    elif score < -0.05:
        return ("NEGATIVE", score)
    else:
        return ("NEUTRAL", score)



def perform_sentiment_analysis(cryptosentiments_df, spark):
    # Initialize VADER Sentiment Analyzer
    analyzer = SentimentIntensityAnalyzer()

    # Register UDF
    sentiment_udf = udf(get_sentiment, StructType([StructField("label", StringType(), True), StructField("score", FloatType(), True)]))


    # Apply UDF to get sentiment
    df_with_sentiment = cryptosentiments_df.withColumn("post_sentiment", sentiment_udf(cryptosentiments_df["post_title"])) \
                                        .withColumn("comment_sentiment", sentiment_udf(cryptosentiments_df["comment_text"]))

    # Extract sentiment labels and scores
    cols = ['post_id','post_title','post_timestamp','comment_id','comment_text','comment_date',
            'social_media','post_label','post_score','comment_label','comment_score']

    df_sentiments = df_with_sentiment.withColumn("post_label", col("post_sentiment.label"))\
                                    .withColumn("post_score", col("post_sentiment.score"))\
                                    .withColumn("comment_label", col("comment_sentiment.label"))\
                                    .withColumn("comment_score", col("comment_sentiment.score"))\
                                    .select(cols)
    
    # Register as a temp table
    df_sentiments.registerTempTable('sentiments')
    
    # Perform further enhancements to get add weighted metrics to post and comment sentiments
    # and calculate the hourly velocity of comments per post
    df_sentiments_processed = spark.sql("""
                                        
        SELECT
            hour_timestamp,
            post_title,
            post_timestamp,
            comment_text,
            comment_date As comment_timestamp,
            weighted_post_sentiment,
            weighted_comment_sentiment,
            COUNT(comment_text) OVER (PARTITION BY post_title, post_timestamp, hour_timestamp) AS velocity
        FROM
            (
                SELECT
                    *,
                    post_score*(1-((post_score-comment_score)/(1 + (post_score-comment_score)))) AS weighted_post_sentiment,
                    comment_score*((post_score-comment_score)/(1 + (post_score-comment_score))) AS weighted_comment_sentiment,
                    date_trunc("Hour",post_timestamp) AS hour_timestamp
                FROM sentiments
            )

        """)

    return df_sentiments_processed


def read_and_transform_prices(spark, prices_path):
    # Read crypto prices data
    crypto_prices = read_parquet_files(spark, f"{prices_path}/*")

    #register as temp table
    crypto_prices.registerTempTable('crypto_prices')

    #extract the result
    crypto_prices_df = spark.sql("""
    WITH data AS 
    (
        SELECT
            *,
            row_number() over(partition by timestamp order by ingested_at desc) AS row_num
        FROM
            crypto_prices
    )
    SELECT * FROM data WHERE row_num=1;
    """)

    # Write the cleaned crypto prices data to GCS
    crypto_prices_df.write.parquet('gs://zoomcamp_project_v1/crypto_data/crypto_prices_merged', mode='overwrite')

    # Register as a temp table
    crypto_prices_df.registerTempTable('prices')

    # Calculate daily volatility of crypto prices
    crypto_prices_df = spark.sql("""
    SELECT 
        hour_timestamp,
        measured_timestamp,
        price,
        market_cap,
        volume,
        stddev(price) OVER (PARTITION BY daily_timestamp) AS daily_volatility
    FROM
    (
        SELECT 
            date_trunc("Hour",timestamp) AS hour_timestamp,
            date_trunc("Day",timestamp) AS daily_timestamp,
            timestamp as measured_timestamp,
            price,
            market_cap,
            volume
        FROM prices
    );
    """)
    return crypto_prices_df


def perform_aggregation(crypto_prices_df, sentiments_df, spark):

    #Register the DataFrames as temporary tables
    sentiments_df.registerTempTable('sentiments_processed')
    crypto_prices_df.registerTempTable('prices_processed')

    combined_results = spark.sql("""

    WITH aggregated_sentiments AS
    (
        SELECT 
            hour_timestamp,
            AVG(weighted_post_sentiment) AS avg_weighted_post_sentiment,
            AVG(weighted_comment_sentiment) AS avg_weighted_comment_sentiment,
            AVG(velocity) AS avg_comment_velocity
        FROM sentiments_processed
        GROUP BY hour_timestamp
    ),
    aggregated_prices AS
    (
        SELECT 
            hour_timestamp,
            AVG(price) as avg_price,
            AVG(market_cap) AS avg_market_cap,
            AVG(volume) AS avg_volume,
            AVG(daily_volatility) AS daily_volatility
        FROM prices_processed
        GROUP BY hour_timestamp
    )
    SELECT
        A.hour_timestamp AS hour_timestamp,
        A.avg_price AS avg_price,
        A.avg_market_cap AS avg_market_cap,
        A.avg_volume AS avg_volume,   
        A.daily_volatility AS daily_volatility,
        B.avg_weighted_post_sentiment AS avg_weighted_post_sentiment,
        B.avg_weighted_comment_sentiment AS avg_weighted_comment_sentiment,
        B.avg_comment_velocity AS avg_comment_velocity
    FROM
        aggregated_prices A
        JOIN aggregated_sentiments B
        ON A.hour_timestamp=B.hour_timestamp
    ORDER BY A.hour_timestamp

    """)
    return combined_results

def write_to_bigquery(df, table_name, bigquery_dataset_output):
    # Save the DataFrame to BigQuery
    df.write.format('bigquery').mode('overwrite') \
        .option('table', f'{bigquery_dataset_output}.{table_name}') \
        .save()

    print(f"Data written to BigQuery table: {bigquery_dataset_output}.{table_name}")


def main(params):

    # Unpack the params
    crypto_prices_path = params.crypto_prices_path
    reddit_sentiments_path = params.reddit_sentiments_path
    cryptopanic_sentiments_path = params.cryptopanic_sentiments_path
    bigquery_dataset_output = params.bigquery_dataset_output

    # Initialize Spark session
    spark = init()

    # Read and transform crypto prices data
    crypto_prices_df = read_and_transform_prices(spark, crypto_prices_path)
    
    # Read and transform Reddit sentiments data
    reddit_df = read_and_transform_sentiments(spark, reddit_sentiments_path, social_media='reddit')

    # Read and transform Cryptopanic sentiments data
    cryptopanic_df = read_and_transform_sentiments(spark, cryptopanic_sentiments_path, social_media='cryptopanic')

    # Merge the two DataFrames
    sentiments_df = reddit_df.unionAll(cryptopanic_df)
    
    # Write the combined sentiments data to GCS
    sentiments_df.write.parquet('gs://zoomcamp_project_v1/crypto_sentiments/crypto_sentiments_merged', mode='overwrite')
                      
    # Perform sentiment analysis
    sentiments_df = perform_sentiment_analysis(sentiments_df, spark)

    # Perform aggregation
    combined_results = perform_aggregation(crypto_prices_df, sentiments_df, spark)

    # Use the Cloud Storage bucket for temporary BigQuery export data used
    # by the connector.
    bucket = "zoomcamp_project_v1"
    spark.conf.set('temporaryGcsBucket', bucket)

    #Write the aggregated data to bigquery
    write_to_bigquery(combined_results, 'hourly_aggregated_data', bigquery_dataset_output)
    # Write the processed sentiments data to BigQuery       
    write_to_bigquery(sentiments_df, 'sentiments', bigquery_dataset_output)
    # Write the processed prices data to BigQuery
    write_to_bigquery(crypto_prices_df, 'prices', bigquery_dataset_output)


    
if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    #run the main function
    main(args)

    
    











