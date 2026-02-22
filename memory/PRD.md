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

### PHASE P1-HOTSPOTS V3 — REFONTE ORGANIQUE (Complétée — 22 Février 2026)
**Module d'affichage cartographique des hotspots BIONIC**

#### Spécifications Visuelles CONFORMES

| Critère | Exigé | Implémenté | Statut |
|---------|-------|------------|--------|
| Forme | 100% ORGANIQUE | Marching Squares + Chaikin | ✅ |
| Superficie | 5000-10000 m² | 5006-8574 m² | ✅ |
| Contours | Ultra-fins (1-2px) | 1.5px | ✅ |
| Centre | Transparent | fillOpacity=0 | ✅ |
| Points | Lissés | 39-71 par contour | ✅ |
| Effets | ZÉRO | Aucun | ✅ |

#### Pipeline de Génération
1. **IntensityGridGenerator** — Grille d'intensité P0-STABLE
2. **MarchingSquares** — Extraction iso-contours organiques
3. **Chaikin Smoothing** — Lissage multi-passes (3 itérations)
4. **Validation Superficie** — Filtrage 5000-10000 m²
5. **OSMCacheService** — Évitement zones d'exclusion (STRUCTURE CRÉÉE)

#### Couleurs par Espèce
| Espèce | Couleur | Code |
|--------|---------|------|
| Orignal | Orange vif | #FF6B00 |
| Chevreuil | Brun | #8B4513 |
| Ours | Gris foncé | #4A4A4A |
| Dindon sauvage | Or foncé | #DAA520 |
| Wapiti | Peru | #CD853F |

#### Backend (93% Tests Passés)
- ✅ **OrganicContourGenerator** — Marching Squares + Chaikin
- ✅ **IntensityGridGenerator** — Grille multi-noyaux par espèce
- ✅ **MarchingSquares** — Extraction iso-contours
- ✅ **OSMCacheService** — Cache multi-régions (STRUCTURE CRÉÉE)

#### Frontend (100% Tests Passés)
- ✅ **Dropdown "Espèce cible"** avec data-testid
- ✅ **Indicateur de couleur** par espèce
- ✅ **Boutons multi-espèces** pour superposition
- ✅ **Seuil par défaut: 50** (réduit pour plus de résultats)

## Composants à COMPLÉTER (Production)

### OSM Cache — Extraction Overpass (NON EXÉCUTÉE)
- Structure de cache créée: `/app/backend/data/osm_cache/`
- Régions prédéfinies: CA-QC, CA-ON, CA-BC, CA-AB, US-NY, US-MT, etc.
- **ACTION REQUISE:** Exécuter extraction batch via Overpass API
- Types d'exclusion: water, roads, urban, infrastructure, agriculture, recreation

## Phases Planifiées (Backlog)

### P1-OSM — Extraction Cache OSM (PRIORITAIRE)
- Exécuter `osm_cache.extract_from_overpass("CA-QC")` pour chaque région
- Peupler le cache avec données réelles OSM
- Activer évitement RÉEL des zones d'exclusion

### P1-ENV — Intégration OpenWeatherMap
- Données météorologiques en temps réel

### P1-SCORE — Système de Scoring Dynamique
- Algorithme de scoring personnalisé

### P2 — Moteur de Recommandations
- Suggestions personnalisées

## Stack Technique
- **Backend**: Python FastAPI + NumPy + SciPy + Shapely
- **Frontend**: React 18 + Leaflet
- **Database**: MongoDB
- **Tests**: pytest + Playwright

## Fichiers de Référence V3
- `/app/backend/modules/bionic_engine_p0/services/organic_contour_generator.py`
- `/app/backend/modules/bionic_engine_p0/services/osm_cache_service.py`
- `/app/backend/modules/bionic_engine_p0/services/hotspot_service.py`
- `/app/frontend/src/modules/map_hotspots/HotspotOverlay.jsx`
- `/app/frontend/src/modules/map_hotspots/HotspotControlPanel.jsx`

## Notes Importantes
- Communication en français uniquement
- Directives de COPILOT MAÎTRE sont absolues et non négociables
- Respect strict des spécifications visuelles BIONIC V5
- **Cache OSM = STRUCTURE CRÉÉE, DONNÉES = VIDES**
