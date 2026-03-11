# BIONIC HUNT/Chasse — Product Requirements Document

## Problème original
Application d'analyse de territoire de chasse intégrant un moteur géospatial (BIONIC Engine V7), une carte interactive (Leaflet/React-Leaflet), un scoring dynamique influencé par la météo en temps réel, et un système de validation automatisé (BCE).

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

### V8.2.2 — Améliorations UI/UX
- Calque de vent directionnel (WindFlowLayer)
- Exclusions masquées par défaut (mode debug)
- Persistance contexte utilisateur (localStorage)

### V8.3.A — Widget de Comparaison + Ajustements UX (10 mars 2026)
- Endpoint `/api/v1/compare/waypoints` (POST, 2-3 waypoints en parallèle)
- Sélection multi-waypoints dans le panneau Waypoints (checkboxes, max 3)
- CompareWidget overlay modal avec affichage côte à côte
- Sections : Scores, Zones, Corridors, Météo, Pression anthropique
- Fermeture auto du panneau TYPE DE CARTE après sélection (Popover contrôlé)
- Persistance du type de carte dans le contexte utilisateur
- Effet vent +25% (densité particules 1000, longueur vecteurs +25%, opacité cap 0.30, vitesse animation inchangée)
- Mode Particules auto-activé lors de l'ajout d'un waypoint

## État actuel
- **Stable** : Toutes les fonctionnalités livrées et testées
- **BCE** : Aucune régression détectée
- **Tests** : 100% backend (7/7 pytest) + 100% frontend (8/8 Playwright)

## Backlog prioritisé

### P1 — Phase E : Décommission Carte Interactive
- Auditer et supprimer les fichiers legacy
- Nettoyer les composants frontend obsolètes

### P2 — Fonctionnalités avancées
- Vent animé (Canvas 2D dynamique)
- Dashboard BCE (interface d'administration)
- Enrichissement prédictif (hotspots, heatmaps)

## Intégrations tierces
- OpenWeatherMap (clé API dans .env)
- Overpass API (données géospatiales)
- Leaflet.js / React-Leaflet (cartographie)
- Shapely (géométrie backend)
