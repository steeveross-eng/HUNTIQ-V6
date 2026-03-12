# BIONIC HUNT V8 — PRD (Product Requirements Document)

## Original Problem Statement
Build a sophisticated ecological analysis tool for hunting (BIONIC HUNT), continuing development from the GitHub repo `steeveross-eng/HUNTIQ-V5` (branch `v6_autosave`). The tool integrates ecological knowledge, terrain analysis, and wildlife behavior modeling for Quebec-based hunting.

## Strategie BIONIC 2000%
Active depuis le 12 mars 2026. 4 phases:
- Phase 1: Geler et securiser DONE
- Phase 2: Reconstruction propre DONE
- Phase 3: Certification BIONIC DONE (8/8 PASS)
- Phase 4: Futur (V8.4+) — Branches creees

## Normes Architecturales BIONIC (BCE Permanent)
- Architecture 100% modulaire
- Aucun croisement de responsabilites entre composants
- Aucun duplicat de logique ou de donnees
- Aucun import inutile ou dormant
- Aucun composant "fourre-tout"
- Aucun couplage fort entre modules
- Aucun artefact legacy conserve sans justification
- Chaque composant: autonome, tracable, testable, remplacable, documente

## Tech Stack
- **Frontend**: React, Leaflet.js, TailwindCSS, Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB

## Completed Tasks

### P0 — A* Corridors (DONE)
- A* pathfinding in corridor_10x.py, 93% optimal paths

### P1 — EcologicalPanel Integration (DONE)
- Refactored to accept dynamic props, zero mock data
- 6/6 tests PASS

### P2 — Right Panel Refactoring (DONE - 12 Mars 2026)
- Fused CorridorStatsPanel + EcologicalPanel into `CorridorsEcologyPanel.jsx`
- Restructured SidePanelZones with new layout:
  1. Score Global V8 (badge BCE)
  2. Zones / Zoom counter
  3. Corridors & Ecologie V8 (unified panel)
  4. Meteo Influence V8.2
  5. Ecological Intelligence Hub (9 engines)
  6. Waypoint Cible + Export
- Created `BionicEngineHub.jsx` with 9 BIONIC engine placeholders
- Cleaned 25+ dead imports from MonTerritoireBionicPage.jsx
- 12/12 tests PASS

### P3 — Phase 4 Branches (DONE)
- Created: feature/vent_animation, feature/corridors_dem, feature/comparaison_saisons

### Phase E — Decommission (PARTIAL)
- Deleted: CorridorsVisualLayer.jsx, CorridorStatsPanel.jsx, EcologicalPanel.jsx
- 8 files remaining (referenced by active routes /map and components)

## Key API Endpoints
- `POST /api/v1/bionic/organic-zones` — Zones + corridors A*
- `GET /api/v1/ecological-knowledge/{species}` — Donnees V8 par espece
- `GET /api/bce/status` — Statut BCE

## Ecological Intelligence Hub — 9 BIONIC Engines (V9-V10)
| # | Engine | Status | Influences |
|---|--------|--------|------------|
| 1 | Nutrition Engine | Planned | scoring, attractivite, zones critiques |
| 2 | Daily Routine Engine | Planned | fenetres activite, prediction deplacements |
| 3 | Weather Engine | Partial | scoring, prediction, comportements saisonniers |
| 4 | Disturbance Engine | Planned | scoring, zones critiques, lecture terrain |
| 5 | Movement Engine | Active | prediction deplacements, priorisation corridors |
| 6 | Phenology Engine | Planned | comportements saisonniers, attractivite |
| 7 | Typology Engine | Planned | prediction deplacements, fenetres activite |
| 8 | Learning Engine | Planned | scoring, recommandations |
| 9 | Habitat Enhancement | Planned | recommandations, lecture terrain |

## Remaining Legacy Files (Phase E incomplete)
- NdviOverlayLayer.jsx, RoutePlannerLayer.jsx, RouteReplayLayer.jsx (WaypointMap/MapPage)
- SeasonalConditionsWidget.jsx, ZoneInfoPanel.jsx (DiagnosticExclusionsPanel)
- SmartMapTooltip.jsx (BionicMicroZones)
- TerritoryShell.jsx, BionicMapOverlay.jsx (WaypointMap/MapPage)

## Known Issues
- OWM_API_KEY manquante (meteo fallback Open-Meteo actif)
