"""
BIONIC V8 — Corridors 10X avec Classification WWF + Base Écologique
Service de génération de corridors biologiquement réalistes.

VERSION: 10X V8-READY — Intégration base écologique complète
Réf: INSTRUCTION OFFICIELLE — CORRIDORS 10X + CLASSIFICATION WWF

Classification WWF:
  1. Macro-corridors (largeur > 5 km) — connecter régions géographiques
  2. Corridors biologiques (1-5 km) — maintenir écosystèmes connectés  
  3. Corridors de conservation (< 1 km) — relier reliques en paysage fragmenté

Critères biologiques 10X:
  - Connectivité: alimentation, repos, rut, transition, refuges, observation, thermique
  - Topographie: vallées, coulées, ravines, plateaux, crêtes douces, drainage
  - Habitats: lisières forêt-agriculture, forêts matures, zones semi-ouvertes
  - Évitement: zones ouvertes, perturbations humaines, obstacles physiques

Algorithme A*:
  - Coût faible: vallées, coulées, bandes boisées
  - Coût moyen: forêts mixtes continues
  - Coût élevé: champs ouverts, zones urbaines, routes

Bénéfices écologiques:
  - Déplacement naturel du gibier
  - Recherche alimentaire
  - Échanges génétiques
  - Adaptation au changement climatique
"""

import logging
import math
import heapq
from typing import Dict, List, Any, Optional, Tuple, Set
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger("bionic_engine.corridor_10x")

# =====================================================================
# CLASSIFICATION WWF
# =====================================================================

class WWFCorridorType(Enum):
    """Classification WWF des corridors écologiques"""
    MACRO = "macro_corridor"           # > 5 km — connexion régionale
    BIOLOGICAL = "biological_corridor" # 1-5 km — connexion écosystèmes
    CONSERVATION = "conservation_corridor"  # < 1 km — reliques fragmentées


@dataclass
class CorridorMetadata:
    """Métadonnées enrichies pour un corridor"""
    wwf_type: WWFCorridorType
    width_m: float
    length_m: float
    
    # Critères biologiques
    connects_zones: List[str] = field(default_factory=list)  # Types de zones connectées
    habitat_quality: float = 0.0  # 0-100
    connectivity_score: float = 0.0  # 0-100
    
    # Critères topographiques
    terrain_types: List[str] = field(default_factory=list)
    avg_slope: float = 0.0
    follows_drainage: bool = False
    
    # Critères écologiques
    genetic_exchange_potential: float = 0.0
    climate_adaptation_value: float = 0.0
    fragmentation_mitigation: float = 0.0


# =====================================================================
# CRITÈRES BIOLOGIQUES 10X
# =====================================================================

# Types de zones à connecter (priorité haute)
ZONE_CONNECTIVITY_PRIORITY = {
    "alimentation": 100,
    "repos": 95,
    "rut": 90,
    "transition": 85,
    "refuge": 80,
    "observation": 75,
    "thermique": 70,
}

# Types de terrain privilégiés
PREFERRED_TERRAIN = {
    "vallee": {"score": 100, "description": "Vallées naturelles"},
    "coulee": {"score": 95, "description": "Coulées et ravins"},
    "ravine": {"score": 90, "description": "Ravines et dépressions"},
    "plateau_coulee_crete": {"score": 85, "description": "Plateau entre coulée et crête"},
    "repli_terrain": {"score": 80, "description": "Replis de terrain"},
    "crete_douce": {"score": 75, "description": "Crêtes douces (pente < 15%)"},
    "drainage": {"score": 70, "description": "Zones de drainage"},
    "pente_faible": {"score": 65, "description": "Pentes < 10%"},
    "pente_moderee": {"score": 50, "description": "Pentes 10-20%"},
}

# Habitats propices
PREFERRED_HABITATS = {
    "lisiere_foret_agriculture": {"score": 100, "description": "Lisière forêt-agriculture"},
    "foret_mature": {"score": 95, "description": "Forêt mature"},
    "foret_clairsemee": {"score": 85, "description": "Forêt clairsemée"},
    "zone_semi_ouverte": {"score": 80, "description": "Zone semi-ouverte"},
    "bande_boisee_lineaire": {"score": 90, "description": "Bande boisée linéaire"},
    "haie_naturelle": {"score": 75, "description": "Haie naturelle"},
}

