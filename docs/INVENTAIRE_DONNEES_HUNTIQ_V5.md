# INVENTAIRE GLOBAL DES DONNÉES - HUNTIQ-V5 BIONIC
## Document préparé pour COPILOT MAÎTRE (STEEVE)
### Version: 1.0 | Date: Décembre 2025

---

# 1. INTELLIGENCE → ANALYTICS
## `/app/frontend/src/pages/AnalyticsPage.jsx` | `/app/frontend/src/modules/analytics/`

### VARIABLES BRUTES
| Variable | Type | Source | Description |
|----------|------|--------|-------------|
| `total_trips` | integer | MongoDB | Nombre total de sorties de chasse |
| `successful_trips` | integer | MongoDB | Sorties avec succès |
| `total_hours` | float | MongoDB | Heures totales de chasse |
| `total_observations` | integer | MongoDB | Observations fauniques totales |
| `date` | datetime | MongoDB | Date de chaque sortie |
| `duration_hours` | float | MongoDB | Durée de chaque sortie |
| `weather_conditions` | string | MongoDB | Conditions météo enregistrées |
| `species` | enum | MongoDB | Espèce ciblée (deer, moose, bear, wild_turkey, duck, wild_boar, goose) |
| `observations` | integer | MongoDB | Nombre d'observations par sortie |
| `success` | boolean | MongoDB | Succès ou non de la sortie |

### VARIABLES DÉRIVÉES
| Variable | Formule | Description |
|----------|---------|-------------|
| `success_rate` | `(successful_trips / total_trips) * 100` | Taux de succès global (%) |
| `avg_trip_duration` | `total_hours / total_trips` | Durée moyenne par sortie (h) |
| `most_active_species` | Agrégation | Espèce avec le plus d'observations |
| `best_success_species` | Agrégation | Espèce avec le meilleur taux de succès |

### SCORES, INDICES, FACTEURS D'INFLUENCE
| Score | Pondération | Description |
|-------|-------------|-------------|
| `species_breakdown[].trips` | - | Nombre de sorties par espèce |
| `species_breakdown[].success_rate` | - | Taux de succès par espèce |
| `species_breakdown[].total_observations` | - | Observations par espèce |
| `weather_analysis[].success_rate` | - | Taux de succès par condition météo |
| `weather_analysis[].avg_observations` | - | Observations moyennes par météo |
| `optimal_times[].success_rate` | - | Taux de succès par créneau horaire |
| `optimal_times[].trips` | - | Nombre de sorties par créneau |

### RÈGLES MÉTIER APPLIQUÉES
- Filtrage par période: `week`, `month`, `season`, `year`, `all`
- Agrégation par espèce avec couleurs SPECIES_COLORS
- Conditions météo catégorisées: `Ensoleillé`, `Nuageux`, `Pluvieux`, `Brumeux`, `Neigeux`
- Créneaux horaires: Analyse par heure de début de chasse

### SOURCES DE DONNÉES
- **Collection MongoDB**: `hunting_trips` (via `/api/v1/analytics/`)
- **API Endpoints**:
  - `GET /api/v1/analytics/dashboard`
  - `GET /api/v1/analytics/species`
  - `GET /api/v1/analytics/weather`
  - `GET /api/v1/analytics/optimal-times`
  - `GET /api/v1/analytics/trends`

### FRÉQUENCE DE MISE À JOUR
- Temps réel lors de création/suppression de sorties
- Agrégation calculée à chaque requête dashboard

### TRANSFORMATIONS / NORMALISATIONS
- Labels espèces: `deer` → `Cerf`, `moose` → `Orignal`, etc.
- Dates formatées: `fr-CA` locale
- Pourcentages arrondis à l'entier

---

# 2. INTELLIGENCE → PRÉVISIONS
## `/app/frontend/src/pages/ForecastPage.jsx` | `/app/backend/modules/predictive_engine/`

### DONNÉES MÉTÉO UTILISÉES
| Variable | Type | Source | Pondération |
|----------|------|--------|-------------|
| `temperature` | float | API Météo | 30% |
| `wind_speed` | float | API Météo | 25% |
| `humidity` | float | API Météo | 15% |
| `pressure` | float | API Météo | 20% |
| `precipitation` | float | API Météo | 10% |
| `cloud_cover` | integer | API Météo | - |

