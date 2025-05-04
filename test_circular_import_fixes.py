"""
Test circular import fixes

This script verifies that the model modules can be imported without circular reference errors.
"""

import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_event_model():
    """Test importing Event model"""
    try:
        from models.event import Event, Connection
        
        logger.info("✅ Successfully imported Event and Connection models")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to import Event model: {e}")
        return False

async def test_faction_model():
    """Test importing Faction model"""
    try:
        from models.faction import Faction
        
        logger.info("✅ Successfully imported Faction model")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to import Faction model: {e}")
        return False

async def test_player_model():
    """Test importing Player model"""
    try:
        from models.player import Player
        
        logger.info("✅ Successfully imported Player model")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to import Player model: {e}")
        return False

async def test_guild_model():
    """Test importing Guild model"""
    try:
        from models.guild import Guild
        
        logger.info("✅ Successfully imported Guild model")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to import Guild model: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("Testing circular import fixes...")
    
    # Test each model individually
    try:
        from models.event import Event, Connection
        logger.info("✅ Successfully imported Event and Connection models")
    except Exception as e:
        logger.error(f"❌ Failed to import Event model: {e}")
    
    try:
        from models.faction import Faction
        logger.info("✅ Successfully imported Faction model")
    except Exception as e:
        logger.error(f"❌ Failed to import Faction model: {e}")
    
    try:
        from models.player import Player
        logger.info("✅ Successfully imported Player model")
    except Exception as e:
        logger.error(f"❌ Failed to import Player model: {e}")
    
    try:
        from models.guild import Guild
        logger.info("✅ Successfully imported Guild model")
    except Exception as e:
        logger.error(f"❌ Failed to import Guild model: {e}")
    
    logger.info("Circular import test completed!")

if __name__ == "__main__":
    main()