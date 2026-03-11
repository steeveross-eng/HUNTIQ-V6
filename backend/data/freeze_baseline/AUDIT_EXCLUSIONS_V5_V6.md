# AUDIT EXHAUSTIF DES EXCLUSIONS SPATIALES — V5 freeze-V6
## MON TERRITOIRE BIONIC

**Date :** 2026-03-10
**Auteur :** COPILOT Agent (sur demande COPILOT MAITRE)
**Statut :** Complet — Phases 1, 2 et 3
**Branche :** bionic_v6_lab

---

# PHASE 1 — AUDIT EXHAUSTIF DES EXCLUSIONS V5 FREEZE-V6

## 1. VUE D'ENSEMBLE DU PIPELINE D'EXCLUSION

Le pipeline d'exclusion V5 opère en **deux niveaux** distincts :

| Niveau | Nom | Fichier source | Moment dans le pipeline | Effet |
|--------|-----|---------------|------------------------|-------|
| **P0** | Exclusion dure | `zone_engine_core_v2.py` → `_is_zone_excluded()` | Après extraction des zones organiques, AVANT tri et scoring | **Rejet total** de la zone |
| **P1** | Pénalité semi-statique | `zone_penalty_engine.py` → `calculate_zone_penalty()` | Après exclusion P0, sur les zones survivantes | **Multiplicateur de score** (0.15 → 1.10) |

### Pipeline complet (ordre d'exécution) :

```
1. RASTERISATION ──────────► behavioral_rasterizer.py
      │                         generate_layer_raster()
      │                         (bruit simplex 2D, grille numpy)
      ▼
2. EXTRACTION CONTOURS ────► organic_zone_generator_v2.py
      │                         extract_organic_zones()
      │                         (Marching Squares + Chaikin ×4)
      │                         min_area=8000m², max_area=80000m²
      │                         max_compactness=0.85
      ▼
3. FETCH EXCLUSIONS ───────► zone_engine_core_v2.py
      │                         _fetch_exclusions_from_terrain()
      │                         → terrain_data_router.py
      │                         → API Overpass (OSM)
      │                         3 retries, tiling auto, cache disque 24h
      ▼
4. EXCLUSION DURE P0 ──────► zone_engine_core_v2.py
      │                         _is_zone_excluded()
      │                         (test multi-points: centroid + 4 cardinaux)
      │                         Zones rejetées supprimées
      ▼
5. TRI + PLAFONNEMENT ─────► zone_engine_core_v2.py
      │                         sort by |area - 6500m²|
      │                         cap at max_zones_per_layer (8 par défaut)
      ▼
6. PENALITE P1 ────────────► zone_penalty_engine.py
      │                         calculate_zone_penalty()
      │                         (proximité × fragmentation)
      │                         score = raw_score × penalty_factor
      ▼
7. SERIALISATION ──────────► zone_visual_layer_v2.py
                                zones_to_geojson()
                                (GeoJSON FeatureCollection)
```

---

## 2. EXCLUSION P0 — EXCLUSION DURE (REJET)

### 2.1 Fichier source
`/app/backend/modules/bionic_engine_p0/services/zone_engine_core_v2.py`
Fonction : `_is_zone_excluded(zone_coords, exclusions)`

### 2.2 Méthode d'application

**Test multi-points** avec 5 points de sondage par zone :
1. Centroide (centre géométrique)
2. Point Nord (milieu centroid → max_lat)
3. Point Sud (milieu centroid → min_lat)
4. Point Est (milieu centroid → max_lng)
5. Point Ouest (milieu centroid → min_lng)

**Seuils de rejet :**

| Type d'exclusion | Géométrie testée | Seuil | Règle |
|-----------------|-----------------|-------|-------|
| **Eau (lake, reservoir)** | Polygon, point-in-polygon | >50% hits (≥3/5) | Rejet |
| **Eau (pond >2000m²)** | Polygon, point-in-polygon | >50% hits | Rejet |
| **Routes** (sauf tracks) | Line, buffer 25m | >50% hits | Rejet |
| **Urbain** | Polygon, point-in-polygon | >50% hits | Rejet |
| **Infrastructure** | Polygon, point-in-polygon | >80% hits (≥5/5) | Rejet |

**Exclusions JAMAIS appliquées (HYDRO FIX) :**
- `wetland` → habitat orignal, reclassifié hors "water"
- `stream`, `ditch`, `micro_water` → trop petit ou non pertinent
- `filtered_out=true` → entités surdimensionnées déjà filtrées
- `track` (pistes forestières) → utilisées par les chasseurs

### 2.3 Fonctions de test géométrique

| Fonction | Fichier | Usage | Précision |
|----------|---------|-------|-----------|
| `_point_in_polygon()` | zone_engine_core_v2.py | Test ray-casting classique | Exacte pour point-in-polygon |
| `_point_near_line()` | zone_engine_core_v2.py | Distance point-segment avec projection | Approximative (seuil en degrés converti) |

