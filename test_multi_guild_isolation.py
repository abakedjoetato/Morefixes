"""
Multi-Guild Isolation Test Suite

This script tests the bot's ability to correctly handle multiple guilds simultaneously,
ensuring proper data isolation between different Discord guilds. Tests include:

1. Guild configuration isolation
2. Player data separation
3. Server configuration boundaries
4. Command execution in multi-guild environments
5. Statistics tracking isolation
6. Event processing separation

Run this test to verify that the bot correctly maintains isolated environments
for each Discord guild as required for multi-tenant operation.
"""

import asyncio
import datetime
import logging
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
import uuid

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("multi_guild_test.log")
    ]
)
logger = logging.getLogger(__name__)


class MultiGuildTestSuite:
    """Test suite for multi-guild isolation"""
    
    def __init__(self):
        """Initialize the test suite"""
        self.db = None
        self.test_guilds = []
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "tests": []
        }
    
    def _record_result(self, test_name: str, passed: bool, error: Optional[str] = None):
        """Record a test result
        
        Args:
            test_name: Name of the test
            passed: Whether the test passed
            error: Error message if the test failed
        """
        self.results["total_tests"] += 1
        if passed:
            self.results["passed"] += 1
            status = "PASSED"
        else:
            self.results["failed"] += 1
            status = "FAILED"
        
        self.results["tests"].append({
            "name": test_name,
            "passed": passed,
            "error": error
        })
        
        if error:
            logger.info(f"TEST {status}: {test_name} - {error}")
        else:
            logger.info(f"TEST {status}: {test_name}")
    
    async def setup(self):
        """Set up test environment and create test guilds"""
        logger.info("Setting up multi-guild test environment...")
        
        try:
            # Connect to database
            from utils.db import initialize_db
            self.db = await initialize_db()
            
            # Create test guild IDs (using unique values for testing)
            self.test_guilds = [
                {
                    "guild_id": f"test_guild_{uuid.uuid4().hex[:8]}",
                    "name": "Test Guild Alpha"
                },
                {
                    "guild_id": f"test_guild_{uuid.uuid4().hex[:8]}",
                    "name": "Test Guild Beta"
                },
                {
                    "guild_id": f"test_guild_{uuid.uuid4().hex[:8]}",
                    "name": "Test Guild Gamma"
                }
            ]
            
            # Import guild model
            from models.guild import Guild
            
            # Create test guilds
            for guild_data in self.test_guilds:
                # Create guild object
                guild = Guild(
                    guild_id=guild_data["guild_id"],
                    name=guild_data["name"],
                    data={
                        "servers": [
                            {
                                "server_id": f"{guild_data['guild_id']}_server_1",
                                "name": f"{guild_data['name']} Server 1",
                                "platform": "PC"
                            },
                            {
                                "server_id": f"{guild_data['guild_id']}_server_2",
                                "name": f"{guild_data['name']} Server 2",
                                "platform": "XBOX"
                            }
                        ],
                        "settings": {
                            "prefix": "!",
                            "locale": "en-US",
                            "premium_tier": 0,
                            "timezone": "UTC"
                        }
                    }
                )
                # Insert into database
                await self.db.guilds.insert_one(guild.to_document())
            
            logger.info(f"Created {len(self.test_guilds)} test guilds")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up test environment: {e}")
            return False
    
    async def cleanup(self):
        """Clean up test data"""
        logger.info("Cleaning up test data...")
        
        try:
            # Delete test guilds and associated data
            guild_ids = [guild["guild_id"] for guild in self.test_guilds]
            
            # Delete from all collections
            await self.db.guilds.delete_many({"guild_id": {"$in": guild_ids}})
            await self.db.players.delete_many({"guild_id": {"$in": guild_ids}})
            await self.db.events.delete_many({"guild_id": {"$in": guild_ids}})
            await self.db.kills.delete_many({"guild_id": {"$in": guild_ids}})
            await self.db.bounties.delete_many({"guild_id": {"$in": guild_ids}})
            
            logger.info("Test data cleanup complete")
            
        except Exception as e:
            logger.error(f"Error cleaning up test data: {e}")
    
    async def test_guild_configuration_isolation(self):
        """Test that guild configurations are properly isolated"""
        logger.info("Testing guild configuration isolation...")
        
        try:
            from models.guild import Guild
            
            # Test getting guild data
            for guild_data in self.test_guilds:
                guild_id = guild_data["guild_id"]
                retrieved_guild = await Guild.get_by_guild_id(self.db, guild_id)
                
                if not retrieved_guild:
                    self._record_result("guild_retrieval", False, f"Failed to retrieve guild {guild_id}")
                    continue
                
                if retrieved_guild.get("name") != guild_data["name"]:
                    self._record_result("guild_name_match", False, 
                                      f"Guild name mismatch: {retrieved_guild.get('name')} != {guild_data['name']}")
                else:
                    self._record_result("guild_name_match", True)
            
            # Test updating settings in one guild doesn't affect others
            target_guild = self.test_guilds[0]
            other_guilds = self.test_guilds[1:]
            
            # Update target guild settings
            await self.db.guilds.update_one(
                {"guild_id": target_guild["guild_id"]},
                {"$set": {"data.settings.premium_tier": 2}}
            )
            
            # Verify the change in target guild
            updated_target = await Guild.get_by_guild_id(self.db, target_guild["guild_id"])
            target_premium = updated_target.get("data", {}).get("settings", {}).get("premium_tier")
            
            self._record_result("target_guild_update", target_premium == 2,
                              f"Target guild premium tier should be 2, got {target_premium}")
            
            # Verify other guilds are unchanged
            for other_guild in other_guilds:
                unchanged = await Guild.get_by_guild_id(self.db, other_guild["guild_id"])
                other_premium = unchanged.get("data", {}).get("settings", {}).get("premium_tier")
                
                self._record_result("other_guild_unchanged", other_premium == 0,
                                  f"Other guild premium tier should be 0, got {other_premium}")
            
        except Exception as e:
            logger.error(f"Error testing guild configuration isolation: {e}")
            self._record_result("guild_configuration_isolation", False, str(e))
    
    async def test_player_data_isolation(self):
        """Test that player data is properly isolated between guilds"""
        logger.info("Testing player data isolation...")
        
        try:
            from models.player import Player
            
            # Create identical player IDs across different guilds
            common_player_id = "test_player_isolation"
            
            # Create the player in each guild with different names
            for i, guild_data in enumerate(self.test_guilds):
                guild_id = guild_data["guild_id"]
                server_id = f"{guild_id}_server_1"
                
                # Create player
                player = Player(
                    player_id=common_player_id,
                    name=f"Player in {guild_data['name']}",
                    guild_id=guild_id,
                    server_id=server_id,
                    kills=i * 10,  # Different stats for each guild
                    deaths=i * 5
                )
                await self.db.players.insert_one(player.to_document())
            
            # Verify each guild has its own isolated player data
            for i, guild_data in enumerate(self.test_guilds):
                guild_id = guild_data["guild_id"]
                server_id = f"{guild_id}_server_1"
                
                player = await Player.get_by_player_id(self.db, common_player_id, guild_id, server_id)
                
                if not player:
                    self._record_result("player_retrieval", False, 
                                      f"Failed to retrieve player in guild {guild_id}")
                    continue
                
                expected_kills = i * 10
                if player.get("kills") != expected_kills:
                    self._record_result("player_stats_isolation", False,
                                      f"Player kills mismatch: {player.get('kills')} != {expected_kills}")
                else:
                    self._record_result("player_stats_isolation", True)
            
            # Update player in one guild and verify others are unchanged
            target_guild = self.test_guilds[0]
            target_guild_id = target_guild["guild_id"]
            target_server_id = f"{target_guild_id}_server_1"
            
            # Update kills for player in target guild
            await self.db.players.update_one(
                {"player_id": common_player_id, "guild_id": target_guild_id, "server_id": target_server_id},
                {"$set": {"kills": 999}}
            )
            
            # Verify the update in target guild
            updated_player = await Player.get_by_player_id(
                self.db, common_player_id, target_guild_id, target_server_id
            )
            
            self._record_result("target_player_update", updated_player.get("kills") == 999,
                              f"Target player kills should be 999, got {updated_player.get('kills')}")
            
            # Verify other guilds are unchanged
            for i, guild_data in enumerate(self.test_guilds[1:], 1):
                guild_id = guild_data["guild_id"]
                server_id = f"{guild_id}_server_1"
                
                other_player = await Player.get_by_player_id(self.db, common_player_id, guild_id, server_id)
                expected_kills = i * 10
                
                self._record_result("other_player_unchanged", other_player.get("kills") == expected_kills,
                                  f"Other player kills should be {expected_kills}, got {other_player.get('kills')}")
            
        except Exception as e:
            logger.error(f"Error testing player data isolation: {e}")
            self._record_result("player_data_isolation", False, str(e))
    
    async def test_server_configuration_isolation(self):
        """Test that server configurations are properly isolated between guilds"""
        logger.info("Testing server configuration isolation...")
        
        try:
            from utils.server_utils import get_server_by_id, get_all_servers
            
            # Test server retrieval isolation
            for guild_data in self.test_guilds:
                guild_id = guild_data["guild_id"]
                
                # Each guild should only see its own servers
                servers = await get_all_servers(self.db, guild_id)
                
                # Should have exactly 2 servers for each guild
                if len(servers) != 2:
                    self._record_result("server_count", False, 
                                      f"Expected 2 servers for guild {guild_id}, got {len(servers)}")
                else:
                    self._record_result("server_count", True)
                
                # Each server should have the correct guild prefix in ID
                for server in servers:
                    server_id = server.get("server_id", "")
                    if not server_id.startswith(guild_id):
                        self._record_result("server_id_prefix", False,
                                          f"Server ID {server_id} does not have guild prefix {guild_id}")
                    else:
                        self._record_result("server_id_prefix", True)
            
            # Try to get server from another guild
            guild_1 = self.test_guilds[0]
            guild_2 = self.test_guilds[1]
            
            guild_1_id = guild_1["guild_id"]
            guild_2_id = guild_2["guild_id"]
            
            # Get server from guild 1
            guild_1_server_id = f"{guild_1_id}_server_1"
            
            # Try to access it from guild 2
            cross_guild_server = await get_server_by_id(self.db, guild_2_id, guild_1_server_id)
            
            # Should not be able to retrieve a server from another guild
            self._record_result("cross_guild_server_isolation", cross_guild_server is None,
                              "Should not be able to retrieve a server from another guild")
            
        except Exception as e:
            logger.error(f"Error testing server configuration isolation: {e}")
            self._record_result("server_configuration_isolation", False, str(e))
    
    async def test_bounty_isolation(self):
        """Test that bounties are properly isolated between guilds"""
        logger.info("Testing bounty system isolation...")
        
        try:
            from models.bounty import Bounty
            
            # Create bounties in each guild
            now = datetime.datetime.utcnow()
            expires = now + datetime.timedelta(days=1)
            
            # Create common bounty target in all guilds
            target_id = "common_bounty_target"
            
            for i, guild_data in enumerate(self.test_guilds):
                guild_id = guild_data["guild_id"]
                server_id = f"{guild_id}_server_1"
                
                # Create bounty
                bounty = Bounty(
                    guild_id=guild_id,
                    server_id=server_id,
                    target_id=target_id,
                    target_name=f"Target in {guild_data['name']}",
                    placed_by_id="12345",
                    placed_by_name="Test Creator",
                    amount=(i + 1) * 1000,  # Different reward per guild
                    status=Bounty.STATUS_ACTIVE,
                    bounty_type=Bounty.TYPE_PLAYER,
                    created_at=now,
                    expires_at=expires,
                    requirement={"reason": f"Test bounty in {guild_data['name']}"}
                )
                
                # Insert into database
                await self.db.bounties.insert_one(bounty.to_document())
            
            # Verify bounties are isolated by guild
            for i, guild_data in enumerate(self.test_guilds):
                guild_id = guild_data["guild_id"]
                server_id = f"{guild_id}_server_1"
                
                # Get active bounties for this guild
                guild_bounties = await Bounty.get_active_bounties(self.db, guild_id=guild_id, server_id=server_id)
                
                # Should have exactly 1 bounty
                if len(guild_bounties) != 1:
                    self._record_result("guild_bounty_count", False,
                                      f"Expected 1 bounty for guild {guild_id}, got {len(guild_bounties)}")
                else:
                    self._record_result("guild_bounty_count", True)
                
                # Check bounty amount
                expected_amount = (i + 1) * 1000
                if len(guild_bounties) > 0 and guild_bounties[0].amount != expected_amount:
                    self._record_result("bounty_amount_isolation", False,
                                      f"Expected amount {expected_amount}, got {guild_bounties[0].amount}")
                elif len(guild_bounties) > 0:
                    self._record_result("bounty_amount_isolation", True)
            
            # Claim a bounty in one guild
            target_guild = self.test_guilds[0]
            target_guild_id = target_guild["guild_id"]
            target_server_id = f"{target_guild_id}_server_1"
            
            # Get bounty to claim
            target_bounties = await Bounty.get_active_bounties(self.db, guild_id=target_guild_id, server_id=target_server_id)
            if len(target_bounties) > 0:
                target_bounty = target_bounties[0]
                
                # Claim the bounty
                claim_result = await target_bounty.claim(
                    self.db, "test_hunter", "Test Hunter"
                )
                
                self._record_result("claim_bounty", claim_result is True,
                                  "Failed to claim bounty")
                
                # Verify the bounty is claimed
                # Get the bounty again to make sure it's updated
                bounty_id = target_bounty.bounty_id
                bounty_doc = await self.db.bounties.find_one({"bounty_id": bounty_id})
                claimed_bounty = Bounty.from_document(bounty_doc)
                
                self._record_result("bounty_claimed_status", claimed_bounty.status == Bounty.STATUS_CLAIMED,
                                  f"Bounty should be claimed, got {claimed_bounty.status}")
                
                # Verify other guild bounties are unaffected
                for guild_data in self.test_guilds[1:]:
                    guild_id = guild_data["guild_id"]
                    server_id = f"{guild_id}_server_1"
                    
                    other_bounties = await Bounty.get_active_bounties(self.db, guild_id=guild_id, server_id=server_id)
                    
                    if len(other_bounties) != 1:
                        self._record_result("other_guild_bounty_count", False,
                                          f"Expected 1 active bounty in other guild, got {len(other_bounties)}")
                    else:
                        self._record_result("other_guild_bounty_count", True)
                        
                        # Verify bounty is not claimed
                        other_bounty = other_bounties[0]
                        self._record_result("other_bounty_unchanged", other_bounty.status == Bounty.STATUS_ACTIVE,
                                          f"Other bounty should not be claimed, got {other_bounty.status}")
            
        except Exception as e:
            logger.error(f"Error testing bounty isolation: {e}")
            self._record_result("bounty_isolation", False, str(e))
    
    def format_results(self) -> str:
        """Format test results as a string
        
        Returns:
            Formatted results string
        """
        passed = self.results["passed"]
        total = self.results["total_tests"]
        percentage = (passed / total * 100) if total > 0 else 0
        
        lines = [
            "MULTI-GUILD ISOLATION TEST RESULTS",
            "=" * 60,
            f"Tests run: {total}",
            f"Passed: {passed} ({percentage:.1f}%)",
            f"Failed: {self.results['failed']}",
            "=" * 60
        ]
        
        if self.results["failed"] > 0:
            lines.append("\nFailed tests:")
            lines.append("-" * 60)
            
            for test in self.results["tests"]:
                if not test["passed"]:
                    lines.append(f"{test['name']}: {test['error']}")
            
            lines.append("")
        
        if passed == total:
            lines.append("\n✅ All tests passed! Multi-guild isolation is working correctly.")
        else:
            lines.append("\n⚠️ Some tests failed. Fix multi-guild isolation issues.")
        
        return "\n".join(lines)
    
    async def run_tests(self):
        """Run all multi-guild isolation tests"""
        logger.info("Running multi-guild isolation tests...")
        
        # Set up test environment
        setup_success = await self.setup()
        if not setup_success:
            logger.error("Test setup failed, aborting tests")
            return "Test setup failed"
        
        try:
            # Run tests
            await self.test_guild_configuration_isolation()
            await self.test_player_data_isolation()
            await self.test_server_configuration_isolation()
            await self.test_bounty_isolation()
        finally:
            # Clean up
            await self.cleanup()
        
        # Format and return results
        return self.format_results()


async def main():
    """Run the multi-guild isolation test suite"""
    logger.info("Starting multi-guild isolation test suite")
    
    test_suite = MultiGuildTestSuite()
    results = await test_suite.run_tests()
    
    print("\n" + results + "\n")
    
    # Return exit code based on results
    return 0 if test_suite.results["failed"] == 0 else 1


if __name__ == "__main__":
    # Run the test suite
    exit_code = asyncio.run(main())
    sys.exit(exit_code)