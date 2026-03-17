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
  - Chaque polygone ~300m de cote, terrain-aware, deterministe
- **Frontend BionicCorridorsV10Layer.jsx**: Rendu polygones V10 avec normes BCE-4X
  - fillOpacity 0.35 (hover 0.40), contour darkenHex(0.82), weight 1.5
  - Points centraux synchronises (center_lat/center_lng)
- **Frontend MapContent.jsx**: BionicMicroZones (V9) SUPPRIME DEFINITIVEMENT
- Tests: Backend 8/8 + Frontend 15/15 = 23/23 (100%), 0 regression

### NORME STEEVE-MAX — Polygones organiques BIONIC (2026-03-17) — iteration_35 (35/35)
- **Backend engine.py REECRIT**: Algorithme organique complet
  - _convex_hull() SUPPRIME → remplace par algorithme organique 5 phases
  - Phase 1: BFS flood-fill etendu (radius=15, cells=150, threshold=15%)
  - Phase 2: Extraction de frontiere (cellules avec voisins non-zone)
  - Phase 3: Tri angulaire depuis centroide
  - Phase 4: _terrain_perturbation() — 6 facteurs terrain:
    canopy_density, slope, distance_eau_m, distance_route_m, feuillus_nobles, strate_1_3m
  - Phase 5: _catmull_rom_closed() — spline Catmull-Rom (8 segments/point)
  - ZERO simplification (BCE-4X: geometrie sanctuarisee et inviolable)
- **Resultats**: 64 polygones, avg 879 vertices (min 145, max 1185)
  - Aucun segment rectiligne — courbure continue fluide naturelle
  - Fidelite ecologique: foret, eau, pente, peuplements, drainage
  - Zones ~400-560m de couverture geographique
  - Rendu deterministe et reproductible
- **Protection BCE-4X active**:
  - Interdiction de simplifier, lisser, reduire, reechantillonner
  - Polygones organiques = entites protegees et inviolables
- Tests: Backend 19/19 + Frontend 16/16 = 35/35 (100%), 0 regression

### Standard Visuel STEEVE-MAX (2026-03-17) — iteration_36 (16/16)
- Filtrage corridors par slider, reduction bruit visuel, points centraux restaures
- Hierarchie visuelle: Zones (bas) → Corridors (milieu) → Points (haut)

### STEEVE-MAX Dimension + Fusion + Adoucissement (2026-03-17) — iteration_37 (25/25)
- **Fusion ecologique**: _cluster_zones_by_type() avec super-quadrant 2x2
  - 64 zones → 16 polygones fusionnes (4 par type, cluster_size=4)
  - Zero effet confetti — zones coherentes et lisibles
- **Dimension dynamique**: proportionnelle a l'attraction
  - max_radius = 8 + score × 14 (8-22 cells)
  - max_cells = 40 + score × 200 (40-240 cells)
  - Zones fortes: ~1000-1450m | Zones faibles: ~500-700m
- **Adoucissement anti-etoile**: _chaikin_smooth() Chaikin corner-cutting
  - 2 iterations apres Catmull-Rom(6 segments)
  - avg ~5000 vertices par polygone — contours fluides sans spikes
  - Pipeline: BFS multi-source → boundary → angular sort → terrain perturbation → Catmull-Rom → Chaikin
- **Multi-source BFS**: depart depuis TOUS les centres du cluster fusionnee
- **all_centers**: chaque polygone contient les 4 centres originaux BCE-4X
  - 64 points centraux totaux preserves et rendus (radius 6, contour blanc)
- Tests: Backend 11/11 + Frontend 14/14 = 25/25 (100%), 0 regression
- Fond: terrain satellite 100% visible (aucune couche opaque)
- Corridors: V10 uniquement (palette normative CRITIQUE→FAIBLE, BCE-4X: aucun glow)
  - CRITIQUE: #B80000 + contour #660000 + micro-hachures
  - MAJEUR: #FF0000 + contour #CC0000, aucun pattern
