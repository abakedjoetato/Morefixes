"""
Helper utilities for the Discord bot
"""
import logging
import os
import asyncio
from typing import Any, Dict, List, Optional, Union, Callable
import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

def is_home_guild_admin(bot, user_id: int) -> bool:
    """Check if a user is an admin of the home guild
    
    Args:
        bot: Discord bot instance
        user_id: Discord user ID to check
        
    Returns:
        True if the user is an admin of the home guild, False otherwise
    """
    # Check if bot has home_guild_id attribute
    if not hasattr(bot, 'home_guild_id') or not bot.home_guild_id:
        # Try to get home_guild_id from environment
        home_guild_id = os.environ.get('HOME_GUILD_ID')
        if not home_guild_id:
            # No home guild set
            return False
        try:
            bot.home_guild_id = int(home_guild_id)
        except (ValueError, TypeError):
            # Invalid home_guild_id
            return False
    
    # Get home guild
    home_guild = bot.get_guild(bot.home_guild_id)
    if not home_guild:
        # Bot is not in home guild
        return False
    
    # Get member
    member = home_guild.get_member(user_id)
    if not member:
        # User is not in home guild
        return False
    
    # Check if user is an admin
    return member.guild_permissions.administrator or member.id == bot.owner_id
    
def has_admin_permission(ctx) -> bool:
    """Check if a user has admin permission in the current guild
    
    Args:
        ctx: Command context
        
    Returns:
        True if the user has admin permission, False otherwise
    """
    # Check if user is bot owner
    if ctx.author.id == ctx.bot.owner_id:
        return True
        
    # Check if user is home guild admin
    if is_home_guild_admin(ctx.bot, ctx.author.id):
        return True
        
    # Check if user has admin permission in the current guild
    if ctx.guild and ctx.author.guild_permissions.administrator:
        return True
        
    return False
    
def has_mod_permission(ctx) -> bool:
    """Check if a user has moderator permission in the current guild
    
    Args:
        ctx: Command context
        
    Returns:
        True if the user has moderator permission, False otherwise
    """
    # Admin permissions include mod permissions
    if has_admin_permission(ctx):
        return True
        
    # Check for specific mod permissions
    if ctx.guild and ctx.author.guild_permissions.manage_messages:
        return True
        
    # Check if user has a mod role
    if ctx.guild:
        # Try to get mod roles from guild settings
        guild_id = str(ctx.guild.id)
        try:
            # This part would normally query the database for mod roles
            # For now, just check for basic mod role names
            mod_role_names = ['mod', 'moderator']
            for role in ctx.author.roles:
                if role.name.lower() in mod_role_names:
                    return True
        except Exception as e:
            logger.error(f"Error checking mod roles: {e}")
        
    return False
    
async def get_guild_premium_tier(db, guild_id: str) -> int:
    """Get premium tier for a guild
    
    Args:
        db: Database connection
        guild_id: Discord guild ID
        
    Returns:
        Premium tier (0-3)
    """
    # Get guild from database
    guild_coll = db["guilds"]
    guild_doc = await guild_coll.find_one({"guild_id": str(guild_id)})
    
    if not guild_doc:
        return 0
        
    return guild_doc.get("premium_tier", 0)
    
async def update_voice_channel_name(bot, channel_id: int, name: str) -> bool:
    """Update voice channel name
    
    Args:
        bot: Discord bot instance
        channel_id: Voice channel ID
        name: New channel name
        
    Returns:
        True if successful, False otherwise
    """
    try:
        channel = bot.get_channel(channel_id)
        if not channel:
            channel = await bot.fetch_channel(channel_id)
            
        if not channel:
            return False
            
        await channel.edit(name=name)
        return True
    except Exception as e:
        logger.error(f"Failed to update voice channel name: {e}")
        return False

