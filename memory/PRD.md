# BIONIC V3 — PRD

## Probleme original
Construire CORRIDORS-V10, un moteur ecologique sophistique. Le projet a evolue vers un refactoring majeur "OPTION B" pour transformer le module INTELLIGENCE en un systeme moderne, auto-adaptatif et decouple.

## Objectif actuel
Implementer le cockpit central flottant `IntelligenceDashboard` SUPRA-INTELLIGENT avec gouvernance stricte STEEVE-MAX + BCE-4X.

## Architecture
- **Frontend:** React + Leaflet + Zustand (useBionicStore)
- **Backend:** FastAPI + modules dynamiques (EngineRegistry, BCE-4X/STEEVE-MAX validators)
- **No external DB** — donnees generees par les moteurs backend

## Charte de Gouvernance BIONIC
- **Autorite unique:** Steeve
- **INTELLIGENCE:** 2 etats uniquement (ferme / cockpit complet)
- **Interdictions:** PiP, widget, mini-tableau, duplication analytique, palette multiple
- **Processus:** suggestion → justification → conformite → validation → GO → dev → test → audit → integration

## Ce qui est implemente

### Backend
- [x] EngineRegistry dynamique + BCE-4X/STEEVE-MAX validators (23/23, 12/12)
- [x] API Gateway /api/v3/* (summary, forecast, plan, guide-pro, solunar, scientifique)
- [x] Endpoint guide-pro: retourne weather_official (temperature, vent)
- [x] Endpoint solunar: curve_24h, hunting_windows, periods

### Frontend — Corrections C1-C4 (VALIDEES)
- [x] C1: Mode isCompact supprime — 2 etats uniquement
- [x] C2: Palette terrain premium harmonisee (vert foret, brun terre, sable, gris roche)
- [x] C3: Fond topographique + verre depoli 78% sur cockpit
- [x] C4: Commentaires residuels nettoyes

### Frontend — Sections 2-7 (VALIDEES)
- [x] S2: TerritoireToolbar — palette terrain premium (INTELLIGENCE + CURSEUR)
- [x] S3: Doublon INTELLIGENCE supprime de la barre superieure (App.js + mobile)
- [x] S3.1: Logo Brain dans toolbar INTELLIGENCE
- [x] S3.2: Logo Brain dans entete cockpit INTELLIGENCE
- [x] S4: Header epure (aucun score, seulement temperature/vent/LIVE)
- [x] S4: Score Terrain + Score Chasse deplaces dans GUIDE PRO
- [x] S5: Temperature synchronisee header ↔ GUIDE PRO via weather_official + Zustand
- [x] S6: HEURES HOT SUPRA-INTELLIGENT (heures exactes, courbe coloree, badges HOT, halo temps reel, mini-legende)
- [x] S7: SolunarChart SUPRA-INTELLIGENT (3D, glass, topographie, animations, hierarchie visuelle)

### Refactoring
- [x] MonTerritoireBionicPage.jsx: 2119 → 1357 lignes (cible ~800)
- [x] Extractions: TerritoireToolbar, TerritoireDialogs, NutritionPanel, useTerritoireEffects

## Backlog prioritise

### P0
- [ ] Continuer refactoring MonTerritoireBionicPage.jsx (1357 → ~800 lignes)
- [ ] Synchronisation bidirectionnelle Intelligence → Carte (markers/highlights sur la carte)
- [ ] Gel de version bionic-v3-stable + branches supra/certification

### P1
- [ ] Preparation certification BIONIC V3 (documentation M1-M4, rapport compliance)

### P2
- [ ] Migration legacy engines (RUT-V1, AFFUTS-V1, TRAJETS-V1) — GELE

### P3
- [ ] Certification finale BIONIC V3

## Credentials
- **User:** Steeve.ross@gmail.com / Saturn5858*
- **Admin Architecte:** Saturn5858*
