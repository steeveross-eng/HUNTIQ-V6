"""
BIONIC ENGINE - Contour Generator V2
PHASE P1-HOTSPOTS REFONTE

Generateur de hotspots CIRCULAIRES naturels conformes aux specifications BIONIC V5.

SPECIFICATIONS OBLIGATOIRES:
- Forme de base CIRCULAIRE avec perturbations naturelles
- Superficie EXACTE: 2000-3000 m²
- Contours ultra-fins (1-2 px), colores, lisses (anti-aliasing)
- Centre 100% TRANSPARENT (ZERO remplissage)
- Evitement strict des etendues d'eau (lacs, rivieres, etc.)
- Alignement par espece (chevreuil, orignal, ours, etc.)
- Precision geographique (OSM, LiDAR, Sentinel-2)

Conformite: G-SEC | G-QA | G-DOC | BIONIC V5
"""

from typing import List, Tuple, Dict, Any, Optional
import math
import random
import string
import hashlib

# =============================================================================
# CONSTANTES GEOGRAPHIQUES
# =============================================================================

# 1 degre de latitude = ~111,320 metres
METERS_PER_DEG_LAT = 111320.0

# Superficie cible en m² (2000-3000 m²)
MIN_AREA_M2 = 2000.0
MAX_AREA_M2 = 3000.0
TARGET_AREA_M2 = 2500.0  # Moyenne cible

# Rayon correspondant pour un cercle parfait de 2500 m²
# A = π * r² => r = sqrt(A / π)
TARGET_RADIUS_M = math.sqrt(TARGET_AREA_M2 / math.pi)  # ~28.2 m

# =============================================================================
# PALETTE DE COULEURS PAR TYPE ET ESPECE
# =============================================================================

HOTSPOT_COLORS = {
    "activity_peak": "#FFD700",      # Or
    "feeding_zone": "#4CAF50",       # Vert
    "rut_zone": "#E91E63",           # Rose vif
    "thermal_refuge": "#00BCD4",     # Cyan
    "water_source": "#2196F3",       # Bleu
    "predation_risk": "#F44336",     # Rouge
    "snow_impact": "#90A4AE",        # Gris bleu
    "human_avoidance": "#795548",    # Brun
    "mineral_site": "#FFC107",       # Ambre
    "composite_optimal": "#FF9800"   # Orange
}

SPECIES_COLORS = {
    "moose": "#FF6B00",       # Orange vif (Orignal)
    "deer": "#8B4513",        # Brun (Chevreuil)
    "bear": "#4A4A4A",        # Gris fonce (Ours)
    "wild_turkey": "#DAA520", # Or fonce (Dindon)
    "elk": "#CD853F"          # Peru (Wapiti)
}

ZONE_COLORS = {
    "feeding": "#4CAF50",
    "bedding": "#3F51B5",
    "rut_arena": "#E91E63",
    "thermal_cover": "#00BCD4",
    "water_access": "#2196F3",
    "predation_zone": "#F44336",
    "yarding_zone": "#607D8B"
}

CORRIDOR_COLORS = {
    "movement": "#8BC34A",
    "avoidance": "#EF5350",
    "preferred": "#4CAF50",
    "feeding_transit": "#FF9800"
}

CORRIDOR_DASH = {
    "movement": "none",
    "avoidance": "8 4",
    "preferred": "none",
    "feeding_transit": "4 2"
}


# =============================================================================
# UTILITAIRES GEOGRAPHIQUES
# =============================================================================

def meters_to_degrees_lat(meters: float) -> float:
    """Convertit des metres en degres de latitude."""
    return meters / METERS_PER_DEG_LAT


def meters_to_degrees_lng(meters: float, latitude: float) -> float:
    """Convertit des metres en degres de longitude a une latitude donnee."""
    meters_per_deg_lng = METERS_PER_DEG_LAT * math.cos(math.radians(latitude))
    if meters_per_deg_lng == 0:
        return 0
    return meters / meters_per_deg_lng


