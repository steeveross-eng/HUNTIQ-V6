# BIONIC HUNT V8 — PRD (Product Requirements Document)

## Original Problem Statement
Build a sophisticated ecological analysis tool for hunting (BIONIC HUNT), continuing development from the GitHub repo `steeveross-eng/HUNTIQ-V5` (branch `v6_autosave`). The tool integrates ecological knowledge, terrain analysis, and wildlife behavior modeling for Quebec-based hunting.

## Stratégie BIONIC 2000%
Active depuis le 12 mars 2026. 4 phases:
- Phase 1: Geler et sécuriser ✅ (branche BIONIC_LAB_EMERGENT créée)
- Phase 2: Reconstruction propre ✅ (nettoyage, archivage, documentation)
- Phase 3: Certification BIONIC ✅ (8/8 certifications PASS, 100% COMPLIANT)
- Phase 4: Futur (V8.4+) — EN ATTENTE

## Tech Stack
- **Frontend**: React, Leaflet.js, TailwindCSS, Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB

## Modules Certifiés (V8)

### Backend
1. ecological_database_v8.py (1061L) — Base de connaissances 3 espèces
2. ecological_validators_v8.py (557L) — Validateurs BCE
3. ecological_router_v8.py (357L) — API /api/v1/ecological/*
4. corridor_10x.py (733L) — Service corridor WWF
5. zone_engine_core_v2.py (977L) — Zones + corridors 10X
6. bce_ruleset_v8.py (689L) — Règles conformité V8
7. bce_max_4_1.py (418L) — Anti-régression

### Frontend
1. useBionicSession.js (167L) — Session BCE-MAX (source unique)
2. useBionicLayers.js (100L) — Couches sans localStorage legacy
3. useTerritoryAutoLoad.js (264L) — Auto-chargement
4. useZoneOrchestrator.js (241L) — Pipeline zones
5. useSpatialClipping.js (223L) — Clipping 2km
6. MonTerritoireBionicPage.jsx (1506L) — Page principale
7. MapContent.jsx (185L) — Carte avec corridors
8. BionicZone2km.jsx (148L) — Carré 2km
9. CorridorsVisualLayer.jsx (331L) — Rendu corridors
10. EcologicalPanel.jsx (294L) — Panneau écologique

## Key API Endpoints
- `POST /api/v1/bionic/organic-zones` — Zones + corridors
- `GET /api/v1/ecological/species` — Liste espèces V8
- `GET /api/v1/ecological/species/{id}/zones` — Zones par espèce
- `POST /api/v1/ecological/validate` — Validation BCE
- `GET /api/bce/status` — Statut BCE (10 validateurs)

## Phase 4 — Backlog
- P1: Animation vent V8.4 (Canvas 2D)
- P2: Corridors DEM (SRTM elevation)
- P3: Comparaison saisons (split view)
- P4: Panneau droit refactor (après validation audit)
- P5: Phase E — Décommission legacy
- P6: OWM_API_KEY pour météo
