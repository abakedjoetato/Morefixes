#!/bin/bash

# Start the Tower of Temptation PvP Statistics Web App

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${BLUE}${BOLD}=== Starting Tower of Temptation PvP Statistics Web App ===\n${NC}"
echo -e "${GREEN}Starting web app on port 5000...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the app${NC}\n"

# Ensure all required directories exist
python -c "from app import ensure_directories; ensure_directories()"

# Run the web app
python app.py