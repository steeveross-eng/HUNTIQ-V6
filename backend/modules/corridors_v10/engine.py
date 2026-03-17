"""
CORRIDORS-V10 — Moteur principal (Orchestrateur)
====================================================
Norme CORRIDOR-V1/V10 officielle.
Pipeline:
  1. Charger le profil espece (12 parametres + description corridor)
  2. Generer la grille de couts enrichie (ECL, micro-topo, nourriture, refuge, etc.)
  3. Construire le reseau de corridors (A* + continuite absolue COR-006)
  4. Scorer le reseau + classification normative par corridor
  5. Valider BCE-4X + Steeve-MAX
  6. Retourner les resultats avec niveaux/couleurs/largeurs normatifs
"""
from .species_profiles import SPECIES_LIST, get_profile, get_season, get_season_modifiers, PARAM_KEYS
from .cost_surface import generate_cost_grid
from .network_builder import build_network
from .scoring import compute_corridor_score, compute_corridor_levels
from .validator import validate_bce4x, validate_steeve_max
from .classifier import classify_batch, CORRIDOR_LEVELS


def analyze_corridors(
    center_lat: float,
    center_lng: float,
    species: str = "CERF",
    month: int = 10,
    side_m: float = 2000.0,
    cell_m: float = 25.0,
) -> dict:
    """Analyse complete des corridors fauniques (version legere, sans GeoJSON)."""
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

    # Scorer chaque corridor individuellement avec classification normative
    enriched_corridors = compute_corridor_levels(
        network["corridors"], grid_result["cell_data"]
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

    # Resume corridors avec niveaux normatifs
    corridors_summary = []
    for c in enriched_corridors:
        corridors_summary.append({
            "id": c["id"],
            "from_zone": c["from_zone"]["type"],
            "to_zone": c["to_zone"]["type"],
            "length_cells": c["length_cells"],
            "cost": c["cost"],
            "score_individuel": c["score_individuel"],
            "niveau": c["niveau"],
            "color": c["color"],
            "largeur_m": c["largeur_m"],
            "forced": c.get("forced_connection", False),
        })

    # Distribution normative
    niveau_distribution = {}
    for lvl_name, lvl_info in CORRIDOR_LEVELS.items():
        count = sum(1 for c in enriched_corridors if c["niveau"] == lvl_name)
        niveau_distribution[lvl_name] = {
            "count": count,
            "color": lvl_info["color"],
            "largeur_m": lvl_info["largeur_m"],
            "label_fr": lvl_info["label_fr"],
        }

    return {
        "engine": "CORRIDORS-V10",
        "version": "10.0.0",
        "species": species,
        "season": season,
        "month": month,
        "profile_params": {k: profile[k] for k in PARAM_KEYS},
        "description_corridor": profile.get("description_corridor", ""),
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
            "niveau_distribution": niveau_distribution,
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
    Analyse complete AVEC GeoJSON pour visualisation cartographique.
    Chaque corridor LineString inclut niveau, couleur, largeur normatifs.
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

    enriched_corridors = compute_corridor_levels(
        network["corridors"], grid_result["cell_data"]
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

    # GeoJSON corridors avec proprietes normatives
    geojson_features = []
    for c in enriched_corridors:
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
                "score": c["score_individuel"],
                "niveau": c["niveau"],
                "niveau_label": c["niveau_label"],
                "color": c["color"],
                "pattern": c["pattern"],
                "largeur_m": c["largeur_m"],
                "render_weight": c["render_weight"],
                "dash_array": c["dash_array"],
            },
            "geometry": {
                "type": "LineString",
                "coordinates": coords,
            },
        }
        geojson_features.append(feature)

    # GeoJSON zones ecologiques
    zone_colors = {
        "alimentation": "#4CAF50",
        "repos": "#2196F3",
        "rut": "#FF5722",
        "eau": "#00BCD4",
    }
    for z in network["zones"]:
        feature = {
            "type": "Feature",
            "properties": {
                "zone_type": z["type"],
                "score": z["score"],
                "species": species,
                "color": zone_colors.get(z["type"], "#9E9E9E"),
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

    # Distribution normative
    niveau_distribution = {}
    for lvl_name, lvl_info in CORRIDOR_LEVELS.items():
        count = sum(1 for c in enriched_corridors if c["niveau"] == lvl_name)
        niveau_distribution[lvl_name] = {
            "count": count,
            "color": lvl_info["color"],
            "largeur_m": lvl_info["largeur_m"],
            "label_fr": lvl_info["label_fr"],
        }

    return {
        "engine": "CORRIDORS-V10",
        "version": "10.0.0",
        "species": species,
        "season": season,
        "month": month,
        "description_corridor": profile.get("description_corridor", ""),
        "score_corridor": score_result["score_corridor"],
        "classe_corridor": score_result["classe_corridor"],
        "classe_label": score_result["classe_label"],
        "classe_color": score_result["classe_color"],
        "score_detail": score_result["detail"],
        "network": network["network_stats"],
        "niveau_distribution": niveau_distribution,
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
            "description_corridor": r["description_corridor"],
            "network_summary": {
                "total_zones": r["network"]["total_zones"],
                "total_corridors": r["network"]["total_corridors"],
                "niveau_distribution": r["network"]["niveau_distribution"],
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
        "palette_normative": CORRIDOR_LEVELS,
    }
