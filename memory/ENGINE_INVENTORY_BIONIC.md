# INVENTAIRE COMPLET DES ENGINES — CARTE INTERACTIVE BIONIC™
## Version: V8.2 | Date: 2026-03-10 | Compliance: BIONIC 1000%

---

# ═══════════════════════════════════════════════════════════════
# 1. ENGINES BACKEND (V7/V8)
# ═══════════════════════════════════════════════════════════════

## 1.1 ZONE ENGINE CORE V2 — Orchestrateur Principal
- **Rôle:** Orchestre le pipeline complet de génération de zones organiques. Coordonne rasterisation, contours, exclusions, corridors, GeoJSON. Thread pool parallèle (6 workers). Cache mémoire TTL 15min.
- **Point d'entrée:** `services/zone_engine_core_v2.py` → `generate_organic_zones()` (737L)
- **Input:** bounds, species, layers[], resolution, max_zones_per_layer, waypoint_center, biological_season
- **Output:** GeoJSON FeatureCollection {features[], corridors[], stats{}, corridor_styles{}, zone_type_config{}}
- **Dépendances:**
  - _fetch_exclusions_from_terrain → terrain_data_router (Overpass API)
  - behavioral_rasterizer → rasters par couche
  - organic_zone_generator_v2 → contours + polygones
  - zone_visual_layer_v2 → conversion GeoJSON
  - zone_penalty_engine → pénalités zones
  - pipeline_v7 → enrichissement par couche
  - generate_all_corridors_v7 → corridors A*
  - srtm_provider_v7 → DEM
- **Temps moyen:** 26s (Overpass fail + dégradation) | 12s (Overpass OK) | 0.5s (cache hit)
- **Risque doublon:** AUCUN — seul orchestrateur V7
- **Tests:** test_v7_engine.py, test_v8_2_resilience_pipeline.py, test_rural_zone_generation.py

---

## 1.2 PIPELINE V7 — Enrichissement par Couche
- **Rôle:** Pipeline V7 séquentiel par couche. Exclusion V6 → Shape Enhancement → Enrichissement V7 → Hotspot Detection → Zone Merge. Filtre les zones par le périmètre du waypoint.
- **Point d'entrée:** `services/pipeline_v7.py` → `process_zones_v7()` (412L)
- **Input:** raw_zones, bounds, exclusions, layer_id, species, weather, dem_data, month, biological_season, waypoint_center
- **Output:** (valid_zones[], rejected_zones[], stats{})
- **Dépendances:** exclusion_engine_v6, zone_typology_v7, zone_shape_v7, species_behavior_v7, terrain_signals_v7, corridor_v7
- **Fonctions clés:**
  - `process_zones_v7()` — Pipeline complet
  - `_filter_zones_by_perimeter()` — Filtre distance waypoint
  - `generate_all_corridors_v7()` — Génère tous corridors
  - `_merge_nearby_same_type_zones()` — Fusion zones proches
  - `build_v7_response_metadata()` — Métadonnées V7
- **Temps moyen:** ~1.2s par couche (x5 = ~6s total, exécuté en parallèle)
- **Risque doublon:** AUCUN — seul pipeline V7
- **Tests:** test_passe2_corridors.py, test_v7_engine.py

---

## 1.3 CORRIDOR V7 — Pathfinding A* Terrain-Aware
- **Rôle:** Génération de corridors de déplacement A* terrain-aware. Différencie mâle/femelle, réel/IA. Lissage Chaikin. Score et confiance. Intersection routes.
- **Point d'entrée:** `services/corridor_v7.py` (1143L)
- **Fonctions clés:**
  - `_astar()` — Pathfinding A* sur grille de coûts
  - `_grid_path_to_latlon()` — Conversion grille → coordonnées
  - `_chaikin_smooth()` — Lissage courbes
  - `_score_trail()` — Score du corridor
  - `_assess_confidence()` — Niveau de confiance
  - `_corridors_intersect_roads()` — Intersection routes
- **Input:** zones[], exclusions, species, terrain_signals, dem_data, month, waypoint_center
- **Output:** corridors[] {coords, score, sex, type, confidence, length_m}
- **Dépendances:** trail_cost_grid_v7, species_behavior_v7
- **Temps moyen:** ~1-3s (selon nombre de zones)
- **Risque doublon:** MEDIUM — `corridor_service.py` (539L) est LEGACY Phase G, encore importé par `router.py` legacy
- **Tests:** test_corridors_v7.py, test_corridor_filtering_v7.py, test_passe2_corridors.py

---

## 1.4 EXCLUSION ENGINE V6 — Filtrage Géométrique
- **Rôle:** Exclusion géométrique Shapely. P0 eau + P1 routes + P2 urbain. Buffers configurables. Calcul d'intersection ratio et distance minimale.
- **Point d'entrée:** `services/exclusion_engine_v6.py` → `process_zones_v6()` (361L)
- **Input:** raw_zones[], bounds, exclusions[], layer_id, species
- **Output:** (valid_zones[], rejected_zones[], v6_stats{})
- **Dépendances:** exclusion_config_v6 (132L), exclusion_geometry_v6 (297L)
- **Sous-modules:**
  - `exclusion_config_v6.py` → `get_buffer_m()` — Buffers par type
  - `exclusion_geometry_v6.py` → `build_exclusion_unions()` — Unions Shapely, `trim_zone()` — Découpe, `calculate_intersection_ratio()`
