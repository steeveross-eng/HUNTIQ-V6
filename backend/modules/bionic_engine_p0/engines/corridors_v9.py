"""
Corridor Engine V9 — Orchestrateur des 9 moteurs BIONIC
=========================================================
Pipeline complet:
  1. Generer corridor A* (via corridor_10x)
  2. Evaluer avec 9 moteurs BIONIC
  3. Classifier (5 niveaux)
  4. Valider (BCE-4X)
  5. Enrichir et retourner

Classification 5 niveaux:
  - gris    (potentiel)     : score 0-30
  - jaune   (opportuniste)  : score 31-50
  - orange  (fonctionnel)   : score 51-70
  - rouge   (primaire)      : score 71-85
  - rouge_raye (critique)   : score 86-100

Zero hardcoding. Scores 100% dynamiques.
"""

import logging
import math
from datetime import datetime, timezone
from typing import Dict, List, Any

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


def classify_corridor_v9(score: float, classification_impacts: List[int] = None) -> Dict[str, Any]:
    """Classifie un corridor selon son score composite + impacts moteurs."""
    impacts = classification_impacts or []
    total_impact = sum(impacts)
    adjusted_score = max(0, min(100, score + total_impact * 3))

    for level, config in CLASSIFICATION_V9.items():
        if config["min"] <= adjusted_score <= config["max"]:
            return {
                "level": level,
                "label": config["label"],
                "color": config["color"],
                "width": config["width"],
                "opacity": config["opacity"],
                "dash": config["dash"],
                "base_score": round(score, 1),
                "adjusted_score": round(adjusted_score, 1),
                "impact_sum": total_impact,
            }
    return {"level": "gris", "label": "Potentiel", "color": "#9E9E9E", "width": 1.5, "opacity": 0.5, "dash": "8,4", "base_score": round(score, 1), "adjusted_score": round(adjusted_score, 1), "impact_sum": total_impact}


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
                "score": r.score,
                "weight": r.weight,
                "certainty": r.certainty,
                "classification_impact": r.classification_impact,
                "details": r.details,
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
        """Applique clipping strict 2km² et validation."""
        coords = corridor.get("geometry", {}).get("coordinates", [])
        if not coords or not bounds:
            return corridor

        margin = 0.0005
        south = bounds.get("south", -90) - margin
        north = bounds.get("north", 90) + margin
        west = bounds.get("west", -180) - margin
        east = bounds.get("east", 180) + margin

        clipped = []
        for c in coords:
            lng, lat = c[0], c[1]
            clng = max(west, min(east, lng))
            clat = max(south, min(north, lat))
            clipped.append([clng, clat])

        corridor["geometry"]["coordinates"] = clipped
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
        """
        Repare les gaps de continuite en interpolant des points intermediaires.
        BCE-4X: Corrige les 4 violations de continuite identifiees.
        """
        coords = corridor.get("geometry", {}).get("coordinates", [])
        if len(coords) < 2:
            return corridor

        fixed_coords = [coords[0]]
        gaps_fixed = 0

        for i in range(len(coords) - 1):
            c1, c2 = coords[i], coords[i + 1]
            dist = self._haversine(c1[1], c1[0], c2[1], c2[0])

            if dist > max_gap_m:
                # Interpolate intermediate points
                n_intermediate = max(1, int(dist / (max_gap_m * 0.8)))
                for j in range(1, n_intermediate + 1):
                    t = j / (n_intermediate + 1)
                    inter_lng = c1[0] + t * (c2[0] - c1[0])
                    inter_lat = c1[1] + t * (c2[1] - c1[1])
                    # Add slight natural curve
                    offset = 0.00005 * math.sin(t * math.pi)
                    fixed_coords.append([
                        round(inter_lng + offset, 6),
                        round(inter_lat + offset, 6),
                    ])
                gaps_fixed += 1

            fixed_coords.append(c2)

        corridor["geometry"]["coordinates"] = fixed_coords
        if gaps_fixed > 0:
            corridor["properties"]["continuity_gaps_fixed"] = gaps_fixed
            logger.info(f"[V9-Continuity] Fixed {gaps_fixed} gaps in corridor {corridor.get('id', '?')}")

        return corridor

    def enrich_corridor(self, corridor: Dict) -> Dict:
        """
        Enrichit un corridor avec des metadonnees ecologiques avancees.
        Appele apres evaluation et validation.
        """
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
        3. Clip to bounds
        4. Enrich
        5. Validate
        """
        # Step 1: Evaluate with 9 BIONIC engines
        corridor = self.evaluate_corridor(corridor_feature, global_context)

        # Step 2: Fix continuity gaps BEFORE validation
        corridor = self.fix_continuity_gaps(corridor)

        # Step 3: Clip to bounds
        if bounds:
            corridor = self.validate_and_clip(corridor, bounds)

        # Step 4: Enrich with ecological metadata
        corridor = self.enrich_corridor(corridor)

        # Step 5: Final continuity validation
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
