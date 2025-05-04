#!/bin/bash

# Start the Tower of Temptation PvP Statistics Discord Bot

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Starting Tower of Temptation PvP Discord Bot ===${NC}"
echo -e "${YELLOW}This script will start the bot in a continuous running mode${NC}"
echo -e "${BLUE}=============================================${NC}\n"

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo -e "${RED}Python is not installed. Please install Python 3.8+ to run the bot.${NC}"
    exit 1
fi

# Verify that main.py exists
if [ ! -f "main.py" ]; then
    echo -e "${RED}main.py not found. Make sure you're in the correct directory.${NC}"
    exit 1
fi

# Run the bot
echo -e "${GREEN}Starting Discord bot...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the bot${NC}\n"

python3 main.py