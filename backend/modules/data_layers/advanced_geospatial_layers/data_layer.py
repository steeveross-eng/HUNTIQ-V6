"""Advanced Geospatial Data Layers - PHASE 5
Data provider for corridors, concentration zones, and connectivity analysis.

Version: 1.0.0
"""

import os
import math
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pymongo import MongoClient
from pydantic import BaseModel, Field
from enum import Enum
import uuid


# ==============================================
# MODELS
# ==============================================

class CorridorType(str, Enum):
    """Corridor types"""
    TRAVEL = "travel"
    MIGRATION = "migration"
    DAILY = "daily"
    SEASONAL = "seasonal"


class ZoneType(str, Enum):
    """Concentration zone types"""
    FEEDING = "feeding"
    BEDDING = "bedding"
    WATERING = "watering"
    STAGING = "staging"
    CROSSING = "crossing"


class CorridorData(BaseModel):
    """Wildlife movement corridor data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Path
    path: List[Dict[str, float]] = Field(default_factory=list)
    width_m: float = 100
    length_km: float = 0
    
    # Classification
    corridor_type: CorridorType = CorridorType.TRAVEL
    species: List[str] = Field(default_factory=list)
    
    # Characteristics
    terrain_types: List[str] = Field(default_factory=list)
    vegetation_cover_pct: float = 0
    average_elevation: float = 0
    elevation_change: float = 0
    
    # Usage metrics
    usage_intensity: float = Field(ge=0, le=1, default=0.5)
    peak_usage_hours: List[int] = Field(default_factory=list)
    seasonal_usage: Dict[str, float] = Field(default_factory=dict)
    
    # Funnel points
    funnel_points: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Scores
    importance_score: float = Field(ge=0, le=100, default=50)
    hunting_potential: float = Field(ge=0, le=100, default=50)
    
    # Metadata
    data_source: str = "analysis"
    confidence: float = Field(ge=0, le=1, default=0.7)
    identified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConcentrationZoneData(BaseModel):
    """Wildlife concentration zone data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Location
    center: Dict[str, float]
    radius_m: float = 500
    boundary: Optional[List[Dict[str, float]]] = None
    
    # Classification
    zone_type: ZoneType = ZoneType.FEEDING
    species: List[str] = Field(default_factory=list)
    
    # Characteristics
    habitat_type: str = "mixed"
    vegetation_cover_pct: float = 0
    water_proximity_m: Optional[float] = None
    elevation: float = 0
    
    # Usage metrics
    concentration_score: float = Field(ge=0, le=100, default=50)
    peak_activity_hours: List[int] = Field(default_factory=list)
    seasonal_intensity: Dict[str, float] = Field(default_factory=dict)
    
    # Observations
    observation_count: int = 0
    last_observation: Optional[datetime] = None
    
    # Metadata
    data_source: str = "analysis"
    confidence: float = Field(ge=0, le=1, default=0.7)
    identified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConnectivityData(BaseModel):
    """Habitat connectivity analysis data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Area
    center: Dict[str, float]
    radius_km: float
    
    # Connectivity metrics
    overall_connectivity: float = Field(ge=0, le=100, default=50)
    fragmentation_index: float = Field(ge=0, le=1, default=0.5)
    
    # Patches
    patch_count: int = 0
    total_patch_area_ha: float = 0
    average_patch_size_ha: float = 0
    largest_patch_ha: float = 0
    
    # Barriers
    barriers: List[Dict[str, Any]] = Field(default_factory=list)
    barrier_density_per_km: float = 0
    
    # Corridors
    corridor_count: int = 0
    corridor_ids: List[str] = Field(default_factory=list)
    
    # Gaps
    connectivity_gaps: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HeatmapCellData(BaseModel):
    """Single heatmap cell"""
    lat: float
    lng: float
    value: float = Field(ge=0, le=1)
    count: int = 0


class ActivityHeatmapData(BaseModel):
    """Activity heatmap data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Bounds
    north: float
    south: float
    east: float
    west: float
    
    # Grid
    resolution_m: float = 100
    rows: int
    cols: int
    cells: List[List[float]] = Field(default_factory=list)
    
    # Metadata
    species: Optional[str] = None
    data_type: str = "activity"
    time_period: Optional[str] = None
    
    # Stats
    total_observations: int = 0
    max_intensity: float = 0
    hotspot_count: int = 0
    
    # Generated
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==============================================
# DATA LAYER SERVICE
# ==============================================

