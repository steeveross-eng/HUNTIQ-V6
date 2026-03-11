"""Ecoforestry Data Layers - PHASE 5
Data provider for ecoforestry information (SIEF, MFFP, forest inventory).

Version: 1.0.0
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pymongo import MongoClient
from pydantic import BaseModel, Field
import uuid


# ==============================================
# MODELS
# ==============================================

class ForestStandData(BaseModel):
    """Raw forest stand data from SIEF"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Location
    geom_id: str  # SIEF geometry ID
    coordinates: Dict[str, float]
    bbox: Optional[Dict[str, float]] = None
    
    # SIEF attributes
    type_couv: str  # Type de couverture (F, E, etc.)
    gr_ess: str  # Groupe d'essences
    cl_age: Optional[str] = None  # Classe d'âge
    cl_dens: Optional[str] = None  # Classe de densité
    cl_haut: Optional[str] = None  # Classe de hauteur
    
    # Composition
    essence_1: Optional[str] = None
    essence_2: Optional[str] = None
    essence_3: Optional[str] = None
    pct_essence_1: Optional[int] = None
    pct_essence_2: Optional[int] = None
    pct_essence_3: Optional[int] = None
    
    # Metadata
    source: str = "SIEF"
    vintage: Optional[str] = None  # Year of data
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ForestCutData(BaseModel):
    """Forest cut/harvest data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Location
    coordinates: Dict[str, float]
    area_ha: float
    
    # Cut info
    year: int
    treatment_type: str  # CPRS, CPE, EPC, etc.
    treatment_desc: Optional[str] = None
    
    # Regeneration
    regen_year: Optional[int] = None
    regen_type: Optional[str] = None
    
    # Source
    source: str = "MFFP"
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HabitatSuitabilityData(BaseModel):
    """Habitat suitability index data"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Location
    coordinates: Dict[str, float]
    cell_size_m: int = 100
    
    # Species-specific indices
    species: str
    hsi_food: float = Field(ge=0, le=1, default=0.5)
    hsi_cover: float = Field(ge=0, le=1, default=0.5)
    hsi_water: float = Field(ge=0, le=1, default=0.5)
    hsi_overall: float = Field(ge=0, le=1, default=0.5)
    
    # Metadata
    model_version: str = "1.0"
    computed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==============================================
# DATA LAYER SERVICE
# ==============================================

