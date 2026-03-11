"""3D Data Layers - PHASE 5
Data provider for terrain elevation and 3D analysis.

Version: 1.0.0
"""

import os
import math
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
from pymongo import MongoClient
from pydantic import BaseModel, Field
import uuid


# ==============================================
# MODELS
# ==============================================

class DEMTileData(BaseModel):
    """Digital Elevation Model tile data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Tile bounds
    north: float
    south: float
    east: float
    west: float
    
    # Resolution
    resolution_m: float = 30  # meters per pixel
    rows: int
    cols: int
    
    # Elevation data
    elevations: List[List[float]] = Field(default_factory=list)
    # 2D array [row][col] of elevation values
    
    # Stats
    min_elevation: float = 0
    max_elevation: float = 0
    mean_elevation: float = 0
    
    # Metadata
    source: str = "SRTM"  # SRTM, CDEM, LiDAR
    acquired_at: Optional[datetime] = None
    cached_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ElevationPoint(BaseModel):
    """Single elevation point"""
    lat: float
    lng: float
    elevation: float
    source: str = "DEM"
    resolution_m: float = 30


class SlopeAspectData(BaseModel):
    """Slope and aspect analysis data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Location
    coordinates: Dict[str, float]
    
    # Slope
    slope_degrees: float
    slope_percent: float
    slope_class: str  # flat, gentle, moderate, steep, very_steep
    
    # Aspect
    aspect_degrees: float  # 0-360, 0=N, 90=E, 180=S, 270=W
    aspect_direction: str  # N, NE, E, SE, S, SW, W, NW
    
    # Curvature
    curvature: Optional[float] = None  # Positive=convex, negative=concave


