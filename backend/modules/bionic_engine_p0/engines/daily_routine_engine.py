"""
Daily Routine Engine — Rythmes circadiens par espece
======================================================
Fenetres d'activite: aube, jour, crepuscule, nuit.
Integre cycles saisonniers et effets du rut.
"""

import math
from .base import BionicEngine, EngineResult

# Fenetres d'activite par espece (score 0-100 pour chaque periode)
ACTIVITY_WINDOWS = {
    "moose": {"dawn": 90, "day": 35, "dusk": 95, "night": 50},
    "deer": {"dawn": 85, "day": 25, "dusk": 90, "night": 60},
    "bear": {"dawn": 70, "day": 55, "dusk": 75, "night": 30},
}

# Zones preferees par periode (affinite corridor-temps)
ZONE_PERIOD_AFFINITY = {
    "dawn": {"alimentation": 90, "trajets": 80, "habitats": 50, "repos": 20, "salines": 85, "affuts": 30, "rut": 60, "thermique": 25},
    "day": {"repos": 90, "thermique": 85, "habitats": 50, "alimentation": 30, "trajets": 20, "affuts": 15, "rut": 25, "salines": 40},
    "dusk": {"alimentation": 90, "trajets": 85, "rut": 80, "habitats": 60, "salines": 75, "affuts": 40, "repos": 20, "thermique": 30},
    "night": {"repos": 80, "habitats": 70, "thermique": 60, "alimentation": 40, "trajets": 30, "rut": 65, "affuts": 10, "salines": 25},
}

# Seasonal activity modification (rut period increases movement)
SEASON_ACTIVITY_MOD = {
    "moose": {"printemps": 1.0, "ete": 0.9, "automne": 1.3, "hiver": 0.7},  # Rut Oct
    "deer": {"printemps": 1.0, "ete": 0.9, "automne": 1.2, "hiver": 0.6},   # Rut Nov
    "bear": {"printemps": 1.4, "ete": 1.1, "automne": 1.3, "hiver": 0.0},   # Hibernate
}

# Sunrise/sunset hours by month (Quebec approximate)
DAYLIGHT_HOURS = {
    1: (7, 16), 2: (7, 17), 3: (6, 18), 4: (6, 19),
    5: (5, 20), 6: (5, 21), 7: (5, 21), 8: (6, 20),
    9: (6, 19), 10: (7, 18), 11: (7, 16), 12: (7, 16),
}

MONTH_TO_SEASON = {
    1: "hiver", 2: "hiver", 3: "printemps", 4: "printemps",
    5: "printemps", 6: "ete", 7: "ete", 8: "ete",
    9: "automne", 10: "automne", 11: "automne", 12: "hiver",
}


class DailyRoutineEngine(BionicEngine):
    ENGINE_ID = "daily_routine"
    ENGINE_NAME = "Daily Routine Engine"
    DEFAULT_WEIGHT = 0.10

    def evaluate(self, context):
        species = context.get("species", "moose")
        hour = context.get("hour", 6)
        month = context.get("month", 10)
        from_zone = context.get("from_zone_type", "habitats")
        to_zone = context.get("to_zone_type", "habitats")
        season = context.get("season", "automne")

        if not season or season not in SEASON_ACTIVITY_MOD.get(species, {}):
            season = MONTH_TO_SEASON.get(month, "automne")

        # Determine period based on actual daylight for the month
        sunrise, sunset = DAYLIGHT_HOURS.get(month, (6, 18))
        period = self._get_period_dynamic(hour, sunrise, sunset)

        # Base activity level
        sp_windows = ACTIVITY_WINDOWS.get(species, ACTIVITY_WINDOWS["moose"])
        activity_level = sp_windows[period]

        # Seasonal modifier
        season_mod = SEASON_ACTIVITY_MOD.get(species, {}).get(season, 1.0)
        activity_level = min(100, activity_level * season_mod)

        # Bear hibernation check
        if species == "bear" and season == "hiver":
            return EngineResult(
                engine_id=self.ENGINE_ID,
                score=5.0,
                weight=self.DEFAULT_WEIGHT,
                certainty=0.95,
                justification="Ours en hibernation - aucun deplacement",
                classification_impact=-2,
                details={"period": "hibernation", "activity_level": 0, "species": species},
            )

        # Zone affinity for this period
        zone_affinity = ZONE_PERIOD_AFFINITY.get(period, {})
        from_aff = zone_affinity.get(from_zone, 40)
        to_aff = zone_affinity.get(to_zone, 40)
        corridor_relevance = (from_aff + to_aff) / 2

        # Movement urgency: dawn/dusk corridors between food and rest are critical
        urgency_bonus = 0
        if period in ("dawn", "dusk"):
            if (from_zone == "alimentation" and to_zone == "repos") or \
               (from_zone == "repos" and to_zone == "alimentation"):
                urgency_bonus = 15

        score = min(100, max(5, activity_level * 0.50 + corridor_relevance * 0.35 + urgency_bonus))
        impact = 1 if score > 70 else 0 if score > 40 else -1

        return EngineResult(
            engine_id=self.ENGINE_ID,
            score=round(score, 1),
            weight=self.DEFAULT_WEIGHT,
            certainty=0.70,
            justification=(
                f"Periode {period} ({hour}h): activite={activity_level:.0f} (x{season_mod:.1f} {season}), "
                f"pertinence corridor={corridor_relevance:.0f}"
            ),
            classification_impact=impact,
            details={
                "period": period,
                "hour": hour,
                "sunrise": sunrise,
                "sunset": sunset,
                "activity_level": round(activity_level, 1),
                "season_modifier": season_mod,
                "corridor_relevance": round(corridor_relevance, 1),
                "urgency_bonus": urgency_bonus,
                "species": species,
            },
        )

    @staticmethod
    def _get_period_dynamic(hour, sunrise, sunset):
        """Determine period using actual sunrise/sunset hours."""
        dawn_start = sunrise - 1
        dawn_end = sunrise + 1
        dusk_start = sunset - 1
        dusk_end = sunset + 1

        if dawn_start <= hour < dawn_end:
            return "dawn"
        elif dawn_end <= hour < dusk_start:
            return "day"
        elif dusk_start <= hour < dusk_end:
            return "dusk"
        return "night"
