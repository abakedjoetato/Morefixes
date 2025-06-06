"""
Killfeed commands and background tasks for monitoring kill feeds
"""
import logging
import asyncio
import time
import os
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from models.guild import Guild
from models.server import Server
from models.player import Player
from utils.sftp import SFTPClient
from utils.parsers import CSVParser
from utils.embed_builder import EmbedBuilder
from utils.helpers import has_admin_permission

logger = logging.getLogger(__name__)

async def server_id_autocomplete(interaction, current):
    """Autocomplete for server IDs"""
    try:
        # Get user's guild ID
        guild_id = interaction.guild_id

        # Get cached server data or fetch it
        cog = interaction.client.get_cog("Killfeed")
        if not cog:
            cog = interaction.client.get_cog("Stats")  # Fallback to Stats cog cache

        if not cog or not hasattr(cog, "server_autocomplete_cache"):
            # Initialize cache if it doesn't exist
            if not hasattr(cog, "server_autocomplete_cache"):
                cog.server_autocomplete_cache = {}

        # Update cache if needed
        if guild_id not in cog.server_autocomplete_cache or \
           (datetime.now() - cog.server_autocomplete_cache.get(guild_id, {}).get("last_update", datetime.min)).total_seconds() > 300:

            # Fetch guild data
            guild_data = await interaction.client.db.guilds.find_one({"guild_id": guild_id})

            if guild_data and "servers" in guild_data:
                # Update cache
                cog.server_autocomplete_cache[guild_id] = {
                    "servers": [
                        {
                            "id": server.get("server_id", ""),
                            "name": server.get("server_name", "Unknown Server")
                        }
                        for server in guild_data.get("servers", [])
                    ],
                    "last_update": datetime.now()
                }

        # Get servers from cache
        servers = cog.server_autocomplete_cache.get(guild_id, {}).get("servers", [])

        # Filter by current input
        filtered_servers = [
            app_commands.Choice(name=server['name'], value=server['id'])
            for server in servers
            if current.lower() in server['id'].lower() or current.lower() in server['name'].lower()
        ]

        return filtered_servers[:25]

    except Exception as e:
        logger.error(f"Error in server autocomplete: {e}", exc_info=True)
        return [app_commands.Choice(name="Error loading servers", value="error")]

