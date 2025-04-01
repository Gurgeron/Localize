#!/bin/bash

# LocaLocaLocalize Run Script
# This script activates the virtual environment and runs the localization testing tool

# Set environment variables for the tool
# Set Google Cloud Vision API key
export GOOGLE_VISION_API_KEY="AIzaSyD9C2WWJd0ezIi4dtfqDKH_RQ1YAtmqKRM"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Display banner
echo -e "${BLUE}"
echo "================================================================"
echo "                    LocaLocaLocalize                            "
echo "            Automated Localization Testing Tool                 "
echo "================================================================"
echo -e "${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating it now...${NC}"
    python3 -m venv venv
    
    echo -e "${YELLOW}Installing dependencies...${NC}"
    source venv/bin/activate
    pip install -r requirements.txt
    
    echo -e "${YELLOW}Installing Playwright browsers...${NC}"
    python -c "from playwright.sync_api import sync_playwright; sync_playwright().start().stop()"
    playwright install
    
    echo -e "${GREEN}Setup complete!${NC}"
else
    echo -e "${GREEN}Found existing virtual environment.${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if configuration file exists
if [ ! -f "config/config.yaml" ]; then
    echo -e "${RED}Configuration file not found!${NC}"
    echo -e "${YELLOW}Creating default configuration from sample...${NC}"
    
    if [ ! -d "config" ]; then
        mkdir -p config
    fi
    
    if [ -f "config/config.sample.yaml" ]; then
        cp config/config.sample.yaml config/config.yaml
        echo -e "${GREEN}Created config/config.yaml. Please review the file before proceeding.${NC}"
        read -p "Do you want to edit the configuration file now? (y/n): " edit_config
        if [[ $edit_config == "y" || $edit_config == "Y" ]]; then
            ${EDITOR:-nano} config/config.yaml
        fi
    else
        echo -e "${RED}Sample configuration file not found! Please create a config/config.yaml file.${NC}"
        exit 1
    fi
fi

# Check for required directories
for dir in logs reports screenshots; do
    if [ ! -d "$dir" ]; then
        echo -e "${YELLOW}Creating $dir directory...${NC}"
        mkdir -p "$dir"
    fi
done

# Display API configuration
echo -e "${GREEN}Using Google Cloud Vision API for improved OCR accuracy${NC}"

# Run the tool
echo -e "${BLUE}Starting LocaLocaLocalize...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the tool at any time.${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""

# Set PYTHONPATH to include the current directory for proper module resolution
cd $(dirname $0)
export PYTHONPATH=$(pwd):$PYTHONPATH

python src/main.py "$@"

# Check exit status
if [ $? -eq 0 ]; then
    echo -e "${GREEN}LocaLocaLocalize completed successfully!${NC}"
else
    echo -e "${RED}LocaLocaLocalize exited with an error.${NC}"
fi

# Deactivate virtual environment
deactivate

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}Thanks for using LocaLocaLocalize!${NC}" 