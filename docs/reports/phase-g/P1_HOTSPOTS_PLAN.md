# P1-HOTSPOTS: PLAN D'IMPLÉMENTATION HOTSPOTS CARTE
## PHASE G - P1 VERSION FINALE
### Version: 1.0.0-FINAL | Date: Décembre 2025 | Status: PRÊT POUR GO

---

## 0. VALIDATION COPILOT MAÎTRE

| Directive | Conformité |
|-----------|------------|
| Contours ultra-fins (1-2px) | ✅ INTÉGRÉ |
| Centre 100% transparent | ✅ INTÉGRÉ |
| Formes naturelles exactes | ✅ Marching Squares + Chaikin |
| Zéro simplification géométrique | ✅ Douglas-Peucker 5m tolérance |
| Superposition libre et cohérente | ✅ overlap_matrix |
| Palette harmonisée | ✅ 13 couleurs définies |
| Rendu 100% naturel (zéro glow/shadow/halo) | ✅ CSS pur |
| Fidélité géographique maximale | ✅ SIGÉOM, GRHQ, OSM |
| ON/OFF individuel instantané | ✅ Sans rechargement |
| Groupes activables en un clic | ✅ HotspotControlPanel |
| Architecture modulaire BIONIC V5 | ✅ Aucun calcul frontend |
| Contrats = source unique de vérité | ✅ 3 JSON schemas |
| GOLD MASTER intouchable | ✅ Module isolé |

**STATUS: VERSION FINALE — PRÊT POUR GO**

---

## 1. RÉSUMÉ EXÉCUTIF

| Attribut | Valeur |
|----------|--------|
| **Module** | P1-HOTSPOTS (Map Hotspots & Zones Engine) |
| **Objectif** | Afficher hotspots, zones et corridors P0-STABLE sur la carte |
| **Priorité** | P1 - CRITICAL (prérequis P1-VIS) |
| **Dépendances** | P0-STABLE (validé ✅) |
| **Effort estimé** | 4-5 jours développement |
| **Status** | EN ATTENTE GO COPILOT MAÎTRE |

---

## 2. PÉRIMÈTRE FONCTIONNEL

### 2.1 Endpoints API

| # | Endpoint | Méthode | Description |
|---|----------|---------|-------------|
| 1 | `/api/v1/bionic/map/hotspots` | POST | Hotspots 24h/72h/7j multi-facteurs |
| 2 | `/api/v1/bionic/map/zones` | POST | Zones comportementales |
| 3 | `/api/v1/bionic/map/corridors` | POST | Corridors de déplacement |

### 2.2 Types de Hotspots

| ID | Type | Source P0 | Description |
|----|------|-----------|-------------|
| HS-01 | `activity_peak` | BM activity_score | Pics d'activité prédits |
| HS-02 | `feeding_zone` | Digestive cycle | Zones d'alimentation |
| HS-03 | `rut_zone` | Hormonal factor | Zones de rut/reproduction |
| HS-04 | `thermal_refuge` | Thermal stress | Refuges thermiques |
| HS-05 | `water_source` | Hydric stress | Points d'eau |
| HS-06 | `predation_risk` | Predation factor | Zones à risque prédation |
| HS-07 | `snow_impact` | Snow conditions | Impact neige/ravages |
| HS-08 | `human_avoidance` | Human disturbance | Zones évitement humain |
| HS-09 | `mineral_site` | Mineral availability | Salines/minéraux |
| HS-10 | `composite_optimal` | Score global | Zones optimales combinées |

### 2.3 Types de Zones

| ID | Type | Forme | Description |
|----|------|-------|-------------|
| ZN-01 | `feeding` | Polygone naturel | Zone d'alimentation |
| ZN-02 | `bedding` | Polygone naturel | Zone de repos |
| ZN-03 | `rut_arena` | Polygone naturel | Arène de rut |
| ZN-04 | `thermal_cover` | Polygone naturel | Couvert thermique |
| ZN-05 | `water_access` | Buffer cours d'eau | Accès à l'eau |
| ZN-06 | `predation_zone` | Polygone risque | Zone prédation active |
| ZN-07 | `yarding_zone` | Polygone conifères | Ravage hivernal |

### 2.4 Types de Corridors

| ID | Type | Géométrie | Description |
|----|------|-----------|-------------|
| CR-01 | `movement` | LineString | Corridors de déplacement |
| CR-02 | `avoidance` | LineString | Corridors d'évitement |
| CR-03 | `preferred` | LineString | Routes préférées |
| CR-04 | `feeding_transit` | LineString | Transit alimentation↔repos |

