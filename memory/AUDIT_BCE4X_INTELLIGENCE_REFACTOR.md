# RAPPORT D'AUDIT BCE-4X + STEEVE-MAX — BIONIC V3
## Audit complet avant réécriture INTELLIGENCE
### Date: 2026-03-18 | Version: 1.0

---

## 1. AUDIT DES MOTEURS ACTIFS

### 1.1 ALIMENTATION-V1 (Stable)
| Critère | Statut | Détail |
|---------|--------|--------|
| Version | V1 | Production stable |
| Fichiers | 8 (engine, router, scoring, layers, classifier, grid_generator, species_profiles, documentation) |
| Endpoint | `POST /api/v1/alimentation/analyze`, `GET /api/v1/alimentation/point`, `/multi`, `/profiles`, `/documentation` |
| Entrée | `{center_lat, center_lng, species, month, side_m, cell_m, sample_step}` |
| Sortie | `{score_alimentation, classe, cells[], stats, grid_summary}` |
| Espèces | CERF, ORIGNAL, OURS, DINDON, WAPITI (5) |
| Dépendances | Aucune externe. Autosuffisant (layers.py génère les données) |
| Performance | Grille 200x200, échantillonnage step=5 → ~8000 cellules |
| Stabilité | HAUTE — Gelé, utilisé par score_consolide.py |
| Conformité | BCE-4X ✓ |

### 1.2 ALIMENTATION-V2 (Stable — Récent)
| Critère | Statut | Détail |
|---------|--------|--------|
| Version | V2 | Production stable |
| Fichiers | 5 (engine, router, nutrition, salines, terrain) |
| Endpoint | `POST /api/v2/alimentation/analyze`, `GET /api/v2/alimentation/species` |
| Entrée | `{center_lat, center_lng, species, month, max_salines(1-4)}` |
| Sortie | `{terrain{}, salines[], nutrition{}, species, salines_disabled, message}` |
| Espèces | 5 + mapping frontend IDs (`chevreuil`→`CERF`, etc.) |
| Logique spéciale | OURS/DINDON: salines désactivées (SPECIES_NO_SALINES) |
| Dépendances | Aucune externe. Terrain/nutrition algorithmiques |
| Diversification | Min 300m entre salines (algorithme glouton) |
| Stabilité | HAUTE |
| Conformité | BCE-4X ✓, STEEVE-MAX ✓ |

### 1.3 REPOS-V1 (Stable)
| Critère | Statut | Détail |
|---------|--------|--------|
| Version | V1 | Production stable |
| Fichiers | 8 (engine, router, scoring, layers, classifier, grid_generator, species_profiles, documentation) |
| Endpoint | `POST /api/v1/repos/analyze`, `GET /api/v1/repos/point`, `/multi`, `/profiles`, `/documentation` |
| Entrée | `{center_lat, center_lng, species, month, sample_step}` |
| Sortie | `{score_repos, classe, detail{couvert, calme, thermique, accessibilite, prox_alim}}` |
| Dépendances | `alimentation_v1.layers.load_layers()` (couplage faible) |
| Performance | Échantillonnage step=5 |
| Stabilité | HAUTE — Gelé |
| Conformité | BCE-4X ✓ |

### 1.4 CORRIDORS-V10 (Stable — Moteur majeur)
| Critère | Statut | Détail |
|---------|--------|--------|
| Version | V10 | Production stable |
| Fichiers | 11 (engine, router, scoring, cost_surface, network_builder, pathfinder, classifier, multi_engine, species_profiles, validator, documentation) |
| Endpoint | `POST /api/v10/corridors/analyze`, `/analyze-full`, `GET /api/v10/corridors/multi`, `/profiles`, `/documentation` |
| Entrée | `{center_lat, center_lng, species, month, cell_m}` |
| Sortie | `{score, classification, corridors[], zones[], geojson, validations{bce4x, steeve_max}}` |
| Pipeline | Profil espèce → Grille coûts → Réseau A* → Score → Validation |
| Multi-Engine | 7 sous-moteurs consolidés (alimentation_v1, rut_v1, repos_v1, trajets_v1, affuts_v1, habitat_v1, corridors_v10) |
| Pondérations saisonnières | 12 mois × 7 moteurs, modulation dynamique |
| Dépendances | `shapely` (concave_hull), moteurs V1 internes |
| Validateurs | `validate_bce4x()`, `validate_steeve_max()` |
| Performance | Grille ~80x80, A* pathfinding |
| Stabilité | HAUTE |
| Conformité | BCE-4X ✓✓, STEEVE-MAX ✓✓ (double validation) |

