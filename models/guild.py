"""
Guild model for Tower of Temptation PvP Statistics Bot

This module defines the Guild data structure for Discord guilds.
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional, ClassVar, List
import uuid

from models.base_model import BaseModel

logger = logging.getLogger(__name__)

class Guild(BaseModel):
    """Discord guild configuration"""
    collection_name: ClassVar[str] = "guilds"

    def to_dict(self) -> Dict[str, Any]:
        """Convert Guild object to dictionary
        
        Returns:
            Dict containing all guild data
        """
        return {
            "_id": self._id,
            "guild_id": self.guild_id,
            "name": self.name,
            "premium_tier": self.premium_tier,
            "admin_role_id": self.admin_role_id,
            "admin_users": self.admin_users,
            "servers": self.servers,
            "color_primary": self.color_primary,
            "color_secondary": self.color_secondary, 
            "color_accent": self.color_accent,
            "icon_url": self.icon_url,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    def __init__(
        self,
        db,
        guild_id: Optional[str] = None,
        name: Optional[str] = None,
        premium_tier: int = 0,
        admin_role_id: Optional[str] = None,
        admin_users: Optional[List[str]] = None,
        servers: Optional[List[Dict[str, Any]]] = None,
        color_primary: str = "#7289DA",
        color_secondary: str = "#FFFFFF",
        color_accent: str = "#23272A",
        icon_url: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        **kwargs
    ):
        self._id = None
        self.db = db
        self.guild_id = guild_id
        self.name = name
        self.premium_tier = premium_tier
        self.admin_role_id = admin_role_id
        self.admin_users = admin_users or []
        self.color_primary = color_primary
        self.color_secondary = color_secondary
        self.color_accent = color_accent
        self.icon_url = icon_url
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

        self.servers = servers or []

        # Add any additional guild attributes
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)

    async def add_server(self, server_data: Dict[str, Any]) -> bool:
        """Add a server to the guild

        Args:
            server_data: Server configuration dictionary

        Returns:
            bool: True if added successfully, False otherwise
        """
        if not server_data.get("server_id"):
            return False

        # Add server to list
        self.servers.append(server_data)
        self.updated_at = datetime.utcnow()

        # Update in database
        result = await self.db.guilds.update_one(
            {"guild_id": self.guild_id},
            {
                "$set": {
                    "servers": self.servers,
                    "updated_at": self.updated_at
                }
            }
        )

        return result.modified_count > 0

    async def remove_server(self, server_id: str) -> bool:
        """Remove a server from the guild

        Args:
            server_id: Server ID to remove

        Returns:
            bool: True if removed successfully, False otherwise
        """
        # Find and remove server
        self.servers = [s for s in self.servers if str(s.get("server_id")) != str(server_id)]
        self.updated_at = datetime.utcnow()

        # Update in database
        result = await self.db.guilds.update_one(
            {"guild_id": self.guild_id},
            {
                "$set": {
                    "servers": self.servers,
                    "updated_at": self.updated_at
                }
            }
        )

        return result.modified_count > 0

    async def get_server(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get a server by ID

        Args:
            server_id: Server ID to find

        Returns:
            Optional[Dict]: Server data if found, None otherwise
        """
        for server in self.servers:
            if str(server.get("server_id")) == str(server_id):
                return server
        return None

    def get_max_servers(self) -> int:
        """Get maximum number of servers allowed for guild's tier"""
        from config import PREMIUM_TIERS
        tier_info = PREMIUM_TIERS.get(self.premium_tier, {})
        return tier_info.get("max_servers", 1)

    @classmethod
    async def get_by_guild_id(cls, db, guild_id: str) -> Optional['Guild']:
        """Get a guild by guild_id

        Args:
            db: Database connection
            guild_id: Discord guild ID

        Returns:
            Guild object or None if not found
        """
        document = await db.guilds.find_one({"guild_id": guild_id})
        return cls.from_document(document, db) if document else None

    async def set_premium_tier(self, db, tier: int) -> bool:
        """Set premium tier for guild

        Args:
            db: Database connection
            tier: Premium tier (0-3)

        Returns:
            True if updated successfully, False otherwise
        """
        if tier < 0 or tier > 3:
            return False

        self.premium_tier = tier
        self.updated_at = datetime.utcnow()

        # Update in database
        result = await db.guilds.update_one(
            {"guild_id": self.guild_id},
            {"$set": {
                "premium_tier": self.premium_tier,
                "updated_at": self.updated_at
            }}
        )

        return result.modified_count > 0

    async def set_admin_role(self, db, role_id: str) -> bool:
        """Set admin role for guild

        Args:
            db: Database connection
            role_id: Discord role ID

        Returns:
            True if updated successfully, False otherwise
        """
        self.admin_role_id = role_id
        self.updated_at = datetime.utcnow()

        # Update in database
        result = await db.guilds.update_one(
            {"guild_id": self.guild_id},
            {"$set": {
                "admin_role_id": self.admin_role_id,
                "updated_at": self.updated_at
            }}
        )

        return result.modified_count > 0

    async def add_admin_user(self, db, user_id: str) -> bool:
        """Add admin user for guild

        Args:
            db: Database connection
            user_id: Discord user ID

        Returns:
            True if updated successfully, False otherwise
        """
        if not hasattr(self, "admin_users"):
            self.admin_users = []

        if user_id in self.admin_users:
            return True

        self.admin_users.append(user_id)
        self.updated_at = datetime.utcnow()

        # Update in database
        result = await db.guilds.update_one(
            {"guild_id": self.guild_id},
            {"$set": {
                "admin_users": self.admin_users,
                "updated_at": self.updated_at
            }}
        )

        return result.modified_count > 0

    async def remove_admin_user(self, db, user_id: str) -> bool:
        """Remove admin user for guild

        Args:
            db: Database connection
            user_id: Discord user ID

        Returns:
            True if updated successfully, False otherwise
        """
        if not hasattr(self, "admin_users") or user_id not in self.admin_users:
            return True

        self.admin_users.remove(user_id)
        self.updated_at = datetime.utcnow()

        # Update in database
        result = await db.guilds.update_one(
            {"guild_id": self.guild_id},
            {"$set": {
                "admin_users": self.admin_users,
                "updated_at": self.updated_at
            }}
        )

        return result.modified_count > 0

    async def update_theme(self, db, color_primary: Optional[str] = None, color_secondary: Optional[str] = None, color_accent: Optional[str] = None, icon_url: Optional[str] = None) -> bool:
        """Update theme colors for guild

        Args:
            db: Database connection
            color_primary: Primary color (hex)
            color_secondary: Secondary color (hex)
            color_accent: Accent color (hex)
            icon_url: Icon URL

        Returns:
            True if updated successfully, False otherwise
        """
        update_dict = {"updated_at": datetime.utcnow()}

        if color_primary is not None:
            self.color_primary = color_primary
            update_dict["color_primary"] = color_primary

        if color_secondary is not None:
            self.color_secondary = color_secondary
            update_dict["color_secondary"] = color_secondary

        if color_accent is not None:
            self.color_accent = color_accent
            update_dict["color_accent"] = color_accent

        if icon_url is not None:
            self.icon_url = icon_url
            update_dict["icon_url"] = icon_url

        self.updated_at = update_dict["updated_at"]

        # Update in database
        result = await db.guilds.update_one(
            {"guild_id": self.guild_id},
            {"$set": update_dict}
        )

        return result.modified_count > 0

    @classmethod
    async def get_by_id(cls, db, guild_id):
        """Get a guild by its Discord ID (alias for get_by_guild_id)"""
        return await cls.get_by_guild_id(db, str(guild_id))

    @classmethod
    async def create(cls, db, guild_id: str, name: str) -> Optional['Guild']:
        """Create a new guild

        Args:
            db: Database connection
            guild_id: Discord guild ID
            name: Guild name

        Returns:
            Created Guild object or None if creation failed
        """
        # Create document
        document = {
            "guild_id": str(guild_id),
            "name": name,
            "premium_tier": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Insert into database
        try:
            result = await db.guilds.insert_one(document)
            if result.inserted_id:
                document["_id"] = result.inserted_id
                return cls.from_document(document, db)
        except Exception as e:
            logger.error(f"Error creating guild: {e}")

        return None

    def check_feature_access(self, feature_name: str) -> bool:
        """Check if this guild has access to a premium feature

        Args:
            feature_name: Name of the feature to check

        Returns:
            True if the guild has access to the feature, False otherwise
        """
        from config import PREMIUM_TIERS

        # Get features for current tier
        tier_info = PREMIUM_TIERS.get(self.premium_tier, {})
        features = tier_info.get("features", [])

        # Check if feature is in allowed features
        return feature_name in features

    def get_available_features(self) -> List[str]:
        """Get list of features available for this guild's premium tier"""
        from config import PREMIUM_TIERS
        tier_info = PREMIUM_TIERS.get(self.premium_tier, {})
        return tier_info.get("features", [])

    @classmethod
    async def from_document(cls, document: Dict[str, Any], db) -> Optional['Guild']:
        """Create a Guild instance from a database document"""
        if document is None:
            return None
        instance = cls(db, **document)
        # Ensure all IDs are strings
        if hasattr(instance, 'guild_id'):
            instance.guild_id = str(instance.guild_id)
        if hasattr(instance, 'admin_role_id'):
            instance.admin_role_id = str(instance.admin_role_id) if instance.admin_role_id else None
        return instance