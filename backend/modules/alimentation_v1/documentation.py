"""
ALIMENTATION-V1 — Documentation et fiche technique
=====================================================
Génère la fiche technique JSON et les métadonnées du moteur.
"""
from datetime import datetime, timezone
from .species_profiles import ALIM_PROFILES, SPECIES_LIST
from .classifier import CLASSIFICATION_THRESHOLDS


def generate_documentation() -> dict:
    return {
        "engine": {
            "id": "ALIMENTATION-V1",
            "version": "1.0.0",
            "date_creation": "2026-03-16",
            "auteur": "BIONIC Engine Builder",
            "statut": "PRODUCTION",
            "type": "Moteur alimentaire scientifique multi-especes",
        },
        "description": (
            "Moteur independant d'analyse alimentaire pour la faune du Quebec. "
            "Grille 10m x 10m dans le carre 2km2 existant. "
            "5 especes supportees. Score composite PROTEINES + ENERGIE + MINERAUX + SECURITE + EFFORT."
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
                "PROTEINES": {"min": 0, "max": 25, "description": "Disponibilite sources proteinees"},
                "ENERGIE": {"min": 0, "max": 25, "description": "Ressources energetiques (mast, cultures, baies)"},
                "MINERAUX": {"min": 0, "max": 20, "description": "Calcium, phosphore, sodium, zones humides"},
                "SECURITE": {"min": 0, "max": 20, "description": "Couvert, distance perturbations"},
                "EFFORT": {"min": 0, "max": 10, "description": "Pente, obstacles, accessibilite"},
            },
            "score_total": {"min": 0, "max": 100},
        },
        "classification": CLASSIFICATION_THRESHOLDS,
        "especes_supportees": SPECIES_LIST,
        "profils": {k: {
            "nom_fr": v["nom_fr"],
            "nom_scientifique": v["nom_scientifique"],
            "nb_sources_proteines": len(v["sources_proteines"]),
            "nb_sources_energie": len(v["sources_energie"]),
            "nb_sources_mineraux": len(v["sources_mineraux"]),
        } for k, v in ALIM_PROFILES.items()},
        "contraintes": {
            "carre_2km2": "Reutilise le carre existant de BIONIC, aucune recreation",
            "engines_existants": "Aucune modification (V2, V3, IA, V9)",
            "seuil_dynamique": "Inchange et compatible avec toutes les especes",
        },
        "validation_bce4x": {
            "GEOM-001": "Score dans [0, 100]",
            "GEOM-002": "Classification valide (4 niveaux)",
            "CLIP-001": "Analyse dans carre 2km2 existant",
            "VALID-001": "Chaque cellule 10m x 10m validee",
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
