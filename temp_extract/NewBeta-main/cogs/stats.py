"""
Statistics commands for player and server stats
"""
import logging
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from models.server import Server
from models.player import Player
from models.guild import Guild
from utils.embed_builder import EmbedBuilder
from config import EMBED_COLOR, EMBED_FOOTER
from utils.helpers import paginate_embeds, format_time_ago

logger = logging.getLogger(__name__)


async def server_id_autocomplete(interaction, current):
    """Autocomplete for server IDs"""
    try:
        # Get user's guild ID
        guild_id = interaction.guild_id

        if guild_id is None:
            return [app_commands.Choice(name="Must use in a server", value="error")]

        # Get cached server data or fetch it
        cog = interaction.client.get_cog("Stats")

        if cog is None:
            logger.error("Stats cog not found in server_id_autocomplete")
            return [app_commands.Choice(name="Error: Stats module not loaded", value="error")]

        # Update cache if needed
        cache_expired = False
        if guild_id not in cog.server_autocomplete_cache:
            cache_expired = True
        else:
            last_update = cog.server_autocomplete_cache.get(guild_id, {}).get("last_update", datetime.min)
            cache_expired = (datetime.now() - last_update).total_seconds() > 300

        if cache_expired:
            try:
                # Fetch guild data with a timeout
                guild_data = await asyncio.wait_for(
                    interaction.client.db.guilds.find_one({"guild_id": guild_id}),
                    timeout=2.0
                )

                if guild_data and "servers" in guild_data:
                    # Update cache with server data
                    server_list = []
                    for server in guild_data.get("servers", []):
                        raw_id = server.get("server_id", "")
                        server_id = str(raw_id) if raw_id is not None else ""
                        server_name = server.get("server_name", "Unknown")

                        # Make sure we have a valid display name
                        if server_name == "Unknown" and server_id:
                            server_name = f"Server {server_id}"

                        server_list.append({
                            "id": server_id,  # Always store as string
                            "name": server_name
                        })

                    # Update cache
                    cog.server_autocomplete_cache[guild_id] = {
                        "servers": server_list,
                        "last_update": datetime.now()
                    }
            except asyncio.TimeoutError:
                logger.warning(f"Database timeout in server_id_autocomplete for guild {guild_id}")
                # Use existing cache if available, or return an error
                if guild_id not in cog.server_autocomplete_cache:
                    return [app_commands.Choice(name="Timeout loading servers", value="error")]
            except Exception as e:
                logger.error(f"Error fetching guild data: {e}")
                # Use existing cache if available, or return an error
                if guild_id not in cog.server_autocomplete_cache:
                    return [app_commands.Choice(name="Error loading servers", value="error")]

        # Get servers from cache
        servers = cog.server_autocomplete_cache.get(guild_id, {}).get("servers", [])

        # Filter by current input
        filtered_servers = []
        for server in servers:
            server_id = server['id']  # Already stored as string in cache

            # Check if current input matches server name or ID
            if current.lower() in server_id.lower() or current.lower() in server['name'].lower():
                filtered_servers.append(app_commands.Choice(
                    name=server['name'], 
                    value=server_id
                ))

        return filtered_servers[:25]

    except Exception as e:
        logger.error(f"Error in server autocomplete: {e}", exc_info=True)
        return [app_commands.Choice(name="Error loading servers", value="error")]


async def player_name_autocomplete(interaction, current):
    """Autocomplete for player names"""
    try:
        # Get user's guild ID and the server ID from the command options
        guild_id = interaction.guild_id

        if guild_id is None:
            return [app_commands.Choice(name="Must use in a server", value="")]

        # Try to get the server_id from the interaction
        server_id = None
        try:
            for option in interaction.data.get("options", []):
                if option.get("name") == "server_id":
                    raw_id = option.get("value")
                    server_id = str(raw_id) if raw_id is not None else None
                    logger.debug(f"player_name_autocomplete converting server_id from {type(raw_id).__name__} to string: {server_id}")
                    break

                # Check in subcommands
                for suboption in option.get("options", []):
                    if suboption.get("name") == "server_id":
                        raw_id = suboption.get("value")
                        server_id = str(raw_id) if raw_id is not None else None
                        logger.debug(f"player_name_autocomplete (subcommand) converting server_id from {type(raw_id).__name__} to string: {server_id}")
                        break
        except Exception as e:
            logger.error(f"Error extracting server_id from interaction: {e}")
            server_id = None

        if not server_id:
            return [app_commands.Choice(name="Select a server first", value="")]

        # Get cached player data or fetch it
        cog = interaction.client.get_cog("Stats")

        if cog is None:
            logger.error("Stats cog not found in player_name_autocomplete")
            return [app_commands.Choice(name="Error: Stats module not loaded", value="")]

        cache_key = f"{guild_id}_{server_id}"

        # Update cache if needed
        cache_expired = False
        if cache_key not in cog.player_autocomplete_cache:
            cache_expired = True
        else:
            last_update = cog.player_autocomplete_cache.get(cache_key, {}).get("last_update", datetime.min)
            cache_expired = (datetime.now() - last_update).total_seconds() > 300

        if cache_expired:
            try:
                # Fetch players with a timeout
                players_cursor = interaction.client.db.players.find(
                    {"server_id": str(server_id), "active": True},
                    {"player_id": 1, "player_name": 1}
                ).limit(100)  # Reduced limit for faster queries

                players = await asyncio.wait_for(
                    players_cursor.to_list(length=100),
                    timeout=2.0
                )

                if players:
                    # Update cache with valid player data
                    player_list = []
                    for player_data in players:
                        player_id = player_data.get("player_id", "")
                        player_name = player_data.get("player_name", "Unknown Player")

                        # Skip invalid entries
                        if not player_name or player_name == "Unknown Player":
                            continue

                        player_list.append({
                            "id": player_id,
                            "name": player_name
                        })

                    # Update cache
                    cog.player_autocomplete_cache[cache_key] = {
                        "players": player_list,
                        "last_update": datetime.now()
                    }
            except asyncio.TimeoutError:
                logger.warning(f"Database timeout in player_name_autocomplete for server {server_id}")
                # Use existing cache if available
                if cache_key not in cog.player_autocomplete_cache:
                    return [app_commands.Choice(name="Timeout loading players", value="")]
            except Exception as e:
                logger.error(f"Error fetching players: {e}")
                # Use existing cache if available
                if cache_key not in cog.player_autocomplete_cache:
                    return [app_commands.Choice(name="Error loading players", value="")]

        # Get players from cache
        players = cog.player_autocomplete_cache.get(cache_key, {}).get("players", [])

        if not players:
            return [app_commands.Choice(name="No players found", value="")]

        # Filter by current input
        try:
            if current:
                filtered_players = [
                    app_commands.Choice(name=player['name'], value=player['name'])
                    for player in players
                    if current.lower() in player['name'].lower()
                ]
            else:
                # Without filtering, take a sample of players (max 25)
                import random
                sample_size = min(25, len(players))
                sampled_players = random.sample(players, sample_size) if sample_size > 0 else []

                filtered_players = [
                    app_commands.Choice(name=player['name'], value=player['name'])
                    for player in sampled_players
                ]

            # Always limit to max 25 choices
            return filtered_players[:25]
        except Exception as e:
            logger.error(f"Error filtering players: {e}")
            return [app_commands.Choice(name="Error processing players", value="")]

    except Exception as e:
        logger.error(f"Error in player autocomplete: {e}", exc_info=True)
        return [app_commands.Choice(name="Error loading players", value="")]


