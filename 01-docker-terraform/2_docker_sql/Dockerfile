FROM python:3.12.8

RUN apt-get install wget
RUN pip install pandas sqlalchemy psycopg2

WORKDIR /app
COPY load_green_taxi.py load_green_taxi.py

ENTRYPOINT [ "python", "load_green_taxi.py" ]