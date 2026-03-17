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
### Corrections V9->V10 labels + Performance — iteration_31 (14/14)
### Fond orange retire + Suppression V9 (2026-03-17) — iteration_32 (22/22)
### Raffinements visuels BCE-4X (2026-03-17) — iteration_33 (13/13)
### Anomalie critique V9/V10 — Purge V9 + Polygones V10 (2026-03-17) — iteration_34 (23/23)
### NORME STEEVE-MAX — Polygones organiques BIONIC (2026-03-17) — iteration_35 (35/35)
### Standard Visuel STEEVE-MAX (2026-03-17) — iteration_36 (16/16)
### STEEVE-MAX Dimension + Fusion + Adoucissement (2026-03-17) — iteration_37 (25/25)
### Directive Superposition Transparente STEEVE-MAX (2026-03-17) — iteration_38 (26/26)
### Correction Contours Organiques — Pipeline Buffer Union (2026-03-17) — iteration_39 (21/21)
### COMMANDE FINALE — Hierarchie Visuelle STEEVE-MAX (2026-03-17) — iteration_40 (17/17)
### STEVE-MAX-MULTI — Consolidation 7 Engines (2026-03-17) — iteration_41 (21/21)
### Optimisation Comportementale + Reduction Points (2026-03-17) — iteration_42 (100%)
### UX STEEVE-MAX — Onglets ZONES + POINTS CHAUDS (2026-03-17) — iteration_43
### OPTIMISATION UX STEEVE-MAX V2 (2026-03-17) — iteration_44 (100%)
### MODE ZONE D'ANALYSE + PERFORMANCE V3 (2026-03-17) — iteration_45 (100%)
### EXTENSION UX STEEVE-MAX — Sous-elements granulaires (2026-03-17) — iteration_46 (100%)

### BUG FIX: Corridors disparaissant (2026-03-17) — iteration_47
- **Cause**: Prop `center` (objet {lat,lng}) recree a chaque re-render parent
  → cascade dependances: center → analysisBox → renderData → fetchAndRender → cleanup clearLayers
  → couches perpetuellement effacees avant affichage
- **Fix 1**: analysisBox useMemo depend de center?.lat, center?.lng (primitives) au lieu de center (objet)
- **Fix 2**: fetchAndRender decouple de renderData via renderDataRef (ref stable)
- **Fix 3**: fetchAndRender ne depend plus de renderData, skip si key identique ET layers existent
- **Fix 4**: Re-render visuel (filtres/toggles) gere par effect separe dependant de renderData
- Resultat: Corridors, zones et points visibles correctement

## API Endpoints CORRIDORS-V10
- POST /api/v10/corridors/analyze
- POST /api/v10/corridors/analyze-full (GeoJSON normatif simplifie)
- GET /api/v10/corridors/multi
- GET /api/v10/corridors/profiles
- GET /api/v10/corridors/profile/{species}
- GET /api/v10/corridors/documentation

## Normes Actives
- **STEEVE-MAX**: Hierarchie visuelle Zones > Corridors > Points, palette normative, polygones organiques
- **BCE-4X**: 16 zones, 64 centres, zero modification geometrique, firewall 13 tests
- **Corridors EXTREME**: CRITIQUE (score 85-100) = surbrillance +40% weight, opacity 0.75, jamais attenue
- **Vent V8.3.B**: +15% intensite visuelle (fleches + particules)
- **Zone d'analyse**: 2km x 2km, attenuation automatique hors-zone
- **Sous-elements**: 7 zones + 4 corridors + 8 points = 19 filtres individuels

## Backlog
### P1 — Integration score consolide CORRIDORS-V10 dans heatmap
### P2 — HABITAT-V1 (prochaine commande utilisateur)
### P2 — RUT-V1, AFFUTS-V1, TRAJETS-V1 (sequentiel, sur commande)
### P3 — Certification Finale BIONIC V3
### P3 — Phase 4: Integration transversale (BLOQUEE — necessite tous les moteurs V1)
### P3 — Refactoring engine.py en modules specialises

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin:** `Saturn5858*`
