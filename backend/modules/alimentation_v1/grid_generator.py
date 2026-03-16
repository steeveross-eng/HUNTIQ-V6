"""
ALIMENTATION-V1 — Générateur de grille 10m×10m
================================================
Génère une grille de cellules 10m×10m à l'intérieur du carré 2km² existant.
NE RECRÉE PAS le périmètre — utilise lat/lng + rayon existant.
"""
import math

METERS_PER_DEG_LAT = 111320.0


def meters_per_deg_lng(lat: float) -> float:
    return 111320.0 * math.cos(math.radians(lat))


def generate_grid_10m(center_lat: float, center_lng: float, side_m: float = 2000.0, cell_m: float = 10.0):
    """
    Génère une grille de cellules dans le carré 2km² existant.

    Args:
        center_lat: Latitude du centre du carré existant
        center_lng: Longitude du centre du carré existant
        side_m: Côté du carré en mètres (défaut 2000 = 2km²)
        cell_m: Taille de chaque cellule en mètres (défaut 10m)

    Returns:
        Liste de cellules, chacune avec (row, col, lat, lng, bounds)
    """
    half_side = side_m / 2.0
    n_cells = int(side_m / cell_m)
    m_per_lng = meters_per_deg_lng(center_lat)

    lat_start = center_lat - (half_side / METERS_PER_DEG_LAT)
    lng_start = center_lng - (half_side / m_per_lng)

    d_lat = cell_m / METERS_PER_DEG_LAT
    d_lng = cell_m / m_per_lng

    cells = []
    for row in range(n_cells):
        for col in range(n_cells):
            cell_lat = lat_start + (row + 0.5) * d_lat
            cell_lng = lng_start + (col + 0.5) * d_lng
            cells.append({
                "row": row,
                "col": col,
                "lat": round(cell_lat, 7),
                "lng": round(cell_lng, 7),
                "bounds": {
                    "south": round(lat_start + row * d_lat, 7),
                    "north": round(lat_start + (row + 1) * d_lat, 7),
                    "west": round(lng_start + col * d_lng, 7),
                    "east": round(lng_start + (col + 1) * d_lng, 7),
                },
            })

    return {
        "center": {"lat": center_lat, "lng": center_lng},
        "side_m": side_m,
        "cell_m": cell_m,
        "n_cells_per_side": n_cells,
        "total_cells": len(cells),
        "cells": cells,
    }


def get_grid_summary(center_lat: float, center_lng: float, side_m: float = 2000.0, cell_m: float = 10.0):
    n_cells = int(side_m / cell_m)
    return {
        "center": {"lat": center_lat, "lng": center_lng},
        "side_m": side_m,
        "cell_m": cell_m,
        "n_cells_per_side": n_cells,
        "total_cells": n_cells * n_cells,
        "area_km2": (side_m / 1000) ** 2,
    }