async def weapon_name_autocomplete(interaction, current):
    """Autocomplete for weapon names"""
    try:
        # Get user's guild ID and the server ID from the command options
        guild_id = interaction.guild_id

        if guild_id is None:
            return [app_commands.Choice(name="Must use in a server", value="")]

        # Try to get the server_id from the interaction
        server_id = None
        try:
            for option in interaction.data.get("options", []):
                if option.get("name") == "server_id":
                    raw_id = option.get("value")
                    server_id = str(raw_id) if raw_id is not None else None
                    logger.debug(f"weapon_name_autocomplete converting server_id from {type(raw_id).__name__} to string: {server_id}")
                    break

                # Check in subcommands
                for suboption in option.get("options", []):
                    if suboption.get("name") == "server_id":
                        raw_id = suboption.get("value")
                        server_id = str(raw_id) if raw_id is not None else None
                        logger.debug(f"weapon_name_autocomplete (subcommand) converting server_id from {type(raw_id).__name__} to string: {server_id}")
                        break
        except Exception as e:
            logger.error(f"Error extracting server_id from interaction in weapon_name_autocomplete: {e}")
            server_id = None

        if not server_id:
            return [app_commands.Choice(name="Select a server first", value="")]

        # Import weapon stats
        try:
            from utils.weapon_stats import WEAPON_CATEGORIES, WEAPON_DETAILS
        except ImportError as e:
            logger.error(f"Error importing weapon stats: {e}")
            return [app_commands.Choice(name="Error loading weapon data", value="")]

        try:
            # Get all available weapon names
            all_weapons = []

            # Add weapons from categories
            for category, weapons in WEAPON_CATEGORIES.items():
                if category != "death_types":  # Exclude death types
                    all_weapons.extend(weapons)

            # Add any additional weapons from WEAPON_DETAILS that might not be in categories
            extra_weapons = []
            death_types = WEAPON_CATEGORIES.get("death_types", [])

            for weapon in WEAPON_DETAILS.keys():
                if weapon not in all_weapons and weapon not in death_types:
                    extra_weapons.append(weapon)

            all_weapons.extend(extra_weapons)

            # Ensure list is not too large
            all_weapons = all_weapons[:500]  # Reasonable limit

            # Filter by current input
            if current:
                current_lower = current.lower()
                filtered_weapons = []

                # First pass: exact matches
                for weapon in all_weapons:
                    if weapon.lower() == current_lower:
                        filtered_weapons.append(app_commands.Choice(name=weapon, value=weapon))

                # Second pass: starts with the input string
                if len(filtered_weapons) < 25:
                    for weapon in all_weapons:
                        if weapon.lower().startswith(current_lower) and not any(choice.value == weapon for choice in filtered_weapons):
                            filtered_weapons.append(app_commands.Choice(name=weapon, value=weapon))

                # Third pass: contains the input string
                if len(filtered_weapons) < 25:
                    for weapon in all_weapons:
                        if current_lower in weapon.lower() and not any(choice.value == weapon for choice in filtered_weapons):
                            filtered_weapons.append(app_commands.Choice(name=weapon, value=weapon))
                            if len(filtered_weapons) >= 25:
                                break
            else:
                # Without filtering, show top weapons
                import random
                sample_size = min(25, len(all_weapons))
                sampled_weapons = random.sample(all_weapons, sample_size) if sample_size > 0 else []

                filtered_weapons = [
                    app_commands.Choice(name=weapon, value=weapon)
                    for weapon in sampled_weapons
                ]

            return filtered_weapons[:25]

        except Exception as e:
            logger.error(f"Error processing weapons in weapon_name_autocomplete: {e}", exc_info=True)
            return [app_commands.Choice(name="Error processing weapons", value="")]

    except Exception as e:
        logger.error(f"Error in weapon autocomplete: {e}", exc_info=True)
        return [app_commands.Choice(name="Error loading weapons", value="")]