### DONNÉES FAUNIQUES
| Variable | Description |
|----------|-------------|
| `SPECIES_PATTERNS[species].dawn_activity` | Score activité à l'aube (0-100) |
| `SPECIES_PATTERNS[species].midday_activity` | Score activité mi-journée |
| `SPECIES_PATTERNS[species].dusk_activity` | Score activité crépuscule |
| `SPECIES_PATTERNS[species].night_activity` | Score activité nocturne |
| `SPECIES_PATTERNS[species].best_temp_range` | Plage température optimale (°C) |
| `SPECIES_PATTERNS[species].weather_sensitivity` | Sensibilité météo (0-1) |

### CYCLES TEMPORELS
| Cycle | Facteurs | Description |
|-------|----------|-------------|
| **Heures** | `dawn_activity`, `midday_activity`, `dusk_activity` | Activité par période du jour |
| **Mois (SEASON_FACTORS)** | 0.5 à 0.95 | Multiplicateurs saisonniers |
| **Phase lunaire** | Cycle 29.53 jours | Impact nouvelle/pleine lune |

### FACTEURS SEASON_FACTORS (par mois)
```
Janvier: 0.6 | Février: 0.5 | Mars: 0.6 | Avril: 0.7
Mai: 0.75 | Juin: 0.65 | Juillet: 0.5 | Août: 0.6
Septembre: 0.85 | Octobre: 0.95 | Novembre: 0.9 | Décembre: 0.7
```

### PROBABILITÉS ET NIVEAUX D'ACTIVITÉ
| Niveau | Score | Description |
|--------|-------|-------------|
| `very_high` | ≥ 80 | Activité maximale |
| `high` | ≥ 60 | Forte activité |
| `moderate` | ≥ 40 | Activité modérée |
| `low` | ≥ 20 | Faible activité |
| `very_low` | < 20 | Très faible activité |

### HEURES DE POINTE (PredictiveService)
- Période d'aube: `sunrise - 1h` à `sunrise + 2h`
- Période de crépuscule: `sunset - 2h` à `sunset + 1h`
- Mi-journée: Entre aube et crépuscule

### FACTEURS PRÉDICTIFS EN PLACE
| Facteur | Pondération | Calcul |
|---------|-------------|--------|
| Saison | 25% | `SEASON_FACTORS[month] * 100` |
| Météo | 20% | Algorithme température/vent |
| Phase lunaire | 15% | Position cycle 29.53 jours |
| Pression atmo | 20% | Variation barométrique |
| Activité récente | 20% | Observations locales simulées |

### RÈGLES MÉTIER / PONDÉRATIONS
```python
# Calcul score final
weights = [0.25, 0.20, 0.15, 0.20, 0.20]
success_probability = sum(factor.score * weight for factor, weight in zip(factors, weights))
```

### CONDITIONS MÉTÉO OPTIMALES (WeatherService)
```python
OPTIMAL_CONDITIONS = {
    "temperature": {"min": -5, "max": 15, "ideal": 5},
    "humidity": {"min": 40, "max": 80, "ideal": 60},
    "wind_speed": {"min": 0, "max": 20, "ideal": 8},
    "pressure_change": 5  # hPa
}
```

---

# 3. INTELLIGENCE → PLAN MAÎTRE
## `/app/frontend/src/pages/PlanMaitrePage.jsx` | `/app/frontend/src/modules/planmaitre/`

### PROBABILITÉ DE SUCCÈS
| Variable | Source | Description |
|----------|--------|-------------|
| `success_probability` | PredictiveService | Probabilité calculée (0-100) |
| `confidence` | PredictiveService | Niveau de confiance (0-1) |

### CONFIANCE
- 0.85 si données météo disponibles
- 0.70 si données météo absentes

