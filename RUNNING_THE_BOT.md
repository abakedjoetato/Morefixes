# Tower of Temptation Discord Bot - Running Instructions

## Using the Replit Run Button

The Discord bot is configured to start automatically when you press the Replit Run button. This is the simplest and recommended way to run the bot:

1. Make sure all environment variables are set in Replit Secrets:
   - `DISCORD_TOKEN`
   - `BOT_APPLICATION_ID`
   - `HOME_GUILD_ID`
   - `MONGODB_URI`

2. Click the **Run** button at the top of the Replit interface.

3. Wait for the bot to initialize and connect to Discord. You'll see a message like:
   ```
   Bot connected to Discord as Emeralds Killfeed#XXXX (ID: XXXXXXXXXX)
   Bot is in X guilds
   Bot is ready for commands!
   ```

4. To stop the bot, simply click the **Stop** button in the Replit interface.

## Manual Execution

If you need to run the bot manually, you can use the following scripts:

- **Main Run Script**: `./run_bot.sh`
  This script validates environment variables before starting the bot.

- **Verification Script**: `python verify_bot.py`
  This script performs a comprehensive verification of all bot components.

## Deployment

For production deployment, the bot is configured to automatically use the main.py file as its entry point.

## Troubleshooting

If the bot fails to start:

1. Check the logs for error messages
2. Verify that all required environment variables are set
3. Run the verification script to diagnose issues: `python verify_bot.py`
4. Ensure MongoDB connection is working
5. Verify Discord token is valid

## Workflows

The bot is set up to be run as a single process. There's no need for separate workflows as the main.py file handles all the necessary initialization and connection to Discord and MongoDB.