# P1-VIS: SPÉCIFICATION DES OVERLAYS VISUELS
## PHASE G - P1 PRÉPARATION
### Version: 1.0.0-draft | Date: Décembre 2025 | Status: EN ATTENTE GO

---

## 1. RÉSUMÉ EXÉCUTIF

| Attribut | Valeur |
|----------|--------|
| **Module** | P1-VIS (Visual Overlays / Heatmaps) |
| **Objectif** | Overlays cartographiques basés sur les scores P0 |
| **Priorité** | P1 - MEDIUM |
| **Dépendances** | P0-STABLE (validé ✅), P1-SCORE |
| **Effort estimé** | 3-4 jours développement |
| **Status** | EN ATTENTE GO COPILOT MAÎTRE |

---

## 2. TYPES D'OVERLAYS

### 2.1 Catalogue des Overlays

| # | Overlay | Source Données | Priorité |
|---|---------|----------------|----------|
| 1 | **Heatmap Score Territorial** | PT score | HIGH |
| 2 | **Heatmap Activité Comportementale** | BM activity_score | HIGH |
| 3 | **Zones de Prédation** | Facteur 1 (predation) | MEDIUM |
| 4 | **Stress Thermique** | Facteur 2 (thermal_stress) | MEDIUM |
| 5 | **Corridors Hormonaux (Rut)** | Facteur 8 (hormonal) | HIGH |
| 6 | **Impact Neige** | Facteur 14 (snow) | MEDIUM |
| 7 | **Activité Humaine** | Facteur 12 (human_disturbance) | LOW |
| 8 | **Overlay Composite** | Score global pondéré | HIGH |

### 2.2 Wireframe Overlay Selector

```
┌─────────────────────────────────────────────────────────────────┐
│  CARTE - Overlays BIONIC                                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────┐  ┌──────────────────┐  │
│  │                                     │  │ OVERLAYS         │  │
│  │                                     │  │                  │  │
│  │       ████████████████              │  │ ☑ Score Global   │  │
│  │     ██████████████████████          │  │ ☐ Activité       │  │
│  │   ████████▓▓▓▓▓▓▓▓████████          │  │ ☐ Prédation      │  │
│  │  ████████▓▓▓▓▓▓▓▓▓▓████████         │  │ ☐ Stress Therm.  │  │
│  │  ███████▓▓▓▓░░░░▓▓▓▓███████         │  │ ☑ Rut/Hormonal   │  │
│  │   ██████▓▓▓░░░░░░▓▓▓██████          │  │ ☐ Neige          │  │
│  │    █████▓▓░░░░░░░░▓▓█████           │  │ ☐ Humain         │  │
│  │      ████▓░░░░░░░░▓████             │  │                  │  │
│  │        ███░░░░░░░███                │  │ ─────────────────│  │
│  │          █████████                  │  │ Opacité: ████░░  │  │
│  │                                     │  │ 70%              │  │
│  │                                     │  │                  │  │
│  └─────────────────────────────────────┘  └──────────────────┘  │
│                                                                  │
│  LÉGENDE                                                         │
│  ████ Exceptionnel (90-100)  ▓▓▓▓ Bon (60-80)  ░░░░ Faible (<40)│
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. ARCHITECTURE TECHNIQUE

### 3.1 Pipeline de Génération

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Grid Points │ ──► │  P0 Scoring  │ ──► │  Heatmap     │
│  Generator   │     │  (batch)     │     │  Generator   │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │
       │ Grille 50x50       │ Scores 2500pts     │ Canvas/WebGL
       │ (viewport)         │                    │
       ▼                    ▼                    ▼
┌──────────────────────────────────────────────────────────┐
│                    Leaflet Heatmap Layer                  │
│                    (leaflet.heat plugin)                  │
└──────────────────────────────────────────────────────────┘
```

### 3.2 Composants

```
/app/frontend/src/components/map/overlays/
├── HeatmapLayer.jsx           # Couche Leaflet heatmap
├── OverlaySelector.jsx        # UI sélection overlays
├── OverlayLegend.jsx          # Légende dynamique
├── hooks/
│   ├── useHeatmapData.js      # Génération données
│   └── useOverlayConfig.js    # Configuration overlays
└── utils/
    └── gridGenerator.js       # Génération grille points
```

