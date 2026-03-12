# BIONIC HUNT — PRD.md

## Probleme Original
Application d'analyse ecologique "military-grade" nommee BIONIC HUNT. Developpement dirige par Steeve avec strategie par phases et quality gate BCE-4X.

## Phase Actuelle: Corridors V9 — Visual Overhaul COMPLETE

## Architecture
- **Frontend**: React + Leaflet (Pane z-index 650) + Shadcn/UI
- **Backend**: FastAPI + Python + Shapely (buffer/clip)
- **Weather**: OpenWeatherMap API (cache 60 min BCE-4X)
- **Quality Gate**: BCE-4X — 9 regles geometriques + 4 couverture UI

## Implemente — Phase Corridors V9 (2026-03-12)

### 9 Moteurs BIONIC (logique algorithmique reelle)
1. NutritionEngine — NDVI/sol/fourrage
2. DailyRoutineEngine — Rythmes circadiens
3. WeatherEngine V9 — OWM live + cache 60min
4. DisturbanceEngine — Pression humaine
5. MovementEngineV9 — DEM Quebec + A*
6. PhenologyEngine — Cycles vegetatifs
7. TypologyEngine — 5 profils comportementaux
8. LearningEngine — Observations terrain
9. HabitatEnhancementEngine — Sol/recommandations

### Visual V9 — Rubans multicouches
| Bande | Couleur | Largeur | fillOpacity |
|-------|---------|---------|-------------|
| gris (halo) | #9E9E9E | 311m | 0.25 |
| jaune | #FFC107 | 222m | 0.40 |
| orange | #FF9800 | 155m | 0.55 |
| rouge | #F44336 | 89m | 0.65 |
| rouge_raye | #B71C1C | 44m | 0.80 |

### BCE-4X Couverture Complete
- GEOM-001 (shape), GEOM-002 (continuite), GEOM-003 (gradient)
- CLIP-001 (perimetre), VISUAL-001 (migration look)
- PIPE-001 (alignement donnees), UI-001 (5 bandes), UI-002 (couleurs), UI-003 (isolation)

### Tests
- Iteration 7: 13/13 backend, 6/6 frontend — PASS
- Iteration 8: 19/19 backend, 7/7 frontend — PASS
- Iteration 9: 34/34 backend, 8/8 frontend — PASS

## Backlog
### P1
- Hunting Path Engine
### P2
- Learning Engine avance
- Export corridors KML/GeoJSON
### P3
- Multi-territoire comparison

## Credentials
- Steeve.ross@gmail.com / Saturn5858*
- OWM_API_KEY dans backend/.env
