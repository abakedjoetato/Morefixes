"""
Server Validation Utilities

This module contains utilities for validating server existence and handling server IDs consistently.
"""
import logging
from typing import Optional, Union, Dict, Any

import discord
from models.server import Server
from models.guild import Guild

logger = logging.getLogger(__name__)

async def get_server(db, server_id: str, guild_id: Union[str, int]) -> Optional[Dict[str, Any]]:
    """
    Get server by ID and guild ID.

    Args:
        db: Database connection
        server_id: Server ID
        guild_id: Guild ID

    Returns:
        Optional[Dict]: Server data if found, None otherwise
    """
    # Ensure consistent type handling
    str_guild_id = str(guild_id)
    str_server_id = str(server_id)

    # Get guild first using flexible query
    guild_data = await db.guilds.find_one({
        "$or": [
            {"guild_id": str_guild_id},
            {"guild_id": int(str_guild_id) if str_guild_id.isdigit() else str_guild_id}
        ]
    })
    
    if not guild_data:
        return None

    # Look for server in guild's servers with consistent string comparison
    for server in guild_data.get("servers", []):
        if str(server.get("server_id", "")).strip() == str_server_id.strip():
            return server

    return None

async def get_server_by_id(db, server_id: str, guild_id: Union[str, int] = None) -> Optional[Dict[str, Any]]:
    """Alias for get_server for compatibility"""
    return await get_server(db, server_id, guild_id)

async def check_server_existence(
    guild: discord.Guild, 
    server_id: str, 
    db=None
) -> bool:
    """
    Check if a server exists using multiple methods with fallbacks.
    """
    if not server_id:
        logger.warning("Empty server ID provided for validation")
        return False

    # Ensure server_id is a string for consistent comparison
    server_id = str(server_id).strip()

    try:
        # Method 1: Database validation (if db provided)
        if db:
            server = await get_server(db, server_id, guild.id)
            if server:
                logger.debug(f"Server {server_id} validated through database")
                return True

        # Method 2: Guild cache validation
        if hasattr(guild, 'servers_cache'):
            if server_id in guild.servers_cache:
                logger.debug(f"Server {server_id} validated through guild cache")
                return True

    except Exception as e:
        logger.error(f"Error validating server {server_id}: {e}")

    logger.warning(f"Server {server_id} validation failed through all methods")
    return False

def standardize_server_id(server_id: Union[str, int]) -> str:
    """Standardize server ID to string format for consistent handling."""
    return str(server_id).strip()

# Alias for backward compatibility
check_server_exists = check_server_existence