### FACTEURS D'INFLUENCE
| Facteur | Impact | Score (0-100) |
|---------|--------|---------------|
| Saison | `very_positive` à `negative` | Variable |
| Météo | `very_positive` à `negative` | Variable |
| Phase lunaire | `very_positive` à `negative` | Variable |
| Pression atmosphérique | `very_positive` à `negative` | Variable |
| Activité récente | `very_positive` à `negative` | Variable |

### RECOMMANDATIONS IA
| Score | Recommandation |
|-------|----------------|
| ≥ 80 | "Conditions excellentes pour la chasse. Maximisez votre temps à l'aube." |
| ≥ 65 | "Bonnes conditions. Privilégiez les périodes d'aube et crépuscule." |
| ≥ 50 | "Conditions moyennes. La patience sera clé." |
| < 50 | "Conditions défavorables. Reportez si possible." |

### SCORES PRODUITS / STRATÉGIES (ScoringService)
| Critère | Poids | Max |
|---------|-------|-----|
| `attraction_days` | 15 | 10 |
| `natural_palatability` | 12 | 10 |
| `olfactory_power` | 12 | 10 |
| `persistence` | 10 | 10 |
| `nutrition` | 8 | 10 |
| `behavioral_compounds` | 8 | 10 |
| `rainproof` | 8 | 10 |
| `feed_proof` | 7 | 10 |
| `certified` | 6 | 10 |
| `physical_resistance` | 5 | 10 |
| `ingredient_purity` | 4 | 10 |
| `loyalty` | 3 | 10 |
| `chemical_stability` | 2 | 10 |

### DONNÉES COMPORTEMENTALES
| Variable | Source | Description |
|----------|--------|-------------|
| `activity_patterns` | BehavioralService | Patterns horaires d'activité |
| `feeding_zones` | BehavioralService | Zones d'alimentation |
| `bedding_areas` | BehavioralService | Zones de repos |
| `movement_corridors` | BehavioralService | Corridors de déplacement |
| `rutting_activity` | BehavioralService | Activité de rut |

### DONNÉES TERRITORIALES
- Coordonnées GPS (lat, lng)
- Waypoints utilisateur
- Zones analysées
- Scores par module BIONIC

---

# 4. CARTE → CARTE INTERACTIVE
## `/app/frontend/src/pages/MapPage.jsx` | `/app/frontend/src/components/TerritoryMap.jsx`

### COUCHES CARTOGRAPHIQUES EXISTANTES
| ID | Nom | Couleur | Description |
|----|-----|---------|-------------|
| `habitats` | Habitats optimaux | #22c55e | Zones d'habitat idéales |
| `rut` | Rut potentiel | #e91e63 | Zones de rut identifiées |
| `salines` | Salines potentielles | #00bcd4 | Points de salines |
| `affuts` | Affûts potentiels | #9c27b0 | Positions d'affût |
| `trajets` | Trajets de chasse | #ff9800 | Routes recommandées |
| `peuplements` | Peuplements forestiers | #4caf50 | Types de forêt |
| `ensoleillement` | Ensoleillement | #ffeb3b | Exposition solaire |
| `orientation` | Orientation | #2196f3 | Direction terrain |
| `hydro` | Hydrographie avancée | #1976d2 | Cours d'eau |
| `alimentation` | Zones d'alimentation | #8bc34a | Sources de nourriture |
| `repos` | Zones de repos | #795548 | Zones de coucher |
| `ndvi` | NDVI / Densité végétale | #66bb6a | Végétation satellite |
| `pentes` | Pentes | #ff7043 | Inclinaison terrain |
| `altitude` | Altitude relative | #78909c | Élévation |
| `corridors` | Corridors fauniques | #ff5722 | Passages faune |

### DONNÉES TERRITORIALES AFFICHÉES
| Donnée | Source | Description |
|--------|--------|-------------|
| Events (observations) | MongoDB | Marqueurs d'observations |
| Cameras | MongoDB | Caméras de trail |
| Waypoints utilisateur | MongoDB | Points enregistrés |
| Heatmap activité | API `/territory/layers/heatmap_activite` | Carte de chaleur |

