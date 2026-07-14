#!/bin/bash

# Discord Bot Hosting - Deployment Script
# This script helps deploy the application to a VPS

echo "=========================================="
echo "  Discord Bot Hosting - Deployment Script"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Warning: Node.js is not installed. It's required for running Node.js bots."
    echo "Install it with: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs"
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p uploads bots logs

# Initialize database
echo "Initializing database..."
python -c "from database import init_db; init_db()"

echo ""
echo "=========================================="
echo "  Deployment Complete!"
echo "=========================================="
echo ""
echo "To start the application:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "For production use:"
echo "  source venv/bin/activate"
echo "  gunicorn -w 4 -b 0.0.0.0:5000 app:app"
echo ""
echo "Access the application at: http://localhost:5000"
echo ""