class TerrainFeatureData(BaseModel):
    """Terrain feature (saddle, ridge, valley, etc.)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Location
    coordinates: Dict[str, float]
    
    # Feature
    feature_type: str  # saddle, ridge, valley, peak, depression, bench
    elevation: float
    
    # Context
    prominence: Optional[float] = None
    isolation_km: Optional[float] = None
    
    # Hunting relevance
    hunting_score: float = Field(ge=0, le=100, default=50)
    hunting_notes: Optional[str] = None
    
    # Metadata
    identified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ViewshedCellData(BaseModel):
    """Viewshed analysis cell"""
    lat: float
    lng: float
    visible: bool
    distance_m: float
    elevation_diff: float


# ==============================================
# DATA LAYER SERVICE
# ==============================================

class Layers3DDataLayer:
    """Data layer for 3D terrain data"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
        
        # DEM sources and their resolutions
        self.dem_sources = {
            "SRTM": {"resolution_m": 30, "coverage": "global"},
            "CDEM": {"resolution_m": 20, "coverage": "canada"},
            "LiDAR": {"resolution_m": 1, "coverage": "limited"}
        }
        
        # Slope classifications
        self.slope_classes = [
            (0, 2, "flat"),
            (2, 8, "gentle"),
            (8, 16, "moderate"),
            (16, 30, "steep"),
            (30, 90, "very_steep")
        ]
        
        # Aspect directions
        self.aspect_ranges = [
            (337.5, 360, "N"), (0, 22.5, "N"),
            (22.5, 67.5, "NE"),
            (67.5, 112.5, "E"),
            (112.5, 157.5, "SE"),
            (157.5, 202.5, "S"),
            (202.5, 247.5, "SW"),
            (247.5, 292.5, "W"),
            (292.5, 337.5, "NW")
        ]
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    @property
    def tiles_collection(self):
        return self.db.dem_tiles
    
    @property
    def features_collection(self):
        return self.db.terrain_features
    
    # ===========================================
    # ELEVATION DATA
    # ===========================================
    
    async def get_elevation(
        self,
        lat: float,
        lng: float,
        source: str = "SRTM"
    ) -> ElevationPoint:
        """Get elevation at a point"""
        # Check cache
        tile = await self._get_tile_for_point(lat, lng)
        
        if tile:
            elevation = self._interpolate_elevation(tile, lat, lng)
        else:
            # Generate simulated elevation
            elevation = self._simulate_elevation(lat, lng)
        
        return ElevationPoint(
            lat=lat,
            lng=lng,
            elevation=round(elevation, 1),
            source=source,
            resolution_m=self.dem_sources.get(source, {}).get("resolution_m", 30)
        )
    
    async def get_elevations_bulk(
        self,
        points: List[Tuple[float, float]]
    ) -> List[ElevationPoint]:
        """Get elevations for multiple points"""
        results = []
        for lat, lng in points:
            elev = await self.get_elevation(lat, lng)
            results.append(elev)
        return results
    
    async def get_elevation_profile(
        self,
        start_lat: float,
        start_lng: float,
        end_lat: float,
        end_lng: float,
        num_points: int = 50
    ) -> Dict[str, Any]:
        """Get elevation profile along a line"""
        points = []
        elevations = []
        
        for i in range(num_points):
            t = i / (num_points - 1)
            lat = start_lat + t * (end_lat - start_lat)
            lng = start_lng + t * (end_lng - start_lng)
            
            elev_point = await self.get_elevation(lat, lng)
            points.append({"lat": lat, "lng": lng, "elevation": elev_point.elevation})
            elevations.append(elev_point.elevation)
        
        # Calculate stats
        distance_km = self._haversine(start_lat, start_lng, end_lat, end_lng)
        
        gain = 0
        loss = 0
        for i in range(1, len(elevations)):
            diff = elevations[i] - elevations[i-1]
            if diff > 0:
                gain += diff
            else:
                loss += abs(diff)
        
        return {
            "points": points,
            "distance_km": round(distance_km, 2),
            "min_elevation": round(min(elevations), 1),
            "max_elevation": round(max(elevations), 1),
            "elevation_gain": round(gain, 1),
            "elevation_loss": round(loss, 1),
            "average_slope_pct": round((max(elevations) - min(elevations)) / (distance_km * 1000) * 100, 1) if distance_km > 0 else 0
        }
    
    # ===========================================
    # SLOPE & ASPECT
    # ===========================================
    
    async def get_slope_aspect(
        self,
        lat: float,
        lng: float,
        cell_size_m: float = 30
    ) -> SlopeAspectData:
        """Calculate slope and aspect at a point"""
        # Get elevations for 3x3 neighborhood
        delta = cell_size_m / 111000  # Approximate degrees
        
        # Get 9 elevation points
        elevations = {}
        for di, dj in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]:
            p_lat = lat + di * delta
            p_lng = lng + dj * delta
            elev = await self.get_elevation(p_lat, p_lng)
            elevations[(di, dj)] = elev.elevation
        
        # Calculate slope using Horn's method
        dz_dx = (
            (elevations[(1,-1)] + 2*elevations[(1,0)] + elevations[(1,1)]) -
            (elevations[(-1,-1)] + 2*elevations[(-1,0)] + elevations[(-1,1)])
        ) / (8 * cell_size_m)
        
        dz_dy = (
            (elevations[(-1,1)] + 2*elevations[(0,1)] + elevations[(1,1)]) -
            (elevations[(-1,-1)] + 2*elevations[(0,-1)] + elevations[(1,-1)])
        ) / (8 * cell_size_m)
        
        slope_rad = math.atan(math.sqrt(dz_dx**2 + dz_dy**2))
        slope_deg = math.degrees(slope_rad)
        slope_pct = math.tan(slope_rad) * 100
        
        # Calculate aspect
        aspect_rad = math.atan2(-dz_dy, -dz_dx)
        aspect_deg = math.degrees(aspect_rad)
        if aspect_deg < 0:
            aspect_deg += 360
        
        # Classify
        slope_class = self._classify_slope(slope_deg)
        aspect_dir = self._classify_aspect(aspect_deg)
        
        return SlopeAspectData(
            coordinates={"lat": lat, "lng": lng},
            slope_degrees=round(slope_deg, 1),
            slope_percent=round(slope_pct, 1),
            slope_class=slope_class,
            aspect_degrees=round(aspect_deg, 1),
            aspect_direction=aspect_dir
        )
    
    def _classify_slope(self, slope_deg: float) -> str:
        """Classify slope"""
        for min_s, max_s, cls in self.slope_classes:
            if min_s <= slope_deg < max_s:
                return cls
        return "very_steep"
    
    def _classify_aspect(self, aspect_deg: float) -> str:
        """Classify aspect direction"""
        for min_a, max_a, direction in self.aspect_ranges:
            if min_a <= aspect_deg < max_a:
                return direction
        return "N"
    
    # ===========================================
    # TERRAIN FEATURES
    # ===========================================
    
    async def identify_terrain_features(
        self,
        lat: float,
        lng: float,
        radius_km: float = 2.0
    ) -> List[TerrainFeatureData]:
        """Identify terrain features in area"""
        # Check cache
        features = list(self.features_collection.find({
            "coordinates.lat": {"$gte": lat - radius_km/111, "$lte": lat + radius_km/111},
            "coordinates.lng": {"$gte": lng - radius_km/111, "$lte": lng + radius_km/111}
        }, {"_id": 0}))
        
        if features:
            return [TerrainFeatureData(**f) for f in features]
        
        # Generate placeholder features
        return self._generate_placeholder_features(lat, lng, radius_km)
    
    async def get_saddles_in_area(
        self,
        lat: float,
        lng: float,
        radius_km: float = 2.0
    ) -> List[TerrainFeatureData]:
        """Get saddles (key hunting locations)"""
        features = await self.identify_terrain_features(lat, lng, radius_km)
        return [f for f in features if f.feature_type == "saddle"]
    
    def _generate_placeholder_features(
        self,
        lat: float,
        lng: float,
        radius_km: float
    ) -> List[TerrainFeatureData]:
        """Generate placeholder terrain features"""
        import random
        
        features = []
        feature_types = ["saddle", "ridge", "valley", "bench", "funnel"]
        
        for i in range(random.randint(3, 8)):
            f_lat = lat + (random.random() - 0.5) * (radius_km / 55)
            f_lng = lng + (random.random() - 0.5) * (radius_km / 55)
            f_type = random.choice(feature_types)
            
            # Hunting score based on feature type
            hunting_scores = {
                "saddle": random.randint(80, 95),
                "funnel": random.randint(75, 90),
                "ridge": random.randint(60, 80),
                "bench": random.randint(55, 75),
                "valley": random.randint(50, 70)
            }
            
            features.append(TerrainFeatureData(
                coordinates={"lat": f_lat, "lng": f_lng},
                feature_type=f_type,
                elevation=200 + random.random() * 300,
                hunting_score=hunting_scores.get(f_type, 60),
                hunting_notes=f"Point stratégique: {f_type}"
            ))
        
        return features
    
    # ===========================================
    # VIEWSHED
    # ===========================================
    
    async def calculate_viewshed(
        self,
        lat: float,
        lng: float,
        observer_height: float = 1.7,
        radius_m: float = 2000,
        resolution_m: float = 50
    ) -> Dict[str, Any]:
        """Calculate viewshed from a point"""
        observer_elev = (await self.get_elevation(lat, lng)).elevation + observer_height
        
        # Generate viewshed grid
        visible_cells = []
        total_cells = 0
        
        num_rings = int(radius_m / resolution_m)
        
        for ring in range(1, num_rings + 1):
            ring_radius_m = ring * resolution_m
            circumference = 2 * math.pi * ring_radius_m
            num_points = max(8, int(circumference / resolution_m))
            
            for i in range(num_points):
                angle = 2 * math.pi * i / num_points
                
                # Calculate target position
                delta_lat = (ring_radius_m / 111000) * math.cos(angle)
                delta_lng = (ring_radius_m / (111000 * math.cos(math.radians(lat)))) * math.sin(angle)
                
                target_lat = lat + delta_lat
                target_lng = lng + delta_lng
                
                target_elev = (await self.get_elevation(target_lat, target_lng)).elevation
                
                # Simple line-of-sight check
                visible = self._check_los(
                    observer_elev, target_elev, ring_radius_m
                )
                
                total_cells += 1
                if visible:
                    visible_cells.append({
                        "lat": target_lat,
                        "lng": target_lng,
                        "distance_m": ring_radius_m
                    })
        
        visible_area_km2 = math.pi * (radius_m / 1000) ** 2 * (len(visible_cells) / total_cells)
        
        return {
            "observer": {"lat": lat, "lng": lng, "elevation": observer_elev},
            "radius_m": radius_m,
            "visible_cells": len(visible_cells),
            "total_cells": total_cells,
            "visible_percentage": round(len(visible_cells) / total_cells * 100, 1),
            "visible_area_km2": round(visible_area_km2, 2)
        }
    
    def _check_los(
        self,
        observer_elev: float,
        target_elev: float,
        distance_m: float
    ) -> bool:
        """Simple line-of-sight check"""
        # Simplified - doesn't account for terrain between points
        angle = math.atan2(target_elev - observer_elev, distance_m)
        return angle > -0.05  # ~3 degrees below horizontal
    
    # ===========================================
    # HELPERS
    # ===========================================
    
    async def _get_tile_for_point(
        self,
        lat: float,
        lng: float
    ) -> Optional[DEMTileData]:
        """Get cached DEM tile containing point"""
        tile = self.tiles_collection.find_one({
            "north": {"$gte": lat},
            "south": {"$lte": lat},
            "east": {"$gte": lng},
            "west": {"$lte": lng}
        }, {"_id": 0})
        
        if tile:
            return DEMTileData(**tile)
        return None
    
    def _interpolate_elevation(
        self,
        tile: DEMTileData,
        lat: float,
        lng: float
    ) -> float:
        """Interpolate elevation from tile"""
        # Calculate position in tile
        lat_pct = (tile.north - lat) / (tile.north - tile.south)
        lng_pct = (lng - tile.west) / (tile.east - tile.west)
        
        row = int(lat_pct * (tile.rows - 1))
        col = int(lng_pct * (tile.cols - 1))
        
        row = max(0, min(row, tile.rows - 1))
        col = max(0, min(col, tile.cols - 1))
        
        return tile.elevations[row][col]
    
    def _simulate_elevation(self, lat: float, lng: float) -> float:
        """Simulate elevation for demo purposes"""
        # Create some terrain variation
        base = 200
        variation = (
            math.sin(lat * 50) * 50 +
            math.cos(lng * 50) * 40 +
            math.sin((lat + lng) * 30) * 30
        )
        return base + variation
    
    def _haversine(
        self,
        lat1: float,
        lng1: float,
        lat2: float,
        lng2: float
    ) -> float:
        """Calculate distance in km"""
        R = 6371
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    # ===========================================
    # STATS
    # ===========================================
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get data layer statistics"""
        return {
            "layer": "layers_3d",
            "version": "1.0.0",
            "cached_tiles": self.tiles_collection.count_documents({}),
            "cached_features": self.features_collection.count_documents({}),
            "dem_sources": list(self.dem_sources.keys()),
            "feature_types": ["saddle", "ridge", "valley", "peak", "bench", "funnel"],
            "status": "operational"
        }


# Singleton instance
_layer_instance = None

def get_3d_layer() -> Layers3DDataLayer:
    """Get singleton instance"""
    global _layer_instance
    if _layer_instance is None:
        _layer_instance = Layers3DDataLayer()
    return _layer_instance
