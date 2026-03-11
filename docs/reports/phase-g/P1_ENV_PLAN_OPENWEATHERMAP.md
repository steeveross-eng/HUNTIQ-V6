# P1-ENV: PLAN D'INTÉGRATION OPENWEATHERMAP
## PHASE G - P1 PRÉPARATION
### Version: 1.0.0-draft | Date: Décembre 2025 | Status: EN ATTENTE GO

---

## 1. RÉSUMÉ EXÉCUTIF

| Attribut | Valeur |
|----------|--------|
| **Module** | P1-ENV (Environmental Data Bridge) |
| **Objectif** | Intégrer les données météo temps réel via OpenWeatherMap API |
| **Priorité** | P1 - HIGH |
| **Dépendances** | P0-STABLE (validé ✅) |
| **Effort estimé** | 3-4 jours développement |
| **Status** | EN ATTENTE GO COPILOT MAÎTRE |

---

## 2. OBJECTIFS

### 2.1 Objectifs Fonctionnels

| # | Objectif | Priorité |
|---|----------|----------|
| O1 | Récupérer les données météo temps réel pour une position | CRITICAL |
| O2 | Alimenter automatiquement le WeatherOverride des modules P0 | CRITICAL |
| O3 | Fournir des prévisions 24h-48h pour planification | HIGH |
| O4 | Détecter automatiquement les conditions extrêmes | HIGH |
| O5 | Cacher les données pour optimiser les appels API | MEDIUM |

### 2.2 Objectifs Non-Fonctionnels

| # | Objectif | Cible |
|---|----------|-------|
| NF1 | Latence API < 500ms | P95 |
| NF2 | Cache TTL 15 minutes | Standard |
| NF3 | Fallback si API indisponible | 100% graceful |
| NF4 | Rate limiting respecté | 60 calls/min |

---

## 3. ARCHITECTURE PROPOSÉE

### 3.1 Diagramme de Composants

```
┌─────────────────────────────────────────────────────────────────┐
│                    BIONIC ENGINE P1-ENV                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  WeatherBridgeService                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │   │
│  │  │ OWM Client  │  │ Cache Layer │  │ Fallback Handler│   │   │
│  │  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘   │   │
│  │         │                │                   │            │   │
│  │         └────────────────┼───────────────────┘            │   │
│  │                          │                                │   │
│  │  ┌───────────────────────┴────────────────────────────┐  │   │
│  │  │              WeatherDataTransformer                 │  │   │
│  │  │  OWM Response → WeatherOverride (P0 compatible)     │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              P0-STABLE (Predictive Territorial)           │   │
│  │              weather_override auto-alimenté               │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  OpenWeatherMap API │
                    │  (External Service) │
                    └─────────────────────┘
```

### 3.2 Structure des Fichiers

```
/app/backend/modules/bionic_engine_p0/
├── services/                          # NOUVEAU
│   ├── __init__.py
│   └── weather_bridge.py              # WeatherBridgeService
├── clients/                           # NOUVEAU
│   ├── __init__.py
│   └── openweathermap_client.py       # Client OWM
└── cache/                             # NOUVEAU (optionnel)
    └── weather_cache.py               # Redis/Memory cache
```

---

## 4. CONTRAT API OPENWEATHERMAP

### 4.1 Endpoints Utilisés

| Endpoint | Usage | Fréquence |
|----------|-------|-----------|
| `/data/2.5/weather` | Données actuelles | À chaque requête (avec cache) |
| `/data/2.5/forecast` | Prévisions 5 jours | Rafraîchissement horaire |
| `/data/2.5/onecall` | Données complètes | Alternative premium |

### 4.2 Mapping OWM → WeatherOverride

| Champ OWM | Champ WeatherOverride | Transformation |
|-----------|----------------------|----------------|
| `main.temp` | `temperature` | Kelvin → Celsius |
| `wind.speed` | `wind_speed` | m/s → km/h |
| `main.pressure` | `pressure` | hPa direct |
| `rain.1h` ou `snow.1h` | `precipitation` | mm/h direct |
| `clouds.all` | (nouveau) `cloud_cover` | % direct |
| `main.humidity` | (nouveau) `humidity` | % direct |

### 4.3 Exemple de Réponse Transformée

```json
{
  "weather_override": {
    "temperature": 5.2,
    "wind_speed": 15.5,
    "pressure": 1018,
    "precipitation": 0.5,
    "cloud_cover": 75,
    "humidity": 82
  },
  "conditions": {
    "is_extreme": false,
    "extreme_type": null,
    "weather_description": "light rain",
    "visibility_km": 8.5
  },
  "forecast_24h": [
    {"hour": 0, "temp": 4.0, "precip_prob": 0.3},
    {"hour": 6, "temp": 2.5, "precip_prob": 0.1},
    ...
  ],
  "metadata": {
    "source": "openweathermap",
    "timestamp": "2025-12-21T10:00:00Z",
    "cache_hit": false,
    "api_calls_remaining": 58
  }
}
```

---

## 5. GESTION DES CREDENTIALS

