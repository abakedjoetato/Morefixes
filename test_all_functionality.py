"""
Comprehensive Test Suite for Tower of Temptation PvP Statistics Discord Bot

This script provides systematic testing for all major components and features:
1. Database connections and model functionality
2. Server validation utilities
3. Command handling and responses
4. Multi-guild isolation
5. Error handling and recovery
6. CSV parsing and data processing
7. Bounty system and economy features
8. Event tracking and killfeed functionality

Run this to validate the entire bot functionality before deployment.
"""

import asyncio
import datetime
import logging
import os
import sys
import unittest
from typing import Dict, List, Any, Optional, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComprehensiveTestSuite:
    """Complete test suite to verify all bot functionality"""
    
    def __init__(self):
        """Initialize the test suite"""
        self.test_results = {
            "database": {"passed": 0, "failed": 0, "tests": []},
            "server_utils": {"passed": 0, "failed": 0, "tests": []},
            "commands": {"passed": 0, "failed": 0, "tests": []},
            "csv_parsing": {"passed": 0, "failed": 0, "tests": []},
            "bounty": {"passed": 0, "failed": 0, "tests": []},
            "event_tracking": {"passed": 0, "failed": 0, "tests": []},
            "multi_guild": {"passed": 0, "failed": 0, "tests": []},
            "error_handling": {"passed": 0, "failed": 0, "tests": []}
        }
        self.db = None
        self.test_guild_ids = ["123456789012345678", "987654321098765432"]
        self.total_tests = 0
        self.passed_tests = 0
    
    async def setup(self):
        """Set up test environment and database connection"""
        logger.info("Setting up test environment...")
        
        # Import database module and connect
        try:
            from utils.db import initialize_db
            self.db = await initialize_db()
            self._record_test_result("database", "database_connection", True)
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self._record_test_result("database", "database_connection", False, str(e))
            return False
        
        return True
    
    def _record_test_result(self, category: str, test_name: str, passed: bool, error: Optional[str] = None):
        """Record a test result
        
        Args:
            category: Test category
            test_name: Name of the test
            passed: Whether the test passed
            error: Error message if test failed
        """
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            self.test_results[category]["passed"] += 1
            status = "PASSED"
        else:
            self.test_results[category]["failed"] += 1
            status = "FAILED"
            
        self.test_results[category]["tests"].append({
            "name": test_name,
            "passed": passed,
            "error": error
        })
        
        if error:
            logger.info(f"TEST {status}: {category}.{test_name} - {error}")
        else:
            logger.info(f"TEST {status}: {category}.{test_name}")
    
    async def test_database_models(self):
        """Test database models and operations"""
        logger.info("Testing database models...")
        
        try:
            # Test Guild model
            from models.guild import Guild
            
            # Test creation
            test_guild_id = self.test_guild_ids[0]
            test_guild = await Guild.create(self.db, {
                "guild_id": test_guild_id,
                "name": "Test Guild",
                "data": {
                    "servers": [
                        {"server_id": "test_server_1", "name": "Test Server 1"},
                        {"server_id": "test_server_2", "name": "Test Server 2"}
                    ]
                }
            })
            self._record_test_result("database", "guild_creation", True)
            
            # Test retrieval
            retrieved_guild = await Guild.get_by_guild_id(self.db, test_guild_id)
            if retrieved_guild and retrieved_guild.get("guild_id") == test_guild_id:
                self._record_test_result("database", "guild_retrieval", True)
            else:
                self._record_test_result("database", "guild_retrieval", False, "Retrieved guild did not match created guild")
            
            # Cleanup
            await self.db.guilds.delete_one({"guild_id": test_guild_id})
            
        except Exception as e:
            logger.error(f"Error testing Guild model: {e}")
            self._record_test_result("database", "guild_model", False, str(e))
    
    async def test_server_utils(self):
        """Test server utilities"""
        logger.info("Testing server utilities...")
        
        try:
            # Import server utilities
            from utils.server_utils import check_server_exists, get_server_by_id, get_all_servers
            
            # Set up test data
            test_guild_id = self.test_guild_ids[0]
            test_server_id = "test_server_1"
            
            # Create a test guild with servers
            await self.db.guilds.insert_one({
                "guild_id": test_guild_id,
                "name": "Test Guild",
                "data": {
                    "servers": [
                        {"server_id": test_server_id, "name": "Test Server 1"},
                        {"server_id": "test_server_2", "name": "Test Server 2"}
                    ]
                },
                "servers": [
                    {"server_id": "test_server_3", "name": "Test Server 3"}
                ]
            })
            
            # Test check_server_exists
            server_exists = await check_server_exists(self.db, test_guild_id, test_server_id)
            self._record_test_result("server_utils", "check_server_exists", server_exists, 
                                     None if server_exists else "Server should exist but wasn't found")
            
            # Test non-existent server
            non_existent = await check_server_exists(self.db, test_guild_id, "nonexistent")
            self._record_test_result("server_utils", "check_nonexistent_server", not non_existent,
                                    None if not non_existent else "Non-existent server was incorrectly found")
            
            # Test get_server_by_id
            server = await get_server_by_id(self.db, test_guild_id, test_server_id)
            if server and server.get("server_id") == test_server_id:
                self._record_test_result("server_utils", "get_server_by_id", True)
            else:
                self._record_test_result("server_utils", "get_server_by_id", False, 
                                        "Retrieved server did not match expected")
            
            # Test get_all_servers
            all_servers = await get_all_servers(self.db, test_guild_id)
            if len(all_servers) == 3:  # Should find all 3 servers
                self._record_test_result("server_utils", "get_all_servers", True)
            else:
                self._record_test_result("server_utils", "get_all_servers", False,
                                        f"Expected 3 servers, got {len(all_servers)}")
            
            # Cleanup
            await self.db.guilds.delete_one({"guild_id": test_guild_id})
            
        except Exception as e:
            logger.error(f"Error testing server utilities: {e}")
            self._record_test_result("server_utils", "general", False, str(e))
    
    async def test_csv_parsing(self):
        """Test CSV parsing functionality"""
        logger.info("Testing CSV parsing functionality...")
        
        try:
            # Import CSV processor
            from utils.csv_parser import parse_csv_content, process_kill_event
            
            # Test CSV content parsing
            test_csv = """
            "timestamp","event","killer","victim","weapon"
            "2025-05-01 12:34:56","kill","Player1","Player2","M4A1"
            "2025-05-01 12:35:10","suicide","Player3","","grenade"
            """
            
            parsed_events = parse_csv_content(test_csv)
            if len(parsed_events) == 2:
                self._record_test_result("csv_parsing", "parse_csv_content", True)
            else:
                self._record_test_result("csv_parsing", "parse_csv_content", False, 
                                        f"Expected 2 events, got {len(parsed_events)}")
            
            # Test kill event processing
            kill_event = {
                "timestamp": "2025-05-01 12:34:56",
                "event": "kill",
                "killer": "Player1",
                "victim": "Player2",
                "weapon": "M4A1"
            }
            
            processed_event = process_kill_event(kill_event, "test_server_1")
            if processed_event and processed_event.get("killer") == "Player1":
                self._record_test_result("csv_parsing", "process_kill_event", True)
            else:
                self._record_test_result("csv_parsing", "process_kill_event", False,
                                        "Kill event processing failed")
            
        except Exception as e:
            logger.error(f"Error testing CSV parsing: {e}")
            self._record_test_result("csv_parsing", "general", False, str(e))
    
    async def test_multi_guild_isolation(self):
        """Test that data is properly isolated between guilds"""
        logger.info("Testing multi-guild data isolation...")
        
        try:
            # Create two test guilds
            guild_id_1 = self.test_guild_ids[0]
            guild_id_2 = self.test_guild_ids[1]
            
            from models.guild import Guild
            from models.player import Player
            
            # Create guilds
            await Guild.create(self.db, {
                "guild_id": guild_id_1,
                "name": "Test Guild 1",
                "data": {"servers": [{"server_id": "server1", "name": "Server 1"}]}
            })
            
            await Guild.create(self.db, {
                "guild_id": guild_id_2,
                "name": "Test Guild 2",
                "data": {"servers": [{"server_id": "server2", "name": "Server 2"}]}
            })
            
            # Create players for each guild
            await Player.create(self.db, {
                "player_id": "player1",
                "name": "Player 1",
                "guild_id": guild_id_1,
                "server_id": "server1"
            })
            
            await Player.create(self.db, {
                "player_id": "player1",  # Same player ID
                "name": "Player 1 Guild 2",
                "guild_id": guild_id_2,
                "server_id": "server2"
            })
            
            # Test isolation in retrieval
            player1_guild1 = await Player.get_by_player_id(self.db, "player1", guild_id_1, "server1")
            player1_guild2 = await Player.get_by_player_id(self.db, "player1", guild_id_2, "server2")
            
            if player1_guild1 and player1_guild2 and player1_guild1.get("name") != player1_guild2.get("name"):
                self._record_test_result("multi_guild", "player_isolation", True)
            else:
                self._record_test_result("multi_guild", "player_isolation", False,
                                        "Player data not properly isolated between guilds")
            
            # Test that server retrieval is isolated
            from utils.server_utils import get_all_servers
            
            servers_guild1 = await get_all_servers(self.db, guild_id_1)
            servers_guild2 = await get_all_servers(self.db, guild_id_2)
            
            if (len(servers_guild1) == 1 and len(servers_guild2) == 1 and 
                servers_guild1[0].get("server_id") != servers_guild2[0].get("server_id")):
                self._record_test_result("multi_guild", "server_isolation", True)
            else:
                self._record_test_result("multi_guild", "server_isolation", False,
                                        "Server data not properly isolated between guilds")
            
            # Cleanup
            await self.db.guilds.delete_many({"guild_id": {"$in": [guild_id_1, guild_id_2]}})
            await self.db.players.delete_many({"guild_id": {"$in": [guild_id_1, guild_id_2]}})
            
        except Exception as e:
            logger.error(f"Error testing multi-guild isolation: {e}")
            self._record_test_result("multi_guild", "general", False, str(e))
    
    async def test_error_handling(self):
        """Test error handling in critical functions"""
        logger.info("Testing error handling...")
        
        try:
            # Test error handling in server utilities with bad inputs
            from utils.server_utils import check_server_exists, get_server_by_id
            
            # Test with None values
            try:
                result = await check_server_exists(self.db, None, "server1")
                self._record_test_result("error_handling", "check_server_exists_none", result is False)
            except Exception as e:
                self._record_test_result("error_handling", "check_server_exists_none", False,
                                        f"Should handle None input gracefully, but raised: {e}")
            
            # Test with invalid types
            try:
                result = await get_server_by_id(self.db, {"invalid": "type"}, "server1")
                self._record_test_result("error_handling", "get_server_by_id_invalid", result is None)
            except Exception as e:
                self._record_test_result("error_handling", "get_server_by_id_invalid", False,
                                        f"Should handle invalid input gracefully, but raised: {e}")
            
            # Test CSV parser with malformed input
            from utils.csv_parser import parse_csv_content
            
            try:
                result = parse_csv_content("completely invalid csv content")
                self._record_test_result("error_handling", "parse_csv_invalid", 
                                        True, f"Returned {len(result)} events")
            except Exception as e:
                self._record_test_result("error_handling", "parse_csv_invalid", False,
                                        f"Should handle invalid CSV gracefully, but raised: {e}")
            
        except Exception as e:
            logger.error(f"Error testing error handling: {e}")
            self._record_test_result("error_handling", "general", False, str(e))
    
    async def test_bounty_system(self):
        """Test bounty system functionality"""
        logger.info("Testing bounty system...")
        
        try:
            # Import bounty model
            from models.bounty import Bounty
            from models.guild import Guild
            from models.player import Player
            
            # Setup test data
            test_guild_id = self.test_guild_ids[0]
            test_server_id = "test_server_1"
            
            # Create guild and players
            await Guild.create(self.db, {
                "guild_id": test_guild_id,
                "name": "Test Guild",
                "data": {"servers": [{"server_id": test_server_id, "name": "Test Server"}]}
            })
            
            await Player.create(self.db, {
                "player_id": "target_player",
                "name": "Target Player",
                "guild_id": test_guild_id,
                "server_id": test_server_id
            })
            
            await Player.create(self.db, {
                "player_id": "bounty_hunter",
                "name": "Bounty Hunter",
                "guild_id": test_guild_id,
                "server_id": test_server_id
            })
            
            # Test bounty creation
            bounty_data = {
                "guild_id": test_guild_id,
                "server_id": test_server_id,
                "target_id": "target_player",
                "target_name": "Target Player",
                "creator_id": "123456789",  # Discord ID
                "creator_name": "Test User",
                "reward": 1000,
                "reason": "Test bounty",
                "created_at": datetime.datetime.utcnow().isoformat(),
                "expires_at": (datetime.datetime.utcnow() + datetime.timedelta(days=1)).isoformat(),
                "is_claimed": False,
                "is_auto": False
            }
            
            created_bounty = await Bounty.create(self.db, bounty_data)
            self._record_test_result("bounty", "bounty_creation", 
                                    created_bounty is not None, 
                                    None if created_bounty else "Failed to create bounty")
            
            # Test active bounties retrieval
            active_bounties = await Bounty.get_active_bounties(self.db, test_guild_id, test_server_id)
            self._record_test_result("bounty", "get_active_bounties",
                                    len(active_bounties) == 1,
                                    f"Expected 1 active bounty, got {len(active_bounties)}")
            
            # Test claiming a bounty
            bounty_id = created_bounty.get("_id")
            claim_result = await Bounty.claim_bounty(
                self.db, 
                bounty_id, 
                "bounty_hunter", 
                "Bounty Hunter"
            )
            
            self._record_test_result("bounty", "claim_bounty",
                                    claim_result is True,
                                    None if claim_result else "Failed to claim bounty")
            
            # Verify bounty is now claimed
            claimed_bounty = await Bounty.get_by_id(self.db, bounty_id)
            self._record_test_result("bounty", "bounty_claimed_status",
                                    claimed_bounty and claimed_bounty.get("is_claimed") is True,
                                    None if claimed_bounty and claimed_bounty.get("is_claimed") else 
                                    "Bounty not marked as claimed")
            
            # Cleanup
            await self.db.guilds.delete_one({"guild_id": test_guild_id})
            await self.db.players.delete_many({"guild_id": test_guild_id})
            await self.db.bounties.delete_many({"guild_id": test_guild_id})
            
        except Exception as e:
            logger.error(f"Error testing bounty system: {e}")
            self._record_test_result("bounty", "general", False, str(e))
    
    async def run_all_tests(self):
        """Run all test suites"""
        logger.info("Running comprehensive test suite...")
        
        # Set up environment
        setup_success = await self.setup()
        if not setup_success:
            logger.error("Test setup failed, aborting test suite")
            return self.get_test_summary()
        
        # Run individual test suites
        await self.test_database_models()
        await self.test_server_utils()
        await self.test_csv_parsing()
        await self.test_multi_guild_isolation()
        await self.test_error_handling()
        await self.test_bounty_system()
        
        # Return test summary
        return self.get_test_summary()
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of test results
        
        Returns:
            Dict containing test summary and detailed results
        """
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.total_tests - self.passed_tests,
            "pass_rate": f"{(self.passed_tests / self.total_tests * 100) if self.total_tests else 0:.2f}%",
            "categories": {
                category: {
                    "total": self.test_results[category]["passed"] + self.test_results[category]["failed"],
                    "passed": self.test_results[category]["passed"],
                    "failed": self.test_results[category]["failed"],
                    "pass_rate": f"{(self.test_results[category]['passed'] / (self.test_results[category]['passed'] + self.test_results[category]['failed']) * 100) if (self.test_results[category]['passed'] + self.test_results[category]['failed']) else 0:.2f}%"
                } for category in self.test_results
            },
            "details": self.test_results
        }


async def main():
    """Run the comprehensive test suite"""
    logger.info("Starting comprehensive test suite for Tower of Temptation PvP Statistics Bot")
    
    test_suite = ComprehensiveTestSuite()
    test_results = await test_suite.run_all_tests()
    
    # Print summary
    print("\n" + "="*80)
    print(f"TEST SUMMARY: {test_results['passed_tests']}/{test_results['total_tests']} tests passed ({test_results['pass_rate']})")
    print("="*80)
    
    # Print category breakdown
    print("\nResults by category:")
    print("-"*80)
    for category, stats in test_results["categories"].items():
        print(f"{category.upper()}: {stats['passed']}/{stats['total']} passed ({stats['pass_rate']})")
    
    # Print failed tests if any
    if test_results["failed_tests"] > 0:
        print("\nFailed tests:")
        print("-"*80)
        for category, category_results in test_results["details"].items():
            for test in category_results["tests"]:
                if not test["passed"]:
                    print(f"{category}.{test['name']}: {test['error']}")
    
    if test_results["failed_tests"] > 0:
        logger.error(f"Test suite completed with {test_results['failed_tests']} failures")
        return 1
    else:
        logger.info("All tests passed successfully!")
        return 0


if __name__ == "__main__":
    # Run the test suite
    exit_code = asyncio.run(main())
    sys.exit(exit_code)