- **Temps moyen:** ~1.2s par couche
- **Risque doublon:** AUCUN
- **Tests:** test_exclusions_v1.py, test_bionic_p0_exclusion_zones.py, test_urban_exclusion_v7.py

---

## 1.5 ZONE TYPOLOGY V7 — Classification + Scoring
- **Rôle:** Classification multi-critères des zones. Score global (0-1) avec sous-scores. Détection de hotspots. Pertinence saisonnière.
- **Point d'entrée:** `services/zone_typology_v7.py` → `enrich_zone_v7()` (479L)
- **Input:** zone, layer_id, species, exclusions, weather, month, dem_stats
- **Output:** zone enrichie {zone_type, score_global, subscores{habitat, terrain, season, behavior, weather}, confidence}
- **Fonctions clés:**
  - `compute_subscores()` — Sous-scores multi-critères
  - `compute_global_score()` — Score global pondéré
  - `classify_zone_type()` — Classification (bedding, feeding, travel, water_edge, etc.)
  - `detect_hotspots()` — Détection hotspots
  - `get_zone_season_relevance()` — Pertinence saisonnière par zone_type
- **Dépendances:** species_behavior_v7, terrain_signals_v7
- **Temps moyen:** <50ms par zone
- **Risque doublon:** AUCUN
- **Tests:** test_v7_engine.py (intégré)

---

## 1.6 SPECIES BEHAVIOR V7 — Matrices Comportementales
- **Rôle:** Définit les besoins comportementaux par espèce, saison, sexe. Matrices de coûts pour corridors. Modificateurs météo.
- **Point d'entrée:** `services/species_behavior_v7.py` (281L)
- **Fonctions clés:**
  - `get_species_needs()` — Besoins par espèce
  - `get_sex_params()` — Paramètres sexe-spécifiques
  - `get_season_modifier()` — Modificateur saisonnier (mois → facteur)
  - `get_corridor_cost()` — Coûts corridor (mâle/femelle × feature)
  - `get_weather_modifier()` — Impact météo par zone_type
- **Input:** species, season/month, sex, weather_condition
- **Output:** Dict de facteurs/coefficients
- **Dépendances:** AUCUNE (module autonome)
- **Temps moyen:** <1ms (lookup table)
- **Risque doublon:** AUCUN
- **Tests:** test_v8_1_biological_seasons.py

---

## 1.7 SRTM PROVIDER V7 — DEM Engine
- **Rôle:** Récupère les données d'élévation SRTM depuis OpenTopography API. Cache interne. Fournit altitude, pente, orientation, rugosité.
- **Point d'entrée:** `services/srtm_provider_v7.py` → `fetch_dem_for_pipeline()` (234L)
- **Input:** bounds {north, south, east, west}
- **Output:** {status, stats{alt_min, alt_max, slope_mean, roughness_mean, pixel_size_m}, data(numpy)}
- **Dépendances:** httpx (OpenTopography API externe)
- **Temps moyen:** ~2s (premier appel) | ~10ms (cache)
- **Risque doublon:** MEDIUM — `dem_service.py` fait aussi des appels DEM, mais pour des endpoints différents
- **Tests:** test_srtm_integration.py, test_dem_opentopography_api.py

---

## 1.8 OVERPASS ENGINE (Cache + Fetch)
- **Rôle:** Fetch des données OpenStreetMap (exclusions: eau, routes, urbain, infrastructure). Cache MongoDB + fichier avec TTL. Parsing des résultats Overpass.
- **Point d'entrée:**
  - `routers/terrain_data_router.py` → `get_terrain_data()` (717L) — Route API
  - `services/zone_engine_core_v2.py` → `_fetch_exclusions_from_terrain()` — Pipeline intégré
- **Input:** bounds, exclude_types[], detail_level
- **Output:** exclusion_zones[] {type, sub_type, geometry, name, buffer_m}
- **Sous-modules:**
  - `osm_cache_service.py` (714L) — Cache en mémoire + régions
  - `osm_extractor_v2.py` (384L) — Extraction OSM batch
- **Dépendances:** MongoDB (collection overpass_cache_r5), httpx (Overpass API)
- **Temps moyen:** 12s (1er appel, Overpass OK) | 0s (cache) | 26s (dégradation V8.2)
- **Cache TTL:** MongoDB 1h | Fichier 7j | Mémoire 15min
- **Risque doublon:** LOW — osm_cache_service.py a un système de cache régional parallèle au cache terrain_data_router
- **Tests:** test_overpass_cache_r5.py, test_v8_2_resilience_pipeline.py

---

## 1.9 BEHAVIORAL RASTERIZER — Génération Rasters
- **Rôle:** Génère les rasters comportementaux par couche via bruit Simplex fractal. Graine déterministe (coords + layer + species). Modulation par couche.
- **Point d'entrée:** `services/behavioral_rasterizer.py` → `generate_layer_raster()` (293L)
- **Input:** bounds, layer_id, species, resolution
- **Output:** numpy 2D array (valeurs 0-1)
- **Dépendances:** numpy
- **Temps moyen:** ~100ms par couche
- **Risque doublon:** AUCUN
- **Tests:** test_v7_engine.py (intégré)

