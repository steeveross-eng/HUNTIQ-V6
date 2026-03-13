"""
BIONIC HUNT — Engines V2 Registry
STEVE-MAX: 12 moteurs BIONIC V2 integres dans le pipeline.

Chaque moteur:
- a un compute() qui retourne un score [0-100] + metadata
- est appele dans le pipeline de scoring global
- est valide par BCE-4X
"""

import logging
import math
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger("bionic.engines_v2")


class BionicEngineV2Base:
    """Base class for all BIONIC V2 engines."""
    engine_id: str = "base"
    engine_name: str = "Base Engine"
    version: str = "2.0"
    weight: float = 1.0  # Weight in global scoring

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def status(self) -> Dict[str, Any]:
        return {
            "id": self.engine_id,
            "name": self.engine_name,
            "version": self.version,
            "weight": self.weight,
            "status": "active",
        }


# ══════════════════════════════════════════════════════════
# ENGINE #1 — Behavior Engine
# Analyse les patterns comportementaux: aube/crepuscule, repos, alimentation
# ══════════════════════════════════════════════════════════
class BehaviorEngine(BionicEngineV2Base):
    engine_id = "behavior"
    engine_name = "Behavior Engine"
    version = "2.0"
    weight = 1.2

    # Activity peaks by hour (0-23) — moose behavioral data
    ACTIVITY_CURVE = {
        0: 15, 1: 10, 2: 8, 3: 8, 4: 15, 5: 45, 6: 80, 7: 70,
        8: 50, 9: 35, 10: 25, 11: 20, 12: 15, 13: 15, 14: 20,
        15: 30, 16: 50, 17: 75, 18: 85, 19: 70, 20: 45, 21: 30,
        22: 25, 23: 20,
    }

    SEASON_BEHAVIOR = {
        "printemps": {"activity_mod": 1.1, "feeding_pct": 0.6, "rut_active": False},
        "ete": {"activity_mod": 0.9, "feeding_pct": 0.5, "rut_active": False},
        "automne": {"activity_mod": 1.3, "feeding_pct": 0.4, "rut_active": True},
        "hiver": {"activity_mod": 0.7, "feeding_pct": 0.7, "rut_active": False},
    }

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        hour = context.get("hour", datetime.now(timezone.utc).hour)
        season = context.get("season", "automne")
        species = context.get("species", "moose")

        base_activity = self.ACTIVITY_CURVE.get(hour, 30)
        season_data = self.SEASON_BEHAVIOR.get(season, self.SEASON_BEHAVIOR["automne"])
        activity_score = min(100, base_activity * season_data["activity_mod"])

        return {
            "score": round(activity_score),
            "hour": hour,
            "season": season,
            "activity_level": "haute" if activity_score > 60 else "moyenne" if activity_score > 30 else "basse",
            "rut_active": season_data["rut_active"],
            "feeding_probability": season_data["feeding_pct"],
            "peak_hours": [6, 7, 17, 18, 19],
        }


# ══════════════════════════════════════════════════════════
# ENGINE #2 — KeyZone Engine V2
# Detection zones cles amelioree (densite, score qualite)
# ══════════════════════════════════════════════════════════
class KeyZoneEngineV2(BionicEngineV2Base):
    engine_id = "keyzone_v2"
    engine_name = "KeyZone Engine V2"
    version = "2.0"
    weight = 1.5

    ZONE_WEIGHTS = {
        "habitats": 1.3, "rut": 1.5, "repos": 1.2, "alimentation": 1.4,
        "corridors": 0.8, "salines": 1.3, "affuts": 1.1, "peuplements": 0.7,
        "hydro": 0.6, "pentes": 0.5, "trajets": 0.9, "altitude": 0.3,
    }

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        zones = context.get("zones", [])
        layer_counts = {}
        total_weighted = 0
        for z in zones:
            lid = z.get("properties", {}).get("layer_id", "unknown")
            layer_counts[lid] = layer_counts.get(lid, 0) + 1
            total_weighted += self.ZONE_WEIGHTS.get(lid, 0.5)

        diversity = len(layer_counts)
        density_score = min(100, total_weighted * 8)
        diversity_score = min(100, diversity * 14)
        combined = (density_score * 0.6 + diversity_score * 0.4)

        return {
            "score": round(combined),
            "zone_count": len(zones),
            "diversity": diversity,
            "layer_counts": layer_counts,
            "density_rating": "elevee" if combined > 70 else "moyenne" if combined > 40 else "faible",
        }


