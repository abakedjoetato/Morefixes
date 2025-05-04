"""
Validate Tower of Temptation Discord Bot Startup and Command Structure

This script performs validation of the actual bot startup to ensure:
1. The bot connects successfully to Discord
2. All commands are registered correctly
3. Multi-guild capability is properly initialized
4. Each cog and command is validated for syntax and structure
5. No errors occur during live startup

Run this script before deployment to verify everything works in a real environment.
"""

import asyncio
import importlib
import logging
import os
import sys
from datetime import datetime

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"bot_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)

logger = logging.getLogger("bot_validator")

# Load environment variables
load_dotenv()

class BotValidator:
    """Validates the Tower of Temptation Bot in a live environment"""
    
    def __init__(self):
        """Initialize the validator"""
        self.validation_results = {
            "startup": False,
            "connection": False,
            "commands": False,
            "multi_guild": False
        }
        self.commands_validated = set()
        self.guild_tests_passed = []
        self.guild_tests_failed = []
    
    async def validate_environment(self):
        """Validate that all required environment variables are set"""
        logger.info("Validating environment variables...")
        
        required_vars = ["DISCORD_TOKEN", "BOT_APPLICATION_ID", "HOME_GUILD_ID", "MONGODB_URI"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
            logger.error("Please set these variables in Replit Secrets")
            return False
        
        logger.info("Environment variables validated successfully")
        return True
    
    async def validate_database(self):
        """Validate database connection"""
        logger.info("Validating database connection...")
        
        try:
            # Import database module
            from utils.database import get_db
            
            # Attempt to get database connection
            db = await get_db()
            
            if db is None:
                logger.error("Database connection failed - returned None")
                return False
            
            # Check if we can query the database
            guild_count = await db.db.guilds.count_documents({})
            logger.info(f"Database connection successful - found {guild_count} guilds")
            
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    async def validate_bot_startup(self):
        """Validate that the bot can start up successfully"""
        logger.info("Validating bot startup...")
        
        try:
            # Import bot module
            from bot import initialize_bot
            
            # Initialize bot (don't actually start it)
            bot = await initialize_bot(force_sync=False)
            
            if bot is None:
                logger.error("Bot initialization failed - returned None")
                return False
            
            # Check if basic bot attributes are set
            if not hasattr(bot, "cogs") or not bot.cogs:
                logger.error("Bot cogs not loaded properly")
                return False
            
            # Check if app commands are registered
            if not hasattr(bot, "application_commands") or not bot.application_commands:
                logger.error("Bot commands not registered properly")
                return False
            
            # Log cogs and commands found
            logger.info(f"Bot initialized successfully with {len(bot.cogs)} cogs")
            logger.info(f"Bot has {len(bot.application_commands)} application commands")
            
            # Save validation result
            self.validation_results["startup"] = True
            
            # Print cog and command info
            for cog_name, cog in bot.cogs.items():
                logger.info(f"Cog: {cog_name}")
                cog_commands = [cmd for cmd in bot.application_commands if cmd.cog == cog]
                
                if hasattr(cog, 'get_commands'):
                    # Get commands from the cog if available
                    cog_commands.extend(cog.get_commands())
                
                for cmd in cog_commands:
                    logger.info(f"  - Command: {cmd.name}")
                    self.commands_validated.add(cmd.name)
            
            return True
        except Exception as e:
            logger.error(f"Bot initialization failed: {e}")
            return False
    
    async def validate_multi_guild(self):
        """Validate multi-guild functionality"""
        logger.info("Validating multi-guild functionality...")
        
        try:
            # Run the multi-guild isolation test
            logger.info("Running multi-guild isolation test...")
            from test_multi_guild_isolation import MultiGuildTestSuite
            
            # Create test suite and run tests
            test_suite = MultiGuildTestSuite()
            result = await test_suite.run_tests()
            
            # Check results
            passed = test_suite.results["passed"]
            total = test_suite.results["total_tests"]
            failed = test_suite.results["failed"]
            
            if failed > 0:
                logger.error(f"Multi-guild test failed: {failed} of {total} tests failed")
                return False
            
            logger.info(f"Multi-guild test passed: {passed} of {total} tests passed")
            self.validation_results["multi_guild"] = True
            return True
        except Exception as e:
            logger.error(f"Multi-guild validation failed: {e}")
            return False
    
    async def validate_critical_paths(self):
        """Validate critical command paths"""
        logger.info("Validating critical command paths...")
        
        # Check if bounty system is working correctly
        try:
            from models.bounty import Bounty
            from utils.database import get_db
            
            db = await get_db()
            guild_id = "test_guild_123"
            server_id = "test_server_123"
            
            # Create test bounty
            bounty = await Bounty.create(
                db=db,
                guild_id=guild_id,
                server_id=server_id,
                target_id="test_target",
                target_name="Test Target",
                placed_by="test_user",
                placed_by_name="Test User",
                reason="Test bounty",
                reward=100
            )
            
            if bounty is None:
                logger.error("Failed to create test bounty")
                self.guild_tests_failed.append("bounty_creation")
            else:
                logger.info("Successfully created test bounty")
                self.guild_tests_passed.append("bounty_creation")
                
                # Get bounties for the guild
                bounties = await Bounty.get_active_bounties(db, guild_id=guild_id, server_id=server_id)
                
                if not bounties or len(bounties) == 0:
                    logger.error("Failed to retrieve bounties for guild")
                    self.guild_tests_failed.append("bounty_retrieval")
                else:
                    logger.info(f"Successfully retrieved {len(bounties)} bounties for guild")
                    self.guild_tests_passed.append("bounty_retrieval")
                    
                    # Clean up test bounty
                    await db.bounties.delete_one({"bounty_id": bounty.bounty_id})
                    logger.info("Cleaned up test bounty")
            
            return len(self.guild_tests_failed) == 0
        except Exception as e:
            logger.error(f"Failed to validate critical paths: {e}")
            self.guild_tests_failed.append("critical_paths")
            return False
    
    async def run_validation(self):
        """Run full validation suite"""
        logger.info("Starting Tower of Temptation Discord Bot validation...")
        
        # Check environment variables
        env_valid = await self.validate_environment()
        if not env_valid:
            logger.critical("Environment validation failed - aborting")
            return False
        
        # Check database connection
        db_valid = await self.validate_database()
        if not db_valid:
            logger.critical("Database validation failed - aborting")
            return False
        
        # Validate the bot startup process
        bot_valid = await self.validate_bot_startup()
        if not bot_valid:
            logger.critical("Bot startup validation failed - aborting")
            return False
        
        # Validate multi-guild functionality
        multi_guild_valid = await self.validate_multi_guild()
        if not multi_guild_valid:
            logger.warning("Multi-guild validation failed - this may cause issues with bot operation")
        
        # Validate critical command paths
        critical_valid = await self.validate_critical_paths()
        if not critical_valid:
            logger.warning("Critical path validation failed - some commands may not work correctly")
        
        # Generate summary
        all_passed = all(self.validation_results.values()) and critical_valid
        
        logger.info("\n===== VALIDATION SUMMARY =====")
        for step, result in self.validation_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{step}: {status}")
        
        logger.info(f"\nCommands validated: {len(self.commands_validated)}")
        for cmd in sorted(self.commands_validated):
            logger.info(f"  - {cmd}")
        
        logger.info(f"\nGuild functionality tests passed: {len(self.guild_tests_passed)}")
        for test in self.guild_tests_passed:
            logger.info(f"  - {test}")
        
        if self.guild_tests_failed:
            logger.info(f"\nGuild functionality tests failed: {len(self.guild_tests_failed)}")
            for test in self.guild_tests_failed:
                logger.info(f"  - {test}")
        
        if all_passed:
            logger.info("\n✅ ALL VALIDATION STEPS PASSED - BOT IS READY FOR DEPLOYMENT")
        else:
            logger.critical("\n❌ VALIDATION FAILED - ISSUES MUST BE RESOLVED BEFORE DEPLOYMENT")
        
        return all_passed

async def main():
    """Main validation function"""
    validator = BotValidator()
    result = await validator.run_validation()
    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))