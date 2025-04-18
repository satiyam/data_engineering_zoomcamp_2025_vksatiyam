## Course Project

CryptoPulse: Sentiment-Driven Market Insights


### Background & Overview:
CryptoPulse is a data engineering project focused on understanding the impact of social media sentiment on cryptocurrency market trends. The project integrates Reddit posts/comments, news aggregator content (like CryptoPanic), and market data (prices, volume, market cap) to uncover patterns in how online sentiment influences crypto asset behavior.

![image](https://github.com/user-attachments/assets/910c801e-8a1f-49b8-a29e-debd91477804)

As can be seen above, the key components include:

Data Ingestion: Using Python-based web scrapers and the DLT library to collect Reddit and CryptoPanic sentiments data on Bitcoin as well as pricing data on Bitcoin from CoinGecko API.

Processing: Data is cleaned and enriched with sentiment scores using NLP models like VADER on dataprocs cluster for sentiment analysis. 

Transformation: With PySpark on the DataProc cluster, data is processed into hourly aggregates and polarity-weighted average to account for post - to - comment sentiment influences.

Storage: Data is stored in Google Cloud Storage and loaded into BigQuery for analysis.

Modeling: Using PySpark again, sentiment and market data are joined to create meaningful analytical tables (e.g., hourly_aggregated_data).

Visualization: Final dashboards are built in Power BI, showing:

- Sentiment polarity over time

- Market trends aligned with social buzz

- Category breakdowns of sentiment (Very Positive to Very Negative)

This pipeline is fully orchestrated with Kestra, automating the entire workflow from ingestion to dashboard update.

![image](https://github.com/user-attachments/assets/b024e95a-03d0-47fb-9a16-0502c045cb2d)



