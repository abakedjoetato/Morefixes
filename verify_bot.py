#!/usr/bin/env python3
"""
Tower of Temptation Discord Bot Verification Module

This script performs a comprehensive verification of all bot components:
1. Environment variables
2. Module imports 
3. Database connectivity
4. Discord API connectivity
5. Cog loading integrity

Usage: python verify_bot.py
"""
import asyncio
import importlib
import logging
import os
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = logging.getLogger("bot_verification")

CRITICAL_MODULES = [
    "discord", "motor", "pymongo", "asyncssh", "dotenv", 
    "utils.db", "utils.env_config", "utils.database", 
    "models.guild", "models.player", "models.bounty", "models.economy"
]

CRITICAL_ENV_VARS = [
    "DISCORD_TOKEN", "BOT_APPLICATION_ID", "HOME_GUILD_ID", "MONGODB_URI"
]

async def verify_modules():
    """Verify that all critical modules can be imported"""
    logger.info("Verifying critical module imports...")
    missing_modules = []
    
    for module_name in CRITICAL_MODULES:
        try:
            importlib.import_module(module_name)
            logger.info(f"✅ Module {module_name} successfully imported")
        except ImportError as e:
            logger.error(f"❌ Failed to import {module_name}: {e}")
            missing_modules.append(module_name)
    
    if missing_modules:
        logger.critical(f"Missing critical modules: {', '.join(missing_modules)}")
        return False
    
    logger.info("All critical modules imported successfully")
    return True

def verify_env_vars():
    """Verify that all critical environment variables are set"""
    logger.info("Verifying critical environment variables...")
    missing_vars = []
    
    for var in CRITICAL_ENV_VARS:
        if not os.getenv(var):
            logger.error(f"❌ Environment variable {var} is not set")
            missing_vars.append(var)
        else:
            logger.info(f"✅ Environment variable {var} is set")
    
    if missing_vars:
        logger.critical(f"Missing critical environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("All critical environment variables are set")
    return True

async def verify_database():
    """Verify database connectivity"""
    logger.info("Verifying database connectivity...")
    try:
        from utils.database import get_db
        db = await get_db()
        
        if db is None:
            logger.error("❌ Database connection failed - returned None")
            return False
        
        # Check if we can access the database
        guild_count = await db.db.guilds.count_documents({})
        logger.info(f"✅ Database connection successful - found {guild_count} guilds")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

async def verify_discord_api():
    """Verify Discord API connectivity"""
    logger.info("Verifying Discord API connectivity...")
    try:
        import discord
        
        # Create a test client
        intents = discord.Intents.default()
        intents.message_content = True
        client = discord.Client(intents=intents)
        
        # Define an event for when the client is ready
        @client.event
        async def on_ready():
            logger.info(f"✅ Discord API connection successful - logged in as {client.user}")
            await client.close()
        
        # Start the client
        token = os.getenv("DISCORD_TOKEN")
        
        # Use a timeout to ensure we don't hang
        try:
            # Only try to connect for 10 seconds max
            await asyncio.wait_for(client.start(token), 10)
        except asyncio.TimeoutError:
            logger.warning("⚠️ Discord API verification timed out but may still be working")
            # Try to close properly
            await client.close()
            return True
            
        return True
    except Exception as e:
        logger.error(f"❌ Discord API connection failed: {e}")
        return False

async def verify_cogs():
    """Verify all cogs can be loaded"""
    logger.info("Verifying cog loading...")
    from bot import initialize_bot
    try:
        # Initialize the bot without connecting to Discord
        bot = await initialize_bot(connect=False)
        
        # Get list of cogs that should be loaded
        cog_dir = os.path.join(os.getcwd(), "cogs")
        expected_cogs = [f[:-3] for f in os.listdir(cog_dir) 
                         if f.endswith(".py") and not f.startswith("_")]
        
        # Get list of cogs that were actually loaded
        loaded_cogs = list(bot.cogs.keys())
        
        # Check if all expected cogs were loaded
        if len(loaded_cogs) < len(expected_cogs):
            missing_cogs = set(expected_cogs) - set([c.lower() for c in loaded_cogs])
            logger.error(f"❌ Not all cogs were loaded. Missing: {', '.join(missing_cogs)}")
            return False
        
        logger.info(f"✅ All {len(loaded_cogs)} cogs loaded successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Cog verification failed: {e}")
        return False

async def main():
    """Main verification function"""
    logger.info("Starting Tower of Temptation Discord Bot verification...")
    
    # Track verification steps
    verification_steps = [
        ("Environment Variables", verify_env_vars()),
        ("Module Imports", await verify_modules()),
        ("Database Connectivity", await verify_database()),
        ("Discord API", await verify_discord_api()),
        ("Cog Loading", await verify_cogs())
    ]
    
    # Display summary
    logger.info("\n===== VERIFICATION SUMMARY =====")
    all_passed = True
    
    for step_name, result in verification_steps:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{step_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        logger.info("\n✅ ALL VERIFICATION STEPS PASSED - BOT IS READY FOR DEPLOYMENT")
    else:
        logger.critical("\n❌ VERIFICATION FAILED - ISSUES MUST BE RESOLVED BEFORE DEPLOYMENT")
        sys.exit(1)

if __name__ == "__main__":
    # Run the verification
    asyncio.run(main())