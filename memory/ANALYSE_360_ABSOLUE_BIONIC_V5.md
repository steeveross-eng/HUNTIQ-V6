# ANALYSE 360° ABSOLUE — BIONIC V5
# EXTRACTION COMPLÈTE DE L'ARCHITECTURE, SYSTÈMES, DONNÉES ET LOGIQUES
# Document de référence — 27 Février 2026

---

# TABLE DES MATIÈRES

1. [ARCHITECTURE PRODUIT GLOBALE](#1-architecture-produit-globale)
2. [LES DEUX CARTES](#2-les-deux-cartes)
3. [MOTEURS INTERNES (18+ SERVICES)](#3-moteurs-internes)
4. [DONNÉES TERRAIN RÉELLES](#4-données-terrain-réelles)
5. [LES 15 COUCHES BIONIC V5](#5-les-15-couches-bionic-v5)
6. [LES 5 ESPÈCES](#6-les-5-espèces)
7. [LE SCORING COMPLET](#7-le-scoring-complet)
8. [LE MODÈLE HYBRIDE (RÈGLES + IA)](#8-le-modèle-hybride)
9. [LE MOTEUR MÉTÉO](#9-le-moteur-météo)
10. [LE STRATEGY ENGINE](#10-le-strategy-engine)
11. [SYSTÈME FREEMIUM / PREMIUM](#11-système-freemium--premium)
12. [SEO / ASO / DISTRIBUTION](#12-seo--aso--distribution)
13. [SÉCURITÉ & CONFORMITÉ](#13-sécurité--conformité)
14. [PERFORMANCE & SCALABILITÉ](#14-performance--scalabilité)

---

# 1. ARCHITECTURE PRODUIT GLOBALE

## 1.1 Vue d'ensemble

| Dimension | Détail |
|-----------|--------|
| **Nom** | HUNTIQ V5-ULTIME-FUSION (BIONIC) |
| **Version** | 5.0.0 |
| **Backend** | FastAPI (Python 3.11+), 78 modules enregistrés, ~207 482 lignes |
| **Frontend** | React 18 + TailwindCSS + ShadcnUI + Leaflet.js, ~143 543 lignes |
| **Base de données** | MongoDB (Motor async) |
| **Hébergement** | Kubernetes (preview), Supervisor (frontend:3000, backend:8001) |
| **Architecture** | Modulaire v2.0 — Orchestrateur pur (server_orchestrator.py) |
| **Sources fusionnées** | V4 (ossature), V3 (frontpage), V2 (backup/formations), BASE (social/admin) |

## 1.2 Structure Frontend

```
frontend/src/
├── core/bionic/           # Moteurs JS: Scoring (610L), Strategy (496L), Weather (420L), Hybrid (378L), Config (251L)
├── services/              # BionicZoneService (782L), ExportService, GeolocationService, WaypointScoringService
├── pages/                 # 22 pages: MapPage, MonTerritoireBionicPage (2294L), DashboardPage, ShopPage, etc.
├── components/            # 100+ composants: territoire/, map/, bionic/, frontpage/, layout/, ui/
├── modules/               # 30+ modules: weather/, analytics/, strategy/, scoring/, groupe/, etc.
├── hooks/                 # useBionicLayers, useBionicWeather, useBionicScoring, useMapType, etc.
├── config/                # bionic-config, bionic-colors, mapSources, moduleRegistry
├── data_layers/           # advanced_geospatial, behavioral, ecoforestry, simulation, layers_3d
└── design-system/         # Thème et composants BIONIC
```

**Pages principales:**
- `/mon-territoire-bionic` — Mon Territoire (2294 lignes, carte BIONIC complète)
- `/map` — Carte Interactive terrain (383 lignes)
- `/dashboard` — Tableau de bord
- `/forecast` — Prévisions
- `/trips` — Sorties de chasse
- `/calibration` — Dashboard calibration
- `/observations` — Formulaire observations terrain
- `/reports` — Téléchargement/upload des rapports

**Bibliothèque de composants:**
- ShadcnUI (Accordion, Button, Card, Dialog, Select, Switch, Tabs, Badge, etc.)
- Leaflet.js (MapContainer, TileLayer, WMSTileLayer, Marker, Polygon, etc.)
- Lucide-react (icônes)
- Sonner (toasts)

## 1.3 Structure Backend

```
backend/
├── server.py                    # Point d'entrée FastAPI
├── server_orchestrator.py       # Orchestrateur modulaire v2.0
├── modules/                     # 78 modules organisés par phase
│   ├── routers.py               # Registre central de TOUS les routeurs
│   ├── bionic_engine_p0/        # COEUR: Moteur BIONIC (20+ services, 15+ routeurs)
│   ├── scoring_engine/          # Scoring produit (Phase 2)
│   ├── strategy_engine/         # Stratégie de chasse (Phase 2)
│   ├── weather_engine/          # Météo OpenWeatherMap (Phase 2)
│   ├── ai_engine/               # IA GPT-5.2 (Phase 2)
│   ├── wms_engine/              # WMS Québec (Phase 2)
│   ├── auth_engine/             # Auth JWT + Google OAuth (Phase P4)
│   ├── freemium_engine/         # Monétisation (Phase MON)
│   ├── payment_engine/          # Stripe (Phase MON)
│   ├── seo_engine/              # SEO complet (11 140 lignes)
│   ├── analytics_engine/        # Analytics & KPIs
│   ├── territory_engine/        # Gestion territoires
│   ├── collaborative_engine/    # Collaboration chasseurs
│   ├── live_heading_engine/     # Navigation immersive
│   ├── notification_engine/     # Notifications multi-canal
│   └── ... (60+ autres modules)
├── routes/                      # Routeurs additionnels (reports, advanced_zones, bathymetry)
├── services/                    # Services transverses (scheduler, territory_analysis)
├── models/                      # Modèles Pydantic
└── data/                        # Cache OSM, données terrain
```

**Modules par Phase:**

| Phase | Modules | Exemples |
|-------|---------|----------|
| Phase 2 | 7 | nutrition, scoring, ai, weather, geospatial, wms, strategy |
| Phase 3 | 7 | user, admin_unified, notification_unified, referral, territory, tracking, marketplace |
| Phase 4 | 10 | recommendation, collaborative, ecoforestry, engine_3d, wildlife_behavior, simulation, adaptive_strategy, advanced_geospatial, progression, networking |
| Phase 5 | 5 | ecoforestry_data, behavioral_data, simulation_data, layers_3d_data, advanced_geo_data |
| Phase 6 | 1 | live_heading (navigation immersive) |
| Phase 7 | 7 | products, orders, suppliers, customers, cart, affiliate, alerts |
| Phase 8 | 2 | legal_time, predictive |
| Phase P3 | 2 | analytics, waypoint_scoring |
| Phase P4 | 3 | geolocation, auth, hunting_trip_logger |
| Phase P5 | 1 | roles (permissions) |
| Extras | 20+ | camera, onboarding, formations, partner, contact, messaging, global_master_switch, etc. |
| **BIONIC P0** | 1 (20+ sub) | Moteur central: scoring, hotspots, corridors, zones, terrain, observations, GPS, calibration, notifications |

## 1.4 Structure Données (MongoDB)

| Collection | Rôle | Champs clés |
|------------|------|-------------|
| `observations` | Observations terrain | timestamp, lat, lon, species, behavior, source_id |
| `users` | Comptes utilisateurs | email, password_hash, tier, profile |
| `territories` | Territoires enregistrés | name, bounds, waypoints, owner_id |
| `waypoints` | Points d'intérêt | lat, lon, name, type, scores, territory_id |
| `trips` | Sorties de chasse | date, duration, observations, track_gps |
| `payments` | Transactions | user_id, amount, status, stripe_id |
| `subscriptions` | Abonnements | user_id, tier, start_date, end_date |
| `hunting_groups` | Groupes | name, members, territory_id |
| `zone_favorites` | Favoris zones | user_id, zone_id, alerts |
| `seo_*` | SEO (clusters, pages, analytics) | slug, keywords, content, scores |

## 1.5 Structure Synchronisation

- **PC ↔ Mobile:** Application web responsive (React), pas d'app native dédiée
- **Offline:** `OfflineService.js` + `serviceWorkerRegistration.js` pour le mode hors-ligne
- **Temps réel:** WebSocket pour le live tracking et notifications push
- **GPS:** `GeolocationService.js` + `BackgroundTracker.jsx` pour suivi continu
- **État partagé:** Contextes React (`LanguageContext`, `PopupContext`, `AuthProvider`, `NotificationProvider`)

## 1.6 Structure Sécurité

- **Authentification:** JWT + Google OAuth hybride (`auth_engine`)
- **Permissions:** Rôles par tier (FREE/PREMIUM/PRO) via `roles_engine` + `freemium_engine`
- **Validation:** Pydantic automatique sur toutes les routes
- **CORS:** Configuré pour tous les origines (développement)
- **Logging:** Structured logging Python (`G-SEC` compliance)

## 1.7 Structure Monétisation

- **3 niveaux:** FREE → PREMIUM → PRO
- **Paiement:** Stripe (paiements uniques + abonnements récurrents + Apple Pay/Google Pay)
- **Quotas:** Limites par tier sur chaque fonctionnalité
- **Upsell:** Module dédié (`upsell_engine`)
- **Publicité:** Affiliate engine + Ad spaces engine

## 1.8 Structure Distribution

- **SEO Engine complet:** 11 140 lignes, clusters, pages, JSON-LD, automatisation, génération contenu
- **Contenu éducatif:** Articles piliers générés (orignal, chevreuil, ours, pistage, rut)
- **Marketing:** Calendar engine + marketing engine
- **Partenariats:** Partner engine + partner dashboard

## 1.9 Structure IA

- **AI Engine:** Intégration GPT-5.2 pour analyse et recommandations
- **Modèle hybride:** Règles (Niveau 1) + IA (Niveau 2) dans `bionicHybridModel.js`
- **Prédiction:** `predictive_engine` + `predictive_territorial` (1216L)
- **Comportement:** `behavioral_models` (1095L) avec 12 facteurs avancés
- **Scoring unifié:** 9 services orchestrés par `unified_scoring_service` (1170L)

---

# 2. LES DEUX CARTES

## 2.1 MON TERRITOIRE (`MonTerritoireBionicPage.jsx` — 2294 lignes)

### Rôle
Carte BIONIC complète dédiée à l'analyse approfondie d'un territoire de chasse spécifique. C'est le **coeur de l'application** — l'outil principal du chasseur pour comprendre et exploiter son territoire.

### Portée
- Affiche les 15 couches BIONIC filtrées par espèce
- Gère les waypoints, favoris, alertes, groupes
- Intègre météo live, scoring, stratégie, observations
- Supporte le mode GPS Ultimate (suivi temps réel)
- Zone géographique: Québec (lat 40-65, lon -85 à -50)

### Couches affichées
- 15 couches BIONIC (4 comportementales + 7 environnementales + 4 stratégiques)
- Couches écoforestières (WMS gouvernemental: peuplements, topographie, hydrographie, etc.)
- Couches de base interchangeables (OpenStreetMap, Satellite, Topo Québec)
- Zones d'exclusion terrain (eau, routes, urbain, infrastructure)
- Waypoints utilisateur avec marqueurs personnalisés
- Zones favorites avec alertes
- Groupes de chasseurs (tracking live, tirs, heatmap session)

### Moteurs utilisés
- `BionicZoneService.js` (génération zones organiques + exclusion terrain)
- `bionicScoring.js` (15 fonctions de scoring)
- `bionicWeatherEngine.js` (météo Open-Meteo)
- `bionicStrategyEngine.js` (projections, chemins d'approche, risques)
- `bionicHybridModel.js` (règles + IA)
- `useBionicLayers` / `useBionicWeather` / `useBionicScoring` (hooks React)

### Données consommées
- API Overpass (exclusions terrain via proxy backend)
- Open-Meteo (météo live + prévisions)
- WMS Québec (couches gouvernementales)
- MongoDB (waypoints, territoires, favoris, observations)
- GPS device (position live)

### Forces
- Interface riche et complète
- 15 couches BIONIC avec filtrage par espèce
- Exclusion "Tolérance Zéro" fonctionnelle et validée
- Polygones organiques conformes (~5000 m², Chaikin 2x, compacité <0.85)
- Intégration météo live
- Mode groupe collaboratif

### Faiblesses
- Page très lourde (2294 lignes — difficile à maintenir)
- Données simulées pour certains modules internes (pente, forêt, pression)
- Scoring UI non connecté aux endpoints backend de scoring
- WQS (Waypoint Quality Score) backend prêt mais non affiché
- Observations terrain → zones BIONIC non connecté

### Évolution prévue
- Mode "Comparaison Espèces" (split-screen)
- Mini-dashboard "Conditions Saisonnières" (PHASE E)
- Connexion UI ↔ WQS, Heatmap, Ranking
- Tooltips interactifs sur les zones BIONIC

---

## 2.2 CARTE INTERACTIVE (`MapPage.jsx` — 383 lignes)

### Rôle
Carte terrain simplifiée pour la navigation et l'exploration rapide. Donne un accès direct à la carte sans la complexité des 15 couches.

### Portée
- Vue carte de base avec couches sélectionnables
- Création rapide de waypoints
- Overlay BIONIC optionnel (via `BionicMapOverlay`)
- Zone géographique: Québec

### Couches affichées
- Carte de base (OSM, Satellite, etc.)
- Overlay BIONIC (si activé, via `BionicMapOverlay.jsx`)
- Waypoints utilisateur

### Moteurs utilisés
- Leaflet.js (carte de base)
- `BionicMapOverlay.jsx` (overlay des zones BIONIC)
- `BionicZoneService.js` (si overlay BIONIC activé)

### Forces
- Interface légère et rapide
- Bonne pour l'exploration rapide

### Faiblesses
- Manque les contrôles espèce + ON/OFF de Mon Territoire
- Fonctionnalités limitées comparé à Mon Territoire
- L'overlay BIONIC est optionnel et pas aussi riche

### Interactions entre les deux cartes
- Partagent le même `BionicZoneService.js` pour la génération des zones
- Partagent les mêmes hooks (`useBionicLayers`, etc.)
- Les waypoints sont partagés via MongoDB
- `MonTerritoireBionicPage` est l'outil d'analyse, `MapPage` est l'outil de navigation

### Évolution prévue
- Ajout des contrôles espèce + ON/OFF identiques à Mon Territoire (P1)
- Unification progressive des fonctionnalités

---

# 3. MOTEURS INTERNES (18+ SERVICES)

## 3.1 Inventaire complet des moteurs

| # | Moteur | Fichier | Lignes | État | Rôle |
|---|--------|---------|--------|------|------|
| 1 | **Scoring Unifié** | `unified_scoring_service.py` | 1170 | Actif | Orchestre 9 services de scoring |
| 2 | **Score Probabilité** | `score_probability_service.py` | 192 | Actif | Probabilité de présence |
| 3 | **Score Habitat** | `score_habitat_service.py` | 259 | Actif | Qualité de l'habitat |
| 4 | **Score Pression** | `score_pressure_service.py` | 274 | Actif | Pression humaine |
| 5 | **Score Météo** | `score_weather_service.py` | 287 | Actif | Impact météo |
| 6 | **Score Comportement** | `score_behavior_service.py` | 297 | Actif | Activité/comportement |
| 7 | **Score Multi-facteur** | `score_multifactor_service.py` | 387 | Actif | Combinaison de facteurs |
| 8 | **Score Densité** | `score_density_service.py` | 332 | Actif | Densité de population |
| 9 | **Score Risque** | `score_risk_service.py` | 398 | Actif | Risques environnementaux |
| 10 | **Score Mobilité** | `score_mobility_service.py` | 446 | Actif | Mobilité du gibier |
| 11 | **Scoring Dynamique** | `dynamic_scoring_service.py` | 884 | Actif | Scoring temps réel (7 composants) |
| 12 | **Modèles Comportementaux** | `behavioral_models.py` | 1095 | Actif | 12 facteurs comportementaux |
| 13 | **Prédiction Territoriale** | `predictive_territorial.py` | 1216 | Actif | Score territorial prédictif |
| 14 | **Météo OpenWeatherMap** | `weather_service.py` | 754 | Actif (si clé API) | Intégration OWM |
| 15 | **Corridors** | `corridor_service.py` | 490 | Actif | Corridors de déplacement |
| 16 | **Hotspots** | `hotspot_service.py` | 513 | Actif | Points chauds d'activité |
| 17 | **Zones** | `zone_service.py` | 369 | Actif | Zones comportementales |
| 18 | **Heatmap Fusion** | `heatmap_fusion_service.py` | 683 | Actif | Fusion WQS + Score Final |
| 19 | **Heures Légales** | `legal_hours_service.py` | 635 | Actif | Calcul lever/coucher soleil |
| 20 | **Analyse Waypoint** | `waypoint_analysis_service.py` | 955 | Actif | Analyse complète centrée waypoint |
| 21 | **Contours Organiques** | `organic_contour_generator.py` | 806 | Actif | Marching Squares + Chaikin |
| 22 | **Calibration** | `calibration_service.py` | ~700 | Actif | Optimisation des pondérations |
| 23 | **Stratégie** | `strategy_engine/v1/service.py` | 353 | Actif | Génération de stratégies |
| 24 | **WMS Québec** | `wms_engine/v1/service.py` | 204 | Actif | Couches WMS gouvernementales |
| 25 | **3D Terrain** | `engine_3d/v1/service.py` | 264 | Placeholder | Élévation, profils, viewshed |
| 26 | **Multi-facteur PHASE D** | `multifactor_scoring_engine.py` | 342 | Actif | Score composite Phase B+C |
| 27 | **Couches Dynamiques** | `dynamic_layer_generator.py` | ~400 | Actif | Couches saisonnières |
| 28 | **Knowledge Normalizer** | `knowledge_normalizer.py` | ~300 | Actif | Intégrité du Knowledge Layer |

## 3.2 Détail des moteurs clés

### 3.2.1 Scoring Unifié (1170 lignes)
- **Responsabilité:** Orchestre les 9 services de scoring canoniques
- **Pipeline:** ScoreContext → 9 services → agrégation pondérée → ajustement temporel → UnifiedScoreResult
- **Niveaux de sortie:** EXCELLENT (≥85), GOOD (≥70), MODERATE (≥50), POOR (≥30), VERY_POOR (<30)
- **Intégrations:** LegalHoursService (heures légales), AdvancedFactorsRegistry (PHASE B), SeasonalModel (PHASE C), HumanPressureRegistry (NIVEAU 3), CorridorRegistry (NIVEAU 4), MobilityRegistry (NIVEAU 5)
- **Modes d'analyse:** LIVE, PRE_RUT, RUT, POST_RUT

### 3.2.2 Modèles Comportementaux (1095 lignes)
- **12 facteurs intégrés:**
  1. Prédation (PredatorRisk, PredatorCorridors)
  2. Stress physiologique (Thermal/Hydric/Social)
  3. Hiérarchie sociale (DominanceScore, GroupBehavior)
  4. Compétition inter-espèces
  5. Signaux faibles (WeakSignals, Anomalies)
  6. Cycles hormonaux (rut, lactation, bois)
  7. Cycles digestifs (feeding→bedding)
  8. Mémoire territoriale (AvoidanceMemory, PreferredRoutes)
  9. Apprentissage comportemental (AdaptiveBehavior)
  10. Activité humaine non-chasse (HumanDisturbance)
  11. Disponibilité minérale (MineralAvailability, SaltLick)
  12. Conditions de neige (SnowDepth, CrustRisk, WinterPenalty)
- **Sortie:** ActivityPrediction, Timeline 24h, StrategyRecommendation

### 3.2.3 Prédiction Territoriale (1216 lignes)
- **Mêmes 12 facteurs** intégrés que les modèles comportementaux
- **Patterns d'activité horaire** par espèce (24h, heure par heure)
- **Probabilités d'activité** par période (aube, jour, crépuscule, nuit)
- **Sortie:** TerritorialScoreOutput avec score 0-100 et recommandations

### 3.2.4 Corridors (490 lignes)
- **Types:** movement, avoidance, preferred, feeding_transit
- **Règle stricte:** Aucun corridor ne traverse de grande masse d'eau
- **Intégrations:** PredictiveTerritorialService, BehavioralModelsService, WaterExclusionService

### 3.2.5 Hotspots (513 lignes)
- **Types:** activity_peak, feeding_zone, rut_zone, thermal_refuge, water_source, predation_risk, snow_impact, human_avoidance, mineral_site, composite_optimal
- **Formes:** 100% organiques via Marching Squares + Chaikin
- **Superficie:** 5000-10000 m²
- **Contour:** 1-2px, centre transparent (fill_opacity=0)

### 3.2.6 Scoring Dynamique (884 lignes)
- **7 composants pondérés:**
  - Weather (20%) — conditions météo actuelles
  - Activity (20%) — probabilité d'activité
  - Feeding (15%) — conditions d'alimentation
  - Movement (15%) — probabilité de déplacement
  - Temporal (15%) — heure, saison
  - Pressure (10%) — tendance barométrique
  - Lunar (5%) — phase de la lune
- **Seuils par espèce:** Orignal, Chevreuil, Ours, Dindon, Wapiti

### 3.2.7 Heatmap Fusion (683 lignes)
- **Fusion:** WQS (40%) + SCORE_FINAL (60%)
- **Sous-scores extraits:** densité, pression, mobilité, risques
- **Couleurs:** Or (Excellent), Vert (Bon), Ambre (Modéré), Orange (Faible), Rouge (Très faible)

### 3.2.8 Heures Légales (635 lignes)
- **Règle réglementaire:** Début = 30 min AVANT lever du soleil, Fin = 30 min APRÈS coucher
- **Calcul:** Bibliothèque `astral` (précision astronomique)
- **Fuseaux:** Canada (Montréal, Toronto), US (New York), France (Paris)
- **Statuts:** LEGAL, ILLEGAL, MARGINAL (<15 min des limites)

---

# 4. DONNÉES TERRAIN RÉELLES

## 4.1 Sources de données

| Source | Type | État | Méthode d'accès |
|--------|------|------|-----------------|
| **Overpass API (OSM)** | Exclusion terrain | ACTIF | Proxy backend `/api/v1/bionic/terrain/terrain-data` |
| **Open-Meteo** | Météo live + prévisions | ACTIF | Appel direct frontend |
| **OpenWeatherMap** | Météo détaillée | ACTIF (si clé API) | Backend `weather_service.py` |
| **WMS Québec** | Couches gouvernementales | ACTIF | WMSTileLayer Leaflet |
| **GPS Device** | Position utilisateur | ACTIF | `GeolocationService.js` |
| **NDVI Sentinel-2** | Densité végétale | PLACEHOLDER | `wms_engine` pré-configuré |
| **DEM 30m** | Élévation terrain | PLACEHOLDER | `engine_3d` simulé |
| **Données utilisateur** | Observations, waypoints, trips | ACTIF | MongoDB |

## 4.2 Détail par type de donnée

### NDVI réel
- **État:** SIMULÉ. Le `bionicModules.js` définit la couche "ndvi" mais les valeurs sont calculées par `fractalNoise` dans `BionicZoneService.js` (pas de satellite réel)
- **Source prévue:** Sentinel-2 via WMS Engine
- **Risque:** Toute l'analyse de densité végétale repose sur du bruit pseudo-aléatoire

### Pente réelle
- **État:** SIMULÉ. Le backend `engine_3d` utilise `base_elevation = 200 + (lat * 10) + (lng * -5)` (formule linéaire)
- **Source prévue:** DEM 30m (CDEM Québec)
- **Risque:** Les scores de pente ne reflètent pas la réalité terrain

### Peuplements forestiers réels
- **État:** PARTIELLEMENT RÉEL. Les couches WMS Québec (`peuplements_forestiers`) sont disponibles mais les données sont affichées en overlay visuel uniquement — pas intégrées dans le scoring
- **Source:** WMS Gouvernement du Québec (`geoegl.msp.gouv.qc.ca`)

### Hydrographie réelle
- **État:** MIXTE. L'exclusion des zones d'eau est RÉELLE (Overpass API/OSM avec 35 127 entités). Mais la couche "hydro" BIONIC pour le scoring utilise des données simulées
- **Source réelle:** OpenStreetMap via Overpass API

### Pression humaine réelle
- **État:** SIMULÉ. Le module `human_pressure_model.py` (838L) contient un modèle complet mais utilise des données de base simulées. L'exclusion des zones urbaines est RÉELLE (OSM)
- **Source prévue:** Données de fréquentation, routes, bâtiments (OSM partiel)

### Météo réelle
- **État:** ACTIF. Open-Meteo fournit des données temps réel (température, vent, humidité, pression, précipitations, prévisions horaires 48h, sunrise/sunset)
- **Source:** Open-Meteo API (gratuit, sans clé) + OpenWeatherMap (si clé disponible)

### Données OSM
- **État:** ACTIF. 35 127 entités d'exclusion pour la zone Québec/Lévis
- **Types:** Eau (400), Urbain (21 814), Routes (12 259), Infrastructure (654)
- **Cache:** 24h sur disque, tuiling automatique

### Données satellites
- **État:** PLACEHOLDER. WMS Engine pré-configuré mais pas de flux satellite temps réel
- **Couches prévues:** NDVI Sentinel-2, imagerie aérienne

### Données GPS
- **État:** ACTIF. `GeolocationService.js` + `BackgroundTracker.jsx` pour le suivi continu
- **Intégrations:** `gps_ultimate_router` (hotspots, sécurité, auto-cartographie)
- **Backend:** `hunting_trip_logger` pour l'enregistrement des sorties

### Observations terrain
- **État:** PARTIELLEMENT ACTIF. Backend `observations_router.py` (441L) + Frontend `FieldObservationForm.jsx` existent
- **Limitation:** Non connecté aux zones BIONIC (architecture de feedback manquante)

---

# 5. LES 15 COUCHES BIONIC V5

## 5.1 Inventaire détaillé

| # | Couche | ID | Type | Couleur | Rôle | Dépendances | Pondération |
|---|--------|----|------|---------|------|-------------|-------------|
| 1 | Zone de rut | `rut` | Comportementale | #FF4D6D | Zones d'activité reproductrice | Espèce, saison, hormones | Élevée en automne |
| 2 | Zone de repos | `repos` | Comportementale | #8B5CF6 | Remises et couches | Couvert, pente, exposition | Constante |
| 3 | Zone d'alimentation | `alimentation` | Comportementale | #22C55E | Gagnages et sources de nourriture | Peuplements, saison, NDVI | Élevée aube/crépuscule |
| 4 | Corridor faunique | `corridors` | Comportementale | #06B6D4 | Routes de déplacement | Topographie, eau, couvert | Variable selon mobilité |
| 5 | Habitat optimal | `habitats` | Environnementale | #10B981 | Zones refuge idéales | Forêt, eau, pente, exposition | Très élevée |
| 6 | Ensoleillement | `ensoleillement` | Environnementale | #FCD34D | Exposition solaire | Orientation, saison | Élevée en hiver |
| 7 | Orientation | `orientation` | Environnementale | #2196F3 | Orientation du terrain | DEM, aspect | Interne (scoring) |
| 8 | Hydrographie | `hydro` | Environnementale | #3B82F6 | Proximité eau | OSM waterways | Critique pour orignal/ours |
| 9 | Peuplements forestiers | `peuplements` | Environnementale | #15803D | Type de forêt | WMS Québec, NDVI | Très élevée |
| 10 | NDVI / Densité végétale | `ndvi` | Environnementale | #66BB6A | Verdure et biomasse | Satellite (simulé) | Élevée printemps/été |
| 11 | Pentes | `pentes` | Environnementale | #FF7043 | Déclivité du terrain | DEM (simulé) | Élevée pour mouvement |
| 12 | Saline potentielle | `salines` | Stratégique | #FFFF00 | Sites minéraux | Géologie, GPS | Critique pour orignal |
| 13 | Affût potentiel | `affuts` | Stratégique | #F5A623 | Positions de tir | Couvert, visibilité, vent | Très élevée |
| 14 | Trajets de chasse | `trajets` | Stratégique | #FF9800 | Routes recommandées | Accès, corridors, pression | Variable |
| 15 | Altitude relative | `altitude` | Environnementale | #78909C | Position altitudinale | DEM (simulé) | Modérée |

## 5.2 Interactions entre couches

```
rut ←→ corridors (le rut augmente l'utilisation des corridors)
alimentation ←→ repos (proximité = bonus de +6 dans le modèle hybride)
corridors ←→ affuts (position d'affût sur corridor = bonus de +5)
habitats ←→ hydro (proximité eau = qualité habitat)
ensoleillement ←→ peuplements (exposition influence le type de couvert)
pentes ←→ corridors (le gibier suit les courbes de niveau)
salines ←→ alimentation (les salines sont des points d'alimentation minérale)
altitude ←→ pression (altitude relative influence la pression de chasse)
ndvi ←→ alimentation (densité végétale = ressource alimentaire)
```

## 5.3 Impact sur le scoring

Chaque couche contribue au `score_Bionic_final` via les facteurs dans `bionicScoring.js`:

| Facteur scoring | Couches contributrices | Poids indicatif |
|-----------------|----------------------|-----------------|
| score_H (Habitat) | habitats, peuplements, ndvi | 20% |
| score_R (Rut/Comportement) | rut, corridors, repos | 15% |
| score_S (Stratégie) | affuts, trajets, salines | 15% |
| score_A (Accès) | corridors, altitude, pentes | 10% |
| score_T (Terrain) | pentes, orientation, altitude | 15% |
| score_P (Pression) | pression, distance routes | 10% |
| score_W (Météo) | données temps réel | 15% |

---

# 6. LES 5 ESPÈCES

## 6.1 Orignal (Alces americanus)

| Dimension | Détail |
|-----------|--------|
| **Couches actives** | 9: habitats, alimentation, corridors, repos, hydro, salines, rut, peuplements, pentes |
| **Préférences habitat** | Proximité eau, forêts de conifères, zones humides, marécages |
| **Comportement saisonnier** | **Printemps:** alimentation intensive post-hivernage, mise bas (C.1). **Été:** zones fraîches, eau. **Automne:** RUT INTENSE, déplacements erratiques. **Hiver:** ravages (yarding), économie d'énergie |
| **Corridors typiques** | Vallées riveraines, lisières forêt/marais, crêtes pour le rut |
| **Sensibilité vent** | Moyenne — détecte odeurs à 800m+ par vent favorable |
| **Sensibilité bruit** | Moyenne — curieux mais prudent |
| **Sensibilité pression** | Moyenne — s'adapte mais évite les zones de chasse intensive |
| **Température optimale** | -10°C à 15°C (stress thermique >25°C) |
| **Heures d'activité peak** | 5h-7h, 17h-20h (crépusculaire) |
| **Probabilités activité** | Aube: alimentation 65%, déplacement 25%. Jour: repos 70%. Crépuscule: alimentation 60%, déplacement 30% |

## 6.2 Chevreuil (Odocoileus virginianus)

| Dimension | Détail |
|-----------|--------|
| **Couches actives** | 8: habitats, alimentation, corridors, rut, affûts, repos, peuplements, ensoleillement |
| **Préférences habitat** | Lisières, écotones, bordures de champs, forêts mixtes |
| **Comportement saisonnier** | **Printemps:** faonnage (C.1), dispersion juvénile (C.2). **Été:** gagnages ouverts. **Automne:** RUT, marquage territorial. **Hiver:** ravages, dépendance au couvert |
| **Corridors typiques** | Bordures de champs, haies, lisières forestières, ruisseaux |
| **Sensibilité vent** | Élevée — détection olfactive supérieure |
| **Sensibilité bruit** | Élevée — fuit rapidement |
| **Sensibilité pression** | Élevée — devient nocturne en zone chassée |
| **Température optimale** | 0°C à 20°C (stress thermique >30°C) |
| **Heures d'activité peak** | 5h-7h, 18h-20h |
| **Probabilités activité** | Aube: alimentation 70%, déplacement 20%. Jour: repos 75%. Crépuscule: alimentation 65%, déplacement 25% |

## 6.3 Ours noir (Ursus americanus)

| Dimension | Détail |
|-----------|--------|
| **Couches actives** | 8: habitats, alimentation, corridors, repos, hydro, peuplements, ndvi, pentes |
| **Préférences habitat** | Forêt dense, proximité eau, altitude modérée, zones riches en petits fruits |
| **Comportement saisonnier** | **Printemps:** sortie d'hibernation, alimentation INTENSIVE. **Été:** petits fruits, insectes. **Automne:** hyperphagie pré-hibernation. **Hiver:** hibernation |
| **Corridors typiques** | Ravins, vallées boisées, corridors vers sources alimentaires |
| **Sensibilité vent** | Faible à modérée — odorat excellent mais moins craintif |
| **Sensibilité bruit** | Faible — s'habitue aux bruits humains |
| **Sensibilité pression** | Faible — concentré sur l'alimentation |
| **Température optimale** | 5°C à 25°C (stress thermique >35°C) |
| **Heures d'activité peak** | 6h-9h, 17h-19h (plus diurne que les cervidés) |
| **Probabilités activité** | Aube: alimentation 50%, déplacement 35%. Jour: alimentation 40%, repos 40%. Crépuscule: alimentation 55%, déplacement 30% |

## 6.4 Dindon sauvage (Meleagris gallopavo)

| Dimension | Détail |
|-----------|--------|
| **Couches actives** | 7: habitats, alimentation, repos, affûts, peuplements, ensoleillement, ndvi |
| **Préférences habitat** | Lisières, champs ouverts, vergers, forêts de feuillus clairsemées |
| **Comportement saisonnier** | **Printemps:** parade nuptiale, glouglement. **Été:** élevage poussins. **Automne:** regroupement, alimentation. **Hiver:** dortoirs communaux en arbres |
| **Corridors typiques** | Bordures de champs → dortoirs (arbres), itinéraires d'alimentation prévisibles |
| **Sensibilité vent** | Modérée — affecte la détection des prédateurs |
| **Sensibilité bruit** | Très élevée — fuit au moindre bruit |
| **Sensibilité pression** | Modérée — s'adapte en changeant de dortoir |
| **Température optimale** | 5°C à 25°C (stress thermique >35°C) |
| **Heures d'activité peak** | 6h-8h, 16h-18h (strictement diurne) |
| **Probabilités activité** | Matin: alimentation 60%, déplacement 30%. Jour: alimentation 50%, repos 30%. Soir: retour au dortoir 70% |

## 6.5 Wapiti (Cervus canadensis) — étendu

| Dimension | Détail |
|-----------|--------|
| **Couches actives** | 8: habitats, alimentation, corridors, repos, rut, peuplements, pentes, altitude |
| **Préférences habitat** | Prairies alpines, forêts boréales ouvertes, vallées montagneuses |
| **Comportement saisonnier** | **Printemps:** migration vers alpages. **Été:** pâturages d'altitude. **Automne:** RUT SPECTACULAIRE, bugling. **Hiver:** descente en vallée |
| **Corridors typiques** | Sentiers migratoires altitudinaux, vallées entre massifs |
| **Température optimale** | -10°C à 20°C (stress thermique >28°C) |
| **Heures d'activité peak** | 5h-7h, 17h-20h |

---

# 7. LE SCORING COMPLET

## 7.1 Architecture du scoring

Le scoring BIONIC V5 est organisé en **3 niveaux:**

### Niveau 1 — Frontend (`bionicScoring.js` — 610 lignes)
**15 fonctions de scoring individuelles:**

| Fonction | Entrée | Sortie | Description |
|----------|--------|--------|-------------|
| `scoreSlope` | pente (°), contexte | 0-1 | Score basé sur la déclivité |
| `scoreWaterDistance` | distance (m) | 0-1 | Proximité eau (décroissance exponentielle) |
| `scoreForestDensity` | densité (%) | 0-1 | Couvert forestier |
| `scoreForestType` | type peuplement, espèce | 0-1 | Adéquation du peuplement |
| `scoreStandType` | type stand | 0-1 | Matrice de peuplement |
| `scoreNDVI` | valeur NDVI | 0-1 | Végétation active |
| `scoreHumanPressure` | pression (0-100) | 0-1 | Inversement proportionnel |
| `scoreWindImpact` | vitesse, direction | 0-1 | Impact olfactif |
| `scoreTemperature` | temp °C, espèce | 0-1 | Confort thermique |
| `scorePrecipitation` | mm/h | 0-1 | Tolérance |
| `scorePressure` | hPa | 0-1 | Pression barométrique |
| `scoreMoonPhase` | phase 0-1 | 0-1 | Luminosité nocturne |
| `scoreElevation` | altitude relative | 0-1 | Position dominante |
| `scoreAccessibility` | distance route | 0-1 | Facilité d'accès |
| `getScoresForWaypoint` | waypoint, espèce | Object | Agrégation H-R-S-A-T-P |

### Niveau 2 — Frontend (`bionicHybridModel.js` — 378 lignes)
**10 règles d'ajustement:**

| Règle | Condition | Ajustement | Description |
|-------|-----------|------------|-------------|
| HABITAT_RUT_SYNERGY | H≥70 ET R≥70 | +8 | Synergie habitat-rut |
| FEEDING_RESTING_PROXIMITY | <200m et <300m | +6 | Zones proches |
| CORRIDOR_AFFUT_COMBO | A≥75 ET T≥65 | +5 | Affût sur corridor |
| TRANSITION_ZONE_BONUS | isTransition=true | +7 | Zone écotone |
| WATER_COMPLEX_BONUS | confluence/méandre | +5 | Complexité hydro |
| HIGH_PRESSURE_PENALTY | humanPressure>70 | -12 | Forte pression |
| EXPOSED_POSITION_PENALTY | sparse+pente>20 | -8 | Position exposée |
| POOR_ACCESS_PENALTY | T<40 | -5 | Accès difficile |
| OPTIMAL_STAND_TYPE | tremble/cèdre/érable | +4 | Peuplement optimal |
| DOMINANT_POSITION | élévation>30 | +3 | Position dominante |

**Pipeline IA Niveau 2:** Le score ajusté est envoyé au backend AI Engine (GPT-5.2) pour un raffinement contextuel. Retourne un ajustement IA de -10 à +10 points.

### Niveau 3 — Backend (9 services, 3822 lignes total)

**Pondérations des 9 services:**

| Service | Catégorie | Poids par défaut | Description |
|---------|-----------|-----------------|-------------|
| Probability | Probabilité | ~15% | Présence estimée |
| Habitat | Habitat | ~15% | Qualité structurelle |
| Pressure | Pression | ~10% | Pression humaine |
| Weather | Météo | ~15% | Conditions actuelles |
| Behavior | Comportement | ~15% | Activité du gibier |
| MultiFactor | Multi-facteur | ~10% | Combinaisons |
| Density | Densité | ~8% | Population |
| Risk | Risque | ~7% | Dangers |
| Mobility | Mobilité | ~5% | Déplacements |

### Matrice de peuplements forestiers (dans `bionicScoring.js`)

| Peuplement | Orignal | Chevreuil | Ours | Dindon |
|------------|---------|-----------|------|--------|
| Tremblaie | 0.95 | 0.90 | 0.85 | 0.80 |
| Cédrière | 0.90 | 0.95 | 0.70 | 0.60 |
| Érablière | 0.80 | 0.85 | 0.90 | 0.95 |
| Sapinière | 0.85 | 0.80 | 0.80 | 0.50 |
| Pessière | 0.80 | 0.60 | 0.75 | 0.40 |
| Pinède | 0.75 | 0.85 | 0.80 | 0.75 |
| Mixte | 0.85 | 0.90 | 0.85 | 0.85 |

## 7.2 Limites actuelles du scoring

1. **Données simulées:** NDVI, pente, élévation, pression humaine sont simulées → scores non fiables pour ces facteurs
2. **UI non connectée:** Le scoring backend (9 services, WQS, Heatmap) n'est PAS appelé par le frontend Mon Territoire
3. **Pas de calibration terrain:** Le système de calibration existe (backend) mais n'a pas de données réelles
4. **Pas de feedback loop:** Les observations terrain ne rétroalimentent pas les scores

---

# 8. LE MODÈLE HYBRIDE (RÈGLES + IA)

## 8.1 Architecture (`bionicHybridModel.js` — 378 lignes)

```
[Données terrain] → [bionicScoring.js] → [Score brut H-R-S-A-T-P]
                                              ↓
                                    [Moteur de Règles - 10 règles]
                                              ↓
                                    [Score ajusté Niveau 1]
                                              ↓
                                    [AI Engine GPT-5.2 - Niveau 2]
                                              ↓
                                    [Score final BIONIC™]
```

## 8.2 Les 10 règles détaillées

Voir tableau en section 7.1, Niveau 2.

## 8.3 Pipeline IA Niveau 2

- **Modèle:** GPT-5.2 via `AI Engine` backend
- **Entrée:** Score Niveau 1, contexte complet (espèce, météo, terrain, saison)
- **Sortie:** Ajustement IA (-10 à +10), recommandations textuelles
- **Fallback:** Si AI Engine indisponible, le score Niveau 1 est utilisé tel quel
- **Latence cible:** < 2 secondes

## 8.4 Limites

- L'appel IA est optionnel et dépend de la disponibilité de la clé API
- Le modèle n'est pas entraîné sur des données de chasse réelles
- Pas de boucle d'apprentissage automatique (résultats terrain → ajustement modèle)

---

# 9. LE MOTEUR MÉTÉO

## 9.1 Architecture

**Deux sources de données météo:**

### Frontend — Open-Meteo (`bionicWeatherEngine.js` — 420 lignes)
- **API:** Open-Meteo (gratuit, sans clé)
- **Données actuelles:** température, humidité, ressenti, précipitations, code météo, couverture nuageuse, pression, vent (vitesse, direction, rafales)
- **Prévisions horaires 48h:** température, humidité, probabilité précipitations, précipitations, couverture nuageuse, vent
- **Données quotidiennes:** sunrise, sunset, T°max, T°min
- **Fuseau:** America/Toronto

### Backend — OpenWeatherMap (`weather_service.py` — 754 lignes)
- **API:** OpenWeatherMap (nécessite clé API `OWM_API_KEY`)
- **Mode:** "inactive" si clé absente
- **Cache:** 10 min (actuel), 30 min (prévisions)
- **Données:** température, ressenti, humidité, pression, vent (vitesse, direction, rafales), précipitations 1h, neige 1h, couverture nuageuse, visibilité, sunrise/sunset
- **Conditions:** CLEAR, CLOUDS, RAIN, DRIZZLE, SNOW, THUNDERSTORM, MIST, FOG

## 9.2 Analyse du vent

| Paramètre | Seuil | Impact scoring |
|-----------|-------|----------------|
| Vent < 10 km/h | Faible | Activité normale, dispersion odeurs faible |
| Vent 10-20 km/h | Modéré | Activité réduite 10-20%, bonne dispersion odeurs |
| Vent 20-30 km/h | Fort | Réduction activité 30%, risque olfactif élevé |
| Vent > 30 km/h | Très fort | Réduction activité 50%+, gibier couché |
| Direction vent | Variable | Impacte le chemin d'approche et le positionnement |

## 9.3 Température et impact

| Espèce | Optimal (°C) | Stress froid (°C) | Stress chaud (°C) |
|--------|-------------|-------------------|-------------------|
| Orignal | -5 à 15 | < -25 | > 25 |
| Chevreuil | 0 à 20 | < -20 | > 30 |
| Ours | 5 à 25 | < -10 | > 35 |
| Dindon | 5 à 25 | < -15 | > 35 |
| Wapiti | -10 à 20 | < -30 | > 28 |

## 9.4 Pression barométrique

- **Optimale:** 1010-1025 hPa
- **Tendance montante:** Bonus activité (+10-15%)
- **Tendance descendante:** Alimentation intensive avant tempête (+20%)
- **Pression stable:** Score neutre
- **Front froid:** Pic d'activité 6-12h avant l'arrivée

## 9.5 Fronts météorologiques

Le Weather Engine détecte 4 types:
- **NONE:** Pas de front — conditions stables
- **COLD:** Front froid — pic d'activité avant, réduction après
- **WARM:** Front chaud — activité modérée
- **UNSTABLE:** Instabilité — comportement imprévisible

## 9.6 Impact scoring

Le score météo contribue à 20% du scoring dynamique et 15% du scoring frontend. Composants:
- Score température (confort espèce)
- Score vent (activité + risque olfactif)
- Score précipitations (tolérance espèce)
- Score pression (tendance barométrique)
- Score conditions (clair, nuageux, pluie, neige...)

## 9.7 Impact stratégie

- **Direction du vent** → calcul du chemin d'approche optimal (éviter d'être au vent)
- **Visibilité** → recommandation distance d'affût
- **Précipitations** → recommandation équipement et type de chasse
- **Température** → recommandation timing (gibier actif aux heures optimales)

---

# 10. LE STRATEGY ENGINE

## 10.1 Architecture (`bionicStrategyEngine.js` — 496 lignes)

### Pipeline de stratégie
```
[Waypoint + Scores + Météo + Territoire]
    ↓
calculateStandProjections()     → Score actuel, +1h, +3h
calculateApproachPath()         → Direction, vent, couvert
analyzeGameMovement()           → Probabilités activité, directions
evaluateRisks()                 → Risques olfactifs, visuels, sonores
recommendProducts()             → Équipement recommandé
calculateLiveFlags()            → Drapeaux LIVE temps réel
    ↓
[Stratégie complète avec résumé exécutif]
```

### Backend (`strategy_engine/v1/service.py` — 353 lignes)

**Patterns par espèce:**

| Espèce | Heures actives | Alimentation | Terrain préféré | Sensibilité | Distance approche |
|--------|---------------|--------------|-----------------|-------------|-------------------|
| Deer | Aube, crépuscule | Aube, après-midi, crépuscule | Lisière, forêt | Élevée | 30m |
| Moose | Aube, crépuscule, nuit | Aube, après-midi, crépuscule | Marais, forêt | Moyenne | 50m |
| Bear | Aube→après-midi | Matin, après-midi | Forêt, lisière | Faible | 40m |
| Turkey | Aube→après-midi | Matin, après-midi | Champ, lisière | Très élevée | 20m |

**Modificateurs saisonniers:**

| Saison | Boost activité | Focus alimentaire | Territorial | Notes |
|--------|---------------|-------------------|-------------|-------|
| Printemps | 1.2x | Oui | Oui | Sortie hibernation |
| Été | 0.8x | Oui | Non | Chaleur réduit activité |
| Automne | 1.5x | Oui | Oui | RUT — activité maximale |
| Hiver | 0.9x | Oui | Non | Conservation énergie |

**Impact météo sur stratégie:**

| Condition | Modificateur | Visibilité | Dispersion odeurs |
|-----------|-------------|------------|-------------------|
| Clair | 1.0 | Excellente | Bonne |
| Nuageux | 1.1 | Bonne | Modérée |
| Pluie | 0.7 | Réduite | Excellente (lavage) |
| Neige | 0.8 | Réduite | Bonne |
| Brouillard | 1.2 | Très réduite | Très faible |
| Vent fort | 0.6 | Bonne | Élevée (risque) |

## 10.2 Projections

- **Score actuel:** Score BIONIC en temps réel
- **Score +1h:** Ajusté selon prévisions météo horaires
- **Score +3h:** Ajusté selon tendance météo

## 10.3 Fenêtres optimales

Calculées en croisant:
- Heures légales (30 min avant lever → 30 min après coucher)
- Pics d'activité par espèce
- Conditions météo favorables
- Niveau de pression de chasse

## 10.4 Chemins d'approche

- **Direction:** Toujours face au vent (anti-olfactif)
- **Couvert:** Privilégie les zones denses (forêt, haies)
- **Distance:** Selon sensibilité espèce (20-50m)
- **Bruit:** Évite les zones de feuilles sèches, branches

## 10.5 Risques évalués

- **Risque olfactif:** Direction vent vs position chasseur
- **Risque visuel:** Couvert disponible, exposition
- **Risque sonore:** Type de terrain sous les pieds
- **Risque thermique:** Température et stress gibier

## 10.6 Flags LIVE

| Flag | Condition | Signification |
|------|-----------|---------------|
| HOT_ZONE | Score > 80 | Zone à haut potentiel |
| COLD_ZONE | Score < 40 | Zone déconseillée |
| WIND_ALERT | Vent > 25 km/h | Attention vent |
| LEGAL_WARNING | < 30 min de la fin | Bientôt hors période |
| ACTIVITY_PEAK | Pic horaire | Moment optimal |
| PRESSURE_RISING | Pression monte | Activité accrue probable |

---

# 11. SYSTÈME FREEMIUM / PREMIUM

## 11.1 Les 3 niveaux (`freemium_engine/router.py` — 443 lignes)

### FREE (Gratuit)

| Fonctionnalité | Limite |
|----------------|--------|
| Générations stratégie / jour | 3 |
| Vérifications météo / jour | 10 |
| Zones territoire | 2 |
| Waypoints par zone | 5 |
| Historique analytics | 7 jours |
| Recommandations IA | 5 / jour |
| Phases Plan Maître | 2 |
| Export rapports | Non |
| Règles personnalisées | Non |
| Support prioritaire | Non |
| Couches avancées | Non |
| Live Heading | Non |

### PREMIUM (Payant — Abonnement)

| Fonctionnalité | Limite |
|----------------|--------|
| Générations stratégie / jour | 50 |
| Vérifications météo / jour | 100 |
| Zones territoire | 10 |
| Waypoints par zone | 50 |
| Historique analytics | 90 jours |
| Recommandations IA | 50 / jour |
| Phases Plan Maître | 5 |
| Export rapports | Oui |
| Règles personnalisées | Oui |
| Support prioritaire | Non |
| Couches avancées | Oui |
| Live Heading | Non |

### PRO (Professionnel)

| Fonctionnalité | Limite |
|----------------|--------|
| Toutes les fonctionnalités | Illimitées |
| Support prioritaire | Oui |
| Couches avancées | Oui |
| Live Heading | Oui |
| API access | Oui |
| White-label | Oui |
| Multi-territoire | Illimité |

## 11.2 Logique de progression

```
FREE → Utilisateur découvre les couches de base et 2 zones
     → Atteint la limite de 3 stratégies/jour
     → Pop-up upsell (upsell_engine)
     → PREMIUM unlock: 10 zones, 50 waypoints, export, couches avancées
          → Chasseur sérieux veut Live Heading et API
          → PRO unlock: tout illimité + support
```

## 11.3 Logique de rétention

- **Quotas graduels:** Le FREE donne assez pour créer l'habitude, pas assez pour tout faire
- **Alertes de zones:** Les favoris avec alertes créent un engagement récurrent
- **Groupes:** Le module collaboratif crée un effet réseau (si mes amis sont là, j'y reste)
- **Saisonnalité:** Les données changent avec les saisons → raison de revenir
- **Notifications push:** Rappels lors des pics d'activité, changements météo

## 11.4 Ce qui devrait être réservé aux PROS

- **Scoring backend complet** (9 services unifiés, heatmap fusion)
- **Modèle hybride IA** (Niveau 2 avec GPT-5.2)
- **Analyse waypoint complète** (tous les sous-scores)
- **Corridors dynamiques** (calcul en temps réel)
- **Live Heading** (navigation immersive 3D)
- **API access** (intégration outils tiers)
- **Export données brutes** (CSV, GeoJSON)

## 11.5 Tarification (`payment_engine/router.py`)

| Package | Prix | Durée |
|---------|------|-------|
| PREMIUM Mensuel | ~14.99$/mois | 1 mois |
| PREMIUM Annuel | ~99.99$/an | 12 mois |
| PRO Mensuel | ~29.99$/mois | 1 mois |
| PRO Annuel | ~199.99$/an | 12 mois |

---

# 12. SEO / ASO / DISTRIBUTION

## 12.1 SEO Engine (`seo_engine/` — 11 140 lignes)

### Composants

| Composant | Fichier | Rôle |
|-----------|---------|------|
| Clusters | `seo_clusters.py` | Groupement thématique de mots-clés |
| Pages | `seo_pages.py` | Gestion des pages SEO |
| JSON-LD | `seo_jsonld.py` | Données structurées Schema.org |
| Analytics | `seo_analytics.py` | KPIs SEO (classement, trafic, conversions) |
| Automation | `seo_automation.py` | Publication automatique |
| Generation | `seo_generation.py` | Génération de contenu IA |
| Enrichment | `seo_enrichment.py` | Enrichissement des contenus |
| Normalization | `seo_normalization.py` | Nettoyage et normalisation |
| Rules Engine | `seo_rules_engine.py` | Règles de scoring SEO |

### Articles piliers générés (dans `/app/docs/`)

| Sujet | Fichier | Mots-clés cibles |
|-------|---------|-------------------|
| Orignal | `generated_pillar_orignal.md` | chasse orignal québec |
| Appel orignal | `generated_pillar_appel_orignal.md` | technique appel orignal |
| Appel orignal technique | `generated_pillar_appel_orignal_technique_call.md` | call technique orignal |
| Chevreuil | `generated_pillar_chasse_chevreuil_quebec.md` | chasse chevreuil québec |
| Ours noir | `generated_pillar_chasse_ours_noir_quebec.md` | chasse ours noir québec |
| Wapiti | `generated_pillar_chasse_wapiti_quebec.md` | chasse wapiti québec |
| Abitibi | `generated_pillar_chasse_abitibi_quebec.md` | chasse abitibi |
| Laurentides | `generated_pillar_chasse_laurentides_quebec.md` | chasse laurentides |
| Pistage | `generated_pillar_pistage_gibier.md` | pistage repérage gibier |
| Rut orignal | `generated_pillar_rut_orignal.md` | rut orignal québec |

### Objectif stratégique
- **Positionnement:** Devenir la référence #1 pour "chasse intelligente québec"
- **Trafic organique cible:** +300% en 12 mois
- **Conversion:** Visiteur → FREE → PREMIUM → PRO

## 12.2 ASO (App Store Optimization)

- **État:** Non implémenté (application web uniquement, pas d'app native)
- **Potentiel:** Conversion en PWA avec publication sur stores

## 12.3 Marketing

- **Marketing Calendar Engine:** Planification de campagnes saisonnières
- **Marketing Engine:** Outils de marketing automatisé
- **Partner Engine:** Gestion des partenariats (pourvoiries, boutiques)
- **Affiliate Engine:** Programme d'affiliation
- **Ad Spaces Engine:** Espaces publicitaires dans l'app

## 12.4 Contenu éducatif

- 10+ articles piliers générés par IA
- Formations en ligne (`formations_engine`)
- Tutoriels intégrés (`tutorial_engine`)
- Documentation API complète (`/api/docs`, `/api/redoc`)

## 12.5 Positionnement marché

- **Marché cible:** Chasseurs québécois (400 000+ permis/an)
- **Différenciateur:** Seule plateforme combinant IA + données terrain + météo + scoring pour la chasse
- **Compétiteurs:** onX Hunt, HuntStand (US-centric, pas de scoring IA)
- **Avantage:** Données OSM québécoises + WMS gouvernemental + 15 couches BIONIC

---

# 13. SÉCURITÉ & CONFORMITÉ

## 13.1 Authentification

- **JWT:** Tokens avec expiration, refresh
- **Google OAuth:** Intégration hybride (JWT + Google)
- **Mot de passe:** Hashage bcrypt
- **Sessions:** `session_id` côté frontend pour le tracking

## 13.2 Permissions

- **Rôles:** `roles_engine` (admin, user, partner, pro)
- **Tiers:** `freemium_engine` (FREE, PREMIUM, PRO)
- **Feature flags:** `feature_controls` (activation/désactivation dynamique)
- **Master Switch:** `global_master_switch` (bouton rouge — désactive tout)

## 13.3 Validation des données

- **Backend:** Pydantic sur TOUTES les routes (validation automatique)
- **Frontend:** Validation formulaires React
- **API:** Bornes géographiques (Québec: lat 40-65, lon -85 à -50)
- **Fichiers:** Validation type et taille sur l'upload

## 13.4 Logging et monitoring

- **Python logging structuré** avec conformité G-SEC
- **Supervisord** pour le monitoring des processus
- **Health checks:** `/api/v1/bionic/health`, endpoints status par module
- **Logging des actions utilisateur** (analytics_engine)

## 13.5 Conformité légale

- **Cookies:** Bannière de consentement (`CookieConsent`)
- **Vie privée:** Données restent au Québec (MongoDB local)
- **Heures légales:** Calcul conforme à la réglementation MFFP
- **Langue:** Interface bilingue FR/EN (`LanguageContext`)

## 13.6 Sécurité terrain

- **Safety Engine:** `safety_engine.py` dans GPS Ultimate
- **Zones de danger:** Détection et alertes
- **Groupes:** Tracking live des membres (sécurité en forêt)
- **Hors-ligne:** Mode offline pour les zones sans réseau

---

# 14. PERFORMANCE & SCALABILITÉ

## 14.1 Limites identifiées

### CPU/GPU mobile
- **Génération des zones:** 15 couches × N zones × polygone organique (16 vertices + Chaikin 2x = 65 vertices) — potentiellement lourd sur mobile
- **Exclusion terrain:** Validation de chaque point contre 35 000+ entités OSM
- **Spatial hashing:** Optimisation implémentée côté client

### Réseau
- **Overpass API:** Limite de requête par zone (tiling nécessaire)
- **Open-Meteo:** API gratuite — pas de garantie SLA
- **WMS Québec:** Serveurs gouvernementaux — latence variable
- **MongoDB:** Local — bon pour le développement, à migrer pour production

### Batterie
- **GPS continu:** `BackgroundTracker` consomme de la batterie
- **Mises à jour fréquentes:** Météo, exclusions, zones — appels réseau
- **Leaflet rendering:** Rendu de polygones complexes en continu

### Overpass API
- **Limite bbox:** Tiling automatique (`TILE_MAX_LAT=0.25, TILE_MAX_LNG=0.35`)
- **Cache 24h:** Réduit les appels
- **Rate limiting:** Pas de gestion explicite des quotas Overpass
- **Risque:** Overpass peut être lent ou indisponible

## 14.2 Optimisations implémentées

| Optimisation | Fichier | Description |
|------------|---------|-------------|
| **Spatial hashing** | `BionicZoneService.js` | Indexation spatiale pour la validation d'exclusion |
| **Tiling Overpass** | `BionicZoneService.js` | Découpage en tuiles pour l'API |
| **Cache disque 24h** | `terrain_data_router.py` | Cache des réponses Overpass |
| **Lazy loading** | `App.js` | 20+ composants chargés en lazy |
| **Cache météo** | `weather_service.py` | 10 min (actuel), 30 min (prévisions) |
| **Viewport clearing** | `MonTerritoireBionicPage.jsx` | Vidage des zones au changement de vue |
| **Render blocking** | `BionicZoneService.js` | Pas de rendu avant chargement des exclusions |
| **Hot reload** | Supervisor | Redémarrage automatique frontend/backend |

## 14.3 Optimisations des zones organiques

| Paramètre | Valeur | Impact |
|-----------|--------|--------|
| Vertices de base | 16 | Bon compromis détail/performance |
| Chaikin iterations | 2 | 65 vertices final — fluide mais léger |
| Octaves fractal | 4 | Bon niveau de détail organique |
| Compacité max | 0.85 | Rejette les cercles (réduit les recalculs) |
| Variance arêtes min | 0.03 | Rejette les polygones réguliers |
| Aire cible | 5000 m² ± 500 | Scaling proportionnel si hors cible |

## 14.4 Points d'attention pour la scalabilité

1. **MonTerritoireBionicPage.jsx** (2294 lignes) — Candidate au refactoring en sous-composants
2. **BionicZoneService.js** (782 lignes) — Exclusion côté client lourd → envisager un worker Web
3. **35 000+ entités OSM** — La validation point-par-point est O(n) mitigée par spatial hashing mais reste le goulot
4. **MongoDB local** — Migration vers Atlas ou replica set pour la production
5. **Pas de CDN** — Images et assets servis directement
6. **Pas de SSR** — React client-side uniquement → SEO limité pour le contenu dynamique

---

# RÉSUMÉ EXÉCUTIF

## Forces principales
1. **Architecture modulaire robuste:** 78 modules isolés, contrats formels, orchestrateur pur
2. **Moteur de scoring multi-niveaux:** Frontend (15 fonctions) + Hybrid (10 règles + IA) + Backend (9 services)
3. **Exclusion "Tolérance Zéro" validée:** 35 127 entités OSM, buffer 2000m pour grandes masses d'eau
4. **Polygones organiques conformes:** Chaikin 2x, compacité <0.85, variance >0.03
5. **15 couches BIONIC** avec filtrage par espèce et 5 espèces documentées
6. **Modèle hybride Règles + IA:** Pipeline de scoring sophistiqué
7. **Météo temps réel:** Open-Meteo + OpenWeatherMap intégrés
8. **SEO Engine complet:** 11 140 lignes, 10+ articles piliers

## Faiblesses principales
1. **Données simulées:** NDVI, pente, élévation, pression humaine — scoring partiellement fictif
2. **UI ↔ Backend déconnecté:** Le scoring backend (WQS, Heatmap, 9 services) n'est pas appelé par le frontend
3. **Observations → Zones non connecté:** Architecture de feedback absente
4. **Page Mon Territoire surchargée:** 2294 lignes, difficile à maintenir
5. **Pas de données de chasse réelles:** Le modèle IA n'est pas calibré terrain
6. **MapPage limitée:** Manque les contrôles espèce + ON/OFF

## Risques
1. **Overpass API:** Indisponibilité possible → impact sur les exclusions
2. **Performance mobile:** 15 couches × exclusions = charge importante
3. **Dépendance API gratuites:** Open-Meteo sans SLA
4. **Données simulées prises pour réelles:** Utilisateur peut baser ses décisions sur du bruit

## Opportunités
1. **Connexion UI ↔ Backend scoring:** Débloque 90% de la valeur backend déjà codée
2. **Données Sentinel-2 (NDVI réel):** Transforme le scoring végétal
3. **DEM réel (CDEM):** Pente, altitude, viewshed réels
4. **Feedback loop:** Observations terrain → calibration automatique
5. **PWA + App Stores:** Distribution mobile native
6. **Partenariats pourvoiries:** Données terrain exclusives

## Priorités recommandées

| Priorité | Tâche | Impact |
|----------|-------|--------|
| P0 | Connexion UI ↔ WQS/Heatmap backend | Valeur immédiate |
| P1 | Mode Comparaison Espèces | UX différenciante |
| P1 | Contrôles MapPage identiques | Cohérence produit |
| P1 | PHASE E: Conditions Saisonnières | Engagement utilisateur |
| P2 | Intégration NDVI réel (Sentinel-2) | Fiabilité scoring |
| P2 | Intégration DEM réel | Fiabilité pente/altitude |
| P2 | Feedback loop observations → zones | Calibration automatique |
| P3 | PWA + App Stores | Distribution mobile |
| P3 | ML comportemental (PHASE H) | Prédiction avancée |

---

*Document généré le 27 Février 2026 — Analyse exhaustive de 351 025 lignes de code (207 482 backend + 143 543 frontend)*
