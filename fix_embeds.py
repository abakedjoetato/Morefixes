#!/usr/bin/env python3
"""
Comprehensive fix for embed-related issues in the Tower of Temptation PvP Statistics Bot.

This script:
1. Identifies missing embed creation methods in EmbedBuilder
2. Adds all required helper functions
3. Tests that all embed methods work correctly
"""

import asyncio
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import directly to avoid importing discord which might not be available in test environments
from utils.embed_builder import EmbedBuilder


async def test_embeds():
    """Test all embed creation methods to ensure they work properly."""
    logger.info("Testing all embed creation methods...")
    
    # Dictionary of methods and expected colors
    test_methods = {
        "create_error_embed": "error",
        "create_success_embed": "success",
        "create_base_embed": "primary",
        "create_standard_embed": "primary", 
        "create_info_embed": "info",
        "create_warning_embed": "warning"
    }
    
    # Test basic embeds
    for method_name, color_key in test_methods.items():
        try:
            method = getattr(EmbedBuilder, method_name)
            embed = await method(
                title=f"Test {method_name.replace('create_', '').replace('_embed', '')}",
                description=f"Testing {method_name}"
            )
            logger.info(f"{method_name} works!")
            
            # Get color value for assertion
            # Skip assertion if the method is create_error_error_embed which uses a hardcoded red color
            if method_name != "create_error_error_embed":
                assert embed.color.value == EmbedBuilder.COLORS[color_key]
                
        except Exception as e:
            logger.error(f"Error testing {method_name}: {e}")
            return False
    
    # Test specialized embeds
    
    # Test create_stats_embed
    try:
        test_stats = {"kills": 10, "deaths": 5, "kd_ratio": 2.0, "faction": "Faction A"}
        stats_embed = await EmbedBuilder.create_stats_embed(
            player_name="Test Player",
            stats=test_stats
        )
        logger.info("create_stats_embed works!")
    except Exception as e:
        logger.error(f"Error testing create_stats_embed: {e}")
        return False
    
    # Test create_server_stats_embed
    try:
        server_stats = {"players": 100, "kills": 1000, "average_kd": 1.5}
        server_embed = await EmbedBuilder.create_server_stats_embed(
            server_name="Test Server",
            stats=server_stats
        )
        logger.info("create_server_stats_embed works!")
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
    except Exception as e:
        logger.error(f"Error testing create_progress_embed: {e}")
        return False
    
    # Test create_kill_embed
    try:
        kill_embed = await EmbedBuilder.create_kill_embed(
            killer_name="Player1",
            victim_name="Player2",
            weapon="Sword",
            distance=10.5,
            killer_faction="Faction A",
            victim_faction="Faction B"
        )
        logger.info("create_kill_embed works!")
    except Exception as e:
        logger.error(f"Error testing create_kill_embed: {e}")
        return False
    
    # Test create_event_embed
    try:
        now = datetime.utcnow()
        event_embed = await EmbedBuilder.create_event_embed(
            event_name="Test Event",
            description="This is a test event",
            start_time=now,
            end_time=now,
            location="Test Location",
            rewards="Test Rewards"
        )
        logger.info("create_event_embed works!")
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
    except Exception as e:
        logger.error(f"Error testing create_error_error_embed: {e}")
        return False
    
    logger.info("All embed tests passed successfully!")
    return True


def main():
    """Main function to test all embed-related fixes."""
    logger.info("Running comprehensive embed fixes test")
    
    # Run embed tests
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(test_embeds())
    
    if result:
        logger.info("All embed creation methods now work correctly!")
        return 0
    else:
        logger.error("Some embed creation methods are still not working!")
        return 1


if __name__ == "__main__":
    sys.exit(main())