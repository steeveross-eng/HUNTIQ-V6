# BIONIC HUNT/Chasse — Product Requirements Document

## Problème original
Application d'analyse de territoire de chasse intégrant un moteur géospatial (BIONIC Engine V7), une carte interactive (Leaflet/React-Leaflet), un scoring dynamique influencé par la météo en temps réel, et un système de validation automatisé (BCE).

Repo GitHub: https://github.com/steeveross-eng/HUNTIQ-V5
Branche: v6_autosave

## Utilisateur cible
Chasseurs francophones du Québec, analystes de territoire.

## Architecture
- **Frontend**: React + Leaflet + shadcn/ui + Tailwind
- **Backend**: FastAPI + MongoDB
- **Moteur**: BIONIC Engine V7 (zones organiques, exclusions, corridors)
- **Météo**: OpenWeatherMap (cache 30min, influence scoring)
- **Validation**: BIONIC Compliance Engine (BCE)

## Fonctionnalités implémentées

### V7 — Moteur d'exclusion (VERROUILLÉ)
- Génération de zones organiques avec exclusions anthropiques
- Scoring multi-couches (habitats, alimentation, repos, rut, corridors)
- Pipeline backend unique source de vérité

### V8.2 — Météo dynamique
- Service météo complet (now, forecast, influence)
- Cache backend 30min pour optimiser les appels OWM
- Influence météo sur le scoring en temps réel

### V8.3.A — Widget de Comparaison + Ajustements UX
- Endpoint `/api/v1/compare/waypoints` (POST, 2-3 waypoints en parallèle)
- Sélection multi-waypoints dans le panneau Waypoints
- CompareWidget overlay modal avec affichage côte à côte

### V6 — Session 11 Mars 2026 (NOUVELLES IMPLÉMENTATIONS)

#### 1. Zone 2 km² (IMPLÉMENTÉ ✅)
- Carré unique 2 km × 2 km centré sur le waypoint actif
- Contour pointillé orangé BIONIC (#f5a623)
- Sans remplissage (fillOpacity = 0)
- Affiché en permanence pour le waypoint sélectionné
- Composant: `/frontend/src/components/territoire/BionicZone2km.jsx`

#### 2. Suppression lignes rouges (IMPLÉMENTÉ ✅)
- StructureContrastLayer désactivé (return null)
- Carte propre, zéro pollution visuelle
- Fichier: `/frontend/src/components/territoire/StructureContrastLayer.jsx`

#### 3. Corridors 10X + Classification WWF (IMPLÉMENTÉ ✅)
- Service backend: `/backend/modules/bionic_engine_p0/services/corridor_10x.py`
- Classification WWF: Macro-corridors (>5km), Biologiques (1-5km), Conservation (<1km)
- Critères biologiques: connectivité, topographie, habitats, évitement
- Bénéfices écologiques: échanges génétiques, adaptation climatique, fragmentation
- Validation continuité automatique

## État actuel
- **Stable** : Zone 2km² et suppression lignes rouges déployées
- **BCE** : Opérationnel avec 10 validateurs
- **Tests** : À valider avec testing_agent

## Backlog prioritisé

### P1 — En cours
- [ ] Corridors 10X: Intégration complète dans le pipeline V7
- [ ] Optimisation pipeline zones (<0.5 sec)
- [ ] Tests BCE Auto-Run complets

### P2 — Phase E
- [ ] Audit fichiers legacy
- [ ] Décommission composants obsolètes
- [ ] Nettoyage architecture

### P3 — V8.4
- [ ] Vent animé Canvas 2D
- [ ] Dashboard BCE (interface d'administration)
- [ ] Enrichissement prédictif (hotspots, heatmaps)

## Intégrations tierces
- OpenWeatherMap (clé API dans .env)
- Overpass API (données géospatiales)
- Leaflet.js / React-Leaflet (cartographie)
- Shapely (géométrie backend)

## Dates clés
- 2026-03-11: Implémentation Zone 2km², Suppression lignes rouges, Corridors 10X
- 2026-03-10: Widget Comparaison V8.3.A
- 2026-02-24: PHASE C/D Knowledge Layer
