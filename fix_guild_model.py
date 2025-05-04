"""
Fix missing Guild.get_by_id method

This script adds the get_by_id method to the Guild model class
to resolve the error in the help command.
"""
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_guild_model():
    """Add the get_by_id method to the Guild model"""
    
    # Check if the models/guild.py file exists
    if os.path.exists('models/guild.py'):
        guild_model_path = 'models/guild.py'
    else:
        guild_model_path = 'models.py'  # Fallback to models.py
    
    logger.info(f"Fixing Guild model in {guild_model_path}")
    
    with open(guild_model_path, 'r') as f:
        content = f.read()
    
    # Check if get_by_guild_id method exists but get_by_id doesn't
    if 'async def get_by_guild_id(' in content and 'async def get_by_id(' not in content:
        # Find the class definition
        if 'class Guild(' in content:
            # Add the get_by_id method
            get_by_id_method = '''
    @classmethod
    async def get_by_id(cls, db, guild_id):
        """Get a guild by its Discord ID (alias for get_by_guild_id)"""
        return await cls.get_by_guild_id(db, str(guild_id))
'''
            # Find a good position to insert the method
            last_method_pos = content.rfind('@classmethod')
            if last_method_pos != -1:
                # Find the end of the last method
                method_end = content.find('\n\n', last_method_pos)
                if method_end != -1:
                    # Insert after the last method
                    updated_content = content[:method_end] + '\n' + get_by_id_method + content[method_end:]
                    
                    # Write the updated content back
                    with open(guild_model_path, 'w') as f:
                        f.write(updated_content)
                    
                    logger.info("✅ Successfully added get_by_id method to Guild model")
                    return True
                else:
                    # Append to the end of the file
                    with open(guild_model_path, 'a') as f:
                        f.write('\n' + get_by_id_method)
                    
                    logger.info("✅ Successfully added get_by_id method to Guild model (appended to end)")
                    return True
            else:
                logger.error("Could not find a suitable position to insert get_by_id method")
                return False
        else:
            logger.error("Guild class not found in the file")
            return False
    else:
        if 'async def get_by_id(' in content:
            logger.info("get_by_id method already exists in Guild model - no fix needed")
        else:
            logger.error("get_by_guild_id method not found in Guild model")
        return False

if __name__ == "__main__":
    fix_guild_model()