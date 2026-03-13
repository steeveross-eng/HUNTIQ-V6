"""
BIONIC V3 — Integration Totale des Engines
STEVE-MAX++: 24 engines connectes au scoring, zones, corridors, hotspots, faunique et IA.

Architecture:
- 12 engines V2 existants (behavior, keyzone, food, wind, terrain, pressure, corridor, attractiveness, action, predictive, bce, rendering)
- 12 NOUVEAUX engines V3 (hierarchy, interaction, geopedology, connectivity, temporal, hotspot, forest_v2, food_v2, wetness_v2, geoform_v2, behavior_v2, attractiveness_v2)
- 3 modeles fauniques (moose, deer, bear) avec ponderations specifiques
- 3 engines IA (predictive_models, dynamic_scoring, temporal_analysis)

Pipeline:
Phase 1: Engines independants (V2 + V3)
Phase 2: Engines dependants (attractiveness, action, predictive, IA)
Phase 3: Scoring faunique (moose, deer, bear)
Phase 4: Score final integre
"""

import math
import logging
from typing import Dict, Any, List

logger = logging.getLogger("bionic_v3")


class BionicEngineV3Base:
    """Base class for all V3 engines."""
    engine_id: str = ""
    engine_name: str = ""
    version: str = "3.0"
    weight: float = 1.0
    category: str = "analysis"

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def status(self) -> Dict[str, Any]:
        return {"id": self.engine_id, "name": self.engine_name, "version": self.version, "weight": self.weight, "status": "active"}


# ══════════════════════════════════════════════════════════
# 12 NOUVEAUX ENGINES V3
# ══════════════════════════════════════════════════════════

class EcologicalHierarchyEngine(BionicEngineV3Base):
    """Engine V3 #1: Analyse la hierarchie ecologique du territoire (strates vegetales, succession)."""
    engine_id = "ecological_hierarchy"
    engine_name = "EcologicalHierarchy Engine"
    weight = 1.1
    category = "ecology"

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        zones = context.get("zones", [])
        species = context.get("species", "moose")

        strata = {"canopy": 0, "understory": 0, "ground": 0, "aquatic": 0}
        for z in zones:
            lid = z.get("properties", {}).get("layer_id", "")
            if lid in ("peuplements", "ndvi"):
                strata["canopy"] += 1
            elif lid in ("alimentation", "habitats"):
                strata["understory"] += 1
            elif lid in ("pentes", "altitude"):
                strata["ground"] += 1
            elif lid == "hydro":
                strata["aquatic"] += 1

        total = sum(strata.values()) or 1
        diversity = sum(1 for v in strata.values() if v > 0) / 4
        succession_score = min(100, int(diversity * 60 + (total / max(len(zones), 1)) * 40))

        species_mod = {"moose": 1.1, "deer": 0.9, "bear": 1.2}.get(species, 1.0)
        score = min(100, int(succession_score * species_mod))

        return {"score": score, "strata": strata, "diversity": round(diversity, 2), "succession_stage": "mature" if score > 70 else "intermediate" if score > 40 else "early"}


class InteractionEngine(BionicEngineV3Base):
    """Engine V3 #2: Analyse les interactions entre zones (effet de lisiere, complementarite)."""
    engine_id = "interaction"
    engine_name = "Interaction Engine"
    weight = 1.0
    category = "ecology"

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        zones = context.get("zones", [])
        species = context.get("species", "moose")

        layer_ids = [z.get("properties", {}).get("layer_id", "") for z in zones]
        unique_layers = set(layer_ids)

        complementary_pairs = [
            ("alimentation", "repos"), ("habitats", "hydro"), ("peuplements", "ndvi"),
            ("rut", "corridors"), ("affuts", "trajets"), ("alimentation", "hydro"),
        ]
        pair_count = sum(1 for a, b in complementary_pairs if a in unique_layers and b in unique_layers)
        edge_effect = min(100, pair_count * 18)

        species_bonus = {"moose": 10, "deer": 15, "bear": 5}.get(species, 0)
        score = min(100, edge_effect + species_bonus)

        return {"score": score, "complementary_pairs": pair_count, "edge_effect": edge_effect, "unique_layers": len(unique_layers)}


