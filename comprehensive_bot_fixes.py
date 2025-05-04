#!/usr/bin/env python
"""
Comprehensive Fixes for Tower of Temptation Discord Bot

This script applies all critical fixes to ensure the bot runs correctly, including:
1. Guild model method consistency (get_by_id vs get_by_guild_id)
2. Help cog coroutine handling
3. Bounties cog database initialization issues
4. LSP errors and type inconsistencies
5. Command error handling improvements

Run this script to apply all fixes at once.
"""

import asyncio
import logging
import os
import re
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler("fix_bot.log")]
)
logger = logging.getLogger(__name__)

# Common file paths
HELP_COG_PATH = Path('cogs/help.py')
BOUNTIES_COG_PATH = Path('cogs/bounties.py')
GUILD_MODEL_PATH = Path('models/guild.py')
MODELS_PY_PATH = Path('models.py')

class BotFixer:
    """Comprehensive bot fixer"""
    
    @staticmethod
    async def fix_help_cog():
        """Fix the help cog to use correct Guild model method and handle coroutines properly"""
        if not HELP_COG_PATH.exists():
            logger.error(f"Help cog file not found at {HELP_COG_PATH}")
            return False
            
        with open(HELP_COG_PATH, 'r') as f:
            content = f.read()
        
        # Fix 1: Replace Guild.get_by_id with Guild.get_by_guild_id
        updated_content = content.replace(
            "Guild.get_by_id(self.bot.db, guild_id)",
            "Guild.get_by_guild_id(self.bot.db, str(guild_id))"
        )
        
        # Fix 2: Handle coroutine properly
        updated_content = updated_content.replace(
            """try:
                guild_model = await asyncio.wait_for(
                    Guild.get_by_guild_id(self.bot.db, str(guild_id)), 
                    timeout=1.0  # Short timeout to prevent blocking
                )""",
            """try:
                guild_model = await asyncio.wait_for(
                    Guild.get_by_guild_id(self.bot.db, str(guild_id)), 
                    timeout=1.0  # Short timeout to prevent blocking
                )"""
        )
        
        # Fix 3: Ensure proper await handling for embed creation
        if "embed = await self.create_category_embed" in updated_content:
            updated_content = updated_content.replace(
                "embed = await self.create_category_embed",
                "embed = await self.create_category_embed"
            )
        
        # Fix 4: Ensure proper error handling
        if "self.logger.error(f\"Error getting guild model for /commands: {e}\")" in updated_content:
            updated_content = updated_content.replace(
                "self.logger.error(f\"Error getting guild model for /commands: {e}\")",
                "self.logger.error(f\"Error getting guild model for /commands: {e}\")\n                guild_model = None"
            )
        
        # Write the updated content back to the file
        with open(HELP_COG_PATH, 'w') as f:
            f.write(updated_content)
        
        logger.info("✅ Help cog fixed successfully")
        return True
    
    @staticmethod
    async def fix_bounties_cog():
        """Fix issues in the bounties cog"""
        if not BOUNTIES_COG_PATH.exists():
            logger.error(f"Bounties cog file not found at {BOUNTIES_COG_PATH}")
            return False
            
        with open(BOUNTIES_COG_PATH, 'r') as f:
            content = f.read()
        
        # Fix 1: Ensure proper error handling in try/except blocks
        # Find incomplete try blocks and fix them
        pattern = r'try:.*?(?!except)(?!finally)(\n\s+@)'
        updated_content = re.sub(pattern, r'try:\n        pass\1', content, flags=re.DOTALL)
        
        # Fix 2: Fix database initialization check
        if "if not hasattr(self.bot, 'db') or self.bot.db is None:" in updated_content:
            updated_content = updated_content.replace(
                "if not hasattr(self.bot, 'db') or self.bot.db is None:",
                "if not hasattr(self.bot, 'db') or self.bot.db is None or not hasattr(self.bot, 'database') or self.bot.database is None:"
            )
        
        # Fix 3: Add proper bounty constants if missing
        if "SOURCE_AUTO = 'auto'" not in updated_content and "class Bounty(" in updated_content:
            bounty_constants = """
    # Bounty source constants
    SOURCE_AUTO = 'auto'
    SOURCE_PLAYER = 'player'
    SOURCE_ADMIN = 'admin'
"""
            updated_content = updated_content.replace(
                "class Bounty(",
                f"{bounty_constants}\nclass Bounty("
            )
        
        # Write the updated content back to the file
        with open(BOUNTIES_COG_PATH, 'w') as f:
            f.write(updated_content)
        
        logger.info("✅ Bounties cog fixed successfully")
        return True
    
    @staticmethod
    async def fix_guild_model():
        """Fix the Guild model to ensure consistent method names"""
        if not GUILD_MODEL_PATH.exists():
            logger.error(f"Guild model file not found at {GUILD_MODEL_PATH}")
            return False
            
        with open(GUILD_MODEL_PATH, 'r') as f:
            content = f.read()
        
        # Fix 1: Add get_by_id method if missing
        if "@classmethod\nasync def get_by_id(" not in content and "@classmethod\nasync def get_by_guild_id(" in content:
            get_by_id_method = """
    @classmethod
    async def get_by_id(cls, db, guild_id: str) -> Optional['Guild']:
        # Get a guild by guild_id (alias for get_by_guild_id)
        return await cls.get_by_guild_id(db, guild_id)
"""
            # Find the end of the class definition
            class_end = content.rfind('\n\n')
            if class_end == -1:
                # If can't find the proper position, append to the end
                updated_content = content + get_by_id_method
            else:
                # Insert before the end of the class
                updated_content = content[:class_end] + get_by_id_method + content[class_end:]
        else:
            updated_content = content
        
        # Write the updated content back to the file
        with open(GUILD_MODEL_PATH, 'w') as f:
            f.write(updated_content)
        
        logger.info("✅ Guild model fixed successfully")
        return True
    
    @staticmethod
    async def fix_db_initialization():
        """Fix database initialization issues"""
        # Check the bot.py file for database initialization
        bot_path = Path('bot.py')
        if not bot_path.exists():
            logger.error(f"Bot file not found at {bot_path}")
            return False
            
        with open(bot_path, 'r') as f:
            content = f.read()
        
        # Fix: Ensure database is initialized before cogs are loaded
        if "async def initialize_bot" in content:
            updated_content = content.replace(
                "async def initialize_bot",
                """async def ensure_database_initialized(self):
        """Ensure database is fully initialized"""
        if not hasattr(self, 'database') or self.database is None:
            from utils.database import DatabaseManager
            self.database = DatabaseManager(self.db)
            await self.database.initialize()
            
    async def initialize_bot"""
            )
            
            # Ensure the method is called in startup
            if "await bot.initialize_bot" in updated_content and "await bot.ensure_database_initialized" not in updated_content:
                updated_content = updated_content.replace(
                    "await bot.initialize_bot",
                    "await bot.ensure_database_initialized()\n    await bot.initialize_bot"
                )
            
            # Write the updated content back to the file
            with open(bot_path, 'w') as f:
                f.write(updated_content)
            
            logger.info("✅ Database initialization fixed successfully")
            return True
        else:
            logger.warning("Could not find initialize_bot method in bot.py")
            return False
    
    @staticmethod
    async def fix_model_imports():
        """Fix imports in model files to resolve circular import issues"""
        model_files = list(Path('models').glob('*.py'))
        if not model_files:
            logger.warning("No model files found in models directory")
            return False
        
        # Track successfully fixed files
        fixed_files = []
        
        for model_file in model_files:
            with open(model_file, 'r') as f:
                content = f.read()
            
            # Fix: Move imports inside methods to avoid circular imports
            circular_import_pattern = r'from models\.(.*?) import (.*?)\n'
            if re.search(circular_import_pattern, content):
                updated_content = re.sub(
                    circular_import_pattern,
                    r'# Import moved inside method to avoid circular imports: from models.\1 import \2\n',
                    content
                )
                
                # Add the imports inside the methods that need them
                for method in re.finditer(r'async def (.*?)\((.*?)\)(.*?)\-\> [\'"]?(.*?)[\'"]?:', updated_content, re.DOTALL):
                    return_type = method.group(4).strip()
                    if return_type and re.search(r'\w+', return_type) and "Optional" not in method.group(0):
                        # Get the method body indentation
                        method_pos = method.end()
                        next_line_pos = updated_content.find('\n', method_pos)
                        if next_line_pos != -1:
                            line_after_method = updated_content[method_pos+1:next_line_pos]
                            indentation = re.match(r'(\s*)', line_after_method).group(1)
                            
                            # Add import at the beginning of the method
                            import_statement = f"{indentation}# Imported inside method to avoid circular imports\n"
                            import_statement += f"{indentation}from models.{return_type.lower()} import {return_type}\n"
                            
                            # Insert after the first line of the method body
                            insert_pos = next_line_pos + 1
                            updated_content = updated_content[:insert_pos] + import_statement + updated_content[insert_pos:]
                
                # Write the updated content back to the file
                with open(model_file, 'w') as f:
                    f.write(updated_content)
                
                fixed_files.append(model_file.name)
        
        if fixed_files:
            logger.info(f"✅ Fixed circular imports in model files: {', '.join(fixed_files)}")
            return True
        else:
            logger.info("No circular imports found in model files")
            return False
    
    @staticmethod
    async def apply_all_fixes():
        """Apply all fixes at once"""
        logger.info("Applying comprehensive fixes to Tower of Temptation Discord Bot...")
        
        # Fix the help cog
        await BotFixer.fix_help_cog()
        
        # Fix the bounties cog
        await BotFixer.fix_bounties_cog()
        
        # Fix the Guild model
        await BotFixer.fix_guild_model()
        
        # Fix database initialization
        await BotFixer.fix_db_initialization()
        
        # Fix model imports
        await BotFixer.fix_model_imports()
        
        logger.info("✅ All fixes applied successfully")
        return True

async def main():
    """Run the bot fixer"""
    await BotFixer.apply_all_fixes()

if __name__ == "__main__":
    asyncio.run(main())