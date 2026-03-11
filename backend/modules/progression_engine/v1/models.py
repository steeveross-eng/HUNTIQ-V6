"""Progression Engine Models - PLAN MAITRE
Pydantic models for gamification and user progression.

Version: 1.0.0
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid


class BadgeCategory(str, Enum):
    """Badge categories"""
    HUNTING = "hunting"
    ANALYSIS = "analysis"
    SOCIAL = "social"
    LEARNING = "learning"
    SEASONAL = "seasonal"
    SPECIAL = "special"


class ChallengeType(str, Enum):
    """Challenge types"""
    DAILY = "daily"
    WEEKLY = "weekly"
    SEASONAL = "seasonal"
    ACHIEVEMENT = "achievement"


class UserProgression(BaseModel):
    """User progression data"""
    user_id: str
    
    # Level system
    level: int = 1
    current_xp: int = 0
    xp_to_next_level: int = 100
    total_xp: int = 0
    
    # Titles
    current_title: str = "Débutant"
    unlocked_titles: List[str] = Field(default_factory=lambda: ["Débutant"])
    
    # Stats
    total_analyses: int = 0
    total_hunts_logged: int = 0
    successful_hunts: int = 0
    days_active: int = 0
    
    # Streaks
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[datetime] = None
    
    # Rankings
    global_rank: Optional[int] = None
    regional_rank: Optional[int] = None
    region: Optional[str] = None
    
    # Metadata
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Badge(BaseModel):
    """Badge definition"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Identity
    name: str
    description: str
    icon: str  # Icon name or URL
    category: BadgeCategory = BadgeCategory.HUNTING
    
    # Rarity
    rarity: Literal["common", "uncommon", "rare", "epic", "legendary"] = "common"
    xp_reward: int = 10
    
    # Requirements
    requirement_type: str  # "analyses", "hunts", "streak", etc.
    requirement_value: int
    
    # Status
    is_active: bool = True
    is_secret: bool = False


class UserBadge(BaseModel):
    """Badge earned by user"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    badge_id: str
    badge_name: str
    
    # Earning details
    earned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    progress_when_earned: int = 0
    
    # Display
    is_featured: bool = False
    showcase_order: Optional[int] = None


class Challenge(BaseModel):
    """Challenge definition"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Identity
    title: str
    description: str
    challenge_type: ChallengeType = ChallengeType.WEEKLY
    
    # Timing
    start_date: datetime
    end_date: datetime
    
    # Requirements
    target_action: str  # "analyze", "log_hunt", "share", etc.
    target_count: int
    species_filter: Optional[str] = None
    
    # Rewards
    xp_reward: int = 50
    badge_reward: Optional[str] = None
    special_reward: Optional[str] = None
    
    # Status
    is_active: bool = True
    participant_count: int = 0
    completion_count: int = 0


class ChallengeProgress(BaseModel):
    """User progress on a challenge"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    challenge_id: str
    
    # Progress
    current_count: int = 0
    target_count: int
    completed: bool = False
    
    # Timing
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    
    # Rewards claimed
    rewards_claimed: bool = False


class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    rank: int
    user_id: str
    user_name: str
    
    # Stats
    score: int = 0
    level: int = 1
    badge_count: int = 0
    
    # Context
    region: Optional[str] = None
    title: Optional[str] = None
    
    # Change
    rank_change: int = 0  # Positive = improved, negative = dropped


class Reward(BaseModel):
    """Reward definition"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Identity
    name: str
    description: str
    reward_type: Literal["discount", "feature", "badge", "title", "cosmetic"] = "badge"
    
    # Value
    value: Optional[str] = None  # "10%" for discount, feature name, etc.
    
    # Requirements
    required_level: Optional[int] = None
    required_xp: Optional[int] = None
    required_badge: Optional[str] = None
    
    # Status
    is_active: bool = True
    limited_quantity: Optional[int] = None
    claimed_count: int = 0


class XPEvent(BaseModel):
    """XP gain event"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    
    # Event
    action: str  # "analysis", "hunt_logged", "badge_earned", etc.
    xp_gained: int
    
    # Context
    details: Dict[str, Any] = Field(default_factory=dict)
    
    # Result
    new_total_xp: int = 0
    level_up: bool = False
    new_level: Optional[int] = None
    
    # Metadata
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