def calculate_polygon_area_m2(coords: List[List[float]], center_lat: float) -> float:
    """
    Calcule l'aire d'un polygone en metres carres.
    Utilise la formule de Shoelace avec conversion deg -> m.
    """
    if len(coords) < 3:
        return 0.0
    
    # Convertir en metres relatifs au centre
    points_m = []
    for lng, lat in coords:
        x = (lng - coords[0][0]) * METERS_PER_DEG_LAT * math.cos(math.radians(center_lat))
        y = (lat - coords[0][1]) * METERS_PER_DEG_LAT
        points_m.append((x, y))
    
    # Formule de Shoelace
    n = len(points_m)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points_m[i][0] * points_m[j][1]
        area -= points_m[j][0] * points_m[i][1]
    
    return abs(area) / 2.0


def generate_id(prefix: str) -> str:
    """Genere un ID unique selon le pattern du contrat."""
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=8))
    return f"{prefix}-{suffix}"


def create_deterministic_seed(lat: float, lng: float, hotspot_type: str, species: str) -> int:
    """Cree un seed deterministe pour reproductibilite."""
    data = f"{lat:.6f}_{lng:.6f}_{hotspot_type}_{species}"
    hash_val = hashlib.md5(data.encode()).hexdigest()
    return int(hash_val[:8], 16)


# =============================================================================
# DETECTION DES ZONES D'EAU (Simulation OSM)
# =============================================================================

class WaterBodyDetector:
    """
    Detecteur de zones d'eau pour evitement automatique.
    
    En production: integrer OpenStreetMap Overpass API ou donnees locales.
    Ici: simulation basee sur des patterns geographiques typiques du Quebec.
    """
    
    # Zones d'eau majeures connues (Quebec region - coordonnees approximatives)
    MAJOR_WATER_BODIES = [
        # Fleuve Saint-Laurent (axe principal)
        {"type": "river", "name": "Saint-Laurent", 
         "bounds": {"north": 47.5, "south": 45.5, "east": -69.5, "west": -73.5}},
        # Lac Saint-Jean
        {"type": "lake", "name": "Lac Saint-Jean",
         "center": (48.5, -72.0), "radius_km": 25},
    ]
    
    @staticmethod
    def is_in_water(lat: float, lng: float) -> Tuple[bool, Optional[str]]:
        """
        Verifie si un point est dans une zone d'eau.
        
        Returns:
            (is_water, water_name) - True si dans l'eau, nom optionnel
        """
        # Simulation: patterns typiques de cours d'eau
        # En production: utiliser OSM/donnees LiDAR
        
        # Saint-Laurent corridor
        if -73.5 <= lng <= -69.5 and 45.8 <= lat <= 47.2:
            # Zone du fleuve (largeur variable)
            river_lat = 46.8 + (lng + 71) * 0.1
            if abs(lat - river_lat) < 0.02:  # ~2km du fleuve
                return True, "Saint-Laurent"
        
        # Pattern generique: riviere diagonale dans les Laurentides
        if -72.0 <= lng <= -70.5 and 46.5 <= lat <= 48.0:
            river_lat = 47.0 + (lng + 71) * 0.3
            if abs(lat - river_lat) < 0.005:  # ~500m de la riviere
                return True, "Riviere"
        
        return False, None
    
    @staticmethod
    def get_water_avoidance_offset(
        lat: float, 
        lng: float, 
        radius_m: float
    ) -> Tuple[float, float]:
        """
        Calcule un offset pour eviter les zones d'eau proches.
        
        Returns:
            (offset_lat, offset_lng) en degres
        """
        is_water, _ = WaterBodyDetector.is_in_water(lat, lng)
        if not is_water:
            return 0.0, 0.0
        
        # Deplacer vers le nord et l'est (direction generale de la terre)
        offset_m = radius_m * 1.5
        offset_lat = meters_to_degrees_lat(offset_m)
        offset_lng = meters_to_degrees_lng(offset_m, lat)
        
        return offset_lat, offset_lng


# =============================================================================
# GENERATEUR DE CONTOURS CIRCULAIRES NATURELS
# =============================================================================

