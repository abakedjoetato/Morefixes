"""
Tower of Temptation PvP Statistics Discord Bot

This is the main entry point for the Discord bot. It handles:
1. Loading environment variables
2. Setting up Discord client
3. Connecting to MongoDB
4. Loading cogs (command modules)
5. Starting the bot
"""
import os
import sys
import asyncio
import logging
import traceback
from datetime import datetime

import discord
from discord.ext import commands

from utils.env_config import validate_environment, configure_logging
from utils.db import initialize_db, close_db_connection

# Set up logging
configure_logging()
logger = logging.getLogger(__name__)

# Check that we have our required environment variables
if not validate_environment():
    logger.critical("Missing critical environment variables. Bot cannot start.")
    sys.exit(1)

# Get environment settings
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
BOT_APPLICATION_ID = os.environ.get('BOT_APPLICATION_ID')
COMMAND_PREFIX = os.environ.get('COMMAND_PREFIX', '!')
HOME_GUILD_ID = os.environ.get('HOME_GUILD_ID')
DEBUG_MODE = os.environ.get('DEBUG', 'false').lower() in ('true', '1', 'yes', 'y')

# Set up intents (what events the bot will receive)
intents = discord.Intents.default()
intents.guilds = True           # For server join/leave events
intents.guild_messages = True   # For message commands
intents.message_content = True  # For reading message content
intents.members = True          # For member info and nickname functions

# Initialize the bot with command prefix and intents
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, application_id=BOT_APPLICATION_ID)

# Add background_tasks dictionary to track running tasks
bot.background_tasks = {}

# Add sftp_connections dictionary to track SFTP connections
bot.sftp_connections = {}

# Track bot startup time
start_time = datetime.utcnow()

@bot.event
async def on_ready():
    """Called when the bot is ready and connected to Discord."""
    logger.info(f"Bot connected to Discord as {bot.user} (ID: {bot.user.id})")
    logger.info(f"Bot is in {len(bot.guilds)} guilds")
    
    # Log some guild details in debug mode
    if DEBUG_MODE:
        for guild in bot.guilds:
            logger.debug(f"  - {guild.name} (ID: {guild.id})")
    
    # Set bot status
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="PvP battles | !help"
    )
    await bot.change_presence(activity=activity)
    
    # Start auto-bounty system background task
    try:
        from utils.auto_bounty import AutoBountySystem
        
        # Create task for auto-bounty system (runs every 5 minutes)
        if 'auto_bounty_task' not in bot.background_tasks:
            logger.info("Starting auto-bounty system background task...")
            auto_bounty_task = asyncio.create_task(
                AutoBountySystem.start_auto_bounty_task(bot, interval_minutes=5)
            )
            bot.background_tasks['auto_bounty_task'] = auto_bounty_task
            logger.info("Auto-bounty system started successfully")
    except Exception as e:
        logger.error(f"Failed to start auto-bounty system: {e}", exc_info=True)
    
    # Update status
    try:
        home_guild = bot.get_guild(int(HOME_GUILD_ID)) if HOME_GUILD_ID else None
        status_channel = next((channel for channel in home_guild.text_channels if 'status' in channel.name), None) if home_guild else None
        
        if status_channel:
            uptime = (datetime.utcnow() - start_time).total_seconds()
            await status_channel.send(f"Bot is online! Startup took {uptime:.2f} seconds.")
    except Exception as e:
        logger.error(f"Failed to send startup message: {e}")
    
    logger.info("Bot is ready for commands!")