### DONNÉES FAUNIQUES
| Type | Description |
|------|-------------|
| Heatmap points | `[lat, lon, intensity]` |
| Species config | `orignal`, `chevreuil`, `ours`, `autre` |
| Event types | `observation`, `camera_photo`, `tir`, `cache`, `saline`, `feeding_station` |

### DONNÉES MÉTÉO SUR CARTE
| Variable | Affichage |
|----------|-----------|
| Température | Badge avec icône thermomètre |
| Vent | Direction + vitesse km/h |
| Score chasse | Score /100 |
| État | Badge LIVE |

### DONNÉES CAMÉRAS
| Champ | Type | Description |
|-------|------|-------------|
| `latitude` | float | Position |
| `longitude` | float | Position |
| `name` | string | Nom caméra |
| `species` | string | Espèce détectée |
| `species_confidence` | float | Confiance IA |

### RÈGLES DE VISUALISATION
| Zone | Opacité | Poids contour |
|------|---------|---------------|
| Score ≥ 85 | 0.08 | 2.5 |
| Score ≥ 75 | 0.06 | 2 |
| Score ≥ 65 | 0.04 | 1.5 |
| Score < 65 | 0.02 | 1 |

### SOURCES WMS (Gouvernement Québec)
| Layer | URL | Couches |
|-------|-----|---------|
| `foret` | servicescarto.mffp.gouv.qc.ca | Couverture forestière |
| `hydro` | servicescarto.mern.gouv.qc.ca | Hydrographie GRHQ |
| `topo` | servicescarto.mern.gouv.qc.ca | Relief LiDAR |
| `routes` | servicescarto.mern.gouv.qc.ca | Routes et chemins |
| `cadastre` | servicescarto.mern.gouv.qc.ca | Cadastre |

### FRÉQUENCES DE MISE À JOUR
- Events/Cameras: Temps réel
- Heatmap: Recalcul à chaque changement de filtres
- WMS: Cache navigateur

---

# 5. CARTE → MON TERRITOIRE
## `/app/frontend/src/pages/MonTerritoireBionicPage.jsx`

### DONNÉES PROPRES À L'UTILISATEUR
| Type | Collection MongoDB | Description |
|------|-------------------|-------------|
| Waypoints | `user_waypoints` | Points GPS personnels |
| Lieux | `user_places` | Lieux enregistrés (ZEC, camp, etc.) |
| Tracks | `user_tracks` | Tracés GPS |
| Favoris | `zone_favorites` | Zones favorites avec alertes |

### TYPES DE WAYPOINTS
| Type | Icône | Couleur |
|------|-------|---------|
| `zec` | Tent | #22c55e |
| `pourvoirie` | Building | #3b82f6 |
| `prive` | Lock | #f5a623 |
| `sepaq` | CircleDot | #8b5cf6 |
| `affut` | Target | #ef4444 |
| `saline` | Droplet | #06b6d4 |
| `observation` | Eye | #ec4899 |
| `stationnement` | ParkingCircle | #6b7280 |
| `camp` | Tent | #84cc16 |
| `autre` | Pin | #a855f7 |

### WAYPOINTS, ZONES, POLYGONES
| Champ | Type | Description |
|-------|------|-------------|
| `id` | string | Identifiant unique |
| `name` | string | Nom du waypoint |
| `lat` | float | Latitude |
| `lng` | float | Longitude |
| `type` | enum | Type de waypoint |
| `active` | boolean | Waypoint actif |
| `notes` | string | Notes utilisateur |
| `created_at` | datetime | Date création |

### HISTORIQUE D'ACTIVITÉ
| Donnée | Description |
|--------|-------------|
| `trackPoints` | Points GPS enregistrés |
| `activeTrack` | Session de tracking en cours |
| `totalDistance` | Distance parcourue (km) |
| `sessionDuration` | Durée session |

### DONNÉES FAUNIQUES/MÉTÉO SPÉCIFIQUES
- Zones BIONIC calculées autour des waypoints actifs
- Météo LIVE positionnée sur waypoints
- Scores BIONIC par position

