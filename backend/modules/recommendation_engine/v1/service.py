"""Recommendation Engine Service - PLAN MAITRE
Business logic for intelligent recommendation system.

Version: 1.0.0
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pymongo import MongoClient

from .models import (
    RecommendationType, ProductRecommendation, StrategyRecommendation,
    RecommendationRequest, RecommendationResponse, UserPreferenceProfile,
    SimilarityScore, RecommendationFeedback
)


class RecommendationService:
    """Service for intelligent recommendations"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
    
    @property
    def db(self):
        """Lazy database connection"""
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    @property
    def recommendations_collection(self):
        return self.db.recommendations
    
    @property
    def user_profiles_collection(self):
        return self.db.recommendation_user_profiles
    
    @property
    def feedback_collection(self):
        return self.db.recommendation_feedback
    
    @property
    def similarity_collection(self):
        return self.db.product_similarity
    
    async def get_product_recommendations(
        self,
        request: RecommendationRequest
    ) -> RecommendationResponse:
        """
        Get personalized product recommendations.
        
        Uses hybrid filtering:
        - Collaborative: Based on similar users' preferences
        - Content-based: Based on product attributes
        - Contextual: Based on weather, season, species
        """
        start_time = datetime.now(timezone.utc)
        
        # Build context
        context = {
            "species": request.species,
            "season": request.season,
            "weather": request.weather_conditions,
            "location": request.location
        }
        
        # Get user profile if available
        user_profile = None
        if request.user_id:
            user_profile = await self.get_user_profile(request.user_id)
        
        # Generate recommendations (placeholder logic)
        recommendations = await self._generate_product_recommendations(
            request, user_profile, context
        )
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        return RecommendationResponse(
            recommendation_type=RecommendationType.PRODUCT,
            total_results=len(recommendations),
            products=recommendations,
            context_used=context,
            processing_time_ms=processing_time
        )
    
    async def get_strategy_recommendations(
        self,
        species: str,
        conditions: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> RecommendationResponse:
        """Get hunting strategy recommendations"""
        start_time = datetime.now(timezone.utc)
        
        # Placeholder strategy recommendations
        strategies = [
            StrategyRecommendation(
                strategy_type="morning_hunt",
                title="Chasse matinale optimale",
                description="Conditions idéales pour une approche matinale",
                score=85.0,
                conditions=conditions,
                suggested_products=[],
                best_timing="05:30 - 08:00"
            )
        ]
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        return RecommendationResponse(
            recommendation_type=RecommendationType.STRATEGY,
            total_results=len(strategies),
            strategies=strategies,
            context_used={"species": species, "conditions": conditions},
            processing_time_ms=processing_time
        )
    
    async def get_similar_products(
        self,
        product_id: str,
        limit: int = 10
    ) -> List[ProductRecommendation]:
        """Get similar products based on attributes"""
        # Placeholder - would use similarity matrix in production
        return [
            ProductRecommendation(
                product_id=f"similar_{i}",
                product_name=f"Produit similaire {i}",
                product_type="attractant",
                score=90.0 - (i * 5),
                confidence=0.85,
                reasons=["Même catégorie", "Même espèce cible"],
                is_similar=True
            )
            for i in range(min(limit, 5))
        ]
    
    async def get_complementary_products(
        self,
        product_id: str,
        limit: int = 10
    ) -> List[ProductRecommendation]:
        """Get complementary products"""
        # Placeholder - would analyze purchase patterns
        return [
            ProductRecommendation(
                product_id=f"complementary_{i}",
                product_name=f"Produit complémentaire {i}",
                product_type="accessory",
                score=80.0 - (i * 5),
                confidence=0.75,
                reasons=["Souvent acheté ensemble", "Améliore l'efficacité"],
                is_complementary=True
            )
            for i in range(min(limit, 3))
        ]
    
    async def get_personalized_recommendations(
        self,
        user_id: str,
        limit: int = 10
    ) -> RecommendationResponse:
        """Get fully personalized recommendations for a user"""
        start_time = datetime.now(timezone.utc)
        
        user_profile = await self.get_user_profile(user_id)
        
        # Build recommendations based on profile
        recommendations = []
        
        if user_profile:
            # Would use ML model in production
            recommendations = [
                ProductRecommendation(
                    product_id=f"personalized_{i}",
                    product_name=f"Recommandation personnalisée {i}",
                    product_type="attractant",
                    score=95.0 - (i * 3),
                    confidence=0.90,
                    reasons=[
                        f"Basé sur vos préférences: {', '.join(user_profile.preferred_species[:2])}",
                        "Historique d'analyses similaires"
                    ]
                )
                for i in range(min(limit, 5))
            ]
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        return RecommendationResponse(
            recommendation_type=RecommendationType.PRODUCT,
            total_results=len(recommendations),
            products=recommendations,
            context_used={"user_id": user_id, "personalized": True},
            processing_time_ms=processing_time
        )
    
    async def get_contextual_recommendations(
        self,
        species: str,
        season: str,
        weather: Optional[Dict[str, Any]] = None,
        location: Optional[Dict[str, float]] = None,
        limit: int = 10
    ) -> RecommendationResponse:
        """Get context-aware recommendations"""
        start_time = datetime.now(timezone.utc)
        
        context = {
            "species": species,
            "season": season,
            "weather": weather,
            "location": location
        }
        
        # Placeholder contextual recommendations
        recommendations = [
            ProductRecommendation(
                product_id=f"contextual_{i}",
                product_name=f"Produit optimal pour {species}",
                product_type="attractant",
                score=92.0 - (i * 4),
                confidence=0.88,
                reasons=[
                    f"Optimal pour: {species}",
                    f"Saison: {season}",
                    "Conditions météo favorables" if weather else "Toutes conditions"
                ],
                context_match={
                    "species": 0.95,
                    "season": 0.90,
                    "weather": 0.85 if weather else 0.5
                }
            )
            for i in range(min(limit, 5))
        ]
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        return RecommendationResponse(
            recommendation_type=RecommendationType.PRODUCT,
            total_results=len(recommendations),
            products=recommendations,
            context_used=context,
            processing_time_ms=processing_time
        )
    
    async def get_user_profile(self, user_id: str) -> Optional[UserPreferenceProfile]:
        """Get user's preference profile for recommendations"""
        profile_dict = self.user_profiles_collection.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        if profile_dict:
            return UserPreferenceProfile(**profile_dict)
        # Return default profile
        return UserPreferenceProfile(user_id=user_id)
    
    async def update_user_profile(
        self,
        user_id: str,
        profile_data: Dict[str, Any]
    ) -> UserPreferenceProfile:
        """Update user's preference profile"""
        profile_data["user_id"] = user_id
        profile_data["updated_at"] = datetime.now(timezone.utc)
        
        self.user_profiles_collection.update_one(
            {"user_id": user_id},
            {"$set": profile_data},
            upsert=True
        )
        
        return await self.get_user_profile(user_id)
    
    async def record_feedback(self, feedback: RecommendationFeedback) -> bool:
        """Record user feedback on recommendations"""
        feedback_dict = feedback.model_dump()
        feedback_dict.pop("_id", None)
        self.feedback_collection.insert_one(feedback_dict)
        return True
    
    async def _generate_product_recommendations(
        self,
        request: RecommendationRequest,
        user_profile: Optional[UserPreferenceProfile],
        context: Dict[str, Any]
    ) -> List[ProductRecommendation]:
        """Internal method to generate product recommendations"""
        # Placeholder implementation
        recommendations = []
        
        for i in range(min(request.max_results, 10)):
            rec = ProductRecommendation(
                product_id=f"rec_{i}",
                product_name=f"Attractant recommandé #{i+1}",
                product_type="attractant",
                score=95.0 - (i * 5),
                confidence=0.85 - (i * 0.05),
                reasons=[
                    "Score nutritionnel élevé",
                    f"Adapté pour: {context.get('species', 'cerf')}"
                ]
            )
            recommendations.append(rec)
        
        return recommendations
    
    async def compute_similarity(
        self,
        product_id_1: str,
        product_id_2: str
    ) -> SimilarityScore:
        """Compute similarity between two products"""
        # Placeholder - would use product attributes
        return SimilarityScore(
            source_id=product_id_1,
            target_id=product_id_2,
            similarity_type="product",
            score=0.75,
            factors={
                "category": 0.9,
                "species_target": 0.8,
                "price_range": 0.6
            }
        )
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get recommendation engine statistics"""
        total_feedback = self.feedback_collection.count_documents({})
        total_profiles = self.user_profiles_collection.count_documents({})
        
        return {
            "total_user_profiles": total_profiles,
            "total_feedback_entries": total_feedback,
            "recommendation_types": [t.value for t in RecommendationType],
            "algorithms": [
                "collaborative_filtering",
                "content_based",
                "contextual",
                "hybrid"
            ]
        }
