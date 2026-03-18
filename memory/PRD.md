# BIONIC V3 — PRD

## Probleme Original
Application BIONIC V3 — Outil d'analyse ecologique full-stack pour la gestion de la faune au Quebec.

## Architecture
- **Frontend:** React + Leaflet + Zustand (v5.0.12)
- **Backend:** FastAPI (Python)
- **Database:** MongoDB
- **Rules:** /app/bionic/ (BCE4X.toml, STEEVEMAX.toml, AutoValidator)
- **Gateway:** /app/backend/modules/api_gateway/router.py

## OPTION B — TOUTES PHASES COMPLETEES

### M1 STANDARDISATION — VALIDÉ 100%
- Interface BionicEngine (ABC), 5 adaptateurs, PRESSION-V1 extrait
- Mapping especes: CHEVREUIL, ORIGNAL, OURS, DINDON, WAPITI

### M2 REGISTRY + REGLES — VALIDÉ 100%
- BCE4XGuard (23 tests), SteeveMaxRules (12 tests), AutoValidator
- /api/v3/engines/{name}/score, /api/v3/engines/validate

### M3 API GATEWAY — VALIDÉ 100%
- server.py V3 endpoints extraits vers modules/api_gateway/router.py
- Routeur unifie /api/v3/* comme source unique de verite

### M4 INTELLIGENCE FRONTEND — VALIDÉ 100%
- Analytics: Score consolide, domaines, recommandations auto
- Forecast: Variation 12 mois, saisons, meilleur/pire mois
- Plan Maitre: Actions priorisees par urgence (CRITIQUE→FAIBLE)
- Zustand store global (useBionicStore.js): synchronisation carte ↔ intelligence
- 3 pages dans /pages/intelligence/, App.js et routes.js mis a jour

## API Endpoints V3
- GET /api/v3/engines/registry, /score-point, /score-grid, /{name}/score, /validate
- GET /api/v3/intelligence/summary, /forecast, /plan
- GET /api/v3/species

## Tests
- M1: 31/31 PASS | M2: 19/19 PASS | M3+M4: 18/18 PASS
- BCE-4X: 23/23 | STEEVE-MAX: 12/12
- 0 regression: ZONES 23, V10 19 corridors, ALIMENTATION badge

## Backlog
### P0 — Validation finale utilisateur
### P2 — Migration legacy (RUT-V1, AFFUTS-V1, TRAJETS-V1) — GELE
### P3 — Certification BIONIC V3 + refactoring MonTerritoireBionicPage.jsx

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin Architecte:** `Saturn5858*`
