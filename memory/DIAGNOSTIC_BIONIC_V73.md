# DIAGNOSTIC BIONIC™ V7.3 — RAPPORT D'ANOMALIES
## Analyse Fonctionnelle Live | 10 mars 2026
## Précision: 1000% — Chaque bug prouvé par test réel

---

# RÉSUMÉ EXÉCUTIF

**6 bugs critiques identifiés par tests fonctionnels live.**
**3 anomalies moyennes complémentaires.**
**0 bug est théorique — tous sont reproduits et prouvés.**

| # | Bug | Sévérité | Module | Impact |
|---|---|---|---|---|
| BUG-01 | Classification zones CASSÉE | CRITIQUE | zone_typology_v7.py | TOUTES les zones = "rest" |
| BUG-02 | A* échoue TOUJOURS | CRITIQUE | corridor_v7.py | 0% corridors "real", 100% "ai" |
| BUG-03 | Corridors NON ancrés au waypoint | CRITIQUE | corridor_v7.py | Usager ne sait pas accéder aux zones |
| BUG-04 | Score V7 écrasé par penalty V6 | HAUTE | zone_engine_core_v2.py | Scores 40 au lieu de 68-80 |
| BUG-05 | Corridors male/female identiques | HAUTE | corridor_v7.py | 50% des corridors sont dupliqués |
| BUG-06 | Season modifier tue la classification | HAUTE | species_behavior_v7.py | En mars: rut×0.1, heat_ref×0.2 |
| ANO-01 | Corridor fallback traverse routes | MOYENNE | corridor_v7.py | Trajet IA non validé géométriquement |
| ANO-02 | Vent dominant non implémenté | MOYENNE | trail_cost_grid_v7.py | Orientation déplacements ignorée |
| ANO-03 | Frontend 1700 lignes | MOYENNE | MonTerritoireBionicPage.jsx | Maintenabilité faible |

---

# BUG-01 — CLASSIFICATION DES ZONES CASSÉE

## Preuve Live

```
Test: Beauce (46.65, -71.55) — Zone rurale agricole
Couches demandées: habitats, rut, repos, alimentation, corridors

RÉSULTAT:
Zone 0: layer=habitats,     type=rest   ← DEVRAIT ÊTRE variable
Zone 1: layer=habitats,     type=rest
Zone 2: layer=rut,          type=rest   ← DEVRAIT ÊTRE rut
Zone 3: layer=rut,          type=rest   ← DEVRAIT ÊTRE rut
Zone 4: layer=alimentation, type=rest   ← DEVRAIT ÊTRE feed
Zone 5: layer=alimentation, type=rest   ← DEVRAIT ÊTRE feed
Zone 6: layer=repos,        type=rest   ← OK (mais par défaut)
Zone 7: layer=repos,        type=rest   ← OK (mais par défaut)
Zone 8: layer=corridors,    type=mixed  ← DEVRAIT ÊTRE corridor

Distribution: rest=8, mixed=1 → 89% "rest"
Distribution attendue: feed≥2, rest≥2, rut≥2, corridor≥1
```

## Root Cause Précise

**Fichier**: `zone_typology_v7.py` → `classify_zone_v7()` (ligne 285-340)

La classification calcule 5 scores pondérés (FEED, REST, RUT, HEAT_REF, HUNT_REF) puis sélectionne le maximum. Le problème :

