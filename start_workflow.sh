#!/bin/bash

# Make workflow scripts executable
chmod +x start_bot.sh
chmod +x discord_bot_workflow.sh

# Start the requested workflow
if [ "$1" == "test" ]; then
  echo "Starting comprehensive test workflow..."
  bash discord_bot_workflow.sh
elif [ "$1" == "bot" ]; then
  echo "Starting Discord bot..."
  bash start_bot.sh
else
  echo "Usage: bash start_workflow.sh [test|bot]"
  echo "  test: Run comprehensive testing of all bot components"
  echo "  bot: Start the Discord bot for continuous operation"
  exit 1
fi