# PROPOSITION ENDPOINT: /api/v1/bionic/analyze_hunt_plan
## PHASE G - P1 PRÉPARATION
### Version: 1.0.0-draft | Date: Décembre 2025 | Status: EN ATTENTE GO

---

## 1. RÉSUMÉ EXÉCUTIF

| Attribut | Valeur |
|----------|--------|
| **Endpoint** | `POST /api/v1/bionic/analyze_hunt_plan` |
| **Module** | P1-PLAN (Hunt Plan Analyzer) |
| **Objectif** | Générer un plan de chasse optimal basé sur les 12 facteurs |
| **Priorité** | P1 - HIGH (différenciateur produit) |
| **Dépendances** | P0-STABLE ✅, P1-ENV, P1-SCORE |
| **Effort estimé** | 2-3 jours développement |
| **Status** | EN ATTENTE GO COPILOT MAÎTRE |

---

## 2. VISION PRODUIT

### 2.1 Concept

L'endpoint `/analyze_hunt_plan` est le **point culminant** de l'intelligence BIONIC V5. Il synthétise les 12 facteurs comportementaux pour générer un **plan de chasse personnalisé et actionnable** incluant :

- **Horaires optimaux** (fenêtres de tir recommandées)
- **Positions stratégiques** (waypoints suggérés)
- **Stratégies adaptées** (selon les facteurs dominants)
- **Équipement recommandé** (appels, leurres, camo)
- **Alertes et risques** (météo, prédation, pression)

### 2.2 Différenciateur Marché

