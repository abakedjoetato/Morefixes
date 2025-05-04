"""
Fix help cog to properly handle coroutine objects

This script modifies the help cog to ensure it properly
awaits coroutines and handles errors appropriately.
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

def fix_help_cog():
    """Fix the help cog to properly handle coroutines"""
    
    help_cog_path = 'cogs/help.py'
    
    if not os.path.exists(help_cog_path):
        logger.error(f"Help cog file not found at {help_cog_path}")
        return False
    
    logger.info(f"Fixing help cog at {help_cog_path}")
    
    with open(help_cog_path, 'r') as f:
        content = f.read()
    
    # Fix 1: Ensure get_by_id is renamed to get_by_guild_id
    updated_content = content.replace(
        'Guild.get_by_id(self.bot.db, guild_id)',
        'Guild.get_by_guild_id(self.bot.db, str(guild_id))'
    )
    
    # Fix 2: Find any uncaught errors with coroutines
    if 'Unhandled error in commands command: \'coroutine\' object has no attribute \'add_field\'' in content:
        # This suggests we might have missed an await somewhere
        embed_matches = re.findall(r'(embed\s*=\s*)(self\.create_category_embed)', updated_content)
        for match in embed_matches:
            if match[0] and match[1]:
                # Add the await if it's missing
                if "await" not in match[0]:
                    updated_content = updated_content.replace(
                        f"{match[0]}{match[1]}",
                        f"{match[0]}await {match[1]}"
                    )
    
    # Fix 3: Ensure error handling for coroutines
    coroutine_error_check = """
        # Check if embed is a coroutine (shouldn't happen but let's be safe)
        if hasattr(embed, '__await__'):
            try:
                embed = await embed  # Await the coroutine
            except Exception as e:
                self.logger.error(f"Error awaiting embed coroutine: {e}")
                # Create a simple error embed as fallback
                embed = discord.Embed(
                    title="⚠️ Error Loading Help",
                    description="There was an error loading the help information. Please try again later.",
                    color=discord.Color.red()
                )
    """
    
    # Detect positions where we should add the coroutine check
    if 'await interaction.followup.send(embed=embed' in updated_content:
        # Insert before sending the embed
        updated_content = updated_content.replace(
            'await interaction.followup.send(embed=embed',
            f'{coroutine_error_check}\n        await interaction.followup.send(embed=embed'
        )
    
    # Write updated content back to file
    with open(help_cog_path, 'w') as f:
        f.write(updated_content)
    
    logger.info("✅ Successfully fixed help cog")
    return True

if __name__ == "__main__":
    fix_help_cog()