# JOURNAL P1 — BIONIC Migration & Stabilisation

## Chronologie des événements

### 2026-03-10 — Incident P0 : Zones dans l'eau
- **Symptôme**: Zones générées dans les plans d'eau
- **Cause racine**: `build_exclusion_unions` n'incluait pas `filtered_out`
- **Fix**: Ajout des exclusions filtrées dans les unions Shapely
- **Tests**: 6/6 (`test_water_exclusion_p0.py`)
- **Statut**: RÉSOLU

### 2026-03-10 — BIONIC Compliance Engine (BCE)
- 10 validateurs implémentés
- Golden State certifié
- 55+ tests (`test_bce_compliance.py`)
- API: `/api/bce/validate`, `/api/bce/certify`, `/api/bce/validate-with-zones`
- **Statut**: OPÉRATIONNEL

### 2026-03-10 — Diagnostics de Rejet
- Backend propage `rejection_diagnostics` dans `/api/v1/bionic/organic-zones`
- Frontend affiche dans `SidePanelZones.jsx`
- **Statut**: OPÉRATIONNEL

### 2026-03-10 — Migration Carte Interactive → Mon Territoire
- 7 moteurs canoniques migrés
- Validé et certifié par le BCE
- **Statut**: COMPLÉTÉ

### 2026-03-10 — Incident P0 : Waypoint rural sans zones
- **Symptôme**: Waypoint (47.0, -72.28) en zone rurale affiche 0 zones
- **Cause racine**: Marges d'exclusion V6 trop agressives pour le contexte rural
- **Fix**: Création du moteur V7 exclusif avec marges RÉDUITES
  - `exclusion_config_v7.py`: Eau (rivière 40m, lac 75m, ruisseau 10m), Routes (principale 75m, secondaire 35m, chemin 10m), Habitations (120m, agricoles 75m), Végétation (densité min 0.20)
  - `exclusion_engine_v7.py`: Moteur d'exclusion V7 avec seuils intersection relaxés et pression anthropique adaptée au rural
  - `pipeline_v7.py` modifié pour utiliser exclusivement V7
- **Validation**: 3 waypoints testés — Rural (8 zones), Forêt (18 zones), Périurbain (0 zones correctement)
- **BCE**: PASS (9/10, water WARN normal)
- **Tests**: 19/19 (`test_v7_p0_regression.py`)
- **Statut**: RÉSOLU

### 2026-03-10 — Verrouillage moteur V7
- `ENGINE_V7_LOCKED=true` ajouté dans `.env`
- Fichiers V6 (`exclusion_config_v6.py`, `exclusion_engine_v6.py`) marqués LEGACY FIGÉ
- `exclusion_geometry_v6.py` conservé (fonctions géométriques partagées)
- Golden State re-certifié pour V7
- **Statut**: VERROUILLÉ

### 2026-03-10 — V8.2 : Météo Dynamique (OpenWeatherMap)
- **Service**: `weather_service_v1.py` avec cache TTL 30 minutes
  - Cache in-memory avec clé `weather:{lat}:{lng}` arrondi à 2 décimales
  - Max 1 appel OWM / 30 min par coordonnée
  - OWM_API_KEY lu depuis `.env`, jamais loggée
- **Endpoints**:
  - `GET /api/v1/weather/now?lat=X&lng=Y` — Météo actuelle
  - `GET /api/v1/weather/forecast?lat=X&lng=Y` — Prévisions 5j/3h
  - `GET /api/v1/weather/influence?lat=X&lng=Y` — Influence météo sur scores biologiques
  - `GET /api/v1/weather/cache-stats` — Statistiques cache
- **Hook scoring V7**: `compute_weather_influence()` calcule des multiplicateurs [0.7, 1.3] par catégorie :
  - repos: pluie/froid → augmenté (animal se réfugie)
  - alimentation: conditions modérées → optimal
  - corridors: vent fort → réduit
  - rut: très peu influencé (hormonal)
  - habitats: légèrement modulé par confort thermique
- **Frontend**: `bionicWeatherEngine.js` modifié pour utiliser backend OWM en priorité, fallback Open-Meteo
- **Tests**: 8/8 (testing agent iteration 157)
- **Statut**: OPÉRATIONNEL

## Fichiers legacy gelés
| Fichier | Date gel | Remplacé par |
|---------|----------|-------------|
| `exclusion_config_v6.py` | 2026-03-10 | `exclusion_config_v7.py` |
| `exclusion_engine_v6.py` | 2026-03-10 | `exclusion_engine_v7.py` |

## Compteur de tests
| Suite | Tests | Statut |
|-------|-------|--------|
| V7 P0 Regression | 19 | PASS |
| BCE Compliance | 55 | PASS |
| Water Exclusion | 6 | PASS |
| Weather V8.2 | 8 | PASS |
| **Total** | **88** | **PASS** |
