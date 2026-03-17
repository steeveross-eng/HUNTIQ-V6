# BIONIC V3 — PRD (Product Requirements Document)

## Problème Original
Application BIONIC V3 — Outil d'analyse écologique full-stack pour la gestion de la faune au Québec.

## Architecture
- **Frontend:** React + Leaflet/react-leaflet
- **Backend:** FastAPI (Python)
- **Database:** MongoDB

## Tâches Complétées

### Sécurité & Consolidation — iteration_22/23
### Audit Écologique Global — iteration_24
### Bouton Carte + Deep Link — iteration_24 (10/10)
### ENGINE ALIMENTATION-V1 + REPOS-V1 + Wapiti — iteration_25
### PLAN DE MATCH STEEVE-MAX v1 + Heatmap Officiel — iteration_26 (29/29 + 9/9)

### Correction BCE-4X: Affûts sur eau (2026-03-17) — iteration_27
- **Bug:** Affût placé sur surface d'eau (lac) — violation BCE-4X majeure
- **Cause:** Seuil water intersection trop permissif (8%)
- **Corrections:**
  1. Seuil global eau: 0.08 → 0.03
  2. LAYER_WATER_THRESHOLDS: affuts=0.0, salines=0.0, trajets=0.01
  3. Frontend: _pointInPolygon ray-casting pour exclusion centroïde sur hydro
  4. Score consolidé: retourne score=0 pour surfaces d'eau
- **Tests:** Backend 16/16 (100%), Frontend 7/7 (100%), 0 régression
- **BCE-4X: PASS** — affuts=0% eau, salines=0% eau

## Contraintes
- Aucun engine existant modifié (V2, V3, IA, V9)
- Carré 2km² réutilisé, seuil dynamique inchangé
- Phase 4 intégration transversale BLOQUÉE

## Backlog
### P0 — Moteurs futurs (sur commande Steeve)
1. CORRIDORS-V10, 2. HABITAT-V1, 3. RUT-V1, 4. AFFÛTS-V1, 5. TRAJETS-V1
### P1 — Certification Finale BIONIC V3
### P2 — Propositions audit (P-ALIM-01 à P-HOT-01)

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin:** `Saturn5858*`
