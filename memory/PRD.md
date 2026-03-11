# BIONIC HUNT V8 — Product Requirements Document

## Problème original
Application d'analyse de territoire de chasse avec moteur géospatial BIONIC Engine, base écologique complète pour 3 espèces (Orignal, Chevreuil, Ours Noir), et système de validation automatisé BCE.

**Repo GitHub:** https://github.com/steeveross-eng/HUNTIQ-V5  
**Branche:** v6_autosave

## Architecture V8

### Backend (FastAPI + MongoDB)
- **Moteur BIONIC:** V7 avec zones organiques, exclusions, corridors
- **Base écologique V8:** 3 espèces × 4+ zones chacune
- **Corridors 10X:** Classification WWF + algorithme A*
- **BCE:** BIONIC Compliance Engine (validateurs écologiques)
- **Météo:** OpenWeatherMap avec cache 30min

### Frontend (React + Leaflet)
- **Zone 2 km²:** Carré centré sur waypoint actif
- **Panneau écologique:** Corridors actifs, légende WWF, zones par espèce
- **Carte interactive:** Exclusions, zones organiques, corridors

## Fonctionnalités implémentées

### Session 11 Mars 2026 — BIONIC V8

#### 1. Base Écologique Complète ✅
**Fichier:** `/backend/modules/bionic_engine_p0/knowledge/ecological_database_v8.py`

Espèces couvertes:
- **ORIGNAL:** Alimentation, Repos, Rut, Corridor
- **CHEVREUIL:** Alimentation, Repos, Rut, Corridor
- **OURS NOIR:** Alimentation, Repos, Tanière, Corridor

Pour chaque zone:
- Habitat (types de forêt, couvert, sous-étage)
- Topographie (pente, aspect, élévation)
- Hydrologie (distance eau, types)
- Pression humaine (distance routes, seuils)
- Nourriture par saison
- Critères algorithmiques V8-ready (NDVI, landcover, poids A*)
- Règles BCE

#### 2. Corridors 10X avec Classification WWF ✅
**Fichier:** `/backend/modules/bionic_engine_p0/services/corridor_10x.py`

Classification WWF:
- **Macro-corridors (> 5 km):** Connexion régionale
- **Corridors biologiques (1-5 km):** Connexion écosystèmes
- **Corridors de conservation (< 1 km):** Reliques fragmentées

Algorithme A*:
- Coûts de terrain par type (vallées, forêts, champs, urbain)
- Pathfinding optimal avec heuristique
- Lissage de trajectoire

#### 3. Validateurs BCE Écologiques ✅
**Fichier:** `/backend/bce/validators/ecological_validators_v8.py`

Validateurs:
- `bce_zone_classification_valid`
- `bce_corridor_continuity_valid`
- `bce_wwf_classification_valid`
- `bce_human_pressure_respected`
- `bce_topographic_coherence_valid`

#### 4. API Écologique V8 ✅
**Fichier:** `/backend/routes/ecological_router_v8.py`

Endpoints:
- `GET /api/v1/ecological/species`
- `GET /api/v1/ecological/species/{species}/zones`
- `GET /api/v1/ecological/species/{species}/zones/{zone_type}`
- `POST /api/v1/ecological/validate`
- `GET /api/v1/ecological/corridors/summary`

#### 5. Zone 2 km² carrée ✅
**Fichier:** `/frontend/src/components/territoire/BionicZone2km.jsx`
- Carré 2km × 2km centré sur waypoint actif
- Contour pointillé orangé (#f5a623)
- Sans remplissage

#### 6. Suppression lignes rouges ✅
**Fichier:** `/frontend/src/components/territoire/StructureContrastLayer.jsx`
- Return null — désactivation totale

#### 7. Panneau Écologique ✅
**Fichier:** `/frontend/src/components/territoire/EcologicalPanel.jsx`
- Indicateur "X corridors actifs détectés"
- Légende WWF
- Zones dominantes par espèce

## Critères algorithmiques intégrés

| Critère | Description |
|---------|-------------|
| NDVI | Seuils par saison (0.3-0.85) |
| Landcover | Codes NLCD |
| Pente | 0-60% selon zone |
| Aspect | N, S, E, W préférés |
| Distance eau | 0-2000m |
| Distance routes | 50-800m |
| Canopy cover | 20-95% |
| Pression humaine | 0-0.4 |
| Corridor cost | 1.0-5.0 (A*) |

## Backlog

### P0 — Critique (Fait)
- [x] Base écologique 3 espèces
- [x] Critères algorithmiques V8
- [x] Corridors 10X + WWF
- [x] Validateurs BCE
- [x] Zone 2 km²
- [x] API écologique

### P1 — En cours
- [ ] Intégration corridors 10X dans pipeline V7
- [ ] Affichage corridors sur carte
- [ ] Fiches écologiques interactives frontend

### P2 — Phase E
- [ ] Audit fichiers legacy
- [ ] Décommission composants obsolètes

### P3 — V8.4
- [ ] Vent animé Canvas 2D
- [ ] Heatmaps prédictives
- [ ] Dashboard BCE admin

## Sources scientifiques
- MFFP-QC-2023
- WWF-2020
- Renecker-1987, Peek-1997 (Orignal)
- VerCauteren-2003, Nixon-1991 (Chevreuil)
- Rogers-1987, Pelton-2003 (Ours noir)
- Beier-1998, Chetkiewicz-2006 (Corridors)

## Dates clés
- **2026-03-11:** BIONIC V8 — Base écologique complète, Corridors 10X, Validateurs BCE
- **2026-03-10:** Widget Comparaison V8.3.A
- **2026-02-24:** PHASE C/D Knowledge Layer
