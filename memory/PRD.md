# BIONIC V3 — PRD (Product Requirements Document)

## Problème Original
Application BIONIC V3 — Outil d'analyse écologique full-stack (React + FastAPI + MongoDB) pour la gestion de la faune au Québec. Moteurs écologiques complexes (V1, V2, V3, V9) pour l'analyse de données géographiques et environnementales.

## Architecture
- **Frontend:** React + Leaflet/react-leaflet
- **Backend:** FastAPI (Python)
- **Database:** MongoDB
- **Intégrations:** OpenWeatherMap, Open-Meteo, Open-Elevation, NASA MODIS, OSM Overpass

## Tâches Complétées

### Sécurité & Consolidation
- Gate admin, suppression BCE-4X public, consolidation UI (iteration_22/23)

### Audit Écologique Global (2026-03-16)
- Phase 1-4 complètes: MD, YAML, PDF, pipeline ASCII
- Accessible via `/api/audit/{filename}`

### Bouton "Carte" + Deep Link Mon Territoire (2026-03-16)
- Bouton dans tableau hotspots, preview satellite 300x180, deep link (iteration_24: 10/10)

### ENGINE ALIMENTATION-V1 (2026-03-16)
- Module 100% indépendant: `/app/backend/modules/alimentation_v1/`
- 5 espèces: CERF, ORIGNAL, OURS, DINDON, WAPITI
- Score SITE (0-100): PROTÉINES(0-25) + ÉNERGIE(0-25) + MINÉRAUX(0-20) + SÉCURITÉ(0-20) + EFFORT(0-10)
- Classification: OPTIMALE / TRÈS BONNE / UTILISABLE / FAIBLE
- Grille 10m×10m dans carré 2km² existant
- Couches: LiDAR, essences, occupation sol, hydro, conifères, pente
- Validation BCE-4X: PASS
- API: `/api/v1/alimentation/analyze`, `/point`, `/profiles`, `/profile/{species}`, `/documentation`, `/multi`
- Tests: 17/18 PASS (iteration_25)

### ENGINE REPOS-V1 (2026-03-16)
- Module 100% indépendant: `/app/backend/modules/repos_v1/`
- 5 espèces: CERF, ORIGNAL, OURS, DINDON, WAPITI
- Score REPOS (0-100): COUVERT(0-30) + CALME(0-25) + THERMIQUE(0-20) + ACCESSIBILITÉ(0-15) + PROX_ALIM(0-10)
- Classification: OPTIMAL / TRÈS BON / UTILISABLE / FAIBLE
- Réutilise layers de ALIMENTATION-V1
- Validation BCE-4X: PASS
- API: `/api/v1/repos/analyze`, `/point`, `/profiles`, `/profile/{species}`, `/documentation`, `/multi`
- Tests: 16/17 PASS (iteration_25)

### Ajout Wapiti dans Mon Territoire (2026-03-16)
- speciesConfig.js: Wapiti ajouté (couleur #B8860B, icône Mountain)
- Dropdown: 6 espèces (Orignal, Chevreuil, Ours noir, Dindon sauvage, Wapiti, Toutes)
- Seuil dynamique d'attractivité inchangé
- Tests frontend: 6/6 PASS (iteration_25)

## Contraintes Non Négociables Respectées
1. Aucun engine existant modifié (V2, V3, IA, V9)
2. Carré 2km² réutilisé tel quel
3. Seuil dynamique d'attractivité actif et inchangé

## Backlog

### P0 — PLAN DE MATCH STEEVE-MAX
- Optimisation modèles écologiques (en attente instructions Steeve)

### P0 — Phase 4 Intégration Transversale (BLOQUÉE)
- Remplacer food_score_v2 par alimentation_v1 (Hotspots)
- Remplacer nutrition par alimentation_v1 (Corridors V9)
- Intégrer dans Behavior, Predictive AI, Global Attractiveness
- **Exécution uniquement sur commande explicite de Steeve**

### P1 — Certification Finale BIONIC V3

### P2 — Propositions d'amélioration
- P-ALIM-01 à P-HOT-01 (identifiées dans l'audit)

## Données Mockées
- Données territoriales + couches fines (LiDAR, essences, etc.) — algorithmiques, approuvées

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin:** `Saturn5858*`
