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
- IntelligenceDashboard.jsx integre comme OVERLAY dans MonTerritoireBionicPage
- 3 modes: GUIDE PRO, SCIENTIFIQUE, TERRAIN
- 6 blocs: Analytics, Conditions, Mode actif, Forecast, Plan Maitre, Donnees brutes
- Tableau solunaire LUNASOLCAL complet
- AnalysisSidePanel supprime definitivement
- BCE-4X: 23/23 | STEEVE-MAX: 12/12

### RESTAURATION CARTE + ANTI-REGRESSION (2026-03-18) — VALIDE 100%
- Carte TOUJOURS dans le DOM (jamais supprimee, jamais masquee)
- Intelligence = superposition modale (absolute z-900 dans le conteneur carte)
- Toolbar accessible en tout temps
- Transition carte <-> intelligence sans perte d'etat (23 zones, 19 corridors preserves)
- BCE-4X R3/R7/R11/R14/R18/R21 tous valides

## API Endpoints V3
- GET /api/v3/engines/registry, /score-point, /score-grid, /{name}/score, /validate
- GET /api/v3/intelligence/summary, /forecast, /plan
- GET /api/v3/intelligence/solunar, /guide-pro, /scientifique
- GET /api/v3/species

## Pages Frontend
- /analytics — Score consolide, domaines, recommandations (auto-adaptatif)
- /forecast — Variation 12 mois, saisons, best/worst
- /plan-maitre — Actions priorisees (CRITIQUE -> FAIBLE)
- /territoire — MON TERRITOIRE (carte + overlays + INTELLIGENCE overlay)

## Composants Intelligence
- IntelligenceDashboard.jsx — Overlay, selecteur de mode, 6 blocs
- ModeGuidePro.jsx — Solunaire + fenetres chasse + plan approche
- ModeScientifique.jsx — Ponderations, formules, metadonnees BCE-4X
- ModeTerrain.jsx — Vue simplifiee mobile/hors reseau
- SolunarChart.jsx — Courbe SVG LUNASOLCAL 24h

## Regles d'integration (BCE-4X Anti-Regression)
- La carte est l'element MAITRE de MON TERRITOIRE
- Interdiction de supprimer, masquer, remplacer ou degrader la carte
- Toute integration = superposee, modale ou adjacente, JAMAIS substitutive
- Passage entre modes instantane, sans perte d'etat ou d'overlays

## Backlog
### P0 — Synchronisation bi-directionnelle avancee (intelligence -> carte: highlight zones)
### P1 — Refactoring MonTerritoireBionicPage (reduction de ~2100 lignes)
### P1 — Certification BIONIC V3 (documentation finale M1-M4)
### P2 — Migration legacy (RUT-V1, AFFUTS-V1, TRAJETS-V1) — GELE
### P3 — Certification BIONIC V3

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin Architecte:** `Saturn5858*`
