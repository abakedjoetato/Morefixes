"""
Verify Tower of Temptation Discord Bot Startup

This script tests the main.py entry point to ensure it correctly:
1. Loads environment variables
2. Validates required configuration
3. Initializes database connections
4. Sets up Discord client
5. Loads cogs without errors

This is a lightweight verification that doesn't actually connect to Discord,
but validates all the startup code paths to ensure the bot will start correctly.
"""

import importlib
import logging
import os
import sys
import asyncio
import time
from unittest.mock import patch, MagicMock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("verify_startup.log")
    ]
)
logger = logging.getLogger(__name__)


async def mock_startup_sequence():
    """Mock the bot startup sequence to verify it works correctly"""
    logger.info("Starting mock startup sequence")
    
    # Record start time
    start_time = time.time()
    
    # Step 1: Check environment variables
    logger.info("Step 1: Checking environment variables")
    
    required_vars = ["DISCORD_TOKEN", "BOT_APPLICATION_ID", "HOME_GUILD_ID", "MONGODB_URI"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in Replit Secrets or .env file")
        return {
            "success": False,
            "step": "environment_check",
            "error": f"Missing variables: {', '.join(missing_vars)}",
            "time_taken": time.time() - start_time
        }
    
    logger.info("Environment variables look good")
    
    # Step 2: Import main module
    logger.info("Step 2: Importing main module")
    
    try:
        main_module = importlib.import_module("main")
        logger.info("Successfully imported main module")
    except Exception as e:
        logger.error(f"Failed to import main module: {e}")
        return {
            "success": False,
            "step": "import_main",
            "error": str(e),
            "time_taken": time.time() - start_time
        }
    
    # Step 3: Check startup function exists
    logger.info("Step 3: Checking startup function exists")
    
    if not hasattr(main_module, "start_bot"):
        logger.error("Main module does not have start_bot function")
        return {
            "success": False,
            "step": "check_start_bot",
            "error": "start_bot function not found in main.py",
            "time_taken": time.time() - start_time
        }
    
    logger.info("start_bot function exists")
    
    # Step 4: Mock bot startup
    logger.info("Step 4: Mocking bot startup")
    
    # We'll patch the actual startup function that connects to Discord
    # but let all the initialization code run
    try:
        with patch("bot.startup") as mock_bot_startup:
            # Set up mock to return a coroutine
            async def mock_async_function():
                await asyncio.sleep(0)
                return True
                
            mock_bot_startup.return_value = mock_async_function()
            
            # Call the start_bot function
            main_module.start_bot()
            
            # If we got here without exceptions, startup validation passed
            logger.info("Bot startup sequence completed successfully")
            
            return {
                "success": True,
                "step": "complete",
                "error": None,
                "time_taken": time.time() - start_time
            }
    except Exception as e:
        logger.error(f"Error during bot startup: {e}")
        return {
            "success": False,
            "step": "bot_startup",
            "error": str(e),
            "time_taken": time.time() - start_time
        }


def format_results(results):
    """Format verification results as a string
    
    Args:
        results: Results dictionary from verification
    
    Returns:
        Formatted string with results
    """
    lines = ["BOT STARTUP VERIFICATION RESULTS", "=" * 60, ""]
    
    # Show success/failure
    if results["success"]:
        lines.append("✅ SUCCESS: Bot startup verification passed")
    else:
        lines.append(f"❌ FAILED: Bot startup failed at step '{results['step']}'")
        lines.append(f"Error: {results['error']}")
    
    # Show timing
    lines.append(f"\nTime taken: {results['time_taken']:.2f} seconds")
    
    # Add recommendations
    lines.append("\nRecommendations:")
    if results["success"]:
        lines.append("- Run the bot with 'python main.py' to start it normally")
        lines.append("- Use the Replit Run button which calls main.py")
        lines.append("- Consider setting up Replit's Always On feature to keep the bot running")
    else:
        if results["step"] == "environment_check":
            lines.append("- Add the missing environment variables to Replit Secrets")
            lines.append("- Check .env file if you're running locally")
        elif results["step"] == "import_main":
            lines.append("- Check main.py for syntax errors")
            lines.append("- Ensure all imports in main.py are available")
        elif results["step"] == "check_start_bot":
            lines.append("- Add a start_bot function to main.py")
            lines.append("- Ensure main.py is set up correctly to start the bot")
        elif results["step"] == "bot_startup":
            lines.append("- Check bot.py for errors during initialization")
            lines.append("- Ensure database connection settings are correct")
            lines.append("- Check for errors in cog loading")
    
    return "\n".join(lines)


async def main():
    """Run the startup verification"""
    logger.info("Starting bot startup verification")
    
    # Run the verification
    results = await mock_startup_sequence()
    
    # Format and print results
    output = format_results(results)
    print("\n" + output + "\n")
    
    # Return exit code based on success
    return 0 if results["success"] else 1


if __name__ == "__main__":
    # Run the verification
    exit_code = asyncio.run(main())
    sys.exit(exit_code)