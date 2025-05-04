"""
Parser utilities for Tower of Temptation PvP Statistics Discord Bot.

This module provides:
1. Integration of the three-part parsing system:
   - Historical CSV parser (one-time parsing of historical data)
   - 5-minute automatic CSV parser (ongoing parsing of CSV files)
   - Deadside.log parser (real-time event processing)
2. Helper functions for normalizing data between parsers
3. Utilities for ensuring parser coordination and avoiding duplicates
"""
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set, Tuple

from utils.csv_parser import CSVParser
from utils.log_parser import LogParser, parse_log_file

logger = logging.getLogger(__name__)

class ParserCoordinator:
    """Coordinates between the three parser subsystems to avoid duplicate events"""
    
    def __init__(self):
        """Initialize parser coordinator"""
        self.last_processed_csv_timestamps = {}  # server_id -> timestamp
        self.last_processed_log_timestamps = {}  # server_id -> timestamp
        self.processed_event_hashes = set()  # Set to track processed event hashes
        self.recent_event_window = 3600  # 1 hour window for deduplication
        
    def generate_event_hash(self, event: Dict[str, Any]) -> str:
        """Generate a hash for an event to check for duplicates
        
        Args:
            event: Event dictionary
            
        Returns:
            str: Hash string
        """
        # For kill events
        if "killer_id" in event and "victim_id" in event:
            timestamp = event.get("timestamp", "")
            if isinstance(timestamp, datetime):
                timestamp = timestamp.isoformat()
                
            # Create a unique string from key event properties
            hash_string = f"{timestamp}_{event.get('killer_id', '')}_{event.get('victim_id', '')}_{event.get('weapon', '')}"
            return hash_string
            
        # For mission events
        elif "event_type" in event and event.get("event_type") == "mission":
            timestamp = event.get("timestamp", "")
            if isinstance(timestamp, datetime):
                timestamp = timestamp.isoformat()
                
            hash_string = f"{timestamp}_{event.get('mission_name', '')}_{event.get('location', '')}"
            return hash_string
            
        # For other game events (airdrop, helicrash, etc.)
        elif "event_type" in event and event.get("event_type") in ["airdrop", "helicrash", "trader", "convoy"]:
            timestamp = event.get("timestamp", "")
            if isinstance(timestamp, datetime):
                timestamp = timestamp.isoformat()
                
            hash_string = f"{timestamp}_{event.get('event_type', '')}_{event.get('event_id', '')}"
            return hash_string
            
        # For connection events
        elif "event_type" in event and event.get("event_type") in ["register", "unregister", "join", "kick"]:
            timestamp = event.get("timestamp", "")
            if isinstance(timestamp, datetime):
                timestamp = timestamp.isoformat()
                
            hash_string = f"{timestamp}_{event.get('event_type', '')}_{event.get('player_id', '')}"
            return hash_string
            
        # Fallback for unknown event types
        else:
            timestamp = event.get("timestamp", "")
            if isinstance(timestamp, datetime):
                timestamp = timestamp.isoformat()
                
            return f"{timestamp}_{hash(str(event))}"
    
    def is_duplicate_event(self, event: Dict[str, Any]) -> bool:
        """Check if an event has already been processed
        
        Args:
            event: Event dictionary
            
        Returns:
            bool: True if duplicate, False otherwise
        """
        event_hash = self.generate_event_hash(event)
        
        if event_hash in self.processed_event_hashes:
            return True
            
        # Add to processed set
        self.processed_event_hashes.add(event_hash)
        
        # Keep the set from growing too large by periodically pruning old entries
        self._prune_old_hashes()
        
        return False
    
    def _prune_old_hashes(self):
        """Remove old event hashes to prevent memory growth"""
        # Every 1000 events, check if we should prune
        if len(self.processed_event_hashes) > 10000:
            # Keep only the most recent 1000 events
            # In a real implementation this would be time-based, but
            # that would require storing timestamps with each hash
            if len(self.processed_event_hashes) > 1000:
                self.processed_event_hashes = set(list(self.processed_event_hashes)[-1000:])
    
    def update_csv_timestamp(self, server_id: str, timestamp: datetime):
        """Update last processed CSV timestamp for a server
        
        Args:
            server_id: Server ID
            timestamp: Last processed timestamp
        """
        self.last_processed_csv_timestamps[server_id] = timestamp
    
    def update_log_timestamp(self, server_id: str, timestamp: datetime):
        """Update last processed log timestamp for a server
        
        Args:
            server_id: Server ID
            timestamp: Last processed timestamp
        """
        self.last_processed_log_timestamps[server_id] = timestamp
    
    def get_last_csv_timestamp(self, server_id: str) -> Optional[datetime]:
        """Get last processed CSV timestamp for a server
        
        Args:
            server_id: Server ID
            
        Returns:
            datetime or None: Last processed timestamp
        """
        return self.last_processed_csv_timestamps.get(server_id)
    
    def get_last_log_timestamp(self, server_id: str) -> Optional[datetime]:
        """Get last processed log timestamp for a server
        
        Args:
            server_id: Server ID
            
        Returns:
            datetime or None: Last processed timestamp
        """
        return self.last_processed_log_timestamps.get(server_id)
    
    def should_process_csv(self, server_id: str, csv_timestamp: datetime) -> bool:
        """Check if a CSV file should be processed
        
        Args:
            server_id: Server ID
            csv_timestamp: Timestamp of the CSV file
            
        Returns:
            bool: True if should process, False otherwise
        """
        last_timestamp = self.get_last_csv_timestamp(server_id)
        
        # If we haven't processed any CSV for this server, process it
        if last_timestamp is None:
            return True
            
        # Process only if it's newer than the last processed timestamp
        return csv_timestamp > last_timestamp
    
    def should_process_log(self, server_id: str, log_timestamp: datetime) -> bool:
        """Check if a log entry should be processed
        
        Args:
            server_id: Server ID
            log_timestamp: Timestamp of the log entry
            
        Returns:
            bool: True if should process, False otherwise
        """
        last_timestamp = self.get_last_log_timestamp(server_id)
        
        # If we haven't processed any logs for this server, process it
        if last_timestamp is None:
            return True
            
        # Process only if it's newer than the last processed timestamp
        return log_timestamp > last_timestamp