---

## 1.10 ORGANIC ZONE GENERATOR V2 — Contours + Polygones
- **Rôle:** Extraction de contours par Marching Squares. Lissage Chaikin. Jitter aléatoire pour aspect organique. Calcul aire et compacité.
- **Point d'entrée:** `services/organic_zone_generator_v2.py` → `extract_contours()` (387L)
- **Input:** grid(numpy), bounds, threshold
- **Output:** contours[] (listes de coordonnées [lng, lat])
- **Fonctions clés:**
  - `extract_contours()` — Marching Squares
  - `chaikin_smooth()` — Lissage itératif
  - `_jitter_vertices()` — Variation organique
  - `polygon_area_m2()` — Calcul surface
- **Dépendances:** numpy
- **Temps moyen:** ~200ms
- **Risque doublon:** LOW — `organic_contour_generator.py` existe aussi (V1 legacy?)
- **Tests:** test_v7_engine.py (intégré)

---

## 1.11 ZONE VISUAL LAYER V2 — GeoJSON Converter
- **Rôle:** Convertit les zones internes en features GeoJSON avec styles (couleur, opacité) et propriétés frontend.
- **Point d'entrée:** `services/zone_visual_layer_v2.py` → `zones_to_geojson()` (143L)
- **Input:** zones[], layer_styles
- **Output:** GeoJSON features[]
- **Dépendances:** AUCUNE
- **Temps moyen:** <10ms
- **Risque doublon:** AUCUN
- **Tests:** test_v7_engine.py (intégré)

---

## 1.12 ZONE PENALTY ENGINE — Pénalités
- **Rôle:** Applique des pénalités de score basées sur la proximité aux exclusions (urbain, routes, infrastructure).
- **Point d'entrée:** `services/zone_penalty_engine.py` → `calculate_zone_penalty()` (228L)
- **Input:** zone, exclusions, species
- **Output:** penalty_factor (0-1), penalty_details{}
- **Dépendances:** AUCUNE
- **Temps moyen:** <5ms par zone
- **Risque doublon:** AUCUN
- **Tests:** test_bionic_p1_zone_penalties.py

---

## 1.13 ZONE SHAPE V7 — Lissage + Topologie
- **Rôle:** Lissage adaptatif des contours. Snap aux berges. Fusion zones adjacentes. Validation topologique.
- **Point d'entrée:** `services/zone_shape_v7.py` (252L)
- **Fonctions clés:**
  - `smooth_zone_adaptive()` — Lissage selon rugosité terrain
  - `snap_to_shorelines()` — Accrochage berges
  - `merge_adjacent_zones()` — Fusion zones proches
  - `validate_zone_topology()` — Validation géométrie
- **Input:** coords[], terrain_roughness
- **Output:** smoothed_coords[]
- **Dépendances:** AUCUNE
- **Temps moyen:** <20ms par zone
- **Risque doublon:** AUCUN
- **Tests:** test_v7_engine.py (intégré)

---

## 1.14 TERRAIN SIGNALS V7 — Signaux Terrain
- **Rôle:** Extrait des signaux terrain depuis les exclusions (proximité eau, routes, forêt). Signaux utilisés pour le scoring.
- **Point d'entrée:** `services/terrain_signals_v7.py` (189L)
- **Fonctions clés:**
  - `extract_terrain_signals_from_exclusions()` — Signaux depuis géométries
  - `fetch_weather_signals()` — Signaux météo (async)
  - `fetch_dem_signals()` — Signaux DEM (async)
- **Input:** centroid, exclusions, radius
- **Output:** {near_water, near_road, forest_density, water_distance_m, road_distance_m}
- **Dépendances:** exclusion_geometry_v6
- **Temps moyen:** ~5ms
- **Risque doublon:** AUCUN
- **Tests:** test_v7_engine.py (intégré)

---

## 1.15 TRAIL COST GRID V7 — Grille de Coûts A*
- **Rôle:** Construit la grille de coûts numpy pour le pathfinding A*. Rasterise les exclusions (eau=impassable, routes=coûteux, urbain=très coûteux). Gradient de proximité.
- **Point d'entrée:** `services/trail_cost_grid_v7.py` → `build_cost_grid()` (441L)
- **Input:** bounds, exclusions[], dem_data
- **Output:** numpy 2D cost_grid (valeurs 1.0 - inf)
- **Dépendances:** numpy
- **Temps moyen:** ~200ms
- **Risque doublon:** AUCUN
- **Tests:** test_corridors_v7.py (intégré)

---

## 1.16 WEATHER ENGINE V1 — Météo Externe
- **Rôle:** Module séparé pour les données météo. Intègre OpenWeatherMap 2.5. Cache 30min. Fallback données simulées si pas de clé API.
- **Point d'entrée:**
  - `weather_engine/v1/router.py` (321L) — Routes: /current, /hourly, /daily, /full, /analyze, /score, /moon
  - `weather_engine/v1/service.py` (218L) — WeatherService (scoring chasse)
  - `weather_engine/v1/external_service.py` (611L) — OpenWeatherMapService