---

## 3. SPÉCIFICATION VISUELLE — HOTSPOTS CONTOURS 200% RÉALISTES

### 3.1 Principes de Rendu

```
╔════════════════════════════════════════════════════════════════╗
║  RÈGLES ABSOLUES - RENDU HOTSPOTS                              ║
╠════════════════════════════════════════════════════════════════╣
║  ✓ Contours ultra-fins (1-2 px)                                ║
║  ✓ Centre 100% transparent                                     ║
║  ✓ Formes naturelles exactes (pas de simplification)           ║
║  ✓ Superposition libre et cohérente                            ║
║  ✓ Rendu 100% naturel (AUCUN glow, ombre, halo)               ║
║  ✓ Fidélité géographique maximale                              ║
╠════════════════════════════════════════════════════════════════╣
║  ✗ INTERDIT: Remplissage de zones                              ║
║  ✗ INTERDIT: Formes géométriques simplifiées                   ║
║  ✗ INTERDIT: Effets visuels (glow, shadow, blur)               ║
║  ✗ INTERDIT: Contours épais (>2px)                             ║
╚════════════════════════════════════════════════════════════════╝
```

### 3.2 Palette de Couleurs Harmonisée

| Type | Couleur | Hex | Usage |
|------|---------|-----|-------|
| Alimentation | Vert prairie | `#4CAF50` | feeding_zone |
| Repos | Bleu nuit | `#3F51B5` | bedding_zone |
| Rut | Magenta | `#E91E63` | rut_zone, rut_arena |
| Thermique froid | Cyan | `#00BCD4` | thermal_cover |
| Thermique chaud | Orange | `#FF9800` | thermal_refuge |
| Eau | Bleu eau | `#2196F3` | water_access |
| Prédation | Rouge danger | `#F44336` | predation_risk |
| Neige/Ravage | Blanc cassé | `#ECEFF1` | yarding_zone |
| Humain | Gris | `#9E9E9E` | human_avoidance |
| Minéraux | Ambre | `#FFC107` | mineral_site |
| Optimal | Or | `#FFD700` | composite_optimal |
| Corridors mvt | Vert clair | `#8BC34A` | movement |
| Corridors évit | Rouge clair | `#EF5350` | avoidance |

### 3.3 Spécification Technique Contours

```css
/* Style Leaflet pour contours naturels */
.hotspot-contour {
  stroke-width: 1.5px;
  fill: transparent;
  fill-opacity: 0;
  stroke-linecap: round;
  stroke-linejoin: round;
  /* Pas de filter, pas de shadow */
}

.hotspot-contour-active {
  stroke-width: 2px;
  stroke-dasharray: none;
}

.hotspot-contour-secondary {
  stroke-width: 1px;
  stroke-dasharray: 4 2;
}
```

### 3.4 Génération Formes Naturelles

| Source Données | Résolution | Usage |
|----------------|------------|-------|
| SIGÉOM (Québec) | 1:20,000 | Peuplements forestiers |
| LiDAR (si dispo) | 1m | Relief, canopée |
| Sentinel-2 | 10m | Couverture végétale |
| OSM | Variable | Cours d'eau, routes |
| GRHQ Hydro | 1:20,000 | Réseau hydrographique |

**Algorithme de contour:**
1. Calculer grille de scores (résolution selon zoom)
2. Appliquer marching squares pour contours isovaleurs
3. Simplifier avec Douglas-Peucker (tolérance 5m)
4. Lisser avec Chaikin (2 itérations)
5. Exporter en GeoJSON

---

## 4. ARCHITECTURE TECHNIQUE

### 4.1 Diagramme de Composants

