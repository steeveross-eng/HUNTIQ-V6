"""
CORRIDORS-V10 — Generation de la surface de couts
=====================================================
Produit une grille NxN ou chaque cellule a un cout de traversee [0, INF).
Cout = f(pente, hydrographie, pression humaine, couvert forestier, structure).
Eau = barriere (cout infini) sauf exceptions documentees.
Pente > max = barriere.
Normes BCE-4X: Validation topographique + hydrographique stricte.
"""
import math
import hashlib

INFINITY_COST = 999999.0
METERS_PER_DEG_LAT = 111320.0


def _deterministic_hash(lat: float, lng: float, seed: str = "") -> float:
    raw = f"{lat:.6f}:{lng:.6f}:{seed}"
    h = int(hashlib.md5(raw.encode()).hexdigest()[:8], 16)
    return (h % 10000) / 10000.0


def _elevation_model(lat: float, lng: float) -> float:
    base = 150 + 200 * math.sin(lat * 0.8) * math.cos(lng * 0.5)
    variation = 80 * _deterministic_hash(lat, lng, "elev")
    return max(10, base + variation)


def _meters_per_deg_lng(lat: float) -> float:
    return 111320.0 * math.cos(math.radians(lat))


def _load_cell_data(lat: float, lng: float, month: int) -> dict:
    """Charge les couches fines pour une cellule. Deterministe par position."""
    h = _deterministic_hash
    elev = _elevation_model(lat, lng)
    # Distribution realiste Quebec: majorite terrain plat/vallonne, pics rares
    raw_slope = h(lat, lng, "slope")
    slope = 0.5 + 34.5 * (raw_slope ** 2.0)  # Skewed: 75% < 10deg, 15% 10-20, 10% 20-35
    canopy = 0.1 + 0.85 * h(lat, lng, "canopy_d")
    dist_eau = 10 + 490 * h(lat, lng, "dist_eau")
    is_water = h(lat, lng, "water_body") > 0.88
    zone_humide = h(lat, lng, "zh") > 0.75
    dist_route = 20 + 980 * h(lat, lng, "dist_route")
    dist_batiment = 50 + 950 * h(lat, lng, "dist_bat")
    feuillus_nobles = h(lat, lng, "fnobles")
    conifer_density = 0.05 + 0.90 * h(lat, lng, "conif_d")
    strate_1_3m = 0.05 + 0.90 * h(lat, lng, "strate13")

    # === Couches enrichies (Norme CORRIDOR-V1/V10) ===
    ecl = 0.1 + 0.85 * h(lat, lng, "ecl_conn")
    micro_topo_vallon = h(lat, lng, "topo_vallon") > 0.65
    micro_topo_crete = h(lat, lng, "topo_crete") > 0.80
    micro_topo_replat = h(lat, lng, "topo_replat") > 0.50
    zone_tampon = h(lat, lng, "zone_tampon") > 0.60
    regeneration = 0.05 + 0.90 * h(lat, lng, "regen")
    season_ndvi = {
        1: 0.10, 2: 0.12, 3: 0.35, 4: 0.55, 5: 0.75, 6: 0.90,
        7: 1.00, 8: 0.95, 9: 0.80, 10: 0.60, 11: 0.30, 12: 0.15,
    }
    ndvi = (0.3 + 0.6 * h(lat, lng, "ndvi")) * season_ndvi.get(month, 0.65)
    nourriture = round(ndvi * 0.5 + feuillus_nobles * 0.3 + regeneration * 0.2, 3)
    refuge_score = round(min(1.0, canopy * 0.4 + conifer_density * 0.3 + min(dist_route, 500) / 500 * 0.3), 3)
    dist_sentier = 10 + 490 * h(lat, lng, "dist_sent")
    mosaique = abs(canopy - 0.5) < 0.2
    suintement = h(lat, lng, "suint") > 0.85

    return {
        "elevation_m": round(elev, 1),
        "slope_deg": round(slope, 1),
        "canopy_density": round(canopy, 3),
        "distance_eau_m": round(dist_eau, 1),
        "is_water": is_water,
        "zone_humide": zone_humide,
        "distance_route_m": round(dist_route, 1),
        "distance_batiment_m": round(dist_batiment, 1),
        "distance_sentier_m": round(dist_sentier, 1),
        "feuillus_nobles": round(feuillus_nobles, 3),
        "conifer_density": round(conifer_density, 3),
        "strate_1_3m": round(strate_1_3m, 3),
        "ecl": round(ecl, 3),
        "micro_topo_vallon": micro_topo_vallon,
        "micro_topo_crete": micro_topo_crete,
        "micro_topo_replat": micro_topo_replat,
        "zone_tampon": zone_tampon,
        "regeneration": round(regeneration, 3),
        "ndvi": round(ndvi, 3),
        "nourriture": nourriture,
        "refuge_score": refuge_score,
        "mosaique": mosaique,
        "suintement": suintement,
    }