### 5.1 Configuration

| Variable | Source | Fallback |
|----------|--------|----------|
| `OWM_API_KEY` | Environment variable | Erreur si absent |
| `OWM_BASE_URL` | Environment variable | `https://api.openweathermap.org` |
| `OWM_CACHE_TTL` | Environment variable | 900 (15 min) |

### 5.2 Sécurité (G-SEC)

| Mesure | Implémentation |
|--------|----------------|
| API Key non exposée | Via env, jamais en code |
| Rate limiting client | 60 req/min max |
| Timeout | 5s par requête |
| Retry policy | 3 tentatives avec backoff |

---

## 6. FALLBACK STRATEGY

### 6.1 Scénarios de Fallback

| Scénario | Action | Impact Score |
|----------|--------|--------------|
| API timeout | Utiliser cache expiré | Confidence -10% |
| API erreur 4xx | Utiliser valeurs par défaut région | Confidence -20% |
| API erreur 5xx | Retry puis cache | Confidence -15% |
| Pas de cache | Valeurs saisonnières moyennes | Confidence -30% |

### 6.2 Valeurs Par Défaut (Québec)

| Saison | Temp (°C) | Vent (km/h) | Pression (hPa) |
|--------|-----------|-------------|----------------|
| Printemps (Mar-Mai) | 8 | 15 | 1013 |
| Été (Jun-Août) | 20 | 12 | 1015 |
| Automne (Sep-Nov) | 10 | 18 | 1012 |
| Hiver (Déc-Fév) | -10 | 20 | 1020 |

---

## 7. INTÉGRATION AVEC P0-STABLE

### 7.1 Mode d'Intégration

```python
# Option A: Injection automatique (recommandé)
@router.post("/territorial/score")
async def calculate_territorial_score(request: TerritorialScoreInput):
    # Si weather_override non fourni, récupérer automatiquement
    if request.weather_override is None:
        weather_bridge = WeatherBridgeService()
        request.weather_override = await weather_bridge.get_current_weather(
            latitude=request.latitude,
            longitude=request.longitude
        )
    
    result = _pt_service.calculate_score(...)
```

### 7.2 Nouveau Paramètre API

| Paramètre | Type | Default | Description |
|-----------|------|---------|-------------|
| `auto_weather` | bool | `true` | Récupérer météo auto si weather_override absent |

---

## 8. TESTS G-QA

### 8.1 Tests Unitaires Requis

| Test | Description |
|------|-------------|
| test_owm_client_parse_response | Parsing réponse OWM |
| test_weather_transformer | Transformation → WeatherOverride |
| test_cache_hit | Cache fonctionnel |
| test_cache_expiry | Expiration cache |
| test_fallback_timeout | Fallback sur timeout |
| test_fallback_error | Fallback sur erreur |
| test_rate_limiting | Respect rate limit |

### 8.2 Tests d'Intégration

| Test | Description |
|------|-------------|
| test_owm_live_call | Appel réel OWM (staging key) |
| test_pt_with_auto_weather | PT avec météo auto |
| test_bm_with_auto_weather | BM avec météo auto |

---

## 9. ESTIMATION EFFORT

| Phase | Tâche | Durée |
|-------|-------|-------|
| 1 | Client OWM + Transformer | 4h |
| 2 | Cache layer | 2h |
| 3 | Fallback handler | 2h |
| 4 | Intégration P0 | 2h |
| 5 | Tests unitaires (8) | 3h |
| 6 | Tests intégration (3) | 2h |
| 7 | Documentation G-DOC | 1h |
| **Total** | | **16h (~2 jours)** |

---

## 10. RISQUES ET MITIGATIONS

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| API OWM indisponible | LOW | HIGH | Fallback robuste + cache |
| Rate limit atteint | MEDIUM | MEDIUM | Cache 15min + monitoring |
| Données inexactes région | LOW | LOW | Validation croisée |
| Coût API (plan gratuit) | LOW | LOW | 1000 calls/jour suffisants |

---

## 11. LIVRABLES ATTENDUS

| # | Livrable | Type |
|---|----------|------|
| 1 | `openweathermap_client.py` | Code |
| 2 | `weather_bridge.py` | Code |
| 3 | `weather_cache.py` | Code |
| 4 | `test_weather_bridge.py` | Tests |
| 5 | `P1_ENV_CONTRACT.json` | Contrat |
| 6 | Documentation mise à jour | G-DOC |

---

## 12. CHECKLIST PRÉ-IMPLÉMENTATION

| # | Item | Status |
|---|------|--------|
| 1 | GO COPILOT MAÎTRE | ⏳ EN ATTENTE |
| 2 | Clé API OWM disponible | ⏳ À CONFIRMER |
| 3 | Plan validé | ⏳ EN ATTENTE |
| 4 | Contrat JSON approuvé | ⏳ EN ATTENTE |

---

*Document préparé conformément aux normes G-DOC Phase G*
*Status: DRAFT - EN ATTENTE VALIDATION COPILOT MAÎTRE*
