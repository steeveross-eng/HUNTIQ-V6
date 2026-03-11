"""
MODULE D — Zone Visual Layer V2
BIONIC V5 — Pipeline Organique Unifié

Génération des couches visuelles organiques.
Couleurs BIONIC, opacité dynamique, bordures lissées.
Sortie: GeoJSON strict.

100% indépendant. Aucune dépendance transversale.
"""

from typing import Dict, List, Any

# Palette BIONIC V5 officielle — identique à bionicModules.js
BIONIC_COLORS = {
    "rut":            {"color": "#FF4D6D", "label": "Zone de rut",            "category": "behavioral"},
    "repos":          {"color": "#8B5CF6", "label": "Zone de repos",          "category": "behavioral"},
    "alimentation":   {"color": "#22C55E", "label": "Zone d'alimentation",    "category": "behavioral"},
    "corridors":      {"color": "#06B6D4", "label": "Corridor faunique",      "category": "behavioral"},
    "habitats":       {"color": "#10B981", "label": "Habitat optimal",        "category": "environmental"},
    "ensoleillement": {"color": "#FCD34D", "label": "Ensoleillement",         "category": "environmental"},
    "orientation":    {"color": "#2196F3", "label": "Orientation",            "category": "environmental"},
    "hydro":          {"color": "#3B82F6", "label": "Hydrographie",           "category": "environmental"},
    "peuplements":    {"color": "#15803D", "label": "Peuplements forestiers",  "category": "environmental"},
    "ndvi":           {"color": "#66BB6A", "label": "NDVI / Densité végétale","category": "environmental"},
    "pentes":         {"color": "#FF7043", "label": "Pentes",                 "category": "environmental"},
    "salines":        {"color": "#FFFF00", "label": "Saline potentielle",     "category": "strategic"},
    "affuts":         {"color": "#F5A623", "label": "Affût potentiel",        "category": "strategic"},
    "trajets":        {"color": "#FF9800", "label": "Trajets de chasse",      "category": "strategic"},
    "altitude":       {"color": "#78909C", "label": "Altitude relative",      "category": "environmental"},
}


def zone_to_geojson_feature(
    zone: Dict,
    layer_id: str,
    zone_id: str,
    score: int = 0,
    species: str = "moose",
    penalty: Dict = None,
) -> Dict[str, Any]:
    """
    Convertit une zone organique en GeoJSON Feature.
    BIONIC V5 P1: Inclut penalty_factor et penalty_details.
    """
    meta = BIONIC_COLORS.get(layer_id, {"color": "#999999", "label": layer_id, "category": "unknown"})

    properties = {
        "layer_id": layer_id,
        "label": meta["label"],
        "category": meta["category"],
        "species": species,
        "score": score,
        "score_display": score,
        "area_m2": zone["area_m2"],
        "compactness": zone["compactness"],
        "vertices": zone["vertices"],
        "centroid_lat": zone["centroid"]["lat"],
        "centroid_lng": zone["centroid"]["lng"],
        "style": {
            "stroke_color": meta["color"],
            "stroke_width": 4,
            "stroke_opacity": 0.95,
            "fill_color": meta["color"],
            "fill_opacity": 0.0,
        }
    }

    # P1: Pénalités semi-statiques
    if penalty:
        properties["penalty_factor"] = penalty.get("factor", 1.0)
        properties["raw_score"] = penalty.get("raw_score", score)
        properties["penalty_details"] = penalty.get("details", {})

    # V7: Enrichissement typologique
    v7_data = zone.get("v7")
    if not v7_data and penalty:
        v7_data = penalty.get("v7")
    if v7_data:
        properties["v7"] = v7_data
        properties["zone_type"] = v7_data.get("zone_type", "mixed")
        properties["zone_type_label"] = v7_data.get("zone_type_label", "")
        properties["zone_type_color"] = v7_data.get("zone_type_color", "")
        properties["score_global"] = v7_data.get("score_global", 0)
        properties["subscores"] = v7_data.get("subscores", {})
        properties["confidence"] = v7_data.get("confidence", 0)
        properties["hotspot"] = v7_data.get("hotspot", False)
        properties["hotspot_type"] = v7_data.get("hotspot_type")
        properties["season_relevance"] = v7_data.get("season_relevance", {})
        # BIONIC V7.4: score = score_display = int(score_global) — UNIQUE source de vérité
        v7_score = max(25, int(v7_data.get("score_global", 0)))
        properties["score"] = v7_score
        properties["score_display"] = v7_score

    # Source ID
    properties["source_id"] = f"BIONIC-{layer_id.upper()}-V7" if v7_data else f"BIONIC-{layer_id.upper()}"
    properties["scoring_detail"] = "V7-multicriteria" if v7_data else "V5-penalty"

    return {
        "type": "Feature",
        "id": zone_id,
        "geometry": {
            "type": "Polygon",
            "coordinates": [zone["coordinates"]]
        },
        "properties": properties,
    }


def zones_to_geojson(
    zones_by_layer: Dict[str, List[Dict]],
    species: str = "moose",
    scores_by_layer: Dict[str, List[int]] = None,
    penalties_by_layer: Dict[str, List[Dict]] = None,
) -> Dict[str, Any]:
    """
    Convertit toutes les zones en GeoJSON FeatureCollection.
    BIONIC V5 P1: Inclut les pénalités semi-statiques par zone.
    """
    features = []
    zone_idx = 0

    for layer_id, zones in zones_by_layer.items():
        layer_scores = (scores_by_layer or {}).get(layer_id, [])
        layer_penalties = (penalties_by_layer or {}).get(layer_id, [])
        for i, zone in enumerate(zones):
            score = layer_scores[i] if i < len(layer_scores) else 0
            penalty = layer_penalties[i] if i < len(layer_penalties) else None
            zone_id = f"bionic-{layer_id}-{zone_idx}"
            features.append(zone_to_geojson_feature(zone, layer_id, zone_id, score, species, penalty))
            zone_idx += 1

    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "species": species,
            "total_zones": len(features),
            "layers": list(zones_by_layer.keys()),
            "generator": "zone_visual_layer_v2",
            "version": "2.1.0-P1"
        }
    }