# Zones à éviter
AVOID_ZONES = {
    "zone_ouverte": {"penalty": -50, "description": "Zone trop ouverte"},
    "zone_dense": {"penalty": -40, "description": "Zone trop dense"},
    "perturbation_humaine": {"penalty": -80, "description": "Perturbation humaine"},
    "coupe_recente": {"penalty": -60, "description": "Coupe forestière récente"},
    "surface_minerale": {"penalty": -70, "description": "Surface minérale"},
    "obstacle_physique": {"penalty": -100, "description": "Obstacle physique infranchissable"},
}


# =====================================================================
# SERVICE CORRIDORS 10X
# =====================================================================

class Corridor10XService:
    """
    Service de génération et validation des corridors 10X.
    Intègre les critères biologiques, topographiques et la classification WWF.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("bionic_engine.corridor_10x")
    
    def classify_corridor_wwf(self, width_m: float) -> WWFCorridorType:
        """
        Classifie un corridor selon la typologie WWF.
        
        Args:
            width_m: Largeur du corridor en mètres
            
        Returns:
            Type de corridor WWF
        """
        if width_m > 5000:
            return WWFCorridorType.MACRO
        elif width_m >= 1000:
            return WWFCorridorType.BIOLOGICAL
        else:
            return WWFCorridorType.CONSERVATION
    
    def calculate_connectivity_score(
        self,
        from_zone_type: str,
        to_zone_type: str,
    ) -> float:
        """
        Calcule le score de connectivité entre deux types de zones.
        
        Args:
            from_zone_type: Type de zone de départ
            to_zone_type: Type de zone d'arrivée
            
        Returns:
            Score de connectivité 0-100
        """
        from_priority = ZONE_CONNECTIVITY_PRIORITY.get(from_zone_type, 50)
        to_priority = ZONE_CONNECTIVITY_PRIORITY.get(to_zone_type, 50)
        
        # Score moyen pondéré
        return (from_priority + to_priority) / 2
    
    def calculate_terrain_score(
        self,
        terrain_types: List[str],
        avg_slope: float,
        follows_drainage: bool,
    ) -> float:
        """
        Calcule le score topographique du corridor.
        
        Args:
            terrain_types: Liste des types de terrain traversés
            avg_slope: Pente moyenne en %
            follows_drainage: Suit un réseau de drainage
            
        Returns:
            Score topographique 0-100
        """
        if not terrain_types:
            return 50.0
        
        # Score des types de terrain
        terrain_scores = [
            PREFERRED_TERRAIN.get(t, {"score": 40})["score"]
            for t in terrain_types
        ]
        terrain_avg = sum(terrain_scores) / len(terrain_scores)
        
        # Pénalité de pente
        slope_penalty = 0
        if avg_slope > 30:
            slope_penalty = -30
        elif avg_slope > 20:
            slope_penalty = -15
        elif avg_slope > 10:
            slope_penalty = -5
        
        # Bonus drainage
        drainage_bonus = 15 if follows_drainage else 0
        
        return min(100, max(0, terrain_avg + slope_penalty + drainage_bonus))
    
    def calculate_habitat_score(
        self,
        habitat_types: List[str],
        avoid_zones_crossed: List[str],
    ) -> float:
        """
        Calcule le score d'habitat du corridor.
        
        Args:
            habitat_types: Types d'habitats traversés
            avoid_zones_crossed: Zones à éviter traversées
            
        Returns:
            Score d'habitat 0-100
        """
        if not habitat_types:
            base_score = 50.0
        else:
            habitat_scores = [
                PREFERRED_HABITATS.get(h, {"score": 40})["score"]
                for h in habitat_types
            ]
            base_score = sum(habitat_scores) / len(habitat_scores)
        
        # Pénalités des zones à éviter
        penalties = sum(
            AVOID_ZONES.get(z, {"penalty": 0})["penalty"]
            for z in avoid_zones_crossed
        )
        
        return min(100, max(0, base_score + penalties))
    
    def calculate_ecological_benefits(
        self,
        corridor_length_m: float,
        connectivity_score: float,
        wwf_type: WWFCorridorType,
    ) -> Dict[str, float]:
        """
        Calcule les bénéfices écologiques du corridor.
        
        Args:
            corridor_length_m: Longueur du corridor en mètres
            connectivity_score: Score de connectivité
            wwf_type: Classification WWF
            
        Returns:
            Dict des scores de bénéfices écologiques
        """
        # Multiplicateurs par type WWF
        wwf_multipliers = {
            WWFCorridorType.MACRO: {"genetic": 1.5, "climate": 1.8, "fragmentation": 1.2},
            WWFCorridorType.BIOLOGICAL: {"genetic": 1.2, "climate": 1.3, "fragmentation": 1.5},
            WWFCorridorType.CONSERVATION: {"genetic": 1.0, "climate": 1.0, "fragmentation": 1.8},
        }
        
        mult = wwf_multipliers.get(wwf_type, {"genetic": 1.0, "climate": 1.0, "fragmentation": 1.0})
        
        # Base scores
        base_genetic = min(100, connectivity_score * 0.8 + (corridor_length_m / 100))
        base_climate = min(100, connectivity_score * 0.7 + (corridor_length_m / 150))
        base_fragmentation = min(100, connectivity_score * 0.9)
        
        return {
            "genetic_exchange_potential": min(100, base_genetic * mult["genetic"]),
            "climate_adaptation_value": min(100, base_climate * mult["climate"]),
            "fragmentation_mitigation": min(100, base_fragmentation * mult["fragmentation"]),
        }
    
    def validate_corridor_continuity(
        self,
        corridor_points: List[Tuple[float, float]],
        max_gap_m: float = 100.0,
    ) -> Tuple[bool, List[Dict]]:
        """
        Valide la continuité d'un corridor (aucun saut, aucune rupture).
        
        Args:
            corridor_points: Liste des points (lat, lng) du corridor
            max_gap_m: Gap maximum autorisé en mètres
            
        Returns:
            Tuple (is_valid, list of issues)
        """
        if len(corridor_points) < 2:
            return False, [{"type": "insufficient_points", "message": "Corridor needs at least 2 points"}]
        
        issues = []
        METERS_PER_DEG = 111320.0
        
        for i in range(len(corridor_points) - 1):
            p1, p2 = corridor_points[i], corridor_points[i + 1]
            
            # Calcul distance
            lat_diff = (p2[0] - p1[0]) * METERS_PER_DEG
            lng_diff = (p2[1] - p1[1]) * METERS_PER_DEG * abs(
                __import__("math").cos(__import__("math").radians((p1[0] + p2[0]) / 2))
            )
            distance = (lat_diff**2 + lng_diff**2) ** 0.5
            
            if distance > max_gap_m:
                issues.append({
                    "type": "gap_detected",
                    "segment_index": i,
                    "distance_m": distance,
                    "max_allowed_m": max_gap_m,
                    "point_start": p1,
                    "point_end": p2,
                })
        
        return len(issues) == 0, issues
    
    def enrich_corridor(
        self,
        corridor_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Enrichit un corridor avec les métadonnées 10X et classification WWF.
        
        Args:
            corridor_data: Données brutes du corridor
            
        Returns:
            Corridor enrichi avec métadonnées complètes
        """
        # Extraction des données
        positions = corridor_data.get("positions", [])
        width_m = corridor_data.get("width_m", 500)
        from_zone = corridor_data.get("fromZoneType", "unknown")
        to_zone = corridor_data.get("toZoneType", "unknown")
        terrain_types = corridor_data.get("terrain_types", [])
        habitat_types = corridor_data.get("habitat_types", [])
        avg_slope = corridor_data.get("avg_slope", 5.0)
        follows_drainage = corridor_data.get("follows_drainage", False)
        avoid_zones = corridor_data.get("avoid_zones_crossed", [])
        
        # Classification WWF
        wwf_type = self.classify_corridor_wwf(width_m)
        
        # Calcul longueur
        length_m = corridor_data.get("distanceM", 0)
        if not length_m and len(positions) >= 2:
            length_m = self._calculate_path_length(positions)
        
        # Scores
        connectivity_score = self.calculate_connectivity_score(from_zone, to_zone)
        terrain_score = self.calculate_terrain_score(terrain_types, avg_slope, follows_drainage)
        habitat_score = self.calculate_habitat_score(habitat_types, avoid_zones)
        
        # Bénéfices écologiques
        eco_benefits = self.calculate_ecological_benefits(length_m, connectivity_score, wwf_type)
        
        # Validation continuité
        is_continuous, continuity_issues = self.validate_corridor_continuity(
            [(p.get("lat", p[0]) if isinstance(p, dict) else p[0],
              p.get("lng", p[1]) if isinstance(p, dict) else p[1])
             for p in positions]
        )
        
        # Score final composite
        final_score = (
            connectivity_score * 0.30 +
            terrain_score * 0.25 +
            habitat_score * 0.25 +
            eco_benefits["fragmentation_mitigation"] * 0.20
        )
        
        # Enrichissement
        enriched = {
            **corridor_data,
            "wwf_classification": {
                "type": wwf_type.value,
                "label": self._get_wwf_label(wwf_type),
                "width_m": width_m,
            },
            "scores_10x": {
                "connectivity": round(connectivity_score, 1),
                "terrain": round(terrain_score, 1),
                "habitat": round(habitat_score, 1),
                "composite": round(final_score, 1),
            },
            "ecological_benefits": {
                k: round(v, 1) for k, v in eco_benefits.items()
            },
            "validation": {
                "is_continuous": is_continuous,
                "issues_count": len(continuity_issues),
                "issues": continuity_issues[:3],  # Limiter pour performance
            },
            "metadata_10x": {
                "connects_zones": [from_zone, to_zone],
                "terrain_types": terrain_types,
                "habitat_types": habitat_types,
                "follows_drainage": follows_drainage,
                "length_m": round(length_m, 1),
            },
            "score": round(final_score, 1),  # Override score principal
        }
        
        return enriched
    
    def _calculate_path_length(self, positions: List) -> float:
        """Calcule la longueur totale du chemin en mètres."""
        if len(positions) < 2:
            return 0.0
        
        METERS_PER_DEG = 111320.0
        total = 0.0
        
        for i in range(len(positions) - 1):
            p1 = positions[i]
            p2 = positions[i + 1]
            
            lat1 = p1.get("lat", p1[0]) if isinstance(p1, dict) else p1[0]
            lng1 = p1.get("lng", p1[1]) if isinstance(p1, dict) else p1[1]
            lat2 = p2.get("lat", p2[0]) if isinstance(p2, dict) else p2[0]
            lng2 = p2.get("lng", p2[1]) if isinstance(p2, dict) else p2[1]
            
            lat_diff = (lat2 - lat1) * METERS_PER_DEG
            lng_diff = (lng2 - lng1) * METERS_PER_DEG * abs(
                __import__("math").cos(__import__("math").radians((lat1 + lat2) / 2))
            )
            total += (lat_diff**2 + lng_diff**2) ** 0.5
        
        return total
    
    def _get_wwf_label(self, wwf_type: WWFCorridorType) -> str:
        """Retourne le label français pour un type WWF."""
        labels = {
            WWFCorridorType.MACRO: "Macro-corridor (> 5 km)",
            WWFCorridorType.BIOLOGICAL: "Corridor biologique (1-5 km)",
            WWFCorridorType.CONSERVATION: "Corridor de conservation (< 1 km)",
        }
        return labels.get(wwf_type, "Corridor")


