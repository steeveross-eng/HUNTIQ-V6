# INVENTAIRE PREDICTIF TOTAL - HUNTIQ BIONIC V5
## PHASE G - BIONIC ULTIMATE INTEGRATION
### Document préparé pour COPILOT MAITRE (STEEVE)
### Version: 1.3.0-beta2 | Date: Decembre 2025 | Revision: Integration 12 Facteurs Comportementaux

---

# PREAMBULE

Ce document constitue l'**INVENTAIRE PREDICTIF TOTAL** pour la Phase G P0-BETA2. Cette version integre les **12 FACTEURS COMPORTEMENTAUX** requis pour atteindre le niveau **BIONIC V5 ULTIME x2**.

**Nouveautes v1.3.0-beta2:**
- Integration complete des 12 facteurs comportementaux
- Nouvelles pondérations dynamiques
- Recommandations contextuelles avancées
- Strategies basées sur les facteurs

**Conformite:** G-SEC | G-QA | G-DOC
**Objectif:** Alimenter l'onglet INTELLIGENCE (Analytics, Previsions, Plan Maitre)

---

# 12 FACTEURS COMPORTEMENTAUX - BIONIC V5 ULTIME x2

## RESUME EXECUTIF

| # | Facteur | Module | Poids | Status |
|---|---------|--------|-------|--------|
| 1 | Prédation (PredatorRisk, PredatorCorridors) | advanced_factors.py | 2.0% | ✅ INTEGRE |
| 2 | Stress Thermique | advanced_factors.py | 1.5% | ✅ INTEGRE |
| 3 | Stress Hydrique | advanced_factors.py | 1.0% | ✅ INTEGRE |
| 4 | Stress Social | advanced_factors.py | 1.0% | ✅ INTEGRE |
| 5 | Hiérarchie Sociale (DominanceScore, GroupBehavior) | advanced_factors.py | 1.5% | ✅ INTEGRE |
| 6 | Compétition Inter-espèces | advanced_factors.py | 1.0% | ✅ INTEGRE |
| 7 | Signaux Faibles (WeakSignals, Anomalies) | advanced_factors.py | 1.0% | ✅ INTEGRE |
| 8 | Cycles Hormonaux (rut, lactation, bois) | advanced_factors.py | 2.5% | ✅ INTEGRE |
| 9 | Cycles Digestifs (feeding→bedding) | advanced_factors.py | 1.5% | ✅ INTEGRE |
| 10 | Mémoire Territoriale (AvoidanceMemory, PreferredRoutes) | advanced_factors.py | 1.5% | ✅ INTEGRE |
| 11 | Apprentissage Comportemental (AdaptiveBehavior) | advanced_factors.py | 2.0% | ✅ INTEGRE |
| 12 | Activité Humaine Non-Chasse (HumanDisturbance) | advanced_factors.py | 1.5% | ✅ INTEGRE |
| 13 | Disponibilité Minérale (MineralAvailability, SaltLickAttraction) | advanced_factors.py | 1.0% | ✅ INTEGRE |
| 14 | Conditions de Neige (SnowDepth, CrustRisk, WinterPenalty) | advanced_factors.py | 2.0% | ✅ INTEGRE |

**Total Poids Facteurs Avancés:** 20%
**Poids Score de Base:** 80%

## DETAILS DES FACTEURS

### Facteur 1: PREDATION (PredatorRisk, PredatorCorridors)
- **Classe:** `PredatorRiskModel`
- **Inputs:** species, latitude, hour, month
- **Outputs:** risk_score, dominant_predator, wolf_risk, bear_risk, corridor_risk
- **Logique:** 
  - Risque loup élevé à l'aube/crépuscule (6-8h, 17-20h)
  - Risque ours = 0 en hiver (hibernation mois 12,1,2,3)
  - Plus haut risque en automne (chasse active des loups)

### Facteur 2: STRESS THERMIQUE
- **Classe:** `StressModel.calculate_thermal_stress`
- **Inputs:** species, temperature
- **Outputs:** stress_score, stress_type, behavioral_response
- **Logique:**
  - Orignal: optimal 0-15°C, stress >18°C ou <-20°C
  - Cerf: optimal 5-18°C, stress >22°C ou <-15°C
  - Reponses: seeking_water_shade, seeking_shelter, normal

### Facteur 3: STRESS HYDRIQUE
- **Classe:** `StressModel.calculate_hydric_stress`
- **Inputs:** species, water_distance_m, temperature
- **Outputs:** stress_score, water_seeking
- **Logique:**
  - Distance >1000m = stress élevé
  - Amplifié par température >20°C
  - Déclenche recherche d'eau active

### Facteur 4: STRESS SOCIAL
- **Classe:** `StressModel.calculate_social_stress`
- **Inputs:** species, month, group_size
- **Outputs:** stress_score, dominance_seeking
- **Logique:**
  - Pic pendant le rut (mois 10-11)
  - Groupes >5 individus = stress
  - Déclenche comportements de dominance

### Facteur 5: HIERARCHIE SOCIALE
- **Classe:** `SocialHierarchyModel`
- **Inputs:** species, month, is_male
- **Outputs:** dominance_score, aggression_level, movement_pattern
- **Logique:**
  - Males: dominance élevée pendant rut
  - Mouvement: expanded_range vs core_territory
  - Agressivité: high/medium/low

### Facteur 6: COMPETITION INTER-ESPECES
- **Classe:** `InterspeciesCompetitionModel`
- **Inputs:** target_species, region_species_list
- **Outputs:** total_competition_score, competitors
- **Logique:**
  - Chevauchement d'habitat
  - Concurrence alimentaire
  - Effets de displacement

### Facteur 7: SIGNAUX FAIBLES
- **Classe:** `WeakSignalsModel`
- **Inputs:** current_score, historical_avg, weather_rapid_change, unusual_activity
- **Outputs:** anomaly_score, anomalies_detected, confidence_adjustment
- **Logique:**
  - Détecte déviation >15% de la baseline
  - Changement météo rapide
  - Activité anormale
  - Ajuste la confiance du score

### Facteur 8: CYCLES HORMONAUX
- **Classe:** `HormonalCycleModel`
- **Inputs:** species, month
- **Outputs:** phase, activity_modifier, behavioral_focus, aggression_level
- **Phases:**
  - pre_rut (Sep): modifier 1.3x
  - rut_peak (Oct-Nov): modifier 1.5x
  - post_rut (Dec): modifier 0.8x
  - antler_growth (Avr-Jun): mineral_seeking
  - recovery (Jan-Mar): modifier 0.7x

### Facteur 9: CYCLES DIGESTIFS
- **Classe:** `DigestiveCycleModel`
- **Inputs:** species, hour
- **Outputs:** phase, feeding_probability, movement_likelihood
- **Phases:**
  - active_feeding (6-8h, 17-19h): prob 0.9
  - transitioning (5h, 9-11h, 16h, 20-21h): prob 0.5
  - resting (12-15h, 22-4h): prob 0.1-0.2

### Facteur 10: MEMOIRE TERRITORIALE
- **Classe:** `TerritorialMemoryModel`
- **Inputs:** species, days_since_disturbance, disturbance_intensity
- **Outputs:** memory_active, avoidance_score, days_until_return, preferred_route_shift
- **Logique:**
  - Mémoire active si perturbation <7-14 jours
  - Évitement proportionnel à l'intensité
  - Shift vers routes alternatives

### Facteur 11: APPRENTISSAGE COMPORTEMENTAL
- **Classe:** `AdaptiveBehaviorModel`
- **Inputs:** species, hunting_pressure_history, success_rate_hunters
- **Outputs:** adaptation_level, behavioral_shift, nocturnal_shift
- **Logique:**
  - Pression >50 = adaptation élevée
  - Success rate >0.25 = shift nocturne
  - Comportements: highly_nocturnal, increased_caution, modified_patterns

### Facteur 12: ACTIVITE HUMAINE NON-CHASSE
- **Classe:** `HumanDisturbanceModel`
- **Inputs:** disturbances_list, is_weekend, is_summer
- **Outputs:** disturbance_score, behavioral_response
- **Types:** hiking, atv, logging, camping, fishing
- **Logique:**
  - Weekend = +30% perturbation
  - Été = +20% perturbation
  - Réponses: avoidance, caution, normal

### Facteur 13: DISPONIBILITE MINERALE
- **Classe:** `MineralAvailabilityModel`
- **Inputs:** species, month, salt_lick_distance_m
- **Outputs:** mineral_need_score, salt_lick_attraction, seeking_behavior, optimal_monitoring_time
- **Logique:**
  - Besoin max printemps (Avr-Jun): croissance des bois
  - Distance <500m = forte attraction
  - Meilleur monitoring: matin

### Facteur 14: CONDITIONS DE NEIGE
- **Classe:** `SnowConditionModel`
- **Inputs:** species, snow_depth_cm, is_crusted, temperature
- **Outputs:** snow_condition, winter_penalty_score, yarding_likelihood, energy_expenditure_increase, crust_risk
- **Conditions:**
  - none: 0cm
  - light: <20cm
  - moderate: 20-50cm
  - deep: >50cm
  - crusted: croûte de glace
- **Logique:**
  - Neige profonde = ravage (yarding)
  - Croûte = mobilité réduite
  - Pénalité énergétique proportionnelle

---

# TABLE DES MATIERES

