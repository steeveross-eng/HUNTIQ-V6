# BIONIC V3 — PRD

## Probleme Original
Application BIONIC V3 — Outil d'analyse ecologique full-stack pour la gestion de la faune au Quebec.

## Architecture
- **Frontend:** React + Leaflet/react-leaflet
- **Backend:** FastAPI (Python)
- **Database:** MongoDB
- **Rules:** /app/bionic/ (BCE4X.toml, STEEVEMAX.toml, AutoValidator)

## OPTION B — Progression
### M1 STANDARDISATION (2026-03-18) — VALIDÉ 100% (31/31)
- Interface BionicEngine (ABC), 5 adaptateurs, PRESSION-V1 extrait
- Mapping especes: CHEVREUIL, ORIGNAL, OURS, DINDON, WAPITI
- Engine Registry auto-decouverte + DynamicConsolidator decoupled
- 0 regression

### M2 REGISTRY ENRICHI + REGLES (2026-03-18) — VALIDÉ 100% (19/19)
- /api/v3/engines/{name}/score — Score moteur individuel
- /api/v3/engines/validate — Validation BCE-4X + STEEVE-MAX temps reel
- BCE4XGuard.py: 23 tests (schemas, especes, dependances, versionnement, rollback, scores)
- SteeveMaxRules.py: 12 tests (modularite, taille fichiers, decouplage, code quality)
- AutoValidator.py: CLI executable, rapport JSON
- BCE4X.toml + STEEVEMAX.toml: configs declaratives
- 0 regression

### M3 API GATEWAY /api/v3/* — EN ATTENTE
### M4 INTELLIGENCE FRONTEND — EN ATTENTE

## API Endpoints
### V3 (M1+M2)
- GET /api/v3/engines/registry
- GET /api/v3/engines/score-point
- GET /api/v3/engines/score-grid
- GET /api/v3/engines/{name}/score
- GET /api/v3/engines/validate
### V1/V10 (legacy intact)
- /api/v1/alimentation/*, /api/v1/repos/*, /api/v1/score-consolide/*
- /api/v10/corridors/*

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin Architecte:** `Saturn5858*`
