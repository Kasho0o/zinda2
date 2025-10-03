#!/usr/bin/env bash
# exit on error
set -o errexit

# Update package list
apt-get update

# Install required tools and Chrome dependencies
apt-get install -y wget unzip fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 libu2f-udev libvulkan1 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 xdg-utils

# Download and install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb

# Install Python dependencies
pip install -r requirements.txt