- Zones: **POLYGONES ORGANIQUES V10** — Protection BCE-4X
  - 64 polygones Catmull-Rom (avg 879 vertices, max 1185)
  - 4 types: alimentation (vert), repos (bleu), rut (orange), eau (teal)
  - Courbure continue, fluide, naturelle — ZERO segment rectiligne
  - Fidelite ecologique: foret, eau, pente, peuplements, micro-reliefs
  - Transparence calibree 35% (hover 40%), contours assombris 18%
  - Points centraux synchronises
  - Polygones cliquables avec tooltips
  - ZERO zones V9 restantes
  - ZERO simplification Douglas-Peucker sur zones
- Legende: 3X normative (3 blocs, compteurs, toggles)
- Panneau lateral: entierement V10
- Toolbar: "CORRIDORS V10" avec toggle
- BCE-4X: applique a la racine, geometrie sanctuarisee

## API Endpoints CORRIDORS-V10
- POST /api/v10/corridors/analyze
- POST /api/v10/corridors/analyze-full (GeoJSON normatif simplifie)
- GET /api/v10/corridors/multi
- GET /api/v10/corridors/profiles
- GET /api/v10/corridors/profile/{species}
- GET /api/v10/corridors/documentation

### Optimisation Comportementale + Reduction Points (2026-03-17) — iteration_42 (100%)
- **Frontend**: Points reduits de 64 a 16 centroides representatifs (1 par polygone, score max)
  - radius=3, fillOpacity=0.30, opacity=0.35, weight=1 (overlay leger)
  - Tooltip: "Type — Score% (N pts)" pour chaque centroide
- **Backend multi_engine.py**: Ponderation saisonniere SEASONAL_MODIFIERS
  - 12 mois: rut booste automne (×1.6), repos booste hiver (×1.5), alimentation printemps (×1.3)
  - get_seasonal_weights(month) renormalise les poids
  - season_month dans metadata GeoJSON
- **Hierarchie visuelle permanente**:
  - DOMINANT: Zones (weight=3, opacity=1.0, fillOpacity=0)
  - SECONDAIRE: Corridors (opacity=0.30, weights 1-2)
  - OVERLAY LEGER: Points (radius=3, opacity=0.30-0.35)
- Carte radicalement plus lisible — zero regression BCE-4X (13/13)

### STEVE-MAX-MULTI — Consolidation 7 Engines (2026-03-17) — iteration_41 (21/21)
- **Multi-engine module** (`multi_engine.py`):
  - 7 attracteurs V1: alimentation_v1, rut_v1, repos_v1, trajets_v1, affuts_v1, habitat_v1, corridors_v10
  - Ponderations normatives: 12-18% par engine, boost 25% pour engine primaire
  - Consolidation: 55% base type + 45% multi-engine
  - Registre ENGINE_REGISTRY pour validation et diagnostic
- **Backend engine.py**: BFS utilise `score_cell_multi_engine()` pour scoring consolide
  - Buffer d_lat*1.5, simplify d_lat*0.6, Chaikin 3 iterations
  - Post-validation polygone (buffer(0) auto-repair self-intersections)
  - Metadata GeoJSON: engine=STEVE-MAX-MULTI, engines_count=7, engines_active
- **Firewall BCE-4X etendu**: 13 tests (9 geometriques + 4 multi-engine)
  - test_firewall_multi_engine_metadata, test_firewall_7_engines_active
  - test_firewall_centers_invariance, test_firewall_surface_invariance
- **Hierarchie visuelle permanente**:
  - DOMINANT: Zones (weight=3, opacity=1.0, fillOpacity=0)
  - SECONDAIRE: Corridors (opacity=0.30, weights 1-2)
  - TERTIAIRE: Points (radius=4, fillOpacity=0.85)
- Tests: Backend 13/13 + Frontend 8/8 = 21/21 (100%), 0 regression

### COMMANDE FINALE — Hierarchie Visuelle STEEVE-MAX (2026-03-17) — iteration_40 (17/17)
- **Frontend BionicCorridorsV10Layer.jsx**: Hierarchie visuelle stricte
  - DOMINANT: Zones contours (weight=3, opacity=1.0, fillOpacity=0)
  - SECONDAIRE: Corridors (opacity=0.30, weights: CRITIQUE/MAJEUR=2, FORT=1.5, MODERE=1.2, FAIBLE=1)
  - TERTIAIRE: Points centraux (radius=4, fillOpacity=0.85, border=1.5)
  - Corridors poids et opacite reduits pour ceder la dominance visuelle aux zones
