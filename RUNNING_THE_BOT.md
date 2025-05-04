# Running the Tower of Temptation PvP Statistics Bot

This document explains how to run the Tower of Temptation PvP Statistics Discord Bot.

## Running Options

You have several options for running the Discord bot:

### Option 1: Use the Replit Run Button (Recommended)

The simplest way to run the bot is to use the Replit "Run" button, which will:

1. Start the Discord bot using the discord_bot.sh script
2. Manage the bot process with automatic restart on errors

This is handled by the `main.py` file, which calls the bot's startup function.

### Option 2: Run via Command Line

To run the Discord bot from the command line:

```bash
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

## Additional Resources

For more detailed information, see:

- `TESTING_WORKFLOW.md` - Instructions for testing the bot
- `README.md` - General project information
- `PvP_Stats_Bot_Manual.md` - Bot command reference