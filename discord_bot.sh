#!/bin/bash

# Discord Bot Worker Script - Runs the Discord bot in continuous mode

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BLUE}${BOLD}=== Tower of Temptation PvP Discord Bot ===\n${NC}"
echo -e "${GREEN}Starting Discord bot in continuous mode...${NC}"
echo -e "${YELLOW}Bot will restart automatically if it crashes${NC}\n"

# Create a flag file to indicate this is running in a workflow
touch .running_in_workflow

# Run the bot in an infinite loop to auto-restart on errors
while true; do
  echo -e "${GREEN}$(date) - Starting bot...${NC}"
  
  # Run the bot
  python main.py
  
  # Check exit code
  EXIT_CODE=$?
  if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}$(date) - Bot shut down cleanly. Restarting...${NC}"
  else
    echo -e "${YELLOW}$(date) - Bot crashed with exit code $EXIT_CODE. Restarting in 10 seconds...${NC}"
    sleep 10
  fi
  
  # Small delay to prevent CPU hammering in case of repeated rapid failures
  sleep 1
done