"""
Tower of Temptation PvP Statistics Bot - Main Entry Point

This file serves as the primary entry point for the Discord bot, making it easy to run
with the Replit Run button. It imports and executes the Discord bot code from bot.py.
"""
import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log")
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def start_bot():
    """Import and run the bot startup code"""
    try:
        # Check for required environment variables
        required_vars = ["DISCORD_TOKEN", "BOT_APPLICATION_ID", "HOME_GUILD_ID", "MONGODB_URI"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.critical(f"Missing required environment variables: {', '.join(missing_vars)}")
            logger.critical("Please set these variables in Replit Secrets or .env file")
            return
            
        # Dynamically import to avoid circular imports
        from bot import startup
        
        # Run the Discord bot
        logger.info("Starting Tower of Temptation PvP Statistics Bot")
        
        # Set up asyncio event loop
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(startup())
        except KeyboardInterrupt:
            logger.info("Bot shutting down due to keyboard interrupt...")
        except Exception as e:
            logger.critical(f"Unhandled exception: {e}", exc_info=True)
        finally:
            loop.close()
            logger.info("Bot has shut down. Goodbye!")
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}", exc_info=True)

if __name__ == "__main__":
    start_bot()