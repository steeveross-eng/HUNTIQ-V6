# PHASE 3 - Plan Détaillé : Moteurs Métier Backend

## 📋 Objectif
Extraire les 8 moteurs métier (business logic) du monolithe vers des modules indépendants et versionnés.

---

## 🎯 Modules à Extraire

### 1. `marketplace_engine` (Priorité: HAUTE)
**Source**: `/app/backend/marketplace.py` (31 045 lignes)

**Fonctionnalités à extraire:**
- Gestion des listings de produits
- Système de recherche et filtrage
- Gestion des vendeurs
- Système d'évaluation et avis
- Transactions C2C (Consumer-to-Consumer)

**Endpoints cibles:**
```
/api/v1/marketplace/
/api/v1/marketplace/listings
/api/v1/marketplace/sellers
/api/v1/marketplace/reviews
/api/v1/marketplace/transactions
```

**Dépendances:** notification_engine (pour les alertes)

---

### 2. `user_engine` (Priorité: HAUTE)
**Sources**: server.py (sections utilisateur), partnership.py

**Fonctionnalités à extraire:**
- Inscription et authentification
- Profils utilisateurs
- Préférences et paramètres
- Historique d'activité
- Gestion des rôles

**Endpoints cibles:**
```
/api/v1/user/
/api/v1/user/profile
/api/v1/user/preferences
/api/v1/user/history
/api/v1/user/roles
```

**Dépendances:** Aucune (module fondamental)

---

### 3. `admin_engine` (Priorité: HAUTE)
**Source**: server.py (sections @api_router.*/admin/*), maintenance_controller.py

**Fonctionnalités à extraire:**
- Authentification admin
- Tableau de bord
- Gestion des produits
- Rapports et statistiques
- Alertes système
- Gestion de maintenance

**Endpoints cibles:**
```
/api/v1/admin/
/api/v1/admin/auth
/api/v1/admin/dashboard
/api/v1/admin/products
/api/v1/admin/reports
/api/v1/admin/alerts
/api/v1/admin/maintenance
```

**Dépendances:** user_engine

---

### 4. `territory_engine` (Priorité: MOYENNE)
**Sources**: `/app/backend/territories.py` (1 597 lignes), lands_rental.py

**Fonctionnalités à extraire:**
- Gestion des territoires de chasse
- Zones et périmètres
- Locations de terres
- Droits d'accès
- Cartes et polygones

**Endpoints cibles:**
```
/api/v1/territory/
/api/v1/territory/zones
/api/v1/territory/rentals
/api/v1/territory/access
/api/v1/territory/maps
```

**Dépendances:** geospatial_engine, wms_engine

---

### 5. `referral_engine` (Priorité: MOYENNE)
**Source**: `/app/backend/referral_system.py` (914 lignes)

**Fonctionnalités à extraire:**
- Système de parrainage
- Codes d'invitation
- Niveaux et tiers
- Calcul des commissions
- Promotions saisonnières
- Applications partenaires

**Endpoints cibles:**
```
/api/v1/referral/
/api/v1/referral/invites
/api/v1/referral/tiers
/api/v1/referral/commissions
/api/v1/referral/promotions
/api/v1/referral/partners
```

**Dépendances:** user_engine

---

### 6. `tracking_engine` (Priorité: MOYENNE)
**Source**: `/app/backend/live_tracking.py` (21 943 lignes)

**Fonctionnalités à extraire:**
- Suivi GPS en temps réel
- Historique des positions
- Partage de position
- Alertes de proximité
- Zones de sécurité

**Endpoints cibles:**
```
/api/v1/tracking/
/api/v1/tracking/live
/api/v1/tracking/history
/api/v1/tracking/share
/api/v1/tracking/alerts
```

**Dépendances:** geospatial_engine, user_engine

---

### 7. `notification_engine` (Priorité: MOYENNE)
**Sources**: `/app/backend/notifications.py`, `/app/backend/email_notifications.py`, `/app/backend/email_service.py`

**Fonctionnalités à extraire:**
- Notifications in-app
- Notifications push
- Emails transactionnels
- Templates de messages
- Préférences de notification

**Endpoints cibles:**
```
/api/v1/notification/
/api/v1/notification/send
/api/v1/notification/templates
/api/v1/notification/preferences
/api/v1/notification/history
```

**Dépendances:** user_engine

---

### 8. `plugins_engine` (Priorité: BASSE)
**Sources**: feature_controls.py, autres modules optionnels

**Fonctionnalités à extraire:**
- Gestion des features flags
- Activation/désactivation de fonctionnalités
- Configuration dynamique
- Extensions tierces

**Endpoints cibles:**
```
/api/v1/plugins/
/api/v1/plugins/features
/api/v1/plugins/config
/api/v1/plugins/extensions
```

**Dépendances:** admin_engine

---

## 📊 Ordre d'Extraction Recommandé

| Étape | Module | Raison | Lignes estimées |
|-------|--------|--------|-----------------|
| 1 | user_engine | Fondamental, aucune dépendance | ~300 |
| 2 | admin_engine | Dépend de user_engine | ~500 |
| 3 | notification_engine | Utilisé par plusieurs modules | ~400 |
| 4 | referral_engine | Déjà isolé dans referral_system.py | ~350 |
| 5 | territory_engine | Dépend de geo/wms engines | ~400 |
| 6 | tracking_engine | Dépend de geo/user | ~350 |
| 7 | marketplace_engine | Complexe, nombreuses dépendances | ~500 |
| 8 | plugins_engine | Non critique | ~200 |

---

## 🛠️ Structure Type par Module

```
/app/backend/modules/{module_name}/
├── __init__.py              # Exports du module
├── v1/
│   ├── __init__.py          # Version exports
│   ├── router.py            # FastAPI router
│   ├── service.py           # Logique métier
│   ├── models.py            # Modèles Pydantic
│   ├── schemas.py           # Schémas DB (si différents)
│   └── data/                # Données statiques
│       └── *.py
```

---

## ✅ Critères de Validation par Module

1. **Isolation**: Aucune importation croisée avec autres modules métier
2. **Versionnement**: Préfixe `/api/v1/` sur tous les endpoints
3. **Documentation**: Docstrings sur toutes les fonctions publiques
4. **Tests**: Endpoints testables via curl
5. **Non-régression**: API legacy toujours fonctionnelle

---

## ⚠️ Risques Identifiés

| Risque | Impact | Mitigation |
|--------|--------|------------|
| Dépendances circulaires | Élevé | Extraire user_engine en premier |
| Régression des commandes | Critique | Tests E2E après chaque extraction |
| Perte de données | Critique | Pas de modification des modèles MongoDB |
| Interruption de service | Moyen | Hot reload, pas de redémarrage complet |

---

## 📅 Estimation

- **Durée estimée**: 6-8 heures de travail
- **Modules par session**: 2-3 modules maximum
- **Tests requis**: Après chaque module

---

## 🚀 Prêt pour Exécution

Confirmez l'ordre d'extraction souhaité ou ajustez les priorités avant de commencer.