def format_datetime(dt) -> str:
    """Format a datetime object into a string
    
    Args:
        dt: Datetime object
        
    Returns:
        Formatted datetime string
    """
    if not dt:
        return "Unknown"
        
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    
def format_time_ago(dt) -> str:
    """Format a datetime object into a human-readable 'time ago' string
    
    Args:
        dt: Datetime object
        
    Returns:
        Human-readable 'time ago' string (e.g., "5 minutes ago", "2 hours ago")
    """
    if not dt:
        return "Unknown"
        
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:  # 7 days
        days = int(seconds // 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:  # 30 days
        weeks = int(seconds // 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif seconds < 31536000:  # 365 days
        months = int(seconds // 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = int(seconds // 31536000)
        return f"{years} year{'s' if years != 1 else ''} ago"

def format_duration(seconds: int) -> str:
    """Format a duration in seconds into a human-readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        sec = seconds % 60
        return f"{minutes}m {sec}s"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"

def format_currency(amount: Union[int, float]) -> str:
    """Format a currency amount
    
    Args:
        amount: Currency amount
        
    Returns:
        Formatted currency string
    """
    return f"{amount:,}"

def calculate_kd_ratio(kills: int, deaths: int) -> float:
    """Calculate a K/D ratio
    
    Args:
        kills: Number of kills
        deaths: Number of deaths
        
    Returns:
        K/D ratio (kills / deaths, with deaths=1 if deaths=0)
    """
    if deaths == 0:
        deaths = 1
    return kills / deaths

def is_feature_enabled(guild_doc: Dict[str, Any], feature_name: str) -> bool:
    """Check if a feature is enabled for a guild
    
    Args:
        guild_doc: Guild document from the database
        feature_name: Name of the feature to check
        
    Returns:
        True if the feature is enabled, False otherwise
    """
    # Premium tier requirements for different features
    feature_requirements = {
        'bounties': 2,
        'rivalries': 1,
        'factions': 2,
        'events': 1,
        'leaderboards': 0,
        'history': 0,
        'stats': 0,
        'kill_feed': 0,
    }
    
    # Get required tier for the feature
    required_tier = feature_requirements.get(feature_name, 3)
    
    # Get guild premium tier (default to 0)
    guild_tier = guild_doc.get('premium_tier', 0)
    
    # Check if the guild meets the required tier
    return guild_tier >= required_tier

async def paginate_embeds(ctx, embeds: List[discord.Embed], timeout: int = 180):
    """Create a paginated view of embeds
    
    Args:
        ctx: Command context
        embeds: List of embeds to paginate
        timeout: Timeout in seconds for the pagination controls
    """
    if not embeds:
        await ctx.send("No data to display.")
        return
        
    if len(embeds) == 1:
        await ctx.send(embed=embeds[0])
        return
    
    # Create a simple custom paginator view
    class PaginationView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=timeout)
            self.current_page = 0
            self.embeds = embeds
        
        @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
        async def previous_button(self, button, interaction):
            self.current_page = max(0, self.current_page - 1)
            await interaction.response.edit_message(embed=self.embeds[self.current_page])
        
        @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
        async def next_button(self, button, interaction):
            self.current_page = min(len(self.embeds) - 1, self.current_page + 1)
            await interaction.response.edit_message(embed=self.embeds[self.current_page])
    
    # Send the first embed with pagination view
    view = PaginationView()
    if hasattr(ctx, 'interaction') and ctx.interaction:
        await ctx.interaction.response.send_message(embed=embeds[0], view=view)
    else:
        await ctx.send(embed=embeds[0], view=view)

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size
    
    Args:
        lst: List to split
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def normalize_weapon_name(weapon: str) -> str:
    """Normalize weapon name to consistent format
    
    Args:
        weapon: Raw weapon name from logs
        
    Returns:
        Normalized weapon name
    """
    if not weapon:
        return "Unknown"
        
    # Convert to lowercase for comparison
    weapon = weapon.lower().strip()
    
    # Handle common variations
    if 'suicide' in weapon or 'killed_self' in weapon:
        return "Suicide"
    elif 'vehicle' in weapon:
        return "Vehicle"
    elif 'fall' in weapon:
        return "Fall Damage"
    elif 'relocation' in weapon:
        return "Relocation"
    
    # Remove unnecessary prefixes
    prefixes = ['weapon_', 'item_', 'gadget_']
    for prefix in prefixes:
        if weapon.startswith(prefix):
            weapon = weapon[len(prefix):]
    
    # Capitalize for display
    return weapon.title()

async def throttle(coro, max_calls: int, interval: float, key: Optional[Callable] = None):
    """Throttle a coroutine to limit execution rate
    
    Args:
        coro: Coroutine to throttle
        max_calls: Maximum number of calls in the interval
        interval: Interval in seconds
        key: Optional function to generate a key for tracking calls
        
    Returns:
        Result of the coroutine
    """
    # Use default key function if none provided
    if key is None:
        key = lambda: "default"
    
    # Initialize throttling state if not already done
    if not hasattr(throttle, "_state"):
        throttle._state = {}
    
    # Get or create throttling state for this key
    key_value = key()
    if key_value not in throttle._state:
        throttle._state[key_value] = {"calls": 0, "reset_at": asyncio.get_event_loop().time() + interval}
    
    state = throttle._state[key_value]
    
    # Check if we need to reset the counter
    now = asyncio.get_event_loop().time()
    if now >= state["reset_at"]:
        state["calls"] = 0
        state["reset_at"] = now + interval
    
    # Check if we're at the limit
    if state["calls"] >= max_calls:
        wait_time = state["reset_at"] - now
        logger.debug(f"Throttling {coro.__name__}: waiting {wait_time:.2f}s")
        await asyncio.sleep(wait_time)
        # Recursively call ourselves after waiting
        return await throttle(coro, max_calls, interval, key)
    
    # Increment counter and run the coroutine
    state["calls"] += 1
    return await coro
    
async def confirm(ctx, message: str = "Are you sure?", timeout: int = 60, delete_after: bool = True) -> bool:
    """Ask for confirmation before proceeding with an action
    
    Args:
        ctx: Command context
        message: Message to show
        timeout: Timeout in seconds
        delete_after: Whether to delete the confirmation message after
        
    Returns:
        True if confirmed, False otherwise
    """
    class ConfirmView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=timeout)
            self.value = None
            
        @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
        async def yes_button(self, button, interaction):
            self.value = True
            self.stop()
            
        @discord.ui.button(label="No", style=discord.ButtonStyle.red)
        async def no_button(self, button, interaction):
            self.value = False
            self.stop()
            
    view = ConfirmView()
    
    # Send the confirmation message
    msg = await ctx.send(message, view=view)
    
    # Wait for a response
    await view.wait()
    
    # Delete the message if needed
    if delete_after:
        try:
            await msg.delete()
        except Exception:
            pass
    
    return view.value is True

def get_bot_name(bot, guild) -> str:
    """Get the bot's display name in a guild
    
    Args:
        bot: The Discord bot instance
        guild: The Discord guild
        
    Returns:
        The bot's display name (nickname or username)
    """
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