class GeoPedologyEngine(BionicEngineV3Base):
    """Engine V3 #3: Analyse la pedologie et geomorphologie (type de sol, drainage)."""
    engine_id = "geopedology"
    engine_name = "GeoPedology Engine"
    weight = 0.8
    category = "terrain"

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        zones = context.get("zones", [])
        species = context.get("species", "moose")
        bounds = context.get("bounds", {})

        has_hydro = any(z.get("properties", {}).get("layer_id") == "hydro" for z in zones)
        has_pentes = any(z.get("properties", {}).get("layer_id") == "pentes" for z in zones)
        has_altitude = any(z.get("properties", {}).get("layer_id") == "altitude" for z in zones)

        drainage = 70 if has_hydro else 40
        soil_depth = 60 if not has_pentes else 45
        organic_matter = 55 + (15 if has_altitude else 0)

        base = int(drainage * 0.4 + soil_depth * 0.3 + organic_matter * 0.3)
        species_mod = {"moose": 1.0, "deer": 1.1, "bear": 0.9}.get(species, 1.0)
        score = min(100, int(base * species_mod))

        return {"score": score, "drainage": drainage, "soil_depth": soil_depth, "organic_matter": organic_matter}


class ConnectivityEngine(BionicEngineV3Base):
    """Engine V3 #4: Analyse la connectivite fonctionnelle du paysage."""
    engine_id = "connectivity"
    engine_name = "Connectivity Engine"
    weight = 1.2
    category = "landscape"

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        corridors = context.get("corridors", [])
        zones = context.get("zones", [])
        species = context.get("species", "moose")

        n_corridors = len(corridors)
        n_zones = len(zones)
        connected = sum(1 for c in corridors if c.get("properties", {}).get("continuity_valid"))

        connectivity_ratio = connected / max(n_corridors, 1)
        zone_coverage = min(1.0, n_zones / 10)
        corridor_density = min(1.0, n_corridors / 8)

        base = int(connectivity_ratio * 40 + zone_coverage * 30 + corridor_density * 30)
        species_mod = {"moose": 1.15, "deer": 1.0, "bear": 0.85}.get(species, 1.0)
        score = min(100, int(base * species_mod))

        return {"score": score, "connectivity_ratio": round(connectivity_ratio, 2), "zone_coverage": round(zone_coverage, 2), "corridor_density": round(corridor_density, 2)}


class TemporalDynamicsEngine(BionicEngineV3Base):
    """Engine V3 #5: Analyse les variations temporelles (saisonnieres, circadiennes)."""
    engine_id = "temporal_dynamics"
    engine_name = "TemporalDynamics Engine"
    weight = 1.0
    category = "temporal"

    SEASONAL_ACTIVITY = {
        "printemps": {"moose": 0.7, "deer": 0.8, "bear": 0.9},
        "ete": {"moose": 0.6, "deer": 0.7, "bear": 1.0},
        "automne": {"moose": 1.0, "deer": 0.9, "bear": 0.8},
        "hiver": {"moose": 0.5, "deer": 0.4, "bear": 0.1},
    }

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        season = context.get("season", "automne")
        hour = context.get("hour", 6)
        species = context.get("species", "moose")

        seasonal_mod = self.SEASONAL_ACTIVITY.get(season, {}).get(species, 0.7)
        circadian = 1.0 - 0.4 * abs(math.sin(math.pi * (hour - 5) / 12)) if 4 <= hour <= 20 else 0.3
        crepuscular_bonus = 0.2 if hour in (5, 6, 17, 18, 19) else 0.0

        activity = min(1.0, seasonal_mod * circadian + crepuscular_bonus)
        score = min(100, int(activity * 100))

        return {"score": score, "seasonal_mod": round(seasonal_mod, 2), "circadian": round(circadian, 2), "crepuscular_bonus": crepuscular_bonus, "peak_hours": [5, 6, 17, 18]}


