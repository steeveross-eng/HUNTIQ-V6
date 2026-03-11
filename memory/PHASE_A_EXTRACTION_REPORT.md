# PHASE A — RAPPORT D'EXTRACTION MILITAIRE
## Migration 1000% PROOF — Carte INTERACTIVE → MON TERRITOIRE
### Date: 10 mars 2026

---

## 1. ENGINES CANONIQUES V7 (À MIGRER)

Les 7 engines canoniques et leurs fichiers sources. **Statut d'intégration dans MON TERRITOIRE** :

### 1.1 zone_typology_v7
- **Fichier:** `modules/bionic_engine_p0/services/zone_typology_v7.py` (480 lignes)
- **Rôle:** Classification des zones (feed, rest, rut, heat_ref, hunt_ref, corridor, mixed)
- **Dépendances:** species_behavior_v7.py
- **Intégré dans MON TERRITOIRE:** OUI (via pipeline_v7.py)
- **Statut:** CANONIQUE, ACTIF

### 1.2 zone_exclusion_engine
- **Fichiers:**
  - `services/exclusion_engine_v6.py` (362 lignes) — Moteur principal
  - `services/exclusion_geometry_v6.py` (298 lignes) — Géométrie Shapely (WATER FIX appliqué)
  - `services/exclusion_config_v6.py` (133 lignes) — Configuration seuils/buffers
- **Rôle:** Exclusion des zones invalides (eau, urbain, routes, infrastructure)
- **Dépendances:** shapely, Overpass API, terrain_data_router.py
- **Intégré dans MON TERRITOIRE:** OUI (via pipeline_v7.py → process_zones_v6)
- **Statut:** CANONIQUE, ACTIF, BCE-CERTIFIÉ (water fix)

### 1.3 zone_merge_engine
- **Fichiers:**
  - `services/zone_engine_core_v2.py` (790 lignes) — Moteur central de génération
  - `services/zone_shape_v7.py` — Formes/lissage des zones
  - `services/organic_zone_generator_v2.py` — Générateur organique
  - `services/organic_contour_generator.py` — Extraction de contours
  - `services/contour_generator.py` — Générateur de contours base
