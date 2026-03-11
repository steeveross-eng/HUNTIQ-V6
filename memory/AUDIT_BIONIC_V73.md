# AUDIT TOTAL BIONIC™ V7.3
## Architecture Complète | Arbre des Fonctions | Pipelines | Paramètres | Tests
### Rapport Exhaustif — 10 mars 2026

---

# A. ARCHITECTURE GLOBALE — ARBRE COMPLET

## A.1 — Schéma d'Architecture

```
FRONTEND (React + Leaflet)                    BACKEND (FastAPI + MongoDB)
═══════════════════════════                    ═══════════════════════════
                                               
MonTerritoireBionicPage.jsx ─────────────────► /api/v1/bionic/organic-zones
  ├── useZoneOrchestrator.js                     └── organic_zones_router.py
  │     ├── BionicZoneService.js                       └── zone_engine_core_v2.py
  │     │     └── generateWaypointZonesV5()                 ├── behavioral_rasterizer.py    [MODULE A]
  │     └── useZoneCache.js (idb-keyval)                    ├── organic_zone_generator_v2.py [MODULE B]
  │                                                         ├── zone_visual_layer_v2.py
  ├── BionicMicroZones.jsx (rendu polygones)                ├── zone_penalty_engine.py       [MODULE P1]
  ├── MovementCorridorsLayer.jsx                            └── (V7) pipeline_v7.py
  ├── CorridorStatsPanel.jsx                                     ├── exclusion_engine_v6.py
  ├── AnalysisSidePanel.jsx                                      ├── exclusion_geometry_v6.py
  ├── PlacesSidePanel.jsx                                        ├── exclusion_config_v6.py
  ├── TerritoryShell.jsx (bounds viz)                            ├── zone_typology_v7.py
  ├── ExclusionOverlayLayer.jsx                                  ├── zone_shape_v7.py
  ├── HydrographyOverlayLayer.jsx                                ├── terrain_signals_v7.py
  ├── WindFlowLayer.jsx                                          ├── species_behavior_v7.py
  └── EcoforestryLayers.jsx                                      ├── corridor_v7.py
                                                                  ├── trail_cost_grid_v7.py
  useSpatialClipping.js ─────────── Clipping client 3000m         └── srtm_provider_v7.py
                                               
  useZoneOrchestrator.js ────────► /api/v1/bionic/terrain/terrain-data
                                     └── terrain_data_router.py
                                           ├── Overpass API (3 miroirs)
                                           ├── MongoDB cache R5 (TTL 1h)
                                           └── Disk cache fallback
```

## A.2 — Arbre des Dépendances (Ordre d'Appel)