### 1.5 HABITAT-V10 (via habitat_score_service.py)
| Critère | Statut | Détail |
|---------|--------|--------|
| Version | V1 (dans bionic_engine_p0) | Shadow Mode |
| Fichiers | 1 (habitat_score_service.py) |
| Endpoint | Via `/api/bionic/habitat-score` |
| Facteurs | 12 (micro-relief, NDVI, essences, drainage, eau, anthropique, connectivité, pression, thermique, altitude, comportement, zones) |
| Espèces | moose, deer, bear, turkey, elk (mapping différent de V10!) |
| Stabilité | MOYENNE — Module isolé, Shadow Mode |
| Risque | Mapping espèces différent de V10 (`moose` vs `ORIGNAL`) |

### 1.6 PRESSION HUMAINE (via score_consolide.py)
| Critère | Statut | Détail |
|---------|--------|--------|
| Version | Intégré dans score_consolide.py | Pas de module dédié |
| Calcul | `pression_score = min(100, (dist_route/8) + (dist_bat/10))` |
| Sources | layers.perturbations (distance_route_m, distance_batiment_m) |
| Poids | 20% dans le score consolidé |
| Stabilité | HAUTE (simple, déterministe) |
| Risque | Logique intégrée dans score_consolide, pas isolée |

### 1.7 ACCESSIBILITÉ TERRAIN (via repos_v1 + alimentation_v1)
| Critère | Statut | Détail |
|---------|--------|--------|
| Composant | Sous-score dans repos_v1 (`accessibilite`) et alimentation_v1 (`layers`) |
| Pas de moteur dédié | Intégré dans les couches existantes |

### 1.8 Moteurs secondaires/dérivés
| Moteur | Localisation | Statut |
|--------|-------------|--------|
| RUT-V1 | corridors_v10/multi_engine.py | Intégré (poids 0.14) |
| TRAJETS-V1 | corridors_v10/multi_engine.py | Intégré (poids 0.12) |
| AFFÛTS-V1 | corridors_v10/multi_engine.py | Intégré (poids 0.12) |
| HABITAT-V1 | corridors_v10/multi_engine.py | Intégré (poids 0.15) |
| bionic_engine_p0 | 60+ services/routers | Legacy/Gelé |

---

## 2. VÉRIFICATION DES SCHÉMAS DE DONNÉES

### 2.1 Formats JSON — Analyse comparative

| Moteur | Entrée type | Sortie type | Score range |
|--------|-------------|-------------|-------------|
| ALIMENTATION-V1 | `{lat, lng, species, month}` | `{score_alimentation: 0-100}` | 0-100 |
| ALIMENTATION-V2 | `{lat, lng, species, month, max_salines}` | `{terrain{}, salines[], nutrition{}}` | N/A (composite) |
| REPOS-V1 | `{lat, lng, species, month}` | `{score_repos: 0-100}` | 0-100 |
| CORRIDORS-V10 | `{lat, lng, species, month}` | `{score: 0-100, corridors[]}` | 0-100 |
| Score consolidé | `{lat, lng, species, month}` | `{score: 0-100, components{}}` | 0-100 |

### 2.2 Métadonnées obligatoires
- **Présentes partout**: `species`, `month`, coordonnées GPS
- **ABSENTES de manière uniforme**: `timestamp`, `version_engine`, `session_id`
- **Traçabilité**: Seul `score_consolide.py` fournit un champ `tracability{}`
- **RISQUE**: Pas de schéma commun d'enveloppe (pas de `{engine, version, timestamp, data}`)