@bot.event
async def on_guild_join(guild):
    """Called when the bot joins a new guild."""
    logger.info(f"Bot has been added to new guild: {guild.name} (ID: {guild.id})")
    
    # Try to find a general or bot channel to send welcome message
    welcome_channel = None
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            if 'general' in channel.name.lower() or 'bot' in channel.name.lower():
                welcome_channel = channel
                break
    
    if not welcome_channel:
        # If no preferred channel found, use the first one we can send to
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                welcome_channel = channel
                break
    
    if welcome_channel:
        await welcome_channel.send(
            "👋 Thanks for adding Tower of Temptation PvP Statistics Bot!\n\n"
            "Type `/` to see available commands or use `/help` for more information.\n\n"
            "To get started, server admins can use `/server setup` to configure game server connections."
        )

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for traditional commands."""
    if isinstance(error, commands.CommandNotFound):
        return
    
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument: {error.param.name}")
        return
    
    if isinstance(error, commands.BadArgument):
        await ctx.send(f"Invalid argument: {error}")
        return
    
    # Log the full error with traceback
    logger.error(f"Command error in {ctx.command}: {error}", exc_info=error)
    
    # Send a user-friendly error message
    await ctx.send(
        f"❌ An error occurred while executing the command: `{error}`\n"
        "The error has been logged and will be looked into."
    )

@bot.tree.error
async def on_app_command_error(interaction, error):
    """Global error handler for application (/) commands."""
    if isinstance(error, commands.MissingRequiredArgument):
        await interaction.response.send_message(
            f"Missing required argument: {error.param.name}", 
            ephemeral=True
        )
        return
    
    if isinstance(error, commands.BadArgument):
        await interaction.response.send_message(
            f"Invalid argument: {error}", 
            ephemeral=True
        )
        return
    
    # Log the full error with traceback
    command_name = interaction.command.name if interaction.command else "Unknown"
    logger.error(f"App command error in {command_name}: {error}", exc_info=error)
    
    # Check if the interaction is still valid and not already responded to
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ An error occurred while executing the command. The error has been logged.",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                "❌ An error occurred while executing the command. The error has been logged.",
                ephemeral=True
            )
    except discord.errors.NotFound:
        logger.debug("Failed to respond to interaction - likely already timed out")
    except Exception as e:
        logger.error(f"Error while responding to error: {e}")

async def load_cogs():
    """Load all cogs (extensions) from the cogs directory."""
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('_'):
            # Strip the .py extension
            cog_name = filename[:-3]
            
            try:
                await bot.load_extension(f'cogs.{cog_name}')
                logger.info(f"Loaded cog: {cog_name}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog_name}: {e}", exc_info=True)

async def initialize_bot(force_sync=False):
    """Initialize the bot and database.
    
    Args:
        force_sync: Whether to force a sync of all commands
        
    Returns:
        The initialized bot object
    """
    # Initialize the database connection
    logger.info("Initializing database connection...")
    db_manager = await initialize_db()
    # Attach the database manager to the bot for global access
    bot.db = db_manager
    logger.info("Database connection established")
    
    # Load all cogs
    logger.info("Loading cogs...")
    await load_cogs()
    
    # Sync commands if requested
    if force_sync:
        logger.info("Syncing commands globally...")
        try:
            # Ensure bot is ready before syncing commands
            if not bot.is_ready():
                logger.warning("Bot not ready, waiting before syncing commands")
                await bot.wait_until_ready()
                logger.info("Bot ready, proceeding with command sync")
            
            # Wait a short time to ensure all internal Discord.py caches are initialized
            await asyncio.sleep(2)
            
            # Clear commands in development guild if specified
            if HOME_GUILD_ID:
                try:
                    guild = discord.Object(id=int(HOME_GUILD_ID))
                    bot.tree.clear_commands(guild=guild)
                    await bot.tree.sync(guild=guild)
                    logger.info(f"Cleared and synced commands in development guild {HOME_GUILD_ID}")
                except Exception as guild_error:
                    logger.error(f"Error syncing guild commands: {guild_error}", exc_info=True)
            
            # Sync commands globally with additional protection
            try:
                bot.tree.clear_commands()
                await asyncio.sleep(1)  # Rate limit protection
                await bot.tree.sync()
                logger.info("Commands synced globally")
            except Exception as global_error:
                logger.error(f"Error syncing global commands: {global_error}", exc_info=True)
                
        except Exception as e:
            logger.error(f"Error in command sync process: {e}", exc_info=True)
            # Don't let this error block bot startup, it can sync later
    
    return bot

async def startup():
    """Initialize the bot and database, then start the bot."""
    try:
        # Initialize the bot
        logger.info("Initializing bot...")
        initialized_bot = await initialize_bot(force_sync=False)  # Initialize without syncing
        
        # Start the bot first
        logger.info("Starting bot...")
        # Run the bot in the background
        bot_task = asyncio.create_task(initialized_bot.start(DISCORD_TOKEN))
        
        # Wait for the bot to be fully ready
        await asyncio.sleep(5)
        
        # Now sync commands when bot is surely ready
        if initialized_bot.is_ready():
            logger.info("Bot is ready, syncing commands now...")
            try:
                # Try syncing global commands
                await initialized_bot.tree.sync()
                logger.info("Successfully synced global commands")
                
                # If home guild is set, sync there too
                if HOME_GUILD_ID:
                    guild = discord.Object(id=int(HOME_GUILD_ID))
                    await initialized_bot.tree.sync(guild=guild)
                    logger.info(f"Successfully synced commands to home guild {HOME_GUILD_ID}")
            except Exception as sync_error:
                logger.error(f"Failed to sync commands: {sync_error}", exc_info=True)
                logger.info("Bot will continue running, commands may not be fully available")
        else:
            logger.warning("Bot not ready after waiting, commands will not be synced now")
        
        # Wait for the bot to finish (which should be never unless it disconnects)
        await bot_task
        
    except Exception as e:
        logger.critical(f"Error during startup: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Close the database connection
        await close_db_connection()

if __name__ == "__main__":
    # Run the startup process
    logger.info("Tower of Temptation PvP Statistics Bot starting up...")
    
    # Set up asyncio event loop
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(startup())
    except KeyboardInterrupt:
        logger.info("Bot shutting down...")
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
    finally:
        loop.close()
        logger.info("Bot has shut down. Goodbye!")