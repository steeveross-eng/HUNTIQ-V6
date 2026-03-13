# BIONIC HUNT — PRD.md

## Branche: steve-max — RECONSTRUCTION TOTALE

## Architecture
- **Frontend**: React + Leaflet (3 Panes: zones z-400, corridors z-650, hunting path z-700) + Shadcn/UI
- **Backend**: FastAPI + Python + Shapely + 9 Moteurs BIONIC + Hunting Path Engine
- **Weather**: OpenWeatherMap API (cache 60 min BCE-4X)
- **Quality Gate**: BCE-4X — 14 regles (color+geometry+runtime)

## Implemente

### Phase 1: Resonance Magnetique (2026-03-12)
- PURGE Legacy MovementCorridorsLayer
- CONTRAT COULEURS NORMATIVES 15 couleurs
- ISOLATION PANES Leaflet (zones/corridors)
- Labels V9 dans panneau

### Phase 1b: P0+P1+P4 (2026-03-13)
- **P0 Continuite corridors**: densification (30m spacing), Chaikin smoothing
- **P1 Reduction visuelle 50%**: gris max 36m, jaune max 24m, fillOpacity: jaune=0.15, orange=0.22
- **P4 Palette 1:1**: Zone legend dans panneau lateral utilisant LAYER_TYPES importes de BionicZoneService.js

### Phase 2: P2+P6 (2026-03-13)
- **P2 Zones cles**: 11 types detectes (rut, repos, alimentation, corridors, peuplements, hydro, pentes, orientation, affuts, trajets, altitude)
- **P6 BCE-4X**: COR-006, VIS-007, ZONE-008, COLOR-010 — tous PASS

### Phase 3: P3+P5 (2026-03-13)
- **P3 Trajet de chasse**: Moteur TSP nearest-neighbor pondere par vent, 44 points, 5 waypoints strategiques (depart, saline, cache, alimentation_sec, fin)
- **P5 Amenagement 2km**: 8 sections (saline, alimentation_sec, cache, trajet, vents, zones, corridors, plan_action)
- Endpoints: POST /api/v1/bionic/hunting-path, POST /api/v1/bionic/amenagement-report
- Frontend: HuntingPathLayer (orange dashed polyline z-700), AmenagementPanel, toggle visibility

## BCE-4X Rules (14 total)
| Rule | Name | Status |
|------|------|--------|
| COLOR-001 | ZoneColorContract | PASS |
| COLOR-002 | PanelLegendConsistency | PASS |
| COLOR-003 | CorridorPaletteIsolation | PASS |
| COLOR-010 | PaletteStrictMatch | PASS |
| UI-004 | ZoneCorridorMixViolation | PASS |
| UI-005 | NoLegacyMovementCorridors | PASS |
| UI-006 | NoTooltipSuppression | PASS |
| GEOM-004 | CorridorBoundingBoxCompliance | PASS |
| GEOM-005 | CorridorWidthNormalization | PASS |
| CLIP-002 | PostSmoothingClipEnforcement | PASS |
| PIPE-002 | FrontendReconstructionGuard | PASS |
| COR-006 | CorridorContinuity | PASS |
| VIS-007 | CorridorVisualBalance | PASS |
| PATH-009 | HuntingPathValidity | PASS (runtime) |

## Tests
- Iteration 12: Backend 12/12 PASS, Frontend 10/10 PASS (P0-P5 all VERIFIED)
- Iteration 11: Backend 11/11 PASS (geometry)
- Iteration 10: Backend 12/12 PASS (color)

## API Endpoints
- POST /api/v1/bionic/organic-zones — zones + corridors V9
- POST /api/v1/bionic/hunting-path — trajet de chasse optimal
- POST /api/v1/bionic/amenagement-report — rapport amenagement 2km complet
- POST /api/bce/validate-color-contract — 7 regles
- POST /api/bce/validate-geometry-compliance — 3 regles
- POST /api/bce/validate-corridors-runtime — runtime validation

## Backlog
### P0
- Validation utilisateur Steeve
### P1
- Learning Engine avance
### P2
- Export KML/GeoJSON, Multi-territoire
### P3
- Analytics dashboard

## Credentials
- Steeve.ross@gmail.com / Saturn5858*
- OWM_API_KEY dans backend/.env