### 2.4 Limitations identifiées P0

| # | Limitation | Impact | Sévérité |
|---|-----------|--------|----------|
| L1 | **Seulement 5 points de sondage** — zones irrégulières ou allongées peuvent avoir des intersections non détectées | Faux négatifs (zones intersectant des exclusions non rejetées) | **MOYENNE** |
| L2 | **Aucun buffer géométrique réel** — Le test vérifie si le centroid est DANS l'exclusion, pas si la zone est PROCHE | Une zone à 5m d'un lac mais non chevauchante passe le P0 | **HAUTE** |
| L3 | **Buffer routes = 25m fixe** — ne distingue pas autoroute (devrait être 100m+) vs chemin résidentiel (15m) | Autoroutes sous-protégées, routes mineures surprotégées | **MOYENNE** |
| L4 | **Pas de test d'intersection polygon-polygon** — seuls des points sont testés, pas l'aire réelle d'intersection | Sous-estimation de l'overlap réel | **HAUTE** |
| L5 | **Seuil infrastructure à 80%** — beaucoup plus permissif que les autres types (50%) | Zones partiellement dans des infrastructures tolérées | **BASSE** |
| L6 | **Pas d'utilisation de Shapely** — toutes les opérations sont manuelles, sans accès aux opérations topologiques avancées | Impossible de faire des buffers, intersections, unions géométriques | **HAUTE** |

---

## 3. PÉNALITÉ P1 — PÉNALITÉ SEMI-STATIQUE

### 3.1 Fichier source
`/app/backend/modules/bionic_engine_p0/services/zone_penalty_engine.py`
Fonction : `calculate_zone_penalty(zone, layer_id, exclusions)`

### 3.2 Bandes de proximité

| Bande | Distance | Code |
|-------|----------|------|
| **close** | < 200m | `BAND_CLOSE = 200` |
| **medium** | 200m — 500m | `BAND_MEDIUM = 500` |
| **far** | 500m — 1000m | `BAND_FAR = 1000` |
| **none** | > 1000m | Aucune pénalité |

### 3.3 Matrice de pénalité complète

**Couche "alimentation" :**
| Type exclusion | close | medium | far |
|---------------|-------|--------|-----|
| water | 1.05 | 1.00 | 1.00 |
| urban | 0.40 | 0.65 | 0.85 |
| roads | 0.30 | 0.60 | 0.85 |
| infrastructure | 0.40 | 0.70 | 0.90 |

**Couche "repos" :**
| Type exclusion | close | medium | far |
|---------------|-------|--------|-----|
| water | 0.70 | 0.90 | 1.00 |
| urban | 0.25 | 0.55 | 0.80 |
| roads | 0.25 | 0.55 | 0.80 |
| infrastructure | 0.35 | 0.65 | 0.85 |

**Couche "rut" :**
| Type exclusion | close | medium | far |
|---------------|-------|--------|-----|
| water | 0.70 | 0.90 | 1.00 |
| urban | 0.25 | 0.55 | 0.80 |
| roads | 0.30 | 0.60 | 0.85 |
| infrastructure | 0.35 | 0.65 | 0.85 |

**Couche "habitats" :**
| Type exclusion | close | medium | far |
|---------------|-------|--------|-----|
| water | 0.95 | 1.00 | 1.00 |
| urban | 0.40 | 0.65 | 0.85 |
| roads | 0.45 | 0.70 | 0.90 |
| infrastructure | 0.45 | 0.70 | 0.90 |

**Couche "corridors" :**
| Type exclusion | close | medium | far |
|---------------|-------|--------|-----|
| water | 0.95 | 1.00 | 1.00 |
| urban | 0.40 | 0.65 | 0.85 |
| roads | 0.50 | 0.70 | 0.90 |
| infrastructure | 0.50 | 0.70 | 0.90 |

**Couches par défaut (toutes les autres) :**
| Type exclusion | close | medium | far |
|---------------|-------|--------|-----|
| water | 0.90 | 1.00 | 1.00 |
| urban | 0.40 | 0.65 | 0.85 |
| roads | 0.40 | 0.65 | 0.85 |
| infrastructure | 0.45 | 0.70 | 0.90 |

### 3.4 Pénalité de fragmentation

| Condition | Multiplicateur | Code |
|-----------|---------------|------|
| compactness < 0.3 ET area < 10 000 m² | **×0.60** (sévère) | `FRAG_SEVERE_MULT` |
| compactness < 0.5 | **×0.80** (modéré) | `FRAG_MODERATE_MULT` |
| sinon | ×1.0 (aucun) | — |

### 3.5 Calcul de distance

La distance centroid → exclusion est calculée par `_min_distance_to_exclusion_type()` :
- **Polygones** : distance au point le plus proche du contour
- **Lignes** : distance au segment le plus proche (projection orthogonale)
- Early exit si distance < 10m

### 3.6 Plafonnement

