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

### SUPPRESSION CORRIDORS V10 (2026-03-18) — iteration_48 (100%)
- **Bouton CORRIDORS V10 retire** de la toolbar (JSX + separator supprimes)
- **showCorridors = true permanent** : V10 layer toujours actif, plus de toggle externe
- **Controle unique via ZONES** > Corridors SECONDAIRE (4 sous-elements)
- **Boutons supprimes definitivement** :
  - LAYERS (iteration_47)
  - CORRIDORS V10 (iteration_48)
- Toolbar finale: PRINT → SPLIT → CARTE → OBSERVATION → ANALYSE → LOCK → ZONES → POINTS CHAUDS → SEUIL → CURSEUR → FAIBLE
- Tests: Screenshot verification PASS, 0 regression

## Architecture de controle STEEVE-MAX (FINAL)
```
ZONES (unique centre de controle)
├── Zones DOMINANT
│   ├── Alimentation, Repos, Rut, Habitat, Affuts, Trajets
│   └── Multi-Engines (override)
├── Corridors SECONDAIRE
│   ├── Normaux (FAIBLE/MODERE), Intenses (FORT/MAJEUR)
│   ├── EXTREME (CRITIQUE, surbrillance +40%)
│   └── Saisonniers (override)
├── Points TERTIAIRE
│   ├── Alimentation, Rut, Repos, Trajets, Affuts, Habitat
│   ├── Centroides (mode normal)
│   └── Individuels (mode chauds)
└── Overlays
    ├── Vent directionnel (Minimaliste / Particules)
    └── Exclusions
```

## Onglets SUPPRIMES (INTERDICTION de recreer)
- LAYERS — supprime iteration_47
- CORRIDORS V10 — supprime iteration_48

## API Endpoints CORRIDORS-V10
- POST /api/v10/corridors/analyze
- POST /api/v10/corridors/analyze-full
- GET /api/v10/corridors/multi
- GET /api/v10/corridors/profiles
- GET /api/v10/corridors/profile/{species}
- GET /api/v10/corridors/documentation

## Normes Actives
- **STEEVE-MAX**: ZONES = unique centre de controle, hierarchie Zones > Corridors > Points
- **BCE-4X**: 16 zones, 64 centres, zero modification geometrique, firewall 13 tests
- **EXTREME**: CRITIQUE = +40% weight, opacity 0.75, jamais attenue
- **Zone d'analyse**: 2km x 2km, attenuation hors-zone
- **V10 permanent**: showCorridors = true, jamais desactivable

## Backlog
### P1 — Integration score consolide CORRIDORS-V10 dans heatmap
### P2 — HABITAT-V1
### P2 — RUT-V1, AFFUTS-V1, TRAJETS-V1
### P3 — Certification Finale BIONIC V3
### P3 — Refactoring engine.py en modules specialises

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin:** `Saturn5858*`