class HotspotEngine(BionicEngineV3Base):
    """Engine V3 #6: Detection et scoring des hotspots (zones a forte concentration d'activite)."""
    engine_id = "hotspot"
    engine_name = "Hotspot Engine"
    weight = 1.3
    category = "strategic"

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        zones = context.get("zones", [])
        corridors = context.get("corridors", [])
        species = context.get("species", "moose")
        engine_scores = context.get("engine_scores", {})

        strategic_layers = {"affuts", "salines", "rut", "trajets"}
        strategic_count = sum(1 for z in zones if z.get("properties", {}).get("layer_id") in strategic_layers)

        high_score_corridors = sum(1 for c in corridors if c.get("properties", {}).get("scoring", {}).get("score", 0) > 60)

        zone_density = min(1.0, len(zones) / 12)
        strategic_ratio = strategic_count / max(len(zones), 1)
        corridor_quality = high_score_corridors / max(len(corridors), 1)

        avg_engine = 0
        if engine_scores:
            scores_list = [v.get("score", 0) for v in engine_scores.values() if isinstance(v, dict)]
            avg_engine = sum(scores_list) / max(len(scores_list), 1) / 100

        base = int(zone_density * 25 + strategic_ratio * 30 + corridor_quality * 25 + avg_engine * 20)
        species_mod = {"moose": 1.1, "deer": 1.0, "bear": 0.9}.get(species, 1.0)
        score = min(100, int(base * species_mod * 100 / max(base, 1) if base > 0 else 0))
        score = min(100, int((zone_density * 25 + strategic_ratio * 30 + corridor_quality * 25 + avg_engine * 20) * species_mod))

        hotspots_detected = max(1, strategic_count)
        return {"score": score, "hotspots_detected": hotspots_detected, "strategic_count": strategic_count, "zone_density": round(zone_density, 2)}


class ForestStructureV2Engine(BionicEngineV3Base):
    """Engine V3 #7: Analyse avancee de la structure forestiere (densite, age, composition)."""
    engine_id = "forest_structure_v2"
    engine_name = "ForestStructure Engine v2"
    weight = 1.0
    category = "ecology"

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        zones = context.get("zones", [])
        species = context.get("species", "moose")

        forest_layers = {"peuplements", "ndvi", "habitats"}
        forest_zones = [z for z in zones if z.get("properties", {}).get("layer_id") in forest_layers]
        n_forest = len(forest_zones)

        canopy_density = min(100, n_forest * 15 + 30)
        age_diversity = min(100, 40 + n_forest * 10)
        composition = min(100, 35 + len(set(z.get("properties", {}).get("layer_id") for z in forest_zones)) * 25)

        base = int(canopy_density * 0.4 + age_diversity * 0.3 + composition * 0.3)
        species_mod = {"moose": 1.0, "deer": 1.1, "bear": 1.15}.get(species, 1.0)
        score = min(100, int(base * species_mod))

        return {"score": score, "canopy_density": canopy_density, "age_diversity": age_diversity, "composition": composition, "forest_zone_count": n_forest}


class FoodScoreV2Engine(BionicEngineV3Base):
    """Engine V3 #8: Scoring alimentaire avance (qualite, quantite, accessibilite)."""
    engine_id = "food_score_v2"
    engine_name = "FoodScore v2"
    weight = 1.2
    category = "ecology"

    SPECIES_FOOD = {
        "moose": {"aquatic_plants": 30, "browse": 40, "bark": 20, "herbs": 10},
        "deer": {"browse": 35, "herbs": 30, "mast": 25, "crops": 10},
        "bear": {"berries": 30, "insects": 20, "fish": 25, "vegetation": 25},
    }

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        zones = context.get("zones", [])
        season = context.get("season", "automne")
        species = context.get("species", "moose")

        food_layers = {"alimentation", "ndvi", "hydro"}
        food_zones = sum(1 for z in zones if z.get("properties", {}).get("layer_id") in food_layers)

        season_quality = {"printemps": 0.7, "ete": 0.9, "automne": 1.0, "hiver": 0.3}.get(season, 0.7)
        availability = min(100, food_zones * 20 + 25)
        quality = int(availability * season_quality)
        accessibility = min(100, 60 + food_zones * 8)

        base = int(quality * 0.4 + availability * 0.3 + accessibility * 0.3)
        food_prefs = self.SPECIES_FOOD.get(species, {})
        diversity_bonus = min(20, len(food_prefs) * 5)
        score = min(100, base + diversity_bonus)

        return {"score": score, "quality": quality, "availability": availability, "accessibility": accessibility, "season_quality": season_quality, "food_preferences": food_prefs}


