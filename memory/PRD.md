# BIONIC HUNT — PRD.md

## Phase Actuelle: STEVE-MAX++ — Resonance Magnetique Complete

## Architecture
- **Frontend**: React + Leaflet (Panes isoles: zones z-400, corridors z-650) + Shadcn/UI
- **Backend**: FastAPI + Python + Shapely (buffer/clip proportionnel)
- **Weather**: OpenWeatherMap API (cache 60 min BCE-4X)
- **Quality Gate**: BCE-4X — 9 regles moteurs + 6 regles Color Contract + 4 couverture UI
- **Branche**: steve-max (reconstruction totale)

## Implemente (2026-03-12)

### STEVE-MAX: Resonance Magnetique Complete
1. **PURGE Legacy MovementCorridorsLayer**: Import et usage supprimes de MapContent.jsx ET WaypointMap.jsx
2. **CONTRAT COULEURS NORMATIVES**: 15 couleurs fixes par layer_id — identiques backend, carte, panneau
3. **ISOLATION PANES Leaflet**: Zones dans bionic-zones-pane (z-400), Corridors dans corridors-v9-pane (z-650)
4. **BionicAntiDoublesGuard NETTOYÉ**: CSS ne masque plus .leaflet-tooltip-pane ni .leaflet-popup-pane
5. **Labels V9**: Panneau lateral affiche "V9 + Meteo", "Pipeline V9 + Meteo V8.2.1 + 9 Moteurs BIONIC"
6. **6 nouvelles regles BCE-4X Color Contract**:
   - BCE-4X-COLOR-001 ZoneColorContract — PASS
   - BCE-4X-COLOR-002 PanelLegendConsistency — PASS
   - BCE-4X-COLOR-003 CorridorPaletteIsolation — PASS
   - BCE-4X-UI-004 ZoneCorridorMixViolation — PASS
   - BCE-4X-UI-005 NoLegacyMovementCorridors — PASS
   - BCE-4X-UI-006 NoTooltipSuppression — PASS
7. **Endpoint BCE**: POST /api/bce/validate-color-contract

### Palette Normative Zones
| Layer | Couleur | Hex |
|-------|---------|-----|
| habitats | Emeraude | #10B981 |
| rut | Rose-Rouge | #FF4D6D |
| repos | Violet | #8B5CF6 |
| alimentation | Vert vif | #22C55E |
| corridors | Cyan | #06B6D4 |
| peuplements | Vert foret | #15803D |
| ndvi | Vert clair | #66BB6A |
| pentes | Orange terre | #FF7043 |
| orientation | Bleu | #2196F3 |
| ensoleillement | Or | #FCD34D |
| salines | Jaune | #FFFF00 |
| affuts | Ambre | #F5A623 |
| trajets | Orange | #FF9800 |
| altitude | Gris acier | #78909C |

### Palette Normative Corridors V9
| Bande | Couleur | Hex | fillOpacity |
|-------|---------|-----|-------------|
| gris | Gris | #9E9E9E | 0.20 |
| jaune | Jaune | #FFC107 | 0.35 |
| orange | Orange | #FF9800 | 0.50 |
| rouge | Rouge | #F44336 | 0.65 |
| rouge_raye | Rouge fonce | #B71C1C | 0.80 |

### 9 Moteurs BIONIC (logique algorithmique reelle)
NutritionEngine, DailyRoutineEngine, WeatherEngine V9 (OWM 60min),
DisturbanceEngine, MovementEngineV9 (DEM Quebec), PhenologyEngine,
TypologyEngine, LearningEngine, HabitatEnhancementEngine

### Tests
- Iteration 10 (STEVE-MAX): Backend 12/12 PASS, Frontend 11/11 PASS
- BCE-4X Color Contract: 6/6 PASS
- Iteration 12 (pre-STEVE-MAX): 34/34 backend, 8/8 frontend

## Backlog
### P0
- Validation utilisateur: confirmer que les visuels correspondent aux attentes
### P1
- Hunting Path Engine
### P2
- Learning Engine avance, Export KML/GeoJSON
### P3
- Multi-territoire, Analytics dashboard

## Credentials
- Steeve.ross@gmail.com / Saturn5858*
- OWM_API_KEY dans backend/.env
