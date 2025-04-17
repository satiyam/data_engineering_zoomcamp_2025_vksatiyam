FROM python:3.12-slim

# Set environment variables
ENV CHROME_VERSION=135.0.7049.84
ENV CHROMEDRIVER_VERSION=135.0.7049.84


# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl wget unzip gnupg2 \
    xvfb x11-utils libxi6 libgconf-2-4 libnss3 libxss1 \
    libxcomposite1 libxcursor1 libxdamage1 libxrandr2 \
    libasound2 libatk1.0-0 libgtk-3-0 libgbm1 libxshmfence1 \
    fonts-liberation xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Download Chrome
RUN wget -O /tmp/chrome-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip && \
    unzip /tmp/chrome-linux64.zip -d /usr/local/ && \
    ln -s /usr/local/chrome-linux64/chrome /usr/bin/chrome && \
    rm /tmp/chrome-linux64.zip


RUN wget -O /tmp/chromedriver-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver-linux64.zip -d /tmp && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver-linux64 /tmp/chromedriver-linux64.zip




# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install dlt[gs]
RUN pip install dlt[parquet]

#install unmet dependencies
RUN apt-get -f install -y

#Clean up old user data on every run
RUN rm -rf /tmp/.com.google.Chrome*

# Copy app files
COPY . /app
WORKDIR /app

# Set display for Xvfb
ENV DISPLAY=:99

# Make port 8888 available to the world outside this container
EXPOSE 8888

CMD ["sh", "-c", "Xvfb :99 -screen 0 1920x1080x24 & python Data_Ingestion.py || tail -f /dev/null"]



