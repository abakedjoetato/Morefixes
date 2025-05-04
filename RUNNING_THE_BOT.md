# Running the Tower of Temptation PvP Statistics System

This document explains how to run the complete Tower of Temptation PvP Statistics System, which includes both the Discord bot and the web dashboard.

## System Components

The system consists of two main components:

1. **Discord Bot** - Handles all Discord interactions, command processing, and game statistics tracking
2. **Web Dashboard** - Provides a web interface for viewing statistics, leaderboards, and rivalries

## Running Options

You have several options for running the system:

### Option 1: Run Everything with One Command (Recommended)

The simplest way to run the entire system is to use the Replit "Run" button, which will:

1. Start the Discord bot in the background
2. Start the web dashboard
3. Manage both components together

This is handled by the `main.py` file, which imports `start_app.py` to manage both components.

### Option 2: Run Components Individually

If you need to run just one component or troubleshoot a specific part:

#### Discord Bot Only

To run just the Discord bot:

```bash
bash discord_bot.sh
```

Or use the Replit workflow:
- Go to the "Tools" tab
- Select "Workflows"
- Click the "Run" button next to "Discord Bot"

#### Web Dashboard Only

To run just the web dashboard:

```bash
bash start_web_app.sh
```

Or use the Replit workflow:
- Go to the "Tools" tab
- Select "Workflows"
- Click the "Run" button next to "Web Application"

### Option 3: Run Complete System Script

You can also run both components with the `run_complete_system.sh` script:

```bash
bash run_complete_system.sh
```

## Environment Variables

The system requires several environment variables to function properly:

### Discord Bot Requirements
- `DISCORD_TOKEN` - Discord bot token
- `BOT_APPLICATION_ID` - Discord application ID
- `HOME_GUILD_ID` - ID of your home Discord server
- `MONGODB_URI` - MongoDB connection string

### Web Dashboard Requirements
- `DATABASE_URL` - PostgreSQL database connection URL
- `SESSION_SECRET` - Secret key for session management

## Accessing the Web Dashboard

Once the system is running, you can access the web dashboard at:

- In Replit: Click the webview button
- Local development: http://localhost:5000

## Restarting the System

If you need to restart the entire system:

1. Stop the current process (Ctrl+C or stop the Replit run)
2. Click the Run button again

## Troubleshooting

### Discord Bot Not Connecting

If the Discord bot fails to connect:

1. Check that `DISCORD_TOKEN` is set correctly
2. Verify that the bot has the necessary permissions
3. Check the logs for specific error messages

### Web Dashboard Not Working

If the web dashboard isn't working:

1. Check that `DATABASE_URL` is configured correctly
2. Ensure PostgreSQL is running and accessible
3. Check for errors in the web app log output

### Both Components Failing

If both components fail:

1. Check all environment variables
2. Restart the Replit environment
3. Check Discord API status at https://discordstatus.com/

## Monitoring and Logs

The system produces several log files:

- `bot.log` - Discord bot specific logs
- `system.log` - Combined system logs
- Console output - Real-time logs from both components

## Additional Resources

For more detailed information, see:

- `TESTING_WORKFLOW.md` - Instructions for testing the system
- `README.md` - General project information
- `PvP_Stats_Bot_Manual.md` - Bot command reference