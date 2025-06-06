# Tower of Temptation PvP Statistics Bot

A robust Discord bot for tracking Tower of Temptation PvP gameplay data, offering multi-guild isolation, player statistics, and advanced rivalry tracking with comprehensive debugging tools.

## Features

- **PvP Kill Tracking**: Real-time monitoring and detailed statistics for player kills
- **Multi-Guild Support**: Complete isolation of data between Discord servers
- **Player Rivalries**: Track nemesis and prey relationships between players
- **Bounty System**: Place bounties on players and claim rewards for fulfilling them
- **Server Statistics**: Detailed statistics for each game server
- **Historical Parsing**: Process historical game logs to build a comprehensive statistics database

## Running the Bot on Replit

### Quick Start Guide

1. **Start the Bot**: Simply click the **Run** button at the top of the Replit interface.
2. **Monitor Status**: Watch the console for startup messages. You should see:
   - "Connected to MongoDB"
   - "Bot is ready!"
   - "Logged in as Tower of Temptation PvP Statistics Bot"
3. **Accessing the Bot**: The bot will appear online in your Discord server
4. **Stop the Bot**: Click the **Stop** button to terminate the process.

### Using the Discord Bot Workflow

You can also run the Discord bot using Replit workflows:

1. Go to the "Tools" tab in Replit
2. Select "Workflows"
3. Click the "Run" button next to "Discord Bot"

### Troubleshooting

If the bot fails to start:
- Check that all required environment variables are set in Replit Secrets
- Verify MongoDB connection is working
- Check Discord token validity and permissions

For detailed instructions, see [RUNNING_THE_BOT.md](RUNNING_THE_BOT.md).

## Bot Architecture

The Tower of Temptation PvP Statistics Bot is designed with a modular architecture:

### Discord Bot Components

The Discord bot is responsible for:
- Interacting with users via Discord commands
- Processing game statistics from CSV files
- Managing player leaderboards and rivalries
- Handling the bounty system
- Providing real-time statistics via Discord embeds

## Environment Variables

The bot requires the following environment variables:

- `DISCORD_TOKEN`: Your Discord bot token
- `BOT_APPLICATION_ID`: Your Discord application ID  
- `HOME_GUILD_ID`: Discord ID of your home/main guild
- `MONGODB_URI`: MongoDB connection string

## Multi-Guild Isolation

The Tower of Temptation PvP Statistics Bot is designed with robust multi-guild isolation:

- Each Discord server (guild) has its own isolated data
- Player statistics are tracked separately for each guild
- Server configurations are guild-specific
- Commands operate only on the guild where they're executed

This ensures that multiple Discord communities can use the bot without data leakage between them.

## Database Architecture

The bot uses MongoDB for storage and retrieval of all data:

### MongoDB Collections
- **guilds**: Discord server configurations
- **players**: Player statistics and profiles
- **events**: Kill events and other game events
- **bounties**: Active and completed bounties
- **factions**: Team or faction information
- **rivalries**: Tracked player rivalries

## Bot Utilities

The Tower of Temptation PvP Statistics Bot includes several utilities for maintenance and management:

### Bot Management Scripts

```bash
# Start the Discord bot
./discord_bot.sh

# Apply all bot fixes
python comprehensive_bot_fixes.py
```

### Diagnostic Tools

```bash
# Verify bot startup and environment
python validate_bot_startup.py

# Test comprehensive functionality
python test_all_functionality.py

# Check multi-guild isolation
python test_multi_guild_isolation.py

# Diagnose server issues
python diagnose_server.py
```

### Database Tools

```bash
# Check database connectivity
python check_db.py

# Fix type inconsistencies in the database
python fix_server_validation.py
```

## Data Security

All server IDs, user IDs, and other sensitive identifiers are properly typed and validated throughout the codebase:

- Guild IDs are stored as integers in MongoDB
- Server IDs (for game servers) are stored as strings for compatibility
- All IDs are validated before use in database operations
- Input validation is performed on all user-submitted data

---

Tower of Temptation PvP Statistics Bot © 2025