- **Input:** lat, lng
- **Output:** {current, hourly[], daily[], hunting_analysis{}, moon_phase{}}
- **Dépendances:** httpx (OpenWeatherMap API), MongoDB (cache optionnel)
- **Temps moyen:** ~2s (1er appel) | ~10ms (cache)
- **Risque doublon:** MEDIUM — `weather_service.py` (754L) dans bionic_engine_p0 est un DOUBLON (même API)
- **Tests:** test_weather_shadow_v5_iteration79.py (partiel)

---

## 1.17 WEATHER SERVICE P0 — Météo Interne
- **Rôle:** Service météo interne au bionic_engine_p0. Modèles Pydantic (CurrentWeather, HourlyForecast, etc.). Facteurs comportementaux météo. Utilisé par le pipeline pour le scoring.
- **Point d'entrée:** `services/weather_service.py` → `WeatherService` (754L)
- **Input:** lat, lng
- **Output:** WeatherResponse (current, hourly, daily, behavior_factors)
- **Dépendances:** httpx (OpenWeatherMap API)
- **Temps moyen:** ~2s (identique au V1)
- **Risque doublon:** HIGH — Duplique weather_engine/v1 pour l'essentiel
- **Tests:** Partiel

---

## 1.18 WEATHER CACHE SERVICE
- **Rôle:** Cache MongoDB pour les données météo associées aux zones.
- **Point d'entrée:** `services/weather_cache_service.py` (140L) → `cache_put()`, `cache_get()`, `cache_stats()`
- **Input:** bounds, resolution, data
- **Output:** cached_data ou None
- **Dépendances:** MongoDB
- **Temps moyen:** <5ms
- **Risque doublon:** AUCUN
- **Tests:** AUCUN spécifique

---

## 1.19 WINDFIELD SERVICE — Grille Vectorielle Vent
- **Rôle:** Génère une grille vectorielle de vent (u, v) pour l'animation de particules frontend. Décomposition vitesse/direction en composantes.
- **Point d'entrée:** `services/windfield_service.py` (142L) → `generate_windfield()`, `fetch_and_generate_windfield()`
- **Input:** lat, lng, grid_size
- **Output:** {u_grid, v_grid, metadata}
- **Dépendances:** weather_engine (pour données vent)
- **Temps moyen:** ~100ms
- **Risque doublon:** AUCUN
- **Tests:** test_windfield_v5_iteration81.py

---

## 1.20 SSE ENGINE — Landcover + Microrelief
- **Rôle:** Génère des rasters de couverture terrestre (landcover), microrelief, et transitions de lisière. Utilisé pour des layers visuels avancés.
- **Point d'entrée:** `services/sse_engine.py` (544L) → `generate_sse_composite()`
- **Input:** bounds, species, resolution
- **Output:** {landcover_raster, microrelief_raster, edge_transitions[]}
- **Dépendances:** numpy
- **Temps moyen:** ~200ms
- **Risque doublon:** AUCUN
- **Tests:** test_sse_engine.py

---

## 1.21 SPATIAL CLIPPING — Découpe Spatiale
- **Rôle:** Calcule la bbox d'analyse (1km² autour du waypoint) et découpe les zones au périmètre.
- **Point d'entrée:** `services/spatial_clipping.py` (150L) → `clip_zones()`, `compute_analysis_bbox()`
- **Input:** zones[], bbox{north,south,east,west}
- **Output:** clipped_zones[]
- **Dépendances:** shapely
- **Temps moyen:** <10ms
- **Risque doublon:** AUCUN
- **Tests:** test_spatial_clipping.py, test_spatial_clipping_api.py

---

## 1.22 SCORING ENGINES — Système Multi-Niveau

### 1.22a SCORING ZONE INTEGRATION (V5 Legacy)
- **Fichier:** `services/scoring_zone_integration.py` (183L)
- **Rôle:** Enrichit le GeoJSON avec des scores V5. Conditionnel (désactivé quand V7 actif).
- **Importé par:** organic_zones_router.py, spatial_clipping_router.py
- **Risque doublon:** SAFE — Feature flag

### 1.22b UNIFIED SCORING SERVICE
- **Fichier:** `services/unified_scoring_service.py` (1159L)
- **Rôle:** Service de scoring unifié multi-facteurs. Utilisé par waypoint_analysis et heatmap_fusion.
- **Importé par:** waypoint_analysis_service.py, heatmap_fusion_service.py, waypoint_analysis_router.py
- **Risque doublon:** MEDIUM — Recouvre partiellement zone_typology_v7

### 1.22c DYNAMIC SCORING SERVICE
- **Fichier:** `services/dynamic_scoring_service.py` (883L)
- **Rôle:** Scoring dynamique avec pondérations ajustables. Utilisé par hunt_plan_analyzer et scoring_router.
- **Importé par:** hunt_plan_analyzer_service.py, scoring_router.py
- **Risque doublon:** MEDIUM — Recouvre partiellement unified_scoring_service

