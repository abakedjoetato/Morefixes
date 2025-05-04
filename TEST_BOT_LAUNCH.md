# Bot Launch Test Instructions

## Testing the Discord Bot Launch Process

This document provides step-by-step instructions for testing that the Tower of Temptation Discord bot launches correctly using the Replit Run button.

### Prerequisites

Before testing, ensure all required environment variables are set in Replit Secrets:
- `DISCORD_TOKEN`
- `BOT_APPLICATION_ID`
- `HOME_GUILD_ID`
- `MONGODB_URI`

### Test Procedure

1. **Prepare for testing**
   - Make sure no other instances of the bot are running
   - Close any terminal processes that might be using the bot

2. **Launch using Run button**
   - Click the **Run** button at the top of the Replit interface
   - Watch the console output

3. **Verification checks**
   - You should see messages about connecting to MongoDB
   - You should see messages about loading all cogs, including "bounties"
   - You should see a message confirming connection to Discord
   - The final message should be "Bot is ready for commands!"

4. **Stopping the bot**
   - Click the **Stop** button in the Replit interface
   - Verify the bot process stops completely

### Expected Output

The console should show output similar to this:

```
Starting Tower of Temptation Discord Bot...
Initializing bot...
Initializing database connection...
Connecting to MongoDB database: tower_of_temptation
Successfully connected to MongoDB
Database connection established
Loading cogs...
[List of loaded cogs]
Loaded cog: bounties
Starting bot...
Bot connected to Discord as Emeralds Killfeed#XXXX
Bot is in X guilds
Bot is ready for commands!
```

### Troubleshooting

If the bot fails to start:
1. Check the error messages in the console
2. Verify all environment variables are correctly set
3. Ensure the Discord token is valid
4. Confirm MongoDB connection parameters are correct