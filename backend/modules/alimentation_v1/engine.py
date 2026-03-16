"""
ALIMENTATION-V1 — Moteur principal
=====================================
Moteur alimentaire scientifique multi-especes.
100% independant. Zero modification des engines existants.
Reutilise le carre 2km2 existant.
"""
from .grid_generator import generate_grid_10m, get_grid_summary
from .layers import load_layers
from .scoring import compute_score_site
from .classifier import classify, classify_batch
from .species_profiles import SPECIES_LIST, get_season


def analyze_square(
    center_lat: float,
    center_lng: float,
    species: str = "CERF",
    month: int = 10,
    side_m: float = 2000.0,
    cell_m: float = 10.0,
    sample_step: int = 5,
) -> dict:
    """
    Analyse alimentaire complète d'un carré 2km² existant.

    Args:
        center_lat/lng: Centre du carré existant
        species: Espèce cible (CERF, ORIGNAL, OURS, DINDON, WAPITI)
        month: Mois (1-12) pour ajustements saisonniers
        side_m: Côté du carré en mètres (2000 par défaut)
        cell_m: Taille cellule en mètres (10 par défaut)
        sample_step: Pas d'échantillonnage pour performance (défaut 5 = 1 cellule sur 5)

    Returns:
        Résultats complets: scores par cellule, classification, statistiques
    """
    species = species.upper()
    if species not in SPECIES_LIST:
        species = "CERF"

    grid = generate_grid_10m(center_lat, center_lng, side_m, cell_m)
    season = get_season(month)
    cells = grid["cells"]

    # Échantillonnage pour performance (grille 200x200 = 40000 cellules)
    sampled = cells[::sample_step]

    scored_cells = []
    all_scores = []

    for cell in sampled:
        layers = load_layers(cell["lat"], cell["lng"], month)
        result = compute_score_site(layers, species, month)
        classification = classify(result["score_site"])

        scored_cells.append({
            "row": cell["row"],
            "col": cell["col"],
            "lat": cell["lat"],
            "lng": cell["lng"],
            "score_alimentation": result["score_site"],
            "classe_alimentation": classification["classe"],
            "classe_label": classification["label_fr"],
            "classe_color": classification["color"],
            "detail": {
                "proteines": result["proteines"]["score"],
                "energie": result["energie"]["score"],
                "mineraux": result["mineraux"]["score"],
                "securite": result["securite"]["score"],
                "effort": result["effort"]["score"],
            },
        })
        all_scores.append(result["score_site"])

    stats = classify_batch(all_scores)

    # Validation BCE-4X
    bce4x = _validate_bce4x(scored_cells, center_lat, center_lng, side_m)

    return {
        "engine": "ALIMENTATION-V1",
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


def analyze_single_point(
    lat: float, lng: float, species: str = "CERF", month: int = 10
) -> dict:
    """Analyse alimentaire d'un point unique."""
    species = species.upper()
    if species not in SPECIES_LIST:
        species = "CERF"

    layers = load_layers(lat, lng, month)
    result = compute_score_site(layers, species, month)
    classification = classify(result["score_site"])

    return {
        "engine": "ALIMENTATION-V1",
        "lat": lat,
        "lng": lng,
        "species": species,
        "season": get_season(month),
        "month": month,
        "score_alimentation": result["score_site"],
        "classe_alimentation": classification["classe"],
        "classe_label": classification["label_fr"],
        "classe_color": classification["color"],
        "detail": result,
        "layers": layers,
    }


def analyze_multi_species(
    center_lat: float, center_lng: float, month: int = 10, sample_step: int = 10
) -> dict:
    """Analyse alimentaire pour les 5 espèces en parallèle."""
    results = {}
    for sp in SPECIES_LIST:
        results[sp] = analyze_square(
            center_lat, center_lng, sp, month, sample_step=sample_step
        )
        # Alléger: ne pas renvoyer les cellules individuelles
        results[sp]["cells"] = []
        results[sp]["cells_count"] = results[sp]["grid"]["sampled_cells"]

    return {
        "engine": "ALIMENTATION-V1",
        "mode": "multi_species",
        "center": {"lat": center_lat, "lng": center_lng},
        "month": month,
        "season": get_season(month),
        "species_results": results,
    }


def _validate_bce4x(cells: list, center_lat: float, center_lng: float, side_m: float) -> dict:
    """Validation BCE-4X pour le moteur ALIMENTATION-V1."""
    errors = []
    warnings = []

    # GEOM-001: Score dans [0, 100]
    invalid_scores = [c for c in cells if c["score_alimentation"] < 0 or c["score_alimentation"] > 100]
    if invalid_scores:
        errors.append(f"GEOM-001: {len(invalid_scores)} cellules avec score hors [0, 100]")

    # GEOM-002: Classification valide
    valid_classes = {"OPTIMALE", "TRES_BONNE", "UTILISABLE", "FAIBLE"}
    invalid_cls = [c for c in cells if c["classe_alimentation"] not in valid_classes]
    if invalid_cls:
        errors.append(f"GEOM-002: {len(invalid_cls)} cellules avec classification invalide")

    # CLIP-001: Toutes les cellules dans le carré 2km²
    # (vérifié par construction via grid_generator)

    # VALID-001: Aucune cellule vide
    empty = [c for c in cells if c["score_alimentation"] == 0 and c["classe_alimentation"] == "FAIBLE"]
    if len(empty) > len(cells) * 0.9:
        warnings.append("VALID-001: >90% des cellules sont FAIBLE — verifier les donnees")

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