```
REQUÊTE UTILISATEUR (clic waypoint)
│
├─► [FRONTEND] useZoneOrchestrator.js
│     │ Paramètres: waypoint(lat,lng), zoom, layers[], species
│     │
│     ├─► [ÉTAPE 1] useZonePreview.js → preview rapide (client-side)
│     ├─► [ÉTAPE 2] useZoneCache.js → vérif cache IndexedDB
│     └─► [ÉTAPE 3] BionicZoneService.generateWaypointZonesV5()
│           │ POST /api/v1/bionic/organic-zones
│           │ Body: { bounds, species, layers, resolution, waypoint_center }
│           │
│           └─► [BACKEND] organic_zones_router.py
│                 └─► zone_engine_core_v2.generate_organic_zones()
│                       │
│                       ├─► [1] _fetch_exclusions_from_terrain()
│                       │     └─► terrain_data_router.py
│                       │           ├─► _load_cache() → MongoDB overpass_cache_r5
│                       │           ├─► Overpass API (retry 3x, 3 miroirs)
│                       │           ├─► _load_cache_expired() (fallback dernier recours)
│                       │           ├─► _parse_overpass() → exclusion_zones[]
│                       │           └─► _save_cache() → MongoDB + disque
│                       │
│                       ├─► [2] _process_all_layers_parallel() [ThreadPoolExecutor x6]
│                       │     └─► Pour chaque layer:
│                       │           ├─► behavioral_rasterizer.generate_layer_raster()
│                       │           ├─► organic_zone_generator_v2.extract_organic_zones()
│                       │           │     ├─► extract_contours() [Marching Squares]
│                       │           │     ├─► chaikin_smooth() [4 itérations]
│                       │           │     └─► vertex_jitter()
│                       │           ├─► [V5] _is_zone_excluded() → exclusion basique
│                       │           │   [V7] pipeline_v7.process_zones_v7()
│                       │           │         ├─► exclusion_engine_v6.process_zones_v6()
│                       │           │         │     ├─► exclusion_geometry_v6 (Shapely STRtree)
│                       │           │         │     ├─► Intersection ratio vs seuils
│                       │           │         │     └─► Pression anthropique (penalties)
│                       │           │         ├─► zone_shape_v7 (lissage adaptatif, snapping)
│                       │           │         ├─► zone_typology_v7 (classification + scoring)
│                       │           │         │     └─► species_behavior_v7 (matrices)
│                       │           │         └─► _merge_nearby_same_type_zones() (<200m)
│                       │           └─► zone_penalty_engine.calculate_zone_penalty()
│                       │
│                       ├─► [3] generate_all_corridors_v7()
│                       │     ├─► _filter_zones_by_perimeter() (1500m)
│                       │     ├─► trail_cost_grid_v7.build_cost_grid() [male + female]
│                       │     ├─► _find_complementary_pairs() → paires feed/rest/rut
│                       │     ├─► _astar() [A* 8-connectivity, max 8000 itérations]
│                       │     ├─► _chaikin_smooth() [3 itérations]
│                       │     ├─► _score_trail() [5 sous-scores pondérés]
│                       │     └─► _assess_confidence() [9 facteurs, seuil 0.60]
│                       │
│                       └─► [4] zones_to_geojson() → FeatureCollection
│
└─► [FRONTEND] Rendu
      ├─► setZonesData() / setZeroZonesReason()
      ├─► useSpatialClipping.js → clipping 3000m bbox
      ├─► BionicMicroZones.jsx → Polygon Leaflet
      ├─► MovementCorridorsLayer.jsx → Polyline Leaflet
      └─► CorridorStatsPanel.jsx → statistiques
```

## A.3 — Carte des Flux Complète

```
WAYPOINT → EXCLUSIONS → RASTERISATION → CONTOUR → EXCLUSION V6 → LISSAGE →
CLASSIFICATION → SCORING → FUSION → ZONES FINALES → CORRIDORS A* → RENDU MAP
```

---

# B. EXCLUSIONS / OVERPASS / INFRASTRUCTURES

## B.1 — Sources et Configuration

| Paramètre | Valeur |
|---|---|
| **Service** | Overpass API (OpenStreetMap) |
| **Endpoints** | `overpass-api.de`, `overpass.kumi.systems`, `maps.mail.ru/osm` |
| **Format** | JSON (Overpass QL) |
| **Timeout** | 30s (httpx AsyncClient) |
| **Retry** | 3 tentatives, backoff exponentiel (2s, 4s, 8s) |
| **Cache MongoDB** | Collection `overpass_cache_r5`, TTL 3600s (1h) |
| **Cache disque** | `/app/backend/data/osm_cache/*.json`, TTL 3600s |
| **Mode strict** | Oui (V7.2) — échec Overpass = 0 zones |
| **Fallback cache expiré** | Oui (V7.3) — cache MongoDB/disque même expiré |

## B.2 — Types d'Exclusion Requêtés

| Type | Tags OSM Requêtés | Classifié comme |
|---|---|---|
| **water** | `natural=water`, `waterway=*` | `water` |
| **urban** | `landuse=residential\|commercial\|industrial\|retail\|recreation_ground\|cemetery\|construction\|military\|quarry\|landfill` | `urban` |
| **roads** | `highway=motorway\|trunk\|primary\|secondary\|tertiary\|residential\|unclassified\|track` | `roads` |
| **infrastructure** | `power=line\|tower`, `railway=rail\|station`, `aeroway=*` | `infrastructure` |

### Tags V7.3 RETIRÉS des exclusions urbaines (cause bug P0) :
- ~~`farmland`~~, ~~`farmyard`~~, ~~`orchard`~~, ~~`vineyard`~~, ~~`allotments`~~
- **Raison** : Ces tags agricoles couvraient de vastes surfaces en milieu rural, provoquant l'exclusion de 100% des zones.

## B.3 — Buffers d'Exclusion (exclusion_config_v6.py)

### Water
| Sub-type | Buffer (m) |
|---|---|
| lake | 20 |
| reservoir | 20 |
| pond | 15 |
| river | 15 |
| stream | 8 |
| wetland | 5 |
| _default | 10 |