```
╔════════════════════════════════════════════════════════════════╗
║  "BIONIC V5 ne vous donne pas juste un score.                  ║
║   Il vous dit QUAND, OÙ, et COMMENT chasser."                  ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 3. SPÉCIFICATION API

### 3.1 Endpoint

```
POST /api/v1/bionic/analyze_hunt_plan
Content-Type: application/json
```

### 3.2 Request Schema

```json
{
  "species": "moose",
  "territory": {
    "center": { "latitude": 48.5, "longitude": -70.5 },
    "radius_km": 10
  },
  "date_range": {
    "start": "2025-10-15",
    "end": "2025-10-17"
  },
  "hunter_profile": {
    "experience_level": "intermediate",
    "preferred_method": "still_hunting",
    "physical_condition": "good",
    "equipment_available": ["rifle", "calls", "decoy"]
  },
  "constraints": {
    "legal_hours_only": true,
    "max_walk_distance_km": 5,
    "avoid_zones": [
      { "latitude": 48.52, "longitude": -70.48, "radius_m": 500 }
    ]
  },
  "preferences": {
    "priority": "trophy",
    "risk_tolerance": "moderate"
  }
}
```

### 3.3 Response Schema

```json
{
  "success": true,
  "hunt_plan": {
    "summary": {
      "overall_opportunity_score": 87,
      "best_day": "2025-10-16",
      "best_window": { "start": "06:30", "end": "08:30" },
      "primary_strategy": "rut_calling",
      "confidence": 0.85
    },
    
    "daily_plans": [
      {
        "date": "2025-10-15",
        "opportunity_score": 82,
        "dominant_factors": ["hormonal_peak", "low_predation"],
        
        "optimal_windows": [
          {
            "window_id": "morning_prime",
            "start": "06:15",
            "end": "08:30",
            "score": 92,
            "reason_fr": "Pic d'activité hormonale + alimentation matinale",
            "reason_en": "Hormonal peak + morning feeding"
          },
          {
            "window_id": "evening_secondary",
            "start": "16:30",
            "end": "18:00",
            "score": 78,
            "reason_fr": "Deuxième période d'alimentation",
            "reason_en": "Secondary feeding period"
          }
        ],
        
        "suggested_positions": [
          {
            "position_id": "P1",
            "latitude": 48.52,
            "longitude": -70.48,
            "score": 88,
            "type": "ambush",
            "description_fr": "Carrefour de corridors, vue dégagée 100m",
            "description_en": "Corridor intersection, 100m clear view",
            "approach_direction": "NW",
            "wind_consideration": "Vent prévu du SE - position optimale"
          },
          {
            "position_id": "P2",
            "latitude": 48.51,
            "longitude": -70.50,
            "score": 75,
            "type": "calling_station",
            "description_fr": "Zone ouverte idéale pour appels",
            "description_en": "Open area ideal for calling"
          }
        ],
        
        "strategies": [
          {
            "strategy_id": "S1",
            "name": "rut_peak_calling",
            "effectiveness": 95,
            "description_fr": "Appels de femelle + rattling agressif",
            "description_en": "Cow calls + aggressive rattling",
            "steps": [
              "Arriver 30 min avant l'aube",
              "Série de 3 appels espacés de 5 min",
              "Attendre 20 min en silence",
              "Rattling si pas de réponse"
            ],
            "equipment_needed": ["cow_call", "grunt_tube", "rattling_antlers"]
          }
        ],
        
        "equipment_recommendations": [
          {
            "item": "cow_call",
            "priority": "essential",
            "reason_fr": "Pic du rut - les mâles répondent activement"
          },
          {
            "item": "scent_eliminator",
            "priority": "recommended",
            "reason_fr": "Vent variable prévu"
          },
          {
            "item": "decoy",
            "priority": "optional",
            "reason_fr": "Efficace si mâle dominant dans la zone"
          }
        ],
        
        "alerts": [
          {
            "type": "weather",
            "severity": "info",
            "message_fr": "Légère pluie prévue 10h-12h - ne pas affecter l'aube",
            "message_en": "Light rain expected 10h-12h - won't affect dawn"
          }
        ],
        
        "weather_forecast": {
          "dawn": { "temp": 5, "wind": 10, "precip_prob": 0.1 },
          "midday": { "temp": 12, "wind": 15, "precip_prob": 0.4 },
          "dusk": { "temp": 8, "wind": 8, "precip_prob": 0.1 }
        }
      }
    ],
    
    "factors_analysis": {
      "predation": {
        "score": 35,
        "impact": "positive",
        "insight_fr": "Faible risque - animaux moins vigilants"
      },
      "hormonal": {
        "score": 92,
        "impact": "very_positive",
        "phase": "rut_peak",
        "insight_fr": "PIC DU RUT - opportunité maximale"
      },
      "snow": {
        "score": 0,
        "impact": "neutral",
        "insight_fr": "Pas de neige - mobilité normale"
      },
      "human_disturbance": {
        "score": 25,
        "impact": "positive",
        "insight_fr": "Faible pression humaine hors week-end"
      }
    },
    
    "risk_assessment": {
      "overall_risk": "low",
      "factors": [
        {
          "risk": "weather_change",
          "probability": 0.2,
          "mitigation": "Surveiller météo, plan B si pluie forte"
        },
        {
          "risk": "hunting_pressure",
          "probability": 0.3,
          "mitigation": "Éviter zones accessibles en véhicule"
        }
      ]
    },
    
    "success_probability": {
      "sighting": 0.75,
      "shot_opportunity": 0.45,
      "harvest": 0.25,
      "factors_contributing": ["rut_peak", "optimal_timing", "good_positions"]
    }
  },
  
  "metadata": {
    "generated_at": "2025-12-21T10:00:00Z",
    "version": "P1-PLAN-1.0",
    "calculation_time_ms": 2500,
    "data_sources": ["openweathermap", "p0_stable", "historical"],
    "confidence_factors": {
      "weather_data": 0.95,
      "behavioral_model": 0.90,
      "historical_data": 0.75
    }
  }
}
```

---

## 4. ARCHITECTURE TECHNIQUE

### 4.1 Diagramme de Flux

```
┌────────────────────────────────────────────────────────────────┐
│                     /analyze_hunt_plan                          │
└───────────────────────────┬────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│                   HuntPlanAnalyzerService                       │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │ DateRangeLoop   │  │ PositionFinder  │  │ StrategyEngine │  │
│  │ (pour chaque    │  │ (waypoints      │  │ (matching      │  │
│  │  jour)          │  │  optimaux)      │  │  stratégies)   │  │
│  └────────┬────────┘  └────────┬────────┘  └───────┬────────┘  │
│           │                    │                    │           │
│           └────────────────────┼────────────────────┘           │
│                                │                                │
│  ┌─────────────────────────────┴─────────────────────────────┐ │
│  │                    P0-STABLE Integration                   │ │
│  │  ┌───────────────────┐    ┌───────────────────────────┐   │ │
│  │  │ PredictiveTerrit. │    │ BehavioralModels          │   │ │
│  │  │ (scores par heure)│    │ (timelines + strategies)  │   │ │
│  │  └───────────────────┘    └───────────────────────────┘   │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                │                                │
│  ┌─────────────────────────────┴─────────────────────────────┐ │
│  │                    P1-ENV Integration                      │ │
│  │  ┌───────────────────────────────────────────────────────┐│ │
│  │  │ WeatherBridge (prévisions multi-jours)                ││ │
│  │  └───────────────────────────────────────────────────────┘│ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

