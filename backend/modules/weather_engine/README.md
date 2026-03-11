# Weather Engine

## Module d'Analyse Météorologique pour la Chasse

### Version: 1.0.0
### Phase: 2 (Core Engines)
### API Prefix: `/api/v1/weather`

---

## Description

Le **Weather Engine** analyse les conditions météorologiques et calcule leur impact sur le comportement du gibier et les conditions de chasse.

---

## Endpoints API

### 1. Info Module
```
GET /api/v1/weather/
```

### 2. Analyse Conditions
```
POST /api/v1/weather/analyze
```
Analyse complète des conditions météo.

**Body:**
```json
{
  "temperature": 10,
  "humidity": 60,
  "wind_speed": 15,
  "wind_direction": "NW",
  "pressure": 1013,
  "precipitation": 0,
  "condition": "Partiellement nuageux"
}
```

### 3. Score Rapide
```
GET /api/v1/weather/score
```
Calcul rapide du score de chasse.

**Paramètres:**
- `temperature` (float): Température en °C
- `humidity` (float): Humidité %
- `wind_speed` (float): Vitesse du vent km/h
- `wind_direction` (string): Direction du vent
- `pressure` (float): Pression hPa
- `precipitation` (float): Précipitations mm

### 4. Phase Lunaire
```
GET /api/v1/weather/moon
```
Retourne la phase lunaire et son impact sur la chasse.

### 5. Conditions Optimales
```
GET /api/v1/weather/optimal
```
Retourne les conditions optimales de référence.

### 6. Meilleurs Horaires
```
GET /api/v1/weather/times
```
Retourne les meilleurs horaires selon la météo.

---

## Conditions Optimales

| Paramètre | Min | Max | Idéal |
|-----------|-----|-----|-------|
| Température | -5°C | 15°C | 5°C |
| Humidité | 40% | 80% | 60% |
| Vent | 0 km/h | 20 km/h | 8 km/h |

---

## Calcul du Score

Le score de chasse (0-10) est calculé avec les pondérations:
- Température: 30%
- Vent: 25%
- Pression: 20%
- Humidité: 15%
- Précipitations: 10%

---

## Tests

```bash
pytest tests/test_weather_engine.py -v
```

---

*HUNTIQ V3 - Weather Engine - Phase 2*