class Killfeed(commands.Cog):
    """Killfeed commands and background tasks"""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(name="killfeed", description="Killfeed commands")
    @commands.guild_only()
    async def killfeed(self, ctx):
        """Killfeed command group"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Please specify a subcommand.")

    @killfeed.command(name="start", description="Start monitoring killfeed for a server")
    @app_commands.describe(server_id="Select a server by name to monitor")
    @app_commands.autocomplete(server_id=server_id_autocomplete)
    async def start(self, ctx, server_id: str):
        """Start the killfeed monitor for a server"""
        try:
            # Get guild model for themed embed
            guild_data = None
            guild_model = None
            try:
                guild_data = await self.bot.db.guilds.find_one({"guild_id": ctx.guild.id})
                if guild_data:
                    guild_model = Guild(self.bot.db, guild_data)
            except Exception as e:
                logger.warning(f"Error getting guild model: {e}")

            # Check permissions
            if not await self._check_permission(ctx):
                return

            # Get guild data
            guild_data = await self.bot.db.guilds.find_one({"guild_id": ctx.guild.id})
            if not guild_data:
                embed = EmbedBuilder.create_error_embed(
                    "Error",
                    "This guild is not set up. Please use the setup commands first."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # Check if server exists in this guild
            server_exists = False
            for server in guild_data.get("servers", []):
                if server.get("server_id") == server_id:
                    server_exists = True
                    break

            if not server_exists:
                embed = EmbedBuilder.create_error_embed(
                    "Error",
                    f"Server '{server_id}' not found in this guild. Please use an existing server name."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # Start killfeed monitor
            task_name = f"killfeed_{ctx.guild.id}_{server_id}"

            # Check if task is already running
            if task_name in self.bot.background_tasks:
                # If task exists but is done, remove it
                if self.bot.background_tasks[task_name].done():
                    self.bot.background_tasks.pop(task_name)
                else:
                    embed = EmbedBuilder.create_error_embed(
                        "Already Running",
                        f"Killfeed monitor for server {server_id} is already running."
                    , guild=guild_model)
                    await ctx.send(embed=embed)
                    return

            # Create initial response
            embed = EmbedBuilder.create_base_embed(
                "Starting Killfeed Monitor",
                f"Starting killfeed monitor for server {server_id}..."
            , guild=guild_model)
            message = await ctx.send(embed=embed)

            # Start the task
            task = asyncio.create_task(
                start_killfeed_monitor(self.bot, ctx.guild.id, server_id)
            )
            self.bot.background_tasks[task_name] = task

            # Add callback to handle completion
            task.add_done_callback(
                lambda t: asyncio.create_task(
                    self._handle_task_completion(t, ctx.guild.id, server_id, message)
                )
            )

            # Update response after a short delay
            await asyncio.sleep(2)
            embed = EmbedBuilder.create_success_embed(
                "Killfeed Monitor Started",
                f"Killfeed monitor for server {server_id} has been started successfully."
            , guild=guild_model)
            await message.edit(embed=embed)

        except Exception as e:
            logger.error(f"Error starting killfeed monitor: {e}", exc_info=True)
            embed = EmbedBuilder.create_error_embed(
                "Error",
                f"An error occurred while starting the killfeed monitor: {e}"
            , guild=guild_model)
            await ctx.send(embed=embed)

    @killfeed.command(name="stop", description="Stop monitoring killfeed for a server")
    @app_commands.describe(server_id="Select a server by name to stop monitoring")
    @app_commands.autocomplete(server_id=server_id_autocomplete)
    async def stop(self, ctx, server_id: str):
        """Stop the killfeed monitor for a server"""

        try:
            # Get guild model for themed embed
            guild_data = None
            guild_model = None
            try:
                guild_data = await self.bot.db.guilds.find_one({"guild_id": ctx.guild.id})
                if guild_data:
                    guild_model = Guild(self.bot.db, guild_data)
            except Exception as e:
                logger.warning(f"Error getting guild model: {e}")

            # Check permissions
            if not await self._check_permission(ctx):
                return

            # Check if task is running
            task_name = f"killfeed_{ctx.guild.id}_{server_id}"
            if task_name not in self.bot.background_tasks:
                embed = EmbedBuilder.create_error_embed(
                    "Not Running",
                    f"Killfeed monitor for server {server_id} is not running."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # Cancel the task
            task = self.bot.background_tasks[task_name]
            task.cancel()

            # Remove the task
            self.bot.background_tasks.pop(task_name)

            # Send success message
            embed = EmbedBuilder.create_success_embed(
                "Killfeed Monitor Stopped",
                f"Killfeed monitor for server {server_id} has been stopped successfully."
            , guild=guild_model)
            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Error stopping killfeed monitor: {e}", exc_info=True)
            embed = EmbedBuilder.create_error_embed(
                "Error",
                f"An error occurred while stopping the killfeed monitor: {e}"
            , guild=guild_model)
            await ctx.send(embed=embed)

    @killfeed.command(name="status", description="Check killfeed monitor status")
    async def status(self, ctx):
        """Check the status of killfeed monitors for this guild"""

        try:
            # Get guild model for themed embed
            guild_data = None
            guild_model = None
            try:
                guild_data = await self.bot.db.guilds.find_one({"guild_id": ctx.guild.id})
                if guild_data:
                    guild_model = Guild(self.bot.db, guild_data)
            except Exception as e:
                logger.warning(f"Error getting guild model: {e}")

            # Get guild data
            guild_data = await self.bot.db.guilds.find_one({"guild_id": ctx.guild.id})
            if not guild_data:
                embed = EmbedBuilder.create_error_embed(
                    "Error",
                    "This guild is not set up. Please use the setup commands first."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # Check running tasks for this guild
            running_monitors = []
            for task_name, task in self.bot.background_tasks.items():
                if task_name.startswith(f"killfeed_{ctx.guild.id}_"):
                    parts = task_name.split("_")
                    if len(parts) >= 3:
                        server_id = parts[2]

                        # Find server name
                        server_name = server_id
                        for server in guild_data.get("servers", []):
                            if server.get("server_id") == server_id:
                                server_name = server.get("server_name", server_id)
                                break

                        running_monitors.append({
                            "server_id": server_id,
                            "server_name": server_name,
                            "status": "Running" if not task.done() else "Completed"
                        })

            # Create embed
            if running_monitors:
                embed = EmbedBuilder.create_base_embed(
                    "Killfeed Monitor Status",
                    f"Currently running killfeed monitors for {ctx.guild.name}"
                , guild=guild_model)

                for monitor in running_monitors:
                    embed.add_field(
                        name=f"{monitor['server_name']} ({monitor['server_id']})",
                        value=f"Status: {monitor['status']}",
                        inline=False
                    )
            else:
                embed = EmbedBuilder.create_base_embed(
                    "Killfeed Monitor Status",
                    f"No killfeed monitors are currently running for {ctx.guild.name}."
                , guild=guild_model)

                # Add instructions
                embed.add_field(
                    name="How to Start",
                    value="Use `/killfeed start server:<server_name>` to start monitoring a server.",
                    inline=False
                )

            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Error checking killfeed status: {e}", exc_info=True)
            embed = EmbedBuilder.create_error_embed(
                "Error",
                f"An error occurred while checking killfeed status: {e}"
            , guild=guild_model)
            await ctx.send(embed=embed)

    async def _check_permission(self, ctx) -> bool:
        """Check if user has permission to use the command"""
        # Initialize guild_model to None first to avoid UnboundLocalError
        guild_model = None

        # Check if user has admin permission
        if has_admin_permission(ctx):
            return True

        # If not, send error message
        # Get the guild model for theme
        try:
            guild_model = await Guild.get_by_id(self.bot.db, ctx.guild.id)
        except Exception as e:
            logger.warning(f"Error getting guild model in permission check: {e}")

        embed = EmbedBuilder.create_error_embed(
            "Permission Denied",
            "You need administrator permission or the designated admin role to use this command.",
            guild=guild_model)
        await ctx.send(embed=embed, ephemeral=True)
        return False

    async def _handle_task_completion(self, task, guild_id, server_id, message):
        """Handle completion of a background task"""
        try:
            # Check if task was cancelled
            if task.cancelled():
                logger.info(f"Killfeed monitor for server {server_id} was cancelled.")
                return

            # Check if task completed with an exception
            if task.exception():
                logger.error(
                    f"Killfeed monitor for server {server_id} failed: {task.exception()}", 
                    exc_info=task.exception()
                )

                # Update message if still exists
                try:
                    # Find the guild for the server
                    try:
                        guild_data = await self.bot.db.guilds.find_one({"servers.server_id": server_id})
                        guild_model = None
                        if guild_data:
                            guild_model = Guild(self.bot.db, guild_data)

                        embed = await EmbedBuilder.create_error_embed(
                            "Killfeed Monitor Failed",
                            f"The killfeed monitor for server {server_id} has failed: {task.exception()}",
                            guild=guild_model
                        )
                    except Exception as ex:
                        # Fallback to simple error embed
                        logger.error(f"Error creating themed embed: {ex}")
                        embed = await EmbedBuilder.create_error_embed(
                            "Killfeed Monitor Failed",
                            f"The killfeed monitor for server {server_id} has failed: {task.exception()}"
                        )
                    await message.edit(embed=embed)
                except:
                    pass

                return

            # Task completed normally
            logger.info(f"Killfeed monitor for server {server_id} completed successfully.")

        except Exception as e:
            logger.error(f"Error handling task completion: {e}", exc_info=True)


async def start_killfeed_monitor(bot, guild_id: int, server_id: str):
    """Background task to monitor killfeed for a server"""
    from config import KILLFEED_REFRESH_INTERVAL

    # Initialize reconnection tracking
    reconnect_attempts = 0
    max_reconnect_attempts = 10
    backoff_time = 5  # Start with 5 seconds
    last_successful_connection = time.time()

    # Check if we actually have server data in the database
    # This prevents errors when the bot starts up with empty database
    if await bot.db.guilds.count_documents({"guild_id": guild_id, "servers": {"$exists": True, "$ne": []}}) == 0:
        logger.warning(f"No servers found for guild {guild_id} - skipping killfeed monitor")
        return

    # Check if guild exists in bot's cache
    discord_guild = bot.get_guild(int(guild_id))
    if not discord_guild:
        logger.error(f"Guild {guild_id} not found in bot's cache - skipping killfeed monitor")
        return

    logger.info(f"Starting killfeed monitor for server {server_id} in guild {guild_id}")

    try:
        # Get server data
        server = await Server.get_by_id(bot.db, server_id, guild_id)
        if not server:
            logger.error(f"Server {server_id} not found in guild {guild_id}")
            return

        # Verify channel configuration
        killfeed_channel_id = server.killfeed_channel_id
        channel_configured = True
        if not killfeed_channel_id:
            logger.warning(f"No killfeed channel configured for server {server_id} in guild {guild_id}")
            # Send a direct message to administrators about missing configuration
            try:
                guild_model = await Guild.get_by_id(bot.db, guild_id)
                if guild_model and guild_model.admin_role_id:
                    # Try to get admin role
                    guild = bot.get_guild(guild_id)
                    if guild:
                        admin_role = guild.get_role(guild_model.admin_role_id)
                        if admin_role and admin_role.members:
                            admin = admin_role.members[0]  # Get first admin
                            await admin.send(f"⚠️ Killfeed notifications for server {server.name} cannot be sent because no killfeed channel is configured. Please use `/setup setup_channels` to set one up.")
            except Exception as notify_e:
                logger.warning(f"Could not notify admin about missing killfeed channel: {notify_e}")
            # Instead of returning, we'll continue but mark that we don't have a channel
            channel_configured = False
            logger.info(f"Continuing killfeed monitor for server {server_id} without a channel - data will be processed but not displayed")

        # Create SFTP client connection
        sftp_client = SFTPClient(
            host=server.sftp_host,
            port=server.sftp_port,
            username=server.sftp_username,
            password=server.sftp_password,
            server_id=server.id
        )

        # Try to connect
        sftp_connected = False
        connected = await sftp_client.connect()
        if not connected:
            logger.error(f"Failed to connect to SFTP server for {server_id}: {sftp_client.last_error}")
            # Try to notify an admin if possible
            try:
                guild = bot.get_guild(guild_id)
                if guild and guild.owner:
                    await guild.owner.send(f"⚠️ Could not connect to SFTP server for {server.name}. Error: {sftp_client.last_error}")
            except Exception:
                pass  # Silently ignore if we can't message the owner
            # Don't return here, we'll try to reconnect later
            sftp_connected = False
        else:
            sftp_connected = True

        # Store client for later use, even if not connected
        bot.sftp_connections[f"{guild_id}_{server_id}"] = sftp_client

        # If not connected, we'll log it and try to reconnect periodically
        if not sftp_connected:
            logger.warning(f"Not connected to SFTP for server {server_id}, will attempt periodic reconnection")

        # Get killfeed channel
        guild = bot.get_guild(guild_id)
        if not guild:
            logger.error(f"Guild {guild_id} not found - will continue processing data without sending Discord messages")
            # Don't return here, we'll still process data for when the guild is available later

        killfeed_channel = None
        if channel_configured and guild:  # Only try to get the channel if guild exists
            killfeed_channel_id = server.killfeed_channel_id
            # Log channel ID details for diagnosis
            logger.info(f"Retrieved killfeed_channel_id: {killfeed_channel_id} (type: {type(killfeed_channel_id).__name__})")

            # Ensure the channel ID is an integer
            try:
                if killfeed_channel_id is not None:
                    # Convert to int if it's not already and handle string numbers
                    if not isinstance(killfeed_channel_id, int):
                        killfeed_channel_id = int(str(killfeed_channel_id).strip())
                        logger.info(f"Converted killfeed_channel_id to int: {killfeed_channel_id}")

                    # Try to get the channel
                    killfeed_channel = guild.get_channel(killfeed_channel_id)
                    logger.info(f"Attempted to get channel: {killfeed_channel_id}, result: {killfeed_channel is not None}")

                    if not killfeed_channel:
                        try:
                            # Try to fetch channel through HTTP API in case it's not in cache
                            logger.info(f"Channel not in cache, trying HTTP fetch for: {killfeed_channel_id}")
                            killfeed_channel = await guild.fetch_channel(killfeed_channel_id)
                            logger.info(f"HTTP fetch successful for channel: {killfeed_channel.name if killfeed_channel else None}")
                        except discord.NotFound:
                            logger.error(f"Killfeed channel {killfeed_channel_id} not found in guild {guild_id}")
                            channel_configured = False
                            logger.info(f"Channel not found, continuing without killfeed channel for server {server_id}")
                        except Exception as fetch_e:
                            logger.error(f"Error fetching killfeed channel: {fetch_e}")
                            channel_configured = False
                            logger.info(f"Error fetching channel, continuing without killfeed channel for server {server_id}")
                else:
                    logger.warning(f"No killfeed_channel_id found for server {server_id}")
                    channel_configured = False
            except (ValueError, TypeError) as e:
                logger.error(f"Error converting killfeed_channel_id to int: {e}")
                channel_configured = False
        else:
            channel_configured = False
            logger.info(f"Guild or channel not available, continuing without killfeed channel for server {server_id}")

        # Send initial notification to confirm monitor is running
        if channel_configured and killfeed_channel:
            try:
                guild_model = await Guild.get_by_id(bot.db, guild_id)
                embed = EmbedBuilder.create_base_embed(
                    "Killfeed Monitor Active",
                    f"Monitoring killfeed for server {server.name} (ID: {server_id}).",
                    guild=guild_model
                )
                embed.add_field(
                    name="Status", 
                    value="Active and monitoring for new kills", 
                    inline=False
                )
                embed.set_footer(text=f"Started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Powered By Discord.gg/EmeraldServers")
                await killfeed_channel.send(embed=embed)
            except Exception as notify_e:
                logger.warning(f"Could not send startup notification: {notify_e}")
        else:
            logger.info(f"No killfeed channel configured for server {server_id}, monitoring will run silently until channel is configured")

        # Main monitoring loop
        consecutive_errors = 0
        max_consecutive_errors = 5

        while True:
            try:
                # Get latest CSV file across ALL subdirectories
                logger.info(f"Searching for most recent CSV file across ALL world subdirectories for server {server_id}")
                latest_csv = await sftp_client.get_latest_csv_file()
                if not latest_csv:
                    logger.warning(f"No CSV file found for server {server_id} in any subdirectory")
                    # If we haven't found a CSV file for a while, try reconnecting
                    if time.time() - last_successful_connection > 300:  # 5 minutes
                        logger.info(f"No CSV file found for 5 minutes, reconnecting SFTP for server {server_id}")
                        await sftp_client.disconnect()
                        await asyncio.sleep(1)
                        await sftp_client.connect()
                        last_successful_connection = time.time()
                    await asyncio.sleep(KILLFEED_REFRESH_INTERVAL)
                    continue

                # Log which directory the latest CSV file was found in
                csv_dir = os.path.dirname(latest_csv)
                logger.info(f"Found most recent CSV file in directory: {csv_dir}")

                # Get last processed line number
                last_line = server.last_csv_line

                # Get total lines in the file with timeout protection
                try:
                    total_lines = await sftp_client.get_file_size(
                        latest_csv,
                        chunk_size=5000  # Use a reasonable chunk size for better performance
                    )

                    # Reset consecutive errors on success
                    consecutive_errors = 0
                    reconnect_attempts = 0
                    backoff_time = 5
                    last_successful_connection = time.time()

                    # If no new lines, sleep and continue
                    if total_lines <= last_line:
                        await asyncio.sleep(KILLFEED_REFRESH_INTERVAL)
                        continue

                    # Read new lines with timeout protection
                    new_lines = await sftp_client.read_file(
                        latest_csv, 
                        start_line=last_line,
                        max_lines=None,  # Read all new lines
                        chunk_size=1000  # Process in smaller chunks to prevent timeout
                    )
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout reading CSV data for {server_id}, will retry")
                    # Reconnect after timeout
                    await sftp_client.disconnect()
                    await asyncio.sleep(1)
                    connected = await sftp_client.connect()
                    if not connected:
                        logger.error(f"Failed to reconnect after timeout for server {server_id}")
                        consecutive_errors += 1
                    await asyncio.sleep(KILLFEED_REFRESH_INTERVAL)
                    continue
                except Exception as file_e:
                    logger.error(f"Error reading CSV file: {file_e}")
                    consecutive_errors += 1
                    await asyncio.sleep(KILLFEED_REFRESH_INTERVAL)
                    continue

                if not new_lines:
                    logger.debug(f"No new lines in CSV file for server {server_id}")
                    await asyncio.sleep(KILLFEED_REFRESH_INTERVAL)
                    continue

                # Parse new lines
                kill_events = CSVParser.parse_kill_lines(new_lines)

                # Log successful parsing
                if kill_events:
                    logger.info(f"Parsed {len(kill_events)} kill events from {len(new_lines)} lines for server {server_id}")

                # Process each kill event
                processed_events = 0
                # Always process kill events, even if no channel is configured
                for kill_event in kill_events:
                    try:
                        await process_kill_event(bot, server, kill_event, killfeed_channel if killfeed_channel else None)
                        processed_events += 1
                    except Exception as event_e:
                        logger.error(f"Error processing kill event: {event_e}", exc_info=True)

                # Update last processed line only if we successfully processed events
                if processed_events > 0 or len(kill_events) == 0:
                    await server.update_last_csv_line(last_line + len(new_lines))
                    logger.info(f"Updated last CSV line to {last_line + len(new_lines)} for server {server_id}")

                # Reset consecutive errors on success
                consecutive_errors = 0

            except asyncio.CancelledError:
                logger.info(f"Killfeed monitor for server {server_id} cancelled")
                break

            except Exception as e:
                logger.error(f"Error in killfeed monitor for server {server_id}: {e}", exc_info=True)
                consecutive_errors += 1

                # Attempt reconnection if we've had too many consecutive errors
                if consecutive_errors >= max_consecutive_errors:
                    if reconnect_attempts < max_reconnect_attempts:
                        logger.warning(f"Too many consecutive errors ({consecutive_errors}), attempting reconnection for server {server_id}")
                        try:
                            await sftp_client.disconnect()
                            await asyncio.sleep(backoff_time)  # Exponential backoff
                            connected = await sftp_client.connect()
                            if connected:
                                logger.info(f"Successfully reconnected SFTP for server {server_id}")
                                consecutive_errors = 0
                                backoff_time = min(backoff_time * 2, 60)  # Exponential backoff with max of 60 seconds
                            reconnect_attempts += 1
                        except Exception as reconnect_e:
                            logger.error(f"Error during reconnection attempt: {reconnect_e}")
                    else:
                        logger.error(f"Exceeded maximum reconnection attempts for server {server_id}, stopping monitor")
                        # Try to notify an admin if possible
                        try:
                            guild = bot.get_guild(guild_id)
                            if guild and guild.owner:
                                await guild.owner.send(f"⚠️ Killfeed monitor for {server.name} has been stopped due to too many connection failures. Please restart it manually with `/killfeed start`.")
                        except Exception:
                            pass  # Silently ignore if we can't message the owner
                        break

            # Sleep before next check
            await asyncio.sleep(KILLFEED_REFRESH_INTERVAL)

    except asyncio.CancelledError:
        logger.info(f"Killfeed monitor for server {server_id} cancelled")

    except Exception as e:
        logger.error(f"Error in killfeed monitor for server {server_id}: {e}", exc_info=True)

    finally:
        # Clean up resources
        if f"{guild_id}_{server_id}" in bot.sftp_connections:
            client = bot.sftp_connections.pop(f"{guild_id}_{server_id}")
            await client.disconnect()

        logger.info(f"Killfeed monitor for server {server_id} stopped")

        # Try to send notification that monitor has stopped
        try:
            guild = bot.get_guild(guild_id)
            if guild:
                server = await Server.get_by_id(bot.db, server_id, guild_id)
                if server and server.killfeed_channel_id:
                    try:
                        # Ensure channel ID is an integer
                        channel_id = server.killfeed_channel_id
                        if not isinstance(channel_id, int):
                            channel_id = int(str(channel_id).strip())
                            logger.info(f"Converted killfeed shutdown notification channel_id to int: {channel_id}")

                        channel = guild.get_channel(channel_id)
                        if channel:
                            guild_model = await Guild.get_by_id(bot.db, guild_id)
                            embed = await EmbedBuilder.create_error_embed(
                                "Killfeed Monitor Stopped",
                                f"The killfeed monitor for server {server.name} has stopped.",
                                guild=guild_model
                            )
                            embed.add_field(
                                name="Restart", 
                                value="Use `/killfeed start` to restart the monitor.", 
                                inline=False
                            )
                            await channel.send(embed=embed)
                    except Exception as inner_e:
                        logger.error(f"Error in inner killfeed shutdown notification block: {inner_e}")
                        # Do not re-raise, let outer handler handle it
        except Exception as notify_e:
            logger.warning(f"Could not send shutdown notification: {notify_e}")


async def process_kill_event(bot, server, kill_event, channel):
    """Process a kill event and update the database"""
    try:
        # Ensure timestamp is consistent format for processing
        # If it's a string, convert to datetime for processing
        if isinstance(kill_event["timestamp"], str):
            try:
                # Try ISO format first (from historical parser)
                kill_event["timestamp"] = datetime.fromisoformat(kill_event["timestamp"])
            except ValueError:
                # Try the CSV file format as fallback
                try:
                    kill_event["timestamp"] = datetime.strptime(
                        kill_event["timestamp"], "%Y.%m.%d-%H.%M.%S"
                    )
                except ValueError:
                    logger.warning(f"Could not parse timestamp: {kill_event['timestamp']}")
                    # Use current time as last resort
                    kill_event["timestamp"] = datetime.utcnow()

        # Add server_id to the event
        kill_event["server_id"] = server.id

        # Store in database
        await bot.db.kills.insert_one(kill_event)

        # Check if this is a suicide and if notification is enabled
        is_suicide = kill_event.get("is_suicide", False)
        if is_suicide:
            suicide_type = kill_event.get("suicide_type", "other")
            if suicide_type in server.suicide_notifications and not server.suicide_notifications.get(suicide_type, True):
                logger.debug(f"Skipping notification for {suicide_type} suicide as it's disabled for server {server.id}")
                # We still update player stats, but don't send a message
                await update_player_stats(bot, server.id, kill_event)
                return

        # Get guild data for the server to check premium features
        guild_data = await bot.db.guilds.find_one({"servers.server_id": server.id})
        has_economy = False
        guild_model = None

        if guild_data:
            guild_model = Guild(bot.db, guild_data)
            has_economy = guild_model.check_feature_access("economy")
        else:
            has_economy = False

        # Create embed for the kill
        embed = EmbedBuilder.create_kill_embed(kill_event, guild=guild_model)

        # Add economy notification placeholder if the guild has economy feature
        if has_economy and not is_suicide:
            embed.add_field(
                name="💰 Economy",
                value="*Processing rewards...*",
                inline=False
            )

        # Get the icon file for the kill embed
        from utils.embed_icons import create_discord_file, KILLFEED_ICON
        icon_file = create_discord_file(KILLFEED_ICON)

        # Send to channel with the icon file if channel exists
        kill_message = None
        if channel:
            try:
                if icon_file:
                    kill_message = await channel.send(embed=embed, file=icon_file)
                else:
                    # Fallback if file can't be created
                    kill_message = await channel.send(embed=embed)
            except Exception as send_error:
                logger.error(f"Error sending kill event to channel: {send_error}")
        else:
            # No channel to send to, but we still log this and continue processing
            logger.info(f"Kill event processed but not displayed (no channel): {kill_event['killer_name']} killed {kill_event['victim_name']} with {kill_event.get('weapon', 'unknown')} from {kill_event.get('distance', 0)}m")

        # Update player stats and get economy results
        await update_player_stats(bot, server.id, kill_event)

        # Update the embed with economy info if applicable
        if has_economy:
            try:
                if not kill_event["is_suicide"]:
                    # Get killer's economy info
                    from models.economy import Economy
                    killer_id = kill_event["killer_id"]
                    killer_economy = await Economy.get_by_player(bot.db, killer_id, server.id)

                    if killer_economy:
                        # Get reward info
                        base_reward = 10
                        distance = kill_event.get("distance", 0)

                        if distance >= 100:
                            base_reward += min(int(distance / 10), 50)  # Cap bonus at +50 credits

                        # Get killer player for streak info
                        killer = await Player.get_by_id(bot.db, killer_id, server.id)
                        killstreak = killer.current_streak if killer else 0

                        # Calculate streak bonus
                        streak_bonus = 0
                        if killstreak == 5:
                            streak_bonus = 25
                        elif killstreak == 10:
                            streak_bonus = 50
                        elif killstreak == 15:
                            streak_bonus = 100
                        elif killstreak == 20:
                            streak_bonus = 200
                        elif killstreak >= 25:
                            streak_bonus = 300
                        elif killstreak >= 3:
                            streak_bonus = 15

                        # Update the embed with economy info
                        reward_text = f"+{base_reward} credits for kill"

                        if distance >= 100:
                            reward_text += f"\n+{min(int(distance / 10), 50)} distance bonus"

                        if streak_bonus > 0:
                            reward_text += f"\n+{streak_bonus} killstreak bonus (x{killstreak})"

                        reward_text += f"\nBalance: {await killer_economy.get_balance()} credits"

                        # Update the embed
                        embed.set_field_at(
                            index=embed.fields.index([f for f in embed.fields if f.name == "💰 Economy"][0]),
                            name="💰 Economy",
                            value=reward_text,
                            inline=False
                        )

                        # Update the message if it exists
                        if kill_message:
                            await kill_message.edit(embed=embed)
                        else:
                            logger.debug(f"Economy info processed but message not updated (no channel): {kill_event['killer_name']} earned {base_reward + streak_bonus} credits")
            except Exception as e:
                logger.error(f"Error updating economy info in embed: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Error processing kill event: {e}", exc_info=True)


async def update_player_stats(bot, server_id, kill_event):
    """Update player statistics based on a kill event"""
    try:
        # Get or create killer player with direct database query to ensure fresh data
        killer_id = kill_event["killer_id"]
        killer_name = kill_event["killer_name"]
        killer_data = {
            "player_id": killer_id,
            "player_name": killer_name,
            "server_id": server_id,
            "active": True
        }
        killer = await Player.create_or_update(bot.db, killer_data)

        # Get or create victim player with direct database query to ensure fresh data
        victim_id = kill_event["victim_id"]
        victim_name = kill_event["victim_name"]
        victim_data = {
            "player_id": victim_id,
            "player_name": victim_name,
            "server_id": server_id,
            "active": True
        }
        victim = await Player.create_or_update(bot.db, victim_data)

        # Get guild data for the server to check premium features
        guild_data = await bot.db.guilds.find_one({"servers.server_id": server_id})
        if guild_data:
            guild = Guild(bot.db, guild_data)
            has_economy = guild.check_feature_access("economy")
            has_rivalries = guild.check_feature_access("rivalries")
        else:
            has_economy = False
            has_rivalries = False

        # Handle suicide case
        if kill_event["is_suicide"]:
            # For suicides, get fresh data to ensure stats are up to date
            victim = await Player.get_by_id(bot.db, victim_id, server_id)
            if not victim:
                victim = await Player.create_or_update(bot.db, victim_data)

            # Record the suicide
            suicide_result = await victim.record_suicide(kill_event["suicide_type"])

            # Verify the suicide was recorded
            if not suicide_result:
                logger.warning(f"Failed to record suicide for player {victim_name} ({victim_id}) - retrying with updated data")
                # Try one more time with fresh data
                victim = await Player.get_by_id(bot.db, victim_id, server_id)
                if victim:
                    await victim.record_suicide(kill_event["suicide_type"])

            # Economy penalty for suicide if enabled
            if has_economy:
                from models.economy import Economy
                victim_economy = await Economy.get_by_player(bot.db, victim_id, server_id)
                if victim_economy:
                    # Small penalty for suicide
                    await victim_economy.remove_currency(5, "suicide_penalty", {
                        "suicide_type": kill_event.get("suicide_type", "unknown")
                    })
        else:
            # For kills, get fresh data to ensure stats are up to date
            killer = await Player.get_by_id(bot.db, killer_id, server_id)
            victim = await Player.get_by_id(bot.db, victim_id, server_id)

            if not killer:
                killer = await Player.create_or_update(bot.db, killer_data)
            if not victim:
                victim = await Player.create_or_update(bot.db, victim_data)

            # Record kill for killer (with null checking)
            if killer and victim:
                kill_result = await killer.record_kill(
                    victim_id=victim.id,
                    victim_name=victim.name,
                    weapon=kill_event["weapon"],
                    distance=kill_event["distance"]
                )

                # Verify the kill was recorded
                if not kill_result:
                    logger.warning(f"Failed to record kill for player {killer_name} ({killer_id}) - retrying with updated data")
                    # Try one more time with fresh data
                    killer = await Player.get_by_id(bot.db, killer_id, server_id)
                    if killer:
                        await killer.record_kill(
                            victim_id=victim.id,
                            victim_name=victim.name,
                            weapon=kill_event["weapon"],
                            distance=kill_event["distance"]
                        )
            else:
                logger.warning(f"Could not record kill: killer={killer is not None}, victim={victim is not None}")
                # Try to create the missing players again
                if not killer:
                    killer = await Player.create_or_update(bot.db, killer_data)
                if not victim:
                    victim = await Player.create_or_update(bot.db, victim_data)
                # If both players exist now, try again
                if killer and victim:
                    await killer.record_kill(
                        victim_id=victim.id,
                        victim_name=victim.name,
                        weapon=kill_event["weapon"],
                        distance=kill_event["distance"]
                    )

            # Record death for victim (with null checking)
            if victim and killer:
                death_result = await victim.record_death(
                    killer_id=killer.id,
                    killer_name=killer.name
                )

            # Update rivalry data (Prey/Nemesis tracking)
            if has_rivalries:
                try:
                    from utils.rivalry_tracker import RivalryTracker
                    # Track rivalry data based on this kill event
                    await RivalryTracker.update_rivalry_on_kill(bot.db, {
                        "killer_id": killer_id,
                        "victim_id": victim_id,
                        "server_id": server_id,
                        "timestamp": kill_event["timestamp"]
                    })
                    logger.debug(f"Updated rivalry data for kill: {killer_name} → {victim_name}")
                except Exception as e:
                    logger.warning(f"Failed to update rivalry data: {e}")
                    # This is non-critical, so we continue processing

                # Verify the death was recorded
                if not death_result:
                    logger.warning(f"Failed to record death for player {victim_name} ({victim_id}) - retrying with updated data")
                    # Try one more time with fresh data
                    victim = await Player.get_by_id(bot.db, victim_id, server_id)
                    if victim:
                        await victim.record_death(
                            killer_id=killer.id,
                            killer_name=killer.name
                        )
            else:
                logger.warning(f"Could not record death: killer={killer is not None}, victim={victim is not None}")
                # We already tried to create the players again above, but double-check
                if killer and victim:
                    await victim.record_death(
                        killer_id=killer.id,
                        killer_name=killer.name
                    )

            # Award currency for kill if economy feature is enabled
            if has_economy and killer and victim:  # Ensure both players exist before awarding currency
                try:
                    from models.economy import Economy

                    # Get or create economy data for killer
                    killer_economy = await Economy.get_by_player(bot.db, killer.id, server_id)
                    if not killer_economy:
                        killer_economy = await Economy.create_or_update(bot.db, killer.id, server_id)

                    if killer_economy:  # Double-check that we have a valid economy object
                        # Base reward amount
                        reward_amount = 10

                        # Bonus for long-distance kills
                        distance = kill_event.get("distance", 0)
                        if distance >= 100:
                            reward_amount += min(int(distance / 10), 50)  # Cap bonus at +50 credits

                        # Bonus for killstreaks
                        if killer.current_streak > 1:
                            killstreak = killer.current_streak

                            # Escalating rewards for killstreaks
                            if killstreak == 5:
                                streak_bonus = 25
                                streak_type = "killstreak_5"
                            elif killstreak == 10:
                                streak_bonus = 50
                                streak_type = "killstreak_10"
                            elif killstreak == 15:
                                streak_bonus = 100
                                streak_type = "killstreak_15"
                            elif killstreak == 20:
                                streak_bonus = 200
                                streak_type = "killstreak_20"
                            elif killstreak >= 25:
                                streak_bonus = 300
                                streak_type = "killstreak_25_plus"
                            elif killstreak >= 3:
                                streak_bonus = 15
                                streak_type = "killstreak_3"
                            else:
                                streak_bonus = 0
                                streak_type = None

                            # If there's a streak bonus, award it separately
                            if streak_bonus > 0 and streak_type:
                                await killer_economy.add_currency(streak_bonus, streak_type, {
                                    "killstreak": killstreak,
                                    "victim_id": victim.id,
                                    "victim_name": victim.name
                                })

                        # Award base currency with kill details
                        await killer_economy.add_currency(reward_amount, "kill_reward", {
                            "victim_id": victim.id,
                            "victim_name": victim.name,
                            "weapon": kill_event.get("weapon", "unknown"),
                            "distance": distance
                        })
                    else:
                        logger.warning(f"Could not create economy profile for player {killer_name} ({killer_id})")
                except Exception as econ_e:
                    logger.error(f"Error updating economy for kill: {econ_e}")
            elif has_economy:
                logger.warning(f"Could not award currency: killer={killer is not None}, victim={victim is not None}")


        # Explicitly update leaderboards by resetting cache
        # This is a workaround to ensure leaderboards reflect the new stats
        if hasattr(bot, "leaderboard_cache"):
            cache_key = f"leaderboard_{server_id}_kills"
            if cache_key in bot.leaderboard_cache:
                del bot.leaderboard_cache[cache_key]

    except Exception as e:
        logger.error(f"Error updating player stats: {e}", exc_info=True)


async def setup(bot):
    """Set up the Killfeed cog"""
    await bot.add_cog(Killfeed(bot))