# BIONIC V3 — PRD (Product Requirements Document)

## Probleme Original
Application BIONIC V3 — Outil d'analyse ecologique full-stack pour la gestion de la faune au Quebec.

## Architecture
- **Frontend:** React + Leaflet/react-leaflet
- **Backend:** FastAPI (Python)
- **Database:** MongoDB

## Taches Completees (resume)
### iterations 22-43 (voir historique complet)
### OPTIMISATION UX STEEVE-MAX V2 — iteration_44 (100%)
### MODE ZONE D'ANALYSE + PERFORMANCE V3 — iteration_45 (100%)
### EXTENSION UX — Sous-elements granulaires — iteration_46 (100%)
### FUSION UX STEEVE-MAX + BUG FIX corridors — iteration_47 (100%)
### SUPPRESSION CORRIDORS V10 — iteration_48a (button removed)

### ENGINE ALIMENTATION-V2 (2026-03-18) — iteration_48 (100%)
- Backend module complet: /backend/modules/alimentation_v2/
- Frontend salines: AlimentationV2Layer.jsx — points jaunes (#FFD700) dans zone 2km
- Panneau nutritionnel: Panneau flottant avec carences, aliments, proteines, oligo-elements
- Onglet ALIMENTATION: Toolbar tab avec toggles Salines + Recommandations

### BUG FIX: ALIMENTATION-V2 Tab + Salines Visibility (2026-03-18) — iteration_49 (100%)
- Onglet ALIMENTATION repositionne: ZONES > ALIMENTATION > POINTS CHAUDS
- Active state: bg-yellow-500/15 text-yellow-400
- Master toggle + stabilite center prop (useMemo) + onDataLoaded ref pattern

### DIRECTIVE ESPECES STEEVE-MAX (2026-03-18) — iteration_50 (100%)
- **OURS NOIR**: Aucune saline generee (directive biologique). Toggle Salines desactive.
  Message: "L'ours noir n'utilise pas les salines..."
- **DINDON SAUVAGE**: Aucune saline generee. Toggle Salines desactive.
  Message: "Le dindon n'utilise pas les salines..."
- **CHEVREUIL / ORIGNAL**: Salines identiques (besoins mineraux similaires). Fonctionnel.
- **WAPITI**: Salines fonctionnelles.
- Backend: SPECIES_NO_SALINES = {OURS, DINDON}, FRONTEND_SPECIES_MAP pour mapping IDs
- Frontend: Toggle disabled + message explicatif amber + saline_composition masquee
- Panneau nutritionnel: Recommandations pertinentes par espece, saline_composition masquee pour OURS/DINDON
- Tests: Backend 11/11 + Frontend 100% (iteration_50.json), 0 regression

## Architecture de controle STEEVE-MAX (FINAL)
```
ZONES (unique centre de controle)
--- Zones DOMINANT (7 sous-elements)
--- Corridors SECONDAIRE (4 sous-elements)
--- Points TERTIAIRE (8 sous-elements)
--- Overlays (Vent + Exclusions)

ALIMENTATION (V2) — Position: apres ZONES, avant POINTS CHAUDS
--- Master toggle (Alimentation V2)
--- Salines (toggle, disabled pour OURS/DINDON)
--- Recommandations (panneau flottant)

POINTS CHAUDS (filtrage comportemental)
```

## Onglets SUPPRIMES (INTERDICTION de recreer)
- LAYERS — supprime iteration_47
- CORRIDORS V10 — supprime iteration_48a

## API Endpoints
### CORRIDORS-V10
- POST /api/v10/corridors/analyze-full
- GET /api/v10/corridors/multi | profiles | documentation

### ALIMENTATION-V2
- POST /api/v2/alimentation/analyze (accepte IDs frontend: chevreuil, orignal, ours_noir, dindon_sauvage, wapiti)
- GET /api/v2/alimentation/species

## Normes Actives
- **STEEVE-MAX**: ZONES unique centre, hierarchie Zones > Corridors > Points
- **BCE-4X**: 16 zones, 64 centres, zero modification geometrique, firewall 13 tests
- **EXTREME**: CRITIQUE = +40% weight, opacity 0.75
- **V10 permanent**: showCorridors = true
- **ALIMENTATION-V2**: Salines algorithmiques (sauf OURS/DINDON), nutrition par espece

## Backlog
### P1 — Integration score consolide CORRIDORS-V10 dans heatmap
### P2 — RUT-V1, AFFUTS-V1, TRAJETS-V1
### P3 — Certification Finale BIONIC V3
### P3 — Refactoring engine.py en modules specialises
### P3 — Refactoring MonTerritoireBionicPage.jsx (trop volumineux)
### P3 — React Context pour etat carte (eviter pattern re-render recurrent)

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin:** `Saturn5858*`
