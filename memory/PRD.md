# BIONIC V3 — PRD (Product Requirements Document)

## Probleme Original
Application BIONIC V3 — Outil d'analyse ecologique full-stack pour la gestion de la faune au Quebec.

## Architecture
- **Frontend:** React + Leaflet/react-leaflet
- **Backend:** FastAPI (Python)
- **Database:** MongoDB

## Taches Completees (resume)
### iterations 22-48a (voir historique complet)
### ENGINE ALIMENTATION-V2 — iteration_48 (100%)
### BUG FIX Tab + Salines Visibility — iteration_49 (100%)
### DIRECTIVE ESPECES STEEVE-MAX — iteration_50 (100%)

### OPTIMISATION SALINES + DIVERSIFICATION SPATIALE (2026-03-18) — iteration_51 (100%)
- **Diversification spatiale**: Algorithme grille 4x4 (16 candidats) + selection gloutonne avec min_distance 300m
- **Selecteur intelligent 1-4 salines**:
  - 1 saline: Meilleur spot absolu (score max)
  - 2 salines: Couverture maximale (2 axes)
  - 3 salines: Triangulation optimale
  - 4 salines: Quadrillage optimal (4 zones cardinales)
- **Rendu visuel**: Selectionnees = jaune (#FFD700, r=9), Candidats = gris (#9CA3AF, r=5, opacity 0.35)
- **Badge UX**: ALIMENTATION (X) dans la toolbar, masque pour OURS/DINDON
- **Resume zone**: Format "X/Y candidats" (ex: "4/16 candidats")
- **Backend**: compute_salines V2 avec grid_candidates + _select_with_min_distance + rank
- **Suppression V1**: alimentation_sec SUPPRIME de hunting_path.py + AmenagementPanel.jsx + HuntingPathLayer.jsx + BANNED_LAYERS
- Tests: Backend 16/16 + Frontend 100% (iteration_51.json), 0 regression

## Elements SUPPRIMES (INTERDICTION de recreer)
- Onglet LAYERS — supprime iteration_47
- Onglet CORRIDORS V10 — supprime iteration_48a
- Point "Alimentation secondaire" (V1) — supprime iteration_51
- Couches BIONIC alimentation/salines/alimentation_sec (V1) — dans BANNED_LAYERS

## Architecture de controle STEEVE-MAX (FINAL)
```
ZONES (unique centre de controle)
--- Zones DOMINANT (7 sous-elements)
--- Corridors SECONDAIRE (4 sous-elements)
--- Points TERTIAIRE (8 sous-elements)
--- Overlays (Vent + Exclusions)

ALIMENTATION (V2) — Position: apres ZONES, avant POINTS CHAUDS
--- Badge (X) = nombre salines actives
--- Master toggle (Alimentation V2)
--- Salines (toggle, disabled pour OURS/DINDON)
--- Selecteur 1-4 salines (strategies intelligentes)
--- Recommandations (panneau flottant)

POINTS CHAUDS (filtrage comportemental)
```

## API Endpoints
### CORRIDORS-V10
- POST /api/v10/corridors/analyze-full
### ALIMENTATION-V2
- POST /api/v2/alimentation/analyze (params: center_lat, center_lng, species, month, max_salines)
- GET /api/v2/alimentation/species

## Normes Actives
- STEEVE-MAX: ZONES unique centre, diversification spatiale 300m min
- BCE-4X: 16 zones, 64 centres, zero modification geometrique
- ALIMENTATION-V2: 16 candidats grille, selection gloutonne, OURS/DINDON desactives

## Backlog
### P1 — Integration score consolide CORRIDORS-V10 dans heatmap
### P2 — RUT-V1, AFFUTS-V1, TRAJETS-V1
### P3 — Certification Finale BIONIC V3
### P3 — Refactoring MonTerritoireBionicPage.jsx

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin:** `Saturn5858*`
