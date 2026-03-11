# ENGINE MAP BIONIC - Audit Complet P0
## Date: 2026-02-XX | Version: V8.1 Post-Stabilisation

---

## 1. ENGINE MAP - Backend

### 1.1 Pipeline Principal (ACTIF - V7)

| Engine | Fichier | Role | Input | Output | Dependances |
|--------|---------|------|-------|--------|-------------|
| **Zone Engine Core V2** | `bionic_engine_p0/services/zone_engine_core_v2.py` (704L) | Orchestrateur principal du pipeline. Coordonne rasterisation, contours, exclusions, GeoJSON. Thread pool parallele (6 workers). Cache TTL 15min. | bounds, species, layers, exclusions, resolution, waypoint_center | GeoJSON (features, corridors, stats) | behavioral_rasterizer, organic_zone_generator_v2, zone_visual_layer_v2, zone_penalty_engine, pipeline_v7, corridor_v7, osm_cache_service, srtm_provider_v7 |
| **Pipeline V7** | `bionic_engine_p0/services/pipeline_v7.py` (413L) | Pipeline V7 par couche: Exclusion V6 -> Shape Enhancement -> Enrichissement V7 -> Hotspot Detection -> Zone Merge | raw_zones, bounds, exclusions, layer_id, species, weather, dem_data, month | (valid_zones, rejected_zones, stats) | exclusion_engine_v6, zone_typology_v7, terrain_signals_v7, corridor_v7, zone_shape_v7, species_behavior_v7 |
| **Corridor V7** | `bionic_engine_p0/services/corridor_v7.py` (1144L) | Generation corridors A* terrain-aware. Differengie male/femelle, reel/IA. | zones, exclusions, species, terrain_signals, dem_data, month, waypoint_center | corridors[] | species_behavior_v7, trail_cost_grid_v7 |
| **Exclusion Engine V6** | `bionic_engine_p0/services/exclusion_engine_v6.py` | Exclusion geometrique Shapely (P0 eau + P1 routes + P2 urbain) | raw_zones, bounds, exclusions, layer_id, species | (valid_zones, rejected_zones, v6_stats) | exclusion_config_v6, exclusion_geometry_v6 |
| **Zone Typology V7** | `bionic_engine_p0/services/zone_typology_v7.py` | Classification + scoring multi-criteres des zones | zone, layer_id, species, exclusions, weather, month, dem_stats | zone enrichie (v7: {zone_type, score_global, subscores}) | - |
| **Zone Shape V7** | `bionic_engine_p0/services/zone_shape_v7.py` | Lissage adaptatif, snap berges, validation topologie | coords, iterations, terrain_roughness | smoothed/validated coords | - |
| **Species Behavior V7** | `bionic_engine_p0/services/species_behavior_v7.py` | Matrices comportementales par espece, saison, sexe | species, season, month | needs, season_modifier, sex_params | - |
| **Terrain Signals V7** | `bionic_engine_p0/services/terrain_signals_v7.py` | Signaux terrain depuis exclusions (proximite eau, routes, foret) | centroid, exclusions, radius | terrain_signals dict | - |
| **Trail Cost Grid V7** | `bionic_engine_p0/services/trail_cost_grid_v7.py` | Grille de couts pour pathfinding A* | bounds, exclusions, dem_data | cost_grid numpy array | - |
| **SRTM Provider V7** | `bionic_engine_p0/services/srtm_provider_v7.py` | Donnees DEM SRTM depuis OpenTopography | bounds | {status, stats, data} | httpx (OpenTopography API) |

### 1.2 Engines de Support (ACTIFS)

| Engine | Fichier | Role | Actif? |
|--------|---------|------|--------|
| **Behavioral Rasterizer** | `services/behavioral_rasterizer.py` | Generation rasters comportementaux par couche | OUI |
| **Organic Zone Generator V2** | `services/organic_zone_generator_v2.py` | Marching Squares + Chaikin smoothing -> polygones | OUI |
| **Zone Visual Layer V2** | `services/zone_visual_layer_v2.py` | Conversion zones -> GeoJSON avec styles | OUI |
| **Zone Penalty Engine** | `services/zone_penalty_engine.py` | Penalites sur zones (urbain, routes proches) | OUI |
| **OSM Cache Service** | `services/osm_cache_service.py` | Cache MongoDB pour donnees Overpass | OUI |
| **OSM Extractor V2** | `services/osm_extractor_v2.py` | Extraction donnees Overpass API | OUI |
| **Scoring Zone Integration** | `services/scoring_zone_integration.py` | Enrichissement GeoJSON avec scores V5 (DESACTIVE si V7) | CONDITIONNEL |
| **Weather Cache Service** | `services/weather_cache_service.py` | Cache pour donnees meteo | OUI |

### 1.3 Weather Engine (ACTIF - Module Separe)

