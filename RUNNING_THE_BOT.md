# Running the Tower of Temptation PvP Statistics Bot

This document explains how to run the Tower of Temptation PvP Statistics Discord Bot.

## Running Options

You have several options for running the Discord bot:

### Option 1: Use the Replit Run Button (Recommended)

The simplest way to run the bot is to use the Replit "Run" button, which will:

1. Start the Discord bot using our enhanced launcher script
2. Manage the bot process with automatic restart on errors
3. Display detailed connection and startup information

This is handled by the `run_discord_on_replit.py` file, which calls the bot's startup function in `main.py`.

### Option 2: Run via Command Line

To run the Discord bot from the command line, you have several options:

```bash
# Recommended launcher (same as Run button):
python run_discord_on_replit.py

# Alternative bash script launcher:
bash run-discord-bot.sh

# Original script:
bash discord_bot.sh
```

### Option 3: Use Replit Workflow

You can also use the Replit workflow:
- Go to the "Tools" tab
- Select "Workflows"
- Click the "Run" button next to "Discord Bot"

## Environment Variables

The bot requires several environment variables to function properly:

### Required Environment Variables
- `DISCORD_TOKEN` - Discord bot token
- `BOT_APPLICATION_ID` - Discord application ID
- `HOME_GUILD_ID` - ID of your home Discord server
- `MONGODB_URI` - MongoDB connection string

## Restarting the Bot

If you need to restart the bot:

1. Stop the current process (Ctrl+C or stop the Replit run)
2. Click the Run button again

## Troubleshooting

### Discord Bot Not Connecting

If the Discord bot fails to connect:

1. Check that `DISCORD_TOKEN` is set correctly
2. Verify that the bot has the necessary permissions
3. Check the logs for specific error messages

### Database Connection Issues

If the bot can't connect to the database:

1. Check that `MONGODB_URI` is configured correctly
2. Verify MongoDB is running and accessible
3. Check the bot.log file for specific error messages

## Monitoring and Logs

The bot produces several log files:

- `bot.log` - Discord bot specific logs
- `bot_validation.log` - Logs from validation checks
- Console output - Real-time logs from the bot

## Recent Fixes and Improvements

The following critical fixes have been applied to the bot:

1. **Circular Import Resolution**: Fixed circular imports in `models/event.py`, `models/faction.py`, and `models/rivalry.py` by properly moving imports inside methods
2. **Embed Builder Completion**: Implemented all missing methods in the `EmbedBuilder` class
3. **Server Validation**: Enhanced `server_utils.py` with robust multi-tier fallback approach for server validation
4. **Coroutine Handling**: Fixed coroutine handling in the Help cog
5. **Guild Model Consistency**: Standardized Guild model methods for consistent ID handling
6. **Database Access**: Improved database access patterns and connection handling
7. **Multi-Guild Isolation**: Enhanced data isolation between different Discord guilds

All these fixes have been verified and tested to ensure the bot runs properly without errors.

## Additional Resources

For more detailed information, see:

- `TESTING_WORKFLOW.md` - Instructions for testing the bot
- `README.md` - General project information
- `PvP_Stats_Bot_Manual.md` - Bot command reference
- `comprehensive_fix_implementation.py` - Script that verifies all fixes are properly applied
- `fix_embeds.py` - Script that validates embed functionality