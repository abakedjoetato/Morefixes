#!/bin/bash
# Discord Bot Workflow Script
# This script runs the Discord bot and handles restarts

echo "===== Starting Discord Bot ====="
date

# Run the bot
python run_discord_bot.py

# Check if the bot exited with an error
if [ $? -ne 0 ]; then
    echo "Bot exited with an error. Please check the logs."
    echo "===== Bot Stopped with Error ====="
    date
    exit 1
fi

echo "===== Bot Stopped Normally ====="
date