### Urban (V7.3 — sans tags agricoles)
| Sub-type | Buffer (m) |
|---|---|
| residential | 100 |
| commercial | 100 |
| industrial | 100 |
| retail | 80 |
| recreation_ground | 30 |
| cemetery | 30 |
| construction | 150 |
| military | 150 |
| quarry | 150 |
| landfill | 150 |
| building | 20 |
| _default | 50 |

### Roads
| Sub-type | Buffer (m) |
|---|---|
| motorway | 80 |
| trunk | 60 |
| primary | 50 |
| secondary | 40 |
| tertiary | 30 |
| residential | 30 |
| unclassified | 20 |
| track | 10 |
| _default | 25 |

### Infrastructure
| Sub-type | Buffer (m) |
|---|---|
| power_line | 30 |
| power_tower | 15 |
| railway | 40 |
| station | 60 |
| aeroway | 100 |
| _default | 25 |

## B.4 — Seuils d'Intersection (INTERSECTION_THRESHOLDS_V6)

| Type | Seuil V7.3 | Ancien (V7.2) | Signification |
|---|---|---|---|
| water | 0.05 | 0.05 | 5% de la zone couverte par eau = rejet |
| urban | 0.08 | 0.08 | 8% de la zone couverte par urbain = rejet |
| roads | **0.15** | 0.08 | 15% de la zone couverte par routes = rejet |
| infrastructure | **0.18** | 0.12 | 18% de la zone couverte par infra = rejet |

## B.5 — Critères de Rejet Anthropique (exclusion_engine_v6.py)

| Critère | Condition V7.3 | Ancien (V7.2) | Raison rejet |
|---|---|---|---|
| Urban + Roads combo | `urban_pen < 0.50 AND roads_pen < 0.55` | `< 0.60 AND < 0.65` | `anthropic_urban_roads` |
| Major road seul | `roads_pen < 0.35` | `< 0.45` | `anthropic_major_road` |
| Infra + Roads combo | `infra_pen < 0.45 AND roads_pen < 0.55` | `< 0.55 AND < 0.65` | `anthropic_infra_roads` |
| Urban seul | `urban_pen < 0.35` | `< 0.45` | `anthropic_urban_close` |
| Combined (produit) | `u × r × i < 0.15` | `< 0.20` | `anthropic_combined` |

## B.6 — Erreurs Possibles et Comportements

| Erreur | Code | Comportement V7.3 |
|---|---|---|
| Rate limit Overpass | 429 | Retry 3x + rotation miroirs + fallback cache expiré |
| Timeout Overpass | Timeout | Retry 3x + fallback cache expiré |
| Cache MongoDB down | Exception | Fallback disque |
| Tous retries échouent + pas de cache | - | `exclusion_failed: true`, 0 zones, toast frontend |

---

# C. PIPELINE ZONES V5 / V7

## C.1 — Étapes Détaillées

### Étape 1 : Rasterisation Comportementale (behavioral_rasterizer.py)

Génère un raster 2D numpy par couche avec bruit simplex.

**Paramètres par couche (LAYER_PARAMS) :**

| Couche | Octaves | Base Freq | Threshold | Cluster |
|---|---|---|---|---|
| rut | 5 | 0.0012 | 0.52 | 0.65 |
| repos | 4 | 0.0008 | 0.55 | 0.70 |
| alimentation | 5 | 0.0015 | 0.48 | 0.55 |
| corridors | 5 | 0.0018 | 0.40 | 0.45 |
| habitats | 4 | 0.0010 | 0.50 | 0.65 |
| salines | 5 | 0.0025 | 0.55 | 0.35 |
| affuts | 5 | 0.0016 | 0.55 | 0.45 |
| trajets | 5 | 0.0018 | 0.45 | 0.45 |

**Pondérations espèce (SPECIES_WEIGHTS) :**

| Couche | Orignal | Cerf | Ours | Dindon | Wapiti |
|---|---|---|---|---|---|
| rut | 0.95 | 0.90 | 0.40 | 0.75 | 0.90 |
| repos | 0.80 | 0.85 | 0.85 | 0.70 | 0.80 |
| alimentation | 0.85 | 0.90 | 0.95 | 0.90 | 0.85 |
| corridors | 0.90 | 0.85 | 0.80 | 0.60 | 0.90 |
| habitats | 0.95 | 0.90 | 0.90 | 0.85 | 0.85 |

