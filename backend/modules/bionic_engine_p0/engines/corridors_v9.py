"""
Corridor Engine V9 — Orchestrateur des 9 moteurs BIONIC
=========================================================
Pipeline complet:
  1. Generer corridor A* (via corridor_10x)
  2. Evaluer avec 9 moteurs BIONIC
  3. Classifier (5 niveaux)
  4. Lisser (Chaikin)
  5. Generer bandes polygonales (5 niveaux concentrques)
  6. Clipper au perimetre 2km2
  7. Valider (BCE-4X)
  8. Enrichir et retourner

Classification 5 niveaux:
  - gris    (potentiel)     : score 0-30   — bande externe (halo)
  - jaune   (opportuniste)  : score 31-50
  - orange  (fonctionnel)   : score 51-70
  - rouge   (primaire)      : score 71-85
  - rouge_raye (critique)   : score 86-100 — bande centrale (coeur)

Zero hardcoding. Scores 100% dynamiques.
"""

import logging
import math
from datetime import datetime, timezone
from typing import Dict, List, Any

from shapely.geometry import LineString as ShapelyLine, Polygon as ShapelyPolygon, box as shapely_box
from shapely.ops import unary_union

from modules.bionic_engine_p0.engines.nutrition_engine import NutritionEngine
from modules.bionic_engine_p0.engines.daily_routine_engine import DailyRoutineEngine
from modules.bionic_engine_p0.engines.weather_engine_v9 import WeatherEngineV9
from modules.bionic_engine_p0.engines.disturbance_engine import DisturbanceEngine
from modules.bionic_engine_p0.engines.movement_engine_v9 import MovementEngineV9
from modules.bionic_engine_p0.engines.phenology_engine import PhenologyEngine
from modules.bionic_engine_p0.engines.typology_engine import TypologyEngine
from modules.bionic_engine_p0.engines.learning_engine import LearningEngine
from modules.bionic_engine_p0.engines.habitat_enhancement_engine import HabitatEnhancementEngine

logger = logging.getLogger("bionic.corridors_v9")

# =====================================================================
# CLASSIFICATION 5 NIVEAUX
# =====================================================================

CLASSIFICATION_V9 = {
    "gris": {"min": 0, "max": 30, "label": "Potentiel", "color": "#9E9E9E", "width": 1.5, "opacity": 0.5, "dash": "8,4"},
    "jaune": {"min": 31, "max": 50, "label": "Opportuniste", "color": "#FFC107", "width": 2.0, "opacity": 0.65, "dash": None},
    "orange": {"min": 51, "max": 70, "label": "Fonctionnel", "color": "#FF9800", "width": 2.8, "opacity": 0.75, "dash": None},
    "rouge": {"min": 71, "max": 85, "label": "Primaire", "color": "#F44336", "width": 3.5, "opacity": 0.85, "dash": None},
    "rouge_raye": {"min": 86, "max": 100, "label": "Critique", "color": "#B71C1C", "width": 4.5, "opacity": 0.95, "dash": "12,3,3,3"},
}

# Band buffer widths in degrees (outer to inner)
# At Quebec ~46.8N: 0.001 deg lat ≈ 111m, 0.001 deg lng ≈ 76m
BAND_WIDTHS = {
    "gris":       0.00055,   # ~55m buffer radius (outermost halo)
    "jaune":      0.00040,   # ~40m
    "orange":     0.00028,   # ~28m
    "rouge":      0.00016,   # ~16m
    "rouge_raye": 0.00007,   # ~7m (innermost core)
}

BAND_COLORS = {
    "gris":       {"color": "#9E9E9E", "opacity": 0.20, "fillOpacity": 0.15},
    "jaune":      {"color": "#FFC107", "opacity": 0.35, "fillOpacity": 0.25},
    "orange":     {"color": "#FF9800", "opacity": 0.50, "fillOpacity": 0.40},
    "rouge":      {"color": "#F44336", "opacity": 0.70, "fillOpacity": 0.55},
    "rouge_raye": {"color": "#B71C1C", "opacity": 0.90, "fillOpacity": 0.75},
}


def classify_corridor_v9(score: float, classification_impacts: List[int] = None) -> Dict[str, Any]:
    """Classifie un corridor selon son score composite + impacts moteurs."""
    impacts = classification_impacts or []
    total_impact = sum(impacts)
    adjusted_score = max(0, min(100, score + total_impact * 3))

    for level, config in CLASSIFICATION_V9.items():
        if config["min"] <= adjusted_score <= config["max"]:
            return {
                "level": level, "label": config["label"], "color": config["color"],
                "width": config["width"], "opacity": config["opacity"], "dash": config["dash"],
                "base_score": round(score, 1), "adjusted_score": round(adjusted_score, 1),
                "impact_sum": total_impact,
            }
    return {"level": "gris", "label": "Potentiel", "color": "#9E9E9E", "width": 1.5, "opacity": 0.5,
            "dash": "8,4", "base_score": round(score, 1), "adjusted_score": round(adjusted_score, 1), "impact_sum": total_impact}


