# ANALYSE TOTALE 360° — BIONIC V5
# MON TERRITOIRE + CARTE INTERACTIVE
# Document de référence — 25 Février 2026

---

## 1. MON TERRITOIRE — CONTENU RÉEL

### 1.1 Couches BIONIC V5 (Fonctionnel)

| # | Couche | Type | Couleur | Espèces associées |
|---|--------|------|---------|-------------------|
| 1 | Zone de rut | Comportementale | #FF4D6D | Orignal, Chevreuil, Dindon |
| 2 | Zone de repos | Comportementale | #8B5CF6 | Toutes |
| 3 | Zone d'alimentation | Comportementale | #22C55E | Toutes |
| 4 | Corridor faunique | Comportementale | #06B6D4 | Orignal, Chevreuil, Ours |
| 5 | Habitat optimal | Environnementale | #10B981 | Toutes |
| 6 | Ensoleillement | Environnementale | #FCD34D | Chevreuil, Dindon |
| 7 | Orientation | Environnementale | #2196f3 | — (interne) |
| 8 | Hydrographie | Environnementale | #3B82F6 | Orignal, Ours |
| 9 | Peuplements forestiers | Environnementale | #15803D | Toutes |
| 10 | NDVI / Densité végétale | Environnementale | #66bb6a | Ours, Dindon |
| 11 | Pentes | Environnementale | #ff7043 | Orignal, Ours |
| 12 | Saline potentielle | Stratégique | #FFFF00 | Orignal |
| 13 | Affût potentiel | Stratégique | #F5A623 | Chevreuil, Dindon |
| 14 | Trajets de chasse | Stratégique | #ff9800 | — (global) |
| 15 | Altitude relative | Environnementale | #78909c | — (global) |

### 1.2 Espèces (Fonctionnel)

| Espèce | Couches actives | Préférences habitat |
|--------|----------------|---------------------|
| **Orignal** (Alces americanus) | 9 couches (habitats, alimentation, corridors, repos, hydro, salines, rut, peuplements, pentes) | Proximité eau, conifères |
| **Chevreuil** (Odocoileus virginianus) | 8 couches (habitats, alimentation, corridors, rut, affûts, repos, peuplements, ensoleillement) | Lisières, écotones |
| **Ours noir** (Ursus americanus) | 8 couches (habitats, alimentation, corridors, repos, hydro, peuplements, ndvi, pentes) | Forêt dense, eau, altitude |
| **Dindon sauvage** (Meleagris gallopavo) | 7 couches (habitats, alimentation, repos, affûts, peuplements, ensoleillement, ndvi) | Lisières, ensoleillement |
| **Toutes** | 15 couches (aucun filtrage) | — |

### 1.3 Modules internes (Fonctionnel — scoring disponible, données simulées)

| Module | Fonction | État |
|--------|----------|------|
| soleil | Exposition solaire par orientation | Moteur prêt, données simulées |
| pente | Pentes et orientation du terrain | Moteur prêt, données simulées |
| forêt | Couvert forestier et densité | Moteur prêt, données simulées |
| thermique | Zones de confort thermique | Moteur prêt, connecté météo |
| hotspot | Points chauds d'activité | Moteur prêt, non affiché |
| pression | Pression humaine | Moteur prêt, données simulées |
| accès | Points et difficulté d'accès | Moteur prêt, données simulées |
| fraîcheur | Proximité eau / zones fraîches | Moteur prêt, données simulées |
| transition | Écotones / zones tampons | Moteur prêt, données simulées |

### 1.4 Exclusion Terrain — Tolérance Zéro (Fonctionnel)

