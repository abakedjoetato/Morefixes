#!/usr/bin/env python3
"""
Individual Command Testing Utility for Tower of Temptation PvP Statistics Bot

This script provides utility functions to test individual Discord slash commands.
Run this script with a specific command argument to test just that command.
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('command_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Environment variables
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
TEST_CHANNEL_ID = 1360632422957449237  # Specified test channel

# All available commands by category
ALL_COMMANDS = {
    "Admin": [
        "/admin ping",
        "/admin status",
    ],
    "Setup": [
        "/setup check",
        "/setup info",
    ],
    "Stats": [
        "/stats player",
        "/stats server",
        "/stats leaderboard",
    ],
    "Rivalry": [
        "/rivalry list",
        "/rivalry top",
    ],
    "Help": [
        "/help",
    ],
    "Bounties": [
        "/bounty list",
    ],
    "Kill Feed": [
        "/killfeed status",
    ],
}

# Flatten commands list for easier access
ALL_COMMAND_LIST = [cmd for category in ALL_COMMANDS.values() for cmd in category]

class CommandTester(commands.Bot):
    """Bot client for testing commands"""
    
    def __init__(self, command_to_test=None):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.command_to_test = command_to_test
        self.test_channel = None
        self.testing_complete = asyncio.Event()
        
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f"Logged in as {self.user}")
        
        # Get the test channel
        self.test_channel = self.get_channel(TEST_CHANNEL_ID)
        if not self.test_channel:
            logger.error(f"Test channel {TEST_CHANNEL_ID} not found")
            await self.close()
            return
            
        logger.info(f"Testing in channel: {self.test_channel.name}")
        
        # Start the test process
        self.loop.create_task(self.test_command())
            
    async def test_command(self):
        """Test the specified command"""
        try:
            await self.test_channel.send(f"🧪 **Testing Command:** `{self.command_to_test}`")
            
            # Send the command
            await self.test_channel.send(self.command_to_test)
            
            # Wait briefly to allow the command to process
            await asyncio.sleep(5)
            
            # Report success
            await self.test_channel.send(f"✅ Command `{self.command_to_test}` test completed")
            logger.info(f"Command {self.command_to_test} test completed")
            
        except Exception as e:
            logger.error(f"Error testing {self.command_to_test}: {e}")
            await self.test_channel.send(f"❌ Error testing `{self.command_to_test}`: {e}")
        finally:
            # Signal that testing is complete
            self.testing_complete.set()
            await asyncio.sleep(1)  # Give time for messages to send
            await self.close()

async def test_single_command(command):
    """Test a single command"""
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN environment variable not set")
        return 1
        
    logger.info(f"Testing command: {command}")
    
    # Create and run the bot instance
    bot = CommandTester(command)
    try:
        async with bot:
            await bot.start(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        return 1
    
    logger.info(f"Command {command} test complete")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <command>")
        print("Available commands:")
        for category, commands in ALL_COMMANDS.items():
            print(f"\n{category}:")
            for cmd in commands:
                print(f"  {cmd}")
        sys.exit(1)
    
    command_to_test = sys.argv[1]
    
    # If a numeric index is provided, use it to access the command list
    if command_to_test.isdigit():
        index = int(command_to_test)
        if 0 <= index < len(ALL_COMMAND_LIST):
            command_to_test = ALL_COMMAND_LIST[index]
        else:
            print(f"Error: Index {index} out of range")
            sys.exit(1)
    
    # Check if the command is valid
    if command_to_test not in ALL_COMMAND_LIST:
        print(f"Error: Unknown command {command_to_test}")
        print("Available commands:")
        for i, cmd in enumerate(ALL_COMMAND_LIST):
            print(f"  {i}: {cmd}")
        sys.exit(1)
    
    print(f"Testing command: {command_to_test}")
    sys.exit(asyncio.run(test_single_command(command_to_test)))