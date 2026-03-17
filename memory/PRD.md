# BIONIC V3 — PRD (Product Requirements Document)

## Problème Original
Application BIONIC V3 — Outil d'analyse écologique full-stack (React + FastAPI + MongoDB) pour la gestion de la faune au Québec.

## Architecture
- **Frontend:** React + Leaflet/react-leaflet
- **Backend:** FastAPI (Python)
- **Database:** MongoDB
- **Intégrations:** OpenWeatherMap, Open-Meteo, OSM Overpass

## Tâches Complétées

### Sécurité & Consolidation
- Gate admin, suppression BCE-4X public, consolidation UI (iteration_22/23)

### Audit Écologique Global (2026-03-16)
- Livrables: MD, YAML, PDF, pipeline ASCII — `/api/audit/{filename}`

### Bouton Carte + Deep Link (2026-03-16)
- Bouton dans tableau hotspots, preview satellite, deep link Mon Territoire (iteration_24: 10/10)

### ENGINE ALIMENTATION-V1 (2026-03-16)
- Module indépendant, 5 espèces, PROTÉINES+ÉNERGIE+MINÉRAUX+SÉCURITÉ+EFFORT, BCE-4X PASS

### ENGINE REPOS-V1 (2026-03-16)
- Module indépendant, 5 espèces, COUVERT+CALME+THERMIQUE+ACCESSIBILITÉ+PROX_ALIM, BCE-4X PASS

### Ajout Wapiti (2026-03-16)
- speciesConfig.js: Wapiti #B8860B, 6 espèces total (iteration_25)

### PLAN DE MATCH STEEVE-MAX v1 (2026-03-17)
- Document normatif: 9 définitions écologiques 3× plus précises
- Normes BCE-4X (géométrie, écologie, topographie, comportement, anti-régression, inter-moteurs)
- Normes Steeve-MAX (documentation, traçabilité, cohérence visuelle/multi-espèces/saisonnière/opérationnelle)
- Roadmap: CORRIDORS-V10, HABITAT-V1, RUT-V1, AFFÛTS-V1, TRAJETS-V1
- Livrables: MD + PDF via `/api/audit/PLAN_DE_MATCH_STEEVE_MAX_v1.*`

### Heatmap Officiel BIONIC (2026-03-17)
- Score consolidé: ALIMENTATION(0.45) + REPOS(0.35) + PRESSION(0.20) → Score 0-100
- BionicScoreHeatmap: couche principale, palette bleu→vert→jaune→rouge, leaflet.heat
- BionicScoreBadge: anneau circulaire + label dans toolbar header
- SessionHeatmap redondant retiré, remplacé par heatmap écologique
- API: `/api/v1/score-consolide/point`, `/api/v1/score-consolide/heatmap`
- Pondérations transparentes, traçabilité complète
- Engines en attente: corridors_v10, habitat_v1, rut_v1
- Tests iteration_26: Backend 29/29 (100%), Frontend 9/9 (100%)

## Contraintes
- Aucun engine existant modifié (V2, V3, IA, V9)
- Carré 2km² réutilisé, seuil dynamique inchangé
- Phase 4 intégration transversale BLOQUÉE

## Backlog

### P0 — Moteurs futurs (sur commande Steeve)
1. CORRIDORS-V10
2. HABITAT-V1
3. RUT-V1
4. AFFÛTS-V1
5. TRAJETS-V1

### P1 — Certification Finale BIONIC V3

### P2 — Propositions audit (P-ALIM-01 à P-HOT-01)

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin:** `Saturn5858*`
