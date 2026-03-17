"""
STEVE-MAX-MULTI — Consolidateur multi-engines
=================================================
Norme STEVE-MAX-MULTI + BCE-4X

Integre les attracteurs de 7 engines ecologiques:
  1. ALIMENTATION-V1 — Disponibilite nourriture (canopy, feuillus nobles)
  2. RUT-V1 — Zones de reproduction (strate, ouverture)
  3. REPOS-V1 — Zones de repos (couvert, distance humaine)
  4. TRAJETS-V1 — Corridors de deplacement (connectivite, pente faible)
  5. AFFUTS-V1 — Points d'observation strategiques (elevation, visibilite)
  6. HABITAT-V1 — Qualite globale habitat (multi-strate, diversite)
  7. CORRIDORS-V10 — Proximite corridors (connectivite ecologique)

Pipeline:
  1. Chaque engine calcule un score d'attraction [0, 1] par cellule
  2. Le consolidateur combine les scores avec ponderations normatives
  3. Le score multi-engine est utilise pour le BFS des zones organiques
  4. La fusion 64→16, la dimension dynamique et le smoothing restent inchanges

BCE-4X: Aucune alteration geometrique. Aucun deplacement de centre.
"""
import math


# ══════════════════════════════════════════════════════════
# Ponderations normatives STEVE-MAX-MULTI
# ══════════════════════════════════════════════════════════
ENGINE_WEIGHTS_BASE = {
    "alimentation_v1": 0.18,
    "rut_v1": 0.14,
    "repos_v1": 0.14,
    "trajets_v1": 0.12,
    "affuts_v1": 0.12,
    "habitat_v1": 0.15,
    "corridors_v10": 0.15,
}

# Ajustements saisonniers (mois 1-12) — modulent ENGINE_WEIGHTS
SEASONAL_MODIFIERS = {
    # Printemps (4-5): alimentation forte (regeneration), trajets actifs
    4: {"alimentation_v1": 1.3, "trajets_v1": 1.2, "rut_v1": 0.7},
    5: {"alimentation_v1": 1.3, "trajets_v1": 1.2, "rut_v1": 0.7},
    # Ete (6-8): habitat dominant, repos important (chaleur)
    6: {"habitat_v1": 1.3, "repos_v1": 1.2, "rut_v1": 0.6},
    7: {"habitat_v1": 1.3, "repos_v1": 1.3, "rut_v1": 0.5},
    8: {"habitat_v1": 1.2, "repos_v1": 1.2, "rut_v1": 0.6},
    # Automne/Rut (9-11): rut dominant, affuts importants, corridors actifs
    9: {"rut_v1": 1.4, "affuts_v1": 1.3, "corridors_v10": 1.2},
    10: {"rut_v1": 1.6, "affuts_v1": 1.4, "corridors_v10": 1.3, "repos_v1": 0.7},
    11: {"rut_v1": 1.5, "affuts_v1": 1.3, "corridors_v10": 1.2},
    # Hiver (12-3): repos dominant (conservation energie), trajets reduits
    12: {"repos_v1": 1.4, "habitat_v1": 1.2, "trajets_v1": 0.7, "rut_v1": 0.5},
    1: {"repos_v1": 1.5, "habitat_v1": 1.3, "trajets_v1": 0.6, "rut_v1": 0.4},
    2: {"repos_v1": 1.4, "habitat_v1": 1.2, "trajets_v1": 0.7, "rut_v1": 0.5},
    3: {"alimentation_v1": 1.2, "repos_v1": 1.2, "rut_v1": 0.6},
}


def get_seasonal_weights(month=10):
    """Retourne les ENGINE_WEIGHTS ajustes selon la saison."""
    weights = dict(ENGINE_WEIGHTS_BASE)
    mods = SEASONAL_MODIFIERS.get(month, {})
    for engine, modifier in mods.items():
        if engine in weights:
            weights[engine] *= modifier
    # Renormaliser pour que la somme = 1.0
    total = sum(weights.values())
    if total > 0:
        weights = {k: v / total for k, v in weights.items()}
    return weights


