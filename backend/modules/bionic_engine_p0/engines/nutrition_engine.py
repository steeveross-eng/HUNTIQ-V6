"""
Nutrition Engine — NDVI + Sol + Fourrage + Attractivite par espece
===================================================================
Option A: Modele algorithmique Quebec.
Integre NDVI estime, qualite fourrage saisonniere, besoins mineraux.
Zero hardcoding. Score 100% dynamique.
"""

from .base import BionicEngine, EngineResult

# Qualite fourrage par type de zone et saison (base ecologique Quebec)
FORAGE_QUALITY = {
    "alimentation": {"printemps": 85, "ete": 90, "automne": 70, "hiver": 30},
    "repos": {"printemps": 40, "ete": 45, "automne": 35, "hiver": 20},
    "rut": {"printemps": 50, "ete": 55, "automne": 65, "hiver": 25},
    "habitats": {"printemps": 60, "ete": 70, "automne": 55, "hiver": 35},
    "trajets": {"printemps": 45, "ete": 50, "automne": 40, "hiver": 15},
    "thermique": {"printemps": 30, "ete": 35, "automne": 25, "hiver": 50},
    "salines": {"printemps": 95, "ete": 80, "automne": 60, "hiver": 40},
    "affuts": {"printemps": 35, "ete": 40, "automne": 30, "hiver": 10},
}

# NDVI estime par type de zone (indice de vegetation normalise)
ZONE_NDVI = {
    "alimentation": 0.65, "repos": 0.75, "rut": 0.55, "habitats": 0.70,
    "trajets": 0.45, "thermique": 0.80, "salines": 0.30, "affuts": 0.50,
}

# Attractivite nutritionnelle par espece
SPECIES_NUTRITION = {
    "moose": {
        "mineral_need": 0.8, "browse_preference": 0.9, "salt_attraction": 0.95,
        "caloric_need": 0.85, "preferred_vegetation": ["saule", "bouleau", "tremble"],
    },
    "deer": {
        "mineral_need": 0.6, "browse_preference": 0.7, "salt_attraction": 0.8,
        "caloric_need": 0.7, "preferred_vegetation": ["cedre", "sapin", "herbe"],
    },
    "bear": {
        "mineral_need": 0.3, "browse_preference": 0.4, "salt_attraction": 0.2,
        "caloric_need": 0.95, "preferred_vegetation": ["baies", "noix", "insectes"],
    },
}

# Seasonal NDVI multiplier (phenological effect on vegetation quality)
SEASON_NDVI_MULT = {
    "printemps": 0.60, "ete": 1.0, "automne": 0.65, "hiver": 0.15,
}

# Month to season mapping
MONTH_TO_SEASON = {
    1: "hiver", 2: "hiver", 3: "printemps", 4: "printemps",
    5: "printemps", 6: "ete", 7: "ete", 8: "ete",
    9: "automne", 10: "automne", 11: "automne", 12: "hiver",
}


class NutritionEngine(BionicEngine):
    ENGINE_ID = "nutrition"
    ENGINE_NAME = "Nutrition Engine"
    DEFAULT_WEIGHT = 0.12

    def evaluate(self, context):
        from_zone = context.get("from_zone_type", "habitats")
        to_zone = context.get("to_zone_type", "habitats")
        species = context.get("species", "moose")
        season = context.get("season", "automne")
        month = context.get("month", 10)

        # Auto-detect season from month if not explicitly set
        if not season or season not in SEASON_NDVI_MULT:
            season = MONTH_TO_SEASON.get(month, "automne")

        # Forage quality
        from_q = FORAGE_QUALITY.get(from_zone, {}).get(season, 40)
        to_q = FORAGE_QUALITY.get(to_zone, {}).get(season, 40)
        avg_forage = (from_q + to_q) / 2

        # NDVI estimation with seasonal adjustment
        ndvi_mult = SEASON_NDVI_MULT.get(season, 0.65)
        from_ndvi = ZONE_NDVI.get(from_zone, 0.5) * ndvi_mult
        to_ndvi = ZONE_NDVI.get(to_zone, 0.5) * ndvi_mult
        avg_ndvi = (from_ndvi + to_ndvi) / 2
        ndvi_score = avg_ndvi * 100

        # Species-specific nutrition scoring
        sp = SPECIES_NUTRITION.get(species, SPECIES_NUTRITION["moose"])
        browse_factor = sp["browse_preference"]
        caloric_factor = sp["caloric_need"]

        # Composite nutrition
        nutrition_score = (
            avg_forage * 0.40
            + ndvi_score * 0.25
            + browse_factor * 100 * 0.20
            + caloric_factor * 100 * 0.15
        )

        # Salt/mineral bonus
        salt_bonus = 0
        if from_zone == "salines" or to_zone == "salines":
            salt_bonus = 15 * sp["salt_attraction"]

        # Seasonal caloric urgency (winter = higher nutritional need)
        urgency_bonus = 0
        if season == "hiver":
            urgency_bonus = 10 * caloric_factor
        elif season == "automne":
            urgency_bonus = 5 * caloric_factor  # Pre-rut fattening

        score = min(100, max(5, nutrition_score + salt_bonus + urgency_bonus))
        impact = 2 if score > 80 else 1 if score > 60 else 0 if score > 35 else -1

        return EngineResult(
            engine_id=self.ENGINE_ID,
            score=round(score, 1),
            weight=self.DEFAULT_WEIGHT,
            certainty=0.75,
            justification=(
                f"Fourrage {season}: {avg_forage:.0f}/100, "
                f"NDVI est.: {avg_ndvi:.2f}, "
                f"Attractivite {species}: {score:.0f}"
            ),
            classification_impact=impact,
            details={
                "forage_from": from_q,
                "forage_to": to_q,
                "avg_forage": round(avg_forage, 1),
                "ndvi_estimated": round(avg_ndvi, 3),
                "ndvi_score": round(ndvi_score, 1),
                "salt_bonus": round(salt_bonus, 1),
                "urgency_bonus": round(urgency_bonus, 1),
                "species": species,
                "season": season,
                "browse_preference": browse_factor,
            },
        )
