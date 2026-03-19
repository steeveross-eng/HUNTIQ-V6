# BIONIC V3 — PRD

## Probleme Original
Application BIONIC V3 — Outil d'analyse ecologique full-stack pour la gestion de la faune au Quebec.

## Architecture
- **Frontend:** React + Leaflet + Zustand v5.0.12
- **Backend:** FastAPI (Python)
- **Database:** MongoDB
- **Rules:** /app/bionic/ (BCE4X.toml, STEEVEMAX.toml, AutoValidator)
- **Gateway:** /app/backend/modules/api_gateway/router.py

## OPTION B — TOUTES PHASES COMPLETEES

### M1 STANDARDISATION — VALIDE 100%
### M2 REGISTRY + REGLES — VALIDE 100%
### M3 API GATEWAY — VALIDE 100%
### M4 INTELLIGENCE FRONTEND — VALIDE 100%

### FUSION ANALYSE -> INTELLIGENCE — VALIDE 100%
### TABLEAU CENTRAL INTELLIGENCE — VALIDE 100%
### RESTAURATION CARTE + ANTI-REGRESSION — VALIDE 100%
### TABLEAU FLOTTANT NON-BLOQUANT — VALIDE 100%

### UNIFICATION ANALYTIQUE (2026-03-19) — VALIDE 100%
- BionicLegend supprimee de la carte (absorbee par INTELLIGENCE)
- SidePanelZones supprime (TRAJET & AMENAGEMENT absorbes par INTELLIGENCE)
- Side panel uniquement pour onglets operationnels (waypoints, lieux, groupe, exclusions)
- Carte epuree: overlays, zones, corridors, marqueurs UNIQUEMENT
- INTELLIGENCE = seule source analytique centrale
- Refactoring: 2119 -> 1356 lignes (-36%)
- Composants extraits: TerritoireToolbar, TerritoireDialogs, NutritionPanel, useTerritoireEffects
- BCE-4X 23/23 | STEEVE-MAX 12/12 | Tests 100%

## Composants Extraits (Refactoring STEEVE-MAX)
- TerritoireToolbar.jsx — Toolbar complete extraite
- TerritoireDialogs.jsx — Tous les dialogues (places, waypoints, share, group)
- NutritionPanel.jsx — Panneau recommandations ALIMENTATION-V2
- useTerritoireEffects.js — Hooks extraits (toasts, amenagement, snapshot, scores)
- IntelligenceDashboard.jsx — Tableau flottant central non-bloquant
- ModeGuidePro/ModeScientifique/ModeTerrain.jsx — 3 modes
- SolunarChart.jsx — Courbe SVG LUNASOLCAL 24h

## Regles BCE-4X Anti-Regression
- La carte est l'element MAITRE de MON TERRITOIRE
- INTELLIGENCE = seule source analytique (zero doublon)
- Aucun panneau lateral analytique autorise
- Carte toujours pleine largeur en mode carte
- Side panel = operationnel uniquement (waypoints, lieux, groupe, exclusions)

## Backlog
### P1 — Refactoring avance (1356 -> ~800 lignes, extraction zone processing)
### P1 — Certification BIONIC V3 (documentation finale M1-M4)
### P2 — Migration legacy (RUT-V1, AFFUTS-V1, TRAJETS-V1) — GELE

## Credentials
- **User:** `Steeve.ross@gmail.com` / `Saturn5858*`
- **Admin Architecte:** `Saturn5858*`
