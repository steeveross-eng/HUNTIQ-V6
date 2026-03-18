# BIONIC V3 — PRD

## Probleme Original
Application BIONIC V3 — Outil d'analyse ecologique full-stack pour la gestion de la faune au Quebec.

## Architecture
- **Frontend:** React + Leaflet + Zustand v5.0.12
- **Backend:** FastAPI (Python)
- **Database:** MongoDB
- **Rules:** /app/bionic/ (BCE4X.toml, STEEVEMAX.toml, AutoValidator)
- **Gateway:** /app/backend/modules/api_gateway/router.py

## OPTION B — TOUTES PHASES COMPLETEES

### M1 STANDARDISATION — VALIDÉ 100% (31/31)
### M2 REGISTRY + REGLES — VALIDÉ 100% (19/19)
### M3 API GATEWAY — VALIDÉ 100% (18/18)
### M4 INTELLIGENCE FRONTEND — VALIDÉ 100%

### FUSION ANALYSE → INTELLIGENCE (2026-03-18) — VALIDÉ 100%
- Onglet ANALYSE (legacy) supprime de la navigation (header, mobile, routes.js)
- /analyze redirige vers /analytics (React Router Navigate)
- INTELLIGENCE = unique point d'acces analytique
- Tab interne 'Analyse' dans toolbar MON TERRITOIRE preservee
- 0 regression: ZONES 23, V10 19, ALIMENTATION badge, V1 endpoints

## API Endpoints V3
- GET /api/v3/engines/registry, /score-point, /score-grid, /{name}/score, /validate
- GET /api/v3/intelligence/summary, /forecast, /plan
- GET /api/v3/species

## Pages Frontend
- /analytics — Score consolide, domaines, recommandations (auto-adaptatif)
- /forecast — Variation 12 mois, saisons, best/worst
- /plan-maitre — Actions priorisees (CRITIQUE → FAIBLE)
- /territoire — MON TERRITOIRE (carte, zones, corridors, alimentation)

## Backlog
### P0 — Validation finale utilisateur
### P2 — Migration legacy (RUT-V1, AFFUTS-V1, TRAJETS-V1) — GELE
### P3 — Certification BIONIC V3

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin Architecte:** `Saturn5858*`
