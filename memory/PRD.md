# BIONIC HUNT V8 — PRD (Product Requirements Document)

## Original Problem Statement
Build a sophisticated ecological analysis tool for hunting (BIONIC HUNT), continuing development from the GitHub repo `steeveross-eng/HUNTIQ-V5` (branch `v6_autosave`). The tool integrates ecological knowledge, terrain analysis, and wildlife behavior modeling for Quebec-based hunting.

## Core Requirements
1. **2km² Zone**: Permanent spatial reference box centered on active waypoint
2. **V8 Ecological Knowledge Base**: In-memory database for Moose, Deer, Bear with habitats, behaviors, algorithmic criteria
3. **Corridors 10X**: Advanced displacement corridors with WWF classification, connecting functional zones
4. **BCE-MAX x4.1**: Military-grade compliance engine — ANTI-REGRESSION, ANTI-DEPLOYMENT, ANTI-BYPASS
5. **Full Session Persistence**: Complete auto-restore of position, zoom, species, layers, waypoint, context
6. **Performance**: Zone loading < 0.5s via caching
7. **UI/UX**: Clean right panel, EcologicalPanel integration, no visual clutter

## Tech Stack
- **Frontend**: React, Leaflet.js, TailwindCSS, Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Maps**: Leaflet with satellite/topographic tiles

## What's Been Implemented

### Completed (as of March 11, 2026)
- [x] Project setup from GitHub (v6_autosave branch)
- [x] 2km² square zone component (BionicZone2km.jsx)
- [x] V8 ecological knowledge base + API endpoints
- [x] Zone clipping to 2km² box (useSpatialClipping.js)
- [x] Auto-load zones on page load (useZoneOrchestrator)
- [x] Removal of StructureContrastLayer "red lines"
- [x] **P0: Full Session Persistence (BCE-MAX x4.1)**
  - Unified `useBionicSession.js` as SINGLE source of truth
  - Removed duplicate localStorage from `useBionicLayers.js`
  - Removed legacy `USER_CONTEXT_KEY` system
  - Saves/restores: position, zoom, species, ALL layers, waypointId, classificationToggles, biologicalSeason, visual options
  - Debounced save (300ms), 30-day TTL, validation on load
- [x] **P1: Corridors 10X Integration (Backend + Frontend)**
  - `_generate_corridors_10x()` in zone_engine_core_v2.py
  - Connects functional zones (alimentation, repos, rut, affuts, trajets, etc.)
  - Bezier curve interpolation for natural paths
  - WWF classification (macro, biological, conservation corridors)
  - Color/width/opacity styling per corridor type
  - Intra-layer fallback when single zone type exists
  - Frontend rendering via BionicMicroZones + V7CorridorLine
  - CorridorStatsPanel displays corridor statistics

### Testing Status
- Testing agent iteration 3: All major tests PASS
- Session persistence: PASS (save + restore all fields)
- Corridors generation: PASS
- Corridors display: PASS
- Auto-load zones: PASS
- 13 layers active by default: PASS
- 2km box visible: PASS

## P0/P1/P2 Feature Backlog

### P2 — API Bug Fixes
- Weather API returns 500 (OWM_API_KEY missing) — non-blocking
- `/api/v1/ecological/species/orignal/zones/alimentation` returns 500

### P3 — Right Panel Audit & Refactor
- AUDIT_COMPLET.md created, waiting user validation
- Integrate EcologicalKnowledgePanel.jsx into panel

### P4 — Phase E: Legacy Decommission
- Identify and remove unused legacy files
- Pending user approval of file list

### P5 — Future Features
- Wind Animation (V8.4) — Canvas 2D layer
- BCE-MAX backend validation endpoints
- Corridor DEM enhancement (SRTM elevation data)

## Key Architecture Files
- `frontend/src/hooks/useBionicSession.js` — Session persistence (BCE-MAX x4.1)
- `frontend/src/hooks/useBionicLayers.js` — Layer state management
- `frontend/src/hooks/useZoneOrchestrator.js` — Zone loading pipeline
- `frontend/src/pages/MonTerritoireBionicPage.jsx` — Main page
- `backend/modules/bionic_engine_p0/services/zone_engine_core_v2.py` — Zone + corridor generation
- `backend/modules/bionic_engine_p0/services/corridor_10x.py` — Corridor 10X service

## Key API Endpoints
- `POST /api/v1/bionic/organic-zones` — Generate zones + corridors
- `GET /api/v8/ecological-knowledge/{species}` — V8 ecological data
- `GET /api/v1/bce/status-v8` — BCE status
