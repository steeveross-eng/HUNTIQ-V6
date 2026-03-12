# BIONIC HUNT V8 — PRD (Product Requirements Document)

## Original Problem Statement
Build a sophisticated ecological analysis tool for hunting (BIONIC HUNT), continuing development from the GitHub repo `steeveross-eng/HUNTIQ-V5` (branch `v6_autosave`). The tool integrates ecological knowledge, terrain analysis, and wildlife behavior modeling for Quebec-based hunting.

## Strategie BIONIC 2000%
Active depuis le 12 mars 2026. 4 phases:
- Phase 1: Geler et securiser DONE (branche BIONIC_LAB_EMERGENT creee)
- Phase 2: Reconstruction propre DONE (nettoyage, archivage, documentation)
- Phase 3: Certification BIONIC DONE (8/8 certifications PASS, 100% COMPLIANT)
- Phase 4: Futur (V8.4+) — EN ATTENTE

## Tech Stack
- **Frontend**: React, Leaflet.js, TailwindCSS, Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB

## Modules Certifies (V8)

### Backend
1. ecological_database_v8.py — Base de connaissances 3 especes
2. corridor_10x.py — Service corridor WWF + A* pathfinding
3. zone_engine_core_v2.py — Zones + corridors 10X
4. bce_max_4_1.py — Anti-regression

### Frontend
1. useBionicSession.js — Session BCE-MAX (source unique)
2. useZoneOrchestrator.js — Pipeline zones
3. MonTerritoireBionicPage.jsx — Page principale
4. MapContent.jsx — Carte avec couches
5. EcologicalPanel.jsx — Panneau ecologique V8 (DYNAMIQUE, zero mock)
6. SidePanelZones.jsx — Panneau lateral carte (integre EcologicalPanel)

## Key API Endpoints
- `POST /api/v1/bionic/organic-zones` — Zones + corridors A*
- `GET /api/v1/ecological-knowledge/{species}` — Donnees V8 par espece
- `GET /api/bce/status` — Statut BCE

## Completed Tasks (12 Mars 2026)
- P0: A* Corridors integration DONE
- P1: EcologicalPanel refactoring + integration DONE (6/6 tests PASS)
- P2 Pre-requis: Analyse 360 complete Mon Territoire DONE (voir /app/docs/ANALYSE_360_MON_TERRITOIRE_V8.md)

## Current Priorities
- **P2**: Refactoring panneau droit (apres validation analyse par utilisateur)
- **P3**: Branches Phase 4 (feature/vent_animation, feature/corridors_dem, feature/comparaison_saisons)
- **Phase E**: Decommission 12 fichiers legacy identifies

## Backlog — Ecological Intelligence Hub (V9-V10)
1. BIONIC Nutrition Engine — Sol, Nutriments, Fourrage, Attractivite
2. BIONIC Daily Routine Engine — Rythmes journaliers
3. BIONIC Weather Engine — Vent, pression, temperature, precipitations
4. BIONIC Disturbance Engine — Routes, chalets, odeurs, pression humaine
5. BIONIC Movement Engine — Corridors A* + DEM + risques + nutrition
6. BIONIC Phenology Engine — Debourrement, floraison, senescence
7. BIONIC Individual Typology Engine — Profils comportementaux
8. BIONIC Learning Engine — Ajustement modeles selon observations
9. BIONIC Habitat Enhancement Engine — Analyse sol + recommandations

## Known Issues
- OWM_API_KEY manquante (meteo fallback Open-Meteo actif)
