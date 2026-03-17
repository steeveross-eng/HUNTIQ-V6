"""
CORRIDORS-V10 — Profils d'especes (12 parametres obligatoires)
================================================================
5 especes: CERF, ORIGNAL, OURS, DINDON, WAPITI
Chaque profil contient exactement 12 parametres pour le calcul de corridors.
Aucune interpretation libre. Respect integral Steeve-MAX.

PARAMETRES (12):
  1. pente_optimale_deg        — Pente ideale de deplacement
  2. pente_max_deg             — Pente maximale tolerable (barriere au-dela)
  3. sensibilite_pression      — Sensibilite aux perturbations humaines [0-1]
  4. style_deplacement         — lineaire | sinueux | opportuniste | migratoire | territorial
  5. tolerance_obstacles       — Capacite a franchir obstacles physiques [0-1]
  6. distance_route_evitement_m — Distance minimale d'evitement des routes
  7. distance_batiment_evitement_m — Distance minimale d'evitement des batiments
  8. largeur_corridor_m        — Largeur fonctionnelle du corridor
  9. preference_forestiere     — Affinite pour le couvert forestier [0-1]
  10. affinite_hydro           — Attraction vers l'eau sans traversee [0-1]
  11. influence_dominants      — Impact hierarchie sociale sur mouvement [0-1]
  12. vitesse_deplacement      — lent | modere | rapide
"""

