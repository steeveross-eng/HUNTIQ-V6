# DOCUMENTATION COMPLÈTE - SEO ENGINE V5-ULTIME
## BIONIC - Module SEO Premium

**Date de génération :** Décembre 2025  
**Version :** 1.0.0  
**Architecture :** LEGO V5 (Module Isolé)  
**Auteur :** BIONIC System  

---

## TABLE DES MATIÈRES

1. [Vue d'Ensemble](#1-vue-densemble)
2. [Architecture et Structure des Fichiers](#2-architecture-et-structure-des-fichiers)
3. [Endpoints API Complets (41)](#3-endpoints-api-complets-41)
4. [Fonctionnalités Actives](#4-fonctionnalités-actives)
5. [Logique Métier Détaillée](#5-logique-métier-détaillée)
6. [Automatisations en Place](#6-automatisations-en-place)
7. [Règles SEO Existantes](#7-règles-seo-existantes)
8. [Dépendances Internes](#8-dépendances-internes)
9. [Intégrations Actuelles](#9-intégrations-actuelles)
10. [Indicateurs de Performance (KPIs)](#10-indicateurs-de-performance-kpis)
11. [Paramètres et Configurations](#11-paramètres-et-configurations)
12. [Schémas de Données (MongoDB)](#12-schémas-de-données-mongodb)
13. [Base de Données Fournisseurs](#13-base-de-données-fournisseurs)
14. [Annexes Techniques](#14-annexes-techniques)

---

## 1. VUE D'ENSEMBLE

### 1.1 Description du Module

Le **SEO Engine V5-ULTIME** est le module central de gestion du référencement naturel de la plateforme BIONIC. Il implémente une architecture de contenu basée sur des **clusters thématiques** avec une stratégie visant une augmentation de **+300% du trafic organique**.

### 1.2 Objectifs Stratégiques

| Objectif | Description | Métrique Cible |
|----------|-------------|----------------|
| Position moyenne | Apparaître dans le top 10 Google | < 10.0 |
| CTR | Taux de clic sur les résultats | > 5.0% |
| Score SEO | Qualité technique des pages | > 80/100 |
| Indexation | Taux de pages indexées | > 95% |
| Conversion | Visiteurs → Actions | > 2.0% |

### 1.3 Principes Architecturaux

- **Module Isolé** : Aucun import croisé avec d'autres modules
- **Architecture LEGO V5** : Composants indépendants et testables
- **Intégration Knowledge Layer** : Enrichissement des contenus avec données comportementales
- **Bilingue** : Support FR/EN natif (règle permanente)

### 1.4 Composants Principaux

```
seo_router.py         → Routes API (41 endpoints)
seo_service.py        → Orchestration des services
seo_clusters.py       → Gestion des clusters SEO
seo_pages.py          → Gestion des pages (piliers, satellites, opportunités)
seo_jsonld.py         → Schémas JSON-LD structurés
seo_analytics.py      → Analytics et KPIs
seo_automation.py     → Règles d'automatisation
seo_generation.py     → Génération de structures de contenu
seo_content_generator.py → Génération IA via LLM
seo_suppliers_router.py  → Base de données fournisseurs (104 entrées)
```

---

## 2. ARCHITECTURE ET STRUCTURE DES FICHIERS

### 2.1 Arborescence Complète

```
/app/backend/modules/seo_engine/
├── __init__.py                 # Exports publics du module
├── seo_router.py               # Routes API principales (prefix: /api/v1/bionic/seo)
├── seo_suppliers_router.py     # Routes fournisseurs (prefix: /api/v1/bionic/seo/suppliers)
├── seo_service.py              # Service orchestrateur
├── seo_models.py               # Modèles Pydantic (13 enums, 18 modèles)
├── seo_clusters.py             # Gestionnaire de clusters (9 clusters de base)
├── seo_pages.py                # Gestionnaire de pages (6 templates)
├── seo_jsonld.py               # Schémas JSON-LD (9 types supportés)
├── seo_analytics.py            # Analytics et métriques
├── seo_automation.py           # Règles d'automatisation (5 règles par défaut)
├── seo_generation.py           # Génération de structures
├── seo_content_generator.py    # Génération IA (Emergent LLM Key)
└── data/
    ├── clusters/               # (Réservé pour données clusters)
    ├── jsonld/                 # (Réservé pour templates JSON-LD)
    ├── pages/                  # (Réservé pour templates pages)
    └── suppliers/
        ├── __init__.py
        └── suppliers_database.py   # Base de 104 fournisseurs (13 catégories)
```

### 2.2 Exports Publics (`__init__.py`)

```python
__all__ = [
    "router",           # APIRouter FastAPI
    "SEOService",       # Service principal
    "SEOCluster",       # Modèle cluster
    "SEOPage",          # Modèle page
    "SEOJsonLD",        # Modèle JSON-LD
    "SEOCampaign",      # Modèle campagne
    "SEOAnalytics"      # Modèle analytics
]

__version__ = "1.0.0"
__module__ = "seo_engine"
```

---

## 3. ENDPOINTS API COMPLETS (41)

### 3.1 Routes Principales (`/api/v1/bionic/seo`)

#### Module Info
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Information sur le module SEO |
| GET | `/dashboard` | Dashboard complet SEO |
| GET | `/documentation` | Documentation interne du module |

#### Clusters (8 endpoints)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/clusters` | Liste des clusters (filtres: type, active) |
| GET | `/clusters/stats` | Statistiques des clusters |
| GET | `/clusters/hierarchy` | Hiérarchie complète |
| GET | `/clusters/{cluster_id}` | Détail d'un cluster |
| POST | `/clusters` | Créer un cluster |
| PUT | `/clusters/{cluster_id}` | Modifier un cluster |
| DELETE | `/clusters/{cluster_id}` | Supprimer un cluster |

#### Pages (10 endpoints)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/pages` | Liste des pages (filtres: cluster, type, status) |
| GET | `/pages/stats` | Statistiques des pages |
| GET | `/pages/templates` | Templates disponibles |
| GET | `/pages/{page_id}` | Détail d'une page |
| POST | `/pages` | Créer une page |
| PUT | `/pages/{page_id}` | Modifier une page |
| POST | `/pages/{page_id}/publish` | Publier une page |
| DELETE | `/pages/{page_id}` | Supprimer une page |
| GET | `/pages/{page_id}/internal-links` | Suggestions de liens internes |
| GET | `/pages/{page_id}/optimize` | Recommandations d'optimisation |

#### JSON-LD (8 endpoints)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/jsonld` | Liste des schémas |
| GET | `/jsonld/stats` | Statistiques des schémas |
| POST | `/jsonld/generate/article` | Générer schéma Article |
| POST | `/jsonld/generate/howto` | Générer schéma HowTo |
| POST | `/jsonld/generate/faq` | Générer schéma FAQPage |
| POST | `/jsonld/generate/breadcrumb` | Générer schéma Breadcrumb |
| POST | `/jsonld/save` | Sauvegarder un schéma |
| POST | `/jsonld/validate` | Valider un schéma |

#### Analytics (6 endpoints)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/analytics/dashboard` | Dashboard analytics |
| GET | `/analytics/top-pages` | Pages les plus performantes |
| GET | `/analytics/top-clusters` | Clusters les plus performants |
| GET | `/analytics/traffic-trend` | Tendance du trafic |
| GET | `/analytics/opportunities` | Opportunités d'optimisation |
| GET | `/analytics/report` | Rapport SEO complet |

#### Automation (6 endpoints)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/automation/rules` | Règles d'automatisation |
| PUT | `/automation/rules/{rule_id}/toggle` | Activer/désactiver règle |
| GET | `/automation/suggestions` | Suggestions de contenu |
| GET | `/automation/calendar` | Calendrier de contenu |
| GET | `/automation/tasks` | Tâches planifiées |
| POST | `/automation/tasks` | Planifier une tâche |
| GET | `/automation/alerts` | Alertes SEO |
| PUT | `/automation/alerts/{alert_id}/read` | Marquer alerte comme lue |

#### Generation (5 endpoints)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/generate/outline` | Générer outline de page |
| POST | `/generate/meta-tags` | Générer meta tags |
| POST | `/generate/seo-score` | Calculer score SEO |
| POST | `/generate/viral-capsule` | Générer capsule virale |
| POST | `/generate/pillar-content` | Générer contenu pilier (IA) |
| GET | `/generate/pillar-content/history` | Historique des contenus générés |

#### Workflow (2 endpoints)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/workflow/create-content` | Workflow création de contenu |
| POST | `/workflow/enrich-with-knowledge` | Enrichir avec Knowledge Layer |

#### Reports (1 endpoint)
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/reports/full` | Rapport SEO complet |

### 3.2 Routes Fournisseurs (`/api/v1/bionic/seo/suppliers`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Liste tous les fournisseurs (pagination, filtres) |
| GET | `/categories` | Liste des catégories |
| GET | `/by-category/{category}` | Fournisseurs par catégorie |
| GET | `/search?q=` | Recherche par nom |
| GET | `/by-country/{country}` | Fournisseurs par pays |
| GET | `/stats` | Statistiques de la base |
| GET | `/export` | Export JSON ou CSV |
| GET | `/seo-pages` | Structure pages SEO pour chaque fournisseur |

---

## 4. FONCTIONNALITÉS ACTIVES

### 4.1 Gestion des Clusters SEO

**9 Clusters de Base Pré-configurés :**

| ID | Nom FR | Type | Espèces/Régions |
|----|--------|------|-----------------|
| `cluster_moose` | Chasse à l'Orignal | species | moose |
| `cluster_deer` | Chasse au Cerf de Virginie | species | deer |
| `cluster_bear` | Chasse à l'Ours Noir | species | bear |
| `cluster_laurentides` | Chasse dans les Laurentides | region | laurentides |
| `cluster_abitibi` | Chasse en Abitibi | region | abitibi |
| `cluster_rut_season` | Chasse pendant le Rut | season | rut |
| `cluster_calling` | Techniques d'Appel | technique | moose, deer |
| `cluster_scouting` | Repérage et Pistage | technique | moose, deer, bear |
| `cluster_equipment` | Équipement de Chasse | equipment | - |

**Types de Clusters Supportés :**
- `species` : Par espèce de gibier
- `region` : Par région géographique
- `season` : Par saison de chasse
- `technique` : Par technique de chasse
- `equipment` : Par type d'équipement
- `territory` : Par territoire
- `behavior` : Comportemental
- `weather` : Météorologique

### 4.2 Gestion des Pages SEO

**6 Templates de Pages :**

| Type | Template | Mots Cibles | Temps Lecture |
|------|----------|-------------|---------------|
| Pillar | `tpl_species_guide` | 3400 | 15 min |
| Pillar | `tpl_region_guide` | 2600 | 12 min |
| Pillar | `tpl_technique_guide` | 2000 | 10 min |
| Satellite | `tpl_species_behavior` | 1000 | 5 min |
| Satellite | `tpl_seasonal_tips` | 1100 | 5 min |
| Opportunity | `tpl_specific_question` | 650 | 3 min |
| Opportunity | `tpl_location_specific` | 700 | 3 min |

**Statuts de Page :**
- `draft` : Brouillon
- `review` : En révision
- `published` : Publié
- `scheduled` : Planifié
- `archived` : Archivé

### 4.3 Schémas JSON-LD

**9 Types de Schémas Supportés :**

| Type | Usage | Auto-généré |
|------|-------|-------------|
| `Article` | Contenu éditorial | Oui |
| `HowTo` | Guides étape par étape | Oui |
| `FAQPage` | Questions/Réponses | Oui |
| `LocalBusiness` | Pourvoiries, ZECs | Oui |
| `Product` | Produits affiliés | Manuel |
| `Event` | Événements | Manuel |
| `Organization` | Info entreprise | Pré-configuré |
| `BreadcrumbList` | Fil d'Ariane | Oui |
| `VideoObject` | Vidéos | Manuel |

**Schéma Organisation BIONIC (pré-configuré) :**
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "BIONIC - Chasse Bionic",
  "url": "https://chassebionic.com",
  "description": "Plateforme intelligente de chasse au Québec"
}
```

### 4.4 Génération de Contenu IA

**Capacités de Génération :**
- Génération de pages piliers complètes (3500+ mots)
- Intégration données Knowledge Layer (comportement, habitat, rut)
- Structure automatique avec H2/H3
- Génération FAQ (8 questions)
- Optimisation SEO automatique
- Support multilingue (FR prioritaire)

**Modèle IA Utilisé :**
- Provider : OpenAI (via Emergent Universal Key)
- Modèle : `gpt-4o`
- Fallback : Structure template sans contenu IA

---

## 5. LOGIQUE MÉTIER DÉTAILLÉE

### 5.1 Calcul du Score SEO

Le score SEO est calculé sur **100 points** avec les critères suivants :

| Critère | Points | Conditions |
|---------|--------|------------|
| Titre | 15 | Présent, 30-60 caractères, contient mot-clé |
| Meta Description | 10 | Présente, 120-160 caractères |
| Mot-clé dans Titre | 10 | Mot-clé principal présent |
| H1 | 10 | Présent, contient mot-clé |
| Sous-titres H2 | 5 | Minimum 3 H2 |
| Longueur Contenu | 15 | Selon type (pillar: 2000+, satellite: 800+) |
| Liens Internes | 10 | Minimum 2 liens sortants |
| JSON-LD | 10 | Au moins 1 schéma |
| Images | 10 | (À implémenter) |

**Grades :**
- A : 90-100
- B : 80-89
- C : 70-79
- D : 60-69
- F : < 60

### 5.2 Score de Santé Global

Le score de santé est calculé à partir de :

```python
score = 100.0

# Pénalités Position (cible < 10)
if avg_position > 20: score -= 30
elif avg_position > 10: score -= 15

# Pénalités CTR (cible > 5%)
if avg_ctr < 3: score -= 20
elif avg_ctr < 5: score -= 10

# Pénalités Score SEO (cible > 80)
if avg_seo_score < 60: score -= 25
elif avg_seo_score < 80: score -= 10

# Pénalités Taux Publication
if published_rate < 50: score -= 15
elif published_rate < 80: score -= 5
```

### 5.3 Workflow de Création de Contenu

1. **Génération Outline** : Structure de page basée sur cluster et mot-clé
2. **Création Draft** : Page créée en statut `draft`
3. **Calcul Score SEO** : Score initial calculé
4. **Suggestions Liens Internes** : Recommandations automatiques
5. **Génération JSON-LD** : Schémas recommandés
6. **Publication** : Passage en statut `published`

### 5.4 Maillage Interne Automatique

**Algorithme de Suggestions :**
1. Rechercher pages du même cluster
2. Rechercher pages avec mêmes espèces cibles
3. Rechercher pages avec mêmes régions cibles
4. Prioriser par type de lien :
   - `pillar` (lien vers page pilier) - Priorité haute
   - `contextual` (même cluster) - Priorité moyenne
   - `related` (espèces/régions communes) - Priorité normale

---

## 6. AUTOMATISATIONS EN PLACE

### 6.1 Règles d'Automatisation par Défaut

| ID | Nom | Trigger | Action | Config |
|----|-----|---------|--------|--------|
| `auto_internal_linking` | Maillage interne automatique | page_created | suggest_links | max: 5, score min: 0.6 |
| `seo_score_alert` | Alerte score SEO | page_updated | alert | seuil: 60, type: warning |
| `publish_reminder` | Rappel de publication | scheduled | notify | jours: 7, fréquence: daily |
| `seasonal_content` | Générateur contenu saisonnier | scheduled | suggest_content | avance: 4 semaines |
| `keyword_tracking` | Suivi positions mots-clés | scheduled | track | fréquence: weekly, alerte si -5 |

### 6.2 Suggestions Saisonnières

**Septembre (Pré-rut Orignal) :**
- Guide complet du pré-rut de l'orignal
- Techniques d'appel de la femelle orignal

**Octobre (Pic du Rut) :**
- Stratégies pour le pic du rut de l'orignal

**Novembre (Rut Cerf) :**
- Chasse au cerf pendant le rut - Guide complet

### 6.3 Système d'Alertes

**Types d'Alertes :**
- `low_ctr` : CTR faible malgré bonnes impressions
- `low_seo_score` : Score SEO inférieur au seuil
- `page_2_ranking` : Page en position 11-20 (proche page 1)
- `publish_reminder` : Page en draft depuis trop longtemps

---

## 7. RÈGLES SEO EXISTANTES

### 7.1 Règle Bilingue Permanente

**ID :** `bilingual_communication_rule`

**Description :** Toute communication générée automatiquement DOIT inclure les versions française ET anglaise.

**Application :**
- Messages aux affiliés
- Notifications système
- Contenu généré par IA
- Templates emails

**Format Obligatoire :**
```
🇫🇷 FRANÇAIS
[Contenu en français]

🇬🇧 ENGLISH  
[Contenu en anglais]
```

### 7.2 Règles de Scoring

| Règle | Description | Pénalité |
|-------|-------------|----------|
| `title_length` | Titre entre 30-60 caractères | -5 à -15 pts |
| `meta_description_length` | Meta 120-160 caractères | -5 à -10 pts |
| `keyword_in_title` | Mot-clé dans le titre | -10 pts |
| `keyword_in_h1` | Mot-clé dans le H1 | -5 pts |
| `min_h2_count` | Minimum 3 sous-titres H2 | -5 pts |
| `min_word_count` | Selon type de page | -15 pts |
| `internal_links` | Minimum 2 liens internes | -10 pts |
| `jsonld_present` | Au moins 1 schéma JSON-LD | -10 pts |

### 7.3 Règles de Validation JSON-LD

**Critères de Validation :**
- `@context` doit être `https://schema.org`
- `@type` obligatoire
- Champs requis selon le type :
  - Article : headline, author, publisher, datePublished
  - HowTo : au moins 1 step
  - FAQPage : au moins 1 mainEntity

---

## 8. DÉPENDANCES INTERNES

### 8.1 Dépendances Python

```python
# Core
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
from enum import Enum

# Database
from motor.motor_asyncio import AsyncIOMotorClient

# Environment
import os
from dotenv import load_dotenv

# Utilities
import logging
import uuid
import json
import re

# LLM (optionnel)
from emergentintegrations.llm.chat import LlmChat, UserMessage
```

### 8.2 Dépendances Inter-Composants

```
seo_router.py
    ├── seo_service.py (orchestration)
    ├── seo_clusters.py (clusters)
    ├── seo_pages.py (pages)
    ├── seo_jsonld.py (schémas)
    ├── seo_analytics.py (métriques)
    ├── seo_automation.py (règles)
    ├── seo_generation.py (structures)
    └── seo_content_generator.py (IA)

seo_suppliers_router.py
    └── data/suppliers/suppliers_database.py
```

### 8.3 Dépendances Externes

| Service | Usage | Obligatoire |
|---------|-------|-------------|
| MongoDB | Stockage données | Oui |
| Emergent LLM Key | Génération contenu IA | Non (fallback disponible) |
| Knowledge Layer | Enrichissement données | Non (optionnel) |

---

## 9. INTÉGRATIONS ACTUELLES

### 9.1 MongoDB

**Collections Utilisées :**

| Collection | Usage |
|------------|-------|
| `seo_clusters` | Clusters SEO custom |
| `seo_pages` | Pages SEO |
| `seo_jsonld` | Schémas JSON-LD |
| `seo_alerts` | Alertes SEO |
| `seo_scheduled_tasks` | Tâches planifiées |
| `seo_automation_rules` | Règles custom |
| `seo_generated_content` | Historique contenus IA |

**Configuration :**
```python
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'bionic_db')
```

### 9.2 Knowledge Layer (BIONIC)

**Points d'Intégration :**
- Données comportementales par espèce
- Phases saisonnières
- Règles de chasse applicables
- Préférences d'habitat
- Sources alimentaires

**Utilisation :**
- Enrichissement pages piliers
- Suggestions de contenu saisonnier
- Optimisation timing publication

### 9.3 Emergent LLM Integration

**Configuration :**
```python
api_key = os.environ.get("EMERGENT_LLM_KEY")
model_provider = "openai"
model_name = "gpt-4o"
```

**Fonctionnalités :**
- Génération pages piliers complètes
- Optimisation automatique SEO
- Intégration données Knowledge Layer dans le contenu

---

## 10. INDICATEURS DE PERFORMANCE (KPIs)

### 10.1 KPIs Cibles

| KPI | Cible | Description |
|-----|-------|-------------|
| `avg_position` | < 10.0 | Position moyenne dans les SERP |
| `ctr` | > 5.0% | Taux de clic |
| `seo_score` | > 80/100 | Score SEO technique |
| `indexed_rate` | > 95% | Taux d'indexation |
| `conversion_rate` | > 2.0% | Taux de conversion |

### 10.2 Métriques Trackées par Page

| Métrique | Type | Description |
|----------|------|-------------|
| `impressions` | int | Nombre d'affichages SERP |
| `clicks` | int | Nombre de clics |
| `ctr` | float | Taux de clic (%) |
| `avg_position` | float | Position moyenne |
| `conversions` | int | Nombre de conversions |
| `seo_score` | float | Score SEO (0-100) |
| `word_count` | int | Nombre de mots |
| `reading_time_min` | int | Temps de lecture (min) |

### 10.3 Métriques Agrégées (Dashboard)

```json
{
  "clusters": {
    "total": 9,
    "active": 9
  },
  "pages": {
    "total": 0,
    "published": 0,
    "draft": 0
  },
  "traffic": {
    "total_clicks": 0,
    "total_impressions": 0,
    "avg_ctr": 0
  },
  "performance": {
    "avg_position": 0,
    "avg_seo_score": 0,
    "total_conversions": 0
  },
  "technical": {
    "schemas_count": 0,
    "health_score": 100
  }
}
```

---

## 11. PARAMÈTRES ET CONFIGURATIONS

### 11.1 Variables d'Environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `MONGO_URL` | URL connexion MongoDB | `mongodb://localhost:27017` |
| `DB_NAME` | Nom de la base | `bionic_db` |
| `EMERGENT_LLM_KEY` | Clé API LLM | (requis pour génération IA) |

### 11.2 Limites et Quotas

| Paramètre | Valeur | Endpoint |
|-----------|--------|----------|
| `max_clusters_per_request` | 500 | `/clusters` |
| `max_pages_per_request` | 500 | `/pages` |
| `max_schemas_per_request` | 500 | `/jsonld` |
| `max_alerts` | 200 | `/automation/alerts` |
| `max_suggestions` | 5 | Auto internal linking |
| `min_relevance_score` | 0.6 | Suggestions liens |
| `seo_score_threshold` | 60 | Alertes |
| `days_threshold_draft` | 7 | Rappel publication |
| `seasonal_lead_time` | 4 semaines | Suggestions contenu |

### 11.3 Configuration Templates Pages

| Template | Word Count Min | Liens Internes Cibles | JSON-LD |
|----------|----------------|----------------------|---------|
| Pillar Species | 3400 | 8 | Article, HowTo, FAQPage |
| Pillar Region | 2600 | 6 | Article, LocalBusiness |
| Pillar Technique | 2000 | 5 | Article, HowTo |
| Satellite Behavior | 1000 | 3 | Article |
| Satellite Seasonal | 1100 | 4 | Article, HowTo |
| Opportunity Question | 650 | 2 | Article, FAQPage |
| Opportunity Location | 700 | 3 | Article, LocalBusiness |

---

## 12. SCHÉMAS DE DONNÉES (MongoDB)

### 12.1 Collection `seo_clusters`

```javascript
{
  "id": "string",                    // Ex: "cluster_custom_123"
  "name": "string",                  // Nom EN
  "name_fr": "string",               // Nom FR
  "cluster_type": "string",          // species|region|season|technique|equipment
  "description": "string",           // Description EN
  "description_fr": "string",        // Description FR
  "primary_keyword": {
    "keyword": "string",
    "keyword_fr": "string",
    "search_volume": "int",
    "difficulty": "float (0-1)",
    "intent": "string",              // informational|transactional|navigational
    "priority": "int (1-5)",
    "is_primary": "boolean"
  },
  "secondary_keywords": [/* même structure */],
  "long_tail_keywords": ["string"],
  "pillar_page_id": "string|null",
  "satellite_page_ids": ["string"],
  "opportunity_page_ids": ["string"],
  "parent_cluster_id": "string|null",
  "sub_cluster_ids": ["string"],
  "species_ids": ["string"],
  "region_ids": ["string"],
  "season_tags": ["string"],
  "total_pages": "int",
  "total_traffic": "int",
  "avg_position": "float",
  "created_at": "datetime ISO",
  "updated_at": "datetime ISO",
  "is_active": "boolean"
}
```

### 12.2 Collection `seo_pages`

```javascript
{
  "id": "string",                    // Ex: "page_abc12345"
  "cluster_id": "string",
  "page_type": "string",             // pillar|satellite|opportunity|viral|interactive|tool
  "status": "string",                // draft|review|published|scheduled|archived
  "slug": "string",
  "url_path": "string",
  "title": "string",
  "title_fr": "string",
  "meta_description": "string",
  "meta_description_fr": "string",
  "content_format": "string",        // article|guide|checklist|infographic|video|quiz|calculator|map|comparison
  "h1": "string",
  "h2_list": ["string"],
  "word_count": "int",
  "reading_time_min": "int",
  "primary_keyword": "string",
  "secondary_keywords": ["string"],
  "keyword_density": "float",
  "seo_score": "float (0-100)",
  "internal_links_out": [{
    "target_page_id": "string",
    "anchor_text": "string",
    "anchor_text_fr": "string",
    "context": "string",
    "link_type": "string",           // contextual|navigation|related|cta
    "priority": "int"
  }],
  "internal_links_in": ["string"],   // Page IDs
  "jsonld_types": ["string"],        // Article|HowTo|FAQPage|etc
  "jsonld_data": "object",
  "target_audience": "string",       // beginner|intermediate|expert|guide|landowner|all
  "target_regions": ["string"],
  "target_seasons": ["string"],
  "target_species": ["string"],
  "knowledge_rules_applied": ["string"],
  "knowledge_data_used": "object",
  "impressions": "int",
  "clicks": "int",
  "ctr": "float",
  "avg_position": "float",
  "conversions": "int",
  "author": "string",
  "created_at": "datetime ISO",
  "updated_at": "datetime ISO",
  "published_at": "datetime ISO|null",
  "scheduled_at": "datetime ISO|null"
}
```

### 12.3 Collection `seo_jsonld`

```javascript
{
  "id": "string",
  "page_id": "string",
  "schema_type": "string",           // Article|HowTo|FAQPage|LocalBusiness|etc
  "schema_data": "object",           // Schéma JSON-LD complet
  "is_valid": "boolean",
  "validation_errors": ["string"],
  "created_at": "datetime ISO"
}
```

### 12.4 Collection `seo_alerts`

```javascript
{
  "id": "string",
  "type": "string",                  // low_ctr|low_seo_score|page_2_ranking|etc
  "message": "string",
  "page_id": "string|null",
  "priority": "string",              // low|medium|high
  "is_read": "boolean",
  "created_at": "datetime ISO"
}
```

### 12.5 Collection `seo_scheduled_tasks`

```javascript
{
  "id": "string",
  "type": "string",                  // content_creation|optimization|etc
  "title": "string",
  "description": "string",
  "scheduled_at": "datetime ISO",
  "target_page_id": "string|null",
  "target_cluster_id": "string|null",
  "priority": "string",              // low|medium|high
  "status": "string",                // pending|completed|cancelled
  "created_at": "datetime ISO"
}
```

### 12.6 Collection `seo_generated_content`

```javascript
{
  "type": "string",                  // pillar_generated
  "species_id": "string",
  "keyword": "string",
  "content": {
    "title_fr": "string",
    "content_html": "string",
    "content_markdown": "string",
    "word_count": "int",
    "h2_list": ["string"],
    "faq_items": [{"question": "string", "answer": "string"}],
    "meta_description_fr": "string",
    "primary_keyword": "string",
    "reading_time_min": "int"
  },
  "metadata": {
    "species_id": "string",
    "keyword": "string",
    "model_used": "string",
    "generated_at": "datetime ISO",
    "word_count": "int"
  },
  "status": "string",                // draft|published
  "created_at": "datetime ISO"
}
```

---

## 13. BASE DE DONNÉES FOURNISSEURS

### 13.1 Vue d'Ensemble

| Métrique | Valeur |
|----------|--------|
| **Total Fournisseurs** | 104 |
| **Catégories** | 13 |
| **Pays Représentés** | 7 (USA, Canada, Allemagne, Autriche, Italie, International) |
| **Priorité High** | ~45% |
| **Priorité Medium** | ~45% |
| **Priorité Low** | ~10% |

### 13.2 Catégories Disponibles

| Catégorie | Code | Nombre | Description |
|-----------|------|--------|-------------|
| Caméras de Chasse | `cameras` | 13 | Trail cameras, cellulaires, sécurité |
| Arcs & Arbalètes | `arcs_arbaletes` | 12 | Compound, recurve, crossbows |
| Treestands & Saddles | `treestands` | 9 | Stands, plateformes, saddle hunting |
| Urines & Attractants | `urines_attractants` | 9 | Scents, urines, attractifs |
| Vêtements Techniques | `vetements` | 10 | Camo, couches, outdoor apparel |
| Optiques | `optiques` | 7 | Lunettes, binoculaires, rangefinders |
| Bottes | `bottes` | 7 | Hunting boots, rubber boots |
| Backpacks | `backpacks` | 6 | Packs de chasse, frames |
| Couteaux | `knives` | 7 | Fixed blade, folding, processing |
| Boats/Kayaks/Motors | `boats_kayaks` | 7 | Kayaks, canoes, trolling motors |
| Électronique | `electronics` | 6 | GPS, thermal, ozone generators |
| Coolers | `coolers` | 6 | Glacières premium et budget |
| Processing | `processing` | 6 | Grinders, smokers, dehydrators |

### 13.3 Structure Fournisseur

```javascript
{
  "company": "string",           // Nom de l'entreprise
  "country": "string",           // Pays d'origine
  "official_url": "string",      // URL officielle
  "free_shipping": "string",     // Oui|Non|Parfois|N/A
  "type": "string",              // manufacturer|retailer|software
  "specialty": ["string"],       // Spécialités (3-4 max)
  "seo_priority": "string"       // high|medium|low
}
```

### 13.4 Fournisseurs Priorité Haute (Exemples)

| Catégorie | Fournisseur | Pays | Spécialités |
|-----------|-------------|------|-------------|
| cameras | Spypoint | Canada | Cellular trail cameras, Solar |
| cameras | Bushnell | USA | Trail cameras, Optics |
| arcs_arbaletes | Mathews | USA | Premium compound bows |
| arcs_arbaletes | Ravin | USA | Helicoil crossbows |
| treestands | Tethrd | USA | Saddle hunting |
| urines_attractants | Code Blue | USA | Deer scents, Estrus |
| vetements | Sitka Gear | USA | Premium hunting systems |
| optiques | Vortex | USA | VIP warranty, riflescopes |
| bottes | LaCrosse | USA | Alphaburly Pro |
| backpacks | Mystery Ranch | USA | Military grade packs |
| electronics | Garmin | USA | GPS, Dog tracking |
| coolers | YETI | USA | Premium coolers |
| processing | LEM Products | USA | Meat grinders |

---

## 14. ANNEXES TECHNIQUES

### 14.1 Enums Disponibles (seo_models.py)

**ClusterType :**
```python
SPECIES, REGION, SEASON, TECHNIQUE, EQUIPMENT, TERRITORY, BEHAVIOR, WEATHER
```

**PageType :**
```python
PILLAR, SATELLITE, OPPORTUNITY, VIRAL, INTERACTIVE, TOOL, LANDING
```

**PageStatus :**
```python
DRAFT, REVIEW, PUBLISHED, SCHEDULED, ARCHIVED
```

**ContentFormat :**
```python
ARTICLE, GUIDE, CHECKLIST, INFOGRAPHIC, VIDEO, PODCAST, QUIZ, CALCULATOR, MAP, COMPARISON
```

**JsonLDType :**
```python
ARTICLE, HOWTO, FAQ, LOCAL_BUSINESS, PRODUCT, EVENT, ORGANIZATION, BREADCRUMB, VIDEO
```

**TargetAudience :**
```python
BEGINNER, INTERMEDIATE, EXPERT, GUIDE, LANDOWNER, ALL
```

### 14.2 Modèles Pydantic Disponibles

| Modèle | Description |
|--------|-------------|
| `SEOKeyword` | Mot-clé avec métriques |
| `SEOCluster` | Cluster thématique complet |
| `InternalLink` | Lien interne avec contexte |
| `SEOPage` | Page SEO complète |
| `SEOJsonLD` | Schéma structuré |
| `ViralCapsule` | Capsule virale |
| `InteractiveWidget` | Widget interactif |
| `SEOCampaign` | Campagne SEO |
| `SEOAnalytics` | Analytics agrégées |
| `SEODashboardStats` | Stats dashboard |

### 14.3 Request Models API

| Modèle | Endpoint |
|--------|----------|
| `GenerateOutlineRequest` | `/generate/outline` |
| `GenerateMetaTagsRequest` | `/generate/meta-tags` |
| `GenerateViralCapsuleRequest` | `/generate/viral-capsule` |
| `CreateContentWorkflowRequest` | `/workflow/create-content` |
| `EnrichWithKnowledgeRequest` | `/workflow/enrich-with-knowledge` |
| `GeneratePillarContentRequest` | `/generate/pillar-content` |
| `GenerateFAQRequest` | `/jsonld/generate/faq` |
| `ContentGenerationRequest` | (usage interne) |

### 14.4 Exemple Complet - Workflow Création Page Pilier

```python
# 1. Appel API génération outline
POST /api/v1/bionic/seo/generate/outline
{
  "cluster_id": "cluster_moose",
  "page_type": "pillar",
  "target_keyword": "chasse orignal québec",
  "knowledge_data": {
    "species": {...},
    "seasonal": {...}
  }
}

# 2. Création page draft
POST /api/v1/bionic/seo/pages
{
  "cluster_id": "cluster_moose",
  "page_type": "pillar",
  "slug": "guide-complet-chasse-orignal-quebec",
  "title_fr": "Guide Complet: Chasse à l'Orignal au Québec",
  ...
}

# 3. Génération contenu IA
POST /api/v1/bionic/seo/generate/pillar-content
{
  "species_id": "moose",
  "keyword": "chasse orignal québec",
  "knowledge_data": {...}
}

# 4. Optimisation et validation
GET /api/v1/bionic/seo/pages/{page_id}/optimize

# 5. Publication
POST /api/v1/bionic/seo/pages/{page_id}/publish
```

### 14.5 Codes de Réponse API

| Code | Signification |
|------|---------------|
| 200 | Succès |
| 400 | Requête invalide |
| 404 | Ressource non trouvée |
| 500 | Erreur serveur |

**Format Réponse Standard :**
```json
{
  "success": true|false,
  "data": {...},
  "error": "string (si échec)"
}
```

---

## RÉSUMÉ EXÉCUTIF

Le **SEO Engine V5-ULTIME** est un module complet et autonome offrant :

- **41 endpoints API** pour une gestion complète du SEO
- **9 clusters de base** pré-configurés pour la chasse au Québec
- **6 templates de pages** (piliers, satellites, opportunités)
- **9 types de schémas JSON-LD** pour le référencement structuré
- **5 règles d'automatisation** par défaut
- **104 fournisseurs** répertoriés dans 13 catégories
- **Génération IA** via Emergent LLM Key (GPT-4o)
- **Intégration Knowledge Layer** pour enrichissement contextuel
- **Support bilingue FR/EN** natif (règle permanente)

Le module est conçu pour atteindre une **augmentation de +300% du trafic organique** grâce à une stratégie de clusters thématiques et une optimisation continue.

---

**Document généré par BIONIC SEO Engine V5-ULTIME**  
**Version :** 1.0.0  
**Dernière mise à jour :** Décembre 2025
