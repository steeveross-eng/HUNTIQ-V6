"""Progression Engine Service - PLAN MAITRE
Business logic for gamification and user progression.

Version: 1.0.0
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient

from .models import (
    UserProgression, Badge, BadgeCategory, UserBadge,
    Challenge, ChallengeType, ChallengeProgress,
    LeaderboardEntry, Reward, XPEvent
)


class ProgressionService:
    """Service for gamification and progression"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
        
        # Level thresholds
        self.level_thresholds = [
            0, 100, 250, 500, 1000, 2000, 3500, 5500, 8000, 11000,
            15000, 20000, 27000, 35000, 45000, 57000, 71000, 87000, 105000, 125000
        ]
        
        # Titles by level
        self.titles = {
            1: "Débutant",
            5: "Chasseur",
            10: "Chasseur Confirmé",
            15: "Expert",
            20: "Maître Chasseur"
        }
        
        # Default badges
        self.default_badges = [
            Badge(
                name="Première Analyse",
                description="Effectuer votre première analyse de produit",
                icon="analysis",
                category=BadgeCategory.ANALYSIS,
                rarity="common",
                xp_reward=25,
                requirement_type="analyses",
                requirement_value=1
            ),
            Badge(
                name="Analyste",
                description="Effectuer 10 analyses de produits",
                icon="star",
                category=BadgeCategory.ANALYSIS,
                rarity="uncommon",
                xp_reward=100,
                requirement_type="analyses",
                requirement_value=10
            ),
            Badge(
                name="Expert Analyste",
                description="Effectuer 100 analyses de produits",
                icon="trophy",
                category=BadgeCategory.ANALYSIS,
                rarity="rare",
                xp_reward=500,
                requirement_type="analyses",
                requirement_value=100
            ),
            Badge(
                name="Première Chasse",
                description="Enregistrer votre première sortie de chasse",
                icon="target",
                category=BadgeCategory.HUNTING,
                rarity="common",
                xp_reward=25,
                requirement_type="hunts",
                requirement_value=1
            ),
            Badge(
                name="Série de 7 Jours",
                description="Être actif pendant 7 jours consécutifs",
                icon="fire",
                category=BadgeCategory.SPECIAL,
                rarity="uncommon",
                xp_reward=150,
                requirement_type="streak",
                requirement_value=7
            )
        ]
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    @property
    def progression_collection(self):
        return self.db.user_progression
    
    @property
    def badges_collection(self):
        return self.db.user_badges
    
    @property
    def challenges_collection(self):
        return self.db.challenges
    
    @property
    def challenge_progress_collection(self):
        return self.db.challenge_progress
    
    @property
    def xp_events_collection(self):
        return self.db.xp_events
    
    async def get_user_progression(self, user_id: str) -> UserProgression:
        """Get user's progression data"""
        prog_dict = self.progression_collection.find_one(
            {"user_id": user_id}, {"_id": 0}
        )
        
        if prog_dict:
            return UserProgression(**prog_dict)
        
        # Create new progression
        progression = UserProgression(user_id=user_id)
        prog_dict = progression.model_dump()
        prog_dict.pop("_id", None)
        self.progression_collection.insert_one(prog_dict)
        
        return progression
    
    async def add_xp(
        self,
        user_id: str,
        xp_amount: int,
        action: str,
        details: Optional[Dict[str, Any]] = None
    ) -> XPEvent:
        """Add XP to user"""
        progression = await self.get_user_progression(user_id)
        
        # Calculate new XP
        new_total = progression.total_xp + xp_amount
        new_current = progression.current_xp + xp_amount
        
        # Check for level up
        level_up = False
        new_level = progression.level
        
        while new_level < len(self.level_thresholds) - 1:
            if new_total >= self.level_thresholds[new_level]:
                new_level += 1
                level_up = True
            else:
                break
        
        # Calculate XP to next level
        xp_to_next = self.level_thresholds[new_level] - new_total if new_level < len(self.level_thresholds) else 0
        
        # Get new title if applicable
        new_title = progression.current_title
        unlocked_titles = progression.unlocked_titles.copy()
        
        for level, title in self.titles.items():
            if new_level >= level and title not in unlocked_titles:
                unlocked_titles.append(title)
                new_title = title
        
        # Update progression
        self.progression_collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "level": new_level,
                "current_xp": new_current if not level_up else new_current - self.level_thresholds[progression.level],
                "total_xp": new_total,
                "xp_to_next_level": max(0, xp_to_next),
                "current_title": new_title,
                "unlocked_titles": unlocked_titles,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        # Create XP event
        event = XPEvent(
            user_id=user_id,
            action=action,
            xp_gained=xp_amount,
            details=details or {},
            new_total_xp=new_total,
            level_up=level_up,
            new_level=new_level if level_up else None
        )
        
        event_dict = event.model_dump()
        event_dict.pop("_id", None)
        self.xp_events_collection.insert_one(event_dict)
        
        return event
    
    async def get_badges(self) -> List[Badge]:
        """Get all available badges"""
        return self.default_badges
    
    async def get_user_badges(self, user_id: str) -> List[UserBadge]:
        """Get badges earned by user"""
        badges = list(self.badges_collection.find(
            {"user_id": user_id}, {"_id": 0}
        ))
        return [UserBadge(**b) for b in badges]
    
    async def award_badge(
        self,
        user_id: str,
        badge_id: str,
        badge_name: str,
        xp_reward: int = 0
    ) -> UserBadge:
        """Award a badge to user"""
        # Check if already has badge
        existing = self.badges_collection.find_one({
            "user_id": user_id,
            "badge_id": badge_id
        })
        
        if existing:
            return UserBadge(**existing)
        
        # Award badge
        user_badge = UserBadge(
            user_id=user_id,
            badge_id=badge_id,
            badge_name=badge_name
        )
        
        badge_dict = user_badge.model_dump()
        badge_dict.pop("_id", None)
        self.badges_collection.insert_one(badge_dict)
        
        # Award XP
        if xp_reward > 0:
            await self.add_xp(user_id, xp_reward, "badge_earned", {
                "badge_name": badge_name
            })
        
        return user_badge
    
    async def check_badge_eligibility(
        self,
        user_id: str
    ) -> List[Badge]:
        """Check which badges user is eligible for"""
        progression = await self.get_user_progression(user_id)
        user_badges = await self.get_user_badges(user_id)
        earned_ids = {b.badge_id for b in user_badges}
        
        eligible = []
        
        for badge in self.default_badges:
            if badge.id in earned_ids:
                continue
            
            # Check requirements
            if badge.requirement_type == "analyses":
                if progression.total_analyses >= badge.requirement_value:
                    eligible.append(badge)
            elif badge.requirement_type == "hunts":
                if progression.total_hunts_logged >= badge.requirement_value:
                    eligible.append(badge)
            elif badge.requirement_type == "streak":
                if progression.current_streak >= badge.requirement_value:
                    eligible.append(badge)
        
        return eligible
    
    async def get_active_challenges(self) -> List[Challenge]:
        """Get active challenges"""
        now = datetime.now(timezone.utc)
        
        challenges = list(self.challenges_collection.find({
            "is_active": True,
            "start_date": {"$lte": now},
            "end_date": {"$gte": now}
        }, {"_id": 0}))
        
        if not challenges:
            # Return default challenges
            week_end = now + timedelta(days=7 - now.weekday())
            return [
                Challenge(
                    title="Défi Hebdomadaire",
                    description="Effectuez 5 analyses cette semaine",
                    challenge_type=ChallengeType.WEEKLY,
                    start_date=now,
                    end_date=week_end,
                    target_action="analyze",
                    target_count=5,
                    xp_reward=100
                )
            ]
        
        return [Challenge(**c) for c in challenges]
    
    async def get_challenge_progress(
        self,
        user_id: str,
        challenge_id: str
    ) -> Optional[ChallengeProgress]:
        """Get user's progress on a challenge"""
        progress_dict = self.challenge_progress_collection.find_one({
            "user_id": user_id,
            "challenge_id": challenge_id
        }, {"_id": 0})
        
        if progress_dict:
            return ChallengeProgress(**progress_dict)
        return None
    
    async def update_challenge_progress(
        self,
        user_id: str,
        challenge_id: str,
        increment: int = 1
    ) -> ChallengeProgress:
        """Update challenge progress"""
        progress = await self.get_challenge_progress(user_id, challenge_id)
        
        if not progress:
            # Get challenge to know target
            challenge = self.challenges_collection.find_one(
                {"id": challenge_id}, {"_id": 0}
            )
            target = challenge.get("target_count", 5) if challenge else 5
            
            progress = ChallengeProgress(
                user_id=user_id,
                challenge_id=challenge_id,
                target_count=target
            )
        
        new_count = progress.current_count + increment
        completed = new_count >= progress.target_count
        
        update_data = {
            "current_count": new_count,
            "completed": completed
        }
        
        if completed and not progress.completed:
            update_data["completed_at"] = datetime.now(timezone.utc)
        
        self.challenge_progress_collection.update_one(
            {"user_id": user_id, "challenge_id": challenge_id},
            {"$set": update_data},
            upsert=True
        )
        
        progress.current_count = new_count
        progress.completed = completed
        
        return progress
    
    async def get_leaderboard(
        self,
        limit: int = 50,
        region: Optional[str] = None
    ) -> List[LeaderboardEntry]:
        """Get leaderboard"""
        query = {}
        if region:
            query["region"] = region
        
        users = list(self.progression_collection.find(
            query, {"_id": 0}
        ).sort("total_xp", -1).limit(limit))
        
        entries = []
        for i, user in enumerate(users, 1):
            badge_count = self.badges_collection.count_documents({
                "user_id": user["user_id"]
            })
            
            entries.append(LeaderboardEntry(
                rank=i,
                user_id=user["user_id"],
                user_name=user.get("user_name", f"Chasseur #{i}"),
                score=user.get("total_xp", 0),
                level=user.get("level", 1),
                badge_count=badge_count,
                region=user.get("region"),
                title=user.get("current_title", "Débutant")
            ))
        
        return entries
    
    async def get_rewards(self, user_id: str) -> List[Reward]:
        """Get available rewards for user"""
        progression = await self.get_user_progression(user_id)
        
        # Default rewards
        rewards = [
            Reward(
                name="Analyse Gratuite",
                description="Débloquez une analyse IA gratuite",
                reward_type="feature",
                value="ai_analysis",
                required_level=5
            ),
            Reward(
                name="Badge Exclusif",
                description="Badge 'Premier Pionnier'",
                reward_type="badge",
                required_xp=1000
            )
        ]
        
        # Filter by eligibility
        eligible = []
        for reward in rewards:
            if reward.required_level and progression.level < reward.required_level:
                continue
            if reward.required_xp and progression.total_xp < reward.required_xp:
                continue
            eligible.append(reward)
        
        return eligible
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get progression engine statistics"""
        return {
            "total_users": self.progression_collection.count_documents({}),
            "total_badges_awarded": self.badges_collection.count_documents({}),
            "active_challenges": self.challenges_collection.count_documents({"is_active": True}),
            "badge_types": len(self.default_badges),
            "max_level": len(self.level_thresholds)
        }