### 4.2 Structure des Fichiers

```
/app/backend/modules/bionic_engine_p0/
├── services/
│   ├── hunt_plan_analyzer.py     # Service principal
│   ├── position_finder.py        # Recherche positions optimales
│   └── strategy_matcher.py       # Matching stratégies
└── contracts/
    └── hunt_plan_contract.json   # Contrat API
```

---

## 5. ALGORITHMES CLÉS

### 5.1 Calcul des Fenêtres Optimales

```python
def find_optimal_windows(
    timeline_24h: List[TimelineEntry],
    legal_hours: Tuple[int, int],
    min_score_threshold: int = 70
) -> List[OptimalWindow]:
    """
    Identifie les fenêtres horaires optimales.
    
    Algorithme:
    1. Filtrer heures légales
    2. Grouper heures consécutives > threshold
    3. Scorer chaque groupe par moyenne pondérée
    4. Retourner top 3 fenêtres
    """
    windows = []
    current_window = None
    
    for entry in timeline_24h:
        if entry.is_legal and entry.score >= min_score_threshold:
            if current_window is None:
                current_window = WindowBuilder(entry)
            else:
                current_window.extend(entry)
        else:
            if current_window:
                windows.append(current_window.build())
                current_window = None
    
    return sorted(windows, key=lambda w: w.score, reverse=True)[:3]
```

### 5.2 Recherche de Positions Stratégiques

```python
def find_strategic_positions(
    center: Coordinates,
    radius_km: float,
    species: Species,
    factors: Dict[str, FactorResult],
    constraints: HuntConstraints
) -> List[SuggestedPosition]:
    """
    Recherche les positions optimales dans le rayon.
    
    Critères:
    1. Score territorial élevé
    2. Intersection corridors probables
    3. Couvert pour approche
    4. Vue dégagée pour tir
    5. Respect des zones à éviter
    """
    grid_points = generate_grid(center, radius_km, resolution=20)
    
    positions = []
    for point in grid_points:
        if not is_in_avoid_zone(point, constraints.avoid_zones):
            score = evaluate_position(point, species, factors)
            if score >= 70:
                positions.append(SuggestedPosition(
                    coordinates=point,
                    score=score,
                    type=determine_position_type(point, factors),
                    approach_analysis=analyze_approach(point)
                ))
    
    return cluster_and_select_top(positions, max_positions=5)
```

### 5.3 Matching de Stratégies

```python
def match_strategies(
    factors: Dict[str, FactorResult],
    hunter_profile: HunterProfile,
    equipment: List[str]
) -> List[StrategyRecommendation]:
    """
    Sélectionne les stratégies adaptées au contexte.
    
    Règles de matching:
    - hormonal.phase == "rut_peak" → rut_calling (95%)
    - snow.yarding == True → yarding_approach (90%)
    - thermal.stress == "cold" → thermal_ambush (80%)
    - digestive.phase == "feeding" → feeding_intercept (85%)
    """
    strategies = []
    
    if factors["hormonal"].phase in ["rut_peak", "pre_rut"]:
        if "calls" in equipment:
            strategies.append(RUT_CALLING_STRATEGY)
        if "decoy" in equipment:
            strategies.append(RUT_DECOY_STRATEGY)
    
    if factors["snow"].yarding_likelihood:
        strategies.append(YARDING_APPROACH_STRATEGY)
    
    # ... autres règles de matching
    
    return filter_by_experience(strategies, hunter_profile.experience_level)
```

