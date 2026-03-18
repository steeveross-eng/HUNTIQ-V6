# BIONIC V3 — PRD (Product Requirements Document)

## Probleme Original
Application BIONIC V3 — Outil d'analyse ecologique full-stack pour la gestion de la faune au Quebec.

## Architecture
- **Frontend:** React + Leaflet/react-leaflet
- **Backend:** FastAPI (Python)
- **Database:** MongoDB

## Taches Completees
### HEATMAP V10 100% TRANSPARENT (2026-03-18)
- Modes Lite/Pro ABOLIS — composant data-only
- Toggle Corridors V10 ON/OFF dans Overlays
- 0 regression

### AUDIT BCE-4X COMPLET (2026-03-18)
- 7 moteurs audites (ALIM-V1, ALIM-V2, REPOS-V1, CORRIDORS-V10, HABITAT, PRESSION, ACCESSIBILITE)
- API: 30+ endpoints documentes, 3 schemas versionnement identifies
- UI/UX: Navigation, toolbar, interactions carte-Intelligence analysees
- Risques: mapping especes, couplage score_consolide, MonTerritoireBionicPage 2114L
- Plan migration M1-M5 produit
- Rapport complet: /app/memory/AUDIT_BCE4X_INTELLIGENCE_REFACTOR.md

## API Endpoints
### Ecologiques (actifs)
- POST /api/v1/alimentation/analyze, GET /point, /multi, /profiles
- POST /api/v2/alimentation/analyze, GET /species
- POST /api/v1/repos/analyze, GET /point, /multi, /profiles
- POST /api/v10/corridors/analyze, /analyze-full, GET /multi, /profiles
- GET /api/v1/score-consolide/point, /heatmap

## Backlog
### P0 — Validation finale ALIMENTATION-V2 + Heatmap transparente
### M1 — Standardisation moteurs (interface commune, mapping especes)
### M2 — Engine Registry + Consolidateur dynamique
### M3 — API Gateway unifie /api/v3/*
### M4 — INTELLIGENCE Frontend (rewrite Analytics, Forecast, Plan Maitre)
### M5 — Validation + Certification BCE-4X
### P2 — Migration legacy (RUT-V1, AFFUTS-V1, TRAJETS-V1)
### P3 — Refactoring MonTerritoireBionicPage.jsx

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin Architecte:** `Saturn5858*`
