# BIONIC V3 — PRD (Product Requirements Document)

## Probleme Original
Application BIONIC V3 — Outil d'analyse ecologique full-stack pour la gestion de la faune au Quebec.

## Architecture
- **Frontend:** React + Leaflet/react-leaflet + leaflet.heat
- **Backend:** FastAPI (Python)
- **Database:** MongoDB

## Taches Completees (resume)
### iterations 22-56 (voir historique complet)

### OPTIMISATION TRAILS CRITIQUES (2026-03-18) — iteration_57 (100%)
- **CRITIQUE**: weight 4px, color #FF4500, glow externe (8px op0.15 + 4px op0.35), glow interne (2px #FFF op0.25)
- **Animation pulsation**: CSS keyframes corridorCritiquePulse 1.5s ease-in-out infinite (20 paths actifs)
- **Tooltip CRITIQUE**: Badge #FF4500 "Critique", score gras 800, fleche directionnelle visible
- **MODERE**: weight 2px, color #FFA500 (orange)
- **FAIBLE**: weight 1px, color #FFD27F (or pale)
- **MAJEUR**: weight 2.5px, color #FF0000
- **FORT**: weight 2px, color #FF8C00
- 0 regression: ZONES 23, V10 19 corridors, Heatmap V10, ALIMENTATION 4 badge

### HEATMAP V10 LITE vs PRO (2026-03-18) — iteration_54 (100%)
- **Mode Lite** (usager standard): opacite 0.05-0.4, palette pastel (bleu/vert/beige doux), radius 40, blur 30
- **Mode Pro** (Admin Architecte): opacite 0.45, palette thermique haute-contraste (bleu→vert→jaune→rouge)
- **Toggle comparaison**: Corridors V10 ON/OFF dans Overlays, backend include_corridors param
- **Backend**: compute_heatmap_grid(include_corridors=True/False) — ponderation dynamique
- **Indicateur**: "Heatmap Lite" / "Heatmap Pro" + "(sans V10)" si corridors desactives
- 0 regression: ZONES 12, V10 corridors 15/14.1km, ALIMENTATION badge 4

## Elements SUPPRIMES/DEPLACES (ADMIN ONLY)
- Onglet LAYERS, CORRIDORS V10, Point Alimentation secondaire V1
- Labels DOMINANT/SECONDAIRE/TERTIAIRE, Mode SECRET, Popup zone analyse

## API Endpoints
### CORRIDORS-V10
- POST /api/v10/corridors/analyze-full
### ALIMENTATION-V2
- POST /api/v2/alimentation/analyze
### SCORE CONSOLIDE
- GET /api/v1/score-consolide/heatmap (params: lat, lng, species, month, grid_size, include_corridors)
- GET /api/v1/score-consolide/point

## Backlog
### P0 — Validation finale utilisateur ALIMENTATION-V2 + Heatmap Lite
### P2 — RUT-V1, AFFUTS-V1, TRAJETS-V1 (GELE jusqu'a certification)
### P3 — Certification Finale BIONIC V3
### P3 — Refactoring MonTerritoireBionicPage.jsx

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin Architecte:** `Saturn5858*`
