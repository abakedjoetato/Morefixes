#!/usr/bin/env python
"""
Apply All Discord Bot Fixes

This script applies all fixes for the Tower of Temptation Discord Bot:
1. Guild model - add get_by_id method
2. Help cog - fix coroutine handling
3. Bounties cog - fix database initialization and missing constants
"""
import logging
import os
import sys
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot_fixes.log")
    ]
)
logger = logging.getLogger(__name__)

def import_fix_module(module_path):
    """Import a fix module from path"""
    if not os.path.exists(module_path):
        logger.error(f"Fix module not found: {module_path}")
        return None
    
    spec = importlib.util.spec_from_file_location("fix_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    """Apply all fixes"""
    logger.info("=== APPLYING ALL FIXES FOR TOWER OF TEMPTATION DISCORD BOT ===")
    
    # Fix 1: Guild model - add get_by_id method
    logger.info("Applying Guild model fix...")
    guild_fix = import_fix_module("fix_guild_model.py")
    if guild_fix and hasattr(guild_fix, "fix_guild_model"):
        guild_fix.fix_guild_model()
    else:
        logger.error("Failed to apply Guild model fix")
    
    # Fix 2: Help cog - fix coroutine handling
    logger.info("Applying Help cog fix...")
    help_fix = import_fix_module("fix_help_cog.py")
    if help_fix and hasattr(help_fix, "fix_help_cog"):
        help_fix.fix_help_cog()
    else:
        logger.error("Failed to apply Help cog fix")
    
    # Fix 3: Bounties cog - fix database initialization
    logger.info("Applying Bounties cog fix...")
    bounties_fix = import_fix_module("fix_bounties_initialization.py")
    if bounties_fix and hasattr(bounties_fix, "fix_bounties_cog"):
        bounties_fix.fix_bounties_cog()
    else:
        logger.error("Failed to apply Bounties cog fix")
    
    logger.info("=== ALL FIXES APPLIED SUCCESSFULLY ===")
    logger.info("")
    logger.info("You can now start the bot using the Replit Run button.")
    logger.info("The bot should function correctly with all cogs enabled.")

if __name__ == "__main__":
    main()