class EcoforestryDataLayer:
    """Data layer for ecoforestry information"""
    
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'test_database')
        self._client = None
        self._db = None
        
        # SIEF forest type mappings
        self.forest_types = {
            "F": "Forêt",
            "FH": "Forêt humide",
            "A": "Arbustaie",
            "E": "Eau",
            "AL": "Aulnaie",
            "DS": "Dénudé sec",
            "DH": "Dénudé humide"
        }
        
        # Species group mappings
        self.species_groups = {
            "R": "Résineux",
            "F": "Feuillus",
            "M": "Mixte",
            "FI": "Feuillus intolérants",
            "FT": "Feuillus tolérants",
            "RR": "Résineux à régénération rapide"
        }
        
        # Quebec tree species codes
        self.tree_species = {
            "EPN": "Épinette noire",
            "EPB": "Épinette blanche",
            "EPR": "Épinette rouge",
            "SAB": "Sapin baumier",
            "PIG": "Pin gris",
            "PIB": "Pin blanc",
            "PIR": "Pin rouge",
            "THO": "Thuya occidental",
            "MEL": "Mélèze",
            "BOP": "Bouleau à papier",
            "BOJ": "Bouleau jaune",
            "ERS": "Érable à sucre",
            "ERR": "Érable rouge",
            "PET": "Peuplier faux-tremble",
            "PEB": "Peuplier baumier",
            "CHR": "Chêne rouge",
            "HEG": "Hêtre à grandes feuilles",
            "FRN": "Frêne noir",
            "TIL": "Tilleul d'Amérique"
        }
    
    @property
    def db(self):
        if self._db is None:
            self._client = MongoClient(self.mongo_url)
            self._db = self._client[self.db_name]
        return self._db
    
    @property
    def stands_collection(self):
        return self.db.ecoforestry_stands
    
    @property
    def cuts_collection(self):
        return self.db.ecoforestry_cuts
    
    @property
    def hsi_collection(self):
        return self.db.habitat_suitability
    
    # ===========================================
    # FOREST STANDS
    # ===========================================
    
    async def get_stands_in_bbox(
        self,
        north: float,
        south: float,
        east: float,
        west: float
    ) -> List[ForestStandData]:
        """Get forest stands within bounding box"""
        # Query cached data or generate placeholder
        stands = list(self.stands_collection.find({
            "coordinates.lat": {"$gte": south, "$lte": north},
            "coordinates.lng": {"$gte": west, "$lte": east}
        }, {"_id": 0}))
        
        if stands:
            return [ForestStandData(**s) for s in stands]
        
        # Generate placeholder data for demo
        return self._generate_placeholder_stands(north, south, east, west)
    
    async def get_stands_at_point(
        self,
        lat: float,
        lng: float,
        radius_km: float = 1.0
    ) -> List[ForestStandData]:
        """Get forest stands around a point"""
        # Convert radius to approximate degrees
        lat_delta = radius_km / 111.0
        lng_delta = radius_km / (111.0 * abs(cos(radians(lat))))
        
        return await self.get_stands_in_bbox(
            lat + lat_delta, lat - lat_delta,
            lng + lng_delta, lng - lng_delta
        )
    
    async def get_stand_by_id(self, stand_id: str) -> Optional[ForestStandData]:
        """Get specific forest stand"""
        stand = self.stands_collection.find_one({"id": stand_id}, {"_id": 0})
        if stand:
            return ForestStandData(**stand)
        return None
    
    # ===========================================
    # FOREST CUTS
    # ===========================================
    
    async def get_cuts_in_area(
        self,
        lat: float,
        lng: float,
        radius_km: float = 5.0,
        years_back: int = 10
    ) -> List[ForestCutData]:
        """Get forest cuts in area"""
        current_year = datetime.now().year
        min_year = current_year - years_back
        
        cuts = list(self.cuts_collection.find({
            "year": {"$gte": min_year}
        }, {"_id": 0}).limit(50))
        
        if cuts:
            return [ForestCutData(**c) for c in cuts]
        
        # Generate placeholder
        return self._generate_placeholder_cuts(lat, lng, min_year, current_year)
    
    async def get_cuts_by_year(self, year: int) -> List[ForestCutData]:
        """Get all cuts for a specific year"""
        cuts = list(self.cuts_collection.find(
            {"year": year}, {"_id": 0}
        ))
        return [ForestCutData(**c) for c in cuts]
    
    # ===========================================
    # HABITAT SUITABILITY
    # ===========================================
    
    async def get_hsi_data(
        self,
        species: str,
        lat: float,
        lng: float,
        radius_km: float = 2.0
    ) -> List[HabitatSuitabilityData]:
        """Get habitat suitability index data"""
        hsi_data = list(self.hsi_collection.find({
            "species": species.lower()
        }, {"_id": 0}).limit(100))
        
        if hsi_data:
            return [HabitatSuitabilityData(**h) for h in hsi_data]
        
        # Generate placeholder
        return self._generate_placeholder_hsi(species, lat, lng, radius_km)
    
    async def compute_hsi(
        self,
        species: str,
        lat: float,
        lng: float
    ) -> HabitatSuitabilityData:
        """Compute HSI for a specific location"""
        # Placeholder computation based on species preferences
        species_prefs = {
            "deer": {"food": 0.8, "cover": 0.7, "water": 0.6},
            "moose": {"food": 0.7, "cover": 0.75, "water": 0.9},
            "bear": {"food": 0.85, "cover": 0.6, "water": 0.7}
        }
        
        prefs = species_prefs.get(species.lower(), {"food": 0.6, "cover": 0.6, "water": 0.6})
        
        # Simulate variation based on location
        import math
        variation = (math.sin(lat * 10) + math.cos(lng * 10)) * 0.1
        
        hsi_food = min(1, max(0, prefs["food"] + variation))
        hsi_cover = min(1, max(0, prefs["cover"] - variation * 0.5))
        hsi_water = min(1, max(0, prefs["water"] + variation * 0.3))
        hsi_overall = (hsi_food * 0.4 + hsi_cover * 0.35 + hsi_water * 0.25)
        
        return HabitatSuitabilityData(
            coordinates={"lat": lat, "lng": lng},
            species=species.lower(),
            hsi_food=round(hsi_food, 3),
            hsi_cover=round(hsi_cover, 3),
            hsi_water=round(hsi_water, 3),
            hsi_overall=round(hsi_overall, 3)
        )
    
    # ===========================================
    # REFERENCE DATA
    # ===========================================
    
    def get_forest_type_name(self, code: str) -> str:
        """Get forest type name from code"""
        return self.forest_types.get(code, code)
    
    def get_species_group_name(self, code: str) -> str:
        """Get species group name from code"""
        return self.species_groups.get(code, code)
    
    def get_tree_species_name(self, code: str) -> str:
        """Get tree species name from code"""
        return self.tree_species.get(code, code)
    
    def get_all_tree_species(self) -> Dict[str, str]:
        """Get all tree species mappings"""
        return self.tree_species.copy()
    
    # ===========================================
    # PLACEHOLDER GENERATORS
    # ===========================================
    
    def _generate_placeholder_stands(
        self,
        north: float,
        south: float,
        east: float,
        west: float
    ) -> List[ForestStandData]:
        """Generate placeholder forest stand data"""
        import random
        
        stands = []
        num_stands = min(20, int((north - south) * (east - west) * 1000))
        
        essences = list(self.tree_species.keys())
        groups = list(self.species_groups.keys())
        
        for i in range(num_stands):
            lat = south + random.random() * (north - south)
            lng = west + random.random() * (east - west)
            
            stands.append(ForestStandData(
                geom_id=f"SIEF_{i}_{int(lat*100)}_{int(lng*100)}",
                coordinates={"lat": lat, "lng": lng},
                type_couv="F",
                gr_ess=random.choice(groups),
                cl_age=random.choice(["10", "30", "50", "70", "90", "120"]),
                cl_dens=random.choice(["A", "B", "C", "D"]),
                cl_haut=str(random.randint(5, 25)),
                essence_1=random.choice(essences),
                essence_2=random.choice(essences),
                pct_essence_1=random.randint(40, 80),
                pct_essence_2=random.randint(10, 40),
                vintage="2023"
            ))
        
        return stands
    
    def _generate_placeholder_cuts(
        self,
        lat: float,
        lng: float,
        min_year: int,
        max_year: int
    ) -> List[ForestCutData]:
        """Generate placeholder cut data"""
        import random
        
        cuts = []
        treatments = ["CPRS", "CPE", "EPC", "EC", "CJ", "ES"]
        
        for i in range(random.randint(3, 8)):
            cut_lat = lat + (random.random() - 0.5) * 0.1
            cut_lng = lng + (random.random() - 0.5) * 0.1
            year = random.randint(min_year, max_year)
            
            cuts.append(ForestCutData(
                coordinates={"lat": cut_lat, "lng": cut_lng},
                area_ha=random.uniform(5, 50),
                year=year,
                treatment_type=random.choice(treatments),
                regen_year=year + random.randint(1, 3) if random.random() > 0.3 else None
            ))
        
        return cuts
    
    def _generate_placeholder_hsi(
        self,
        species: str,
        lat: float,
        lng: float,
        radius_km: float
    ) -> List[HabitatSuitabilityData]:
        """Generate placeholder HSI data grid"""
        import random
        
        hsi_data = []
        cell_size_deg = 0.01  # ~1km
        
        num_cells = int(radius_km * 2 / 1.0)
        
        for i in range(num_cells):
            for j in range(num_cells):
                cell_lat = lat - radius_km/111 + (i * cell_size_deg)
                cell_lng = lng - radius_km/111 + (j * cell_size_deg)
                
                hsi_data.append(HabitatSuitabilityData(
                    coordinates={"lat": cell_lat, "lng": cell_lng},
                    species=species.lower(),
                    hsi_food=round(random.uniform(0.3, 0.9), 3),
                    hsi_cover=round(random.uniform(0.3, 0.9), 3),
                    hsi_water=round(random.uniform(0.2, 0.8), 3),
                    hsi_overall=round(random.uniform(0.4, 0.8), 3)
                ))
        
        return hsi_data
    
    # ===========================================
    # STATS
    # ===========================================
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get data layer statistics"""
        return {
            "layer": "ecoforestry_layers",
            "version": "1.0.0",
            "cached_stands": self.stands_collection.count_documents({}),
            "cached_cuts": self.cuts_collection.count_documents({}),
            "cached_hsi": self.hsi_collection.count_documents({}),
            "tree_species_count": len(self.tree_species),
            "data_sources": ["SIEF", "MFFP", "MRNF"],
            "status": "operational"
        }


# Import math functions
from math import cos, radians


# Singleton instance
_layer_instance = None

def get_ecoforestry_layer() -> EcoforestryDataLayer:
    """Get singleton instance of ecoforestry data layer"""
    global _layer_instance
    if _layer_instance is None:
        _layer_instance = EcoforestryDataLayer()
    return _layer_instance
