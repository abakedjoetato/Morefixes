#!/usr/bin/env python3
"""
Test script to ensure the bot can start up without errors.
This simply tests initialization without actually connecting to Discord.
"""
import asyncio
import logging
from datetime import datetime
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Test bot initialization."""
    try:
        logger.info(f"Starting bot test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Import the bot initialization from bot.py
        from bot import initialize_bot
        
        # Initialize the bot without syncing commands
        logger.info("Initializing bot...")
        bot = await initialize_bot(force_sync=False)
        
        if bot:
            logger.info("Bot initialization successful!")
            return 0
        else:
            logger.error("Bot initialization failed")
            return 1
    except Exception as e:
        logger.error(f"Error testing bot startup: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print(f"Starting bot startup test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    result = asyncio.run(main())
    sys.exit(result)