# =====================================================================
# ALGORITHME A* POUR CORRIDORS ÉCOLOGIQUES
# =====================================================================

# Coûts de traversée par type de terrain (A*)
TERRAIN_COSTS = {
    # Coût faible — terrain préféré
    "valley": 1.0,
    "coulee": 1.0,
    "ravine": 1.2,
    "drainage": 1.1,
    "wooded_strip": 1.0,
    "hedgerow": 1.1,
    "riparian": 1.0,
    "forest_edge": 1.2,
    
    # Coût moyen — terrain acceptable
    "mixed_forest": 1.5,
    "mature_forest": 1.4,
    "conifer_forest": 1.6,
    "deciduous_forest": 1.5,
    "plateau": 1.8,
    "gentle_ridge": 1.7,
    "saddle": 1.3,
    
    # Coût élevé — terrain à éviter
    "open_field": 3.0,
    "agriculture": 2.5,
    "clearcut": 4.0,
    "urban_edge": 5.0,
    "road_crossing": 4.5,
    "steep_slope": 3.5,
    "dense_thicket": 2.8,
    
    # Coût prohibitif — obstacles
    "urban": 10.0,
    "water_body": 8.0,
    "cliff": 15.0,
    "highway": 12.0,
}


class AStarNode:
    """Noeud pour l'algorithme A*"""
    def __init__(self, position: Tuple[float, float], g_cost: float = 0, h_cost: float = 0, parent=None):
        self.position = position
        self.g_cost = g_cost  # Coût depuis le départ
        self.h_cost = h_cost  # Heuristique (distance estimée à l'arrivée)
        self.f_cost = g_cost + h_cost
        self.parent = parent
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        if isinstance(other, AStarNode):
            return self.position == other.position
        return False
    
    def __hash__(self):
        return hash(self.position)


