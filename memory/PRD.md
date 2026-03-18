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
### Fond orange retire + Suppression V9 — iteration_32 (22/22)
### Raffinements visuels BCE-4X — iteration_33 (13/13)
### Anomalie critique V9/V10 — Purge V9 + Polygones V10 — iteration_34 (23/23)
### NORME STEEVE-MAX — Polygones organiques BIONIC — iteration_35 (35/35)
### Standard Visuel STEEVE-MAX — iteration_36 (16/16)
### STEEVE-MAX Dimension + Fusion + Adoucissement — iteration_37 (25/25)
### Directive Superposition Transparente STEEVE-MAX — iteration_38 (26/26)
### Correction Contours Organiques — Pipeline Buffer Union — iteration_39 (21/21)
### COMMANDE FINALE — Hierarchie Visuelle STEEVE-MAX — iteration_40 (17/17)
### STEVE-MAX-MULTI — Consolidation 7 Engines — iteration_41 (21/21)
### Optimisation Comportementale + Reduction Points — iteration_42 (100%)
### UX STEEVE-MAX — Onglets ZONES + POINTS CHAUDS — iteration_43
### OPTIMISATION UX STEEVE-MAX V2 — iteration_44 (100%)
### MODE ZONE D'ANALYSE + PERFORMANCE V3 — iteration_45 (100%)
### EXTENSION UX — Sous-elements granulaires — iteration_46 (100%)
### BUG FIX: Corridors disparaissant — iteration_47a (ref cascade fix)

### FUSION UX STEEVE-MAX (2026-03-18) — iteration_47 (100%)
- **LAYERS supprime**: Bouton LAYERS retire de la toolbar, JSX et logique UI retires
  - Controles vent + exclusions migres dans ZONES > section Overlays
- **ZONES = centre de controle unique STEEVE-MAX**:
  - Section 1: Zones DOMINANT (7 sous-elements)
  - Section 2: Corridors SECONDAIRE (4 sous-elements)
  - Section 3: Points TERTIAIRE (8 sous-elements)
  - Section 4: Overlays (Vent directionnel + modes, Exclusions)
- **Zero duplication fonctionnelle**
- **Zero modification geometrique**, conformite BCE-4X totale
- Tests: Frontend 100% (iteration_47.json), 0 regression

## Architecture de controle STEEVE-MAX
```
ZONES (unique centre de controle)
├── Zones DOMINANT
│   ├── Alimentation, Repos, Rut, Habitat, Affuts, Trajets
│   └── Multi-Engines (override: tout afficher)
├── Corridors SECONDAIRE
│   ├── Normaux (FAIBLE/MODERE), Intenses (FORT/MAJEUR)
│   ├── EXTREME (CRITIQUE, surbrillance +40%)
│   └── Saisonniers (override: tout afficher)
├── Points TERTIAIRE
│   ├── Alimentation, Rut, Repos, Trajets, Affuts, Habitat
│   ├── Centroides (mode normal)
│   └── Individuels (mode chauds)
└── Overlays
    ├── Vent directionnel (Minimaliste / Particules)
    └── Exclusions
```

## API Endpoints CORRIDORS-V10
- POST /api/v10/corridors/analyze
- POST /api/v10/corridors/analyze-full
- GET /api/v10/corridors/multi
- GET /api/v10/corridors/profiles
- GET /api/v10/corridors/profile/{species}
- GET /api/v10/corridors/documentation

## Normes Actives
- **STEEVE-MAX**: Hierarchie Zones > Corridors > Points, palette normative
- **BCE-4X**: 16 zones, 64 centres, zero modification geometrique, firewall 13 tests
- **EXTREME**: CRITIQUE = +40% weight, opacity 0.75, jamais attenue
- **Zone d'analyse**: 2km x 2km, attenuation hors-zone
- **LAYERS INTERDIT**: Onglet LAYERS supprime definitivement

## Backlog
### P1 — Integration score consolide CORRIDORS-V10 dans heatmap
### P2 — HABITAT-V1
### P2 — RUT-V1, AFFUTS-V1, TRAJETS-V1
### P3 — Certification Finale BIONIC V3
### P3 — Refactoring engine.py en modules specialises

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin:** `Saturn5858*`
