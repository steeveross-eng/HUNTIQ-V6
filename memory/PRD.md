# BIONIC HUNT - PRD.md

## Branche: steve-max

## Architecture
- **Frontend**: React + Leaflet + Shadcn/UI
- **Backend**: FastAPI + 27 Engines + Hotspot Engine V3 + Scheduler annuel
- **Database**: MongoDB (admin_hotspots)
- **Weather**: OpenWeatherMap (cache 60min)
- **Quality Gate**: BCE-4X (12+ regles, 1200/1200 PASS)

## Statut: PRET POUR CERTIFICATION FINALE BIONIC V3

### Securite & Consolidation (2026-03-16) - VALIDE
- BCE-4X indicateur retire de l'espace usager (/territoire) - PASS
- Admin (/admin) securise avec mot de passe Saturn5858* - PASS
- Admin Premium (/admin-premium) securise avec mot de passe Saturn5858* - PASS
- Onglet "Hotspots V3" supprime de /admin - PASS
- Module Hotspots V3 consolide dans Admin Premium > Terres/Hotspots - PASS
- Ancien mot de passe admin123 rejete - PASS

### Tache P0-1: Carte Leaflet interactive (2026-03-13) PASS
- Carte CartoDB dark tiles avec 300 polygones hotspots
- Couleurs: rouge=MAJEUR (80+), orange=FORT (60-79)
- Popup: score, espece, justification engines, type territoire, acces, ville, altitude, GPS
- Zoom automatique par region, controles zoom
- Bascule Carte/Tableau

### Tache P0-2: Liste complete enrichie (2026-03-13) PASS
- GPS (lat/lng), ville, code postal, altitude
- 7 types territoire: Prive, Public, Gouvernemental, ZEC, Pourvoirie, Reserve faunique, Territoire autochtone
- 4 statuts acces: Libre, Restreint, Payant, Permission requise
- Espece dominante, ScoreHotspot, justification engines, accessibilite, corridors V9
- 6 filtres: region, espece, classification, type territoire, acces, categorie
- 12 regions Quebec avec donnees realistes (villes, codes postaux, altitudes)

### Tache P0-3: Acces proprietaire/gestionnaire (2026-03-13) PASS
- ZEC: nom reel, tel, courriel, site web
- Pourvoiries: nom, tel, courriel, web
- Reserves fauniques: SEPAQ avec coordonnees
- Gouvernemental: MELCCFP, 1-800-561-1616, reglements acces
- Autochtone: Nations innue, algonquine, mi'gmaq avec coordonnees
- Terres privees: numero lot, cadastre, lien registre foncier
- Bouton "Contacter le gestionnaire du territoire"

### Tache P0-4: Extraction automatique ANNUELLE (2026-03-13) PASS
- POST /scheduler/run declenche extraction complete
- Retourne: run number, total_hotspots, next_scheduled (annee+1)
- Rapport BCE-4X automatique (PASS 1200/1200)
- Stockage MongoDB avec batch tracking

### Modules precedents
- Rotation 3D logos BIONIC (10s, preserve-3d)
- Phase 7: 3 controles inline toolbar (Corridors V9, Seuil 10%, Curseur)
- Phase 6: Document CI/CD BCE-4X
- BIONIC V3: 27 engines, 3 modeles fauniques
- Harmonisation couleurs, corridors V9 continuity

## Tests de regression (2026-03-16)
- Iteration 23: 16/16 backend + 100% frontend (Regression complete - 7 P0 tasks)
- Iteration 22: 16/16 backend + 100% frontend (7 P0 tasks certified)
- Iteration 21: 14/14 backend + 100% frontend (4 P0 features certified)

## API Endpoints
- POST /api/v1/admin/bionic-hotspots/scheduler/run - Extraction annuelle + BCE-4X
- GET /api/v1/admin/bionic-hotspots/scheduler/status - Statut scheduler
- GET /api/v1/admin/bionic-hotspots/territory-types - Types + distribution
- POST /api/v1/admin/bionic-hotspots/extract - Extraction standard
- GET /api/v1/admin/bionic-hotspots/list - Liste filtrable enrichie
- GET /api/v1/admin/bionic-hotspots/stats - Stats agregees
- GET /api/v1/admin/bionic-hotspots/export/geojson - Export GeoJSON
- GET /api/v1/admin/bionic-hotspots/export/json - Export JSON
- GET /api/v1/admin/bionic-hotspots/report/bce4x - Rapport BCE-4X
- GET /api/v1/admin/bionic-hotspots/report/daily - Rapport quotidien

## Donnees MOCKEES (approuve par l'utilisateur)
- territory_data_provider.py genere des donnees territoriales realistes pour le Quebec
- Non connecte aux registres publics en direct

## Backlog
### P1 - Conditions meteo locales OWM par hotspot
### P1 - Distance depuis waypoint utilisateur
### P2 - Dashboard analytics / apprentissage machine
### P3 - Multi-territoire

## Credentials
- Login utilisateur: Steeve.ross@gmail.com / Saturn5858*
- Admin (gate composant): Saturn5858*
- OWM_API_KEY dans backend/.env
