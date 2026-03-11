"""Adaptive Strategy Engine Service - PLAN MAITRE
Business logic for adaptive hunting strategies.

Version: 1.0.0
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient

from .models import (
    StrategyType, AdaptationTrigger, AdaptiveStrategy,
    StrategyAdjustment, StrategyFeedback, RouteOptimization,
    LearningEntry
)


class AdaptiveStrategyService:
    """Service for adaptive strategy management"""
    
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
    
    @property
    def strategies_collection(self):
        return self.db.adaptive_strategies
    
    @property
    def adjustments_collection(self):
        return self.db.strategy_adjustments
    
    @property
    def feedback_collection(self):
        return self.db.strategy_feedback
    
    @property
    def learning_collection(self):
        return self.db.strategy_learning
    
    async def create_strategy(
        self,
        species: str,
        lat: float,
        lng: float,
        strategy_type: Optional[str] = None,
        conditions: Optional[Dict[str, Any]] = None
    ) -> AdaptiveStrategy:
        """Create a new adaptive strategy"""
        # Determine best strategy if not specified
        if strategy_type:
            try:
                primary = StrategyType(strategy_type)
            except ValueError:
                primary = StrategyType.STAND
        else:
            primary = await self._determine_best_strategy(species, conditions)
        
        # Get backup strategies
        backups = self._get_backup_strategies(primary)
        
        # Calculate initial score
        initial_score = await self._calculate_strategy_score(
            primary, species, {"lat": lat, "lng": lng}, conditions
        )
        
        strategy = AdaptiveStrategy(
            primary_strategy=primary,
            backup_strategies=backups,
            species=species,
            location={"lat": lat, "lng": lng},
            conditions=conditions or {},
            start_time=datetime.now(timezone.utc),
            initial_score=initial_score,
            current_score=initial_score,
            success_probability=initial_score / 100,
            next_adaptation_check=datetime.now(timezone.utc) + timedelta(minutes=30)
        )
        
        strategy_dict = strategy.model_dump()
        strategy_dict.pop("_id", None)
        self.strategies_collection.insert_one(strategy_dict)
        
        return strategy
    
    async def get_strategy(self, strategy_id: str) -> Optional[AdaptiveStrategy]:
        """Get strategy by ID"""
        strategy_dict = self.strategies_collection.find_one(
            {"id": strategy_id}, {"_id": 0}
        )
        if strategy_dict:
            return AdaptiveStrategy(**strategy_dict)
        return None
    
    async def check_for_adjustments(
        self,
        strategy_id: str,
        current_conditions: Optional[Dict[str, Any]] = None
    ) -> List[StrategyAdjustment]:
        """Check if strategy needs adjustment"""
        strategy = await self.get_strategy(strategy_id)
        if not strategy:
            return []
        
        adjustments = []
        
        # Check time elapsed
        elapsed = datetime.now(timezone.utc) - strategy.start_time
        if elapsed > timedelta(hours=2) and strategy.current_phase < strategy.total_phases:
            adjustments.append(StrategyAdjustment(
                strategy_id=strategy_id,
                trigger=AdaptationTrigger.TIME_ELAPSED,
                trigger_details={"elapsed_hours": elapsed.total_seconds() / 3600},
                recommended_action="Passer à la phase suivante",
                priority="medium",
                reason="Temps écoulé sans résultat significatif"
            ))
        
        # Check weather changes
        if current_conditions:
            original_temp = strategy.conditions.get("temperature")
            current_temp = current_conditions.get("temperature")
            
            if original_temp and current_temp and abs(current_temp - original_temp) > 5:
                adjustments.append(StrategyAdjustment(
                    strategy_id=strategy_id,
                    trigger=AdaptationTrigger.WEATHER_CHANGE,
                    trigger_details={
                        "original_temp": original_temp,
                        "current_temp": current_temp
                    },
                    recommended_action="Ajuster position selon nouvelles conditions",
                    priority="high",
                    reason="Changement significatif de température"
                ))
            
            # Wind shift
            original_wind_dir = strategy.conditions.get("wind_direction")
            current_wind_dir = current_conditions.get("wind_direction")
            
            if original_wind_dir and current_wind_dir and original_wind_dir != current_wind_dir:
                adjustments.append(StrategyAdjustment(
                    strategy_id=strategy_id,
                    trigger=AdaptationTrigger.WIND_SHIFT,
                    trigger_details={
                        "original": original_wind_dir,
                        "current": current_wind_dir
                    },
                    recommended_action="Repositionner face au vent",
                    new_strategy=None,
                    priority="high",
                    reason="Direction du vent a changé"
                ))
        
        # Save adjustments
        for adj in adjustments:
            adj_dict = adj.model_dump()
            adj_dict.pop("_id", None)
            self.adjustments_collection.insert_one(adj_dict)
        
        return adjustments
    
    async def apply_adjustment(
        self,
        strategy_id: str,
        adjustment_id: str
    ) -> Optional[AdaptiveStrategy]:
        """Apply an adjustment to strategy"""
        strategy = await self.get_strategy(strategy_id)
        if not strategy:
            return None
        
        adjustment_dict = self.adjustments_collection.find_one(
            {"id": adjustment_id}, {"_id": 0}
        )
        if not adjustment_dict:
            return None
        
        adjustment = StrategyAdjustment(**adjustment_dict)
        
        # Apply changes
        updates = {
            "updated_at": datetime.now(timezone.utc),
            "adaptations_made": strategy.adaptations_made + [{
                "adjustment_id": adjustment_id,
                "trigger": adjustment.trigger.value,
                "action": adjustment.recommended_action,
                "applied_at": datetime.now(timezone.utc).isoformat()
            }]
        }
        
        if adjustment.new_strategy:
            updates["primary_strategy"] = adjustment.new_strategy.value
        
        if adjustment.location_change:
            updates["location"] = adjustment.location_change
        
        # Recalculate score
        new_score = strategy.current_score * (1 + adjustment.expected_improvement / 100)
        updates["current_score"] = min(100, new_score)
        updates["success_probability"] = new_score / 100
        
        # Update strategy
        self.strategies_collection.update_one(
            {"id": strategy_id},
            {"$set": updates}
        )
        
        # Mark adjustment as applied
        self.adjustments_collection.update_one(
            {"id": adjustment_id},
            {"$set": {"applied": True, "applied_at": datetime.now(timezone.utc)}}
        )
        
        return await self.get_strategy(strategy_id)
    
    async def submit_feedback(
        self,
        strategy_id: str,
        user_id: str,
        outcome: str,
        sighting: bool = False,
        harvest: bool = False,
        rating: int = 3,
        notes: Optional[str] = None
    ) -> StrategyFeedback:
        """Submit feedback on strategy"""
        feedback = StrategyFeedback(
            strategy_id=strategy_id,
            user_id=user_id,
            outcome=outcome,
            sighting=sighting,
            harvest=harvest,
            overall_rating=rating,
            notes=notes
        )
        
        feedback_dict = feedback.model_dump()
        feedback_dict.pop("_id", None)
        self.feedback_collection.insert_one(feedback_dict)
        
        # Update strategy status
        status = "completed" if outcome in ["success", "partial"] else "abandoned"
        self.strategies_collection.update_one(
            {"id": strategy_id},
            {"$set": {"status": status, "updated_at": datetime.now(timezone.utc)}}
        )
        
        # Record for learning
        strategy = await self.get_strategy(strategy_id)
        if strategy:
            await self._record_learning(strategy, feedback)
        
        return feedback
    
    async def optimize_route(
        self,
        start_lat: float,
        start_lng: float,
        end_lat: Optional[float] = None,
        end_lng: Optional[float] = None,
        waypoints: Optional[List[Dict[str, float]]] = None,
        optimize_for: str = "balanced"
    ) -> RouteOptimization:
        """Optimize hunting route"""
        start = {"lat": start_lat, "lng": start_lng}
        end = {"lat": end_lat, "lng": end_lng} if end_lat and end_lng else None
        
        # Calculate route (placeholder)
        total_distance = 0
        if end:
            total_distance = self._calculate_distance(start, end)
        
        if waypoints:
            prev = start
            for wp in waypoints:
                total_distance += self._calculate_distance(prev, wp)
                prev = wp
            if end:
                total_distance += self._calculate_distance(prev, end)
        
        route = RouteOptimization(
            start_point=start,
            end_point=end,
            waypoints=waypoints or [],
            optimized_for=optimize_for,
            total_distance_km=round(total_distance, 2),
            estimated_time_hours=round(total_distance / 3, 2),  # ~3 km/h walking
            route_score=75,
            wind_advantage_score=80,
            cover_score=70
        )
        
        return route
    
    async def _determine_best_strategy(
        self,
        species: str,
        conditions: Optional[Dict[str, Any]]
    ) -> StrategyType:
        """Determine best strategy based on conditions"""
        # Check historical success rates
        # For now, use simple heuristics
        
        wind_speed = conditions.get("wind_speed", 0) if conditions else 0
        
        if wind_speed > 25:
            return StrategyType.STAND  # Stay put in high wind
        
        if species.lower() == "moose":
            return StrategyType.CALLING
        elif species.lower() == "bear":
            return StrategyType.STAND
        else:
            return StrategyType.STAND
    
    def _get_backup_strategies(self, primary: StrategyType) -> List[StrategyType]:
        """Get backup strategies"""
        backups = {
            StrategyType.STAND: [StrategyType.STALKING, StrategyType.SPOT_AND_STALK],
            StrategyType.STALKING: [StrategyType.STAND, StrategyType.AMBUSH],
            StrategyType.CALLING: [StrategyType.STAND, StrategyType.STALKING],
            StrategyType.SPOT_AND_STALK: [StrategyType.STALKING, StrategyType.STAND]
        }
        return backups.get(primary, [StrategyType.STAND])
    
    async def _calculate_strategy_score(
        self,
        strategy: StrategyType,
        species: str,
        location: Dict[str, float],
        conditions: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate strategy effectiveness score"""
        base_score = 70
        
        # Adjust based on conditions
        if conditions:
            temp = conditions.get("temperature", 10)
            if 5 <= temp <= 15:
                base_score += 10
            
            wind = conditions.get("wind_speed", 0)
            if wind > 30:
                base_score -= 15
        
        return min(100, max(0, base_score))
    
    def _calculate_distance(
        self,
        p1: Dict[str, float],
        p2: Dict[str, float]
    ) -> float:
        """Calculate distance between two points in km"""
        import math
        R = 6371
        
        lat1, lng1 = math.radians(p1["lat"]), math.radians(p1["lng"])
        lat2, lng2 = math.radians(p2["lat"]), math.radians(p2["lng"])
        
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    async def _record_learning(
        self,
        strategy: AdaptiveStrategy,
        feedback: StrategyFeedback
    ):
        """Record data for machine learning"""
        entry = LearningEntry(
            species=strategy.species,
            strategy_type=strategy.primary_strategy,
            conditions=strategy.conditions,
            location_features={
                "lat": strategy.location.get("lat"),
                "lng": strategy.location.get("lng")
            },
            success=feedback.outcome == "success",
            score=feedback.overall_rating * 20
        )
        
        entry_dict = entry.model_dump()
        entry_dict.pop("_id", None)
        self.learning_collection.insert_one(entry_dict)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            "total_strategies": self.strategies_collection.count_documents({}),
            "active_strategies": self.strategies_collection.count_documents({"status": "active"}),
            "total_feedback": self.feedback_collection.count_documents({}),
            "learning_entries": self.learning_collection.count_documents({}),
            "strategy_types": [s.value for s in StrategyType]
        }