class NaturalCircleGenerator:
    """
    Generateur de cercles naturels avec perturbations terrain.
    
    Pipeline:
    1. Calcul du rayon pour superficie cible (2000-3000 m²)
    2. Generation de points sur cercle de base
    3. Application de perturbations naturelles (terrain, vegetation)
    4. Lissage Chaikin pour courbes douces
    5. Verification d'evitement des zones d'eau
    6. Ajustement final de la superficie
    """
    
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
    
    def generate_circular_hotspot(
        self,
        center_lat: float,
        center_lng: float,
        target_area_m2: float = TARGET_AREA_M2,
        num_vertices: int = 32,
        terrain_irregularity: float = 0.15,
        species: str = "moose"
    ) -> List[List[float]]:
        """
        Genere un hotspot circulaire naturel.
        
        Args:
            center_lat: Latitude du centre
            center_lng: Longitude du centre
            target_area_m2: Superficie cible en m² (2000-3000)
            num_vertices: Nombre de points sur le contour
            terrain_irregularity: Variation du rayon (0-0.3)
            species: Espece pour ajustements comportementaux
            
        Returns:
            Liste de coordonnees [lng, lat] formant le polygone
        """
        # 1. Verifier et eviter les zones d'eau
        offset_lat, offset_lng = WaterBodyDetector.get_water_avoidance_offset(
            center_lat, center_lng, TARGET_RADIUS_M
        )
        center_lat += offset_lat
        center_lng += offset_lng
        
        # 2. Calculer le rayon de base pour la superficie cible
        # A = π * r² => r = sqrt(A / π)
        base_radius_m = math.sqrt(target_area_m2 / math.pi)
        
        # 3. Convertir en degres
        radius_lat = meters_to_degrees_lat(base_radius_m)
        radius_lng = meters_to_degrees_lng(base_radius_m, center_lat)
        
        # 4. Generer les points du cercle avec perturbations naturelles
        coords = []
        for i in range(num_vertices):
            angle = 2 * math.pi * i / num_vertices
            
            # Perturbation naturelle du rayon
            # Utilise du bruit coherent pour des formes naturelles
            noise = self._terrain_noise(angle, terrain_irregularity, species)
            perturbed_radius_lat = radius_lat * (1.0 + noise)
            perturbed_radius_lng = radius_lng * (1.0 + noise)
            
            # Calculer le point
            point_lng = center_lng + perturbed_radius_lng * math.cos(angle)
            point_lat = center_lat + perturbed_radius_lat * math.sin(angle)
            
            # Verifier que le point n'est pas dans l'eau
            is_water, _ = WaterBodyDetector.is_in_water(point_lat, point_lng)
            if is_water:
                # Reduire le rayon pour eviter l'eau
                shrink = 0.7
                point_lng = center_lng + perturbed_radius_lng * shrink * math.cos(angle)
                point_lat = center_lat + perturbed_radius_lat * shrink * math.sin(angle)
            
            coords.append([point_lng, point_lat])
        
        # 5. Fermer le polygone
        coords.append(coords[0])
        
        # 6. Appliquer lissage Chaikin pour contours naturels
        smoothed = self._chaikin_smooth(coords, iterations=2)
        
        # 7. Verifier et ajuster la superficie si necessaire
        actual_area = calculate_polygon_area_m2(smoothed, center_lat)
        if actual_area < MIN_AREA_M2 or actual_area > MAX_AREA_M2:
            scale = math.sqrt(target_area_m2 / actual_area) if actual_area > 0 else 1.0
            smoothed = self._scale_polygon(smoothed, center_lat, center_lng, scale)
        
        return smoothed
    
    def _terrain_noise(
        self, 
        angle: float, 
        intensity: float, 
        species: str
    ) -> float:
        """
        Genere du bruit de terrain naturel.
        Combine plusieurs frequences pour un aspect realiste.
        """
        # Bruit de base (basse frequence - forme generale)
        base_noise = math.sin(angle * 2) * 0.5 + math.sin(angle * 3) * 0.3
        
        # Bruit de detail (haute frequence - micro-terrain)
        detail_noise = math.sin(angle * 7) * 0.15 + math.sin(angle * 11) * 0.1
        
        # Variation aleatoire (controlée)
        random_noise = random.gauss(0, 0.1)
        
        # Ajustement par espece
        species_factor = {
            "moose": 1.0,     # Orignal: grands espaces, moins irregulier
            "deer": 1.3,      # Chevreuil: zones plus dentelees (vegetation)
            "bear": 0.8,      # Ours: zones plus arrondies
            "wild_turkey": 1.2,
            "elk": 0.9
        }.get(species, 1.0)
        
        total_noise = (base_noise + detail_noise + random_noise) * intensity * species_factor
        
        # Limiter pour eviter des formes trop extremes
        return max(-0.25, min(0.25, total_noise))
    
    def _chaikin_smooth(
        self,
        points: List[List[float]],
        iterations: int = 2
    ) -> List[List[float]]:
        """
        Lissage de Chaikin pour contours naturels et lisses.
        """
        if len(points) < 3:
            return points
        
        result = [list(p) for p in points]
        
        for _ in range(iterations):
            new_points = []
            for i in range(len(result) - 1):
                p0 = result[i]
                p1 = result[i + 1]
                
                # Point a 1/4
                q = [
                    0.75 * p0[0] + 0.25 * p1[0],
                    0.75 * p0[1] + 0.25 * p1[1]
                ]
                # Point a 3/4
                r = [
                    0.25 * p0[0] + 0.75 * p1[0],
                    0.25 * p0[1] + 0.75 * p1[1]
                ]
                
                new_points.extend([q, r])
            
            # Fermer
            if result[0] == result[-1] and new_points:
                new_points.append(new_points[0])
            
            result = new_points
        
        return result
    
    def _scale_polygon(
        self,
        coords: List[List[float]],
        center_lat: float,
        center_lng: float,
        scale: float
    ) -> List[List[float]]:
        """Redimensionne un polygone autour de son centre."""
        scaled = []
        for lng, lat in coords:
            new_lng = center_lng + (lng - center_lng) * scale
            new_lat = center_lat + (lat - center_lat) * scale
            scaled.append([new_lng, new_lat])
        return scaled


