# MOTEUR UNIQUE BIONIC ULTIME — Plan Strategique Mon Territoire
## Date: 2026-03-10 | Version: V8.2

---

# ══════════════════════════════════════════════════════════════
# PHASE 0 — CARTOGRAPHIE: CARTE INTERACTIVE vs MON TERRITOIRE
# ══════════════════════════════════════════════════════════════

## PIPELINE PRINCIPAL (utilise par POST /organic-zones)

| # | Engine | Role | Statut Mon Territoire | Impact | Decision |
|---|--------|------|----------------------|--------|----------|
| 01 | zone_engine_core_v2 | Orchestrateur pipeline V7 | **ACTIF** | CRITIQUE | CONSERVER — Coeur unique |
| 02 | pipeline_v7 | Enrichissement par couche | **ACTIF** | CRITIQUE | CONSERVER |
| 03 | corridor_v7 | Pathfinding A* terrain-aware | **ACTIF** | HAUTE | CONSERVER |
| 04 | exclusion_engine_v6 | Filtrage geometrique | **ACTIF** | HAUTE | CONSERVER |
| 05 | exclusion_config_v6 | Buffers par type | **ACTIF** | HAUTE | CONSERVER (sous-module #04) |
| 06 | exclusion_geometry_v6 | Operations Shapely | **ACTIF** | HAUTE | CONSERVER (sous-module #04) |
| 07 | zone_typology_v7 | Scoring pipeline (UNIQUE) | **ACTIF** | CRITIQUE | CONSERVER — Scoring reference |
| 08 | species_behavior_v7 | Matrices comportementales | **ACTIF** | HAUTE | CONSERVER |
| 09 | srtm_provider_v7 | DEM OpenTopography | **ACTIF** | HAUTE | CONSERVER |
| 10 | terrain_signals_v7 | Signaux terrain | **ACTIF** | HAUTE | CONSERVER |
| 11 | trail_cost_grid_v7 | Grille couts A* | **ACTIF** | HAUTE | CONSERVER |
| 12 | behavioral_rasterizer | Rasters Simplex | **ACTIF** | CRITIQUE | CONSERVER |
| 13 | organic_zone_generator_v2 | Contours Marching Squares | **ACTIF** | CRITIQUE | CONSERVER |
| 14 | zone_visual_layer_v2 | Conversion GeoJSON | **ACTIF** | HAUTE | CONSERVER |
| 15 | zone_penalty_engine | Penalites proximite | **ACTIF** | MOYENNE | CONSERVER |
| 16 | zone_shape_v7 | Lissage + topologie | **ACTIF** | HAUTE | CONSERVER |

**VERDICT: 16/16 engines pipeline = ACTIFS et NECESSAIRES. Zero a supprimer.**

## OVERPASS / CACHE

| # | Engine | Role | Statut Mon Territoire | Decision |
|---|--------|------|----------------------|----------|
| 17 | terrain_data_router | Overpass + cache MongoDB | **ACTIF** | CONSERVER |
| 18 | osm_cache_service | Cache regional memoire | **ACTIF** | CONSERVER |
| 19 | osm_extractor_v2 | Extraction batch | **ACTIF** | CONSERVER |

## WEATHER

| # | Engine | Role | Statut Mon Territoire | Decision |
|---|--------|------|----------------------|----------|
| 20 | weather_engine/v1/external | OpenWeatherMap API | **ACTIF** (simule) | CONSERVER — Moteur meteo UNIQUE |
| 21 | weather_engine/v1/service | Scoring meteo chasse | **ACTIF** | CONSERVER |
| 22 | weather_engine/v1/router | Endpoints meteo | **ACTIF** | CONSERVER |
| 23 | weather_cache_service | Cache MongoDB meteo | **ACTIF** | CONSERVER |
| 24 | **weather_service.py (P0)** | **DOUBLON 754L** | **DOUBLON** | **SUPPRIMER** — Remplace par #20-22 |

## SCORING — ANALYSE DE COMPETITION

| # | Engine | Appele par | Statut Mon Territoire | Decision |
|---|--------|-----------|----------------------|----------|
| 25 | zone_typology_v7 (#07) | pipeline_v7 (PIPELINE PRINCIPAL) | **ACTIF** | **SCORING UNIQUE MON TERRITOIRE** |
| 26 | unified_scoring_service | waypoint_analysis_service | SECONDAIRE | ABSORBER dans #25 |
| 27 | dynamic_scoring_service | hunt_plan_analyzer, scoring_router | SECONDAIRE | ABSORBER dans #25 |
| 28 | multifactor_scoring_engine | router.py legacy, dynamic_scores_router | SECONDAIRE | ABSORBER dans #25 |
| 29 | scoring_zone_integration | organic_zones_router (feature flag OFF) | **INACTIF** | **SUPPRIMER** |
| 30-39 | 10 score_*_service.py | multifactor_scoring_engine | SECONDAIRE | ABSORBER les meilleurs dans #25 |

**COMPETITION IDENTIFIEE: 4 systemes de scoring concurrents.**
**RESOLUTION: zone_typology_v7 = scoring unique. Absorber score_weather et score_habitat dans ses sous-scores.**

## SERVICES COMPLEMENTAIRES

| # | Engine | Role | Statut Mon Territoire | Decision |
|---|--------|------|----------------------|----------|
| 40 | spatial_clipping | Decoupe bbox waypoint | **ACTIF** | CONSERVER |
| 41 | sse_engine | Landcover/microrelief | INACTIF (backend pret, UI manquante) | ACTIVER V8.4 |
| 42 | windfield_service | Grille vent vectorielle | INACTIF (backend pret, UI V8.3) | ACTIVER V8.3 |
| 43 | hotspot_service | Hotspots organiques | INACTIF | EVALUER — utile pour prediction |
| 44 | hunt_plan_analyzer_service | Plan de chasse | INACTIF | ACTIVER V8.5 |
| 45 | hunt_plan_analyzer | Version etendue | INACTIF | DOUBLON avec #44 — CONSOLIDER |
| 46 | waypoint_analysis_service | Analyse complete waypoint | INACTIF | ACTIVER V8.4 |
| 47 | heatmap_fusion_service | Heatmap unifiee | INACTIF | ACTIVER V8.5 |
| 48 | layer_aggregator_service | Agregation multi-couches | INACTIF | EVALUER |
| 49 | seasonal_conditions_service | Conditions saisonnieres | **ACTIF** (endpoint) | CONSERVER |
| 50 | dem_service | Service DEM complementaire | INACTIF | DOUBLON #09 — SUPPRIMER |
| 51 | comparison_service | Comparaison | INACTIF | EVALUER si Split View le couvre |

## LEGACY — A SUPPRIMER

| # | Engine | Lignes | Supercede par | Decision |
|---|--------|--------|---------------|----------|
| 52 | corridor_service.py | 488 | corridor_v7 (#03) | **SUPPRIMER** |
| 53 | zone_service.py | 368 | zone_engine_core_v2 (#01) | **SUPPRIMER** |
| 54 | weather_service.py | 754 | weather_engine/v1 (#20-22) | **SUPPRIMER** |
| 55 | organic_contour_generator.py | 804 | organic_zone_generator_v2 (#13) | **SUPPRIMER** |
| 56 | pipeline_service.py | 247 | pipeline_v7 (#02) | **SUPPRIMER** |
| 57 | contour_generator.py | 618 | organic_zone_generator_v2 (#13) | **SUPPRIMER** |
| 58 | scoring_zone_integration.py | 183 | zone_typology_v7 (#07) | **SUPPRIMER** |
| 59 | dem_service.py | 170 | srtm_provider_v7 (#09) | **SUPPRIMER** |

**TOTAL A SUPPRIMER: 8 fichiers, 3,632 lignes de code mort**

## FRONTEND — MON TERRITOIRE

| # | Composant/Hook | Role | Statut | Decision |
|---|---------------|------|--------|----------|
| 60 | MonTerritoireBionicPage | Page principale | **ACTIF** | CONSERVER |
| 61 | useZoneOrchestrator | Pipeline frontend | **ACTIF** | CONSERVER |
| 62 | useWaypointActions | CRUD waypoints | **ACTIF** | CONSERVER |
| 63 | useZoneCache | Cache IndexedDB | **ACTIF** | CONSERVER |
| 64 | useSplitViewSync | Sync 2 cartes | **ACTIF** | CONSERVER |
| 65 | useSplitViewZones | Zones carte droite | **ACTIF** | CONSERVER |
| 66 | useBionicWeather | Meteo live | **ACTIF** | CONSERVER |
| 67 | useBionicLayers | Toggle couches | **ACTIF** | CONSERVER |
| 68 | useBionicScoring | Scoring frontend | **ACTIF** | CONSERVER |
| 69 | useSpatialClipping | Decoupe bbox | **ACTIF** | CONSERVER |
| 70 | useGeolocation | GPS | **ACTIF** | CONSERVER |
| 71 | useMapType | Toggle carte | **ACTIF** | CONSERVER |
| 72 | useUserData | Persistance | **ACTIF** | CONSERVER |
| 73 | MapContent | Carte Leaflet | **ACTIF** | CONSERVER |
| 74 | SplitViewContainer | Split View | **ACTIF** | CONSERVER |
| 75 | MonTerritoireToolbar | Barre outils | **ACTIF** | CONSERVER |
| 76 | BiologicalSeasonSelector | Dropdown saison | **ACTIF** | CONSERVER |
| 77 | EcoforestryLayers | WMS ecoforestier | **ACTIF** | CONSERVER |
| 78 | MovementCorridorsLayer | Corridors V7 | **ACTIF** | CONSERVER |
| 79 | HydrographyOverlayLayer | Hydro WMS | **ACTIF** | CONSERVER |
| 80 | ExclusionOverlayLayer | Exclusions | **ACTIF** | CONSERVER |
| 81 | WindFlowLayer | Vent anime | SQUELETTE | ACTIVER V8.3 |
| 82 | BionicLegend | Legende | **ACTIF** | CONSERVER |
| 83 | SeasonalConditionsWidget | Widget meteo | **ACTIF** | CONSERVER |
| 84 | SmartMapTooltip | Tooltip zone | **ACTIF** | CONSERVER |
| 85 | bionicWeatherEngine | Calculs meteo | **ACTIF** | CONSERVER |
| 86 | bionicScoring | Scoring frontend | **ACTIF** | CONSERVER |
| 87 | bionicDataAdapter | Adaptation donnees | **ACTIF** | CONSERVER |
| 88 | bionicConfig | Config globale | **ACTIF** | CONSERVER |
| 89 | bionicSpecies | Config especes | **ACTIF** | CONSERVER |
| 90 | **speciesConfig** | Config especes (alt) | **DOUBLON** | **SUPPRIMER** — Fusionner dans #89 |
| 91 | biologicalSeasons | 5 saisons bio | **ACTIF** | CONSERVER |


# ══════════════════════════════════════════════════════════════
# PHASE 1 — ENGINES MANQUANTS POUR MON TERRITOIRE
# ══════════════════════════════════════════════════════════════

## A) ENGINES RECOMMANDES POUR ACTIVATION

| # | Engine | Role | Benefice Utilisateur | Dependances | Risque | Priorite |
|---|--------|------|---------------------|-------------|--------|----------|
| M1 | windfield_service + WindFlowLayer | Vent anime (particules Canvas 2D) | Visualise direction/intensite vent en temps reel → predire mouvements gibier | weather_engine | LOW | V8.3 |
| M2 | waypoint_analysis_service | Analyse complete par waypoint (score unifie, heatmap) | Score detaille par point + recommandations | unified_scoring (a absorber) | MEDIUM | V8.4 |
| M3 | hotspot_service | Detection hotspots organiques | Identifie les points chauds d'activite animale | behavioral_rasterizer | LOW | V8.4 |
| M4 | sse_engine | Landcover + microrelief | Couches visuelles avancees (type de sol, lisiere) | numpy | LOW | V8.4 |
| M5 | hunt_plan_analyzer | Plan de chasse intelligent | Recommandation temps/lieu optimal | weather + scoring + behavior | MEDIUM | V8.5 |
| M6 | heatmap_fusion | Heatmap unifiee | Visualisation probabiliste sur la carte | scoring + zones | LOW | V8.5 |

## B) ENGINES A NE PAS ACTIVER

| # | Engine | Raison |
|---|--------|--------|
| B1 | unified_scoring_service (1159L) | DOUBLON — zone_typology_v7 est le scoring du pipeline. Absorber les bonnes parties. |
| B2 | dynamic_scoring_service (883L) | DOUBLON — Meme raisonnement. Absorber score_weather dans zone_typology_v7. |
| B3 | multifactor_scoring_engine + 10 sous-services (3816L) | DOUBLON — Trop granulaire. Les meilleurs sous-scores sont deja dans zone_typology_v7. |
| B4 | layer_aggregator_service (1268L) | Trop complexe pour le benefice. Le pipeline_v7 fait deja l'agregation. |
| B5 | comparison_service (153L) | Le Split View couvre ce besoin cote frontend. |
| B6 | ml_feature_builder | Experimental, pas encore mature. |

## C) ENGINES A CREER POUR BIONIC ULTIME

| # | Engine Futur | Role | Benefice | Complexite |
|---|-------------|------|----------|-----------|
| F1 | **Behavior Prediction Engine** | Predit la position probable du gibier dans les 1-6h basee sur: saison + meteo + heure + pression barometrique + phase lunaire + comportement espece | "Ou sera l'orignal dans 3h?" — valeur differenciante massive | HAUTE |
| F2 | **Human Pressure Engine** | Modele la pression de chasse humaine: routes d'acces, stationnements, popularite zone, jour de semaine | "Ou les autres chasseurs ne vont pas?" — avantage strategique | MOYENNE |
| F3 | **Learning/Adaptation Engine** | Apprend des observations validees par l'utilisateur (gibier vu ici a telle heure/saison) pour affiner les predictions | Precision qui augmente avec l'usage — fidelisation utilisateur | HAUTE |
| F4 | **Simulation/Forecast Engine** | Simule differents scenarios (si vent change de direction, si pluie arrive dans 2h) et montre l'impact sur les zones | "Que se passe-t-il si le vent tourne?" — aide a la decision | HAUTE |
| F5 | **Alert Engine** | Notifie l'utilisateur quand les conditions deviennent optimales pour une zone favorite | "Tes conditions ideales sont reunies MAINTENANT" — engagement | MOYENNE |


# ══════════════════════════════════════════════════════════════
# PHASE 2 — ELIMINATION DOUBLONS & PIPELINE UNIQUE
# ══════════════════════════════════════════════════════════════

## SCORING UNIQUE — Resolution de la competition

```
AVANT (4 systemes concurrents):
┌─────────────────────────────────────┐
│ zone_typology_v7 (pipeline)         │ ← Scoring du pipeline principal
│ unified_scoring_service (1159L)     │ ← Scoring waypoint_analysis
│ dynamic_scoring_service (883L)      │ ← Scoring hunt_plan
│ multifactor_scoring (342L + 3816L)  │ ← Scoring dynamic_scores
└─────────────────────────────────────┘
  = 6,879 lignes de scoring concurrents

APRES (1 systeme unique):
┌─────────────────────────────────────┐
│ zone_typology_v7 (ENRICHI)          │
│ ├── Sous-scores existants:          │
│ │   habitat, terrain, season,       │
│ │   behavior, weather, confidence   │
│ ├── Sous-scores absorbes:           │
│ │   + weather_pressure (de #34)     │
│ │   + habitat_density (de #33)      │
│ │   + mobility_factor (de #37)      │
│ └── Export unifie:                  │
│     score_global + 9 sous-scores    │
└─────────────────────────────────────┘
  = ~600 lignes (vs 6,879 avant)
```

## WEATHER UNIQUE

```
AVANT (2 systemes):
┌──────────────────────────────┐
│ weather_engine/v1 (1151L)    │ ← API externe, scoring chasse
│ weather_service.py P0 (754L) │ ← Modeles Pydantic, facteurs
└──────────────────────────────┘

APRES (1 systeme):
┌──────────────────────────────┐
│ weather_engine/v1 (ENRICHI)  │
│ ├── external_service.py      │ ← OpenWeatherMap (inchange)
│ ├── service.py               │ ← Scoring (absorbe P0 models)
│ └── router.py                │ ← Endpoints (inchange)
└──────────────────────────────┘
```

## PIPELINE UNIQUE MON TERRITOIRE

```
POST /api/v1/bionic/organic-zones
  │
  ▼
zone_engine_core_v2 (ORCHESTRATEUR UNIQUE)
  ├── _fetch_exclusions (Overpass, 5 phases resilience)
  ├── srtm_provider_v7 (DEM)
  ├── behavioral_rasterizer (rasters x couche, 6 threads)
  ├── organic_zone_generator_v2 (contours)
  │
  └──► pipeline_v7 (PAR COUCHE)
        ├── exclusion_engine_v6 (Shapely)
        ├── zone_shape_v7 (lissage)
        ├── zone_typology_v7 (SCORING UNIQUE)
        │   ├── subscores: habitat, terrain, season, behavior, weather
        │   ├── confidence level
        │   └── zone_type classification
        ├── zone_penalty_engine (penalites)
        │
        └──► corridor_v7 (A* UNIQUE)
              ├── trail_cost_grid_v7
              └── species_behavior_v7

  [V8.3] + windfield_service ──► WindFlowLayer (Canvas 2D)
  [V8.4] + hotspot_service ──► HotspotLayer
  [V8.4] + sse_engine ──► LandcoverLayer
  [V8.5] + hunt_plan_analyzer ──► HuntPlanPanel

  [FUTUR] + behavior_prediction_engine
  [FUTUR] + human_pressure_engine
  [FUTUR] + alert_engine
```


# ══════════════════════════════════════════════════════════════
# PHASE 3 — PLAN D'ACTIVATION PROGRESSIVE
# ══════════════════════════════════════════════════════════════

## ETAPE 1 — NETTOYAGE (P0, 0 risque, ~1h)

**Action: Supprimer 8 fichiers legacy + 1 doublon frontend**

| Fichier a supprimer | Lignes | Supercede par |
|---------------------|--------|---------------|
| services/corridor_service.py | 488 | corridor_v7.py |
| services/zone_service.py | 368 | zone_engine_core_v2.py |
| services/weather_service.py | 754 | weather_engine/v1 |
| services/organic_contour_generator.py | 804 | organic_zone_generator_v2.py |
| services/pipeline_service.py | 247 | pipeline_v7.py |
| services/contour_generator.py | 618 | organic_zone_generator_v2.py |
| services/scoring_zone_integration.py | 183 | zone_typology_v7.py |
| services/dem_service.py | 170 | srtm_provider_v7.py |
| core/bionic/speciesConfig.js | 136 | bionicSpecies.js |
| **TOTAL** | **3,768** | |

**Pre-requis:** Verifier que router.py legacy n'expose pas d'endpoints utilises par le frontend.
**Tests:** Relancer tous les tests backend + frontend apres suppression.

## ETAPE 2 — VERROUILLAGE MOTEURS UNIQUES (P0, ~2h)

**2a. Scoring unique = zone_typology_v7**
- Absorber `score_weather_service.py` et `score_habitat_service.py` dans zone_typology_v7
- Retirer les imports des services secondaires dans les routers qui ne sont pas utilises par Mon Territoire
- Ne PAS supprimer unified/dynamic/multifactor tout de suite (endpoints secondaires peuvent en avoir besoin)
- Marquer comme DEPRECATED avec warning log

**2b. Weather unique = weather_engine/v1**
- Deja le cas apres suppression de weather_service.py
- Verifier que le pipeline utilise bien weather_engine/v1 pour les facteurs comportementaux

**Tests:** 32+ tests backend + testing_agent frontend

## ETAPE 3 — V8.3 VENT ANIME (~3h)

1. Activer windfield_service dans le pipeline (endpoint /wind-field)
2. Implementer Canvas 2D dans WindFlowLayer.jsx (particules animees)
3. Toggle ON/OFF dans la toolbar
4. Synchroniser avec donnees meteo reelles
5. Compatible mobile (touch, performance)

**Tests:** Tests backend + testing_agent UI

## ETAPE 4 — V8.4 ENRICHISSEMENT (~4h)

1. Activer waypoint_analysis_service dans Mon Territoire
2. Activer hotspot_service → layer hotspots sur la carte
3. Activer sse_engine → layer landcover
4. Creer les composants UI correspondants

**Tests:** Tests unitaires + integration + UI

## ETAPE 5 — V8.5 PLAN DE CHASSE (~4h)

1. Consolider hunt_plan_analyzer (fusionner les 2 versions)
2. Activer heatmap_fusion → overlay heatmap
3. Creer HuntPlanPanel (recommandations)

## ETAPE 6 — BIONIC ULTIME (FUTUR)

1. Behavior Prediction Engine (position probable gibier T+1h a T+6h)
2. Human Pressure Engine (pression chasse humaine)
3. Learning/Adaptation Engine (apprentissage observations)
4. Simulation/Forecast Engine (scenarios "what-if")
5. Alert Engine (notification conditions optimales)


# ══════════════════════════════════════════════════════════════
# COMPLIANCE BIONIC™
# ══════════════════════════════════════════════════════════════

| Critere | Avant Nettoyage | Apres Etape 1 | Apres Etape 2 |
|---------|----------------|---------------|---------------|
| Moteur unique | NON (4 scorings) | NON (4 scorings, legacy supprime) | OUI |
| Zero doublon | NON (8 legacy) | OUI | OUI |
| Zero code mort | NON (3,768L) | OUI | OUI |
| Deterministe | OUI | OUI | OUI |
| Modulaire | OUI | OUI | OUI |
| Extensible | OUI | OUI | OUI (F1-F5 pluggables) |
| Teste | OUI (110+ tests) | OUI (regression verifiee) | OUI |
