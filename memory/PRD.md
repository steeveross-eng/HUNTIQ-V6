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
- **BCE-4X compliance**: Aucun glow/halo/degrade sur aucun corridor, contours sombres pour tous les niveaux
- **V9 purge definitive**: Code V9CorridorRibbon, CorridorLine, CORRIDOR_STYLES supprimes de BionicMicroZones
- **Props nettoyees**: corridors=[] et showCorridors=false retires de MapContent -> BionicMicroZones
- Tests: Frontend 13/13 (100%), 0 regression

### Anomalie critique V9/V10 — Purge V9 + Polygones V10 (2026-03-17) — iteration_34 (23/23)
- **Backend**: engine.py — Ajout generation polygones V10 (BFS flood-fill + convex hull Andrew)
- **Frontend BionicCorridorsV10Layer.jsx**: Rendu polygones V10 avec normes BCE-4X
- **Frontend MapContent.jsx**: BionicMicroZones (V9) SUPPRIME DEFINITIVEMENT
- Tests: Backend 8/8 + Frontend 15/15 = 23/23 (100%), 0 regression

### NORME STEEVE-MAX — Polygones organiques BIONIC (2026-03-17) — iteration_35 (35/35)
- **Backend engine.py REECRIT**: Algorithme organique complet 5 phases
- Tests: Backend 19/19 + Frontend 16/16 = 35/35 (100%), 0 regression

### Standard Visuel STEEVE-MAX (2026-03-17) — iteration_36 (16/16)
- Filtrage corridors par slider, reduction bruit visuel, points centraux restaures

### STEEVE-MAX Dimension + Fusion + Adoucissement (2026-03-17) — iteration_37 (25/25)
- **Fusion ecologique**: 64 zones -> 16 polygones fusionnes (4 par type)
- **Dimension dynamique**: proportionnelle a l'attraction
- **Adoucissement anti-etoile**: Chaikin corner-cutting

### Directive Superposition Transparente STEEVE-MAX (2026-03-17) — iteration_38 (26/26)
- Zones transparentes avec contours opaques, superposition libre

### Correction Contours Organiques — Pipeline Buffer Union (2026-03-17) — iteration_39 (21/21)
- Nouveau pipeline: MultiPoint.buffer -> union -> simplify -> Catmull-Rom -> Chaikin
- **Firewall BCE-4X**: 9 tests geometriques permanents

### COMMANDE FINALE — Hierarchie Visuelle STEEVE-MAX (2026-03-17) — iteration_40 (17/17)
- DOMINANT: Zones (weight=3, opacity=1.0, fillOpacity=0)
- SECONDAIRE: Corridors (opacity=0.30, weights 1-2)
- TERTIAIRE: Points centraux (radius=4, fillOpacity=0.85)

### STEVE-MAX-MULTI — Consolidation 7 Engines (2026-03-17) — iteration_41 (21/21)
- 7 attracteurs V1, ponderation normative, consolidation multi-engine
- Firewall BCE-4X etendu: 13 tests

### Optimisation Comportementale + Reduction Points (2026-03-17) — iteration_42 (100%)
- Points reduits de 64 a 16 centroides representatifs
- Ponderation saisonniere SEASONAL_MODIFIERS

### UX STEEVE-MAX — Onglets ZONES + POINTS CHAUDS (2026-03-17) — iteration_43
- Onglet ZONES avec toggles Zones/Corridors/Points
- Onglet POINTS CHAUDS avec filtrage comportemental
- Correction bug `corridors is not defined`

### OPTIMISATION UX STEEVE-MAX V2 (2026-03-17) — iteration_44 (100%)
- **ZONES tab**: Hierarchie visuelle STEEVE-MAX affichee (DOMINANT, SECONDAIRE, TERTIAIRE) avec labels
- **Points visibilite +25%**: Mode normal radius 4->5 (x1.25), opacity 0.65
- **Points chauds mode retabli**: Apparence anterieure fine (radius=4, fillOpacity=0.65, opacity=0.70) pour lecture detaillee des 64 centres
- **Corridors EXTREME (CRITIQUE) surbrillance**: weight +40% (2->2.8), opacity 0.30->0.75, hachures renforcees
- **Effet vent +15%**: Epaisseur fleches 1.0->1.15, longueur +15%, opacite cap 0.30->0.345, particules lineWidth 0.75->0.86
- **Zero modification geometrique**: Conformite totale STEEVE-MAX + BCE-4X
- Tests: Frontend 100% (iteration_44.json), 0 regression

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
- **Corridors EXTREME**: CRITIQUE (score 85-100) = surbrillance +40% weight, opacity 0.75
- **Vent V8.3.B**: +15% intensite visuelle (fleches + particules)

## Backlog
### P1 — Integration score consolide CORRIDORS-V10 dans heatmap
### P2 — HABITAT-V1 (prochaine commande utilisateur)
### P2 — RUT-V1, AFFUTS-V1, TRAJETS-V1 (sequentiel, sur commande)
### P3 — Certification Finale BIONIC V3
### P3 — Phase 4: Integration transversale (BLOQUEE — necessite tous les moteurs V1)

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin:** `Saturn5858*`