# ══════════════════════════════════════════════════════════
# ENGINE #3 — Food Deficit Engine
# Analyse deficit alimentaire (NDVI, saisons, pression)
# ══════════════════════════════════════════════════════════
class FoodDeficitEngine(BionicEngineV2Base):
    engine_id = "food_deficit"
    engine_name = "Food Deficit Engine"
    version = "2.0"
    weight = 1.1

    SEASONAL_NDVI = {
        "printemps": 0.55, "ete": 0.75, "automne": 0.50, "hiver": 0.15,
    }

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        season = context.get("season", "automne")
        zones = context.get("zones", [])

        base_ndvi = self.SEASONAL_NDVI.get(season, 0.5)
        feeding_zones = sum(1 for z in zones if z.get("properties", {}).get("layer_id") == "alimentation")
        habitat_zones = sum(1 for z in zones if z.get("properties", {}).get("layer_id") == "habitats")

        food_availability = min(100, base_ndvi * 100 + feeding_zones * 15)
        deficit = max(0, 70 - food_availability)
        score = min(100, 50 + deficit * 0.7 + (10 if feeding_zones == 0 else 0))

        return {
            "score": round(score),
            "ndvi_estimate": round(base_ndvi, 2),
            "feeding_zones": feeding_zones,
            "habitat_zones": habitat_zones,
            "food_availability": round(food_availability),
            "deficit_level": "critique" if deficit > 40 else "modere" if deficit > 20 else "faible",
            "suggestion": "Installer une saline ou un site d'alimentation secondaire" if deficit > 30 else "Ressources alimentaires suffisantes",
        }


# ══════════════════════════════════════════════════════════
# ENGINE #4 — Wind Intelligence Engine
# Analyse vent strategique (direction optimale approche)
# MAINTENU — integre comme moteur isole, pas dans le pipeline TSP
# ══════════════════════════════════════════════════════════
class WindIntelligenceEngine(BionicEngineV2Base):
    engine_id = "wind_intelligence"
    engine_name = "Wind Intelligence Engine"
    version = "2.0"
    weight = 0.8

    CARDINALS = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        weather = context.get("weather", {})
        wind = weather.get("wind", {})
        wind_deg = wind.get("deg", 0)
        wind_speed = wind.get("speed", 0)
        wind_kmh = wind_speed * 3.6

        # Optimal approach: perpendicular to wind or downwind
        optimal_approach = (wind_deg + 180) % 360
        cardinal_idx = round(wind_deg / 45) % 8
        approach_idx = round(optimal_approach / 45) % 8

        # Score: light wind (5-15 km/h) is best, calm or strong is worse
        if 5 <= wind_kmh <= 15:
            wind_score = 85
        elif wind_kmh < 5:
            wind_score = 50  # too calm, scent doesn't disperse
        elif wind_kmh <= 30:
            wind_score = 65
        else:
            wind_score = 30  # too strong

        return {
            "score": wind_score,
            "wind_direction_deg": wind_deg,
            "wind_direction_cardinal": self.CARDINALS[cardinal_idx],
            "wind_speed_kmh": round(wind_kmh, 1),
            "optimal_approach_deg": optimal_approach,
            "optimal_approach_cardinal": self.CARDINALS[approach_idx],
            "condition": "optimale" if wind_score > 70 else "acceptable" if wind_score > 50 else "difficile",
            "advice": f"Approcher depuis le {self.CARDINALS[approach_idx]} (face au vent: {self.CARDINALS[cardinal_idx]})",
        }


# ══════════════════════════════════════════════════════════
# ENGINE #5 — Terrain Engine
# Analyse terrain (pentes, orientation, couvert forestier)
# ══════════════════════════════════════════════════════════
class TerrainEngine(BionicEngineV2Base):
    engine_id = "terrain"
    engine_name = "Terrain Engine"
    version = "2.0"
    weight = 0.9

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        zones = context.get("zones", [])
        bounds = context.get("bounds", {})

        slope_zones = sum(1 for z in zones if z.get("properties", {}).get("layer_id") == "pentes")
        forest_zones = sum(1 for z in zones if z.get("properties", {}).get("layer_id") == "peuplements")
        hydro_zones = sum(1 for z in zones if z.get("properties", {}).get("layer_id") == "hydro")

        # Score based on terrain diversity and cover
        terrain_diversity = min(3, slope_zones) + min(2, forest_zones) + min(2, hydro_zones)
        score = min(100, 30 + terrain_diversity * 10)

        return {
            "score": round(score),
            "slope_zones": slope_zones,
            "forest_zones": forest_zones,
            "hydro_zones": hydro_zones,
            "terrain_diversity": terrain_diversity,
            "walkability": "bonne" if slope_zones <= 2 else "moderee" if slope_zones <= 4 else "difficile",
            "cover_quality": "bonne" if forest_zones >= 2 else "moderee" if forest_zones >= 1 else "faible",
        }


