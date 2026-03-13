# BIONIC HUNT — PRD.md

## Branche: steve-max — RECONSTRUCTION TOTALE

## Architecture
- **Frontend**: React + Leaflet (3 Panes: zones z-400, corridors z-650, hunting path z-700) + Shadcn/UI
- **Backend**: FastAPI + Python + Shapely + 9 Moteurs BIONIC V1 + 12 Moteurs BIONIC V2 + Hunting Path Engine
- **Weather**: OpenWeatherMap API (cache 60 min BCE-4X)
- **Quality Gate**: BCE-4X — 16+ regles (color+geometry+runtime+continuity+visual)

## Implemente

### Phase 1: Resonance Magnetique (2026-03-12)
- PURGE Legacy MovementCorridorsLayer
- CONTRAT COULEURS NORMATIVES 15 couleurs
- ISOLATION PANES Leaflet (zones/corridors)
- Labels V9 dans panneau

### Phase 1b: P0+P1+P4 (2026-03-13)
- P0 Continuite corridors: densification (30m spacing), Chaikin smoothing
- P1 Reduction visuelle 50%
- P4 Palette 1:1: Zone legend dans panneau lateral

### Phase 2: P2+P6 (2026-03-13)
- P2 Zones cles: 11 types detectes
- P6 BCE-4X: COR-006, VIS-007, ZONE-008, COLOR-010

### Phase 3: P3+P5 (2026-03-13)
- P3 Trajet de chasse: Moteur TSP nearest-neighbor ecologique pur (vent supprime du pipeline)
- P5 Amenagement 2km: 8 sections

### STEVE-MAX++ Phase (2026-03-13)
- P0 Suppression vent pipeline: Logique vent supprimee du TSP et amenagement
- P0 Reduction visuelle 40% + elargissement +20%
- P0 Continuite corridors graph-based: Algorithme detect dead-ends + connecting segments
- 12 BIONIC V2 Engines integres (backend compute + API + frontend display)

### Corrections Finales (2026-03-13)
- **Corridors +20%**: BAND_RATIO gris=26m, jaune=17m, orange=11m, rouge=6m, rouge_raye=4m
- **Harmonisation couleurs**: 15 couleurs identiques dans BionicMicroZones, BionicZoneService, bionicModules
- **Continuite 100%**: ensure_corridor_network_continuity() dans pipeline zone_engine_core_v2
- **BCE-4X COR-006**: CorridorNetworkContinuity validation endpoint
- **BCE-4X VIS-007**: CorridorVisualBalance validation endpoint
- **GEOM-005 updated**: Validates +20% widening

## 12 BIONIC V2 Engines
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

## Tests
- Iteration 14: Backend 20/20 PASS, Frontend all UI verified (Corrections Finales VERIFIED)
- Iteration 13: Backend 18/18 PASS, Frontend 12/12 engines (V2 Integration VERIFIED)
- Iteration 12: Backend 12/12 PASS, Frontend 10/10 PASS (P0-P5 VERIFIED)

## API Endpoints
- POST /api/v1/bionic/organic-zones
- POST /api/v1/bionic/hunting-path
- POST /api/v1/bionic/amenagement-report
- GET /api/v1/bionic/engines-v2/status
- POST /api/v1/bionic/engines-v2/compute
- POST /api/bce/validate-color-contract
- POST /api/bce/validate-geometry-compliance
- POST /api/bce/validate-corridors-runtime
- POST /api/bce/validate-corridor-continuity
- POST /api/bce/validate-visual-balance

## Backlog
### P0 - Validation utilisateur Steeve
### P1 - Export GeoJSON avec continuity metadata
### P2 - Export KML, Multi-territoire, Analytics dashboard

## Credentials
- Steeve.ross@gmail.com / Saturn5858*
- OWM_API_KEY dans backend/.env