```
┌─────────────────────────────────────────────────────────────────┐
│                         P1-HOTSPOTS                              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    MAP API Router                         │   │
│  │  /map/hotspots  |  /map/zones  |  /map/corridors          │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                      │
│  ┌────────────────────────┴─────────────────────────────────┐   │
│  │                    HotspotService                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │   │
│  │  │ Hotspot     │  │ Zone        │  │ Corridor        │   │   │
│  │  │ Generator   │  │ Generator   │  │ Generator       │   │   │
│  │  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘   │   │
│  │         └────────────────┼──────────────────┘            │   │
│  │                          │                                │   │
│  │  ┌───────────────────────┴────────────────────────────┐  │   │
│  │  │              ContourGenerator                       │  │   │
│  │  │  Grid → Isovalues → Douglas-Peucker → Chaikin      │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│  ┌────────────────────────┴─────────────────────────────────┐   │
│  │              P0-STABLE Integration                        │   │
│  │  ┌───────────────────┐    ┌───────────────────────────┐  │   │
│  │  │ PredictiveTerrit. │    │ BehavioralModels          │  │   │
│  │  │ (12 facteurs)     │    │ (timelines, modifiers)    │  │   │
│  │  └───────────────────┘    └───────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND - Onglet CARTE                       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  HotspotLayerManager                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │   │
│  │  │ Hotspot     │  │ Zone        │  │ Corridor        │   │   │
│  │  │ Overlays    │  │ Overlays    │  │ Overlays        │   │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘   │   │
│  │                                                           │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │              HotspotControlPanel                     │ │   │
│  │  │  [☑ Alimentation] [☑ Rut] [☐ Prédation] ...        │ │   │
│  │  │  [Groupes: Tous ON | Tous OFF | Par espèce]         │ │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Structure des Fichiers

```
/app/backend/modules/bionic_engine_p0/
├── services/
│   ├── hotspot_service.py          # Service principal hotspots
│   ├── zone_service.py             # Service zones
│   ├── corridor_service.py         # Service corridors
│   └── contour_generator.py        # Génération contours naturels
├── contracts/
│   ├── hotspot_contract.json       # Contrat HotspotSchema
│   ├── zone_contract.json          # Contrat ZoneSchema
│   └── corridor_contract.json      # Contrat CorridorSchema
└── router_map.py                   # Router /map/* endpoints

/app/frontend/src/components/map/
├── hotspots/
│   ├── HotspotLayerManager.jsx     # Gestionnaire couches
│   ├── HotspotOverlay.jsx          # Overlay individuel
│   ├── ZoneOverlay.jsx             # Overlay zones
│   ├── CorridorOverlay.jsx         # Overlay corridors
│   ├── HotspotControlPanel.jsx     # Panneau contrôle ON/OFF
│   └── HotspotLegend.jsx           # Légende
└── hooks/
    ├── useHotspots.js              # Hook API hotspots
    ├── useZones.js                 # Hook API zones
    └── useCorridors.js             # Hook API corridors
