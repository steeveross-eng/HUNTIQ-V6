"""
Disturbance Engine — Pression humaine, routes, structures, odeurs
==================================================================
Option A: Modele algorithmique. Calcul de pression humaine
a partir des types de zones, latitude, et estimations spatiales.
5 facteurs: route, activite humaine, bruit/odeur, sentiers, structures.
Score INVERSE: haute pression = faible score corridor.
"""

import math
from .base import BionicEngine, EngineResult

# Pression humaine de base par type de zone (0 = sauvage, 100 = urbain)
ZONE_DISTURBANCE = {
    "alimentation": 10, "repos": 5, "rut": 8, "habitats": 15,
    "trajets": 25, "thermique": 3, "salines": 20, "affuts": 12,
}

# Facteurs de perturbation et leurs poids
DISTURBANCE_FACTORS = {
    "road_proximity": {"weight": 0.30, "threshold_m": 500, "desc": "Proximite routes"},
    "human_activity": {"weight": 0.25, "threshold_m": 1000, "desc": "Activite humaine"},
    "noise_olfactory": {"weight": 0.20, "threshold_m": 300, "desc": "Bruit et odeurs"},
    "trail_proximity": {"weight": 0.15, "threshold_m": 200, "desc": "Sentiers"},
    "structure_proximity": {"weight": 0.10, "threshold_m": 400, "desc": "Structures"},
}

# Seasonal hunting pressure multiplier (Quebec hunting seasons)
HUNTING_PRESSURE = {
    "printemps": 0.3,   # Spring bear
    "ete": 0.1,         # Low
    "automne": 1.0,     # Peak: moose, deer season
    "hiver": 0.4,       # Some trapping
}

# Species sensitivity to disturbance
SPECIES_SENSITIVITY = {
    "moose": {"road": 0.8, "noise": 0.7, "human": 0.9, "flight_dist_m": 300},
    "deer": {"road": 0.6, "noise": 0.8, "human": 0.7, "flight_dist_m": 150},
    "bear": {"road": 0.5, "noise": 0.6, "human": 0.8, "flight_dist_m": 200},
}

# Month to season mapping
MONTH_TO_SEASON = {
    1: "hiver", 2: "hiver", 3: "printemps", 4: "printemps",
    5: "printemps", 6: "ete", 7: "ete", 8: "ete",
    9: "automne", 10: "automne", 11: "automne", 12: "hiver",
}


class DisturbanceEngine(BionicEngine):
    ENGINE_ID = "disturbance"
    ENGINE_NAME = "Disturbance Engine"
    DEFAULT_WEIGHT = 0.12

    def evaluate(self, context):
        from_zone = context.get("from_zone_type", "habitats")
        to_zone = context.get("to_zone_type", "habitats")
        distance_m = context.get("distance_m", 500)
        lat = context.get("lat", 46.8)
        lng = context.get("lng", -71.2)
        species = context.get("species", "moose")
        season = context.get("season", "automne")
        month = context.get("month", 10)
        hour = context.get("hour", 6)

        if not season or season not in HUNTING_PRESSURE:
            season = MONTH_TO_SEASON.get(month, "automne")

        sp = SPECIES_SENSITIVITY.get(species, SPECIES_SENSITIVITY["moose"])

        # Base zone disturbance
        from_dist = ZONE_DISTURBANCE.get(from_zone, 20)
        to_dist = ZONE_DISTURBANCE.get(to_zone, 20)
        zone_pressure = (from_dist + to_dist) / 2

        # Road proximity estimate (longer corridors = higher road crossing probability)
        road_factor = min(40, distance_m / 100) * sp["road"]

        # Algorithmic human pressure based on latitude (southern Quebec = more populated)
        latitude_pressure = max(0, (47.5 - lat) * 15) * sp["human"]

        # Longitude effect (St. Lawrence corridor = more pressure)
        longitude_pressure = 0
        if -72.0 < lng < -70.0:
            longitude_pressure = 10 * sp["human"]

        # Time-of-day effect (daytime = more human activity)
        time_factor = 1.0
        if 8 <= hour <= 17:
            time_factor = 1.5  # Peak human activity
        elif 6 <= hour < 8 or 17 < hour <= 20:
            time_factor = 1.2  # Transition
        else:
            time_factor = 0.5  # Night - minimal human activity

        # Hunting season pressure
        hunting_mult = HUNTING_PRESSURE.get(season, 0.5)

        # Noise/olfactory disturbance estimate
        noise_factor = zone_pressure * sp["noise"] * time_factor * 0.3

        total_pressure = (
            zone_pressure * 0.30
            + road_factor * 0.25
            + latitude_pressure * 0.15
            + longitude_pressure * 0.05
            + noise_factor * 0.15
            + hunting_mult * 20 * 0.10
        )
        total_pressure = min(100, max(0, total_pressure * time_factor))

        # Score is INVERTED: high pressure = low corridor score
        score = max(5, 100 - total_pressure)
        impact = 1 if score > 70 else 0 if score > 45 else -1 if score > 25 else -2

        # Identify dominant disturbance sources
        sources = []
        if road_factor > 15:
            sources.append("route_probable")
        if latitude_pressure > 10:
            sources.append("zone_habitee")
        if zone_pressure > 20:
            sources.append("activite_humaine_zone")
        if hunting_mult > 0.5:
            sources.append(f"pression_chasse_{season}")
        if time_factor > 1.0:
            sources.append("heures_activite_humaine")
        if noise_factor > 10:
            sources.append("bruit_odeur")

        return EngineResult(
            engine_id=self.ENGINE_ID,
            score=round(score, 1),
            weight=self.DEFAULT_WEIGHT,
            certainty=0.55,
            justification=(
                f"Pression: zone={zone_pressure:.0f}, route={road_factor:.0f}, "
                f"latitude={latitude_pressure:.0f}, chasse={hunting_mult:.1f}. "
                f"Sources: {', '.join(sources) or 'aucune'}"
            ),
            classification_impact=impact,
            details={
                "zone_pressure": round(zone_pressure, 1),
                "road_factor": round(road_factor, 1),
                "latitude_pressure": round(latitude_pressure, 1),
                "longitude_pressure": round(longitude_pressure, 1),
                "noise_factor": round(noise_factor, 1),
                "hunting_pressure": hunting_mult,
                "time_factor": time_factor,
                "total_pressure": round(total_pressure, 1),
                "sources": sources,
                "species_sensitivity": sp,
            },
        )