### Étape 2 : Extraction de Contours (organic_zone_generator_v2.py)

| Paramètre | Valeur | Description |
|---|---|---|
| MIN_AREA_M2 | 8 000 | Surface minimale d'une zone (m²) |
| MAX_AREA_M2 | 80 000 | Surface maximale (m²) |
| TARGET_AREA_M2 | 25 000 | Surface cible (m²) |
| MAX_COMPACTNESS | 0.85 | Compacité max (force irrégularité) |
| MIN_COMPACTNESS | 0.10 | Compacité min |
| MIN_VERTICES | 8 | Nombre min de sommets |
| Chaikin iterations | 4 | Lissage Chaikin |
| Upsample factor | 2x | Bilinéaire avant Marching Squares |

### Étape 3 : Exclusion V6 (exclusion_engine_v6.py)

Pipeline en 3 phases :
1. **P0** — Exclusion dure par intersection géométrique (Shapely STRtree)
2. **P1** — Trimming des bordures qui débordent sur les exclusions
3. **P2** — Rejet par pression anthropique combinée (voir B.5)

### Étape 4 : Lissage V7 (zone_shape_v7.py)

- Chaikin adaptatif (4 itérations × rugosité terrain)
- Snapping berges (30m de tolérance)
- Validation topologique (surface > 100m², compacité > 0.05)

### Étape 5 : Classification V7 (zone_typology_v7.py)

**Types de zones :** `feed`, `rest`, `rut`, `heat_ref`, `hunt_ref`, `corridor`, `mixed`

**Sous-scores (7) :**

| Sous-score | Poids | Description |
|---|---|---|
| food | 0.25 | Ressources alimentaires |
| safety | 0.20 | Sécurité (couvert, éloignement humain) |
| access | 0.15 | Accessibilité terrain |
| stealth | 0.15 | Discrétion (couvert, visibilité réduite) |
| water | 0.10 | Proximité eau |
| topo | 0.10 | Topographie favorable |
| dynamic | 0.05 | Facteurs dynamiques (météo, saison) |

### Étape 6 : Fusion V7.2 (pipeline_v7.py)

- Zones du même `layer_id` à < 200m (centroïde à centroïde) → fusionnées
- Union-Find (Kruskal) pour identifier les clusters
- `shapely.unary_union` pour fusionner les polygones
- Si MultiPolygon → garde le plus grand

## C.2 — Paramètres Pipeline Complets

| Paramètre | Fichier | Valeur |
|---|---|---|
| EXCLUSION_ENGINE_VERSION | .env | `v7` |
| CACHE_TTL zone | zone_engine_core_v2.py | 900s (15min) |
| CACHE_TTL overpass | terrain_data_router.py | 3600s (1h) |
| Thread pool workers | zone_engine_core_v2.py | 6 |
| Grid resolution | organic_zones_router.py | 60 (default) |
| Max zones per layer | organic_zones_router.py | 8 (default) |
| Analysis bbox frontend | useSpatialClipping.js | 3000m |
| Perimeter filter corridors | pipeline_v7.py | 1500m |
| Merge distance | pipeline_v7.py | 200m |
| Hotspot threshold | pipeline_v7.py | 68.0 |

---

# D. CORRIDORS V7

## D.1 — Génération (corridor_v7.py)

### Architecture

1. **Grille de coûts** : Rasterisation des exclusions OSM en grille 60×60
2. **A* pathfinding** : 8-connectivity, max 8000 itérations
3. **Lissage** : Chaikin 3 itérations post-simplification
4. **Scoring** : 5 sous-scores pondérés
5. **Confiance** : 9 facteurs écologiques, seuil `real` ≥ 0.60

### Paires Complémentaires

| Paire | Type |
|---|---|
| rest ↔ feed | Repos → Alimentation |
| rest ↔ rut | Repos → Reproduction |
| rest ↔ heat_ref | Repos → Refuge chaleur |
| rest ↔ hunt_ref | Repos → Refuge pression |
| feed ↔ heat_ref | Alimentation → Refuge |
| feed ↔ corridor | Alimentation → Transition |
| rest ↔ corridor | Repos → Transition |
| rut ↔ feed | Reproduction → Alimentation |
| hunt_ref ↔ feed | Refuge → Alimentation |

### Coûts de Grille (trail_cost_grid_v7.py)

