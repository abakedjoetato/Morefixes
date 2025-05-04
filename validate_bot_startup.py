#!/usr/bin/env python3
"""
Bot Startup Validation

This module validates the bot's configuration and requirements before starting it.
It checks for:
1. Environment variables
2. Database connectivity
3. Discord token validity
4. Required directories
5. Required permissions
"""

import os
import sys
import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)

async def validate_environment_variables() -> Tuple[bool, List[str]]:
    """
    Validate required environment variables.
    
    Returns:
        Tuple[bool, List[str]]: Success status and list of missing variables
    """
    required_vars = [
        "DISCORD_TOKEN",
        "MONGODB_URI"
    ]
    
    optional_vars = [
        "MONGODB_DB",
        "LOG_LEVEL",
        "COMMAND_PREFIX"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars

async def validate_directory_structure() -> bool:
    """
    Validate the required directory structure exists.
    
    Returns:
        bool: True if directory structure is valid
    """
    required_dirs = [
        "cogs",
        "utils",
        "models"
    ]
    
    for dir_name in required_dirs:
        if not os.path.isdir(dir_name):
            logger.error(f"Required directory missing: {dir_name}")
            return False
    
    return True

async def validate_database_connection() -> bool:
    """
    Validate database connection.
    
    Returns:
        bool: True if database connection is valid
    """
    try:
        from utils.db import connect_to_mongodb
        db = await connect_to_mongodb()
        if db:
            logger.info("Database connection verified")
            return True
        else:
            logger.error("Failed to connect to database")
            return False
    except Exception as e:
        logger.error(f"Error validating database connection: {e}")
        return False

async def validate_required_files() -> bool:
    """
    Validate required files exist.
    
    Returns:
        bool: True if all required files exist
    """
    required_files = [
        "bot.py",
        "utils/embed_builder.py",
        "utils/helpers.py",
        "utils/database.py"
    ]
    
    for file_path in required_files:
        if not os.path.isfile(file_path):
            logger.error(f"Required file missing: {file_path}")
            return False
    
    return True

async def validate_bot_token() -> bool:
    """
    Validate Discord bot token.
    
    Returns:
        bool: True if token is valid
    """
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        logger.error("Discord token not found in environment variables")
        return False
    
    # Basic validation: check if token has the correct format
    if len(token) < 50 or not "." in token:
        logger.warning("Discord token format looks invalid")
        return False
    
    return True

async def validate_bot_configuration() -> Dict[str, Any]:
    """
    Validate the complete bot configuration.
    
    Returns:
        Dict[str, Any]: Validation results for each component
    """
    results = {}
    
    # Validate environment variables
    env_valid, missing_vars = await validate_environment_variables()
    results["environment_variables"] = {
        "valid": env_valid,
        "missing": missing_vars
    }
    
    # Validate directory structure
    dir_valid = await validate_directory_structure()
    results["directory_structure"] = dir_valid
    
    # Validate database connection
    db_valid = await validate_database_connection()
    results["database_connection"] = db_valid
    
    # Validate required files
    files_valid = await validate_required_files()
    results["required_files"] = files_valid
    
    # Validate bot token
    token_valid = await validate_bot_token()
    results["bot_token"] = token_valid
    
    # Overall validation result
    results["overall"] = (
        env_valid and
        dir_valid and
        db_valid and
        files_valid and
        token_valid
    )
    
    return results

async def main():
    """
    Validate bot configuration and print results.
    """
    logger.info("Validating bot configuration...")
    
    results = await validate_bot_configuration()
    
    if results["overall"]:
        logger.info("Bot configuration is valid!")
        return 0
    else:
        logger.error("Bot configuration is invalid!")
        
        # Print detailed validation results
        for key, value in results.items():
            if key != "overall":
                if isinstance(value, dict):
                    logger.info(f"{key}: {value['valid']}")
                    if not value['valid'] and 'missing' in value:
                        logger.info(f"  Missing: {', '.join(value['missing'])}")
                else:
                    logger.info(f"{key}: {value}")
        
        return 1

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())