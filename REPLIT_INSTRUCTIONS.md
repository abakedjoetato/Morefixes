# Running the Tower of Temptation Discord Bot on Replit

This document explains how to run and manage the Discord bot on Replit using the Run button.

## Prerequisites

Before starting the bot, ensure you have set up the following Replit Secrets:

1. `DISCORD_TOKEN` - Your Discord bot token
2. `BOT_APPLICATION_ID` - Your Discord application ID
3. `HOME_GUILD_ID` - The ID of your primary Discord server
4. `MONGODB_URI` - MongoDB connection string

To set these secrets:
1. Click on the "Secrets" tool in the left sidebar (lock icon)
2. Click "Add new secret"
3. Enter the key and value
4. Click "Add Secret"

## Starting the Bot

### Method 1: Using the Run Button (Recommended)

1. Simply click the **Run** button at the top of the Replit interface
2. The bot will automatically start using main.py
3. You'll see console output as the bot initializes and connects

### Method 2: Using Start Script

If the Run button doesn't work as expected, you can:

1. Open a Shell terminal in Replit
2. Run the following command:
   ```
   ./start_bot.sh
   ```

## Verifying the Bot is Running

The bot is running correctly when you see the following messages:

```
Successfully connected to MongoDB
Bot connected to Discord as Emeralds Killfeed
Bot is in X guilds
Bot is ready for commands!
```

## Stopping the Bot

To stop the bot:

1. Click the **Stop** button at the top of the Replit interface
2. This will terminate the bot process

## Troubleshooting

If the bot fails to start:

1. Check that all required Replit Secrets are set correctly
2. Look for error messages in the console output
3. Verify MongoDB connection by checking the logs
4. Ensure Discord token is valid

## Maintenance

The bot includes several maintenance utilities:

- `python maintenance.py help` - Show all maintenance commands
- `python maintenance.py restart` - Restart the bot
- `python maintenance.py diagnose` - Run diagnostics
- `python verify_bot.py` - Verify bot configuration

## Creating a Run Configuration

If you need to recreate the Run configuration:

1. Ensure main.py is set up to run the bot (it is by default)
2. The bot will start automatically when main.py is executed
3. No additional configuration is needed