class WetnessScoreV2Engine(BionicEngineV3Base):
    """Engine V3 #9: Score d'humidite avance (sources d'eau, precipitations, drainage)."""
    engine_id = "wetness_v2"
    engine_name = "WetnessScore v2"
    weight = 0.9
    category = "hydrology"

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        zones = context.get("zones", [])
        weather = context.get("weather", {})
        species = context.get("species", "moose")

        hydro_count = sum(1 for z in zones if z.get("properties", {}).get("layer_id") == "hydro")
        water_proximity = min(100, hydro_count * 25 + 20)

        humidity = weather.get("humidity", 60)
        precipitation = min(100, humidity * 0.8 + 20)

        drainage = 65
        base = int(water_proximity * 0.4 + precipitation * 0.3 + drainage * 0.3)
        species_mod = {"moose": 1.2, "deer": 0.9, "bear": 1.1}.get(species, 1.0)
        score = min(100, int(base * species_mod))

        return {"score": score, "water_proximity": water_proximity, "precipitation": precipitation, "drainage": drainage, "hydro_zones": hydro_count}


class GeoFormScoreV2Engine(BionicEngineV3Base):
    """Engine V3 #10: Score geomorphologique avance (formes de terrain, exposition)."""
    engine_id = "geoform_v2"
    engine_name = "GeoFormScore v2"
    weight = 0.8
    category = "terrain"

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        zones = context.get("zones", [])
        species = context.get("species", "moose")

        terrain_layers = {"pentes", "altitude", "orientation"}
        terrain_zones = sum(1 for z in zones if z.get("properties", {}).get("layer_id") in terrain_layers)

        slope_diversity = min(100, terrain_zones * 20 + 30)
        aspect_score = 65 if any(z.get("properties", {}).get("layer_id") == "orientation" for z in zones) else 40
        elevation_range = 55 if any(z.get("properties", {}).get("layer_id") == "altitude" for z in zones) else 35

        base = int(slope_diversity * 0.4 + aspect_score * 0.3 + elevation_range * 0.3)
        species_mod = {"moose": 0.9, "deer": 1.1, "bear": 1.0}.get(species, 1.0)
        score = min(100, int(base * species_mod))

        return {"score": score, "slope_diversity": slope_diversity, "aspect_score": aspect_score, "elevation_range": elevation_range}


class BehaviorV2Engine(BionicEngineV3Base):
    """Engine V3 #11: Modele comportemental avance (patterns deplacements, repos, alimentation)."""
    engine_id = "behavior_v2"
    engine_name = "Behavior Engine v2"
    weight = 1.2
    category = "behavioral"

    SPECIES_PATTERNS = {
        "moose": {"home_range_km2": 25, "daily_movement_km": 3, "rest_pct": 0.6, "feed_pct": 0.3, "move_pct": 0.1},
        "deer": {"home_range_km2": 8, "daily_movement_km": 2, "rest_pct": 0.5, "feed_pct": 0.35, "move_pct": 0.15},
        "bear": {"home_range_km2": 100, "daily_movement_km": 8, "rest_pct": 0.4, "feed_pct": 0.4, "move_pct": 0.2},
    }

    CIRCADIAN = {
        "moose": [15, 10, 5, 5, 20, 80, 95, 70, 40, 25, 20, 15, 15, 15, 20, 30, 75, 95, 85, 60, 35, 25, 20, 15],
        "deer":  [10, 5, 5, 5, 15, 70, 90, 65, 35, 20, 15, 10, 10, 10, 15, 25, 65, 90, 80, 55, 30, 20, 15, 10],
        "bear":  [5, 3, 2, 2, 10, 40, 70, 85, 90, 85, 75, 60, 55, 60, 70, 80, 85, 75, 50, 30, 15, 10, 8, 5],
    }

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        hour = context.get("hour", 6)
        season = context.get("season", "automne")
        species = context.get("species", "moose")
        zones = context.get("zones", [])

        pattern = self.SPECIES_PATTERNS.get(species, self.SPECIES_PATTERNS["moose"])
        circadian = self.CIRCADIAN.get(species, self.CIRCADIAN["moose"])
        activity = circadian[hour % 24]

        season_mod = {"printemps": 0.8, "ete": 0.7, "automne": 1.0, "hiver": 0.4}.get(season, 0.7)
        if species == "bear" and season == "hiver":
            season_mod = 0.05  # hibernation

        food_zones = sum(1 for z in zones if z.get("properties", {}).get("layer_id") in ("alimentation", "ndvi"))
        rest_zones = sum(1 for z in zones if z.get("properties", {}).get("layer_id") in ("repos", "habitats"))
        habitat_quality = min(1.0, (food_zones * pattern["feed_pct"] + rest_zones * pattern["rest_pct"]) / 2 + 0.3)

        score = min(100, int(activity * season_mod * habitat_quality))
        return {
            "score": score, "activity_level": activity, "season_mod": round(season_mod, 2),
            "habitat_quality": round(habitat_quality, 2), "pattern": pattern,
            "peak_hours": [i for i, v in enumerate(circadian) if v >= 70],
        }


