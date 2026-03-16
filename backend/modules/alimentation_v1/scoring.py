"""
ALIMENTATION-V1 — Scoring alimentaire scientifique
====================================================
SCORE_SITE (0-100) composé de 5 axes:
  PROTEINES (0-25) + ENERGIE (0-25) + MINERAUX (0-20) + SECURITE (0-20) + EFFORT (0-10)
"""
from .species_profiles import get_profile, get_season


def _clamp(val: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, val))


def score_proteines(layers: dict, profile: dict, season: str) -> dict:
    """PROTEINES (0-25): Disponibilité de sources protéinées."""
    ess = layers["essences"]
    occ = layers["occupation_sol"]
    veg = layers["vegetation"]
    saison_mult = profile["saisonnalite"].get(season, {}).get("proteines", 0.7)

    # Score basé sur les sources protéiques du profil
    sources = profile["sources_proteines"]
    raw = 0.0
    count = 0

    # Mapping couches -> sources
    mapping = {
        "friches": occ.get("friches", 0),
        "legumineuses": occ.get("friches", 0) * 0.7,
        "arbustes": ess.get("arbustes", 0),
        "jeunes_feuillus_1_3m": layers["lidar"].get("strate_1_3m", 0),
        "herbes": occ.get("champs", 0) * 0.6,
        "jeunes_feuillus_bouleau": ess.get("feuillus_secondaires", 0),
        "jeunes_feuillus_saule": ess.get("feuillus_secondaires", 0) * 0.8,
        "vegetation_aquatique": 0.8 if layers["hydrographie"]["zone_humide"] else 0.2,
        "repousses_ligneuses": ess.get("arbustes", 0) * 0.9,
        "insectes": veg.get("ndvi", 0.5) * 0.8,
        "herbacees_printanieres": occ.get("champs", 0) * 0.7 if season == "printemps" else 0.2,
        "larves": veg.get("ndvi", 0.4) * 0.5,
        "charognes": 0.15,
        "graines": occ.get("cultures", 0) * 0.6,
        "invertebres": veg.get("ndvi", 0.4) * 0.5,
        "herbacees": occ.get("champs", 0) * 0.8,
        "graminees": occ.get("champs", 0) * 0.7,
        "jeunes_pousses": layers["lidar"].get("strate_1_3m", 0) * 0.8,
    }

    for src, weight in sources.items():
        availability = mapping.get(src, 0.3)
        raw += weight * availability
        count += 1

    avg = (raw / max(count, 1)) * saison_mult
    score = _clamp(avg * 25, 0, 25)

    return {"score": round(score, 2), "raw": round(raw, 3), "saison_mult": saison_mult}


def score_energie(layers: dict, profile: dict, season: str) -> dict:
    """ENERGIE (0-25): Ressources énergétiques (mast, cultures, baies)."""
    ess = layers["essences"]
    occ = layers["occupation_sol"]
    saison_mult = profile["saisonnalite"].get(season, {}).get("energie", 0.7)

    sources = profile["sources_energie"]
    raw = 0.0
    count = 0

    mapping = {
        "mast_chene": ess.get("feuillus_nobles", 0) * 0.9,
        "mast_hetre": ess.get("feuillus_nobles", 0) * 0.8,
        "mast_pommier": ess.get("arbustes", 0) * 0.6,
        "mast_glands": ess.get("feuillus_nobles", 0) * 0.95,
        "mast_secondaire": ess.get("feuillus_secondaires", 0) * 0.5,
        "cultures_energetiques": occ.get("cultures", 0),
        "cultures_energetiques_mais": occ.get("cultures", 0) * 0.9,
        "glands": ess.get("feuillus_nobles", 0) * 0.95,
        "baies": ess.get("arbustes", 0) * 0.8,
        "fruits": ess.get("arbustes", 0) * 0.7,
        "mais_hyperphagie": occ.get("cultures", 0) * 0.95,
        "miel": 0.2,
        "cereales": occ.get("cultures", 0) * 0.8,
        "mais": occ.get("cultures", 0) * 0.9,
        "repousses_ligneuses": ess.get("arbustes", 0) * 0.5,
        "ecorce": ess.get("feuillus_secondaires", 0) * 0.4,
        "vegetation_aquatique": 0.6 if layers["hydrographie"]["zone_humide"] else 0.1,
    }

    for src, weight in sources.items():
        availability = mapping.get(src, 0.2)
        raw += weight * availability
        count += 1

    avg = (raw / max(count, 1)) * saison_mult
    score = _clamp(avg * 25, 0, 25)

    return {"score": round(score, 2), "raw": round(raw, 3), "saison_mult": saison_mult}


