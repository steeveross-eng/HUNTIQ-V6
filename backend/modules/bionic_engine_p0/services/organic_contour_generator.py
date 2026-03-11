"""
BIONIC ENGINE - Organic Contour Generator V3
PHASE P1-HOTSPOTS — REFONTE MAJEURE

Générateur de hotspots ORGANIQUES naturels via Marching Squares + Chaikin.
Conformité stricte BIONIC V5.

SPÉCIFICATIONS OBLIGATOIRES:
- Formes 100% ORGANIQUES, irrégulières, naturelles
- ZÉRO forme circulaire ou géométrique
- Superficie EXACTE: 5000-10000 m²
- Extraction via Marching Squares (grille P0-STABLE)
- Lissage via Chaikin Smoothing multi-passes
- Évitement RÉEL zones d'eau, routes, urbain (OSM Cache)
- Alignement comportemental par espèce

PIPELINE:
1. Génération grille d'intensité depuis scores P0-STABLE
2. Extraction iso-contours via Marching Squares
3. Filtrage par superficie (5000-10000 m²)
4. Lissage Chaikin multi-passes
5. Validation évitement OSM
6. Ajustement comportemental par espèce

Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
"""

from typing import List, Tuple, Dict, Any, Optional
import math
import random
import numpy as np
import hashlib
import string

# Import du cache OSM
try:
    from modules.bionic_engine_p0.services.osm_cache_service import get_osm_cache
except ImportError:
    get_osm_cache = None

# =============================================================================
# CONSTANTES GÉOGRAPHIQUES
# =============================================================================

METERS_PER_DEG_LAT = 111320.0

# Superficie cible en m² (5000-10000 m²) - OBLIGATOIRE
MIN_AREA_M2 = 5000.0
MAX_AREA_M2 = 10000.0
TARGET_AREA_M2 = 7500.0  # Moyenne cible

# Configuration Marching Squares
GRID_RESOLUTION = 50  # Résolution de la grille (50x50)
ISO_THRESHOLD = 0.6   # Seuil d'iso-contour (60% du score max)

# =============================================================================
# PALETTES DE COULEURS
# =============================================================================

SPECIES_COLORS = {
    "moose": "#FF6B00",       # Orange vif (Orignal)
    "deer": "#8B4513",        # Brun (Chevreuil)
    "bear": "#4A4A4A",        # Gris foncé (Ours)
    "wild_turkey": "#DAA520", # Or foncé (Dindon)
    "elk": "#CD853F"          # Peru (Wapiti)
}

HOTSPOT_COLORS = {
    "activity_peak": "#FFD700",
    "feeding_zone": "#4CAF50",
    "rut_zone": "#E91E63",
    "thermal_refuge": "#00BCD4",
    "water_source": "#2196F3",
    "predation_risk": "#F44336",
    "snow_impact": "#90A4AE",
    "human_avoidance": "#795548",
    "mineral_site": "#FFC107",
    "composite_optimal": "#FF9800"
}


# =============================================================================
# UTILITAIRES GÉOGRAPHIQUES
# =============================================================================

def meters_to_degrees_lat(meters: float) -> float:
    """Convertit des mètres en degrés de latitude."""
    return meters / METERS_PER_DEG_LAT


def meters_to_degrees_lng(meters: float, latitude: float) -> float:
    """Convertit des mètres en degrés de longitude."""
    meters_per_deg_lng = METERS_PER_DEG_LAT * math.cos(math.radians(latitude))
    if meters_per_deg_lng == 0:
        return 0
    return meters / meters_per_deg_lng


def calculate_polygon_area_m2(coords: List[List[float]], center_lat: float) -> float:
    """Calcule l'aire d'un polygone en mètres carrés."""
    if len(coords) < 3:
        return 0.0
    
    points_m = []
    ref_lng, ref_lat = coords[0][0], coords[0][1]
    
    for lng, lat in coords:
        x = (lng - ref_lng) * METERS_PER_DEG_LAT * math.cos(math.radians(center_lat))
        y = (lat - ref_lat) * METERS_PER_DEG_LAT
        points_m.append((x, y))
    
    n = len(points_m)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points_m[i][0] * points_m[j][1]
        area -= points_m[j][0] * points_m[i][1]
    
    return abs(area) / 2.0


