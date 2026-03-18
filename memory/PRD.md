# BIONIC V3 — PRD (Product Requirements Document)

## Probleme Original
Application BIONIC V3 — Outil d'analyse ecologique full-stack pour la gestion de la faune au Quebec.

## Architecture
- **Frontend:** React + Leaflet/react-leaflet
- **Backend:** FastAPI (Python)
- **Database:** MongoDB

## Taches Completees (resume)
### iterations 22-48a (voir historique complet)
### ENGINE ALIMENTATION-V2 — iteration_48 (100%)
### BUG FIX Tab + Salines Visibility — iteration_49 (100%)
### DIRECTIVE ESPECES STEEVE-MAX — iteration_50 (100%)

### OPTIMISATION SALINES + DIVERSIFICATION SPATIALE — iteration_51 (100%)
- Algorithme grille 4x4 (16 candidats) + selection gloutonne 300m min
- Selecteur intelligent 1-4 salines (strategies: spot/couverture/triangulation/quadrillage)
- Badge ALIMENTATION (X), salines jaunes/candidats gris
- Suppression complète Alimentation secondaire V1

### DEPLACEMENT COUCHES STEEVE-MAX (2026-03-18) — iteration_52 (100%)
- **Mode Admin Architecte**: Bouton bouclier (Shield) dans toolbar, protege par mot de passe
- **Vue standard (defaut)**: ZONES popover propre sans "Couches STEEVE-MAX", DOMINANT, SECONDAIRE, TERTIAIRE
- **Vue admin**: Titre "Couches STEEVE-MAX" + badges DOMINANT/SECONDAIRE/TERTIAIRE visibles
- **Tooltip admin**: "Controle la dominance comportementale interne, pas l'affichage."
- **Bouton violet quand actif**, gris quand inactif, desactivation sans mot de passe
- Tests: Frontend 100% (iteration_52.json), 0 regression

## Elements SUPPRIMES (INTERDICTION de recreer)
- Onglet LAYERS — supprime iteration_47
- Onglet CORRIDORS V10 — supprime iteration_48a
- Point "Alimentation secondaire" (V1) — supprime iteration_51
- Couches BIONIC alimentation/salines/alimentation_sec (V1) — dans BANNED_LAYERS

## Architecture de controle STEEVE-MAX (FINAL)
```
ZONES (unique centre de controle)
--- Zones (sous-elements: 7)
--- Corridors (sous-elements: 4)
--- Points (sous-elements: 8)
--- Overlays (Vent + Exclusions)
--- [ADMIN ONLY] Labels: DOMINANT/SECONDAIRE/TERTIAIRE + titre "Couches STEEVE-MAX"

ALIMENTATION (V2) — Position: apres ZONES, avant POINTS CHAUDS
--- Badge (X) = nombre salines actives
--- Master toggle + Salines toggle (disabled OURS/DINDON)
--- Selecteur 1-4 salines + Recommandations panel

POINTS CHAUDS (filtrage comportemental)
```

## API Endpoints
### CORRIDORS-V10
- POST /api/v10/corridors/analyze-full
### ALIMENTATION-V2
- POST /api/v2/alimentation/analyze (params: center_lat, center_lng, species, month, max_salines)
- GET /api/v2/alimentation/species

## Backlog
### P1 — Integration score consolide CORRIDORS-V10 dans heatmap
### P2 — RUT-V1, AFFUTS-V1, TRAJETS-V1
### P3 — Certification Finale BIONIC V3
### P3 — Refactoring MonTerritoireBionicPage.jsx

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin Architecte:** `Saturn5858*`
