

import pandas as pd
import time, os, argparse
from sqlalchemy import create_engine



def main(params):
    '''
    write code to do the following:
    1. get the green taxi data from the URL
    2. Establish connection to postgresql database 'ny_taxi'.
    3. Insert data into the table 'green_taxi_data' within the 'ny_taxi' database.
    4. time the insertion of data
    
    '''

    #unpack params
    greentaxi_url = params.greentaxi_url
    zones_url = params.zones_url
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table = params.table
    batch_size = params.batch_size

    # 1. get the green taxi data from the URL
    print(greentaxi_url)
    os.system(f"wget {greentaxi_url}")


    # 2. Establish connection to postgresql database 'ny_taxi'.
    engine=create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")
    df = pd.read_csv('green_tripdata_2019-10.csv.gz')

    # 3. Insert data into the table 'green_taxi_data' within the 'ny_taxi' database.
    df.head(n=0).to_sql(table, con=engine, if_exists='replace')
    df_iter = pd.read_csv('green_tripdata_2019-10.csv.gz', iterator=True, chunksize=int(batch_size))

    i=1
    while True:
        try:
            time_start = time.time()
            df = next(df_iter)
            df.to_sql('green_taxi_data', con=engine, if_exists='append')
            time_end = time.time()
            duration = time_end-time_start
            print(f'Inserted chunk {i} which took {duration:.3f} s')
            i+=1
        except:
            break

    # 4. Download zones lookup data
    print(zones_url)
    os.system(f"wget {zones_url}")

    # 5. Insert data into the zones lookup table.
    zones = pd.read_csv('taxi_zone_lookup.csv')
    zones.to_sql('zones', con=engine, if_exists='replace')



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest CSV data into postgres')
    parser.add_argument('--greentaxi_url', help='URL for the CSV file')
    parser.add_argument('--zones_url', help='URL for the Zones CSV file')
    parser.add_argument('--user', help='user name for postgres')
    parser.add_argument('--password', help='password for postgres')
    parser.add_argument('--host', help='host for postgres')
    parser.add_argument('--port', help='port for postgres')
    parser.add_argument('--db', help='DB for postgres')
    parser.add_argument('--table', help='Table name for postgres data insertion')
    parser.add_argument('--batch_size', help='Chunk size for writing data into postgres')
    args = parser.parse_args()
    main(args)



 









