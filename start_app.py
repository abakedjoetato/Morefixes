"""
Tower of Temptation PvP Statistics System Launcher

This script serves as the main entry point for both the Discord bot and web application
components of the Tower of Temptation PvP Statistics system. It will:

1. Start the Discord bot in a background process
2. Start the Flask web application

This allows both components to run simultaneously from a single entry point,
which is ideal for deployment on platforms like Replit.
"""
import os
import sys
import subprocess
import threading
import signal
import time
import logging
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("system.log")
    ]
)

logger = logging.getLogger(__name__)

# Global variables to track processes
processes: Dict[str, subprocess.Popen] = {}
running = True

def start_process(name: str, cmd: List[str], env: Optional[Dict[str, str]] = None) -> None:
    """Start a process and store it in the processes dictionary.
    
    Args:
        name: Name of the process for identification
        cmd: Command list to execute
        env: Optional environment variables
    """
    try:
        logger.info(f"Starting {name}...")
        
        # Merge current environment with additional vars if provided
        proc_env = os.environ.copy()
        if env:
            proc_env.update(env)
            
        proc = subprocess.Popen(
            cmd,
            env=proc_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        processes[name] = proc
        logger.info(f"{name} started with PID {proc.pid}")
        
        # Start a thread to monitor process output
        threading.Thread(target=monitor_output, args=(name, proc), daemon=True).start()
    except Exception as e:
        logger.error(f"Failed to start {name}: {e}")

def monitor_output(name: str, proc: subprocess.Popen) -> None:
    """Monitor and log the output of a process.
    
    Args:
        name: Process name
        proc: Process object
    """
    try:
        if proc.stdout:
            for line in proc.stdout:
                logger.info(f"[{name}] {line.strip()}")
    except Exception as e:
        logger.error(f"Error monitoring {name} output: {e}")
    
    exit_code = proc.poll()
    if exit_code is not None:
        logger.info(f"{name} exited with code {exit_code}")
        
        # Restart the process if it died and system is still running
        if running and exit_code != 0:
            logger.info(f"Restarting {name}...")
            if name == "discord_bot":
                start_discord_bot()
            elif name == "web_app":
                start_web_app()

def start_discord_bot() -> None:
    """Start the Discord bot component."""
    bot_cmd = ["python", "main.py"]
    start_process("discord_bot", bot_cmd)

def start_web_app() -> None:
    """Start the web application component."""
    web_cmd = ["python", "app.py"]
    # Set specific environment for web app if needed
    web_env = {"PORT": "5000"}
    start_process("web_app", web_cmd, web_env)

def cleanup() -> None:
    """Clean up all processes on shutdown."""
    global running
    running = False
    logger.info("Shutting down all components...")
    
    for name, proc in processes.items():
        try:
            logger.info(f"Terminating {name}...")
            proc.terminate()
            # Give process 5 seconds to terminate gracefully
            for _ in range(5):
                if proc.poll() is not None:
                    break
                time.sleep(1)
            
            # Force kill if still running
            if proc.poll() is None:
                logger.info(f"Force killing {name}...")
                proc.kill()
        except Exception as e:
            logger.error(f"Error terminating {name}: {e}")
    
    logger.info("All components stopped.")

def handle_signal(signum, frame) -> None:
    """Signal handler for graceful shutdown."""
    logger.info(f"Received signal {signum}, shutting down...")
    cleanup()
    sys.exit(0)

def main() -> None:
    """Main entry point to start all system components."""
    logger.info("Starting Tower of Temptation PvP Statistics System...")
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    # Start components
    start_discord_bot()
    start_web_app()
    
    logger.info("All components started successfully!")
    
    try:
        # Keep main thread alive to receive signals
        while running:
            # Check if processes are still running and restart if needed
            for name, proc in list(processes.items()):
                if proc.poll() is not None and running:
                    logger.warning(f"{name} has exited with code {proc.poll()}, restarting...")
                    if name == "discord_bot":
                        start_discord_bot()
                    elif name == "web_app":
                        start_web_app()
            time.sleep(5)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()

if __name__ == "__main__":
    main()