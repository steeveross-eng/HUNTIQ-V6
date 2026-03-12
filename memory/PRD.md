# BIONIC HUNT — PRD.md

## Probleme Original
Application d'analyse ecologique "military-grade" nommee BIONIC HUNT. Developpement dirige par Steeve avec strategie par phases et quality gate BCE-4X.

## Phase Actuelle: Corridors V9 — COMPLETE + Visual Overhaul

## Architecture
- **Frontend**: React + Leaflet + Shadcn/UI + Polygon rendering multicouche
- **Backend**: FastAPI + Python + Shapely (buffering geometrique)
- **Donnees**: In-memory (pas de MongoDB pour les zones)
- **Weather**: OpenWeatherMap API (cache 60 min BCE-4X)
- **Quality Gate**: BCE-4X avec 16 modules critiques + 5 regles geometriques

## Ce qui est implemente

### Phase Corridors V9 — Iteration 2 (2026-03-12)

**9 Moteurs BIONIC avec logique algorithmique reelle:**
1. NutritionEngine — NDVI/sol/fourrage/attractivite par espece
2. DailyRoutineEngine — Rythmes circadiens, fenetres d'activite
3. WeatherEngine V9 — OWM live, cache 60min, BCE-4X blocking
4. DisturbanceEngine — Pression humaine, routes, chasse saisonniere
5. MovementEngineV9 — DEM algorithmique Quebec, A*, energie
6. PhenologyEngine — Cycles vegetatifs, NDVI saisonnier
7. TypologyEngine — 5 profils comportementaux
8. LearningEngine — Calibration observations terrain
9. HabitatEnhancementEngine — Sol, recommandations

**Classification V9 — 5 niveaux:**
- Gris (Potentiel): Score 0-30
- Jaune (Opportuniste): Score 31-50
- Orange (Fonctionnel): Score 51-70
- Rouge (Primaire): Score 71-85
- Rouge Raye (Critique): Score 86-100

**Rendu visuel V9 — Rubans ecologiques multicouches:**
- Axe central lisse (Chaikin smoothing)
- 5 bandes polygonales concentriques (Shapely buffer)
- Gradient: gris (halo externe) → jaune → orange → rouge → rouge_raye (coeur)
- Clipping strict Shapely au perimetre 2km2

**Regles BCE-4X nouvelles:**
- BCE-4X-GEOM-001: CorridorShapeViolation (pas circulaire/isotrope)
- BCE-4X-GEOM-002: CorridorContinuityViolation (ruban continu)
- BCE-4X-GEOM-003: CorridorGradientViolation (5 niveaux)
- BCE-4X-CLIP-001: CorridorOutsideActiveArea (hors perimetre = BLOQUE)
- BCE-4X-VISUAL-001: CorridorMigrationLook (centerline lisse)

**Score Global V9:** Zones (65%) + Corridors V9 (35%)

**Corridors par espece:** Endpoint `POST /api/v1/bionic/corridors-v9/by-species`

**Weather 60min:** OWM cache 60min, update < 60min BLOQUE par BCE-4X

### Tests
- Iteration 7: Backend 13/13, Frontend 6/6 — 100% PASS
- Iteration 8: Backend 19/19, Frontend 7/7 — 100% PASS

## Backlog

### P1
- Hunting Path Engine (chemins de chasse optimaux via corridors V9)

### P2
- Learning Engine avance (camera traps, observations terrain)
- Export corridors KML/GeoJSON

### P3
- Multi-territoire comparison
- Analytics dashboard corridors V9

## Endpoints API Cles
- `POST /api/v1/bionic/organic-zones` — Generation zones + corridors V9
- `POST /api/v1/bionic/corridors-v9/by-species` — Corridors par espece
- `GET /api/bce/status` — Statut BCE-4X
- `GET /api/bce/registry` — Registre 16 modules critiques
- `GET /api/bce/weather-compliance` — Conformite Weather 60 min
- `POST /api/bce/validate-corridors-v9` — Validation corridors V9
- `POST /api/auth/login` — Connexion utilisateur

## Credentials
- Steeve.ross@gmail.com / Saturn5858*
- OWM_API_KEY: Dans backend/.env
