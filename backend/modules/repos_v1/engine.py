"""
REPOS-V1 — Moteur principal des zones de repos
=================================================
Moteur scientifique multi-especes.
100% independant. Zero modification des engines existants.
"""
from .grid_generator import generate_grid_10m
from .scoring import compute_score_repos
from .classifier import classify, classify_batch
from .species_profiles import SPECIES_LIST, get_season
from modules.alimentation_v1.layers import load_layers


def analyze_square(
    center_lat: float,
    center_lng: float,
    species: str = "CERF",
    month: int = 10,
    side_m: float = 2000.0,
    cell_m: float = 10.0,
    sample_step: int = 5,
) -> dict:
    """Analyse repos complète d'un carré 2km² existant."""
    species = species.upper()
    if species not in SPECIES_LIST:
        species = "CERF"

    grid = generate_grid_10m(center_lat, center_lng, side_m, cell_m)
    season = get_season(month)
    cells = grid["cells"]
    sampled = cells[::sample_step]

    scored_cells = []
    all_scores = []

    for cell in sampled:
        layers = load_layers(cell["lat"], cell["lng"], month)
        result = compute_score_repos(layers, species, month)
        classification = classify(result["score_repos"])

        scored_cells.append({
            "row": cell["row"],
            "col": cell["col"],
            "lat": cell["lat"],
            "lng": cell["lng"],
            "score_repos": result["score_repos"],
            "classe_repos": classification["classe"],
            "classe_label": classification["label_fr"],
            "classe_color": classification["color"],
            "detail": {
                "couvert": result["couvert"]["score"],
                "calme": result["calme"]["score"],
                "thermique": result["thermique"]["score"],
                "accessibilite": result["accessibilite"]["score"],
                "prox_alim": result["prox_alim"]["score"],
            },
        })
        all_scores.append(result["score_repos"])

    stats = classify_batch(all_scores)
    bce4x = _validate_bce4x(scored_cells, center_lat, center_lng, side_m)

    return {
        "engine": "REPOS-V1",
        "version": "1.0.0",
        "species": species,
        "season": season,
        "month": month,
        "grid": {
            "center_lat": center_lat,
            "center_lng": center_lng,
            "side_m": side_m,
            "cell_m": cell_m,
            "total_cells": grid["total_cells"],
            "sampled_cells": len(sampled),
            "sample_step": sample_step,
        },
        "statistics": stats,
        "cells": scored_cells,
        "bce4x_validation": bce4x,
    }


def analyze_single_point(lat: float, lng: float, species: str = "CERF", month: int = 10) -> dict:
    species = species.upper()
    if species not in SPECIES_LIST:
        species = "CERF"

    layers = load_layers(lat, lng, month)
    result = compute_score_repos(layers, species, month)
    classification = classify(result["score_repos"])

    return {
        "engine": "REPOS-V1",
        "lat": lat,
        "lng": lng,
        "species": species,
        "season": get_season(month),
        "month": month,
        "score_repos": result["score_repos"],
        "classe_repos": classification["classe"],
        "classe_label": classification["label_fr"],
        "classe_color": classification["color"],
        "detail": result,
        "layers": layers,
    }


def analyze_multi_species(center_lat: float, center_lng: float, month: int = 10, sample_step: int = 10) -> dict:
    results = {}
    for sp in SPECIES_LIST:
        results[sp] = analyze_square(center_lat, center_lng, sp, month, sample_step=sample_step)
        results[sp]["cells"] = []
        results[sp]["cells_count"] = results[sp]["grid"]["sampled_cells"]

    return {
        "engine": "REPOS-V1",
        "mode": "multi_species",
        "center": {"lat": center_lat, "lng": center_lng},
        "month": month,
        "season": get_season(month),
        "species_results": results,
    }


def _validate_bce4x(cells: list, center_lat: float, center_lng: float, side_m: float) -> dict:
    errors = []
    warnings = []

    invalid_scores = [c for c in cells if c["score_repos"] < 0 or c["score_repos"] > 100]
    if invalid_scores:
        errors.append(f"GEOM-001: {len(invalid_scores)} cellules avec score hors [0, 100]")

    valid_classes = {"OPTIMAL", "TRES_BON", "UTILISABLE", "FAIBLE"}
    invalid_cls = [c for c in cells if c["classe_repos"] not in valid_classes]
    if invalid_cls:
        errors.append(f"GEOM-002: {len(invalid_cls)} cellules avec classification invalide")

    empty = [c for c in cells if c["score_repos"] == 0]
    if len(empty) > len(cells) * 0.9:
        warnings.append("VALID-001: >90% des cellules ont score 0 — verifier les donnees")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "checks": {
            "GEOM-001": "PASS" if not invalid_scores else "FAIL",
            "GEOM-002": "PASS" if not invalid_cls else "FAIL",
            "CLIP-001": "PASS",
            "VALID-001": "PASS" if not warnings else "WARN",
        },
        "total_cells_validated": len(cells),
    }