# Default weights (sera recalcule par saison)
ENGINE_WEIGHTS = ENGINE_WEIGHTS_BASE

# Type-specific boost: chaque type recoit un bonus de son engine primaire
TYPE_PRIMARY_ENGINE = {
    "alimentation": "alimentation_v1",
    "repos": "repos_v1",
    "rut": "rut_v1",
    "eau": "habitat_v1",
}

TYPE_PRIMARY_BOOST = 0.25  # Bonus du engine primaire pour son type


# ══════════════════════════════════════════════════════════
# Attracteurs V1 individuels
# ══════════════════════════════════════════════════════════

def alimentation_v1_attractor(cell):
    """
    ALIMENTATION-V1 — Score d'attraction nutritionnelle.
    Facteurs: canopy_density, feuillus_nobles, regeneration, NDVI saisonnier.
    """
    if cell.get("barrier"):
        return 0
    canopy = cell.get("canopy_density", 0)
    feuillus = cell.get("feuillus_nobles", 0)
    regen = cell.get("regeneration", 0.3)
    ndvi = cell.get("ndvi_seasonal", 0.5)
    return canopy * 0.35 + feuillus * 0.30 + regen * 0.15 + ndvi * 0.20


def rut_v1_attractor(cell):
    """
    RUT-V1 — Score d'attraction pour la reproduction.
    Facteurs: strate 1-3m, ouverture canopee, distance route, terrain plat.
    """
    if cell.get("barrier"):
        return 0
    strate = cell.get("strate_1_3m", 0)
    ouverture = 1.0 - cell.get("canopy_density", 0)
    d_route = min(cell.get("distance_route_m", 0), 800) / 800
    slope = cell.get("slope", 0)
    terrain_plat = max(0, 1.0 - slope / 20.0)
    return strate * 0.35 + ouverture * 0.25 + d_route * 0.20 + terrain_plat * 0.20


def repos_v1_attractor(cell):
    """
    REPOS-V1 — Score d'attraction pour le repos.
    Facteurs: couvert dense, distance humaine, terrain abrite.
    """
    if cell.get("barrier"):
        return 0
    canopy = cell.get("canopy_density", 0)
    d_route = min(cell.get("distance_route_m", 0), 500) / 500
    d_bat = min(cell.get("distance_batiment_m", 0), 500) / 500
    conifer = cell.get("conifer_density", 0.5)
    return canopy * 0.30 + d_route * 0.25 + d_bat * 0.20 + conifer * 0.25


def trajets_v1_attractor(cell):
    """
    TRAJETS-V1 — Score d'attraction pour les deplacements.
    Facteurs: connectivite ecologique, pente faible, absence de barrieres.
    """
    if cell.get("barrier"):
        return 0
    ecl = cell.get("ecl_connectivity", 0.5)
    slope = cell.get("slope", 0)
    pente_score = max(0, 1.0 - slope / 25.0)
    d_eau = cell.get("distance_eau_m", 500)
    # Proximite eau favorise les trajets (points d'eau en transit)
    eau_prox = max(0, 1.0 - d_eau / 300)
    vallon = 0.2 if cell.get("micro_topo_vallon", False) else 0
    return ecl * 0.35 + pente_score * 0.30 + eau_prox * 0.15 + vallon + 0.20


def affuts_v1_attractor(cell):
    """
    AFFUTS-V1 — Score d'attraction pour les points d'observation.
    Facteurs: elevation relative, visibilite, crete, lisiere.
    """
    if cell.get("barrier"):
        return 0
    crete = 0.3 if cell.get("micro_topo_crete", False) else 0
    replat = 0.2 if cell.get("micro_topo_replat", False) else 0
    canopy = cell.get("canopy_density", 0)
    lisiere = 1.0 - abs(canopy - 0.5) * 2  # Optimal a 50% canopy = lisiere
    d_route = min(cell.get("distance_route_m", 0), 500) / 500
    return crete + replat + lisiere * 0.30 + d_route * 0.20