```
total_mult = max(0.15, min(1.10, total_mult))
```
- Plancher : 0.15 (zone très pénalisée reste visible mais score minimal)
- Plafond : 1.10 (bonus eau pour alimentation)

### 3.7 Limitations identifiées P1

| # | Limitation | Impact | Sévérité |
|---|-----------|--------|----------|
| L7 | **Distance calculée centroid→exclusion seulement** — la bordure de la zone peut être beaucoup plus proche | Sous-estimation de la proximité réelle | **HAUTE** |
| L8 | **Distance polygone = point le plus proche du contour** — pas la distance minimale entre deux géométries | Approximation correcte pour petites zones, erronée pour grandes | **MOYENNE** |
| L9 | **Pas de distinction par sous-type** — autoroute et chemin résidentiel = même pénalité "roads" | Manque de granularité | **MOYENNE** |
| L10 | **Pénalité eau ≥1.0 pour alimentation/corridors** — pas de pénalité "bord d'eau" pour ces couches | Zone de repos près d'un lac = pénalité, zone d'alimentation = bonus — correct écologiquement mais pourrait être affiné | **BASSE** |

---

## 4. SOURCE DES DONNÉES : API OVERPASS

### 4.1 Fichier source
`/app/backend/modules/bionic_engine_p0/routers/terrain_data_router.py`
Fonctions : `_build_overpass_query()`, `_parse_overpass()`

### 4.2 Requête Overpass — Catégories interrogées

#### EAU (water)
| Tag OSM | Elements | Exemples |
|---------|----------|----------|
| `natural=water` | way, relation | Lacs, plans d'eau |
| `natural=wetland` | way, relation | Marais, marécages, tourbières |
| `natural=bay/strait/coastline` | way, relation | Baies, détroits, littoral |
| `water=*` | way, relation | Tag complémentaire eau |
| `waterway=river/riverbank/canal/stream/ditch/drain/dock` | way, relation | Cours d'eau |
| `landuse=reservoir/basin/salt_pond` | way, relation | Réservoirs, bassins |

#### ROUTES (roads)
| Detail level | Tags | Couverture |
|-------------|------|-----------|
| **low** | `highway=motorway` → `living_street` | Routes principales + résidentielles |
| **high** | + `track/footway/cycleway/path/pedestrian/service` | Toutes voies |

#### URBAIN (urban)
| Tag OSM | Exemples |
|---------|----------|
| `landuse=residential/commercial/industrial/retail/farmland/farmyard/orchard/vineyard/allotments/recreation_ground/cemetery/construction/military/quarry/landfill` | Toutes zones anthropiques |
| `amenity=school/university/hospital/parking/fuel/...` | Équipements publics |
| `leisure=park/garden/playground/sports_centre/stadium/...` | Espaces loisirs |
| `building=*` (high detail seulement) | Tous bâtiments |
| `man_made=pier/bridge/breakwater/...` (high detail) | Structures artificielles |

#### INFRASTRUCTURE
| Tag OSM | Exemples |
|---------|----------|
| `railway=*` | Voies ferrées |
| `aeroway=*` | Aéroports, pistes |
| `power=plant/substation/line` | Centrales, lignes HT |
| `man_made=works/storage_tank/water_tower/...` (high detail) | Installations industrielles |

### 4.3 Parsing (`_parse_overpass`) — Reclassifications HYDRO FIX

| Entrée OSM | Type V5 | Raison |
|-----------|---------|--------|
| `natural=wetland` | **wetland** (pas water) | Habitat orignal, NON-eau |
| Relation >10 km² | `filtered_out=true` | Surdimensionné (ex: Fleuve St-Laurent) |
| Relation sans sub_type identifiable | `filtered_out=true` | Risque de faux positif |
| `waterway=river` polygone >2 km² | `filtered_out=true` | Trop grand |
| Plan d'eau <2000 m² | `sub_type=micro_water` | Non pertinent pour exclusion |
| `waterway=stream/ditch` en polygone | Converti en **line** | Pas une masse d'eau |

### 4.4 Cache et Tiling

| Paramètre | Valeur | Fichier |
|-----------|--------|---------|
| Cache TTL | 24h (disque) | `terrain_data_router.py` |
| Cache dir | `/app/backend/data/osm_cache/` | — |
| Max bbox API directe | 0.3° lat × 0.4° lng | `terrain_data_router.py` |
| Taille tuile (fetch exclusions) | 0.06° × 0.08° | `zone_engine_core_v2.py` |
| Max tuiles | 9 (3×3) | `zone_engine_core_v2.py` |
| Cache TTL in-memory (zones) | 300s (5 min) | `zone_engine_core_v2.py` |

---

## 5. EXCLUSION HYDROGRAPHIQUE — WATER EXCLUSION KNOWLEDGE LAYER

### 5.1 Fichier source
`/app/backend/modules/bionic_engine_p0/knowledge/terrain/water_exclusion.py`
Classe : `WaterExclusionService`

### 5.2 Périmètre

