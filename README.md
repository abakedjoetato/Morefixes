# Tower of Temptation PvP Statistics System

A comprehensive gaming statistics system that combines a powerful Discord bot with a web dashboard for tracking Tower of Temptation PvP gameplay data. This system offers multi-guild isolation, robust player statistics, and advanced rivalry tracking.

## Features

- **PvP Kill Tracking**: Real-time monitoring and detailed statistics for player kills
- **Multi-Guild Support**: Complete isolation of data between Discord servers
- **Player Rivalries**: Track nemesis and prey relationships between players
- **Bounty System**: Place bounties on players and claim rewards for fulfilling them
- **Server Statistics**: Detailed statistics for each game server
- **Web Dashboard**: View leaderboards, stats, and player information on a responsive web interface
- **Historical Parsing**: Process historical game logs to build a comprehensive statistics database

## Running the Complete System on Replit

### Quick Start Guide

1. **Start the System**: Simply click the **Run** button at the top of the Replit interface.
2. **Monitor Status**: Watch the console for startup messages. You should see:
   - "Starting Tower of Temptation PvP Statistics System..."
   - "Discord Bot started with PID [number]"
   - "Web Application started with PID [number]"
   - "All components started successfully!"
3. **Access Components**: 
   - Web Dashboard: Available at the Replit webview
   - Discord Bot: Will appear online in your Discord server
4. **Stop the System**: Click the **Stop** button to terminate all processes.

### Running Individual Components

You can also run just the Discord bot or just the web application using Replit workflows:

1. Go to the "Tools" tab in Replit
2. Select "Workflows"
3. Choose one of the following:
   - "Discord Bot" - Runs only the Discord bot
   - "Web Application" - Runs only the web dashboard
   - "Complete System" - Runs both components together

### Troubleshooting

If the system fails to start:
- Check that all required environment variables are set in Replit Secrets
- Verify MongoDB and PostgreSQL connections are working
- Check Discord token validity and permissions

For detailed instructions, see [RUNNING_THE_BOT.md](RUNNING_THE_BOT.md).

## System Architecture

The Tower of Temptation PvP Statistics System consists of two main components:

### 1. Discord Bot

The Discord bot component is responsible for:
- Interacting with users via Discord commands
- Processing game statistics from CSV files
- Managing player leaderboards and rivalries
- Handling the bounty system
- Providing real-time statistics via Discord embeds

### 2. Web Dashboard

The web application provides:
- A visual overview of PvP statistics
- Leaderboards for top players
- Rivalry tracking and visualization
- Admin controls for system configuration
- Server performance statistics

## Environment Variables

The system requires the following environment variables:

### Discord Bot
- `DISCORD_TOKEN`: Your Discord bot token
- `BOT_APPLICATION_ID`: Your Discord application ID
- `HOME_GUILD_ID`: Discord ID of your home/main guild
- `MONGODB_URI`: MongoDB connection string

### Web Dashboard
- `DATABASE_URL`: PostgreSQL database connection string
- `SESSION_SECRET`: Secret key for session management
- `PORT`: Web server port (default: 5000)

## Multi-Guild Isolation

The Tower of Temptation PvP Statistics System is designed with robust multi-guild isolation:

- Each Discord server (guild) has its own isolated data
- Player statistics are tracked separately for each guild
- Server configurations are guild-specific
- Commands operate only on the guild where they're executed

This ensures that multiple Discord communities can use the bot without data leakage between them.

## Database Architecture

The system uses two separate databases:

1. **MongoDB** - For the Discord bot's real-time data:
   - Player statistics
   - Kill events
   - Faction information
   - Rivalries and bounties

2. **PostgreSQL** - For the web dashboard:
   - User accounts and authentication
   - Dashboard configuration
   - Performance metrics
   - Long-term statistics

## System Utilities

The Tower of Temptation PvP Statistics System includes several utilities for maintenance and management:

### Bot Management Scripts

```bash
# Start the complete system (both bot and web app)
./run_complete_system.sh

# Start only the Discord bot
./discord_bot.sh

# Start only the web application
./start_web_app.sh

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

Tower of Temptation PvP Statistics System © 2025