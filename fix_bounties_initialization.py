"""
Fix bounties cog database initialization warning

This script modifies the bounties cog to properly handle database initialization
and avoid the 'Database not properly initialized' warning.
"""
import os
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_bounties_cog():
    """Fix database initialization in the bounties cog"""
    
    bounties_cog_path = 'cogs/bounties.py'
    
    if not os.path.exists(bounties_cog_path):
        logger.error(f"Bounties cog file not found at {bounties_cog_path}")
        return False
    
    logger.info(f"Fixing bounties cog at {bounties_cog_path}")
    
    with open(bounties_cog_path, 'r') as f:
        content = f.read()
    
    # Fix 1: Improve database initialization check
    db_check_pattern = r'if not hasattr\(self\.bot, \'db\'\) or self\.bot\.db is None:'
    if re.search(db_check_pattern, content):
        updated_content = re.sub(
            db_check_pattern,
            'if not hasattr(self.bot, \'db\') or self.bot.db is None or not hasattr(self.bot, \'database\') or self.bot.database is None:',
            content
        )
    else:
        updated_content = content
    
    # Fix 2: Add missing Bounty class constants
    if 'class Bounty(' in updated_content and 'SOURCE_AUTO = ' not in updated_content:
        bounty_constants = """
    # Bounty source constants
    SOURCE_AUTO = 'auto'
    SOURCE_PLAYER = 'player'
    SOURCE_ADMIN = 'admin'
"""
        # Find the Bounty class and add constants
        updated_content = updated_content.replace(
            'class Bounty(',
            f'{bounty_constants}\nclass Bounty('
        )
    
    # Fix 3: Ensure create method exists on Bounty class
    if 'async def create(' not in updated_content and 'class Bounty(' in updated_content:
        create_method = """
    @classmethod
    async def create(cls, db, guild_id, target_id, issuer_id, reason, reward, expiry=None, source='player'):
        # Create a new bounty
        bounty = cls(
            guild_id=guild_id,
            target_id=target_id,
            issuer_id=issuer_id,
            reason=reason,
            reward=reward,
            expiry=expiry,
            source=source
        )
        result = await db[cls.collection_name].insert_one(bounty.to_dict())
        bounty._id = result.inserted_id
        return bounty
"""
        # Find the end of the Bounty class
        bounty_class_end = updated_content.find('class', updated_content.find('class Bounty(') + 10)
        if bounty_class_end == -1:
            # If we can't find the end, append to the end of the file
            updated_content += create_method
        else:
            # Insert before the next class definition
            updated_content = updated_content[:bounty_class_end] + create_method + updated_content[bounty_class_end:]
    
    # Fix 4: Fix any incomplete try/except blocks
    # This is a bit risky to do with regex, but let's look for obvious issues
    try_pattern = r'try:[\s\n]*(?!except|finally)(@[a-z_])'
    updated_content = re.sub(
        try_pattern,
        'try:\n        pass\n        \\1',
        updated_content
    )
    
    # Write updated content back to file
    with open(bounties_cog_path, 'w') as f:
        f.write(updated_content)
    
    logger.info("✅ Successfully fixed bounties cog")
    return True

if __name__ == "__main__":
    fix_bounties_cog()