| Type terrain | Coût | Description |
|---|---|---|
| Plans d'eau, urbain dense | **999** (IMPASSABLE) | Infranchissable |
| Très favorable | 0.2-0.5 | Lisières, vallées, ruisseaux |
| Favorable | 0.5-1.0 | Forêt modérée, pentes douces |
| Défavorable | 1.0-5.0 | Pentes raides, proximité routes |
| Quasi-impassable | 10+ | Infrastructure lourde |

### Scoring Trail (5 sous-scores)

| Sous-score | Poids | Description |
|---|---|---|
| Topographie | 0.25 | Coût moyen A* |
| Couvert | 0.20 | Proxy forêt |
| Eau | 0.15 | Proximité plans d'eau |
| Pression | 0.25 | Distance routes/urbain |
| Comportement | 0.15 | Cohérence distance/sexe |

## D.2 — Styles Visuels

| Style | Couleur | Largeur | Opacité | Trait | Label |
|---|---|---|---|---|---|
| male_real | #1565C0 | 3.0 | 0.85 | Continu | Trajet mâle (terrain) |
| male_ai | #42A5F5 | 2.5 | 0.65 | 12 6 | Trajet mâle (estimé IA) |
| female_real | #C62828 | 2.5 | 0.80 | Continu | Trajet femelle (terrain) |
| female_ai | #EF5350 | 2.0 | 0.60 | 8 4 | Trajet femelle (estimé IA) |
| mixed_real | #F57F17 | 2.0 | 0.70 | Continu | Trajet mixte (terrain) |
| mixed_ai | #FFB74D | 1.5 | 0.55 | 10 5 | Trajet mixte (estimé IA) |

## D.3 — Confiance (9 Facteurs)

| # | Facteur | Bonus max |
|---|---|---|
| 1 | Qualité chemin A* (longueur) | +0.17 |
| 2 | Coût écologique (bas = corridors naturels) | +0.12 |
| 3 | Absence coût extrême | +0.06 |
| 4 | Couvert forestier | +0.06 |
| 5 | Présence ruisseaux/eau | +0.04 |
| 6 | Faible perturbation humaine | +0.05 |
| 7 | Distance cohérente | +0.04 |
| 8 | DEM SRTM disponible | +0.06 |
| 9 | Lisières + corridors eau dans grille | +0.06 |

**Base** : 0.40 | **Seuil real** : ≥ 0.60 | **Min** : 0.15 | **Max** : 0.95

## D.4 — INCOHÉRENCES DÉTECTÉES (Corridors)

| # | Incohérence | Sévérité | Fichier | Description |
|---|---|---|---|---|
| C1 | **Corridors non ancrés au waypoint** | HAUTE | corridor_v7.py | Les corridors connectent zone↔zone mais pas waypoint↔zone. L'ancrage au waypoint n'est pas implémenté. |
| C2 | **Pas de vérification intersection routes** | HAUTE | corridor_v7.py | Le A* utilise la grille de coûts qui rend les routes `IMPASSABLE`, MAIS le fallback direct (`_direct_path_latlon`) ne vérifie pas géométriquement si le trajet traverse une route — il "pousse" seulement les points. |
| C3 | **Orientation vent dominant non implémentée** | MOYENNE | corridor_v7.py | Aucune logique ne prend en compte la direction du vent dominant pour orienter les déplacements. |
| C4 | **Max corridors hardcodé à 20** | BASSE | pipeline_v7.py L.336 | La valeur est fixe, pas configurable par espèce ou densité de zones. |

---

# E. DIAGNOSTIC V3 (zone_typology_v7.py)

## E.1 — Critères de Classification

La classification utilise le `layer_id` comme signal principal, modifié par les signaux terrain :

| Layer ID | Type primaire | Conditions alternatives |
|---|---|---|
| alimentation | feed | — |
| repos | rest | — |
| rut | rut | → heat_ref si forêt dense + nord |
| habitats | Dépend terrain | feed si edge, rest si forêt dense, hunt_ref si isolé |
| corridors | corridor | — |

## E.2 — Pondérations Comportementales (species_behavior_v7.py)

### Orignal — Besoins par type

| Facteur | feed | rest | rut | heat_ref | hunt_ref |
|---|---|---|---|---|---|
| mixed_cover | 1.4 | — | — | — | — |
| canopy_dense | — | 1.4 | — | 1.5 | 1.5 |
| water_proximity | 1.2 | 0.9 | 1.3 | 1.5 | 0.9 |
| road_distance | 0.8 | 1.3 | 1.0 | 1.0 | 1.6 |
| edge_proximity | 1.3 | — | 1.2 | — | — |
| regeneration | 1.5 | — | — | — | — |
| wetland_positive | 1.3 | — | 1.5 | — | — |

