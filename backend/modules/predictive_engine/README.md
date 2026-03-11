# Predictive Engine

## Module de Prédiction de Succès de Chasse

### Version: 1.0.0
### Phase: 8 (Plan Maître BIONIC)
### API Prefix: `/api/v1/predictive`

---

## Description

Le **Predictive Engine** fournit des prédictions de succès de chasse basées sur plusieurs facteurs : saison, météo, phase lunaire, pression atmosphérique et activité récente.

Ce module est **intégré avec le Legal Time Engine** pour garantir que toutes les heures optimales recommandées respectent la fenêtre de chasse légale.

---

## Espèces Supportées

| Code | Nom Français | Activité Max |
|------|--------------|--------------|
| `deer` | Cerf de Virginie | Aube (95%) |
| `moose` | Orignal | Aube (85%) |
| `bear` | Ours noir | Crépuscule (75%) |
| `wild_turkey` | Dindon sauvage | Aube (90%) |

---

## Endpoints API

### 1. Info Module
```
GET /api/v1/predictive/
```
Retourne les informations du module et les espèces supportées.

---

### 2. Prédiction de Succès
```
GET /api/v1/predictive/success
```
Prédit la probabilité de succès de chasse.

**Paramètres:**
| Param | Type | Défaut | Description |
|-------|------|--------|-------------|
| `species` | string | deer | Espèce ciblée |
| `date` | string | aujourd'hui | Date YYYY-MM-DD |
| `lat` | float | 46.8139 | Latitude |
| `lng` | float | -71.2080 | Longitude |
| `weather` | JSON | null | Données météo optionnelles |

**Réponse:**
```json
{
  "success": true,
  "species": "deer",
  "prediction": {
    "success_probability": 68,
    "confidence": 0.85,
    "factors": [
      {"name": "Saison", "impact": "very_positive", "score": 95},
      {"name": "Météo", "impact": "positive", "score": 75},
      {"name": "Phase lunaire", "impact": "neutral", "score": 50},
      {"name": "Pression atmosphérique", "impact": "positive", "score": 70},
      {"name": "Activité récente", "impact": "positive", "score": 65}
    ],
    "optimal_times": [
      {"period": "Aube", "time": "06:28-08:58", "score": 95, "is_legal": true},
      {"period": "Crépuscule", "time": "15:00-17:30", "score": 90, "is_legal": true}
    ],
    "recommendation": "Excellentes conditions pour la chasse au Cerf de Virginie."
  }
}
```

---

### 3. Niveau d'Activité Actuel
```
GET /api/v1/predictive/activity
```
Retourne le niveau d'activité actuel pour une espèce.

**Réponse:**
```json
{
  "success": true,
  "species": "deer",
  "current_time": "14:30",
  "activity": {
    "level": "moderate",
    "score": 45,
    "peak_times": [
      "06:28 - 08:28",
      "15:30 - 17:30"
    ]
  }
}
```

---

### 4. Facteurs d'Influence
```
GET /api/v1/predictive/factors
```
Retourne les facteurs détaillés qui influencent le succès.

**Réponse:**
```json
{
  "success": true,
  "overall_score": 68,
  "factors": [
    {
      "name": "Saison",
      "impact": "very_positive",
      "score": 95,
      "description": "Automne - Saison optimale"
    },
    {
      "name": "Météo",
      "impact": "positive",
      "score": 75,
      "description": "Conditions météo pour l'espèce ciblée"
    }
  ]
}
```

---

### 5. Timeline d'Activité 24h
```
GET /api/v1/predictive/timeline
```
Retourne le niveau d'activité heure par heure avec statut légal.

**Réponse:**
```json
{
  "success": true,
  "legal_window": {
    "start": "06:28",
    "end": "17:30"
  },
  "timeline": [
    {"hour": 0, "activity_level": 30, "is_legal": false, "light_condition": "dark"},
    {"hour": 7, "activity_level": 95, "is_legal": true, "light_condition": "daylight"},
    {"hour": 12, "activity_level": 30, "is_legal": true, "light_condition": "daylight"},
    {"hour": 17, "activity_level": 90, "is_legal": true, "light_condition": "dusk"}
  ]
}
```

---

### 6. Heures Optimales
```
GET /api/v1/predictive/optimal-times
```
Retourne les meilleurs créneaux pour la chasse.

---

### 7. Prévisions Multi-jours
```
GET /api/v1/predictive/forecast/{species}
```
Prévisions de succès pour plusieurs jours.

**Paramètres:**
| Param | Type | Défaut | Description |
|-------|------|--------|-------------|
| `days` | int | 7 | Nombre de jours (1-14) |

