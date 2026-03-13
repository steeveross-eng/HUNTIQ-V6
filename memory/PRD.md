# BIONIC HUNT — PRD.md

## Branche: steve-max

## Architecture
- **Frontend**: React + Leaflet + Shadcn/UI — 42 composants territoire
- **Backend**: FastAPI + 9 Moteurs V1 (corridors) + 12 Moteurs V2 (territoire) + Pipeline V9
- **Weather**: OpenWeatherMap (cache 60min)
- **Quality Gate**: BCE-4X (12 regles, 100% PASS)

## Implemente (resume)
- 15 couches ecologiques normatives (habitats, rut, repos, alimentation, etc.)
- 9 moteurs V1 (corridor scoring V9)
- 12 moteurs V2 (territoire scoring global)
- Corridor continuity graph-based
- Hunting path TSP (vent supprime du pipeline)
- Amenagement 2km report
- BionicEngineHub frontend (12 moteurs temps reel)
- BCE-4X: 12 regles PASS (COLOR, UI, GEOM, COR, VIS)
- BAND_RATIO +20% (gris=26m, jaune=17m, orange=11m, rouge=6m, rouge_raye=4m)
- 15/15 couleurs harmonisees (backend, map, panel, core)

## Tests
- Iteration 14: 20/20 PASS (corrections finales)
- Iteration 13: 18/18 PASS (V2 integration)
- Iteration 12: 12/12 PASS (P0-P5)

## Audit (2026-03-13)
- Rapport complet: /app/memory/AUDIT_BIONIC_V2_COMPLET.md
- 12/12 engines actifs, 12/12 BCE PASS, 15/15 couleurs OK
- Constats: Species non differenciees (V2), ActionPlan score fixe=75

## Backlog
### P1
- Differencier scores par espece dans Engines V2
- Rendre ActionPlanEngine score dynamique
### P2
- Supprimer MovementCorridorsLayer.jsx (orphelin)
- Export GeoJSON/KML
### P3
- Injecter DEM/NDVI reels dans V2
- Multi-territoire, Analytics dashboard

## Credentials
- Steeve.ross@gmail.com / Saturn5858*
- OWM_API_KEY dans backend/.env