# ══════════════════════════════════════════════════════════
# ENGINE #6 — Human Pressure Engine
# Pression anthropique (routes, batiments, activites)
# ══════════════════════════════════════════════════════════
class HumanPressureEngine(BionicEngineV2Base):
    engine_id = "human_pressure"
    engine_name = "Human Pressure Engine"
    version = "2.0"
    weight = 1.0

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        bounds = context.get("bounds", {})
        zones = context.get("zones", [])

        # Estimate human pressure based on zone types and area characteristics
        lat = (bounds.get("north", 46.82) + bounds.get("south", 46.81)) / 2
        lng = (bounds.get("east", -71.20) + bounds.get("west", -71.21)) / 2

        # Simple pressure model: hash-based deterministic for coordinates
        seed = int(hashlib.md5(f"{lat:.4f},{lng:.4f}".encode()).hexdigest()[:8], 16)
        base_pressure = (seed % 40) + 10  # 10-50

        # More forest cover = less pressure
        forest_count = sum(1 for z in zones if z.get("properties", {}).get("layer_id") in ("peuplements", "habitats"))
        pressure_reduction = min(20, forest_count * 5)
        pressure = max(5, base_pressure - pressure_reduction)

        # Score: HIGH pressure = LOW hunting quality (inverted)
        score = max(0, 100 - pressure)

        return {
            "score": round(score),
            "pressure_level": pressure,
            "pressure_rating": "faible" if pressure < 25 else "moderee" if pressure < 50 else "elevee",
            "forest_buffer": forest_count,
            "recommendation": "Zone a faible pression — favorable" if pressure < 30 else "Pression moderee — prudence recommandee",
        }


# ══════════════════════════════════════════════════════════
# ENGINE #7 — Corridor Continuity Engine
# Fusion/reparation automatique corridors
# ══════════════════════════════════════════════════════════
class CorridorContinuityEngine(BionicEngineV2Base):
    engine_id = "corridor_continuity"
    engine_name = "Corridor Continuity Engine"
    version = "2.0"
    weight = 1.0

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        corridors = context.get("corridors", [])

        total = len(corridors)
        continuous = 0
        with_bands = 0
        densified = 0

        for c in corridors:
            p = c.get("properties", {})
            if p.get("continuity_valid"):
                continuous += 1
            if len(p.get("bands", [])) > 0:
                with_bands += 1
            if p.get("densified"):
                densified += 1

        pct = (continuous / total * 100) if total > 0 else 0
        score = round(pct)

        return {
            "score": score,
            "total_corridors": total,
            "continuous": continuous,
            "with_bands": with_bands,
            "densified": densified,
            "continuity_pct": round(pct, 1),
            "status": "parfaite" if pct == 100 else "bonne" if pct >= 80 else "a ameliorer",
        }


# ══════════════════════════════════════════════════════════
# ENGINE #8 — Global Attractiveness Engine
# Score attractivite global du carre 2km
# ══════════════════════════════════════════════════════════
class GlobalAttractivenessEngine(BionicEngineV2Base):
    engine_id = "global_attractiveness"
    engine_name = "Global Attractiveness Engine"
    version = "2.0"
    weight = 1.3

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        engine_scores = context.get("engine_scores", {})

        # Weighted average of all other engine scores
        total_weight = 0
        weighted_sum = 0
        components = {}
        for engine_id, data in engine_scores.items():
            if engine_id == self.engine_id:
                continue
            s = data.get("score", 50)
            w = data.get("weight", 1.0)
            weighted_sum += s * w
            total_weight += w
            components[engine_id] = {"score": s, "weight": w}

        global_score = (weighted_sum / total_weight) if total_weight > 0 else 50

        return {
            "score": round(global_score),
            "components": components,
            "rating": "excellent" if global_score > 75 else "bon" if global_score > 55 else "moyen" if global_score > 35 else "faible",
            "confidence": min(95, 40 + len(components) * 5),
        }