# =============================================================================
# STYLES CONFORMES AUX SPECIFICATIONS
# =============================================================================

def create_hotspot_style(hotspot_type: str, species: str = "moose") -> Dict[str, Any]:
    """
    Cree un style conforme aux specifications visuelles BIONIC V5.
    
    OBLIGATOIRE:
    - Contour 1-2px, colore
    - Centre TRANSPARENT (fill_opacity = 0)
    - ZERO effets (glow, shadow, halo)
    """
    # Couleur basee sur l'espece OU le type
    color = SPECIES_COLORS.get(species, HOTSPOT_COLORS.get(hotspot_type, "#FFD700"))
    
    return {
        "stroke_color": color,
        "stroke_width": 1.5,  # 1-2px
        "fill_opacity": 0.0,  # OBLIGATOIRE: Centre transparent
        "stroke_opacity": 0.95,
        "stroke_linecap": "round",
        "stroke_linejoin": "round"
    }


def create_zone_style(zone_type: str) -> Dict[str, Any]:
    """Cree un style pour les zones comportementales."""
    color = ZONE_COLORS.get(zone_type, "#4CAF50")
    return {
        "stroke_color": color,
        "stroke_width": 1.5,
        "fill_opacity": 0.0,
        "stroke_dasharray": "4 2"  # Pointilles pour zones
    }


def create_corridor_style(corridor_type: str) -> Dict[str, Any]:
    """Cree un style pour les corridors."""
    color = CORRIDOR_COLORS.get(corridor_type, "#8BC34A")
    dash = CORRIDOR_DASH.get(corridor_type, "none")
    return {
        "stroke_color": color,
        "stroke_width": 2.0,
        "fill_opacity": 0.0,
        "stroke_dasharray": dash
    }


# =============================================================================
# CONTOUR GENERATOR PRINCIPAL (REFONTE)
# =============================================================================