### SCORES CALCULÉS (BIONIC)
| Score | Clé | Poids |
|-------|-----|-------|
| Habitat | `score_H` | 25% |
| Rut | `score_R` | 20% |
| Salines | `score_S` | 10% |
| Affûts | `score_A` | 20% |
| Trajets | `score_T` | 15% |
| Peuplements | `score_P` | 10% |

### COUCHES PERSONNALISÉES
| Couche | Mode | Description |
|--------|------|-------------|
| Micro-zones | Cercles concentriques | Affichage haute précision |
| Classic | Hexagones | Affichage standard |
| Corridors | Lignes | Chemins de déplacement |

### SYSTÈME GROUPE
| Fonctionnalité | Description |
|----------------|-------------|
| Partage waypoints | Entre membres du groupe |
| Tracking live | Position temps réel |
| Chat | Communication groupe |
| Zones de sécurité | Secteurs de tir |
| Session heatmap | Carte chaleur collective |

---

# 6. MÉTADONNÉES & TRANSFORMATIONS

## TRANSFORMATIONS APPLIQUÉES

### Frontend
| Transformation | Fichier | Description |
|----------------|---------|-------------|
| Espèces → Labels FR | `SPECIES_LABELS` | deer → Cerf |
| Conditions météo → Couleurs | `WEATHER_COLORS` | Mapping couleurs |
| Score → Rating | `getProbabilityRating()` | Score → level (optimal/high/good/moderate/low) |
| DMS ↔ Decimal | `dmsToDecimal()`, `decimalToDms()` | Conversion coordonnées |

### Backend
| Transformation | Module | Description |
|----------------|--------|-------------|
| ObjectId → string | Tous | Conversion MongoDB |
| datetime → ISO | Tous | Format UTC |
| Score normalization | ScoringService | Score 0-10 pondéré |
| Weather scoring | WeatherService | Multi-critères → score unique |

## PONDÉRATIONS

### Predictive Engine
```python
factors_weights = [0.25, 0.20, 0.15, 0.20, 0.20]
# Saison, Météo, Lune, Pression, Activité
```

### Weather Engine
```python
temp_weight = 0.30
wind_weight = 0.25
pressure_weight = 0.20
humidity_weight = 0.15
precipitation_weight = 0.10
```

### BIONIC Scoring
```python
category_weights = {
    'habitat': 0.25,
    'rut': 0.20,
    'salines': 0.10,
    'affuts': 0.20,
    'trajets': 0.15,
    'peuplements': 0.10
}
```

### Attractant Scoring (13 critères)
```python
total_weight = 100  # Somme des poids critères
final_score = (weighted_sum / total_weight) * 10
```

## SEUILS

### Scores généraux
| Seuil | Label | Couleur |
|-------|-------|---------|
| ≥ 85 | Exceptionnel | green-500 |
| ≥ 70 | Excellent | lime-500 |
| ≥ 55 | Bon | yellow-500 |
| < 55 | Modéré | orange-500 |

### Attractants
| Seuil | Pastille | Label |
|-------|----------|-------|
| ≥ 7.5 | green | Attraction forte |
| ≥ 5.0 | yellow | Attraction modérée |
| < 5.0 | red | Attraction faible |

### Micro-zones BIONIC
| Seuil | Visibilité |
|-------|------------|
| ≥ 60 | Affichées (probabilityThreshold) |
| < 60 | Masquées |

## NORMALISATIONS

### Coordonnées
- Latitude: -90 à 90
- Longitude: -180 à 180
- Précision: 6 décimales

### Scores
- Tous normalisés 0-100
- Affichage parfois /10 (attractants)

### Dates
- Stockage: UTC ISO-8601
- Affichage: `fr-CA` locale

## MODÈLES IA UTILISÉS

### Intégrés
| Modèle | Usage | Statut |
|--------|-------|--------|
| BIONIC Hybrid | Scoring waypoints | Actif |
| Weather Predictor | Conditions chasse | Actif |
| Species Detector | Photos caméra | Actif (backend) |

### Planifiés (Phase G)
| Modèle | Usage | Statut |
|--------|-------|--------|
| GPT-5.2 | Enrichissement contextuel | Planifié |
| Moteur Prédictif Territorial | Prédictions P0 | À implémenter |
| Modèles Comportementaux | Patterns P0 | À implémenter |

