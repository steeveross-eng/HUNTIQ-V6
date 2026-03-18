# BIONIC V3 — PRD

## Probleme Original
Application BIONIC V3 — Outil d'analyse ecologique full-stack pour la gestion de la faune au Quebec.

## Architecture
- **Frontend:** React + Leaflet/react-leaflet
- **Backend:** FastAPI (Python)
- **Database:** MongoDB

## OPTION B — Progression
### M1 STANDARDISATION (2026-03-18) — VALIDÉ 100%
- Interface BionicEngine (ABC): meta(), score_point(), score_grid()
- Mapping especes unifie: CHEVREUIL, ORIGNAL, OURS, DINDON, WAPITI
- PRESSION-V1 extrait comme moteur standalone
- 5 adaptateurs: AlimentationV1, AlimentationV2, ReposV1, CorridorsV10, PressionV1
- Engine Registry auto-decouverte: /api/v3/engines/registry
- DynamicConsolidator decoupled: /api/v3/engines/score-point, /score-grid
- Tests: 31/31 backend PASS + frontend 100% PASS
- 0 regression MON TERRITOIRE

### M2 ENGINE REGISTRY DYNAMIQUE — EN ATTENTE
### M3 API GATEWAY /api/v3/* — EN ATTENTE
### M4 INTELLIGENCE FRONTEND — EN ATTENTE

## API Endpoints
### V3 (nouveau)
- GET /api/v3/engines/registry
- GET /api/v3/engines/score-point
- GET /api/v3/engines/score-grid
### V1/V10 (legacy, intact)
- POST /api/v1/alimentation/analyze, GET /point
- POST /api/v2/alimentation/analyze
- POST /api/v1/repos/analyze, GET /point
- POST /api/v10/corridors/analyze-full
- GET /api/v1/score-consolide/point, /heatmap

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin Architecte:** `Saturn5858*`