---

## Algorithme de Prédiction

### Facteurs et Pondération

| Facteur | Poids | Description |
|---------|-------|-------------|
| Saison | 25% | Facteur saisonnier (rut en novembre = 95%) |
| Météo | 20% | Température, vent, précipitations |
| Phase lunaire | 15% | Nouvelle lune = +15%, pleine lune = -10% |
| Pression | 20% | Changements barométriques |
| Activité récente | 20% | Observations dans la région |

### Formule de Calcul
```
success_probability = Σ(factor_score × weight) 
confidence = 0.85 (avec météo) | 0.70 (sans météo)
```

### Patterns d'Activité par Espèce

```python
SPECIES_PATTERNS = {
    "deer": {
        "dawn_activity": 95,      # Très actif à l'aube
        "midday_activity": 30,    # Repos mi-journée
        "dusk_activity": 90,      # Très actif au crépuscule
        "best_temp_range": (-5, 15)
    },
    "moose": {
        "dawn_activity": 85,
        "midday_activity": 25,
        "dusk_activity": 80,
        "best_temp_range": (-10, 10)
    }
}
```

---

## Intégration avec Legal Time Engine

Le Predictive Engine utilise automatiquement le Legal Time Engine pour :

1. **Filtrer les heures optimales** - Seules les heures légales sont recommandées
2. **Marquer la timeline** - Chaque heure indique si elle est légale
3. **Calculer les créneaux** - Aube et crépuscule ajustés à la fenêtre légale

```python
# Exemple d'intégration
from modules.legal_time_engine.v1.service import LegalTimeService

class PredictiveService:
    def __init__(self):
        self.legal_time_service = LegalTimeService()
    
    def get_optimal_times(self, date, location):
        # Obtenir la fenêtre légale
        legal_window = self.legal_time_service.get_legal_hunting_window(date, location)
        
        # Filtrer les heures optimales
        slots = self.legal_time_service.get_recommended_hunting_slots(date, location)
        
        return [s for s in slots if s.is_legal]
```

---

## Structure des Fichiers

```
predictive_engine/
├── __init__.py           # Export du router
└── v1/
    ├── __init__.py       # Exports v1
    ├── router.py         # Endpoints FastAPI (5 endpoints)
    ├── service.py        # Logique de prédiction
    └── models.py         # Modèles Pydantic
```

---

## Modèles de Données

### HuntingPrediction
```python
class HuntingPrediction(BaseModel):
    success_probability: int    # 0-100
    confidence: float           # 0-1
    factors: List[PredictionFactor]
    optimal_times: List[OptimalTimeSlot]
    recommendation: str
```

### PredictionFactor
```python
class PredictionFactor(BaseModel):
    name: str
    impact: Literal["very_positive", "positive", "neutral", "negative", "very_negative"]
    score: int                  # 0-100
    description: Optional[str]
```

### ActivityTimeline
```python
class ActivityTimeline(BaseModel):
    hour: int                   # 0-23
    activity_level: int         # 0-100
    is_legal: bool
    light_condition: str        # "dark", "dawn", "daylight", "dusk"
```

---

## Intégration Frontend

### Service JavaScript
```javascript
import { PredictiveService } from '../modules/predictive';

// Prédiction de succès
const prediction = await PredictiveService.predictHuntingSuccess({
    species: 'deer',
    lat: 46.8139,
    lng: -71.2080
});

// Niveau d'activité
const activity = await PredictiveService.getActivity('deer');

// Timeline 24h
const timeline = await PredictiveService.getTimeline('deer');
```

### Composant React
```jsx
<PredictiveWidget 
    species="deer"
    coordinates={{ lat: 46.8139, lng: -71.2080 }}
/>
```

---

## Tests

```bash
cd /app/backend
pytest tests/test_predictive_engine.py -v
```

---

## Exemples cURL

```bash
# Prédiction de succès
curl "https://api.huntiq.com/api/v1/predictive/success?species=deer"

# Avec météo
curl "https://api.huntiq.com/api/v1/predictive/success?species=deer&weather=%7B%22temperature%22:10%7D"

# Timeline
curl "https://api.huntiq.com/api/v1/predictive/timeline?species=moose"

# Prévisions 7 jours
curl "https://api.huntiq.com/api/v1/predictive/forecast/deer?days=7"
```

---

## Changelog

### v1.0.0 (2026-02-09)
- Création du module
- 5 endpoints API
- Support 4 espèces
- Intégration Legal Time Engine
- Tests unitaires complets

---

*HUNTIQ V3 - Predictive Engine - Phase 8*
