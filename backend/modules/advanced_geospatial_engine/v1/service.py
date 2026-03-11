"""Advanced Geospatial Engine Service - PLAN MAITRE
Business logic for advanced geospatial analysis.

Version: 1.0.0
"""

import os
import math
from typing import Optional, List, Dict, Any
from pymongo import MongoClient

from .models import (
    ConcentrationZone, MovementCorridor, HabitatConnectivity,
    HeatmapData, DispersionModel
)


class AdvancedGeospatialService:
    """Service for advanced geospatial analysis"""
    
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
    def zones_collection(self):
        return self.db.concentration_zones
    
    @property
    def corridors_collection(self):
        return self.db.movement_corridors
    
    @property
    def heatmaps_collection(self):
        return self.db.activity_heatmaps
    
    async def identify_concentration_zones(
        self,
        lat: float,
        lng: float,
        radius_km: float = 5.0,
        species: Optional[str] = None
    ) -> List[ConcentrationZone]:
        """Identify wildlife concentration zones in area"""
        # Center coordinates used for zone calculations
        _ = {"lat": lat, "lng": lng}  # Reserved for future use
        
        # Placeholder - would analyze observation data, habitat, etc.
        zones = [
            ConcentrationZone(
                center={"lat": lat + 0.01, "lng": lng - 0.005},
                radius_m=300,
                zone_type="feeding",
                species=[species] if species else ["deer"],
                concentration_score=82,
                confidence=0.78,
                peak_activity_times=["06:00-08:00", "17:00-19:00"],
                data_sources=["observations", "habitat_analysis"],
                observation_count=15
            ),
            ConcentrationZone(
                center={"lat": lat - 0.008, "lng": lng + 0.003},
                radius_m=200,
                zone_type="bedding",
                species=[species] if species else ["deer"],
                concentration_score=75,
                confidence=0.72,
                peak_activity_times=["10:00-15:00"],
                data_sources=["terrain_analysis"],
                observation_count=8
            ),
            ConcentrationZone(
                center={"lat": lat + 0.005, "lng": lng + 0.008},
                radius_m=150,
                zone_type="watering",
                species=[species] if species else ["deer", "moose"],
                concentration_score=88,
                confidence=0.85,
                peak_activity_times=["07:00-09:00", "16:00-18:00"],
                data_sources=["water_features", "observations"],
                observation_count=22
            )
        ]
        
        return zones
    
    async def identify_corridors(
        self,
        lat: float,
        lng: float,
        radius_km: float = 5.0,
        species: Optional[str] = None
    ) -> List[MovementCorridor]:
        """Identify movement corridors in area"""
        # Placeholder corridor identification
        corridors = [
            MovementCorridor(
                path=[
                    {"lat": lat - 0.02, "lng": lng - 0.01},
                    {"lat": lat - 0.01, "lng": lng - 0.005},
                    {"lat": lat, "lng": lng},
                    {"lat": lat + 0.01, "lng": lng + 0.008},
                    {"lat": lat + 0.02, "lng": lng + 0.01}
                ],
                width_m=80,
                length_km=3.2,
                corridor_type="travel",
                species=[species] if species else ["deer"],
                terrain_type=["ridge", "forest_edge"],
                vegetation_cover=65,
                elevation_change=45,
                usage_frequency="high",
                peak_usage_times=["06:00-08:00", "17:00-19:00"],
                importance_score=85,
                hunting_potential=90,
                funnel_points=[
                    {"lat": lat, "lng": lng, "type": "saddle", "score": 92}
                ]
            )
        ]
        
        return corridors
    
    async def analyze_connectivity(
        self,
        lat: float,
        lng: float,
        radius_km: float = 5.0
    ) -> HabitatConnectivity:
        """Analyze habitat connectivity"""
        return HabitatConnectivity(
            center={"lat": lat, "lng": lng},
            radius_km=radius_km,
            overall_connectivity=72,
            fragmentation_index=0.35,
            patch_count=8,
            average_patch_size_ha=25.5,
            largest_patch_ha=85.0,
            barriers=[
                {"type": "road", "severity": "medium", "location": {"lat": lat + 0.01, "lng": lng}},
                {"type": "river", "severity": "low", "crossable": True}
            ],
            corridors_identified=3,
            connectivity_gaps=[
                {"location": {"lat": lat - 0.005, "lng": lng + 0.01}, "severity": "high"}
            ]
        )
    
    async def generate_heatmap(
        self,
        north: float,
        south: float,
        east: float,
        west: float,
        species: Optional[str] = None,
        data_type: str = "activity",
        resolution_m: float = 100
    ) -> HeatmapData:
        """Generate activity heatmap"""
        bounds = {"north": north, "south": south, "east": east, "west": west}
        
        # Calculate grid dimensions
        lat_range = north - south
        lng_range = east - west
        
        # Approximate meters per degree at this latitude
        m_per_deg_lat = 111320
        m_per_deg_lng = 111320 * math.cos(math.radians((north + south) / 2))
        
        rows = int((lat_range * m_per_deg_lat) / resolution_m)
        cols = int((lng_range * m_per_deg_lng) / resolution_m)
        
        # Limit grid size
        rows = min(rows, 100)
        cols = min(cols, 100)
        
        # Generate placeholder grid data
        import random
        grid = []
        hotspots = []
        max_intensity = 0
        
        for i in range(rows):
            row = []
            for j in range(cols):
                # Create some hotspot patterns
                center_dist = math.sqrt((i - rows/2)**2 + (j - cols/2)**2)
                base_value = max(0, 1 - center_dist / (rows/2))
                noise = random.random() * 0.3
                value = min(1, base_value + noise)
                row.append(round(value, 2))
                
                if value > max_intensity:
                    max_intensity = value
                
                if value > 0.7:
                    hotspot_lat = south + (i / rows) * lat_range
                    hotspot_lng = west + (j / cols) * lng_range
                    hotspots.append({
                        "lat": hotspot_lat,
                        "lng": hotspot_lng,
                        "intensity": value
                    })
            grid.append(row)
        
        return HeatmapData(
            bounds=bounds,
            resolution_m=resolution_m,
            species=species,
            data_type=data_type,
            grid=grid,
            total_points=rows * cols,
            max_intensity=max_intensity,
            hotspot_count=len(hotspots),
            hotspots=hotspots[:10]  # Top 10 hotspots
        )
    
    async def model_dispersion(
        self,
        lat: float,
        lng: float,
        species: str,
        time_hours: float = 24
    ) -> DispersionModel:
        """Model wildlife dispersion from a point"""
        source = {"lat": lat, "lng": lng}
        
        # Calculate probable area based on species movement rates
        movement_rates = {
            "deer": 3.0,  # km per day
            "moose": 5.0,
            "bear": 8.0
        }
        
        rate = movement_rates.get(species.lower(), 3.0)
        max_distance_km = rate * (time_hours / 24)
        area = math.pi * (max_distance_km ** 2)
        
        # Generate probability zones
        def circle_points(center_lat, center_lng, radius_km, n_points=16):
            points = []
            for i in range(n_points):
                angle = 2 * math.pi * i / n_points
                # Convert km to degrees (approximate)
                dlat = (radius_km / 111) * math.cos(angle)
                dlng = (radius_km / (111 * math.cos(math.radians(center_lat)))) * math.sin(angle)
                points.append({"lat": center_lat + dlat, "lng": center_lng + dlng})
            return points
        
        return DispersionModel(
            source_point=source,
            species=species,
            time_hours=time_hours,
            probable_area_km2=round(area, 2),
            high_probability_area=circle_points(lat, lng, max_distance_km * 0.3),
            medium_probability_area=circle_points(lat, lng, max_distance_km * 0.6),
            low_probability_area=circle_points(lat, lng, max_distance_km),
            terrain_barriers=[
                {"type": "highway", "impact": "high"}
            ],
            attractors=[
                {"type": "water_source", "distance_km": 0.5}
            ]
        )
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            "total_zones_cached": self.zones_collection.count_documents({}),
            "total_corridors_cached": self.corridors_collection.count_documents({}),
            "total_heatmaps": self.heatmaps_collection.count_documents({}),
            "analysis_types": [
                "concentration_zones",
                "movement_corridors",
                "habitat_connectivity",
                "activity_heatmaps",
                "dispersion_modeling"
            ]
        }
