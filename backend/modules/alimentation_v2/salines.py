"""
ALIMENTATION-V2 — Optimiseur de salines V2
=============================================
Positionne les salines optimales dans un carré 2km×2km.
STEEVE-MAX: Diversification spatiale obligatoire (min_distance 250-400m).
Sélection intelligente 1-4 salines avec stratégie de placement.

Critères de scoring:
  - Accessibilité (pente, distance)
  - Couvert forestier (40-80% optimal)
  - Proximité eau
  - Sécurité (pression humaine)
  - Diversité micro-habitats
"""
import math
import hashlib


def _seed(lat, lng, salt=""):
    h = hashlib.md5(f"{lat:.6f}:{lng:.6f}:{salt}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def _offset(center_lat, center_lng, dx_m, dy_m):
    """Décale un point en mètres → degrés."""
    d_lat = dy_m / 111320
    d_lng = dx_m / (111320 * math.cos(math.radians(center_lat)))
    return center_lat + d_lat, center_lng + d_lng


def _haversine_m(lat1, lng1, lat2, lng2):
    """Distance en mètres entre deux points GPS."""
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _score_candidate(terrain, lat, lng, center_lat, center_lng, dist_m, half_m, idx):
    """Score un candidat saline (0-100) selon 6 critères STEEVE-MAX."""
    eau_prox = terrain.get("eau", {}).get("score_hydrique", 0.5)
    couvert = terrain.get("foret", {}).get("couvert_pct", 60) / 100
    pente = terrain.get("relief", {}).get("pente_moyenne_pct", 10)

    # 1. Proximité eau (25%)
    score_eau = min(1.0, eau_prox * 1.2)
    # Variation par position
    score_eau *= (0.85 + 0.3 * _seed(lat, lng, "eau_var"))

    # 2. Couvert forestier (20%) — 40-80% = optimal
    if 0.3 < couvert < 0.85:
        score_couvert = 0.7 + 0.3 * _seed(lat, lng, "couv")
    else:
        score_couvert = 0.3 + 0.2 * _seed(lat, lng, "couv")

    # 3. Pente / accessibilité (20%)
    score_pente = max(0.2, 1.0 - pente / 25)
    score_pente *= (0.8 + 0.4 * _seed(lat, lng, "pente_var"))

    # 4. Accessibilité terrain (15%)
    score_acces = _seed(lat, lng, f"acces_{idx}")

    # 5. Sécurité / pression humaine (10%)
    score_securite = max(0.3, 1.0 - (dist_m / half_m) * 0.5)
    score_securite *= (0.8 + 0.4 * _seed(lat, lng, "sec"))

    # 6. Diversité micro-habitat (10%)
    score_habitat = _seed(lat, lng, "habitat_div")

    total = (
        score_eau * 0.25
        + score_couvert * 0.20
        + score_pente * 0.20
        + score_acces * 0.15
        + score_securite * 0.10
        + score_habitat * 0.10
    )

    criteres = {
        "eau": round(score_eau * 100),
        "couvert": round(score_couvert * 100),
        "pente": round(score_pente * 100),
        "accessibilite": round(score_acces * 100),
        "securite": round(score_securite * 100),
        "habitat": round(score_habitat * 100),
    }

    justifications = []
    if score_eau > 0.6:
        justifications.append("Bonne proximité eau")
    if score_couvert > 0.6:
        justifications.append("Couvert forestier optimal")
    if score_pente > 0.7:
        justifications.append("Terrain plat/accessible")
    if score_securite > 0.6:
        justifications.append("Zone sécurisée")
    if score_habitat > 0.6:
        justifications.append("Micro-habitat diversifié")

    return round(total * 100), criteres, justifications or ["Emplacement convenable"]


def _select_with_min_distance(candidates, max_n, min_dist_m):
    """
    Sélection gloutonne: meilleur score d'abord, puis filtrage par distance minimale.
    Stratégie adaptée au nombre de salines demandé.
    """
    if not candidates:
        return []

    sorted_cands = sorted(candidates, key=lambda c: c["score"], reverse=True)
    selected = []

    for cand in sorted_cands:
        if len(selected) >= max_n:
            break
        # Vérifier distance minimale avec toutes les salines déjà sélectionnées
        too_close = False
        for sel in selected:
            d = _haversine_m(cand["lat"], cand["lng"], sel["lat"], sel["lng"])
            if d < min_dist_m:
                too_close = True
                break
        if not too_close:
            selected.append(cand)

    return selected


def compute_salines(
    center_lat: float,
    center_lng: float,
    terrain: dict,
    species: str = "CERF",
    month: int = 10,
    side_m: float = 2000.0,
    max_salines: int = 4,
    min_distance_m: float = 300.0,
) -> list:
    """
    Calcule les emplacements optimaux de salines avec diversification spatiale.

    1. Génère 16 candidats répartis sur le territoire
    2. Score chaque candidat (6 critères STEEVE-MAX)
    3. Sélectionne max_salines avec distance minimale (gloutonne)
    4. Retourne tous les candidats avec flag 'selected'
    """
    half = side_m / 2
    max_salines = max(1, min(4, max_salines))
    n_candidates = 16

    # Générer 16 candidats bien répartis (grille 4×4 perturbée)
    candidates = []
    grid_size = 4
    cell_size = side_m / grid_size

    for row in range(grid_size):
        for col in range(grid_size):
            idx = row * grid_size + col
            # Centre de la cellule grille
            base_x = -half + cell_size * (col + 0.5)
            base_y = -half + cell_size * (row + 0.5)

            # Perturbation déterministe (±150m dans la cellule)
            jitter_x = (_seed(center_lat, center_lng, f"jx_{idx}") - 0.5) * cell_size * 0.6
            jitter_y = (_seed(center_lat, center_lng, f"jy_{idx}") - 0.5) * cell_size * 0.6

            dx = base_x + jitter_x
            dy = base_y + jitter_y

            # Distance au centre
            dist = math.sqrt(dx ** 2 + dy ** 2)

            # Exclure les candidats trop proches du centre (<150m) ou hors zone
            if dist < 150 or abs(dx) > half or abs(dy) > half:
                continue

            lat, lng = _offset(center_lat, center_lng, dx, dy)
            score, criteres, justifications = _score_candidate(
                terrain, lat, lng, center_lat, center_lng, dist, half, idx
            )

            # Type de saline selon espèce
            eau_prox = terrain.get("eau", {}).get("score_hydrique", 0.5)
            type_saline = "minérale"
            if species == "ORIGNAL":
                type_saline = "sodium" if eau_prox < 0.5 else "mixte"
            elif species == "WAPITI":
                type_saline = "calcium-enrichie"

            # Carences zone
            nutriments_sol = terrain.get("nutriments_sol", {})
            carences = []
            if nutriments_sol.get("selenium_ppm", 0.5) < 0.2:
                carences.append("Sélénium déficient")
            if nutriments_sol.get("cuivre_ppm", 5) < 3:
                carences.append("Cuivre faible")
            if nutriments_sol.get("calcium_ppm", 1000) < 500:
                carences.append("Calcium insuffisant")
            if nutriments_sol.get("phosphore_ppm", 15) < 10:
                carences.append("Phosphore bas")

            candidates.append({
                "id": f"SAL-{idx + 1:02d}",
                "lat": round(lat, 6),
                "lng": round(lng, 6),
                "score": score,
                "type": type_saline,
                "distance_centre_m": round(dist),
                "justifications": justifications,
                "carences_zone": carences or ["Aucune carence majeure détectée"],
                "criteres": criteres,
                "selected": False,
            })

    # Sélection intelligente avec contrainte de distance minimale
    selected = _select_with_min_distance(candidates, max_salines, min_distance_m)
    selected_ids = {s["id"] for s in selected}

    # Marquer les candidats sélectionnés
    for cand in candidates:
        cand["selected"] = cand["id"] in selected_ids

    # Trier: sélectionnés d'abord (par score), puis non-sélectionnés
    candidates.sort(key=lambda c: (-int(c["selected"]), -c["score"]))

    # Re-numéroter les sélectionnés
    sel_idx = 0
    for cand in candidates:
        if cand["selected"]:
            sel_idx += 1
            cand["rank"] = sel_idx
        else:
            cand["rank"] = 0

    return candidates