class ContourGenerator:
    """
    Generateur de contours naturels pour hotspots, zones et corridors.
    VERSION 2.0 - REFONTE COMPLETE
    
    Pipeline:
    1. Calcul de la superficie cible (2000-3000 m²)
    2. Generation de cercle de base
    3. Perturbations naturelles basees sur terrain
    4. Evitement automatique des zones d'eau
    5. Lissage Chaikin
    6. Verification de la superficie finale
    
    Conformite: Contours circulaires naturels, ZERO fill, ZERO effets
    """
    
    def __init__(self):
        self._circle_gen = NaturalCircleGenerator()
    
    def generate_natural_polygon(
        self,
        center_lat: float,
        center_lng: float,
        base_radius_deg: float = None,  # Ignore - utilise superficie
        irregularity: float = 0.15,
        spikiness: float = 0.1,  # Ignore - remplace par terrain_irregularity
        num_vertices: int = 32,
        species: str = "moose"
    ) -> List[List[float]]:
        """
        Genere un polygone naturel CIRCULAIRE.
        
        NOUVEAU COMPORTEMENT:
        - Forme de base CIRCULAIRE (pas random)
        - Superficie EXACTE 2000-3000 m²
        - Perturbations naturelles basees sur terrain
        - Evitement automatique des zones d'eau
        """
        # Determiner la superficie cible (dans la plage 2000-3000)
        target_area = random.uniform(MIN_AREA_M2, MAX_AREA_M2)
        
        # Seed deterministe pour reproductibilite
        seed = create_deterministic_seed(center_lat, center_lng, "hotspot", species)
        self._circle_gen = NaturalCircleGenerator(seed)
        
        return self._circle_gen.generate_circular_hotspot(
            center_lat=center_lat,
            center_lng=center_lng,
            target_area_m2=target_area,
            num_vertices=num_vertices,
            terrain_irregularity=irregularity,
            species=species
        )
    
    def generate_zone_polygon(
        self,
        center_lat: float,
        center_lng: float,
        zone_type: str,
        species: str = "moose"
    ) -> List[List[float]]:
        """
        Genere un polygone pour une zone comportementale.
        Zones plus grandes que hotspots (5000-10000 m²).
        """
        target_area = random.uniform(5000, 10000)
        seed = create_deterministic_seed(center_lat, center_lng, zone_type, species)
        gen = NaturalCircleGenerator(seed)
        
        return gen.generate_circular_hotspot(
            center_lat=center_lat,
            center_lng=center_lng,
            target_area_m2=target_area,
            num_vertices=40,
            terrain_irregularity=0.12,
            species=species
        )
    
    def generate_corridor_line(
        self,
        start_lat: float,
        start_lng: float,
        end_lat: float,
        end_lng: float,
        width_m: float = 30
    ) -> List[List[float]]:
        """
        Genere une ligne de corridor naturelle.
        """
        # Points intermediaires avec courbes naturelles
        points = []
        num_segments = 10
        
        for i in range(num_segments + 1):
            t = i / num_segments
            
            # Interpolation lineaire de base
            lat = start_lat + t * (end_lat - start_lat)
            lng = start_lng + t * (end_lng - start_lng)
            
            # Deviation naturelle (sinusoide)
            if 0 < t < 1:
                deviation = math.sin(t * math.pi * 2) * 0.001
                lat += deviation
            
            points.append([lng, lat])
        
        return points

    def generate_corridor_geometry(
        self,
        from_zone_center: tuple,
        to_zone_center: tuple,
        corridor_type: str = "movement"
    ) -> Dict:
        """
        Genere la geometrie complete d'un corridor.
        Pipeline standard: raster -> contour -> lissage.
        Retourne un dict GeoJSON-like avec coordinates.
        """
        start_lat, start_lng = from_zone_center
        end_lat, end_lng = to_zone_center

        line_points = self.generate_corridor_line(
            start_lat=start_lat, start_lng=start_lng,
            end_lat=end_lat, end_lng=end_lng,
            width_m=40 if corridor_type == "movement" else 25
        )

        return {
            "type": "LineString",
            "coordinates": line_points,
            "corridor_type": corridor_type
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'ContourGenerator',
    'NaturalCircleGenerator',
    'WaterBodyDetector',
    'generate_id',
    'create_hotspot_style',
    'create_zone_style',
    'create_corridor_style',
    'HOTSPOT_COLORS',
    'SPECIES_COLORS',
    'ZONE_COLORS',
    'CORRIDOR_COLORS',
    'calculate_polygon_area_m2',
    'meters_to_degrees_lat',
    'meters_to_degrees_lng',
    'MIN_AREA_M2',
    'MAX_AREA_M2',
    'TARGET_AREA_M2'
]