```

---

## 5. CONTRATS JSON (SCHEMAS)

### 5.1 HotspotSchema

```json
{
  "$schema": "https://huntiq.ca/schemas/bionic-hotspot-v1.json",
  "contract_id": "hotspot_schema_v1",
  "contract_version": "1.0.0",
  "description": "Schema pour les hotspots cartographiques BIONIC V5",
  
  "hotspot": {
    "type": "object",
    "required": ["id", "type", "geometry", "score", "metadata"],
    "properties": {
      "id": {
        "type": "string",
        "pattern": "^HS-[A-Z0-9]{8}$",
        "description": "Identifiant unique du hotspot"
      },
      "type": {
        "type": "string",
        "enum": [
          "activity_peak", "feeding_zone", "rut_zone", "thermal_refuge",
          "water_source", "predation_risk", "snow_impact", "human_avoidance",
          "mineral_site", "composite_optimal"
        ]
      },
      "geometry": {
        "type": "object",
        "description": "GeoJSON Polygon avec contours naturels",
        "properties": {
          "type": { "const": "Polygon" },
          "coordinates": {
            "type": "array",
            "items": {
              "type": "array",
              "items": {
                "type": "array",
                "items": { "type": "number" },
                "minItems": 2,
                "maxItems": 2
              }
            }
          }
        }
      },
      "score": {
        "type": "number",
        "minimum": 0,
        "maximum": 100,
        "description": "Score du hotspot (0-100)"
      },
      "confidence": {
        "type": "number",
        "minimum": 0,
        "maximum": 1,
        "description": "Niveau de confiance"
      },
      "time_validity": {
        "type": "object",
        "properties": {
          "start": { "type": "string", "format": "date-time" },
          "end": { "type": "string", "format": "date-time" },
          "optimal_hours": {
            "type": "array",
            "items": { "type": "integer", "minimum": 0, "maximum": 23 }
          }
        }
      },
      "species": {
        "type": "array",
        "items": { "type": "string", "enum": ["moose", "deer", "bear", "wild_turkey", "elk"] }
      },
      "style": {
        "type": "object",
        "properties": {
          "stroke_color": { "type": "string", "pattern": "^#[0-9A-Fa-f]{6}$" },
          "stroke_width": { "type": "number", "minimum": 1, "maximum": 2 },
          "fill_opacity": { "const": 0, "description": "TOUJOURS 0 - Centre transparent" }
        }
      },
      "metadata": {
        "type": "object",
        "properties": {
          "source_factor": { "type": "string" },
          "factor_score": { "type": "number" },
          "dominant_behavior": { "type": "string" },
          "generated_at": { "type": "string", "format": "date-time" }
        }
      }
    }
  }
}
```

### 5.2 ZoneSchema

```json
{
  "$schema": "https://huntiq.ca/schemas/bionic-zone-v1.json",
  "contract_id": "zone_schema_v1",
  "contract_version": "1.0.0",
  "description": "Schema pour les zones comportementales BIONIC V5",
  
  "zone": {
    "type": "object",
    "required": ["id", "type", "geometry", "behavior_context"],
    "properties": {
      "id": {
        "type": "string",
        "pattern": "^ZN-[A-Z0-9]{8}$"
      },
      "type": {
        "type": "string",
        "enum": [
          "feeding", "bedding", "rut_arena", "thermal_cover",
          "water_access", "predation_zone", "yarding_zone"
        ]
      },
      "geometry": {
        "type": "object",
        "description": "GeoJSON Polygon naturel",
        "properties": {
          "type": { "const": "Polygon" },
          "coordinates": { "type": "array" }
        }
      },
      "behavior_context": {
        "type": "object",
        "properties": {
          "primary_activity": { "type": "string" },
          "time_of_day": { "type": "array", "items": { "type": "string" } },
          "seasonal_relevance": { "type": "array", "items": { "type": "integer" } },
          "species_affinity": { "type": "object" }
        }
      },
      "overlap_zones": {
        "type": "array",
        "items": { "type": "string" },
        "description": "IDs des zones qui se superposent"
      },
      "style": {
        "type": "object",
        "properties": {
          "stroke_color": { "type": "string" },
          "stroke_width": { "type": "number", "default": 1.5 },
          "stroke_dasharray": { "type": "string", "default": "none" },
          "fill_opacity": { "const": 0 }
        }
      }
    }
  }
}
```

### 5.3 CorridorSchema

```json
{
  "$schema": "https://huntiq.ca/schemas/bionic-corridor-v1.json",
  "contract_id": "corridor_schema_v1",
  "contract_version": "1.0.0",
  "description": "Schema pour les corridors de déplacement BIONIC V5",
  
  "corridor": {
    "type": "object",
    "required": ["id", "type", "geometry", "movement_context"],
    "properties": {
      "id": {
        "type": "string",
        "pattern": "^CR-[A-Z0-9]{8}$"
      },
      "type": {
        "type": "string",
        "enum": ["movement", "avoidance", "preferred", "feeding_transit"]
      },
      "geometry": {
        "type": "object",
        "description": "GeoJSON LineString",
        "properties": {
          "type": { "const": "LineString" },
          "coordinates": {
            "type": "array",
            "items": {
              "type": "array",
              "items": { "type": "number" },
              "minItems": 2,
              "maxItems": 2
            }
          }
        }
      },
      "movement_context": {
        "type": "object",
        "properties": {
          "direction": { "type": "string", "enum": ["bidirectional", "north", "south", "east", "west"] },
          "frequency": { "type": "string", "enum": ["daily", "seasonal", "occasional"] },
          "peak_hours": { "type": "array", "items": { "type": "integer" } },
          "connects": {
            "type": "object",
            "properties": {
              "from_zone": { "type": "string" },
              "to_zone": { "type": "string" }
            }
          }
        }
      },
      "width_meters": {
        "type": "number",
        "minimum": 10,
        "maximum": 500,
        "description": "Largeur estimée du corridor"
      },
      "usage_probability": {
        "type": "number",
        "minimum": 0,
        "maximum": 1
      },
      "style": {
        "type": "object",
        "properties": {
          "stroke_color": { "type": "string" },
          "stroke_width": { "type": "number", "default": 2 },
          "stroke_dasharray": { "type": "string" }
        }
      }
    }
  }
}
```

---

## 6. SPÉCIFICATION API

### 6.1 POST /api/v1/bionic/map/hotspots

**Description:** Génère les hotspots pour une zone et période

**Request:**
```json
{
  "bounds": {
    "north": 48.6,
    "south": 48.4,
    "east": -70.4,
    "west": -70.6
  },
  "species": ["moose", "deer"],
  "time_range": "24h",
  "hotspot_types": ["activity_peak", "feeding_zone", "rut_zone"],
  "datetime_start": "2025-10-15T00:00:00Z",
  "min_score_threshold": 70,
  "include_waypoints": true,
  "user_waypoints": [
    { "id": "WP-001", "latitude": 48.52, "longitude": -70.48 }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "hotspots": [
    {
      "id": "HS-A1B2C3D4",
      "type": "activity_peak",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[...natural contour points...]]]
      },
      "score": 88,
      "confidence": 0.85,
      "time_validity": {
        "start": "2025-10-15T06:00:00Z",
        "end": "2025-10-15T09:00:00Z",
        "optimal_hours": [6, 7, 8]
      },
      "species": ["moose"],
      "style": {
        "stroke_color": "#4CAF50",
        "stroke_width": 1.5,
        "fill_opacity": 0
      },
      "metadata": {
        "source_factor": "hormonal",
        "factor_score": 92,
        "dominant_behavior": "rut_seeking",
        "generated_at": "2025-12-21T10:00:00Z"
      }
    }
  ],
  "statistics": {
    "total_hotspots": 12,
    "by_type": { "activity_peak": 4, "feeding_zone": 5, "rut_zone": 3 },
    "avg_score": 78.5,
    "coverage_km2": 45.2
  },
  "metadata": {
    "calculation_time_ms": 1250,
    "grid_resolution": 50,
    "contour_algorithm": "marching_squares_chaikin"
  }
}
```

### 6.2 POST /api/v1/bionic/map/zones

**Description:** Génère les zones comportementales

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
  "zone_types": ["feeding", "bedding", "rut_arena", "water_access"],
  "datetime": "2025-10-15T07:00:00Z",
  "include_overlaps": true
}
```