## DONNÉES CALCULÉES MAIS NON AFFICHÉES

| Donnée | Localisation | Raison |
|--------|--------------|--------|
| `weighted_scores` par critère | ScoringService | Détail technique |
| `hourlyForecast` complet | WeatherEngine | Affiche que résumé |
| `huntingFactors` détaillés | PredictiveService | Agrégé en score |
| `microZones` filtrées eau | WaterExclusionService | Exclusion silencieuse |

---

# 7. OBJECTIF - CONSOLIDATION PHASE G

## ÉVITER DUPLICATION/REDONDANCE
| Donnée existante | Module actuel | Action P0 |
|------------------|---------------|-----------|
| Activité par heure | BehavioralService | Réutiliser |
| Score météo | WeatherEngine | Intégrer |
| Patterns espèces | SPECIES_PATTERNS | Enrichir |
| Coordonnées waypoints | UserData | Connecter |

## GARANTIR COHÉRENCE
| Source | Destination | Validation |
|--------|-------------|------------|
| WeatherEngine scores | PredictiveEngine | Même formule |
| BIONIC layer colors | All maps | bionic-colors.js |
| Species codes | Tous modules | Enum partagé |

## FACTEURS PRÉDICTIFS FINAUX P0

### À intégrer dans Moteur Prédictif Territorial
1. **Données existantes**:
   - `SPECIES_PATTERNS` (backend)
   - `SEASON_FACTORS` (backend)
   - `OPTIMAL_CONDITIONS` (WeatherEngine)
   - `BIONIC_LAYERS` scores (frontend core)

2. **Nouvelles données P0**:
   - Données GPS agrégées caméras
   - Historique observations utilisateur
   - Pression de chasse calculée
   - Corridors détectés

### À intégrer dans Modèles Comportementaux
1. **Données existantes**:
   - `activity_patterns` (BehavioralService)
   - `feeding_zones`, `bedding_areas` (BehavioralService)
   - `rutting_activity` (BehavioralService)

2. **Nouvelles données P0**:
   - Patterns horaires par saison
   - Réponse aux conditions météo
   - Influence phase lunaire détaillée

## INTÉGRER AGRÉGATS CAMÉRAS
| Source | Agrégat | Usage P0 |
|--------|---------|----------|
| `species_confidence` | Moyenne par zone | Score densité |
| `timestamp` photos | Distribution horaire | Patterns activité |
| Localisation caméras | Cluster spatial | Corridors |

## VERSION ULTIME MOTEUR P0

### Architecture finale
```
┌─────────────────────────────────────────────┐
│           BIONIC ENGINE P0                  │
├─────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────────┐    │
│  │ Predictive  │    │  Behavioral     │    │
│  │ Territorial │    │  Models         │    │
│  └──────┬──────┘    └────────┬────────┘    │
│         │                    │              │
│  ┌──────▼────────────────────▼──────┐      │
│  │      UNIFIED SCORING ENGINE       │      │
│  │ (WeatherEngine + BIONIC + New)    │      │
│  └──────────────────────────────────┘      │
│         │                                   │
│  ┌──────▼──────────────────────────┐       │
│  │    EXISTING DATA SOURCES         │       │
│  │ - MongoDB (waypoints, cameras)   │       │
│  │ - Weather APIs                   │       │
│  │ - WMS Quebec                     │       │
│  └──────────────────────────────────┘       │
└─────────────────────────────────────────────┘
```

---

## RÉSUMÉ EXÉCUTIF

### Total variables inventoriées: **~150+**
### Modules analysés: **12**
### APIs cartographiées: **25+**
### Scores/indices identifiés: **35+**
### Règles métier documentées: **20+**

### Prochaines étapes P0:
1. Implémenter logique `predictive_territorial.py`
2. Créer `behavioral_models.py`
3. Intégrer données existantes sans duplication
4. Respecter cadres G-QA, G-SEC, G-DOC

---
*Document généré pour PHASE G - BIONIC ULTIMATE INTEGRATION*
*HUNTIQ-V5 GOLD MASTER BIONIC*
