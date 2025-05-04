#!/usr/bin/env python3
"""
Sequential Command Testing for Tower of Temptation PvP Statistics Bot

This script runs all commands sequentially with proper delays to avoid timeouts.
"""
import os
import sys
import time
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('all_command_tests.log')
    ]
)
logger = logging.getLogger(__name__)

# Commands to test
COMMANDS = [
    "/admin ping",
    "/admin status",
    "/setup check",
    "/setup info",
    "/stats player",
    "/stats server",
    "/stats leaderboard",
    "/rivalry list",
    "/rivalry top",
    "/help",
    "/bounty list",
    "/killfeed status",
]

def main():
    """Run all commands sequentially"""
    logger.info("Starting sequential command testing")
    
    results = {}
    passed = 0
    failed = 0
    
    for i, command in enumerate(COMMANDS):
        logger.info(f"Testing command {i+1}/{len(COMMANDS)}: {command}")
        
        # Run the individual command test script
        try:
            result = subprocess.run(
                ["python", "test_individual_commands.py", command],
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout per command
            )
            
            if result.returncode == 0:
                status = "PASS"
                passed += 1
            else:
                status = "FAIL"
                failed += 1
                
            results[command] = {
                "status": status,
                "return_code": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }
            
            logger.info(f"Command {command}: {status}")
            
            if result.stderr:
                logger.warning(f"Command {command} stderr: {result.stderr.strip()}")
                
        except subprocess.TimeoutExpired:
            logger.error(f"Command {command} timed out")
            results[command] = {
                "status": "TIMEOUT",
                "return_code": None,
                "stdout": "",
                "stderr": "Command timed out after 30 seconds"
            }
            failed += 1
        except Exception as e:
            logger.error(f"Error testing {command}: {e}")
            results[command] = {
                "status": "ERROR",
                "return_code": None,
                "stdout": "",
                "stderr": str(e)
            }
            failed += 1
            
        # Wait between commands to avoid rate limiting
        time.sleep(5)
    
    # Print summary
    print("\n===== COMMAND TEST RESULTS =====")
    for command, result in results.items():
        status = result["status"]
        status_display = "✅" if status == "PASS" else "❌"
        print(f"{status_display} {command}: {status}")
        
        # Print output if failed
        if status != "PASS":
            print(f"  Error: {result['stderr']}")
            
    print(f"\nTotal Commands: {len(COMMANDS)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/len(COMMANDS)*100:.1f}%")
    
    # Write detailed results to a file
    with open("command_test_results.txt", "w") as f:
        f.write(f"Command Test Results - {datetime.now()}\n")
        f.write("=" * 50 + "\n\n")
        
        for command, result in results.items():
            f.write(f"Command: {command}\n")
            f.write(f"Status: {result['status']}\n")
            f.write(f"Return Code: {result['return_code']}\n")
            
            if result['stdout']:
                f.write(f"Output:\n{result['stdout']}\n")
                
            if result['stderr']:
                f.write(f"Error:\n{result['stderr']}\n")
                
            f.write("-" * 50 + "\n\n")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    print(f"Starting command tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sys.exit(main())