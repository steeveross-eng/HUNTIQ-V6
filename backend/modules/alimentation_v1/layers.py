"""
ALIMENTATION-V1 — Chargement des couches fines
================================================
Simule/charge les couches LiDAR, essences, occupation du sol, hydro, conifères.
Modèle algorithmique pour le Québec. Données déterministes par position.
"""
import math
import hashlib


def _deterministic_hash(lat: float, lng: float, seed: str = "") -> float:
    """Hash déterministe [0, 1] basé sur les coordonnées."""
    raw = f"{lat:.6f}:{lng:.6f}:{seed}"
    h = int(hashlib.md5(raw.encode()).hexdigest()[:8], 16)
    return (h % 10000) / 10000.0


def _elevation_model(lat: float, lng: float) -> float:
    """Modèle numérique de terrain algorithmique (MNT) pour le Québec."""
    base = 150 + 200 * math.sin(lat * 0.8) * math.cos(lng * 0.5)
    variation = 80 * _deterministic_hash(lat, lng, "elev")
    return max(10, base + variation)


def load_layers(lat: float, lng: float, month: int = 10) -> dict:
    """
    Charge les couches fines pour une cellule 10m×10m.

    Couches:
    - LiDAR: MNT, CHM (canopy height), densité, strate 1-3m
    - Essences: feuillus nobles, secondaires, arbustes, mast
    - Occupation du sol: friches, cultures, champs
    - Hydrographie: zones humides, suintements, distance_eau
    - Couvert coniférien: densité, hauteur
    - Pente
    """
    h = _deterministic_hash
    elev = _elevation_model(lat, lng)

    # === LiDAR ===
    chm = 2 + 28 * h(lat, lng, "chm")  # Canopy Height Model (2-30m)
    canopy_density = 0.1 + 0.85 * h(lat, lng, "canopy_d")
    strate_1_3m = 0.05 + 0.90 * h(lat, lng, "strate13")  # Sous-bois 1-3m

    # === Essences ===
    feuillus_nobles = h(lat, lng, "fnobles")  # Chêne, érable, hêtre
    feuillus_secondaires = h(lat, lng, "fsecond")  # Bouleau, peuplier
    arbustes = h(lat, lng, "arbustes")
    mast_production = h(lat, lng, "mast")  # Production glands/faînes/fruits
    # Normaliser: total ne dépasse pas 1
    total_ess = feuillus_nobles + feuillus_secondaires + arbustes + mast_production
    if total_ess > 0:
        feuillus_nobles /= total_ess
        feuillus_secondaires /= total_ess
        arbustes /= total_ess
        mast_production /= total_ess

    # === Occupation du sol ===
    friches = h(lat, lng, "friches")
    cultures = h(lat, lng, "cultures")
    champs = h(lat, lng, "champs")
    total_occ = friches + cultures + champs
    if total_occ > 1:
        friches /= total_occ
        cultures /= total_occ
        champs /= total_occ

    # === Hydrographie ===
    dist_eau = 10 + 490 * h(lat, lng, "dist_eau")  # 10-500m
    zone_humide = 1 if h(lat, lng, "zh") > 0.75 else 0
    suintement = 1 if h(lat, lng, "suint") > 0.85 else 0

    # === Couvert coniférien ===
    conifer_density = 0.05 + 0.90 * h(lat, lng, "conif_d")
    conifer_height = 3 + 22 * h(lat, lng, "conif_h")

    # === Pente ===
    slope_deg = 0.5 + 34.5 * h(lat, lng, "slope")  # 0.5-35 degrés

    # === Perturbations humaines ===
    dist_route = 20 + 980 * h(lat, lng, "dist_route")  # 20-1000m
    dist_batiment = 50 + 950 * h(lat, lng, "dist_bat")  # 50-1000m
    dist_sentier = 10 + 490 * h(lat, lng, "dist_sent")

    # === Ajustements saisonniers ===
    season_ndvi_mult = {
        1: 0.10, 2: 0.12, 3: 0.35, 4: 0.55, 5: 0.75, 6: 0.90,
        7: 1.00, 8: 0.95, 9: 0.80, 10: 0.60, 11: 0.30, 12: 0.15,
    }
    ndvi = (0.3 + 0.6 * h(lat, lng, "ndvi")) * season_ndvi_mult.get(month, 0.65)

    return {
        "lidar": {
            "mnt_elevation_m": round(elev, 1),
            "chm_canopy_height_m": round(chm, 1),
            "canopy_density": round(canopy_density, 3),
            "strate_1_3m": round(strate_1_3m, 3),
        },
        "essences": {
            "feuillus_nobles": round(feuillus_nobles, 3),
            "feuillus_secondaires": round(feuillus_secondaires, 3),
            "arbustes": round(arbustes, 3),
            "mast_production": round(mast_production, 3),
        },
        "occupation_sol": {
            "friches": round(friches, 3),
            "cultures": round(cultures, 3),
            "champs": round(champs, 3),
        },
        "hydrographie": {
            "distance_eau_m": round(dist_eau, 1),
            "zone_humide": zone_humide,
            "suintement": suintement,
        },
        "couvert_coniferien": {
            "densite": round(conifer_density, 3),
            "hauteur_m": round(conifer_height, 1),
        },
        "terrain": {
            "pente_deg": round(slope_deg, 1),
            "elevation_m": round(elev, 1),
        },
        "perturbations": {
            "distance_route_m": round(dist_route, 1),
            "distance_batiment_m": round(dist_batiment, 1),
            "distance_sentier_m": round(dist_sentier, 1),
        },
        "vegetation": {
            "ndvi": round(ndvi, 3),
        },
    }