# ══════════════════════════════════════════════════════════
# ENGINE #9 — Action Plan Engine
# Generation plan d'action chasse
# ══════════════════════════════════════════════════════════
class ActionPlanEngine(BionicEngineV2Base):
    engine_id = "action_plan"
    engine_name = "Action Plan Engine"
    version = "2.0"
    weight = 0.5  # informational, not scoring

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        engine_scores = context.get("engine_scores", {})
        zones = context.get("zones", [])
        corridors = context.get("corridors", [])

        behavior = engine_scores.get("behavior", {})
        food = engine_scores.get("food_deficit", {})
        wind = engine_scores.get("wind_intelligence", {})
        terrain = engine_scores.get("terrain", {})

        steps = []
        steps.append(f"1. Niveau d'activite: {behavior.get('activity_level', 'inconnu')}")
        if behavior.get("rut_active"):
            steps.append("2. Rut actif — concentrer les efforts sur les zones de rut")
        if food.get("deficit_level") in ("critique", "modere"):
            steps.append(f"3. {food.get('suggestion', 'Verifier les ressources alimentaires')}")
        if wind.get("advice"):
            steps.append(f"4. Vent: {wind.get('advice')}")
        steps.append(f"5. Terrain: marchabilite {terrain.get('walkability', 'inconnue')}, couvert {terrain.get('cover_quality', 'inconnu')}")
        steps.append(f"6. {len(zones)} zones et {len(corridors)} corridors identifies")

        return {
            "score": 75,
            "steps": steps,
            "priority": "haute" if behavior.get("rut_active") else "normale",
        }


# ══════════════════════════════════════════════════════════
# ENGINE #10 — Predictive AI Engine
# Predictions probabilistes de presence
# ══════════════════════════════════════════════════════════
class PredictiveAIEngine(BionicEngineV2Base):
    engine_id = "predictive_ai"
    engine_name = "Predictive AI Engine"
    version = "2.0"
    weight = 1.1

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        engine_scores = context.get("engine_scores", {})
        hour = context.get("hour", 12)
        season = context.get("season", "automne")

        # Combine behavioral + habitat + food signals for prediction
        behavior_score = engine_scores.get("behavior", {}).get("score", 50)
        keyzone_score = engine_scores.get("keyzone_v2", {}).get("score", 50)
        food_score = engine_scores.get("food_deficit", {}).get("score", 50)
        pressure_score = engine_scores.get("human_pressure", {}).get("score", 50)

        # Weighted prediction
        prediction = (
            behavior_score * 0.30 +
            keyzone_score * 0.25 +
            food_score * 0.20 +
            pressure_score * 0.25
        )

        # Season + hour modifiers
        if season == "automne" and 5 <= hour <= 8:
            prediction *= 1.15
        elif season == "automne" and 16 <= hour <= 19:
            prediction *= 1.20

        prediction = min(99, max(5, prediction))

        return {
            "score": round(prediction),
            "probability_pct": round(prediction),
            "confidence": "haute" if len(engine_scores) >= 5 else "moyenne",
            "best_window": "aube (5h-8h)" if hour < 12 else "crepuscule (16h-19h)",
            "factors": {
                "behavior": round(behavior_score),
                "habitat": round(keyzone_score),
                "food": round(food_score),
                "pressure": round(pressure_score),
            },
        }


# ══════════════════════════════════════════════════════════
# ENGINE #11 — BCE-4X Compliance Engine
# Validation automatique conformite
# ══════════════════════════════════════════════════════════
class BCEComplianceEngine(BionicEngineV2Base):
    engine_id = "bce_compliance"
    engine_name = "BCE-4X Compliance Engine"
    version = "2.0"
    weight = 0.3  # meta-engine

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from bce.validators.color_contract import validate as validate_color
            from bce.validators.geometry_compliance import validate as validate_geom
            color_result = validate_color()
            geom_result = validate_geom()

            color_pass = color_result.get("status") == "PASS"
            geom_pass = geom_result.get("status") == "PASS"

            total_checks = len(color_result.get("checks", [])) + len(geom_result.get("checks", []))
            passed = sum(1 for c in color_result.get("checks", []) if c["status"] == "PASS")
            passed += sum(1 for c in geom_result.get("checks", []) if c["status"] == "PASS")

            pct = (passed / total_checks * 100) if total_checks > 0 else 0

            return {
                "score": round(pct),
                "color_contract": color_result.get("status"),
                "geometry_compliance": geom_result.get("status"),
                "total_rules": total_checks,
                "passed": passed,
                "compliance_pct": round(pct, 1),
                "status": "conforme" if pct == 100 else "non-conforme",
            }
        except Exception as e:
            return {"score": 0, "error": str(e), "status": "erreur"}