def chaikin_smooth(coords, iterations=2):
    """Lissage Chaikin sur une liste de coordonnees [lng, lat]."""
    for _ in range(iterations):
        if len(coords) < 3:
            return coords
        new_coords = [coords[0]]
        for i in range(len(coords) - 1):
            p0 = coords[i]
            p1 = coords[i + 1]
            q = [0.75 * p0[0] + 0.25 * p1[0], 0.75 * p0[1] + 0.25 * p1[1]]
            r = [0.25 * p0[0] + 0.75 * p1[0], 0.25 * p0[1] + 0.75 * p1[1]]
            new_coords.extend([q, r])
        new_coords.append(coords[-1])
        coords = new_coords
    return coords


def generate_corridor_bands(centerline_coords, bounds=None, score=50):
    """
    Genere 5 bandes polygonales concentriques autour de l'axe central.
    Utilise Shapely pour le buffering + clipping.
    
    Returns: list of band dicts with GeoJSON polygon coordinates
    """
    if len(centerline_coords) < 2:
        return []

    # Smooth the centerline
    smoothed = chaikin_smooth(centerline_coords, iterations=2)

    try:
        line = ShapelyLine(smoothed)
    except Exception:
        return []

    if line.is_empty or line.length < 0.00001:
        return []

    # Create clip box from bounds
    clip_box = None
    if bounds:
        clip_box = shapely_box(
            bounds.get("west", -180),
            bounds.get("south", -90),
            bounds.get("east", 180),
            bounds.get("north", 90),
        )

    # Determine which bands to generate based on score
    # Higher score = more bands visible (core bands only for high-scoring corridors)
    bands = []
    band_levels = list(BAND_WIDTHS.keys())  # gris, jaune, orange, rouge, rouge_raye

    for level in band_levels:
        width = BAND_WIDTHS[level]
        style = BAND_COLORS[level]
        level_config = CLASSIFICATION_V9[level]

        # Only generate inner bands if score is high enough
        if level == "rouge_raye" and score < 80:
            continue
        if level == "rouge" and score < 65:
            continue
        if level == "orange" and score < 45:
            continue
        if level == "jaune" and score < 25:
            continue

        try:
            buffered = line.buffer(width, cap_style=2, join_style=2, resolution=8)
            if buffered.is_empty:
                continue

            # Clip to bounds
            if clip_box and not clip_box.is_empty:
                buffered = buffered.intersection(clip_box)
                if buffered.is_empty:
                    continue

            # Extract polygon coordinates
            polys = _extract_polygon_coords(buffered)
            if polys:
                bands.append({
                    "level": level,
                    "label": level_config["label"],
                    "color": style["color"],
                    "opacity": style["opacity"],
                    "fillOpacity": style["fillOpacity"],
                    "coordinates": polys,
                    "width_m": round(width * 111000, 0),
                })
        except Exception as e:
            logger.debug(f"Band {level} generation failed: {e}")

    return bands


def _extract_polygon_coords(geom):
    """Extract polygon ring coordinates from a Shapely geometry."""
    if geom.is_empty:
        return None

    if geom.geom_type == 'Polygon':
        exterior = list(geom.exterior.coords)
        return [[[round(c[0], 6), round(c[1], 6)] for c in exterior]]
    elif geom.geom_type == 'MultiPolygon':
        # Merge or take the largest
        all_coords = []
        for poly in geom.geoms:
            exterior = list(poly.exterior.coords)
            all_coords.append([[round(c[0], 6), round(c[1], 6)] for c in exterior])
        return all_coords
    return None


# =====================================================================
# CORRIDOR ENGINE V9
# =====================================================================

