"""
Habitat Enhancement Engine — Sol + Recommandations d'amelioration
==================================================================
Mineraux, chaux, semis, drainage. Analyse par zone et espece.
Produit des recommandations concretes pour ameliorer l'habitat.
"""

from .base import BionicEngine, EngineResult

# Qualite sol estimee par type de zone Quebec
SOIL_QUALITY = {
    "alimentation": {"ph": 5.8, "minerals": 65, "organic": 70, "drainage": "bon", "texture": "loam"},
    "repos": {"ph": 5.5, "minerals": 50, "organic": 60, "drainage": "modere", "texture": "argile"},
    "rut": {"ph": 5.6, "minerals": 55, "organic": 55, "drainage": "variable", "texture": "loam"},
    "habitats": {"ph": 5.7, "minerals": 60, "organic": 65, "drainage": "bon", "texture": "sable_loam"},
    "trajets": {"ph": 5.3, "minerals": 40, "organic": 45, "drainage": "faible", "texture": "sable"},
    "thermique": {"ph": 5.4, "minerals": 55, "organic": 75, "drainage": "modere", "texture": "argile_loam"},
    "salines": {"ph": 6.2, "minerals": 85, "organic": 50, "drainage": "variable", "texture": "loam"},
    "affuts": {"ph": 5.5, "minerals": 45, "organic": 50, "drainage": "modere", "texture": "sable_loam"},
}

# Recommendations with priority levels
RECOMMENDATIONS = {
    "low_ph": {"action": "Chaulage recommande (2-3 tonnes/ha)", "priority": "haute", "threshold": 5.4, "cost": "modere"},
    "low_minerals": {"action": "Supplement mineral (bloc a sel + mineraux traces)", "priority": "moyenne", "threshold": 50, "cost": "faible"},
    "low_organic": {"action": "Semis fourrager (trefle, luzerne, panic erige)", "priority": "moyenne", "threshold": 50, "cost": "modere"},
    "poor_drainage": {"action": "Amenagement drainage (fosses, pontceaux)", "priority": "basse", "cost": "eleve"},
    "corridor_planting": {"action": "Plantation corridor boise (epinette, bouleau)", "priority": "haute", "cost": "eleve"},
}

# Species-specific habitat needs
SPECIES_HABITAT_NEEDS = {
    "moose": {
        "browse_height_m": 2.5, "cover_need": 0.6, "water_proximity_m": 500,
        "preferred_stand": "mixed_regeneration",
    },
    "deer": {
        "browse_height_m": 1.5, "cover_need": 0.7, "water_proximity_m": 300,
        "preferred_stand": "cedar_fir",
    },
    "bear": {
        "browse_height_m": 0.5, "cover_need": 0.5, "water_proximity_m": 200,
        "preferred_stand": "berry_producing",
    },
}


class HabitatEnhancementEngine(BionicEngine):
    ENGINE_ID = "habitat_enhancement"
    ENGINE_NAME = "Habitat Enhancement Engine"
    DEFAULT_WEIGHT = 0.05

    def evaluate(self, context):
        from_zone = context.get("from_zone_type", "habitats")
        to_zone = context.get("to_zone_type", "habitats")
        species = context.get("species", "moose")
        distance_m = context.get("distance_m", 500)

        from_soil = SOIL_QUALITY.get(from_zone, SOIL_QUALITY["habitats"])
        to_soil = SOIL_QUALITY.get(to_zone, SOIL_QUALITY["habitats"])

        avg_minerals = (from_soil["minerals"] + to_soil["minerals"]) / 2
        avg_ph = (from_soil["ph"] + to_soil["ph"]) / 2
        avg_organic = (from_soil["organic"] + to_soil["organic"]) / 2

        # Species habitat needs
        sp = SPECIES_HABITAT_NEEDS.get(species, SPECIES_HABITAT_NEEDS["moose"])

        # Composite soil score
        soil_score = (
            avg_minerals * 0.35
            + avg_organic * 0.25
            + min(100, avg_ph * 15) * 0.25
            + sp["cover_need"] * 100 * 0.15
        )

        # Corridor enhancement potential
        corridor_potential = 0
        if distance_m > 500 and avg_organic < 60:
            corridor_potential = 15  # Long corridor with poor soil = high enhancement potential

        score = min(100, max(5, soil_score + corridor_potential))

        # Generate recommendations
        recs = []
        if avg_ph < RECOMMENDATIONS["low_ph"]["threshold"]:
            recs.append({"action": RECOMMENDATIONS["low_ph"]["action"], "priority": "haute"})
        if avg_minerals < RECOMMENDATIONS["low_minerals"]["threshold"]:
            recs.append({"action": RECOMMENDATIONS["low_minerals"]["action"], "priority": "moyenne"})
        if avg_organic < RECOMMENDATIONS["low_organic"]["threshold"]:
            recs.append({"action": RECOMMENDATIONS["low_organic"]["action"], "priority": "moyenne"})
        if distance_m > 800:
            recs.append({"action": RECOMMENDATIONS["corridor_planting"]["action"], "priority": "haute"})

        impact = 1 if score > 70 else 0 if score > 40 else -1

        return EngineResult(
            engine_id=self.ENGINE_ID,
            score=round(score, 1),
            weight=self.DEFAULT_WEIGHT,
            certainty=0.45,
            justification=(
                f"Sol: pH={avg_ph:.1f}, Mineraux={avg_minerals:.0f}, "
                f"Organique={avg_organic:.0f}. {len(recs)} recommandation(s)"
            ),
            classification_impact=impact,
            details={
                "avg_ph": round(avg_ph, 2),
                "avg_minerals": round(avg_minerals, 1),
                "avg_organic": round(avg_organic, 1),
                "soil_score": round(soil_score, 1),
                "corridor_potential": corridor_potential,
                "recommendations": recs,
                "species_needs": sp,
            },
        )
