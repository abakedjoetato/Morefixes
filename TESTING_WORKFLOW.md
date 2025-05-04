# Tower of Temptation Discord Bot - Testing Workflow

This document explains the comprehensive testing workflow for the Tower of Temptation PvP Statistics Discord Bot.

## Testing Philosophy

Following the guidelines in `rule.md`, our testing philosophy is to ensure:

1. **Production-Ready Testing**: All components must be tested in a real-world environment
2. **Multi-Guild Isolation**: All features must properly isolate data between different Discord guilds
3. **Holistic Validation**: All systems must be tested together, not just in isolation
4. **Live Environment Verification**: All commands must be verified in a live Discord environment

## Testing Workflow

The testing workflow is divided into several stages, each validating different aspects of the bot:

### 1. Component Verification

This stage verifies that all individual components are working correctly:

```bash
python verify_bot.py
```

This script checks:
- Environment variables
- Module imports
- Database connectivity
- Discord API connectivity
- Cog loading integrity

### 2. Multi-Guild Isolation Testing

This stage tests that all database operations properly isolate data between guilds:

```bash
python test_multi_guild_isolation.py
```

This script validates:
- Guild models are properly isolated
- Player data is separated by guild
- Events and kills are filtered by guild
- Bounties and economy data respect guild boundaries

### 3. Comprehensive Functionality Testing

This stage tests all bot commands and features:

```bash
python test_all_functionality.py
```

This script tests:
- All slash commands and traditional commands
- Command argument handling and validation
- Error handling and edge cases
- Database operations and data persistence
- CSV parsing and historical data import

### 4. Live Startup Validation

This stage validates the bot's startup process in a real environment:

```bash
python validate_bot_startup.py
```

This script checks:
- Bot initialization
- Command registration
- Discord connection
- Guild-specific configuration loading

### 5. Full Testing Workflow

To run all tests in sequence, use:

```bash
bash discord_bot_workflow.sh
```

This script runs all the above tests and provides a comprehensive report.

## Running the Bot

After verifying that all tests pass, you can run the bot with:

```bash
bash start_bot.sh
```

Or use the unified workflow script:

```bash
bash start_workflow.sh bot
```

## Continuous Integration

Every code change should be validated with the full testing workflow:

```bash
bash start_workflow.sh test
```

## Deployment

The bot is configured to run automatically when the Replit Run button is pressed, which executes `python main.py` as specified in the `.replit` configuration.

## Troubleshooting

If you encounter issues:

1. Check the log files (`bot.log`, `bot_fixes.log`, `bot_validation_*.log`)
2. Run specific test stages to isolate the problem
3. Use the comprehensive fix script to apply all critical fixes:

```bash
python comprehensive_bot_fixes.py
```

## Secret Management

The bot requires several environment variables to function:
- `DISCORD_TOKEN`: Discord bot token
- `BOT_APPLICATION_ID`: Discord application ID
- `HOME_GUILD_ID`: Home guild ID for global command registration
- `MONGODB_URI`: MongoDB connection string

These should be configured in Replit Secrets.