| Engine | Fichier | Role |
|--------|---------|------|
| **Weather Service** | `weather_engine/v1/service.py` (219L) | Logique de scoring meteo pour la chasse |
| **External Service (OpenWeatherMap)** | `weather_engine/v1/external_service.py` (612L) | Integration OpenWeatherMap 2.5 API, cache 30min, fallback simule |
| **Weather Router** | `weather_engine/v1/router.py` (322L) | Endpoints: /current, /hourly, /daily, /full, /analyze, /score, /moon |

### 1.4 Engines Heritage / Potentiels Doublons

| Engine | Fichier | Statut | Risque Doublon |
|--------|---------|--------|----------------|
| **Corridor Service (V5/G)** | `services/corridor_service.py` | LEGACY - Phase G P1-Hotspots | MEDIUM - Supercede par corridor_v7.py |
| **Zone Service (V5/G)** | `services/zone_service.py` | LEGACY - Phase G P1-Hotspots | MEDIUM - Supercede par zone_engine_core_v2.py |
| **Weather Service (Bionic P0)** | `bionic_engine_p0/services/weather_service.py` | Potentiel doublon avec weather_engine | A VERIFIER |
| **Scoring Zone Integration** | `services/scoring_zone_integration.py` | V5 scoring - DESACTIVE quand V7 est actif | SAFE - Feature flag |
| **Unified Scoring Service** | `services/unified_scoring_service.py` | Scoring unifie | A VERIFIER si utilise |
| **Dynamic Scoring Service** | `services/dynamic_scoring_service.py` | Scoring dynamique | A VERIFIER |

---

## 2. ENGINE MAP - Frontend

### 2.1 Page Principale

| Composant | Fichier | Lignes | Role |
|-----------|---------|--------|------|
| **MonTerritoireBionicPage** | `pages/MonTerritoireBionicPage.jsx` | 1152 | Page principale, orchestration des composants, etat global |

### 2.2 Composants Territoire (Extraits IM1/IM1.2)

| Composant | Fichier | Lignes | Role |
|-----------|---------|--------|------|
| **MapContent** | `territoire/map/MapContent.jsx` | 169 | Carte Leaflet et ses layers (React.memo) |
| **SplitViewContainer** | `territoire/map/SplitViewContainer.jsx` | 247 | Mode Split View V8.1 (2 cartes synchronisees) |
| **MapHelpers** | `territoire/map/MapHelpers.jsx` | ~100 | Utilitaires carte |
| **TerritoireHeader** | `territoire/ui/TerritoireHeader.jsx` | 53 | Header de la page (React.memo) |
| **TerritoireDialogs** | `territoire/ui/TerritoireDialogs.jsx` | 198 | Modales et dialogs |
| **SidePanelZones** | `territoire/ui/SidePanelZones.jsx` | 98 | Panel lateral zones (React.memo) |
| **BiologicalSeasonSelector** | `territoire/ui/BiologicalSeasonSelector.jsx` | 60 | Selecteur de saison V8.1 |
| **BionicLegend** | `territoire/BionicLegend.jsx` | ~120 | Legende des zones |
| **MonTerritoireToolbar** | `territoire/MonTerritoireToolbar.jsx` | ~200 | Barre d'outils |

### 2.3 Hooks (Logique Metier)

| Hook | Fichier | Lignes | Role |
|------|---------|--------|------|
| **useZoneOrchestrator** | `hooks/useZoneOrchestrator.js` | 211 | Orchestration pipeline zones: Cache -> Backend -> Affichage |
| **useWaypointActions** | `hooks/useWaypointActions.js` | 188 | CRUD waypoints, selection, suppression |
| **useZoneCache** | `hooks/useZoneCache.js` | 107 | Cache IndexedDB (idb-keyval) |
| **useSplitViewSync** | `hooks/useSplitViewSync.js` | 79 | Synchronisation zoom/pan entre 2 cartes |
| **useSplitViewZones** | `hooks/useSplitViewZones.js` | 80 | Chargement zones pour carte droite (Split View) |
| **useBionicWeather** | `hooks/useBionicWeather.js` | 181 | Donnees meteo LIVE avec polling |
| **useGeolocation** | `hooks/useGeolocation.js` | ~60 | Geolocalisation navigateur |
| **useMapType** | `hooks/useMapType.js` | ~40 | Toggle type de carte |
| **useBionicLayers** | `hooks/useBionicLayers.js` | ~100 | Gestion layers actifs |
| **useBionicScoring** | `hooks/useBionicScoring.js` | ~80 | Scoring frontend (affichage) |

### 2.4 Services Frontend

| Service | Fichier | Lignes | Role |
|---------|---------|--------|------|
| **BionicZoneService** | `services/BionicZoneService.js` | 247 | Interface backend zones. POST /organic-zones. Cache en memoire. |