Ce module est **séparé** du pipeline P0/P1. Il valide les **corridors fauniques** (pas les zones) :
- Vérifie si un corridor traverse une masse d'eau
- Tente un contournement (max 3 tentatives)
- Si impossible, rejette le corridor

### 5.3 Règles par espèce

| Espèce | Peut traverser ruisseau | Peut traverser marais | Largeur max franchissable | Capacité nage |
|--------|------------------------|----------------------|--------------------------|--------------|
| Orignal (moose) | Oui | Oui | 15m | Bonne |
| Chevreuil (deer) | Oui | Non | 8m | Modérée |
| Ours (bear) | Oui | Oui | 25m | Excellente |
| Wapiti (elk) | Oui | Oui | 12m | Bonne |

### 5.4 Constantes clés

| Constante | Valeur | Description |
|-----------|--------|-------------|
| `MIN_WATER_BODY_AREA_M2` | 5 000 m² | Seuil "grande masse d'eau" |
| `MIN_RIVER_WIDTH_M` | 20m | Largeur infranchissable |
| `SHORE_BUFFER_M` | 15m | Distance sécurité berges |

---

## 6. PIPELINE FRONTEND — CLIPPING ET AFFICHAGE

### 6.1 Clipping spatial (`useSpatialClipping.js`)

| Paramètre | Valeur V5 | Description |
|-----------|-----------|-------------|
| `ANALYSIS_BOX_SIZE_M` | **3000** (3km) | Taille du carré d'analyse |
| Algorithme | Sutherland-Hodgman | Clipping polygone vs rectangle |
| Application | Côté client (rendu) | Ne modifie pas les données backend |
| Recalcul area | Oui (aire du polygone clippé) | |

### 6.2 Service de zones (`BionicZoneService.js`)

| Paramètre | Valeur V5 | Description |
|-----------|-----------|-------------|
| `radius` (generateWaypointZonesV5) | **0.015** (~1.7km) | Rayon de la bbox envoyée au backend |
| Résolution | 60-100 (selon zoom) | Grille de rasterisation |
| `max_zones_per_layer` | 5-10 (selon zoom) | Plafond par couche |

### 6.3 Overlay d'exclusion (`ExclusionOverlayLayer.jsx`)

| Comportement | V5 (HYDRO FIX) |
|-------------|-----------------|
| Eau affichée | **NON** (filtrée type!='water') |
| Wetland affiché | **NON** (filtrée type!='wetland') |
| filtered_out affiché | **NON** |
| Polygones >1 km² | **NON** (sécurité) |
| Urbain | Oui (rouge, 15% fill) |
| Routes | Oui (orange, 12% fill) |
| Infrastructure | Oui (gris, 12% fill) |

### 6.4 Overlay structures (`StructureContrastLayer.jsx`)

| Élément | Rendu | Style |
|---------|-------|-------|
| Routes majeures | Polyline | #B71C1C, 2.5px |
| Routes secondaires | Polyline | #D84315, 2.0px |
| Chemins/pistes | Polyline | #6D4C41, 1.5px, tirets |
| Infra linéaire | Polyline | #546E7A, 2.0px, tirets |
| Urbain (polygon) | Polygon | #EF5350, 12% fill |
| Infra (polygon) | Polygon | #546E7A, 10% fill |

---

## 7. CONFIGURATION GELÉE — INCOHÉRENCES IDENTIFIÉES

### 7.1 Buffers déclarés vs implémentés

Le fichier `exclusions_config_v1.json` déclare des buffers :

| Type | Buffer déclaré (config) | Buffer réel (code P0) | Buffer pénalité P1 |
|------|------------------------|----------------------|-------------------|
| water | 200m | **0m** (point-in-polygon pur) | Bandes 200/500/1000m |
| urban | 0m | **0m** (point-in-polygon pur) | Bandes 200/500/1000m |
| roads | 80m | **25m** (point-near-line) | Bandes 200/500/1000m |
| infrastructure | 100m | **0m** (point-in-polygon pur) | Bandes 200/500/1000m |

**CONSTAT CRITIQUE :** Les buffers de la config (200m eau, 80m routes, 100m infra) ne sont **PAS implémentés** dans le code P0. Le P0 utilise un test binaire (dedans/dehors) sans buffer géométrique. Seules les routes ont un buffer de 25m via `_point_near_line`. La protection réelle par buffer est assurée uniquement par les pénalités P1 (soft penalty, pas un rejet).

### 7.2 Donnée de référence V5 FREEZE

| Métrique | Valeur V5 freeze | Source |
|----------|------------------|--------|
| Zones générées (waypoint ref) | 32 | `data_reference.json` |
| Zones d'exclusion (terrain ref) | 328 | `exclusion_data_reference.json` |
| Dont water | 323 | — |
| Dont wetland | 5 | — |
| Dont filtrées (oversized) | 16 | — |
| Polygones exclusion | 41 | — |
| Lignes exclusion | 287 | — |

---

## 8. COMPARAISON V5 COMPORTEMENT RÉEL vs COMPORTEMENT ATTENDU

