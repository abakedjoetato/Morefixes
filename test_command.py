#!/usr/bin/env python3
"""
Simple Command Tester for Discord Bot

Tests a single command provided as an argument
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
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('command_test.log')
    ]
)
logger = logging.getLogger()

# Discord channel for testing
TEST_CHANNEL_ID = 1360632422957449237

class SimpleCommandTester(commands.Bot):
    def __init__(self, command):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.test_command = command
        self.test_channel = None
        self.complete = asyncio.Event()
        
    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")
        
        # Get test channel
        self.test_channel = self.get_channel(TEST_CHANNEL_ID)
        if not self.test_channel:
            logger.error(f"Test channel {TEST_CHANNEL_ID} not found")
            self.complete.set()
            return
            
        logger.info(f"Testing in channel: {self.test_channel.name}")
        
        # Run test
        try:
            await self.test_single_command()
        finally:
            self.complete.set()
            
    async def test_single_command(self):
        try:
            logger.info(f"Testing command: {self.test_command}")
            await self.test_channel.send(f"Testing command: `{self.test_command}`")
            
            # Send the command
            msg = await self.test_channel.send(self.test_command)
            
            # Wait for a moment
            await asyncio.sleep(3)
            
            # Mark as complete
            await self.test_channel.send(f"✅ Test complete for `{self.test_command}`")
            logger.info(f"Command {self.test_command} test complete")
            
        except Exception as e:
            logger.error(f"Error testing {self.test_command}: {e}")
            await self.test_channel.send(f"❌ Error: {e}")

async def main():
    if len(sys.argv) < 2:
        print("Usage: python test_command.py <command>")
        return 1
    
    command = sys.argv[1]
    token = os.environ.get("DISCORD_TOKEN")
    
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set")
        return 1
    
    bot = SimpleCommandTester(command)
    
    try:
        await bot.start(token)
        await bot.complete.wait()
        await bot.close()
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    asyncio.run(main())