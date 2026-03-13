# BIONIC HUNT — PRD.md

## Branche: steve-max

## Architecture
- **Frontend**: React + Leaflet + Shadcn/UI
- **Backend**: FastAPI + 27 Engines (12 V2, 12 V3, 3 IA) + 3 modeles fauniques + Hotspot Engine V3
- **Weather**: OpenWeatherMap (cache 60min)
- **Quality Gate**: BCE-4X (12+ regles, 100% PASS)
- **Database**: MongoDB (admin_hotspots collection)

## Implemente

### Rotation 3D Logos BIONIC (2026-03-13)
- Classe CSS globale `.bionic-logo-3d-rotate` dans App.css
- Keyframes `rotate3d360`: rotateY 0deg -> 360deg, linear, 10s, infinite
- Applique sur: BionicLogoGlobal (toutes pages), BionicLogo (header), MainLayout logo
- perspective: 1000px, preserve-3d, aucune distorsion
- Compatible desktop + mobile, aucun conflit animations existantes
- Valide sur: Territoire, Admin, Dashboard

### Indicateur BCE-4X temps reel (2026-03-13)
- Composant BCE4XIndicator.jsx dans le header territoire
- Statut PASS/WARNING/FAIL, timestamp, validateurs, violations HIGH/MEDIUM/LOW

### Moteur d'extraction Hotspots BIONIC V3 (2026-03-13)
- Backend: 9 API endpoints /api/v1/admin/bionic-hotspots/*
- 12 regions Quebec, 300 hotspots (25/region), scoring pondere 9 engines
- Frontend: Admin tab "Hotspots V3", tableau, filtres, exports GeoJSON/JSON

### Phase 7 — Optimisation UI Onglet OUTIL (2026-03-13)
- 3 controles inline: Corridors V9, Seuil (min 10%), Curseur BIONIC

### Phase 6 — BCE-4X CI/CD Enforcement (2026-03-13)
- Document /app/docs/BCE-4X-CI-Pipeline.md

### BIONIC V3 Integration Totale (2026-03-13)
- 27 engines actifs, 3 modeles fauniques, pipeline integre

## Tests
- Iteration 20: 13/13 backend + frontend 95% (Hotspots + BCE-4X indicator)
- Iteration 17: 12/12 PASS (Phase 7 + Phase 6)
- Logo 3D: Valide par screenshots sur 3 pages (Territoire, Admin, Dashboard)

## API Endpoints
- POST /api/v1/admin/bionic-hotspots/extract
- GET /api/v1/admin/bionic-hotspots/regions
- GET /api/v1/admin/bionic-hotspots/list
- GET /api/v1/admin/bionic-hotspots/stats
- GET /api/v1/admin/bionic-hotspots/export/geojson
- GET /api/v1/admin/bionic-hotspots/export/json
- GET /api/v1/admin/bionic-hotspots/report/bce4x
- GET /api/v1/admin/bionic-hotspots/report/daily
- POST /api/bce/validate

## Backlog
### P1 - Carte interactive Leaflet dans Admin Hotspots V3
### P1 - Export GeoJSON/KML avec metadata engines
### P2 - Dashboard analytics / apprentissage machine
### P3 - Multi-territoire
### P3 - Extraction automatique 24h (scheduler)

## Credentials
- Steeve.ross@gmail.com / Saturn5858*
- Admin: admin123 (admin@huntiq.ca)
- OWM_API_KEY dans backend/.env
