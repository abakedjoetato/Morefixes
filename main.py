#!/usr/bin/env python3
"""
Tower of Temptation PvP Statistics Discord Bot - Main Entry Point

This is the main entry point for the Discord bot. It handles:
1. Loading environment variables
2. Setting up Discord client
3. Connecting to MongoDB
4. Loading cogs (command modules)
5. Starting the bot

Run this file directly with Python to start the bot.
"""

import os
import sys
import logging
import asyncio
from datetime import datetime

# Check if running in a workflow
is_workflow = os.path.exists(".running_in_workflow")
print(f"Running in workflow mode: {is_workflow}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log')
    ]
)

async def main():
    """Main entry point for the bot."""
    try:
        # Import the bot startup from bot.py
        from bot import startup
        
        # Run the bot
        await startup()
    except Exception as e:
        logging.error(f"Error starting bot: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # For Python 3.10+, use this:
    print(f"Starting bot at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.run(main())