# Create a global coordinator instance
parser_coordinator = ParserCoordinator()

def normalize_event_data(event: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize event data from different parser sources
    
    Ensures consistent field names and data types across all parser outputs.
    
    Args:
        event: Raw event dictionary
        
    Returns:
        Dict: Normalized event dictionary
    """
    normalized = event.copy()
    
    # Ensure timestamp is datetime
    if "timestamp" in normalized:
        timestamp = normalized["timestamp"]
        if isinstance(timestamp, str):
            try:
                # Try ISO format first
                normalized["timestamp"] = datetime.fromisoformat(timestamp)
            except ValueError:
                try:
                    # Try other common formats
                    common_formats = [
                        "%Y.%m.%d-%H.%M.%S",
                        "%Y.%m.%d-%H.%M.%S:%f",
                        "%Y-%m-%d %H:%M:%S",
                        "%Y-%m-%d %H:%M:%S.%f"
                    ]
                    
                    for fmt in common_formats:
                        try:
                            normalized["timestamp"] = datetime.strptime(timestamp, fmt)
                            break
                        except ValueError:
                            continue
                            
                    # If we still haven't parsed it, use current time
                    if isinstance(normalized["timestamp"], str):
                        logger.warning(f"Could not parse timestamp: {timestamp}")
                        normalized["timestamp"] = datetime.utcnow()
                except Exception as e:
                    logger.error(f"Error parsing timestamp '{timestamp}': {e}")
                    normalized["timestamp"] = datetime.utcnow()
    else:
        # If no timestamp, add current time
        normalized["timestamp"] = datetime.utcnow()
    
    # Normalize player identifiers
    if "killer_id" in normalized and normalized["killer_id"] is None:
        normalized["killer_id"] = ""
        
    if "victim_id" in normalized and normalized["victim_id"] is None:
        normalized["victim_id"] = ""
        
    if "player_id" in normalized and normalized["player_id"] is None:
        normalized["player_id"] = ""
    
    # Normalize string fields
    for field in ["killer_name", "victim_name", "player_name", "weapon", "location"]:
        if field in normalized and normalized[field] is None:
            normalized[field] = ""
    
    # Normalize numeric fields
    for field in ["distance"]:
        if field in normalized and normalized[field] is None:
            normalized[field] = 0
            
        # Convert string distances to integers
        if field in normalized and isinstance(normalized[field], str):
            try:
                normalized[field] = int(float(normalized[field]))
            except (ValueError, TypeError):
                normalized[field] = 0
    
    return normalized

def categorize_event(event: Dict[str, Any]) -> str:
    """Categorize an event by type
    
    Args:
        event: Event dictionary
        
    Returns:
        str: Event category (kill, suicide, connection, mission, game_event)
    """
    # If event has an explicit type, use it
    if "event_type" in event:
        event_type = event["event_type"]
        if event_type in ["register", "unregister", "join", "kick"]:
            return "connection"
        elif event_type == "mission":
            return "mission"
        elif event_type in ["airdrop", "helicrash", "trader", "convoy"]:
            return "game_event"
            
    # Kill events have killer and victim fields
    if "killer_id" in event and "victim_id" in event:
        # Check for suicide
        if event["killer_id"] and event["victim_id"] and event["killer_id"] == event["victim_id"]:
            return "suicide"
        return "kill"
        
    # Connection events have player_id and action fields
    if "player_id" in event and "action" in event:
        return "connection"
        
    # Unknown event type
    return "unknown"