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
### RETRAIT MODE SECRET — iteration_53 (100%)

### REPOSITIONNEMENT INDICATEUR ZONE D'ANALYSE (2026-03-18) — iteration_54 (100%)
- Indicateur fixe repositionne en bas-gauche de la carte (position: bottom-[120px] left-2)
- Gap 20px avec la legende (conforme 16-24px STEEVE-MAX)
- Aucune superposition avec: toolbar, badges, popovers, selecteurs, panneaux lateraux
- Stable: position CSS absolue, z-index 999, pointer-events-none
- Tooltip hover BionicZone2km desactive (showTooltip=false par defaut)
- Affichage: icone carree pointillee orange + "Zone d'analyse" + "2 km x 2 km — {waypoint.name}"
- Visible uniquement quand selectedWaypointForZones actif

## Elements SUPPRIMES/DEPLACES
- Onglet LAYERS — supprime iteration_47
- Onglet CORRIDORS V10 — supprime iteration_48a
- Point "Alimentation secondaire" (V1) — supprime iteration_51
- Labels DOMINANT/SECONDAIRE/TERTIAIRE — ADMIN ONLY (iteration_52)
- Mode SECRET (cadenas) — ADMIN ONLY (iteration_53)

## Architecture de controle STEEVE-MAX (FINAL)
```
ZONES > ALIMENTATION > POINTS CHAUDS > SEUIL > CURSEUR > ADMIN(Shield)

Indicateur zone d'analyse: bas-gauche (120px du bas, gap 20px legende)
Legende: bas-gauche (56px du bas)
Zoom controls: haut-gauche
```

## Backlog
### P1 — Integration score consolide CORRIDORS-V10 dans heatmap
### P2 — RUT-V1, AFFUTS-V1, TRAJETS-V1
### P3 — Certification Finale BIONIC V3
### P3 — Refactoring MonTerritoireBionicPage.jsx

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin Architecte:** `Saturn5858*`