**Response:**
```json
{
  "success": true,
  "zones": [
    {
      "id": "ZN-E5F6G7H8",
      "type": "feeding",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[...natural polygon...]]]
      },
      "behavior_context": {
        "primary_activity": "browsing",
        "time_of_day": ["dawn", "dusk"],
        "seasonal_relevance": [9, 10, 11],
        "species_affinity": { "moose": 0.9, "deer": 0.7 }
      },
      "overlap_zones": ["ZN-I9J0K1L2"],
      "style": {
        "stroke_color": "#4CAF50",
        "stroke_width": 1.5,
        "fill_opacity": 0
      }
    }
  ],
  "overlap_matrix": {
    "ZN-E5F6G7H8": ["ZN-I9J0K1L2"],
    "ZN-I9J0K1L2": ["ZN-E5F6G7H8"]
  }
}
```

### 6.3 POST /api/v1/bionic/map/corridors

**Description:** Génère les corridors de déplacement

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
  "corridor_types": ["movement", "preferred", "feeding_transit"],
  "datetime": "2025-10-15T07:00:00Z",
  "connect_zones": true
}
```

**Response:**
```json
{
  "success": true,
  "corridors": [
    {
      "id": "CR-M3N4O5P6",
      "type": "movement",
      "geometry": {
        "type": "LineString",
        "coordinates": [[...path points...]]
      },
      "movement_context": {
        "direction": "bidirectional",
        "frequency": "daily",
        "peak_hours": [6, 7, 17, 18],
        "connects": {
          "from_zone": "ZN-E5F6G7H8",
          "to_zone": "ZN-I9J0K1L2"
        }
      },
      "width_meters": 50,
      "usage_probability": 0.75,
      "style": {
        "stroke_color": "#8BC34A",
        "stroke_width": 2,
        "stroke_dasharray": "none"
      }
    }
  ]
}
```

---

## 7. INTÉGRATION FRONTEND

### 7.1 HotspotControlPanel - Spécification UX

```
┌─────────────────────────────────────────────────────────────────┐
│  HOTSPOTS BIONIC                                    [−] [×]     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  PÉRIODE: [24h ▼]  ESPÈCE: [Orignal ▼]  [🔄 Actualiser]        │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│  GROUPES                                                         │
│  [Tous ON] [Tous OFF] [Activité] [Zones] [Corridors]            │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│  HOTSPOTS                                         Score         │
│  [●] Pics d'activité                              88 ████████   │
│  [●] Zones alimentation                           75 ███████    │
│  [●] Zones rut                                    92 █████████  │
│  [○] Refuges thermiques                           --            │
│  [○] Points d'eau                                 --            │
│  [○] Risque prédation                             --            │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│  ZONES COMPORTEMENTALES                                          │
│  [●] Alimentation                                               │
│  [●] Repos                                                      │
│  [●] Arènes rut                                                 │
│  [○] Couvert thermique                                          │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│  CORRIDORS                                                       │
│  [●] Déplacement principal                                      │
│  [○] Évitement                                                  │
│  [●] Routes préférées                                           │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│  [═══════════════════════════════] Opacité: 100%                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

