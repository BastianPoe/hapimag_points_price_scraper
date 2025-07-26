# Use a base image with Python and necessary build tools
FROM python:3.9.23-bookworm

# Set environment variables for headless Chrome
ENV DEBIAN_FRONTEND=noninteractive
# Specify a compatible ChromeDriver version
ENV CHROME_DRIVER_VERSION=138.0.7204.168
# Specify a compatible Chrome version
ENV CHROME_VERSION=138.0.7204.168

# Install Google Chrome and ChromeDriver
# This section has been updated to use a more robust method for adding the GPG key
# and installing Chrome, addressing potential issues with apt-key add.
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
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
    --no-install-recommends 

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \ 
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
RUN apt-get update && apt-get install -y google-chrome-stable=${CHROME_VERSION}-1 --no-install-recommends

# Add Google Chrome GPG key and repository using a more modern approach
#RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
#    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
#    apt-get update && \
#    apt-get install -y google-chrome-stable=${CHROME_VERSION}-1 --no-install-recommends

# Dynamically find the installed Chrome version and download compatible ChromeDriver
#RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+') && \
#    CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" | \
#                           grep -oP "\"$CHROME_VERSION\"[^}]*\"chromedriver\":\s*\[\s*{\s*\"platform\":\s*\"linux64\",\s*\"url\":\s*\"([^\"]+)\"" | \
#                           head -1 | sed -E 's/.*"url":\s*"([^"]+)".*/\1/') && \
#    wget -N "$CHROMEDRIVER_VERSION" -O /tmp/chromedriver-linux64.zip && \
#    unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ && \
#    mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
#    rm -rf /tmp/chromedriver-linux64.zip /usr/local/bin/chromedriver-linux64 && \
#    chmod +x /usr/local/bin/chromedriver && \
#    apt-get clean && \
#    rm -rf /var/lib/apt/lists/*
    
# Download and install ChromeDriver
RUN wget -N https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_DRIVER_VERSION}/linux64/chromedriver-linux64.zip -P /tmp/ && \
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

ENV DISPLAY=:99

# Install Python dependencies
# It's recommended to use a requirements.txt file for your dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the Python script
# Use --headless=new for newer Chrome versions
CMD ["python", "hapimag_points_price_scraper.py"]
