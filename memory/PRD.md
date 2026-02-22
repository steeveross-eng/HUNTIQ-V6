# HUNTIQ-V5 — Product Requirements Document

## Original Problem Statement
Projet HUNTIQ-V5 dirigé par COPILOT MAÎTRE (Steeve). Application de chasse avec moteur d'intelligence artificielle BIONIC intégrant 12 facteurs comportementaux avancés pour l'analyse territoriale et comportementale du gibier.

## Architecture BIONIC V5
- Architecture 100% modulaire
- Pilotée par contrats JSON (source unique de vérité)
- Normes G-QA (Qualité), G-SEC (Sécurité), G-DOC (Documentation)
- GOLD MASTER: Code source stable et intouchable

## Phases Complétées

### PHASE P0-STABLE — BIONIC V5 ULTIME x2 (Validée)
**Date: Février 2025**
- ✅ Intégration des 12 facteurs comportementaux majeurs
- ✅ 91 tests (70 unitaires + 21 API) passés
- ✅ Documentation complète mise à jour
- ✅ 4 rapports de revue exécutive générés

### PHASE P1-HOTSPOTS (Complétée — 22 Février 2026)
**Module d'affichage cartographique des hotspots BIONIC**

#### Backend (100% Complété)
- ✅ **GET /api/v1/bionic/map/status** — Statut du module P1-HOTSPOTS
- ✅ **POST /api/v1/bionic/map/hotspots** — Génération de hotspots GeoJSON
  - 10 types supportés: activity_peak, feeding_zone, rut_zone, thermal_refuge, water_source, predation_risk, snow_impact, human_avoidance, mineral_site, composite_optimal
  - Géométrie: Polygon avec contours Chaikin
- ✅ **POST /api/v1/bionic/map/zones** — Zones comportementales
  - 7 types: feeding, bedding, rut_arena, thermal_cover, water_access, predation_zone, yarding_zone
  - Matrice de superposition incluse
- ✅ **POST /api/v1/bionic/map/corridors** — Corridors de déplacement
  - 4 types: movement, avoidance, preferred, feeding_transit
  - Context de mouvement inclus

#### Frontend (100% Complété)
- ✅ **HotspotOverlay.jsx** — Composant Leaflet pour affichage GeoJSON
- ✅ **HotspotControlPanel.jsx** — Panneau de contrôle ON/OFF
  - Activation/désactivation individuelle
  - Activation par groupe (Activity, Feeding, Reproduction, Environment, Risk)
  - Filtres: espèces, période (24h/72h/7j), score minimum

#### Spécifications Visuelles Respectées
- Contours ultra-fins (2px minimum)
- Centres 100% transparents (fillOpacity: 0)
- Formes naturelles (Chaikin smoothing)
- ZERO glow, shadow, halo

#### Tests (100% Passés)
- 20/20 tests API
- Frontend UI/UX validé
- 64 hotspots rendus sur la carte

## Phases Planifiées (Backlog)

### P1-ENV — Intégration OpenWeatherMap
- Données météorologiques en temps réel
- Impact sur les prédictions comportementales

### P1-SCORE — Système de Scoring Dynamique
- Algorithme de scoring personnalisé
- Dashboard de scoring

### P1-API — Endpoint /api/v1/bionic/analyze_hunt_plan
- Analyse complète d'un plan de chasse
- Recommandations optimisées

### P2 — Moteur de Recommandations
- Suggestions personnalisées
- Apprentissage des préférences utilisateur

### P2 — Intégrations API Externes
- APIs tierces pour enrichissement des données

### P3 — BionicMarket
- Plateforme marketplace
- Échanges entre chasseurs

## Stack Technique
- **Backend**: Python FastAPI
- **Frontend**: React 18 + Leaflet
- **Database**: MongoDB
- **Tests**: pytest + Playwright

## Fichiers de Référence Principaux
- `/app/backend/modules/bionic_engine_p0/router.py`
- `/app/backend/modules/bionic_engine_p0/services/hotspot_service.py`
- `/app/frontend/src/modules/map_hotspots/HotspotOverlay.jsx`
- `/app/frontend/src/modules/map_hotspots/HotspotControlPanel.jsx`

## Notes
- Communication en français uniquement
- Directives de COPILOT MAÎTRE sont absolues et non négociables
- Respect strict des spécifications visuelles BIONIC V5