class CorridorEngineV9:
    """Orchestrateur V9 — evalue un corridor avec les 9 moteurs BIONIC."""

    def __init__(self):
        self.engines = [
            NutritionEngine(),
            DailyRoutineEngine(),
            WeatherEngineV9(),
            DisturbanceEngine(),
            MovementEngineV9(),
            PhenologyEngine(),
            TypologyEngine(),
            LearningEngine(),
            HabitatEnhancementEngine(),
        ]

    def evaluate_corridor(self, corridor_feature: Dict, global_context: Dict) -> Dict:
        """
        Evalue un corridor GeoJSON avec les 9 moteurs.
        Retourne le corridor enrichi avec scores dynamiques V9.
        """
        props = corridor_feature.get("properties", {})
        coords = corridor_feature.get("geometry", {}).get("coordinates", [])

        if len(coords) < 2:
            return corridor_feature

        start = coords[0]
        end = coords[-1]

        # Build context for engines
        context = {
            "from_zone_type": props.get("from_zone_type", "habitats"),
            "to_zone_type": props.get("to_zone_type", "habitats"),
            "from_lat": start[1], "from_lng": start[0],
            "to_lat": end[1], "to_lng": end[0],
            "lat": (start[1] + end[1]) / 2,
            "lng": (start[0] + end[0]) / 2,
            "distance_m": props.get("distance_m", 500),
            "pathfinding": props.get("pathfinding", "A*"),
            "connectivity": props.get("scoring", {}).get("subscores", {}).get("connectivity", 80),
            "species": global_context.get("species", "moose"),
            "season": global_context.get("season", "automne"),
            "month": global_context.get("month", 10),
            "hour": global_context.get("hour", 6),
            "weather": global_context.get("weather", {}),
            "observations": global_context.get("observations", []),
            "waypoint_history": global_context.get("waypoint_history", []),
            "corridor_id": corridor_feature.get("id", "unknown"),
        }

        # Run all 9 engines
        results = []
        total_weighted_score = 0
        total_weight = 0
        classification_impacts = []
        certainties = []

        for engine in self.engines:
            try:
                result = engine.evaluate(context)
                results.append(result)
                total_weighted_score += result.score * result.weight
                total_weight += result.weight
                classification_impacts.append(result.classification_impact)
                certainties.append(result.certainty)
            except Exception as e:
                logger.warning(f"Engine {engine.ENGINE_ID} failed: {e}")

        # Composite score (weighted average)
        composite_score = total_weighted_score / total_weight if total_weight > 0 else 50
        avg_certainty = sum(certainties) / len(certainties) if certainties else 0.5

        # Classification V9
        classification = classify_corridor_v9(composite_score, classification_impacts)

        # Build engine scores dict
        engine_scores = {}
        engine_justifications = []
        for r in results:
            engine_scores[r.engine_id] = {
                "score": r.score, "weight": r.weight, "certainty": r.certainty,
                "classification_impact": r.classification_impact, "details": r.details,
            }
            engine_justifications.append(f"[{r.engine_id}] {r.justification}")

        # Update corridor properties
        props["scoring"] = {
            "score": round(composite_score, 1),
            "subscores": {r.engine_id: r.score for r in results},
            "weights": {r.engine_id: r.weight for r in results},
            "justification": engine_justifications,
        }
        props["classification_v9"] = classification
        props["corridor_type"] = classification["level"]
        props["certainty"] = round(avg_certainty, 3)
        props["engines_evaluated"] = len(results)
        props["scores_10x"] = engine_scores
        props["dem_enhanced"] = True
        props["v9_pipeline"] = True
        props["evaluated_at"] = datetime.now(timezone.utc).isoformat()

        corridor_feature["properties"] = props
        return corridor_feature

    def validate_and_clip(self, corridor: Dict, bounds: Dict) -> Dict:
        """Applique clipping strict 2km2 via Shapely intersection."""
        coords = corridor.get("geometry", {}).get("coordinates", [])
        if not coords or not bounds:
            return corridor

        try:
            clip_box = shapely_box(
                bounds.get("west", -180), bounds.get("south", -90),
                bounds.get("east", 180), bounds.get("north", 90),
            )
            line = ShapelyLine(coords)
            clipped = line.intersection(clip_box)
            if clipped.is_empty:
                corridor["properties"]["clipped"] = True
                corridor["properties"]["in_perimeter"] = False
                return corridor

            if clipped.geom_type == 'LineString':
                corridor["geometry"]["coordinates"] = [
                    [round(c[0], 6), round(c[1], 6)] for c in clipped.coords
                ]
            elif clipped.geom_type == 'MultiLineString':
                # Take the longest segment
                longest = max(clipped.geoms, key=lambda g: g.length)
                corridor["geometry"]["coordinates"] = [
                    [round(c[0], 6), round(c[1], 6)] for c in longest.coords
                ]
        except Exception as e:
            logger.debug(f"Shapely clipping failed: {e}")
            # Fallback: simple coordinate clamping
            south = bounds.get("south", -90)
            north = bounds.get("north", 90)
            west = bounds.get("west", -180)
            east = bounds.get("east", 180)
            corridor["geometry"]["coordinates"] = [
                [max(west, min(east, c[0])), max(south, min(north, c[1]))] for c in coords
            ]

        corridor["properties"]["clipped"] = True
        corridor["properties"]["in_perimeter"] = True
        return corridor

    def validate_continuity(self, corridor: Dict, max_gap_m: float = 150) -> bool:
        """Valide la continuite du corridor (aucun gap > seuil)."""
        coords = corridor.get("geometry", {}).get("coordinates", [])
        for i in range(len(coords) - 1):
            c1, c2 = coords[i], coords[i + 1]
            dist = self._haversine(c1[1], c1[0], c2[1], c2[0])
            if dist > max_gap_m:
                return False
        return True

    def fix_continuity_gaps(self, corridor: Dict, max_gap_m: float = 150) -> Dict:
        """Repare les gaps de continuite en interpolant des points intermediaires."""
        coords = corridor.get("geometry", {}).get("coordinates", [])
        if len(coords) < 2:
            return corridor

        fixed_coords = [coords[0]]
        gaps_fixed = 0

        for i in range(len(coords) - 1):
            c1, c2 = coords[i], coords[i + 1]
            dist = self._haversine(c1[1], c1[0], c2[1], c2[0])

            if dist > max_gap_m:
                n_intermediate = max(1, int(dist / (max_gap_m * 0.8)))
                for j in range(1, n_intermediate + 1):
                    t = j / (n_intermediate + 1)
                    inter_lng = c1[0] + t * (c2[0] - c1[0])
                    inter_lat = c1[1] + t * (c2[1] - c1[1])
                    offset = 0.00005 * math.sin(t * math.pi)
                    fixed_coords.append([round(inter_lng + offset, 6), round(inter_lat + offset, 6)])
                gaps_fixed += 1

            fixed_coords.append(c2)

        corridor["geometry"]["coordinates"] = fixed_coords
        if gaps_fixed > 0:
            corridor["properties"]["continuity_gaps_fixed"] = gaps_fixed

        return corridor

    def generate_bands(self, corridor: Dict, bounds: Dict = None) -> Dict:
        """
        Genere les 5 bandes polygonales concentriques (ruban ecologique).
        Chaque bande: gris (halo) → jaune → orange → rouge → rouge_raye (coeur).
        """
        coords = corridor.get("geometry", {}).get("coordinates", [])
        score = corridor.get("properties", {}).get("scoring", {}).get("score", 50)

        bands = generate_corridor_bands(coords, bounds, score)
        corridor["properties"]["bands"] = bands
        corridor["properties"]["has_bands"] = len(bands) > 0
        corridor["properties"]["band_count"] = len(bands)

        # Also store smoothed centerline
        smoothed = chaikin_smooth(coords, iterations=2)
        corridor["properties"]["centerline"] = [[round(c[0], 6), round(c[1], 6)] for c in smoothed]

        return corridor

    def enrich_corridor(self, corridor: Dict) -> Dict:
        """Enrichit un corridor avec des metadonnees ecologiques avancees."""
        try:
            from bce.bce_corridor_v9 import enrich_corridor as bce_enrich
            corridor = bce_enrich(corridor)
        except Exception as e:
            logger.warning(f"Enrichment failed: {e}")
        return corridor

    def process_corridor_full(self, corridor_feature: Dict, global_context: Dict, bounds: Dict = None) -> Dict:
        """
        Pipeline V9 complet pour un corridor:
        1. Evaluate (9 engines)
        2. Fix continuity gaps
        3. Clip to bounds (Shapely)
        4. Generate bands (5-level polygon ribbon)
        5. Enrich
        6. Validate
        """
        # Step 1: Evaluate with 9 BIONIC engines
        corridor = self.evaluate_corridor(corridor_feature, global_context)

        # Step 2: Fix continuity gaps
        corridor = self.fix_continuity_gaps(corridor)

        # Step 3: Clip to bounds (strict Shapely intersection)
        if bounds:
            corridor = self.validate_and_clip(corridor, bounds)

        # Step 4: Generate 5-level polygon bands (the ribbon)
        corridor = self.generate_bands(corridor, bounds)

        # Step 5: Enrich with ecological metadata
        corridor = self.enrich_corridor(corridor)

        # Step 6: Final continuity validation
        corridor["properties"]["continuity_valid"] = self.validate_continuity(corridor)

        return corridor

    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2):
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        return 6371000 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# Singleton
corridor_engine_v9 = CorridorEngineV9()
