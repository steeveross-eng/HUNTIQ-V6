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

### PHASE P1-HOTSPOTS V2 — REFONTE CIRCULAIRE (Complétée — 22 Février 2026)
**Module d'affichage cartographique des hotspots BIONIC**

#### Spécifications Visuelles Implémentées (CONFORMES)
- ✅ Forme de base **CIRCULAIRE** avec perturbations naturelles terrain
- ✅ Superficie **EXACTE: 2000-3000 m²** (mesuré: ~2128 m²)
- ✅ Contours **ultra-fins (1.5px)**, colorés, lissés (Chaikin 129 points)
- ✅ Centre **100% TRANSPARENT** (fillOpacity = 0)
- ✅ Évitement automatique des zones d'eau (SIMULÉ)
- ✅ Alignement par espèce avec couleurs distinctes
- ✅ **Dropdown de sélection d'espèce** dans les filtres

#### Couleurs par Espèce
| Espèce | Couleur | Code |
|--------|---------|------|
| Orignal | Orange vif | #FF6B00 |
| Chevreuil | Brun | #8B4513 |
| Ours | Gris foncé | #4A4A4A |
| Dindon sauvage | Or foncé | #DAA520 |
| Wapiti | Peru | #CD853F |

#### Backend (100% Complété)
- ✅ **ContourGenerator V2** — Génération de cercles naturels
- ✅ **NaturalCircleGenerator** — Calcul de rayon pour superficie cible
- ✅ **WaterBodyDetector** — Évitement des zones d'eau (SIMULÉ)
- ✅ **Chaikin Smoothing** — Lissage des contours (129 points)

#### Frontend (100% Complété)
- ✅ **Dropdown "Espèce cible"** avec indicateur de couleur
- ✅ **Boutons multi-espèces** pour superposition
- ✅ **65+ hotspots circulaires** rendus sur la carte
- ✅ **Centres transparents** (carte visible à travers)

#### Tests (100% Passés)
- 10/10 tests backend
- 100% validation frontend
- Toutes les spécifications visuelles vérifiées

## Note Importante: Composants SIMULÉS
- **WaterBodyDetector** : Évitement d'eau basé sur patterns géographiques typiques du Québec. En production, intégrer OpenStreetMap Overpass API ou données LiDAR locales.

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

### P2 — Intégration OSM Water Data (Production)
- Remplacer WaterBodyDetector simulé par données réelles
- Intégration OpenStreetMap Overpass API

### P3 — BionicMarket
- Plateforme marketplace
- Échanges entre chasseurs

## Stack Technique
- **Backend**: Python FastAPI
- **Frontend**: React 18 + Leaflet
- **Database**: MongoDB
- **Tests**: pytest + Playwright

## Fichiers de Référence Principaux
- `/app/backend/modules/bionic_engine_p0/services/contour_generator.py` (V2 - refonte)
- `/app/backend/modules/bionic_engine_p0/services/hotspot_service.py`
- `/app/frontend/src/modules/map_hotspots/HotspotOverlay.jsx`
- `/app/frontend/src/modules/map_hotspots/HotspotControlPanel.jsx`

## Notes
- Communication en français uniquement
- Directives de COPILOT MAÎTRE sont absolues et non négociables
- Respect strict des spécifications visuelles BIONIC V5
