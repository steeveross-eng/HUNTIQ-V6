# BIONIC V3 — PRD (Product Requirements Document)

## Probleme Original
Application BIONIC V3 — Outil d'analyse ecologique full-stack pour la gestion de la faune au Quebec.

## Architecture
- **Frontend:** React + Leaflet/react-leaflet
- **Backend:** FastAPI (Python)
- **Database:** MongoDB

## Taches Completees (resume)
### iterations 22-43 (voir historique complet)
### OPTIMISATION UX STEEVE-MAX V2 — iteration_44 (100%)
### MODE ZONE D'ANALYSE + PERFORMANCE V3 — iteration_45 (100%)
### EXTENSION UX — Sous-elements granulaires — iteration_46 (100%)
### FUSION UX STEEVE-MAX + BUG FIX corridors — iteration_47 (100%)
### SUPPRESSION CORRIDORS V10 — iteration_48a (button removed)

### ENGINE ALIMENTATION-V2 (2026-03-18) — iteration_48 (100%)
- **Backend module complet**: `/backend/modules/alimentation_v2/`
  - `engine.py`: Analyse territoriale + calcul salines + recommandations
  - `terrain.py`: Analyse algorithmique terrain (relief, eau, foret, sol, nutriments)
  - `salines.py`: Optimiseur salines (eau, couvert, pente, accessibilite, securite)
  - `nutrition.py`: Base statique nutritionnelle (CERF, ORIGNAL, OURS, WAPITI, DINDON)
  - `router.py`: POST /api/v2/alimentation/analyze + GET /api/v2/alimentation/species
- **Frontend salines**: AlimentationV2Layer.jsx — points jaunes (#FFD700) dans zone 2km
- **Panneau nutritionnel**: Panneau flottant avec carences, aliments, proteines, oligo-elements
- **Onglet ALIMENTATION**: Toolbar tab avec toggles Salines + Recommandations
- **Sites permanents SUPPRIMES**: alimentation + salines dans BANNED_LAYERS (useBionicLayers)
- **Especes supportees**: Cerf, Orignal, Ours noir, Wapiti, Dindon sauvage
- Tests: Backend 19/19 + Frontend 100% (iteration_48.json), 0 regression

## Architecture de controle STEEVE-MAX (FINAL)
```
ZONES (unique centre de controle)
├── Zones DOMINANT (7 sous-elements)
├── Corridors SECONDAIRE (4 sous-elements)
├── Points TERTIAIRE (8 sous-elements)
└── Overlays (Vent + Exclusions)

ALIMENTATION (V2)
├── Salines (toggle)
└── Recommandations (panneau flottant)

POINTS CHAUDS (filtrage comportemental)
```

## Onglets SUPPRIMES (INTERDICTION de recreer)
- LAYERS — supprime iteration_47
- CORRIDORS V10 — supprime iteration_48a

## API Endpoints
### CORRIDORS-V10
- POST /api/v10/corridors/analyze-full
- GET /api/v10/corridors/multi | profiles | documentation

### ALIMENTATION-V2
- POST /api/v2/alimentation/analyze
- GET /api/v2/alimentation/species

## Normes Actives
- **STEEVE-MAX**: ZONES unique centre, hierarchie Zones > Corridors > Points
- **BCE-4X**: 16 zones, 64 centres, zero modification geometrique, firewall 13 tests
- **EXTREME**: CRITIQUE = +40% weight, opacity 0.75
- **V10 permanent**: showCorridors = true
- **ALIMENTATION-V2**: Salines algorithmiques, nutrition statique, sites permanents interdits

## Backlog
### P1 — Integration score consolide CORRIDORS-V10 dans heatmap
### P2 — RUT-V1, AFFUTS-V1, TRAJETS-V1
### P3 — Certification Finale BIONIC V3
### P3 — Refactoring engine.py en modules specialises

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin:** `Saturn5858*`