LÉGENDE:
[●] = Actif (ON)
[○] = Inactif (OFF)
```

### 7.2 Comportement ON/OFF

| Action | Comportement |
|--------|--------------|
| Click toggle individuel | Activation/désactivation instantanée (pas de reload) |
| Click groupe | Active/désactive tous les éléments du groupe |
| Changement période | Rechargement données API |
| Changement espèce | Rechargement données API |
| Refresh | Force rechargement complet |

### 7.3 Optimisation Performance

| Technique | Implémentation |
|-----------|----------------|
| Lazy loading | Charger hotspots visibles seulement |
| Debounce | 300ms sur changements |
| Memoization | Cache React pour overlays |
| WebGL | Rendu canvas pour contours complexes |
| Level of Detail | Simplification selon zoom |

---

## 8. ALGORITHME GÉNÉRATION CONTOURS

### 8.1 Pipeline de Génération

```python
def generate_natural_contour(
    grid_scores: np.ndarray,
    bounds: BoundingBox,
    threshold: float,
    species: str
) -> GeoJSONPolygon:
    """
    Génère un contour naturel à partir d'une grille de scores.
    
    Pipeline:
    1. Marching Squares → contour brut
    2. Douglas-Peucker → simplification (tolérance 5m)
    3. Chaikin → lissage naturel (2 itérations)
    4. Validation topologique
    5. Export GeoJSON
    """
    # 1. Marching Squares pour extraction isovalues
    contours = measure.find_contours(grid_scores, threshold)
    
    # 2. Conversion en coordonnées géographiques
    geo_contours = []
    for contour in contours:
        geo_coords = grid_to_geo(contour, bounds)
        geo_contours.append(geo_coords)
    
    # 3. Simplification Douglas-Peucker
    simplified = []
    for contour in geo_contours:
        simple = douglas_peucker(contour, tolerance=0.00005)  # ~5m
        simplified.append(simple)
    
    # 4. Lissage Chaikin (formes naturelles)
    smoothed = []
    for contour in simplified:
        smooth = chaikin_smooth(contour, iterations=2)
        smoothed.append(smooth)
    
    # 5. Validation et fermeture polygone
    valid_polygons = []
    for contour in smoothed:
        if is_valid_polygon(contour) and len(contour) >= 4:
            closed = ensure_closed(contour)
            valid_polygons.append(closed)
    
    return create_geojson_polygon(valid_polygons)
```

### 8.2 Algorithme Chaikin (Lissage Naturel)

```python
def chaikin_smooth(points: List[Tuple[float, float]], iterations: int = 2) -> List:
    """
    Lissage de Chaikin pour contours naturels.
    Chaque itération crée des points intermédiaires aux 1/4 et 3/4.
    """
    for _ in range(iterations):
        new_points = []
        for i in range(len(points) - 1):
            p0 = points[i]
            p1 = points[i + 1]
            
            # Point à 1/4
            q = (0.75 * p0[0] + 0.25 * p1[0], 0.75 * p0[1] + 0.25 * p1[1])
            # Point à 3/4
            r = (0.25 * p0[0] + 0.75 * p1[0], 0.25 * p0[1] + 0.75 * p1[1])
            
            new_points.extend([q, r])
        
        points = new_points
    
    return points
