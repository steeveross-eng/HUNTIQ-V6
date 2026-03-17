"""
CORRIDORS-V10 — Moteur principal (Orchestrateur)
====================================================
Orchestre l'analyse complete des corridors fauniques.
100% independant. Zero modification des engines existants.
Reutilise le carre 2km2 existant.

Pipeline:
  1. Charger le profil espece (12 parametres)
  2. Generer la grille de couts
  3. Construire le reseau de corridors (A* + continuite absolue)
  4. Scorer le reseau
  5. Valider BCE-4X + Steeve-MAX
  6. Retourner les resultats

Version: 10.0.0
"""
from .species_profiles import SPECIES_LIST, get_profile, get_season, get_season_modifiers, PARAM_KEYS
from .cost_surface import generate_cost_grid
from .network_builder import build_network
from .scoring import compute_corridor_score
from .validator import validate_bce4x, validate_steeve_max
from .classifier import classify_batch


def analyze_corridors(
    center_lat: float,
    center_lng: float,
    species: str = "CERF",
    month: int = 10,
    side_m: float = 2000.0,
    cell_m: float = 25.0,
) -> dict:
    """
    Analyse complete des corridors fauniques pour un carre 2km2.

    Args:
        center_lat/lng: Centre du carre 2km2 existant
        species: Espece cible (CERF, ORIGNAL, OURS, DINDON, WAPITI)
        month: Mois (1-12)
        side_m: Cote du carre en metres (2000 par defaut)
        cell_m: Taille cellule en metres (25 par defaut — corridors = echelle paysagere)

    Returns:
        Resultats complets: reseau, score, classification, validations
    """
    species = species.upper()
    if species not in SPECIES_LIST:
        species = "CERF"

    profile = get_profile(species)
    season = get_season(month)
    season_mods = get_season_modifiers(species, month)

    # 1. Generer grille de couts
    grid_result = generate_cost_grid(
        center_lat, center_lng, profile, season_mods, side_m, cell_m, month
    )

    # 2. Construire reseau de corridors
    network = build_network(
        cost_grid=grid_result["grid"],
        cell_data=grid_result["cell_data"],
        n=grid_result["n"],
        profile=profile,
        season_mods=season_mods,
        grid_meta=grid_result["metadata"],
    )

    # 3. Scorer le reseau
    score_result = compute_corridor_score(
        zones=network["zones"],
        corridors=network["corridors"],
        continuity=network["continuity"],
        network_stats=network["network_stats"],
        profile=profile,
        cell_m=cell_m,
    )

    # 4. Valider BCE-4X
    bce4x = validate_bce4x(
        corridors=network["corridors"],
        zones=network["zones"],
        continuity=network["continuity"],
        cost_grid=grid_result["grid"],
        cell_data=grid_result["cell_data"],
        n=grid_result["n"],
        profile=profile,
    )

    # 5. Valider Steeve-MAX
    steeve_max = validate_steeve_max(
        profile=profile,
        zones=network["zones"],
        corridors=network["corridors"],
        network_stats=network["network_stats"],
        season=season,
        month=month,
    )

    # 6. Assembler corridors allegeris (sans path complet pour la reponse legere)
    corridors_summary = []
    for c in network["corridors"]:
        corridors_summary.append({
            "id": c["id"],
            "from_zone": c["from_zone"]["type"],
            "to_zone": c["to_zone"]["type"],
            "length_cells": c["length_cells"],
            "cost": c["cost"],
            "forced": c.get("forced_connection", False),
            "dead_end_fix": c.get("dead_end_fix", False),
        })

    return {
        "engine": "CORRIDORS-V10",
        "version": "10.0.0",
        "species": species,
        "season": season,
        "month": month,
        "profile_params": {k: profile[k] for k in PARAM_KEYS},
        "grid": {
            "center_lat": center_lat,
            "center_lng": center_lng,
            "side_m": side_m,
            "cell_m": cell_m,
            "n": grid_result["n"],
            "total_cells": grid_result["metadata"]["total_cells"],
            "water_barriers": grid_result["metadata"]["water_barriers"],
            "slope_barriers": grid_result["metadata"]["slope_barriers"],
            "traversable_cells": grid_result["metadata"]["traversable_cells"],
        },
        "score_corridor": score_result["score_corridor"],
        "classe_corridor": score_result["classe_corridor"],
        "classe_label": score_result["classe_label"],
        "classe_color": score_result["classe_color"],
        "score_detail": score_result["detail"],
        "network": {
            "total_zones": network["network_stats"]["total_zones"],
            "total_corridors": network["network_stats"]["total_corridors"],
            "zone_types": network["network_stats"]["zone_types"],
            "corridors_summary": corridors_summary,
        },
        "continuity": network["continuity"],
        "validation": {
            "bce4x": bce4x,
            "steeve_max": steeve_max,
        },
    }