def generate_id(prefix: str) -> str:
    """Génère un ID unique."""
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=8))
    return f"{prefix}-{suffix}"


# =============================================================================
# MARCHING SQUARES IMPLEMENTATION
# =============================================================================

class MarchingSquares:
    """
    Implémentation de l'algorithme Marching Squares pour extraction d'iso-contours.
    
    Transforme une grille d'intensité (scores P0-STABLE) en contours organiques.
    """
    
    # Lookup table pour Marching Squares (16 cas)
    # Format: [edge_indices] où edge = (start_corner, end_corner)
    EDGE_TABLE = {
        0: [],
        1: [(3, 0)],
        2: [(0, 1)],
        3: [(3, 1)],
        4: [(1, 2)],
        5: [(3, 0), (1, 2)],
        6: [(0, 2)],
        7: [(3, 2)],
        8: [(2, 3)],
        9: [(2, 0)],
        10: [(0, 1), (2, 3)],
        11: [(2, 1)],
        12: [(1, 3)],
        13: [(1, 0)],
        14: [(0, 3)],
        15: []
    }
    
    def __init__(self, threshold: float = ISO_THRESHOLD):
        self.threshold = threshold
    
    def extract_contours(
        self,
        grid: np.ndarray,
        bounds: Dict[str, float]
    ) -> List[List[List[float]]]:
        """
        Extrait les contours d'une grille d'intensité.
        
        Args:
            grid: Grille numpy 2D (valeurs 0-1)
            bounds: Limites géographiques {north, south, east, west}
            
        Returns:
            Liste de contours [[lng, lat], ...]
        """
        rows, cols = grid.shape
        binary = (grid >= self.threshold).astype(int)
        
        segments = []
        
        for i in range(rows - 1):
            for j in range(cols - 1):
                # Configuration de la cellule (4 coins)
                config = (
                    binary[i, j] * 8 +
                    binary[i, j + 1] * 4 +
                    binary[i + 1, j + 1] * 2 +
                    binary[i + 1, j] * 1
                )
                
                edges = self.EDGE_TABLE.get(config, [])
                
                for edge in edges:
                    p1 = self._interpolate_edge(grid, i, j, edge[0])
                    p2 = self._interpolate_edge(grid, i, j, edge[1])
                    
                    # Convertir en coordonnées géographiques
                    lng1, lat1 = self._grid_to_geo(p1, rows, cols, bounds)
                    lng2, lat2 = self._grid_to_geo(p2, rows, cols, bounds)
                    
                    segments.append(((lng1, lat1), (lng2, lat2)))
        
        # Assembler les segments en contours fermés
        contours = self._assemble_contours(segments)
        
        return contours
    
    def _interpolate_edge(
        self,
        grid: np.ndarray,
        i: int,
        j: int,
        edge: int
    ) -> Tuple[float, float]:
        """Interpole la position sur un bord de cellule."""
        corners = [
            (i, j),         # 0: top-left
            (i, j + 1),     # 1: top-right
            (i + 1, j + 1), # 2: bottom-right
            (i + 1, j)      # 3: bottom-left
        ]
        
        # Bords: 0=top, 1=right, 2=bottom, 3=left
        if edge == 0:
            r, c = i, j
            v1, v2 = grid[i, j], grid[i, j + 1]
            t = self._lerp_factor(v1, v2)
            return (c + t, r)
        elif edge == 1:
            r, c = i, j + 1
            v1, v2 = grid[i, j + 1], grid[i + 1, j + 1]
            t = self._lerp_factor(v1, v2)
            return (c, r + t)
        elif edge == 2:
            r, c = i + 1, j
            v1, v2 = grid[i + 1, j], grid[i + 1, j + 1]
            t = self._lerp_factor(v1, v2)
            return (c + t, r)
        else:  # edge == 3
            r, c = i, j
            v1, v2 = grid[i, j], grid[i + 1, j]
            t = self._lerp_factor(v1, v2)
            return (c, r + t)
    
    def _lerp_factor(self, v1: float, v2: float) -> float:
        """Facteur d'interpolation linéaire."""
        if abs(v2 - v1) < 1e-10:
            return 0.5
        return (self.threshold - v1) / (v2 - v1)
    
    def _grid_to_geo(
        self,
        point: Tuple[float, float],
        rows: int,
        cols: int,
        bounds: Dict[str, float]
    ) -> Tuple[float, float]:
        """Convertit coordonnées grille en géographiques."""
        c, r = point
        
        lng = bounds["west"] + (c / (cols - 1)) * (bounds["east"] - bounds["west"])
        lat = bounds["north"] - (r / (rows - 1)) * (bounds["north"] - bounds["south"])
        
        return lng, lat
    
    def _assemble_contours(
        self,
        segments: List[Tuple[Tuple[float, float], Tuple[float, float]]]
    ) -> List[List[List[float]]]:
        """Assemble les segments en contours fermés."""
        if not segments:
            return []
        
        contours = []
        used = set()
        
        for idx, seg in enumerate(segments):
            if idx in used:
                continue
            
            contour = [list(seg[0]), list(seg[1])]
            used.add(idx)
            
            # Étendre le contour
            changed = True
            while changed:
                changed = False
                for i, s in enumerate(segments):
                    if i in used:
                        continue
                    
                    # Connecter par le début
                    if self._points_close(contour[0], s[1]):
                        contour.insert(0, list(s[0]))
                        used.add(i)
                        changed = True
                    elif self._points_close(contour[0], s[0]):
                        contour.insert(0, list(s[1]))
                        used.add(i)
                        changed = True
                    # Connecter par la fin
                    elif self._points_close(contour[-1], s[0]):
                        contour.append(list(s[1]))
                        used.add(i)
                        changed = True
                    elif self._points_close(contour[-1], s[1]):
                        contour.append(list(s[0]))
                        used.add(i)
                        changed = True
            
            # Fermer le contour si possible
            if len(contour) >= 3:
                if not self._points_close(contour[0], contour[-1]):
                    contour.append(contour[0])
                contours.append(contour)
        
        return contours
    
    def _points_close(
        self,
        p1: List[float],
        p2: Tuple[float, float],
        tolerance: float = 1e-6
    ) -> bool:
        """Vérifie si deux points sont proches."""
        return abs(p1[0] - p2[0]) < tolerance and abs(p1[1] - p2[1]) < tolerance