class CorridorPathfinder:
    """
    Algorithme A* pour trouver des corridors écologiques optimaux.
    Intègre les coûts de terrain et les critères biologiques.
    """
    
    def __init__(self, grid_resolution: float = 100.0):
        """
        Args:
            grid_resolution: Résolution de la grille en mètres
        """
        self.grid_resolution = grid_resolution
        self.logger = logging.getLogger("bionic_engine.corridor_pathfinder")
    
    def _heuristic(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calcule la distance euclidienne entre deux points (heuristique)."""
        METERS_PER_DEG = 111320.0
        lat_diff = (pos2[0] - pos1[0]) * METERS_PER_DEG
        lng_diff = (pos2[1] - pos1[1]) * METERS_PER_DEG * math.cos(math.radians((pos1[0] + pos2[0]) / 2))
        return math.sqrt(lat_diff**2 + lng_diff**2)
    
    def _get_terrain_cost(self, position: Tuple[float, float], terrain_data: Dict[str, Any]) -> float:
        """
        Récupère le coût de terrain pour une position.
        
        Args:
            position: (lat, lng)
            terrain_data: Données de terrain indexées par position
            
        Returns:
            Coût de traversée
        """
        # Clé de position simplifiée
        key = f"{position[0]:.4f},{position[1]:.4f}"
        
        terrain_info = terrain_data.get(key, {})
        terrain_type = terrain_info.get("type", "mixed_forest")
        
        base_cost = TERRAIN_COSTS.get(terrain_type, 2.0)
        
        # Modificateurs additionnels
        slope = terrain_info.get("slope", 5)
        if slope > 30:
            base_cost *= 1.5
        elif slope > 20:
            base_cost *= 1.2
        
        human_pressure = terrain_info.get("human_pressure", 0)
        base_cost *= (1 + human_pressure)
        
        return base_cost
    
    def _get_neighbors(self, node: AStarNode, bounds: Tuple[float, float, float, float]) -> List[Tuple[float, float]]:
        """
        Génère les voisins d'un noeud dans la grille.
        
        Args:
            node: Noeud courant
            bounds: (min_lat, min_lng, max_lat, max_lng)
            
        Returns:
            Liste des positions voisines valides
        """
        METERS_PER_DEG = 111320.0
        step_lat = self.grid_resolution / METERS_PER_DEG
        step_lng = self.grid_resolution / (METERS_PER_DEG * math.cos(math.radians(node.position[0])))
        
        directions = [
            (step_lat, 0),      # N
            (-step_lat, 0),     # S
            (0, step_lng),      # E
            (0, -step_lng),     # W
            (step_lat, step_lng),    # NE
            (step_lat, -step_lng),   # NW
            (-step_lat, step_lng),   # SE
            (-step_lat, -step_lng),  # SW
        ]
        
        neighbors = []
        for dlat, dlng in directions:
            new_lat = node.position[0] + dlat
            new_lng = node.position[1] + dlng
            
            # Vérification des bornes
            if bounds[0] <= new_lat <= bounds[2] and bounds[1] <= new_lng <= bounds[3]:
                neighbors.append((new_lat, new_lng))
        
        return neighbors
    
    def find_corridor_path(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        terrain_data: Dict[str, Any],
        max_iterations: int = 5000,
    ) -> Optional[Dict[str, Any]]:
        """
        Trouve le chemin optimal entre deux points avec A*.
        Optimisé: O(n log n) avec g_cost_map et grid snapping.
        """
        # Snap to grid
        def snap(pos):
            METERS_PER_DEG = 111320.0
            step_lat = self.grid_resolution / METERS_PER_DEG
            step_lng = self.grid_resolution / (METERS_PER_DEG * math.cos(math.radians(pos[0])))
            return (round(pos[0] / step_lat) * step_lat, round(pos[1] / step_lng) * step_lng)

        start = snap(start)
        end = snap(end)

        margin = 0.02
        bounds = (
            min(start[0], end[0]) - margin,
            min(start[1], end[1]) - margin,
            max(start[0], end[0]) + margin,
            max(start[1], end[1]) + margin,
        )

        start_node = AStarNode(start, 0, self._heuristic(start, end))
        open_set: List[AStarNode] = [start_node]
        g_cost_map: Dict[Tuple[float, float], float] = {start: 0}

        iterations = 0

        while open_set and iterations < max_iterations:
            iterations += 1
            current = heapq.heappop(open_set)

            # Skip if we already found a better path to this node
            if current.g_cost > g_cost_map.get(current.position, float('inf')):
                continue

            if self._heuristic(current.position, end) < self.grid_resolution * 1.5:
                path = []
                node = current
                while node:
                    path.append({"lat": node.position[0], "lng": node.position[1]})
                    node = node.parent
                path.reverse()
                return {
                    "path": path,
                    "total_cost": current.g_cost,
                    "iterations": iterations,
                    "length_m": self._heuristic(start, end),
                    "efficiency": self._heuristic(start, end) / max(current.g_cost, 1),
                }

            for neighbor_pos in self._get_neighbors(current, bounds):
                snapped = snap(neighbor_pos)
                terrain_cost = self._get_terrain_cost(snapped, terrain_data)
                move_cost = self._heuristic(current.position, snapped) * terrain_cost
                g_cost = current.g_cost + move_cost

                if g_cost < g_cost_map.get(snapped, float('inf')):
                    g_cost_map[snapped] = g_cost
                    h_cost = self._heuristic(snapped, end)
                    heapq.heappush(open_set, AStarNode(snapped, g_cost, h_cost, current))

        self.logger.warning(f"A* failed to find path after {iterations} iterations")
        return None
    
    def smooth_path(self, path: List[Dict[str, float]], smoothing_factor: float = 0.3) -> List[Dict[str, float]]:
        """
        Lisse un chemin pour éliminer les angles aigus.
        
        Args:
            path: Liste de points [{lat, lng}, ...]
            smoothing_factor: Facteur de lissage (0-1)
            
        Returns:
            Chemin lissé
        """
        if len(path) < 3:
            return path
        
        smoothed = [path[0]]  # Premier point fixe
        
        for i in range(1, len(path) - 1):
            prev = path[i - 1]
            curr = path[i]
            next_pt = path[i + 1]
            
            # Moyenne pondérée
            new_lat = curr["lat"] * (1 - smoothing_factor) + (prev["lat"] + next_pt["lat"]) / 2 * smoothing_factor
            new_lng = curr["lng"] * (1 - smoothing_factor) + (prev["lng"] + next_pt["lng"]) / 2 * smoothing_factor
            
            smoothed.append({"lat": new_lat, "lng": new_lng})
        
        smoothed.append(path[-1])  # Dernier point fixe
        
        return smoothed


# Instance singleton pathfinder
corridor_pathfinder = CorridorPathfinder(grid_resolution=100.0)

# Instance singleton service
corridor_10x_service = Corridor10XService()