def analyze_corridors_full(
    center_lat: float,
    center_lng: float,
    species: str = "CERF",
    month: int = 10,
    side_m: float = 2000.0,
    cell_m: float = 25.0,
) -> dict:
    """
    Analyse complete AVEC les chemins GeoJSON pour visualisation.
    Plus lourd que analyze_corridors() — utiliser pour export/visualisation.
    """
    species = species.upper()
    if species not in SPECIES_LIST:
        species = "CERF"

    profile = get_profile(species)
    season = get_season(month)
    season_mods = get_season_modifiers(species, month)

    grid_result = generate_cost_grid(
        center_lat, center_lng, profile, season_mods, side_m, cell_m, month
    )

    network = build_network(
        cost_grid=grid_result["grid"],
        cell_data=grid_result["cell_data"],
        n=grid_result["n"],
        profile=profile,
        season_mods=season_mods,
        grid_meta=grid_result["metadata"],
    )

    score_result = compute_corridor_score(
        zones=network["zones"],
        corridors=network["corridors"],
        continuity=network["continuity"],
        network_stats=network["network_stats"],
        profile=profile,
        cell_m=cell_m,
    )

    bce4x = validate_bce4x(
        corridors=network["corridors"],
        zones=network["zones"],
        continuity=network["continuity"],
        cost_grid=grid_result["grid"],
        cell_data=grid_result["cell_data"],
        n=grid_result["n"],
        profile=profile,
    )

    steeve_max = validate_steeve_max(
        profile=profile,
        zones=network["zones"],
        corridors=network["corridors"],
        network_stats=network["network_stats"],
        season=season,
        month=month,
    )

    # GeoJSON corridors
    geojson_features = []
    for c in network["corridors"]:
        coords = [[pt["lng"], pt["lat"]] for pt in c["path"]]
        feature = {
            "type": "Feature",
            "properties": {
                "corridor_id": c["id"],
                "from_type": c["from_zone"]["type"],
                "to_type": c["to_zone"]["type"],
                "length_cells": c["length_cells"],
                "cost": c["cost"],
                "species": species,
            },
            "geometry": {
                "type": "LineString",
                "coordinates": coords,
            },
        }
        geojson_features.append(feature)

    # GeoJSON zones
    for z in network["zones"]:
        feature = {
            "type": "Feature",
            "properties": {
                "zone_type": z["type"],
                "score": z["score"],
                "species": species,
            },
            "geometry": {
                "type": "Point",
                "coordinates": [z["lng"], z["lat"]],
            },
        }
        geojson_features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": geojson_features,
    }

    return {
        "engine": "CORRIDORS-V10",
        "version": "10.0.0",
        "species": species,
        "season": season,
        "month": month,
        "score_corridor": score_result["score_corridor"],
        "classe_corridor": score_result["classe_corridor"],
        "classe_label": score_result["classe_label"],
        "classe_color": score_result["classe_color"],
        "score_detail": score_result["detail"],
        "network": network["network_stats"],
        "continuity": network["continuity"],
        "validation": {
            "bce4x": bce4x,
            "steeve_max": steeve_max,
        },
        "geojson": geojson,
    }


def analyze_multi_species(
    center_lat: float,
    center_lng: float,
    month: int = 10,
) -> dict:
    """Analyse corridors pour les 5 especes."""
    results = {}
    for sp in SPECIES_LIST:
        r = analyze_corridors(center_lat, center_lng, sp, month)
        results[sp] = {
            "score_corridor": r["score_corridor"],
            "classe_corridor": r["classe_corridor"],
            "classe_label": r["classe_label"],
            "classe_color": r["classe_color"],
            "continuity": r["continuity"],
            "network_summary": {
                "total_zones": r["network"]["total_zones"],
                "total_corridors": r["network"]["total_corridors"],
            },
            "bce4x_status": r["validation"]["bce4x"]["status"],
            "steeve_max_status": r["validation"]["steeve_max"]["status"],
        }

    all_scores = [results[sp]["score_corridor"] for sp in SPECIES_LIST]
    stats = classify_batch(all_scores)

    return {
        "engine": "CORRIDORS-V10",
        "mode": "multi_species",
        "center": {"lat": center_lat, "lng": center_lng},
        "month": month,
        "season": get_season(month),
        "species_results": results,
        "statistics": stats,
    }