### Paramètres par Sexe (SEX_PARAMS)

| Param | Orignal ♂ | Orignal ♀ | Cerf ♂ | Cerf ♀ | Ours ♂ |
|---|---|---|---|---|---|
| daily_range_km | 4.0 | 2.5 | 2.5 | 1.5 | 8.0 |
| road_tolerance | 0.6 | 0.3 | 0.7 | 0.4 | 0.5 |
| cover_preference | 0.6 | 0.8 | 0.5 | 0.8 | 0.7 |
| min_road_distance_m | 150 | 250 | 120 | 200 | 200 |
| water_affinity | 0.7 | 0.8 | 0.5 | 0.6 | 0.9 |

---

# F. FRONTEND / UX / ÉTATS

## F.1 — Machine d'États

```
[NONE] ──► waypoint sélectionné ──► [LOADING]
                                        │
                                        ├─► cache hit ──► [CACHE]
                                        │
                                        ├─► preview généré ──► [PREVIEW]
                                        │
                                        ├─► backend OK, zones > 0 ──► [BACKEND] ✅
                                        │
                                        ├─► backend OK, zones = 0 ──► [BACKEND_EMPTY]
                                        │     └─► toast "Aucune zone" + zeroZonesReason
                                        │
                                        └─► backend erreur ──► [ERROR]
                                              └─► toast "Erreur de calcul"
```

### États (zoneSource)
- `none` — Pas de waypoint
- `preview` — Preview client-side (non validé)
- `cache` — Données en cache IndexedDB
- `backend` — Source de vérité (validé)

### zeroZonesReason (V7.3)
- `null` — Zones présentes
- `overpass_unavailable` — Overpass API échoué
- `all_filtered_by_exclusions` — Toutes zones rejetées
- `no_candidates_generated` — Pas de candidats
- `backend_error` — Erreur serveur

## F.2 — Composants Principaux

| Composant | Fichier | Rôle | Lignes |
|---|---|---|---|
| MonTerritoireBionicPage | pages/ | Page principale, orchestration | ~1700 |
| BionicMicroZones | territoire/ | Rendu polygones Leaflet | ~450 |
| MovementCorridorsLayer | territoire/ | Rendu corridors polylines | ~200 |
| CorridorStatsPanel | territoire/ | Stats corridors | ~150 |
| TerritoryShell | territoire/ | Bounds visualization | ~100 |
| BionicAntiDoublesGuard | territoire/ | Gestion clics zones | ~118 |
| AnalysisSidePanel | territoire/ | Panneau analyse (sidebar) | ~200 |
| PlacesSidePanel | territoire/ | Panneau lieux (sidebar) | ~150 |
| WaypointUnifiedPanel | territoire/ | Gestion waypoints | ~400 |

## F.3 — Paramètres de Rendu (BionicMicroZones.jsx V7.3)

| Paramètre | Valeur V7.3 | Ancien | Description |
|---|---|---|---|
| fillOpacity | **0.18** | 0.08 | Opacité remplissage |
| fillOpacity hover | **0.25** | 0.15 | Opacité au survol |
| Base weight | **2.5px** | 1.5px | Épaisseur trait (score=30%) |
| Max weight | **6.0px** | 5.5px | Épaisseur trait (score=100%) |
| Hover weight | **7px** | 6px | Épaisseur au survol |
| Min score filter | 30% | 30% | Score min pour affichage |

## F.4 — INCOHÉRENCES DÉTECTÉES (Frontend)

| # | Incohérence | Sévérité | Description |
|---|---|---|---|
| F1 | **MonTerritoireBionicPage.jsx trop volumineux** | HAUTE | ~1700 lignes. Décomposition Phases 3-4 en pause. |
| F2 | **useSpatialClipping ANALYSIS_BOX_SIZE_M = 3000m** | MOYENNE | Le backend génère dans un bounds de ~0.015° (~1670m radius). Le clipping frontend est de 3000m (1500m radius). Cohérent mais la marge est large. |
| F3 | **useZonePreview.js génère des zones client-side** | INFO | Ces zones ne sont pas validées par les exclusions. Le V7.1 fix empêche leur persistance après verdict backend. |

---