# ══════════════════════════════════════════════════════════
# ENGINE #12 — Rendering Engine
# Optimisation rendu carte
# ══════════════════════════════════════════════════════════
class RenderingEngine(BionicEngineV2Base):
    engine_id = "rendering"
    engine_name = "Rendering Engine"
    version = "2.0"
    weight = 0.2  # meta-engine

    def compute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        zones = context.get("zones", [])
        corridors = context.get("corridors", [])

        total_features = len(zones) + len(corridors)
        # Estimate rendering complexity from feature count
        total_coords = 0
        for c in corridors:
            bands = c.get("properties", {}).get("bands", [])
            if isinstance(bands, list):
                for band in bands:
                    if isinstance(band, dict):
                        coords = band.get("coordinates", [])
                        if isinstance(coords, list):
                            total_coords += sum(len(ring) if isinstance(ring, list) else 0 for ring in coords)

        complexity = "faible" if total_features < 20 else "moyenne" if total_features < 50 else "elevee"
        # Base score on feature count — fewer features = better performance
        if total_features == 0:
            perf_score = 80  # default good
        elif total_coords > 0:
            perf_score = max(30, 100 - total_coords / 50)
        else:
            perf_score = max(40, 100 - total_features * 2)

        return {
            "score": round(min(100, perf_score)),
            "total_features": total_features,
            "total_band_coords": total_coords,
            "complexity": complexity,
            "recommendation": "Rendu optimal" if perf_score > 70 else "Reduire la resolution pour meilleures performances",
        }


# ══════════════════════════════════════════════════════════
# ENGINE REGISTRY — V2
# ══════════════════════════════════════════════════════════
ENGINE_REGISTRY_V2 = {
    "behavior": BehaviorEngine(),
    "keyzone_v2": KeyZoneEngineV2(),
    "food_deficit": FoodDeficitEngine(),
    "wind_intelligence": WindIntelligenceEngine(),
    "terrain": TerrainEngine(),
    "human_pressure": HumanPressureEngine(),
    "corridor_continuity": CorridorContinuityEngine(),
    "global_attractiveness": GlobalAttractivenessEngine(),
    "action_plan": ActionPlanEngine(),
    "predictive_ai": PredictiveAIEngine(),
    "bce_compliance": BCEComplianceEngine(),
    "rendering": RenderingEngine(),
}


def compute_all_engines(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute all 12 BIONIC V2 engines and return combined results.
    Engines #8 (Global Attractiveness), #9 (Action Plan), and #10 (Predictive AI)
    run AFTER others since they depend on previous engine scores.
    """
    results = {}

    # Phase 1: Independent engines (1-7, 11, 12)
    independent = ["behavior", "keyzone_v2", "food_deficit", "wind_intelligence",
                    "terrain", "human_pressure", "corridor_continuity",
                    "bce_compliance", "rendering"]
    for eid in independent:
        engine = ENGINE_REGISTRY_V2.get(eid)
        if engine:
            try:
                result = engine.compute(context)
                result["weight"] = engine.weight
                results[eid] = result
            except Exception as e:
                logger.warning(f"Engine {eid} failed: {e}")
                results[eid] = {"score": 0, "error": str(e), "weight": engine.weight}

    # Phase 2: Dependent engines (need engine_scores)
    context["engine_scores"] = results
    dependent = ["global_attractiveness", "action_plan", "predictive_ai"]
    for eid in dependent:
        engine = ENGINE_REGISTRY_V2.get(eid)
        if engine:
            try:
                result = engine.compute(context)
                result["weight"] = engine.weight
                results[eid] = result
            except Exception as e:
                logger.warning(f"Engine {eid} failed: {e}")
                results[eid] = {"score": 0, "error": str(e), "weight": engine.weight}

    return results


def get_engine_statuses() -> List[Dict[str, Any]]:
    """Return status of all 12 engines."""
    return [engine.status() for engine in ENGINE_REGISTRY_V2.values()]
