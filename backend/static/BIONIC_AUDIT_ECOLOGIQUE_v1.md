# AUDIT ÉCOLOGIQUE BIONIC — VERSION ACTUELLE
# ══════════════════════════════════════════════════
# Date: 2026-03-16
# Auditeur: Emergent AI (mode observation)
# Périmètre: TOUS les modèles/règles écologiques BIONIC
# Statut: OBSERVATION UNIQUEMENT — AUCUNE MODIFICATION
# ══════════════════════════════════════════════════

---

## TABLE DES MATIÈRES

1. [Inventaire des Modules / Engines](#1-inventaire-des-modules--engines)
2. [Schéma de dépendances](#2-schema-de-dependances)
3. [Thème: Zones d'alimentation](#3-theme-zones-dalimentation)
4. [Thème: Zones de repos](#4-theme-zones-de-repos)
5. [Thème: Corridors / Déplacements](#5-theme-corridors--deplacements)
6. [Thème: Sécurité / Couvert](#6-theme-securite--couvert)
7. [Thème: Thermique / Refuge](#7-theme-thermique--refuge)
8. [Thème: Hotspots](#8-theme-hotspots)
9. [Thème: Prédiction / Comportement](#9-theme-prediction--comportement)
10. [Pipeline global: du brut au score à la carte](#10-pipeline-global)
11. [Limites connues](#11-limites-connues)

---

## 1. INVENTAIRE DES MODULES / ENGINES

### 1.1 — LEGACY ENGINE (GELÉ — NE PAS MODIFIER)

| # | Module | Fichier | Rôle | Espèces | Contexte |
|---|--------|---------|------|---------|----------|
| L1 | ThermalScore v1.0 | `bionic_engine.py` L172-178 | Confort thermique (T°, aspect, élévation, canopée, eau) | Toutes | Backend analyse |
| L2 | WetnessScore v1.0 | `bionic_engine.py` L180-186 | Hydrologie (TWI, distance ruisseau, zone humide, précip, NDWI) | Toutes | Backend analyse |
| L3 | FoodScore v1.0 | `bionic_engine.py` L187-193 | Nourriture (NDVI, type forêt, lisière, glands, brout) | Toutes | Backend analyse |
| L4 | PressureScore v1.0 | `bionic_engine.py` L194-200 | Pression humaine (routes, bâtiments, chasse, bruit, lumière) | Toutes | Backend analyse |
| L5 | AccessScore v1.0 | `bionic_engine.py` L201-207 | Accessibilité chasse (sentiers, routes, terrain, visibilité, parking) | Toutes | Backend analyse |
| L6 | CorridorScore v1.0 | `bionic_engine.py` L208-214 | Corridors (connectivité, goulots, traversées, continuité, barrières) | Toutes | Backend analyse |
| L7 | GeoFormScore v1.0 | `bionic_engine.py` L215-220 | Géomorphologie (pente, aspect, courbure, rugosité, type relief) | Toutes | Backend analyse |
| L8 | CanopyScore v1.0 | `bionic_engine.py` L221-228 | Canopée (hauteur, fermeture, sous-bois, diversité, classe âge) | Toutes | Backend analyse |
| L-M | MooseScore v1.0 | `bionic_engine.py` L232-248 | Modèle orignal (thermal 15%, wetness 20%, food 25%, pressure 15%, corridor 10%, canopy 10%, geoform 5%) | Orignal | Backend analyse |
| L-D | DeerScore v1.0 | `bionic_engine.py` L249-264 | Modèle cerf (food 30%, corridor 15%, pressure 15%, thermal 10%, wetness 10%, canopy 10%, geoform 10%) | Cerf | Backend analyse |
| L-B | BearScore v1.0 | `bionic_engine.py` L265-278 | Modèle ours (food 35%, pressure 20%, wetness 15%, thermal 10%, corridor 10%, canopy 5%, geoform 5%) | Ours | Backend analyse |
| L-C | CaribouScore v1.0 | `bionic_engine.py` L280-296 | Modèle caribou (pressure 25%, food 20%, thermal 15%, wetness 15%, corridor 15%) | Caribou | Backend analyse |
| L-W | WolfScore v1.0 | `bionic_engine.py` L297-312 | Modèle loup (pressure 30%, corridor 25%, food 15%, geoform 10%, wetness 10%) | Loup | Backend analyse |
| L-T | TurkeyScore v1.0 | `bionic_engine.py` L313-328 | Modèle dindon (food 35%, canopy 20%, corridor 10%, geoform 10%, thermal 10%) | Dindon | Backend analyse |
| L-AI | AI Predictions | `bionic_engine.py` L654-757 | Prévisions 24h/72h/7j (weather-adjusted, movement prediction) | Toutes | Backend API |
| L-HY | Hybrid AI Adjust | `bionic_engine.py` L1496-1675 | Ajustement IA GPT-4o (fallback rule-based) | Toutes | Backend API |

**Statut:** GELÉ (date gel: 2026-03-10). Remplacé par `bionic_engine_p0/`.

### 1.2 — ENGINES V2 (12 moteurs)

| # | Engine ID | Nom | Fichier | Poids | Rôle | Espèces |
|---|-----------|-----|---------|-------|------|---------|
| V2-1 | `behavior` | Behavior Engine | `engines_v2.py` L44-82 | 1.2 | Courbes d'activité horaires/saisonnières, détection rut | Orignal (default) |
| V2-2 | `keyzone_v2` | KeyZone Engine V2 | `engines_v2.py` L89-121 | 1.5 | Densité et diversité des zones clés (habitats, rut, repos, alim.) | Toutes |
| V2-3 | `food_deficit` | Food Deficit Engine | `engines_v2.py` L128-158 | 1.1 | Déficit alimentaire (NDVI saisonnier, zones alimentation) | Toutes |
| V2-4 | `wind_intelligence` | Wind Intelligence Engine | `engines_v2.py` L166-205 | 0.8 | Direction vent optimale approche, score vent | Toutes |
| V2-5 | `terrain` | Terrain Engine | `engines_v2.py` L212-238 | 0.9 | Pentes, forêts, hydrologie — diversité terrain | Toutes |
| V2-6 | `human_pressure` | Human Pressure Engine | `engines_v2.py` L245-277 | 1.0 | Pression anthropique (routes, structures, couvert forestier) | Toutes |
| V2-7 | `corridor_continuity` | Corridor Continuity Engine | `engines_v2.py` L284-318 | 1.0 | Santé réseau corridors (continuité, bandes, densification) | Toutes |
| V2-8 | `global_attractiveness` | Global Attractiveness Engine | `engines_v2.py` L325-354 | 1.3 | Score attractivité global (moyenne pondérée tous engines) | Toutes |
| V2-9 | `action_plan` | Action Plan Engine | `engines_v2.py` L361-392 | 0.5 | Plan d'action chasse (informatif, pas scoring) | Toutes |
| V2-10 | `predictive_ai` | Predictive AI Engine | `engines_v2.py` L399-443 | 1.1 | Prédiction probabiliste (behavior 30%, keyzone 25%, food 20%, pressure 25%) | Toutes |
| V2-11 | `bce_compliance` | BCE-4X Compliance Engine | `engines_v2.py` L450-482 | 0.3 | Validation conformité couleurs + géométrie | Méta |
| V2-12 | `rendering` | Rendering Engine | `engines_v2.py` L489-526 | 0.2 | Performance rendu carte (complexité features) | Méta |

### 1.3 — ENGINES V3 (12 nouveaux moteurs)

| # | Engine ID | Nom | Fichier | Poids | Cat. | Rôle |
|---|-----------|-----|---------|-------|------|------|
| V3-1 | `ecological_hierarchy` | EcologicalHierarchy Engine | `engines_v3.py` L44-74 | 1.1 | ecology | Hiérarchie strates végétales (canopée, sous-bois, sol, aquatique) |
| V3-2 | `interaction` | Interaction Engine | `engines_v3.py` L77-101 | 1.0 | ecology | Effet lisière, paires complémentaires (alim+repos, habitats+hydro) |
| V3-3 | `geopedology` | GeoPedology Engine | `engines_v3.py` L104-128 | 0.8 | terrain | Pédologie (drainage, profondeur sol, matière organique) |
| V3-4 | `connectivity` | Connectivity Engine | `engines_v3.py` L131-155 | 1.2 | landscape | Connectivité fonctionnelle (corridors, zones, couverture) |
| V3-5 | `temporal_dynamics` | TemporalDynamics Engine | `engines_v3.py` L158-184 | 1.0 | temporal | Variations saisonnières + circadiennes (crépusculaire) |
| V3-6 | `hotspot` | Hotspot Engine | `engines_v3.py` L187-220 | 1.3 | strategic | Détection hotspots (zones stratégiques × corridors × engines) |
| V3-7 | `forest_structure_v2` | ForestStructure Engine v2 | `engines_v3.py` L223-246 | 1.0 | ecology | Structure forestière (densité canopée, diversité âge, composition) |
| V3-8 | `food_score_v2` | FoodScore v2 | `engines_v3.py` L249-280 | 1.2 | ecology | Scoring alimentaire avancé (qualité×saison, disponibilité, accessibilité) |
| V3-9 | `wetness_v2` | WetnessScore v2 | `engines_v3.py` L283-306 | 0.9 | hydrology | Humidité avancée (proximité eau, précipitations, drainage) |
| V3-10 | `geoform_v2` | GeoFormScore v2 | `engines_v3.py` L309-331 | 0.8 | terrain | Géomorphologie avancée (diversité pentes, aspect, élévation) |
| V3-11 | `behavior_v2` | Behavior Engine v2 | `engines_v3.py` L334-376 | 1.2 | behavioral | Modèle circadien 24h par espèce (repos/alim/déplacement) |
| V3-12 | `attractiveness_v2` | GlobalAttractiveness Engine v2 | `engines_v3.py` L379-410 | 1.5 | synthesis | Score global v2 (intègre TOUS les engines V2+V3) |

### 1.4 — ENGINES IA (3 moteurs)

| # | Engine ID | Nom | Fichier | Poids | Rôle |
|---|-----------|-----|---------|-------|------|
| IA-1 | `predictive_models` | Predictive Models Engine | `engines_v3.py` L480-511 | 1.0 | Prédictions 24h/72h/7j avec décroissance confiance |
| IA-2 | `dynamic_scoring` | Dynamic Scoring Engine | `engines_v3.py` L514-541 | 1.0 | Ajustements temps réel (vent, température, heure) |
| IA-3 | `temporal_analysis` | Temporal Analysis Engine | `engines_v3.py` L544-573 | 0.9 | Trends, patterns, forecast horaire |

### 1.5 — MODÈLES FAUNIQUES V3 (3 espèces)

| Espèce | Fichier | Pondérations clés (top 5) |
|--------|---------|---------------------------|
| **Orignal** | `engines_v3.py` L421-439 | behavior_v2: 1.4, food_score_v2: 1.3, wetness_v2: 1.2, connectivity: 1.2, ecological_hierarchy: 1.1 |
| **Cerf** | `engines_v3.py` L428-438 | behavior_v2: 1.3, forest_structure_v2: 1.3, food_score_v2: 1.2, interaction: 1.2, geoform_v2: 1.1 |
| **Ours** | `engines_v3.py` L432-438 | food_score_v2: 1.5, behavior_v2: 1.2, forest_structure_v2: 1.2, temporal_dynamics: 1.1, ecological_hierarchy: 1.1 |

### 1.6 — 9 MOTEURS CORRIDOR V9 (sous-engines)

| # | Engine ID | Nom | Fichier | Poids | Rôle |
|---|-----------|-----|---------|-------|------|
| C9-1 | `nutrition` | Nutrition Engine | `nutrition_engine.py` | 0.12 | NDVI + fourrage saisonnier + minéraux + besoins espèce |
| C9-2 | `daily_routine` | Daily Routine Engine | `daily_routine_engine.py` | 0.10 | Rythmes circadiens, lever/coucher soleil Québec |
| C9-3 | `weather` | Weather Engine V9 | `weather_engine_v9.py` | 0.10 | OWM live + cache 60min BCE-4X + fallback algorithmique |
| C9-4 | `disturbance` | Disturbance Engine | `disturbance_engine.py` | 0.12 | Pression humaine 5 facteurs (score INVERSÉ) |
| C9-5 | `movement` | Movement Engine V9 | `movement_engine_v9.py` | 0.15 | DEM algorithmique + A* + énergie + relief Québec |
| C9-6 | `phenology` | Phenology Engine | `phenology_engine.py` | 0.08 | Cycles végétatifs 12 mois, NDVI, couvert |
| C9-7 | `typology` | Typology Engine | `typology_engine.py` | 0.08 | 5 profils comportementaux × saison × espèce |
| C9-8 | `learning` | Learning Engine | `learning_engine.py` | 0.05 | Calibration observations terrain (caméras, pistes, waypoints) |
| C9-9 | `habitat_enhancement` | Habitat Enhancement Engine | `habitat_enhancement_engine.py` | 0.05 | Sol, minéraux, recommandations amélioration habitat |

**Total poids V9:** 0.12 + 0.10 + 0.10 + 0.12 + 0.15 + 0.08 + 0.08 + 0.05 + 0.05 = **0.85** (normalisé à 1.0 dans le composite)

### 1.7 — HOTSPOT ENGINE

| Module | Fichier | Rôle |
|--------|---------|------|
| Hotspot Extraction | `hotspots/hotspot_engine.py` | Grille 50m × extraction → scoring → DBSCAN → polygone |
| Territory Data | `hotspots/territory_data_provider.py` | Enrichissement territorial (ville, code postal, gestionnaire) |
| Scheduler | `hotspots/hotspot_scheduler.py` | Exécution automatique annuelle (APScheduler) |

### 1.8 — MODULES SUPPORT

| Module | Fichier | Rôle |
|--------|---------|------|
| Geospatial Data Service | `geospatial_data.py` | Open-Meteo + Open-Elevation + NASA MODIS |
| Pipeline V7 | `services/pipeline_v7.py` | Orchestrateur pipeline zones → corridors → scoring |
| Corridor Service | `services/corridor_service.py` | Génération corridors A* |
| Corridor 10x | `services/corridor_10x.py` | Pathfinding optimisé |
| Exclusion Engine V7 | `services/exclusion_engine_v7.py` | Zones d'exclusion (eau, urbain) |
| BCE-4X | `bce/` | Quality gate validation (couleurs, géométrie, corridors) |
| Wildlife Behavior Engine | `modules/wildlife_behavior_engine/` | Comportement faune (module séparé) |
| Predictive Engine | `modules/predictive_engine/` | Moteur prédictif (module séparé) |

---

## 2. SCHÉMA DE DÉPENDANCES

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENTRÉE UTILISATEUR                            │
│  (lat, lng, rayon, espèce, saison, heure, waypoints)           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              DONNÉES EXTERNES (COUCHE A)                         │
│  ┌──────────────┐  ┌────────────────┐  ┌─────────────────────┐ │
│  │ Open-Meteo   │  │ Open-Elevation │  │ NASA MODIS/Seasonal │ │
│  │ Météo temps  │  │ Terrain DEM    │  │ NDVI, NDWI, LAI     │ │
│  │ réel + prévu │  │ Pente, Aspect  │  │ Végétation indices   │ │
│  └──────┬───────┘  └───────┬────────┘  └──────────┬──────────┘ │
│         │                  │                       │            │
│  ┌──────┴──────────────────┴───────────────────────┴──────────┐ │
│  │     OpenWeatherMap (OWM) — Cache 60min BCE-4X              │ │
│  │     Température, vent, précipitations, pression, visibilité│ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           PHASE 1: ENGINES INDÉPENDANTS (COUCHE B)              │
│                                                                  │
│  V2 Indépendants:                V3 Indépendants:               │
│  ┌─────────────────┐             ┌─────────────────────────┐    │
│  │ behavior (1.2)  │             │ ecological_hierarchy    │    │
│  │ keyzone_v2(1.5) │             │ interaction             │    │
│  │ food_deficit    │             │ geopedology             │    │
│  │ wind_intel(0.8) │             │ connectivity (1.2)      │    │
│  │ terrain (0.9)   │             │ temporal_dynamics        │    │
│  │ human_pressure  │             │ forest_structure_v2      │    │
│  │ corridor_cont.  │             │ food_score_v2 (1.2)     │    │
│  │ bce_compliance  │             │ wetness_v2 (0.9)        │    │
│  │ rendering(0.2)  │             │ geoform_v2 (0.8)        │    │
│  └────────┬────────┘             │ behavior_v2 (1.2)       │    │
│           │                      └────────────┬────────────┘    │
│           └────────────┬──────────────────────┘                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           PHASE 2: ENGINES DÉPENDANTS (COUCHE C)                │
│                                                                  │
│  V2 Dépendants:                  V3 Dépendants:                 │
│  ┌──────────────────────┐        ┌─────────────────────────┐    │
│  │ global_attractiveness │        │ hotspot (1.3)           │    │
│  │ action_plan (0.5)     │        │ attractiveness_v2 (1.5) │    │
│  │ predictive_ai (1.1)   │        └─────────────────────────┘    │
│  └──────────────────────┘                                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           PHASE 3: ENGINES IA (COUCHE D)                        │
│  ┌────────────────────┐ ┌─────────────────┐ ┌────────────────┐ │
│  │ predictive_models   │ │ dynamic_scoring │ │ temporal_anal. │ │
│  │ 24h/72h/7j         │ │ temps réel      │ │ trends/patterns│ │
│  └────────────────────┘ └─────────────────┘ └────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           PHASE 4: MODÈLES FAUNIQUES (COUCHE E)                 │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────┐         │
│  │ Orignal  │    │ Cerf Virginie│    │ Ours noir     │         │
│  │ 14 poids │    │ 14 poids     │    │ 14 poids      │         │
│  └──────────┘    └──────────────┘    └───────────────┘         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│       PHASE 5: SCORE FINAL INTÉGRÉ                              │
│  Moyenne pondérée de TOUS les engines (V2+V3+IA) = final_score │
└────────────────────────┬────────────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
┌──────────────────────┐  ┌─────────────────────────────────┐
│ CORRIDOR V9 PIPELINE │  │ HOTSPOT PIPELINE                │
│ 9 sub-engines        │  │ Grille 50m → Score → DBSCAN     │
│ Classification 5 niv │  │ → Polygone → BCE-4X             │
│ Bandes concentriques │  │ → Enrichissement territorial    │
│ Clipping 2km²        │  └─────────────────────────────────┘
│ Continuité réseau    │
└──────────────────────┘
```

---

## 3. THÈME: ZONES D'ALIMENTATION

### [A] Couches utilisées

| Couche | Source | Résolution | Millésime |
|--------|--------|-----------|-----------|
| NDVI | NASA MODIS/Seasonal (via `geospatial_data.py`) OU estimation saisonnière | ~250m | Temps réel ou estimation |
| Zones alimentation | OSM Overpass (`osm_extractor.py`) | Variable | Temps réel |
| Hydrographie | OSM/Gouvernement QC | Variable | Variable |
| Peuplements forestiers | WMS écoforestier QC (proxy) | 1:20000 | Variable |

### [B] Variables dérivées

| Variable | Formule/Source | Unité |
|----------|----------------|-------|
| `NDVI estimé` | ZONE_NDVI_BASE[type_zone] × SEASON_NDVI_MULT[saison] | 0-1 |
| `Qualité fourrage` | FORAGE_QUALITY[type_zone][saison] | 0-100 |
| `Disponibilité alimentaire` | base_ndvi × 100 + feeding_zones × 15 | 0-100 |
| `Déficit alimentaire` | max(0, 70 - food_availability) | 0-70 |
| `Score brout (browse)` | SPECIES_NUTRITION[espèce].browse_preference × 100 | 0-100 |
| `Bonus saline` | 15 × SPECIES_NUTRITION[espèce].salt_attraction (si zone saline) | 0-15 |
| `Bonus urgence calorique` | 10 × caloric_need (hiver) ou 5 × caloric_need (automne) | 0-10 |
| `Qualité saisonnière` | {printemps: 0.7, été: 0.9, automne: 1.0, hiver: 0.3} | 0-1 |

### [C] Règles de scoring

**FoodScore v2 (V3-8):**
```
qualite = disponibilité × qualité_saisonnière
base = qualite × 0.4 + disponibilité × 0.3 + accessibilité × 0.3
score = base + bonus_diversité (min 20, len(food_prefs) × 5)
```

**Food Deficit Engine (V2-3):**
```
food_availability = base_ndvi × 100 + feeding_zones × 15
deficit = max(0, 70 - food_availability)
score = 50 + deficit × 0.7 + (10 si feeding_zones == 0)
```

**Nutrition Engine (C9-1):**
```
nutrition_score = avg_forage × 0.40 + ndvi_score × 0.25 + browse × 0.20 + caloric × 0.15
score = nutrition_score + salt_bonus + urgency_bonus (min 100, max 5)
```

**Préférences alimentaires par espèce:**
| Espèce | Aquatique | Brout | Écorce | Herbes | Baies | Insectes | Poisson |
|--------|-----------|-------|--------|--------|-------|----------|---------|
| Orignal | 30% | 40% | 20% | 10% | — | — | — |
| Cerf | — | 35% | — | 30% | — | — | — |
| Ours | — | — | — | 25% | 30% | 20% | 25% |

### [D] Règles saisonnières

| Saison | NDVI mult. | Qualité fourrage | Urgence calorique |
|--------|-----------|-----------------|-------------------|
| Printemps | 0.60 | 0.7 | 0 |
| Été | 1.00 | 0.9 | 0 |
| Automne | 0.65 | 1.0 | 5 × caloric_need (pré-rut) |
| Hiver | 0.15 | 0.3 | 10 × caloric_need |

### [E] Post-traitement
- Aucun lissage spatial sur les scores alimentaires
- Agrégation par moyenne pondérée dans le pipeline V3
- Filtrage indirect: seuls les hotspots avec score >= 60 (FORT) sont conservés

---

## 4. THÈME: ZONES DE REPOS

### [A] Couches utilisées

| Couche | Source | Résolution |
|--------|--------|-----------|
| Zones repos | OSM + classification interne | Variable |
| Habitats | OSM + classification interne | Variable |
| Peuplements | WMS écoforestier QC | 1:20000 |
| Altitude | DEM algorithmique Québec | ~1km |

### [B] Variables dérivées

| Variable | Formule/Source |
|----------|----------------|
| `rest_pct` | BehaviorV2: moose=0.6, deer=0.5, bear=0.4 |
| `repos zone affinity` (day) | 90/100 (période jour = repos maximal) |
| `repos zone affinity` (night) | 80/100 |
| `cover_value` | PhenologyEngine: 0.20 (hiver) → 0.95 (juillet) |
| `forest_structure score` | canopy_density × 0.4 + age_diversity × 0.3 + composition × 0.3 |

### [C] Règles de scoring

**Repos = Composante du BehaviorV2 Engine (V3-11):**
```
circadian = CIRCADIAN_CURVE[espèce][heure]  (0-100 par heure)
Orignal: pics repos = 0h-4h (10-15%), 10h-14h (15-25%)
Cerf: pics repos = 0h-4h (5-10%), 10h-14h (10-20%)
Ours: repos nocturne fort (5-10%), jour actif (55-90%)
```

**Interaction Engine (V3-2):**
```
Paire complémentaire (alimentation, repos) = +18 pts edge effect
```

### [D] Règles saisonnières
- Hiver: repos forcé (moose: activité réduite 40-50%, deer: ravage hivernal, bear: hibernation)
- Automne (rut): repos réduit, exploration accrue

### [E] Post-traitement
- Classification en 5 profils comportementaux (typology_engine.py):
  - Conservateur: cover_need = 0.8, exploration_range = 500m
  - Territorial: cover_need = 0.7, exploration_range = 800m

---

## 5. THÈME: CORRIDORS / DÉPLACEMENTS

### [A] Couches utilisées

| Couche | Source | Résolution |
|--------|--------|-----------|
| Corridors A* | `corridor_10x.py` / `corridor_service.py` | Points GPS |
| DEM | Algorithmique Québec (`movement_engine_v9.py`) | ~1km estimé |
| OSM routes/sentiers | Overpass API | Variable |
| Zones sources/destinations | Toutes zones détectées | Variable |

### [B] Variables dérivées

| Variable | Formule |
|----------|---------|
| `altitude_m` | estimate_altitude_m(lat, lng) — modèle Laurentides, Appalaches, St-Laurent, Abitibi, Saguenay |
| `pente_deg` | atan(abs(alt2 - alt1) / distance_m) |
| `cout_energetique` | < 3°: 1.0, 3-8°: 1.3, 8-15°: 1.8, 15-25°: 2.5, >25°: 4.0 |
| `terrain_feature` | coulée (5-15°, +15), crête (10-25°, -10), plateau (0-3°, +5), falaise (25+°, -30) |
| `distance_fitness` | Optimal: orignal 200-2000m (idéal 800m), cerf 100-1500m (idéal 500m), ours 300-3000m (idéal 1200m) |
| `connectivity_ratio` | corridors_connectés / total_corridors |

### [C] Règles de scoring

**Corridor V9 — Pipeline complet:**
```
1. Génération A* (corridor_10x)
2. Évaluation par 9 moteurs BIONIC (nutrition, daily_routine, weather, disturbance, 
   movement, phenology, typology, learning, habitat_enhancement)
3. Score composite = somme_pondérée(score_i × poids_i) / somme(poids_i)
4. Classification 5 niveaux:
   - gris (0-30): Potentiel — bande externe, dash 8,4
   - jaune (31-50): Opportuniste — bande 2.0px
   - orange (51-70): Fonctionnel — bande 2.8px
   - rouge (71-85): Primaire — bande 3.5px
   - rouge_rayé (86-100): Critique — bande 4.5px, dash 12,3,3,3
5. Lissage Chaikin (2 itérations)
6. Bandes concentriques (5 niveaux) — buffer proportionnel à la longueur
7. Clipping strict 2km² (Shapely)
8. Validation continuité (max gap 150m)
```

**Bandes polygonales (buffer en mètres):**
| Niveau | Ratio | Min | Max |
|--------|-------|-----|-----|
| gris | 0.012 | 6m | 26m |
| jaune | 0.008 | 5m | 17m |
| orange | 0.005 | 2m | 11m |
| rouge | 0.004 | 1m | 6m |
| rouge_rayé | 0.001 | 1m | 4m |

**Continuité réseau (graph-based post-processing):**
```
- Seuil connexion: proximity_threshold = 150m
- Distance max connexion: 800m
- Algorithme: identification dead-ends → connexion au noeud valide le plus proche
- Segments de connexion: score = 35, type = gris
```

### [D] Règles saisonnières

**Activity par espèce × saison (corridor_relevance):**
| Espèce | Printemps | Été | Automne | Hiver |
|--------|-----------|-----|---------|-------|
| Orignal | 1.0 | 0.9 | 1.3 (rut) | 0.7 |
| Cerf | 1.0 | 0.9 | 1.2 (rut) | 0.6 |
| Ours | 1.4 (post-hibernation) | 1.1 | 1.3 (hyperphagie) | 0.0 (hibernation) |

### [E] Post-traitement
- Densification: aucun segment > 30m
- Lissage Chaikin (2 itérations) sur centerline CLIPPÉE
- Clipping Shapely strict au périmètre 2km²
- Re-clipping de chaque bande polygonale
- BCE-4X-GEOM-004: Aucun pixel hors du carré 2km

---

## 6. THÈME: SÉCURITÉ / COUVERT

### [A] Couches utilisées

| Couche | Source |
|--------|--------|
| Couvert forestier | NDVI estimé + WMS écoforestier |
| Perturbation humaine | Algorithmique (lat/lng/heure) |
| Routes | OSM (distance estimée) |
| Zones exclusion | `exclusion_engine_v7.py` |

### [B] Variables dérivées

| Variable | Formule |
|----------|---------|
| `cover_value` | Phénologie: 0.20 (jan) → 0.95 (juil) → 0.65 (déc) |
| `zone_disturbance` | Base par type: alimentation=10, repos=5, trajets=25 |
| `road_factor` | min(40, distance_m / 100) × sp.road_sensitivity |
| `latitude_pressure` | max(0, (47.5 - lat) × 15) × sp.human_sensitivity |
| `flight_distance_m` | Orignal: 300m, Cerf: 150m, Ours: 200m |
| `hunting_pressure` | Printemps: 0.3, Été: 0.1, Automne: 1.0, Hiver: 0.4 |

### [C] Règles de scoring

**Disturbance Engine (C9-4) — Score INVERSÉ:**
```
total_pressure = zone_pressure × 0.30 + road_factor × 0.25 + latitude_pressure × 0.15 
               + longitude_pressure × 0.05 + noise_factor × 0.15 + hunting × 0.10
total_pressure × time_factor (jour: 1.5, transition: 1.2, nuit: 0.5)
score = 100 - total_pressure (haute pression = bas score corridor)
```

**Human Pressure Engine (V2-6):**
```
base_pressure = hash(lat, lng) % 40 + 10 (10-50 déterministe)
forest_reduction = min(20, forest_count × 5)
pressure = max(5, base_pressure - forest_reduction)
score = 100 - pressure
```

**CanopyScore v1.0 (Legacy):**
```
Pondérations: canopy_height 0.20, canopy_closure 0.25, understory_density 0.20, 
              species_diversity 0.20, age_class 0.15
```

### [D] Règles saisonnières
- Automne (chasse): pression × 1.0 (pic)
- Hiver: couvert conifère crucial pour cerf (ravage)
- Phénologie couvert: minimum jan-fév (0.15-0.20), maximum juil (0.95)

### [E] Post-traitement
- Score inversé pour intégration dans pipeline (haute sécurité = haut score)

---

## 7. THÈME: THERMIQUE / REFUGE

### [A] Couches utilisées

| Couche | Source |
|--------|--------|
| Température | OpenWeatherMap (OWM) live OU fallback algorithmique |
| Humidité | OWM live |
| Vent | OWM live (vitesse + direction) |
| Pression barométrique | OWM live |
| Couvert nuageux | OWM live |
| Visibilité | OWM live |

### [B] Variables dérivées

| Variable | Formule |
|----------|---------|
| `temp_score` | Zone optimale espèce → 80, sinon pénalité progressive |
| `wind_category` | calm (<5), light (5-15), moderate (15-30), strong (30-50), storm (>50) km/h |
| `wind_mod` | calm: +10, light: +5, moderate: -5, strong: -20, storm: -40 |
| `precip_mod` | rain_light: -3, rain_moderate: -8, rain_heavy: -15, snow_light: -5, snow_moderate: -12, snow_heavy: -25 |
| `pressure_mod` | <1000 hPa: -10 (tempête), 1000-1008: -5, 1020-1025: +5, >1025: +8 |
| `humidity_mod` | >85% + T>15°C: -8, >90%: -5 |
| `visibility_mod` | <500m: -10, <1000m: -5 |
| `cloud_mod` | >80% + T<0°C: +3 (isolation), <20% + T>20°C: -5 (stress soleil) |

### [C] Règles de scoring

**Weather Engine V9 (C9-3):**
```
score = temp_score + wind_mod + precip_mod + pressure_mod + humidity_mod + visibility_mod + cloud_mod
Borné [5, 100]
```

**Confort thermique par espèce:**
| Espèce | Optimal min | Optimal max | Stress chaleur | Stress froid |
|--------|-------------|-------------|----------------|-------------|
| Orignal | -10°C | 15°C | 25°C | -35°C |
| Cerf | -5°C | 20°C | 30°C | -25°C |
| Ours | 5°C | 25°C | 35°C | -10°C |

**ThermalScore v1.0 (Legacy):**
```
Pondérations: temperature 0.30, aspect 0.20, elevation 0.20, canopy_cover 0.20, water_proximity 0.10
```

**Fallback algorithmique (sans OWM):**
```
T_base = seasonal_temp[mois] (jan:-15 → juil:22 → déc:-10)
± variation diurne (jour: +3, nuit: -4)
- altitude_effect (lat > 46.0)
```

### [D] Règles saisonnières
- Cache OWM: 60 minutes (règle BCE-4X non-négociable)
- Phases lunaires: nouvelle_lune: -10 activité nocturne, pleine_lune: +15

### [E] Post-traitement
- Certitude: 0.90 (OWM live), 0.60 (fallback algorithmique), 0.50 (inconnu)
- Cache global partagé entre tous les corridors d'une même analyse

---

## 8. THÈME: HOTSPOTS

### [A] Couches utilisées

| Couche | Source | Résolution |
|--------|--------|-----------|
| Grille d'analyse | Générée algorithmiquement | 50m × 50m (adaptatif) |
| 9 scores engines | Calculés par cellule de grille | Par cellule |
| 12 régions Québec | Prédéfinies (centres + rayons) | Régional |
| Données territoriales | `territory_data_provider.py` (MOCKÉ) | Par hotspot |

### [B] Variables dérivées

| Variable | Formule |
|----------|---------|
| `engine_scores` | Hash-based deterministic per cell + season_mod + hour_mod + concentration_bonus |
| `concentration_bonus` | ~8% des cellules: ×1.35, ~12% supplémentaires: ×1.15 |
| `hotspot_score` | Somme pondérée des 9 engines |
| `dominant_species` | orignal: forest×0.4 + wetness×0.35 + food×0.25 (+ seed) |
| `category` | Max de {alimentation, corridors, déplacement, repos, rut, pression_faible} |
| `accessibility` | corridors_v9 × 0.4 + geoform × 0.6 |

### [C] Règles de scoring

**Pondérations hotspot officielles:**
| Engine | Poids |
|--------|-------|
| corridors_v9 | 20% |
| food_score_v2 | 15% |
| forest_structure_v2 | 15% |
| wetness_score_v2 | 10% |
| geoform_score_v2 | 10% |
| temporal_dynamics | 10% |
| behavior_v2 | 10% |
| disturbance | 5% |
| global_attractiveness_v2 | 5% |

**Classification:**
| Catégorie | Seuil |
|-----------|-------|
| MAJEUR | >= 80 |
| FORT | >= 60 |
| MODÉRÉ | >= 40 |
| FAIBLE | < 40 |

**Filtres d'extraction:**
- Score minimum: FORT (>= 60)
- Corridor à proximité: obligatoire (score corridors >= 50)
- Accessibilité minimum: 40
- Maximum 25 hotspots par région

### [D] Clustering DBSCAN
```
eps_m = effective_spacing × 2.5
min_samples = 5
Conversion polygon: convex hull trié par angle
```

### [E] Post-traitement
- Enrichissement territorial: ville, code_postal, altitude, type_territoire (7 types), 
  acces_status (4 statuts), gestionnaire, lot_info
- Validation BCE-4X: GEOM-001 (polygone >=3 sommets), GEOM-002 (score 0-100), 
  CLIP-001 (corridor 150m), VISUAL-001 (classification valide)
- Export GeoJSON + JSON
- Tri par score décroissant

---

## 9. THÈME: PRÉDICTION / COMPORTEMENT

### [A] Couches utilisées

| Couche | Source |
|--------|--------|
| Courbes circadiennes | Tables hardcodées par espèce (24h) |
| Profils comportementaux | 5 types × 3 espèces × 4 saisons |
| Observations terrain | Caméras, pistes, scat, waypoints |
| Scores engines | Agrégation de tous les engines V2+V3 |

### [B] Variables dérivées

| Variable | Formule |
|----------|---------|
| `activity_curve` | CIRCADIAN[espèce][heure] (0-100 par heure) |
| `seasonal_modifier` | SEASON_ACTIVITY_MOD[espèce][saison] |
| `prediction_24h` | avg_engines × 0.4 + behavior × 0.3 + temporal × 0.3 |
| `prediction_72h` | avg_engines × 0.5 + food × 0.25 + behavior × 0.25 |
| `prediction_7j` | avg_engines × 0.6 + food × 0.2 + temporal × 0.2 |
| `confidence_decay` | 24h: 85%, 72h: 70%, 7j: 55% |

### [C] Règles de scoring

**Predictive Models Engine (IA-1):**
```
base_24h = avg_scores × 0.4 + behavior_v2 × 0.3 + temporal_dynamics × 0.3
decay = {24h: 1.0, 72h: 0.85, 7d: 0.7}
probability = base × decay
```

**Dynamic Scoring Engine (IA-2):**
```
Ajustements temps réel:
- Vent > 20 km/h: -5, > 10 km/h: -2
- Temp < -10°C: -5, < 0°C: -3, > 25°C: -5
- Heure 5-6h/17-18h: +10, 4h/7h/16h/19h: +5
```

**Profils comportementaux (Typology Engine C9-7):**
| Profil | Tolérance risque | Range (m) | Couvert préféré | Nuit |
|--------|-----------------|-----------|-----------------|------|
| Conservateur | 0.2 | 500 | 0.8 | 0.3 |
| Explorateur | 0.7 | 2000 | 0.4 | 0.5 |
| Nocturne | 0.5 | 1200 | 0.6 | 0.9 |
| Opportuniste | 0.6 | 1500 | 0.5 | 0.6 |
| Territorial | 0.3 | 800 | 0.7 | 0.4 |

**Profil dominant par espèce × saison:**
| Espèce | Défaut | Automne | Printemps | Hiver |
|--------|--------|---------|-----------|-------|
| Orignal | Territorial | Explorateur (rut) | Territorial (vêlage) | — |
| Cerf | Conservateur | Explorateur (rut) | — | Conservateur (ravage) |
| Ours | Explorateur | Opportuniste (hyperphagie) | Explorateur (post-hibernation) | Conservateur (pré-hibernation) |

### [D] Calibration par apprentissage (Learning Engine C9-8)

| Type observation | Confiance | Décroissance temporelle |
|-----------------|-----------|------------------------|
| camera_trap | 0.20 | 30 jours |
| visual_sighting | 0.15 | 3 jours |
| vocal | 0.12 | — |
| tracks | 0.10 | 7 jours |
| scat | 0.08 | 14 jours |
| rub_scrape | 0.07 | — |
| browse_sign | 0.06 | 21 jours |
| bedding_site | 0.05 | — |
| waypoint | 0.04 | 60 jours |

Score sans données: 50 (confiance 20%). Avec données: 50 + min(35, obs×5 + wp×3).

### [E] Post-traitement
- Prédictions bornées: 24h max 99%, 72h max 95%, 7j max 90%
- Confiance: OWM live = 0.90, fallback = 0.60

---

## 10. PIPELINE GLOBAL: DU BRUT AU SCORE À LA CARTE

```
ENTRÉE                                          SORTIE
┌───────┐                                       ┌────────────┐
│ GPS   │──→ Open-Meteo ──→ Météo              │ Score 0-100│
│ Espèce│──→ Open-Elevation ──→ DEM            │ Zones GeoJSON│
│ Saison│──→ NASA MODIS ──→ NDVI               │ Corridors V9│
│ Heure │──→ OSM Overpass ──→ POI              │ Hotspots    │
└───────┘                                       │ Prédictions │
     │                                          │ Carte Leaflet│
     ▼                                          └────────────┘
┌──────────────────────────────────────────────────┐
│ 1. Fetch données géospatiales (cache 5min)       │
│ 2. Génération zones (12 types)                    │
│ 3. Génération corridors A* (entre zones)          │
│ 4. Évaluation V9 (9 moteurs × N corridors)        │
│ 5. Classification 5 niveaux (gris→rouge_rayé)     │
│ 6. Bandes concentriques (Shapely buffer)          │
│ 7. Clipping 2km² (Shapely intersection)           │
│ 8. Continuité réseau (graph-based)                │
│ 9. Engines V2 (12) + V3 (12) + IA (3)            │
│ 10. Modèles fauniques (3 espèces)                 │
│ 11. Score final intégré                            │
│ 12. BCE-4X validation                              │
│ 13. Rendu frontend (Leaflet + React)               │
└──────────────────────────────────────────────────┘
```

---

## 11. LIMITES CONNUES

### 11.1 Données

| Limite | Impact | Statut |
|--------|--------|--------|
| **NDVI estimé** (pas satellite réel) | Les valeurs NDVI sont des estimations saisonnières basées sur des tables, pas des données satellite en temps réel. Précision ~60-70%. | Connu, approuvé |
| **DEM algorithmique** (pas SRTM/LiDAR) | L'altitude est estimée par un modèle multi-régional Québec, pas par données SRTM ou LiDAR réelles. Précision ~100-200m. | Connu |
| **Pression humaine algorithmique** | Pas de données OSM réelles de densité routière/bâtiments. Estimation par hash(lat,lng) + latitude. | Connu |
| **Données territoriales MOCKÉES** | Les villes, codes postaux, gestionnaires sont générés aléatoirement de manière réaliste, pas connectés aux registres publics. | Approuvé par utilisateur |
| **Pas de données de récolte** | Aucune intégration des statistiques de récolte MFFP. | Absent |

### 11.2 Modèles

| Limite | Impact |
|--------|--------|
| **Scores hash-based** pour hotspots | Les scores par cellule de grille utilisent des valeurs pseudo-aléatoires déterministes (hash lat/lng), pas de vrais calculs écologiques. |
| **Pas de vrai machine learning** | Le "Learning Engine" collecte des observations mais ne fait pas d'entraînement ML réel. Score = 50 + bonus linéaire. |
| **Profils comportementaux statiques** | Les 5 profils (conservateur, explorateur, etc.) sont des tables fixes, pas calibrés sur des données GPS/telemetry. |
| **Confort thermique simplifié** | Zones optimales rectangulaires (min/max), pas de courbes gaussiennes ni d'acclimatation. |
| **Aucun modèle de prédation** | Les interactions prédateur-proie (loup-cerf, ours-orignal) ne sont pas modélisées. |

### 11.3 Hypothèses

| Hypothèse | Justification |
|-----------|---------------|
| Conversion 1° ≈ 111km | Approximation latitude Québec (~46.8°N). Acceptable pour la résolution utilisée. |
| Cache météo 60 min | Règle BCE-4X. Assume que la météo est stable sur 60 minutes. |
| Grille 50m effective → adaptative | Pour les grandes régions, la grille effective est ajustée (max 50 cellules par axe). |
| Profil "nocturne" forcé la nuit | Si le profil dominant a night_activity < 0.5, override vers "nocturne" entre 22h et 5h. |

---

## CONTRAINTE NON NÉGOCIABLE

> Toute suggestion d'amélioration ou de modification est marquée comme **PROPOSITION** 
> et n'est **PAS appliquée** sans commande explicite de Steeve.

---

### PROPOSITIONS (SÉPARÉES DU RAPPORT — NON APPLIQUÉES)

1. **P-ALIM-01:** Remplacer NDVI estimé par intégration Sentinel-2 réel (résolution 10m)
2. **P-TERR-01:** Intégrer SRTM/ALOS 30m au lieu du DEM algorithmique
3. **P-PRESS-01:** Utiliser densité routière OSM réelle au lieu de hash(lat,lng)
4. **P-ML-01:** Implémenter un vrai modèle ML dans Learning Engine (gradient boosting sur observations)
5. **P-PRED-01:** Ajouter modèle prédateur-proie (impact loup sur comportement cerf/orignal)
6. **P-THERM-01:** Remplacer zones optimales rectangulaires par courbes gaussiennes de confort
7. **P-HOT-01:** Remplacer scoring hash-based par scoring écologique réel par cellule

---

*Fin du rapport d'audit. Aucune modification effectuée. Photo fidèle de l'état actuel.*