### 1.22d MULTIFACTOR SCORING ENGINE
- **Fichier:** `services/scoring/multifactor_scoring_engine.py` (342L)
- **Rôle:** Engine de scoring multi-facteurs avec poids dynamiques. Sous-services: habitat, weather, behavior, density, mobility, pressure, probability, risk.
- **Sous-services:** scoring/score_habitat_service.py, score_weather_service.py, score_behavior_service.py, score_density_service.py, score_mobility_service.py, score_pressure_service.py, score_probability_service.py, score_risk_service.py
- **Risque doublon:** HIGH — Recouvre zone_typology_v7 + unified_scoring + dynamic_scoring

---

## 1.23 ENGINES LEGACY (NE PAS UTILISER POUR NOUVEAUX DÉVELOPPEMENTS)

| Engine | Fichier | Lignes | Importé par | Action recommandée |
|--------|---------|--------|-------------|-------------------|
| corridor_service.py | services/ | 539 | router.py (legacy) | SUPPRIMER (supercédé par corridor_v7.py) |
| zone_service.py | services/ | ~400 | router.py (legacy) | SUPPRIMER (supercédé par zone_engine_core_v2.py) |
| organic_contour_generator.py | services/ | ~200 | ? | VÉRIFIER puis supprimer (supercédé par organic_zone_generator_v2.py) |
| pipeline_service.py | services/ | ~300 | ? | VÉRIFIER (supercédé par pipeline_v7.py?) |
| hotspot_service.py | services/ | ~200 | ? | VÉRIFIER (intégré dans zone_typology_v7.detect_hotspots?) |


# ═══════════════════════════════════════════════════════════════
# 2. ENGINES FRONTEND (CARTE INTERACTIVE)
# ═══════════════════════════════════════════════════════════════

## 2.1 MAP RENDERING ENGINE — Carte Leaflet
- **Rôle:** Rendu de la carte interactive Leaflet. Couches de tuiles, marqueurs waypoints, polygones zones, polylines corridors.
- **Composants:**
  - `map/MapContent.jsx` (169L) — Composant principal carte (React.memo)
  - `map/MapHelpers.jsx` (167L) — Helpers (LayerStyle, polygone rendering)
- **Hooks:** Aucun hook dédié (géré par MonTerritoireBionicPage via useRef)
- **Flux:** MonTerritoireBionicPage → bionicZones (useMemo) → MapContent (React.memo) → <Polygon>, <Polyline>, <Marker>
- **Dépendances:** react-leaflet, leaflet
- **Risque re-render:** LOW — React.memo protège MapContent. Props stables via useMemo.
- **Tests:** Testing agent iterations 147-149

---

## 2.2 LAYER ENGINE — Gestion des Couches Visuelles
- **Rôle:** Active/désactive les couches de la carte. Gestion des toggles de classification (relief, forêt, dominantes, waypoints).
- **Composants:**
  - `MonTerritoireToolbar.jsx` (503L) — Toggles couches
  - `BionicLegend.jsx` (115L) — Légende des couches
  - `EcoforestryLayers.jsx` (1245L) — Couches WMS écoforestières
  - `HydrographyOverlayLayer.jsx` (107L) — Overlay hydrographie WMS
  - `ExclusionOverlayLayer.jsx` (160L) — Overlay exclusions
  - `NdviOverlayLayer.jsx` — Overlay NDVI
  - `StructureContrastLayer.jsx` — Contraste structure
- **Hook:** `useBionicLayers.js` (119L) — État des couches actives + toggles
- **Flux:** useBionicLayers → layersVisible{} → MonTerritoireBionicPage → bionicZones (filtre useMemo) → MapContent
- **Dépendances:** react-leaflet TileLayer, WMSTileLayer
- **Risque re-render:** LOW — layersVisible change seulement sur interaction utilisateur
- **Tests:** Testing agent (toggles testés)

---

## 2.3 SPLIT VIEW ENGINE — Comparaison Côte à Côte
- **Rôle:** Mode de comparaison de deux cartes synchronisées, chacune avec sa propre saison biologique.
- **Composants:**
  - `map/SplitViewContainer.jsx` (247L) — Container Split View (2 SeasonMaps + divider VS)
- **Hooks:**
  - `useSplitViewSync.js` (78L) — Synchronisation zoom/pan entre les 2 cartes
  - `useSplitViewZones.js` (82L) — Chargement zones pour carte droite (cache key stabilisé)
- **Flux:** splitViewEnabled → SplitViewContainer → [SeasonMap left (saison A)] [SeasonMap right (saison B)] → useSplitViewSync (zoom/pan sync)
- **Dépendances:** react-leaflet, BionicZoneService
- **Risque re-render:** LOW — splitCacheKey stabilisé via useMemo (V8.2 P0 fix)
- **Tests:** iteration_147 (17/17), iteration_149

---

## 2.4 SEASON VISUAL ENGINE — Sélecteur de Saisons Biologiques
- **Rôle:** Interface pour sélectionner la saison biologique. Affecte les données envoyées au backend et le scoring des zones.
- **Composants:**
  - `ui/BiologicalSeasonSelector.jsx` (60L) — Sélecteur avec icônes Lucide, indicateur saison actuelle (dot pulsant)
