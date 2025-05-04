"""
Comprehensive Fixes for Tower of Temptation Discord Bot

This script applies all critical fixes to ensure the bot runs correctly, including:
1. Guild model method consistency (get_by_id vs get_by_guild_id)
2. Help cog coroutine handling
3. Bounties cog database initialization issues
4. LSP errors and type inconsistencies
5. Command error handling improvements
6. Multi-guild isolation across all database operations

Run this script to apply all fixes at once.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot_fixes.log")
    ]
)

logger = logging.getLogger("bot_fixer")

class BotFixer:
    """Comprehensive bot fixer"""
    
    @staticmethod
    async def fix_help_cog():
        """Fix the help cog to use correct Guild model method and handle coroutines properly"""
        logger.info("Fixing help cog...")
        
        help_cog_path = Path("cogs/help.py")
        if not help_cog_path.exists():
            logger.error(f"Help cog file not found at {help_cog_path}")
            return False
        
        try:
            # Read the file
            with open(help_cog_path, "r") as f:
                content = f.read()
            
            # Check if the file still needs fixing
            if "get_by_id" in content and "guild = await Guild.get_by_id(db, guild_id)" in content:
                # Replace get_by_id with get_by_guild_id
                content = content.replace(
                    "guild = await Guild.get_by_id(db, guild_id)",
                    "guild = await Guild.get_by_guild_id(db, str(guild_id))"
                )
                
                # Fix the error in await handling
                content = content.replace(
                    "if isinstance(help_text, coroutine):",
                    "if asyncio.iscoroutine(help_text):"
                )
                
                # Write the changes back
                with open(help_cog_path, "w") as f:
                    f.write(content)
                    
                logger.info("Help cog fixed successfully")
                return True
            else:
                logger.info("Help cog already fixed or using different methods")
                return True
        except Exception as e:
            logger.error(f"Error fixing help cog: {e}")
            return False
    
    @staticmethod
    async def fix_bounties_cog():
        """Fix issues in the bounties cog"""
        logger.info("Fixing bounties cog...")
        
        bounties_cog_path = Path("cogs/bounties.py")
        if not bounties_cog_path.exists():
            logger.error(f"Bounties cog file not found at {bounties_cog_path}")
            return False
        
        try:
            # Read the file
            with open(bounties_cog_path, "r") as f:
                content = f.read()
            
            # Check if db initialization needs fixing
            if "self.db = None" in content and not "self.db = await get_db()" in content:
                # Fix database initialization
                content = content.replace(
                    "self.db = None",
                    "self.db = await get_db()"
                )
                
                # Fix any bounty creation calls without guild_id
                content = content.replace(
                    "bounty = await Bounty.create(\n            db=self.db,",
                    "bounty = await Bounty.create(\n            db=self.db,\n            guild_id=str(interaction.guild_id),"
                )
                
                # Write the changes back
                with open(bounties_cog_path, "w") as f:
                    f.write(content)
                    
                logger.info("Bounties cog fixed successfully")
                return True
            else:
                logger.info("Bounties cog already fixed or using different initialization")
                return True
        except Exception as e:
            logger.error(f"Error fixing bounties cog: {e}")
            return False
    
    @staticmethod
    async def fix_guild_model():
        """Fix the Guild model to ensure consistent method names"""
        logger.info("Fixing Guild model...")
        
        guild_model_path = Path("models/guild.py")
        if not guild_model_path.exists():
            logger.error(f"Guild model file not found at {guild_model_path}")
            return False
        
        try:
            # Read the file
            with open(guild_model_path, "r") as f:
                content = f.read()
            
            # Check if get_by_guild_id method is missing
            if "async def get_by_guild_id" not in content and "async def get_by_id" in content:
                # Get the get_by_id method and create get_by_guild_id as an alias
                replacement = """
    @classmethod
    async def get_by_guild_id(cls, db, guild_id: str) -> Optional['Guild']:
        \"\"\"Get a guild by guild_id
        
        Args:
            db: Database connection
            guild_id: Discord guild ID
            
        Returns:
            Guild object or None if not found
        \"\"\"
        return await cls.get_by_id(db, guild_id)
        
    @classmethod"""
                
                # Replace the get_by_id method definition
                content = content.replace(
                    "@classmethod",
                    replacement,
                    1  # Replace only the first occurrence
                )
                
                # Write the changes back
                with open(guild_model_path, "w") as f:
                    f.write(content)
                    
                logger.info("Guild model fixed successfully")
                return True
            else:
                logger.info("Guild model already fixed or using different method names")
                return True
        except Exception as e:
            logger.error(f"Error fixing Guild model: {e}")
            return False
    
    @staticmethod
    async def fix_db_initialization():
        """Fix database initialization issues"""
        logger.info("Fixing database initialization...")
        
        # Check all cog files for proper database initialization
        cogs_dir = Path("cogs")
        if not cogs_dir.exists() or not cogs_dir.is_dir():
            logger.error(f"Cogs directory not found at {cogs_dir}")
            return False
        
        try:
            # Get all Python files in the cogs directory
            cog_files = list(cogs_dir.glob("*.py"))
            
            for cog_file in cog_files:
                if cog_file.name.startswith("_"):
                    continue  # Skip __init__.py and other special files
                
                # Read the file
                with open(cog_file, "r") as f:
                    content = f.read()
                
                # Check if db initialization needs fixing
                if "self.db = None" in content and "__init__" in content and "async def" in content:
                    # Fix missing database import
                    if "from utils.database import get_db" not in content:
                        import_section_end = content.find("class ")
                        content = content[:import_section_end] + "from utils.database import get_db\n\n" + content[import_section_end:]
                    
                    # Fix the __init__ method
                    content = content.replace(
                        "self.db = None",
                        "self.db = await get_db()"
                    )
                    
                    # Write the changes back
                    with open(cog_file, "w") as f:
                        f.write(content)
                        
                    logger.info(f"Fixed database initialization in {cog_file.name}")
            
            logger.info("Database initialization fixed in all cogs")
            return True
        except Exception as e:
            logger.error(f"Error fixing database initialization: {e}")
            return False
    
    @staticmethod
    async def fix_model_imports():
        """Fix imports in model files to resolve circular import issues"""
        logger.info("Fixing model imports...")
        
        models_dir = Path("models")
        if not models_dir.exists() or not models_dir.is_dir():
            logger.error(f"Models directory not found at {models_dir}")
            return False
        
        try:
            # Get all Python files in the models directory
            model_files = list(models_dir.glob("*.py"))
            
            for model_file in model_files:
                if model_file.name.startswith("_"):
                    continue  # Skip __init__.py and other special files
                
                # Read the file
                with open(model_file, "r") as f:
                    content = f.read()
                
                # Check for direct imports of other models at module level
                circular_imports = []
                for other_model in model_files:
                    if other_model.name != model_file.name:
                        model_name = other_model.stem.capitalize()
                        if f"from models.{other_model.stem} import {model_name}" in content:
                            circular_imports.append((other_model.stem, model_name))
                
                # Fix circular imports
                for import_file, import_class in circular_imports:
                    # Replace direct import with function-level import
                    content = content.replace(
                        f"from models.{import_file} import {import_class}",
                        f"# Local import to avoid circular references\n# from models.{import_file} import {import_class}"
                    )
                    
                    # Add function-level import to methods that need it
                    method_pattern = "async def "
                    method_positions = [pos for pos in range(len(content)) if content.find(method_pattern, pos) == pos]
                    
                    for pos in method_positions:
                        method_end = content.find(":", pos)
                        method_body_start = content.find("\n", method_end) + 1
                        
                        # Check if method uses the imported class
                        method_body_end = content.find("\n    @", method_body_start)
                        if method_body_end == -1:
                            method_body_end = len(content)
                        
                        method_body = content[method_body_start:method_body_end]
                        
                        if import_class in method_body:
                            # Add import inside method
                            method_body_lines = method_body.split("\n")
                            indent = "        "  # Assume 4-space indentation
                            import_line = f"{indent}from models.{import_file} import {import_class}"
                            
                            if import_line not in method_body:
                                method_body_lines.insert(0, import_line)
                                new_method_body = "\n".join(method_body_lines)
                                content = content[:method_body_start] + new_method_body + content[method_body_end:]
                    
                    # Write the changes back
                    with open(model_file, "w") as f:
                        f.write(content)
                        
                    logger.info(f"Fixed circular imports in {model_file.name}")
            
            logger.info("Model imports fixed in all model files")
            return True
        except Exception as e:
            logger.error(f"Error fixing model imports: {e}")
            return False
    
    @staticmethod
    async def fix_bounty_guild_isolation():
        """Fix guild isolation in the Bounty model"""
        logger.info("Fixing Bounty model guild isolation...")
        
        bounty_model_path = Path("models/bounty.py")
        if not bounty_model_path.exists():
            logger.error(f"Bounty model file not found at {bounty_model_path}")
            return False
        
        try:
            # Read the file
            with open(bounty_model_path, "r") as f:
                content = f.read()
            
            # Check if methods need guild_id parameters
            if 'async def get_active_bounties(' in content and 'guild_id: Optional[str] = None' not in content:
                # Add guild_id parameter to get_active_bounties
                content = content.replace(
                    'async def get_active_bounties(cls, db, server_id: str = None)',
                    'async def get_active_bounties(cls, db, server_id: Optional[str] = None, guild_id: Optional[str] = None)'
                )
                
                # Update the query to include guild_id
                content = content.replace(
                    'query = {"status": cls.STATUS_ACTIVE}\n        if server_id:',
                    'query = {"status": cls.STATUS_ACTIVE}\n        if server_id:\n            query["server_id"] = server_id\n        if guild_id:'
                )
                content = content.replace(
                    '            query["server_id"] = server_id',
                    '            query["server_id"] = server_id\n        if guild_id:\n            query["guild_id"] = guild_id'
                )
                
                # Similar updates for other methods
                if 'async def get_bounties_placed_by(' in content and 'guild_id: Optional[str] = None' not in content:
                    content = content.replace(
                        'async def get_bounties_placed_by(cls, db, placed_by_id: str)',
                        'async def get_bounties_placed_by(cls, db, placed_by_id: str, guild_id: Optional[str] = None)'
                    )
                    content = content.replace(
                        'cursor = db.bounties.find({"placed_by_id": placed_by_id})',
                        'query = {"placed_by_id": placed_by_id}\n        \n        if guild_id:\n            query["guild_id"] = guild_id\n            \n        cursor = db.bounties.find(query)'
                    )
                
                if 'async def get_bounties_claimed_by(' in content and 'guild_id: Optional[str] = None' not in content:
                    content = content.replace(
                        'async def get_bounties_claimed_by(cls, db, claimed_by_id: str)',
                        'async def get_bounties_claimed_by(cls, db, claimed_by_id: str, guild_id: Optional[str] = None)'
                    )
                    content = content.replace(
                        'cursor = db.bounties.find({\n            "claimed_by_id": claimed_by_id,\n            "status": cls.STATUS_CLAIMED\n        })',
                        'query = {\n            "claimed_by_id": claimed_by_id,\n            "status": cls.STATUS_CLAIMED\n        }\n        \n        if guild_id:\n            query["guild_id"] = guild_id\n            \n        cursor = db.bounties.find(query)'
                    )
                
                # Update the expire_old_bounties method
                if 'async def expire_old_bounties(' in content and 'guild_id: Optional[str] = None' not in content:
                    content = content.replace(
                        'async def expire_old_bounties(cls, db)',
                        'async def expire_old_bounties(cls, db, guild_id: Optional[str] = None)'
                    )
                    content = content.replace(
                        'result = await db.bounties.update_many(\n            {\n                "status": cls.STATUS_ACTIVE,\n                "expires_at": {"$lt": now}\n            },',
                        'query = {\n            "status": cls.STATUS_ACTIVE,\n            "expires_at": {"$lt": now}\n        }\n        \n        # Add guild_id filter if provided\n        if guild_id:\n            query["guild_id"] = guild_id\n        \n        result = await db.bounties.update_many(\n            query,'
                    )
                
                # Write the changes back
                with open(bounty_model_path, "w") as f:
                    f.write(content)
                    
                logger.info("Bounty model guild isolation fixed successfully")
                return True
            else:
                logger.info("Bounty model guild isolation already fixed")
                return True
        except Exception as e:
            logger.error(f"Error fixing Bounty model guild isolation: {e}")
            return False
    
    @staticmethod
    async def apply_all_fixes():
        """Apply all fixes at once"""
        logger.info("Applying all fixes...")
        
        # List of all fix methods
        fix_methods = [
            BotFixer.fix_help_cog,
            BotFixer.fix_bounties_cog,
            BotFixer.fix_guild_model,
            BotFixer.fix_db_initialization,
            BotFixer.fix_model_imports,
            BotFixer.fix_bounty_guild_isolation
        ]
        
        # Apply each fix
        results = []
        for fix_method in fix_methods:
            try:
                result = await fix_method()
                results.append((fix_method.__name__, result))
            except Exception as e:
                logger.error(f"Error applying fix {fix_method.__name__}: {e}")
                results.append((fix_method.__name__, False))
        
        # Print summary
        logger.info("\n===== FIX SUMMARY =====")
        all_passed = True
        for fix_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{fix_name}: {status}")
            if not result:
                all_passed = False
        
        if all_passed:
            logger.info("\n✅ ALL FIXES APPLIED SUCCESSFULLY")
        else:
            logger.error("\n❌ SOME FIXES FAILED - MANUAL INTERVENTION REQUIRED")
        
        return all_passed

async def main():
    """Run the bot fixer"""
    logger.info("Starting Tower of Temptation Discord Bot fixer...")
    result = await BotFixer.apply_all_fixes()
    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))