# BIONIC V3 — PRD (Product Requirements Document)

## Probleme Original
Application BIONIC V3 — Outil d'analyse ecologique full-stack pour la gestion de la faune au Quebec.

## Architecture
- **Frontend:** React + Leaflet/react-leaflet
- **Backend:** FastAPI (Python)
- **Database:** MongoDB

## Taches Completees (resume)
### iterations 22-56 (voir historique complet)

### OPTIMISATION TRAILS CRITIQUES (2026-03-18) — iteration_57 (100%)
- **CRITIQUE**: weight 4px, color #FF4500, glow externe (8px op0.15 + 4px op0.35), glow interne (2px #FFF op0.25)
- **Animation pulsation**: CSS keyframes corridorCritiquePulse 1.5s ease-in-out infinite (20 paths actifs)
- 0 regression

### HEATMAP V10 100% TRANSPARENT (2026-03-18) — iteration_55 (100%)
- **Modes Lite/Pro ABOLIS** — aucune reference dans UI ni code
- **ConsolidatedHeatmapLayer.jsx**: composant data-only, zero rendu graphique (pas de useMap, pas de gradient)
- **Toggle Corridors V10 ON/OFF**: dans Overlays (Zones popover), backend include_corridors param
- **Indicateur**: "Score V10" + score + "(sans corridors)" si toggle OFF
- 0 regression: ZONES 12, V10 corridors 15/14.1km, ALIMENTATION badge 4

## Elements SUPPRIMES/DEPLACES (ADMIN ONLY)
- Onglet LAYERS, CORRIDORS V10, Point Alimentation secondaire V1
- Labels DOMINANT/SECONDAIRE/TERTIAIRE, Mode SECRET, Popup zone analyse
- Modes Heatmap Lite/Pro (ABOLIS)

## API Endpoints
### CORRIDORS-V10
- POST /api/v10/corridors/analyze-full
### ALIMENTATION-V2
- POST /api/v2/alimentation/analyze
### SCORE CONSOLIDE
- GET /api/v1/score-consolide/heatmap (params: lat, lng, species, month, grid_size, include_corridors)
- GET /api/v1/score-consolide/point

## Backlog
### P0 — Validation finale utilisateur ALIMENTATION-V2 + Heatmap transparente
### P2 — RUT-V1, AFFUTS-V1, TRAJETS-V1 (GELE jusqu'a certification)
### P3 — Certification Finale BIONIC V3
### P3 — Refactoring MonTerritoireBionicPage.jsx

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin Architecte:** `Saturn5858*`
