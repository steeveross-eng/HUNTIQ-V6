# Legal Time Engine

## Module de Calcul des Heures Légales de Chasse

### Version: 1.0.0
### Phase: 8 (Plan Maître BIONIC)
### API Prefix: `/api/v1/legal-time`

---

## Description

Le **Legal Time Engine** calcule les heures légales de chasse basées sur les heures de lever et coucher du soleil, conformément au Règlement sur la chasse du Québec.

### Règlementation Québec
- **Début légal**: 30 minutes AVANT le lever du soleil
- **Fin légale**: 30 minutes APRÈS le coucher du soleil

---

## Installation

Ce module utilise la bibliothèque `astral` pour les calculs astronomiques précis.

```bash
pip install astral
```

---

## Configuration

### Localisation par défaut
```python
DEFAULT_LOCATION = {
    "latitude": 46.8139,      # Québec, QC
    "longitude": -71.2080,
    "timezone": "America/Toronto"
}
```

---

## Endpoints API

### 1. Info Module
```
GET /api/v1/legal-time/
```
Retourne les informations du module et la configuration.

**Réponse:**
```json
{
  "module": "legal_time_engine",
  "version": "1.0.0",
  "regulations": {
    "jurisdiction": "Québec, Canada",
    "rule": "30 min avant lever - 30 min après coucher"
  },
  "default_location": {...}
}
```

---

### 2. Fenêtre Légale
```
GET /api/v1/legal-time/legal-window
```
Calcule la fenêtre de chasse légale pour une date et localisation.

**Paramètres:**
| Param | Type | Défaut | Description |
|-------|------|--------|-------------|
| `date` | string | aujourd'hui | Date au format YYYY-MM-DD |
| `lat` | float | 46.8139 | Latitude |
| `lng` | float | -71.2080 | Longitude |
| `timezone` | string | America/Toronto | Fuseau horaire |

**Réponse:**
```json
{
  "success": true,
  "date": "2026-02-09",
  "legal_window": {
    "start_time": "06:28",
    "end_time": "17:30",
    "duration_hours": 11.0,
    "sunrise": "06:58",
    "sunset": "17:00"
  },
  "status": {
    "is_currently_legal": true,
    "current_status": "legal"
  }
}
```

---

### 3. Heures Solaires
```
GET /api/v1/legal-time/sun-times
```
Retourne les heures de lever, coucher, aube et crépuscule.

**Réponse:**
```json
{
  "success": true,
  "sun_times": {
    "sunrise": "06:58",
    "sunset": "17:00",
    "dawn": "06:25",
    "dusk": "17:33",
    "day_length_hours": 10.0
  }
}
```

---

### 4. Vérification Temps Réel
```
GET /api/v1/legal-time/check
```
Vérifie si la chasse est actuellement légale.

**Réponse:**
```json
{
  "success": true,
  "current_time": "14:30:00",
  "is_legal": true,
  "message": "Période légale. 180 minutes restantes.",
  "legal_window": {
    "start": "06:28",
    "end": "17:30"
  }
}
```

---

### 5. Créneaux Recommandés
```
GET /api/v1/legal-time/recommended-slots
```
Retourne les meilleurs créneaux de chasse dans la fenêtre légale.

**Réponse:**
```json
{
  "success": true,
  "slots": [
    {
      "period": "Aube",
      "start_time": "06:28",
      "end_time": "08:58",
      "score": 95,
      "light_condition": "dawn",
      "recommendation": "Période optimale"
    },
    {
      "period": "Crépuscule",
      "start_time": "15:00",
      "end_time": "17:30",
      "score": 90,
      "light_condition": "dusk",
      "recommendation": "Excellente période"
    }
  ]
}
```

---

### 6. Programme Journalier
```
GET /api/v1/legal-time/schedule
```
Retourne un programme complet pour la journée.

---

### 7. Prévisions Multi-jours
```
GET /api/v1/legal-time/forecast?days=7
```
Retourne les fenêtres légales pour plusieurs jours.

**Paramètres:**
| Param | Type | Défaut | Min | Max |
|-------|------|--------|-----|-----|
| `days` | int | 7 | 1 | 14 |

---

## Structure des Fichiers

```
legal_time_engine/
├── __init__.py           # Export du router
└── v1/
    ├── __init__.py       # Exports v1
    ├── router.py         # Endpoints FastAPI
    ├── service.py        # Logique métier
    └── models.py         # Modèles Pydantic
```

---

## Modèles de Données

### LocationInput
```python
class LocationInput(BaseModel):
    latitude: float = 46.8139
    longitude: float = -71.2080
    timezone: str = "America/Toronto"
```

### LegalHuntingWindow
```python
class LegalHuntingWindow(BaseModel):
    date: date
    start_time: time        # 30 min avant lever
    end_time: time          # 30 min après coucher
    duration_minutes: int
    sunrise: time
    sunset: time
    is_currently_legal: bool
    current_status: str     # "before_legal", "legal", "after_legal"
```

### HuntingTimeSlot
```python
class HuntingTimeSlot(BaseModel):
    period_name: str        # "Aube", "Crépuscule", etc.
    start_time: time
    end_time: time
    score: int              # 0-100
    is_legal: bool
    light_condition: str    # "dawn", "daylight", "dusk"
    recommendation: str
```

---

## Intégration Frontend

### Service JavaScript
```javascript
import { LegalTimeService } from '../modules/legaltime';

// Obtenir la fenêtre légale
const window = await LegalTimeService.getLegalWindow();

// Vérifier si légal maintenant
const status = await LegalTimeService.checkLegalNow();

// Obtenir les créneaux recommandés
const slots = await LegalTimeService.getRecommendedSlots();
```

### Composants React
- `LegalTimeWidget` - Widget complet avec toutes les infos
- `LegalTimeBar` - Barre compacte pour headers

---

## Tests

Exécuter les tests unitaires:
```bash
cd /app/backend
pytest tests/test_legal_time_engine.py -v
```

---

## Exemples d'Utilisation

### Python
```python
from modules.legal_time_engine.v1.service import LegalTimeService
from datetime import date

service = LegalTimeService()

# Obtenir la fenêtre légale
window = service.get_legal_hunting_window(date.today())
print(f"Début: {window.start_time}")
print(f"Fin: {window.end_time}")

# Vérifier si légal
is_legal, msg = service.is_time_legal(datetime.now())
print(msg)
```

### cURL
```bash
# Fenêtre légale
curl "https://api.huntiq.com/api/v1/legal-time/legal-window"

# Avec localisation personnalisée
curl "https://api.huntiq.com/api/v1/legal-time/legal-window?lat=45.5&lng=-73.5"

# Vérification temps réel
curl "https://api.huntiq.com/api/v1/legal-time/check"
```

---

## Changelog

### v1.0.0 (2026-02-09)
- Création du module
- Intégration bibliothèque `astral`
- 7 endpoints API
- Intégration frontend (Widget + Bar)
- Tests unitaires complets

---

*HUNTIQ V3 - Legal Time Engine - Phase 8*
