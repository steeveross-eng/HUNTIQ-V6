"""Ecoforestry Engine Service - PLAN MAITRE
Business logic for ecoforestry data and habitat analysis.

Version: 1.0.0
"""

import os
from typing import List, Dict, Any
from datetime import datetime
from pymongo import MongoClient

from .models import (
    ForestStand, ForestStandType, HabitatAnalysis, HabitatQuality,
    RecentCut, EcoforestryRequest, EcoforestryResponse
)


class EcoforestryService:
    """Service for ecoforestry analysis"""
    
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
    def stands_collection(self):
        return self.db.forest_stands
    
    @property
    def cuts_collection(self):
        return self.db.forest_cuts
    
    @property
    def habitats_collection(self):
        return self.db.habitat_analyses
    
    async def analyze_area(
        self,
        request: EcoforestryRequest
    ) -> EcoforestryResponse:
        """Analyze ecoforestry data for an area"""
        center = {"lat": request.lat, "lng": request.lng}
        
        # Get forest stands (placeholder)
        stands = await self._get_stands_in_radius(center, request.radius_km)
        
        # Get recent cuts
        cuts = []
        if request.include_cuts:
            cuts = await self._get_cuts_in_radius(center, request.radius_km)
        
        # Habitat analysis
        habitat = None
        if request.include_habitats and request.species:
            habitat = await self.analyze_habitat(
                request.species, center, request.radius_km
            )
        
        # Calculate summary
        dominant_type = None
        if stands:
            type_counts = {}
            for s in stands:
                t = s.stand_type.value
                type_counts[t] = type_counts.get(t, 0) + 1
            dominant_type = ForestStandType(max(type_counts, key=type_counts.get))
        
        avg_age = None
        ages = [s.age_years for s in stands if s.age_years]
        if ages:
            avg_age = sum(ages) / len(ages)
        
        total_cut_area = sum(c.area_hectares for c in cuts)
        
        return EcoforestryResponse(
            center=center,
            radius_km=request.radius_km,
            total_stands=len(stands),
            stands=stands,
            recent_cuts=cuts,
            habitat_analysis=habitat,
            dominant_forest_type=dominant_type,
            average_stand_age=avg_age,
            total_cut_area_ha=total_cut_area
        )
    
    async def get_stands(
        self,
        lat: float,
        lng: float,
        radius_km: float = 5.0
    ) -> List[ForestStand]:
        """Get forest stands in area"""
        return await self._get_stands_in_radius({"lat": lat, "lng": lng}, radius_km)
    
    async def analyze_habitat(
        self,
        species: str,
        coordinates: Dict[str, float],
        radius_km: float = 5.0
    ) -> HabitatAnalysis:
        """Analyze habitat suitability for a species"""
        # Placeholder habitat analysis
        # Would integrate with real SIEF data and habitat models
        
        species_preferences = {
            "deer": {
                "food_availability": 75,
                "cover_quality": 70,
                "water_proximity": 65,
                "disturbance_level": 40,
                "connectivity": 80
            },
            "moose": {
                "food_availability": 70,
                "cover_quality": 75,
                "water_proximity": 85,
                "disturbance_level": 30,
                "connectivity": 75
            },
            "bear": {
                "food_availability": 80,
                "cover_quality": 65,
                "water_proximity": 70,
                "disturbance_level": 35,
                "connectivity": 70
            }
        }
        
        prefs = species_preferences.get(species.lower(), {
            "food_availability": 60,
            "cover_quality": 60,
            "water_proximity": 60,
            "disturbance_level": 50,
            "connectivity": 60
        })
        
        # Calculate overall score
        scores = list(prefs.values())
        overall_score = sum(scores) / len(scores)
        
        # Determine quality
        if overall_score >= 80:
            quality = HabitatQuality.EXCELLENT
        elif overall_score >= 65:
            quality = HabitatQuality.GOOD
        elif overall_score >= 50:
            quality = HabitatQuality.MODERATE
        elif overall_score >= 35:
            quality = HabitatQuality.POOR
        else:
            quality = HabitatQuality.UNSUITABLE
        
        # Identify limiting factors
        limiting = []
        for factor, score in prefs.items():
            if score < 50:
                limiting.append(factor.replace("_", " ").title())
        
        return HabitatAnalysis(
            species=species,
            coordinates=coordinates,
            analysis_radius_km=radius_km,
            overall_quality=quality,
            quality_score=overall_score,
            **prefs,
            limiting_factors=limiting,
            recommendations=[
                f"Zone favorable pour {species}",
                "Présence de coupes récentes attirantes",
                "Bonne connectivité des habitats"
            ] if overall_score >= 60 else [
                "Habitat limité pour cette espèce",
                "Considérer des zones alternatives"
            ]
        )
    
    async def get_recent_cuts(
        self,
        lat: float,
        lng: float,
        radius_km: float = 10.0,
        years_back: int = 5
    ) -> List[RecentCut]:
        """Get recent forest cuts"""
        return await self._get_cuts_in_radius(
            {"lat": lat, "lng": lng},
            radius_km,
            years_back
        )
    
    async def _get_stands_in_radius(
        self,
        center: Dict[str, float],
        radius_km: float
    ) -> List[ForestStand]:
        """Get stands in radius (placeholder)"""
        # Would query real geospatial data
        # Returning placeholder data
        return [
            ForestStand(
                coordinates=center,
                area_hectares=25.5,
                stand_type=ForestStandType.MIXED,
                dominant_species=["érable à sucre", "bouleau jaune"],
                secondary_species=["sapin baumier", "épinette rouge"],
                age_years=65,
                density_class="B",
                height_class=18
            ),
            ForestStand(
                coordinates={"lat": center["lat"] + 0.01, "lng": center["lng"] + 0.01},
                area_hectares=42.3,
                stand_type=ForestStandType.CONIFEROUS,
                dominant_species=["épinette noire", "sapin baumier"],
                age_years=45,
                density_class="A",
                height_class=15
            )
        ]
    
    async def _get_cuts_in_radius(
        self,
        center: Dict[str, float],
        radius_km: float,
        years_back: int = 5
    ) -> List[RecentCut]:
        """Get cuts in radius (placeholder)"""
        current_year = datetime.now().year
        
        return [
            RecentCut(
                coordinates={"lat": center["lat"] - 0.005, "lng": center["lng"] + 0.005},
                area_hectares=15.8,
                cut_year=current_year - 2,
                cut_type="selective",
                remaining_coverage=35,
                regeneration_status="early",
                deer_attraction_score=85,
                browse_availability="high"
            )
        ]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get ecoforestry engine statistics"""
        return {
            "total_stands_cached": self.stands_collection.count_documents({}),
            "total_cuts_cached": self.cuts_collection.count_documents({}),
            "total_habitat_analyses": self.habitats_collection.count_documents({}),
            "data_sources": ["SIEF", "MFFP", "Sentinel-2"],
            "supported_species": ["deer", "moose", "bear", "turkey", "grouse"]
        }