1. [12 FACTEURS COMPORTEMENTAUX](#12-facteurs-comportementaux---bionic-v5-ultime-x2)
2. [FAMILLE 1: Donnees Territoriales Avancees](#famille-1-donnees-territoriales-avancees)
3. [FAMILLE 2: Vegetation & Transitions d'Habitats](#famille-2-vegetation--transitions-dhabitats)
4. [FAMILLE 3: Alimentation & Carences](#famille-3-alimentation--carences)
5. [FAMILLE 4: Topographie & Geologie](#famille-4-topographie--geologie)
6. [FAMILLE 5: Zones Thermiques & Microclimats](#famille-5-zones-thermiques--microclimats)
7. [FAMILLE 6: Corridors de Deplacement](#famille-6-corridors-de-deplacement)
8. [FAMILLE 7: Zones de Repos & Abris](#famille-7-zones-de-repos--abris)
9. [FAMILLE 8: Pression de Chasse & Derangement](#famille-8-pression-de-chasse--derangement)
10. [FAMILLE 9: Conditions Extremes](#famille-9-conditions-extremes)
11. [FAMILLE 10: Historiques Multi-Annees](#famille-10-historiques-multi-annees)
12. [FAMILLE 11: Agregats Cameras Avances](#famille-11-agregats-cameras-avances)
13. [FAMILLE 12: Cycles Temporels Avances](#famille-12-cycles-temporels-avances)
14. [SOURCES EMPIRIQUES & SCIENTIFIQUES](#sources-empiriques--scientifiques)
15. [MAPPING MODULES P0](#mapping-modules-p0)
16. [SYNTHESE EXECUTIVE](#synthese-executive)
17. [COMPLEMENTS CRITIQUES P0 (v1.1.0)](#complements-critiques-p0-version-110)
    - [BLOC 1: Agregats Cameras Avances](#bloc-critique-1-agregats-cameras-avances)
    - [BLOC 2: Microclimats et Zones Thermiques](#bloc-critique-2-microclimats-et-zones-thermiques)
    - [BLOC 3: Pression de Chasse](#bloc-critique-3-pression-de-chasse-et-derangement)
    - [BLOC 4: Cycles Temporels Avances](#bloc-critique-4-cycles-temporels-avances)
18. [SOURCES EMPIRIQUES & SCIENTIFIQUES - EDITION COMPLETE](#sources-empiriques--scientifiques---edition-complete)
19. [ANNEXES](#annexes)

---

# FAMILLE 1: DONNEES TERRITORIALES AVANCEES

## 1.1 DONNEES EXISTANTES

### 1.1.1 Coordonnees GPS et Waypoints
| Variable | Type | Source | Localisation Code | Statut |
|----------|------|--------|-------------------|--------|
| `latitude` | float | MongoDB | `backend/modules/waypoint_engine/v1/` | EXPLOITABLE P0 |
| `longitude` | float | MongoDB | `backend/modules/waypoint_engine/v1/` | EXPLOITABLE P0 |
| `waypoint_type` | enum | MongoDB | Types: zec, pourvoirie, prive, sepaq, affut, saline, observation, camp | EXPLOITABLE P0 |
| `waypoint_notes` | string | MongoDB | Notes utilisateur libres | EXPLOITABLE P0 |
| `active` | boolean | MongoDB | Waypoint actif/inactif | EXPLOITABLE P0 |

**Collection MongoDB:** `territory_waypoints`, `waypoints`, `geo_entities`

### 1.1.2 Couches Cartographiques BIONIC
| Layer ID | Nom | Couleur | Description | Poids Scoring |
|----------|-----|---------|-------------|---------------|
| `habitats` | Habitats optimaux | #22c55e | Zones d'habitat ideales | 25% |
| `rut` | Rut potentiel | #e91e63 | Zones de rut identifiees | 20% |
| `salines` | Salines potentielles | #00bcd4 | Points de salines | 10% |
| `affuts` | Affuts potentiels | #9c27b0 | Positions d'affut | 20% |
| `trajets` | Trajets de chasse | #ff9800 | Routes recommandees | 15% |
| `peuplements` | Peuplements forestiers | #4caf50 | Types de foret | 10% |

**Localisation:** `frontend/src/components/TerritoryMap.jsx`

### 1.1.3 Services WMS Gouvernementaux (Quebec)
| Service | URL | Couches | Frequence MAJ |
|---------|-----|---------|---------------|
| Foret | servicescarto.mffp.gouv.qc.ca | Couverture forestiere | Annuelle |
| Hydro | servicescarto.mern.gouv.qc.ca | Hydrographie GRHQ | Statique |
| Topo | servicescarto.mern.gouv.qc.ca | Relief LiDAR | Statique |
| Routes | servicescarto.mern.gouv.qc.ca | Routes et chemins | Annuelle |
| Cadastre | servicescarto.mern.gouv.qc.ca | Cadastre | Annuelle |

**Localisation:** `frontend/src/pages/MapPage.jsx`

### 1.1.4 Entites Territoriales Utilisateur
| Entite | Collection | Champs Cles |
|--------|------------|-------------|
| Lieux | `user_places` | id, name, type, lat, lng, notes |
| Tracks | `user_tracks` | points GPS, distance, duree |
| Favoris | `zone_favorites` | zone_id, alertes, notes |

## 1.2 DONNEES MANQUANTES

| Donnee | Description | Impact P0 | Priorite |
|--------|-------------|-----------|----------|
| Delimitation ZEC/Pourvoiries | Polygones officiels des zones de chasse | CRITIQUE | P0 |
| Zones d'exclusion | Zones interdites a la chasse | CRITIQUE | P0 |
| Cadastre faunique | Decoupage administratif MFFP | HAUTE | P1 |
| Zones de securite tir | Calcul automatique selon reglementation | MOYENNE | P1 |

## 1.3 DONNEES A ACQUERIR

| Source | Donnee | Methode d'acquisition | Fiabilite |
|--------|--------|----------------------|-----------|
| MFFP Quebec | Polygones ZEC/Pourvoiries | API REST ou telechargement shapefile | 0.95 |
| MFFP Quebec | Zones d'exclusion chasse | Donnees ouvertes Quebec | 0.95 |
| OpenStreetMap | Sentiers et chemins | API Overpass | 0.80 |
| Cadastre Quebec | Limites proprietes | WMS/WFS | 0.90 |

## 1.4 LIMITES, BIAIS ET RISQUES

| Limite | Description | Mitigation |
|--------|-------------|------------|
| Precision GPS | ±3-10m selon appareil utilisateur | Algorithme de lissage, moyenne mobile |
| Couverture WMS | Temps de latence variable | Cache local, fallback tiles statiques |
| MAJ Cadastre | Donnees parfois obsoletes (1-2 ans) | Horodatage visible, refresh annuel |
| Biais utilisateur | Waypoints concentres zones accessibles | Ponderation par densite |

---

# FAMILLE 2: VEGETATION & TRANSITIONS D'HABITATS

## 2.1 DONNEES EXISTANTES

### 2.1.1 Variables d'Habitat (Knowledge Layer)
| Variable | ID | Unite | Source | Poids Especes |
|----------|----|----|--------|---------------|
| NDVI | `ndvi` | index [-1, 1] | NASA MODIS, Sentinel2 | moose: 0.7, deer: 0.6, bear: 0.7 |
| Couvert forestier | `canopy_cover` | % [0-100] | Satellite, LiDAR | moose: 0.8, deer: 0.7, bear: 0.6 |
| Densite canopee | `canopy_density` | % [0-100] | LiDAR, Sentinel2 | moose: 0.7, deer: 0.65, bear: 0.6 |
| Densite lisieres | `edge_density` | m/ha [0-500] | Satellite, inventaire | moose: 0.85, deer: 0.9, bear: 0.6 |

**Localisation:** `/app/backend/modules/bionic_knowledge_engine/data/habitat_variables.json`

### 2.1.2 Types d'Habitats (Enums)
```python
class HabitatType(str, Enum):
    CONIFEROUS_FOREST = "coniferous_forest"    # Foret coniferienne
    DECIDUOUS_FOREST = "deciduous_forest"      # Foret feuillue
    MIXED_FOREST = "mixed_forest"              # Foret mixte
    WETLAND = "wetland"                        # Milieu humide
    BOG = "bog"                                # Tourbiere
    MARSH = "marsh"                            # Marecage
    LAKE_SHORE = "lake_shore"                  # Rive de lac
    RIVER_CORRIDOR = "river_corridor"          # Corridor riverain
    RIDGE = "ridge"                            # Crete
    VALLEY = "valley"                          # Vallee
    CLEARCUT = "clearcut"                      # Coupe forestiere
    REGENERATION = "regeneration"              # Regeneration
    AGRICULTURAL = "agricultural"              # Zone agricole
    ALPINE = "alpine"                          # Zone alpine
    TUNDRA = "tundra"                          # Toundra
```

**Localisation:** `/app/backend/modules/bionic_knowledge_engine/knowledge_models.py`

### 2.1.3 Preferences d'Habitat par Espece
| Espece | Habitat Principal | Score | Habitat Secondaire | Score |
|--------|-------------------|-------|-------------------|-------|
| Orignal | wetland | 0.90 | mixed_forest | 0.85 |
| Cerf | forest_edge | 0.85 | regeneration | 0.80 |
| Ours | mixed_forest | 0.80 | berry_patches | 0.75 |

**Localisation:** `/app/backend/modules/bionic_knowledge_engine/data/species/moose.json`

## 2.2 DONNEES MANQUANTES

| Donnee | Description | Impact P0 | Priorite |
|--------|-------------|-----------|----------|
| Ecotones dynamiques | Transitions inter-habitats en temps reel | HAUTE | P0 |
| Age des peuplements | Maturite forestiere (jeune/mature/vieux) | HAUTE | P1 |
| Perturbations recentes | Coupes, feux, epidemies (5 derniers ans) | MOYENNE | P1 |
| Phenologie vegetale | Stade de developpement saisonnier | MOYENNE | P1 |

## 2.3 DONNEES A ACQUERIR

| Source | Donnee | Methode | Fiabilite | Cout |
|--------|--------|---------|-----------|------|
| Sentinel-2 | NDVI haute resolution | API Copernicus | 0.90 | Gratuit |
| MFFP | Inventaire ecoforestier | Donnees ouvertes | 0.95 | Gratuit |
| CFS-NRCan | Perturbations forestieres | API REST | 0.85 | Gratuit |
| NASA MODIS | Phenologie FPAR/LAI | AppEEARS | 0.85 | Gratuit |

## 2.4 LIMITES, BIAIS ET RISQUES

| Limite | Description | Mitigation |
|--------|-------------|------------|
| Resolution NDVI | 10-30m selon source | Interpolation spatiale |
| Delai satellite | 5-16 jours selon orbite | Fusion multi-capteurs |
| Couvert nuageux | Masquage frequent au Quebec | Composite temporel |
| Saisonnalite | NDVI non pertinent en hiver | Modeles saisonniers adaptes |

---

# FAMILLE 3: ALIMENTATION & CARENCES

## 3.1 DONNEES EXISTANTES

### 3.1.1 Sources Alimentaires par Espece
| Espece | Source | Nom FR | Categorie | Mois Dispo | Preference |
|--------|--------|--------|-----------|------------|------------|
| Orignal | willow | Saule | browse | 5-9 | 0.95 |
| Orignal | aquatic_plants | Plantes aquatiques | browse | 6-8 | 0.90 |
| Orignal | birch | Bouleau | browse | 5-10 | 0.80 |
| Orignal | balsam_fir | Sapin baumier | browse | 11-3 | 0.75 |
| Cerf | browse | Brout | browse | toute annee | 0.85 |
| Cerf | forbs | Plantes herbacees | graze | 5-9 | 0.80 |
| Cerf | mast | Glands/noix | mast | 9-11 | 0.90 |
| Ours | berries | Baies | fruit | 7-9 | 0.95 |
| Ours | nuts | Noix | mast | 9-11 | 0.85 |

**Localisation:** `/app/backend/modules/bionic_knowledge_engine/data/species/*.json`

### 3.1.2 Couche Alimentation (Frontend)
| Layer | ID | Couleur | Description |
|-------|----|---------| ------------|
| Zones alimentation | `alimentation` | #8bc34a | Sources de nourriture identifiees |

**Localisation:** `frontend/src/components/TerritoryMap.jsx`

### 3.1.3 Valeurs Nutritionnelles
| Source | Valeur Nutritionnelle | Persistance | Attractivite |
|--------|----------------------|-------------|--------------|
| Plantes aquatiques | 0.90 | 3 mois | 0.95 |
| Saule | 0.80 | 5 mois | 0.90 |
| Baies | 0.85 | 2 mois | 0.95 |

## 3.2 DONNEES MANQUANTES

| Donnee | Description | Impact P0 | Priorite |
|--------|-------------|-----------|----------|
| Cartes de mast | Localisation chenes, noyers, hetre | CRITIQUE | P0 |
| Stress alimentaire | Indicateurs de carence par zone | HAUTE | P0 |
| Salines naturelles | Localisation des sources minerales | HAUTE | P0 |
| Production fruitiere | Estimation annuelle de la production de baies | MOYENNE | P1 |

## 3.3 DONNEES A ACQUERIR

| Source | Donnee | Methode | Fiabilite |
|--------|--------|---------|-----------|
| MFFP | Cartes essences forestieres | Inventaire ecoforestier | 0.90 |
| UQAR | Etudes stress alimentaire | Publications scientifiques | 0.85 |
| Terrain utilisateur | Salines naturelles | Crowdsourcing waypoints | 0.75 |
| Sentinel-2 | Phenologie floraison/fructification | NDVI temporel | 0.70 |

## 3.4 LIMITES, BIAIS ET RISQUES

| Limite | Description | Mitigation |
|--------|-------------|------------|
| Variabilite interannuelle | Production de mast tres variable | Historique 5 ans |
| Localisation approximative | Sources alimentaires estimees | Validation terrain |
| Biais echantillonnage | Donnees concentrees zones accessibles | Modeles predictifs |

---

# FAMILLE 4: TOPOGRAPHIE & GEOLOGIE

## 4.1 DONNEES EXISTANTES

### 4.1.1 Variables Topographiques
| Variable | ID | Unite | Source | Poids |
|----------|----|----|--------|-------|
| Elevation | `elevation` | m | open_elevation, SRTM | moose: 0.5, deer: 0.4 |
| Pente | `slope` | degres [0-90] | DEM derive | moose: 0.3, deer: 0.4 |
| Orientation | `aspect` | degres [0-360] | DEM derive | moose: 0.4, deer: 0.5 |
| Exposition | `slope_aspect` | cardinal (N,NE,E...) | DEM derive | saisonnier |

**Localisation:** `/app/backend/modules/bionic_knowledge_engine/data/habitat_variables.json`

### 4.1.2 Couches Cartographiques Terrain
| Layer | ID | Couleur | Description |
|-------|----|---------| ------------|
| Pentes | `pentes` | #ff7043 | Inclinaison terrain |
| Altitude | `altitude` | #78909c | Elevation relative |
| Orientation | `orientation` | #2196f3 | Direction terrain |
| Ensoleillement | `ensoleillement` | #ffeb3b | Exposition solaire |

**Localisation:** `frontend/src/components/TerritoryMap.jsx`

### 4.1.3 Plages Optimales par Espece
| Espece | Elevation Min | Elevation Max | Elevation Optimale | Pente Preferee |
|--------|---------------|---------------|-------------------|----------------|
| Orignal | 0m | 1200m | 300m | 5-15 degres |
| Cerf | 0m | 800m | 200m | 0-20 degres |
| Ours | 0m | 1500m | 400m | variable |

**Localisation:** `/app/backend/modules/bionic_knowledge_engine/data/species/moose.json`

## 4.2 DONNEES MANQUANTES

| Donnee | Description | Impact P0 | Priorite |
|--------|-------------|-----------|----------|
| Rugosite terrain | Indice de difficulte de deplacement | HAUTE | P0 |
| Geologie surfacique | Type de sol, roche mere | MOYENNE | P1 |
| Drainage | Capacite d'evacuation des eaux | MOYENNE | P1 |
| Microrelief | Depressions, buttes, ravines | BASSE | P2 |

## 4.3 DONNEES A ACQUERIR

| Source | Donnee | Methode | Resolution | Fiabilite |
|--------|--------|---------|------------|-----------|
| USGS | SRTM DEM | Telechargement direct | 30m | 0.90 |
| Quebec LiDAR | MNT haute precision | MERN | 1m | 0.98 |
| GSC | Geologie surfacique | Donnees ouvertes | 1:250k | 0.85 |

## 4.4 LIMITES, BIAIS ET RISQUES

| Limite | Description | Mitigation |
|--------|-------------|------------|
| Resolution SRTM | 30m insuffisant pour microrelief | LiDAR provincial |
| Couverture LiDAR | Non disponible partout au Quebec | Fusion SRTM/LiDAR |
| Artefacts DEM | Erreurs dans zones forestieres denses | Filtrage algorithmique |

---

# FAMILLE 5: ZONES THERMIQUES & MICROCLIMATS

## 5.1 DONNEES EXISTANTES

### 5.1.1 Variables Climatiques
| Variable | ID | Unite | Source | MAJ | Poids |
|----------|----|----|--------|-----|-------|
| Temperature | `temperature` | degC | open_meteo, environment_canada | temps reel | moose: 0.9, deer: 0.6 |
| Vitesse vent | `wind_speed` | km/h | open_meteo | temps reel | moose: 0.6, deer: 0.7 |
| Humidite | `humidity` | % | open_meteo | temps reel | 0.5 |
| Precipitation | `precipitation` | mm/h | open_meteo | horaire | moose: 0.5, deer: 0.6 |
| Pression | `barometric_pressure` | hPa | open_meteo | horaire | moose: 0.4, deer: 0.8 |

**Localisation:** `/app/backend/modules/bionic_knowledge_engine/data/habitat_variables.json`

### 5.1.2 Plages de Temperature Optimales
| Espece | Optimal Min | Optimal Max | Tolerance Min | Tolerance Max | Seuil Activite |
|--------|-------------|-------------|---------------|---------------|----------------|
| Orignal | -5C | 14C | -40C | 25C | 20C |
| Cerf | -5C | 15C | -30C | 30C | 25C |
| Ours | 5C | 25C | -20C | 35C | 30C |

**Localisation:** `/app/backend/modules/bionic_knowledge_engine/data/species/*.json`

### 5.1.3 Conditions Optimales de Chasse
```python
OPTIMAL_CONDITIONS = {
    "temperature": {"min": -5, "max": 15, "ideal": 5},  # Celsius
    "humidity": {"min": 40, "max": 80, "ideal": 60},    # %
    "wind_speed": {"min": 0, "max": 20, "ideal": 8},    # km/h
    "pressure_change": 5  # hPa - declencheur d'activite
}
```

**Localisation:** `/app/backend/modules/weather_engine/v1/service.py`

## 5.2 DONNEES MANQUANTES

| Donnee | Description | Impact P0 | Priorite |
|--------|-------------|-----------|----------|
| Temperature au sol | Differentiel air/sol crucial pour gibier | CRITIQUE | P0 |
| Microclimats topographiques | Poches de froid/chaleur locales | HAUTE | P0 |
| Gradient thermique vertical | Temperature selon altitude | HAUTE | P0 |
| Couverture nuageuse | Impact sur rayonnement et comportement | MOYENNE | P1 |

## 5.3 DONNEES A ACQUERIR

| Source | Donnee | Methode | Fiabilite |
|--------|--------|---------|-----------|
| Open-Meteo | Donnees horaires completes | API REST gratuite | 0.85 |
| Environment Canada | Stations meteo officielles | API REST | 0.95 |
| Modele derive | Microclimats (aspect x elevation) | Calcul local | 0.70 |
| GOES Satellite | Couverture nuageuse temps reel | API NOAA | 0.90 |

## 5.4 LIMITES, BIAIS ET RISQUES

| Limite | Description | Mitigation |
|--------|-------------|------------|
| Resolution spatiale meteo | Stations espacees 50-100km | Interpolation spatiale |
| Previsions > 7 jours | Fiabilite decroissante | Limiter affichage a 5 jours |
| Microclimats non modelises | Variations locales non captees | Modele topographique |
| Delai API | Latence 1-5 min | Cache intelligent |

---

# FAMILLE 6: CORRIDORS DE DEPLACEMENT

## 6.1 DONNEES EXISTANTES

### 6.1.1 Couche Corridors
| Layer | ID | Couleur | Description |
|-------|----|---------| ------------|
| Corridors fauniques | `corridors` | #ff5722 | Passages faune identifies |

**Localisation:** `frontend/src/components/TerritoryMap.jsx`

### 6.1.2 Service Comportemental - Corridors
```javascript
// BehavioralService.js
static async getMovementCorridors(lat, lng, species, radiusKm = 5)
// Retourne: { corridors: [{ id, type, traffic, ... }] }
```

**Localisation:** `/app/frontend/src/modules/behavioral/BehavioralService.js`

### 6.1.3 Patterns de Deplacement Backend
```python
# MovementPattern - modele de donnees
{
    "typical_routes": [
        {"type": "feeding_to_bedding", "distance_km": 0.5, "typical_time": "08:00"},
        {"type": "bedding_to_feeding", "distance_km": 0.5, "typical_time": "16:00"}
    ],
    "travel_corridors": [
        {"type": "ridge_line", "usage": "high"},
        {"type": "creek_bottom", "usage": "medium"}
    ]
}
```

**Localisation:** `/app/backend/modules/wildlife_behavior_engine/v1/service.py`

## 6.2 DONNEES MANQUANTES

| Donnee | Description | Impact P0 | Priorite |
|--------|-------------|-----------|----------|
| Detection corridors GPS | Identification automatique depuis cameras | CRITIQUE | P0 |
| Intensite de trafic | Frequence d'utilisation des corridors | CRITIQUE | P0 |
| Saisonnalite corridors | Variation des routes selon saisons | HAUTE | P0 |
| Goulots d'etranglement | Points de passage obligatoires | HAUTE | P0 |

## 6.3 DONNEES A ACQUERIR

| Source | Donnee | Methode | Fiabilite |
|--------|--------|---------|-----------|
| Cameras trail | Patterns de passage | Agregation temporelle | 0.85 |
| Telemetrie externe | Donnees GPS colliers (etudes MFFP) | Partenariat | 0.95 |
| UQAR | Corridors modelises | Publications | 0.90 |
| Utilisateurs | Observations terrain | Crowdsourcing | 0.70 |

## 6.4 LIMITES, BIAIS ET RISQUES

| Limite | Description | Mitigation |
|--------|-------------|------------|
| Echantillonnage cameras | Couverture partielle | Modeles predictifs |
| Biais placement cameras | Sur sentiers accessibles | Ponderation spatiale |
| Dynamique temporelle | Corridors changent avec perturbations | MAJ annuelle |

---

# FAMILLE 7: ZONES DE REPOS & ABRIS

## 7.1 DONNEES EXISTANTES

### 7.1.1 Couche Repos
| Layer | ID | Couleur | Description |
|-------|----|---------| ------------|
| Zones de repos | `repos` | #795548 | Zones de coucher identifiees |

**Localisation:** `frontend/src/components/TerritoryMap.jsx`

### 7.1.2 Service Comportemental - Zones de Coucher
```javascript
// BehavioralService.js
static async getBeddingAreas(lat, lng, species, radiusKm = 3)
// Retourne: { areas: [{ id, name, score, type }] }
```

**Localisation:** `/app/frontend/src/modules/behavioral/BehavioralService.js`

### 7.1.3 Zones de Concentration
```python
# WildlifeBehaviorService
"concentration_zones": [
    {"type": "bedding_area", "habitat": "thick_cover"},
    {"type": "water_source", "habitat": "stream"}
]
```

**Localisation:** `/app/backend/modules/wildlife_behavior_engine/v1/service.py`

## 7.2 DONNEES MANQUANTES

| Donnee | Description | Impact P0 | Priorite |
|--------|-------------|-----------|----------|
| Ravages hivernaux | Zones de concentration hivernale orignal | CRITIQUE | P0 |
| Abris thermiques | Zones protegees du vent/froid | HAUTE | P0 |
| Densite couvert | Indice de protection visuelle | HAUTE | P0 |
| Distance securite | Eloignement routes/habitations | MOYENNE | P1 |

## 7.3 DONNEES A ACQUERIR

| Source | Donnee | Methode | Fiabilite |
|--------|--------|---------|-----------|
| MFFP | Inventaire ravages | Donnees officielles | 0.95 |
| LiDAR | Densite sous-bois | Analyse 3D | 0.90 |
| Modele derive | Score abri (canopy x slope x aspect) | Calcul | 0.75 |

## 7.4 LIMITES, BIAIS ET RISQUES

| Limite | Description | Mitigation |
|--------|-------------|------------|
| Ravages dynamiques | Changent selon conditions neige | MAJ saisonniere |
| Resolution LiDAR | Non disponible partout | Proxy satellite |

---

# FAMILLE 8: PRESSION DE CHASSE & DERANGEMENT

## 8.1 DONNEES EXISTANTES

### 8.1.1 Variables Impact Humain
| Variable | ID | Unite | Source | Poids |
|----------|----|----|--------|-------|
| Distance route | `road_distance` | m | OSM, MTQ | moose: 0.7, deer: 0.6, bear: 0.5 |
| Distance batiment | `building_distance` | m | OSM, Cadastre | moose: 0.6, deer: 0.5, bear: 0.7 |
| Indice pression humaine | `human_pressure_index` | [0-1] | Composite | moose: 0.75, deer: 0.6, bear: 0.85 |

**Localisation:** `/app/backend/modules/bionic_knowledge_engine/data/habitat_variables.json`

### 8.1.2 Tolerance et Fuite par Espece
| Espece | Tolerance Humaine | Distance Fuite | Evitement Route |
|--------|-------------------|----------------|-----------------|
| Orignal | 0.30 | 150m | 300m |
| Cerf | 0.35 | 100m | 200m |
| Ours | 0.25 | 200m | 250m |

**Localisation:** `/app/backend/modules/bionic_knowledge_engine/data/species/*.json`

### 8.1.3 Sorties de Chasse Enregistrees
| Variable | Type | Source | Collection |
|----------|------|--------|------------|
| `total_trips` | integer | MongoDB | `hunting_trips` |
| `date` | datetime | MongoDB | Par sortie |
| `duration_hours` | float | MongoDB | Par sortie |
| `success` | boolean | MongoDB | Par sortie |
| `location` | coordinates | MongoDB | Par sortie |

**Localisation:** `/app/backend/modules/analytics_engine/`

## 8.2 DONNEES MANQUANTES

| Donnee | Description | Impact P0 | Priorite |
|--------|-------------|-----------|----------|
| Densite chasseurs | Nombre chasseurs par zone/periode | CRITIQUE | P0 |
| Pression cumulative | Historique pression sur plusieurs jours | CRITIQUE | P0 |
| Activites recreatives | Randonnee, VTT, motoneige | HAUTE | P0 |
| Calendrier ouvertures | Dates chasse par zone/espece | HAUTE | P0 |

## 8.3 DONNEES A ACQUERIR

| Source | Donnee | Methode | Fiabilite |
|--------|--------|---------|-----------|
| MFFP | Statistiques recolte | Rapports publics | 0.95 |
| Strava Heatmap | Activites recreatives | API | 0.80 |
| Utilisateurs HUNTIQ | Sorties enregistrees | Agregation interne | 0.85 |
| SEPAQ | Frequentation reserves | Partenariat | 0.90 |

## 8.4 LIMITES, BIAIS ET RISQUES

| Limite | Description | Mitigation |
|--------|-------------|------------|
| Donnees privees | Sorties non partagees | Opt-in anonymise |
| Biais territorial | Concentration zones populaires | Normalisation |
| Temps reel impossible | Pas de tracking live chasseurs | Modeles predictifs |

---

# FAMILLE 9: CONDITIONS EXTREMES

## 9.1 DONNEES EXISTANTES

### 9.1.1 Seuils Climatiques
| Condition | Seuil | Impact Comportement | Source |
|-----------|-------|---------------------|--------|
| Vent fort | > 30 km/h | Reduction activite -25% | WeatherService |
| Pluie forte | > 5 mm/h | Reduction activite -20% | WeatherService |
| Froid extreme | < -20C | Reduction deplacement | SPECIES_PATTERNS |
| Chaleur extreme | > 25C | Inactivite diurne | SPECIES_PATTERNS |

**Localisation:** `/app/backend/modules/weather_engine/v1/service.py`

### 9.1.2 Modificateurs Saisonniers
```python
SEASON_FACTORS = {
    1: 0.6,   # Janvier - froid
    2: 0.5,   # Fevrier - tres froid
    7: 0.5,   # Juillet - chaleur
    10: 0.95, # Octobre - pic
    11: 0.9,  # Novembre - rut
}
```

**Localisation:** `/app/backend/modules/predictive_engine/v1/service.py`

## 9.2 DONNEES MANQUANTES

| Donnee | Description | Impact P0 | Priorite |
|--------|-------------|-----------|----------|
| Epaisseur neige | Impact mobilite et energie | CRITIQUE | P0 |
| Gel au sol | Accessibilite nourriture | HAUTE | P0 |
| Verglas | Dangerosité deplacement | HAUTE | P0 |
| Stress thermique | Index combine (temp + humidex) | MOYENNE | P1 |

## 9.3 DONNEES A ACQUERIR

| Source | Donnee | Methode | Fiabilite |
|--------|--------|---------|-----------|
| Environment Canada | Epaisseur neige stations | API REST | 0.90 |
| NOAA | Modeles neige SNODAS | Telechargement | 0.85 |
| Derive | Stress thermique (formule) | Calcul | 0.80 |

## 9.4 LIMITES, BIAIS ET RISQUES

| Limite | Description | Mitigation |
|--------|-------------|------------|
| Stations espacees | Interpolation necessaire | Krigeage spatial |
| Micro-variabilite neige | Accumulation locale variable | Modele topographique |

---

# FAMILLE 10: HISTORIQUES MULTI-ANNEES

## 10.1 DONNEES EXISTANTES

### 10.1.1 Collections MongoDB Historiques
| Collection | Donnees | Profondeur | Volume Estime |
|------------|---------|------------|---------------|
| `hunting_trips` | Sorties de chasse | Depuis creation | ~51+ records demo |
| `camera_events` | Photos cameras | Depuis creation | Variable |
| `territory_waypoints` | Waypoints | Depuis creation | Variable |
| `user_observations` | Observations faune | Depuis creation | Variable |

### 10.1.2 Modeles Saisonniers
```python
# SeasonalModel - structure
{
    "species_id": "moose",
    "region": "quebec_south",
    "year": 2024,
    "phases": [
        {"name": "rut", "start": "2024-09-15", "peak": "2024-10-01", "end": "2024-10-20"}
    ],
    "accuracy_score": 0.85,
    "validation_observations": 150
}
```

**Localisation:** `/app/backend/modules/bionic_knowledge_engine/knowledge_models.py`

## 10.2 DONNEES MANQUANTES

| Donnee | Description | Impact P0 | Priorite |
|--------|-------------|-----------|----------|
| Historique recolte MFFP | Statistiques officielles multi-annees | CRITIQUE | P0 |
| Tendances populations | Evolution densites par zone | CRITIQUE | P0 |
| Patterns interannuels | Cycles pluriannuels (mastage, populations) | HAUTE | P1 |
| Baseline climat | Normales climatiques 30 ans | MOYENNE | P1 |

## 10.3 DONNEES A ACQUERIR

| Source | Donnee | Methode | Profondeur | Fiabilite |
|--------|--------|---------|------------|-----------|
| MFFP | Statistiques recolte | Rapports PDF/API | 10+ ans | 0.95 |
| Environment Canada | Normales climatiques | API | 30 ans | 0.95 |
| UQAR | Etudes populations | Publications | Variable | 0.90 |
| Louis Gagnon | Historique terrain | Entrevues | 30+ ans | 0.85 |

## 10.4 LIMITES, BIAIS ET RISQUES

| Limite | Description | Mitigation |
|--------|-------------|------------|
| Donnees fragmentees | Formats et sources heterogenes | ETL standardise |
| Biais d'echantillonnage | Zones mieux documentees que d'autres | Ponderation |
| Changements methodo | Protocoles de collecte evolues | Normalisation |

---

# FAMILLE 11: AGREGATS CAMERAS AVANCES

## 11.1 DONNEES EXISTANTES

### 11.1.1 Schema Camera Event
```python
# CameraEvent - modele complet
{
    "id": str,
    "user_id": str,
    "camera_id": str,
    "waypoint_id": str,  # OBLIGATOIRE
    "timestamp": datetime,
    "raw_image_url": str,  # Chemin chiffre
    "exif_data": {
        "timestamp": str,
        "gps_lat": float,
        "gps_lon": float,
        "camera_make": str,
        "camera_model": str
    },
    "species": str,            # Detecte par IA (Phase 2)
    "species_confidence": float,# Score IA
    "created_at": datetime
}
```

**Localisation:** `/app/backend/modules/camera_engine/v1/services.py`

### 11.1.2 Service Detection Especes
| Fonctionnalite | Statut | Module |
|----------------|--------|--------|
| Registre cameras | ACTIF | camera_engine |
| Ingestion email | ACTIF | camera_engine |
| Extraction EXIF | ACTIF | camera_engine |
| Chiffrement images | ACTIF | camera_engine |
| Detection especes IA | PREVU Phase 2 | camera_engine |

**Localisation:** `/app/backend/modules/camera_engine/v1/`

## 11.2 DONNEES MANQUANTES

| Donnee | Description | Impact P0 | Priorite |
|--------|-------------|-----------|----------|
| Classification especes | Detection automatique sur photos | CRITIQUE | P0 |
| Comptage individus | Nombre d'animaux par photo | CRITIQUE | P0 |
| Patterns temporels | Distribution horaire des detections | HAUTE | P0 |
| Heatmaps cameras | Agregation spatiale des detections | HAUTE | P0 |
| Comportement detecte | Alimentation, deplacement, repos | MOYENNE | P1 |

## 11.3 DONNEES A ACQUERIR

| Source | Donnee | Methode | Fiabilite |
|--------|--------|---------|-----------|
| GPT-5.2 Vision | Classification especes | API Emergent LLM | 0.85 |
| MegaDetector | Detection animaux | Modele pre-entraine | 0.90 |
| Agregation interne | Patterns temporels | Calcul | 0.95 |
| PostGIS | Heatmaps spatiaux | Calcul | 0.95 |

## 11.4 LIMITES, BIAIS ET RISQUES

| Limite | Description | Mitigation |
|--------|-------------|------------|
| Qualite photos | Photos nuit basse resolution | Pre-traitement images |
| Faux positifs IA | Detection erronee | Seuil confiance > 0.7 |
| Biais placement | Cameras sur sentiers | Normalisation spatiale |
| Volume images | Stockage et traitement couteux | Compression, purge |

---

# FAMILLE 12: CYCLES TEMPORELS AVANCES

## 12.1 DONNEES EXISTANTES

### 12.1.1 Cycles Horaires d'Activite
```python
# SPECIES_PATTERNS - activite par periode
{
    "deer": {
        "dawn_activity": 95,
        "midday_activity": 30,
        "dusk_activity": 90,
        "night_activity": 60
    },
    "moose": {
        "dawn_activity": 85,
        "midday_activity": 25,
        "dusk_activity": 80,
        "night_activity": 50
    }
}
```

**Localisation:** `/app/backend/modules/predictive_engine/v1/service.py`

### 12.1.2 Patterns Activite Detailles
| Espece | Periode | Niveau Activite | Probabilite Alimentation | Probabilite Mouvement |
|--------|---------|-----------------|-------------------------|----------------------|
| Orignal | dawn | 0.90 | 0.80 | 0.70 |
| Orignal | midday | 0.30 | 0.20 | 0.20 |
| Orignal | dusk | 0.90 | 0.80 | 0.70 |

**Localisation:** `/app/backend/modules/bionic_knowledge_engine/data/species/moose.json`

### 12.1.3 Cycles Lunaires
```python
# MoonPhase - service meteo
{
    "phase": "new/waxing_crescent/first_quarter/...",
    "illumination": 0-100,
    "hunting_impact": "description textuelle"
}
# Cycle: 29.53 jours
# Nouvelle lune: +activite diurne
# Pleine lune: +activite nocturne
```

**Localisation:** `/app/backend/modules/weather_engine/v1/service.py`

### 12.1.4 Cycles Saisonniers
| Saison | Enum | Multiplicateur Activite | Comportements |
|--------|------|------------------------|---------------|
| PRE_RUT | pre_rut | 1.2 | Territorial, scrapes |
| RUT | rut | 1.5 | Rutting, chasing |
| POST_RUT | post_rut | 0.8 | Feeding, recovery |
| WINTER | winter | 0.5 | Minimal movement |

**Localisation:** `/app/backend/modules/wildlife_behavior_engine/v1/service.py`

### 12.1.5 Dates de Rut par Espece
| Espece | Debut Rut | Pic Rut | Fin Rut |
|--------|-----------|---------|---------|
| Orignal | Septembre | Octobre | Octobre |
| Cerf | Octobre | Novembre | Novembre |

## 12.2 DONNEES MANQUANTES

| Donnee | Description | Impact P0 | Priorite |
|--------|-------------|-----------|----------|
| Photopériode | Impact duree du jour sur comportement | CRITIQUE | P0 |
| Cycles pluriannuels | Patterns sur 3-5 ans (populations) | HAUTE | P1 |
| Evenements astronomiques | Lever/coucher soleil precis par coord | HAUTE | P0 |
| Migration saisonnière | Mouvements altitude/latitude | MOYENNE | P1 |

## 12.3 DONNEES A ACQUERIR

| Source | Donnee | Methode | Fiabilite |
|--------|--------|---------|-----------|
| SunCalc | Ephemerides solaires | Bibliotheque calcul | 0.99 |
| legal_time_engine | Heures legales chasse | Calcul | 0.99 |
| NOAA | Photoperiode par latitude | API | 0.95 |
| UQAR | Cycles pluriannuels | Publications | 0.85 |

## 12.4 LIMITES, BIAIS ET RISQUES

| Limite | Description | Mitigation |
|--------|-------------|------------|
| Variabilite interannuelle | Dates rut variables ±2 semaines | Fourchette dynamique |
| Latitude dependante | Patterns differents nord/sud | Regionalisation |

---

# SOURCES EMPIRIQUES & SCIENTIFIQUES

## SOURCES INTEGREES (ACTIVES)

| ID | Nom | Type | Fiabilite | Especes | Statut |
|----|-----|------|-----------|---------|--------|
| `mffp_quebec` | MFFP Quebec | government_report | 0.95 | moose, deer, bear, caribou | INTEGRE |
| `sepaq` | SEPAQ | government_report | 0.90 | moose, deer, bear | INTEGRE |
| `cic_quebec` | Canards Illimites Quebec | scientific_paper | 0.90 | waterfowl | INTEGRE |
| `fqf` | Federation chasseurs Quebec | expert_interview | 0.80 | all | INTEGRE |
| `wildlife_research_ulaval` | CEN U. Laval | scientific_paper | 0.95 | caribou, moose, bear | INTEGRE |
| `wildlife_society_na` | The Wildlife Society | scientific_paper | 0.92 | moose, deer, bear | INTEGRE |
| `usgs_wildlife` | USGS Wildlife Research | scientific_paper | 0.95 | all | INTEGRE |
| `ulaval_forestry` | FFGG U. Laval | scientific_paper | 0.92 | moose, deer, bear | INTEGRE |
| `expert_louis_gagnon` | Louis Gagnon | expert_interview | 0.85 | moose, caribou, bear | INTEGRE |
| `expert_guides_nordiques` | Guides Nordiques QC | expert_interview | 0.82 | all | INTEGRE |

**Localisation:** `/app/backend/modules/bionic_knowledge_engine/data/sources_registry.json`

## SOURCES A INTEGRER (PRIORITAIRES)

| Source | Donnees | Priorite | Methode Integration |
|--------|---------|----------|---------------------|
| UQAR | Etudes comportementales orignal | P0 | Publications PDF, structuration |
| "De la bouche des orignaux" | Savoir empirique compile | P0 | Extraction manuelle, validation |
| Louis Gagnon (approfondi) | 30+ ans terrain nord Quebec | P0 | Entrevues structurees |
| CWS-SCF | Donnees federales faune | P1 | API/Donnees ouvertes |
| iNaturalist Quebec | Observations citoyennes | P1 | API REST |
| eBird Quebec | Observations oiseaux (prey/predators) | P2 | API REST |

## STATUT PAR SOURCE

| Source | Integre | Disponible | A Integrer | Non Disponible |
|--------|---------|------------|------------|----------------|
| MFFP Quebec | X | | | |
| SEPAQ | X | | | |
| CIC Quebec | X | | | |
| Louis Gagnon | X (partiel) | | X (approfondi) | |
| UQAR | | X | X | |
| "De la bouche des orignaux" | | X | X | |
| Telemetrie GPS | | | | X (partenariat requis) |

---

# MAPPING MODULES P0

## PREDICTIVE_TERRITORIAL.PY

### Donnees Exploitables Immediatement
| Famille | Donnees | Variable/Collection | Utilisation |
|---------|---------|---------------------|-------------|
| F1 | Waypoints | `territory_waypoints` | Points d'analyse |
| F1 | Layers BIONIC | `BIONIC_LAYERS` | Scores par zone |
| F2 | NDVI, Canopy | `habitat_variables.json` | Score vegetation |
| F4 | Elevation, Slope | `habitat_variables.json` | Score terrain |
| F5 | Temperature, Vent | `weather_engine` | Score meteo |
| F8 | Distance routes | `habitat_variables.json` | Score pression |
| F12 | Cycles saisonniers | `SEASON_FACTORS` | Multiplicateur |

### Donnees a Integrer (P1)
| Famille | Donnees | Source | Priorite |
|---------|---------|--------|----------|
| F1 | Polygones ZEC | MFFP | P1 |
| F2 | Ecotones | Derive satellite | P1 |
| F6 | Corridors detectes | Cameras | P1 |
| F10 | Historique recolte | MFFP | P1 |

### Donnees a Creer (Nouveau Pipeline)
| Famille | Donnees | Methode | Priorite |
|---------|---------|---------|----------|
| F5 | Microclimats | Modele topo | P0 |
| F8 | Pression cumulative | Agregation interne | P0 |
| F11 | Patterns cameras | Agregation | P0 |

## BEHAVIORAL_MODELS.PY

### Donnees Exploitables Immediatement
| Famille | Donnees | Variable/Collection | Utilisation |
|---------|---------|---------------------|-------------|
| F3 | Food sources | `species/*.json` | Zones alimentation |
| F6 | Movement patterns | `wildlife_behavior_engine` | Corridors |
| F7 | Bedding areas | `wildlife_behavior_engine` | Zones repos |
| F12 | Activity patterns | `SPECIES_PATTERNS` | Horaires |
| F12 | Seasonal behavior | `SeasonalBehavior` | Comportement |

### Donnees a Integrer (P1)
| Famille | Donnees | Source | Priorite |
|---------|---------|--------|----------|
| F6 | Corridors valides terrain | Louis Gagnon | P1 |
| F7 | Ravages officiels | MFFP | P1 |
| F12 | Dates rut regionales | UQAR | P1 |

### Donnees a Creer (Nouveau Pipeline)
| Famille | Donnees | Methode | Priorite |
|---------|---------|---------|----------|
| F11 | Classification especes | GPT-5.2 Vision | P0 |
| F11 | Patterns temporels | Agregation cameras | P0 |

---

# SYNTHESE EXECUTIVE

## METRIQUES GLOBALES

| Metrique | Valeur |
|----------|--------|
| **Familles de donnees** | 12 |
| **Variables d'habitat** | 17 |
| **Especes documentees** | 4 (moose, deer, bear, elk) |
| **Sources scientifiques** | 11 |
| **Collections MongoDB** | 15+ |
| **Layers cartographiques** | 15 |
| **Endpoints API existants** | 80+ |

## MATRICE DE COUVERTURE

| Famille | Existant | Manquant | A Acquerir | Score |
|---------|----------|----------|------------|-------|
| F1 Territoriales | 70% | 20% | 10% | **HAUTE** |
| F2 Vegetation | 60% | 25% | 15% | **MOYENNE** |
| F3 Alimentation | 50% | 35% | 15% | **MOYENNE** |
| F4 Topographie | 75% | 15% | 10% | **HAUTE** |
| F5 Microclimats | 55% | 30% | 15% | **MOYENNE** |
| F6 Corridors | 40% | 45% | 15% | **BASSE** |
| F7 Repos/Abris | 45% | 40% | 15% | **BASSE** |
| F8 Pression | 50% | 35% | 15% | **MOYENNE** |
| F9 Extremes | 60% | 25% | 15% | **MOYENNE** |
| F10 Historiques | 30% | 50% | 20% | **BASSE** |
| F11 Cameras | 35% | 50% | 15% | **BASSE** |
| F12 Cycles | 70% | 20% | 10% | **HAUTE** |

## PRIORITES P0 - ACTIONS IMMEDIATES

### 1. BLOQUEURS CRITIQUES
| Action | Famille | Impact | Effort |
|--------|---------|--------|--------|
| Classifier especes cameras | F11 | CRITIQUE | Moyen (GPT-5.2) |
| Calculer microclimats | F5 | CRITIQUE | Faible (formules) |
| Agreger pression cumulative | F8 | CRITIQUE | Faible (MongoDB) |
| Detecter corridors cameras | F6 | CRITIQUE | Moyen (algorithme) |

### 2. INTEGRATIONS PRIORITAIRES
| Source | Donnees | Famille | Effort |
|--------|---------|---------|--------|
| MFFP | Polygones ZEC | F1 | Moyen |
| MFFP | Ravages | F7 | Moyen |
| UQAR | Comportements | F6, F7, F12 | Faible |
| Louis Gagnon | Expertise terrain | Toutes | Moyen |

### 3. PIPELINES A CREER
| Pipeline | Input | Output | Priorite |
|----------|-------|--------|----------|
| Camera Classifier | Photos brutes | Espece + confiance | P0 |
| Microclimate Engine | DEM + Meteo | Score thermique | P0 |
| Pressure Calculator | Sorties + Waypoints | Score pression | P0 |
| Corridor Detector | GPS cameras | Lignes corridors | P0 |

## RISQUES IDENTIFIES

| Risque | Probabilite | Impact | Mitigation |
|--------|-------------|--------|------------|
| Couverture donnees incomplete | Moyenne | Haut | Modeles predictifs, fallbacks |
| Latence APIs externes | Haute | Moyen | Cache agressif, fallbacks |
| Biais echantillonnage | Haute | Moyen | Ponderation spatiale |
| Qualite photos cameras | Moyenne | Moyen | Pre-traitement, seuils |
| Changement reglementation | Basse | Haut | MAJ trimestrielle sources |

---

# NORMALISATION DES PONDERATIONS (Version 1.2.0)

## HIERARCHIE OFFICIELLE DES FACTEURS

### Niveau 1 - CRITIQUE (Override Absolu)
Ces facteurs ANNULENT ou DOMINENT tous les autres quand actifs.

| Facteur | Condition Declenchement | Action | Priorite |
|---------|------------------------|--------|----------|
| **F9 - Conditions Extremes** | temp < -30C OU temp > 32C OU vent > 60km/h | Override all, survival_mode | 1 |
| **F8 - Pression Extreme** | IPC > 80 | Override habitat, avoidance_mode | 2 |
| **Bear Hibernation** | species=bear AND month IN [12,1,2,3] | score = 0, no_calculation | 1 |

### Niveau 2 - PRIMAIRE (Facteurs Dominants)
Poids de base eleves, ajustables selon contexte.

| Facteur | Poids Base | Module | Ajustement Contextuel |
|---------|------------|--------|----------------------|
| **F12 - Cycles Temporels** | 0.25 | PT + BM | +50% si rut_period |
| **F5 - Microclimats** | 0.20 | PT | +30% si extreme_temp |
| **F2 - Vegetation/Habitat** | 0.20 | PT + BM | Standard |

### Niveau 3 - SECONDAIRE (Facteurs Modulateurs)
Poids moderes, modifient le score final.

| Facteur | Poids Base | Module | Condition Elevation |
|---------|------------|--------|---------------------|
| **F8 - Pression Chasse** | 0.15 | PT + BM | +66% si IPC > 60 |
| **F5 - Weather** | 0.15 | PT | +100% si extreme |
| **F1 - Territoriales** | 0.10 | PT | Standard |

### Niveau 4 - VALIDATION (Facteurs Confirmatoires)
Poids faibles, confirment ou ajustent.

| Facteur | Poids Base | Module | Role |
|---------|------------|--------|------|
| **F11 - Cameras** | 0.10 | BM | Validation patterns |
| **F10 - Historiques** | 0.10 | PT | Baseline regional |
| **F3 - Alimentation** | 0.05 | BM | Contexte saisonnier |

---

## REGLES D'ARBITRAGE EN CAS DE CONFLIT

### Matrice de Priorite

| Conflit | Gagnant | Perdant | Justification |
|---------|---------|---------|---------------|
| Meteo extreme vs Habitat optimal | F9 | F2 | Survie > Confort |
| Pression elevee vs Zone ideale | F8 | F1/F2 | Evitement > Attractivite |
| Rut vs Mauvais temps | F12 | F5 | Reproduction > Confort |
| Camera observations vs Modele | F11 | F12 | Observations > Predictions |
| Historique vs Temps reel | Temps reel | F10 | Actualite > Baseline |
| Cycles horaires vs Cycles hebdo | F12-horaire | F12-hebdo | Precision > Tendance |

### Algorithme de Resolution

```python
def resolve_conflict(factor_a: Factor, factor_b: Factor) -> Factor:
    """
    Resolution de conflit entre deux facteurs.
    
    Regle 1: Niveau hierarchique le plus eleve gagne
    Regle 2: A niveau egal, facteur avec confiance > 0.8 gagne
    Regle 3: A confiance egale, facteur avec source primaire gagne
    Regle 4: Sinon, moyenne ponderee des deux
    """
    
    # Regle 1: Niveau hierarchique
    if factor_a.level < factor_b.level:  # 1 = plus prioritaire
        return factor_a
    elif factor_b.level < factor_a.level:
        return factor_b
    
    # Regle 2: Confiance
    if factor_a.confidence > 0.8 and factor_b.confidence <= 0.8:
        return factor_a
    elif factor_b.confidence > 0.8 and factor_a.confidence <= 0.8:
        return factor_b
    
    # Regle 3: Source primaire
    if factor_a.source_type == "primary" and factor_b.source_type != "primary":
        return factor_a
    elif factor_b.source_type == "primary" and factor_a.source_type != "primary":
        return factor_b
    
    # Regle 4: Moyenne ponderee
    return weighted_average(factor_a, factor_b)
```

---

## NORMALISATION DES POIDS

### Formule de Normalisation

```python
def normalize_weights(weights: Dict[str, float], available_sources: List[str]) -> Dict[str, float]:
    """
    Normalisation dynamique des poids selon disponibilite des sources.
    
    1. Filtrer poids des sources indisponibles
    2. Redistribuer proportionnellement aux sources disponibles
    3. Appliquer contraintes (min/max par facteur)
    4. Verifier somme = 1.0
    """
    
    # Filtrer indisponibles
    active_weights = {k: v for k, v in weights.items() if k in available_sources}
    
    # Redistribuer
    total = sum(active_weights.values())
    normalized = {k: v / total for k, v in active_weights.items()}
    
    # Contraintes
    MIN_WEIGHT = 0.05
    MAX_WEIGHT = 0.40
    
    for k, v in normalized.items():
        normalized[k] = max(MIN_WEIGHT, min(MAX_WEIGHT, v))
    
    # Re-normaliser
    total = sum(normalized.values())
    normalized = {k: v / total for k, v in normalized.items()}
    
    return normalized
```

### Exemple de Normalisation

| Scenario | Sources Actives | Poids Original | Poids Normalise |
|----------|-----------------|----------------|-----------------|
| **Complet** | Toutes | habitat:0.25, weather:0.20, temporal:0.20, pressure:0.15, micro:0.10, historical:0.10 | Inchange |
| **Sans meteo** | -weather | habitat:0.25, temporal:0.20, pressure:0.15, micro:0.10, historical:0.10 | habitat:0.31, temporal:0.25, pressure:0.19, micro:0.12, historical:0.13 |
| **Sans historique** | -historical | Autres | +2.5% chaque autre facteur |
| **Minimum** | habitat, temporal | habitat:0.50, temporal:0.50 | Maximum possible avec 2 facteurs |

---

## PONDERATIONS DYNAMIQUES PAR CONTEXTE

### Contexte: PERIODE RUT

| Facteur | Poids Normal | Poids Rut | Delta |
|---------|--------------|-----------|-------|
| F12 Cycles | 0.20 | 0.30 | +50% |
| F8 Pression | 0.15 | 0.10 | -33% |
| F2 Habitat | 0.20 | 0.25 | +25% |
| Autres | - | - | Redistribue |

### Contexte: CONDITIONS EXTREMES

| Facteur | Poids Normal | Poids Extreme | Delta |
|---------|--------------|---------------|-------|
| F5 Weather | 0.15 | 0.35 | +133% |
| F9 Extremes | 0.05 | 0.20 | +300% |
| F2 Habitat | 0.20 | 0.15 | -25% |
| Autres | - | - | Redistribue |

### Contexte: HAUTE PRESSION CHASSE

| Facteur | Poids Normal | Poids Haute Pression | Delta |
|---------|--------------|---------------------|-------|
| F8 Pression | 0.15 | 0.30 | +100% |
| F7 Repos/Abris | 0.10 | 0.15 | +50% |
| F12 Cycles | 0.20 | 0.15 | -25% |
| Autres | - | - | Redistribue |

---

## INTEGRATION DANS MODULES P0

### predictive_territorial.py

```python
# Configuration des poids P0
PT_WEIGHTS_CONFIG = {
    "base": {
        "habitat_quality": 0.25,
        "weather_conditions": 0.20,
        "temporal_alignment": 0.20,
        "pressure_index": 0.15,
        "microclimate": 0.10,
        "historical_baseline": 0.10
    },
    "constraints": {
        "min_weight": 0.05,
        "max_weight": 0.40,
        "sum_tolerance": 0.01
    },
    "arbitrage": {
        "extreme_weather_threshold": {"temp_min": -30, "temp_max": 32, "wind_max": 60},
        "high_pressure_threshold": 80,
        "rut_boost_factor": 1.5
    }
}
```

### behavioral_models.py

```python
# Configuration des poids P0
BM_WEIGHTS_CONFIG = {
    "base": {
        "temporal_pattern": 0.30,
        "habitat_suitability": 0.25,
        "weather_influence": 0.20,
        "pressure_influence": 0.15,
        "camera_validation": 0.10
    },
    "constraints": {
        "min_weight": 0.05,
        "max_weight": 0.45,
        "sum_tolerance": 0.01
    },
    "arbitrage": {
        "rut_temporal_boost": 1.33,
        "extreme_weather_boost": 1.75,
        "high_pressure_boost": 1.67,
        "hibernation_zero": ["bear"]
    }
}
```

---

## RECOMMANDATIONS

### POUR PREDICTIVE_TERRITORIAL.PY
1. Commencer avec les 5 variables d'habitat les plus documentees (NDVI, canopy, elevation, slope, water_proximity)
2. Implementer le calcul de microclimats comme premiere extension
3. Integrer les sources gouvernementales (MFFP) en priorite

### POUR BEHAVIORAL_MODELS.PY
1. S'appuyer sur les patterns d'activite existants (`SPECIES_PATTERNS`)
2. Prioriser la detection d'especes sur photos cameras
3. Valider avec les donnees de Louis Gagnon avant production

### ARCHITECTURE RECOMMANDEE
```
bionic_engine/
├── core.py                    # Orchestrateur
├── contracts/                 # Interfaces
│   ├── data_contracts.py
│   └── api_contracts.py
├── modules/
│   ├── predictive_territorial.py    # P0
│   ├── behavioral_models.py         # P0
│   ├── camera_classifier.py         # P0
│   ├── microclimate_engine.py       # P0
│   └── pressure_calculator.py       # P0
├── data/
│   └── (donnees statiques)
└── tests/
    └── (tests unitaires G-QA)
```

---

# COMPLEMENTS CRITIQUES P0 (Version 1.1.0)

Les 4 blocs suivants constituent les specifications detaillees requises
pour la validation GO des modules P0.

---

## BLOC CRITIQUE 1: AGREGATS CAMERAS AVANCES

### 1.1 STRUCTURE EXACTE DES DONNEES CAMERAS

#### Schema CameraAggregation
```python
class CameraAggregation:
    """Structure d'agregation pour analyse predictive"""
    
    # Identifiants
    camera_id: str              # ID unique camera
    waypoint_id: str            # OBLIGATOIRE - point d'ancrage
    zone_id: str                # Zone de 1km2 englobante
    
    # Periode d'agregation
    aggregation_period: str     # "hourly" | "daily" | "weekly" | "monthly"
    start_timestamp: datetime
    end_timestamp: datetime
    
    # Comptages par espece
    species_counts: Dict[str, SpeciesCount]
    # Ex: {"moose": SpeciesCount, "deer": SpeciesCount, ...}
    
    # Metriques temporelles
    detection_hours: List[int]      # Heures avec detections [5,6,7,17,18,19]
    peak_hour: int                  # Heure de pic d'activite
    activity_distribution: Dict[str, float]  # {"dawn": 0.35, "day": 0.15, "dusk": 0.40, "night": 0.10}
    
    # Metriques de qualite
    total_photos: int
    valid_detections: int
    false_positives: int
    confidence_avg: float           # Score moyen confiance IA
    
    # Metadonnees
    last_updated: datetime
    data_quality_score: float       # 0-1

class SpeciesCount:
    """Comptage par espece"""
    species_id: str
    common_name_fr: str
    total_detections: int
    unique_individuals_estimate: int  # Estimation via features distinctifs
    confidence_avg: float
    hourly_distribution: Dict[int, int]  # {5: 12, 6: 8, 17: 15, ...}
    behavioral_tags: List[str]      # ["feeding", "traveling", "resting"]
```

### 1.2 REGLES DE FUSION TEMPORELLE

| Periode | Fenetre | Methode Fusion | Cas d'Usage |
|---------|---------|----------------|-------------|
| **Horaire** | 60 min | Comptage simple | Analyse temps reel |
| **Quotidien** | 24h (00:00-23:59) | Somme + Max(confidence) | Patterns journaliers |
| **Hebdomadaire** | Lundi-Dimanche | Moyenne ponderee par jour | Tendances court terme |
| **Mensuel** | 1er-dernier jour | Mediane + variance | Analyse saisonniere |

#### Algorithme de Fusion
```python
def aggregate_detections(events: List[CameraEvent], period: str) -> CameraAggregation:
    """
    Regle 1: Deduplication - 2 detections meme espece < 5 min = 1 individu
    Regle 2: Confiance - Ignorer detections < 0.60 confiance
    Regle 3: Nuit - Penalite -20% confiance pour photos IR (qualite moindre)
    Regle 4: Multi-individus - Si > 1 animal visible, comptage individuel
    """
    
    # Fenetre de deduplication par espece
    DEDUP_WINDOW_MINUTES = 5
    
    # Seuil de confiance minimum
    MIN_CONFIDENCE = 0.60
    
    # Penalite photos nocturnes
    NIGHT_PENALTY = 0.20
    
    # Implementation...
```

### 1.3 PONDERATIONS PAR ESPECE

| Espece | Poids Base | Ajust. Nocturne | Ajust. Saisonnier | Fiabilite Detection |
|--------|------------|-----------------|-------------------|---------------------|
| **Orignal** | 1.0 | -15% (moins actif nuit) | +30% Oct-Nov (rut) | 0.92 |
| **Cerf** | 1.0 | +10% (crepusculaire) | +25% Nov (rut) | 0.88 |
| **Ours** | 0.8 | -30% (diurne) | -100% Dec-Mar (hibernation) | 0.85 |
| **Dindon** | 0.9 | -80% (strictement diurne) | +20% Avril-Mai (reproduction) | 0.90 |

#### Formule de Score Agrege
```python
def calculate_camera_zone_score(aggregation: CameraAggregation, species: str, date: datetime) -> float:
    """
    Score = (detections_norm * poids_espece * ajust_saisonnier * confiance_avg) / jours_periode
    
    Normalisation: detections_norm = min(detections / 10, 1.0)
    Resultat: Score 0-100
    """
    base_score = aggregation.species_counts[species].total_detections
    normalized = min(base_score / 10, 1.0)
    
    weight = SPECIES_WEIGHTS[species]["base"]
    seasonal = get_seasonal_adjustment(species, date.month)
    confidence = aggregation.species_counts[species].confidence_avg
    
    return (normalized * weight * seasonal * confidence) * 100
```

### 1.4 LIMITES ET CAS EXTREMES

| Cas Extreme | Description | Traitement |
|-------------|-------------|------------|
| **Zero detections** | Aucune photo sur periode | Score = 0, flag "no_data" |
| **Camera defaillante** | > 7 jours sans photo | Exclusion agregation, alerte utilisateur |
| **Saturation** | > 100 photos/jour | Echantillonnage aleatoire 100 photos |
| **Faux positifs eleves** | > 30% faux positifs | Flag "low_quality", confiance /2 |
| **Espece non reconnue** | Detection sans classification | Categorie "unknown", score = 0 |
| **Multi-cameras meme zone** | Plusieurs cameras < 500m | Fusion en agregation unique, deduplication croisee |
| **Conditions extremes** | Neige, buee, contre-jour | Pre-traitement image, flag qualite |

---

## BLOC CRITIQUE 2: MICROCLIMATS ET ZONES THERMIQUES

### 2.1 METHODE DE CALCUL

#### Formule Principale - Indice Microclimatique (IMC)
```python
def calculate_microclimate_index(
    lat: float, 
    lng: float, 
    elevation: float,
    slope: float,
    aspect: float,  # 0-360 degres
    canopy_cover: float,
    base_temperature: float,
    wind_speed: float,
    date: datetime
) -> MicroclimateIndex:
    """
    IMC = T_base + Delta_elev + Delta_aspect + Delta_canopy + Delta_wind
    
    Composantes:
    - T_base: Temperature station meteo la plus proche
    - Delta_elev: Gradient adiabatique (-6.5C / 1000m)
    - Delta_aspect: Effet exposition solaire (-3C a +3C)
    - Delta_canopy: Effet couvert forestier (-2C a +2C)
    - Delta_wind: Effet refroidissement eolien (formule windchill)
    """
    
    # Gradient adiabatique
    elevation_ref = 200  # Elevation moyenne stations meteo Quebec
    delta_elev = -0.0065 * (elevation - elevation_ref)
    
    # Effet exposition (aspect)
    delta_aspect = calculate_aspect_effect(aspect, date, lat)
    
    # Effet canopee
    delta_canopy = calculate_canopy_effect(canopy_cover, base_temperature)
    
    # Effet vent (windchill simplifie)
    delta_wind = calculate_wind_chill_effect(wind_speed, base_temperature)
    
    imc = base_temperature + delta_elev + delta_aspect + delta_canopy + delta_wind
    
    return MicroclimateIndex(
        temperature_estimated=imc,
        components={
            "base": base_temperature,
            "elevation": delta_elev,
            "aspect": delta_aspect,
            "canopy": delta_canopy,
            "wind": delta_wind
        },
        confidence=calculate_confidence(sources_available)
    )

def calculate_aspect_effect(aspect: float, date: datetime, lat: float) -> float:
    """
    Exposition Sud (+) vs Nord (-) selon saison
    
    Ete (mai-aout): Sud = +1.5C, Nord = -1.0C
    Hiver (nov-fev): Sud = +3.0C, Nord = -2.0C
    Transitions: Interpolation lineaire
    """
    month = date.month
    
    # Angle solaire effectif
    solar_factor = math.cos(math.radians(aspect - 180))  # Max pour Sud (180)
    
    # Amplitude saisonniere
    if month in [11, 12, 1, 2]:  # Hiver
        amplitude = 2.5
    elif month in [5, 6, 7, 8]:  # Ete
        amplitude = 1.25
    else:  # Transitions
        amplitude = 1.75
    
    return solar_factor * amplitude

def calculate_canopy_effect(canopy_cover: float, temp: float) -> float:
    """
    Couvert forestier:
    - Ete chaud (>25C): Effet rafraichissant (-2C pour 100% couvert)
    - Hiver froid (<0C): Effet isolant (+1.5C pour 100% couvert)
    """
    cover_factor = canopy_cover / 100
    
    if temp > 25:
        return -2.0 * cover_factor
    elif temp < 0:
        return 1.5 * cover_factor
    else:
        # Interpolation
        return ((temp - 25) / 25 * 3.5 - 2.0) * cover_factor
```

### 2.2 RESOLUTION SPATIALE

| Niveau | Resolution | Source Principale | Cas d'Usage |
|--------|------------|-------------------|-------------|
| **Macro** | 10 km | Stations meteo officielles | Baseline regional |
| **Meso** | 1 km | Interpolation + DEM 30m | Analyse zone chasse |
| **Micro** | 100 m | LiDAR + modele local | Precision waypoint |
| **Ultra-micro** | 10 m | Extrapolation (faible confiance) | Recherche |

#### Grille de Calcul
```python
MICROCLIMATE_GRID = {
    "cell_size_m": 100,           # Resolution de base
    "interpolation": "kriging",   # Methode spatiale
    "dem_source": "SRTM_30m",     # Ou LiDAR si disponible
    "canopy_source": "Sentinel2_NDVI",
    "weather_stations_radius_km": 50  # Rayon recherche stations
}
```

### 2.3 FREQUENCE DE MISE A JOUR

| Composante | Frequence MAJ | Declencheur | Latence Max |
|------------|---------------|-------------|-------------|
| **Temperature base** | 1 heure | API meteo | 5 min |
| **Vent** | 1 heure | API meteo | 5 min |
| **Aspect/Slope** | Statique | - | - |
| **Elevation** | Statique | - | - |
| **Canopy cover** | Saisonnier | Changement NDVI > 0.1 | 1 semaine |
| **Score IMC final** | 1 heure | Recalcul complet | 10 min |

### 2.4 SOURCES DE DONNEES

| Donnee | Source Primaire | Source Backup | Fiabilite |
|--------|-----------------|---------------|-----------|
| **DEM** | Quebec LiDAR (1m) | SRTM NASA (30m) | 0.98 / 0.85 |
| **Temperature** | Environment Canada | Open-Meteo | 0.95 / 0.85 |
| **Vent** | Environment Canada | Open-Meteo | 0.92 / 0.82 |
| **Canopy** | LiDAR provincial | Sentinel-2 NDVI | 0.90 / 0.80 |
| **Aspect/Slope** | Derive DEM | - | 0.95 |

### 2.5 ZONES THERMIQUES - CLASSIFICATION

| Zone | Plage IMC (hiver) | Plage IMC (ete) | Impact Faune |
|------|-------------------|-----------------|--------------|
| **Refuge chaud** | > -5C vs baseline | < 25C | Attractif orignal hiver |
| **Confort** | -10C a -5C | 15-25C | Activite normale |
| **Stress modere** | -20C a -10C | 25-30C | Reduction activite |
| **Stress severe** | < -20C | > 30C | Deplacement force |

---

## BLOC CRITIQUE 3: PRESSION DE CHASSE ET DERANGEMENT

### 3.1 GRANULARITE

| Niveau | Echelle Spatiale | Echelle Temporelle | Precision |
|--------|------------------|-------------------|-----------|
| **Zone** | Cellule 1 km2 | Journalier | Haute |
| **Secteur** | 5 km2 | Hebdomadaire | Moyenne |
| **Region** | ZEC/Pourvoirie complete | Mensuel | Basse |
| **Province** | Quebec sud/nord | Saisonnier | Tres basse |

### 3.2 SOURCES DE DONNEES

| Source | Donnee | Disponibilite | Fiabilite | Integration |
|--------|--------|---------------|-----------|-------------|
| **HUNTIQ interne** | Sorties utilisateurs | Temps reel | 0.95 | INTEGREE |
| **SEPAQ** | Frequentation reserves | Mensuel (decale) | 0.90 | A INTEGRER |
| **ZECs** | Enregistrements chasseurs | Annuel | 0.85 | A INTEGRER |
| **MFFP** | Statistiques recolte | Annuel | 0.95 | A INTEGRER |
| **Strava Heatmap** | Activites recreatives | Mensuel | 0.70 | A INTEGRER |
| **Cameras trail** | Passages humains detectes | Temps reel | 0.80 | INTEGREE |

### 3.3 FREQUENCE DE MISE A JOUR

| Metrique | Frequence | Methode |
|----------|-----------|---------|
| **Pression instantanee** | Temps reel | Agregation sorties actives |
| **Pression quotidienne** | Fin de journee | Somme sorties jour |
| **Pression cumulative 7j** | Quotidien | Moyenne mobile 7 jours |
| **Pression saisonniere** | Hebdomadaire | Comparaison historique |
| **Baseline annuelle** | Annuel | Recalcul complet MFFP |

### 3.4 METHODE D'AGREGATION

```python
class PressureCalculator:
    """
    Calcul de l'indice de pression de chasse (IPC)
    Score 0-100: 0 = aucune pression, 100 = pression maximale
    """
    
    # Poids des sources
    WEIGHTS = {
        "huntiq_trips": 0.40,      # Sorties HUNTIQ (temps reel)
        "cameras_human": 0.20,     # Detections humaines cameras
        "historical_harvest": 0.20, # Historique recolte zone
        "recreational": 0.10,       # Activites recreatives
        "road_proximity": 0.10      # Proximite routes
    }
    
    # Seuils de normalisation
    THRESHOLDS = {
        "trips_per_km2_day": {
            "low": 0.5,    # < 0.5 sorties/km2/jour
            "medium": 2.0,  # 0.5-2.0
            "high": 5.0     # > 5.0
        },
        "human_detections_per_week": {
            "low": 5,
            "medium": 20,
            "high": 50
        }
    }
    
    def calculate_pressure_index(
        self, 
        zone_id: str, 
        date: datetime,
        lookback_days: int = 7
    ) -> PressureIndex:
        """
        IPC = sum(source_score * weight) pour toutes les sources
        
        Ajustements:
        - Jour de semaine: Weekend +30%
        - Periode saison: Ouverture +50%, Mi-saison 0%, Fin -20%
        - Meteo: Beau temps +20%, Mauvais temps -30%
        """
        
        scores = {}
        
        # 1. Sorties HUNTIQ dans la zone
        trips = self.get_zone_trips(zone_id, date, lookback_days)
        trips_per_km2 = trips / self.get_zone_area(zone_id)
        scores["huntiq_trips"] = self.normalize_trips(trips_per_km2)
        
        # 2. Detections humaines cameras
        human_detections = self.get_human_detections(zone_id, lookback_days)
        scores["cameras_human"] = self.normalize_detections(human_detections)
        
        # 3. Historique recolte
        historical = self.get_historical_harvest_rate(zone_id)
        scores["historical_harvest"] = historical * 100
        
        # 4. Activites recreatives (si disponible)
        recreational = self.get_recreational_activity(zone_id)
        scores["recreational"] = recreational
        
        # 5. Proximite routes
        road_factor = self.get_road_pressure(zone_id)
        scores["road_proximity"] = road_factor
        
        # Agregation ponderee
        base_ipc = sum(scores[k] * self.WEIGHTS[k] for k in scores)
        
        # Ajustements temporels
        adjusted_ipc = self.apply_temporal_adjustments(base_ipc, date)
        
        return PressureIndex(
            zone_id=zone_id,
            date=date,
            score=min(100, max(0, adjusted_ipc)),
            components=scores,
            confidence=self.calculate_confidence(scores),
            trend=self.calculate_trend(zone_id, lookback_days)
        )
    
    def normalize_trips(self, trips_per_km2: float) -> float:
        """Normalisation 0-100"""
        if trips_per_km2 < self.THRESHOLDS["trips_per_km2_day"]["low"]:
            return trips_per_km2 / 0.5 * 25  # 0-25
        elif trips_per_km2 < self.THRESHOLDS["trips_per_km2_day"]["medium"]:
            return 25 + (trips_per_km2 - 0.5) / 1.5 * 25  # 25-50
        elif trips_per_km2 < self.THRESHOLDS["trips_per_km2_day"]["high"]:
            return 50 + (trips_per_km2 - 2.0) / 3.0 * 25  # 50-75
        else:
            return min(100, 75 + (trips_per_km2 - 5.0) / 5.0 * 25)  # 75-100
```

### 3.5 SEUILS COMPORTEMENTAUX

| IPC Score | Niveau | Impact Comportement Faune | Recommandation Chasseur |
|-----------|--------|--------------------------|-------------------------|
| **0-20** | Minimal | Comportement naturel | Zone ideale |
| **20-40** | Faible | Legerement mefiants, activite normale | Excellentes conditions |
| **40-60** | Modere | Deplacement vers zones moins pressees | Bonnes conditions, patience |
| **60-80** | Eleve | Activite reduite, nocturne accrue | Conditions difficiles |
| **80-100** | Extreme | Fuite, abandon temporaire zone | Deconseille, attendre |

#### Rayon d'Impact par Niveau
| Niveau IPC | Rayon Impact Direct | Rayon Impact Indirect |
|------------|--------------------|-----------------------|
| Minimal | 100m | 200m |
| Faible | 200m | 500m |
| Modere | 500m | 1km |
| Eleve | 1km | 2km |
| Extreme | 2km | 5km |

### 3.6 PRESSION CUMULATIVE

```python
def calculate_cumulative_pressure(
    zone_id: str,
    end_date: datetime,
    lookback_days: int = 30
) -> CumulativePressure:
    """
    La pression cumulative tient compte de la "memoire" du gibier.
    
    Modele de decroissance:
    - Jour J: 100% impact
    - J-1: 80% impact
    - J-3: 50% impact
    - J-7: 25% impact
    - J-14: 10% impact
    - J-30: 5% impact
    
    Formule: PC = sum(IPC_jour * decay_factor) / sum(decay_factors)
    """
    
    DECAY_CURVE = {
        0: 1.00,   # Aujourd'hui
        1: 0.80,
        2: 0.65,
        3: 0.50,
        4: 0.40,
        5: 0.32,
        6: 0.26,
        7: 0.25,
        14: 0.10,
        30: 0.05
    }
    
    daily_pressures = []
    for days_ago in range(lookback_days):
        date = end_date - timedelta(days=days_ago)
        ipc = get_daily_pressure(zone_id, date)
        decay = interpolate_decay(days_ago, DECAY_CURVE)
        daily_pressures.append((ipc, decay))
    
    weighted_sum = sum(ipc * decay for ipc, decay in daily_pressures)
    total_weight = sum(decay for _, decay in daily_pressures)
    
    cumulative = weighted_sum / total_weight
    
    return CumulativePressure(
        zone_id=zone_id,
        score=cumulative,
        lookback_days=lookback_days,
        trend="increasing" if is_increasing(daily_pressures) else "decreasing",
        recovery_estimate_days=estimate_recovery(cumulative)
    )
```

---

## BLOC CRITIQUE 4: CYCLES TEMPORELS AVANCES

### 4.1 CYCLES HORAIRES PAR ESPECE

#### Structure des Patterns Horaires
```python
HOURLY_ACTIVITY_PATTERNS = {
    "moose": {
        # Score d'activite par heure (0-100)
        "hourly_scores": {
            0: 15, 1: 12, 2: 10, 3: 8, 4: 10,
            5: 45, 6: 85, 7: 95, 8: 75, 9: 45,
            10: 25, 11: 18, 12: 15, 13: 18, 14: 22,
            15: 35, 16: 55, 17: 85, 18: 92, 19: 70,
            20: 45, 21: 30, 22: 22, 23: 18
        },
        # Probabilites par type d'activite
        "activity_probabilities": {
            "dawn": {"feeding": 0.65, "traveling": 0.25, "resting": 0.05, "other": 0.05},
            "day": {"feeding": 0.15, "traveling": 0.10, "resting": 0.70, "other": 0.05},
            "dusk": {"feeding": 0.60, "traveling": 0.30, "resting": 0.05, "other": 0.05},
            "night": {"feeding": 0.20, "traveling": 0.15, "resting": 0.60, "other": 0.05}
        },
        # Ajustements saisonniers des heures de pic
        "seasonal_shift": {
            "summer": {"dawn_shift": -30, "dusk_shift": +60},  # minutes
            "winter": {"dawn_shift": +60, "dusk_shift": -90},
            "rut": {"activity_boost": 1.5, "nocturnal_increase": 0.3}
        }
    },
    "deer": {
        "hourly_scores": {
            0: 25, 1: 20, 2: 18, 3: 15, 4: 18,
            5: 55, 6: 90, 7: 95, 8: 70, 9: 40,
            10: 22, 11: 15, 12: 12, 13: 15, 14: 20,
            15: 35, 16: 60, 17: 88, 18: 95, 19: 75,
            20: 50, 21: 35, 22: 28, 23: 25
        },
        "activity_probabilities": {
            "dawn": {"feeding": 0.70, "traveling": 0.20, "resting": 0.05, "other": 0.05},
            "day": {"feeding": 0.10, "traveling": 0.10, "resting": 0.75, "other": 0.05},
            "dusk": {"feeding": 0.65, "traveling": 0.25, "resting": 0.05, "other": 0.05},
            "night": {"feeding": 0.30, "traveling": 0.20, "resting": 0.45, "other": 0.05}
        },
        "seasonal_shift": {
            "summer": {"dawn_shift": -45, "dusk_shift": +45},
            "winter": {"dawn_shift": +45, "dusk_shift": -60},
            "rut": {"activity_boost": 1.8, "nocturnal_increase": 0.4, "diurnal_increase": 0.3}
        }
    },
    "bear": {
        "hourly_scores": {
            0: 5, 1: 3, 2: 2, 3: 2, 4: 3,
            5: 25, 6: 55, 7: 80, 8: 85, 9: 75,
            10: 60, 11: 45, 12: 35, 13: 40, 14: 50,
            15: 65, 16: 75, 17: 80, 18: 70, 19: 45,
            20: 25, 21: 12, 22: 8, 23: 5
        },
        "hibernation_months": [12, 1, 2, 3],  # Score = 0 ces mois
        "hyperphagia_months": [9, 10, 11],    # +40% activite
        "activity_probabilities": {
            "dawn": {"feeding": 0.55, "traveling": 0.35, "resting": 0.05, "other": 0.05},
            "day": {"feeding": 0.45, "traveling": 0.30, "resting": 0.20, "other": 0.05},
            "dusk": {"feeding": 0.50, "traveling": 0.35, "resting": 0.10, "other": 0.05},
            "night": {"feeding": 0.10, "traveling": 0.10, "resting": 0.75, "other": 0.05}
        }
    },
    "wild_turkey": {
        "hourly_scores": {
            0: 0, 1: 0, 2: 0, 3: 0, 4: 0,
            5: 15, 6: 75, 7: 95, 8: 85, 9: 70,
            10: 55, 11: 45, 12: 35, 13: 40, 14: 50,
            15: 60, 16: 70, 17: 75, 18: 50, 19: 15,
            20: 0, 21: 0, 22: 0, 23: 0
        },
        # Strictement diurne
        "roosting_hours": [0,1,2,3,4,5,19,20,21,22,23],
        "activity_probabilities": {
            "dawn": {"feeding": 0.60, "traveling": 0.30, "displaying": 0.05, "other": 0.05},
            "day": {"feeding": 0.50, "traveling": 0.25, "resting": 0.20, "other": 0.05},
            "dusk": {"feeding": 0.70, "traveling": 0.20, "resting": 0.05, "other": 0.05}
        }
    }
}
```

### 4.2 CYCLES HEBDOMADAIRES

| Jour | Pression Chasse Typique | Ajustement Score | Raison |
|------|------------------------|------------------|--------|
| **Lundi** | Basse | +10% activite | Recuperation weekend |
| **Mardi** | Basse | +10% activite | Calme |
| **Mercredi** | Basse | +8% activite | Calme |
| **Jeudi** | Basse-Moyenne | +5% activite | Pre-weekend |
| **Vendredi** | Moyenne | 0% | Arrivees chasseurs |
| **Samedi** | Haute | -20% activite | Pic pression |
| **Dimanche** | Haute | -15% activite | Pression maintenue |

```python
WEEKLY_MODIFIERS = {
    0: 1.10,  # Lundi
    1: 1.10,  # Mardi
    2: 1.08,  # Mercredi
    3: 1.05,  # Jeudi
    4: 1.00,  # Vendredi
    5: 0.80,  # Samedi
    6: 0.85   # Dimanche
}

def apply_weekly_modifier(base_score: float, date: datetime) -> float:
    return base_score * WEEKLY_MODIFIERS[date.weekday()]
```

### 4.3 CYCLES COMBINES (METEO x HABITAT x SAISON)

#### Matrice d'Interaction 3D
```python
class CombinedCycleEngine:
    """
    Score Final = Score_Base * Mod_Meteo * Mod_Habitat * Mod_Saison * Mod_Temporel
    
    Interactions non-lineaires:
    - Chaleur + Foret dense = Refuge (bonus)
    - Froid + Zone ouverte = Stress (malus)
    - Rut + Pression faible = Activite maximale
    - Mauvais temps + Ouverture saison = Opportunite
    """
    
    def calculate_combined_score(
        self,
        species: str,
        datetime_target: datetime,
        location: Coordinates,
        weather: WeatherData,
        habitat: HabitatData
    ) -> CombinedScore:
        
        # Scores de base
        hourly = self.get_hourly_score(species, datetime_target.hour)
        seasonal = self.get_seasonal_score(species, datetime_target)
        weekly = self.get_weekly_modifier(datetime_target)
        
        # Modificateurs environnementaux
        weather_mod = self.calculate_weather_modifier(species, weather)
        habitat_mod = self.calculate_habitat_modifier(species, habitat, datetime_target)
        
        # Interactions
        interaction_mod = self.calculate_interactions(
            species, weather, habitat, datetime_target
        )
        
        # Score final
        final = hourly * seasonal * weekly * weather_mod * habitat_mod * interaction_mod
        
        return CombinedScore(
            final_score=min(100, max(0, final)),
            components={
                "hourly": hourly,
                "seasonal": seasonal,
                "weekly": weekly,
                "weather": weather_mod,
                "habitat": habitat_mod,
                "interaction": interaction_mod
            },
            confidence=self.calculate_confidence(components),
            recommendation=self.generate_recommendation(final, components)
        )
    
    def calculate_interactions(
        self,
        species: str,
        weather: WeatherData,
        habitat: HabitatData,
        dt: datetime
    ) -> float:
        """
        Interactions connues empiriquement:
        """
        modifier = 1.0
        
        # 1. Chaleur + Foret dense = Orignal cherche refuge
        if species == "moose" and weather.temperature > 20 and habitat.canopy_cover > 70:
            modifier *= 1.3  # Bonus - probabilite elevee dans ces zones
        
        # 2. Froid + Zone ouverte = Stress thermique
        if weather.temperature < -15 and habitat.canopy_cover < 30:
            modifier *= 0.6  # Malus - evitement
        
        # 3. Pression baro descendante + Aube = Pic activite
        if weather.pressure_trend == "falling" and 5 <= dt.hour <= 8:
            modifier *= 1.25
        
        # 4. Vent fort + Zone boisee = Refuge auditif
        if weather.wind_speed > 25 and habitat.type in ["mixed_forest", "coniferous"]:
            modifier *= 1.15
        
        # 5. Rut + Temperature fraiche = Activite maximale
        if self.is_rut_period(species, dt) and 0 < weather.temperature < 10:
            modifier *= 1.4
        
        # 6. Nouvelle lune + Nuit = Activite nocturne accrue
        if self.get_moon_phase(dt) == "new" and (dt.hour < 5 or dt.hour > 20):
            modifier *= 1.2
        
        return modifier
```

### 4.4 PONDERATIONS DYNAMIQUES

#### Systeme de Poids Adaptatifs
```python
class DynamicWeightEngine:
    """
    Les ponderations s'ajustent selon:
    - Fiabilite des donnees sources
    - Validations terrain recentes
    - Saison et contexte
    """
    
    BASE_WEIGHTS = {
        "hourly_pattern": 0.25,
        "seasonal_factor": 0.20,
        "weather_impact": 0.20,
        "habitat_quality": 0.15,
        "pressure_index": 0.10,
        "lunar_cycle": 0.05,
        "weekly_pattern": 0.05
    }
    
    def get_dynamic_weights(
        self,
        species: str,
        datetime_target: datetime,
        data_availability: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Ajustement des poids selon:
        1. Disponibilite des donnees (poids redistribue si donnee manquante)
        2. Contexte saisonnier (rut augmente poids saison)
        3. Conditions extremes (meteo augmente poids weather)
        """
        weights = self.BASE_WEIGHTS.copy()
        
        # Ajustement pour donnees manquantes
        total_available = sum(
            weights[k] * data_availability.get(k, 0) 
            for k in weights
        )
        if total_available < 1.0:
            # Redistribuer aux sources disponibles
            for k in weights:
                if data_availability.get(k, 0) > 0.8:
                    weights[k] *= 1.0 / total_available
        
        # Contexte saisonnier
        if self.is_rut_period(species, datetime_target):
            weights["seasonal_factor"] *= 1.5
            weights["hourly_pattern"] *= 1.3
            # Renormaliser
            total = sum(weights.values())
            weights = {k: v/total for k, v in weights.items()}
        
        # Conditions meteo extremes
        weather = self.get_current_weather()
        if weather.is_extreme():
            weights["weather_impact"] *= 2.0
            total = sum(weights.values())
            weights = {k: v/total for k, v in weights.items()}
        
        return weights
    
    # Table de reference des ajustements saisonniers
    SEASONAL_WEIGHT_ADJUSTMENTS = {
        "pre_rut": {
            "seasonal_factor": 1.3,
            "habitat_quality": 1.2,  # Recherche zones rut
            "hourly_pattern": 1.1
        },
        "rut": {
            "seasonal_factor": 1.5,
            "hourly_pattern": 1.4,   # Activite diurne accrue
            "pressure_index": 0.7    # Moins sensibles pression
        },
        "post_rut": {
            "habitat_quality": 1.4,  # Recherche alimentation
            "weather_impact": 1.2    # Plus sensibles froid
        },
        "winter": {
            "weather_impact": 1.5,
            "habitat_quality": 1.3,  # Ravages
            "hourly_pattern": 0.8    # Patterns moins marques
        }
    }
```

### 4.5 CALENDRIER ANNUEL INTEGRE

```python
ANNUAL_CALENDAR = {
    "moose": {
        1: {"season": "winter", "activity_mod": 0.5, "behavior": "survival"},
        2: {"season": "winter", "activity_mod": 0.4, "behavior": "survival"},
        3: {"season": "late_winter", "activity_mod": 0.5, "behavior": "recovery"},
        4: {"season": "spring", "activity_mod": 0.7, "behavior": "feeding"},
        5: {"season": "spring", "activity_mod": 0.8, "behavior": "feeding"},
        6: {"season": "summer", "activity_mod": 0.7, "behavior": "feeding_aquatic"},
        7: {"season": "summer", "activity_mod": 0.6, "behavior": "heat_avoidance"},
        8: {"season": "late_summer", "activity_mod": 0.7, "behavior": "pre_rut"},
        9: {"season": "pre_rut", "activity_mod": 0.9, "behavior": "territorial"},
        10: {"season": "rut", "activity_mod": 1.0, "behavior": "breeding"},
        11: {"season": "post_rut", "activity_mod": 0.8, "behavior": "recovery_feeding"},
        12: {"season": "early_winter", "activity_mod": 0.6, "behavior": "yarding"}
    },
    "deer": {
        1: {"season": "winter", "activity_mod": 0.5, "behavior": "yarding"},
        2: {"season": "winter", "activity_mod": 0.5, "behavior": "yarding"},
        3: {"season": "late_winter", "activity_mod": 0.6, "behavior": "recovery"},
        4: {"season": "spring", "activity_mod": 0.75, "behavior": "feeding"},
        5: {"season": "spring", "activity_mod": 0.8, "behavior": "fawning"},
        6: {"season": "summer", "activity_mod": 0.7, "behavior": "nurturing"},
        7: {"season": "summer", "activity_mod": 0.6, "behavior": "heat_avoidance"},
        8: {"season": "late_summer", "activity_mod": 0.75, "behavior": "velvet_shed"},
        9: {"season": "early_fall", "activity_mod": 0.85, "behavior": "pre_rut"},
        10: {"season": "pre_rut", "activity_mod": 0.95, "behavior": "scraping"},
        11: {"season": "rut", "activity_mod": 1.0, "behavior": "breeding"},
        12: {"season": "post_rut", "activity_mod": 0.7, "behavior": "recovery"}
    }
}
```

---

# SOURCES EMPIRIQUES & SCIENTIFIQUES - EDITION COMPLETE

## ORGANISMES GOUVERNEMENTAUX (SOURCES PRIMAIRES)

### Canada

| ID | Organisme | Province | Donnees | Fiabilite | Statut | Potentiel P0 |
|----|-----------|----------|---------|-----------|--------|--------------|
| `melccfp_qc` | MELCCFP (ex-MFFP) | Quebec | Statistiques chasse, plans gestion, inventaires | 0.95 | PARTIELLEMENT INTEGRE | CRITIQUE |
| `mnrf_on` | Ontario MNRF | Ontario | Rapports biologiques, telemetrie | 0.93 | DISPONIBLE | P1 |
| `bc_wildlife` | BC Wildlife Branch | C-B | Inventaires aeriens, populations | 0.92 | DISPONIBLE | P2 |
| `ab_fish_wildlife` | Alberta Fish & Wildlife | Alberta | Etudes orignal/wapiti/cerf mulet | 0.94 | DISPONIBLE | P1 |
| `env_canada` | Environnement Canada | Federal | Ecosystemes, predateurs, habitats | 0.95 | PARTIELLEMENT INTEGRE | P0 |

**Details MELCCFP Quebec:**
- Plans de gestion orignal/cerf/ours (cycles 5 ans)
- Statistiques recolte annuelles par zone
- Inventaires aeriens periodiques
- Donnees ouvertes: https://www.donneesquebec.ca
- Limites: Delai publication 6-12 mois

### Etats-Unis

| ID | Organisme | Etat | Donnees | Fiabilite | Statut | Potentiel P0 |
|----|-----------|------|---------|-----------|--------|--------------|
| `mt_fwp` | Montana FWP | Montana | Etudes wapiti/cerf, migrations GPS | 0.94 | DISPONIBLE | P1 |
| `wy_gf` | Wyoming Game & Fish | Wyoming | Migration GPS, mortalite hivernale | 0.95 | DISPONIBLE | P1 |
| `co_parks` | Colorado Parks & Wildlife | Colorado | Nutrition, reproduction, CWD | 0.93 | DISPONIBLE | P1 |
| `id_fish_game` | Idaho Fish & Game | Idaho | Donnees recolte, populations | 0.91 | DISPONIBLE | P2 |
| `usgs` | USGS | Federal | Modelisation ecologique, telemetrie | 0.96 | PARTIELLEMENT INTEGRE | P0 |

**Details Montana FWP:**
- Programme telemetrie wapiti/cerf 20+ ans
- Cartes migrations publiques
- Rapports biologiques annuels
- API: Non disponible, PDF/shapefiles
- Limites: Transposabilite Quebec limitee (especes differentes)

---

## CENTRES DE RECHERCHE ET UNIVERSITES

### Canada

| ID | Institution | Specialite | Donnees | Fiabilite | Statut | Potentiel P0 |
|----|-------------|------------|---------|-----------|--------|--------------|
| `craaq` | CRAAQ | Guides pratiques | Guides cervides, bonnes pratiques | 0.88 | A INTEGRER | P1 |
| `ulaval` | Universite Laval | Ecologie cervides | Etudes orignal/cerf Quebec | 0.94 | PARTIELLEMENT INTEGRE | P0 |
| `uqar` | UQAR | Comportement orignal | "De la bouche des orignaux", telemetrie | 0.93 | A INTEGRER | P0 |
| `ualberta` | U. Alberta | Wapiti/cerf mulet | Ecologie Rocheuses | 0.92 | DISPONIBLE | P2 |
| `cen_ulaval` | CEN U. Laval | Caribou/nord | Ecologie nordique | 0.95 | INTEGRE | P1 |

**Details UQAR - Source Critique:**
- Travaux Louis Gagnon (expert terrain)
- Livre "De la bouche des orignaux" - Compilation 30 ans observations
- Telemetrie orignal Cote-Nord/Bas-St-Laurent
- Comportements rut, alimentation, deplacement
- Statut: A INTEGRER EN PRIORITE P0

### Etats-Unis

| ID | Institution | Specialite | Donnees | Fiabilite | Statut | Potentiel P0 |
|----|-------------|------------|---------|-----------|--------|--------------|
| `u_montana` | U. Montana | Wildlife Biology | Comportement wapiti/cerf | 0.93 | DISPONIBLE | P1 |
| `wmi_wyoming` | Wyoming Migration Initiative | Migrations | Corridors GPS, cartes | 0.95 | A INTEGRER | P1 |
| `csu` | Colorado State U. | Nutrition cervides | Reproduction, croissance | 0.92 | DISPONIBLE | P2 |
| `penn_state_dfs` | Penn State Deer-Forest Study | Cerf/habitat | Pression chasse, habitat, survie | 0.94 | A INTEGRER | P0 |

**Details Penn State Deer-Forest Study:**
- Etude long terme (20+ ans) cerf Virginie
- Impact pression chasse sur comportement
- Relation habitat-survie-reproduction
- Publications open-access
- Tres pertinent pour P0 (pression chasse)

---

## BASES DE DONNEES SCIENTIFIQUES

| Plateforme | Type | Couverture | Acces | Utilisation |
|------------|------|------------|-------|-------------|
| **Google Scholar** | Aggregateur | Globale | Gratuit | Recherche initiale |
| **ResearchGate** | Reseau chercheurs | Globale | Gratuit | Acces articles, contact auteurs |
| **JSTOR** | Archive academique | Historique | Payant/institutionnel | Articles historiques |
| **ScienceDirect** | Editeur Elsevier | Large | Payant | Articles recents |
| **Journal of Wildlife Management** | Specialise | Amerique Nord | Payant | Reference or |
| **Wildlife Society Bulletin** | Specialise | Amerique Nord | Payant | Pratique terrain |

**Protocole de Recherche:**
1. Mots-cles: "moose behavior Quebec", "white-tailed deer hunting pressure", "elk migration corridor"
2. Filtres: 2015-2025, peer-reviewed, Amerique Nord
3. Prioriser: Meta-analyses, etudes long terme, donnees GPS

---

## SOURCES EMPIRIQUES DE TERRAIN

### Canada

| ID | Source | Type | Donnees | Fiabilite | Statut | Potentiel P0 |
|----|--------|------|---------|-----------|--------|--------------|
| `sepaq` | SEPAQ | Gestionnaire | Recolte, frequentation | 0.90 | PARTIELLEMENT INTEGRE | P0 |
| `zecs_qc` | Reseau ZECs | Gestionnaires | Statistiques annuelles | 0.85 | A INTEGRER | P1 |
| `fqf` | Federation chasseurs QC | Association | Observations terrain | 0.80 | INTEGRE | P0 |
| `pourvoiries_qc` | Federation pourvoiries | Gestionnaires | Recolte, observations | 0.82 | A INTEGRER | P1 |
| `guides_nordiques` | Guides chasse nord QC | Experts terrain | 30+ ans observations | 0.85 | INTEGRE | P0 |

### Etats-Unis

| ID | Source | Type | Donnees | Fiabilite | Statut | Potentiel P0 |
|----|--------|------|---------|-----------|--------|--------------|
| `rmef` | Rocky Mountain Elk Foundation | Conservation | Habitat, populations wapiti | 0.88 | DISPONIBLE | P2 |
| `nda` | National Deer Association (ex-QDMA) | Conservation | Gestion cerf, habitat | 0.90 | A INTEGRER | P1 |
| `bowhunters` | Pope & Young / Boone & Crockett | Chasseurs | Records, observations | 0.75 | DISPONIBLE | P2 |

**Details NDA (National Deer Association):**
- Anciennement QDMA (Quality Deer Management Association)
- Donnees gestion cerf 40+ ans
- Impact chasse selective sur populations
- Guides pratiques, recherche appliquee
- Pertinent pour P0 (comportement sous pression)

---

## SOURCES POUR L'ANALYSE D'HABITAT

| Source | Type | Donnees | Resolution | Acces | Statut |
|--------|------|---------|------------|-------|--------|
| **Sentinel-2 (ESA)** | Satellite | NDVI, couvert vegetal | 10m | Gratuit | INTEGRE |
| **USGS Earth Explorer** | Archive satellite | Landsat, SRTM DEM | 30m | Gratuit | DISPONIBLE |
| **SIGEOM (Quebec)** | SIG provincial | Geologie, mines | Variable | Gratuit | A INTEGRER |
| **LiDAR provincial QC** | LiDAR | MNT haute precision | 1m | Gratuit | PARTIELLEMENT INTEGRE |
| **OpenStreetMap** | Crowdsource | Routes, batiments | Variable | Gratuit | INTEGRE |
| **MapLibre GL** | Rendu cartes | Visualisation | - | Gratuit | INTEGRE |
| **QGIS** | Outil SIG | Analyse spatiale | - | Gratuit | Outil |

---

## TOP 10 DES MEILLEURES SOURCES ABSOLUES

| Rang | Source | Pourquoi | Fiabilite | Priorite Integration |
|------|--------|----------|-----------|---------------------|
| **1** | MELCCFP Quebec | Source primaire locale, donnees officielles | 0.95 | **P0 - CRITIQUE** |
| **2** | UQAR / Louis Gagnon | Expertise terrain Quebec, 30+ ans | 0.93 | **P0 - CRITIQUE** |
| **3** | Penn State Deer-Forest Study | Pression chasse, comportement, long terme | 0.94 | **P0** |
| **4** | Montana FWP | Methodologie reference, donnees GPS | 0.94 | P1 |
| **5** | Wyoming Migration Initiative | Corridors, migrations, cartes | 0.95 | P1 |
| **6** | Colorado Parks & Wildlife | Nutrition, reproduction, CWD | 0.93 | P1 |
| **7** | USGS | Modelisation ecologique, methodes | 0.96 | P0 |
| **8** | CRAAQ | Guides pratiques Quebec | 0.88 | P1 |
| **9** | NDA (ex-QDMA) | Gestion cerf, impact chasse | 0.90 | P1 |
| **10** | Sentinel-2 + LiDAR QC | Analyse habitat, vegetation | 0.92 | **INTEGRE** |

---

## MATRICE D'INTEGRATION DES SOURCES

| Source | Integre | Partiellement | A Integrer | Non Dispo | Priorite |
|--------|---------|---------------|------------|-----------|----------|
| MELCCFP Quebec | | X | | | P0 |
| UQAR / Louis Gagnon | | X | X | | P0 |
| Penn State DFS | | | X | | P0 |
| USGS | | X | | | P0 |
| SEPAQ | | X | | | P0 |
| Montana FWP | | | X | | P1 |
| Wyoming MI | | | X | | P1 |
| Colorado PW | | | X | | P1 |
| NDA | | | X | | P1 |
| CRAAQ | | | X | | P1 |
| Ontario MNRF | | | X | | P1 |
| Alberta F&W | | | X | | P1 |
| Telemetrie GPS | | | | X | Partenariat |

---

## PROTOCOLE D'INTEGRATION DES SOURCES

### Phase 1: Extraction (P0)
1. **MELCCFP**: Telecharger shapefiles ZEC/pourvoiries, statistiques recolte PDF
2. **UQAR**: Contacter Louis Gagnon, obtenir donnees "De la bouche des orignaux"
3. **Penn State DFS**: Compiler publications open-access, extraire patterns pression

### Phase 2: Structuration (P0-P1)
1. Normaliser formats (JSON standard)
2. Valider coherence inter-sources
3. Creer registre sources avec metadata

### Phase 3: Integration Backend (P1)
1. Importer dans `bionic_knowledge_engine/data/`
2. Creer services d'acces
3. Connecter a `predictive_territorial.py` et `behavioral_models.py`

### Phase 4: Validation (P1)
1. Comparer predictions vs observations terrain
2. Ajuster ponderations selon fiabilite
3. Documenter limites et biais

---

# ANNEXES

## A. GLOSSAIRE

| Terme | Definition |
|-------|------------|
| BIONIC | Branding du systeme intelligent HUNTIQ |
| G-QA | Cadre Qualite Phase G |
| G-SEC | Cadre Securite Phase G |
| G-DOC | Cadre Documentation Phase G |
| NDVI | Normalized Difference Vegetation Index |
| DEM | Digital Elevation Model |
| WMS | Web Map Service |
| ZEC | Zone d'Exploitation Controlee |

## B. FICHIERS DE REFERENCE

| Fichier | Contenu |
|---------|---------|
| `/app/backend/modules/bionic_knowledge_engine/data/habitat_variables.json` | Variables habitat |
| `/app/backend/modules/bionic_knowledge_engine/data/species/*.json` | Donnees especes |
| `/app/backend/modules/bionic_knowledge_engine/data/sources_registry.json` | Sources scientifiques |
| `/app/backend/modules/predictive_engine/v1/service.py` | Patterns predictifs |
| `/app/backend/modules/weather_engine/v1/service.py` | Service meteo |
| `/app/backend/modules/wildlife_behavior_engine/v1/service.py` | Comportements |
| `/app/backend/modules/camera_engine/v1/services.py` | Cameras trail |

## C. CONTACTS SOURCES

| Source | Contact | Type |
|--------|---------|------|
| MFFP Quebec | donnees.ouvertes@mffp.gouv.qc.ca | Donnees ouvertes |
| SEPAQ | info@sepaq.com | Partenariat |
| UQAR | recherche@uqar.ca | Academique |
| Louis Gagnon | (a documenter) | Expert terrain |

---

**Document genere conformement aux cadres G-QA, G-SEC, G-DOC**
**PHASE G - BIONIC ULTIMATE INTEGRATION**
**HUNTIQ V5 GOLD MASTER**

*Ce document constitue le prerequis absolu pour le demarrage des modules P0.*
*Toute implementation est suspendue jusqu'a validation explicite par COPILOT MAITRE.*
