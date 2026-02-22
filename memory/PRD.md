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

### PHASE P1-HOTSPOTS V3 — ÉVITEMENT RÉEL OSM (Complétée — 22 Février 2026)
**Module d'affichage cartographique des hotspots BIONIC avec évitement géospatial RÉEL**

#### Extraction OSM Multi-Régions (COMPLÈTE)
| Région | Zones | Water | Roads | Landuse | Taille |
|--------|-------|-------|-------|---------|--------|
| CA-QC | 23,444 | 13,923 | 6,619 | 2,902 | 7.4 MB |
| CA-ON | 220,174 | 184,363 | 27,831 | 7,980 | 60.6 MB |
| US-NY | 54,215 | 34,402 | 16,889 | 2,924 | 18.0 MB |
| FR-ARA | 120,102 | 32,967 | 71,120 | 16,015 | 31.8 MB |
| **TOTAL** | **417,935** | 265,655 | 122,459 | 29,821 | ~118 MB |

#### Spécifications Visuelles CONFORMES
| Critère | Exigé | Implémenté | Statut |
|---------|-------|------------|--------|
| Forme | 100% ORGANIQUE | Marching Squares + Chaikin | ✅ |
| Superficie | 5000-10000 m² | 5006-8574 m² | ✅ |
| Contours | Ultra-fins (1-2px) | 1.5px | ✅ |
| Centre | Transparent | fillOpacity=0 | ✅ |
| Points | Lissés | 39-87 par contour | ✅ |
| Évitement OSM | RÉEL | Cache local 23K+ zones | ✅ |
| Effets | ZÉRO | Aucun | ✅ |

#### Pipeline de Génération V3
1. **IntensityGridGenerator** — Grille d'intensité P0-STABLE
2. **MarchingSquares** — Extraction iso-contours organiques
3. **Chaikin Smoothing** — Lissage multi-passes (3 itérations)
4. **Validation Superficie** — Filtrage 5000-10000 m²
5. **OSMCacheService** — Évitement RÉEL zones d'exclusion
6. **Préparation géométries** — Cache en mémoire pour performance

#### Couleurs par Espèce
| Espèce | Couleur | Code |
|--------|---------|------|
| Orignal | Orange vif | #FF6B00 |
| Chevreuil | Brun | #8B4513 |
| Ours | Gris foncé | #4A4A4A |
| Dindon sauvage | Or foncé | #DAA520 |
| Wapiti | Peru | #CD853F |

#### Backend (100% Fonctionnel)
- ✅ **OrganicContourGenerator** — Marching Squares + Chaikin
- ✅ **IntensityGridGenerator** — Grille multi-noyaux par espèce
- ✅ **MarchingSquares** — Extraction iso-contours
- ✅ **OSMCacheService** — Cache multi-régions PEUPLÉ
- ✅ **OSMExtractor V2** — Script d'extraction paramétrable

#### Frontend (100% Fonctionnel)
- ✅ **Dropdown "Espèce cible"** avec data-testid
- ✅ **Indicateur de couleur** par espèce
- ✅ **Boutons multi-espèces** pour superposition
- ✅ **Seuil par défaut: 50** (réduit pour plus de résultats)

### P1-UX — Boutons ON/OFF Individuels (Complété — 22 Février 2026)
**Implémentation des contrôles de visibilité individuels par hotspot**

#### Fonctionnalités
- ✅ **Panneau ON/OFF dédié** (`HotspotTogglePanel`) — Liste tous les hotspots avec toggle individuel
- ✅ **Toggle instantané** — Aucun recalcul serveur, purement client-side
- ✅ **Bouton "Tout ON/OFF"** — Activation/désactivation en masse
- ✅ **Indicateur de couleur** — Cercle coloré pour chaque hotspot selon l'espèce
- ✅ **Popup enrichi** — Bouton ON/OFF intégré dans le popup de chaque hotspot
- ✅ **Compteur dynamique** — Affichage du nombre de hotspots visibles

#### Fichiers Modifiés
- `/app/frontend/src/modules/map_hotspots/HotspotOverlay.jsx`
- `/app/frontend/src/modules/map_hotspots/HotspotControlPanel.jsx`
- `/app/frontend/src/modules/territory/components/WaypointMap.jsx`

#### data-testid Ajoutés
- `hotspot-toggle-panel` — Panneau ON/OFF
- `toggle-hotspot-{id}` — Toggle individuel
- `enable-all-hotspots` / `disable-all-hotspots` — Boutons masse
- `open-toggle-panel-btn` — Bouton d'ouverture

## Tâches En Attente

### P1-ENV — Intégration OpenWeatherMap
- Données météorologiques en temps réel
- **Status:** PLANIFIÉ

### P1-SCORE — Système de Scoring Dynamique
- Algorithme de scoring personnalisé
- **Status:** PLANIFIÉ

## Phases Planifiées (Backlog)

### P2 — Moteur de Recommandations
- Suggestions personnalisées

### P2 — Intégrations API externes
- API supplémentaires selon besoins

### P3 — BionicMarket
- Préparation de la plateforme marketplace

## Stack Technique
- **Backend**: Python FastAPI + NumPy + SciPy + Shapely
- **Frontend**: React 18 + Leaflet
- **Database**: MongoDB
- **Tests**: pytest + Playwright
- **OSM Cache**: JSON local (~7.4 MB optimisé)

## Fichiers de Référence V3
- `/app/backend/modules/bionic_engine_p0/services/organic_contour_generator.py`
- `/app/backend/modules/bionic_engine_p0/services/osm_cache_service.py`
- `/app/backend/modules/bionic_engine_p0/services/osm_extractor_v2.py`
- `/app/backend/modules/bionic_engine_p0/services/hotspot_service.py`
- `/app/backend/data/osm_cache/CA-QC.json`
- `/app/frontend/src/modules/map_hotspots/HotspotOverlay.jsx`
- `/app/frontend/src/modules/map_hotspots/HotspotControlPanel.jsx`

## API Endpoints
- `POST /api/v1/bionic/map/hotspots` — Génère hotspots organiques
- `POST /api/v1/bionic/map/zones` — Zones comportementales
- `POST /api/v1/bionic/map/corridors` — Corridors de déplacement

## Notes Importantes
- Communication en français uniquement
- Directives de COPILOT MAÎTRE sont absolues et non négociables
- Respect strict des spécifications visuelles BIONIC V5
- **Cache OSM = PEUPLÉ avec données réelles (23K+ zones)**
- **Évitement géospatial = FONCTIONNEL**

## Changelog
- **22 Février 2026**: Extraction OSM multi-régions complète (CA-ON, US-NY, FR-ARA) — 417,935 zones totales
- **22 Février 2026**: Implémentation boutons ON/OFF individuels pour hotspots (HotspotTogglePanel)
- **22 Février 2026**: Extraction OSM complète pour CA-QC (water, roads, landuse)
- **22 Février 2026**: Optimisation cache OSM (112MB → 7.4MB)
- **22 Février 2026**: Correction génération hotspots (zone de génération agrandie)
- **22 Février 2026**: Optimisation grille adaptative selon taille de zone
