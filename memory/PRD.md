# BIONIC V3 — PRD (Product Requirements Document)

## Problème Original
Application BIONIC V3 — Outil d'analyse écologique full-stack (React + FastAPI + MongoDB) pour la gestion de la faune au Québec. L'application utilise des moteurs écologiques complexes (V1, V2, V3, V9) pour l'analyse de données géographiques et environnementales, la classification de terrain pour la gestion de la faune (zones d'alimentation, corridors, hotspots).

## Architecture
- **Frontend:** React + Leaflet/react-leaflet (mapping)
- **Backend:** FastAPI (Python)
- **Database:** MongoDB
- **Intégrations:** OpenWeatherMap, Open-Meteo, Open-Elevation, NASA MODIS, OSM Overpass

## Tâches Complétées

### Sécurité & Consolidation
- Suppression BCE-4X des sections publiques
- Gate admin par mot de passe (`Saturn5858*`)
- Consolidation UI Hotspots V3
- Validation 100% (iteration_22 + iteration_23)

### AUDIT ÉCOLOGIQUE GLOBAL BIONIC — MODE STEEVE-MAX (2026-03-16)
- Phase 1-4 complètes: MD, YAML, PDF, diagramme ASCII pipeline
- Tous accessibles via `/api/audit/{filename}` et `/api/audit/list`

### Bouton "Carte" + Deep Link Mon Territoire (2026-03-16)
- Bouton "Carte" stylisé (bleu #1E88E5, icône Map) ajouté dans la colonne ACTION du tableau des hotspots
- Mini-preview satellite 300×180px au survol (délai 250ms, Leaflet dédié, fond ArcGIS Imagery)
- Lien dynamique: `/mon-territoire?lat={lat}&lng={lng}&zoom=15&layer=satellite&hotspot={id}`
- Deep link: carte centrée, zoom 15, fond Satellite, highlight cercle 2km² + marker orange
- Chargement automatique du tableau au montage (useEffect initial ajouté)
- Validation 100% — iteration_24: 10/10 tests passés

## Backlog (P0 → P2)

### P0 — PLAN DE MATCH STEEVE-MAX
- Optimisation des modèles écologiques basée sur les résultats de l'audit
- En attente des instructions de Steeve

### P1 — Certification Finale BIONIC V3
- En attente de la complétion du Plan de Match

### P2 — Propositions d'amélioration (identifiées dans l'audit)
- P-ALIM-01: Sentinel-2 réel au lieu de NDVI estimé
- P-TERR-01: SRTM/ALOS 30m au lieu du DEM algorithmique
- P-PRESS-01: Densité routière OSM réelle
- P-ML-01: Vrai modèle ML dans Learning Engine
- P-PRED-01: Modèle prédateur-proie
- P-THERM-01: Courbes gaussiennes de confort thermique
- P-HOT-01: Scoring écologique réel par cellule

## Données Mockées
- Données territoriales (villes, codes postaux, gestionnaires) — approuvé par l'utilisateur

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin:** `Saturn5858*`