class GlobalAttractivenessV2Engine(BionicEngineV3Base):
    """Engine V3 #12: Score d'attractivite global v2 (integre TOUS les engines V2+V3)."""
    engine_id = "attractiveness_v2"
    engine_name = "GlobalAttractiveness Engine v2"
    weight = 1.5
    category = "synthesis"

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        engine_scores = context.get("engine_scores", {})
        species = context.get("species", "moose")

        SPECIES_WEIGHTS = {
            "moose": {"food_score_v2": 1.3, "wetness_v2": 1.2, "behavior_v2": 1.4, "connectivity": 1.2, "forest_structure_v2": 1.0, "hotspot": 1.1},
            "deer": {"food_score_v2": 1.2, "forest_structure_v2": 1.3, "behavior_v2": 1.3, "interaction": 1.2, "geoform_v2": 1.1, "hotspot": 1.0},
            "bear": {"food_score_v2": 1.5, "wetness_v2": 1.1, "forest_structure_v2": 1.2, "behavior_v2": 1.2, "ecological_hierarchy": 1.1, "hotspot": 0.9},
        }

        sp_weights = SPECIES_WEIGHTS.get(species, SPECIES_WEIGHTS["moose"])
        weighted_sum = 0
        weight_total = 0

        for eid, data in engine_scores.items():
            if not isinstance(data, dict):
                continue
            s = data.get("score", 0)
            w = sp_weights.get(eid, 1.0) * data.get("weight", 1.0)
            weighted_sum += s * w
            weight_total += w

        score = min(100, int(weighted_sum / max(weight_total, 1)))

        return {"score": score, "species": species, "engines_integrated": len(engine_scores), "weight_total": round(weight_total, 1)}


# ══════════════════════════════════════════════════════════
# 3 MODELES FAUNIQUES
# ══════════════════════════════════════════════════════════

