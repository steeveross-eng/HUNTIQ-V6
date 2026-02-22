# HUNTIQ V5-ULTIME-FUSION — Documentation API

**Version:** 5.0.0  
**Base URL:** `https://hunt-plan-engine.preview.emergentagent.com`  
**Date:** 2026-02-17  
**Phase:** Release Candidate RC-1.0.0

---

## 📚 Table des Matières

1. [Authentification](#1-authentification)
2. [Waypoint Engine](#2-waypoint-engine)
3. [Waypoint Scoring Engine](#3-waypoint-scoring-engine)
4. [Recommendation Engine](#4-recommendation-engine)
5. [Territory Engine](#5-territory-engine)
6. [Marketing Engine](#6-marketing-engine)
7. [Analytics Engine](#7-analytics-engine)
8. [Tracking Engine](#8-tracking-engine)
9. [AI Engines](#9-ai-engines)
10. [Utilitaires](#10-utilitaires)

---

## 1. Authentification

### POST `/api/auth/register`
Inscription d'un nouvel utilisateur.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "jwt_token_here"
}
```

### POST `/api/auth/login`
Connexion utilisateur.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "success": true,
  "token": "jwt_token_here",
  "user": { ... }
}
```

### POST `/api/auth/logout`
Déconnexion utilisateur.

---

## 2. Waypoint Engine

### GET `/api/v1/waypoints/`
Informations du module Waypoint Engine.

**Response:**
```json
{
  "module": "waypoint_engine",
  "version": "1.0.0",
  "description": "Moteur de gestion des waypoints utilisateur",
  "features": [
    "Create waypoints from map interaction",
    "GPS tracking waypoints",
    "Waypoint filtering by source/user",
    "Geographic bounds queries",
    "Waypoint statistics"
  ]
}
```

### POST `/api/v1/waypoints/create`
Créer un nouveau waypoint.

**Request Body:**
```json
{
  "lat": 46.8139,
  "lng": -71.2080,
  "name": "Mon spot favori",
  "source": "user_double_click",
  "user_id": "user_123"
}
```

**Sources supportées:**
- `user_double_click` — Création via double-clic sur la carte
- `user_manual` — Création manuelle (formulaire)
- `gps_tracking` — Tracking GPS automatique
- `import` — Import externe
- `ai_suggestion` — Suggestion IA

**Response:**
```json
{
  "success": true,
  "waypoint": {
    "id": "waypoint_456",
    "lat": 46.8139,
    "lng": -71.2080,
    "name": "Mon spot favori",
    "source": "user_double_click",
    "user_id": "user_123",
    "timestamp": "2026-02-17T20:30:00Z"
  }
}
```

### GET `/api/v1/waypoints`
Lister les waypoints avec filtres optionnels.

**Query Parameters:**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `user_id` | string | Filtrer par utilisateur |
| `source` | string | Filtrer par source |
| `limit` | integer | Nombre max (défaut: 100, max: 1000) |

**Response:**
```json
{
  "success": true,
  "total": 42,
  "waypoints": [ ... ]
}
```

### GET `/api/v1/waypoints/bounds`
Waypoints dans une zone géographique.

**Query Parameters:**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `north` | float | Latitude nord |
| `south` | float | Latitude sud |
| `east` | float | Longitude est |
| `west` | float | Longitude ouest |
| `user_id` | string | (optionnel) Filtrer par utilisateur |
| `limit` | integer | Nombre max (défaut: 500) |

### GET `/api/v1/waypoints/stats`
Statistiques des waypoints.

**Response:**
```json
{
  "success": true,
  "stats": {
    "total": 150,
    "by_source": {
      "user_double_click": 80,
      "gps_tracking": 50,
      "user_manual": 20
    },
    "by_user": { ... }
  }
}
```

### GET `/api/v1/waypoints/{waypoint_id}`
Récupérer un waypoint par ID.

### PUT `/api/v1/waypoints/{waypoint_id}`
Mettre à jour un waypoint.

### DELETE `/api/v1/waypoints/{waypoint_id}`
Supprimer un waypoint.

---

## 3. Waypoint Scoring Engine

### GET `/api/v1/waypoint-scoring/`
Informations du module WQS (Waypoint Quality Score).

### GET `/api/v1/waypoint-scoring/wqs`
Calculer le score de qualité d'un waypoint.

**Query Parameters:**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `lat` | float | Latitude |
| `lng` | float | Longitude |
| `species` | string | Espèce cible (deer, moose, bear, turkey) |

**Response:**
```json
{
  "success": true,
  "wqs": {
    "overall_score": 85,
    "components": {
      "habitat": 90,
      "terrain": 82,
      "weather": 78,
      "temporal": 88
    },
    "recommendation": "Excellent potentiel pour le cerf"
  }
}
```

### GET `/api/v1/waypoint-scoring/forecast`
Prévision de succès.

### GET `/api/v1/waypoint-scoring/heatmap`
Données heatmap pour visualisation.

### GET `/api/v1/waypoint-scoring/recommendations`
Recommandations de waypoints basées sur les scores.

### GET `/api/v1/waypoint-scoring/recommendations/ai`
Recommandation IA GPT-5.2 personnalisée.

---

## 4. Recommendation Engine

### GET `/api/v1/recommendation/`
Informations du module Recommendation Engine.

**Response:**
```json
{
  "module": "recommendation_engine",
  "version": "1.0.0",
  "status": "operational",
  "features": [
    "Recommandations personnalisées",
    "Filtrage collaboratif",
    "Filtrage basé sur le contenu",
    "Recommandations contextuelles",
    "Produits similaires",
    "Produits complémentaires"
  ]
}
```

### GET `/api/v1/recommendation/health`
Health check.

### GET `/api/v1/recommendation/strategies`
Recommandations de stratégies de chasse.

**Query Parameters:**
| Paramètre | Type | Description |
|-----------|------|-------------|
| `species` | string | Espèce cible (requis) |
| `season` | string | Saison (optionnel) |
| `temperature` | float | Température actuelle |
| `wind_speed` | float | Vitesse du vent |
| `user_id` | string | ID utilisateur pour personnalisation |

**Response:**
```json
{
  "success": true,
  "data": {
    "strategies": [
      {
        "name": "Approche silencieuse",
        "score": 92,
        "description": "...",
        "tips": [ ... ]
      }
    ]
  }
}
```

### GET `/api/v1/recommendation/for-context`
Recommandations contextuelles.

**Query Parameters:**
- `species` (requis)
- `season` (requis)
- `temperature`, `humidity`, `wind_speed`
- `lat`, `lng`
- `limit`

### GET `/api/v1/recommendation/personalized/{user_id}`
Recommandations personnalisées pour un utilisateur.

### GET `/api/v1/recommendation/similar/{product_id}`
Produits similaires.

### GET `/api/v1/recommendation/complementary/{product_id}`
Produits complémentaires.

### POST `/api/v1/recommendation/feedback`
Soumettre un feedback sur une recommandation.

---

## 5. Territory Engine

### GET `/api/v1/territory/`
Informations du module Territory.

### GET `/api/v1/territory/waypoints`
Waypoints du territoire utilisateur.

### POST `/api/v1/territory/waypoints`
Créer un waypoint dans le territoire.

### GET `/api/v1/territory/places`
Lieux enregistrés.

### POST `/api/v1/territory/places`
Créer un lieu.

### GET `/api/v1/territory/zones`
Zones de chasse.

---

## 6. Marketing Engine

### GET `/api/v1/marketing/`
Informations du module Marketing Automation.

### GET `/api/v1/marketing/campaigns`
Liste des campagnes actives.

### POST `/api/v1/marketing/campaigns/trigger`
Déclencher une campagne.

### GET `/api/v1/marketing/segments`
Segments utilisateurs.

---

## 7. Analytics Engine

### GET `/api/v1/analytics/`
Informations du module Analytics.

### GET `/api/v1/analytics/stats`
Statistiques globales.

### GET `/api/v1/analytics/trips`
Statistiques des sorties de chasse.

### GET `/api/v1/analytics/success-rate`
Taux de succès par période.

---

## 8. Tracking Engine

### GET `/api/v1/tracking/`
Informations du module Tracking.

### POST `/api/v1/tracking/event`
Enregistrer un événement.

**Request Body:**
```json
{
  "event_type": "page_view",
  "page": "/territoire",
  "user_id": "user_123",
  "metadata": { ... }
}
```

### GET `/api/v1/tracking/events`
Lister les événements.

### GET `/api/v1/tracking/funnels`
Analyse des funnels de conversion.

### GET `/api/v1/tracking/heatmap`
Données heatmap utilisateur.

---

## 9. AI Engines

### Weather AI
**GET `/api/v1/weather/current`** — Météo actuelle  
**GET `/api/v1/weather/forecast`** — Prévisions

### Scoring AI
**GET `/api/v1/scoring/calculate`** — Calcul de score IA

### Strategy AI
**GET `/api/v1/strategy/recommend`** — Stratégie recommandée

### Prediction AI
**GET `/api/v1/ai/predict`** — Prédictions IA

---

## 10. Utilitaires

### GET `/api/health`
Health check global.

**Response:**
```json
{
  "status": "healthy",
  "version": "5.0.0",
  "modules": {
    "waypoint_engine": "operational",
    "recommendation_engine": "operational",
    "analytics_engine": "operational"
  }
}
```

### GET `/api/docs`
Documentation Swagger UI.

### GET `/api/openapi.json`
Spécification OpenAPI complète.

---

## 📊 Codes de Réponse

| Code | Description |
|------|-------------|
| 200 | Succès |
| 201 | Création réussie |
| 400 | Requête invalide |
| 401 | Non authentifié |
| 403 | Accès interdit |
| 404 | Ressource non trouvée |
| 500 | Erreur serveur |

---

## 🔐 Authentification

La plupart des endpoints nécessitent un token JWT.

**Header d'authentification:**
```
Authorization: Bearer <jwt_token>
```

---

## 📁 Fichiers de Référence

- **OpenAPI JSON:** `/app/docs/openapi.json`
- **Rapport E2E:** `/app/test_reports/e2e_final.json`
- **Conformité P0:** `/app/docs/RAPPORT_CONFORMITE_P0_LAYOUT.md`

---

*Documentation générée automatiquement — HUNTIQ V5-ULTIME-FUSION API*
*Phase 22 — Release Candidate RC-1.0.0*
