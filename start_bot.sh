#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Tower of Temptation Discord Bot...${NC}"

# Check for required environment variables
required_vars=("DISCORD_TOKEN" "BOT_APPLICATION_ID" "HOME_GUILD_ID" "MONGODB_URI")
missing_vars=()

for var in "${required_vars[@]}"
do
  if [ -z "${!var}" ]; then
    missing_vars+=("$var")
  fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
  echo -e "${RED}Error: Missing required environment variables: ${missing_vars[*]}${NC}"
  echo -e "${YELLOW}Please set these variables in Replit Secrets.${NC}"
  exit 1
fi

# Launch the Discord bot using main.py
echo -e "${GREEN}All required environment variables found. Launching bot...${NC}"
python main.py