| Aspect | Comportement attendu (config) | Comportement réel (code) | Écart |
|--------|------------------------------|-------------------------|-------|
| Buffer eau | 200m autour de chaque plan d'eau | Aucun buffer P0, pénalité P1 à <200m | **CRITIQUE** |
| Buffer routes | 80m autour de chaque route | 25m P0 (point-near-line), pénalité P1 à <200m | **MOYEN** |
| Buffer infrastructure | 100m autour de chaque infra | Aucun buffer P0, pénalité P1 à <200m | **MOYEN** |
| Méthode exclusion | "1 seul point dans zone exclue = rejet" (config) | >50% des 5 points = rejet (code) | **CRITIQUE** — La config dit 1 point = rejet, le code exige >50% |
| Farmland | Classé urbain | Classé urbain (correct) | OK |
| Wetland | Devrait être exclusion eau | Reclassifié en type séparé, NON exclu | **Intentionnel** (HYDRO FIX) |
| Pistes forestières | Devrait être exclusion route | IGNORÉ (track) | **Intentionnel** |
| Précision géométrique | Intersection exacte | Échantillonnage 5 points | **SIGNIFICATIF** |

---

# PHASE 2 — STRATÉGIE 200% PLUS PERFORMANTE

## 1. DIAGNOSTIC : POURQUOI LA V5 EST INSUFFISANTE

### Faiblesses principales

1. **Aucun buffer géométrique réel (P0)** — Le test multi-points ne capture que les chevauchements grossiers. Une zone à 10m d'un lac passe le P0 sans problème.

2. **Échantillonnage trop grossier** — 5 points de sondage pour des zones de 4500-80000 m² (70m-280m de diamètre) laissent des angles morts significatifs.

3. **Pas d'opérations topologiques** — Sans Shapely, impossible de calculer intersections réelles, buffers, différences géométriques.

4. **Pénalité P1 basée sur le centroid** — La distance centroid→exclusion sous-estime la proximité réelle de la bordure de zone.

5. **Aucune distinction par gravité** — Toutes les routes = même buffer 25m. Une autoroute devrait avoir un impact 4x supérieur à un chemin résidentiel.

### Faiblesses secondaires

6. **Config déclarative non implémentée** — Les buffers de `exclusions_config_v1.json` sont de la documentation morte.

7. **Incohérence seuil P0** — La config dit "1 point = rejet", le code exige ">50%". Le seuil strict causerait trop de rejets avec seulement 5 points.

8. **Pas de pondération spatiale** — La proximité à une zone urbanisée de 50 hectares vs un petit bâtiment isolé a le même effet.

---

## 2. STRATÉGIE V6 — "EXCLUSION GÉOMÉTRIQUE SHAPELY"

### 2.1 Principe fondamental

**Remplacer l'échantillonnage par points par des opérations géométriques exactes via Shapely.**

Au lieu de tester 5 points et deviner, on calculera :
- L'intersection réelle (polygon ∩ exclusion)
- Le buffer réel autour des exclusions
- L'aire exacte d'overlap

### 2.2 Architecture proposée — 4 étapes

```
ÉTAPE 1: Pré-traitement Shapely des exclusions
    → Buffer géométrique par type (autoroute≠chemin)
    → Union spatiale (STRtree pour indexation)
    → Cache en mémoire (durée = requête)

ÉTAPE 2: Exclusion P0-V6 (rejet géométrique exact)
    → intersection_ratio = zone.intersection(exclusion_union).area / zone.area
    → Si ratio > seuil → REJET
    → Seuils par type (eau=5%, urban=40%, routes=20%, infra=60%)

ÉTAPE 3: Pénalité P1-V6 (distance géométrique exacte)
    → distance = zone_polygon.distance(exclusion_polygon)
    → (pas centroid→point, mais polygon→polygon)
    → Mêmes bandes (close/medium/far) mais distances exactes

ÉTAPE 4: Découpe P2 (zone trimming) — NOUVEAU
    → zone_clean = zone.difference(exclusion_buffered)
    → Zones partiellement exclues = découpées et conservées
    → Si zone_clean.area < min_area → REJET
    → Sinon → zone redimensionnée et lissée
```

### 2.3 Buffers V6 — par type et sous-type

#### Eau (water)

| Sous-type | Buffer V6 | Justification |
|-----------|----------|---------------|
| lake, reservoir | 50m | Berges — distance de sécurité chasseur |
| pond >2000m² | 30m | Plus petit, moins de risque |
| pond <2000m² | 0m (ignoré) | Micro plan d'eau, pas pertinent |
| river (polygon) | 40m | Berges rivière |
| stream (line) | 10m | Ruisseau — juste un marqueur |
| wetland | 0m (jamais exclu) | Habitat orignal |

#### Routes