- **Config:** `config/biologicalSeasons.js` (167L) — Définition des 5 saisons (pre_rut, rut, post_rut, winter, spring) avec mois, couleurs, descriptions
- **Flux:** BiologicalSeasonSelector → onSeasonChange → selectedBiologicalSeason (state) → useZoneOrchestrator (cacheKey) → backend (biological_season param)
- **Dépendances:** lucide-react (icons)
- **Risque re-render:** AUCUN — React.memo
- **Tests:** iteration_149 (5 boutons testés)

---

## 2.5 TREE COLOR ENGINE — Filtres CSS Carte
- **Rôle:** Ajuste l'esthétique des tuiles cartographiques via des filtres CSS. Améliore le contraste des zones forestières.
- **Implémentation:** Filtre CSS inline sur le container `.leaflet-container`
- **Code:** `MonTerritoireBionicPage.jsx` — `style={{ filter: 'saturate(1.1) sepia(0.08) brightness(0.92)' }}`
- **Flux:** Statique — appliqué au montage
- **Dépendances:** AUCUNE
- **Risque re-render:** AUCUN — style statique
- **Tests:** Visuel

---

## 2.6 WAYPOINT ENGINE — Gestion des Points d'Intérêt
- **Rôle:** CRUD complet des waypoints. Sélection d'un waypoint comme cible d'analyse. Placement sur carte via clic. Menu contextuel.
- **Composants:**
  - `WaypointUnifiedPanel.jsx` — Panel unifié waypoints
  - `WaypointContextMenu.jsx` — Menu clic droit
  - `MonTerritoireToolbar.jsx` — Bouton "+ Waypoint"
- **Hook:** `useWaypointActions.js` (188L)
  - `handleAddWaypointFromDialog()` — Ajout + sélection automatique
  - `selectWaypointAsTarget()` — Sélection pour analyse
  - `handleDeleteWaypoint()` — Suppression
- **Flux:** User click → useWaypointActions → addWaypoint (useUserData) → setSelectedWaypointForZones → useZoneOrchestrator (startTransition) → backend
- **Dépendances:** useUserData (persistance), useZoneOrchestrator (analyse)
- **Risque re-render:** LOW — startTransition (V8.2 P0) dépriorise les loading states
- **Tests:** Testing agent (dropdown, ajout testé)

---

## 2.7 ZONE ORCHESTRATOR ENGINE — Pipeline Frontend
- **Rôle:** Orchestre le flux complet de récupération des zones: Cache IndexedDB → Backend API → Affichage. Gestion des états du pipeline (loading, success, empty, error, timeout).
- **Hook:** `useZoneOrchestrator.js` (194L)
- **Flux:**
  1. `cacheKey` change (waypoint + species + season) →
  2. useEffect déclenché →
  3. `getCached(cacheKey)` — check IndexedDB (<100ms) →
  4. `startTransition` → `setIsLoading(true)` (non-bloquant) →
  5. `generateWaypointZonesV5()` — appel backend →
  6. `setZonesData(result)` → `setCached(cacheKey, result)` →
  7. Rendu via useMemo chains
- **Dépendances:** useZoneCache, BionicZoneService, biologicalSeasons config
- **Risque re-render:** LOW — startTransition + console.log supprimés (V8.2 P0)
- **Tests:** iteration_148, iteration_149

---

## 2.8 ZONE CACHE ENGINE — IndexedDB Persistant
- **Rôle:** Cache persistant cross-sessions via IndexedDB (idb-keyval). Clé déterministe par waypoint + species + season.
- **Hook:** `useZoneCache.js` (107L) → `getCached()`, `setCached()`, `clearCache()`
- **Flux:** useZoneOrchestrator → useZoneCache → idb-keyval → IndexedDB
- **Dépendances:** idb-keyval
- **Temps moyen:** <100ms (lecture/écriture)
- **Risque re-render:** AUCUN — pas de state React
- **Tests:** iteration_148 (cache hit testé)

---

## 2.9 WEATHER DISPLAY ENGINE — Affichage Météo
- **Rôle:** Récupère et affiche les données météo en temps réel. Polling périodique.
- **Hook:** `useBionicWeather.js` (180L) — Fetch /weather/full avec polling
- **Composant:** `SeasonalConditionsWidget.jsx` (213L) — Widget conditions
- **Core:** `core/bionic/bionicWeatherEngine.js` (420L) — Calculs météo frontend
- **Flux:** useBionicWeather → fetch /api/v1/weather/full → weatherData state → SeasonalConditionsWidget
- **Dépendances:** weather_engine backend
- **Risque re-render:** LOW — données changent seulement au polling interval
- **Tests:** Partiel

---

## 2.10 WIND FLOW ENGINE — Animation Vent (V8.3 PRÉVU)
- **Rôle:** Layer visuel avec particules animées montrant la direction/intensité du vent.
- **Composant:** `WindFlowLayer.jsx` (280L) — Existe mais implémentation basique
- **Statut:** SQUELETTE — À implémenter pleinement en V8.3
- **Tests:** AUCUN

---

