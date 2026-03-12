# BIONIC HUNT — PRD.md

## Phase Actuelle: STEVE-MAX++ — Corridors 2km Compliance + Reduction 40%

## Architecture
- **Frontend**: React + Leaflet (Panes isoles: zones z-400, corridors z-650) + Shadcn/UI
- **Backend**: FastAPI + Python + Shapely (clip→smooth→buffer→reclip pipeline)
- **Weather**: OpenWeatherMap API (cache 60 min BCE-4X)
- **Quality Gate**: BCE-4X — 9 regles moteurs + 6 regles Color Contract + 4 regles Geometry + 4 couverture UI
- **Branche**: steve-max (reconstruction totale)

## Implemente

### STEVE-MAX P0: Resonance Magnetique (2026-03-12)
1. PURGE Legacy MovementCorridorsLayer: import + usage supprimes de MapContent.jsx ET WaypointMap.jsx
2. CONTRAT COULEURS NORMATIVES: 15 couleurs fixes par layer_id
3. ISOLATION PANES Leaflet: zones z-400, corridors z-650
4. BionicAntiDoublesGuard: CSS ne masque plus tooltips/popups
5. Labels V9: panneau "V9 + Meteo", "Pipeline V9 + 9 Moteurs BIONIC"
6. 6 regles BCE-4X Color Contract: COLOR-001/002/003, UI-004/005/006

### STEVE-MAX P1: Corridors Hors Limites + Reduction 40% (2026-03-12)
1. **CLIPPING STRICT 2km**: Perimetre d'analyse calcule depuis waypoint_center (1000m rayon)
   - Pipeline: CLIP centerline → SMOOTH (Chaikin) → BUFFER bandes → RE-CLIP au 2km
   - 0/3467 coordonnees hors limites (GEOM-004 PASS)
2. **REDUCTION GLOBALE 40%**: BAND_RATIO x0.6
   - gris: ratio 0.033, max 72m (was 0.055/120m)
   - jaune: ratio 0.023, max 48m (was 0.038/80m)
   - orange: ratio 0.014, max 30m (was 0.024/50m)
   - rouge: ratio 0.008, max 18m (was 0.014/30m)
   - rouge_raye: ratio 0.004, max 9m (was 0.007/15m)
3. **Frontend filter**: corridors avec inPerimeter=false ou hasBands=false exclus du rendu
4. **4 nouvelles regles BCE-4X Geometry**:
   - BCE-4X-GEOM-004 CorridorBoundingBoxCompliance — PASS
   - BCE-4X-GEOM-005 CorridorWidthNormalization — PASS
   - BCE-4X-CLIP-002 PostSmoothingClipEnforcement — PASS
   - BCE-4X-PIPE-002 FrontendReconstructionGuard — PASS

### Pipeline V9 Complet (9 moteurs BIONIC)
NutritionEngine, DailyRoutineEngine, WeatherEngine V9 (OWM 60min),
DisturbanceEngine, MovementEngineV9 (DEM Quebec), PhenologyEngine,
TypologyEngine, LearningEngine, HabitatEnhancementEngine

### Tests
- Iteration 11 (STEVE-MAX Geometry): Backend 11/11 PASS, Frontend 6/6 PASS
- Iteration 10 (STEVE-MAX Color): Backend 12/12 PASS, Frontend 11/11 PASS

## BCE-4X Rules Summary (10 rules total)
| Rule | Name | Status |
|------|------|--------|
| COLOR-001 | ZoneColorContract | PASS |
| COLOR-002 | PanelLegendConsistency | PASS |
| COLOR-003 | CorridorPaletteIsolation | PASS |
| UI-004 | ZoneCorridorMixViolation | PASS |
| UI-005 | NoLegacyMovementCorridors | PASS |
| UI-006 | NoTooltipSuppression | PASS |
| GEOM-004 | CorridorBoundingBoxCompliance | PASS |
| GEOM-005 | CorridorWidthNormalization | PASS |
| CLIP-002 | PostSmoothingClipEnforcement | PASS |
| PIPE-002 | FrontendReconstructionGuard | PASS |

## Backlog
### P0
- Validation utilisateur: confirmer visuels
### P1
- Hunting Path Engine
### P2
- Learning Engine avance, Export KML/GeoJSON
### P3
- Multi-territoire, Analytics dashboard

## Credentials
- Steeve.ross@gmail.com / Saturn5858*
- OWM_API_KEY dans backend/.env

## Key API Endpoints
- POST /api/v1/bionic/organic-zones — zones + corridors V9
- POST /api/bce/validate-color-contract — 6 regles couleur
- POST /api/bce/validate-geometry-compliance — 3 regles geometrie
- POST /api/bce/validate-corridors-runtime — validation runtime GEOM-004/005