### 2.5 Core Bionic (Legacy / Reference)

| Module | Fichier | Lignes | Statut |
|--------|---------|--------|--------|
| **bionicWeatherEngine** | `core/bionic/bionicWeatherEngine.js` | 420 | ACTIF - Utilise par useBionicWeather |
| **bionicScoring** | `core/bionic/bionicScoring.js` | 610 | Reference scoring (affichage) |
| **bionicDataAdapter** | `core/bionic/bionicDataAdapter.js` | 418 | Adaptation donnees |
| **bionicHybridModel** | `core/bionic/bionicHybridModel.js` | 378 | Modele hybride |
| **bionicStrategyEngine** | `core/bionic/bionicStrategyEngine.js` | 496 | Strategie chasse |
| **bionicConfig** | `core/bionic/bionicConfig.js` | 251 | Configuration |
| **bionicSpecies** | `core/bionic/bionicSpecies.js` | 162 | Config especes |
| **speciesConfig** | `core/bionic/speciesConfig.js` | 136 | Config especes (doublon?) |
| **bionicModules** | `core/bionic/bionicModules.js` | 149 | Registry modules |
| **index** | `core/bionic/index.js` | 105 | Barrel exports |

---

## 3. ENGINE HEALTH CHECK

### 3.1 Risques de Doublons

| Zone | Risque | Detail | Action Recommandee |
|------|--------|--------|-------------------|
| corridor_service.py vs corridor_v7.py | MEDIUM | corridor_service.py est l'ancien moteur Phase G. corridor_v7.py est le V7 actif. L'ancien n'est plus appele par le pipeline principal. | AUDITER - Confirmer que corridor_service.py n'est importe nulle part sauf dans router.py legacy |
| zone_service.py vs zone_engine_core_v2.py | MEDIUM | zone_service.py est l'ancien moteur. zone_engine_core_v2.py est le V2 actif. | AUDITER |
| bionicSpecies.js vs speciesConfig.js | LOW | Deux fichiers de config especes dans core/bionic/ | VERIFIER si l'un est redondant |
| weather_service.py (P0) vs weather_engine/v1/service.py | MEDIUM | Deux services meteo distincts. P0 semble etre pour le scoring interne, V1 pour l'API externe. | VERIFIER les interactions |
| scoring_zone_integration.py vs zone_typology_v7.py | SAFE | Feature flag empece l'execution du V5 scoring quand V7 est actif | AUCUNE |

### 3.2 Recalculs Inutiles

| Zone | Risque | Detail |
|------|--------|--------|
| Cache memoire backend | LOW | Cache TTL 15min avec cle MD5 arrondie. Efficace apres premier appel. |
| Cache IndexedDB frontend | LOW | Cache persiste entre sessions. Clef deterministique par waypoint+species+season. |
| Cache BionicZoneService | LOW | Cache en memoire simple (1 entree). Efficace pour requetes repetees. |
| **ATTENTION: Premier appel** | HIGH | Premier appel sans cache: ~37.5s (Overpass API + DEM + Pipeline). Goulot d'etranglement majeur. |
| Overpass API fetch | HIGH | Fetch des exclusions = 90% du temps de calcul. Pas de pre-chargement. |

### 3.3 Dependances Circulaires

| Zone | Risque | Detail |
|------|--------|--------|
| Pipeline V7 -> Exclusion V6 -> OSM | NONE | Dependance lineaire, pas de circularite |
| useZoneOrchestrator -> useZoneCache -> idb-keyval | NONE | Dependance lineaire |
| SplitViewContainer -> useSplitViewZones -> BionicZoneService | NONE | Dependance lineaire |
| **Aucune dependance circulaire detectee** | | |

### 3.4 Surcharge Performance

| Zone | Severite | Detail |
|------|----------|--------|
| **Overpass API** | CRITIQUE | 90% du temps pipeline. 1345 exclusions fetched pour un viewport de 3x4km. |
| **SRTM DEM** | MEDIUM | Fetch OpenTopography a chaque premier appel. Cache TTL pourrait etre etendu. |
| Exclusion V6 processing | LOW | ~1200ms par couche (5 couches = ~6s). Acceptable. |
| Pipeline V7 enrichissement | LOW | Rapide apres exclusion. |
| Frontend re-renders | LOW | React.memo applique sur composants cles. |

### 3.5 Couverture de Tests

| Zone | Tests Unitaires | Tests Integration | Tests UI |
|------|----------------|-------------------|----------|
| Pipeline V7 | OUI (test_v7_engine.py, test_passe2_corridors.py) | OUI | - |
| Exclusion Engine | OUI (test_exclusions_v1.py, test_urban_exclusion_v7.py) | OUI | - |
| V8.1 Saisons Bio | OUI (test_v8_1_biological_seasons.py - 10 tests) | OUI | OUI (17/17) |
| V8.1 Split View | - | - | OUI (17/17 via testing_agent) |
| Weather Engine | Partiel | Partiel | NON |
| Frontend hooks | - | - | OUI (via testing_agent) |
| **Total backend tests** | 32+ fichiers | - | - |