```
/app/backend/modules/bionic_engine_p0/
└── services/
    └── heatmap_service.py     # Calcul batch scores
```

---

## 4. SPÉCIFICATION TECHNIQUE

### 4.1 Génération de Grille

| Paramètre | Valeur | Justification |
|-----------|--------|---------------|
| Résolution | 50x50 points | Balance perf/précision |
| Points totaux | 2500 | Calcul <5s |
| Couverture | Viewport visible | Optimisation |
| Rafraîchissement | On zoom/pan | Lazy loading |

### 4.2 Format de Données Heatmap

```javascript
// Input pour leaflet.heat
const heatmapData = [
  [latitude, longitude, intensity],  // intensity: 0-1
  [48.5, -70.5, 0.85],
  [48.51, -70.5, 0.78],
  ...
];
```

### 4.3 Palette de Couleurs

```javascript
const HEATMAP_GRADIENT = {
  0.0: '#1a237e',  // Bleu foncé (très faible)
  0.2: '#3949ab',  // Bleu
  0.4: '#8e24aa',  // Violet
  0.6: '#f57c00',  // Orange
  0.8: '#fdd835',  // Jaune
  1.0: '#ff1744'   // Rouge vif (optimal)
};

// Alternative par type d'overlay
const OVERLAY_GRADIENTS = {
  territorial: { 0: '#1a237e', 0.5: '#fdd835', 1: '#ff1744' },
  predation: { 0: '#4caf50', 0.5: '#ff9800', 1: '#f44336' },
  thermal: { 0: '#2196f3', 0.5: '#4caf50', 1: '#f44336' },
  rut: { 0: '#9e9e9e', 0.5: '#e91e63', 1: '#d500f9' }
};
```

---

## 5. API BACKEND

### 5.1 POST /api/v1/bionic/heatmap/generate

**Description:** Génère les données heatmap pour une zone

**Request:**
```json
{
  "bounds": {
    "north": 48.6,
    "south": 48.4,
    "east": -70.4,
    "west": -70.6
  },
  "species": "moose",
  "overlay_type": "territorial",
  "resolution": 50,
  "datetime": "2025-12-21T10:00:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "heatmap_data": [
    [48.5, -70.5, 0.85],
    [48.51, -70.49, 0.78],
    ...
  ],
  "statistics": {
    "min_score": 45,
    "max_score": 92,
    "avg_score": 72,
    "hotspots": [
      { "lat": 48.52, "lng": -70.48, "score": 92 }
    ]
  },
  "metadata": {
    "points_calculated": 2500,
    "calculation_time_ms": 3200,
    "cache_hit": false
  }
}
```

### 5.2 GET /api/v1/bionic/heatmap/config

**Description:** Configuration des overlays disponibles

**Response:**
```json
{
  "overlays": [
    {
      "id": "territorial",
      "label_fr": "Score Territorial",
      "label_en": "Territorial Score",
      "gradient": {...},
      "default_opacity": 0.7
    },
    {
      "id": "rut",
      "label_fr": "Corridors Rut",
      "label_en": "Rut Corridors",
      "gradient": {...},
      "seasonal": true,
      "active_months": [9, 10, 11]
    }
  ]
}
```

---

## 6. OPTIMISATIONS PERFORMANCE

### 6.1 Stratégies

| Stratégie | Implémentation | Gain |
|-----------|----------------|------|
| **Calcul batch** | Parallel processing 2500 pts | -60% temps |
| **Cache serveur** | Redis TTL 5min par zone | -80% API calls |
| **WebGL rendering** | Canvas accéléré GPU | 60 FPS |
| **Level of Detail** | Résolution adaptative zoom | -70% calculs |
| **Lazy loading** | Génération on-demand | Mémoire optimisée |

### 6.2 Level of Detail (LOD)

| Zoom Level | Résolution | Points |
|------------|------------|--------|
| <10 | 20x20 | 400 |
| 10-12 | 30x30 | 900 |
| 12-14 | 50x50 | 2500 |
| >14 | 75x75 | 5625 |

