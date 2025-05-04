"""
Test server validation utility functions

This script tests the improved server validation utilities in utils/server_utils.py
with various inputs to ensure they handle all edge cases correctly.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockDB:
    """Mock database for testing"""
    
    def __init__(self):
        """Initialize mock database with guilds collection"""
        self.guilds = self  # Make guilds attribute point to self for chaining
    
    async def find_one(self, query):
        """Mock find_one method that returns test data"""
        if 'guild_id' in query and query['guild_id'] == '123456789':
            # Return a mock guild with different server storage formats
            return {
                "guild_id": "123456789",
                "name": "Test Guild",
                # Format 1: Traditional servers array with objects
                "servers": [
                    {
                        "server_id": "1001",
                        "name": "Server 1001",
                        "platform": "steam"
                    },
                    {
                        "server_id": "1002",
                        "name": "Server 1002",
                        "platform": "xbox"
                    }
                ],
                # Format 2: Data object with servers
                "data": {
                    "servers": [
                        {
                            "server_id": "2001",
                            "name": "Server 2001",
                            "platform": "psn"
                        },
                        "3001"  # Format 3: Simple string server ID
                    ]
                },
                # Format 4: Simple array of server IDs
                "server_ids": ["4001", "4002"]
            }
        return None

async def test_check_server_exists():
    """Test check_server_exists function with various inputs"""
    from utils.server_utils import check_server_exists
    
    db = MockDB()
    guild_id = "123456789"
    
    # Test with server from format 1 (regular servers array)
    result1 = await check_server_exists(db, guild_id, "1001")
    logger.info(f"Server 1001 exists: {result1}")
    
    # Test with server from format 2 (data.servers array)
    result2 = await check_server_exists(db, guild_id, "2001")
    logger.info(f"Server 2001 exists: {result2}")
    
    # Test with server from format 3 (string ID in data.servers)
    result3 = await check_server_exists(db, guild_id, "3001")
    logger.info(f"Server 3001 exists: {result3}")
    
    # Test with server from format 4 (server_ids array)
    result4 = await check_server_exists(db, guild_id, "4001")
    logger.info(f"Server 4001 exists: {result4}")
    
    # Test with non-existent server
    result5 = await check_server_exists(db, guild_id, "9999")
    logger.info(f"Server 9999 exists: {result5}")
    
    # Test with None values
    result6 = await check_server_exists(db, guild_id, None)
    logger.info(f"Server None exists: {result6}")
    
    # Test with non-existent guild
    result7 = await check_server_exists(db, "999999", "1001")
    logger.info(f"Server 1001 in guild 999999 exists: {result7}")
    
    # Test with numeric server ID (should be converted to string)
    result8 = await check_server_exists(db, guild_id, 1001)
    logger.info(f"Server 1001 (numeric) exists: {result8}")

async def test_get_server_by_id():
    """Test get_server_by_id function with various inputs"""
    from utils.server_utils import get_server_by_id
    
    db = MockDB()
    guild_id = "123456789"
    
    # Test with server from format 1 (regular servers array)
    result1 = await get_server_by_id(db, guild_id, "1001")
    logger.info(f"Server 1001 data: {result1}")
    
    # Test with server from format 2 (data.servers array)
    result2 = await get_server_by_id(db, guild_id, "2001")
    logger.info(f"Server 2001 data: {result2}")
    
    # Test with server from format 3 (string ID in data.servers)
    result3 = await get_server_by_id(db, guild_id, "3001")
    logger.info(f"Server 3001 data: {result3}")
    
    # Test with server from format 4 (server_ids array)
    result4 = await get_server_by_id(db, guild_id, "4001")
    logger.info(f"Server 4001 data: {result4}")
    
    # Test with non-existent server
    result5 = await get_server_by_id(db, guild_id, "9999")
    logger.info(f"Server 9999 data: {result5}")

async def test_get_all_servers():
    """Test get_all_servers function"""
    from utils.server_utils import get_all_servers
    
    db = MockDB()
    guild_id = "123456789"
    
    # Get all servers for the guild
    servers = await get_all_servers(db, guild_id)
    logger.info(f"Found {len(servers)} servers for guild {guild_id}")
    
    # Print server IDs
    server_ids = [server.get("server_id", "unknown") for server in servers]
    logger.info(f"Server IDs: {server_ids}")
    
    # Test with non-existent guild
    servers2 = await get_all_servers(db, "999999")
    logger.info(f"Found {len(servers2)} servers for non-existent guild")

async def test_validate_server_config():
    """Test validate_server_config function"""
    from utils.server_utils import validate_server_config
    
    db = MockDB()
    guild_id = "123456789"
    
    # Test with valid server
    result1 = await validate_server_config(db, guild_id, "1001")
    logger.info(f"Server 1001 validation: valid={result1['valid']}, fields={result1['missing_fields']}")
    
    # Test with string-only server that should be missing fields
    result2 = await validate_server_config(db, guild_id, "3001")
    logger.info(f"Server 3001 validation: valid={result2['valid']}, fields={result2['missing_fields']}")
    
    # Test with non-existent server
    result3 = await validate_server_config(db, guild_id, "9999")
    logger.info(f"Server 9999 validation: exists={result3['exists']}, error={result3['error']}")

async def main():
    """Run all tests"""
    logger.info("Testing server validation utilities...")
    
    # Run test functions
    await test_check_server_exists()
    logger.info("-" * 50)
    
    await test_get_server_by_id()
    logger.info("-" * 50)
    
    await test_get_all_servers()
    logger.info("-" * 50)
    
    await test_validate_server_config()
    logger.info("-" * 50)
    
    logger.info("All tests completed")

if __name__ == "__main__":
    asyncio.run(main())