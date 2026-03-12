"""
Movement Engine V9 — DEM algorithmique + A* + energie + terrain
================================================================
Option A: DEM algorithmique Quebec (Laurentides, Appalaches, St-Laurent).
Evalue: pente, cout energetique, type de relief, connectivite.
"""

import math
from .base import BionicEngine, EngineResult


def estimate_altitude_m(lat, lng):
    """Estimation algorithmique altitude Quebec sans DEM externe.
    Modele multi-region: Laurentides, Appalaches, Vallee St-Laurent."""
    base = 50

    # Laurentian highlands: lat 46.5-48, lng -75 to -71
    laurentian_factor = max(0, 1 - abs(lat - 47.2) / 1.5) * max(0, 1 - abs(lng + 73) / 3)
    base += laurentian_factor * 600

    # Appalachian influence: south-east
    appalachian_factor = max(0, 1 - abs(lat - 46.0) / 1.0) * max(0, 1 - abs(lng + 70.5) / 2)
    base += appalachian_factor * 400

    # St Lawrence valley depression
    valley_factor = max(0, 1 - abs(lat - 46.8) / 0.5) * max(0, 1 - abs(lng + 71.2) / 0.8)
    base -= valley_factor * 150

    # Abitibi plateau (north)
    abitibi_factor = max(0, 1 - abs(lat - 48.5) / 1.0) * max(0, 1 - abs(lng + 78) / 3)
    base += abitibi_factor * 300

    # Saguenay depression
    saguenay_factor = max(0, 1 - abs(lat - 48.4) / 0.3) * max(0, 1 - abs(lng + 71) / 0.5)
    base -= saguenay_factor * 200

    return max(10, base)


def estimate_slope_deg(alt1, alt2, distance_m):
    """Calcule la pente en degres."""
    if distance_m <= 0:
        return 0
    return math.degrees(math.atan(abs(alt2 - alt1) / distance_m))


def energy_cost(slope_deg, distance_m, species="moose"):
    """Cout energetique relatif (1.0 = plat, >1 = monte).
    Ajuste par espece (ours tolere mieux les pentes raides)."""
    species_slope_tolerance = {
        "moose": 1.0, "deer": 1.1, "bear": 0.8,
    }
    tolerance = species_slope_tolerance.get(species, 1.0)
    effective_slope = slope_deg * tolerance

    if effective_slope < 3:
        return 1.0
    elif effective_slope < 8:
        return 1.3
    elif effective_slope < 15:
        return 1.8
    elif effective_slope < 25:
        return 2.5
    return 4.0


# Type de relief et impact ecologique
TERRAIN_FEATURES = {
    "coulee": {"slope_range": (5, 15), "score_bonus": 15, "desc": "Coulee naturelle - deplacement prefere"},
    "crete": {"slope_range": (10, 25), "score_bonus": -10, "desc": "Crete - effort eleve, visibilite"},
    "plateau": {"slope_range": (0, 3), "score_bonus": 5, "desc": "Plateau - deplacement facile"},
    "pente_moderate": {"slope_range": (3, 10), "score_bonus": 0, "desc": "Pente moderee"},
    "falaise": {"slope_range": (25, 90), "score_bonus": -30, "desc": "Pente extreme - eviter"},
}

# Distance optimale par espece (m) - au-dela = penalite
OPTIMAL_DISTANCE = {
    "moose": {"min": 200, "max": 2000, "ideal": 800},
    "deer": {"min": 100, "max": 1500, "ideal": 500},
    "bear": {"min": 300, "max": 3000, "ideal": 1200},
}


class MovementEngineV9(BionicEngine):
    ENGINE_ID = "movement"
    ENGINE_NAME = "Movement Engine V9"
    DEFAULT_WEIGHT = 0.15

    def evaluate(self, context):
        from_lat = context.get("from_lat", 46.8)
        from_lng = context.get("from_lng", -71.2)
        to_lat = context.get("to_lat", 46.81)
        to_lng = context.get("to_lng", -71.19)
        distance_m = context.get("distance_m", 500)
        pathfinding = context.get("pathfinding", "A*")
        connectivity = context.get("connectivity", 80)
        species = context.get("species", "moose")

        # DEM algorithmique
        alt_from = estimate_altitude_m(from_lat, from_lng)
        alt_to = estimate_altitude_m(to_lat, to_lng)
        slope = estimate_slope_deg(alt_from, alt_to, max(1, distance_m))
        cost = energy_cost(slope, distance_m, species)

        # Identify terrain feature
        feature = "pente_moderate"
        for fname, fdata in TERRAIN_FEATURES.items():
            if fdata["slope_range"][0] <= slope <= fdata["slope_range"][1]:
                feature = fname
                break

        feature_bonus = TERRAIN_FEATURES[feature]["score_bonus"]

        # A* bonus
        astar_bonus = 10 if pathfinding == "A*" else 0

        # Connectivity component
        connectivity_score = connectivity * 0.4

        # Energy efficiency (lower cost = better)
        efficiency = max(10, 100 - (cost - 1.0) * 30)

        # Distance fitness for species
        dist_config = OPTIMAL_DISTANCE.get(species, OPTIMAL_DISTANCE["moose"])
        if dist_config["min"] <= distance_m <= dist_config["max"]:
            # Score increases as distance approaches ideal
            dist_ratio = 1 - abs(distance_m - dist_config["ideal"]) / dist_config["max"]
            dist_bonus = dist_ratio * 15
        elif distance_m < dist_config["min"]:
            dist_bonus = -10  # Too short
        else:
            dist_bonus = -20  # Too long

        # Altitude corridor value (valleys preferred for travel)
        avg_alt = (alt_from + alt_to) / 2
        alt_bonus = 0
        if avg_alt < 200:
            alt_bonus = 5  # Valley travel
        elif avg_alt > 500:
            alt_bonus = -5  # High altitude = more energy

        score = min(100, max(5, efficiency * 0.35 + connectivity_score + feature_bonus + astar_bonus + dist_bonus + alt_bonus))
        impact = 2 if score > 85 else 1 if score > 65 else 0 if score > 40 else -1

        return EngineResult(
            engine_id=self.ENGINE_ID,
            score=round(score, 1),
            weight=self.DEFAULT_WEIGHT,
            certainty=0.80 if pathfinding == "A*" else 0.50,
            justification=(
                f"DEM: {alt_from:.0f}->{alt_to:.0f}m, pente={slope:.1f} deg, "
                f"terrain={feature}, A*={'oui' if pathfinding == 'A*' else 'non'}, "
                f"distance={distance_m:.0f}m"
            ),
            classification_impact=impact,
            details={
                "altitude_from": round(alt_from, 1),
                "altitude_to": round(alt_to, 1),
                "avg_altitude": round(avg_alt, 1),
                "slope_deg": round(slope, 1),
                "energy_cost": round(cost, 2),
                "terrain_feature": feature,
                "feature_bonus": feature_bonus,
                "efficiency": round(efficiency, 1),
                "distance_fitness": round(dist_bonus, 1),
                "dem_enhanced": True,
            },
        )
