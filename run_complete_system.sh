#!/bin/bash

# Run the complete Tower of Temptation PvP Statistics System (both bot and web app)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BLUE}${BOLD}=== Tower of Temptation PvP Complete System ===\n${NC}"
echo -e "${GREEN}Starting both web app and Discord bot in separate processes...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop both components${NC}\n"

# Make sure all scripts are executable
chmod +x start_web_app.sh
chmod +x discord_bot.sh

# Start the web app in background
echo -e "${GREEN}Starting web app on port 5000...${NC}"
./start_web_app.sh &
WEB_PID=$!

# Start the Discord bot
echo -e "${GREEN}Starting Discord bot...${NC}"
./discord_bot.sh &
BOT_PID=$!

# Handle graceful shutdown
function cleanup {
  echo -e "\n${YELLOW}Shutting down both components...${NC}"
  kill -TERM $WEB_PID 2>/dev/null
  kill -TERM $BOT_PID 2>/dev/null
  wait
  echo -e "${GREEN}All components stopped. Goodbye!${NC}"
  exit 0
}

# Trap SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

# Keep script running
echo -e "${GREEN}All components started. System is now running.${NC}"
echo -e "${YELLOW}Access the web dashboard at: http://localhost:5000${NC}"
echo -e "${YELLOW}Press Ctrl+C to shut down both components${NC}\n"

# Wait for both processes
wait