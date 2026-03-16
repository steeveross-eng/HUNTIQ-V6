"""
REPOS-V1 — Scoring des zones de repos
========================================
SCORE_REPOS (0-100) composé de 5 axes:
  COUVERT (0-30) + CALME (0-25) + THERMIQUE (0-20) + ACCESSIBILITE (0-15) + PROX_ALIM (0-10)
"""
from .species_profiles import get_profile, get_season


def _clamp(val: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, val))


def score_couvert(layers: dict, profile: dict) -> dict:
    """COUVERT (0-30): Qualité du couvert pour le repos."""
    lidar = layers["lidar"]
    conif = layers["couvert_coniferien"]

    couvert_config = profile["couvert"]
    factors = []

    # Densité de canopée vs minimum requis
    canopy_min = couvert_config.get("canopy_min", 0.5)
    canopy_score = min(1.0, lidar["canopy_density"] / max(canopy_min, 0.1))
    factors.append(canopy_score * 0.4)

    # Types de couvert spécifiques
    if "coniferes_denses" in couvert_config:
        factors.append(conif["densite"] * couvert_config["coniferes_denses"] * 0.3)
    if "grands_massifs_forestiers" in couvert_config:
        factors.append(lidar["canopy_density"] * couvert_config["grands_massifs_forestiers"] * 0.3)
    if "tres_dense" in couvert_config:
        dense_score = (conif["densite"] + lidar["canopy_density"]) / 2
        factors.append(dense_score * couvert_config["tres_dense"] * 0.3)
    if "bosquets" in couvert_config:
        factors.append(lidar["canopy_density"] * couvert_config["bosquets"] * 0.25)
    if "clairieres" in couvert_config:
        clairiere_score = max(0, 1.0 - lidar["canopy_density"])
        factors.append(clairiere_score * couvert_config["clairieres"] * 0.15)
    if "forets_mixtes" in couvert_config:
        mixte = (lidar["canopy_density"] + conif["densite"]) / 2
        factors.append(mixte * couvert_config["forets_mixtes"] * 0.25)

    # Sous-bois / strate 1-3m
    if "sous_bois" in couvert_config:
        factors.append(lidar["strate_1_3m"] * couvert_config["sous_bois"] * 0.2)
    if "lisieres" in couvert_config:
        factors.append(0.7 * couvert_config["lisieres"] * 0.15)

    # Perchoirs (dindon)
    if "arbres_perchoir" in couvert_config:
        perch = min(1.0, conif["hauteur_m"] / 15.0)
        factors.append(perch * couvert_config["arbres_perchoir"] * 0.25)

    avg = sum(factors) / max(len(factors), 1) if factors else 0
    score = _clamp(avg * 30 / 0.3, 0, 30)  # normalize

    return {"score": round(score, 2), "factors_count": len(factors)}


def score_calme(layers: dict, profile: dict) -> dict:
    """CALME (0-25): Éloignement des perturbations."""
    pert = layers["perturbations"]
    calme_config = profile["calme"]

    factors = []

    # Distance route
    dist_route_min = calme_config.get("distance_route_min_m", 200)
    route_score = min(1.0, pert["distance_route_m"] / max(dist_route_min * 2, 1))
    factors.append(route_score * 0.35)

    # Distance sentier
    dist_sent_min = calme_config.get("distance_sentier_min_m", 100)
    sent_score = min(1.0, pert["distance_sentier_m"] / max(dist_sent_min * 2, 1))
    factors.append(sent_score * 0.25)

    # Distance bâtiment
    dist_bat = pert["distance_batiment_m"]
    bat_score = min(1.0, dist_bat / 600.0)
    factors.append(bat_score * 0.25)

    # Tolérance bruit
    tolerance = calme_config.get("tolerance_bruit", 0.3)
    noise_score = 1.0 - tolerance  # Moins tolérant = besoin plus calme = score basé distance
    factors.append(noise_score * route_score * 0.15)

    avg = sum(factors)
    score = _clamp(avg * 25 / 0.35, 0, 25)

    return {"score": round(score, 2), "distance_route": pert["distance_route_m"]}