class SpeciesModel:
    """Modele faunique — calcule les scores specifiques par espece."""

    WEIGHTS = {
        "moose": {
            "behavior_v2": 1.4, "food_score_v2": 1.3, "wetness_v2": 1.2, "connectivity": 1.2,
            "forest_structure_v2": 1.0, "ecological_hierarchy": 1.1, "temporal_dynamics": 1.0,
            "terrain": 0.8, "hotspot": 1.1, "corridor_continuity": 1.0, "geopedology": 0.7,
            "interaction": 0.9, "geoform_v2": 0.7, "wind_intelligence": 0.8,
        },
        "deer": {
            "behavior_v2": 1.3, "food_score_v2": 1.2, "forest_structure_v2": 1.3, "interaction": 1.2,
            "geoform_v2": 1.1, "connectivity": 1.0, "temporal_dynamics": 1.0, "hotspot": 1.0,
            "ecological_hierarchy": 0.9, "terrain": 1.0, "wetness_v2": 0.8, "corridor_continuity": 0.9,
            "geopedology": 0.8, "wind_intelligence": 0.7,
        },
        "bear": {
            "behavior_v2": 1.2, "food_score_v2": 1.5, "wetness_v2": 1.1, "forest_structure_v2": 1.2,
            "ecological_hierarchy": 1.1, "connectivity": 0.9, "temporal_dynamics": 1.1, "hotspot": 0.9,
            "geopedology": 0.9, "interaction": 0.8, "geoform_v2": 0.8, "terrain": 0.9,
            "corridor_continuity": 0.8, "wind_intelligence": 0.6,
        },
    }

    @staticmethod
    def compute(species: str, engine_scores: Dict[str, Any]) -> Dict[str, Any]:
        weights = SpeciesModel.WEIGHTS.get(species, SpeciesModel.WEIGHTS["moose"])
        weighted_sum = 0
        weight_total = 0
        details = {}

        for eid, w in weights.items():
            data = engine_scores.get(eid, {})
            if not isinstance(data, dict):
                continue
            s = data.get("score", 0)
            weighted_sum += s * w
            weight_total += w
            details[eid] = {"score": s, "weight": w, "weighted": round(s * w, 1)}

        score = min(100, int(weighted_sum / max(weight_total, 1)))

        # Zone-specific scores
        food_score = engine_scores.get("food_score_v2", {}).get("score", 50)
        rest_score = engine_scores.get("behavior_v2", {}).get("score", 50)
        corridor_score = engine_scores.get("connectivity", {}).get("score", 50)
        hotspot_score = engine_scores.get("hotspot", {}).get("score", 50)

        return {
            "score": score, "species": species,
            "food_zone_score": food_score,
            "rest_zone_score": rest_score,
            "corridor_influence": corridor_score,
            "hotspot_influence": hotspot_score,
            "engines_used": len(details),
            "details": details,
        }


# ══════════════════════════════════════════════════════════
# 3 ENGINES IA
# ══════════════════════════════════════════════════════════

class PredictiveModelsEngine(BionicEngineV3Base):
    """Engine IA #1: Modeles predictifs (24h, 72h, 7 jours)."""
    engine_id = "predictive_models"
    engine_name = "Predictive Models Engine"
    weight = 1.0
    category = "ai"

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        engine_scores = context.get("engine_scores", {})
        species = context.get("species", "moose")
        season = context.get("season", "automne")

        all_scores = [v.get("score", 0) for v in engine_scores.values() if isinstance(v, dict)]
        avg = sum(all_scores) / max(len(all_scores), 1)

        behavior_score = engine_scores.get("behavior_v2", {}).get("score", 50)
        temporal_score = engine_scores.get("temporal_dynamics", {}).get("score", 50)
        food_score = engine_scores.get("food_score_v2", {}).get("score", 50)

        base_24h = int(avg * 0.4 + behavior_score * 0.3 + temporal_score * 0.3)
        base_72h = int(avg * 0.5 + food_score * 0.25 + behavior_score * 0.25)
        base_7d = int(avg * 0.6 + food_score * 0.2 + temporal_score * 0.2)

        decay = {"24h": 1.0, "72h": 0.85, "7d": 0.7}
        predictions = {
            "24h": {"probability": min(99, int(base_24h * decay["24h"])), "confidence": 85},
            "72h": {"probability": min(95, int(base_72h * decay["72h"])), "confidence": 70},
            "7d": {"probability": min(90, int(base_7d * decay["7d"])), "confidence": 55},
        }

        score = predictions["24h"]["probability"]
        return {"score": score, "predictions": predictions, "species": species, "season": season}


class DynamicScoringEngine(BionicEngineV3Base):
    """Engine IA #2: Scoring dynamique (ajustement temps reel)."""
    engine_id = "dynamic_scoring"
    engine_name = "Dynamic Scoring Engine"
    weight = 1.0
    category = "ai"

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        engine_scores = context.get("engine_scores", {})
        species = context.get("species", "moose")
        hour = context.get("hour", 6)
        weather = context.get("weather", {})

        all_scores = [v.get("score", 0) for v in engine_scores.values() if isinstance(v, dict)]
        base = sum(all_scores) / max(len(all_scores), 1)

        # Real-time adjustments
        wind_speed = weather.get("wind", {}).get("speed", 5)
        temp = weather.get("temp", 10)

        wind_adj = -5 if wind_speed > 20 else -2 if wind_speed > 10 else 0
        temp_adj = -5 if temp < -10 else -3 if temp < 0 else 0 if temp < 25 else -5
        time_adj = 10 if hour in (5, 6, 17, 18) else 5 if hour in (4, 7, 16, 19) else 0

        score = min(100, max(0, int(base + wind_adj + temp_adj + time_adj)))
        adjustments = {"wind": wind_adj, "temperature": temp_adj, "time_of_day": time_adj}

        return {"score": score, "base_score": round(base, 1), "adjustments": adjustments, "species": species}


