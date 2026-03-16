# BIONIC V3 — PRD (Product Requirements Document)

## Problème Original
Application BIONIC V3 — Outil d'analyse écologique full-stack (React + FastAPI + MongoDB) pour la gestion de la faune au Québec. L'application utilise des moteurs écologiques complexes (V1, V2, V3, V9) pour l'analyse de données géographiques et environnementales, la classification de terrain pour la gestion de la faune (zones d'alimentation, corridors, hotspots).

## Architecture
- **Frontend:** React + Leaflet/react-leaflet (mapping)
- **Backend:** FastAPI (Python)
- **Database:** MongoDB
- **Intégrations:** OpenWeatherMap, Open-Meteo, Open-Elevation, NASA MODIS, OSM Overpass

## Tâches Complétées

### Sécurité & Consolidation (Terminé)
- Suppression BCE-4X des sections publiques
- Gate admin par mot de passe (`Saturn5858*`)
- Consolidation UI Hotspots V3
- Validation 100% (iteration_22 + iteration_23)

### AUDIT ÉCOLOGIQUE GLOBAL BIONIC — MODE STEEVE-MAX (Terminé 2026-03-16)
- **Phase 1:** Inventaire complet de tous les modules/engines (Legacy, V2, V3, IA, V9, Hotspot)
- **Phase 2:** Extraction de toutes les règles, variables, seuils, couches par thème écologique
- **Phase 3:** Rapport structuré livré en 4 formats:
  - `BIONIC_AUDIT_ECOLOGIQUE_v1.md` (Markdown — 775 lignes)
  - `BIONIC_AUDIT_ECOLOGIQUE_v1.yaml` (YAML structuré — 362 lignes)
  - `BIONIC_AUDIT_ECOLOGIQUE_v1.pdf` (PDF professionnel — reportlab)
  - `pipeline_ecologique_v1.txt` (Diagramme ASCII du pipeline complet)
- **Phase 4:** Aucune modification de code — observation et documentation uniquement
- Tous les fichiers accessibles via HTTPS (`/api/audit/{filename}`)
- Endpoint de listing: `/api/audit/list`

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
