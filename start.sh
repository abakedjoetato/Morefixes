#!/bin/bash

# Start script for Tower of Temptation PvP Statistics Discord Bot
# This script is used by the Replit Run button to start the bot

# Create a flag file to indicate this is running in a workflow
touch .running_in_workflow

# Make the script executable
chmod +x discord_bot_workflow.sh

# Run the bot
python main.py