class TemporalAnalysisEngine(BionicEngineV3Base):
    """Engine IA #3: Analyse temporelle (trends, patterns historiques)."""
    engine_id = "temporal_analysis"
    engine_name = "Temporal Analysis Engine"
    weight = 0.9
    category = "ai"

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        engine_scores = context.get("engine_scores", {})
        species = context.get("species", "moose")
        season = context.get("season", "automne")
        hour = context.get("hour", 6)

        all_scores = [v.get("score", 0) for v in engine_scores.values() if isinstance(v, dict)]
        current_avg = sum(all_scores) / max(len(all_scores), 1)

        season_baseline = {"printemps": 55, "ete": 50, "automne": 70, "hiver": 35}.get(season, 55)
        trend = "ascending" if current_avg > season_baseline else "descending" if current_avg < season_baseline - 10 else "stable"
        variation = round(current_avg - season_baseline, 1)

        # Generate hourly forecast for next 24h
        forecast = []
        for h in range(24):
            future_hour = (hour + h) % 24
            circadian = 1.0 - 0.4 * abs(math.sin(math.pi * (future_hour - 5) / 12)) if 4 <= future_hour <= 20 else 0.3
            forecast.append({"hour": future_hour, "predicted_score": min(100, int(current_avg * circadian))})

        score = min(100, int(current_avg * 1.05 if trend == "ascending" else current_avg * 0.95 if trend == "descending" else current_avg))

        return {"score": score, "trend": trend, "variation": variation, "season_baseline": season_baseline, "forecast_24h": forecast[:6]}


# ══════════════════════════════════════════════════════════
# ENGINE REGISTRY V3 — 12 NOUVEAUX ENGINES
# ══════════════════════════════════════════════════════════
ENGINE_REGISTRY_V3 = {
    "ecological_hierarchy": EcologicalHierarchyEngine(),
    "interaction": InteractionEngine(),
    "geopedology": GeoPedologyEngine(),
    "connectivity": ConnectivityEngine(),
    "temporal_dynamics": TemporalDynamicsEngine(),
    "hotspot": HotspotEngine(),
    "forest_structure_v2": ForestStructureV2Engine(),
    "food_score_v2": FoodScoreV2Engine(),
    "wetness_v2": WetnessScoreV2Engine(),
    "geoform_v2": GeoFormScoreV2Engine(),
    "behavior_v2": BehaviorV2Engine(),
    "attractiveness_v2": GlobalAttractivenessV2Engine(),
}

AI_ENGINES = {
    "predictive_models": PredictiveModelsEngine(),
    "dynamic_scoring": DynamicScoringEngine(),
    "temporal_analysis": TemporalAnalysisEngine(),
}


