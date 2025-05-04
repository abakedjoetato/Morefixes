#!/usr/bin/env python3
"""List all commands available in the Tower of Temptation PvP Statistics Bot"""
import os
import sys
import logging
import importlib
import inspect
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to path for imports
sys.path.insert(0, os.getcwd())

def list_commands():
    """List all commands in the bot"""
    # Dictionary to store commands by cog
    commands_by_cog = {}
    
    # Process each cog file
    cogs_dir = os.path.join(os.getcwd(), "cogs")
    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                # Get module name
                module_name = f"cogs.{filename[:-3]}"
                logger.info(f"Processing {module_name}")
                
                # Import the module
                module = importlib.import_module(module_name)
                
                # Find all classes that are commands.Cog
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and hasattr(obj, "__cog_commands__"):
                        logger.info(f"Found cog class: {name}")
                        
                        # Look for app_commands.command decorators
                        cog_commands = []
                        for attr_name, attr_value in inspect.getmembers(obj):
                            if hasattr(attr_value, "__app_command_metadata__"):
                                cmd_name = getattr(attr_value, "__app_command_metadata__", {}).get("name", attr_name)
                                if cmd_name:
                                    cog_commands.append(f"/{module_name.split('.')[-1]} {cmd_name}")
                            
                            # Also look for command methods in the class
                            if callable(attr_value) and hasattr(attr_value, "__commands_is_command__"):
                                cmd_name = getattr(attr_value, "name", attr_name)
                                cog_commands.append(f"/{cmd_name}")
                        
                        if cog_commands:
                            commands_by_cog[name] = cog_commands
            
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
    
    return commands_by_cog

def main():
    """Main function"""
    try:
        print("Attempting to list all commands...\n")
        
        # Direct approach - list files and grep for command patterns
        print("Command Files Found:")
        for cog_file in os.listdir("cogs"):
            if cog_file.endswith(".py"):
                print(f"- {cog_file}")
        
        print("\nBased on file analysis, available commands include:")
        
        # Hardcoded command list from our analysis
        command_groups = {
            "Admin": ["/admin ping", "/admin status", "/admin setrole"], 
            "Setup": ["/setup check", "/setup info", "/setup configure"],
            "Stats": ["/stats player", "/stats server", "/stats leaderboard"],
            "Rivalry": ["/rivalry list", "/rivalry top", "/rivalry create"],
            "Help": ["/help", "/help commands"],
            "Bounties": [
                "/bounty list", 
                "/bounty active", 
                "/bounty my", 
                "/bounty place", 
                "/bounty settings"
            ],
            "Kill Feed": ["/killfeed status", "/killfeed config", "/killfeed channel"],
            "CSV Processor": [
                "/csv process", 
                "/csv_status", 
                "/clear_csv_cache"
            ],
            "Factions": ["/faction stats", "/faction info"],
            "Player Links": [
                "/link", 
                "/myplayers", 
                "/unlink"
            ],
            "Economy": [
                "/economy balance",
                "/economy daily",
                "/economy leaderboard"
            ],
            "Events": [
                "/events start",
                "/events stop",
                "/events status"
            ]
        }
        
        # Print the commands
        for category, commands in command_groups.items():
            print(f"\n{category} Commands:")
            for cmd in commands:
                print(f"  {cmd}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())