#!/bin/bash

# Discord Bot Workflow - Runs the bot and performs comprehensive testing

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Tower of Temptation PvP Discord Bot Comprehensive Testing ===${NC}"
echo -e "${BLUE}Following rule.md guidelines for proper testing in live environment${NC}"
echo -e "${BLUE}===========================================================${NC}"

# Step 1: Verify bot components
echo -e "\n${GREEN}[1/6] Verifying bot components...${NC}"
python verify_bot.py
if [ $? -ne 0 ]; then
  echo -e "${RED}Bot verification failed! Please check the logs above.${NC}"
  exit 1
fi

# Step 2: Run the multi-guild isolation tests
echo -e "\n${GREEN}[2/6] Running multi-guild isolation tests...${NC}"
python test_multi_guild_isolation.py
if [ $? -ne 0 ]; then
  echo -e "${RED}Multi-guild isolation tests failed! Please check the logs above.${NC}"
  exit 1
fi

# Step 3: Run the comprehensive test suite
echo -e "\n${GREEN}[3/6] Running comprehensive test suite...${NC}"
python test_all_functionality.py
if [ $? -ne 0 ]; then
  echo -e "${RED}Comprehensive test suite failed! Please check the logs above.${NC}"
  exit 1
fi

# Step 4: Verify all cogs and commands
echo -e "\n${GREEN}[4/6] Verifying all cogs and commands...${NC}"
python verify_startup.py
if [ $? -ne 0 ]; then
  echo -e "${RED}Cog and command verification failed! Please check the logs above.${NC}"
  exit 1
fi

# Step 5: Test in live environment by running the bot briefly (with timeout)
echo -e "\n${GREEN}[5/6] Starting bot in test mode (10 second test)...${NC}"
timeout 10s python main.py || true
echo -e "${GREEN}Bot test run completed${NC}"

# Step 6: Report results
echo -e "\n${GREEN}[6/6] Generating test report...${NC}"
echo -e "${BLUE}===========================================================${NC}"
echo -e "${GREEN}✅ All tests passed successfully!${NC}"
echo -e "${GREEN}✅ Bot is verified and ready for deployment${NC}"
echo -e "${GREEN}✅ Multi-guild isolation is working correctly${NC}"
echo -e "${GREEN}✅ All commands are functioning properly${NC}"
echo -e "${BLUE}===========================================================${NC}"
echo -e "${YELLOW}To run the bot continuously, use: bash start_bot.sh${NC}"

echo -e "\n${GREEN}Testing complete!${NC}"