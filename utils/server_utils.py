"""
Server utility functions for the Tower of Temptation PvP Statistics Discord Bot

These utilities provide robust server validation and retrieval functions with multiple fallback methods.
They ensure consistent type handling for server IDs and standardize validation across the codebase.
"""

import logging
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)

async def check_server_exists(db, guild_id, server_id) -> bool:
    """Check if a server exists in the guild configuration
    
    This is a centralized utility to standardize server existence checks across the codebase.
    It implements a multi-tiered validation approach with fallbacks at each level for maximum reliability.
    
    Args:
        db: Database connection
        guild_id: Discord guild ID (string or int)
        server_id: Server ID to check (string or int)
        
    Returns:
        bool: True if server exists, False otherwise
    """
    # Ensure guild_id and server_id are strings for consistent comparison
    guild_id = str(guild_id) if guild_id is not None else None
    server_id = str(server_id) if server_id is not None else None
    
    if not guild_id or not server_id:
        logger.debug("Check server failed: Guild ID or Server ID is empty")
        return False
    
    try:
        # APPROACH 1: Check via guild.data if available
        # First query the database to get the guild
        guild = await db.guilds.find_one({"guild_id": guild_id})
        
        if not guild:
            logger.debug(f"Guild {guild_id} not found in database")
            return False
            
        # APPROACH 1: Check via guild.data.servers
        if "data" in guild and isinstance(guild["data"], dict) and "servers" in guild["data"]:
            # New structure with data.servers
            for server in guild["data"]["servers"]:
                if isinstance(server, dict) and "server_id" in server:
                    srv_id = str(server["server_id"])
                    if srv_id == server_id:
                        logger.debug(f"Server {server_id} found in guild {guild_id} (data.servers)")
                        return True
                elif isinstance(server, str):
                    # Handle case where server might be stored as a simple string
                    srv_id = str(server)
                    if srv_id == server_id:
                        logger.debug(f"Server {server_id} found in guild {guild_id} (data.servers strings)")
                        return True
        
        # APPROACH 2: Check via guild.servers (legacy/traditional structure)
        if "servers" in guild:
            for server in guild["servers"]:
                if isinstance(server, dict):
                    # Handle both formatted and raw server IDs
                    srv_id = str(server.get("server_id", ""))
                    if srv_id == server_id:
                        logger.debug(f"Server {server_id} found in guild {guild_id} (servers)")
                        return True
                elif isinstance(server, str):
                    # Handle case where server might be stored as a simple string
                    srv_id = str(server)
                    if srv_id == server_id:
                        logger.debug(f"Server {server_id} found in guild {guild_id} (servers strings)")
                        return True
                        
        # APPROACH 3: Last resort - check server_ids array if it exists
        if "server_ids" in guild and isinstance(guild["server_ids"], list):
            for srv_id in guild["server_ids"]:
                if str(srv_id) == server_id:
                    logger.debug(f"Server {server_id} found in guild {guild_id} (server_ids)")
                    return True
        
        # If we reach here, the server wasn't found in any location
        logger.debug(f"Server {server_id} not found in guild {guild_id} after all checks")
        return False
        
    except Exception as e:
        logger.error(f"Error checking server existence: {str(e)}")
        return False