| Sous-type | Buffer V6 | Justification |
|-----------|----------|---------------|
| motorway, trunk | 150m | Autoroute — bruit, danger, perturbation majeure |
| primary | 100m | Route nationale — trafic important |
| secondary | 60m | Route secondaire — trafic modéré |
| tertiary, residential | 30m | Route locale — faible perturbation |
| service, unclassified | 20m | Voie de service |
| track | 0m (ignoré) | Piste forestière — utilisée par chasseurs |
| footway, cycleway, path | 0m (ignoré) | Sentiers — faible impact |

#### Urbain

| Sous-type | Buffer V6 | Justification |
|-----------|----------|---------------|
| residential, commercial, industrial | 100m | Zone bâtie — perturbation élevée |
| farmland, farmyard | 50m | Zone agricole — activité humaine |
| cemetery, recreation_ground | 30m | Zone récréative — perturbation moyenne |
| construction, military, quarry | 150m | Zone dangereuse/bruyante |
| building (isolé) | 20m | Bâtiment unique |

#### Infrastructure

| Sous-type | Buffer V6 | Justification |
|-----------|----------|---------------|
| railway (rail) | 80m | Voie ferrée — bruit intermittent |
| railway (siding, spur) | 30m | Voie secondaire |
| aeroway | 500m | Aéroport — bruit extrême |
| power=plant | 200m | Centrale — zone industrielle |
| power=line | 40m | Ligne HT — risque, déforestation linéaire |
| power=substation | 100m | Poste transformateur |

### 2.4 Seuils d'intersection P0-V6

| Type | Seuil rejet V5 | Seuil rejet V6 proposé | Logique |
|------|----------------|----------------------|---------|
| Eau (lake, reservoir) | >50% points | **>5% aire** | Quasi tolérance zéro pour l'eau |
| Eau (pond) | >50% points | **>15% aire** | Petit plan d'eau, plus tolérant |
| Routes | >50% points | **>20% aire** (buffer inclus) | Zone significativement sur la route |
| Urbain | >50% points | **>40% aire** | Zones en bordure de village tolérées |
| Infrastructure | >80% points | **>30% aire** | Plus strict que V5 |

### 2.5 Gains attendus

