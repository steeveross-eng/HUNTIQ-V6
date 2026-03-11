# LISTE COMPLETE DES ENGINES — CARTE INTERACTIVE BIONIC™
## Version: V8.2 | Date: 2026-03-10 | 73 Engines Audites

---

# ══════════════════════════════════════════════════════════════════
# 1. BACKEND — PIPELINE V7/V8 (19 engines, 8,280L)
# ══════════════════════════════════════════════════════════════════

## #01 — Zone Engine Core V2
| Champ | Detail |
|-------|--------|
| Fichier | `services/zone_engine_core_v2.py` |
| Lignes | 737 |
| Role | Orchestrateur principal du pipeline V7. Coordonne rasterisation, contours, exclusions, corridors, GeoJSON. Thread pool 6 workers. Cache memoire TTL 15min. Pipeline resilience 5 phases V8.2. |
| Point d'entree | `generate_organic_zones(bounds, species, layers, resolution, max_zones, waypoint_center, biological_season)` |
| Input | bounds{N,S,E,W}, species, layers[], resolution, max_zones_per_layer, waypoint_center, biological_season |
| Output | GeoJSON {features[], corridors[], stats{computation_time_ms, exclusion_degraded, ...}, corridor_styles{}, zone_type_config{}} |
| Deps internes | behavioral_rasterizer, organic_zone_generator_v2, zone_visual_layer_v2, zone_penalty_engine, pipeline_v7, corridor_v7, srtm_provider_v7 |
| Deps externes | Overpass API (via terrain_data_router), OpenTopography API |
| Statut | **ACTIF** — Coeur du pipeline |
| Impact carte | CRITIQUE — Genere toutes les zones et corridors affiches |
| Transferable | **OUI** — Engine central, activable tel quel |
| Risques | Overpass timeout (mitige par V8.2 resilience) |

## #02 — Pipeline V7
| Champ | Detail |
|-------|--------|
| Fichier | `services/pipeline_v7.py` |
| Lignes | 412 |
| Role | Pipeline d'enrichissement par couche: Exclusion V6 -> Shape Enhancement -> Scoring V7 -> Hotspot Detection -> Zone Merge. Filtre zones par perimetre waypoint. Gere la saison biologique. |
| Point d'entree | `process_zones_v7(raw_zones, bounds, exclusions, layer_id, species, weather, dem_data, month, biological_season, waypoint_center)` |
| Input | raw_zones[], bounds, exclusions[], layer_id, species, weather, dem_data, month, biological_season, waypoint_center |
| Output | (valid_zones[], rejected_zones[], stats{}) |
| Deps internes | exclusion_engine_v6, zone_typology_v7, zone_shape_v7, species_behavior_v7, terrain_signals_v7, corridor_v7 |
| Deps externes | Aucune |
| Statut | **ACTIF** |
| Impact carte | CRITIQUE — Qualifie chaque zone |
| Transferable | **OUI** — Module autonome |
| Risques | Aucun |

## #03 — Corridor V7
| Champ | Detail |
|-------|--------|
| Fichier | `services/corridor_v7.py` |
| Lignes | 1143 |
| Role | Pathfinding A* terrain-aware. Differencie male/femelle, reel/IA. Lissage Chaikin. Score et confiance. Intersection routes. |
| Point d'entree | Appele via `pipeline_v7.generate_all_corridors_v7()` |
| Input | zones[], exclusions, species, terrain_signals, dem_data, month, waypoint_center |
| Output | corridors[] {coords, score, sex, type, confidence, length_m} |
| Deps internes | trail_cost_grid_v7, species_behavior_v7 |
| Deps externes | Aucune |
| Statut | **ACTIF** |
| Impact carte | HAUTE — Affiche les corridors de deplacement |
| Transferable | **OUI** |
| Risques | Doublon avec corridor_service.py (legacy) |