- **Backend engine.py**: Pipeline modulaire sequentiel inchange
  - Phase 0: Fusion ecologique (64→16, super-quadrant 2x2)
  - Phase 1: Dimension dynamique (rayon proportionnel a l'attraction)
  - Phase 2: BFS multi-source terrain-aware
  - Phase 3: Shapely buffer union (contour organique)
  - Phase 4: Simplify intermediaire (reduction control points)
  - Phase 5: Sous-echantillonnage (~50 pts)
  - Phase 6: Catmull-Rom(6) (courbure continue)
  - Phase 7: Chaikin(2) (anti-etoile)
- **Protection BCE-4X**: Firewall 9/9 tests (zero spike, zero regression)
- Tests: Backend 9/9 + Frontend 8/8 = 17/17 (100%), 0 regression

### Correction Contours Organiques — Pipeline Buffer Union (2026-03-17) — iteration_39 (21/21)
- **Backend engine.py**: Nouveau pipeline de contour organique
  - Phase 3: `MultiPoint.buffer(d_lat*1.2)` → union de cercles = blob lisse
  - Phase 4: `simplify(d_lat*0.4)` → reduction intermediaire
  - Phase 5: Sous-echantillonnage ~50 control points
  - Phase 6: Catmull-Rom(6) → courbure continue
  - Phase 7: Chaikin(2) → anti-etoile
  - **Ancien pipeline supprime**: tri angulaire + perturbation terrain (cause des spikes)
  - ZERO SPIKES: min_angle=89.1° (seuil: 45°) sur les 16 polygones
  - 817-1201 vertices par polygone, extents 236-607m
- **Firewall BCE-4X**: `/app/backend/tests/test_bce4x_firewall_organic.py` (9 tests)
  - test_firewall_16_polygons, test_firewall_4_per_type, test_firewall_cluster_size_4
  - test_firewall_64_centers, test_firewall_min_vertices, test_firewall_contour_closed
  - test_firewall_zero_spikes (angle<45° = BLOQUE), test_firewall_surface_attraction_ratio
  - test_firewall_polygon_extent_minimum (>150m chaque dimension)
- Tests: Backend firewall 9/9 + Frontend 12/12 = 21/21 (100%), 0 regression

### Directive Superposition Transparente STEEVE-MAX (2026-03-17) — iteration_38 (26/26)
- **Frontend BionicCorridorsV10Layer.jsx**: Rendu zones transparent
  - fillOpacity=0, fillColor=transparent (interieur transparent)
  - Contours opaques: opacity=1.0, weight=3, couleurs vives (non assombries)
  - Hover: weight 3→4 (zero changement de remplissage)
  - Couleurs: alimentation=#4CAF50, repos=#2196F3, rut=#FF5722, eau=#00BCD4
- **Backend engine.py**: BFS superposition libre (sans exclusion territoriale)
  - Fusion ecologique 64→16 zones (4 par type, cluster_size=4)
  - Dimension dynamique preservee (rayon proportionnel attraction)
  - Contours organiques: Catmull-Rom(6) + Chaikin(2), 2000-5500 vertices
  - 64 centres BCE-4X preserves (all_centers, 4 par polygone)
- **Zero pollution visuelle**: contours seuls definissent les zones
- **Superposition libre**: zones peuvent se chevaucher sans masquer les contours
- Tests: Backend 10/10 + Frontend 16/16 = 26/26 (100%), 0 regression

## Backlog
### P1 — Integration score consolide CORRIDORS-V10 dans heatmap
### P2 — HABITAT-V1 (prochaine commande utilisateur)
### P2 — RUT-V1, AFFUTS-V1, TRAJETS-V1 (sequentiel, sur commande)
### P3 — Certification Finale BIONIC V3
### P3 — Phase 4: Integration transversale (BLOQUEE — necessite tous les moteurs V1)

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin:** `Saturn5858*`