---

## 7. COMPOSANTS UI

### 7.1 OverlaySelector

| Propriété | Type | Description |
|-----------|------|-------------|
| `overlays` | array | Liste overlays disponibles |
| `selected` | array | Overlays actifs (multi-select) |
| `opacity` | number | Opacité globale 0-1 |
| `onChange` | function | Callback sélection |

### 7.2 OverlayLegend

| Propriété | Type | Description |
|-----------|------|-------------|
| `gradient` | object | Couleurs par seuil |
| `labels` | object | Labels par seuil |
| `unit` | string | Unité (%, score) |

### 7.3 HeatmapLayer

| Propriété | Type | Description |
|-----------|------|-------------|
| `data` | array | Points [lat, lng, intensity] |
| `gradient` | object | Palette couleurs |
| `radius` | number | Rayon blur (px) |
| `maxZoom` | number | Zoom max intensité |
| `minOpacity` | number | Opacité minimale |

---

## 8. INTÉGRATION LEAFLET

### 8.1 Plugin Recommandé

**leaflet.heat** - Plugin léger et performant

```bash
yarn add leaflet.heat
```

### 8.2 Exemple d'Intégration

```javascript
import L from 'leaflet';
import 'leaflet.heat';

const HeatmapLayer = ({ data, gradient, map }) => {
  useEffect(() => {
    const heatLayer = L.heatLayer(data, {
      radius: 25,
      blur: 15,
      maxZoom: 17,
      gradient: gradient
    }).addTo(map);
    
    return () => map.removeLayer(heatLayer);
  }, [data, map]);
  
  return null;
};
```

---

## 9. TESTS G-QA

### 9.1 Tests Backend

| Test | Description |
|------|-------------|
| test_heatmap_generate | Génération 2500 points |
| test_heatmap_bounds_validation | Validation bounds |
| test_heatmap_cache | Cache Redis |
| test_heatmap_performance | <5s pour 2500 pts |

### 9.2 Tests Frontend

| Test | Description |
|------|-------------|
| test_heatmap_render | Rendu canvas |
| test_overlay_selector | UI sélection |
| test_overlay_toggle | Activation/désactivation |
| test_legend_display | Légende correcte |
| test_zoom_lod | Level of Detail |

---

## 10. ESTIMATION EFFORT

| Phase | Tâche | Durée |
|-------|-------|-------|
| 1 | Backend heatmap_service | 4h |
| 2 | API endpoints (2) | 2h |
| 3 | gridGenerator.js | 2h |
| 4 | HeatmapLayer component | 3h |
| 5 | OverlaySelector component | 2h |
| 6 | OverlayLegend component | 1h |
| 7 | Intégration carte existante | 3h |
| 8 | Optimisations perf | 3h |
| 9 | Tests (8) | 3h |
| 10 | Documentation | 1h |
| **Total** | | **24h (~3 jours)** |

---

## 11. LIVRABLES ATTENDUS

| # | Livrable | Type |
|---|----------|------|
| 1 | `heatmap_service.py` | Backend |
| 2 | 2 endpoints heatmap | Backend |
| 3 | `HeatmapLayer.jsx` | Frontend |
| 4 | `OverlaySelector.jsx` | Frontend |
| 5 | `OverlayLegend.jsx` | Frontend |
| 6 | `gridGenerator.js` | Frontend |
| 7 | Tests backend (4) | Tests |
| 8 | Tests frontend (5) | Tests |
| 9 | Documentation | G-DOC |

---

## 12. CHECKLIST PRÉ-IMPLÉMENTATION

| # | Item | Status |
|---|------|--------|
| 1 | GO COPILOT MAÎTRE | ⏳ EN ATTENTE |
| 2 | P1-SCORE validé | ⏳ DÉPENDANCE |
| 3 | leaflet.heat testé | ⏳ À VALIDER |
| 4 | Palette couleurs approuvée | ⏳ EN ATTENTE |

---

*Document préparé conformément aux normes G-DOC Phase G*
*Status: DRAFT - EN ATTENTE VALIDATION COPILOT MAÎTRE*