## 2.11 CORRIDOR DISPLAY ENGINE — Affichage Corridors
- **Rôle:** Rendu des corridors de déplacement sur la carte. Polylines colorées avec styles par type (mâle/femelle, réel/IA).
- **Composant:** `MovementCorridorsLayer.jsx` (193L) — Layer Leaflet corridors
- **Composant:** `CorridorStatsPanel.jsx` — Statistiques corridors
- **Flux:** bionicZonesData.corridors → MovementCorridorsLayer → <Polyline>
- **Dépendances:** react-leaflet
- **Risque re-render:** LOW — données changent seulement au recalcul
- **Tests:** Testing agent (corridors vérifiés)

---

## 2.12 SCORING DISPLAY ENGINE — Affichage Scores
- **Rôle:** Affiche les scores des zones. Filtre par score minimum. Tooltip au survol.
- **Hook:** `useBionicScoring.js` (166L) — Calculs scores frontend
- **Core:** `core/bionic/bionicScoring.js` (610L) — Logique de scoring complète
- **Composant:** `SmartMapTooltip.jsx` (108L) — Tooltip zone au survol
- **Composant:** `ZoneInfoPanel.jsx` — Panel détails zone
- **Flux:** bionicZones → score filtre (useMemo) → visibleZonesCount → MapContent (polygones filtrés)
- **Risque re-render:** LOW — useMemo protège
- **Tests:** Testing agent (scores vérifiés)

---

## 2.13 GEOLOCATION ENGINE — Position Utilisateur
- **Rôle:** Récupère la position GPS de l'utilisateur. Centrage automatique.
- **Hook:** `useGeolocation.js` (58L) — navigator.geolocation
- **Flux:** useGeolocation → position → mapRef.setView()
- **Dépendances:** Browser Geolocation API
- **Risque re-render:** LOW — position change rarement
- **Tests:** AUCUN spécifique

---

## 2.14 SPATIAL CLIPPING ENGINE — Découpe Visuelle
- **Rôle:** Calcule et applique la bbox d'analyse (2×2 km) côté frontend. Affiche le cadre en pointillés.
- **Hook:** `useSpatialClipping.js` (209L) — Calcul bbox + clip zones client
- **Flux:** selectedWaypointForZones → useSpatialClipping → analysisBbox → clipZonesClient() → allZones (useMemo)
- **Dépendances:** AUCUNE (calcul géométrique pur)
- **Risque re-render:** LOW — recalcule seulement quand waypoint change
- **Tests:** test_spatial_clipping.py (backend)

---

## 2.15 PERFORMANCE ENGINE — Optimisations React
- **Rôle:** Ensemble de patterns React pour minimiser les re-renders.
- **Patterns actifs:**
  - `React.memo` sur MapContent, SidePanelZones, TerritoireHeader, BiologicalSeasonSelector
  - `useMemo` sur rawZones, allZones, bionicZones, visibleZonesCount (console.log supprimés V8.2)
  - `useCallback` sur handleMapMove, handleZoomChange
  - `startTransition` sur setIsLoading, setPipelineState (V8.2 P0)
  - Cache key stabilisé useSplitViewZones (V8.2 P0)
- **Risque re-render global:** LOW après V8.2 P0
- **Tests:** iteration_149 (performance vérifiée)

---

## 2.16 CORE BIONIC MODULES — Logique Métier Frontend

| Module | Fichier | Lignes | Rôle | Utilisé activement? |
|--------|---------|--------|------|-------------------|
| bionicConfig | core/bionic/bionicConfig.js | 251 | Configuration globale (layers, couleurs, seuils) | OUI |
| bionicScoring | core/bionic/bionicScoring.js | 610 | Logique de scoring frontend | OUI (via useBionicScoring) |
| bionicWeatherEngine | core/bionic/bionicWeatherEngine.js | 420 | Calculs météo-chasse | OUI (via useBionicWeather) |
| bionicDataAdapter | core/bionic/bionicDataAdapter.js | 418 | Adaptation données backend→frontend | OUI |
| bionicHybridModel | core/bionic/bionicHybridModel.js | 378 | Modèle hybride (algo+rules) | OUI |
| bionicStrategyEngine | core/bionic/bionicStrategyEngine.js | 496 | Recommandations stratégie de chasse | OUI |
| bionicSpecies | core/bionic/bionicSpecies.js | 162 | Config espèces | OUI |
| speciesConfig | core/bionic/speciesConfig.js | 136 | Config espèces (format alternatif) | DOUBLON POTENTIEL |
| bionicModules | core/bionic/bionicModules.js | 149 | Registry de modules | OUI |


# ═══════════════════════════════════════════════════════════════
# 3. ENGINES TRANSVERSAUX
# ═══════════════════════════════════════════════════════════════

## 3.1 PIPELINE ENGINE (Backend → Frontend)
- **Rôle:** Flux de données end-to-end depuis le clic waypoint jusqu'au rendu carte.
- **Flux complet:**
```
[USER] Click waypoint
  → useWaypointActions.selectWaypointAsTarget()
    → setSelectedWaypointForZones (state)
      → useZoneOrchestrator (cacheKey change)
        → [1] useZoneCache.getCached() (IndexedDB, <100ms)
        → [2] startTransition(setIsLoading) (non-bloquant)
        → [3] BionicZoneService.generateWaypointZonesV5()
              → POST /api/v1/bionic/organic-zones
                → zone_engine_core_v2.generate_organic_zones()
                  → _fetch_exclusions_from_terrain() (Overpass, 5 phases)
                  → behavioral_rasterizer (par couche, 6 threads)
                  → organic_zone_generator_v2 (contours)
                  → pipeline_v7 (exclusion, scoring, merge)
                  → corridor_v7 (A*, terrain-aware)
                ← GeoJSON {features[], corridors[], stats{}}
              ← {zones[], corridors[], stats{}}
        → [4] setZonesData(result), setCached()
          → useMemo chains: rawZones → allZones → bionicZones → visibleZonesCount
            → MapContent (React.memo) → Leaflet render
```

