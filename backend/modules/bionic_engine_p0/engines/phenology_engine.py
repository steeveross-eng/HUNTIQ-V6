"""
Phenology Engine — Cycles vegetatifs, NDVI saisonnier, couvert
================================================================
Modele phenologique Quebec: debourrement, floraison, senescence.
NDVI estime par zone et densite de vegetation mensuelle.
"""

from .base import BionicEngine, EngineResult

# Phenologie Quebec par mois
PHENOLOGY_PHASES = {
    1: {"phase": "dormance", "forage_quality": 15, "vegetation_density": 0.20, "cover_value": 0.70},
    2: {"phase": "dormance", "forage_quality": 12, "vegetation_density": 0.15, "cover_value": 0.65},
    3: {"phase": "pre_debourrement", "forage_quality": 20, "vegetation_density": 0.25, "cover_value": 0.55},
    4: {"phase": "debourrement", "forage_quality": 45, "vegetation_density": 0.40, "cover_value": 0.50},
    5: {"phase": "floraison", "forage_quality": 75, "vegetation_density": 0.70, "cover_value": 0.75},
    6: {"phase": "pleine_vegetation", "forage_quality": 90, "vegetation_density": 0.90, "cover_value": 0.90},
    7: {"phase": "pleine_vegetation", "forage_quality": 95, "vegetation_density": 0.95, "cover_value": 0.95},
    8: {"phase": "maturation", "forage_quality": 85, "vegetation_density": 0.90, "cover_value": 0.90},
    9: {"phase": "senescence_debut", "forage_quality": 65, "vegetation_density": 0.70, "cover_value": 0.80},
    10: {"phase": "senescence", "forage_quality": 45, "vegetation_density": 0.50, "cover_value": 0.70},
    11: {"phase": "senescence_fin", "forage_quality": 25, "vegetation_density": 0.30, "cover_value": 0.60},
    12: {"phase": "dormance", "forage_quality": 18, "vegetation_density": 0.20, "cover_value": 0.65},
}

# NDVI de base par type de zone
ZONE_NDVI_BASE = {
    "alimentation": 0.65, "repos": 0.75, "rut": 0.55, "habitats": 0.70,
    "trajets": 0.45, "thermique": 0.80, "salines": 0.30, "affuts": 0.50,
}

# Species movement patterns during phenological phases
SPECIES_PHENOLOGY_RESPONSE = {
    "moose": {
        "debourrement": 1.2,     # New growth attracts
        "pleine_vegetation": 1.0,
        "senescence": 1.3,       # Rut period overlap
        "dormance": 0.7,         # Reduced movement in winter
    },
    "deer": {
        "debourrement": 1.1,
        "pleine_vegetation": 1.0,
        "senescence": 1.2,       # November rut
        "dormance": 0.5,         # Yard up in winter
    },
    "bear": {
        "debourrement": 1.5,     # Emerging from hibernation
        "pleine_vegetation": 1.1,
        "senescence": 1.4,       # Hyperphagia
        "dormance": 0.0,         # Hibernate
    },
}


class PhenologyEngine(BionicEngine):
    ENGINE_ID = "phenology"
    ENGINE_NAME = "Phenology Engine"
    DEFAULT_WEIGHT = 0.08

    def evaluate(self, context):
        month = context.get("month", 10)
        from_zone = context.get("from_zone_type", "habitats")
        to_zone = context.get("to_zone_type", "habitats")
        species = context.get("species", "moose")

        pheno = PHENOLOGY_PHASES.get(month, PHENOLOGY_PHASES[6])
        forage = pheno["forage_quality"]
        veg_density = pheno["vegetation_density"]
        cover_value = pheno["cover_value"]
        phase = pheno["phase"]

        # NDVI estime
        from_ndvi = ZONE_NDVI_BASE.get(from_zone, 0.5) * veg_density
        to_ndvi = ZONE_NDVI_BASE.get(to_zone, 0.5) * veg_density
        avg_ndvi = (from_ndvi + to_ndvi) / 2

        # Cover score (concealment value for corridor transit)
        cover_score = cover_value * 100

        # Species phenological response
        sp_response = SPECIES_PHENOLOGY_RESPONSE.get(species, {})
        # Match phase to response key
        phase_key = phase
        for key in sp_response:
            if key in phase:
                phase_key = key
                break
        response_mult = sp_response.get(phase_key, 1.0)

        # Bear hibernation override
        if species == "bear" and phase == "dormance":
            return EngineResult(
                engine_id=self.ENGINE_ID,
                score=5.0,
                weight=self.DEFAULT_WEIGHT,
                certainty=0.95,
                justification=f"Phase: {phase} - Ours en hibernation",
                classification_impact=-2,
                details={"phase": phase, "species": species, "hibernation": True},
            )

        # Score combine fourrage + couvert + reponse espece
        base_score = forage * 0.40 + cover_score * 0.30 + (avg_ndvi * 100) * 0.30
        score = min(100, max(5, base_score * response_mult))
        impact = 1 if score > 65 else 0 if score > 35 else -1

        return EngineResult(
            engine_id=self.ENGINE_ID,
            score=round(score, 1),
            weight=self.DEFAULT_WEIGHT,
            certainty=0.70,
            justification=(
                f"Phase: {phase}, Fourrage: {forage}/100, "
                f"NDVI est.: {avg_ndvi:.2f}, Couvert: {cover_value:.0%}, "
                f"Reponse {species}: x{response_mult:.1f}"
            ),
            classification_impact=impact,
            details={
                "phase": phase,
                "month": month,
                "forage_quality": forage,
                "vegetation_density": veg_density,
                "cover_value": cover_value,
                "ndvi_estimated": round(avg_ndvi, 3),
                "cover_score": round(cover_score, 1),
                "species_response": response_mult,
            },
        )
