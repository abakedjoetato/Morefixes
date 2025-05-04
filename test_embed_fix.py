import asyncio
import logging
import os
import sys
from datetime import datetime

import discord
from discord.ext import commands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our EmbedBuilder
from utils.embed_builder import EmbedBuilder

async def test_embeds():
    """Test all embed creation methods to ensure they work properly."""
    logger.info("Testing embed creation methods...")
    
    # Test create_error_embed
    try:
        error_embed = await EmbedBuilder.create_error_embed(
            title="Test Error",
            description="This is a test error embed"
        )
        logger.info("create_error_embed works!")
        assert error_embed.color.value == EmbedBuilder.COLORS["error"]
        assert error_embed.title == "Test Error"
    except Exception as e:
        logger.error(f"Error testing create_error_embed: {e}")
        return False
    
    # Test create_success_embed
    try:
        success_embed = await EmbedBuilder.create_success_embed(
            title="Test Success",
            description="This is a test success embed"
        )
        logger.info("create_success_embed works!")
        assert success_embed.color.value == EmbedBuilder.COLORS["success"]
        assert success_embed.title == "Test Success"
    except Exception as e:
        logger.error(f"Error testing create_success_embed: {e}")
        return False
    
    # Test create_base_embed
    try:
        base_embed = await EmbedBuilder.create_base_embed(
            title="Test Base",
            description="This is a test base embed"
        )
        logger.info("create_base_embed works!")
        assert base_embed.color.value == EmbedBuilder.COLORS["primary"]
        assert base_embed.title == "Test Base"
    except Exception as e:
        logger.error(f"Error testing create_base_embed: {e}")
        return False
        
    # Test create_standard_embed
    try:
        standard_embed = await EmbedBuilder.create_standard_embed(
            title="Test Standard",
            description="This is a test standard embed"
        )
        logger.info("create_standard_embed works!")
        assert standard_embed.color.value == EmbedBuilder.COLORS["primary"]
        assert standard_embed.title == "Test Standard"
    except Exception as e:
        logger.error(f"Error testing create_standard_embed: {e}")
        return False
    
    # Test create_info_embed
    try:
        info_embed = await EmbedBuilder.create_info_embed(
            title="Test Info",
            description="This is a test info embed"
        )
        logger.info("create_info_embed works!")
        assert info_embed.color.value == EmbedBuilder.COLORS["info"]
        assert info_embed.title == "Test Info"
    except Exception as e:
        logger.error(f"Error testing create_info_embed: {e}")
        return False
    
    # Test create_warning_embed
    try:
        warning_embed = await EmbedBuilder.create_warning_embed(
            title="Test Warning",
            description="This is a test warning embed"
        )
        logger.info("create_warning_embed works!")
        assert warning_embed.color.value == EmbedBuilder.COLORS["warning"]
        assert warning_embed.title == "Test Warning"
    except Exception as e:
        logger.error(f"Error testing create_warning_embed: {e}")
        return False
    
    logger.info("All embed tests passed successfully!")
    return True

def run_tests():
    """Run all the tests."""
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(test_embeds())
    return result

if __name__ == "__main__":
    success = run_tests()
    if success:
        logger.info("All embed creation methods now work correctly!")
        sys.exit(0)
    else:
        logger.error("Some embed creation methods are still not working!")
        sys.exit(1)