def habitat_v1_attractor(cell):
    """
    HABITAT-V1 — Score qualite globale de l'habitat.
    Facteurs: diversite structurale, eau, couvert, perturbation humaine.
    """
    if cell.get("barrier"):
        return 0
    canopy = cell.get("canopy_density", 0)
    strate = cell.get("strate_1_3m", 0)
    feuillus = cell.get("feuillus_nobles", 0)
    d_eau = cell.get("distance_eau_m", 500)
    eau_prox = max(0, 1.0 - d_eau / 300)
    d_route = min(cell.get("distance_route_m", 0), 800) / 800
    d_bat = min(cell.get("distance_batiment_m", 0), 800) / 800
    # Diversite structurale (multi-strate)
    diversite = (canopy * strate * feuillus) ** (1.0 / 3.0)
    # Perturbation humaine inverse
    calme = (d_route + d_bat) / 2
    return diversite * 0.35 + eau_prox * 0.15 + calme * 0.25 + canopy * 0.25


def corridors_v10_attractor(cell):
    """
    CORRIDORS-V10 — Score de connectivite ecologique.
    Facteurs: ECL, zone tampon, regeneration, absence de barrieres.
    """
    if cell.get("barrier"):
        return 0
    ecl = cell.get("ecl_connectivity", 0.5)
    tampon = 0.15 if cell.get("zone_tampon", False) else 0
    regen = cell.get("regeneration", 0.3)
    slope = cell.get("slope", 0)
    pente_ok = max(0, 1.0 - slope / 30.0)
    return ecl * 0.40 + tampon + regen * 0.20 + pente_ok * 0.25


# ══════════════════════════════════════════════════════════
# Consolidateur STEVE-MAX-MULTI
# ══════════════════════════════════════════════════════════

# Registre des engines pour validation et firewall
ENGINE_REGISTRY = {
    "alimentation_v1": alimentation_v1_attractor,
    "rut_v1": rut_v1_attractor,
    "repos_v1": repos_v1_attractor,
    "trajets_v1": trajets_v1_attractor,
    "affuts_v1": affuts_v1_attractor,
    "habitat_v1": habitat_v1_attractor,
    "corridors_v10": corridors_v10_attractor,
}


def score_cell_multi_engine(cell, zone_type, base_score, month=10):
    """
    STEVE-MAX-MULTI — Score consolide multi-engine pour une cellule.

    Combine le score de base (type-specific) avec les attracteurs
    de tous les 7 engines V1 selon les ponderations normatives saisonnieres.

    Args:
        cell: Donnees de la cellule (dict)
        zone_type: Type de zone ecologique (str)
        base_score: Score de base du type primaire (float 0-1)
        month: Mois pour ajustement saisonnier (int 1-12)

    Returns:
        float: Score consolide [0, 1]
    """
    if cell.get("barrier"):
        return 0

    # Ponderations saisonnieres
    weights = get_seasonal_weights(month)

    # Calculer les attracteurs multi-engine
    engine_scores = {}
    for name, func in ENGINE_REGISTRY.items():
        engine_scores[name] = func(cell)

    # Score multi-engine pondere
    multi = sum(
        engine_scores[name] * weights.get(name, 0)
        for name in ENGINE_REGISTRY
    )

    # Boost du engine primaire pour ce type de zone
    primary_engine = TYPE_PRIMARY_ENGINE.get(zone_type)
    if primary_engine and primary_engine in engine_scores:
        multi += engine_scores[primary_engine] * TYPE_PRIMARY_BOOST

    # Normaliser [0, 1]
    multi = min(1.0, multi)

    # Combinaison: 55% base type + 45% multi-engine
    consolidated = base_score * 0.55 + multi * 0.45

    return min(1.0, consolidated)


def get_engine_breakdown(cell):
    """
    Retourne le detail des scores par engine pour une cellule.
    Utilise pour le diagnostic et la validation BCE-4X.
    """
    breakdown = {}
    for name, func in ENGINE_REGISTRY.items():
        breakdown[name] = round(func(cell), 4)
    return breakdown