async def get_server_by_id(db, guild_id, server_id) -> Optional[Dict[str, Any]]:
    """Get a server by ID
    
    This is a centralized utility to standardize server retrieval across the codebase.
    It implements a multi-tiered approach with fallbacks at each level for maximum reliability.
    
    Args:
        db: Database connection
        guild_id: Discord guild ID (string or int)
        server_id: Server ID to retrieve (string or int)
        
    Returns:
        Optional[Dict[str, Any]]: Server data if found, None otherwise
    """
    # Ensure guild_id and server_id are strings for consistent comparison
    guild_id = str(guild_id) if guild_id is not None else None
    server_id = str(server_id) if server_id is not None else None
    
    if not guild_id or not server_id:
        logger.debug("Get server failed: Guild ID or Server ID is empty")
        return None
    
    try:
        # First query the database to get the guild
        guild = await db.guilds.find_one({"guild_id": guild_id})
        
        if not guild:
            logger.debug(f"Guild {guild_id} not found in database")
            return None
            
        # APPROACH 1: Check via guild.data.servers
        if "data" in guild and isinstance(guild["data"], dict) and "servers" in guild["data"]:
            for server in guild["data"]["servers"]:
                if isinstance(server, dict) and "server_id" in server:
                    srv_id = str(server["server_id"])
                    if srv_id == server_id:
                        logger.debug(f"Server {server_id} found in guild {guild_id} (data.servers)")
                        return server
                elif isinstance(server, str):
                    # If server is stored as a string, we need to construct a basic server object
                    srv_id = str(server)
                    if srv_id == server_id:
                        logger.debug(f"Server {server_id} found in guild {guild_id} (data.servers strings)")
                        # Create a minimal server object
                        return {
                            "server_id": server_id,
                            "name": f"Server {server_id}",  # Default name
                            "platform": "unknown"  # Default platform
                        }
        
        # APPROACH 2: Check via guild.servers (legacy/traditional structure)
        if "servers" in guild:
            for server in guild["servers"]:
                if isinstance(server, dict):
                    # Handle both formatted and raw server IDs
                    srv_id = str(server.get("server_id", ""))
                    if srv_id == server_id:
                        logger.debug(f"Server {server_id} found in guild {guild_id} (servers)")
                        return server
                elif isinstance(server, str):
                    # If server is stored as a string, we need to construct a basic server object
                    srv_id = str(server)
                    if srv_id == server_id:
                        logger.debug(f"Server {server_id} found in guild {guild_id} (servers strings)")
                        # Create a minimal server object
                        return {
                            "server_id": server_id,
                            "name": f"Server {server_id}",  # Default name
                            "platform": "unknown"  # Default platform
                        }
                        
        # APPROACH 3: Last resort - check server_ids array if it exists and create minimal object
        if "server_ids" in guild and isinstance(guild["server_ids"], list):
            for srv_id in guild["server_ids"]:
                if str(srv_id) == server_id:
                    logger.debug(f"Server {server_id} found in guild {guild_id} (server_ids)")
                    # Create a minimal server object
                    return {
                        "server_id": server_id,
                        "name": f"Server {server_id}",  # Default name
                        "platform": "unknown"  # Default platform
                    }
        
        # If we reach here, the server wasn't found in any location
        logger.debug(f"Server {server_id} not found in guild {guild_id} after all checks")
        return None
        
    except Exception as e:
        logger.error(f"Error getting server by ID: {str(e)}")
        return None
        