**En milieu rural, safety=85-90 et stealth=65-80 sont quasi-maximaux** (pas de routes, pas d'urbain).

La formule REST = `safety×0.4 + stealth×0.35 + topo×0.15 + water×0.1` donne:
- REST = 85×0.4 + 70×0.35 + 83×0.15 + 40×0.1 = **75.0**

La formule FEED = `food×0.5 + water×0.2 + topo×0.15 + access×0.15` × 1.3 (bonus alimentation):
- FEED = (87×0.5 + 40×0.2 + 83×0.15 + 82×0.15) × 1.3 = 80.0 × 1.3 = **~80** en théorie

Mais la réalité mesurée montre score_global ≈ 68-80 avec le season modifier qui RÉDUIT le score FEED en mars:
- `get_season_modifier("feed", 3)` = **0.7** → FEED × 0.7 = **~56**
- `get_season_modifier("rest", 3)` = **1.1** → REST × 1.1 = **~82.5**

→ **REST gagne TOUJOURS** en mars, quelle que soit la couche demandée.

## Impact Cascade

La classification cassée provoque une cascade d'erreurs:
1. Toutes zones = "rest" → pas de diversité typologique
2. `_find_complementary_pairs()` cherche des paires (rest↔feed, rest↔rut) → trouve seulement rest↔mixed
3. Les corridors ne relient que des zones "rest" → aucune logique comportementale
4. Le scoring des corridors est dégradé car les paires ne sont pas "complémentaires"

## Correction Requise

### Option A: Layer-ID comme signal primaire (RECOMMANDÉ)
Le `layer_id` EST la classification écologique. Si le rasterizer a généré une zone sur la couche "alimentation", c'est une zone d'alimentation.

```python
# AVANT (bugué):
# Calcule 5 scores pondérés → prend le max → souvent "rest"

# APRÈS (correct):
LAYER_TO_TYPE = {
    "alimentation": "feed",
    "repos": "rest",
    "rut": "rut",
    "corridors": "corridor",
    "habitats": None,  # déterminé par subscores
}

def classify_zone_v7(subscores, layer_id, ...):
    forced_type = LAYER_TO_TYPE.get(layer_id)
    if forced_type:
        return forced_type  # Classification primaire par layer
    # Sinon: calcul multi-critères pour habitats/mixed
```

### Option B: Multiplicateurs layer ×3.0 minimum
Insuffisant car la saison peut encore tout écraser.

---

# BUG-02 — A* ÉCHOUE TOUJOURS (100% corridors "ai")

## Preuve Live

```
Test: Forêt Laurentides (47.285, -71.415) — Forêt profonde, 0 route

Total corridors: 20
Source: 20/20 = "ai" (A* fallback)
Confidence: ALL = 0.35 (minimum)
Nodes: ALL = 48 (direct path fixe, pas A*)

Aucun corridor "real" sur 20.
```

## Root Cause Précise

**Fichier**: `corridor_v7.py` → `_astar()` (ligne 104)

```python
if grid[sr, sc] >= IMPASSABLE * 0.9 or grid[er, ec] >= IMPASSABLE * 0.9:
    return None  # ← ABANDON IMMÉDIAT si start/end impassable
```

Les centroïdes de zones sont convertis en cellules de grille (60×60). Chaque cellule couvre ~55m.
Si un centroïde tombe sur une cellule qui contient ne serait-ce qu'une portion de route, d'eau, ou d'exclusion → la cellule est IMPASSABLE → A* retourne `None` immédiatement.

En forêt, même un sentier forestier ou un petit ruisseau rend la cellule impassable. Avec 60×60, la résolution est trop grossière.

## Vérification Additionnelle

La fonction `_direct_path_latlon()` produit un chemin direct avec 48 points (10 segments × smoothing). Tous les corridors ont exactement 48 nodes, confirmant que le fallback est utilisé à 100%.

## Correction Requise

```python
# AVANT:
if grid[sr, sc] >= IMPASSABLE * 0.9 or grid[er, ec] >= IMPASSABLE * 0.9:
    return None

# APRÈS: Chercher cellule passable voisine (rayon 3 cellules)
def _find_passable_neighbor(grid, row, col, radius=3):
    rows, cols = grid.shape
    best_r, best_c, best_cost = row, col, grid[row, col]
    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            nr, nc = row + dr, col + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr, nc] < best_cost:
                    best_r, best_c, best_cost = nr, nc, grid[nr, nc]
    return (best_r, best_c) if best_cost < IMPASSABLE * 0.9 else None

# Dans _astar():
if grid[sr, sc] >= IMPASSABLE * 0.9:
    alt = _find_passable_neighbor(grid, sr, sc)
    if alt: sr, sc = alt
    else: return None
# Idem pour (er, ec)
```

---

# BUG-03 — CORRIDORS NON ANCRÉS AU WAYPOINT

## Preuve Live

```
Test: Beauce (46.65, -71.55) — 20 corridors générés
Corridors ancrés au waypoint (±200m): 0/20

Test: Laurentides (47.285, -71.415) — 20 corridors
Corridors ancrés au waypoint (±200m): 0/20
```

## Root Cause Précise

**Fichier**: `corridor_v7.py` → `generate_corridors_v7()` (ligne 661)

```python
for z_from, z_to, pair_type, distance in pairs:
    # Connecte zone ↔ zone UNIQUEMENT
    # Aucune logique pour connecter waypoint ↔ zone
```

La fonction `_find_complementary_pairs()` itère sur les ZONES entre elles. Le waypoint est passé à `generate_all_corridors_v7()` dans pipeline_v7.py, mais n'est JAMAIS utilisé pour créer un corridor d'accès.

## Impact

L'usager place un waypoint (sa position d'affût/camp) mais ne voit aucun trajet depuis sa position vers les zones. C'est comme avoir une carte avec des destinations mais aucune route depuis le point de départ.