## 3.2 CACHE ENGINE (Multi-Niveau)
- **Niveau 1:** Backend mémoire (zone_engine_core_v2._zone_cache, TTL 15min)
- **Niveau 2:** Backend MongoDB (overpass_cache_r5, TTL 1h) + fichier (7j)
- **Niveau 3:** Frontend mémoire (BionicZoneService._cache, 1 entrée)
- **Niveau 4:** Frontend IndexedDB (useZoneCache, persistant cross-sessions)
- **Flux cache hit:** L4 → instant | L3 → instant | L2 → ~0.5s | L1 → ~0.5s

## 3.3 ERROR HANDLING ENGINE
- **Backend:** Try/catch dans zone_engine_core_v2, pipeline_v7. Logging structuré.
- **Frontend:** Try/catch dans useZoneOrchestrator. PipelineState: loading | success | empty | error | timeout.
- **Fallback states:** zeroZonesReason: overpass_unavailable | all_filtered_by_exclusions | timeout | backend_error

## 3.4 FALLBACK ENGINE (Mode Dégradé V8.2)
- **Rôle:** Pipeline 5 phases pour l'Overpass API.
  1. Cache frais (MongoDB + fichier)
  2. Overpass API (12s fast-fail, 1 essai)
  3. Cache expiré (MongoDB + fichier, données stale)
  4. Retry Overpass (2e essai après 1s)
  5. Dégradation gracieuse (exclusions=[], zones générées sans filtrage, flag exclusion_degraded=true)
- **Point d'entrée:** zone_engine_core_v2.py → _fetch_exclusions_from_terrain()
- **Tests:** test_v8_2_resilience_pipeline.py, iteration_148


# ═══════════════════════════════════════════════════════════════
# 4. SYNTHÈSE — DOUBLONS, SURCHARGES, RECOMMANDATIONS
# ═══════════════════════════════════════════════════════════════

## 4.1 Doublons Confirmés

| Doublon | Fichiers | Sévérité | Action |
|---------|----------|----------|--------|
| Corridor Legacy | corridor_service.py vs corridor_v7.py | HIGH | SUPPRIMER corridor_service.py |
| Zone Legacy | zone_service.py vs zone_engine_core_v2.py | HIGH | SUPPRIMER zone_service.py |
| Weather Double | weather_service.py (P0) vs weather_engine/v1 | HIGH | CONSOLIDER en weather_engine/v1 unique |
| Species Config | bionicSpecies.js vs speciesConfig.js | MEDIUM | CONSOLIDER en 1 fichier |
| Scoring Triple | zone_typology_v7 vs unified_scoring vs dynamic_scoring vs multifactor | MEDIUM | Zone_typology_v7 est le actif pour le pipeline. Les autres servent d'autres endpoints. À clarifier. |
| Contour Generator | organic_contour_generator.py vs organic_zone_generator_v2.py | LOW | VÉRIFIER si le V1 est encore utilisé |

## 4.2 Surcharges Performance

| Zone | Impact | Détail | Fix |
|------|--------|--------|-----|
| Overpass API | CRITIQUE | 80% du temps pipeline (12-30s) | Pré-chargement, cache étendu |
| SRTM DEM | MEDIUM | 2s par appel non-caché | Cache TTL étendu |
| EcoforestryLayers | LOW | 1245 lignes, WMS potentiellement lent | Lazy loading |

## 4.3 Couverture Tests

| Catégorie | Fichiers Tests | Couverture |
|-----------|---------------|------------|
| Zone Engine Core V2 | 5+ fichiers | BONNE |
| Corridor V7 | 3 fichiers | BONNE |
| Exclusion V6 | 4 fichiers | BONNE |
| Weather Engine | 1 fichier (partiel) | FAIBLE |
| Windfield | 1 fichier | OK |
| SSE Engine | 1 fichier | OK |
| Frontend (testing agent) | iterations 147-149 | BONNE |
| Scoring Engines | 3 fichiers | MOYENNE |

## 4.4 Architecture Compliance BIONIC™

| Critère | Statut | Détail |
|---------|--------|--------|
| 100% Modulaire | ✅ | Chaque engine dans son propre fichier |
| Déterministe | ✅ | Mêmes inputs → mêmes outputs (graine Simplex fixe) |
| Zéro recalcul visuel | ✅ | Preview supprimé, State Locking actif |
| Zéro code mort | ⚠️ | 5 fichiers legacy encore présents |
| Extensible | ✅ | V8.2/V8.3 prêts à s'intégrer |
| Testable | ✅ | 110+ fichiers de tests |
