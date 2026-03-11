"""Geospatial Engine Service - CORE

Business logic for geospatial hunting analysis.

Version: 1.0.0
"""

from typing import List, Dict, Any
import math
from .models import Coordinates, TerrainAnalysis


class GeospatialService:
    """Service for geospatial hunting analysis"""
    
    # Quebec hunting regions
    QUEBEC_REGIONS = {
        "01": "Bas-Saint-Laurent",
        "02": "Saguenay–Lac-Saint-Jean",
        "03": "Capitale-Nationale",
        "04": "Mauricie",
        "05": "Estrie",
        "06": "Montréal",
        "07": "Outaouais",
        "08": "Abitibi-Témiscamingue",
        "09": "Côte-Nord",
        "10": "Nord-du-Québec",
        "11": "Gaspésie–Îles-de-la-Madeleine",
        "12": "Chaudière-Appalaches",
        "13": "Laval",
        "14": "Lanaudière",
        "15": "Laurentides",
        "16": "Montérégie",
        "17": "Centre-du-Québec"
    }
    
    def calculate_distance(self, point1: Coordinates, point2: Coordinates) -> float:
        """
        Calculate distance between two points using Haversine formula.
        Returns distance in kilometers.
        """
        R = 6371  # Earth's radius in km
        
        lat1 = math.radians(point1.latitude)
        lat2 = math.radians(point2.latitude)
        dlat = math.radians(point2.latitude - point1.latitude)
        dlon = math.radians(point2.longitude - point1.longitude)
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return round(R * c, 2)
    
    def get_bearing(self, point1: Coordinates, point2: Coordinates) -> float:
        """Calculate bearing from point1 to point2 in degrees"""
        lat1 = math.radians(point1.latitude)
        lat2 = math.radians(point2.latitude)
        dlon = math.radians(point2.longitude - point1.longitude)
        
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        bearing = math.degrees(math.atan2(x, y))
        return round((bearing + 360) % 360, 1)
    
    def bearing_to_direction(self, bearing: float) -> str:
        """Convert bearing to cardinal direction"""
        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        index = int((bearing + 22.5) / 45) % 8
        return directions[index]
    
    def analyze_terrain(self, coordinates: Coordinates) -> TerrainAnalysis:
        """
        Analyze terrain at given coordinates.
        Note: This is a simplified implementation. 
        Full implementation would use elevation APIs and satellite data.
        """
        # Simulated analysis based on Quebec typical terrain
        # In production, this would use real elevation data
        base_elevation = 200 + (coordinates.latitude - 45) * 50
        
        return TerrainAnalysis(
            elevation=round(base_elevation, 1),
            slope=round(abs(math.sin(coordinates.longitude)) * 15, 1),
            aspect=self.bearing_to_direction((coordinates.longitude * 10) % 360),
            vegetation_type="Forêt mixte" if coordinates.latitude > 47 else "Forêt feuillue",
            water_proximity=round(abs(math.cos(coordinates.latitude)) * 500, 0),
            road_proximity=round(abs(math.sin(coordinates.longitude)) * 2000, 0),
            hunting_score=round(7 + math.sin(coordinates.latitude) * 2, 1)
        )
    
    def calculate_hunting_score(self, terrain: TerrainAnalysis) -> float:
        """
        Calculate hunting potential score for terrain.
        
        Factors:
        - Slope (gentle slopes are better)
        - Water proximity (closer is better)
        - Road distance (further is better for game)
        - Vegetation type
        """
        score = 5.0
        
        # Slope factor (0-20% is ideal)
        if terrain.slope <= 10:
            score += 2
        elif terrain.slope <= 20:
            score += 1
        else:
            score -= 1
        
        # Water proximity (within 500m is ideal)
        if terrain.water_proximity <= 200:
            score += 2
        elif terrain.water_proximity <= 500:
            score += 1
        
        # Road distance (>1km is better)
        if terrain.road_proximity > 2000:
            score += 1.5
        elif terrain.road_proximity > 1000:
            score += 1
        elif terrain.road_proximity < 300:
            score -= 1
        
        return round(min(10, max(0, score)), 1)
    
    def get_region_info(self, region_code: str) -> Dict[str, Any]:
        """Get information about a Quebec hunting region"""
        name = self.QUEBEC_REGIONS.get(region_code, "Région inconnue")
        
        # Simplified species availability by region
        species_by_region = {
            "01": ["deer", "moose", "bear"],
            "02": ["moose", "bear", "caribou"],
            "03": ["deer", "moose", "turkey"],
            "04": ["deer", "moose", "bear"],
            "05": ["deer", "turkey"],
            "07": ["deer", "moose", "bear", "turkey"],
            "08": ["moose", "bear"],
            "09": ["moose", "bear", "caribou"],
            "10": ["caribou", "moose"],
            "11": ["moose", "deer"],
            "14": ["deer", "moose", "bear"],
            "15": ["deer", "moose", "bear"],
        }
        
        return {
            "code": region_code,
            "name": name,
            "species": species_by_region.get(region_code, ["deer", "moose"]),
            "zone_types": ["zec", "pourvoirie", "public"]
        }
    
    def find_nearby_zones(self, coordinates: Coordinates, radius_km: float = 50) -> List[Dict[str, Any]]:
        """
        Find hunting zones near coordinates.
        Note: Simplified implementation. Would use real zone database in production.
        """
        # Simulated nearby zones
        zones = [
            {
                "id": "zec-001",
                "name": "ZEC Batiscan-Neilson",
                "type": "zec",
                "distance_km": 12.5,
                "species": ["deer", "moose", "bear"]
            },
            {
                "id": "pourv-001", 
                "name": "Pourvoirie du Lac Croche",
                "type": "pourvoirie",
                "distance_km": 28.3,
                "species": ["moose", "bear"]
            },
            {
                "id": "public-001",
                "name": "Terres publiques - Secteur Nord",
                "type": "public",
                "distance_km": 45.0,
                "species": ["deer", "moose"]
            }
        ]
        
        return [z for z in zones if z["distance_km"] <= radius_km]
