# BIONIC HUNT — PRD.md

## Phase Actuelle: Corridors V9 — Audit Visual COMPLETE

## Architecture
- **Frontend**: React + Leaflet (Pane z-index 650) + Shadcn/UI
- **Backend**: FastAPI + Python + Shapely (buffer/clip proportionnel)
- **Weather**: OpenWeatherMap API (cache 60 min BCE-4X)
- **Quality Gate**: BCE-4X — 9 regles + 4 couverture UI

## Implemente (2026-03-12)

### 9 Moteurs BIONIC (logique algorithmique reelle)
NutritionEngine, DailyRoutineEngine, WeatherEngine V9 (OWM 60min),
DisturbanceEngine, MovementEngineV9 (DEM Quebec), PhenologyEngine,
TypologyEngine, LearningEngine, HabitatEnhancementEngine

### Visual V9 — Rubans proportionnels
Largeurs PROPORTIONNELLES a la longueur du corridor:
| Bande | Ratio | Min | Max | Couleur | fillOpacity |
|-------|-------|-----|-----|---------|-------------|
| gris | 5.5% | 25m | 120m | #9E9E9E | 0.20 |
| jaune | 3.8% | 18m | 80m | #FFC107 | 0.35 |
| orange | 2.4% | 12m | 50m | #FF9800 | 0.50 |
| rouge | 1.4% | 7m | 30m | #F44336 | 0.65 |
| rouge_raye | 0.7% | 4m | 15m | #B71C1C | 0.80 |

### Couches corrigees
- MovementCorridorsLayer (LEGACY V1): SUPPRIME definitvement
- Toggle "Deplacements V1": SUPPRIME de l'UI
- Corridors V9 renderus sur Pane z-index 650 (AU-DESSUS des zones)

### BCE-4X Couverture Complete
| Regle | Status |
|-------|--------|
| GEOM-001 | PASS |
| GEOM-002 | PASS |
| GEOM-003 | PASS |
| CLIP-001 | PASS |
| VISUAL-001 | PASS |
| PIPE-001 | PASS |
| UI-001 | PASS |
| UI-002 | PASS |
| UI-003 | PASS |

### Tests
- Iteration 9: 34/34 backend, 8/8 frontend — PASS

## Backlog
### P1
- Hunting Path Engine
### P2
- Learning Engine avance, Export KML/GeoJSON
### P3
- Multi-territoire, Analytics dashboard

## Credentials
- Steeve.ross@gmail.com / Saturn5858*
- OWM_API_KEY dans backend/.env
