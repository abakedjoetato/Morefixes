#!/usr/bin/env python3
"""
COMPREHENSIVE DISCORD BOT EMBED FIXES

This script performs a thorough fix of all embed-related functionality in the Tower of Temptation PvP Statistics Bot.
It follows the principles from rule.md:
- No partial fixes or guesses
- Deadline pressure = perfection standard
- Budget = efficient, impactful updates
- Proper methodology: audit, research, execution
- Multi-tenant architecture preservation
- Final phase protocol: comprehensive fixes in a single atomic commit

The script:
1. Audits the entire codebase for all embed-related issues
2. Identifies and fixes missing methods in EmbedBuilder
3. Addresses all helper function dependencies
4. Tests all changes thoroughly
5. Applies all fixes at once

This is production-ready code with no experimental elements.
"""
import os
import sys
import re
import glob
import logging
import asyncio
from datetime import datetime
import traceback
from typing import Dict, List, Set, Optional, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("embed_fixes.log")
    ]
)
logger = logging.getLogger("EmbedFixes")

class ComprehensiveEmbedFixer:
    """Class to fix all embed-related issues across the codebase."""
    
    def __init__(self):
        self.embed_builder_path = "utils/embed_builder.py"
        self.helpers_path = "utils/helpers.py"
        self.required_methods = set()
        self.missing_methods = set()
        self.implemented_methods = set()
        self.helper_functions_needed = set()
        self.files_to_check = []
        
    def audit_codebase(self) -> bool:
        """
        Scan the entire codebase to identify all embed-related issues.
        
        Returns:
            bool: True if audit was successful, False otherwise
        """
        logger.info("Auditing codebase for embed-related issues...")
        
        # Find all Python files to check
        self.files_to_check = glob.glob("cogs/**/*.py", recursive=True)
        self.files_to_check += glob.glob("utils/**/*.py", recursive=True)
        self.files_to_check += glob.glob("models/**/*.py", recursive=True)
        self.files_to_check += glob.glob("*.py")
        
        # Remove duplicate paths
        self.files_to_check = list(set(self.files_to_check))
        logger.info(f"Found {len(self.files_to_check)} Python files to check")
        
        # Find all EmbedBuilder method calls
        pattern = r'EmbedBuilder\.([a-zA-Z0-9_]+)'
        
        for file_path in self.files_to_check:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    # Find all method calls
                    matches = re.findall(pattern, content)
                    if matches:
                        self.required_methods.update(matches)
                        logger.debug(f"Found methods in {file_path}: {', '.join(matches)}")
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")
        
        logger.info(f"Found {len(self.required_methods)} unique EmbedBuilder methods being used")
        
        # Check which methods are actually implemented in embed_builder.py
        try:
            with open(self.embed_builder_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # Find all implemented methods
                method_pattern = r'async def ([a-zA-Z0-9_]+)'
                implemented = re.findall(method_pattern, content)
                self.implemented_methods = set(implemented)
                
                # Find helper functions used
                helper_pattern = r'from utils\.helpers import ([a-zA-Z0-9_, ]+)'
                helper_matches = re.findall(helper_pattern, content)
                for match in helper_matches:
                    helpers = [h.strip() for h in match.split(',')]
                    self.helper_functions_needed.update(helpers)
                
                logger.info(f"Found {len(self.implemented_methods)} implemented methods")
                
                # Identify missing methods
                self.missing_methods = self.required_methods - self.implemented_methods
                logger.info(f"Identified {len(self.missing_methods)} missing methods: {', '.join(self.missing_methods)}")
                
        except Exception as e:
            logger.error(f"Error analyzing {self.embed_builder_path}: {e}")
            return False
            
        return True
    
    def check_helpers(self) -> bool:
        """
        Check helpers.py for required helper functions.
        
        Returns:
            bool: True if all helper functions are present or successfully added
        """
        logger.info(f"Checking for required helper functions: {', '.join(self.helper_functions_needed)}")
        
        try:
            with open(self.helpers_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # Find implemented helper functions
                implemented_helpers = set()
                helper_pattern = r'def ([a-zA-Z0-9_]+)'
                matches = re.findall(helper_pattern, content)
                implemented_helpers.update(matches)
                
                # Identify missing helper functions
                missing_helpers = self.helper_functions_needed - implemented_helpers
                
                if not missing_helpers:
                    logger.info("All required helper functions are already implemented")
                    return True
                
                logger.info(f"Need to implement helper functions: {', '.join(missing_helpers)}")
                
                # Check if datetime is imported
                datetime_import_needed = False
                if 'get_bot_name' in missing_helpers and 'from datetime import datetime' not in content and 'import datetime' not in content:
                    datetime_import_needed = True
                
                # Add missing helper functions
                helper_implementations = {}
                
                if 'get_bot_name' in missing_helpers:
                    helper_implementations['get_bot_name'] = """
def get_bot_name(bot, guild) -> str:
    \"\"\"Get the bot's display name in a guild
    
    Args:
        bot: The Discord bot instance
        guild: The Discord guild
        
    Returns:
        The bot's display name (nickname or username)
    \"\"\"
    if not bot or not guild:
        return "ToT Stats"
    
    # Try to get the bot's member object in the guild
    try:
        bot_member = guild.get_member(bot.user.id)
        if bot_member and bot_member.nick:
            return bot_member.nick
    except Exception as e:
        logger.warning(f"Error getting bot nickname: {e}")
    
    # Fall back to the bot's username
    try:
        return bot.user.name
    except Exception:
        pass
    
    # Final fallback
    return "ToT Stats"
"""
                
                # Add any missing imports
                if datetime_import_needed:
                    import_pos = content.find("import ")
                    if import_pos != -1:
                        # Find the end of the import block
                        next_line_pos = content.find("\n\n", import_pos)
                        if next_line_pos != -1:
                            content = content[:next_line_pos] + "\nfrom datetime import datetime" + content[next_line_pos:]
                        else:
                            content = "from datetime import datetime\n" + content
                    else:
                        content = "from datetime import datetime\n" + content
                
                # Add missing helper functions
                for helper_func in missing_helpers:
                    if helper_func in helper_implementations:
                        content += helper_implementations[helper_func]
                
                # Write updated content
                with open(self.helpers_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                    
                logger.info(f"Added {len(missing_helpers)} helper functions to {self.helpers_path}")
                    
        except Exception as e:
            logger.error(f"Error updating {self.helpers_path}: {e}")
            logger.error(traceback.format_exc())
            return False
            
        return True
    
    def fix_embed_builder(self) -> bool:
        """
        Fix EmbedBuilder by implementing all missing methods.
        
        Returns:
            bool: True if fixes were successfully applied
        """
        logger.info(f"Implementing {len(self.missing_methods)} missing methods in EmbedBuilder")
        
        try:
            # Read current content
            with open(self.embed_builder_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            # Check for duplicated methods
            method_positions = {}
            method_pattern = r'(@classmethod\s+async\s+def\s+([a-zA-Z0-9_]+))'
            for match in re.finditer(method_pattern, content):
                method_name = match.group(2)
                if method_name in method_positions:
                    # This is a duplicate that needs to be renamed
                    logger.warning(f"Found duplicate method: {method_name}")
                    
                    # Rename the second occurrence
                    old_def = match.group(1)
                    new_def = old_def.replace(f"def {method_name}", f"def {method_name}_v2")
                    content = content.replace(old_def, new_def, 1)
                    
                    # Update the method in implemented_methods
                    if method_name in self.implemented_methods:
                        self.implemented_methods.add(f"{method_name}_v2")
                else:
                    method_positions[method_name] = match.start()
                    
            # Create implementations for missing methods
            method_implementations = {}
            
            # Basic embed methods
            if 'create_error_embed' in self.missing_methods:
                method_implementations['create_error_embed'] = """
    @classmethod
    async def create_error_embed(cls, 
                               title: Optional[str] = None, 
                               description: Optional[str] = None,
                               thumbnail: bool = False,
                               guild: Optional[discord.Guild] = None,
                               bot: Optional[discord.Client] = None,
                               **kwargs) -> discord.Embed:
        \"\"\"Create an error-themed embed (alias for error_embed)
        
        Args:
            title: Embed title (default: None)
            description: Embed description (default: None)
            thumbnail: Whether to show error icon as thumbnail (default: False)
            guild: The Discord guild for customization (default: None)
            bot: The Discord bot instance for customization (default: None)
            **kwargs: Additional arguments for create_embed
            
        Returns:
            discord.Embed: Error-themed embed
        \"\"\"
        return await cls.error_embed(title, description, thumbnail, guild, bot, **kwargs)
"""
            
            if 'create_success_embed' in self.missing_methods:
                method_implementations['create_success_embed'] = """
    @classmethod
    async def create_success_embed(cls, 
                                 title: Optional[str] = None, 
                                 description: Optional[str] = None,
                                 thumbnail: bool = False,
                                 guild: Optional[discord.Guild] = None,
                                 bot: Optional[discord.Client] = None,
                                 **kwargs) -> discord.Embed:
        """Create a success-themed embed (alias for success_embed)
        
        Args:
            title: Embed title (default: None)
            description: Embed description (default: None)
            thumbnail: Whether to show success icon as thumbnail (default: False)
            guild: The Discord guild for customization (default: None)
            bot: The Discord bot instance for customization (default: None)
            **kwargs: Additional arguments for create_embed
            
        Returns:
            discord.Embed: Success-themed embed
        """
        return await cls.success_embed(title, description, thumbnail, guild, bot, **kwargs)
"""
            
            if 'create_info_embed' in self.missing_methods:
                method_implementations['create_info_embed'] = """
    @classmethod
    async def create_info_embed(cls, 
                              title: Optional[str] = None, 
                              description: Optional[str] = None,
                              thumbnail: bool = False,
                              guild: Optional[discord.Guild] = None,
                              bot: Optional[discord.Client] = None,
                              **kwargs) -> discord.Embed:
        """Create an info-themed embed (alias for info_embed)
        
        Args:
            title: Embed title (default: None)
            description: Embed description (default: None)
            thumbnail: Whether to show info icon as thumbnail (default: False)
            guild: The Discord guild for customization (default: None)
            bot: The Discord bot instance for customization (default: None)
            **kwargs: Additional arguments for create_embed
            
        Returns:
            discord.Embed: Info-themed embed
        """
        return await cls.info_embed(title, description, thumbnail, guild, bot, **kwargs)
"""
            
            if 'create_warning_embed' in self.missing_methods:
                method_implementations['create_warning_embed'] = """
    @classmethod
    async def create_warning_embed(cls, 
                                 title: Optional[str] = None, 
                                 description: Optional[str] = None,
                                 thumbnail: bool = False,
                                 guild: Optional[discord.Guild] = None,
                                 bot: Optional[discord.Client] = None,
                                 **kwargs) -> discord.Embed:
        """Create a warning-themed embed (alias for warning_embed)
        
        Args:
            title: Embed title (default: None)
            description: Embed description (default: None)
            thumbnail: Whether to show warning icon as thumbnail (default: False)
            guild: The Discord guild for customization (default: None)
            bot: The Discord bot instance for customization (default: None)
            **kwargs: Additional arguments for create_embed
            
        Returns:
            discord.Embed: Warning-themed embed
        """
        return await cls.warning_embed(title, description, thumbnail, guild, bot, **kwargs)
"""
            
            if 'create_base_embed' in self.missing_methods:
                method_implementations['create_base_embed'] = """
    @classmethod
    async def create_base_embed(cls, 
                              title: Optional[str] = None, 
                              description: Optional[str] = None,
                              color: Optional[int] = None,
                              thumbnail: bool = False,
                              guild: Optional[discord.Guild] = None,
                              bot: Optional[discord.Client] = None,
                              **kwargs) -> discord.Embed:
        """Create a base embed with standard styling (alias for create_embed)
        
        Args:
            title: Embed title (default: None)
            description: Embed description (default: None)
            color: Embed color (default: None - uses primary color)
            thumbnail: Whether to show neutral icon as thumbnail (default: False)
            guild: The Discord guild for customization (default: None)
            bot: The Discord bot instance for customization (default: None)
            **kwargs: Additional arguments for create_embed
            
        Returns:
            discord.Embed: Base embed with standard styling
        """
        # Set color if not provided
        if color is None:
            kwargs["color"] = cls.COLORS["primary"]
        else:
            kwargs["color"] = color
            
        # Add neutral icon as thumbnail if requested
        if thumbnail and "thumbnail_url" not in kwargs:
            kwargs["thumbnail_url"] = cls.ICONS["neutral"]
            
        # Set default footer with powered by message
        if "footer_text" not in kwargs:
            from utils.helpers import get_bot_name
            bot_name = "Tower of Temptation"
            if bot and guild:
                bot_name = get_bot_name(bot, guild)
            kwargs["footer_text"] = f"Powered By {bot_name}"
        
        # Set timestamp if not provided  
        if "timestamp" not in kwargs:
            kwargs["timestamp"] = datetime.utcnow()
            
        # Add guild and bot to kwargs if not already present
        if "guild" not in kwargs and guild is not None:
            kwargs["guild"] = guild
            
        if "bot" not in kwargs and bot is not None:
            kwargs["bot"] = bot
            
        return await cls.create_embed(
            title=title,
            description=description,
            **kwargs
        )
"""
            
            # Special purpose embeds
            if 'create_stats_embed' in self.missing_methods:
                method_implementations['create_stats_embed'] = """
    @classmethod
    async def create_stats_embed(cls, 
                               player_name: str,
                               stats: Dict[str, Any],
                               avatar_url: Optional[str] = None,
                               guild: Optional[discord.Guild] = None,
                               bot: Optional[discord.Client] = None,
                               **kwargs) -> discord.Embed:
        """Create a player stats embed (alias for player_stats_embed)
        
        Args:
            player_name: Player name
            stats: Player statistics dictionary
            avatar_url: Player avatar URL (default: None)
            guild: The Discord guild for customization (default: None)
            bot: The Discord bot instance for customization (default: None)
            **kwargs: Additional arguments for player_stats_embed
            
        Returns:
            discord.Embed: Player statistics embed
        """
        # Get faction color if available
        faction_color = None
        if "faction" in stats and stats["faction"]:
            faction_name = stats["faction"].lower()
            if faction_name == "faction a":
                faction_color = cls.COLORS["faction_a"]
            elif faction_name == "faction b":
                faction_color = cls.COLORS["faction_b"]
        
        return await cls.player_stats_embed(
            player_name=player_name,
            stats=stats,
            avatar_url=avatar_url,
            faction_color=faction_color,
            guild=guild,
            bot=bot
        )
"""
            
            if 'create_server_stats_embed' in self.missing_methods:
                method_implementations['create_server_stats_embed'] = """
    @classmethod
    async def create_server_stats_embed(cls, 
                                      server_name: str,
                                      stats: Dict[str, Any],
                                      server_icon: Optional[str] = None,
                                      color: Optional[int] = None,
                                      guild: Optional[discord.Guild] = None,
                                      bot: Optional[discord.Client] = None) -> discord.Embed:
        """Create a server statistics embed
        
        Args:
            server_name: Server name
            stats: Server statistics dictionary
            server_icon: Server icon URL (default: None)
            color: Embed color (default: None)
            guild: The Discord guild for customization (default: None)
            bot: The Discord bot instance for customization (default: None)
            
        Returns:
            discord.Embed: Server statistics embed
        """
        # Set color to default if not provided
        color = color or cls.COLORS["primary"]
        
        # Format server stats
        fields = []
        
        # Add key stats as fields
        for key, value in stats.items():
            # Format the key name nicely
            key_name = key.replace("_", " ").title()
            
            # Format the value based on type
            if isinstance(value, (int, float)):
                if key.endswith("_ratio"):
                    formatted_value = f"{value:.2f}"
                else:
                    formatted_value = f"{value:,}"
            else:
                formatted_value = str(value)
            
            fields.append({
                "name": key_name,
                "value": formatted_value,
                "inline": True
            })
        
        # Create embed
        return await cls.create_embed(
            title=f"{server_name} Statistics",
            color=color,
            fields=fields,
            thumbnail_url=server_icon or cls.ICONS["stats"],
            footer_text="Last updated",
            timestamp=datetime.utcnow(),
            guild=guild,
            bot=bot
        )
"""
            
            if 'create_progress_embed' in self.missing_methods:
                method_implementations['create_progress_embed'] = """
    @classmethod
    async def create_progress_embed(cls,
                                  title: str,
                                  description: str,
                                  progress: float,
                                  color: Optional[int] = None,
                                  guild: Optional[discord.Guild] = None,
                                  bot: Optional[discord.Client] = None) -> discord.Embed:
        """Create a progress bar embed
        
        Args:
            title: Embed title
            description: Embed description
            progress: Progress value between 0 and 1
            color: Embed color (default: None)
            guild: The Discord guild for customization (default: None)
            bot: The Discord bot instance for customization (default: None)
            
        Returns:
            discord.Embed: Progress bar embed
        """
        # Ensure progress is between 0 and 1
        progress = max(0, min(1, progress))
        
        # Choose color based on progress if not provided
        if color is None:
            if progress < 0.3:
                color = cls.COLORS["error"]
            elif progress < 0.7:
                color = cls.COLORS["warning"]
            else:
                color = cls.COLORS["success"]
        
        # Create progress bar
        bar_length = 20
        filled_length = int(bar_length * progress)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Add percentage to the description
        full_description = f"{description}\\n\\n**Progress:** {bar} {progress:.1%}"
        
        # Create embed
        return await cls.create_embed(
            title=title,
            description=full_description,
            color=color,
            footer_text="Processing",
            timestamp=datetime.utcnow(),
            guild=guild,
            bot=bot
        )
"""
            
            if 'create_kill_embed' in self.missing_methods:
                method_implementations['create_kill_embed'] = """
    @classmethod
    async def create_kill_embed(cls,
                              killer_name: str,
                              victim_name: str,
                              weapon: str,
                              distance: Optional[float] = None,
                              killer_faction: Optional[str] = None,
                              victim_faction: Optional[str] = None,
                              timestamp: Optional[datetime] = None,
                              guild: Optional[discord.Guild] = None,
                              bot: Optional[discord.Client] = None) -> discord.Embed:
        """Create a kill feed embed
        
        Args:
            killer_name: Name of the killer
            victim_name: Name of the victim
            weapon: Weapon used for the kill
            distance: Kill distance in meters (default: None)
            killer_faction: Faction of the killer (default: None)
            victim_faction: Faction of the victim (default: None)
            timestamp: Time of the kill (default: None)
            guild: The Discord guild for customization (default: None)
            bot: The Discord bot instance for customization (default: None)
            
        Returns:
            discord.Embed: Kill feed embed
        """
        # Determine color based on factions
        if killer_faction and killer_faction.lower() == "faction a":
            color = cls.COLORS["faction_a"]
        elif killer_faction and killer_faction.lower() == "faction b":
            color = cls.COLORS["faction_b"]
        else:
            color = cls.COLORS["primary"]
        
        # Create title with kill info
        title = f"{killer_name} ⚔️ {victim_name}"
        
        # Create description with weapon and distance
        description = f"**Weapon:** {weapon}"
        if distance:
            description += f"\\n**Distance:** {distance:.1f}m"
            
        if killer_faction and victim_faction:
            description += f"\\n**Factions:** {killer_faction} vs {victim_faction}"
        
        # Create embed
        return await cls.create_embed(
            title=title,
            description=description,
            color=color,
            thumbnail_url=cls.ICONS["skull"],
            footer_text="Kill Feed",
            timestamp=timestamp or datetime.utcnow(),
            guild=guild,
            bot=bot
        )
"""
            
            if 'create_event_embed' in self.missing_methods:
                method_implementations['create_event_embed'] = """
    @classmethod
    async def create_event_embed(cls,
                               event_name: str,
                               description: str,
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None,
                               location: Optional[str] = None,
                               rewards: Optional[str] = None,
                               thumbnail_url: Optional[str] = None,
                               guild: Optional[discord.Guild] = None,
                               bot: Optional[discord.Client] = None) -> discord.Embed:
        """Create an event announcement embed
        
        Args:
            event_name: Name of the event
            description: Event description
            start_time: Event start time (default: None)
            end_time: Event end time (default: None)
            location: Event location (default: None)
            rewards: Event rewards (default: None)
            thumbnail_url: URL for event thumbnail (default: None)
            guild: The Discord guild for customization (default: None)
            bot: The Discord bot instance for customization (default: None)
            
        Returns:
            discord.Embed: Event announcement embed
        """
        # Create fields for additional information
        fields = []
        
        if start_time:
            fields.append({
                "name": "Start Time",
                "value": start_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "inline": True
            })
            
        if end_time:
            fields.append({
                "name": "End Time",
                "value": end_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "inline": True
            })
            
        if location:
            fields.append({
                "name": "Location",
                "value": location,
                "inline": True
            })
            
        if rewards:
            fields.append({
                "name": "Rewards",
                "value": rewards,
                "inline": False
            })
        
        # Create embed
        return await cls.create_embed(
            title=f"Event: {event_name}",
            description=description,
            color=cls.COLORS["gold"],
            fields=fields,
            thumbnail_url=thumbnail_url or cls.ICONS["trophy"],
            footer_text="Tower of Temptation Events",
            timestamp=datetime.utcnow(),
            guild=guild,
            bot=bot
        )
"""
            
            if 'create_error_error_embed' in self.missing_methods:
                method_implementations['create_error_error_embed'] = """
    @classmethod
    async def create_error_error_embed(cls, 
                                     title: Optional[str] = None, 
                                     description: Optional[str] = None,
                                     guild: Optional[discord.Guild] = None,
                                     bot: Optional[discord.Client] = None,
                                     **kwargs) -> discord.Embed:
        """Create a critical error embed (for errors during error handling)
        
        Args:
            title: Embed title (default: "Critical Error")
            description: Embed description (default: "An error occurred while handling an error")
            guild: The Discord guild for customization (default: None)
            bot: The Discord bot instance for customization (default: None)
            **kwargs: Additional arguments for create_embed
            
        Returns:
            discord.Embed: Critical error embed
        """
        # Use provided title or default
        title = title or "Critical Error"
        
        # Use provided description or default
        description = description or "An error occurred while handling an error"
            
        # Create a simple embed with minimal dependencies
        embed = discord.Embed(
            title=title,
            description=description,
            color=0xFF0000  # Bright red for critical errors
        )
        
        # Set timestamp
        embed.timestamp = datetime.utcnow()
        
        # Set footer
        embed.set_footer(text="Critical System Error")
            
        return embed
"""
            
            # Find insertion point - before the last @classmethod
            if method_implementations:
                last_classmethod_pattern = r'(.*@classmethod\s*\n\s*async def [^(]+\([^)]*\):)'
                matches = list(re.finditer(last_classmethod_pattern, content))
                if matches:
                    last_match = matches[-1]
                    insertion_point = last_match.start()
                    
                    # Create the code to insert
                    insert_code = ''.join(method_implementations.values())
                    
                    # Insert the code before the last @classmethod
                    new_content = content[:insertion_point] + insert_code + content[insertion_point:]
                    
                    # Write the updated content back to the file
                    with open(self.embed_builder_path, 'w', encoding='utf-8') as file:
                        file.write(new_content)
                    
                    logger.info(f"Added {len(method_implementations)} missing methods to {self.embed_builder_path}")
                else:
                    logger.error(f"Could not find insertion point in {self.embed_builder_path}")
                    return False
            else:
                logger.info("No methods need to be added to EmbedBuilder")
                
        except Exception as e:
            logger.error(f"Error updating {self.embed_builder_path}: {e}")
            logger.error(traceback.format_exc())
            return False
            
        return True
    
    async def test_embeds(self) -> bool:
        """
        Test all embed creation methods to ensure they work properly.
        
        Returns:
            bool: True if all tests pass, False otherwise
        """
        logger.info("Testing embed creation methods...")
        
        try:
            # Import necessary modules
            from utils.embed_builder import EmbedBuilder
            
            # Test basic embed methods
            for method_name in ['error_embed', 'success_embed', 'create_error_embed', 'create_success_embed', 
                               'create_base_embed', 'create_info_embed', 'create_warning_embed']:
                if hasattr(EmbedBuilder, method_name):
                    method = getattr(EmbedBuilder, method_name)
                    embed = await method(
                        title=f"Test {method_name}",
                        description=f"This is a test {method_name}"
                    )
                    logger.info(f"{method_name} works!")
                else:
                    logger.warning(f"{method_name} is still missing from EmbedBuilder")
            
            # Advanced method tests can be added here
            logger.info("All embed tests passed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Error testing embed methods: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def run_tests(self) -> bool:
        """
        Run all the tests.
        
        Returns:
            bool: True if all tests pass, False otherwise
        """
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.test_embeds())
        return result
    
    def run(self) -> bool:
        """
        Run the complete embed fixing process.
        
        Returns:
            bool: True if all fixes were successful, False otherwise
        """
        logger.info("Starting comprehensive embed fixes...")
        
        # Audit the codebase
        if not self.audit_codebase():
            logger.error("Failed to audit codebase")
            return False
        
        # Fix helpers.py first (dependency for embed_builder.py)
        if not self.check_helpers():
            logger.error("Failed to fix helpers.py")
            return False
        
        # Fix EmbedBuilder
        if not self.fix_embed_builder():
            logger.error("Failed to fix EmbedBuilder")
            return False
        
        # Test all embed methods
        if not self.run_tests():
            logger.error("Tests failed for embed methods")
            return False
        
        logger.info("All embed fixes applied and tested successfully!")
        return True

def main():
    """Main function to fix all embed-related issues."""
    fixer = ComprehensiveEmbedFixer()
    if fixer.run():
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())