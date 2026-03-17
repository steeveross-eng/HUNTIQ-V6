# BIONIC V3 — PRD (Product Requirements Document)

## Probleme Original
Application BIONIC V3 — Outil d'analyse ecologique full-stack pour la gestion de la faune au Quebec.

## Architecture
- **Frontend:** React + Leaflet/react-leaflet
- **Backend:** FastAPI (Python)
- **Database:** MongoDB

## Taches Completees

### Securite & Consolidation — iteration_22/23
### Audit Ecologique Global — iteration_24
### Bouton Carte + Deep Link — iteration_24 (10/10)
### ENGINE ALIMENTATION-V1 + REPOS-V1 + Wapiti — iteration_25
### PLAN DE MATCH STEEVE-MAX v1 + Heatmap Officiel — iteration_26 (29/29 + 9/9)
### Correction BCE-4X: Affuts sur eau — iteration_27
### ENGINE CORRIDORS-V10 — iteration_28 (31/31)
### Norme CORRIDOR-V1/V10 + Integration Mon Territoire — iteration_29 (26/26)
### Legende Mon Territoire VERSION 3X — iteration_30 (37/37)
### Corrections V9→V10 labels + Performance — iteration_31 (14/14)

### Fond orange retire + Suppression V9 (2026-03-17) — iteration_32 (22/22)
- **BionicScoreHeatmap RETIRE** : import et rendu supprimes de MapContent.jsx
- **V9 corridors DESACTIVES** : BionicMicroZones recoit corridors=[] et showCorridors=false
- **Centre Circle transparent** : fillOpacity=0, fillColor=transparent
- **Rectangle 2km2 transparent** : fillOpacity=0, fillColor=transparent
- **Panneau lateral collapse** : "Corridors & Ecologie V10" (ligne 113 corrigee)
- **Resultat** : Terrain satellite 100% visible, seuls corridors V10 normatifs rendent
- Tests: Backend 8/8 + Frontend 14/14 = 22/22 (100%), 0 regression

### Raffinements visuels BCE-4X (2026-03-17) — iteration_33 (13/13)
- **Zones polygonales**: fillOpacity calibree 35% (hover 40%), contour -25% plus mince, contour 18% plus sombre (darkenColor factor=0.82)
- **CRITIQUE corridors**: couleur interne #B80000, contour #660000, micro-hachures diagonales (dashArray '4,3'), densite +20%
- **MAJEUR corridors**: rouge pur #FF0000, contour #CC0000, aucun pattern, epaisseur identique a CRITIQUE
- **BCE-4X compliance**: Aucun glow/halo/degradé sur aucun corridor, contours sombres pour tous les niveaux
- **V9 purge definitive**: Code V9CorridorRibbon, CorridorLine, CORRIDOR_STYLES supprimes de BionicMicroZones
- **Props nettoyees**: corridors=[] et showCorridors=false retires de MapContent → BionicMicroZones
- Tests: Frontend 13/13 (100%), 0 regression

### Anomalie critique V9/V10 — Purge V9 + Polygones V10 (2026-03-17) — iteration_34 (23/23)
- **Backend**: engine.py — Ajout generation polygones V10 (BFS flood-fill + convex hull Andrew)
  - Fonctions ajoutees: _generate_zone_polygons(), _convex_hull(), _score_cell_for_zone_type()
  - GeoJSON zones: Point → Polygon (64 polygones, 0 points)
  - Parametres: max_radius=10, max_cells=60, threshold=25% center_score
  - Chaque polygone ~300m de cote, terrain-aware, deterministe
- **Frontend BionicCorridorsV10Layer.jsx**: Rendu polygones V10 avec normes BCE-4X
  - fillOpacity 0.35 (hover 0.40), contour darkenHex(0.82), weight 1.5
  - Points centraux synchronises (center_lat/center_lng)
  - Tooltips sur hover avec type + score
- **Frontend MapContent.jsx**: BionicMicroZones (V9) SUPPRIME DEFINITIVEMENT
  - Import retire, rendu retire, seul BionicCorridorsV10Layer rend les zones
- Tests: Backend 8/8 + Frontend 15/15 = 23/23 (100%), 0 regression

## Etat actuel Mon Territoire
- Fond: terrain satellite 100% visible (aucune couche opaque)
- Corridors: V10 uniquement (palette normative CRITIQUE→FAIBLE, BCE-4X: aucun glow)
- CRITIQUE: #B80000 + contour #660000 + micro-hachures
- MAJEUR: #FF0000 + contour #CC0000, aucun pattern
- Zones: **POLYGONES V10** (64 polygones generes par flood-fill + convex hull)
  - 4 types: alimentation (vert), repos (bleu), rut (orange), eau (teal)
  - Transparence calibree 35% (hover 40%), contours assombris 18%
  - Points centraux synchronises
  - Polygones cliquables avec tooltips
  - ZERO zones V9 restantes
- Legende: 3X normative (3 blocs, compteurs, toggles)
- Panneau lateral: entierement V10
- Toolbar: "CORRIDORS V10" avec toggle
- BCE-4X: applique a la racine de tous les modules et moteurs

## API Endpoints CORRIDORS-V10
- POST /api/v10/corridors/analyze
- POST /api/v10/corridors/analyze-full (GeoJSON normatif simplifie)
- GET /api/v10/corridors/multi
- GET /api/v10/corridors/profiles
- GET /api/v10/corridors/profile/{species}
- GET /api/v10/corridors/documentation

## Backlog
### P1 — Integration score consolide CORRIDORS-V10 dans heatmap
### P2 — HABITAT-V1 (prochaine commande utilisateur)
### P2 — RUT-V1, AFFUTS-V1, TRAJETS-V1 (sequentiel, sur commande)
### P3 — Certification Finale BIONIC V3
### P3 — Phase 4: Integration transversale (BLOQUEE — necessite tous les moteurs V1)

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin:** `Saturn5858*`