---

## 6. PROFIL CHASSEUR

### 6.1 Niveaux d'Expérience

| Niveau | Stratégies Autorisées | Complexité Max |
|--------|----------------------|----------------|
| `beginner` | still_hunting, stand_hunting | LOW |
| `intermediate` | + calling, spot_stalk | MEDIUM |
| `advanced` | + rattling, decoy, tracking | HIGH |
| `expert` | Toutes | EXPERT |

### 6.2 Méthodes Préférées

| Méthode | Description | Facteurs Privilégiés |
|---------|-------------|---------------------|
| `still_hunting` | Approche lente | Digestive, Thermal |
| `stand_hunting` | Affût fixe | Corridors, Timeline |
| `spot_stalk` | Repérage + approche | Snow, Predation |
| `calling` | Appels | Hormonal, Social |

---

## 7. TESTS G-QA

### 7.1 Tests Unitaires

| Test | Description |
|------|-------------|
| test_optimal_windows_detection | Détection fenêtres >70 |
| test_position_scoring | Scoring positions |
| test_strategy_matching_rut | Matching rut |
| test_strategy_matching_snow | Matching neige |
| test_equipment_recommendations | Recommandations équipement |
| test_risk_assessment | Évaluation risques |
| test_success_probability | Calcul probabilités |

### 7.2 Tests d'Intégration

| Test | Description |
|------|-------------|
| test_full_hunt_plan_generation | Plan complet 3 jours |
| test_hunt_plan_with_weather | Intégration météo |
| test_hunt_plan_constraints | Respect contraintes |

---

## 8. ESTIMATION EFFORT

| Phase | Tâche | Durée |
|-------|-------|-------|
| 1 | HuntPlanAnalyzerService | 4h |
| 2 | PositionFinder | 3h |
| 3 | StrategyMatcher | 3h |
| 4 | Endpoint + validation | 2h |
| 5 | Tests unitaires (7) | 3h |
| 6 | Tests intégration (3) | 2h |
| 7 | Contrat JSON | 1h |
| 8 | Documentation | 2h |
| **Total** | | **20h (~2.5 jours)** |

---

## 9. VALEUR BUSINESS

### 9.1 Différenciation

| Concurrent | Fonctionnalité | BIONIC V5 |
|------------|----------------|-----------|
| onX Hunt | Cartes + public lands | ✅ + IA prédictive |
| HuntStand | Météo + journal | ✅ + Plan personnalisé |
| ScoutLook | Prévisions météo | ✅ + 12 facteurs comportementaux |

### 9.2 Impact Utilisateur

```
"Avant BIONIC: Je passais 2h à planifier ma sortie"
"Après BIONIC: Plan optimal en 10 secondes"
```

---

## 10. LIVRABLES ATTENDUS

| # | Livrable | Type |
|---|----------|------|
| 1 | `hunt_plan_analyzer.py` | Backend |
| 2 | `position_finder.py` | Backend |
| 3 | `strategy_matcher.py` | Backend |
| 4 | Endpoint POST /analyze_hunt_plan | Backend |
| 5 | `hunt_plan_contract.json` | Contrat |
| 6 | Tests unitaires (7) | Tests |
| 7 | Tests intégration (3) | Tests |
| 8 | Documentation API | G-DOC |

---

## 11. CHECKLIST PRÉ-IMPLÉMENTATION

| # | Item | Status |
|---|------|--------|
| 1 | GO COPILOT MAÎTRE | ⏳ EN ATTENTE |
| 2 | P1-ENV validé | ⏳ DÉPENDANCE |
| 3 | P1-SCORE validé | ⏳ DÉPENDANCE |
| 4 | Contrat API approuvé | ⏳ EN ATTENTE |
| 5 | Stratégies catalogue validé | ⏳ EN ATTENTE |

---

*Document préparé conformément aux normes G-DOC Phase G*
*Status: DRAFT - EN ATTENTE VALIDATION COPILOT MAÎTRE*
