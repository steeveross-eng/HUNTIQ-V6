# BIONIC V3 — PRD (Product Requirements Document)

## Probleme Original
Application BIONIC V3 — Outil d'analyse ecologique full-stack pour la gestion de la faune au Quebec.

## Architecture
- **Frontend:** React + Leaflet/react-leaflet + leaflet.heat
- **Backend:** FastAPI (Python)
- **Database:** MongoDB

## Taches Completees (resume)
### iterations 22-55 (voir historique complet)

### HEATMAP CONSOLIDEE CORRIDORS-V10 (2026-03-18) — iteration_56 (100%)
- **Backend score_consolide.py**: 5 moteurs integres avec ponderations:
  - alimentation: 25%, repos: 20%, corridors_v10: 25%, alimentation_v2: 10%, pression: 20%
- **_corridor_score_for_point**: Score de connectivite reseau, transit peripherique, terrain, ecologie
- **Grille 20x20** (400 points): Score avg ~57/100, classe MODERE-BON
- **Frontend ConsolidatedHeatmapLayer.jsx**: leaflet.heat avec gradient bleu>vert>jaune>rouge
- **Toggle** dans ZONES popover (Overlays > Heatmap V10)
- **Indicateur** "Corridors-V10 integres X/100" en bas-gauche de la carte
- **Couche base**: Heatmap sous zones/corridors/salines (pas d'obstruction)
- **Exclusions eau**: score=0, classe=EXCLU conforme BCE-4X
- Tests: Backend 12/12, Frontend 100% (iteration_53.json), 0 regression

## Elements SUPPRIMES/DEPLACES (ADMIN ONLY)
- Onglet LAYERS, CORRIDORS V10, Point Alimentation secondaire V1
- Labels DOMINANT/SECONDAIRE/TERTIAIRE, Mode SECRET, Popup zone d'analyse

## Architecture de controle STEEVE-MAX (FINAL)
```
ZONES > ALIMENTATION(X) > POINTS CHAUDS > SEUIL > CURSEUR > ADMIN(Shield)

ZONES popover Overlays:
  - Vent
  - Exclusions
  - Heatmap V10 (score consolide multi-moteurs)
```

## API Endpoints
### CORRIDORS-V10
- POST /api/v10/corridors/analyze-full
### ALIMENTATION-V2
- POST /api/v2/alimentation/analyze (center_lat, center_lng, species, month, max_salines)
### SCORE CONSOLIDE
- GET /api/v1/score-consolide/heatmap?lat=X&lng=Y&species=S&month=M&grid_size=N
- GET /api/v1/score-consolide/point?lat=X&lng=Y&species=S&month=M

## Backlog
### P2 — RUT-V1, AFFUTS-V1, TRAJETS-V1
### P3 — Certification Finale BIONIC V3
### P3 — Refactoring MonTerritoireBionicPage.jsx

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin Architecte:** `Saturn5858*`
