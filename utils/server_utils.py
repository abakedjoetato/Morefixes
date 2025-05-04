"""
Server utility functions for the Tower of Temptation PvP Statistics Discord Bot.

This module provides functions for working with game servers, including:
1. Server existence checking with multiple fallback methods
2. Server validation
3. Server data retrieval utilities
"""
import logging
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

async def check_server_existence(guild, server_id: str, db=None) -> bool:
    """Check if a server exists in a guild using multiple methods
    
    Args:
        guild: Guild object
        server_id: Server ID to check
        db: Database connection (optional)
        
    Returns:
        bool: True if server exists, False otherwise
    """
    # Ensure server_id is a string for consistency
    server_id = str(server_id)
    
    # Method 1: Check via guild.data if available
    if hasattr(guild, "data") and isinstance(guild.data, dict):
        servers = guild.data.get("servers", [])
        for srv in servers:
            # Handle server entry being dict or string
            if isinstance(srv, dict):
                srv_id = str(srv.get("server_id", ""))
            else:
                srv_id = str(srv)
                
            if srv_id == server_id:
                return True
    
    # Method 2: Check via guild.servers if available 
    if hasattr(guild, "servers") and guild.servers:
        for srv in guild.servers:
            # Handle server entry being dict or string
            if isinstance(srv, dict):
                srv_id = str(srv.get("server_id", ""))
            else:
                srv_id = str(srv)
                
            if srv_id == server_id:
                return True
    
    # Method 3: Try direct DB lookup as last resort
    if db:
        try:
            # Attempt direct MongoDB lookup
            guild_id = getattr(guild, "guild_id", getattr(guild, "id", None))
            if guild_id:
                server_query = {
                    "guild_id": str(guild_id),
                    "servers.server_id": server_id
                }
                direct_guild = await db.db.guilds.find_one(server_query)
                if direct_guild:
                    return True
        except Exception as e:
            logger.warning(f"Error in direct server lookup: {e}")
    
    # Server not found by any method
    return False

async def get_server_data(guild, server_id: str, db=None) -> Optional[Dict[str, Any]]:
    """Get server data for a specific server in a guild
    
    Args:
        guild: Guild object
        server_id: Server ID to get data for
        db: Database connection (optional)
        
    Returns:
        Optional[Dict[str, Any]]: Server data if found, None otherwise
    """
    # Ensure server_id is a string for consistency
    server_id = str(server_id)
    
    # Method 1: Check via guild.data if available
    if hasattr(guild, "data") and isinstance(guild.data, dict):
        servers = guild.data.get("servers", [])
        for srv in servers:
            if isinstance(srv, dict) and str(srv.get("server_id", "")) == server_id:
                return srv
    
    # Method 2: Check via guild.servers if available 
    if hasattr(guild, "servers") and guild.servers:
        for srv in guild.servers:
            if isinstance(srv, dict) and str(srv.get("server_id", "")) == server_id:
                return srv
    
    # Method 3: Try direct DB lookup as last resort
    if db:
        try:
            # Attempt direct MongoDB lookup and projection to get just the server
            guild_id = getattr(guild, "guild_id", getattr(guild, "id", None))
            if guild_id:
                pipeline = [
                    {"$match": {"guild_id": str(guild_id)}},
                    {"$unwind": "$servers"},
                    {"$match": {"servers.server_id": server_id}},
                    {"$project": {"server": "$servers", "_id": 0}}
                ]
                
                cursor = db.db.guilds.aggregate(pipeline)
                async for doc in cursor:
                    if "server" in doc:
                        return doc["server"]
        except Exception as e:
            logger.warning(f"Error in direct server data lookup: {e}")
    
    # Server not found by any method
    return None