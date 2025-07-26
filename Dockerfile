# Use a base image with Python and necessary build tools
FROM python:3.9-slim-buster

# Set environment variables for headless Chrome
ENV DEBIAN_FRONTEND=noninteractive
ENV CHROME_DRIVER_VERSION=126.0.6478.126 # Specify a compatible ChromeDriver version
ENV CHROME_VERSION=126.0.6478.126 # Specify a compatible Chrome version

# Install Google Chrome and ChromeDriver
# We need to install gnupg for the Google Chrome repository key
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    libglib2.0-0 \
    libnss3 \
    libfontconfig1 \
    libgconf-2-4 \
    libxi6 \
    libsm6 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxrender1 \
    libxtst6 \
    ca-certificates \
    fonts-liberation \
    lsb-release \
    xdg-utils \
    --no-install-recommends && \
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable=${CHROME_VERSION}-1 --no-install-recommends && \
    wget -N https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_DRIVER_VERSION}/linux64/chromedriver-linux64.zip -P /tmp/ && \
    unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ && \
    mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver-linux64.zip /usr/local/bin/chromedriver-linux64 && \
    chmod +x /usr/local/bin/chromedriver && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the Python script and the configuration file into the container
COPY hapimag_points_price_scraper.py .

# Install Python dependencies
# It's recommended to use a requirements.txt file for your dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the Python script
# Use --headless=new for newer Chrome versions
CMD ["python", "hapimag_points_price_scraper.py"]