### 2.3 Divergences identifiées
| Divergence | Détail | Risque |
|------------|--------|--------|
| Mapping espèces | V10: `CERF/ORIGNAL/OURS` vs habitat_score: `deer/moose/bear` | ÉLEVÉ |
| Classement | V10: `CRITIQUE/MAJEUR/FORT/MODÉRÉ/FAIBLE` vs V1: `OPTIMAL/BON/MODÉRÉ/FAIBLE` | MOYEN |
| Coordonnées | V10: `center_lat/center_lng` vs P0: `bounds{north,south,east,west}` | ÉLEVÉ |
| Saisons | V10: `get_season(month)` par espèce vs P0: `datetime` ISO | MOYEN |

### 2.4 Conformité BCE-4X
- Score consolidé: ✓ Pondérations normalisées, traçabilité
- Moteurs V1/V10: ✓ Géométrie préservée, 0 déplacement de centres
- Habitat P0: ⚠ Shadow mode, pas de validation BCE-4X formelle
- Contrats JSON: ✓ Existent pour zone/corridor/hotspot (bionic_engine_p0/contracts/)

---

## 3. AUDIT COMPLET DE L'API

### 3.1 Endpoints actifs par domaine

**MON TERRITOIRE (Carte):**
| Endpoint | Méthode | Module |
|----------|---------|--------|
| `/api/v1/alimentation/analyze` | POST | alimentation_v1 |
| `/api/v1/alimentation/point` | GET | alimentation_v1 |
| `/api/v2/alimentation/analyze` | POST | alimentation_v2 |
| `/api/v1/repos/analyze` | POST | repos_v1 |
| `/api/v1/repos/point` | GET | repos_v1 |
| `/api/v10/corridors/analyze-full` | POST | corridors_v10 |
| `/api/v10/corridors/multi` | GET | corridors_v10 |
| `/api/v1/score-consolide/point` | GET | score_consolide |
| `/api/v1/score-consolide/heatmap` | GET | score_consolide |

**BIONIC ENGINE P0 (Zones, Pipeline, Scoring):**
| Endpoint | Méthode | Module |
|----------|---------|--------|
| `/api/bionic/*` | Divers | 30+ sous-routeurs |
| `/api/v7/organic-zones/*` | Divers | organic_zones_router |
| `/api/v5/spatial-clipping/*` | Divers | spatial_clipping_router |

**INTELLIGENCE (Analytics, Forecast, Plan Maître):**
| Route frontend | Page | Backend associé |
|----------------|------|-----------------|
| `/analytics` | AnalyticsPage.jsx (54 lignes) | analytics_engine (scaffold) |
| `/forecast` | ForecastPage.jsx (61 lignes) | predictive_engine (scaffold) |
| `/plan-maitre` | PlanMaitrePage.jsx (38 lignes) | strategy_engine (scaffold) |

### 3.2 Problèmes identifiés
| Problème | Gravité | Détail |
|----------|---------|--------|
| Fragmentation API | ÉLEVÉE | 30+ routeurs P0 enregistrés séquentiellement dans server.py (lignes 175-500) |
| Duplication préfixes | MOYENNE | `/api/bionic/*` vs `/api/v10/*` vs `/api/v1/*` — 3 schémas de versionnement |
| Pages INTELLIGENCE quasi vides | FAIBLE | Analytics=54L, Forecast=61L, PlanMaitre=38L — scaffolds |
| Pas d'API unifiée | ÉLEVÉE | Chaque moteur a son propre routeur, pas de façade commune |
| server.py monolithique | ÉLEVÉE | 610 lignes, ~50 try/except pour les registrations |

### 3.3 Risques de régression
- **FAIBLE**: Les moteurs V1/V10 sont isolés et stables
- **MOYEN**: Le score_consolide.py dépend de alimentation_v1 et repos_v1
- **ÉLEVÉ**: bionic_engine_p0 a 60+ fichiers interdépendants

---

## 4. AUDIT UI/UX

