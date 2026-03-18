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
### DEPLACEMENT COUCHES STEEVE-MAX — iteration_52 (100%)

### RETRAIT MODE SECRET (2026-03-18) — iteration_53 (100%)
- **Mode SECRET (cadenas vert)** deplace dans ADMIN PREMIUM
- Vue standard: Aucun cadenas visible, toolbar propre (ANALYSE > ZONES direct)
- Vue admin: Cadenas vert/rouge accessible apres activation mode Architecte
- privacyMode default=false: donnees utilisateur visibles par defaut
- Confirmation visuelle: cadenas absent en mode standard, present en mode admin

## Elements SUPPRIMES/DEPLACES (INTERDICTION de montrer a l'usager standard)
- Onglet LAYERS — supprime iteration_47
- Onglet CORRIDORS V10 — supprime iteration_48a
- Point "Alimentation secondaire" (V1) — supprime iteration_51
- Couches BIONIC alimentation/salines/alimentation_sec (V1) — BANNED_LAYERS
- Labels DOMINANT/SECONDAIRE/TERTIAIRE — ADMIN ONLY (iteration_52)
- Mode SECRET (cadenas) — ADMIN ONLY (iteration_53)

## Architecture de controle STEEVE-MAX (FINAL)
```
ZONES (unique centre de controle)
--- Zones (sous-elements: 7)
--- Corridors (sous-elements: 4)
--- Points (sous-elements: 8)
--- Overlays (Vent + Exclusions)

ALIMENTATION (V2) — Position: apres ZONES, avant POINTS CHAUDS
--- Badge (X) = nombre salines actives
--- Master toggle + Salines toggle (disabled OURS/DINDON)
--- Selecteur 1-4 salines + Recommandations panel

POINTS CHAUDS (filtrage comportemental)

ADMIN PREMIUM (bouclier Shield, mot de passe Saturn5858*)
--- Labels DOMINANT/SECONDAIRE/TERTIAIRE
--- Mode SECRET (cadenas privacyMode)
--- Tooltip: "Controle la dominance comportementale interne"
```

## API Endpoints
### CORRIDORS-V10
- POST /api/v10/corridors/analyze-full
### ALIMENTATION-V2
- POST /api/v2/alimentation/analyze (center_lat, center_lng, species, month, max_salines)
- GET /api/v2/alimentation/species

## Backlog
### P1 — Integration score consolide CORRIDORS-V10 dans heatmap
### P2 — RUT-V1, AFFUTS-V1, TRAJETS-V1
### P3 — Certification Finale BIONIC V3
### P3 — Refactoring MonTerritoireBionicPage.jsx

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin Architecte:** `Saturn5858*`
