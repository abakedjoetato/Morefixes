"""
Server Validation Utilities

This module contains utilities for validating server existence and handling server IDs consistently.
"""
import logging
from typing import Optional, Union, Dict, Any

import discord

logger = logging.getLogger(__name__)

async def check_server_existence(
    guild: discord.Guild, 
    server_id: str, 
    db=None
) -> bool:
    """
    Check if a server exists using multiple methods with fallbacks.
    
    This function implements a robust multi-tiered approach to server validation:
    1. Check the database for the server ID (if db is provided)
    2. Check the guild's custom data cache (if available)
    3. Check the direct server ID against verified servers list
    
    Args:
        guild: The Discord guild where the command was invoked
        server_id: The server ID to check as a string
        db: Optional database connection for database checks
        
    Returns:
        bool: True if the server exists, False otherwise
    """
    if not server_id:
        logger.warning("Empty server ID provided for validation")
        return False
    
    # Ensure server_id is a string for consistent comparison
    server_id = str(server_id).strip()
    
    # Attempt to validate through multiple methods
    try:
        # Method 1: Database validation (if db provided)
        if db:
            from models.server import Server
            server = await Server.get_by_server_id(db, server_id, guild.id)
            if server:
                logger.debug(f"Server {server_id} validated through database")
                return True
        
        # Method 2: Guild cache validation
        if hasattr(guild, 'servers_cache'):
            if server_id in guild.servers_cache:
                logger.debug(f"Server {server_id} validated through guild cache")
                return True
        
        # Method 3: Direct server list validation
        from utils.database import get_database_manager
        db_manager = await get_database_manager()
        if db_manager:
            db = db_manager.db
            from models.server import Server
            server = await Server.get_by_server_id(db, server_id, guild.id)
            if server:
                logger.debug(f"Server {server_id} validated through direct server list")
                return True
    
    except Exception as e:
        logger.error(f"Error validating server {server_id}: {e}")
        # Continue with fallbacks even if one method fails
    
    logger.warning(f"Server {server_id} validation failed through all methods")
    return False

def standardize_server_id(server_id: Union[str, int]) -> str:
    """
    Standardize server ID to string format for consistent handling.
    
    Args:
        server_id: The server ID to standardize (string or integer)
        
    Returns:
        str: The standardized server ID as a string
    """
    return str(server_id).strip()

# Alias for backward compatibility
check_server_exists = check_server_existence

# Function for getting server by ID
async def get_server_by_id(db, server_id: str, guild_id: int):
    """
    Get server by ID.
    
    Args:
        db: Database connection
        server_id: Server ID
        guild_id: Guild ID
        
    Returns:
        Optional[Server]: Server object if found, None otherwise
    """
    from models.server import Server
    return await Server.get_by_server_id(db, server_id, guild_id)