# BIONIC HUNT — PRD.md

## Branche: steve-max

## Architecture
- **Frontend**: React + Leaflet + Shadcn/UI
- **Backend**: FastAPI + 12 V1 (corridors) + 12 V2 + 12 V3 + 3 IA engines + 3 modeles fauniques
- **Weather**: OpenWeatherMap (cache 60min)
- **Quality Gate**: BCE-4X (12+ regles, 100% PASS)

## Implemente

### BIONIC V3 Integration Totale (2026-03-13)
- **27 engines actifs** (12 V2 + 12 V3 + 3 IA)
- **V3 engines**: EcologicalHierarchy, Interaction, GeoPedology, Connectivity, TemporalDynamics, Hotspot, ForestStructureV2, FoodScoreV2, WetnessScoreV2, GeoFormScoreV2, BehaviorV2, GlobalAttractivenessV2
- **IA engines**: PredictiveModels (24h/72h/7d), DynamicScoring (temps reel), TemporalAnalysis (trends)
- **Modeles fauniques**: Moose (ponderations specifiques), Deer, Bear — scores differencies
- **Pipeline integre**: Phase 1 (independants) → Phase 2 (dependants) → Phase 3 (IA) → Phase 4 (faunique) → Phase 5 (score final)
- **API V3**: /engines-v3/compute, /engines-v3/status, /engines-v3/species/{id}, /engines-v3/predictions
- **Frontend**: BionicEngineHub V3 avec 4 onglets (V2, V3, IA, Faune)

### Harmonisation Couleurs (2026-03-13)
- Module centralise bionicColorsConfig.js
- 15/15 couleurs harmonisees sur 7 fichiers sources
- Diagnostic panel FACTORS + barres analyse alignes

### Corrections Precedentes
- 12 moteurs V2 (backend + API + frontend)
- Corridor continuity graph-based, BAND_RATIO +20%
- BCE-4X: COR-006, VIS-007, GEOM-005 PASS
- Wind logic removed from hunting path pipeline

## Tests
- Iteration 16: 20/20 PASS (V3 Integration, species differentiation, AI predictions)
- Iteration 15: 19/19 PASS (color harmonization)
- Iteration 14: 20/20 PASS (corrections finales)
- Iteration 13: 18/18 PASS (V2 integration)

## API Endpoints
- POST /api/v1/bionic/engines-v3/compute — 27 engines + 3 species + final score
- GET /api/v1/bionic/engines-v3/status — statut 27 engines
- POST /api/v1/bionic/engines-v3/species/{moose|deer|bear} — scoring par espece
- POST /api/v1/bionic/engines-v3/predictions — predictions IA 24h/72h/7d
- POST /api/v1/bionic/engines-v2/compute — backward compatible
- GET /api/v1/bionic/engines-v2/status — backward compatible

## Backlog
### P1 - Export GeoJSON/KML avec metadata engines
### P2 - Dashboard analytics, apprentissage machine
### P3 - Multi-territoire

## Credentials
- Steeve.ross@gmail.com / Saturn5858*
- OWM_API_KEY dans backend/.env