def compute_all_v3(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    BIONIC V3: Execute ALL engines (V2 + V3 + IA + Faunique) and return integrated results.

    Pipeline:
    Phase 1: Independent V2+V3 engines
    Phase 2: Dependent engines (attractiveness, hotspot)
    Phase 3: AI engines
    Phase 4: Species models
    Phase 5: Final integrated score
    """
    from modules.bionic_engine_p0.engines.engines_v2 import ENGINE_REGISTRY_V2

    species = context.get("species", "moose")
    results = {}

    # Phase 1: Independent V2 engines
    v2_independent = ["behavior", "keyzone_v2", "food_deficit", "wind_intelligence",
                       "terrain", "human_pressure", "corridor_continuity", "bce_compliance", "rendering"]
    for eid in v2_independent:
        engine = ENGINE_REGISTRY_V2.get(eid)
        if engine:
            try:
                result = engine.compute(context)
                result["weight"] = engine.weight
                result["source"] = "v2"
                results[eid] = result
            except Exception as e:
                logger.warning(f"V2 Engine {eid} failed: {e}")
                results[eid] = {"score": 0, "error": str(e), "weight": engine.weight, "source": "v2"}

    # Phase 1b: Independent V3 engines
    v3_independent = ["ecological_hierarchy", "interaction", "geopedology", "connectivity",
                       "temporal_dynamics", "forest_structure_v2", "food_score_v2",
                       "wetness_v2", "geoform_v2", "behavior_v2"]
    for eid in v3_independent:
        engine = ENGINE_REGISTRY_V3.get(eid)
        if engine:
            try:
                result = engine.compute(context)
                result["weight"] = engine.weight
                result["source"] = "v3"
                results[eid] = result
            except Exception as e:
                logger.warning(f"V3 Engine {eid} failed: {e}")
                results[eid] = {"score": 0, "error": str(e), "weight": engine.weight, "source": "v3"}

    # Phase 2: Dependent engines (need engine_scores)
    context["engine_scores"] = results
    v2_dependent = ["global_attractiveness", "action_plan", "predictive_ai"]
    for eid in v2_dependent:
        engine = ENGINE_REGISTRY_V2.get(eid)
        if engine:
            try:
                result = engine.compute(context)
                result["weight"] = engine.weight
                result["source"] = "v2"
                results[eid] = result
            except Exception as e:
                results[eid] = {"score": 0, "error": str(e), "weight": engine.weight, "source": "v2"}

    v3_dependent = ["hotspot", "attractiveness_v2"]
    for eid in v3_dependent:
        engine = ENGINE_REGISTRY_V3.get(eid)
        if engine:
            try:
                context["engine_scores"] = results
                result = engine.compute(context)
                result["weight"] = engine.weight
                result["source"] = "v3"
                results[eid] = result
            except Exception as e:
                results[eid] = {"score": 0, "error": str(e), "weight": engine.weight, "source": "v3"}

    # Phase 3: AI engines
    context["engine_scores"] = results
    for eid, engine in AI_ENGINES.items():
        try:
            result = engine.compute(context)
            result["weight"] = engine.weight
            result["source"] = "ai"
            results[eid] = result
        except Exception as e:
            results[eid] = {"score": 0, "error": str(e), "weight": engine.weight, "source": "ai"}

    # Phase 4: Species models
    species_scores = {}
    for sp in ["moose", "deer", "bear"]:
        species_scores[sp] = SpeciesModel.compute(sp, results)

    # Phase 5: Final integrated score
    all_scores = [v.get("score", 0) for v in results.values() if isinstance(v, dict)]
    all_weights = [v.get("weight", 1.0) for v in results.values() if isinstance(v, dict)]
    weighted_sum = sum(s * w for s, w in zip(all_scores, all_weights))
    weight_total = sum(all_weights) or 1
    final_score = min(100, int(weighted_sum / weight_total))

    return {
        "success": True,
        "engines": results,
        "engine_count": len(results),
        "v2_count": sum(1 for v in results.values() if isinstance(v, dict) and v.get("source") == "v2"),
        "v3_count": sum(1 for v in results.values() if isinstance(v, dict) and v.get("source") == "v3"),
        "ai_count": sum(1 for v in results.values() if isinstance(v, dict) and v.get("source") == "ai"),
        "species_scores": species_scores,
        "final_score": final_score,
        "average_score": round(sum(all_scores) / max(len(all_scores), 1), 1),
    }


def get_all_engine_statuses() -> List[Dict[str, Any]]:
    """Return status of ALL engines (V2 + V3 + AI)."""
    from modules.bionic_engine_p0.engines.engines_v2 import ENGINE_REGISTRY_V2
    statuses = []
    for engine in ENGINE_REGISTRY_V2.values():
        s = engine.status()
        s["source"] = "v2"
        statuses.append(s)
    for engine in ENGINE_REGISTRY_V3.values():
        s = engine.status()
        s["source"] = "v3"
        statuses.append(s)
    for engine in AI_ENGINES.values():
        s = engine.status()
        s["source"] = "ai"
        statuses.append(s)
    return statuses
