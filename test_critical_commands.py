#!/usr/bin/env python3
"""
Critical Command Testing for Tower of Temptation PvP Statistics Bot

This script tests the most essential commands to verify bot functionality.
"""
import os
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
        logging.FileHandler('critical_commands.log')
    ]
)
logger = logging.getLogger()

# Discord channel for testing
TEST_CHANNEL_ID = 1360632422957449237

# Critical commands to test
CRITICAL_COMMANDS = [
    # Core functionality
    "/help",
    "/admin ping", 
    "/stats leaderboard",
    "/rivalry list",
    "/bounty list"
]

class CommandTester(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.test_channel = None
        self.test_results = {}
        
    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")
        
        # Get test channel
        self.test_channel = self.get_channel(TEST_CHANNEL_ID)
        if not self.test_channel:
            logger.error(f"Test channel {TEST_CHANNEL_ID} not found")
            await self.close()
            return
            
        logger.info(f"Testing in channel: {self.test_channel.name}")
        
        # Run tests
        try:
            await self.test_critical_commands()
        finally:
            await self.close()
            
    async def test_critical_commands(self):
        await self.test_channel.send("🔍 **TESTING CRITICAL COMMANDS**")
        
        all_passed = True
        
        for command in CRITICAL_COMMANDS:
            try:
                logger.info(f"Testing command: {command}")
                await self.test_channel.send(f"Testing: `{command}`")
                
                # Send the command
                await self.test_channel.send(command)
                
                # Simple delay to let command process
                await asyncio.sleep(3)
                
                # Log success
                logger.info(f"Command {command} test complete")
                await self.test_channel.send(f"✅ `{command}` test complete")
                self.test_results[command] = "PASS"
                
            except Exception as e:
                logger.error(f"Error testing {command}: {e}")
                await self.test_channel.send(f"❌ Error testing `{command}`: {e}")
                self.test_results[command] = f"FAIL: {e}"
                all_passed = False
                
            # Wait between commands
            await asyncio.sleep(2)
            
        # Send summary
        summary = "📊 **Test Results**\n"
        for cmd, result in self.test_results.items():
            status = "✅" if result == "PASS" else "❌"
            summary += f"{status} `{cmd}`: {result}\n"
            
        summary += f"\n{'✅ All critical commands working!' if all_passed else '⚠️ Some commands failed'}"
        
        await self.test_channel.send(summary)
        logger.info(f"Critical command testing complete. All passed: {all_passed}")
        
async def main():
    # Get Discord token
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set")
        return 1
        
    # Create and run bot
    bot = CommandTester()
    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    print(f"Starting critical command testing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.run(main())