# BIONIC HUNT — PRD.md

## Probleme Original
Application d'analyse ecologique "military-grade" nommee BIONIC HUNT. Developpement dirige par Steeve avec strategie par phases et quality gate BCE-4X.

## Phase Actuelle: Corridors V9 (COMPLETE)
Implementation complete du systeme de generation de corridors ecologiques V9 avec 9 moteurs BIONIC.

## Architecture
- **Frontend**: React + Leaflet + Shadcn/UI
- **Backend**: FastAPI + Python
- **Donnees**: In-memory (pas de MongoDB utilise pour les zones)
- **Weather**: OpenWeatherMap API (cache 60 min)
- **Quality Gate**: BCE-4X avec registre de 16 modules critiques

## Ce qui est implemente

### Phase Corridors V9 (2026-03-12)
1. **9 Moteurs BIONIC** — Logique algorithmique reelle:
   - NutritionEngine: NDVI + sol + fourrage + attractivite par espece
   - DailyRoutineEngine: Rythmes circadiens + fenetres d'activite
   - WeatherEngine V9: OWM live + cache 60 min + BCE-4X blocking
   - DisturbanceEngine: Pression humaine + routes + chasse saisonniere
   - MovementEngineV9: DEM algorithmique Quebec + A* + energie
   - PhenologyEngine: Cycles vegetatifs + NDVI saisonnier
   - TypologyEngine: 5 profils comportementaux par espece/saison
   - LearningEngine: Calibration par observations terrain
   - HabitatEnhancementEngine: Sol + recommandations d'amelioration

2. **Classification V9 — 5 niveaux**:
   - Gris (Potentiel): Score 0-30
   - Jaune (Opportuniste): Score 31-50
   - Orange (Fonctionnel): Score 51-70
   - Rouge (Primaire): Score 71-85
   - Rouge Raye (Critique): Score 86-100

3. **BCE-4X Compliance**:
   - 16 modules critiques enregistres (tous "active")
   - Weather 60-min rule enforced
   - Corridor validator (non-circulaire, perimetre, continuite)
   - 100% compliance rate sur les 3 especes

4. **Corridors par espece**: Endpoint `POST /api/v1/bionic/corridors-v9/by-species`

5. **Score Global V9**: Zones (65%) + Corridors V9 (35%)

6. **Frontend**:
   - CorridorsEcologyPanel avec 9 moteurs BIONIC V9
   - Classification 5 niveaux
   - Score Global V9

### Phases Precedentes (DONE)
- BCE-4X Critical Module Registry
- Right-side panel "Ecological Intelligence Hub"
- Branch compliance checker
- Legacy cleanup, audits, documentation

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
- `GET /api/bce/registry` — Registre modules critiques
- `GET /api/bce/weather-compliance` — Conformite Weather 60 min
- `POST /api/bce/validate-corridors-v9` — Validation corridors V9

## Credentials
- OWM_API_KEY: Dans backend/.env
- Pas d'authentification requise pour utiliser l'app