# G. TESTS ANTI-RÉGRESSION

## G.1 — Tests Existants (Critiques pour BIONIC)

| Fichier | Tests | Description | Statut |
|---|---|---|---|
| `test_rural_zone_generation.py` | 7 | V7.3: Rural (Beauce), Forêt (Laurentides), Urban regression | ✅ PASS |
| `test_urban_exclusion_guard.py` | 5 | V7.1: Québec centre-ville 0 zones, exclusions > 50 | ✅ PASS |
| `test_urban_exclusion_v7.py` | - | V7: Exclusion urbaine V7 | ✅ |
| `test_corridor_filtering_v7.py` | - | V7: Filtrage corridors périmètre | ✅ |
| `test_corridors_v7.py` | - | V7: Génération corridors | ✅ |
| `test_overpass_cache_r5.py` | - | R5: Cache MongoDB Overpass | ✅ |
| `test_permanent_water_exclusion.py` | - | Exclusion eau permanente | ✅ |
| `test_water_exclusion_bionic_v5.py` | - | Exclusion eau V5 (hydro fix) | ✅ |

### Total : 134 fichiers de test dans `/app/backend/tests/`

## G.2 — Tests MANQUANTS (À Créer)

| # | Test manquant | Priorité | Description |
|---|---|---|---|
| T1 | **Ancrage corridors au waypoint** | HAUTE | Vérifier que les corridors incluent un segment vers le waypoint |
| T2 | **Corridors ne traversent pas routes** | HAUTE | Vérifier géométriquement qu'aucun corridor `real` ne croise une route |
| T3 | **Orientation vent dominant** | MOYENNE | Quand implémenté |
| T4 | **Cohérence count backend = count frontend** | HAUTE | Le nombre de zones annoncé dans `stats.total_zones` doit correspondre au nombre de features GeoJSON |
| T5 | **Fallback cache expiré** | MOYENNE | Simuler échec total Overpass et vérifier que le cache expiré est utilisé |
| T6 | **Fusion zones < 200m** | MOYENNE | Vérifier que 2 zones du même type à < 200m sont fusionnées |
| T7 | **Frontend crash test (ResizeObserver)** | BASSE | Déjà couvert par testing agent |

---

# H. INCOHÉRENCES DÉTECTÉES — SYNTHÈSE

## H.1 — Incohérences Critiques

| # | Module | Incohérence | Impact | Correction proposée |
|---|---|---|---|---|
| **IC1** | Corridors | **Corridors non ancrés au waypoint** | Les corridors ne partent pas du waypoint mais connectent zone↔zone. L'usager ne sait pas comment rejoindre les zones. | Ajouter un corridor waypoint→zone_la_plus_proche pour chaque sexe. |
| **IC2** | Corridors | **Fallback direct traverse potentiellement routes** | Le fallback `_direct_path_latlon()` perturbe les points mais ne vérifie pas géométriquement l'intersection avec les routes. | Post-validation géométrique : si un corridor croise une route, le marquer comme `low_confidence`. |
| **IC3** | Pipeline V5/V7 | **Double exclusion : V5 + V7** | `zone_engine_core_v2.py` exécute `_is_zone_excluded()` (V5), puis `pipeline_v7.py` exécute `process_zones_v6()` (V7). Les deux filtrent les zones. En V7, l'exclusion V5 est redondante mais pas désactivée. | Quand `EXCLUSION_ENGINE_VERSION=v7`, skip l'exclusion V5. |

## H.2 — Incohérences Moyennes

| # | Module | Incohérence | Impact | Correction proposée |
|---|---|---|---|---|
| **IM1** | Frontend | **MonTerritoireBionicPage.jsx ~1700 lignes** | Maintenabilité faible, risque de bugs en cascade. | Poursuivre décomposition Phases 3-4. |
| **IM2** | Pipeline | **Orientation vent non implémentée** | Les déplacements ne tiennent pas compte du vent dominant. | Intégrer les données Open-Meteo wind dans la grille de coûts. |
| **IM3** | Pipeline | **zone_penalty_engine V5 appliqué même en V7** | Le penalty engine V5 (`calculate_zone_penalty`) est appliqué en plus du scoring V7, ce qui double-pénalise les zones. | En V7, utiliser uniquement le scoring V7 (`zone_typology_v7`). |
| **IM4** | Terrain Data | **`_fetch_exclusions_from_terrain` utilise `OVERPASS_API_URL` hardcodé** | La fonction dans `zone_engine_core_v2.py` (V5 path) importe `OVERPASS_API_URL` directement sans utiliser les miroirs V7.3. | Router toutes les requêtes via la logique retry+miroirs de `terrain_data_router.py`. |

