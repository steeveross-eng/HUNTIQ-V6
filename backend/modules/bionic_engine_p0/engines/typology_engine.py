"""
Typology Engine — Profils comportementaux par espece et saison
===============================================================
5 profils: conservateur, explorateur, nocturne, opportuniste, territorial.
Affecte la longueur, la couverture et le risque des corridors.
"""

from .base import BionicEngine, EngineResult

BEHAVIORAL_PROFILES = {
    "conservateur": {
        "risk_tolerance": 0.2, "exploration_range_m": 500,
        "preferred_cover": 0.8, "night_activity": 0.3,
        "corridor_score_mod": -5,
        "desc": "Prefere les corridors courts, couverts et securises",
    },
    "explorateur": {
        "risk_tolerance": 0.7, "exploration_range_m": 2000,
        "preferred_cover": 0.4, "night_activity": 0.5,
        "corridor_score_mod": 10,
        "desc": "Utilise des corridors longs et varies",
    },
    "nocturne": {
        "risk_tolerance": 0.5, "exploration_range_m": 1200,
        "preferred_cover": 0.6, "night_activity": 0.9,
        "corridor_score_mod": 5,
        "desc": "Deplacements principalement nocturnes",
    },
    "opportuniste": {
        "risk_tolerance": 0.6, "exploration_range_m": 1500,
        "preferred_cover": 0.5, "night_activity": 0.6,
        "corridor_score_mod": 8,
        "desc": "Adapte son comportement aux opportunites",
    },
    "territorial": {
        "risk_tolerance": 0.3, "exploration_range_m": 800,
        "preferred_cover": 0.7, "night_activity": 0.4,
        "corridor_score_mod": -3,
        "desc": "Corridors reguliers dans un territoire restreint",
    },
}

SPECIES_DOMINANT_PROFILE = {
    "moose": "territorial",
    "deer": "conservateur",
    "bear": "explorateur",
}

# Seasonal profile overrides
SEASON_PROFILE_OVERRIDE = {
    "moose": {
        "automne": "explorateur",    # Rut: males explore widely
        "printemps": "territorial",  # Calving: females stay close
    },
    "deer": {
        "automne": "explorateur",    # Rut: November
        "hiver": "conservateur",     # Yard up: minimal movement
    },
    "bear": {
        "printemps": "explorateur",  # Post-hibernation: wide search
        "automne": "opportuniste",   # Hyperphagia: eat everything
        "hiver": "conservateur",     # Pre-hibernation (if not yet denned)
    },
}

MONTH_TO_SEASON = {
    1: "hiver", 2: "hiver", 3: "printemps", 4: "printemps",
    5: "printemps", 6: "ete", 7: "ete", 8: "ete",
    9: "automne", 10: "automne", 11: "automne", 12: "hiver",
}


class TypologyEngine(BionicEngine):
    ENGINE_ID = "typology"
    ENGINE_NAME = "Typology Engine"
    DEFAULT_WEIGHT = 0.08

    def evaluate(self, context):
        species = context.get("species", "moose")
        distance_m = context.get("distance_m", 500)
        season = context.get("season", "automne")
        month = context.get("month", 10)
        hour = context.get("hour", 6)

        if not season or season not in ("printemps", "ete", "automne", "hiver"):
            season = MONTH_TO_SEASON.get(month, "automne")

        # Determine behavioral profile
        profile_key = SPECIES_DOMINANT_PROFILE.get(species, "opportuniste")
        overrides = SEASON_PROFILE_OVERRIDE.get(species, {})
        if season in overrides:
            profile_key = overrides[season]

        # Nocturnal override
        if hour >= 22 or hour < 5:
            if BEHAVIORAL_PROFILES.get(profile_key, {}).get("night_activity", 0) < 0.5:
                profile_key = "nocturne"

        profile = BEHAVIORAL_PROFILES[profile_key]

        # Distance fit
        range_m = profile["exploration_range_m"]
        range_ratio = distance_m / range_m
        if range_ratio <= 1.0:
            distance_fit = 80 + (1 - range_ratio) * 20
        else:
            distance_fit = max(10, 80 - (range_ratio - 1) * 40)

        # Risk assessment for corridor
        risk_penalty = 0
        if distance_m > range_m * 1.5:
            risk_penalty = -15 * (1 - profile["risk_tolerance"])

        # Cover preference match
        cover_match = profile["preferred_cover"] * 100 * 0.15

        score = min(100, max(5, distance_fit + profile["corridor_score_mod"] + risk_penalty + cover_match))
        impact = 1 if score > 70 else 0 if score > 40 else -1

        return EngineResult(
            engine_id=self.ENGINE_ID,
            score=round(score, 1),
            weight=self.DEFAULT_WEIGHT,
            certainty=0.50,
            justification=(
                f"Profil {profile_key}: {profile['desc']}. "
                f"Distance fit: {distance_fit:.0f}, Range: {range_m}m"
            ),
            classification_impact=impact,
            details={
                "profile": profile_key,
                "risk_tolerance": profile["risk_tolerance"],
                "exploration_range_m": range_m,
                "distance_fit": round(distance_fit, 1),
                "risk_penalty": round(risk_penalty, 1),
                "cover_preference": profile["preferred_cover"],
                "night_activity": profile["night_activity"],
                "season": season,
            },
        )