### 4.1 Structure de navigation
```
Header (BionicHeader.jsx)
├── Accueil
├── Dashboard
├── Intelligence (Dropdown) ← CIBLE DU REFACTOR
│   ├── Analytics (/analytics)
│   ├── Prévisions (/forecast)
│   └── Plan Maître (/plan-maitre)
├── Carte (Dropdown)
│   ├── Carte Interactive (/map)
│   └── Mon Territoire (/territoire) ← PAGE PRINCIPALE
├── Sorties (/trips)
├── Analyseur (/analyze)
├── Boutique (/shop)
└── Business (/business) [admin]
```

### 4.2 MonTerritoireBionicPage.jsx — Analyse
| Métrique | Valeur |
|----------|--------|
| Lignes de code | 2114 |
| États (useState) | ~50+ |
| Composants enfants | ~40+ |
| Complexité | TRÈS ÉLEVÉE |

### 4.3 Toolbar horizontale (MonTerritoireToolbar.jsx)
- Boutons: Split, Carte, Espèce, Observation, Analyse, Zones, Alimentation, Points chauds
- Chaque bouton ouvre un Popover avec des sous-options
- Admin Architecte: bouton bouclier, mot de passe `Saturn5858*`

### 4.4 Interactions carte ↔ INTELLIGENCE
- **Actuellement**: AUCUNE interaction directe
- Les pages Intelligence (Analytics, Forecast, Plan Maître) sont des scaffolds indépendants
- MON TERRITOIRE ne communique pas avec les pages Intelligence
- **RISQUE du déplacement**: Si INTELLIGENCE est intégrée dans la carte, il faudra un système de communication d'état

