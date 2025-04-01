#!/bin/bash

# LocaLocaLocalize Installation Script

echo "=== LocaLocaLocalize Installation ==="
echo "This script will set up the LocaLocaLocalize tool."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$PYTHON_VERSION < 3.8" | bc -l) )); then
    echo "Python version $PYTHON_VERSION is not supported. Please use Python 3.8 or higher."
    exit 1
fi

echo "Using Python $PYTHON_VERSION"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
python -m playwright install chromium

# Create config from sample if it doesn't exist
if [ ! -f config/config.yaml ]; then
    echo "Creating default configuration..."
    mkdir -p config
    cp config/config.sample.yaml config/config.yaml
    echo "Please edit config/config.yaml to configure the tool."
fi

# Create .env from sample if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating environment file..."
    cp .env.sample .env
    echo "Please edit .env to add your credentials and API keys if needed."
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p screenshots reports logs

echo "Installation complete!"
echo ""
echo "To start using LocaLocaLocalize:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Edit config/config.yaml to configure your testing needs"
echo "3. Run the tool: python src/main.py"
echo ""
echo "Happy localizing!" 