"""
Simple script to run the Discord bot
"""
import asyncio
import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log")
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Run the Discord bot"""
    logger.info("Starting Discord bot...")
    
    try:
        # Import the bot module
        from bot import startup
        
        # Run the startup function
        await startup()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    # Run the main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)