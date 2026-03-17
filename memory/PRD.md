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

### Corrections visuelles + Performance (2026-03-17) — iteration_31 (14/14)
- **Fond orange retire** : Rectangle 2km2 fillOpacity=0, fillColor=transparent
- **Panneau lateral V9→V10** : "Corridors & Ecologie V10", "Score V10", "Classification V10", "9 Moteurs BIONIC V10"
- **SidePanelZones V9→V10** : "Score Global V10", "V10 + Meteo", "Cache V10"
- **Performance optimisations:**
  - Backend: Douglas-Peucker simplification (_simplify_coords) — GeoJSON payload reduit
  - Frontend: Caching global (Map avec limite 20 entrees)
  - Frontend: Throttling 200ms debounce sur fetchAndRender
  - Frontend: Pre-rendu des styles (precomputedStyles useMemo)
  - Frontend: Douglas-Peucker client-side (simplifyPath)
  - Frontend: Z-index deterministe (FAIBLE → CRITIQUE → zones)
- Tests: Backend 8/8 (100%), Frontend 6/6 (100%), 0 regression

## Fichiers Cles
```
Backend:
  /app/backend/modules/corridors_v10/   — 11 fichiers Python

Frontend:
  /app/frontend/src/components/territoire/
    BionicLegend.jsx                   — Legende 3X normative
    BionicCorridorsV10Layer.jsx        — Couche Leaflet + cache + throttle + DP
    BionicScoreHeatmap.jsx             — Heatmap score consolide
    CorridorsEcologyPanel.jsx          — Panneau lateral V10
  /app/frontend/src/components/territoire/map/
    MapContent.jsx                     — Rectangle transparent + couches
  /app/frontend/src/components/territoire/ui/
    SidePanelZones.jsx                 — Score Global V10
```

## Backlog
### P0 — HABITAT-V1 (sur commande — prochaine)
### P1 — RUT-V1, AFFUTS-V1, TRAJETS-V1 (sequentiel)
### P1 — Integration score consolide CORRIDORS-V10 dans heatmap
### P2 — Certification Finale BIONIC V3
### P3 — Phase 4: Integration transversale (BLOQUEE)

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin:** `Saturn5858*`
