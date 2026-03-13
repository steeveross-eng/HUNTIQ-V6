# BIONIC HUNT — PRD.md

## Branche: steve-max

## Architecture
- **Frontend**: React + Leaflet + Shadcn/UI — 42 composants territoire
- **Backend**: FastAPI + 9 Moteurs V1 (corridors) + 12 Moteurs V2 (territoire) + Pipeline V9
- **Weather**: OpenWeatherMap (cache 60min)
- **Quality Gate**: BCE-4X (12+ regles, 100% PASS)

## Implemente (resume)
- 15 couches ecologiques normatives
- 9 moteurs V1 (corridor scoring V9)
- 12 moteurs V2 (territoire scoring global)
- Corridor continuity graph-based
- Hunting path TSP (vent supprime)
- Amenagement 2km report
- BionicEngineHub frontend (12 moteurs temps reel)
- BCE-4X: 12+ regles PASS
- BAND_RATIO +20%
- **HARMONISATION TOTALE COULEURS** (2026-03-13):
  - Module centralise: bionicColorsConfig.js (source unique de verite)
  - 15/15 couleurs identiques sur 7 fichiers sources
  - Diagnostic panel FACTORS alignes (Relief=#FF7043, Structure=#15803D, Eau=#3B82F6)
  - Analyse panel barres alignees (Rut=#FF4D6D, Salines=#FFFF00, Trajets=#FF9800)
  - BIONIC_LAYERS legacy corrige (rut, salines, affuts, hydro, peuplements, repos, corridors)
  - bionicDataAdapter NORM_COLORS harmonise

## Tests
- Iteration 15: 19/19 backend + 100% frontend UI verified (Color Harmonization TOTAL)
- Iteration 14: 20/20 PASS (corrections finales)
- Iteration 13: 18/18 PASS (V2 integration)

## Backlog
### P1 - Differencier scores par espece dans Engines V2
### P2 - Supprimer MovementCorridorsLayer.jsx, Export GeoJSON/KML
### P3 - DEM/NDVI reels, Multi-territoire, Analytics dashboard

## Credentials
- Steeve.ross@gmail.com / Saturn5858*
- OWM_API_KEY dans backend/.env