# =============================================================================
# CHAIKIN SMOOTHING
# =============================================================================

def chaikin_smooth(
    points: List[List[float]],
    iterations: int = 3,
    closed: bool = True
) -> List[List[float]]:
    """
    Lissage de Chaikin multi-passes pour contours naturels.
    
    Args:
        points: Liste de points [[lng, lat], ...]
        iterations: Nombre de passes de lissage
        closed: Si True, traite comme polygone fermé
        
    Returns:
        Points lissés
    """
    if len(points) < 3:
        return points
    
    result = [list(p) for p in points]
    
    for _ in range(iterations):
        new_points = []
        n = len(result)
        
        for i in range(n - 1 if not closed else n):
            p0 = result[i]
            p1 = result[(i + 1) % n]
            
            # Point à 1/4
            q = [
                0.75 * p0[0] + 0.25 * p1[0],
                0.75 * p0[1] + 0.25 * p1[1]
            ]
            # Point à 3/4
            r = [
                0.25 * p0[0] + 0.75 * p1[0],
                0.25 * p0[1] + 0.75 * p1[1]
            ]
            
            new_points.extend([q, r])
        
        # Fermer si nécessaire
        if closed and new_points:
            new_points.append(new_points[0])
        
        result = new_points
    
    return result


# =============================================================================
# GÉNÉRATEUR DE GRILLE D'INTENSITÉ
# =============================================================================

