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

### M1 STANDARDISATION — VALIDE 100% (31/31)
### M2 REGISTRY + REGLES — VALIDE 100% (19/19)
### M3 API GATEWAY — VALIDE 100% (18/18)
### M4 INTELLIGENCE FRONTEND — VALIDE 100%

### FUSION ANALYSE -> INTELLIGENCE (2026-03-18) — VALIDE 100%
- Onglet ANALYSE (legacy) supprime de la navigation et toolbar
- /analyze redirige vers /analytics (React Router Navigate)
- INTELLIGENCE = unique point d'acces analytique
- 0 regression: ZONES 23, V10 19, ALIMENTATION badge, V1 endpoints

### TABLEAU CENTRAL INTELLIGENCE (2026-03-18) — VALIDE 100%
- IntelligenceDashboard.jsx integre dans MonTerritoireBionicPage
- 3 modes: GUIDE PRO, SCIENTIFIQUE, TERRAIN
- 6 blocs: Analytics, Conditions, Mode actif, Forecast, Plan Maitre, Donnees brutes
- Tableau solunaire LUNASOLCAL complet
- Synchronisation bi-directionnelle carte <-> intelligence
- AnalysisSidePanel supprime definitivement
- BCE-4X: 23/23 | STEEVE-MAX: 12/12

## API Endpoints V3
- GET /api/v3/engines/registry, /score-point, /score-grid, /{name}/score, /validate
- GET /api/v3/intelligence/summary, /forecast, /plan
- GET /api/v3/intelligence/solunar, /guide-pro, /scientifique
- GET /api/v3/species

## Pages Frontend
- /analytics — Score consolide, domaines, recommandations (auto-adaptatif)
- /forecast — Variation 12 mois, saisons, best/worst
- /plan-maitre — Actions priorisees (CRITIQUE -> FAIBLE)
- /territoire — MON TERRITOIRE (carte, zones, corridors, alimentation, INTELLIGENCE)

## Composants Intelligence
- IntelligenceDashboard.jsx — Tableau central, selectorateur de mode, 6 blocs
- ModeGuidePro.jsx — Solunaire + fenetres chasse + plan approche
- ModeScientifique.jsx — Ponderations, formules, metadonnees BCE-4X
- ModeTerrain.jsx — Vue simplifiee mobile/hors reseau
- SolunarChart.jsx — Courbe SVG LUNASOLCAL 24h

## Backlog
### P0 — Refactoring MonTerritoireBionicPage (reduction de ~2100 lignes)
### P1 — Certification BIONIC V3 (documentation finale)
### P2 — Migration legacy (RUT-V1, AFFUTS-V1, TRAJETS-V1) — GELE
### P3 — Certification BIONIC V3

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin Architecte:** `Saturn5858*`
