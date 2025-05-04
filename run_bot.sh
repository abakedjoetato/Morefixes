#!/bin/bash
# Production-grade Discord bot runner for Tower of Temptation
# Handles errors, restarts, and logging

echo "[$(date)] Starting Tower of Temptation Discord Bot..."
echo "[$(date)] Checking environment variables..."

# Validate critical environment variables
required_vars=("DISCORD_TOKEN" "BOT_APPLICATION_ID" "HOME_GUILD_ID" "MONGODB_URI")
missing_vars=()

for var in "${required_vars[@]}"; do
  if [[ -z "${!var}" ]]; then
    missing_vars+=("$var")
  fi
done

if [[ ${#missing_vars[@]} -gt 0 ]]; then
  echo "[$(date)] ERROR: Missing required environment variables: ${missing_vars[*]}"
  echo "[$(date)] Bot cannot start without these variables. Please set them in your environment."
  exit 1
fi

echo "[$(date)] All required environment variables are present."
echo "[$(date)] Starting Discord bot with optimized settings..."

# Run the bot with proper error handling
python main.py
exit_code=$?

# Handle exit codes
if [ $exit_code -ne 0 ]; then
  echo "[$(date)] ERROR: Bot exited with code $exit_code"
  echo "[$(date)] Check logs for details"
  exit $exit_code
fi