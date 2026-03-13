# BIONIC HUNT — PRD.md

## Branche: steve-max — RECONSTRUCTION TOTALE

## Architecture
- **Frontend**: React + Leaflet (3 Panes: zones z-400, corridors z-650, hunting path z-700) + Shadcn/UI
- **Backend**: FastAPI + Python + Shapely + 9 Moteurs BIONIC V1 + 12 Moteurs BIONIC V2 + Hunting Path Engine
- **Weather**: OpenWeatherMap API (cache 60 min BCE-4X)
- **Quality Gate**: BCE-4X — 16 regles (color+geometry+runtime+continuity+visual)

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
- **P3 Trajet de chasse**: Moteur TSP nearest-neighbor ecologique pur (vent supprime du pipeline), 44 points, 5 waypoints strategiques
- **P5 Amenagement 2km**: 8 sections (saline, alimentation_sec, cache, trajet, vents_ref_engine4, zones, corridors, plan_action)
- Endpoints: POST /api/v1/bionic/hunting-path, POST /api/v1/bionic/amenagement-report
- Frontend: HuntingPathLayer (orange dashed polyline z-700), AmenagementPanel, toggle visibility

### STEVE-MAX++ Phase (2026-03-13)
- **P0 Suppression vent pipeline**: Logique vent supprimee du TSP et amenagement, Wind Intelligence Engine (#4) maintenu comme moteur isole
- **P0 Reduction visuelle 40% supplementaire**: BAND_RATIO: gris=22m, jaune=14m, orange=9m, rouge=5m, rouge_raye=3m
- **P0 Continuite corridors graph-based**: Algorithme graph detect dead-ends, genere connecting segments, topologie 100%
- **12 BIONIC V2 Engines integres** (backend compute + API + frontend display):
  1. Behavior Engine (patterns comportementaux)
  2. KeyZone Engine V2 (detection zones cles)
  3. Food Deficit Engine (deficit alimentaire NDVI)
  4. Wind Intelligence Engine (analyse vent strategique)
  5. Terrain Engine (pentes, marchabilite, couvert)
  6. Human Pressure Engine (pression anthropique)
  7. Corridor Continuity Engine (reparation topologique)
  8. Global Attractiveness Engine (score global 2km)
  9. Action Plan Engine (plan d'action chasse)
  10. Predictive AI Engine (predictions probabilistes)
  11. BCE-4X Compliance Engine (validation conformite)
  12. Rendering Engine (optimisation rendu)
- **BCE-4X-COR-006**: CorridorNetworkContinuity validation
- **BCE-4X-VIS-007**: CorridorVisualBalance validation

## BCE-4X Rules (16 total)
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
| COR-006 | CorridorNetworkContinuity | PASS |
| VIS-007 | CorridorVisualBalance | PASS |
| PATH-009 | HuntingPathValidity | PASS (runtime) |
| ENG-V2-001 | 12EnginesActiveStatus | PASS |
| ENG-V2-002 | 12EnginesComputeScores | PASS |

## Tests
- Iteration 13: Backend 18/18 PASS, Frontend 12/12 engines displayed (STEVE-MAX++ all VERIFIED)
- Iteration 12: Backend 12/12 PASS, Frontend 10/10 PASS (P0-P5 all VERIFIED)

## API Endpoints
- POST /api/v1/bionic/organic-zones — zones + corridors V9
- POST /api/v1/bionic/hunting-path — trajet de chasse optimal (vent supprime)
- POST /api/v1/bionic/amenagement-report — rapport amenagement 2km complet
- GET /api/v1/bionic/engines-v2/status — statut des 12 moteurs V2
- POST /api/v1/bionic/engines-v2/compute — calcul scores 12 moteurs V2
- POST /api/bce/validate-color-contract — 7 regles couleur
- POST /api/bce/validate-geometry-compliance — 3 regles geometrie
- POST /api/bce/validate-corridors-runtime — runtime validation
- POST /api/bce/validate-corridor-continuity — COR-006
- POST /api/bce/validate-visual-balance — VIS-007

## Backlog
### P0
- Validation utilisateur Steeve
### P1
- Learning Engine avance
- Export GeoJSON avec continuity metadata
### P2
- Export KML/GeoJSON, Multi-territoire
### P3
- Analytics dashboard

## Credentials
- Steeve.ross@gmail.com / Saturn5858*
- OWM_API_KEY dans backend/.env
