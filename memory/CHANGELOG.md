# BIONIC V5 — CHANGELOG

## [2026-02-24] PHASE D — Consolidation & Pré-Optimisation

### D.1 — Multi-Factor Scoring Engine
- `multifactor_scoring_engine.py` — Score composite combinant Phase B + Phase C
- Pondération dynamique selon saison, heure, température
- Recommandations contextuelles et niveau de risque
- Endpoint: GET `/phase-d/multifactor-score`

### D.2 — Dynamic Layer Generator
- `dynamic_layer_generator.py` — 4 couches dynamiques Leaflet-ready
- Couches: calving_exclusion, thermal_refuge, pressure_overlay, seasonal_influence
- Styles (color, opacity) adaptatifs selon l'intensité
- Endpoint: GET `/phase-d/dynamic-layers`

### D.3 — Knowledge Layer Normalizer
- `knowledge_normalizer.py` — Validation de 8 modules (100% santé)
- Cross-validation: phase_c_complete, phase_d_ready, calibration_ready, phase_g_ready
- Endpoint: GET `/phase-d/knowledge-integrity`

### Canvas Données Terrain
- Document de référence: `/canvas_donnees_terrain_bionic_v5.md`
- 17 colonnes documentées, formats FR/EN, exemples complets
- Lien d'accès depuis CalibrationDashboard

### Tests
- Backend: 34/34 tests passés (100%)
- Frontend: 12/12 tests passés (100%)
- Non-régression: tous endpoints précédents fonctionnels

---

## [2026-02-24] Import CSV/Excel — Calibration MASTER

### Import en lot
- `import_service.py` — Parser CSV/Excel sécurisé avec validation stricte
- Formats: CSV (virgule, point-virgule, tabulation), Excel (.xlsx)
- Noms de colonnes FR supportés (espèce, comportement, lat, date)
- Normalisation automatique espèces et comportements
- Traçabilité: batch_id + source_ids sur chaque import
- Limites: 10 MB, 5000 lignes

### Endpoints
- `POST /calibration/observations/import` — Upload et import de fichier
- `GET /calibration/import/template` — Modèle CSV téléchargeable

### Frontend
- Panneau d'import dans CalibrationDashboard (bouton "Import")
- Zone drag-and-drop pour fichiers
- Téléchargement template CSV
- Rapport d'import (succès, erreurs, batch_id)

### Tests
- Backend: 27/27 tests passés (100%)
- Frontend: 10/10 tests passés (100%)

---

## [2026-02-24] Calibration MASTER + Nettoyage + PHASE G

### Infrastructure de Calibration MASTER
- `CalibrationService` — Service MongoDB CRUD pour observations terrain (versionné, source_ids)
- Endpoints observation CRUD: POST/GET/GET{id}/DELETE `/calibration/observations`
- Endpoint métriques: GET `/calibration/observations-metrics`
- Endpoint statut: GET `/calibration/calibration-status`
- Formulaire d'observation terrain intégré à `CalibrationDashboard.jsx`
- Liste interactive des observations avec statut, suppression

### Nettoyage PHASE C
- `seasonal_models.py` documenté comme module fondation (NON supprimé — requis par unified_scoring_service)
- Header clarifié: rôle de module de base, exports critiques listés

### Préparation PHASE G
- `phase_g_validation.py` — Structure multi-années/multi-espèces
- Profils: orignal (Tier 1, 50 obs min), cerf_de_virginie (Tier 2, 30), ours_noir (Tier 2, 25)
- Endpoints: GET `/validation/phase-g/plan` et `/validation/phase-g/progress`

### Tests
- Backend: 21/21 tests passés (100%)
- Frontend: 10/10 tests passés (100%)
- Non-régression: Phase C (seasonal/status, seasonal/health) toujours fonctionnels

---

## [2026-02-24] PHASE C — Intégration Frontend

### Nouveaux composants
- `SeasonalFactorsPanel.jsx` — Panneau d'indicateurs visuels pour les 4 facteurs saisonniers (C.1-C.4)
- Accordéon "Facteurs Saisonniers" dans `MonTerritoireBionicPage.jsx` avec badge PHASE C
- Famille `seasonal_factors` dans `LayerControlPanel.jsx` (4 sous-couches: calving, dispersal, thermal, pressure)
- Intégration dans `CarteBionic.jsx` AnalysisInfoPanel

