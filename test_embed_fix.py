import asyncio
import logging
import os
import sys
from datetime import datetime

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
    
    # Test basic embed methods
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
    
    # Test specialized embed methods
    # Test create_stats_embed
    try:
        stats_embed = await EmbedBuilder.create_stats_embed(
            player_name="Test Player",
            stats={"kills": 10, "deaths": 5, "kd_ratio": 2.0, "favorite_weapon": "Sword"}
        )
        logger.info("create_stats_embed works!")
        assert "Test Player" in stats_embed.title
    except Exception as e:
        logger.error(f"Error testing create_stats_embed: {e}")
        return False
    
    # Test create_server_stats_embed
    try:
        server_stats_embed = await EmbedBuilder.create_server_stats_embed(
            server_name="Test Server",
            stats={"players": 100, "kills": 1000, "average_kd": 1.5}
        )
        logger.info("create_server_stats_embed works!")
        assert "Test Server" in server_stats_embed.title
    except Exception as e:
        logger.error(f"Error testing create_server_stats_embed: {e}")
        return False
    
    # Test create_progress_embed
    try:
        progress_embed = await EmbedBuilder.create_progress_embed(
            title="Test Progress",
            description="Testing progress bar",
            progress=0.75
        )
        logger.info("create_progress_embed works!")
        assert "Test Progress" == progress_embed.title
        assert "█" in progress_embed.description
    except Exception as e:
        logger.error(f"Error testing create_progress_embed: {e}")
        return False
    
    # Test create_kill_embed
    try:
        kill_embed = await EmbedBuilder.create_kill_embed(
            killer_name="Player1",
            victim_name="Player2",
            weapon="Sword",
            distance=10.5
        )
        logger.info("create_kill_embed works!")
        assert "Player1" in kill_embed.title
        assert "Player2" in kill_embed.title
    except Exception as e:
        logger.error(f"Error testing create_kill_embed: {e}")
        return False
    
    # Test create_event_embed
    try:
        event_embed = await EmbedBuilder.create_event_embed(
            event_name="Test Event",
            description="This is a test event",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow()
        )
        logger.info("create_event_embed works!")
        assert "Test Event" in event_embed.title
    except Exception as e:
        logger.error(f"Error testing create_event_embed: {e}")
        return False
    
    # Test create_error_error_embed
    try:
        error_error_embed = await EmbedBuilder.create_error_error_embed(
            title="Critical Test Error",
            description="This is a critical test error"
        )
        logger.info("create_error_error_embed works!")
        assert "Critical Test Error" == error_error_embed.title
        assert error_error_embed.color.value == 0xFF0000  # Bright red
    except Exception as e:
        logger.error(f"Error testing create_error_error_embed: {e}")
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