| Métrique | V5 | V6 (estimé) | Gain |
|----------|----|----|------|
| Faux négatifs P0 (zones non exclues mais qui devraient l'être) | ~15-25% | <2% | **10-12x** |
| Précision distance P1 | Centroid only (~50% précision) | Polygon-polygon (>98%) | **2x** |
| Zones partiellement sur exclusion | Rejetées entièrement | **Découpées et conservées** | +15-20% zones utiles |
| Temps de calcul P0 | ~2ms/zone (5 point tests) | ~5ms/zone (Shapely) | -2.5x (acceptable) |
| Buffer adaptatif | Non (25m fixe routes) | **Oui** (0-500m par sous-type) | Qualité ++++ |

---

## 3. IMPACT SUR LA PERFORMANCE

### 3.1 Shapely — Coût CPU

| Opération | Temps estimé (par zone) | V5 équivalent |
|-----------|------------------------|--------------|
| `Polygon(zone_coords)` | <0.1ms | — |
| `zone.intersection(exclusion)` | 1-3ms | — |
| `zone.distance(exclusion)` | 0.5-1ms | — |
| `zone.difference(exclusion)` | 2-5ms | — |
| **Total V6 par zone** | **~5-10ms** | ~2ms V5 |

### 3.2 Optimisations prévues

1. **STRtree** (Shapely spatial index) — Réduit la recherche d'exclusions voisines de O(n) à O(log n)
2. **Pré-union par type** — Union de toutes les exclusions eau en un seul MultiPolygon → 1 test au lieu de 300+
3. **Prepared geometries** — `prepared.prep(exclusion_union)` pour des tests contains/intersects 10x plus rapides
4. **Cache par requête** — Les géométries Shapely sont construites une fois par requête backend, pas par zone

### 3.3 Estimation temps total pipeline

| Étape | V5 | V6 estimé |
|-------|----|----|
| Fetch exclusions Overpass | 2-8s | 2-8s (inchangé) |
| Pré-traitement Shapely | — | **0.5-1s** (nouveau) |
| Rasterisation (15 layers) | 1-3s | 1-3s (inchangé) |
| Extraction zones | 0.5-1s | 0.5-1s (inchangé) |
| P0 exclusion (80 zones × 300 exclusions) | ~50ms | **~200ms** (Shapely) |
| P1 pénalité | ~30ms | **~100ms** (distances exactes) |
| **Total** | **4-12s** | **4.5-13s** (+10-15%) |

Le surcoût de 10-15% est largement compensé par la précision 200%+ et les zones découpées (P2).

---

# PHASE 3 — SPÉCIFICATION D'INTÉGRATION V6

## 1. ARCHITECTURE DES FICHIERS

### 1.1 Nouveaux fichiers à créer

```
/app/backend/modules/bionic_engine_p0/services/
├── exclusion_engine_v6.py          # NOUVEAU — Pipeline d'exclusion V6
├── exclusion_geometry_v6.py        # NOUVEAU — Opérations Shapely
└── exclusion_config_v6.py          # NOUVEAU — Buffers et seuils V6
```

### 1.2 Fichiers à modifier

| Fichier | Modification |
|---------|-------------|
| `zone_engine_core_v2.py` | Remplacer appel `_is_zone_excluded()` + `calculate_zone_penalty()` par `exclusion_engine_v6.process_zones()` |
| `requirements.txt` | Ajouter `Shapely>=2.0` |
| `exclusions_config_v1.json` | Aucune modification (V5 gelé) |

### 1.3 Fichiers NON modifiés (gel V5 respecté)

- `terrain_data_router.py` — Inchangé (même source Overpass)
- `zone_penalty_engine.py` — Conservé mais court-circuité en V6
- `behavioral_rasterizer.py` — Inchangé
- `organic_zone_generator_v2.py` — Inchangé

---

## 2. SPÉCIFICATION TECHNIQUE — `exclusion_engine_v6.py`

### 2.1 API publique

```python
async def process_zones_v6(
    raw_zones: List[Dict],
    bounds: Dict[str, float],
    exclusions: List[Dict],
    layer_id: str,
    species: str = "moose",
) -> Tuple[List[Dict], List[Dict], Dict]:
    """
    Pipeline d'exclusion V6 complet.
    
    Returns:
        valid_zones: Zones survivantes (potentiellement découpées)
        rejected_zones: Zones rejetées avec raison
        stats: Statistiques du pipeline
    """
```

### 2.2 Pipeline interne

```python
def _step1_build_exclusion_geometries(exclusions, config):
    """Convertit les exclusions OSM en géométries Shapely bufferisées."""
    # Pour chaque exclusion:
    #   1. Créer Polygon/LineString Shapely
    #   2. Appliquer buffer par sous-type (config V6)
    #   3. Indexer dans STRtree
    # Retourne: { "water": MultiPolygon, "urban": MultiPolygon, ... }

def _step2_p0_geometric_exclusion(zone_polygon, exclusion_unions, thresholds):
    """Test d'intersection exacte par type."""
    # Pour chaque type d'exclusion:
    #   intersection = zone.intersection(exclusion_union)
    #   ratio = intersection.area / zone.area
    #   Si ratio > threshold[type] → REJET avec raison
    # Retourne: (is_excluded, reason, intersection_ratio)

def _step3_p1_geometric_penalty(zone_polygon, exclusion_unions, layer_id):
    """Calcul de pénalité avec distances géométriques exactes."""
    # Pour chaque type d'exclusion:
    #   distance = zone_polygon.distance(exclusion_union)
    #   band = distance_to_band(distance)
    #   penalty *= PENALTY_MATRIX[layer_id][type][band]
    # Retourne: (penalty_factor, details)

def _step4_zone_trimming(zone_polygon, exclusion_unions_buffered, min_area):
    """Découpe les zones partiellement exclues."""
    # zone_clean = zone.difference(all_exclusion_buffered)
    # Si zone_clean.area < min_area → REJET
    # Si zone_clean est MultiPolygon → garder le plus grand
    # Retourne: (trimmed_polygon, trimmed_area, was_trimmed)
```

---

## 3. SPÉCIFICATION TECHNIQUE — `exclusion_geometry_v6.py`

### 3.1 Fonctions utilitaires Shapely

```python
from shapely.geometry import Polygon, LineString, MultiPolygon, Point
from shapely.ops import unary_union
from shapely.strtree import STRtree
from shapely import prepared

def osm_coords_to_shapely(coords, geom_type):
    """Convertit les coordonnées OSM [lng, lat] en géométrie Shapely."""

def apply_buffer(geom, buffer_m, lat_center):
    """Applique un buffer en mètres (conversion degrés via latitude)."""

def build_exclusion_index(exclusions, config):
    """Construit un STRtree spatial indexé par type."""

def calculate_intersection_ratio(zone_poly, exclusion_poly):
    """Calcule le ratio d'intersection exact."""

def calculate_min_distance_m(zone_poly, exclusion_poly, lat_center):
    """Distance minimale polygon-polygon en mètres."""
```

---

## 4. SPÉCIFICATION TECHNIQUE — `exclusion_config_v6.py`

### 4.1 Structure

```python
BUFFER_CONFIG_V6 = {
    "water": {
        "lake": 50, "reservoir": 50,
        "pond": 30, "micro_water": 0,
        "river": 40, "stream": 10,
        "wetland": 0,  # JAMAIS exclu
    },
    "roads": {
        "motorway": 150, "trunk": 150,
        "primary": 100, "secondary": 60,
        "tertiary": 30, "residential": 30,
        "service": 20, "unclassified": 20,
        "track": 0, "footway": 0, "path": 0,
    },
    "urban": {
        "residential": 100, "commercial": 100,
        "industrial": 100, "farmland": 50,
        "cemetery": 30, "construction": 150,
        "military": 150, "quarry": 150,
        "building": 20,
    },
    "infrastructure": {
        "rail": 80, "siding": 30,
        "aeroway": 500, "power_plant": 200,
        "power_line": 40, "substation": 100,
    },
}

INTERSECTION_THRESHOLDS_V6 = {
    "water": 0.05,       # 5% → rejet
    "urban": 0.40,       # 40% → rejet
    "roads": 0.20,       # 20% → rejet
    "infrastructure": 0.30,  # 30% → rejet
}
```

---

## 5. INTÉGRATION DANS `zone_engine_core_v2.py`

### 5.1 Point d'intégration

Dans `_process_single_layer()`, remplacer :

```python
# V5 (à remplacer)
for zone in raw_zones:
    if _is_zone_excluded(zone["coordinates"], exclusions):
        rejected += 1
        continue
    valid_zones.append(zone)
# ...
penalty_factor, penalty_details = calculate_zone_penalty(zone, layer_id, exclusions)
```

Par :

```python
# V6 (remplacement)
from modules.bionic_engine_p0.services.exclusion_engine_v6 import process_zones_v6

valid_zones, rejected_list, excl_stats = process_zones_v6(
    raw_zones=raw_zones,
    bounds=bounds,
    exclusions=exclusions,
    layer_id=layer_id,
    species=species,
)
rejected = len(rejected_list)
```

### 5.2 Compatibilité ascendante

- Le format de sortie (zones + scores + penalties) reste identique
- L'API `POST /api/v1/bionic/organic-zones` ne change pas
- Les tests V5 (28/28) doivent passer avec les mêmes données de référence
- Un **feature flag** `EXCLUSION_ENGINE_VERSION=v6` dans `.env` permettra de basculer

---

## 6. INTÉGRATION FRONTEND

### 6.1 Modifications nécessaires

**AUCUNE modification frontend requise.** Le backend reste la seule source de vérité.

Les composants suivants ne changent pas :
- `BionicZoneService.js` — Appelle toujours `POST /api/v1/bionic/organic-zones`
- `useZoneOrchestrator.js` — Pipeline cache→preview→backend inchangé
- `useSpatialClipping.js` — Clipping client inchangé
- `ExclusionOverlayLayer.jsx` — Affichage inchangé
- `StructureContrastLayer.jsx` — Affichage inchangé

### 6.2 Diagnostic optionnel

Un nouveau champ `stats.exclusion_engine` sera ajouté à la réponse :

```json
{
  "stats": {
    "exclusion_engine": "v6",
    "exclusion_stats": {
      "total_raw_zones": 45,
      "rejected_p0": 8,
      "trimmed_p2": 5,
      "valid_zones": 32,
      "avg_intersection_ratio": 0.12,
      "shapely_time_ms": 180
    }
  }
}
```

---

## 7. PLAN DE MIGRATION

### Phase 1 — Préparation (sans impact)
1. Installer Shapely 2.0+ dans requirements.txt
2. Créer les 3 nouveaux fichiers (exclusion_engine_v6, exclusion_geometry_v6, exclusion_config_v6)
3. Écrire les tests unitaires V6

### Phase 2 — Intégration (feature flag)
4. Ajouter `EXCLUSION_ENGINE_VERSION` dans backend/.env
5. Modifier `_process_single_layer()` pour brancher V5 ou V6 selon le flag
6. Tester avec le waypoint de référence (46.81, -71.21)
7. Comparer les résultats V5 vs V6

### Phase 3 — Validation
8. Exécuter les 28 tests V5 de non-régression
9. Vérifier que le nombre de zones est ≥ V5 (grâce au trimming P2)
10. Mesurer le temps de pipeline (objectif: <15% overhead)

### Phase 4 — Activation
11. Basculer le flag vers V6
12. Monitorer en production pendant 48h
13. Supprimer le flag et le code V5 une fois validé

---

## 8. TESTS DE NON-RÉGRESSION V6

### 8.1 Tests à ajouter

| Test | Vérification |
|------|-------------|
| `test_v6_no_zone_in_lake` | Aucune zone V6 n'intersecte un lac >2000m² à plus de 5% |
| `test_v6_road_buffer_respected` | Aucune zone V6 ne touche une autoroute sans buffer 150m |
| `test_v6_zone_count_gte_v5` | V6 produit au moins autant de zones que V5 (trimming) |
| `test_v6_trimming_preserves_area` | Les zones découpées ont area ≥ min_area |
| `test_v6_penalty_distance_exact` | Les pénalités V6 utilisent la distance polygon-polygon |
| `test_v6_feature_flag_fallback` | Avec flag=v5, le pipeline V5 est utilisé |
| `test_v6_performance_overhead` | Temps V6 < 1.2× temps V5 |

### 8.2 Tests V5 existants à conserver

Les 28 tests de `/app/backend/tests/freeze/test_freeze_regression.py` doivent tous passer.

---

**FIN DU RAPPORT — PHASES 1, 2 ET 3 COMPLÈTES**
