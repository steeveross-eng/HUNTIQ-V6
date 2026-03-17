# BIONIC V3 — PRD (Product Requirements Document)

## Probleme Original
Application BIONIC V3 — Outil d'analyse ecologique full-stack pour la gestion de la faune au Quebec.

## Architecture
- **Frontend:** React + Leaflet/react-leaflet
- **Backend:** FastAPI (Python)
- **Database:** MongoDB

## Taches Completees

### Securite & Consolidation — iteration_22/23
### Audit Ecologique Global — iteration_24
### Bouton Carte + Deep Link — iteration_24 (10/10)
### ENGINE ALIMENTATION-V1 + REPOS-V1 + Wapiti — iteration_25
### PLAN DE MATCH STEEVE-MAX v1 + Heatmap Officiel — iteration_26 (29/29 + 9/9)

### Correction BCE-4X: Affuts sur eau (2026-03-17) — iteration_27
- **Bug:** Affut place sur surface d'eau (lac) — violation BCE-4X majeure
- **Cause:** Seuil water intersection trop permissif (8%)
- **Corrections:**
  1. Seuil global eau: 0.08 -> 0.03
  2. LAYER_WATER_THRESHOLDS: affuts=0.0, salines=0.0, trajets=0.01
  3. Frontend: _pointInPolygon ray-casting pour exclusion centroide sur hydro
  4. Score consolide: retourne score=0 pour surfaces d'eau
- **Tests:** Backend 16/16 (100%), Frontend 7/7 (100%), 0 regression
- **BCE-4X: PASS** — affuts=0% eau, salines=0% eau

### ENGINE CORRIDORS-V10 (2026-03-17) — iteration_28
- **Moteur:** Corridors fauniques multi-especes avec A* sur surface de couts
- **Module:** `/app/backend/modules/corridors_v10/` (independant)
- **Especes:** CERF, ORIGNAL, OURS, DINDON, WAPITI (12 parametres chacun)
- **Algorithme:** A* pathfinding sur grille 80x80 (25m/cellule) dans carre 2km2
- **Zones ecologiques:** alimentation, repos, rut, eau (64 zones par analyse)
- **Continuite absolue:** connected=True, dead_ends=0 (zero cul-de-sac)
- **Validation BCE-4X:** 7/7 checks PASS (GEOM-001 a COMP-001)
- **Validation Steeve-MAX:** 5/5 checks PASS (SM-001 a SM-005)
- **API:** 6 endpoints `/api/v10/corridors/*`
- **Tests:** Backend 31/31 (100%), 0 regression
- **Anti-regression:** ALIMENTATION-V1 et REPOS-V1 intacts

## Contraintes
- Aucun engine existant modifie (V2, V3, IA, V9)
- Carre 2km2 reutilise, seuil dynamique inchange
- Phase 4 integration transversale BLOQUEE

## Backlog
### P0 — Moteurs futurs (sur commande Steeve)
1. ~~CORRIDORS-V10~~ COMPLETE, 2. HABITAT-V1, 3. RUT-V1, 4. AFFUTS-V1, 5. TRAJETS-V1
### P1 — Integration frontend CORRIDORS-V10 (couche visualisation Mon Territoire)
### P1 — Integration score consolide CORRIDORS-V10 (sur commande)
### P2 — Certification Finale BIONIC V3
### P3 — Propositions audit (P-ALIM-01 a P-HOT-01)

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin:** `Saturn5858*`
