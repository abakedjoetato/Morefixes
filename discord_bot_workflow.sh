#!/bin/bash

# Discord Bot Worker Workflow Script
# This script runs the Discord bot and ensures it stays running

echo "Starting Discord Bot workflow..."
echo "Bot will run continuously in the background"

# Create a flag file to indicate this is running in a workflow
touch .running_in_workflow

# Run the bot
python main.py

# This is a long-running task, it won't exit unless there's an error
echo "Bot workflow completed. Check logs for details."