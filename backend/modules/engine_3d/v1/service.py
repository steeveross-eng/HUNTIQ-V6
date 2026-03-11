"""Engine 3D Service - PLAN MAITRE
Business logic for 3D terrain visualization and analysis.

Version: 1.0.0
"""

import os
import math
from typing import Dict, Any
from pymongo import MongoClient

from .models import (
    ElevationPoint, ElevationProfile, ViewshedAnalysis,
    TerrainAnalysis, Terrain3DExport
)


class Engine3DService:
    """Service for 3D terrain analysis"""
    
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
    
    async def get_elevation(
        self,
        lat: float,
        lng: float
    ) -> ElevationPoint:
        """Get elevation at a single point"""
        # Placeholder - would use DEM data
        # Simulating elevation based on coordinates
        base_elevation = 200 + (lat * 10) + (lng * -5)
        
        return ElevationPoint(
            lat=lat,
            lng=lng,
            elevation=round(base_elevation, 1),
            source="DEM_30m"
        )
    
    async def get_elevation_profile(
        self,
        start_lat: float,
        start_lng: float,
        end_lat: float,
        end_lng: float,
        num_points: int = 50
    ) -> ElevationProfile:
        """Generate elevation profile along a path"""
        start = {"lat": start_lat, "lng": start_lng}
        end = {"lat": end_lat, "lng": end_lng}
        
        # Calculate distance
        distance_km = self._haversine_distance(
            start_lat, start_lng, end_lat, end_lng
        )
        
        # Generate points along path
        points = []
        elevations = []
        
        for i in range(num_points):
            t = i / (num_points - 1)
            lat = start_lat + t * (end_lat - start_lat)
            lng = start_lng + t * (end_lng - start_lng)
            
            elev_point = await self.get_elevation(lat, lng)
            points.append(elev_point)
            elevations.append(elev_point.elevation)
        
        # Calculate stats
        min_elev = min(elevations)
        max_elev = max(elevations)
        
        gain = 0
        loss = 0
        for i in range(1, len(elevations)):
            diff = elevations[i] - elevations[i-1]
            if diff > 0:
                gain += diff
            else:
                loss += abs(diff)
        
        avg_slope = ((max_elev - min_elev) / (distance_km * 1000)) * 100 if distance_km > 0 else 0
        
        return ElevationProfile(
            start_point=start,
            end_point=end,
            distance_km=round(distance_km, 2),
            points=points,
            min_elevation=round(min_elev, 1),
            max_elevation=round(max_elev, 1),
            elevation_gain=round(gain, 1),
            elevation_loss=round(loss, 1),
            average_slope=round(avg_slope, 1)
        )
    
    async def analyze_viewshed(
        self,
        lat: float,
        lng: float,
        observer_height: float = 1.7,
        radius_km: float = 2.0
    ) -> ViewshedAnalysis:
        """Analyze visible area from a point"""
        observer = {"lat": lat, "lng": lng}
        
        # Placeholder viewshed calculation
        # Would use DEM and line-of-sight algorithms
        
        visible_area = math.pi * (radius_km ** 2) * 0.65  # ~65% typically visible
        visible_pct = 65.0
        
        # Identify blind zones (placeholder)
        blind_zones = [
            {
                "direction": "NE",
                "distance_m": 800,
                "reason": "Ridge blocking view",
                "area_m2": 50000
            }
        ]
        
        return ViewshedAnalysis(
            observer_point=observer,
            observer_height=observer_height,
            radius_km=radius_km,
            visible_area_km2=round(visible_area, 2),
            visible_percentage=visible_pct,
            blind_zones=blind_zones
        )
    
    async def analyze_terrain(
        self,
        lat: float,
        lng: float,
        radius_km: float = 1.0
    ) -> TerrainAnalysis:
        """Comprehensive terrain analysis"""
        center = {"lat": lat, "lng": lng}
        
        # Placeholder terrain analysis
        base_elev = 200 + (lat * 10)
        
        # Simulate aspect distribution
        aspects = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        aspect_dist = {a: round(12.5 + (hash(a) % 5), 1) for a in aspects}
        
        # Hunting features
        funnel_points = [
            {
                "lat": lat + 0.002,
                "lng": lng - 0.001,
                "type": "terrain_funnel",
                "score": 85
            }
        ]
        
        saddles = [
            {
                "lat": lat - 0.003,
                "lng": lng + 0.002,
                "elevation": base_elev + 50,
                "score": 78
            }
        ]
        
        return TerrainAnalysis(
            center=center,
            radius_km=radius_km,
            min_elevation=round(base_elev - 30, 1),
            max_elevation=round(base_elev + 120, 1),
            mean_elevation=round(base_elev + 45, 1),
            relief=150,
            average_slope=12.5,
            max_slope=45.0,
            flat_area_percentage=25.0,
            steep_area_percentage=15.0,
            dominant_aspect="SE",
            aspect_distribution=aspect_dist,
            funnel_points=funnel_points,
            saddles=saddles
        )
    
    async def export_3d_terrain(
        self,
        north: float,
        south: float,
        east: float,
        west: float,
        format: str = "glb",
        resolution_m: float = 30.0
    ) -> Terrain3DExport:
        """Export 3D terrain data"""
        bounds = {
            "north": north,
            "south": south,
            "east": east,
            "west": west
        }
        
        # Calculate approximate size
        lat_dist = (north - south) * 111.32  # km
        lng_dist = (east - west) * 111.32 * math.cos(math.radians((north + south) / 2))
        area_km2 = lat_dist * lng_dist
        
        vertices = int((area_km2 * 1e6) / (resolution_m ** 2))
        
        return Terrain3DExport(
            bounds=bounds,
            format=format,
            resolution_m=resolution_m,
            vertex_count=vertices,
            file_url=None,  # Would generate actual file
            file_size_mb=round(vertices * 0.00005, 2)
        )
    
    def _haversine_distance(
        self,
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float
    ) -> float:
        """Calculate distance between two points in km"""
        R = 6371  # Earth radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            "dem_sources": ["SRTM", "CDEM", "LiDAR"],
            "resolution_options": ["30m", "10m", "1m"],
            "export_formats": ["glb", "obj", "stl", "geotiff"],
            "features": [
                "elevation_profiles",
                "viewshed_analysis",
                "terrain_analysis",
                "3d_export"
            ]
        }
