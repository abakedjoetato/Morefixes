#!/usr/bin/env python3
"""
Directly check loaded commands in the Discord bot
"""
import os
import sys
import asyncio
import logging
from datetime import datetime

import discord
from discord.ext import commands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('actual_commands.log')
    ]
)
logger = logging.getLogger(__name__)

# Environment variables
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

class CommandChecker(commands.Bot):
    """Bot to check registered commands"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.check_complete = asyncio.Event()
        
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f"Logged in as {self.user}")
        
        try:
            # Check global commands
            logger.info("Checking global commands...")
            global_commands = await self.tree.fetch_commands()
            logger.info(f"Found {len(global_commands)} global commands")
            
            print("\n=== GLOBAL COMMANDS ===")
            for cmd in global_commands:
                print(f"/{cmd.name} - {cmd.description}")
                
            # Check guild commands for the home guild
            home_guild_id = os.environ.get('HOME_GUILD_ID')
            if home_guild_id:
                logger.info(f"Checking commands for home guild {home_guild_id}...")
                home_guild = discord.Object(id=int(home_guild_id))
                guild_commands = await self.tree.fetch_commands(guild=home_guild)
                logger.info(f"Found {len(guild_commands)} guild commands")
                
                print("\n=== GUILD COMMANDS ===")
                for cmd in guild_commands:
                    print(f"/{cmd.name} - {cmd.description}")
            
            # Check loaded cogs
            print("\n=== LOADED COGS ===")
            for cog_name, cog in self.cogs.items():
                print(f"Cog: {cog_name}")
                app_commands = getattr(cog, "app_commands", [])
                if app_commands:
                    for cmd in app_commands:
                        print(f"  /{cmd.name}")
                        
            # Look at bot's command tree
            print("\n=== COMMAND TREE ===")
            for cmd in self.tree.get_commands():
                print(f"/{cmd.name}")
                if hasattr(cmd, "options") and cmd.options:
                    for option in cmd.options:
                        print(f"  └─ {option.name}: {option.description}")
                
        except Exception as e:
            logger.error(f"Error checking commands: {e}")
        finally:
            self.check_complete.set()
            
async def main():
    """Main function"""
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN environment variable not set")
        return 1
        
    logger.info("Starting command checking...")
    
    # Create the bot instance
    bot = CommandChecker()
    
    try:
        # Start the bot and wait for checking to complete
        bot_task = asyncio.create_task(bot.start(DISCORD_TOKEN))
        await bot.check_complete.wait()
        
        # Wait a moment to make sure logs are flushed
        await asyncio.sleep(1)
        
        # Cancel the bot task
        bot_task.cancel()
        
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        return 1
    finally:
        await bot.close()
        
    logger.info("Command checking complete")
    return 0

if __name__ == "__main__":
    print(f"Starting command checking at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sys.exit(asyncio.run(main()))