async def get_all_servers(db, guild_id) -> List[Dict[str, Any]]:
    """Get all servers for a guild
    
    This utility retrieves all servers associated with a guild from all possible locations
    in the database, merging the results and removing duplicates.
    
    Args:
        db: Database connection
        guild_id: Discord guild ID (string or int)
        
    Returns:
        List[Dict[str, Any]]: List of server data dictionaries, empty list if none found
    """
    # Ensure guild_id is a string for consistent comparison
    guild_id = str(guild_id) if guild_id is not None else None
    
    if not guild_id:
        logger.debug("Get all servers failed: Guild ID is empty")
        return []
    
    all_servers = []
    server_ids_seen = set()  # Track seen server IDs to avoid duplicates
    
    try:
        # Query the database to get the guild
        guild = await db.guilds.find_one({"guild_id": guild_id})
        
        if not guild:
            logger.debug(f"Guild {guild_id} not found in database")
            return []
            
        # SOURCE 1: Check guild.data.servers
        if "data" in guild and isinstance(guild["data"], dict) and "servers" in guild["data"]:
            for server in guild["data"]["servers"]:
                if isinstance(server, dict) and "server_id" in server:
                    srv_id = str(server["server_id"])
                    if srv_id not in server_ids_seen:
                        server_ids_seen.add(srv_id)
                        all_servers.append(server)
                elif isinstance(server, str):
                    # If server is stored as a string, we need to construct a basic server object
                    srv_id = str(server)
                    if srv_id not in server_ids_seen:
                        server_ids_seen.add(srv_id)
                        # Create a minimal server object
                        all_servers.append({
                            "server_id": srv_id,
                            "name": f"Server {srv_id}",  # Default name
                            "platform": "unknown"  # Default platform
                        })
        
        # SOURCE 2: Check guild.servers
        if "servers" in guild:
            for server in guild["servers"]:
                if isinstance(server, dict) and "server_id" in server:
                    srv_id = str(server["server_id"])
                    if srv_id not in server_ids_seen:
                        server_ids_seen.add(srv_id)
                        all_servers.append(server)
                elif isinstance(server, str):
                    # If server is stored as a string, we need to construct a basic server object
                    srv_id = str(server)
                    if srv_id not in server_ids_seen:
                        server_ids_seen.add(srv_id)
                        # Create a minimal server object
                        all_servers.append({
                            "server_id": srv_id,
                            "name": f"Server {srv_id}",  # Default name
                            "platform": "unknown"  # Default platform
                        })
        
        # SOURCE 3: Check server_ids array
        if "server_ids" in guild and isinstance(guild["server_ids"], list):
            for srv_id in guild["server_ids"]:
                srv_id = str(srv_id)
                if srv_id not in server_ids_seen:
                    server_ids_seen.add(srv_id)
                    # Create a minimal server object
                    all_servers.append({
                        "server_id": srv_id,
                        "name": f"Server {srv_id}",  # Default name
                        "platform": "unknown"  # Default platform
                    })
        
        logger.debug(f"Found {len(all_servers)} servers for guild {guild_id}")
        return all_servers
        
    except Exception as e:
        logger.error(f"Error getting all servers: {str(e)}")
        return []
        
async def validate_server_config(db, guild_id, server_id) -> Dict[str, Any]:
    """Validate that a server configuration has all required fields
    
    This utility checks if a server exists and has all required fields properly configured.
    It returns a dictionary with the validation results and any missing fields.
    
    Args:
        db: Database connection
        guild_id: Discord guild ID (string or int)
        server_id: Server ID to check (string or int)
        
    Returns:
        Dict[str, Any]: Validation results containing:
            - valid (bool): Whether the server exists and is properly configured
            - exists (bool): Whether the server exists at all
            - server (Dict or None): The server data if found
            - missing_fields (List[str]): List of missing required fields
            - error (str or None): Error message if any occurred
    """
    result = {
        "valid": False,
        "exists": False,
        "server": None,
        "missing_fields": [],
        "error": None
    }
    
    try:
        # First check if the server exists
        server = await get_server_by_id(db, guild_id, server_id)
        
        if not server:
            result["error"] = f"Server {server_id} not found for guild {guild_id}"
            return result
            
        # Server exists
        result["exists"] = True
        result["server"] = server
        
        # Check for required fields
        required_fields = ["server_id", "name"]
        
        for field in required_fields:
            if field not in server or not server[field]:
                result["missing_fields"].append(field)
        
        # Check for recommended fields
        recommended_fields = ["platform", "description"]
        for field in recommended_fields:
            if field not in server or not server[field]:
                logger.debug(f"Server {server_id} missing recommended field: {field}")
        
        # Server is valid if it has all required fields
        result["valid"] = len(result["missing_fields"]) == 0
        
        return result
        
    except Exception as e:
        error_msg = f"Error validating server configuration: {str(e)}"
        logger.error(error_msg)
        result["error"] = error_msg
        return result