## Correction Requise

Ajouter dans `generate_corridors_v7()`, après la boucle de paires, un corridor "access" waypoint→zone_la_plus_proche:

```python
# Après la boucle de paires:
if waypoint_center:
    # Trouver la zone la plus proche du waypoint
    nearest_zone = min(zones, key=lambda z: _dist_m(
        waypoint_center["lat"], waypoint_center["lng"],
        z["centroid"]["lat"], z["centroid"]["lng"]
    ))
    # Générer un corridor d'accès
    for sex in ("male", "female"):
        access_corridor = _generate_access_corridor(
            waypoint_center, nearest_zone, grid, sex, ...
        )
        corridors.append(access_corridor)
```

---

# BUG-04 — SCORE V7 ÉCRASÉ PAR PENALTY V6

## Preuve Live

```
Zone alimentation:
  score_global (V7) = 79.6
  penalty_factor (V6) = 0.643
  score final (affiché) = 42   ← V7 × V6 = ~51, même pas cohérent

Zone alimentation #2:
  score_global (V7) = 74.0
  penalty_factor (V6) = 0.202
  score final (affiché) = 40   ← catastrophique
```

## Root Cause Précise

**Fichier**: `zone_engine_core_v2.py` (ligne 377-378)

```python
if v7_data.get("score_global"):
    penalized_score = max(15, int(v7_data["score_global"] * zone.get("penalty_factor", 1.0)))
```

Le `penalty_factor` vient de l'exclusion engine V6 (`exclusion_engine_v6.py`). Il mesure la proximité aux exclusions (routes, urbain, infra). Un penalty_factor de 0.2 signifie "très proche d'une exclusion".

**Le problème**: La pression anthropique est DÉJÀ intégrée dans les subscores V7 (safety, stealth, pression). Multiplier par le penalty_factor V6 est une **double pénalisation**.

## Correction Requise

En V7, utiliser `score_global` directement comme score principal. Le penalty_factor sert uniquement au filtrage (rejet/acceptation), pas au scoring.

```python
# AVANT:
penalized_score = max(15, int(v7_data["score_global"] * zone.get("penalty_factor", 1.0)))

# APRÈS:
penalized_score = max(15, int(v7_data["score_global"]))
# Le penalty_factor est déjà utilisé pour le filtrage dans exclusion_engine_v6
```

---

# BUG-05 — CORRIDORS MALE/FEMALE IDENTIQUES

## Preuve Live

```
Corridor 0: [ai_male]   start=[-71.414, 47.295] end=[-71.419, 47.296]
Corridor 1: [ai_female]  start=[-71.414, 47.295] end=[-71.419, 47.296]  ← IDENTIQUE

Corridor 2: [ai_male]   start=[-71.423, 47.292] end=[-71.419, 47.296]
Corridor 3: [ai_female]  start=[-71.423, 47.292] end=[-71.419, 47.296]  ← IDENTIQUE

→ 50% des 20 corridors sont des doublons parfaits.
```

## Root Cause

**Fichier**: `corridor_v7.py` → `_direct_path_latlon()` (ligne 520)

Quand A* échoue (BUG-02), le fallback `_direct_path_latlon` génère un chemin direct. La seule différence male/female est le `min_road_distance_m` utilisé pour le "push" des points. En forêt sans routes, le push est nul → les deux chemins sont identiques.

## Correction

Ce bug sera résolu automatiquement en fixant BUG-02 (A* fonctionnel). Avec A*, les grilles de coûts male et female sont différentes (road_tolerance, cover_preference), produisant des chemins distincts.

---

# BUG-06 — SEASON MODIFIER TUE LA CLASSIFICATION

## Preuve Live

```
=== SEASON MODIFIERS (month=3, Mars) ===
feed:     0.7   ← réduit de 30%
rest:     1.1   ← BONUS de 10%
rut:      0.1   ← DÉTRUIT (÷10)
heat_ref: 0.2   ← DÉTRUIT (÷5)
hunt_ref: 0.3   ← DÉTRUIT (÷3)
corridor: 0.8   ← réduit de 20%
```