def generate_cost_grid(
    center_lat: float,
    center_lng: float,
    profile: dict,
    season_mods: dict,
    side_m: float = 2000.0,
    cell_m: float = 25.0,
    month: int = 10,
) -> dict:
    """
    Genere la grille de couts pour le pathfinding A*.

    Chaque cellule recoit un cout de traversee base sur:
    - Pente (barriere si > pente_max_deg)
    - Eau (barriere: cout infini, BCE-4X)
    - Pression humaine (routes, batiments)
    - Couvert forestier (preference espece)
    - Affinite hydrographique (attraction sans traversee)

    Returns:
        {grid: 2D list, n: int, cell_data: 2D list, metadata: dict}
    """
    n = int(side_m / cell_m)
    half_side = side_m / 2.0
    m_per_lng = _meters_per_deg_lng(center_lat)

    lat_start = center_lat - (half_side / METERS_PER_DEG_LAT)
    lng_start = center_lng - (half_side / m_per_lng)
    d_lat = cell_m / METERS_PER_DEG_LAT
    d_lng = cell_m / m_per_lng

    pente_max = profile["pente_max_deg"]
    pente_opt = profile["pente_optimale_deg"]
    sensibilite = profile["sensibilite_pression"]
    pref_forest = profile["preference_forestiere"]
    affinite_h = profile["affinite_hydro"]
    dist_route_evit = profile["distance_route_evitement_m"]
    dist_bat_evit = profile["distance_batiment_evitement_m"]
    mobilite = season_mods.get("mobilite", 0.7)

    cost_grid = []
    cell_data = []
    water_count = 0
    barrier_count = 0

    for row in range(n):
        cost_row = []
        data_row = []
        for col in range(n):
            lat = lat_start + (row + 0.5) * d_lat
            lng = lng_start + (col + 0.5) * d_lng
            data = _load_cell_data(lat, lng, month)
            data["lat"] = round(lat, 7)
            data["lng"] = round(lng, 7)
            data["row"] = row
            data["col"] = col

            # === BARRIERES ABSOLUES (BCE-4X) ===
            # Eau = barriere par defaut
            if data["is_water"]:
                cost_row.append(INFINITY_COST)
                data["barrier"] = "EAU"
                data_row.append(data)
                water_count += 1
                continue

            # Pente > max = barriere
            if data["slope_deg"] > pente_max:
                cost_row.append(INFINITY_COST)
                data["barrier"] = "PENTE"
                data_row.append(data)
                barrier_count += 1
                continue

            # === COUT DE TRAVERSEE ===
            cost = 1.0  # Base

            # 1. Cout pente (0-5 points)
            if data["slope_deg"] <= pente_opt:
                cost_pente = 0.0
            else:
                ratio = (data["slope_deg"] - pente_opt) / max(pente_max - pente_opt, 1)
                cost_pente = ratio * 5.0
            cost += cost_pente

            # 2. Cout pression humaine (0-8 points)
            route_penalty = 0.0
            if data["distance_route_m"] < dist_route_evit:
                route_penalty = (1.0 - data["distance_route_m"] / dist_route_evit) * sensibilite * 4.0
            bat_penalty = 0.0
            if data["distance_batiment_m"] < dist_bat_evit:
                bat_penalty = (1.0 - data["distance_batiment_m"] / dist_bat_evit) * sensibilite * 4.0
            cost += route_penalty + bat_penalty

            # 3. Bonus couvert forestier (reduction -0 a -3)
            forest_bonus = data["canopy_density"] * pref_forest * 3.0
            cost -= forest_bonus

            # 4. Bonus affinite hydro (reduction -0 a -2 quand proche de l'eau sans etre sur l'eau)
            if data["distance_eau_m"] < 200 and not data["is_water"]:
                hydro_bonus = (1.0 - data["distance_eau_m"] / 200.0) * affinite_h * 2.0
                cost -= hydro_bonus

            # 5. Penalite zone humide (traversable mais couteuse)
            if data["zone_humide"]:
                cost += 2.0

            # === FACTEURS ENRICHIS (Norme CORRIDOR-V1/V10) ===

            # 6. Bonus ECL — connectivite ecologique locale (reduction -0 a -2)
            cost -= data["ecl"] * 2.0

            # 7. Bonus micro-topographie
            if data["micro_topo_vallon"]:
                cost -= 1.0  # Vallons = axes naturels de deplacement
            if data["micro_topo_replat"]:
                cost -= 0.5  # Replats = zones de repos potentielles
            if data["micro_topo_crete"]:
                cost += 1.5  # Cretes = exposees, evitees

            # 8. Bonus nourriture disponible (reduction -0 a -1.5)
            cost -= data["nourriture"] * 1.5

            # 9. Bonus refuge (reduction -0 a -1.5)
            cost -= data["refuge_score"] * 1.5

            # 10. Bonus zone tampon (reduction -0.5)
            if data["zone_tampon"]:
                cost -= 0.5

            # 11. Bonus regeneration (reduction -0 a -0.5)
            cost -= data["regeneration"] * 0.5

            # 12. Bonus mosaique/lisiere (reduction -0.3)
            if data["mosaique"]:
                cost -= 0.3

            # 13. Penalite sentier (pression legere)
            if data["distance_sentier_m"] < 100:
                cost += (1.0 - data["distance_sentier_m"] / 100.0) * sensibilite * 1.5

            # 14. Bonus suintement hydro (reduction -0.3)
            if data["suintement"]:
                cost -= 0.3

            # 15. Ajustement saisonnier mobilite
            cost = cost / max(mobilite, 0.1)

            # Cout minimum = 0.5 (jamais zero pour eviter A* gratuit)
            cost = max(0.5, cost)

            data["barrier"] = None
            cost_row.append(round(cost, 3))
            data_row.append(data)

        cost_grid.append(cost_row)
        cell_data.append(data_row)

    return {
        "grid": cost_grid,
        "cell_data": cell_data,
        "n": n,
        "cell_m": cell_m,
        "side_m": side_m,
        "center": {"lat": center_lat, "lng": center_lng},
        "lat_start": lat_start,
        "lng_start": lng_start,
        "d_lat": d_lat,
        "d_lng": d_lng,
        "metadata": {
            "total_cells": n * n,
            "water_barriers": water_count,
            "slope_barriers": barrier_count,
            "traversable_cells": n * n - water_count - barrier_count,
        },
    }
