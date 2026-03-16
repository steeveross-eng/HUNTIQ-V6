"""
REPOS-V1 — Documentation et fiche technique
==============================================
"""
from datetime import datetime, timezone
from .species_profiles import REPOS_PROFILES, SPECIES_LIST
from .classifier import CLASSIFICATION_THRESHOLDS


def generate_documentation() -> dict:
    return {
        "engine": {
            "id": "REPOS-V1",
            "version": "1.0.0",
            "date_creation": "2026-03-16",
            "auteur": "BIONIC Engine Builder",
            "statut": "PRODUCTION",
            "type": "Moteur zones de repos scientifique multi-especes",
        },
        "description": (
            "Moteur independant d'analyse des zones de repos pour la faune du Quebec. "
            "Grille 10m x 10m dans le carre 2km2 existant. "
            "5 especes supportees. Score composite COUVERT + CALME + THERMIQUE + ACCESSIBILITE + PROX_ALIM."
        ),
        "methode": {
            "grille": "10m x 10m dans carre 2km2 existant",
            "couches_entree": [
                "LiDAR (MNT, CHM, densite, strate 1-3m)",
                "Essences (feuillus nobles, secondaires, arbustes, mast)",
                "Occupation du sol (friches, cultures, champs)",
                "Hydrographie (zones humides, suintements, distance eau)",
                "Couvert coniferien (densite, hauteur)",
                "Terrain (pente, elevation)",
                "Perturbations (distance routes, batiments, sentiers)",
                "Vegetation (NDVI saisonnier)",
            ],
            "score_composite": {
                "COUVERT": {"min": 0, "max": 30, "description": "Qualite du couvert pour le repos"},
                "CALME": {"min": 0, "max": 25, "description": "Eloignement des perturbations"},
                "THERMIQUE": {"min": 0, "max": 20, "description": "Confort thermique"},
                "ACCESSIBILITE": {"min": 0, "max": 15, "description": "Facilite d'acces"},
                "PROX_ALIM": {"min": 0, "max": 10, "description": "Proximite sources alimentation"},
            },
            "score_total": {"min": 0, "max": 100},
        },
        "classification": CLASSIFICATION_THRESHOLDS,
        "especes_supportees": SPECIES_LIST,
        "profils": {k: {
            "nom_fr": v["nom_fr"],
            "nom_scientifique": v["nom_scientifique"],
            "repos_pct": v["rythme_circadien"]["repos_pct"],
        } for k, v in REPOS_PROFILES.items()},
        "contraintes": {
            "carre_2km2": "Reutilise le carre existant de BIONIC",
            "engines_existants": "Aucune modification (V2, V3, IA, V9)",
            "seuil_dynamique": "Inchange et compatible",
        },
        "validation_bce4x": {
            "GEOM-001": "Score dans [0, 100]",
            "GEOM-002": "Classification valide (4 niveaux)",
            "CLIP-001": "Analyse dans carre 2km2 existant",
            "VALID-001": "Chaque cellule 10m x 10m validee",
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
