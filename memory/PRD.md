# BIONIC HUNT V8 — PRD (Product Requirements Document)

## Original Problem Statement
Build a sophisticated ecological analysis tool for hunting (BIONIC HUNT). The tool integrates ecological knowledge, terrain analysis, and wildlife behavior modeling for Quebec-based hunting.

## Strategie BIONIC 2000%
- Phases 1-3: DONE (Freeze, Reconstruct, Certify)
- Phase 4: Branches creees

## Normes Architecturales BIONIC (BCE Permanent)
- Architecture 100% modulaire, zero hardcoding, zero duplication
- Zero croisement responsabilites, zero artefact legacy
- Chaque composant: autonome, tracable, testable, remplacable, documente

## Tech Stack
- Frontend: React, Leaflet.js, TailwindCSS, Shadcn/UI
- Backend: FastAPI (Python), MongoDB
- DEM/NDVI/Pression: Option A — Modele algorithmique interne (confirme)

## Completed Tasks
- P0: A* Corridors DONE
- P1: EcologicalPanel Integration DONE (6/6 tests)
- P2: Right Panel Refactoring DONE (12/12 tests)
- P3: Phase 4 Branches DONE
- Phase E: Decommission PARTIAL (3/12)
- BCE-4X Corridors: DONE (21/21 tests, 64 violations V8 detectees)
- BCE-4X Transfer complet: DONE (16 modules, 8 actifs, 8 planifies, 0 non couverts)

## BCE-4X Coverage (12 Mars 2026)
| Module | Status | Validateur |
|--------|--------|------------|
| corridor_10x | active | corridor_v9 |
| zone_engine_core | active | spatial_integrity |
| ecological_database | active | ecological_validators_v8 |
| movement_engine | active | corridor_v9 |
| weather_engine | active | WeatherEngineValidator |
| waypoint_engine | active | WaypointEngineValidator |
| ui_coherence | active | ui_coherence |
| scoring_determinism | active | scoring_determinism |
| nutrition_engine | planned | NutritionEngineValidator |
| daily_routine_engine | planned | DailyRoutineEngineValidator |
| disturbance_engine | planned | DisturbanceEngineValidator |
| phenology_engine | planned | PhenologyEngineValidator |
| typology_engine | planned | TypologyEngineValidator |
| learning_engine | planned | LearningEngineValidator |
| habitat_enhancement | planned | HabitatEnhancementValidator |
| hunting_path_engine | planned | HuntingPathEngineValidator |

## Current Priority: Phase Corridors V9
EN ATTENTE validation utilisateur. Corrections:
1. Supprimer subscores hardcodes
2. Appeler enrich_corridor() dans pipeline
3. Scores dynamiques (terrain, habitat)
4. Clipping strict 2km²
5. Classification 5 niveaux
6. Integrer 9 moteurs BIONIC
7. Option A: DEM/NDVI/pression algorithmique

## Key API Endpoints
- POST /api/v1/bionic/organic-zones
- GET /api/v1/ecological-knowledge/{species}
- GET /api/bce/status
- GET /api/bce/registry
- POST /api/bce/validate-corridors
- POST /api/bce/validate-engines

## Known Issues
- OWM_API_KEY manquante (fallback actif)
- 64 violations BCE-4X corridors V8 (bloquant, V9 requis)