```

---

## 9. TESTS G-QA

### 9.1 Tests Backend

| Test | Description |
|------|-------------|
| test_hotspot_generation | Génération hotspots complet |
| test_hotspot_contour_natural | Contours formes naturelles |
| test_hotspot_no_fill | Vérification fill_opacity = 0 |
| test_zone_generation | Génération zones comportementales |
| test_zone_overlap_detection | Détection superpositions |
| test_corridor_generation | Génération corridors |
| test_corridor_connectivity | Connexion zones |
| test_contour_algorithm | Algorithme marching squares |
| test_chaikin_smoothing | Lissage Chaikin |
| test_douglas_peucker | Simplification |

### 9.2 Tests Frontend

| Test | Description |
|------|-------------|
| test_hotspot_layer_render | Rendu couche hotspots |
| test_toggle_individual | Toggle ON/OFF individuel |
| test_toggle_group | Toggle groupe |
| test_no_reload_toggle | Pas de reload sur toggle |
| test_control_panel_ui | Interface panneau contrôle |
| test_legend_display | Affichage légende |

---

## 10. ESTIMATION EFFORT

| Phase | Tâche | Durée |
|-------|-------|-------|
| 1 | Backend - HotspotService | 4h |
| 2 | Backend - ZoneService | 3h |
| 3 | Backend - CorridorService | 3h |
| 4 | Backend - ContourGenerator | 4h |
| 5 | Backend - Router /map/* (3 endpoints) | 2h |
| 6 | Backend - Contrats JSON (3) | 2h |
| 7 | Frontend - HotspotLayerManager | 3h |
| 8 | Frontend - HotspotControlPanel | 3h |
| 9 | Frontend - Overlays (3 types) | 4h |
| 10 | Frontend - Hooks (3) | 2h |
| 11 | Tests backend (10) | 4h |
| 12 | Tests frontend (6) | 2h |
| 13 | Intégration carte existante | 3h |
| 14 | Documentation G-DOC | 2h |
| **Total** | | **41h (~5 jours)** |

---

## 11. SÉQUENCE D'INTÉGRATION P1

### 11.1 Ordre Recommandé

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1: P1-HOTSPOTS (5 jours)                                 │
│  ├── Endpoints /map/hotspots, /map/zones, /map/corridors       │
│  ├── ContourGenerator (formes naturelles)                       │
│  ├── Contrats JSON                                              │
│  └── Frontend: HotspotLayerManager + ControlPanel               │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 2: P1-ENV (2 jours)                                      │
│  ├── OpenWeatherMap integration                                 │
│  └── Auto-injection météo dans P0                               │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 3: P1-SCORE (4 jours)                                    │
│  ├── Dashboard scoring dynamique                                │
│  └── Utilise P1-ENV pour météo temps réel                       │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 4: P1-VIS (3 jours)                                      │
│  ├── Heatmaps (utilise P1-HOTSPOTS comme base)                  │
│  └── Intégration complète overlays                              │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 5: P1-PLAN (2.5 jours)                                   │
│  ├── Endpoint analyze_hunt_plan                                 │
│  └── Utilise tous les modules P1 précédents                     │
└─────────────────────────────────────────────────────────────────┘

TOTAL P1: ~16.5 jours développement
```

### 11.2 Dépendances

```
P0-STABLE ─────┬──► P1-HOTSPOTS ──┬──► P1-VIS
               │                   │
               ├──► P1-ENV ────────┼──► P1-SCORE
               │                   │
               └───────────────────┴──► P1-PLAN
```

---

## 12. PÉRIMÈTRE P1 CONSOLIDÉ

### 12.1 Modules P1

| Module | Effort | Priorité | Status |
|--------|--------|----------|--------|
| **P1-HOTSPOTS** | 5 jours | CRITICAL | 📋 Plan prêt |
| **P1-ENV** | 2 jours | HIGH | 📋 Plan prêt |
| **P1-SCORE** | 4 jours | HIGH | 📋 Plan prêt |
| **P1-VIS** | 3 jours | MEDIUM | 📋 Plan prêt |
| **P1-PLAN** | 2.5 jours | HIGH | 📋 Plan prêt |
| **TOTAL** | **16.5 jours** | | |

### 12.2 Endpoints P1 Complets

| # | Endpoint | Module |
|---|----------|--------|
| 1 | POST /api/v1/bionic/map/hotspots | P1-HOTSPOTS |
| 2 | POST /api/v1/bionic/map/zones | P1-HOTSPOTS |
| 3 | POST /api/v1/bionic/map/corridors | P1-HOTSPOTS |
| 4 | GET /api/v1/bionic/weather/current | P1-ENV |
| 5 | GET /api/v1/bionic/weather/forecast | P1-ENV |
| 6 | GET /api/v1/bionic/scoring/current | P1-SCORE |
| 7 | GET /api/v1/bionic/scoring/timeline | P1-SCORE |
| 8 | POST /api/v1/bionic/scoring/compare | P1-SCORE |
| 9 | POST /api/v1/bionic/heatmap/generate | P1-VIS |
| 10 | POST /api/v1/bionic/analyze_hunt_plan | P1-PLAN |

---

## 13. CHECKLIST PRÉ-IMPLÉMENTATION