- **Rôle:** Génération, fusion et lissage des polygones de zones
- **Intégré dans MON TERRITOIRE:** OUI (point d'entrée principal)
- **Statut:** CANONIQUE, ACTIF

### 1.4 corridor_engine_v7
- **Fichiers:**
  - `services/corridor_v7.py` — Moteur de corridors V7
  - `services/corridor_service.py` — Service de corridors
  - `services/trail_cost_grid_v7.py` — Grille de coût de déplacement
- **Rôle:** Génération des corridors de déplacement faunique
- **Dépendances:** srtm_provider_v7, scipy
- **Intégré dans MON TERRITOIRE:** OUI (appelé depuis zone_engine_core_v2.py)
- **Statut:** CANONIQUE, ACTIF

### 1.5 corridor_scoring_engine
- **Fichier:** `services/scoring_zone_integration.py` — Intégration scoring/zones/corridors
- **Rôle:** Scoring des corridors, intégration zone-corridor
- **Intégré dans MON TERRITOIRE:** OUI
- **Statut:** CANONIQUE, ACTIF

### 1.6 scoring_engine_v7
- **Fichiers:**
  - `services/scoring/` — Répertoire complet (10 modules de scoring)
    - base_score_service.py
    - multifactor_scoring_engine.py
    - score_behavior_service.py
    - score_density_service.py
    - score_habitat_service.py
    - score_mobility_service.py
    - score_multifactor_service.py
    - score_pressure_service.py
    - score_probability_service.py
    - score_risk_service.py
    - score_weather_service.py
  - `services/unified_scoring_service.py` — Service unifié
  - `services/dynamic_scoring_service.py` — Scoring dynamique
  - `services/habitat_score_service.py` — Score d'habitat
- **Rôle:** Scoring multi-facteur des zones et waypoints
- **Intégré dans MON TERRITOIRE:** PARTIELLEMENT (zone_typology_v7 actif, scoring/ partiellement)
- **Statut:** CANONIQUE, ACTIVATION CONTRÔLÉE REQUISE

### 1.7 scoring_determinism_engine
- **Fichiers:**
  - `services/species_behavior_v7.py` (282+ lignes) — Comportements par espèce
  - `services/behavioral_rasterizer.py` (294 lignes) — Rastérisation comportementale
- **Rôle:** Scoring déterministe (même entrée → même sortie)
- **Intégré dans MON TERRITOIRE:** OUI
- **Statut:** CANONIQUE, ACTIF, BCE-CERTIFIÉ

---

## 2. SERVICES SUPPORT V7 (Dépendances des engines canoniques)

| Fichier | Rôle | Statut |
|---------|------|--------|
| `pipeline_v7.py` | Orchestration V7 du pipeline | ACTIF |
| `srtm_provider_v7.py` | Données d'élévation SRTM | ACTIF |
| `terrain_signals_v7.py` | Signaux terrain | ACTIF |
| `zone_visual_layer_v2.py` | Visualisation des zones | ACTIF |
| `zone_penalty_engine.py` | Pénalités de zones | ACTIF |
| `open_meteo_service.py` | Météo Open-Meteo | ACTIF |
| `weather_service.py` + `weather_cache_service.py` | Météo + cache | ACTIF |
| `dem_service.py` + `dem_cache_service.py` | DEM + cache | ACTIF |
| `spatial_clipping.py` | Découpe spatiale | ACTIF |
| `osm_extractor_v2.py` + `osm_cache_service.py` | Extraction OSM V2 | ACTIF |

---

## 3. ROUTERS CARTOGRAPHIQUES (bionic_engine_p0/routers/)

| Router | Endpoint Prefix | Migré? | Action |
|--------|----------------|--------|--------|
| `organic_zones_router.py` | `/api/v1/bionic/organic-zones` | OUI | CANONIQUE |
| `terrain_data_router.py` | `/api/v1/bionic/terrain-data` | OUI | CANONIQUE |
| `movement_corridors_router.py` | `/api/v1/bionic/corridors` | OUI | CANONIQUE |
| `pipeline_router.py` | `/api/v1/bionic/pipeline` | LEGACY | GELER |
| `waypoint_analysis_router.py` | `/api/v1/bionic/analyze_waypoint` | NON | ÉVALUER |
| `habitat_score_router.py` | `/api/v1/bionic/habitat-score` | NON | ÉVALUER |
| `dynamic_scores_router.py` | `/api/v1/bionic/dynamic-scores` | NON | ÉVALUER |
| `full_comparison_router.py` | `/api/v1/bionic/compare` | NON | ÉVALUER |
| `dem_router.py` | `/api/v1/bionic/dem` | SUPPORT | PRÉSERVER |
| `dem_shadow_router.py` | `/api/v1/bionic/dem-shadow` | SUPPORT | PRÉSERVER |
| `ndvi_shadow_router.py` | `/api/v1/bionic/ndvi-shadow` | SUPPORT | PRÉSERVER |
| `weather_shadow_router.py` | `/api/v1/bionic/weather-shadow` | SUPPORT | PRÉSERVER |
| `shadow_router.py` | `/api/v1/bionic/shadow` | SUPPORT | PRÉSERVER |
| `seasonal_conditions_router.py` | `/api/v1/bionic/seasonal` | SUPPORT | PRÉSERVER |
| `calibration_router.py` | `/api/v1/bionic/calibration` | SUPPORT | PRÉSERVER |
| `spatial_clipping_router.py` | `/api/v1/bionic/clip` | SUPPORT | PRÉSERVER |
| `gps_ultimate_router.py` | `/api/v1/bionic/gps` | NON-CARTO | PRÉSERVER |
| `observations_router.py` | `/api/v1/bionic/observations` | NON-CARTO | PRÉSERVER |
| `notifications_router.py` | `/api/v1/bionic/notifications` | NON-CARTO | PRÉSERVER |
| `hunt_plan_router.py` | `/api/v1/bionic/hunt-plan` | NON-CARTO | PRÉSERVER |
| `api_keys_router.py` | `/api/v1/bionic/api-keys` | NON-CARTO | PRÉSERVER |
| `ml_router.py` | `/api/v1/bionic/ml` | NON-CARTO | PRÉSERVER |
| `sse_router.py` | `/api/v1/bionic/sse` | NON-CARTO | PRÉSERVER |
| `route_planner_router.py` | `/api/v1/bionic/route` | NON-CARTO | PRÉSERVER |

## 4. ENGINES NON-CARTOGRAPHIQUES (À PRÉSERVER INTÉGRALEMENT)

78+ modules dans `/app/backend/modules/` :
- admin_engine, admin_advanced_engine, admin_unified_engine
- affiliate_engine, affiliate_ads_engine, affiliate_switch_engine
- ai_engine, alerts_engine, analytics_engine, auth_engine
- backup_cloud_engine, bionic_knowledge_engine
- camera_engine, cart_engine, collaborative_engine
- communication_engine, contact_engine, customers_engine
- ecoforestry_engine, formations_engine, freemium_engine
- geo_engine, geolocation_engine, geospatial_engine
- global_master_switch, hunting_trip_logger, legal_time_engine
- live_heading_engine, marketing_calendar_engine, marketing_engine
- master_switch, messaging_engine, networking_engine
- notification_engine, notification_unified_engine
- nutrition_engine, onboarding_engine, orders_engine
- partner_engine, payment_engine, predictive_engine
- products_engine, progression_engine, realestate
- recommendation_engine, referral_engine, rental_engine
- roles_engine, rules_engine, scoring_engine (v1)
- seo_engine (complet), social_engine, strategy_engine
- strategy_master_engine, suppliers_engine, territory_engine
- tracking_engine, trigger_engine, tutorial_engine
- upsell_engine, user_engine, waypoint_engine
- waypoint_scoring_engine, weather_engine
- weather_fauna_simulation_engine, wildlife_behavior_engine
- wms_engine, data_layers/ (5 sous-modules)

**ACTION: AUCUNE MODIFICATION. Préserver intégralement.**

---

## 5. LEGACY FIGÉ (À GELER)

### 5.1 Fichiers racine legacy (/app/backend/)
| Fichier | Lignes | Raison du gel |
|---------|--------|---------------|
| `bionic_engine.py` | 1668 | Ancien monolithe V5 — remplacé par bionic_engine_p0/ |
| `hydrography_service.py` | 1147 | Ancien hydro — remplacé par water fix BCE |
| `hydrography_router.py` | 274 | Routeur hydro legacy |
| `territory_ai.py` | 748 | Ancien territory AI |
| `territory.py` | 68 | Ancien territory |
| `territories.py` | 8 | Stub territory |
| `geospatial_data.py` | 1170 | Ancien geospatial — remplacé par terrain_data_router |

### 5.2 Services legacy dans bionic_engine_p0/
| Fichier | Raison du gel |
|---------|---------------|
| `pipeline_service.py` | Pipeline V2.1 — remplacé par pipeline_v7.py |
| `zone_service.py` | Ancien service de zones — remplacé par zone_engine_core_v2.py |
| `osm_extractor.py` | V1 — remplacé par osm_extractor_v2.py |

### 5.3 Archives
- `/app/backend/data/ARCHIVES_V6/` — Archives complètes V6 (FIGÉ, ne pas toucher)

---

## 6. FRONTEND — CARTE INTERACTIVE vs MON TERRITOIRE

### Carte Interactive (source)
- **Page:** `pages/BionicAnalysisDemoPage.jsx`
- **Composant carte:** `components/bionic/CarteBionic.jsx` (1161 lignes)
- **API principale:** `/api/v1/bionic/analyze_waypoint`
- **Modules frontend:** `modules/map_hotspots/`, `modules/map_interaction/`

### MON TERRITOIRE (destination)
- **Page:** `pages/MonTerritoireBionicPage.jsx` (1316 lignes)
- **API principale:** `/api/v1/bionic/organic-zones`
- **Hooks:** `useZoneOrchestrator.js`, `useUserData.js`, `useBionicLayers.js`
- **Composants:** `components/territoire/` (toolbar, sidebar, map)
- **Service:** `services/BionicZoneService.js`

### Écart d'intégration
Les 7 engines canoniques sont DÉJÀ intégrés dans MON TERRITOIRE via le pipeline V7.
La Carte Interactive utilise un pipeline DIFFÉRENT (analyze_waypoint → scoring individuel).
La migration consiste à :
1. Vérifier que tous les engines canoniques sont 100% actifs dans MON TERRITOIRE
2. Geler le pipeline legacy de la Carte Interactive
3. S'assurer que la Carte Interactive ne contourne pas le pipeline canonique

---

## 7. CONCLUSION PHASE A

**DÉCOUVERTE CLÉ:** Les 7 engines canoniques sont DÉJÀ intégrés dans MON TERRITOIRE.
La migration n'est pas une réécriture mais une VALIDATION + GEL du legacy.

**Actions Phase B→C:**
1. Marquer les fichiers legacy comme FIGÉ (headers de gel)
2. Vérifier l'activation complète de scoring_engine_v7 dans le pipeline
3. Exécuter BCE validate-with-zones pour certification
4. Documenter dans le Journal P1
