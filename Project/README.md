## Course Project

CryptoPulse: Sentiment-Driven Market Insights


### Problem Statement
Cryptocurrency markets are volatile, and sentiment on platforms like Reddit and Twitter significantly influences price trends. Current methods lack real-time sentiment integration for fraud detection and market forecasting. This project addresses that gap by combining social media sentiment analysis with market data to predict fluctuations and detect fraudulent behavior in crypto transactions.



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


## Folder Structure

```bash
.
├── PBI_cryptodashboard.pbix
├── architecture_flow.pptx
├── dataprocs
│   ├── Crypto_Data_Transformation.ipynb
│   ├── Crypto_Data_Transformation.py
│   ├── vaderSentiment-3.3.2-py2.py3-none-any.whl
│   └── vader_sentiment_lib
│       ├── vaderSentiment
│       │   ├── __init__.py
│       │   ├── emoji_utf8_lexicon.txt
│       │   ├── vaderSentiment.py
│       │   └── vader_lexicon.txt
│       └── vaderSentiment-3.3.2.dist-info
│           ├── LICENSE.txt
│           ├── METADATA
│           ├── RECORD
│           ├── WHEEL
│           └── top_level.txt
├── docker-compose.yaml
├── kestra-data
│   └── kestra_docker_files
│       ├── Dockerfile.kestra
│       ├── docker-compose.yml
│       └── service-account
│           └── terraform-demo-435315-7b3f0c915958.json
├── monitor_docker.bat
└── scraper
    ├── Data_Ingestion.ipynb
    ├── Data_Ingestion.py
    ├── Dockerfile
    ├── Dockerfile_bkup.txt
    ├── __pycache__
    │   └── scrappers.cpython-312.pyc
    ├── requirements.txt
    └── scrappers.py
```


There are 3 main folders:
- scraper folder:Contains the docker files required for running selenium based webscraper on the localhost (PC environment of users)
- kestra-data: Contains the docker files for creating a kestra docker container on the GCP VM to orchestrate the process end to end.
- dataprocs: Contains the source code and files for running PySpark on a dataprocs cluster.


### Quickstart guide


#### Spin up a GCP VM cluster

Region: asia-southeast1.
Machine-type: e2-standard-4 (4 vCPUs, 16 GB memory)

Assign a static IP address to the machine on GCP VM. You can follow the screenshot below on where to reserve the static IP address:

![image](https://github.com/user-attachments/assets/2424f2e6-a9d6-450f-885a-2a51835ba050)


#### Creating a new GCS bucket 

1. Go to GCP and setup the following GCS buckets for the project:

![image](https://github.com/user-attachments/assets/de2dc4b9-9104-45ac-8800-288e4c0ee26f)



#### Creating a new principal service account

1. Go to "IAM and Admin" to setup a new principal service account e.g. "project-zoomcamp-api@terraform-demo-435315.iam.gserviceaccount.com"

2. Assign the following roles:
    - BigQuery Admin
    - Compute Admin
    - Dataproc Administrator
    - Storage Admin
  
3. Create key credentials to access the principal service account and store the '.json' file to your local environment
   __Warning: DO NOT SHARE THE CREDENTIALS OR HOST IN PUBLIC WEBSITES__



#### Establish connection between GCP VM and Oracle Virtual Machine (Oracle VM)
1. To establish connection between GCP VM and Oracle VM, we need to create a SSH key on our Oracle VM. Use the following command below in Oracle VM:

```bash
ssh-keygen -t ed25519 -C <username_of_your_pc>
cd ~/.ssh
cat id_ed25519.pub
```

2. Copy the outputs of the public key from Step 1 in Oracle VM and paste to GCP VM under "SSH Keys" of the GCP VM.
   
4. Stop and restart the instance.
  
5. Try to SSH into the GCP VM using the command below, where username refers to the <username_of_your_Oracle VM> in Step 1 and "external-ip" would be the static IP address assigned to the GCP VM:

```bash
ssh -i ~/.ssh/id_ed25519 <username_of_your_Oracle VM>@<external-ip>
```
e.g. ssh -i ~/.ssh/id_ed25519 satiy@34.2.16.41

6. In the Oracle VM, create a config file and store the credentials as follows in the file 'config'

```bash
PS C:\Users\satiy\.ssh> cat config
Host project-ssh
    HostName <external-ip>
    User <username_of_your_Oracle VM>
    IdentityFile ~/.ssh/id_ed25519
```

7. In the Oracle VM, set the appropriate permissions for the config file created.
   
```bash
chmod 600 ~/.ssh/config
```

#### Establish Reverse Tunneling

1. To establish the reverse tunneling, you have to perform the following command below on 

```bash
ssh -v -N -R 9000:localhost:22 <username_of_your_Oracle VM>@<external-ip>
```

2. In a seperate bash terminal, ssh into the VM and see if you can access the IP address of the Oracle VM.

```bash
ssh -p 9000 <username_of_your_Oracle VM>@localhost
```

3. Authentication should be successful.


#### Spinning up docker container on Oracle VMBox

Pre-requisites: Have docker and docker-compose setup beforehand.

1. To spin up the docker container on Oracle Virtual Machine, first copy the 'scraper' folder to the 'Documents' folder of the Oracle Virtual Machine.
   
2. To spin up the docker container, first build from the docker compose using the command below

```bash
docker-compose build --no-cache-dir
```



#### Spinning up kestra orchestrator container on GCP Virtual Machine

Pre-requisites: Have docker and docker-compose setup beforehand.

1. To spin up the docker container on GCP Virtual Machine, first copy the 'kestra_docker_files' directory within the 'kestra-data' folder to the 'Documents' folder of the GCP VM.
   
2. To spin up the docker container, first build from the docker compose using the command below

```bash
docker-compose build --no-cache-dir
```

3. Then run the docker container using the following command

```bash
docker-compose up -d
```

4. Check if kestra is accessible from the <GCP_IP_STATIC_ADDRESS>:8080. e.g. 34.2.16.41:8080

![image](https://github.com/user-attachments/assets/bee92d01-f534-478f-99e7-25f393b9c28b)

#### Setting up the dataproc cluster

1. Create a new dataproc cluster on GCP.
2. Under the GCS bucket, host the following files (the files are present in the "dataprocs" folder within this repository):

   ![image](https://github.com/user-attachments/assets/3f28807e-75f9-41d3-8516-c4b7d62877b6)

   The above is the .whl file of the VADER sentiment analysis library extracted through tar extractor and zipped to a zipped folder.

   

   ![image](https://github.com/user-attachments/assets/e8a24058-f755-43a8-a86f-5044f0fdf331)

   The above is the main python script to run the Pyspark transformations as well as perform predictions using the VADER sentiment analysis library.

#### Creating the kestra workflow

Pre-requisites: Ensure kestra docker is running; dataprocs cluster is set-up and running.

1. Click "Create Flow".

2. Toggle to "No-code editor"

3. Copy paste the code from 'kestra_flow.yaml'.

4. Execute the code and see if it is able to execute successfully. It roughly takes about ~ 30 minutes to run end-to-end.


### Limitations of Project

1. Due to the duration of the project and complexity in establishing the reverse SSH tunneling, a terraform script could not be created for this project. This might be seen as the next leg of the project to deploy it in an IAAC fashion.
   
2. Scraping of reddit webpages cannot be done through scripts deployed on GCP VM as reddit network security blocks such scraping of data - the only route would be to set it up on a Oracle VM machine running locally - however, the trigger to start the 'scraper' docker within the oracle VM requires a trigger from GCP VM (thus the need for reverse tunneling).

   