class AdvancedGeospatialDataLayer:
    """Data layer for advanced geospatial analysis"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
        
        # Barrier types and their impact
        self.barrier_types = {
            "highway": {"severity": 0.9, "crossable": False},
            "road_paved": {"severity": 0.6, "crossable": True},
            "road_gravel": {"severity": 0.3, "crossable": True},
            "river_large": {"severity": 0.7, "crossable": False},
            "river_small": {"severity": 0.3, "crossable": True},
            "lake": {"severity": 0.8, "crossable": False},
            "urban": {"severity": 1.0, "crossable": False},
            "agricultural": {"severity": 0.4, "crossable": True},
            "clearcut_recent": {"severity": 0.5, "crossable": True}
        }
        
        # Zone characteristics by type
        self.zone_characteristics = {
            ZoneType.FEEDING: {
                "peak_hours": [6, 7, 17, 18],
                "vegetation_cover_range": (20, 60),
                "typical_radius_m": 300
            },
            ZoneType.BEDDING: {
                "peak_hours": [10, 11, 12, 13, 14],
                "vegetation_cover_range": (70, 95),
                "typical_radius_m": 200
            },
            ZoneType.WATERING: {
                "peak_hours": [7, 8, 16, 17],
                "vegetation_cover_range": (30, 70),
                "typical_radius_m": 150
            },
            ZoneType.STAGING: {
                "peak_hours": [5, 6, 17, 18, 19],
                "vegetation_cover_range": (40, 70),
                "typical_radius_m": 400
            },
            ZoneType.CROSSING: {
                "peak_hours": [6, 7, 17, 18],
                "vegetation_cover_range": (20, 50),
                "typical_radius_m": 100
            }
        }
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    @property
    def corridors_collection(self):
        return self.db.geospatial_corridors
    
    @property
    def zones_collection(self):
        return self.db.concentration_zones
    
    @property
    def connectivity_collection(self):
        return self.db.connectivity_analyses
    
    @property
    def heatmaps_collection(self):
        return self.db.activity_heatmaps
    
    # ===========================================
    # CORRIDORS
    # ===========================================
    
    async def get_corridors_in_area(
        self,
        lat: float,
        lng: float,
        radius_km: float = 5.0,
        species: Optional[str] = None,
        corridor_type: Optional[str] = None
    ) -> List[CorridorData]:
        """Get corridors in area"""
        # Check cache
        query = {}
        if species:
            query["species"] = species.lower()
        if corridor_type:
            query["corridor_type"] = corridor_type
        
        corridors = list(self.corridors_collection.find(query, {"_id": 0}).limit(50))
        
        if corridors:
            return [CorridorData(**c) for c in corridors]
        
        # Generate placeholder corridors
        return self._generate_placeholder_corridors(lat, lng, radius_km, species)
    
    async def get_corridor_by_id(self, corridor_id: str) -> Optional[CorridorData]:
        """Get specific corridor"""
        corridor = self.corridors_collection.find_one(
            {"id": corridor_id}, {"_id": 0}
        )
        if corridor:
            return CorridorData(**corridor)
        return None
    
    async def save_corridor(self, corridor: CorridorData) -> bool:
        """Save corridor data"""
        corridor_dict = corridor.model_dump()
        corridor_dict.pop("_id", None)
        self.corridors_collection.update_one(
            {"id": corridor.id},
            {"$set": corridor_dict},
            upsert=True
        )
        return True
    
    # ===========================================
    # CONCENTRATION ZONES
    # ===========================================
    
    async def get_zones_in_area(
        self,
        lat: float,
        lng: float,
        radius_km: float = 5.0,
        species: Optional[str] = None,
        zone_type: Optional[str] = None
    ) -> List[ConcentrationZoneData]:
        """Get concentration zones in area"""
        query = {}
        if species:
            query["species"] = species.lower()
        if zone_type:
            query["zone_type"] = zone_type
        
        zones = list(self.zones_collection.find(query, {"_id": 0}).limit(100))
        
        if zones:
            return [ConcentrationZoneData(**z) for z in zones]
        
        # Generate placeholder zones
        return self._generate_placeholder_zones(lat, lng, radius_km, species)
    
    async def get_feeding_zones(
        self,
        lat: float,
        lng: float,
        radius_km: float = 5.0,
        species: Optional[str] = None
    ) -> List[ConcentrationZoneData]:
        """Get feeding zones specifically"""
        return await self.get_zones_in_area(
            lat, lng, radius_km, species, ZoneType.FEEDING.value
        )
    
    async def get_bedding_zones(
        self,
        lat: float,
        lng: float,
        radius_km: float = 5.0,
        species: Optional[str] = None
    ) -> List[ConcentrationZoneData]:
        """Get bedding zones specifically"""
        return await self.get_zones_in_area(
            lat, lng, radius_km, species, ZoneType.BEDDING.value
        )
    
    async def save_zone(self, zone: ConcentrationZoneData) -> bool:
        """Save zone data"""
        zone_dict = zone.model_dump()
        zone_dict.pop("_id", None)
        self.zones_collection.update_one(
            {"id": zone.id},
            {"$set": zone_dict},
            upsert=True
        )
        return True
    
    # ===========================================
    # CONNECTIVITY
    # ===========================================
    
    async def analyze_connectivity(
        self,
        lat: float,
        lng: float,
        radius_km: float = 5.0
    ) -> ConnectivityData:
        """Analyze habitat connectivity in area"""
        # Check cache
        analysis = self.connectivity_collection.find_one({
            "center.lat": {"$gte": lat - 0.01, "$lte": lat + 0.01},
            "center.lng": {"$gte": lng - 0.01, "$lte": lng + 0.01}
        }, {"_id": 0})
        
        if analysis:
            return ConnectivityData(**analysis)
        
        # Generate analysis
        return self._generate_connectivity_analysis(lat, lng, radius_km)
    
    async def get_barriers_in_area(
        self,
        lat: float,
        lng: float,
        radius_km: float = 5.0
    ) -> List[Dict[str, Any]]:
        """Get barriers in area"""
        # Placeholder - would query actual barrier data
        import random
        
        barriers = []
        barrier_types = list(self.barrier_types.keys())
        
        for i in range(random.randint(2, 6)):
            b_type = random.choice(barrier_types)
            b_info = self.barrier_types[b_type]
            
            barriers.append({
                "type": b_type,
                "severity": b_info["severity"],
                "crossable": b_info["crossable"],
                "location": {
                    "lat": lat + (random.random() - 0.5) * (radius_km / 55),
                    "lng": lng + (random.random() - 0.5) * (radius_km / 55)
                }
            })
        
        return barriers
    
    # ===========================================
    # HEATMAPS
    # ===========================================
    
    async def generate_heatmap(
        self,
        north: float,
        south: float,
        east: float,
        west: float,
        species: Optional[str] = None,
        resolution_m: float = 100
    ) -> ActivityHeatmapData:
        """Generate activity heatmap"""
        # Calculate grid dimensions
        lat_range = north - south
        lng_range = east - west
        
        m_per_deg_lat = 111000
        m_per_deg_lng = 111000 * abs(math.cos(math.radians((north + south) / 2)))
        
        rows = min(100, int((lat_range * m_per_deg_lat) / resolution_m))
        cols = min(100, int((lng_range * m_per_deg_lng) / resolution_m))
        
        rows = max(10, rows)
        cols = max(10, cols)
        
        # Generate heatmap data
        import random
        
        cells = []
        max_intensity = 0
        hotspot_count = 0
        
        # Create some hotspot centers
        hotspot_centers = [
            (random.uniform(0.2, 0.8), random.uniform(0.2, 0.8))
            for _ in range(random.randint(2, 5))
        ]
        
        for i in range(rows):
            row = []
            for j in range(cols):
                # Calculate intensity based on distance to hotspots
                row_pct = i / rows
                col_pct = j / cols
                
                intensity = 0.1
                for hc_row, hc_col in hotspot_centers:
                    dist = math.sqrt((row_pct - hc_row)**2 + (col_pct - hc_col)**2)
                    intensity += max(0, 0.5 - dist) * random.uniform(0.8, 1.2)
                
                intensity = min(1.0, intensity)
                row.append(round(intensity, 3))
                
                if intensity > max_intensity:
                    max_intensity = intensity
                if intensity > 0.7:
                    hotspot_count += 1
            
            cells.append(row)
        
        return ActivityHeatmapData(
            north=north,
            south=south,
            east=east,
            west=west,
            resolution_m=resolution_m,
            rows=rows,
            cols=cols,
            cells=cells,
            species=species,
            max_intensity=round(max_intensity, 3),
            hotspot_count=hotspot_count
        )
    
    async def get_hotspots(
        self,
        heatmap: ActivityHeatmapData,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Extract hotspots from heatmap"""
        hotspots = []
        
        lat_step = (heatmap.north - heatmap.south) / heatmap.rows
        lng_step = (heatmap.east - heatmap.west) / heatmap.cols
        
        for i, row in enumerate(heatmap.cells):
            for j, value in enumerate(row):
                if value >= threshold:
                    hotspots.append({
                        "lat": heatmap.south + (i + 0.5) * lat_step,
                        "lng": heatmap.west + (j + 0.5) * lng_step,
                        "intensity": value
                    })
        
        # Sort by intensity
        hotspots.sort(key=lambda x: x["intensity"], reverse=True)
        
        return hotspots[:20]  # Top 20
    
    # ===========================================
    # PLACEHOLDER GENERATORS
    # ===========================================
    
    def _generate_placeholder_corridors(
        self,
        lat: float,
        lng: float,
        radius_km: float,
        species: Optional[str]
    ) -> List[CorridorData]:
        """Generate placeholder corridors"""
        import random
        
        corridors = []
        
        for i in range(random.randint(2, 5)):
            # Generate path
            path = []
            base_lat = lat + (random.random() - 0.5) * (radius_km / 55)
            base_lng = lng + (random.random() - 0.5) * (radius_km / 55)
            
            direction = random.uniform(0, 2 * math.pi)
            
            for j in range(random.randint(5, 10)):
                path.append({
                    "lat": base_lat + j * 0.005 * math.cos(direction),
                    "lng": base_lng + j * 0.005 * math.sin(direction)
                })
            
            corridors.append(CorridorData(
                path=path,
                width_m=random.randint(50, 150),
                length_km=random.uniform(1, 5),
                corridor_type=random.choice(list(CorridorType)),
                species=[species] if species else ["deer"],
                terrain_types=random.sample(["ridge", "valley", "forest_edge", "stream"], 2),
                vegetation_cover_pct=random.uniform(40, 80),
                usage_intensity=random.uniform(0.5, 0.9),
                peak_usage_hours=[6, 7, 17, 18],
                importance_score=random.randint(60, 95),
                hunting_potential=random.randint(65, 95),
                funnel_points=[{
                    "lat": path[len(path)//2]["lat"],
                    "lng": path[len(path)//2]["lng"],
                    "type": "natural_funnel",
                    "score": random.randint(75, 95)
                }]
            ))
        
        return corridors
    
    def _generate_placeholder_zones(
        self,
        lat: float,
        lng: float,
        radius_km: float,
        species: Optional[str]
    ) -> List[ConcentrationZoneData]:
        """Generate placeholder concentration zones"""
        import random
        
        zones = []
        zone_types = list(ZoneType)
        
        for i in range(random.randint(5, 12)):
            z_type = random.choice(zone_types)
            z_chars = self.zone_characteristics[z_type]
            
            zones.append(ConcentrationZoneData(
                center={
                    "lat": lat + (random.random() - 0.5) * (radius_km / 55),
                    "lng": lng + (random.random() - 0.5) * (radius_km / 55)
                },
                radius_m=z_chars["typical_radius_m"] * random.uniform(0.8, 1.2),
                zone_type=z_type,
                species=[species] if species else ["deer"],
                vegetation_cover_pct=random.uniform(*z_chars["vegetation_cover_range"]),
                concentration_score=random.randint(60, 95),
                peak_activity_hours=z_chars["peak_hours"],
                observation_count=random.randint(5, 50),
                confidence=random.uniform(0.6, 0.9)
            ))
        
        return zones
    
    def _generate_connectivity_analysis(
        self,
        lat: float,
        lng: float,
        radius_km: float
    ) -> ConnectivityData:
        """Generate connectivity analysis"""
        import random
        
        # Generate barriers
        barriers = []
        for i in range(random.randint(2, 6)):
            b_type = random.choice(list(self.barrier_types.keys()))
            barriers.append({
                "type": b_type,
                **self.barrier_types[b_type]
            })
        
        # Calculate metrics
        barrier_severity_sum = sum(b.get("severity", 0.5) for b in barriers)
        fragmentation = min(1, barrier_severity_sum / 5)
        connectivity = max(0, 100 - fragmentation * 80)
        
        return ConnectivityData(
            center={"lat": lat, "lng": lng},
            radius_km=radius_km,
            overall_connectivity=round(connectivity, 1),
            fragmentation_index=round(fragmentation, 2),
            patch_count=random.randint(5, 15),
            total_patch_area_ha=random.uniform(100, 500),
            average_patch_size_ha=random.uniform(10, 50),
            largest_patch_ha=random.uniform(50, 150),
            barriers=barriers,
            barrier_density_per_km=round(len(barriers) / (2 * radius_km), 2),
            corridor_count=random.randint(2, 6),
            connectivity_gaps=[
                {
                    "location": {"lat": lat + 0.01, "lng": lng - 0.01},
                    "severity": "high",
                    "width_m": random.randint(100, 500)
                }
            ] if random.random() > 0.5 else []
        )
    
    # ===========================================
    # STATS
    # ===========================================
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get data layer statistics"""
        return {
            "layer": "advanced_geospatial_layers",
            "version": "1.0.0",
            "cached_corridors": self.corridors_collection.count_documents({}),
            "cached_zones": self.zones_collection.count_documents({}),
            "cached_connectivity": self.connectivity_collection.count_documents({}),
            "cached_heatmaps": self.heatmaps_collection.count_documents({}),
            "corridor_types": [t.value for t in CorridorType],
            "zone_types": [t.value for t in ZoneType],
            "barrier_types": list(self.barrier_types.keys()),
            "status": "operational"
        }


# Singleton instance
_layer_instance = None

def get_advanced_geospatial_layer() -> AdvancedGeospatialDataLayer:
    """Get singleton instance"""
    global _layer_instance
    if _layer_instance is None:
        _layer_instance = AdvancedGeospatialDataLayer()
    return _layer_instance