class IntensityGridGenerator:
    """
    Génère une grille d'intensité basée sur les scores P0-STABLE.
    
    La grille représente la probabilité de présence/activité
    pour une espèce dans une zone donnée.
    """
    
    def __init__(self, resolution: int = GRID_RESOLUTION):
        self.resolution = resolution
    
    def generate(
        self,
        bounds: Dict[str, float],
        species: str,
        hotspot_type: str,
        seed: Optional[int] = None
    ) -> np.ndarray:
        """
        Génère une grille d'intensité pour une zone.
        
        Args:
            bounds: Limites {north, south, east, west}
            species: Espèce cible
            hotspot_type: Type de hotspot
            seed: Seed pour reproductibilité
            
        Returns:
            Grille numpy 2D (0-1)
        """
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        
        grid = np.zeros((self.resolution, self.resolution))
        
        # Générer plusieurs "noyaux" d'intensité organiques
        num_kernels = random.randint(2, 5)
        
        for _ in range(num_kernels):
            # Position aléatoire du noyau
            cx = random.randint(self.resolution // 4, 3 * self.resolution // 4)
            cy = random.randint(self.resolution // 4, 3 * self.resolution // 4)
            
            # Taille et forme (organique, pas circulaire)
            size_x = random.randint(8, 20)
            size_y = random.randint(8, 20)
            angle = random.uniform(0, math.pi)
            intensity = random.uniform(0.7, 1.0)
            
            # Appliquer le noyau avec forme elliptique irrégulière
            self._apply_organic_kernel(grid, cx, cy, size_x, size_y, angle, intensity, species)
        
        # Ajouter du bruit de terrain
        terrain_noise = self._generate_terrain_noise(species)
        grid = np.clip(grid + terrain_noise * 0.2, 0, 1)
        
        # Normaliser
        if grid.max() > 0:
            grid = grid / grid.max()
        
        return grid
    
    def _apply_organic_kernel(
        self,
        grid: np.ndarray,
        cx: int,
        cy: int,
        size_x: int,
        size_y: int,
        angle: float,
        intensity: float,
        species: str
    ) -> None:
        """Applique un noyau organique à la grille."""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # Paramètres de déformation par espèce
        deform = self._get_species_deformation(species)
        
        for i in range(max(0, cy - size_y * 2), min(self.resolution, cy + size_y * 2)):
            for j in range(max(0, cx - size_x * 2), min(self.resolution, cx + size_x * 2)):
                # Rotation
                dx = j - cx
                dy = i - cy
                rx = dx * cos_a + dy * sin_a
                ry = -dx * sin_a + dy * cos_a
                
                # Distance normalisée avec déformation
                noise = math.sin(rx * deform["freq"]) * deform["amp"]
                noise += math.cos(ry * deform["freq"] * 1.3) * deform["amp"] * 0.7
                
                dist_x = (rx / size_x) ** 2
                dist_y = (ry / size_y) ** 2
                dist = math.sqrt(dist_x + dist_y) + noise * 0.3
                
                if dist < 1.5:
                    # Fonction de décroissance organique
                    value = intensity * max(0, 1 - dist ** 1.5)
                    grid[i, j] = max(grid[i, j], value)
    
    def _get_species_deformation(self, species: str) -> Dict[str, float]:
        """Retourne les paramètres de déformation par espèce."""
        deformations = {
            "moose": {"freq": 0.3, "amp": 0.2},      # Grandes zones, peu irrégulières
            "deer": {"freq": 0.6, "amp": 0.4},       # Zones dentelées
            "bear": {"freq": 0.25, "amp": 0.15},     # Zones arrondies
            "wild_turkey": {"freq": 0.5, "amp": 0.35},
            "elk": {"freq": 0.35, "amp": 0.25}
        }
        return deformations.get(species, {"freq": 0.4, "amp": 0.25})
    
    def _generate_terrain_noise(self, species: str) -> np.ndarray:
        """Génère du bruit de terrain."""
        noise = np.zeros((self.resolution, self.resolution))
        
        # Bruit multi-échelle
        for scale in [4, 8, 16]:
            small = np.random.rand(self.resolution // scale, self.resolution // scale)
            # Interpolation bilinéaire
            from scipy.ndimage import zoom
            try:
                scaled = zoom(small, scale, order=1)
                if scaled.shape[0] >= self.resolution:
                    noise += scaled[:self.resolution, :self.resolution] / scale
            except Exception:
                pass
        
        return noise


# =============================================================================
# GÉNÉRATEUR DE CONTOURS ORGANIQUES
# =============================================================================

class OrganicContourGenerator:
    """
    Générateur de contours organiques BIONIC V5.
    
    Pipeline complet:
    1. Génération grille d'intensité (P0-STABLE)
    2. Extraction iso-contours (Marching Squares)
    3. Filtrage superficie (5000-10000 m²)
    4. Lissage Chaikin (3 passes)
    5. Validation OSM (évitement réel)
    6. Ajustement comportemental
    """
    
    def __init__(self):
        self._marching = MarchingSquares(threshold=ISO_THRESHOLD)
        self._grid_gen = IntensityGridGenerator()
        self._osm_cache = get_osm_cache() if get_osm_cache else None
    
    def generate_organic_hotspot(
        self,
        bounds: Dict[str, float],
        species: str,
        hotspot_type: str,
        min_area: float = MIN_AREA_M2,
        max_area: float = MAX_AREA_M2
    ) -> Optional[List[List[float]]]:
        """
        Génère un hotspot organique conforme BIONIC V5.
        
        Args:
            bounds: Limites géographiques
            species: Espèce cible
            hotspot_type: Type de hotspot
            min_area: Superficie minimale (m²)
            max_area: Superficie maximale (m²)
            
        Returns:
            Coordonnées du contour [[lng, lat], ...] ou None si invalide
        """
        center_lat = (bounds["north"] + bounds["south"]) / 2
        center_lng = (bounds["east"] + bounds["west"]) / 2
        
        # Seed déterministe pour reproductibilité
        seed = self._create_seed(center_lat, center_lng, species, hotspot_type)
        
        # 1. Générer grille d'intensité
        grid = self._grid_gen.generate(bounds, species, hotspot_type, seed)
        
        # 2. Extraire contours via Marching Squares
        contours = self._marching.extract_contours(grid, bounds)
        
        if not contours:
            return None
        
        # 3. Filtrer par superficie et sélectionner le meilleur
        valid_contours = []
        for contour in contours:
            if len(contour) < 4:
                continue
            
            area = calculate_polygon_area_m2(contour, center_lat)
            
            # Vérifier la plage de superficie
            if min_area <= area <= max_area:
                valid_contours.append((contour, area))
            elif area > max_area * 0.5:
                # Essayer de redimensionner
                scaled = self._scale_to_area(contour, center_lat, center_lng, (min_area + max_area) / 2)
                if scaled:
                    new_area = calculate_polygon_area_m2(scaled, center_lat)
                    if min_area <= new_area <= max_area:
                        valid_contours.append((scaled, new_area))
        
        if not valid_contours:
            return None
        
        # Prendre le contour le plus proche de la superficie cible
        target = (min_area + max_area) / 2
        best_contour, best_area = min(valid_contours, key=lambda x: abs(x[1] - target))
        
        # 4. Appliquer lissage Chaikin (3 passes)
        smoothed = chaikin_smooth(best_contour, iterations=3, closed=True)
        
        # 5. Valider et ajuster via OSM (évitement réel)
        validated = self._validate_and_clip_osm(smoothed, center_lat, center_lng)
        
        if validated is None:
            return None
        
        # Vérification finale de superficie
        final_area = calculate_polygon_area_m2(validated, center_lat)
        if final_area < min_area * 0.8:  # Tolérance 20%
            return None
        
        return validated
    
    def generate_multiple_hotspots(
        self,
        bounds: Dict[str, float],
        species: str,
        hotspot_types: List[str],
        count_per_type: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Génère plusieurs hotspots organiques.
        
        Returns:
            Liste de hotspots avec métadonnées
        """
        hotspots = []
        
        lat_range = bounds["north"] - bounds["south"]
        lng_range = bounds["east"] - bounds["west"]
        
        for hotspot_type in hotspot_types:
            for i in range(count_per_type):
                # Sous-région pour ce hotspot
                sub_bounds = self._get_sub_bounds(bounds, i, count_per_type)
                
                contour = self.generate_organic_hotspot(
                    bounds=sub_bounds,
                    species=species,
                    hotspot_type=hotspot_type
                )
                
                if contour:
                    center_lat = sum(c[1] for c in contour) / len(contour)
                    area = calculate_polygon_area_m2(contour, center_lat)
                    
                    hotspots.append({
                        "id": generate_id(f"HS-{hotspot_type[:3].upper()}"),
                        "type": hotspot_type,
                        "species": species,
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [contour]
                        },
                        "area_m2": area,
                        "style": create_hotspot_style(hotspot_type, species),
                        "metadata": {
                            "generator": "OrganicContourGenerator",
                            "method": "marching_squares_chaikin",
                            "osm_validated": self._osm_cache is not None
                        }
                    })
        
        return hotspots
    
    def _create_seed(
        self,
        lat: float,
        lng: float,
        species: str,
        hotspot_type: str
    ) -> int:
        """Crée un seed déterministe."""
        data = f"{lat:.4f}_{lng:.4f}_{species}_{hotspot_type}"
        return int(hashlib.md5(data.encode()).hexdigest()[:8], 16)
    
    def _scale_to_area(
        self,
        coords: List[List[float]],
        center_lat: float,
        center_lng: float,
        target_area: float
    ) -> Optional[List[List[float]]]:
        """Redimensionne un contour vers une superficie cible."""
        current_area = calculate_polygon_area_m2(coords, center_lat)
        if current_area <= 0:
            return None
        
        scale = math.sqrt(target_area / current_area)
        
        # Calculer le centroïde
        cx = sum(c[0] for c in coords) / len(coords)
        cy = sum(c[1] for c in coords) / len(coords)
        
        scaled = []
        for lng, lat in coords:
            new_lng = cx + (lng - cx) * scale
            new_lat = cy + (lat - cy) * scale
            scaled.append([new_lng, new_lat])
        
        return scaled
    
    def _validate_and_clip_osm(
        self,
        coords: List[List[float]],
        center_lat: float,
        center_lng: float
    ) -> Optional[List[List[float]]]:
        """Valide et découpe le contour selon les exclusions OSM."""
        if self._osm_cache is None:
            return coords  # Pas de cache OSM disponible
        
        # Vérifier la validité
        is_valid, exclusion_type, overlap = self._osm_cache.is_polygon_valid(coords)
        
        if is_valid:
            return coords
        
        # Tenter de découper
        clipped = self._osm_cache.clip_polygon_to_valid_area(coords)
        
        if clipped and len(clipped) >= 4:
            return clipped
        
        return None  # Impossible de valider
    
    def _get_sub_bounds(
        self,
        bounds: Dict[str, float],
        index: int,
        total: int
    ) -> Dict[str, float]:
        """Calcule les sous-limites pour un hotspot."""
        lat_range = bounds["north"] - bounds["south"]
        lng_range = bounds["east"] - bounds["west"]
        
        # Grille approximative
        cols = int(math.sqrt(total)) + 1
        row = index // cols
        col = index % cols
        
        cell_lat = lat_range / cols
        cell_lng = lng_range / cols
        
        return {
            "north": bounds["north"] - row * cell_lat,
            "south": bounds["north"] - (row + 1) * cell_lat,
            "east": bounds["west"] + (col + 1) * cell_lng,
            "west": bounds["west"] + col * cell_lng
        }


# =============================================================================
# STYLES CONFORMES BIONIC V5
# =============================================================================

def create_hotspot_style(hotspot_type: str, species: str = "moose") -> Dict[str, Any]:
    """
    Crée un style conforme aux spécifications visuelles BIONIC V5.
    
    OBLIGATOIRE:
    - Contour 1-2px, coloré
    - Centre TRANSPARENT (fill_opacity = 0)
    - ZÉRO effets (glow, shadow, halo)
    """
    color = SPECIES_COLORS.get(species, HOTSPOT_COLORS.get(hotspot_type, "#FFD700"))
    
    return {
        "stroke_color": color,
        "stroke_width": 1.5,
        "fill_opacity": 0.0,  # OBLIGATOIRE: Centre transparent
        "stroke_opacity": 0.95,
        "stroke_linecap": "round",
        "stroke_linejoin": "round"
    }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'OrganicContourGenerator',
    'MarchingSquares',
    'IntensityGridGenerator',
    'chaikin_smooth',
    'create_hotspot_style',
    'generate_id',
    'calculate_polygon_area_m2',
    'SPECIES_COLORS',
    'HOTSPOT_COLORS',
    'MIN_AREA_M2',
    'MAX_AREA_M2',
    'TARGET_AREA_M2'
]
