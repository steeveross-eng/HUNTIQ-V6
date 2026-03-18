# BIONIC V3 — PRD (Product Requirements Document)

## Probleme Original
Application BIONIC V3 — Outil d'analyse ecologique full-stack pour la gestion de la faune au Quebec.

## Architecture
- **Frontend:** React + Leaflet/react-leaflet
- **Backend:** FastAPI (Python)
- **Database:** MongoDB

## Taches Completees (resume)
### iterations 22-48a (voir historique complet)

### ENGINE ALIMENTATION-V2 (2026-03-18) — iteration_48 (100%)
- Backend module complet: /backend/modules/alimentation_v2/
- Frontend salines: AlimentationV2Layer.jsx — points jaunes (#FFD700) dans zone 2km
- Panneau nutritionnel, onglet ALIMENTATION, sites permanents V1 SUPPRIMES dans BANNED_LAYERS

### BUG FIX: Tab + Salines Visibility (2026-03-18) — iteration_49 (100%)
- Onglet ALIMENTATION repositionne: ZONES > ALIMENTATION > POINTS CHAUDS
- Stabilite center prop (useMemo) + onDataLoaded ref pattern

### DIRECTIVE ESPECES STEEVE-MAX (2026-03-18) — iteration_50 (100%)
- OURS NOIR + DINDON: 0 salines, toggle disabled, message biologique
- CHEVREUIL / ORIGNAL / WAPITI: Salines fonctionnelles

### SUPPRESSION ALIMENTATION SECONDAIRE V1 (2026-03-18) — iteration_51 (100%)
- **Backend hunting_path.py**: Waypoint `alimentation_sec` SUPPRIME de WAYPOINT_TYPES, generation, et rapport amenagement
- **Frontend AmenagementPanel.jsx**: Section `2_alimentation_secondaire` SUPPRIMEE
- **Frontend HuntingPathLayer.jsx**: Couleur `alimentation_sec` SUPPRIMEE de MARKER_COLORS
- **Frontend useBionicLayers.js**: `alimentation_sec` ajoute a BANNED_LAYERS
- **V1 backend module**: Routes /api/v1/alimentation toujours registrees mais bloquees cote frontend (BANNED_LAYERS)
- Confirmation visuelle: Zero point "Alimentation secondaire" sur la carte
- Seul ALIMENTATION-V2 controle l'affichage des salines

## Elements SUPPRIMES (INTERDICTION de recreer)
- Onglet LAYERS — supprime iteration_47
- Onglet CORRIDORS V10 — supprime iteration_48a
- Point "Alimentation secondaire" (V1) — supprime iteration_51
- Couches BIONIC alimentation/salines (V1) — dans BANNED_LAYERS

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

## API Endpoints
### CORRIDORS-V10
- POST /api/v10/corridors/analyze-full
- GET /api/v10/corridors/multi | profiles | documentation

### ALIMENTATION-V2
- POST /api/v2/alimentation/analyze
- GET /api/v2/alimentation/species

## Normes Actives
- **STEEVE-MAX**: ZONES unique centre, hierarchie Zones > Corridors > Points
- **BCE-4X**: 16 zones, 64 centres, zero modification geometrique, firewall 13 tests
- **ALIMENTATION-V2**: Salines algorithmiques (sauf OURS/DINDON), nutrition par espece

## Backlog
### P1 — Integration score consolide CORRIDORS-V10 dans heatmap
### P2 — RUT-V1, AFFUTS-V1, TRAJETS-V1
### P3 — Certification Finale BIONIC V3
### P3 — Refactoring MonTerritoireBionicPage.jsx (trop volumineux)

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin:** `Saturn5858*`
