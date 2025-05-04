"""
Simple test for circular import fixes
"""
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test importing models"""
    logger.info("Testing imports for circular reference issues...")
    
    # Test Event model
    try:
        from models.event import Event, Connection
        logger.info("✅ Successfully imported Event and Connection models")
    except Exception as e:
        logger.error(f"❌ Failed to import Event model: {e}")
    
    # Test Faction model
    try:
        from models.faction import Faction
        logger.info("✅ Successfully imported Faction model")
    except Exception as e:
        logger.error(f"❌ Failed to import Faction model: {e}")
    
    # Test Player model
    try:
        from models.player import Player
        logger.info("✅ Successfully imported Player model")
    except Exception as e:
        logger.error(f"❌ Failed to import Player model: {e}")
    
    # Test Guild model
    try:
        from models.guild import Guild
        logger.info("✅ Successfully imported Guild model")
    except Exception as e:
        logger.error(f"❌ Failed to import Guild model: {e}")
    
    logger.info("Import test completed!")

if __name__ == "__main__":
    test_imports()