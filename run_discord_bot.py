
"""
Entry point script for the Discord bot
"""
import asyncio
import logging
import os
from dotenv import load_dotenv
from bot import initialize_bot

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Initialize and run the bot
    try:
        bot = initialize_bot()
        asyncio.run(bot.start(os.getenv('DISCORD_TOKEN')))
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        raise
