"""
CORRIDORS-V10 — Documentation et fiche technique
====================================================
Genere la fiche technique JSON et les metadonnees du moteur.
Tracabilite complete: inputs, versions, ponderations, changelog.
Norme Steeve-MAX SM-005.
"""
from datetime import datetime, timezone
from .species_profiles import CORRIDOR_PROFILES, SPECIES_LIST, PARAM_KEYS
from .classifier import CLASSIFICATION_THRESHOLDS, CORRIDOR_LEVELS


def generate_documentation() -> dict:
    return {
        "engine": {
            "id": "CORRIDORS-V10",
            "version": "10.0.0",
            "date_creation": "2026-03-17",
            "auteur": "BIONIC Engine Builder",
            "statut": "PRODUCTION",
            "type": "Moteur corridors fauniques multi-especes",
        },
        "description": (
            "Moteur independant de modelisation des corridors fauniques pour la faune du Quebec. "
            "Algorithme A* sur grille de couts 25m x 25m dans le carre 2km2 existant. "
            "5 especes supportees. Continuite absolue du reseau obligatoire (zero dead-end). "
            "Profils a 12 parametres. Validation BCE-4X et Steeve-MAX integrees."
        ),
        "methode": {
            "grille": "25m x 25m dans carre 2km2 existant (80x80 = 6400 cellules)",
            "algorithme": "A* pathfinding sur surface de couts",
            "reseau": "Kruskal MST + forcement de connexion pour continuite absolue",
            "couches_entree": [
                "MNT (elevation, pente)",
                "Hydrographie (eau = barriere, zones humides, distance eau)",
                "Structure forestiere (canopy, feuillus nobles, coniferes, strate 1-3m)",
                "Pression humaine (routes, batiments)",
            ],
            "score_composite": {
                "QUALITE_CHEMIN": {"min": 0, "max": 30, "description": "Cout moyen et regularite des corridors"},
                "DIVERSITE_ZONES": {"min": 0, "max": 25, "description": "Couverture des 4 types de zones ecologiques"},
                "CONTINUITE": {"min": 0, "max": 30, "description": "Connectivite du reseau (CRITIQUE)"},
                "CONFORMITE_ESPECE": {"min": 0, "max": 15, "description": "Respect des 12 parametres espece"},
            },
            "score_total": {"min": 0, "max": 100},
        },
        "parametres_12": PARAM_KEYS,
        "classification": CLASSIFICATION_THRESHOLDS,
        "palette_normative": CORRIDOR_LEVELS,
        "zones_ecologiques": ["alimentation", "repos", "rut", "eau"],
        "especes_supportees": SPECIES_LIST,
        "profils": {k: {
            "nom_fr": v["nom_fr"],
            "nom_scientifique": v["nom_scientifique"],
            **{p: v[p] for p in PARAM_KEYS},
        } for k, v in CORRIDOR_PROFILES.items()},
        "contraintes": {
            "carre_2km2": "Reutilise le carre existant de BIONIC, aucune recreation",
            "engines_existants": "Aucune modification (V2, V3, IA, V9, ALIMENTATION-V1, REPOS-V1)",
            "eau_barriere": "Eau = barriere par defaut. Aucune exception non documentee",
            "continuite_absolue": "Zero cul-de-sac, zero dead-end. Reseau entierement connecte",
            "pente_barriere": "Pente > pente_max_deg = barriere infranchissable",
        },
        "validation_bce4x": {
            "GEOM-001": "Aucun corridor hors grille",
            "GEOM-002": "Pas de self-intersection",
            "GEOM-003": "Clipping propre et continu",
            "HYDRO-001": "Eau = barriere (aucune traversee)",
            "TOPO-001": "Pente <= pente_max_deg respectee",
            "CONT-001": "Continuite spatiale obligatoire (zero dead-end)",
            "COMP-001": "Style deplacement respecte",
        },
        "validation_steeve_max": {
            "SM-001": "Coherence espece -> habitat -> comportement",
            "SM-002": "Coherence saisonniere",
            "SM-003": "12 parametres integralement utilises",
            "SM-004": "Tracabilite complete",
            "SM-005": "Documentation complete",
        },
        "changelog": [
            {"version": "10.0.0", "date": "2026-03-17", "description": "Version initiale CORRIDORS-V10"},
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
