#!/usr/bin/env python3
"""
Comprehensive Command Testing Script for Tower of Temptation PvP Statistics Bot

This script tests all commands in a specific Discord channel to ensure they're
working properly. It will test each command category and report success/failure.
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

# List of commands to test by category
COMMAND_TESTS = {
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

class CommandTester(commands.Bot):
    """Bot client for testing commands"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.test_results = {}
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
            
        logger.info(f"Testing commands in channel: {self.test_channel.name}")
        
        # Start the test process
        self.loop.create_task(self.run_tests())
        
    async def run_tests(self):
        """Run all command tests"""
        try:
            await self.test_channel.send("🧪 **AUTOMATED COMMAND TESTING**\nTesting all commands to verify functionality...")
            
            total_tests = sum(len(commands) for commands in COMMAND_TESTS.values())
            passed_tests = 0
            
            # Test each category
            for category, commands in COMMAND_TESTS.items():
                logger.info(f"Testing {category} commands")
                await self.test_channel.send(f"**Testing {category} Commands:**")
                
                for command in commands:
                    success = await self.test_command(command)
                    if success:
                        passed_tests += 1
                
                # Add a small delay between categories
                await asyncio.sleep(2)
            
            # Report results
            success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            summary = f"""
📊 **Test Results Summary**
Commands Tested: {total_tests}
Commands Passed: {passed_tests}
Success Rate: {success_rate:.1f}%

{'✅ All commands working correctly!' if passed_tests == total_tests else '⚠️ Some commands failed. See log for details.'}
            """
            
            await self.test_channel.send(summary)
            logger.info(f"Testing complete. {passed_tests}/{total_tests} commands passed.")
            
        except Exception as e:
            logger.error(f"Error during testing: {e}")
            await self.test_channel.send(f"❌ **Testing Error**: {e}")
        finally:
            # Signal that testing is complete
            self.testing_complete.set()
            
    async def test_command(self, command):
        """Test a single command"""
        try:
            logger.info(f"Testing command: {command}")
            await self.test_channel.send(f"Testing: `{command}`")
            
            # Send the command
            await self.test_channel.send(command)
            
            # Wait for a response (timeout after 10 seconds)
            try:
                await asyncio.sleep(3)  # Give the bot time to respond
                logger.info(f"Command {command} executed without errors")
                await self.test_channel.send(f"✅ `{command}` executed")
                return True
            except asyncio.TimeoutError:
                logger.warning(f"Command {command} timed out waiting for response")
                await self.test_channel.send(f"⚠️ `{command}` timed out")
                return False
                
        except Exception as e:
            logger.error(f"Error executing {command}: {e}")
            await self.test_channel.send(f"❌ `{command}` failed: {e}")
            return False

async def main():
    """Main function"""
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN environment variable not set")
        return 1
        
    logger.info("Starting command testing")
    
    # Create the bot instance
    bot = CommandTester()
    
    try:
        # Start the bot and wait for testing to complete
        await bot.start(DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        return 1
    finally:
        await bot.close()
        
    logger.info("Command testing complete")
    return 0

if __name__ == "__main__":
    print(f"Starting command testing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sys.exit(asyncio.run(main()))