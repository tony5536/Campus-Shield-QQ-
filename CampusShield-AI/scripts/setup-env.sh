#!/bin/bash

# This script sets up the development environment for CampusShield AI.

# Update package lists
sudo apt-get update

# Install necessary packages
sudo apt-get install -y python3 python3-pip nodejs npm

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies for frontend
cd frontend/web
npm install

# Go back to the root directory
cd ../../

# Print completion message
echo "Development environment setup complete."