CORRIDOR_PROFILES = {
    "CERF": {
        "id": "cerf",
        "nom_fr": "Cerf de Virginie",
        "nom_scientifique": "Odocoileus virginianus",
        "description_corridor": (
            "Corridors etroits, sinueux, opportunistes, suivant lisieres, mosaiques, "
            "regenerations, clairieres, friches. Recherche pentes sud, nourriture, micro-reliefs. "
            "Deplacements prudents, segmentes. Connectivite fine entre ALIMENTATION-V1, REPOS-V1, zones calmes."
        ),
        "pente_optimale_deg": 5,
        "pente_max_deg": 15,
        "sensibilite_pression": 0.75,
        "style_deplacement": "sinueux",
        "tolerance_obstacles": 0.30,
        "distance_route_evitement_m": 150,
        "distance_batiment_evitement_m": 200,
        "largeur_corridor_m": 100,
        "preference_forestiere": 0.85,
        "affinite_hydro": 0.60,
        "influence_dominants": 0.70,
        "vitesse_deplacement": "modere",
        "saisonnalite": {
            "printemps": {"mobilite": 0.80, "couvert": 0.70, "hydro": 0.65},
            "ete": {"mobilite": 0.85, "couvert": 0.75, "hydro": 0.70},
            "automne": {"mobilite": 0.95, "couvert": 0.80, "hydro": 0.55},
            "hiver": {"mobilite": 0.50, "couvert": 0.95, "hydro": 0.40},
        },
    },
    "ORIGNAL": {
        "id": "orignal",
        "nom_fr": "Orignal",
        "nom_scientifique": "Alces americanus",
        "description_corridor": (
            "Corridors massifs, directionnels, ancres dans vallons humides, zones fraiches, "
            "coniferes denses, cuvettes, replats, coulees encaissees. Forte affinite zones humides. "
            "Evitement strict pression humaine. Deplacements rectilignes. Connectivite obligatoire "
            "entre zones humides, repos thermiques, alimentation."
        ),
        "pente_optimale_deg": 8,
        "pente_max_deg": 25,
        "sensibilite_pression": 0.80,
        "style_deplacement": "lineaire",
        "tolerance_obstacles": 0.60,
        "distance_route_evitement_m": 300,
        "distance_batiment_evitement_m": 400,
        "largeur_corridor_m": 150,
        "preference_forestiere": 0.75,
        "affinite_hydro": 0.85,
        "influence_dominants": 0.55,
        "vitesse_deplacement": "modere",
        "saisonnalite": {
            "printemps": {"mobilite": 0.85, "couvert": 0.65, "hydro": 0.90},
            "ete": {"mobilite": 0.80, "couvert": 0.60, "hydro": 0.95},
            "automne": {"mobilite": 0.95, "couvert": 0.70, "hydro": 0.70},
            "hiver": {"mobilite": 0.40, "couvert": 0.90, "hydro": 0.30},
        },
    },
    "OURS": {
        "id": "ours",
        "nom_fr": "Ours noir",
        "nom_scientifique": "Ursus americanus",
        "description_corridor": (
            "Corridors mixtes, frais, couverts, proches eau, fourres denses, regenerations productives, "
            "blocs rocheux. Recherche nourriture + fraicheur + refuge. Evitement zones ouvertes. "
            "Connectivite entre nourriture, zones humides, refuges."
        ),
        "pente_optimale_deg": 12,
        "pente_max_deg": 35,
        "sensibilite_pression": 0.85,
        "style_deplacement": "opportuniste",
        "tolerance_obstacles": 0.80,
        "distance_route_evitement_m": 200,
        "distance_batiment_evitement_m": 300,
        "largeur_corridor_m": 80,
        "preference_forestiere": 0.90,
        "affinite_hydro": 0.50,
        "influence_dominants": 0.40,
        "vitesse_deplacement": "rapide",
        "saisonnalite": {
            "printemps": {"mobilite": 0.90, "couvert": 0.80, "hydro": 0.55},
            "ete": {"mobilite": 0.85, "couvert": 0.85, "hydro": 0.50},
            "automne": {"mobilite": 0.95, "couvert": 0.75, "hydro": 0.45},
            "hiver": {"mobilite": 0.05, "couvert": 0.95, "hydro": 0.10},
        },
    },
    "DINDON": {
        "id": "dindon",
        "nom_fr": "Dindon sauvage",
        "nom_scientifique": "Meleagris gallopavo",
        "pente_optimale_deg": 3,
        "pente_max_deg": 12,
        "sensibilite_pression": 0.65,
        "style_deplacement": "territorial",
        "tolerance_obstacles": 0.20,
        "distance_route_evitement_m": 100,
        "distance_batiment_evitement_m": 150,
        "largeur_corridor_m": 60,
        "preference_forestiere": 0.70,
        "affinite_hydro": 0.35,
        "influence_dominants": 0.80,
        "vitesse_deplacement": "lent",
        "saisonnalite": {
            "printemps": {"mobilite": 0.85, "couvert": 0.60, "hydro": 0.40},
            "ete": {"mobilite": 0.80, "couvert": 0.65, "hydro": 0.45},
            "automne": {"mobilite": 0.70, "couvert": 0.75, "hydro": 0.35},
            "hiver": {"mobilite": 0.35, "couvert": 0.90, "hydro": 0.25},
        },
    },
    "WAPITI": {
        "id": "wapiti",
        "nom_fr": "Wapiti",
        "nom_scientifique": "Cervus canadensis",
        "pente_optimale_deg": 8,
        "pente_max_deg": 22,
        "sensibilite_pression": 0.70,
        "style_deplacement": "migratoire",
        "tolerance_obstacles": 0.50,
        "distance_route_evitement_m": 250,
        "distance_batiment_evitement_m": 350,
        "largeur_corridor_m": 120,
        "preference_forestiere": 0.65,
        "affinite_hydro": 0.55,
        "influence_dominants": 0.60,
        "vitesse_deplacement": "rapide",
        "saisonnalite": {
            "printemps": {"mobilite": 0.90, "couvert": 0.55, "hydro": 0.60},
            "ete": {"mobilite": 0.85, "couvert": 0.60, "hydro": 0.65},
            "automne": {"mobilite": 0.95, "couvert": 0.70, "hydro": 0.50},
            "hiver": {"mobilite": 0.45, "couvert": 0.90, "hydro": 0.35},
        },
    },
}

SPECIES_LIST = list(CORRIDOR_PROFILES.keys())

PARAM_KEYS = [
    "pente_optimale_deg", "pente_max_deg", "sensibilite_pression",
    "style_deplacement", "tolerance_obstacles", "distance_route_evitement_m",
    "distance_batiment_evitement_m", "largeur_corridor_m", "preference_forestiere",
    "affinite_hydro", "influence_dominants", "vitesse_deplacement",
]

MONTH_TO_SEASON = {
    1: "hiver", 2: "hiver", 3: "printemps", 4: "printemps",
    5: "printemps", 6: "ete", 7: "ete", 8: "ete",
    9: "automne", 10: "automne", 11: "automne", 12: "hiver",
}


def get_profile(species: str) -> dict:
    return CORRIDOR_PROFILES.get(species.upper(), CORRIDOR_PROFILES["CERF"])


def get_season(month: int) -> str:
    return MONTH_TO_SEASON.get(month, "automne")


def get_season_modifiers(species: str, month: int) -> dict:
    profile = get_profile(species)
    season = get_season(month)
    return profile["saisonnalite"].get(season, {"mobilite": 0.7, "couvert": 0.7, "hydro": 0.5})
