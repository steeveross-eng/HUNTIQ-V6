# BIONIC V3 - Modular Architecture

## Architecture Modulaire - 40 Modules Backend

### Dernière mise à jour: 9 Février 2026
### Version: 2.0 (Phase 8+ Complete)

---

## Vue d'Ensemble

L'architecture BIONIC V3 est composée de **40 modules backend** indépendants, chacun gérant un domaine fonctionnel spécifique.

### Statistiques
| Métrique | Valeur |
|----------|--------|
| Total Modules | 40 |
| Modules Documentés | 8 |
| Tests Unitaires | 3 fichiers |
| API Endpoints | 100+ |

---

## Modules par Phase

### Phase 2 - Core Engines (5 modules) ✅
| Module | Prefix | Documentation |
|--------|--------|---------------|
| `nutrition_engine` | `/api/v1/nutrition` | ✅ README.md |
| `scoring_engine` | `/api/v1/scoring` | ✅ README.md |
| `weather_engine` | `/api/v1/weather` | ✅ README.md |
| `ai_engine` | `/api/v1/ai` | ✅ README.md |
| `strategy_engine` | `/api/v1/strategy` | ✅ README.md |

### Phase 3-6 - Plan Maître Engines (25+ modules) ✅
| Module | Description |
|--------|-------------|
| `recommendation_engine` | Recommandations produits |
| `wildlife_behavior_engine` | Comportement faune |
| `territory_engine` | Gestion territoires |
| `collaborative_engine` | Observations communautaires |
| `ecoforestry_engine` | Analyse écoforestière |
| `behavioral_engine` | Patterns comportementaux |
| ... | Et 20+ autres modules |

### Phase 7 - Decoupled Engines (7 modules) ✅
| Module | Prefix | Documentation |
|--------|--------|---------------|
| `products_engine` | `/api/v1/products` | ✅ README.md |
| `orders_engine` | `/api/v1/orders` | ✅ README.md |
| `suppliers_engine` | `/api/v1/suppliers` | - |
| `customers_engine` | `/api/v1/customers` | - |
| `cart_engine` | `/api/v1/cart` | - |
| `affiliate_engine` | `/api/v1/affiliate` | - |
| `alerts_engine` | `/api/v1/alerts` | - |

### Phase 8 - Legal Time & Predictive (2 modules) ✅ NEW
| Module | Prefix | Documentation |
|--------|--------|---------------|
| `legal_time_engine` | `/api/v1/legal-time` | ✅ README.md |
| `predictive_engine` | `/api/v1/predictive` | ✅ README.md |

---

## Tests

### Tests Unitaires
```bash
cd /app/backend

# Tous les tests
pytest tests/ -v

# Tests Legal Time Engine
pytest tests/test_legal_time_engine.py -v

# Tests Predictive Engine
pytest tests/test_predictive_engine.py -v

# Tests Intégration Frontend-Backend
pytest tests/test_frontend_backend_integration.py -v
```

### Couverture des Tests
| Fichier | Tests | Couverture |
|---------|-------|------------|
| test_legal_time_engine.py | 35+ | Services + Router |
| test_predictive_engine.py | 40+ | Services + Router |
| test_frontend_backend_integration.py | 20+ | E2E API |

---

## Structure des Modules

Chaque module suit la structure standard:

```
module_name/
├── __init__.py           # Export du router
├── README.md             # Documentation (si disponible)
└── v1/
    ├── __init__.py       # Exports v1
    ├── router.py         # Endpoints FastAPI
    ├── service.py        # Logique métier
    └── models.py         # Modèles Pydantic
```

---

## Intégration Frontend

Les modules sont consommés par les services frontend:

| Service Frontend | Module Backend |
|------------------|----------------|
| LegalTimeService | legal_time_engine |
| PredictiveService | predictive_engine |
| WeatherService | weather_engine |
| ScoringService | scoring_engine |
| ProductsService | products_engine |
| OrdersService | orders_engine |

---

## Changelog

### Phase 8+ (9 Février 2026)
- ✅ Ajout `legal_time_engine` avec 7 endpoints
- ✅ Ajout `predictive_engine` avec 5 endpoints
- ✅ Documentation complète Phase 8
- ✅ Tests unitaires complets
- ✅ Tests intégration frontend-backend

### Phase 7 (Février 2026)
- ✅ Découplage 7 modules du monolithe

---

*BIONIC V3 - Modular Architecture - 40 Modules - Created 2026-02-09*
