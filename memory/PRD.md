# BIONIC HUNT — PRD.md

## Branche: steve-max

## Architecture
- **Frontend**: React + Leaflet + Shadcn/UI
- **Backend**: FastAPI + 27 Engines (12 V2, 12 V3, 3 IA) + 3 modeles fauniques + Hotspot Engine V3
- **Weather**: OpenWeatherMap (cache 60min)
- **Quality Gate**: BCE-4X (12+ regles, 100% PASS)
- **Database**: MongoDB (admin_hotspots collection)

## Implemente

### Indicateur BCE-4X temps reel (2026-03-13)
- Composant `BCE4XIndicator.jsx` dans le header territoire
- Affiche: statut PASS/WARNING/FAIL, timestamp, validateurs actifs, violations HIGH/MEDIUM/LOW
- Popover interactif avec details et bouton refresh
- Appel automatique `POST /api/bce/validate` au montage

### Moteur d'extraction Hotspots BIONIC V3 (2026-03-13)
- **Backend** `/backend/modules/bionic_engine_p0/hotspots/`:
  - `hotspot_engine.py`: Scoring pondere officiel (9 engines), grille 50m, DBSCAN clustering, filtrage
  - `hotspot_router.py`: 9 API endpoints admin (`/api/v1/admin/bionic-hotspots/*`)
  - 12 regions officielles Quebec (Laurentides, Outaouais, Lanaudiere, Mauricie, Estrie, Saguenay, Capitale-Nationale, Chaudiere-Appalaches, Bas-Saint-Laurent, Abitibi, Cote-Nord, Gaspesie)
  - 300 hotspots extraits (25/region), dont ~24 MAJEUR (80+) et ~276 FORT (60-79)
  - Ponderations: Corridors 20%, FoodScore 15%, ForestStructure 15%, Wetness 10%, GeoForm 10%, Temporal 10%, Behavior 10%, Disturbance 5%, GlobalAttractiveness 5%
  - Validation BCE-4X integree (GEOM-001, GEOM-002, CLIP-001, VISUAL-001)
  - Export GeoJSON + JSON
  - Stockage MongoDB (collection `admin_hotspots`)
- **Frontend** `AdminHotspots.jsx`:
  - Section admin "Hotspots V3" avec onglet dedie
  - Extraction toutes regions en un clic
  - Tableau complet (ID, Region, Score, Classification, Categorie, Espece, Accessibilite, Coordonnees)
  - Filtres (region, espece, categorie, classification)
  - Export GeoJSON/JSON
  - Rapport BCE-4X
  - Stats agregees

### Phase 7 — Optimisation UI Onglet OUTIL (2026-03-13)
- Popover "Outils" remplace par 3 controles inline: Corridors V9, Seuil (min 10%), Curseur BIONIC

### Phase 6 — BCE-4X CI/CD Enforcement (2026-03-13)
- Document `/app/docs/BCE-4X-CI-Pipeline.md`: schema pipeline, GitHub Actions, merge bloque

### BIONIC V3 Integration Totale (2026-03-13)
- 27 engines actifs, 3 modeles fauniques, pipeline integre, API V3, BionicEngineHub V3

## API Endpoints
- POST /api/v1/admin/bionic-hotspots/extract — Extraction complete 12 regions
- POST /api/v1/admin/bionic-hotspots/extract/{region_id} — Extraction region specifique
- GET /api/v1/admin/bionic-hotspots/regions — Liste 12 regions
- GET /api/v1/admin/bionic-hotspots/list — Liste filtrable (region, espece, categorie, classification)
- GET /api/v1/admin/bionic-hotspots/stats — Statistiques agregees
- GET /api/v1/admin/bionic-hotspots/export/geojson — Export GeoJSON
- GET /api/v1/admin/bionic-hotspots/export/json — Export JSON
- GET /api/v1/admin/bionic-hotspots/report/bce4x — Rapport BCE-4X
- GET /api/v1/admin/bionic-hotspots/report/daily — Rapport quotidien
- POST /api/bce/validate — Validation BCE-4X globale

## Tests
- Iteration 20: 13/13 backend PASS + frontend 95% (BCE-4X indicator + Admin Hotspots V3 + regressions)
- Iteration 17: 12/12 PASS (Phase 7 UI + Phase 6 doc)

## Backlog
### P1 - Export GeoJSON/KML avec metadata engines complet
### P2 - Dashboard analytics / apprentissage machine
### P3 - Multi-territoire
### P3 - Extraction automatique 24h (scheduler)

## Credentials
- Steeve.ross@gmail.com / Saturn5858*
- Admin: admin123 (admin@huntiq.ca)
- OWM_API_KEY dans backend/.env