## #04 — Exclusion Engine V6
| Champ | Detail |
|-------|--------|
| Fichier | `services/exclusion_engine_v6.py` |
| Lignes | 361 |
| Role | Filtrage geometrique Shapely. P0 eau + P1 routes + P2 urbain. Buffers configurables. Calcul intersection ratio. |
| Point d'entree | `process_zones_v6(raw_zones, bounds, exclusions, layer_id, species)` |
| Input | raw_zones[], bounds, exclusions[], layer_id, species |
| Output | (valid_zones[], rejected_zones[], v6_stats{}) |
| Deps internes | exclusion_config_v6 (#05), exclusion_geometry_v6 (#06) |
| Deps externes | Shapely |
| Statut | **ACTIF** |
| Impact carte | HAUTE — Filtre les zones invalides |
| Transferable | **OUI** |
| Risques | Aucun |

## #05 — Exclusion Config V6
| Champ | Detail |
|-------|--------|
| Fichier | `services/exclusion_config_v6.py` |
| Lignes | 132 |
| Role | Configuration des buffers d'exclusion par type (eau: 50m, routes: 30m, urbain: 100m). |
| Point d'entree | `get_buffer_m(exclusion_type, species)` |
| Statut | **ACTIF** — Sous-module de #04 |
| Transferable | **OUI** |

## #06 — Exclusion Geometry V6
| Champ | Detail |
|-------|--------|
| Fichier | `services/exclusion_geometry_v6.py` |
| Lignes | 297 |
| Role | Operations geometriques Shapely: unions, trim, intersection ratio, distance. |
| Point d'entree | `build_exclusion_unions(exclusions)`, `trim_zone(zone, exclusion_union)`, `calculate_intersection_ratio()` |
| Statut | **ACTIF** — Sous-module de #04 |
| Transferable | **OUI** |

## #07 — Zone Typology V7
| Champ | Detail |
|-------|--------|
| Fichier | `services/zone_typology_v7.py` |
| Lignes | 479 |
| Role | Classification multi-criteres des zones. Score global (0-1) avec sous-scores (habitat, terrain, season, behavior, weather). Detection hotspots. |
| Point d'entree | `enrich_zone_v7(zone, layer_id, species, exclusions, weather, month, dem_stats)` |
| Input | zone, layer_id, species, exclusions, weather, month, dem_stats |
| Output | zone enrichie {zone_type, score_global, subscores{}, confidence} |
| Deps internes | species_behavior_v7, terrain_signals_v7 |
| Statut | **ACTIF** |
| Impact carte | HAUTE — Determine couleur/opacite des zones |
| Transferable | **OUI** |
| Risques | Recouvre partiellement les scoring engines (#35-#38) |

## #08 — Species Behavior V7
| Champ | Detail |
|-------|--------|
| Fichier | `services/species_behavior_v7.py` |
| Lignes | 281 |
| Role | Matrices comportementales par espece, saison, sexe. Couts corridor. Modificateurs meteo. |
| Point d'entree | `get_species_needs(species)`, `get_season_modifier(species, month)`, `get_sex_params(species, sex)` |
| Deps externes | Aucune (lookup tables) |
| Statut | **ACTIF** |
| Transferable | **OUI** — Module 100% autonome |

## #09 — SRTM Provider V7 (DEM Engine)
| Champ | Detail |
|-------|--------|
| Fichier | `services/srtm_provider_v7.py` |
| Lignes | 234 |
| Role | Donnees elevation SRTM via OpenTopography API. Cache interne. Fournit altitude, pente, orientation, rugosite. |
| Point d'entree | `fetch_dem_for_pipeline(bounds)` |
| Input | bounds{N,S,E,W} |
| Output | {status, stats{alt_min, alt_max, slope_mean, roughness_mean, pixel_size_m}, data(numpy)} |
| Deps externes | httpx (OpenTopography API) |
| Statut | **ACTIF** |
| Impact carte | MOYENNE — Enrichit scoring terrain |
| Transferable | **OUI** |
| Risques | Doublon partiel avec dem_service.py (#40) |

## #10 — Terrain Signals V7
| Champ | Detail |
|-------|--------|
| Fichier | `services/terrain_signals_v7.py` |
| Lignes | 189 |
| Role | Signaux terrain depuis exclusions: proximite eau, routes, foret, distances. |
| Point d'entree | `extract_terrain_signals_from_exclusions(centroid, exclusions, radius)` |
| Statut | **ACTIF** |
| Transferable | **OUI** |

## #11 — Trail Cost Grid V7
| Champ | Detail |
|-------|--------|
| Fichier | `services/trail_cost_grid_v7.py` |
| Lignes | 441 |
| Role | Grille de couts numpy pour pathfinding A*. Rasterise exclusions (eau=impassable, routes=couteux). |
| Point d'entree | `build_cost_grid(bounds, exclusions, dem_data)` |
| Statut | **ACTIF** |
| Transferable | **OUI** |

## #12 — Behavioral Rasterizer
| Champ | Detail |
|-------|--------|
| Fichier | `services/behavioral_rasterizer.py` |
| Lignes | 293 |
| Role | Rasters comportementaux par couche via bruit Simplex fractal. Graine deterministe. |
| Point d'entree | `generate_layer_raster(bounds, layer_id, species, resolution)` |
| Statut | **ACTIF** |
| Impact carte | HAUTE — Base de toutes les zones |
| Transferable | **OUI** |

## #13 — Organic Zone Generator V2
| Champ | Detail |
|-------|--------|
| Fichier | `services/organic_zone_generator_v2.py` |
| Lignes | 387 |
| Role | Extraction contours Marching Squares + lissage Chaikin + jitter organique. |
| Point d'entree | `extract_contours(grid, bounds, threshold)` |
| Statut | **ACTIF** |
| Transferable | **OUI** |
| Risques | Doublon avec organic_contour_generator.py (#41) |

## #14 — Zone Visual Layer V2
| Champ | Detail |
|-------|--------|
| Fichier | `services/zone_visual_layer_v2.py` |
| Lignes | 143 |
| Role | Conversion zones -> GeoJSON features avec styles (couleur, opacite). |
| Point d'entree | `zones_to_geojson(zones, layer_styles)` |
| Statut | **ACTIF** |
| Transferable | **OUI** |

## #15 — Zone Penalty Engine
| Champ | Detail |
|-------|--------|
| Fichier | `services/zone_penalty_engine.py` |
| Lignes | 228 |
| Role | Penalites de score basees sur proximite aux exclusions. |
| Point d'entree | `calculate_zone_penalty(zone, exclusions, species)` |
| Statut | **ACTIF** |
| Transferable | **OUI** |

## #16 — Zone Shape V7
| Champ | Detail |
|-------|--------|
| Fichier | `services/zone_shape_v7.py` |
| Lignes | 252 |
| Role | Lissage adaptatif, snap berges, fusion zones, validation topologique. |
| Point d'entree | `smooth_zone_adaptive(coords, terrain_roughness)` |
| Statut | **ACTIF** |
| Transferable | **OUI** |

## #17 — Spatial Clipping
| Champ | Detail |
|-------|--------|
| Fichier | `services/spatial_clipping.py` |
| Lignes | 150 |
| Role | Calcul bbox d'analyse (1km2 autour waypoint) et decoupe zones. |
| Point d'entree | `clip_zones(zones, bbox)`, `compute_analysis_bbox(waypoint)` |
| Statut | **ACTIF** |
| Transferable | **OUI** |

## #18 — SSE Engine
| Champ | Detail |
|-------|--------|
| Fichier | `services/sse_engine.py` |
| Lignes | 544 |
| Role | Landcover, microrelief, transitions de lisiere. Rasters avances. |
| Point d'entree | `generate_sse_composite(bounds, species, resolution)` |
| Statut | **ACTIF** |
| Impact carte | BASSE — Layers visuels avances (non-utilise activement dans la carte) |
| Transferable | **PARTIEL** — Necessite integration UI supplementaire |

## #19 — Windfield Service
| Champ | Detail |
|-------|--------|
| Fichier | `services/windfield_service.py` |
| Lignes | 142 |
| Role | Grille vectorielle vent (u,v) pour animation particules. |
| Point d'entree | `generate_windfield(lat, lng, grid_size)`, `fetch_and_generate_windfield(lat, lng, grid_size)` |
| Statut | **ACTIF** (backend pret, frontend V8.3 a terminer) |
| Impact carte | FUTURE — V8.3 |
| Transferable | **OUI** — Pret a l'emploi |


# ══════════════════════════════════════════════════════════════════
# 2. BACKEND — OVERPASS / CACHE (3 engines, 1,815L)
# ══════════════════════════════════════════════════════════════════

## #20 — Terrain Data Router (Overpass Engine)
| Champ | Detail |
|-------|--------|
| Fichier | `routers/terrain_data_router.py` |
| Lignes | 717 |
| Role | Route API + fetch Overpass + cache MongoDB (overpass_cache_r5) + cache fichier (7j). Parse exclusions. |
| Point d'entree | `get_terrain_data(request)` + fonctions internes `_load_cache`, `_load_cache_expired`, `_save_cache`, `_build_overpass_query`, `_parse_overpass` |
| Deps externes | Overpass API (overpass-api.de), MongoDB |
| Statut | **ACTIF** |
| Transferable | **OUI** |

## #21 — OSM Cache Service
| Champ | Detail |
|-------|--------|
| Fichier | `services/osm_cache_service.py` |
| Lignes | 714 |
| Role | Cache en memoire + regions pour donnees OSM. Pre-calcul geometries unifiees. |
| Point d'entree | `get_osm_cache()`, `cache_get_region()`, `cache_put_region()` |
| Statut | **ACTIF** |
| Transferable | **OUI** |
| Risques | Recouvre partiellement terrain_data_router (cache dual) |

## #22 — OSM Extractor V2
| Champ | Detail |
|-------|--------|
| Fichier | `services/osm_extractor_v2.py` |
| Lignes | 384 |
| Role | Extraction batch donnees Overpass. Batch queries multi-types. |
| Point d'entree | `extract_osm_data(bounds, types, detail_level)` |
| Statut | **ACTIF** |
| Transferable | **OUI** |


# ══════════════════════════════════════════════════════════════════
# 3. BACKEND — WEATHER (4 engines, 1,665L)
# ══════════════════════════════════════════════════════════════════

## #23 — Weather Engine V1 External Service
| Champ | Detail |
|-------|--------|
| Fichier | `weather_engine/v1/external_service.py` |
| Lignes | 611 |
| Role | Integration OpenWeatherMap 2.5 API. Cache 30min. Fallback donnees simulees si pas de cle. |
| Point d'entree | `OpenWeatherMapService.get_current()`, `.get_hourly()`, `.get_daily()`, `.get_full()` |
| Deps externes | httpx (OpenWeatherMap API) |
| Statut | **ACTIF** (donnees SIMULEES — pas de cle API) |
| Transferable | **OUI** — Activable avec cle OpenWeatherMap |

## #24 — Weather Engine V1 Service
| Champ | Detail |
|-------|--------|
| Fichier | `weather_engine/v1/service.py` |
| Lignes | 218 |
| Role | Scoring meteo pour la chasse. Analyse pression, humidite, vent, precipitations. |
| Point d'entree | `WeatherService.get_hunting_analysis(weather_data)`, `.calculate_hunting_score()` |
| Statut | **ACTIF** |
| Transferable | **OUI** |

## #25 — Weather Engine V1 Router
| Champ | Detail |
|-------|--------|
| Fichier | `weather_engine/v1/router.py` |
| Lignes | 322 |
| Role | Endpoints API meteo: /current, /hourly, /daily, /full, /analyze, /score, /moon. |
| Statut | **ACTIF** |
| Transferable | **OUI** |

## #26 — Weather Cache Service
| Champ | Detail |
|-------|--------|
| Fichier | `services/weather_cache_service.py` |
| Lignes | 140 |
| Role | Cache MongoDB pour donnees meteo associees aux zones. |
| Point d'entree | `cache_put()`, `cache_get()`, `cache_stats()` |
| Statut | **ACTIF** |
| Transferable | **OUI** |

## #27 — Weather Service P0 (DOUBLON)
| Champ | Detail |
|-------|--------|
| Fichier | `services/weather_service.py` |
| Lignes | 754 |
| Role | Service meteo interne bionic_engine_p0. Modeles Pydantic. Facteurs comportementaux. |
| Statut | **DOUBLON** — Duplique weather_engine/v1 (#23-#25) |
| Transferable | **NON** — A consolider dans weather_engine/v1 |
| Risques | 754L de code duplique |


# ══════════════════════════════════════════════════════════════════
# 4. BACKEND — SCORING (12 engines, 6,434L)
# ══════════════════════════════════════════════════════════════════

## #28 — Zone Typology V7 (Scoring Principal Pipeline)
> Deja documente en #07. C'est le scoring ACTIF dans le pipeline V7.

## #29 — Unified Scoring Service
| Champ | Detail |
|-------|--------|
| Fichier | `services/unified_scoring_service.py` |
| Lignes | 1159 |
| Role | Scoring unifie multi-facteurs. Utilise par waypoint_analysis et heatmap_fusion. |
| Point d'entree | `get_unified_scoring_service()` |
| Importe par | waypoint_analysis_service.py, heatmap_fusion_service.py, waypoint_analysis_router.py |
| Statut | **ACTIF** (endpoints secondaires) |
| Impact carte | BASSE — Utilise par endpoints d'analyse, pas par le pipeline principal |
| Transferable | **PARTIEL** — Utile pour enrichir Mon Territoire avec analyses avancees |
| Risques | Recouvre partiellement zone_typology_v7 |

## #30 — Dynamic Scoring Service
| Champ | Detail |
|-------|--------|
| Fichier | `services/dynamic_scoring_service.py` |
| Lignes | 883 |
| Role | Scoring dynamique avec ponderations ajustables. Utilise par hunt_plan_analyzer. |
| Point d'entree | `get_dynamic_scoring_service()` |
| Importe par | hunt_plan_analyzer_service.py, scoring_router.py |
| Statut | **ACTIF** (endpoints secondaires) |
| Impact carte | BASSE |
| Transferable | **PARTIEL** |

## #31 — Multifactor Scoring Engine
| Champ | Detail |
|-------|--------|
| Fichier | `services/scoring/multifactor_scoring_engine.py` |
| Lignes | 342 |
| Role | Orchestrateur des 8 sous-services de scoring. |
| Statut | **ACTIF** |
| Transferable | **PARTIEL** |

## #32-#39 — Scoring Sub-Services

| # | Fichier | Lignes | Role | Statut | Transferable |
|---|---------|--------|------|--------|-------------|
| 32 | `scoring/base_score_service.py` | 544 | Classe de base pour les scores | ACTIF | OUI |
| 33 | `scoring/score_habitat_service.py` | 259 | Score habitat (foret, eau, couvert) | ACTIF | OUI |
| 34 | `scoring/score_weather_service.py` | 287 | Score meteo (pression, vent, pluie) | ACTIF | OUI |
| 35 | `scoring/score_behavior_service.py` | 297 | Score comportemental (rut, repos, alimentation) | ACTIF | OUI |
| 36 | `scoring/score_density_service.py` | 331 | Score densite gibier | ACTIF | OUI |
| 37 | `scoring/score_mobility_service.py` | 445 | Score mobilite (corridors, deplacements) | ACTIF | OUI |
| 38 | `scoring/score_pressure_service.py` | 274 | Score pression de chasse | ACTIF | OUI |
| 39 | `scoring/score_probability_service.py` | 191 | Score probabilite observation | ACTIF | OUI |
| 40 | `scoring/score_risk_service.py` | 397 | Score risques (securite, legalite) | ACTIF | OUI |
| 41 | `scoring/score_multifactor_service.py` | 385 | Combinaison multi-facteurs | ACTIF | OUI |

## #42 — Scoring Zone Integration (V5 Legacy)
| Champ | Detail |
|-------|--------|
| Fichier | `services/scoring_zone_integration.py` |
| Lignes | 183 |
| Role | Enrichit GeoJSON avec scores V5. Feature flag: desactive si V7 actif. |
| Statut | **LEGACY** — Feature flag |
| Transferable | **NON** — Supercede par zone_typology_v7 |


# ══════════════════════════════════════════════════════════════════
# 5. BACKEND — SERVICES COMPLEMENTAIRES (8 engines, 5,714L)
# ══════════════════════════════════════════════════════════════════

## #43 — Hotspot Service V3
| Champ | Detail |
|-------|--------|
| Fichier | `services/hotspot_service.py` |
| Lignes | 511 |
| Role | Generation hotspots organiques via Marching Squares + Chaikin. Utilise par hunt_plan_analyzer. |
| Importe par | hunt_plan_analyzer_service.py, router.py (legacy) |
| Statut | **ACTIF** (endpoint secondaire /hotspots) |
| Impact carte | BASSE — Pas dans le pipeline principal |
| Transferable | **PARTIEL** — Pourrait enrichir la carte avec des hotspots |

## #44 — Hunt Plan Analyzer Service
| Champ | Detail |
|-------|--------|
| Fichier | `services/hunt_plan_analyzer_service.py` |
| Lignes | 708 |
| Role | Orchestrateur d'analyse plan de chasse. Combine hotspots + meteo + scoring dynamique. |
| Statut | **ACTIF** (endpoint /hunt-plan) |
| Impact carte | BASSE |
| Transferable | **PARTIEL** — Enrichissement avance pour Mon Territoire |

## #45 — Hunt Plan Analyzer (Version 2)
| Champ | Detail |
|-------|--------|
| Fichier | `services/hunt_plan_analyzer.py` |
| Lignes | 917 |
| Role | Version alternative/etendue du hunt plan analyzer. |
| Statut | **ACTIF** |
| Transferable | **PARTIEL** |
| Risques | Doublon potentiel avec #44 |

## #46 — Waypoint Analysis Service
| Champ | Detail |
|-------|--------|
| Fichier | `services/waypoint_analysis_service.py` |
| Lignes | 951 |
| Role | Analyse complete centree sur le waypoint. Integre SCORE_FINAL, Heatmap Unifiee, tous sous-scores. |
| Statut | **ACTIF** (endpoint /waypoint-analysis) |
| Impact carte | MOYENNE — Enrichit le panneau lateral |
| Transferable | **OUI** — Compatible Mon Territoire |

## #47 — Heatmap Fusion Service
| Champ | Detail |
|-------|--------|
| Fichier | `services/heatmap_fusion_service.py` |
| Lignes | 681 |
| Role | Fusion WQS (structure) + SCORE_FINAL (dynamique) pour heatmap unifiee. |
| Statut | **ACTIF** |
| Impact carte | MOYENNE — Heatmap overlay |
| Transferable | **PARTIEL** — Necessite UI heatmap |

## #48 — Layer Aggregator Service
| Champ | Detail |
|-------|--------|
| Fichier | `services/layer_aggregator_service.py` |
| Lignes | 1268 |
| Role | Agregation multi-couches. Combine tous les layers pour scoring final. |
| Statut | **ACTIF** |
| Transferable | **PARTIEL** |

## #49 — Seasonal Conditions Service
| Champ | Detail |
|-------|--------|
| Fichier | `services/seasonal_conditions_service.py` |
| Lignes | 327 |
| Role | Conditions saisonnieres enrichies (meteo + lune + comportement). |
| Statut | **ACTIF** (endpoint /seasonal-conditions) |
| Impact carte | MOYENNE — Widget conditions |
| Transferable | **OUI** |

## #50 — DEM Service
| Champ | Detail |
|-------|--------|
| Fichier | `services/dem_service.py` |
| Lignes | 170 |
| Role | Service DEM complementaire. Endpoints specifiques DEM (ombres, pentes). |
| Statut | **ACTIF** |
| Transferable | **OUI** |
| Risques | Recouvre partiellement srtm_provider_v7 (#09) |


# ══════════════════════════════════════════════════════════════════
# 6. BACKEND — LEGACY / A SUPPRIMER (7 engines, 3,480L)
# ══════════════════════════════════════════════════════════════════

| # | Fichier | Lignes | Role Original | Supercede par | Importe par | Action |
|---|---------|--------|---------------|---------------|-------------|--------|
| 51 | `corridor_service.py` | 488 | Corridors Phase G | corridor_v7.py (#03) | router.py (legacy) | **SUPPRIMER** |
| 52 | `zone_service.py` | 368 | Zones Phase G | zone_engine_core_v2.py (#01) | router.py (legacy) | **SUPPRIMER** |
| 53 | `weather_service.py` | 754 | Meteo P0 | weather_engine/v1 (#23-25) | pipeline interne | **CONSOLIDER** |
| 54 | `organic_contour_generator.py` | 804 | Contours V1 | organic_zone_generator_v2 (#13) | hotspot_service, layer_aggregator | **VERIFIER** |
| 55 | `pipeline_service.py` | 247 | Pipeline Phase G | pipeline_v7.py (#02) | ml_feature_builder, comparison_service | **VERIFIER** |
| 56 | `comparison_service.py` | 153 | Comparaison | Aucun remplacement direct | pipeline_service | **VERIFIER** |
| 57 | `contour_generator.py` | 618 | Contours V0 | organic_zone_generator_v2 (#13) | corridor_service | **SUPPRIMER** |


# ══════════════════════════════════════════════════════════════════
# 7. FRONTEND — CARTE INTERACTIVE (32 composants, 10,818L)
# ══════════════════════════════════════════════════════════════════

## HOOKS (Logique Metier)

| # | Fichier | Lignes | Role | Statut | Impact Carte | Transferable |
|---|---------|--------|------|--------|-------------|-------------|
| 58 | `useZoneOrchestrator.js` | 194 | Pipeline frontend: Cache -> Backend -> Affichage. startTransition V8.2. | ACTIF | CRITIQUE | OUI |
| 59 | `useWaypointActions.js` | 188 | CRUD waypoints + selection cible analyse | ACTIF | HAUTE | OUI |
| 60 | `useZoneCache.js` | 107 | Cache IndexedDB persistant (idb-keyval) | ACTIF | HAUTE | OUI |
| 61 | `useSplitViewSync.js` | 78 | Synchronisation zoom/pan 2 cartes | ACTIF | HAUTE (SplitView) | OUI |
| 62 | `useSplitViewZones.js` | 82 | Chargement zones carte droite (cache key stable) | ACTIF | HAUTE (SplitView) | OUI |
| 63 | `useBionicWeather.js` | 180 | Donnees meteo live avec polling | ACTIF | MOYENNE | OUI |
| 64 | `useBionicLayers.js` | 119 | Gestion couches actives + toggles | ACTIF | HAUTE | OUI |
| 65 | `useBionicScoring.js` | 166 | Calculs scores frontend | ACTIF | MOYENNE | OUI |
| 66 | `useSpatialClipping.js` | 209 | Calcul bbox + clip zones client | ACTIF | HAUTE | OUI |
| 67 | `useGeolocation.js` | 58 | Position GPS utilisateur | ACTIF | BASSE | OUI |
| 68 | `useMapType.js` | ~40 | Toggle type carte (satellite/terrain) | ACTIF | BASSE | OUI |
| 69 | `useUserData.js` | ~300 | Persistance waypoints, prefs | ACTIF | HAUTE | OUI |
| 70 | `useLiveTracking.js` | ~150 | Tracking GPS live | ACTIF | BASSE | OUI |
| 71 | `useSharing.js` | ~100 | Partage positions groupe | ACTIF | BASSE | OUI |

## COMPOSANTS CARTE

| # | Fichier | Lignes | Role | Statut | Impact Carte | Transferable |
|---|---------|--------|------|--------|-------------|-------------|
| 72 | `MonTerritoireBionicPage.jsx` | 1153 | Page principale, orchestration | ACTIF | CRITIQUE | OUI |
| 73 | `map/MapContent.jsx` | 169 | Carte Leaflet + layers (React.memo) | ACTIF | CRITIQUE | OUI |
| 74 | `map/SplitViewContainer.jsx` | 247 | Mode Split View 2 cartes | ACTIF | HAUTE | OUI |
| 75 | `map/MapHelpers.jsx` | 167 | Utilitaires carte | ACTIF | HAUTE | OUI |
| 76 | `MonTerritoireToolbar.jsx` | 503 | Barre outils complete | ACTIF | HAUTE | OUI |
| 77 | `EcoforestryLayers.jsx` | 1245 | Couches WMS ecoforestiere | ACTIF | HAUTE | OUI |
| 78 | `MovementCorridorsLayer.jsx` | 193 | Affichage corridors V7 | ACTIF | HAUTE | OUI |
| 79 | `HydrographyOverlayLayer.jsx` | 107 | Overlay hydrographie WMS | ACTIF | MOYENNE | OUI |
| 80 | `ExclusionOverlayLayer.jsx` | 160 | Overlay exclusions | ACTIF | MOYENNE | OUI |
| 81 | `WindFlowLayer.jsx` | 280 | Animation vent (squelette V8.3) | EXPERIMENTAL | FUTURE | OUI |
| 82 | `BionicLegend.jsx` | 115 | Legende zones | ACTIF | BASSE | OUI |
| 83 | `SeasonalConditionsWidget.jsx` | 213 | Widget conditions meteo | ACTIF | MOYENNE | OUI |
| 84 | `SmartMapTooltip.jsx` | 108 | Tooltip zone au survol | ACTIF | MOYENNE | OUI |
| 85 | `CorridorStatsPanel.jsx` | 162 | Stats corridors panel | ACTIF | MOYENNE | OUI |
| 86 | `WaypointUnifiedPanel.jsx` | 409 | Panel waypoints | ACTIF | HAUTE | OUI |
| 87 | `WaypointContextMenu.jsx` | 153 | Menu contextuel waypoint | ACTIF | MOYENNE | OUI |
| 88 | `ZoneInfoPanel.jsx` | 161 | Panel details zone | ACTIF | MOYENNE | OUI |
| 89 | `ZoneFavorites.jsx` | 685 | Gestion favoris zones | ACTIF | BASSE | OUI |
| 90 | `BionicMicroZones.jsx` | 449 | Micro-zones visualisation | ACTIF | BASSE | PARTIEL |
| 91 | `CursorBionicLayer.jsx` | 239 | Curseur enrichi sur carte | ACTIF | BASSE | OUI |
| 92 | `NdviOverlayLayer.jsx` | 216 | Overlay NDVI | ACTIF | BASSE | OUI |
| 93 | `StructureContrastLayer.jsx` | 228 | Couche contraste structure | ACTIF | BASSE | OUI |
| 94 | `RoutePlannerLayer.jsx` | 199 | Planificateur itineraire | ACTIF | BASSE | OUI |
| 95 | `RouteReplayLayer.jsx` | 425 | Replay parcours GPS | ACTIF | BASSE | OUI |
| 96 | `GroupDashboard.jsx` | 649 | Dashboard groupe | ACTIF | BASSE | OUI |
| 97 | `ShareComponents.jsx` | 451 | Composants partage | ACTIF | BASSE | OUI |

## UI EXTRAITS (IM1/IM1.2)

| # | Fichier | Lignes | Role | Transferable |
|---|---------|--------|------|-------------|
| 98 | `ui/TerritoireHeader.jsx` | 53 | Header page (React.memo) | OUI |
| 99 | `ui/TerritoireDialogs.jsx` | 198 | Modales et dialogs | OUI |
| 100 | `ui/SidePanelZones.jsx` | 98 | Panel lateral zones (React.memo) | OUI |
| 101 | `ui/BiologicalSeasonSelector.jsx` | 60 | Selecteur saison V8.2 | OUI |

## SERVICES FRONTEND

| # | Fichier | Lignes | Role | Transferable |
|---|---------|--------|------|-------------|
| 102 | `services/BionicZoneService.js` | 247 | Interface backend zones | OUI |
| 103 | `services/WaypointScoringService.js` | 124 | Scoring waypoints | OUI |

## CORE BIONIC (Logique Metier)

| # | Fichier | Lignes | Role | Statut | Transferable |
|---|---------|--------|------|--------|-------------|
| 104 | `core/bionic/bionicConfig.js` | 251 | Config globale | ACTIF | OUI |
| 105 | `core/bionic/bionicScoring.js` | 610 | Logique scoring frontend | ACTIF | OUI |
| 106 | `core/bionic/bionicWeatherEngine.js` | 420 | Calculs meteo-chasse | ACTIF | OUI |
| 107 | `core/bionic/bionicDataAdapter.js` | 418 | Adaptation donnees | ACTIF | OUI |
| 108 | `core/bionic/bionicHybridModel.js` | 378 | Modele hybride | ACTIF | OUI |
| 109 | `core/bionic/bionicStrategyEngine.js` | 496 | Strategie chasse | ACTIF | OUI |
| 110 | `core/bionic/bionicSpecies.js` | 162 | Config especes | ACTIF | OUI |
| 111 | `core/bionic/speciesConfig.js` | 136 | Config especes (alt) | DOUBLON | NON — Fusionner avec #110 |
| 112 | `core/bionic/bionicModules.js` | 149 | Registry modules | ACTIF | OUI |
| 113 | `config/biologicalSeasons.js` | 167 | 5 saisons biologiques | ACTIF | OUI |


# ══════════════════════════════════════════════════════════════════
# 8. ENGINES TRANSVERSAUX
# ══════════════════════════════════════════════════════════════════

## Cache Engine (Multi-Niveau)
| Niveau | Composant | TTL | Persistant |
|--------|-----------|-----|-----------|
| L1 | Backend memoire (_zone_cache) | 15min | NON |
| L2 | Backend MongoDB (overpass_cache_r5) | 1h | OUI |
| L3 | Backend fichier (osm_cache/) | 7j | OUI |
| L4 | Frontend memoire (BionicZoneService) | Session | NON |
| L5 | Frontend IndexedDB (useZoneCache) | Permanent | OUI |

## Fallback Engine V8.2 (Resilience Overpass)
- Phase 1: Cache frais (MongoDB + fichier)
- Phase 2: Overpass API (12s fast-fail)
- Phase 3: Cache expire (stale data)
- Phase 4: Retry Overpass (2e essai)
- Phase 5: Degradation gracieuse (exclusions=[], flag exclusion_degraded)

## Error Handling Engine
- Backend: pipelineState = loading | success | empty | error | timeout
- Frontend: zeroZonesReason = overpass_unavailable | all_filtered | timeout | backend_error


# ══════════════════════════════════════════════════════════════════
# 9. SYNTHESE TRANSFERABILITE
# ══════════════════════════════════════════════════════════════════

## Engines Activables Immediatement dans Mon Territoire (OUI)

| # | Engine | Conditions | Tests Requis |
|---|--------|-----------|-------------|
| 01 | Zone Engine Core V2 | Aucune | test_v7_engine.py |
| 02 | Pipeline V7 | Aucune | test_passe2_corridors.py |
| 03 | Corridor V7 | Aucune | test_corridors_v7.py |
| 04-06 | Exclusion Engine V6 | Aucune | test_exclusions_v1.py |
| 07 | Zone Typology V7 | Aucune | test_v7_engine.py |
| 08 | Species Behavior V7 | Aucune | test_v8_1_biological_seasons.py |
| 09 | SRTM Provider V7 | OpenTopography API | test_srtm_integration.py |
| 10-16 | Terrain/Shape/Visual/Penalty | Aucune | Integres |
| 19 | Windfield Service | Aucune | test_windfield.py |
| 20-22 | Overpass/Cache | Overpass API, MongoDB | test_overpass_cache_r5.py |
| 23-26 | Weather Engine V1 | Cle OpenWeatherMap | test_weather.py |
| 46 | Waypoint Analysis | Aucune | test_waypoint_analysis.py |
| 49 | Seasonal Conditions | Aucune | Aucun specifique |
| 58-71 | Hooks Frontend | Aucune | Testing agent iterations |
| 72-101 | Composants Carte | Aucune | Testing agent iterations |

**Total: 62 engines activables immediatement**

## Engines Necessitant Adaptation (PARTIEL)

| # | Engine | Adaptation Requise | Effort |
|---|--------|--------------------|--------|
| 18 | SSE Engine | Ajouter UI pour layers landcover/microrelief | MOYEN |
| 29 | Unified Scoring | Connecter au panneau Mon Territoire | FAIBLE |
| 30 | Dynamic Scoring | Connecter au plan de chasse | FAIBLE |
| 31-41 | Scoring Sub-Services | Integrer dans scoring panel | MOYEN |
| 43 | Hotspot Service | Ajouter layer hotspots sur carte | MOYEN |
| 44-45 | Hunt Plan Analyzer | Ajouter panel plan de chasse | MOYEN |
| 47 | Heatmap Fusion | Ajouter overlay heatmap | MOYEN |
| 48 | Layer Aggregator | Connecter au pipeline | FAIBLE |
| 90 | BionicMicroZones | Finaliser visualisation | FAIBLE |

**Total: 13 engines necessitant adaptation**

## Engines a Supprimer (NON)

| # | Engine | Raison |
|---|--------|--------|
| 27 | weather_service.py (P0) | Doublon weather_engine/v1 |
| 42 | scoring_zone_integration.py | Supercede par zone_typology_v7 |
| 51 | corridor_service.py | Supercede par corridor_v7 |
| 52 | zone_service.py | Supercede par zone_engine_core_v2 |
| 54 | organic_contour_generator.py | Supercede par organic_zone_generator_v2 |
| 55 | pipeline_service.py | Supercede par pipeline_v7 |
| 57 | contour_generator.py | Supercede par organic_zone_generator_v2 |
| 111 | speciesConfig.js | Doublon bionicSpecies.js |

**Total: 8 engines a supprimer (3,677L de code mort)**


# ══════════════════════════════════════════════════════════════════
# 10. PLAN D'INTEGRATION PROGRESSIF
# ══════════════════════════════════════════════════════════════════

## Phase 1 — Nettoyage (P0, 0 risque)
1. Supprimer corridor_service.py, zone_service.py, contour_generator.py
2. Consolider weather_service.py dans weather_engine/v1
3. Fusionner speciesConfig.js dans bionicSpecies.js
4. Supprimer scoring_zone_integration.py (feature flag deja off)
→ Resultat: -3,677 lignes de code mort

## Phase 2 — V8.2 Meteo (P1)
1. Activer cle OpenWeatherMap dans weather_engine/v1
2. Enrichir widget meteo frontend (pression, UV, lune)
3. Connecter scoring meteo au pipeline de zones

## Phase 3 — V8.3 Vent (P2)
1. Activer windfield_service backend
2. Implementer Canvas 2D dans WindFlowLayer.jsx
3. Toggle ON/OFF, responsive mobile

## Phase 4 — Enrichissement Avance (P2)
1. Activer waypoint_analysis dans Mon Territoire
2. Ajouter hotspots overlay
3. Heatmap fusion overlay
4. SSE landcover layers