### Nouveaux endpoints API
- `GET /api/v1/bionic/seasonal/status` — Statut temps réel des facteurs saisonniers
- `GET /api/v1/bionic/seasonal/health` — Health check modules PHASE C

### Tests
- Backend: 14/14 tests passés (100%)
- Frontend: Tous les éléments UI PHASE C vérifiés (100%)
- Non-régression: Endpoint analyze_waypoint toujours fonctionnel

---

## [2026-02-24] PHASE C — Modèles Saisonniers Knowledge Layer

### C.1 — Calving/Fawning Models (Mise bas)
- **Fichier:** `/app/backend/modules/bionic_engine_p0/knowledge/seasonal/calving_models.py`
- **Modèles:** 10 CalvingPeriod (moose, deer, bear, elk × régions)
- **Fonctionnalités:**
  - `CalvingModelRegistry.get_model(species, region)`
  - `CalvingModelRegistry.is_calving_active(species, region, date)`
  - `CalvingModelRegistry.get_calving_modifier(species, region, date, type)`
- **Source IDs:** SRC-MFFP-CALVING-001, SRC-LAVAL-REPRO-001, SRC-NDA-FAWNING-001, etc.

### C.2 — Juvenile Dispersal Models (Dispersion juvénile)
- **Fichier:** `/app/backend/modules/bionic_engine_p0/knowledge/seasonal/juvenile_dispersion.py`
- **Patterns:** 10 DispersalPattern (4 espèces × sexe × régions)
- **Fonctionnalités:**
  - `JuvenileDispersalRegistry.get_patterns(species, region, sex)`
  - `JuvenileDispersalRegistry.calculate_dispersal_risk(species, region, sex, birth_date, check_date)`
- **Données clés:** Distance moyenne, mortalité, déclencheurs, road_crossing_frequency

### C.3 — Thermal Stress Models (Stress thermique été)
- **Fichier:** `/app/backend/modules/bionic_engine_p0/knowledge/seasonal/thermal_stress.py`
- **Profils:** 4 ThermalStressProfile complets
- **Seuils par espèce:**
  - Orignal: CRITICAL (onset 17°C, critical 30°C)
  - Wapiti: HIGH (onset 22°C, critical 35°C)
  - Cerf: MODERATE (onset 25°C, critical 38°C)
  - Ours: LOW (onset 32°C, critical 42°C)
- **Fonctionnalités:**
  - `ThermalStressRegistry.calculate_stress(species, temp, humidity, hour, month)`
  - Retourne: stress_level, modifiers, recommended_refuges

### C.4 — Hunting Pressure Models (Pression de chasse réelle)
- **Fichier:** `/app/backend/modules/bionic_engine_p0/knowledge/pressure/hunting_pressure.py`
- **Profils:** 4 HuntingPressureProfile + 3 HuntingSeasonConfig
- **Fonctionnalités:**
  - `HuntingPressureRegistry.calculate_pressure_impact(species, intensity, hour, is_weekend)`
  - `HuntingPressureRegistry.is_hunting_season(species, region, date)`
- **Données clés:** human_detection_distance_m, flight_distance_m, nocturnal_shift_threshold

---

## [2026-02-24] Correction P0 — Water Exclusion Rule

### Règle BIONIC V5: Corridors ne traversent JAMAIS de grandes masses d'eau
- **Fichier:** `/app/backend/modules/bionic_engine_p0/knowledge/terrain/water_exclusion.py`
- **Service:** WaterExclusionService avec pipeline de validation
- **Intégration:** corridor_service.py, layer_aggregator_service.py
- **Résultats:** VALID, REROUTED (3 tentatives max), REJECTED
- **Tests:** 100% passés (17/17 backend)

---

## [2026-02-24] Correction P0 — UI/UX Cartes

### Refonte visuelle conforme BIONIC V5
- **Pages:** `/map`, `/mon-territoire-bionic`
- **Corrections:**
  - Sidebar accordéons Shadcn/UI (5 sections)
  - Cartes pleine grandeur
  - Titres "PHASE F"
  - 11 panes Leaflet pour superposabilité
- **Tests:** 100% passés (8/8 frontend)

---

## État actuel: MODE PRÉ-MASTER STABILISÉ

- PHASE F: VERROUILLÉE (136/136 tests)
- PHASE C: COMPLÉTÉE (35/35 tests)
- Calibration MASTER: En attente données terrain réelles