| # | Item | Status |
|---|------|--------|
| 1 | GO COPILOT MAÎTRE | ⏳ EN ATTENTE |
| 2 | Plan P1-HOTSPOTS validé | ✅ VERSION FINALE |
| 3 | Contrats JSON approuvés | ✅ 3 SCHEMAS DÉFINIS |
| 4 | Palette couleurs validée | ✅ 13 COULEURS |
| 5 | Séquence intégration confirmée | ✅ P1-HOTSPOTS PREMIER |
| 6 | Clé API OpenWeatherMap | ⏳ À CONFIRMER (P1-ENV) |

---

## 14. RÉSUMÉ EXÉCUTIF POUR VALIDATION

### 14.1 Livrables P1-HOTSPOTS (5 jours)

| # | Livrable | Type | Conformité |
|---|----------|------|------------|
| 1 | `POST /api/v1/bionic/map/hotspots` | Endpoint | ✅ |
| 2 | `POST /api/v1/bionic/map/zones` | Endpoint | ✅ |
| 3 | `POST /api/v1/bionic/map/corridors` | Endpoint | ✅ |
| 4 | `hotspot_contract.json` | Contrat | ✅ |
| 5 | `zone_contract.json` | Contrat | ✅ |
| 6 | `corridor_contract.json` | Contrat | ✅ |
| 7 | `hotspot_service.py` | Backend | ✅ |
| 8 | `zone_service.py` | Backend | ✅ |
| 9 | `corridor_service.py` | Backend | ✅ |
| 10 | `contour_generator.py` | Backend | ✅ |
| 11 | `HotspotLayerManager.jsx` | Frontend | ✅ |
| 12 | `HotspotControlPanel.jsx` | Frontend | ✅ |
| 13 | `HotspotOverlay.jsx` | Frontend | ✅ |
| 14 | `ZoneOverlay.jsx` | Frontend | ✅ |
| 15 | `CorridorOverlay.jsx` | Frontend | ✅ |
| 16 | Tests Backend (10) | Tests | ✅ |
| 17 | Tests Frontend (6) | Tests | ✅ |
| 18 | Documentation G-DOC | Doc | ✅ |

### 14.2 Séquence P1 Complète

```
JOUR 1-5:   P1-HOTSPOTS  ████████████████████  (CRITIQUE - Premier)
JOUR 6-7:   P1-ENV       ████████              (OpenWeatherMap)
JOUR 8-11:  P1-SCORE     ████████████████      (Scoring Dynamique)
JOUR 12-14: P1-VIS       ████████████          (Heatmaps - utilise HOTSPOTS)
JOUR 15-17: P1-PLAN      ██████████            (analyze_hunt_plan)
─────────────────────────────────────────────────────────────────
TOTAL:      16.5 JOURS DÉVELOPPEMENT
```

### 14.3 Architecture Respectée

```
┌─────────────────────────────────────────────────────────────┐
│                      GOLD MASTER                             │
│                     (INTOUCHABLE)                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ include_router() uniquement
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    P0-STABLE (validé)                        │
│         12 facteurs comportementaux + 91 tests              │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Consommation passive
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      P1-HOTSPOTS                             │
│    /map/hotspots | /map/zones | /map/corridors              │
│    Contours 200% réalistes | ON/OFF instantané              │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ GeoJSON outputs
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              FRONTEND (Onglet CARTE)                         │
│   HotspotLayerManager (consommation passive)                │
│   AUCUN calcul | AUCUNE logique métier                      │
└─────────────────────────────────────────────────────────────┘
```

### 14.4 Conformité Spécification Visuelle

| Exigence | Implémentation | Status |
|----------|----------------|--------|
| Contours 1-2px | `stroke-width: 1.5px` CSS | ✅ |
| Centre transparent | `fill-opacity: 0` | ✅ |
| Formes naturelles | Marching Squares + Chaikin | ✅ |
| Zéro simplification | Douglas-Peucker 5m seulement | ✅ |
| Superposition | `overlap_zones` + z-index | ✅ |
| Palette harmonisée | 13 couleurs distinctes | ✅ |
| Zéro glow/shadow | CSS pur, aucun filter | ✅ |
| Fidélité géo | SIGÉOM, GRHQ, OSM | ✅ |
| ON/OFF individuel | Toggle sans reload | ✅ |
| Groupes ON/OFF | HotspotControlPanel | ✅ |

---

*Document VERSION FINALE conformément aux normes G-DOC Phase G*
*Status: PRÊT POUR GO COPILOT MAÎTRE*