def score_mineraux(layers: dict, profile: dict, season: str) -> dict:
    """MINERAUX (0-20): Calcium, phosphore, sodium, zones humides."""
    hydro = layers["hydrographie"]
    saison_mult = profile["saisonnalite"].get(season, {}).get("mineraux", 0.5)

    sources = profile["sources_mineraux"]
    raw = 0.0
    count = 0

    mapping = {
        "jeunes_feuillus_ca_p": layers["lidar"].get("strate_1_3m", 0) * 0.8,
        "zones_humides_na": 0.9 if hydro["zone_humide"] else 0.15,
        "suintements": 0.95 if hydro["suintement"] else 0.1,
        "salines_naturelles": 0.85 if hydro["suintement"] else 0.1,
        "sols_calcaires": 0.5,
        "faible_ponderation": 0.3,
        "sols_riches": 0.4,
        "sols_nus": 0.6 if layers["lidar"]["canopy_density"] < 0.3 else 0.2,
        "zones_grattage": 0.5 if layers["lidar"]["canopy_density"] < 0.5 else 0.2,
        "gravier": 0.4,
    }

    for src, weight in sources.items():
        availability = mapping.get(src, 0.2)
        raw += weight * availability
        count += 1

    avg = (raw / max(count, 1)) * saison_mult
    score = _clamp(avg * 20, 0, 20)

    return {"score": round(score, 2), "raw": round(raw, 3), "saison_mult": saison_mult}


def score_securite(layers: dict, profile: dict) -> dict:
    """SECURITE (0-20): Couvert, distance perturbations, lisières."""
    pert = layers["perturbations"]
    conif = layers["couvert_coniferien"]
    lidar = layers["lidar"]

    sec_config = profile["securite"]
    factors = []

    # Distance route
    dist_route_min = sec_config.get("distance_route_min_m", 150)
    route_score = min(1.0, pert["distance_route_m"] / max(dist_route_min * 2, 1))
    factors.append(route_score)

    # Distance bâtiment
    dist_bat_min = sec_config.get("distance_batiment_min_m", 200)
    bat_score = min(1.0, pert["distance_batiment_m"] / max(dist_bat_min * 2, 1))
    factors.append(bat_score)

    # Couvert coniférien
    if "couvert_coniferien_dense_150m" in sec_config:
        cover_score = conif["densite"] * sec_config["couvert_coniferien_dense_150m"]
        factors.append(cover_score)
    elif "couvert_dense" in sec_config:
        cover_score = lidar["canopy_density"] * sec_config["couvert_dense"]
        factors.append(cover_score)
    elif "grands_massifs_forestiers" in sec_config:
        cover_score = lidar["canopy_density"] * sec_config["grands_massifs_forestiers"]
        factors.append(cover_score)

    # Lisières / mosaïque
    if "lisieres" in sec_config:
        factors.append(sec_config["lisieres"] * 0.7)
    if "mosaique_lisiere_bosquets" in sec_config:
        factors.append(sec_config["mosaique_lisiere_bosquets"] * 0.7)
    if "mosaique_foret_lisiere_clairiere" in sec_config:
        factors.append(sec_config["mosaique_foret_lisiere_clairiere"] * 0.7)

    avg = sum(factors) / max(len(factors), 1)
    score = _clamp(avg * 20, 0, 20)

    return {"score": round(score, 2), "factors": [round(f, 3) for f in factors]}


def score_effort(layers: dict, profile: dict) -> dict:
    """EFFORT (0-10): Pente, obstacles, accessibilité."""
    slope = layers["terrain"]["pente_deg"]
    effort_config = profile["effort"]

    pente_opt = effort_config.get("pente_optimale_deg", 5)
    pente_max = effort_config.get("pente_max_deg", 20)
    tolerance = effort_config.get("tolerance_obstacles", 0.4)

    # Score pente: optimal = 1.0, max = 0.0
    if slope <= pente_opt:
        pente_score = 1.0
    elif slope >= pente_max:
        pente_score = 0.0
    else:
        pente_score = 1.0 - (slope - pente_opt) / (pente_max - pente_opt)

    # Score obstacles: basé sur la densité + tolérance
    obstacle_factor = 1.0 - (1.0 - tolerance) * (1.0 - layers["lidar"]["canopy_density"])

    combined = pente_score * 0.7 + obstacle_factor * 0.3
    score = _clamp(combined * 10, 0, 10)

    return {
        "score": round(score, 2),
        "pente_score": round(pente_score, 3),
        "obstacle_factor": round(obstacle_factor, 3),
        "slope_deg": slope,
    }


def compute_score_site(layers: dict, species: str, month: int = 10) -> dict:
    """
    Calcule SCORE_SITE (0-100) pour une cellule.

    SCORE = PROTEINES(0-25) + ENERGIE(0-25) + MINERAUX(0-20) + SECURITE(0-20) + EFFORT(0-10)
    """
    profile = get_profile(species)
    season = get_season(month)

    prot = score_proteines(layers, profile, season)
    ener = score_energie(layers, profile, season)
    mine = score_mineraux(layers, profile, season)
    secu = score_securite(layers, profile)
    effo = score_effort(layers, profile)

    total = prot["score"] + ener["score"] + mine["score"] + secu["score"] + effo["score"]
    total = _clamp(total, 0, 100)

    return {
        "score_site": round(total, 1),
        "proteines": prot,
        "energie": ener,
        "mineraux": mine,
        "securite": secu,
        "effort": effo,
        "species": species.upper(),
        "season": season,
        "month": month,
    }
