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
- Bug affut sur lac corrige. Seuils eau resserres. Frontend ray-casting ajoute.
- Tests: Backend 16/16 (100%), Frontend 7/7 (100%)

### ENGINE CORRIDORS-V10 (2026-03-17) — iteration_28
- Module independant `/app/backend/modules/corridors_v10/`
- A* pathfinding sur grille 80x80 (25m/cellule)
- 5 especes, 12 parametres, continuite absolue
- Tests: Backend 31/31 (100%)

### Norme CORRIDOR-V1/V10 + Integration Mon Territoire (2026-03-17) — iteration_29
- **Classification normative 5 niveaux:** CRITIQUE #CC0000 4m, MAJEUR #FF0000 6m, FORT #FF8C00 11m, MODERE #FFD700 17m, FAIBLE #BFBFBF 26m
- **Scoring enrichi:** ECL, micro-topographie, nourriture, refuge, zones tampons, regeneration, mosaiques, suintements
- **Profils especes enrichis:** ORIGNAL (vallons humides, rectilignes), CERF (sinueux, lisieres), OURS (mixtes, frais, couverts)
- **Scoring par corridor:** Chaque corridor recoit score_individuel + niveau/couleur/largeur normative
- **Validation COR-006:** Explicit dans BCE-4X (continuite absolue zero dead-end)
- **Frontend:** `BionicCorridorsV10Layer.jsx` integre dans `MapContent.jsx` — rendu Leaflet Polyline avec palette normative, lissage, hover tooltip, z-ordering
- **Toggle:** "Corridors V10" dans la toolbar Mon Territoire
- **Tests:** Backend 21/21 (100%), Frontend 5/5 (100%) — 0 regression

## Fichiers Cles CORRIDORS-V10
```
/app/backend/modules/corridors_v10/
  __init__.py
  species_profiles.py    — 12 parametres + descriptions comportementales
  cost_surface.py        — Grille couts enrichie (15+ couches)
  pathfinder.py          — A* 8 directions + styles deplacement
  network_builder.py     — Reseau continu (Kruskal MST + forcement connexion)
  scoring.py             — Score reseau + score individuel par corridor
  classifier.py          — 5 niveaux normatifs obligatoires
  validator.py           — BCE-4X (7 checks + COR-006) + Steeve-MAX (5 checks)
  engine.py              — Orchestrateur principal
  router.py              — 6 endpoints API
  documentation.py       — Fiche technique JSON

/app/frontend/src/components/territoire/
  BionicCorridorsV10Layer.jsx  — Couche Leaflet corridors normatifs
```

## API Endpoints CORRIDORS-V10
- `POST /api/v10/corridors/analyze` — Analyse legere (sans GeoJSON)
- `POST /api/v10/corridors/analyze-full` — Analyse avec GeoJSON normatif
- `GET /api/v10/corridors/multi?lat=&lng=&month=` — Multi-especes
- `GET /api/v10/corridors/profiles` — Profils especes
- `GET /api/v10/corridors/profile/{species}` — Profil detaille
- `GET /api/v10/corridors/documentation` — Fiche technique

## Contraintes Actives
- Aucun engine existant modifie (V2, V3, IA, V9)
- Phase 4 integration transversale BLOQUEE
- Carre 2km2 reutilise

## Backlog
### P0 — Moteurs futurs (sur commande)
1. ~~CORRIDORS-V10~~ COMPLETE
2. HABITAT-V1
3. RUT-V1
4. AFFUTS-V1
5. TRAJETS-V1

### P1 — Integration score consolide CORRIDORS-V10 (sur commande)
### P2 — Certification Finale BIONIC V3
### P3 — Phase 4: Integration transversale (BLOQUEE)

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin:** `Saturn5858*`
