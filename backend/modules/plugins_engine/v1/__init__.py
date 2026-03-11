"""Plugins Engine Module v1

Feature flags and plugin management.
Extracted from feature_controls.py.

Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid
import os
from pymongo import MongoClient

router = APIRouter(prefix="/api/v1/plugins", tags=["Plugins Engine"])


# ============================================
# MODELS
# ============================================

class FeatureFlag(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    key: str  # Unique key for code reference
    description: str = ""
    is_enabled: bool = False
    enabled_for_users: List[str] = []  # Specific user IDs
    enabled_for_roles: List[str] = []  # Role names
    percentage_rollout: int = Field(default=0, ge=0, le=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PluginConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    key: str
    config: Dict[str, Any] = {}
    is_active: bool = True
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Extension(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    version: str = "1.0.0"
    author: str = ""
    description: str = ""
    entry_point: str = ""
    dependencies: List[str] = []
    is_installed: bool = False
    is_active: bool = False
    installed_at: Optional[datetime] = None


# ============================================
# DEFAULT FEATURES
# ============================================

DEFAULT_FEATURES = {
    "ai_analysis": {
        "name": "Analyse IA",
        "key": "ai_analysis",
        "description": "Analyse de produits par GPT-5.2",
        "is_enabled": True
    },
    "marketplace": {
        "name": "Marketplace",
        "key": "marketplace",
        "description": "Marché C2C d'équipement",
        "is_enabled": True
    },
    "live_tracking": {
        "name": "Suivi GPS",
        "key": "live_tracking",
        "description": "Suivi GPS en temps réel",
        "is_enabled": True
    },
    "territory_rentals": {
        "name": "Location de territoires",
        "key": "territory_rentals",
        "description": "Location de terres de chasse",
        "is_enabled": True
    },
    "referral_system": {
        "name": "Système de parrainage",
        "key": "referral_system",
        "description": "Parrainage et commissions",
        "is_enabled": True
    },
    "3d_maps": {
        "name": "Cartes 3D",
        "key": "3d_maps",
        "description": "Visualisation 3D des territoires",
        "is_enabled": False
    },
    "weather_alerts": {
        "name": "Alertes météo",
        "key": "weather_alerts",
        "description": "Notifications météo automatiques",
        "is_enabled": False
    }
}


# ============================================
# SERVICE
# ============================================

class PluginsService:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    async def get_all_features(self) -> List[Dict]:
        features = list(self.db.feature_flags.find({}, {"_id": 0}))
        if not features:
            # Initialize with defaults
            for key, data in DEFAULT_FEATURES.items():
                feature = FeatureFlag(**data)
                f_dict = feature.model_dump()
                f_dict.pop("_id", None)
                self.db.feature_flags.insert_one(f_dict)
            features = list(self.db.feature_flags.find({}, {"_id": 0}))
        return features
    
    async def get_feature(self, key: str) -> Optional[Dict]:
        return self.db.feature_flags.find_one({"key": key}, {"_id": 0})
    
    async def is_feature_enabled(self, key: str, user_id: str = None, role: str = None) -> bool:
        feature = await self.get_feature(key)
        if not feature:
            return DEFAULT_FEATURES.get(key, {}).get("is_enabled", False)
        
        # Check global enable
        if feature.get("is_enabled"):
            return True
        
        # Check user-specific
        if user_id and user_id in feature.get("enabled_for_users", []):
            return True
        
        # Check role-specific
        if role and role in feature.get("enabled_for_roles", []):
            return True
        
        # Check percentage rollout (simplified)
        if feature.get("percentage_rollout", 0) > 0:
            # In production, use consistent hashing based on user_id
            import random
            return random.randint(1, 100) <= feature["percentage_rollout"]
        
        return False
    
    async def set_feature(self, key: str, is_enabled: bool) -> Dict:
        self.db.feature_flags.update_one(
            {"key": key},
            {"$set": {"is_enabled": is_enabled, "updated_at": datetime.now(timezone.utc)}},
            upsert=True
        )
        return await self.get_feature(key)
    
    async def get_config(self, key: str) -> Dict:
        config = self.db.plugin_configs.find_one({"key": key}, {"_id": 0})
        return config.get("config", {}) if config else {}
    
    async def set_config(self, key: str, config: Dict) -> Dict:
        self.db.plugin_configs.update_one(
            {"key": key},
            {"$set": {"config": config, "updated_at": datetime.now(timezone.utc)}},
            upsert=True
        )
        return await self.get_config(key)


_service = PluginsService()


# ============================================
# ROUTES
# ============================================

@router.get("/")
async def plugins_engine_info():
    return {
        "module": "plugins_engine",
        "version": "1.0.0",
        "description": "Feature flags and plugin management",
        "features": [
            "Feature flags",
            "User/role targeting",
            "Percentage rollout",
            "Plugin configuration",
            "Extensions"
        ]
    }


@router.get("/features")
async def list_features():
    features = await _service.get_all_features()
    return {"success": True, "features": features}


@router.get("/features/{key}")
async def get_feature(key: str):
    feature = await _service.get_feature(key)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return {"success": True, "feature": feature}


@router.get("/features/{key}/check")
async def check_feature(key: str, user_id: Optional[str] = None, role: Optional[str] = None):
    is_enabled = await _service.is_feature_enabled(key, user_id, role)
    return {"success": True, "key": key, "is_enabled": is_enabled}


@router.put("/features/{key}")
async def set_feature(key: str, is_enabled: bool):
    feature = await _service.set_feature(key, is_enabled)
    return {"success": True, "feature": feature}


@router.get("/config/{key}")
async def get_config(key: str):
    config = await _service.get_config(key)
    return {"success": True, "key": key, "config": config}


@router.put("/config/{key}")
async def set_config(key: str, config: dict):
    updated = await _service.set_config(key, config)
    return {"success": True, "key": key, "config": updated}


@router.get("/defaults")
async def get_default_features():
    return {"success": True, "defaults": DEFAULT_FEATURES}
