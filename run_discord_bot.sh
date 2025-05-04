#!/bin/bash

# Run Discord Bot Workflow - Start the bot for continuous operation

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Starting Tower of Temptation PvP Discord Bot ===${NC}"
echo -e "${BLUE}===============================================${NC}"

# Run the bot
echo -e "${GREEN}Starting Discord bot...${NC}"
echo -e "${YELLOW}The bot will run continuously. Press Ctrl+C in the console to stop.${NC}\n"

# Make sure the script is executable
chmod +x start_bot.sh

# Run the bot
python main.py