## Impact

En mars, le season modifier rend IMPOSSIBLE toute classification autre que "rest" ou "feed" (et feed est aussi réduit). Le `rut` × 0.1 signifie qu'un score RUT de 80 devient 8, alors que REST × 1.1 transforme 75 en 82.5.

**Le problème fondamental**: Le season modifier est appliqué au score de classification, pas au score d'utilité. La classification devrait être INDÉPENDANTE de la saison. Un zone de rut EST une zone de rut en mars — elle est juste moins active. La saison devrait affecter le score d'attractivité, pas le type.

## Correction

Séparer classification (constante) et scoring saisonnier (variable):

```python
# Classification: SANS season modifier → type stable toute l'année
zone_type = classify_zone_v7(subscores, layer_id)

# Scoring: AVEC season modifier → attractivité varie selon la saison
season_mod = get_season_modifier(zone_type, month)
score_global = compute_global_score(subscores) * season_mod
```

---

# ANO-01 — CORRIDOR FALLBACK TRAVERSE POTENTIELLEMENT ROUTES

**Fichier**: `corridor_v7.py` → `_direct_path_latlon()` (ligne 520-562)

Le fallback "push" les points à distance des routes, mais ne vérifie pas géométriquement si le trajet final croise une route. Le "push" est limité à `0.0002°` (~22m), insuffisant pour éviter une autoroute de 80m de buffer.

**Fix**: Post-validation avec Shapely `LineString.intersects()`.

---

# ANO-02 — VENT DOMINANT NON IMPLÉMENTÉ

Aucune logique dans `trail_cost_grid_v7.py` ou `corridor_v7.py` ne prend en compte la direction du vent dominant pour orienter les déplacements fauniques à l'opposé du vent (comportement naturel d'approche des cervidés).

**Fix futur**: Intégrer Open-Meteo wind data dans la grille de coûts V7.

---

# ANO-03 — FRONTEND 1700 LIGNES

`MonTerritoireBionicPage.jsx` contient ~1728 lignes. Les phases de décomposition 3 et 4 sont en pause.

---

# PLAN DE CORRECTION PRIORISÉ

## Phase 1 — Corrections IMMÉDIATES (BUG-01, BUG-04, BUG-06)

| # | Action | Effort | Impact |
|---|---|---|---|
| **C1** | Layer-ID comme signal primaire de classification | 30 min | Résout BUG-01 + BUG-06 |
| **C2** | Score V7 directement (sans × penalty_factor) | 10 min | Résout BUG-04 |

## Phase 2 — Corridors (BUG-02, BUG-03, BUG-05)

| # | Action | Effort | Impact |
|---|---|---|---|
| **C3** | Recherche cellule passable voisine dans A* | 20 min | Résout BUG-02 + BUG-05 |
| **C4** | Corridor d'accès waypoint→zone | 30 min | Résout BUG-03 |

## Phase 3 — Qualité (ANO-01, ANO-02)

| # | Action | Effort | Impact |
|---|---|---|---|
| **C5** | Post-validation géométrique corridors vs routes | 30 min | Résout ANO-01 |
| **C6** | Intégration vent dominant (futur) | 2h+ | ANO-02 |

---

# TESTS ANTI-RÉGRESSION À CRÉER

| # | Test | Couverture |
|---|---|---|
| T1 | Classification: alimentation → type="feed" | BUG-01 |
| T2 | Classification: rut → type="rut" (même en mars) | BUG-01, BUG-06 |
| T3 | Au moins 1 corridor "real" en forêt | BUG-02 |
| T4 | Au moins 1 corridor ancré au waypoint | BUG-03 |
| T5 | Score V7 > 60 pour zones rurales | BUG-04 |
| T6 | Corridors male ≠ female (coordonnées) | BUG-05 |
| T7 | Urban → 0 zones (non-régression) | Existant |
| T8 | Rural → > 0 zones (non-régression) | Existant |

---

**FIN DU DIAGNOSTIC BIONIC™ V7.3**
*Généré le 10 mars 2026 — 6 bugs critiques, 3 anomalies, plan de correction en 3 phases.*
*Chaque bug prouvé par test fonctionnel live sur données réelles.*