## H.3 — Incohérences Basses

| # | Module | Description | Correction |
|---|---|---|---|
| IB1 | Cache | Cache mémoire zone (TTL 15min) vs cache Overpass (TTL 1h). | Aligner les TTL ou documenter la raison. |
| IB2 | Frontend | 404 sur `/api/sharing/groups` et `/api/notifications`. | Créer les routes manquantes ou retirer les appels. |
| IB3 | API | Endpoint `/api/products/top` lent. | Contourné côté client, cause racine non résolue. |
| IB4 | WMS | Erreur 401 MFFP. | Service externe, hors contrôle. |

---

# H.4 — Plan de Correction Priorisé

## Phase 1 — Corrections Critiques (IC1-IC3)

| # | Action | Effort | Fichiers |
|---|---|---|---|
| 1 | Ajouter corridor waypoint→zone | Moyen | `corridor_v7.py`, `pipeline_v7.py` |
| 2 | Post-validation géométrique corridors vs routes | Moyen | `corridor_v7.py` |
| 3 | Skip exclusion V5 quand `EXCLUSION_ENGINE_VERSION=v7` | Faible | `zone_engine_core_v2.py` |

## Phase 2 — Corrections Moyennes (IM1-IM4)

| # | Action | Effort | Fichiers |
|---|---|---|---|
| 4 | Décomposition MonTerritoireBionicPage Phases 3-4 | Élevé | Frontend |
| 5 | Intégrer vent dominant dans grille coûts | Moyen | `trail_cost_grid_v7.py`, `weather_service.py` |
| 6 | Désactiver penalty engine V5 en mode V7 | Faible | `zone_engine_core_v2.py` |
| 7 | Unifier fetch Overpass via terrain_data_router | Faible | `zone_engine_core_v2.py` |

## Phase 3 — Tests Manquants (T1-T7)

| # | Action | Effort |
|---|---|---|
| 8 | Tests ancrage corridors waypoint | Faible |
| 9 | Tests corridors vs routes | Moyen |
| 10 | Test cohérence count backend/frontend | Faible |
| 11 | Test fallback cache expiré | Faible |
| 12 | Test fusion zones < 200m | Faible |

---

# ANNEXE — Résumé des Fichiers Critiques

| Fichier | Lignes | Rôle |
|---|---|---|
| `zone_engine_core_v2.py` | 701 | Orchestrateur principal pipeline |
| `pipeline_v7.py` | 411 | Pipeline V7 (exclusion + enrichissement + fusion) |
| `exclusion_engine_v6.py` | 360 | Moteur d'exclusion géométrique Shapely |
| `exclusion_config_v6.py` | 135 | Configuration buffers + seuils |
| `exclusion_geometry_v6.py` | 298 | Opérations géométriques Shapely |
| `corridor_v7.py` | 768 | Générateur de corridors A* |
| `trail_cost_grid_v7.py` | 442 | Rasterisation grille de coûts |
| `species_behavior_v7.py` | 282 | Matrices comportementales |
| `zone_typology_v7.py` | 445 | Classification + scoring multi-critères |
| `zone_shape_v7.py` | 253 | Morphologie terrain-aware |
| `terrain_signals_v7.py` | 190 | Signaux terrain depuis OSM |
| `behavioral_rasterizer.py` | 294 | Rasterisation comportementale |
| `organic_zone_generator_v2.py` | 388 | Marching Squares + Chaikin |
| `zone_penalty_engine.py` | 229 | Pénalités semi-statiques V5 |
| `terrain_data_router.py` | 718 | API Overpass + cache R5 |
| `MonTerritoireBionicPage.jsx` | 1728 | Page principale frontend |
| `BionicMicroZones.jsx` | 452 | Rendu zones Leaflet |
| `useZoneOrchestrator.js` | 211 | Orchestrateur zones frontend |
| `BionicZoneService.js` | 237 | Service API zones |
| `useSpatialClipping.js` | 210 | Clipping client-side |

---

**FIN DU RAPPORT D'AUDIT TOTAL BIONIC™ V7.3**
*Généré le 10 mars 2026 — Exhaustif, structuré, documenté.*
