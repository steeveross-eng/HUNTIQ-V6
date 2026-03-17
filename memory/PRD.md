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
- Module independant `/app/backend/modules/corridors_v10/`
- A* pathfinding sur grille 80x80 (25m/cellule)

### Norme CORRIDOR-V1/V10 + Integration Mon Territoire — iteration_29 (26/26)
- Classification normative 5 niveaux
- Scoring enrichi (ECL, micro-topo, nourriture, refuge, zones tampons)
- Profils especes enrichis + COR-006 explicite
- Frontend BionicCorridorsV10Layer.jsx avec palette normative

### Legende Mon Territoire VERSION 3X (2026-03-17) — iteration_30 (37/37)
- **3 blocs normatifs:**
  - A. Zones ecologiques (6 items): Habitat, Rut, Repos, Alimentation, Humides, Forets matures
  - B. Corridors V10 (5 niveaux): CRITIQUE #CC0000, MAJEUR #FF0000, FORT #FF8C00, MODERE #FFD700, FAIBLE #BFBFBF
  - C. Facteurs environnementaux (7 items): NDVI, Pentes, Orientation, Ensoleillement, Altitude, Pression, Hydrologie
- **Compteurs dynamiques** par niveau de corridor (CRITIQUE:13, MAJEUR:149, FORT:27)
- **Filtrage espece** avec label dynamique (TOUTES ESPECES / Orignal / etc.)
- **Chaque item cliquable** (toggle visible/masque) + tooltips
- **Blocs collapsibles** avec hierarchie Zones > Corridors > Facteurs
- **Norme BCE-4X + Steeve-MAX** en footer
- **Toolbar** mise a jour: "CORRIDORS V10" (ex-V9)
- **Flux donnees:** V10 API → BionicCorridorsV10Layer → onDataLoaded → state → BionicLegend
- Tests: Frontend 37/37 (100%), 0 regression

## Fichiers Cles
```
Backend:
  /app/backend/modules/corridors_v10/   — 11 fichiers Python (engine complet)

Frontend:
  /app/frontend/src/components/territoire/
    BionicLegend.jsx              — Legende 3X normative (3 blocs)
    BionicCorridorsV10Layer.jsx   — Couche Leaflet corridors
    BionicScoreHeatmap.jsx        — Heatmap score consolide
  /app/frontend/src/components/territoire/map/
    MapContent.jsx                — Integration couches carte
  /app/frontend/src/pages/
    MonTerritoireBionicPage.jsx   — Page principale Mon Territoire
```

## API Endpoints CORRIDORS-V10
- POST /api/v10/corridors/analyze
- POST /api/v10/corridors/analyze-full (GeoJSON normatif)
- GET /api/v10/corridors/multi
- GET /api/v10/corridors/profiles
- GET /api/v10/corridors/profile/{species}
- GET /api/v10/corridors/documentation

## Backlog
### P0 — Moteurs (sur commande)
1. ~~CORRIDORS-V10~~ COMPLETE
2. HABITAT-V1
3. RUT-V1
4. AFFUTS-V1
5. TRAJETS-V1

### P1 — Integration score consolide CORRIDORS-V10 (sur commande)
### P2 — Certification Finale BIONIC V3
### P3 — Phase 4: Integration transversale (BLOQUEE)

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin:** `Saturn5858*`
