"""
Tower of Temptation PvP Statistics Bot Main Entry Point

This file serves as the entry point for the Replit Run button.
It launches the Discord bot with all the required configurations.
"""
import os
import sys
import asyncio
from bot import startup

if __name__ == "__main__":
    # Run the bot's startup function
    try:
        asyncio.run(startup())
    except KeyboardInterrupt:
        print("Bot shutdown requested")
        sys.exit(0)