| Type | Tags OSM couverts | Buffer | Zones (Québec/Lévis) |
|------|-------------------|--------|---------------------|
| **Eau** | natural=water/wetland/bay/strait/coastline, water=*, waterway=river/riverbank/canal/stream/ditch/drain/dock, landuse=reservoir/basin/salt_pond | 300m (standard), **2000m** (grandes masses d'eau — relations OSM) | **400** |
| **Urbain** | landuse=residential/commercial/industrial/retail/farmland/farmyard/orchard/vineyard/allotments/recreation_ground/cemetery/construction/military/quarry/landfill, amenity=*, leisure=*, building=* | **200m** | **21 814** |
| **Routes** | highway=motorway→path (tous types + links) | 80-250m selon zoom | **12 259** |
| **Infrastructure** | railway=*, aeroway=*, power=plant/substation/line, man_made=* | 80-250m selon zoom | **654** |
| **TOTAL** | — | — | **35 127 entités** |

### 1.5 Génération de polygones organiques (Fonctionnel)

| Paramètre | Valeur |
|-----------|--------|
| Vertices de base | 16 |
| Perturbation angulaire | 35% de l'angle inter-vertex |
| Octaves bruit fractal | 4 |
| Variation rayon | 0.55 à 1.45 du rayon de base |
| Lissage Chaikin | 2 itérations → **65 vertices** par zone |
| Superficie cible | **5 000 m²** (± 500 m²) |
| Compacité max | **0.85** (rejette cercles, carrés, hexagones) |
| Variance arêtes min | **0.03** (rejette polygones réguliers) |
| Contour | **4-5px** opaque |
| Centre | **Transparent** |

### 1.6 Waypoints et scoring (Partiellement fonctionnel)

| Composant | État | Détail |
|-----------|------|--------|
| Création waypoint | Fonctionnel | Via MapPage + Mon Territoire |
| Affichage waypoint | Fonctionnel | Marqueurs sur carte |
| WQS (Waypoint Quality Score) | Backend prêt | `/api/v1/waypoint-scoring/wqs` |
| Heatmap waypoints | Backend prêt | `/api/v1/waypoint-scoring/heatmap` |
| Ranking waypoints | Backend prêt | `/api/v1/waypoint-scoring/ranking` |
| Forecast succès | Backend prêt | `/api/v1/waypoint-scoring/forecast/quick` |
| Recommandations IA | Backend prêt | `/api/v1/waypoint-scoring/recommendations` |
| Connexion UI ↔ Backend scoring | **NON connecté** | UI n'appelle pas ces endpoints |

### 1.7 Ce qui N'EST PAS implémenté

| Fonctionnalité | État | Bloqueur |
|----------------|------|----------|
| Observations terrain → zones BIONIC | Backend existe (`observations_router.py`), UI existe (`FieldObservationForm.jsx`), **non connecté aux zones** | Architecture de feedback manquante |
| Historique sorties GPS | Backend existe (`hunting_trip_logger`), **non affiché sur carte** | UI manquante |
| Zones réussite/échec | **Non implémenté** | Système feedback boucle fermée absent |
| Patterns comportementaux récurrents | **Non implémenté** | Analyse temporelle absente |
| Corrélations automatisées multi-facteurs | **Non implémenté** | Données terrain réelles absentes |
| Recommandations personnalisées historique | Strategy Engine prêt, **non connecté à l'historique** | Pas de persistence des résultats |
| Alertes basées sur historique réel | Notification engine prêt, **non connecté** | Pas de triggers terrain |
| IA Niveau 2 (ajustement fin) | Frontend prêt (`bionicHybridModel.js`), **endpoint backend absent** | `/api/bionic/hybrid/ai-adjust` non implémenté |

---

## 1A. MON TERRITOIRE — ANALYSES

### Scoring multi-critères (bionicScoring.js — 611 lignes)

```
Score Global BIONIC = H×0.25 + R×0.20 + S×0.10 + A×0.20 + T×0.15 + P×0.10

H (Habitat) = slope×0.12 + water×0.15 + hydro×0.10 + ndvi×0.15 + stand×0.18 + thermal×0.10 + feeding×0.10 + resting×0.10
R (Rut)     = transition×0.25 + habitat×0.20 + topo×0.15 + hydro×0.15 + feeding×0.15 + stand×0.10
S (Salines) = humidity×0.30 + water×0.25 + access×0.25 + discretion×0.20
A (Affûts)  = visibility×0.20 + position×0.20 + corridors×0.18 + sun×0.12 + feeding×0.15 + resting×0.15
T (Trajets) = trails×0.35 + slope×0.30 + connectivity×0.35
P (Peuplements) = type×0.50 + structure×0.30 + transition×0.20
```

**15 fonctions de scoring individuelles :**

| Fonction | Paramètre | Optimal | Décroissance |
|----------|-----------|---------|-------------|
| `scoreSlope` | Pente (degrés) | 5-15° | Linéaire, bonus plat pour repos |
| `scoreWaterDistance` | Distance eau (m) | ≤200m | Exponentielle (decay=0.001) |
| `scoreHydroComplexity` | Confluence/méandre/riverain | Multi-bonus | Additive (max 1.0) |
| `scoreHumidity` | Humidité sol (%) | 40-70% | Linéaire aux extrêmes |
| `scoreNDVI` | Indice végétation (-1 à 1) | 0.4-0.7 | Pénalité sol nu + très dense |
| `scoreStandType` | Type peuplement (14 types) | Tremblaie, Cédrière | Matrice 14×4 contextes |
| `scoreStandTransition` | Écotone oui/non | Transition feuillus↔résineux | Bonus +0.15 mixte |
| `scoreSunExposure` | Orientation (degrés) | Sud (135-225°) | Bonus est/ouest, pénalité nord |
| `scoreThermalComfort` | Temp/vent/couvert | 0-15°C, vent <10km/h | Multi-facteur |
| `scoreVisibility` | Portée visuelle (m) | 50-150m | Pénalité trop près/loin |
| `scoreDominantPosition` | Altitude relative (m) | 10-50m | Bonus position dominante |
| `scoreCorridors` | Sur corridor + largeur (m) | 50-200m largeur | Pénalité trop étroit/large |
| `scoreTrails` | Distance sentier + type | Gibier=5-30m, humain=100-300m | Type-dépendant |
| `scoreFeedingZone` | Distance + densité + type | ≤100m, haute densité | Exponentielle + matrice |
| `scoreRestingZone` | Couvert + sécurité | Dense + routes fuite | Multi-critère |

### Modèle hybride (bionicHybridModel.js — 379 lignes)

**Niveau 1 — 10 règles d'ajustement :**

| Règle | Condition | Ajustement |
|-------|-----------|-----------|
| Synergie habitat-rut | H≥70 ET R≥70 | **+8** |
| Proximité alimentation-repos | alimentation<200m ET repos<300m | **+6** |
| Corridor + affût | A≥75 ET T≥65 | **+5** |
| Zone de transition (écotone) | isTransition=true | **+7** |
| Complexité hydro | Confluence ou méandre | **+5** |
| Forte pression humaine | humanPressure>70 | **-12** |
| Position exposée sans couvert | Couvert clairsemé ET pente>20° | **-8** |
| Accès difficile | T<40 | **-5** |
| Peuplement optimal | Tremblaie/Cédrière/Érabière | **+4** |
| Position dominante | Altitude relative >30m | **+3** |

**Niveau 2 — IA (NON CONNECTÉ) :**
- Endpoint prévu : `POST /api/bionic/hybrid/ai-adjust`
- Input : scores + données waypoint + météo + contexte (saison, heure, lune)
- Output attendu : score ajusté + recommandations + confiance + raisonnement

### Conditions de chasse (bionicWeatherEngine.js — 421 lignes)

| Facteur | Impact positif | Impact négatif |
|---------|---------------|----------------|
| **Vent** | 5-15 km/h idéal (+15) | <5 km/h odeurs stagnantes (-10), >25 km/h (-20) |
| **Température** | -5 à 15°C (+10) | <-15°C ou >25°C (-15) |
| **Précipitations** | Légères <2mm (+10, masque bruits) | Fortes >5mm (-15) |
| **Thermiques** | Descendants (+10, odeurs au sol) | Ascendants (-10, risque odeurs) |
| **Front météo** | Front froid (+15, activité gibier) | Instable (-10) |
| **Pression baro** | >1020 hPa stable (+5) | <1000 hPa changement (-5) |

**États thermiques :** Stable / Ascendant / Descendant
**Types de front :** Aucun / Froid / Chaud / Instable
**Rating final :** Excellent(≥70) / Bon(≥50) / Modéré(≥30) / Mauvais(<30)

---

## 1B. MON TERRITOIRE — RAMIFICATIONS

### Strategy Engine (bionicStrategyEngine.js — 497 lignes)

**Projections de score :**
- Score actuel × multiplicateur temporel (aube +15%, crépuscule +12%, journée -5%, nuit -15%)
- Projection +1h et +3h basées sur prévisions météo horaires
- Tendance : amélioration / dégradation / stable
- Heure de pointe calculée dans les 12 prochaines heures

**Chemin d'approche :**
- Direction : opposée au vent (180° de la direction du vent)
- Score discrétion : base 80, vent 8-18 km/h (+10), vent <5 km/h (-15), nuages >60% (+5)
- Risque olfactif : thermiques ascendants=élevé, descendants=faible, neutre=moyen
- Risque visuel : nuit=faible, jour ciel dégagé=élevé

**Mouvement gibier :**
- Corridor principal : basé sur score T + aspect du terrain (opposé à la pente)
- Corridor secondaire : perpendiculaire au principal
- Fenêtre d'arrivée : matin 05:30-08:00 (retour repos), soir 16:30-19:30 (alimentation)
- Impact vent : >25 km/h=pénalité, 8-18 km/h=bonus

**Niveau d'activité :**
- Très élevé : heures pointe + front froid
- Élevé : 05:00-08:00, 17:00-20:00
- Modéré : hors pointe
- Faible : 11:00-14:00
- Très faible : faible + précipitations fortes

**Flags LIVE :**
- `isOptimalNow` : score≥70 ET risques≠élevés ET activité élevée
- `willDegradeSoon` : tendance dégradation ET score -3h > -10 pts
- `isRiskyNow` : risques élevés OU inversion thermique élevée
- `peakWindowActive` : activité élevée ou très élevée

**Recommandations produits :**
- Score saline ≥60 → attractant (automne=urine, été=bloc minéral)
- Score affût ≥70 → camouflage anti-odeur

### Backend knowledge (prêt, non connecté)

| Service backend | Fichier | Rôle | État |
|-----------------|---------|------|------|
| Modèles saisonniers | `seasonal_models.py` | Comportement par saison | Prêt |
| Prédiction mobilité | `mobility_models.py` | Déplacements probables | Prêt |
| Détection corridors | `corridor_models.py` | Axes de déplacement | Prêt |
| Pression humaine | `human_pressure_model.py` | Zones de perturbation | Prêt |
| Zones sécurité | `safety_engine.py` | Zones dangereuses | Prêt |
| Auto-cartographie | `auto_cartography.py` | Hotspots dynamiques | Prêt |
| Scoring habitat | `score_habitat_service.py` | Score habitat terrain réel | Prêt |
| Scoring comportement | `score_behavior_service.py` | Score comportemental | Prêt |
| Scoring densité | `score_density_service.py` | Densité animale | Prêt |
| Scoring mobilité | `score_mobility_service.py` | Mobilité prédite | Prêt |
| Scoring météo | `score_weather_service.py` | Impact météo | Prêt |
| Scoring pression | `score_pressure_service.py` | Impact pression humaine | Prêt |
| Scoring risque | `score_risk_service.py` | Évaluation risques | Prêt |
| Scoring probabilité | `score_probability_service.py` | Probabilité observation | Prêt |
| Heatmap fusion | `heatmap_fusion_service.py` | Carte de chaleur composite | Prêt |
| Heures légales | `legal_hours_service.py` | Heures tir autorisées | Prêt |
| Plan de chasse | `hunt_plan_analyzer_service.py` | Analyse plan de chasse | Prêt |
| Contours organiques | `organic_contour_generator.py` | Génération contours backend | Prêt |

---

## 1C. MON TERRITOIRE — VUE 360°

```
                        ESPACE
                    Topographie ✓(moteur)
                  Végétation ✓(moteur)
                Hydrographie ✓(moteur+exclusion)
              Zones légales ✗(backend prêt)
            Zones pression ✓(moteur)
          Zones sécurité ✗(backend prêt)
        /                              \
      /                                  \
TEMPS                                    COMPORTEMENTS
Heure ✓(multiplicateur)               Déplacements ✓(corridors)
Saison ✓(saison auto)                 Repos ✓(scoring zones)
Météo ✓(Open-Meteo LIVE)              Nourriture ✓(scoring zones)
Cycles ✓(lune calculée)               Reproduction ✓(rut scoring)
Historique ✗(non connecté)            Réactions pression ✓(moteur)
      \                                  /
        \                              /
          DYNAMIQUES ÉCOLOGIQUES
          Ressources ✓(alimentation/NDVI)
          Densités ✗(backend prêt)
          Corridors ✓(scoring+couche)
          Perturbations ✓(pression humaine)
                    |
          DYNAMIQUES HUMAINES
          Déplacements ✗(non connecté)
          Pression ✓(moteur règles)
          Perturbations ✓(exclusion urbain)
          Accès ✓(scoring trails)
                    |
          DYNAMIQUES PRÉDICTIVES
          Hotspots ✗(backend prêt)
          Routes probables ✓(corridor principal+secondaire)
          Fenêtres activité ✓(strategy engine)
                    |
          VALIDATIONS TERRAIN
          Observations ✗(backend prêt, non connecté)
          Écarts ✗(non implémenté)
          Corrections ✗(non implémenté)
                    |
          RISQUES / OPPORTUNITÉS
          Sécurité ✓(risques évaluables)
          Réussite ✗(pas de feedback)
          Détection ✓(risque olfactif/visuel)
          Accessibilité ✓(scoring trajets)
```

**Synthèse Mon Territoire :**
- **Score de complétude** : 60% des moteurs sont implémentés, 35% sont prêts mais non connectés, 5% restent à construire
- **Principale lacune** : Les données terrain RÉELLES (pente, NDVI, peuplement) ne sont pas injectées dans le scoring — les zones sont générées procéduralement sans calibration terrain
- **Force majeure** : Le moteur de scoring est complet et scientifiquement fondé avec 15+ fonctions validées

---

## 2. CARTE INTERACTIVE — CONTENU RÉEL

### 2.1 Fonctionnalités actives (MapPage.jsx — 384 lignes)

| Fonctionnalité | Composant | État |
|----------------|-----------|------|
| Overlay BIONIC V5 | `BionicMapOverlay.jsx` | Fonctionnel (espèce + ON/OFF + exclusion) |
| Waypoints | `WaypointMap` (module territory) | Fonctionnel (affichage, création, navigation) |
| GPS Tracking | `BackgroundTracker` + `GeoSyncToggle` | Fonctionnel (géolocalisation temps réel) |
| Tabs | Carte / Satellite / Groupe | Fonctionnel |
| URL params | `?lat=X&lng=Y&zoom=Z` | Fonctionnel (centrage dynamique) |
| Panneau BIONIC V5 | Espèce + couches + stats | Fonctionnel |
| Fond de carte | Standard + Satellite | Fonctionnel |
| Collaboration | `GroupeTab` | Fonctionnel (synchronisation temps réel) |

### 2.2 Moteurs backend disponibles mais NON affichés

| Moteur | API endpoint | Données disponibles | État UI |
|--------|-------------|---------------------|---------|
| Hotspots dynamiques | `auto_cartography.py` | Points chauds d'activité | **NON affiché** |
| Zones de danger | `safety_engine.py` | Zones de sécurité | **NON affiché** |
| Densité animale | `heatmap_fusion_service.py` | Carte de chaleur | **NON affiché** |
| Corridors fauniques | `corridor_service.py` | Axes de déplacement | **NON affiché** |
| Heures légales | `legal_hours_service.py` | Fenêtres de tir | **NON affiché** |
| Pression humaine | `hunting_pressure.py` | Zones perturbées | **NON affiché** |
| Couches écoforestières | `ecoforestry_layers/` | Peuplements réels | **NON affiché** |
| Couches comportementales | `behavioral_layers/` | Comportement modélisé | **NON affiché** |
| Couches simulation | `simulation_layers/` | Scénarios what-if | **NON affiché** |
| Couches 3D | `layers_3d/` | Terrain 3D | **NON affiché** |
| WMS/Sentinel-2 | `wms_engine/` | Imagerie satellite | **NON affiché** |
| Prévisions faune-météo | `weather_fauna_simulation_engine/` | Simulation comportement | **NON affiché** |

---

## 2A. CARTE INTERACTIVE — ANALYSES

| Analyse | Mon Territoire | Carte Interactive |
|---------|---------------|-------------------|
| Zones organiques V5 | Affiché | Affiché (via BionicMapOverlay) |
| Exclusion terrain | Actif (35 127 entités) | Actif (même moteur) |
| Scoring multi-critères | Calculé | **Non calculé** (pas de waypoints dans l'overlay) |
| Modèle hybride | Disponible | **Non disponible** |
| Conditions météo | Calculé (bionicWeatherEngine) | **Non affiché** |
| Strategy Engine | Disponible | **Non disponible** |
| Heatmap densité | Non affiché | **Non affiché** (backend prêt) |
| Corridors détectés | Couche BIONIC | **Non affiché** (backend prêt) |
| Hotspots | Non affiché | **Non affiché** (backend prêt) |
| Danger zones | Non affiché | **Non affiché** (backend prêt) |

---

## 2B. CARTE INTERACTIVE — RAMIFICATIONS

**Actuellement :** La Carte Interactive est un miroir simplifié de Mon Territoire. Elle utilise le même moteur BIONIC V5 mais sans les analyses avancées.

**Moteurs prêts à brancher :**
- Heatmap fusion → carte de chaleur interactive multi-espèces
- Corridors → lignes de déplacement probables
- Hotspots → marqueurs de zones d'activité intense
- Heures légales → overlay temporel (zones vertes/rouges selon l'heure)
- WMS → fond de carte satellite haute résolution
- Simulation → scénarios "que se passe-t-il si..."

---

## 2C. CARTE INTERACTIVE — VUE 360°

```
                        ESPACE
                    Topographie ✗(3D backend prêt)
                  Végétation ✗(WMS/NDVI backend prêt)
                Hydrographie ✓(exclusion active)
              Zones légales ✗(legal_hours backend prêt)
            Zones pression ✗(hunting_pressure backend prêt)
          Zones sécurité ✗(safety_engine backend prêt)
        /                              \
      /                                  \
TEMPS                                    COMPORTEMENTS
Heure ✗(non affiché)                  Déplacements ✗(corridors backend prêt)
Saison ✗(non affiché)                 Repos ✓(couche BIONIC)
Météo ✗(non affiché)                  Nourriture ✓(couche BIONIC)
Cycles ✗(non affiché)                 Reproduction ✓(couche BIONIC)
Historique ✗(non connecté)            Réactions ✗(non affiché)
      \                                  /
        \                              /
          DYNAMIQUES ÉCOLOGIQUES
          Ressources ✓(couches BIONIC)
          Densités ✗(heatmap backend prêt)
          Corridors ✓(couche BIONIC)
          Perturbations ✗(non affiché)
                    |
          DYNAMIQUES HUMAINES
          GPS tracking ✓(BackgroundTracker)
          Collaboration ✓(GroupeTab)
          Pression ✗(non affiché)
                    |
          DYNAMIQUES PRÉDICTIVES
          Hotspots ✗(backend prêt)
          Routes probables ✗(non affiché)
          Fenêtres activité ✗(non affiché)
                    |
          VALIDATIONS TERRAIN
          Observations ✗(non connecté)
          Waypoints ✓(création/navigation)
                    |
          RISQUES / OPPORTUNITÉS
          Sécurité ✗(non affiché)
          Détection ✗(non affiché)
          Accessibilité ✗(non affiché)
```

**Synthèse Carte Interactive :**
- **Score de complétude** : 25% des capacités sont exposées à l'utilisateur
- **Principale lacune** : La quasi-totalité des moteurs backend sont prêts mais NON connectés à l'UI
- **Force majeure** : GPS tracking temps réel + collaboration groupe + overlay BIONIC V5

---

## 7. COMPARAISON DIRECTE

| Critère | MON TERRITOIRE | CARTE INTERACTIVE |
|---------|---------------|-------------------|
| **Vocation** | Analyse approfondie du territoire personnel | Navigation et interaction terrain temps réel |
| **Zones BIONIC V5** | 15 couches organiques | 15 couches organiques (même moteur) |
| **Exclusion terrain** | Tolérance Zéro (35 127 entités) | Tolérance Zéro (même moteur) |
| **Espèces** | 5 espèces avec filtrage | 5 espèces avec filtrage |
| **Scoring** | Multi-critères complet (6 catégories) | **Non exposé** |
| **Modèle hybride** | Niveau 1 actif, Niveau 2 prévu | **Non disponible** |
| **Météo** | Open-Meteo LIVE (conditions chasse) | **Non affiché** |
| **Stratégie** | Approche, mouvement, risques, produits | **Non disponible** |
| **GPS** | Waypoints | GPS tracking LIVE + collaboration |
| **Hotspots** | Non affiché | Non affiché |
| **3D/Satellite** | Non disponible | Tab Satellite (fond de carte) |
| **Groupe** | Non disponible | Collaboration temps réel |
| **Sidebar** | Complète (espèce, couches, stats, affichage) | Panneau flottant réduit |
| **Données terrain réelles** | **Non connectées** | **Non connectées** |
| **Observations** | Non connectées | Non connectées |
| **Type** | Statique-analytique | Dynamique-interactif |

---

## 8. INTERACTIONS ENTRE LES DEUX CARTES

### Actuellement connecté

| Interaction | Mécanisme | État |
|-------------|-----------|------|
| Moteur BIONIC partagé | `BionicZoneService.js` | Fonctionnel |
| Configuration espèce partagée | `speciesConfig.js` | Fonctionnel |
| Configuration couches partagée | `bionicModules.js` | Fonctionnel |
| Exclusion terrain partagée | Même proxy Overpass + cache | Fonctionnel |
| Navigation croisée | URL params `?lat=&lng=&zoom=` | Fonctionnel |

### NON connecté (à implémenter)

| Interaction | Valeur | Complexité |
|-------------|--------|-----------|
| Waypoints Mon Territoire → Carte Interactive | Voir ses waypoints analysés en contexte terrain | Faible |
| Observations Carte → Mon Territoire | Feedback terrain valide les prédictions | Moyenne |
| Scoring Carte → Mon Territoire | Score LIVE sur la position GPS actuelle | Moyenne |
| Historique Carte → Ajustement modèle | Trajets GPS réels calibrent les corridors | Élevée |
| Comparaison prédiction ↔ observation | Écart mesurable entre modèle et réalité | Élevée |
| Recommandations croisées | "Basé sur tes 12 sorties, ce waypoint est optimal" | Élevée |

---

## 9. SYNTHÈSE FORCES / FAIBLESSES / OPPORTUNITÉS / RISQUES

### FORCES

| Force | Détail |
|-------|--------|
| **Moteur de scoring complet** | 15+ fonctions scientifiquement fondées couvrant pente, eau, NDVI, peuplements, thermique, visibilité, corridors, sentiers |
| **Exclusion Tolérance Zéro** | 35 127 entités, ring assembly pour les grandes masses d'eau, buffer type-spécifique |
| **Formes organiques strictes** | 65 vertices, validation compacité + variance, aucune forme géométrique simple |
| **Weather Engine temps réel** | Open-Meteo intégré, état thermique, front météo, conditions de chasse scorées |
| **Strategy Engine** | Approche, mouvement gibier, risques, produits, flags LIVE, projections +1h/+3h |
| **Modèle hybride** | 10 règles d'ajustement contextuelles, architecture prête pour IA Niveau 2 |
| **5 espèces différenciées** | Couches et pondérations distinctes par espèce |
| **Backend riche** | 18+ services de scoring/analyse prêts à connecter |
| **14 types de peuplements** | Matrice de scoring 14×4 (type × contexte) |
| **Validation AVANT rendu** | Zones JAMAIS affichées sans exclusions chargées |

### FAIBLESSES

| Faiblesse | Impact | Criticité |
|-----------|--------|-----------|
| **Données terrain réelles non injectées** | Le scoring calcule sur des données simulées, pas sur la topographie/végétation réelle | CRITIQUE |
| **IA Niveau 2 non connectée** | Le modèle hybride tourne en mode règles uniquement | ÉLEVÉE |
| **Observations non connectées aux zones** | Aucune boucle feedback réel → modèle | ÉLEVÉE |
| **Hotspots non affichés** | Moteur prêt mais invisible pour l'utilisateur | MOYENNE |
| **Carte Interactive sous-exploitée** | 75% des capacités backend non exposées | MOYENNE |
| **Pas d'historique exploitable** | Les sorties GPS ne calibrent pas le modèle | MOYENNE |
| **Performance 35 000+ entités** | Temps de chargement perceptible au changement viewport | FAIBLE |

### OPPORTUNITÉS

| Opportunité | Effort | Impact |
|-------------|--------|--------|
| **Connecter données terrain réelles** (API élévation, NDVI satellite) | Élevé | TRANSFORMATEUR |
| **Afficher heatmap densité** sur Carte Interactive | Moyen | ÉLEVÉ |
| **Afficher corridors** sur les deux cartes | Moyen | ÉLEVÉ |
| **Dashboard conditions saisonnières** (PHASE E) | Moyen | ÉLEVÉ |
| **Mode Comparaison Espèces** (split-screen) | Moyen | ÉLEVÉ |
| **Connecter IA Niveau 2** via LLM | Moyen | ÉLEVÉ |
| **Boucle feedback** observations → ajustement modèle | Élevé | TRANSFORMATEUR |
| **Heures légales overlay** | Faible | MOYEN |
| **Imagerie WMS/Sentinel-2** | Moyen | MOYEN |

### RISQUES

| Risque | Probabilité | Impact | Mitigation |
|--------|------------|--------|-----------|
| **Rate limiting Overpass** | Confirmé (429 observé) | Données manquantes | Cache 24h + tiling |
| **Performance client** | Moyen | UX dégradée | Spatial hashing + grid limité 20×20 |
| **Complexité croissante** | Élevé | Maintenabilité | Architecture modulaire strict |
| **Données OSM incomplètes** | Moyen | Faux négatifs exclusion | Buffer de sécurité + double protection |

---

## VUE 360° GLOBALE — SYNTHÈSE FINALE

```
┌─────────────────────────────────────────────────────────┐
│                   BIONIC V5 STRICT                       │
│                                                          │
│  ┌──────────────────┐     ┌──────────────────────┐      │
│  │  MON TERRITOIRE   │     │  CARTE INTERACTIVE    │      │
│  │                    │     │                        │      │
│  │  Analyse profonde  │◄───►│  Navigation terrain    │      │
│  │  15 couches        │     │  GPS LIVE              │      │
│  │  Scoring H-R-S-A-T-P    │  Collaboration         │      │
│  │  Strategy Engine   │     │  Waypoints             │      │
│  │  Weather LIVE      │     │  Overlay BIONIC        │      │
│  │  Modèle hybride    │     │                        │      │
│  └────────┬───────────┘     └──────────┬─────────────┘      │
│           │                             │                    │
│           ▼                             ▼                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              MOTEUR PARTAGÉ                          │    │
│  │  BionicZoneService.js + speciesConfig + bionicModules│    │
│  │  Exclusion Tolérance Zéro (35 127 entités)          │    │
│  │  Proxy Overpass + Ring Assembly + Cache              │    │
│  └─────────────────────────────────────────────────────┘    │
│           │                             │                    │
│           ▼                             ▼                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              BACKEND KNOWLEDGE (18+ services)        │    │
│  │  scoring/ (8 services) │ seasonal/ │ corridors/     │    │
│  │  mobility/ │ pressure/ │ safety/ │ observations/    │    │
│  │  heatmap_fusion │ legal_hours │ hunt_plan          │    │
│  │  ► 65% PRÊTS mais NON CONNECTÉS à l'UI ◄          │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  COMPLÉTUDE: Mon Territoire 60% │ Carte Interactive 25%     │
│  PRIORITÉ: Connecter données réelles → Scoring → Dashboard  │
└──────────────────────────────────────────────────────────────┘
```

**Conclusion opérationnelle :**
Le système BIONIC V5 possède une architecture solide avec des moteurs scientifiquement fondés. La principale transformation à effectuer est le passage de **données simulées à des données terrain réelles** (topographie, NDVI, peuplements), suivi de l'**exposition des moteurs backend** déjà prêts vers l'UI. La Carte Interactive est le module le plus sous-exploité avec 75% de capacités dormantes.
