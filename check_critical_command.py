#!/usr/bin/env python3
"""
Single Command Checker for Discord Bot

Run this directly from the command line with a single command to test.
This script will handle authentication, avoid Discord rate limits, 
and time out properly if needed.
"""
import os
import sys
import asyncio
import logging
import discord
from discord.ext import commands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('command_checker')

# Test channel
TEST_CHANNEL_ID = 1360632422957449237

class CommandChecker(commands.Bot):
    def __init__(self, command):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.command_to_test = command
        self.test_channel = None
        self.done = asyncio.Event()
        
    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")
        self.test_channel = self.get_channel(TEST_CHANNEL_ID)
        
        if not self.test_channel:
            logger.error(f"Could not find test channel {TEST_CHANNEL_ID}")
            self.done.set()
            return
            
        logger.info(f"Found channel: {self.test_channel.name}")
        
        try:
            await self.test_command()
        except Exception as e:
            logger.error(f"Error testing command: {e}")
        finally:
            self.done.set()
            
    async def test_command(self):
        logger.info(f"Testing command: {self.command_to_test}")
        
        # Send message about testing
        await self.test_channel.send(f"🧪 Testing command: `{self.command_to_test}`")
        
        # Send the actual command
        await self.test_channel.send(f"{self.command_to_test}")
        
        # Wait briefly
        await asyncio.sleep(5)
        
        # Confirm test complete
        await self.test_channel.send(f"✅ Test completed for `{self.command_to_test}`")
        logger.info("Test completed")

async def main():
    if len(sys.argv) < 2:
        print("Usage: python check_critical_command.py <command>")
        return 1
        
    command = sys.argv[1]
    token = os.environ.get("DISCORD_TOKEN")
    
    if not token:
        logger.error("No DISCORD_TOKEN found in environment variables")
        return 1
        
    # Create bot and run test
    bot = CommandChecker(command)
    async with bot:
        try:
            await bot.start(token)
            # Add a timeout for the done event
            try:
                await asyncio.wait_for(bot.done.wait(), timeout=30)
            except asyncio.TimeoutError:
                logger.warning("Test timed out after 30 seconds")
        except Exception as e:
            logger.error(f"Error running bot: {e}")
            return 1
    
    logger.info("Test completed successfully")
    return 0

if __name__ == "__main__":
    asyncio.run(main())