# BIONIC HUNT V8 — PRD (Product Requirements Document)

## Original Problem Statement
Build a sophisticated ecological analysis tool for hunting (BIONIC HUNT). The tool integrates ecological knowledge, terrain analysis, and wildlife behavior modeling for Quebec-based hunting.

## Strategie BIONIC 2000%
- Phase 1-3: DONE (Freeze, Reconstruct, Certify)
- Phase 4: Branches creees, implementation future

## Normes Architecturales BIONIC (BCE Permanent)
- Architecture 100% modulaire
- Aucun croisement de responsabilites
- Aucun duplicat, import inutile, hardcoding
- Chaque composant: autonome, tracable, testable, remplacable

## Tech Stack
- **Frontend**: React, Leaflet.js, TailwindCSS, Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB

## Completed Tasks

### P0 — A* Corridors (DONE)
### P1 — EcologicalPanel Integration (DONE, 6/6 tests)
### P2 — Right Panel Refactoring (DONE, 12/12 tests)
- CorridorsEcologyPanel.jsx fusionne
- BionicEngineHub.jsx (9 moteurs)
- SidePanelZones restructure
- 25+ imports morts nettoyes

### P3 — Phase 4 Branches (DONE)
- feature/vent_animation, feature/corridors_dem, feature/comparaison_saisons

### Phase E — Decommission (PARTIAL, 3/12 fichiers)

### BCE-4X Corridors Integration (DONE — 12 Mars 2026)
- Validateur corridor_v9.py cree avec 8 regles
- 21/21 tests pytest PASS
- Endpoint POST /api/bce/validate-corridors operationnel
- 64 violations detectees sur V8 (40 critical, 24 medium)
- Status: BLOCKED — confirme necessite Phase V9
- Rapport complet: /app/docs/RAPPORT_BCE_4X_CORRIDORS.md

## Current Priority: Phase Corridors V9
EN ATTENTE de validation utilisateur apres rapport BCE-4X.
Corrections a appliquer:
1. Supprimer subscores hardcodes (terrain=65, habitat=70, zone_score=50)
2. Appeler enrich_corridor() dans le pipeline
3. Calculer subscores dynamiquement
4. Activer clipping post-generation
5. Integrer 9 moteurs BIONIC dans scoring corridors

## Key API Endpoints
- `POST /api/v1/bionic/organic-zones` — Zones + corridors A*
- `GET /api/v1/ecological-knowledge/{species}` — Donnees V8
- `GET /api/bce/status` — Statut BCE + BCE-4X corridors
- `POST /api/bce/validate-corridors` — Validation live corridors

## Ecological Intelligence Hub — 9 BIONIC Engines (V9-V10)
| # | Engine | Status |
|---|--------|--------|
| 1 | Nutrition Engine | Planned |
| 2 | Daily Routine Engine | Planned |
| 3 | Weather Engine | Partial |
| 4 | Disturbance Engine | Planned |
| 5 | Movement Engine | Active (A*) |
| 6 | Phenology Engine | Planned |
| 7 | Typology Engine | Planned |
| 8 | Learning Engine | Planned |
| 9 | Habitat Enhancement | Planned |

## Known Issues
- OWM_API_KEY manquante (meteo fallback actif)
- 64 violations BCE-4X corridors (bloquant, V9 requis)
