# BIONIC V3 — PRD (Product Requirements Document)

## Probleme Original
Application BIONIC V3 — Outil d'analyse ecologique full-stack pour la gestion de la faune au Quebec.

## Architecture
- **Frontend:** React + Leaflet/react-leaflet
- **Backend:** FastAPI (Python)
- **Database:** MongoDB

## Taches Completees (resume)
### iterations 22-53 (voir historique complet)

### DESACTIVATION POPUP ZONE D'ANALYSE (2026-03-18) — iteration_55 (100%)
- **Popup zone d'analyse** completement desactive en mode usager standard
- BionicZone2kmLayer: showTooltip=false par defaut, prop explicite (plus de forçage interne)
- BionicZone2km: showTooltip default=false
- Indicateur fixe bas-gauche: visible uniquement en adminArchitecteMode
- Aucune interaction (hover, zoom, pan, clic) ne reactive le popup
- Confirmation visuelle: carte 100% degagee de tout popup zone d'analyse

## Elements SUPPRIMES/DEPLACES (ADMIN ONLY)
- Onglet LAYERS — supprime iteration_47
- Onglet CORRIDORS V10 — supprime iteration_48a
- Point "Alimentation secondaire" (V1) — supprime iteration_51
- Labels DOMINANT/SECONDAIRE/TERTIAIRE — ADMIN ONLY (iteration_52)
- Mode SECRET (cadenas) — ADMIN ONLY (iteration_53)
- Popup zone d'analyse + indicateur fixe — ADMIN ONLY (iteration_55)

## Architecture de controle STEEVE-MAX (FINAL)
```
ZONES > ALIMENTATION(X) > POINTS CHAUDS > SEUIL > CURSEUR > ADMIN(Shield)

ADMIN PREMIUM (bouclier Shield, mot de passe Saturn5858*):
- Labels DOMINANT/SECONDAIRE/TERTIAIRE
- Mode SECRET (cadenas privacyMode)
- Indicateur zone d'analyse (bas-gauche)
- Tooltip zone 2km sur rectangle pointille
```

## Backlog
### P1 — Integration score consolide CORRIDORS-V10 dans heatmap
### P2 — RUT-V1, AFFUTS-V1, TRAJETS-V1
### P3 — Certification Finale BIONIC V3
### P3 — Refactoring MonTerritoireBionicPage.jsx

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin Architecte:** `Saturn5858*`