def score_thermique(layers: dict, profile: dict, season: str) -> dict:
    """THERMIQUE (0-20): Confort thermique pour le repos."""
    conif = layers["couvert_coniferien"]
    lidar = layers["lidar"]

    therm_config = profile["thermique"]
    factors = []

    # Ombrage basé sur la canopée
    ombrage = lidar["canopy_density"]
    if season in ("ete", "printemps"):
        # En été, l'ombrage est critique
        ombrage_need = therm_config.get("ombrage_requis", therm_config.get("ombrage", therm_config.get("ombrage_dense", therm_config.get("ombrage_modere", therm_config.get("ombrage_leger", 0.7)))))
        factors.append(min(1.0, ombrage / max(ombrage_need, 0.1)) * 0.4)
    else:
        # En hiver, les conifères pour protection thermique
        conif_score = conif["densite"]
        if "coniferes_hiver" in therm_config:
            conif_score *= therm_config["coniferes_hiver"]
        factors.append(conif_score * 0.4)

    # Zones fraîches (orignal, ours)
    if "zones_fraiches" in therm_config:
        elev_norm = min(1.0, layers["terrain"]["elevation_m"] / 500.0)
        factors.append(elev_norm * therm_config["zones_fraiches"] * 0.3)

    # Proximité eau pour fraîcheur
    if "proximite_eau" in therm_config:
        eau_score = max(0, 1.0 - layers["hydrographie"]["distance_eau_m"] / 500.0)
        factors.append(eau_score * therm_config["proximite_eau"] * 0.3)

    # Perchoirs nocturnes (dindon)
    if "perchoirs_nocturnes" in therm_config:
        perch = min(1.0, conif["hauteur_m"] / 12.0)
        factors.append(perch * therm_config["perchoirs_nocturnes"] * 0.3)

    avg = sum(factors) / max(len(factors), 1) if factors else 0
    score = _clamp(avg * 20 / 0.35, 0, 20)

    return {"score": round(score, 2), "season_effect": season}


def score_accessibilite(layers: dict, profile: dict) -> dict:
    """ACCESSIBILITE (0-15): Facilité d'accès à la zone de repos."""
    slope = layers["terrain"]["pente_deg"]
    access_config = profile["accessibilite"]

    pente_opt = access_config.get("pente_optimale_deg", 5)
    pente_max = access_config.get("pente_max_deg", 20)

    if slope <= pente_opt:
        pente_score = 1.0
    elif slope >= pente_max:
        pente_score = 0.0
    else:
        pente_score = 1.0 - (slope - pente_opt) / (pente_max - pente_opt)

    # Sol drainé / dégagé
    sol_score = access_config.get("sol_draine", access_config.get("sol_degage", 0.7))
    # Réduire si zone humide
    if layers["hydrographie"]["zone_humide"]:
        sol_score *= 0.6

    combined = pente_score * 0.7 + sol_score * 0.3
    score = _clamp(combined * 15, 0, 15)

    return {"score": round(score, 2), "pente_deg": slope, "pente_score": round(pente_score, 3)}


def score_prox_alim(layers: dict, profile: dict) -> dict:
    """PROX_ALIM (0-10): Proximité des sources d'alimentation."""
    prox_config = profile["prox_alim"]
    importance = prox_config.get("importance", 0.75)

    # Estimation basée sur NDVI et diversité végétale
    ndvi = layers["vegetation"]["ndvi"]
    ess = layers["essences"]
    diversite = (ess["feuillus_nobles"] + ess["arbustes"] + ess["mast_production"]) / 3

    food_proximity = ndvi * 0.5 + diversite * 0.3 + layers["occupation_sol"]["friches"] * 0.2
    score = _clamp(food_proximity * importance * 10, 0, 10)

    return {"score": round(score, 2), "ndvi": ndvi, "importance": importance}


def compute_score_repos(layers: dict, species: str, month: int = 10) -> dict:
    """
    Calcule SCORE_REPOS (0-100) pour une cellule.

    SCORE = COUVERT(0-30) + CALME(0-25) + THERMIQUE(0-20) + ACCESSIBILITE(0-15) + PROX_ALIM(0-10)
    """
    profile = get_profile(species)
    season = get_season(month)

    couv = score_couvert(layers, profile)
    calm = score_calme(layers, profile)
    ther = score_thermique(layers, profile, season)
    acce = score_accessibilite(layers, profile)
    prox = score_prox_alim(layers, profile)

    total = couv["score"] + calm["score"] + ther["score"] + acce["score"] + prox["score"]
    total = _clamp(total, 0, 100)

    return {
        "score_repos": round(total, 1),
        "couvert": couv,
        "calme": calm,
        "thermique": ther,
        "accessibilite": acce,
        "prox_alim": prox,
        "species": species.upper(),
        "season": season,
        "month": month,
    }
