# BIONIC HUNT V8 — Product Requirements Document

## Problème original
Application d'analyse de territoire de chasse avec moteur géospatial BIONIC Engine, base écologique complète pour 3 espèces (Orignal, Chevreuil, Ours Noir), et système de validation automatisé BCE.

**Repo GitHub:** https://github.com/steeveross-eng/HUNTIQ-V5  
**Branche:** v6_autosave

## Architecture V8

### Backend (FastAPI + MongoDB)
- **Moteur BIONIC:** V7 avec zones organiques, exclusions, corridors
- **Base écologique V8:** 3 espèces × 4+ zones chacune
- **Corridors 10X:** Classification WWF + algorithme A*
- **BCE Ruleset V8:** 9 règles (4 zones + 5 corridors) + Auto-Run
- **Météo:** OpenWeatherMap avec cache 30min

### Frontend (React + Leaflet)
- **Zone 2 km²:** Carré centré sur waypoint actif
- **Corridors visuels:** Palette BIONIC, largeur variable, stopovers hachurés
- **Panneau écologique:** Corridors actifs, légende WWF, zones par espèce
- **Auto-load territoire:** Chargement automatique des couches

## Fonctionnalités implémentées — Session 11 Mars 2026

### 1. Base Écologique V8 ✅
**Fichier:** `/backend/modules/bionic_engine_p0/knowledge/ecological_database_v8.py`

Espèces couvertes:
- **ORIGNAL:** Alimentation, Repos, Rut, Corridor
- **CHEVREUIL:** Alimentation, Repos, Rut, Corridor
- **OURS NOIR:** Alimentation, Repos, Tanière, Corridor

### 2. Corridors 10X + Classification WWF ✅
**Fichier:** `/backend/modules/bionic_engine_p0/services/corridor_10x.py`

- Classification WWF: Macro (>5km), Biologique (1-5km), Conservation (<1km)
- Algorithme A* avec coûts de terrain
- Validation continuité automatique

### 3. Style Visuel BIONIC Corridors ✅
**Fichier:** `/frontend/src/components/territoire/CorridorsVisualLayer.jsx`

| Score | Couleur | Largeur | Label |
|-------|---------|---------|-------|
| 0-25% | Gris #D0D0D0 | 10m | Passage occasionnel |
| 25-35% | Jaune #F7E45A | 18m | Faible utilisation |
| 35-45% | Orange #F5A623 | 28m | Utilisation modérée |
| 45-55% | Rouge #D0021B | 38m | Forte utilisation |
| 55-100% | Rouge hachuré | 40m | Stopover (zone critique) |

### 4. BCE Ruleset V8 Complet ✅
**Fichier:** `/backend/bce/bce_ruleset_v8.py`

**Règles Zones (4):**
- `bce_zone_classification_valid`
- `bce_zone_topographic_valid`
- `bce_zone_hydrology_valid`
- `bce_zone_human_pressure_valid`

**Règles Corridors (5):**
- `bce_corridor_continuity_valid`
- `bce_corridor_topography_valid`
- `bce_corridor_wwf_classification_valid`
- `bce_corridor_human_pressure_respected`
- `bce_corridor_stopover_detection_valid`

### 5. BCE Auto-Run ✅
**Activation automatique à:**
- Chargement de MON TERRITOIRE
- Classification de zone
- Génération de corridor
- Détection de stopover
- Mise à jour du pipeline V7/V8

**Statut:** `auto_run_enabled: true`

### 6. Auto-Load Territoire ✅
**Fichier:** `/frontend/src/hooks/useTerritoryAutoLoad.js`

Charge automatiquement:
- Zones écologiques pertinentes
- Corridors 10X
- Stopovers
- Couches V7 nécessaires
- Selon la dernière recherche utilisateur

### 7. Zone 2 km² ✅
- Carré 2km × 2km centré sur waypoint actif
- Contour pointillé orangé (#f5a623)
- Sans remplissage

### 8. Suppression lignes rouges ✅
- StructureContrastLayer désactivé

## Tests validés
- API `/api/v1/ecological/species` → 3 espèces ✅
- API `/api/v1/ecological/species/orignal/zones` → 4 zones complètes ✅
- API `/api/v1/ecological/validate` → COMPLIANT/PARTIAL selon données ✅
- API `/api/bce/status` → 9 règles V8 + Auto-Run activé ✅

## Backlog

### P0 — Terminé
- [x] Base écologique 3 espèces
- [x] Corridors 10X + WWF
- [x] Style visuel BIONIC
- [x] BCE Ruleset V8 (9 règles)
- [x] BCE Auto-Run
- [x] Auto-load territoire
- [x] Zone 2 km²

### P1 — En cours
- [ ] Intégrer CorridorsVisualLayer dans la carte
- [ ] Intégrer EcologicalPanel dans la page territoire
- [ ] Afficher légende WWF dynamique

### P2 — Phase E
- [ ] Audit fichiers legacy
- [ ] Décommission composants obsolètes

### P3 — V8.4
- [ ] Vent animé Canvas 2D
- [ ] Heatmaps prédictives
- [ ] Dashboard BCE admin

## Note sur le merge GitHub
Le merge de `conflict_110326_1207` → `v6_autosave` doit être fait manuellement via:
- Bouton "Save to Github" dans Emergent
- Ou commande: `git merge origin/conflict_110326_1207 --allow-unrelated-histories`

## Dates clés
- **2026-03-11:** BIONIC V8 complet — Base écologique, Corridors visuels, BCE Ruleset V8 + Auto-Run
- **2026-03-10:** Widget Comparaison V8.3.A
