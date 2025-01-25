FROM python:3.9.18

RUN apt-get install wget
RUN pip install pandas sqlalchemy psycopg2

WORKDIR /app
COPY load_green_taxi.py load_green_taxi.py

ENTRYPOINT [ "python", "load_green_taxi.py" ]