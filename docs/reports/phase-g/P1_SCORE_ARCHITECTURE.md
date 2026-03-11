# P1-SCORE: ARCHITECTURE DU SYSTÈME DE SCORING DYNAMIQUE
## PHASE G - P1 PRÉPARATION
### Version: 1.0.0-draft | Date: Décembre 2025 | Status: EN ATTENTE GO

---

## 1. RÉSUMÉ EXÉCUTIF

| Attribut | Valeur |
|----------|--------|
| **Module** | P1-SCORE (Dynamic Scoring System) |
| **Objectif** | Système de scoring temps réel dans l'interface utilisateur |
| **Priorité** | P1 - HIGH |
| **Dépendances** | P0-STABLE (validé ✅), P1-ENV (météo temps réel) |
| **Effort estimé** | 4-5 jours développement |
| **Status** | EN ATTENTE GO COPILOT MAÎTRE |

---

## 2. VISION PRODUIT

### 2.1 Concept

Le Système de Scoring Dynamique transforme l'onglet INTELLIGENCE en un tableau de bord interactif affichant en temps réel :
- **Score territorial global** (0-100) avec jauge animée
- **Breakdown par facteur** (12 facteurs visuels)
- **Évolution temporelle** (courbe 24h-7j)
- **Comparaison multi-zones** (jusqu'à 5 positions)

### 2.2 Wireframe Conceptuel

```
┌─────────────────────────────────────────────────────────────────┐
│  INTELLIGENCE - Scoring Dynamique                    [🔄 Refresh]│
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐   │
│  │    SCORE GLOBAL     │  │     BREAKDOWN 12 FACTEURS       │   │
│  │                     │  │                                 │   │
│  │       ┌───┐         │  │  Prédation      ████████░░ 78%  │   │
│  │      /     \        │  │  Stress Therm.  ██░░░░░░░░ 15%  │   │
│  │     │  85   │       │  │  Hiérarchie     ██████████ 95%  │   │
│  │      \     /        │  │  Hormonal       █████████░ 88%  │   │
│  │       └───┘         │  │  Digestif       ██████░░░░ 60%  │   │
│  │     EXCELLENT       │  │  Mémoire        ███░░░░░░░ 30%  │   │
│  │                     │  │  Adaptation     █████░░░░░ 52%  │   │
│  │  Confiance: 0.85    │  │  Neige          ████████░░ 75%  │   │
│  └─────────────────────┘  └─────────────────────────────────┘   │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  ÉVOLUTION 24H                                             │  │
│  │  100│     ╭──╮                                             │  │
│  │   80│ ╭──╯    ╰──╮    ╭───╮                               │  │
│  │   60│╯           ╰────╯   ╰────                           │  │
│  │   40│                                                      │  │
│  │     └───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬──   │  │
│  │        6h  8h 10h 12h 14h 16h 18h 20h 22h 0h  2h  4h       │  │
│  │        ▲ OPTIMAL: 7h-8h (Score 92)                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  COMPARAISON ZONES                                         │  │
│  │  Zone A (actuelle)  ████████████████░░░░ 85  ★             │  │
│  │  Zone B (+5km N)    ██████████████░░░░░░ 72                │  │
│  │  Zone C (+3km E)    ████████████░░░░░░░░ 65                │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. ARCHITECTURE TECHNIQUE

### 3.1 Composants Frontend

```
/app/frontend/src/components/intelligence/
├── ScoreGauge.jsx              # Jauge circulaire animée
├── FactorBreakdown.jsx         # Barres horizontales 12 facteurs
├── ScoreTimeline.jsx           # Graphique évolution 24h
├── ZoneComparison.jsx          # Comparateur multi-zones
├── ScoringDashboard.jsx        # Conteneur principal
└── hooks/
    ├── useScore.js             # Hook API scoring
    ├── useTimeline.js          # Hook timeline données
    └── useZoneCompare.js       # Hook comparaison
```

### 3.2 Composants Backend

```
/app/backend/modules/bionic_engine_p0/
├── services/
│   └── scoring_service.py      # Orchestration scoring
└── router.py                   # Nouveaux endpoints
    ├── GET /scoring/current    # Score actuel
    ├── GET /scoring/timeline   # Timeline 24h
    └── POST /scoring/compare   # Comparaison zones
```

### 3.3 Flux de Données

```
┌─────────────┐    API Call    ┌─────────────────┐
│   Frontend  │ ─────────────► │    Backend      │
│  Dashboard  │                │  /scoring/*     │
└──────┬──────┘                └────────┬────────┘
       │                                │
       │ WebSocket (optionnel)          │ Appel P0 Services
       │ pour temps réel                │
       │                                ▼
       │                       ┌─────────────────┐
       │                       │ PT + BM Services│
       │                       │ (P0-STABLE)     │
       │                       └────────┬────────┘
       │                                │
       │                                │ 12 facteurs
       │                                ▼
       │                       ┌─────────────────┐
       │                       │  WeatherBridge  │
       │                       │  (P1-ENV)       │
       ◄───────────────────────┴─────────────────┘
              Réponse JSON
```

---

## 4. SPÉCIFICATION API

### 4.1 GET /api/v1/bionic/scoring/current

**Description:** Score actuel pour une position

**Request:**
```
GET /api/v1/bionic/scoring/current?latitude=48.5&longitude=-70.5&species=moose
```

**Response:**
```json
{
  "success": true,
  "score": {
    "overall": 85.2,
    "rating": "excellent",
    "confidence": 0.87,
    "trend": "up"
  },
  "factors": {
    "predation": { "score": 78, "label": "Risque modéré", "color": "#ffa500" },
    "thermal_stress": { "score": 15, "label": "Optimal", "color": "#22c55e" },
    "hormonal": { "score": 88, "label": "Pic rut", "color": "#e91e63" },
    ...
  },
  "recommendations_summary": [
    { "priority": "high", "message": "Pic du rut - moment optimal" }
  ],
  "optimal_time": {
    "hour": 7,
    "score": 92,
    "delta": "+7 points"
  },
  "metadata": {
    "timestamp": "2025-12-21T10:30:00Z",
    "weather_source": "openweathermap",
    "cache_age_seconds": 45
  }
}
```

### 4.2 GET /api/v1/bionic/scoring/timeline

**Description:** Évolution du score sur 24h

**Request:**
```
GET /api/v1/bionic/scoring/timeline?latitude=48.5&longitude=-70.5&species=moose&hours=24
```

**Response:**
```json
{
  "success": true,
  "timeline": [
    { "hour": 0, "score": 45, "factors_summary": "repos nocturne" },
    { "hour": 6, "score": 82, "factors_summary": "alimentation aube" },
    { "hour": 7, "score": 92, "factors_summary": "pic activité", "optimal": true },
    { "hour": 12, "score": 55, "factors_summary": "repos mi-journée" },
    ...
  ],
  "statistics": {
    "min": 45,
    "max": 92,
    "avg": 68.5,
    "optimal_window": { "start": 6, "end": 8 }
  }
}
```

### 4.3 POST /api/v1/bionic/scoring/compare

**Description:** Comparaison de plusieurs zones

**Request:**
```json
{
  "species": "moose",
  "zones": [
    { "id": "A", "latitude": 48.5, "longitude": -70.5, "label": "Position actuelle" },
    { "id": "B", "latitude": 48.55, "longitude": -70.5, "label": "+5km Nord" },
    { "id": "C", "latitude": 48.5, "longitude": -70.45, "label": "+3km Est" }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "comparison": [
    { "id": "A", "score": 85, "rank": 1, "best": true },
    { "id": "B", "score": 72, "rank": 2, "delta": -13 },
    { "id": "C", "score": 65, "rank": 3, "delta": -20 }
  ],
  "recommendation": "Position A offre le meilleur score (+13 vs zone B)"
}
```

---

## 5. COMPOSANTS UI DÉTAILLÉS

### 5.1 ScoreGauge (Jauge Circulaire)

| Propriété | Type | Description |
|-----------|------|-------------|
| `score` | number | Score 0-100 |
| `rating` | string | poor/low/moderate/good/excellent/exceptional |
| `confidence` | number | 0-1 |
| `animated` | boolean | Animation de remplissage |
| `size` | string | sm/md/lg |

**Couleurs par Rating:**
```javascript
const RATING_COLORS = {
  exceptional: "#22c55e", // Vert vif
  excellent: "#84cc16",   // Vert-jaune
  good: "#eab308",        // Jaune
  moderate: "#f97316",    // Orange
  low: "#ef4444",         // Rouge
  poor: "#dc2626"         // Rouge foncé
};
```

### 5.2 FactorBreakdown (Barres de Facteurs)

| Propriété | Type | Description |
|-----------|------|-------------|
| `factors` | object | 12+ facteurs avec scores |
| `showLabels` | boolean | Afficher labels |
| `compact` | boolean | Mode compact |
| `sortBy` | string | score/name/impact |

### 5.3 ScoreTimeline (Graphique Temporel)

| Propriété | Type | Description |
|-----------|------|-------------|
| `data` | array | Points horaires |
| `hours` | number | 24/48/168 |
| `showOptimal` | boolean | Marker point optimal |
| `interactive` | boolean | Hover avec détails |

**Librairie:** LightCharts (déjà intégré GOLD MASTER)

---

## 6. RESPONSIVE DESIGN

### 6.1 Breakpoints

| Breakpoint | Layout |
|------------|--------|
| Mobile (<640px) | Score seul, facteurs en accordéon |
| Tablet (640-1024px) | Score + facteurs, timeline en dessous |
| Desktop (>1024px) | Layout complet 3 colonnes |

### 6.2 Performance Mobile

| Critère | Cible |
|---------|-------|
| First Paint | <1s |
| Interactive | <2s |
| Bundle size delta | <50KB |

---

## 7. TESTS G-QA

### 7.1 Tests Backend

| Test | Description |
|------|-------------|
| test_scoring_current_endpoint | Endpoint score actuel |
| test_scoring_timeline_24h | Timeline 24 points |
| test_scoring_compare_zones | Comparaison 3 zones |
| test_scoring_with_weather | Intégration P1-ENV |
| test_scoring_cache | Cache fonctionnel |

### 7.2 Tests Frontend

| Test | Description |
|------|-------------|
| test_gauge_render | Rendu jauge |
| test_gauge_animation | Animation fluide |
| test_factors_display | Affichage 12 facteurs |
| test_timeline_chart | Graphique timeline |
| test_responsive_mobile | Layout mobile |

---

## 8. ESTIMATION EFFORT

| Phase | Tâche | Durée |
|-------|-------|-------|
| 1 | Backend endpoints (3) | 4h |
| 2 | ScoringService | 3h |
| 3 | ScoreGauge component | 3h |
| 4 | FactorBreakdown component | 2h |
| 5 | ScoreTimeline component | 4h |
| 6 | ZoneComparison component | 2h |
| 7 | ScoringDashboard integration | 3h |
| 8 | Tests backend (5) | 2h |
| 9 | Tests frontend (5) | 2h |
| 10 | Responsive + polish | 3h |
| 11 | Documentation G-DOC | 2h |
| **Total** | | **30h (~4 jours)** |

---

## 9. INTÉGRATION ONGLET INTELLIGENCE

### 9.1 Position dans Navigation

```
INTELLIGENCE
├── Analytics (existant)
├── Prévisions (existant)
├── >>> Scoring Dynamique <<< (NOUVEAU P1-SCORE)
└── Plan Maître (existant)
```

### 9.2 Interaction avec Carte

| Action Carte | Réaction Scoring |
|--------------|------------------|
| Click position | Mise à jour score instantanée |
| Drag marker | Rafraîchissement continu |
| Zoom | Mise à jour zones comparées |

---

## 10. LIVRABLES ATTENDUS

| # | Livrable | Type |
|---|----------|------|
| 1 | `scoring_service.py` | Backend |
| 2 | 3 endpoints scoring | Backend |
| 3 | `ScoreGauge.jsx` | Frontend |
| 4 | `FactorBreakdown.jsx` | Frontend |
| 5 | `ScoreTimeline.jsx` | Frontend |
| 6 | `ZoneComparison.jsx` | Frontend |
| 7 | `ScoringDashboard.jsx` | Frontend |
| 8 | Tests backend (5) | Tests |
| 9 | Tests frontend (5) | Tests |
| 10 | Documentation | G-DOC |

---

## 11. CHECKLIST PRÉ-IMPLÉMENTATION

| # | Item | Status |
|---|------|--------|
| 1 | GO COPILOT MAÎTRE | ⏳ EN ATTENTE |
| 2 | P1-ENV validé | ⏳ DÉPENDANCE |
| 3 | Wireframes approuvés | ⏳ EN ATTENTE |
| 4 | API contracts validés | ⏳ EN ATTENTE |

---

*Document préparé conformément aux normes G-DOC Phase G*
*Status: DRAFT - EN ATTENTE VALIDATION COPILOT MAÎTRE*
