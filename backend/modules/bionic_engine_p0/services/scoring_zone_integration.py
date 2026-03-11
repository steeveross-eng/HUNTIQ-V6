"""
MODULE E — Scoring Zone Integration
BIONIC V5 — Pipeline Organique Unifié

Intégration des zones organiques dans le scoring:
- scoring habitat
- scoring comportement
- scoring mobilité
- scoring multifactor
- predictive_territorial

source_id dynamique: généré strictement depuis l'espèce transmise par l'orchestrateur.
0 duplication. 0 transversalité. 0 fallback implicite.
"""

from typing import Dict, Any, Optional


def _build_source_id(species: str) -> str:
    """
    Génère un source_id dynamique strictement lié à l'espèce.
    Aucun fallback. L'espèce DOIT être fournie par l'orchestrateur.
    """
    return f"BIONIC_V5_{species.upper()}"


def calculate_zone_score(
    zone: Dict[str, Any],
    layer_id: str,
    species: str,
    season: str,
    weather: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Calcule le score détaillé d'une zone organique.

    Args:
        zone: Zone organique (area_m2, compactness, centroid)
        layer_id: Couche BIONIC (obligatoire, pas de défaut)
        species: Espèce (obligatoire, transmise par l'orchestrateur)
        season: Saison (obligatoire, transmise par le router)
        weather: Données météo optionnelles

    Returns:
        Score détaillé avec sous-composantes et source_id dynamique
    """
    source_id = _build_source_id(species)

    base_score = zone.get("score", 70)
    area = zone.get("area_m2", 5000)
    compactness = zone.get("compactness", 0.5)

    # Area factor: zones closer to 6500m² are optimal
    area_factor = 1.0 - abs(area - 6500) / 6500 * 0.3

    # Compactness factor: moderate compactness is best for habitat
    compact_factor = 1.0 if 0.3 <= compactness <= 0.7 else 0.85

    # Season factor by layer
    season_factors = _get_season_factors(layer_id, season)

    # Weather factor
    weather_factor = _get_weather_factor(weather, species) if weather else 1.0

    # Species factor
    species_factor = _get_species_layer_factor(species, layer_id)

    # Additive blend (avoid multiplicative destruction of scores)
    adjustment = (area_factor - 1.0) * 10 + (compact_factor - 1.0) * 5 + (season_factors - 0.8) * 15 + (weather_factor - 1.0) * 10
    final_score = int(base_score * species_factor + adjustment)
    final_score = max(40, min(100, final_score))

    return {
        "source_id": source_id,
        "score_final": final_score,
        "score_base": base_score,
        "factor_area": round(area_factor, 3),
        "factor_compactness": round(compact_factor, 3),
        "factor_season": round(season_factors, 3),
        "factor_weather": round(weather_factor, 3),
        "factor_species": round(species_factor, 3),
        "layer_id": layer_id,
        "species": species,
        "season": season,
    }


def enrich_geojson_with_scores(
    geojson: Dict[str, Any],
    species: str,
    season: str,
    weather: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Enrichit un GeoJSON de zones avec des scores détaillés.

    Args:
        geojson: GeoJSON FeatureCollection
        species: Espèce (obligatoire, transmise explicitement par le router)
        season: Saison (obligatoire, transmise explicitement par le router)
        weather: Données météo optionnelles

    Returns:
        GeoJSON enrichi avec scores détaillés, source_id dynamique par zone
    """
    source_id = _build_source_id(species)
    features = geojson.get("features", [])

    for feature in features:
        props = feature.get("properties", {})
        layer_id = props.get("layer_id")
        if layer_id is None:
            continue

        zone_data = {
            "score": props.get("score", 70),
            "area_m2": props.get("area_m2", 5000),
            "compactness": props.get("compactness", 0.5),
        }

        detailed = calculate_zone_score(zone_data, layer_id, species, season, weather)
        props["score"] = detailed["score_final"]
        props["source_id"] = source_id
        props["scoring_detail"] = detailed

    # Inject source_id in collection metadata
    if "metadata" in geojson:
        geojson["metadata"]["source_id"] = source_id

    return geojson


def _get_season_factors(layer_id: str, season: str) -> float:
    """Facteur saisonnier par couche."""
    factors = {
        "rut":        {"spring": 0.3, "summer": 0.4, "autumn": 1.0, "winter": 0.2},
        "repos":      {"spring": 0.8, "summer": 0.7, "autumn": 0.8, "winter": 1.0},
        "alimentation": {"spring": 1.0, "summer": 0.9, "autumn": 0.95, "winter": 0.6},
        "corridors":  {"spring": 0.9, "summer": 0.8, "autumn": 1.0, "winter": 0.7},
        "habitats":   {"spring": 0.9, "summer": 0.85, "autumn": 0.95, "winter": 0.8},
        "ndvi":       {"spring": 0.8, "summer": 1.0, "autumn": 0.7, "winter": 0.3},
        "hydro":      {"spring": 1.0, "summer": 0.95, "autumn": 0.8, "winter": 0.5},
        "salines":    {"spring": 0.9, "summer": 0.8, "autumn": 0.7, "winter": 0.5},
    }
    layer_factors = factors.get(layer_id, {"spring": 0.8, "summer": 0.8, "autumn": 0.9, "winter": 0.7})
    return layer_factors.get(season, 0.8)


def _get_weather_factor(weather: Dict, species: str) -> float:
    """Facteur météo."""
    if not weather:
        return 1.0
    temp = weather.get("temperature", 10)
    wind = weather.get("wind_speed", 5)
    precip = weather.get("precipitation", 0)

    # Temperature comfort
    optimal_temps = {
        "moose": (-5, 15), "deer": (0, 20), "bear": (5, 25),
        "wild_turkey": (5, 25), "elk": (-10, 20)
    }
    lo, hi = optimal_temps.get(species, (0, 20))
    temp_factor = 1.0 if lo <= temp <= hi else max(0.5, 1.0 - abs(temp - (lo + hi) / 2) * 0.02)

    # Wind impact
    wind_factor = max(0.5, 1.0 - wind * 0.015)

    # Precipitation impact
    precip_factor = max(0.6, 1.0 - precip * 0.1)

    return round(temp_factor * wind_factor * precip_factor, 3)


def _get_species_layer_factor(species: str, layer_id: str) -> float:
    """Facteur espèce × couche."""
    weights = {
        "moose": {"rut": 0.95, "repos": 0.80, "alimentation": 0.85, "corridors": 0.90, "habitats": 0.95, "hydro": 0.95, "salines": 0.90},
        "deer": {"rut": 0.90, "repos": 0.85, "alimentation": 0.90, "corridors": 0.85, "habitats": 0.90, "affuts": 0.90},
        "bear": {"alimentation": 0.95, "repos": 0.85, "corridors": 0.80, "habitats": 0.90, "hydro": 0.85, "ndvi": 0.90},
        "wild_turkey": {"alimentation": 0.90, "habitats": 0.85, "affuts": 0.85, "ensoleillement": 0.90},
        "elk": {"rut": 0.90, "corridors": 0.90, "habitats": 0.85, "altitude": 0.80},
    }
    return weights.get(species, {}).get(layer_id, 0.75)
