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

### M1 STANDARDISATION — VALIDE 100%
### M2 REGISTRY + REGLES — VALIDE 100%
### M3 API GATEWAY — VALIDE 100%
### M4 INTELLIGENCE FRONTEND — VALIDE 100%

### FUSION ANALYSE -> INTELLIGENCE — VALIDE 100%
### TABLEAU CENTRAL INTELLIGENCE — VALIDE 100%
### RESTAURATION CARTE + ANTI-REGRESSION — VALIDE 100%

### TABLEAU FLOTTANT NON-BLOQUANT + REFACTORING P0 (2026-03-18) — VALIDE 100%
- IntelligenceDashboard = panneau flottant central (pointer-events-none wrapper)
- Carte 100% interactive meme quand INTELLIGENCE est ouvert
- Toolbar extraite -> TerritoireToolbar.jsx (composant independant)
- NutritionPanel extraite -> NutritionPanel.jsx (composant independant)
- MonTerritoireBionicPage: 2119 -> 1553 lignes (-27%, -566 lignes)
- Sync bi-directionnelle: Intelligence -> Carte (highlight zones, navigate, marqueurs approche)
- Mode compact (minimize/maximize toggle)
- BCE-4X 23/23 | STEEVE-MAX 12/12 | 21/21 tests PASS

## API Endpoints V3
- GET /api/v3/engines/registry, /score-point, /score-grid, /{name}/score, /validate
- GET /api/v3/intelligence/summary, /forecast, /plan
- GET /api/v3/intelligence/solunar, /guide-pro, /scientifique
- GET /api/v3/species

## Composants Extraits (Refactoring STEEVE-MAX)
- TerritoireToolbar.jsx — Toolbar complete extraite
- NutritionPanel.jsx — Panneau recommandations ALIMENTATION-V2
- IntelligenceDashboard.jsx — Tableau flottant central non-bloquant
- ModeGuidePro/ModeScientifique/ModeTerrain.jsx — 3 modes
- SolunarChart.jsx — Courbe SVG LUNASOLCAL 24h

## Regles BCE-4X Anti-Regression
- La carte est l'element MAITRE de MON TERRITOIRE
- Interdiction de supprimer, masquer, remplacer ou degrader la carte
- INTELLIGENCE = superposition flottante, pointer-events-none, jamais substitutive
- Carte reste interactive en tout temps, meme avec INTELLIGENCE ouvert

## Backlog
### P1 — Certification BIONIC V3 (documentation finale M1-M4)
### P1 — Refactoring avance MonTerritoireBionicPage (1553 -> 800 lignes)
### P2 — Migration legacy (RUT-V1, AFFUTS-V1, TRAJETS-V1) — GELE
### P3 — Certification BIONIC V3

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin Architecte:** `Saturn5858*`