class Stats(commands.Cog):
    """Stats commands for player and server stats"""

    def __init__(self, bot):
        self.bot = bot
        self.server_autocomplete_cache = {}
        self.player_autocomplete_cache = {}

    @commands.hybrid_group(name="stats", description="Statistics commands")
    @commands.guild_only()
    async def stats(self, ctx):
        """Stats command group"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Please specify a subcommand.")

    @stats.command(name="player", description="View player statistics")
    @app_commands.describe(
        server_id="Select a server by name to check stats for",
        player_name="The player name to search for"
    )
    @app_commands.autocomplete(
        server_id=server_id_autocomplete,
        player_name=player_name_autocomplete
    )
    async def player_stats(self, ctx, server_id: str, player_name: str):
        """View statistics for a player"""
        try:
            # Initialize guild_model to None first to avoid UnboundLocalError
            guild_model = None

            # Defer response to prevent timeout
            await ctx.defer()

            # Get guild data and create guild model for embedded themes
            try:
                guild_data = await self.bot.db.guilds.find_one({"guild_id": ctx.guild.id})
                if guild_data:
                    guild_model = Guild(self.bot.db, guild_data)
            except Exception as e:
                logger.warning(f"Error getting guild model: {e}")

            if not guild_data:
                embed = EmbedBuilder.create_error_embed(
                    "Error",
                    "This guild is not set up. Please use the setup commands first."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # Check if the guild has access to stats feature
            guild = Guild(self.bot.db, guild_data)
            if not guild.check_feature_access("stats"):
                embed = EmbedBuilder.create_error_embed(
                    "Premium Feature",
                    "Player statistics is a premium feature. Please upgrade to access this feature."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # Find the server
            server = None
            server_name = server_id
            for s in guild_data.get("servers", []):
                if s.get("server_id") == server_id:
                    server = Server(self.bot.db, s)
                    server_name = s.get("server_name", server_id)
                    break

            if not server:
                embed = EmbedBuilder.create_error_embed(
                    "Server Not Found",
                    f"Server with ID {server_id} not found in this guild."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # Find the player(s)
            players = await Player.get_by_name(self.bot.db, player_name, server_id)

            if not players:
                embed = EmbedBuilder.create_error_embed(
                    "Player Not Found",
                    f"Player '{player_name}' not found on server {server_name}."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # If multiple players found with similar names, use exact match or first match
            player = None
            for p in players:
                if p.name.lower() == player_name.lower():
                    player = p
                    break

            if not player:
                player = players[0]

            # Get detailed player stats
            player_stats = await player.get_detailed_stats()

            # Create multiple embeds for different aspects of player stats
            embeds = []

            # Primary stats embed
            primary_embed = EmbedBuilder.create_stats_embed(player_stats, server_name)

            # Add core statistics
            kills = player_stats.get("kills", 0)
            deaths = player_stats.get("deaths", 0)
            kdr = player_stats.get("kdr", 0)
            suicides = player_stats.get("suicides", 0)
            longest_shot = player_stats.get("longest_shot", 0)

            primary_embed.add_field(name="Kills", value=str(kills), inline=True)
            primary_embed.add_field(name="Deaths", value=str(deaths), inline=True)
            primary_embed.add_field(name="K/D Ratio", value=str(kdr), inline=True)
            primary_embed.add_field(name="Suicides", value=str(suicides), inline=True)
            primary_embed.add_field(name="Longest Shot", value=f"{longest_shot}m", inline=True)

            # Add streak information
            highest_killstreak = player_stats.get("highest_killstreak", 0)
            highest_deathstreak = player_stats.get("highest_deathstreak", 0)
            current_streak = player_stats.get("current_streak", 0)
            streak_desc = "On killing spree!" if current_streak > 0 else "Death streak" if current_streak < 0 else "Neutral"

            primary_embed.add_field(
                name="Streaks", 
                value=f"Best Killstreak: {highest_killstreak}\nWorst Deathstreak: {highest_deathstreak}\nCurrent: {abs(current_streak)} ({streak_desc})", 
                inline=False
            )

            # Add activity information
            first_seen = player_stats.get("first_seen", "Unknown")
            last_seen = player_stats.get("last_seen", "Unknown")

            # Convert ISO format strings to datetime objects
            try:
                first_seen_dt = datetime.fromisoformat(first_seen)
                first_seen_str = first_seen_dt.strftime("%Y-%m-%d %H:%M")
            except:
                first_seen_str = "Unknown"

            try:
                last_seen_dt = datetime.fromisoformat(last_seen)
                last_seen_str = last_seen_dt.strftime("%Y-%m-%d %H:%M")
            except:
                last_seen_str = "Unknown"

            # Add activity info as a field
            primary_embed.add_field(
                name="Activity",
                value=f"First Seen: {first_seen_str}\nLast Seen: {last_seen_str}",
                inline=False
            )

            # Add primary embed to list
            embeds.append(primary_embed)

            # Weapons analysis embed
            weapons_embed = discord.Embed(
                title=f"🔫 Weapon Analysis: {player_stats['player_name']}",
                description=f"Detailed weapon statistics for {player_stats['player_name']}",
                color=EMBED_COLOR,
                timestamp=datetime.utcnow()
            )
            weapons_embed.set_footer(text=EMBED_FOOTER)

            # Add combat statistics
            combat_kills = player_stats.get("combat_kills", 0)
            melee_percentage = player_stats.get("melee_percentage", 0)
            most_used_category = player_stats.get("most_used_category", {})

            weapon_style = ""
            if most_used_category and "name" in most_used_category:
                category_name = most_used_category["name"]
                if category_name == "sniper_rifles":
                    weapon_style = "Sniper"
                elif category_name == "shotguns":
                    weapon_style = "Close Combat Specialist"
                elif category_name == "assault_rifles":
                    weapon_style = "Assault Specialist"
                elif category_name == "smgs":
                    weapon_style = "Run & Gun"
                elif category_name == "pistols":
                    weapon_style = "Sidearm Expert"
                elif category_name == "melee":
                    weapon_style = "Silent Hunter"

            weapons_embed.add_field(
                name="Combat Profile",
                value=f"Combat Kills: {combat_kills}\nMelee Kills: {melee_percentage}%\nCombat Style: {weapon_style or 'Balanced'}",
                inline=False
            )

            # Add weapon category breakdown
            weapon_categories = player_stats.get("weapon_categories", {})
            if weapon_categories:
                # Format categories with percentages
                if combat_kills > 0:
                    category_lines = []
                    for category, count in weapon_categories.items():
                        if category not in ['special', 'death_types', 'unknown']:
                            percentage = round((count / combat_kills) * 100, 1)
                            display_name = category.replace('_', ' ').title()
                            category_lines.append(f"{display_name}: {count} kills ({percentage}%)")

                    category_str = "\n".join(category_lines)
                    weapons_embed.add_field(name="Weapon Categories", value=category_str, inline=False)

            # Add weapon stats if available
            weapons = player_stats.get("weapons", {})
            if weapons:
                # Get top 5 weapons
                sorted_weapons = sorted(weapons.items(), key=lambda x: x[1], reverse=True)[:5]
                weapon_lines = []

                # Add weapon details from weapon database
                from utils.weapon_stats import get_weapon_details

                for weapon, count in sorted_weapons:
                    details = get_weapon_details(weapon)
                    if details and "type" in details:
                        weapon_type = details.get("type", "Unknown")
                        ammo = details.get("ammo", "N/A")
                        weapon_lines.append(f"{weapon} ({weapon_type}): {count} kills | {ammo}")
                    else:
                        weapon_lines.append(f"{weapon}: {count} kills")

                weapon_str = "\n".join(weapon_lines)
                weapons_embed.add_field(name="Top Weapons", value=weapon_str, inline=False)

            # Add weapons embed to list
            embeds.append(weapons_embed)

            # Player matchups embed
            matchups_embed = discord.Embed(
                title=f"⚔️ Player Matchups: {player_stats['player_name']}",
                description=f"Player vs. player statistics for {player_stats['player_name']}",
                color=EMBED_COLOR,
                timestamp=datetime.utcnow()
            )
            matchups_embed.set_footer(text=EMBED_FOOTER)

            # Add victim and nemesis info (using the new Prey/Nemesis terminology)
            favorite_victim = player_stats.get("favorite_victim")
            if favorite_victim:
                prey_title = "🎯 Prey"
                # Calculate KD against this specific player
                prey_kills = favorite_victim.get('kill_count', 0)
                prey_deaths = max(favorite_victim.get('death_count', 0), 1)  # Treat 0 as 1 for KDR calculation
                prey_kd = round(prey_kills / prey_deaths, 2)
                
                matchups_embed.add_field(
                    name=prey_title,
                    value=f"{favorite_victim['player_name']}\n{prey_kills} Kills  {prey_kd} KD",
                    inline=True
                )
                
                # Add a note if this data is from the hourly tracker
                if player_stats.get("rivalries_last_updated"):
                    matchups_embed.set_footer(text=f"Rivalries updated: {format_time_ago(player_stats.get('rivalries_last_updated'))}")

            nemesis = player_stats.get("nemesis")
            if nemesis:
                nemesis_title = "☠️ Nemesis" 
                # Calculate KD against this specific player
                nemesis_deaths = nemesis.get('kill_count', 0)  # Their kills = player's deaths
                nemesis_kills = nemesis.get('death_count', 0)  # Their deaths = player's kills
                nemesis_kd = round(nemesis_kills / max(nemesis_deaths, 1), 2)
                
                matchups_embed.add_field(
                    name=nemesis_title,
                    value=f"{nemesis['player_name']}\n{nemesis_deaths} Deaths  {nemesis_kd} KD",
                    inline=True
                )

            # Get recent kill data for this player from kills collection
            pipeline = [
                {
                    "$match": {
                        "server_id": server_id,
                        "$or": [
                            {"killer_id": player.id},
                            {"victim_id": player.id}
                        ],
                        "is_suicide": False
                    }
                },
                {
                    "$sort": {"timestamp": -1}
                },
                {
                    "$limit": 50
                }
            ]

            cursor = self.bot.db.kills.aggregate(pipeline)
            recent_kills = await cursor.to_list(length=None)

            # Analyze recent performance
            if recent_kills:
                # Count recent kills and deaths
                recent_kills_count = sum(1 for k in recent_kills if k.get("killer_id") == player.id)
                recent_deaths_count = sum(1 for k in recent_kills if k.get("victim_id") == player.id)
                recent_kdr = round(recent_kills_count / max(recent_deaths_count, 1), 2)

                performance_trend = "Improving" if recent_kdr > kdr else "Declining" if recent_kdr < kdr else "Stable"

                matchups_embed.add_field(
                    name="Recent Performance",
                    value=f"Recent K/D: {recent_kdr}\nOverall K/D: {kdr}\nTrend: {performance_trend}",
                    inline=False
                )

                # Find common opponents in recent kills
                opponents = {}
                for kill in recent_kills:
                    if kill.get("killer_id") == player.id:
                        # Player killed someone
                        victim_id = kill.get("victim_id")
                        victim_name = kill.get("victim_name")
                        if victim_id not in opponents:
                            opponents[victim_id] = {"name": victim_name, "kills": 0, "deaths": 0}
                        opponents[victim_id]["kills"] += 1
                    elif kill.get("victim_id") == player.id:
                        # Player was killed by someone
                        killer_id = kill.get("killer_id")
                        killer_name = kill.get("killer_name")
                        if killer_id not in opponents:
                            opponents[killer_id] = {"name": killer_name, "kills": 0, "deaths": 0}
                        opponents[killer_id]["deaths"] += 1

                # Find top matchups
                top_matchups = sorted(
                    [(opp_id, data) for opp_id, data in opponents.items() if data["kills"] + data["deaths"] >= 3],
                    key=lambda x: x[1]["kills"] + x[1]["deaths"],
                    reverse=True
                )[:5]

                if top_matchups:
                    matchup_lines = []
                    for _, data in top_matchups:
                        name = data["name"]
                        kills = data["kills"]
                        deaths = data["deaths"]
                        matchup_kdr = round(kills / max(deaths, 1), 2)
                        matchup_lines.append(f"{name}: {kills}K/{deaths}D (KDR: {matchup_kdr})")

                    matchups_embed.add_field(
                        name="Recent Matchups",
                        value="\n".join(matchup_lines),
                        inline=False
                    )

            # Add matchups embed to list
            embeds.append(matchups_embed)

            # Get historical kills for this player to analyze trends
            pipeline = [
                {
                    "$match": {
                        "server_id": server_id,
                        "killer_id": player.id,
                        "is_suicide": False
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}
                        },
                        "kills": {"$sum": 1},
                        "avg_distance": {"$avg": "$distance"}
                    }
                },
                {
                    "$sort": {"_id": 1}
                },
                {
                    "$limit": 30
                }
            ]

            cursor = self.bot.db.kills.aggregate(pipeline)
            historical_kills = await cursor.to_list(length=None)

            # Create a performance history embed if we have data
            if len(historical_kills) > 2:
                history_embed = discord.Embed(
                    title=f"📈 Performance History: {player_stats['player_name']}",
                    description=f"Historical performance data for {player_stats['player_name']}",
                    color=EMBED_COLOR,
                    timestamp=datetime.utcnow()
                )
                history_embed.set_footer(text=EMBED_FOOTER)

                # Format historical kill data
                kill_dates = [h["_id"] for h in historical_kills[-7:]]
                kill_counts = [h["kills"] for h in historical_kills[-7:]]

                history_embed.add_field(
                    name="Recent Daily Performance",
                    value="```Date       | Kills\n" + 
                          "------------+-------\n" + 
                          "\n".join([f"{date} | {kills}" for date, kills in zip(kill_dates, kill_counts)]) + 
                          "```",
                    inline=False
                )

                # Calculate performance improvement
                if len(historical_kills) >= 3:
                    recent_avg = sum(h["kills"] for h in historical_kills[-3:]) / 3
                    older_avg = sum(h["kills"] for h in historical_kills[-6:-3]) / 3 if len(historical_kills) >= 6 else 0

                    if older_avg > 0:
                        change_pct = round(((recent_avg - older_avg) / older_avg) * 100, 1)
                        trend_text = f"{change_pct}% {'increase' if change_pct >= 0 else 'decrease'} in kills"
                    else:
                        trend_text = "Insufficient historical data"

                    history_embed.add_field(
                        name="Performance Trend",
                        value=f"Recent average: {round(recent_avg, 1)} kills/day\n" + 
                              (f"Previous average: {round(older_avg, 1)} kills/day\n" if older_avg > 0 else "") + 
                              trend_text,
                        inline=False
                    )

                # Add history embed to list
                embeds.append(history_embed)

            # Create pagination view for embeds
            from utils.helpers import create_pagination_buttons, paginate_embeds
            current_embed, view = paginate_embeds(embeds)

            # Send the embed with pagination
            message = await ctx.send(embed=current_embed, view=view)

            # Set up pagination callback
            async def pagination_callback(interaction):
                # Get current page from the pagination indicator label
                current_page = 0
                for item in view.children:
                    if item.custom_id == "pagination_indicator":
                        try:
                            # Extract current page from "Page X/Y" format
                            page_text = item.label
                            current_page = int(page_text.split('/')[0].replace('Page ', '')) - 1
                        except (ValueError, IndexError):
                            current_page = 0
                        break

                if interaction.data["custom_id"] == "pagination_first":
                    new_page = 0
                elif interaction.data["custom_id"] == "pagination_prev":
                    new_page = max(0, current_page - 1)
                elif interaction.data["custom_id"] == "pagination_next":
                    new_page = min(len(embeds) - 1, current_page + 1)
                elif interaction.data["custom_id"] == "pagination_last":
                    new_page = len(embeds) - 1
                else:
                    return

                new_embed, updated_view = paginate_embeds(embeds, new_page)
                await interaction.response.edit_message(embed=new_embed, view=updated_view)

            # Set the callback for each button
            for item in view.children:
                if hasattr(item, "custom_id") and item.custom_id.startswith("pagination_"):
                    item.callback = pagination_callback

        except Exception as e:
            logger.error(f"Error getting player stats: {e}", exc_info=True)
            embed = EmbedBuilder.create_error_embed(
                "Error",
                f"An error occurred while getting player stats: {e}"
            , guild=guild_model)
            await ctx.send(embed=embed)

    @stats.command(name="server", description="View server statistics")
    @app_commands.describe(server_id="Select a server by name to check stats for")
    @app_commands.autocomplete(server_id=server_id_autocomplete)
    async def server_stats(self, ctx, server_id: str):
        """View statistics for a server"""

        try:
            # Defer response to prevent timeout
            await ctx.defer()
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

            # Check if the guild has access to stats feature
            guild = Guild(self.bot.db, guild_data)
            if not guild.check_feature_access("stats"):
                embed = EmbedBuilder.create_error_embed(
                    "Premium Feature",
                    "Server statistics is a premium feature. Please upgrade to access this feature."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # Find the server
            server = None
            for s in guild_data.get("servers", []):
                if s.get("server_id") == server_id:
                    server = Server(self.bot.db, s)
                    break

            if not server:
                embed = EmbedBuilder.create_error_embed(
                    "Server Not Found",
                    f"Server with ID {server_id} not found in this guild."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # Get server stats
            server_stats = await server.get_server_stats()

            # Create embed
            embed = EmbedBuilder.create_server_stats_embed(server_stats)

            # Add top killers
            top_killers = server_stats.get("top_killers", [])
            if top_killers:
                killer_str = "\n".join([
                    f"{i+1}. {killer['player_name']}: {killer['kills']} kills"
                    for i, killer in enumerate(top_killers[:5])
                ])
                embed.add_field(name="Top Killers", value=killer_str, inline=False)

            # Add top weapons
            top_weapons = server_stats.get("top_weapons", [])
            if top_weapons:
                weapon_str = "\n".join([
                    f"{i+1}. {weapon['weapon']}: {weapon['kills']} kills"
                    for i, weapon in enumerate(top_weapons[:5])
                ])
                embed.add_field(name="Top Weapons", value=weapon_str, inline=False)

            # Add recent events
            recent_events = server_stats.get("recent_events", [])
            if recent_events:
                event_str = "\n".join([
                    f"{event['event_type']}: {format_time_ago(event['timestamp'])}"
                    for event in recent_events[:3]
                ])
                embed.add_field(name="Recent Events", value=event_str, inline=False)

            # Send the embed
            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Error getting server stats: {e}", exc_info=True)
            embed = EmbedBuilder.create_error_embed(
                "Error",
                f"An error occurred while getting server stats: {e}"
            , guild=guild_model)
            await ctx.send(embed=embed)

    @stats.command(name="leaderboard", description="View player leaderboards")
    @app_commands.describe(
        server_id="Select a server by name to check leaderboards for",
        stat="The statistic to rank by",
        limit="Number of players to show (max 25)"
    )
    @app_commands.autocomplete(server_id=server_id_autocomplete)
    @app_commands.choices(stat=[
        app_commands.Choice(name="Kills", value="kills"),
        app_commands.Choice(name="Deaths", value="deaths"),
        app_commands.Choice(name="K/D Ratio", value="kdr"),
        app_commands.Choice(name="Longest Shot", value="longest_shot"),
        app_commands.Choice(name="Kill Streak", value="highest_killstreak"),
        app_commands.Choice(name="Suicides", value="suicides")
    ])
    async def leaderboard(self, ctx, server_id: str, stat: str, limit: int = 10):
        """View leaderboards for a specific stat"""

        try:
            # Defer response to prevent timeout
            await ctx.defer()
            # Get guild model for themed embed
            guild_data = None
            guild_model = None
            try:
                guild_data = await self.bot.db.guilds.find_one({"guild_id": ctx.guild.id})
                if guild_data:
                    guild_model = Guild(self.bot.db, guild_data)
            except Exception as e:
                logger.warning(f"Error getting guild model: {e}")

            # Validate limit
            if limit < 1:
                limit = 10
            elif limit > 25:
                limit = 25

            # Get guild data
            guild_data = await self.bot.db.guilds.find_one({"guild_id": ctx.guild.id})
            if not guild_data:
                embed = EmbedBuilder.create_error_embed(
                    "Error",
                    "This guild is not set up. Please use the setup commands first."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # Check if the guild has access to stats feature
            guild = Guild(self.bot.db, guild_data)
            if not guild.check_feature_access("stats"):
                embed = EmbedBuilder.create_error_embed(
                    "Premium Feature",
                    "Leaderboards are a premium feature. Please upgrade to access this feature."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # Find the server
            server = None
            server_name = server_id
            for s in guild_data.get("servers", []):
                if s.get("server_id") == server_id:
                    server = Server(self.bot.db, s)
                    server_name = s.get("server_name", server_id)
                    break

            if not server:
                embed = EmbedBuilder.create_error_embed(
                    "Server Not Found",
                    f"Server with ID {server_id} not found in this guild."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # Get leaderboard data
            leaderboard_data = await Player.get_leaderboard(self.bot.db, server_id, stat, limit)

            if not leaderboard_data:
                embed = EmbedBuilder.create_error_embed(
                    "No Data",
                    f"No player data found for '{stat}' on server {server_name}."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # Create pretty stat name mapping
            stat_names = {
                "kills": "Kills",
                "deaths": "Deaths",
                "kdr": "K/D Ratio",
                "longest_shot": "Longest Shot",
                "highest_killstreak": "Highest Kill Streak",
                "suicides": "Suicides"
            }

            stat_display = stat_names.get(stat, stat.title())

            # Create embed
            embed = EmbedBuilder.create_base_embed(
                f"{stat_display} Leaderboard",
                f"Top {len(leaderboard_data)} players on {server_name}"
            , guild=guild_model)

            # Add leaderboard entries
            value_suffix = "m" if stat == "longest_shot" else ""

            leaderboard_str = ""
            for i, entry in enumerate(leaderboard_data):
                # Use numbers instead of emoji medals for a cleaner look
                position = f"#{i+1}"
                leaderboard_str += f"{position} **{entry['player_name']}**: {entry['value']}{value_suffix}\n"

            embed.add_field(name="Rankings", value=leaderboard_str, inline=False)

            # Get the icon for leaderboard and send with icon
            from utils.embed_icons import send_embed_with_icon, LEADERBOARD_ICON
            await send_embed_with_icon(ctx, embed, LEADERBOARD_ICON)

        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}", exc_info=True)
            embed = EmbedBuilder.create_error_embed(
                "Error",
                f"An error occurred while getting the leaderboard: {e}"
            , guild=guild_model)
            await ctx.send(embed=embed)

    @stats.command(name="weapon_categories", description="View statistics by weapon category")
    @app_commands.describe(
        server_id="Select a server by name to check stats for"
    )
    @app_commands.autocomplete(server_id=server_id_autocomplete)
    async def weapon_categories(self, ctx, server_id: str):
        """View statistics by weapon category"""

        try:
            # Defer response to prevent timeout
            await ctx.defer()
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

            # Check if the guild has access to stats feature
            guild = Guild(self.bot.db, guild_data)
            if not guild.check_feature_access("stats"):
                embed = EmbedBuilder.create_error_embed(
                    "Premium Feature",
                    "Weapon category statistics is a premium feature. Please upgrade to access this feature."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # Find the server
            server = None
            server_name = server_id
            for s in guild_data.get("servers", []):
                if s.get("server_id") == server_id:
                    server = Server(self.bot.db, s)
                    server_name = s.get("server_name", server_id)
                    break

            if not server:
                embed = EmbedBuilder.create_error_embed(
                    "Error",
                    f"Server {server_id} not found. Please select a valid server."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # Import weapon utilities
            from utils.weapon_stats import get_weapon_category, WEAPON_CATEGORIES

            # Query all weapons used on this server
            pipeline = [
                {
                    "$match": {
                        "server_id": server_id,
                        "is_suicide": False
                    }
                },
                {
                    "$group": {
                        "_id": "$weapon",
                        "kills": {"$sum": 1}
                    }
                }
            ]

            cursor = self.bot.db.kills.aggregate(pipeline)
            weapons = await cursor.to_list(length=None)

            if not weapons:
                embed = EmbedBuilder.create_error_embed(
                    "No Data",
                    f"No weapon data found for server {server_name}."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # Compile category stats
            category_stats = {}
            total_kills = 0

            for weapon in weapons:
                weapon_name = weapon["_id"]
                kill_count = weapon["kills"]
                total_kills += kill_count

                category = get_weapon_category(weapon_name)
                if category not in category_stats:
                    category_stats[category] = 0
                category_stats[category] += kill_count

            # Create embed
            embed = EmbedBuilder.create_base_embed(
                f"Weapon Category Stats",
                f"Weapon category breakdown on {server_name}"
            , guild=guild_model)

            # Add total kills
            embed.add_field(name="Total Kills", value=str(total_kills), inline=False)

            # Add category stats
            for category, kills in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
                if category == "unknown" or category == "death_types":
                    continue

                percentage = round((kills / total_kills) * 100, 1)
                embed.add_field(
                    name=category.replace("_", " ").title(),
                    value=f"{kills} kills ({percentage}%)",
                    inline=True
                )

            # Add definitions section
            definitions = []
            for category in category_stats.keys():
                if category in WEAPON_CATEGORIES and category not in ["death_types", "unknown"]:
                    weapons_list = WEAPON_CATEGORIES[category]
                    if len(weapons_list) > 3:
                        weapons_str = ", ".join(weapons_list[:3]) + f" and {len(weapons_list)-3} more"
                    else:
                        weapons_str = ", ".join(weapons_list)
                    definitions.append(f"**{category.replace('_', ' ').title()}**: {weapons_str}")

            if definitions:
                embed.add_field(name="Category Definitions", value="\n".join(definitions), inline=False)

            # Send with appropriate weapon icon
            from utils.embed_icons import send_embed_with_icon, WEAPON_STATS_ICON
            await send_embed_with_icon(ctx, embed, WEAPON_STATS_ICON)

        except Exception as e:
            logger.error(f"Error getting weapon category stats: {e}", exc_info=True)
            embed = EmbedBuilder.create_error_embed(
                "Error",
                f"An error occurred while getting weapon category stats: {e}"
            , guild=guild_model)
            await ctx.send(embed=embed)

    @stats.command(name="weapon", description="View weapon statistics")
    @app_commands.describe(
        server_id="Select a server by name to check stats for",
        weapon_name="The weapon to view statistics for"
    )
    @app_commands.autocomplete(
        server_id=server_id_autocomplete,
        weapon_name=weapon_name_autocomplete
    )
    async def weapon_stats(self, ctx, server_id: str, weapon_name: str):
        """View statistics for a specific weapon"""

        try:
            # Defer response to prevent timeout
            await ctx.defer()
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

            # Check if the guild has access to stats feature
            guild = Guild(self.bot.db, guild_data)
            if not guild.check_feature_access("stats"):
                embed = EmbedBuilder.create_error_embed(
                    "Premium Feature",
                    "Weapon statistics is a premium feature. Please upgrade to access this feature."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # Find the server
            server = None
            server_name = server_id
            for s in guild_data.get("servers", []):
                if s.get("server_id") == server_id:
                    server = Server(self.bot.db, s)
                    server_name = s.get("server_name", server_id)
                    break

            if not server:
                embed = EmbedBuilder.create_error_embed(
                    "Server Not Found",
                    f"Server with ID {server_id} not found in this guild."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # Import weapon utilities
            from utils.weapon_stats import get_weapon_category, is_actual_weapon, get_weapon_details

            # Query kills for this weapon
            pipeline = [
                {
                    "$match": {
                        "server_id": server_id,
                        "weapon": {"$regex": weapon_name, "$options": "i"},
                        "is_suicide": False
                    }
                },
                {
                    "$group": {
                        "_id": "$weapon",
                        "kills": {"$sum": 1},
                        "avg_distance": {"$avg": "$distance"},
                        "max_distance": {"$max": "$distance"},
                        "min_distance": {"$min": "$distance"},
                        "killers": {"$addToSet": "$killer_id"}
                    }
                },
                {
                    "$sort": {"kills": -1}
                },
                {
                    "$limit": 5
                }
            ]

            cursor = self.bot.db.kills.aggregate(pipeline)
            weapon_stats = await cursor.to_list(length=None)

            if not weapon_stats:
                embed = EmbedBuilder.create_error_embed(
                    "No Data",
                    f"No data found for weapons matching '{weapon_name}' on server {server_name}."
                , guild=guild_model)
                await ctx.send(embed=embed)
                return

            # Create embeds for each weapon
            embeds = []

            for weapon in weapon_stats:
                weapon_name = weapon["_id"]
                weapon_category = get_weapon_category(weapon_name)

                # Get top users of this weapon (only store names, no IDs)
                top_users_pipeline = [
                    {
                        "$match": {
                            "server_id": server_id,
                            "weapon": weapon_name,
                            "is_suicide": False
                        }
                    },
                    {
                        "$group": {
                            "_id": {"$toLower": "$killer_name"},
                            "name": {"$first": "$killer_name"},
                            "kills": {"$sum": 1},
                            "avg_distance": {"$avg": "$distance"},
                            "max_distance": {"$max": "$distance"}
                        }
                    },
                    {
                        "$sort": {"kills": -1}
                    },
                    {
                        "$limit": 5
                    }
                ]

                top_users_cursor = self.bot.db.kills.aggregate(top_users_pipeline)
                top_users = await top_users_cursor.to_list(length=None)

                # Get detailed weapon information
                weapon_details = get_weapon_details(weapon_name)

                # Create embed with weapon category
                embed = EmbedBuilder.create_base_embed(
                    f"{weapon_name} Statistics",
                    f"Weapon statistics on {server_name}"
                , guild=guild_model)

                # Add basic stats
                embed.add_field(name="Weapon Type", value=weapon_details.get("type", weapon_category.title()), inline=True)
                embed.add_field(name="Total Kills", value=str(weapon["kills"]), inline=True)
                embed.add_field(name="Unique Users", value=str(len(weapon["killers"])), inline=True)

                # Add weapon details if available
                if weapon_details.get("ammo"):
                    embed.add_field(name="Ammunition", value=weapon_details["ammo"], inline=True)
                if weapon_details.get("damage"):
                    embed.add_field(name="Damage", value=str(weapon_details["damage"]), inline=True)
                if weapon_details.get("effective_range"):
                    embed.add_field(name="Effective Range", value=weapon_details["effective_range"], inline=True)
                if weapon_details.get("fire_rate"):
                    embed.add_field(name="Fire Rate", value=weapon_details["fire_rate"], inline=True)

                # Add weapon description if available
                if weapon_details.get("description"):
                    embed.add_field(name="Description", value=weapon_details["description"], inline=False)

                # Add distance statistics in one field
                distance_info = []
                if weapon.get("avg_distance"):
                    distance_info.append(f"Avg: {round(weapon['avg_distance'], 1)}m")
                if weapon.get("min_distance"):
                    distance_info.append(f"Min: {round(weapon['min_distance'], 1)}m")
                if weapon.get("max_distance"):
                    distance_info.append(f"Max: {round(weapon['max_distance'], 1)}m")

                if distance_info:
                    embed.add_field(
                        name="Distance Stats", 
                        value="\n".join(distance_info), 
                        inline=False
                    )

                # Add top users (only show names, not IDs)
                if top_users:
                    top_users_str = "\n".join([
                        f"{i+1}. **{user['name']}**: {user['kills']} kills" +
                        (f" (max: {round(user['max_distance'], 1)}m)" if user.get('max_distance') else "")
                        for i, user in enumerate(top_users)
                    ])
                    embed.add_field(name="Top Users", value=top_users_str, inline=False)

                # Special note for non-weapon kills
                if not is_actual_weapon(weapon_name):
                    if weapon_name == "land_vehicle":
                        embed.add_field(
                            name="Special Note",
                            value="Vehicle kills represent players killed by vehicles",
                            inline=False
                        )
                    elif weapon_name in ["falling", "suicide_by_relocation"]:
                        embed.add_field(
                            name="Special Note",
                            value="This represents a death type rather than an actual weapon",
                            inline=False
                        )

                embeds.append(embed)

            # Get the weapon icon
            from utils.embed_icons import send_embed_with_icon, WEAPON_STATS_ICON, add_icon_to_embed, create_discord_file

            # Send the first embed with pagination if multiple
            if len(embeds) > 1:
                # For pagination, we have to use standard send first
                current_embed, view = paginate_embeds(embeds)
                # Add the icon to all embeds
                for embed in embeds:
                    add_icon_to_embed(embed, WEAPON_STATS_ICON)
                await ctx.send(embed=current_embed, view=view, file=create_discord_file(WEAPON_STATS_ICON))
            else:
                # Single embed can use our helper
                await send_embed_with_icon(ctx, embeds[0], WEAPON_STATS_ICON)

        except Exception as e:
            logger.error(f"Error getting weapon stats: {e}", exc_info=True)
            embed = EmbedBuilder.create_error_embed(
                "Error",
                f"An error occurred while getting weapon stats: {e}"
            , guild=guild_model)
            await ctx.send(embed=embed)


async def setup(bot):
    """Set up the Stats cog"""
    await bot.add_cog(Stats(bot))