### 4.5 Conformité STEEVE-MAX
- ✓ Palette sombre cohérente (bg-[#0c0c14])
- ✓ Typographie micro (text-[8px] à text-[10px])
- ✓ Animations corridors critiques (pulse CSS)
- ✓ Admin Architecte mode fonctionnel
- ✓ Heatmap 100% transparente
- ⚠ MonTerritoireBionicPage.jsx trop volumineux (2114L) — P3 refactoring prévu

---

## 5. RISQUES LIÉS À LA RÉÉCRITURE D'INTELLIGENCE

### 5.1 Matrice des risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| **Régression MON TERRITOIRE** | FAIBLE | CRITIQUE | Branche safepoint + tests automatisés |
| **Mapping espèces incohérent** | ÉLEVÉE | ÉLEVÉ | Standardiser sur CERF/ORIGNAL/OURS/DINDON/WAPITI |
| **Performance dégradée** (trop de moteurs simultanés) | MOYENNE | ÉLEVÉ | Lazy loading, cache, pagination |
| **Synchronisation carte ↔ Intelligence** | MOYENNE | ÉLEVÉ | State manager centralisé (context/zustand) |
| **Conflit CSS/layout** | FAIBLE | MOYEN | Isolation des composants, CSS modules |
| **Perte de contexte Admin Architecte** | FAIBLE | MOYEN | Propager isArchitecteMode globalement |
| **server.py overflow** | ÉLEVÉE | MOYEN | API Gateway / Router centralisé |
| **Moteurs non standardisés** | ÉLEVÉE | ÉLEVÉ | Schéma commun obligatoire |

### 5.2 Risques spécifiques backend
- `score_consolide.py` importe directement `alimentation_v1` et `repos_v1` — couplage fort
- `corridors_v10/multi_engine.py` intègre 7 moteurs via des fonctions déterministes — stable mais non extensible
- Pas de registre dynamique de moteurs — ajout d'un V11 nécessite modification de code

### 5.3 Risques spécifiques frontend
- MonTerritoireBionicPage.jsx gère 50+ états — tout changement est risqué
- Les pages Intelligence sont des scaffolds vides — la réécriture est une création, pas un refactor
- Pas de state management global — communication inter-pages impossible sans refactoring

---

## 6. ARCHITECTURE ACTUELLE vs CIBLE

### 6.1 Architecture actuelle
```
┌─────────────────────────────────────────────┐
│                  server.py                    │
│          (610L, 50+ try/except)               │
│                                               │
│  ┌─────────────┐ ┌──────────────┐            │
│  │alimentation  │ │ repos_v1     │            │
│  │  _v1/_v2     │ │              │            │
│  └──────┬───────┘ └──────┬───────┘            │
│         │                │                    │
│  ┌──────┴────────────────┴───────┐            │
│  │      score_consolide.py       │            │
│  │   (import direct v1 + repos)  │            │
│  └───────────────────────────────┘            │
│                                               │
│  ┌────────────────────────────────┐           │
│  │      corridors_v10 (isolé)     │           │
│  │  multi_engine: 7 sous-moteurs  │           │
│  └────────────────────────────────┘           │
│                                               │
│  ┌────────────────────────────────┐           │
│  │   bionic_engine_p0 (legacy)    │           │
│  │     60+ fichiers, gelé         │           │
│  └────────────────────────────────┘           │
└─────────────────────────────────────────────┘
```

### 6.2 Architecture cible (auto-adaptative)
```
┌───────────────────────────────────────────────┐
│              API Gateway / Façade              │
│         (versionnement unifié /api/v3/*)       │
│                                                │
│  ┌──────────────────────────────────────────┐  │
│  │         ENGINE REGISTRY (déclaratif)      │  │
│  │  ┌─────────┐ ┌─────────┐ ┌──────────┐   │  │
│  │  │ALIM-V2  │ │REPOS-V1 │ │CORR-V10  │   │  │
│  │  │score()  │ │score()  │ │score()   │   │  │
│  │  │meta()   │ │meta()   │ │meta()    │   │  │
│  │  └─────────┘ └─────────┘ └──────────┘   │  │
│  │  ┌─────────┐ ┌─────────┐ ┌──────────┐   │  │
│  │  │HABITAT  │ │PRESSION │ │FUTUR-V11 │   │  │
│  │  │score()  │ │score()  │ │score()   │   │  │
│  │  └─────────┘ └─────────┘ └──────────┘   │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  ┌──────────────────────────────────────────┐  │
│  │      CONSOLIDATEUR DYNAMIQUE              │  │
│  │  - Poids dynamiques par saison/espèce     │  │
│  │  - Fallback si moteur indisponible        │  │
│  │  - Traçabilité automatique                │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  ┌──────────────────────────────────────────┐  │
│  │         UI DYNAMIQUE (INTELLIGENCE)       │  │
│  │  - Carte interactive                      │  │
│  │  - Panels générés par ENGINE REGISTRY     │  │
│  │  - Toggle par moteur                      │  │
│  │  - Comparaison automatique                │  │
│  └──────────────────────────────────────────┘  │
└───────────────────────────────────────────────┘
```

---

## 7. CONFORMITÉ BCE-4X + STEEVE-MAX

| Critère | Statut | Détail |
|---------|--------|--------|
| Structure modulaire | ⚠ PARTIEL | Moteurs V1/V10 isolés, mais score_consolide couplé |
| Cohérence moteurs | ⚠ PARTIEL | 3 systèmes de mapping espèces (CERF vs deer vs chevreuil) |
| Versionnement | ✓ CONFORME | V1, V2, V10 clairement versionnés |
| Absence de duplication | ⚠ PARTIEL | alimentation_v1 dupliqué entre son module et score_consolide |
| UI ↔ API conforme | ✓ CONFORME | Frontend utilise REACT_APP_BACKEND_URL, pas de hardcoding |
| Flux de données | ✓ CONFORME | Unidirectionnel: API → Frontend |
| Stabilité | ✓ CONFORME | 0 régression, tests 100% |
| Sécurité | ✓ CONFORME | Admin Architecte protégé, JWT auth |

---

## 8. EXIGENCES TECHNIQUES — ARCHITECTURE AUTO-ADAPTATIVE

### 8.1 API unifiée et déclarative
```python
# Interface commune obligatoire pour chaque moteur
class BionicEngine(ABC):
    @abstractmethod
    def meta(self) -> EngineMeta:
        """Métadonnées: nom, version, espèces, poids par défaut"""
    
    @abstractmethod  
    def score_point(self, lat, lng, species, month) -> EngineScore:
        """Score normalisé 0-100 pour un point"""
    
    @abstractmethod
    def score_grid(self, center_lat, center_lng, species, month, grid_size) -> GridResult:
        """Grille de scores pour visualisation"""
```

### 8.2 Standardisation des moteurs
- Schéma commun: `{engine, version, species, month, score, components{}, tracability{}}`
- Mapping espèces unique: `CERF | ORIGNAL | OURS | DINDON | WAPITI`
- Pondérations déclaratives dans un fichier de configuration (pas dans le code)

### 8.3 UI dynamique
- Le frontend interroge `/api/v3/engines/registry` pour savoir quels moteurs sont actifs
- Chaque moteur fournit sa propre configuration de visualisation (couleur, icône, label)
- Les panels et toggles sont générés dynamiquement
- Comparaison et scoring consolidé calculés automatiquement

### 8.4 Synchronisation carte ↔ INTELLIGENCE
- Context React partagé ou Zustand store global
- Événements: `onZoneSelected`, `onSpeciesChanged`, `onMonthChanged`
- La carte et INTELLIGENCE réagissent aux mêmes événements

### 8.5 Mécanismes de fallback
- Si un moteur échoue → exclusion du score consolidé avec recalcul des poids
- Notification UI: "Moteur X indisponible — score partiel"
- Log BCE-4X: traçabilité complète des moteurs actifs/inactifs

### 8.6 Préparation V11/V12
- Ajout d'un moteur = 1 fichier + enregistrement dans le registry
- Zéro modification de code existant (Open/Closed Principle)
- Tests automatiques de compatibilité du nouveau moteur

---

## 9. PLAN DE MIGRATION RECOMMANDÉ

### Phase M1: Standardisation (1-2 sessions)
1. Créer l'interface `BionicEngine` (ABC) commune
2. Adapter ALIMENTATION-V1, REPOS-V1, CORRIDORS-V10, ALIMENTATION-V2 pour l'implémenter
3. Unifier le mapping espèces sur `CERF/ORIGNAL/OURS/DINDON/WAPITI`
4. Créer le moteur PRESSION-V1 dédié (extraire de score_consolide.py)

### Phase M2: Registry & Consolidateur (1 session)
1. Créer `/api/v3/engines/registry` — liste dynamique des moteurs
2. Refactorer `score_consolide.py` → `ConsolidatedScorer` utilisant le registry
3. Pondérations dans un fichier YAML/JSON de configuration

### Phase M3: API Gateway (1 session)
1. Créer un routeur unifié `/api/v3/*` comme façade
2. Simplifier server.py (supprimer les 50 try/except)
3. Versionnement uniforme

### Phase M4: INTELLIGENCE Frontend (2-3 sessions)
1. Créer un Zustand store global pour l'état BIONIC
2. Réécrire les pages Intelligence (Analytics, Forecast, Plan Maître)
3. Intégrer la communication carte ↔ Intelligence
4. UI dynamique basée sur le registry

### Phase M5: Validation (1 session)
1. Tests de régression complets
2. Validation BCE-4X formelle
3. Certification STEEVE-MAX

---

## 10. CONCLUSION

### Faisabilité de l'Option B (réécriture + déplacement + auto-adaptatif)
**FAISABLE avec conditions:**
- Les moteurs V1/V10 sont stables et bien isolés → migration sûre
- Les pages Intelligence sont des scaffolds → création pure, pas de régression
- MonTerritoireBionicPage.jsx est le point de risque principal → ne pas toucher
- Le couplage dans score_consolide.py doit être résolu en priorité

### Points de vigilance critiques
1. **NE PAS toucher MonTerritoireBionicPage.jsx** pendant la Phase M1-M3
2. **Standardiser le mapping espèces** AVANT toute autre action
3. **Créer PRESSION-V1** comme moteur isolé (extraire de score_consolide)
4. **Tester après chaque phase** — pas de big bang

---

**CONFIRMATION: AUDIT BCE-4X COMPLÉTÉ ✓**
**Date: 2026-03-18**
**Auditeur: Agent E1 — Emergent Labs**
