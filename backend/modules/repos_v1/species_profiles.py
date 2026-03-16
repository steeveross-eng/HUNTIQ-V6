"""
REPOS-V1 — Profils d'espèces pour les zones de repos
======================================================
5 profils: CERF, ORIGNAL, OURS, DINDON, WAPITI
Chaque profil définit les besoins en couvert, calme, thermique, accessibilité, proximité alimentaire.
"""

REPOS_PROFILES = {
    "CERF": {
        "id": "cerf",
        "nom_fr": "Cerf de Virginie",
        "nom_scientifique": "Odocoileus virginianus",
        "couvert": {
            "coniferes_denses": 0.90,
            "lisieres": 0.85,
            "sous_bois": 0.80,
            "canopy_min": 0.60,
        },
        "calme": {
            "distance_route_min_m": 200,
            "distance_sentier_min_m": 100,
            "zones_peu_perturbees": 0.85,
            "tolerance_bruit": 0.30,
        },
        "thermique": {
            "coniferes_hiver": 0.90,
            "feuillus_ete": 0.80,
            "ombrage_requis": 0.70,
            "exposition_pref": "sud_ouest",
        },
        "accessibilite": {
            "pente_max_deg": 12,
            "pente_optimale_deg": 3,
            "sol_draine": 0.75,
        },
        "prox_alim": {
            "distance_max_m": 300,
            "importance": 0.80,
        },
        "rythme_circadien": {
            "repos_pct": 50,
            "pic_repos_1": {"debut": 0, "fin": 4, "intensite": 0.90},
            "pic_repos_2": {"debut": 10, "fin": 14, "intensite": 0.85},
        },
    },
    "ORIGNAL": {
        "id": "orignal",
        "nom_fr": "Orignal",
        "nom_scientifique": "Alces americanus",
        "couvert": {
            "grands_massifs_forestiers": 0.85,
            "zones_humides": 0.80,
            "canopy_min": 0.50,
        },
        "calme": {
            "distance_route_min_m": 400,
            "distance_sentier_min_m": 200,
            "eloignement_humain": 0.90,
            "tolerance_bruit": 0.25,
        },
        "thermique": {
            "zones_fraiches": 0.85,
            "ombrage": 0.80,
            "proximite_eau": 0.75,
            "exposition_pref": "nord",
        },
        "accessibilite": {
            "pente_max_deg": 20,
            "pente_optimale_deg": 6,
            "sol_draine": 0.60,
        },
        "prox_alim": {
            "distance_max_m": 500,
            "proximite_vegetation_aquatique": 0.85,
            "importance": 0.75,
        },
        "rythme_circadien": {
            "repos_pct": 60,
            "pic_repos_1": {"debut": 0, "fin": 4, "intensite": 0.95},
            "pic_repos_2": {"debut": 10, "fin": 14, "intensite": 0.90},
        },
    },
    "OURS": {
        "id": "ours",
        "nom_fr": "Ours noir",
        "nom_scientifique": "Ursus americanus",
        "couvert": {
            "tres_dense": 0.95,
            "topographie_refuge": 0.90,
            "ravines": 0.85,
            "canopy_min": 0.70,
        },
        "calme": {
            "distance_route_min_m": 300,
            "distance_sentier_min_m": 200,
            "eloignement_maximal_humain": 0.95,
            "tolerance_bruit": 0.20,
        },
        "thermique": {
            "zones_fraiches": 0.85,
            "ravines": 0.80,
            "ombrage_dense": 0.90,
            "exposition_pref": "nord_est",
        },
        "accessibilite": {
            "pente_max_deg": 35,
            "pente_optimale_deg": 10,
            "tolerance_pente_elevee": 0.85,
        },
        "prox_alim": {
            "distance_max_m": 400,
            "proximite_baies_mast": 0.90,
            "importance": 0.70,
        },
        "rythme_circadien": {
            "repos_pct": 40,
            "pic_repos_1": {"debut": 22, "fin": 5, "intensite": 0.80},
            "pic_repos_2": {"debut": 12, "fin": 15, "intensite": 0.60},
        },
    },
    "DINDON": {
        "id": "dindon",
        "nom_fr": "Dindon sauvage",
        "nom_scientifique": "Meleagris gallopavo",
        "couvert": {
            "bosquets": 0.85,
            "arbres_perchoir": 0.95,
            "mosaique_lisiere": 0.80,
            "canopy_min": 0.40,
        },
        "calme": {
            "distance_route_min_m": 150,
            "distance_sentier_min_m": 80,
            "mosaique_lisiere": 0.80,
            "tolerance_bruit": 0.35,
        },
        "thermique": {
            "ombrage_leger": 0.70,
            "perchoirs_nocturnes": 0.90,
            "exposition_pref": "sud",
        },
        "accessibilite": {
            "pente_max_deg": 10,
            "pente_optimale_deg": 2,
            "sol_degage": 0.85,
        },
        "prox_alim": {
            "distance_max_m": 200,
            "proximite_insectes_graines": 0.90,
            "importance": 0.85,
        },
        "rythme_circadien": {
            "repos_pct": 45,
            "pic_repos_1": {"debut": 20, "fin": 5, "intensite": 0.95},
            "pic_repos_2": {"debut": 12, "fin": 14, "intensite": 0.50},
        },
    },
    "WAPITI": {
        "id": "wapiti",
        "nom_fr": "Wapiti",
        "nom_scientifique": "Cervus canadensis",
        "couvert": {
            "clairieres": 0.75,
            "forets_mixtes": 0.85,
            "lisieres": 0.80,
            "canopy_min": 0.45,
        },
        "calme": {
            "distance_route_min_m": 300,
            "distance_sentier_min_m": 150,
            "zones_calmes": 0.85,
            "vigilance_elevee": 0.90,
            "tolerance_bruit": 0.25,
        },
        "thermique": {
            "ombrage_modere": 0.75,
            "zones_ventilees": 0.70,
            "exposition_pref": "sud_ouest",
        },
        "accessibilite": {
            "pente_max_deg": 18,
            "pente_optimale_deg": 5,
            "eviter_terrains_accidentes": 0.80,
        },
        "prox_alim": {
            "distance_max_m": 400,
            "proximite_herbacees_graminees": 0.85,
            "importance": 0.80,
        },
        "rythme_circadien": {
            "repos_pct": 55,
            "pic_repos_1": {"debut": 0, "fin": 4, "intensite": 0.90},
            "pic_repos_2": {"debut": 11, "fin": 14, "intensite": 0.85},
        },
    },
}

SPECIES_LIST = list(REPOS_PROFILES.keys())

MONTH_TO_SEASON = {
    1: "hiver", 2: "hiver", 3: "printemps", 4: "printemps",
    5: "printemps", 6: "ete", 7: "ete", 8: "ete",
    9: "automne", 10: "automne", 11: "automne", 12: "hiver",
}


def get_profile(species: str) -> dict:
    return REPOS_PROFILES.get(species.upper(), REPOS_PROFILES["CERF"])


def get_season(month: int) -> str:
    return MONTH_TO_SEASON.get(month, "automne")