---

## 4. PERFORMANCE TRACE

### 4.1 Temps de Generation des Zones (Premier Appel - Sans Cache)

| Etape | Temps | % Total | Detail |
|-------|-------|---------|--------|
| **Overpass API fetch** | ~30s | ~80% | Fetch exclusions OSM pour 5 couches. GOULOT PRINCIPAL. |
| SRTM DEM fetch | ~2s | ~5% | OpenTopography API. Cache TTL ok. |
| Rasterisation (5 couches) | ~2s | ~5% | ThreadPoolExecutor 6 workers. |
| Exclusion V6 (5 couches) | ~6s | ~16% | ~1200ms/couche. Shapely geometrique. |
| Pipeline V7 enrichissement | <1s | ~2% | Scoring, hotspots, merge. |
| Corridor A* generation | ~1s | ~3% | Si zones valides. |
| **TOTAL (premier appel)** | **~37.5s** | **100%** | Zone urbaine = pire cas (toutes zones exclues) |
| **TOTAL (cache hit)** | **~0.12s** | - | Cache memoire backend |

### 4.2 Temps de Rendu des Layers Frontend

| Etape | Temps | Detail |
|-------|-------|--------|
| Cache IndexedDB lookup | <100ms | idb-keyval, cle deterministique |
| GeoJSON parsing | ~10ms | Conversion features -> positions Leaflet |
| Leaflet render (zones) | ~50-200ms | Dependant du nombre de polygones |
| Leaflet render (corridors) | ~20-50ms | Polylines avec styles |
| Split View (2 cartes) | ~100-400ms | Double rendu Leaflet |

### 4.3 Poids des Payloads

| Endpoint | Taille | Detail |
|----------|--------|--------|
| /organic-zones (0 zones) | ~2 KB | Stats seulement |
| /organic-zones (10 zones + corridors) | ~15-25 KB | Coordonnees arrondies a 6 decimales |
| /weather/full | ~8-12 KB | Current + 48h hourly + 7d daily |
| Cache IndexedDB par entree | ~5-20 KB | Zones + corridors serialises |

### 4.4 Temps de Reponse Backend (API)

| Endpoint | Premier Appel | Cache Hit | Detail |
|----------|--------------|-----------|--------|
| POST /organic-zones | ~37s | ~0.12s | Cache MD5 en memoire, TTL 15min |
| GET /weather/full | ~2s | ~0.01s | Cache TTL 30min (simule sans cle API) |

---

## 5. INTERACTIONS ENTRE ENGINES

```
[Frontend]
  MonTerritoireBionicPage
    -> useZoneOrchestrator ---------> [useZoneCache (IndexedDB)]
    |                                       |
    |   (cache miss)                        v
    +-> BionicZoneService.js ----------> POST /api/v1/bionic/organic-zones
                                              |
[Backend]                                     v
  organic_zones_router.py ----> zone_engine_core_v2.py
                                     |
                                     +-> osm_cache_service -----> Overpass API (LENT)
                                     +-> srtm_provider_v7 ------> OpenTopography API
                                     +-> behavioral_rasterizer --> raster generation
                                     +-> organic_zone_generator -> contours + polygones
                                     |
                                     v (par couche, 6 threads)
                                pipeline_v7.py
                                     +-> exclusion_engine_v6 (Shapely)
                                     +-> zone_shape_v7 (lissage)
                                     +-> zone_typology_v7 (scoring V7)
                                     |
                                     v (post-traitement)
                                     +-> generate_all_corridors_v7
                                           +-> corridor_v7 (A*, terrain-aware)
                                           +-> trail_cost_grid_v7 (DEM)
```

---

## 6. RECOMMANDATIONS

### 6.1 Optimisations Prioritaires (P0)
1. **Pre-chargement Overpass API**: Declencher le fetch OSM en arriere-plan des que le waypoint est place, AVANT le calcul complet.
2. **Cache Overpass etendu**: Augmenter le TTL du cache MongoDB OSM (actuellement ~15min -> 24h pour donnees statiques).
3. **Parallelisation Overpass**: Fetch les exclusions en parallele avec le DEM SRTM.

### 6.2 Nettoyage Code (P1)
1. **corridor_service.py**: Confirmer inutilisation et supprimer.
2. **zone_service.py**: Confirmer inutilisation et supprimer.
3. **speciesConfig.js vs bionicSpecies.js**: Consolider en un seul fichier.
4. **weather_service.py (P0)**: Verifier si duplique weather_engine/v1.

### 6.3 Architecture V8.2/V8.3 (voir schema separe)
