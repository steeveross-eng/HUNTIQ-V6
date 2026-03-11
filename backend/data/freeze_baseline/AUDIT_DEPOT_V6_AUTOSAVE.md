# RAPPORT D'AUDIT COMPLET — Branche v6_autosave
## BIONIC V5 — Cartographie exhaustive du depot
**Date :** 2026-03-08 | **Statut :** Lecture seule, aucune modification

---

## METRIQUES GLOBALES

| Metrique | Valeur |
|---|---|
| Fichiers frontend (src/) | 623 (378 JSX + 238 JS + 4 CSS + 3 autres) |
| Fichiers backend (.py) | 736 |
| Fichiers public/ | 32 |
| Lignes JSX | 117 647 |
| Lignes JS | 28 434 |
| Lignes Python | 235 063 |
| **Total lignes de code** | **~381 000** |
| Taille frontend src/ | 7.3 MB |
| Taille backend/ | 52 MB |
| Taille public/ | 14 MB |
| Taille /app/sources/ (archives) | 74 MB |
| Taille /app/docs/ | 11 MB |

---

## SECTION 1 — CARTOGRAPHIE DES DOSSIERS

### 1.1 frontend/src/components/ (18 sous-dossiers)

| Dossier | Fichiers | Role | Statut |
|---|---|---|---|
| **territoire/** | 27 JSX | Coeur BIONIC V5 — carte, zones, overlays | **ACTIF, GELE** |
| **territory/** | 10 JSX + 3 JS | Anciens composants territoire (legacy) | SUSPECT |
| **map/** | 2 (JSX+CSS) + index | Popup carte generique | ACTIF |
| **maps/** | 3 JSX | BathymetryLayers, BionicAdvancedZones, BionicMapSelector | SEMI-ACTIF |
| **bionic/** | 9 JSX + 2 sous-dossiers | CarteBionic, Hotspots, Admin, Charts | ACTIF |
| **bionic/charts/** | 2 JSX + index | OptimalWindowsTimeline, ScoreDistribution, Radar | ACTIF |
| **bionic/admin/** | 1 JSX + index | AdminBionicHotspots | ACTIF |
| **charts/** | 1 JSX + index | LightCharts | ACTIF |
| **core/** | 7 JSX + index | CoreButton, CoreCard, CoreError, CoreLayout, etc. | **NON IMPORTE (0 refs)** |
| **admin/** | 2 JSX | MaintenanceControl, SiteAccessControl | ACTIF |
| **filters/** | 1 JSX | AdvancedFilters | ACTIF |
| **frontpage/** | 16 JSX + index | Sections page d'accueil (Hero, Bento, Blog, etc.) | ACTIF |
| **layout/** | 1 JSX + index | BionicHeader | ACTIF |
| **navigation/** | 1 JSX + index | ModularNavigation | ACTIF |
| **partner/** | 1 JSX | PartnerOffers | ACTIF |
| **social/** | 0 fichiers | **VIDE** | PARASITE |
| **trips/** | 5 JSX | ActiveTrip, CreateTrip, TripHistory, TripStats | ACTIF |
| **ui/** (Shadcn) | ~40 fichiers | Composants Shadcn/UI (button, card, dialog, etc.) | ACTIF |

### 1.2 frontend/src/ui/ (9 sous-dossiers)

| Dossier | Fichiers | Statut |
|---|---|---|
| administration/ | 68 fichiers (34 modules admin) | ACTIF |
| monetisation/ | 20 fichiers | ACTIF |
| plan_maitre/ | 6 fichiers | ACTIF |
| scoring/ | 6 fichiers | ACTIF |
| meteo/ | 4 fichiers | ACTIF |
| strategie/ | 4 fichiers | ACTIF |
| territoire/ | 4 fichiers | ACTIF |
| **core/** | **0 fichiers** | **VIDE — PARASITE** |
| **metier/** | **0 fichiers** | **VIDE — PARASITE** |

### 1.3 frontend/src/modules/ (42 modules)

| Categorie | Modules | Statut |
|---|---|---|
| **Modules actifs (>2 fichiers)** | ai, affiliate, analytics, behavioral, cart, collaborative, customers, ecoforestry, groupe, legaltime, live_heading_view, map_interaction, map_hotspots, marketplace, notifications, nutrition, onboarding, orders, predictive, products, realestate, recommendation, scoring, strategy, suppliers, territory, tutorial, user, weather, wildlife | ACTIF |
| **Modules squelettes (1-2 fichiers)** | adaptive_strategy, advanced_geospatial, business, dashboard, engine_3d, formations, geospatial, keyboard, planmaitre, plugins, progression, simulation, tracking, wildlife_behavior, wms | **COQUILLES VIDES** |
| **phase-g/** (13 sous-dossiers, 3 fichiers) | api-bridge, behavioral, contracts, core, data, docs, environmental, marketplace, overlays, predictive, recommendations, scoring, tests | **SQUELETTE MASSIF — 13 dossiers pour 3 fichiers** |

### 1.4 frontend/src/ — Autres dossiers

| Dossier | Fichiers | Role | Statut |
|---|---|---|---|
| hooks/ | 15 JS | Hooks React (useSpatialClipping, useZoneCache, etc.) | ACTIF |
| services/ | 6 JS | BionicZoneService, TripService, WaypointScoring, etc. | ACTIF |
| contexts/ | 2 JSX | LanguageContext, PopupContext | ACTIF |
| config/ | 8 JS | bionic-colors, bionic-config, routes, modules, etc. | ACTIF |
| utils/ | 10 JS | Performance, CDN, SSR, caching, web vitals | ACTIF |
| lib/ | 1 JS | utils.js (Shadcn utility) | ACTIF |
| i18n/ | 1 JS + locales/ | Internationalization | ACTIF |
| styles/ | 1 CSS | bionic-design-system.css | ACTIF |
| data_layers/ | 5 sous-dossiers | advanced_geospatial, behavioral, ecoforestry, layers_3d, simulation | ACTIF |
| design-system/ | 6 JSX + 2 index | BionicButton, BionicCard, BionicNavigation, theme | **2 IMPORTS SEULEMENT** |
| pages/ | 27 JSX | Toutes les pages (MonTerritoireBionic, Admin, Shop, etc.) | ACTIF |
| layouts/ | 1 JSX | MainLayout | ACTIF |

### 1.5 frontend/public/

| Fichier/Dossier | Type | Statut |
|---|---|---|
| index.html, manifest.json, robots.txt, sitemap.xml | Config | ACTIF |
| offline.html | PWA fallback | ACTIF |
| bionic-logo-3d.png (1.8 MB) | Logo | **DOUBLON (voir logos/)** |
| logos/ (12 fichiers, 7.3 MB) | Logos multi-format | **SURDIMENSIONNE** |
| logos/custom/ | **VIDE** | PARASITE |
| images/products/ | Images produits | ACTIF |
| reports/ (3 fichiers MD) | Rapports V5 | ARCHIVE |
| V5_ULTIME_FUSION_COMPLETE.json | Doc V5 | ARCHIVE |
| canvas_donnees_terrain_bionic_v5.md | Doc V5 | ARCHIVE |
| **sw.js** (15 KB) | Service Worker v4 | **DOUBLON** |
| **sw-v2.js** (12 KB) | Service Worker v2 Branche 3 | **DOUBLON** |
| **sw-push.js** (3 KB) | SW push notifications | SEMI-ACTIF |
| **service-worker.js** (8 KB) | SW Branche 1 | **DOUBLON** |

### 1.6 /app/ — Dossiers racine

| Dossier | Fichiers | Statut |
|---|---|---|
| .emergent/ (emergent.yml, summary.txt) | 2 | SYSTEME — NE PAS TOUCHER |
| architecture/ | 7 | Documentation architecture | ARCHIVE |
| backup/ (logos-original-phase-b) | 4 | Backup logos originaux | ARCHIVE |
| **backups/** | **0** | **VIDE — PARASITE** |
| contracts/ | 2 JSON | Contrats API | ARCHIVE |
| docs/reports/ | 155 fichiers | Rapports generes | ARCHIVE (a nettoyer) |
| logs/ | 2 | Logs divers | TRANSITOIRE |
| memory/ (PRD.md) | 1 | Memoire agent | SYSTEME |
| **sources/** (HUNTIQ-BASE/V2/V3/V4) | **2091 fichiers, 74 MB** | **ARCHIVES COMPLETES DES VERSIONS PRECEDENTES** |
| test_reports/ | Variable | Rapports de tests | TRANSITOIRE |
| tests/ | 1 | Tests racine | ACTIF |
| tools/lighthouse/ | 3 | Outils perf | ARCHIVE |

---

## SECTION 2 — DOUBLONS DETECTES

### 2.1 Doublons de fichiers (hash identique)

| Fichier 1 | Fichier 2 | Type |
|---|---|---|
| `core/hooks/useToast.js` | `hooks/use-toast.js` | **DOUBLON EXACT** |

### 2.2 Dossiers dupliques (meme concept, noms differents)

| Dossier A | Dossier B | Diagnostic |
|---|---|---|
| **components/territoire/** (27 fichiers, ACTIF) | **components/territory/** (13 fichiers, LEGACY) | **DOUBLON CONCEPTUEL** — territoire = V5 officiel, territory = ancien |
| **components/map/** (3 fichiers) | **components/maps/** (3 fichiers) | **DOUBLON** — map = popup, maps = overlays avances |
| **components/charts/** (2 fichiers) | **components/bionic/charts/** (3 fichiers) | Chevauchement — deux sources de graphiques |
| **modules/master_switch/** | **modules/global_master_switch/** | **DOUBLON BACKEND** — 512 vs 508 lignes, logique similaire |

### 2.3 Fichiers backend dupliques/suspects

| Fichier | Lignes | Diagnostic |
|---|---|---|
| `territory.py` | 3 324 | **DOUBLON** avec `territories.py` (1 597 lignes) — chevauchement fonctionnel |
| `email_notifications.py` | 642 | **DOUBLON** avec `email_service.py` (274 lignes) |
| **`server_monolith_backup.py`** | **4 687** | **BACKUP EXPLICITE** — version monolithique historique |
| `hydrography_router.py` + `hydrography_service.py` | Backend racine | Possiblement remplace par `bionic_engine_p0/routers/terrain_data_router.py` |

### 2.4 Service Workers (4 versions concurrentes)

| Fichier | Taille | Version | Diagnostic |
|---|---|---|---|
| sw.js | 15 KB | v4 (CACHE_NAME: bionic-hunt-cache-v4) | **Principal** |
| sw-v2.js | 12 KB | Branche 3 (99% -> 99.9%) | **DOUBLON** |
| service-worker.js | 8 KB | Branche 1 POLISH FINAL | **DOUBLON** |
| sw-push.js | 3 KB | Notifications push | Potentiellement actif |

### 2.5 Logos (13 fichiers, 7.3+ MB)

| Logo | Formats | Taille | Diagnostic |
|---|---|---|---|
| bionic-logo-main | .avif (18 KB) + .png (1.8 MB) + .webp (29 KB) | 1.85 MB | **PNG surdimensionne** |
| bionic-logo-official | .avif + .png + .webp | 1.85 MB | **Identique a main? (meme taille PNG)** |
| logo-bionic-hunt-en | .avif + .png + .webp | 1.85 MB | PNG surdimensionne |
| logo-chasse-bionic-fr | .avif + .png + .webp | 1.85 MB | PNG surdimensionne |
| bionic-logo-3d.png (racine public/) | 1.8 MB | **DOUBLON potentiel** avec logos/ |
| logos/custom/ | **VIDE** | 0 | PARASITE |

---

## SECTION 3 — PARASITES ET FICHIERS OBSOLETES

### 3.1 Dossiers vides ou coquilles

| Chemin | Fichiers | Recommandation |
|---|---|---|
| `components/social/` | 0 | **SUPPRIMER** |
| `ui/core/` | 0 | **SUPPRIMER** |
| `ui/metier/` | 0 | **SUPPRIMER** |
| `logos/custom/` | 0 | **SUPPRIMER** |
| `/app/backups/` | 0 | **SUPPRIMER** |
| `modules/phase-g/` (13 sous-dossiers) | 3 fichiers | **SUPPRIMER** (squelette inutile) |

### 3.2 Modules squelettes (index.js seul ou presque)

16 modules frontend ne contiennent que 1-2 fichiers (souvent juste un index.js vide) :
`adaptive_strategy, advanced_geospatial, business, dashboard, engine_3d, formations, geospatial, keyboard, planmaitre, plugins, progression, simulation, tracking, wildlife_behavior, wms`

### 3.3 Archives volumineuses

| Chemin | Taille | Recommandation |
|---|---|---|
| `/app/sources/` (HUNTIQ-BASE/V2/V3/V4) | **74 MB, 2091 fichiers** | **ARCHIVER hors depot ou supprimer** |
| `/app/docs/reports/` | 155 fichiers | **Garder les 5 derniers, archiver le reste** |
| `/app/backup/logos-original-phase-b/` | 4 fichiers | ARCHIVER |
| `public/reports/` | 3 fichiers MD | ARCHIVER (reference V5) |

### 3.4 Fichiers backup explicites

| Fichier | Recommandation |
|---|---|
| `server_monolith_backup.py` (4 687 lignes) | **SUPPRIMER** (historique, pas de valeur) |
| `components/BackupManager.jsx` | Verifier si utilise |

---

## SECTION 4 — ANALYSE VISUELLE

### 4.1 Couleurs (Top 20 par frequence d'utilisation)

| # | Couleur | Occurrences | Utilisation |
|---|---|---|---|
| 1 | `#f5a623` / `#F5A623` | **2 355** | Couleur primaire BIONIC (or/ambre) |
| 2 | `#1a1a2e` | 157 | Background sombre principal |
| 3 | `#0a0a15` | 110 | Background sombre profond |
| 4 | `#0f0f1a` | 89 | Background sombre intermediaire |
| 5 | `#0d0d1a` | 79 | Background sombre variante |
| 6 | `#ef4444` | 59 | Rouge erreur/alerte |
| 7 | `#d4891c` | 56 | Or secondaire |
| 8 | `#22c55e` | 55 | Vert succes/alimentation |
| 9 | `#3b82f6` | 48 | Bleu info/hydro |
| 10 | `#050510` | 45 | Noir quasi-absolu |
| 11 | `#10b981` | 41 | Vert emeraude/habitat |
| 12 | `#f59e0b` | 32 | Ambre alerte |
| 13 | `#8b5cf6` | 22 | Violet repos |
| 14 | `#FF9800` | 19 | Orange routes |
| 15 | `#64748b` | 18 | Gris ardoise |

**PROBLEME :** 5 variantes de noir/dark background (`#1a1a2e`, `#0a0a15`, `#0f0f1a`, `#0d0d1a`, `#050510`, `#0d0d14`, `#0a0a0a`, `#111118`, `#0d1117`) — 9 variations au lieu d'une palette unifiee.

### 4.2 Sources multiples de palettes (6 sources)

| Source | Lignes couleur | Role |
|---|---|---|
| `config/bionic-colors.js` | 33 | **Source officielle frontend** |
| `config/bionic-config.js` | 35 | Couleurs par module |
| `data_layers/` (5 fichiers) | 19 | Couleurs par couche de donnees |
| `zone_visual_layer_v2.py` (backend) | 18 | **Source officielle backend** |
| `BionicMicroZones.jsx` | 21 | Couleurs inline dans le composant |
| `StructureContrastLayer.jsx` | 14 | Palette Anthropique V5 inline |

**PROBLEME :** Les couleurs sont definies a **6 endroits differents** au lieu d'une source unique.

### 4.3 Opacites (dispersees)

| Valeur | Occurrences | Contexte typique |
|---|---|---|
| opacity: 0 | 48 | Elements caches (HYDRO FIX) |
| opacity: 1 | 52 | Elements visibles |
| opacity: 0.5 | 16 | Semi-transparents |
| opacity: 0.6 | 12 | Overlays |
| opacity: 0.8 | 8 | Quasi-opaques |
| opacity: 0.7 | 6 | Overlays secondaires |
| opacity: 0.85 | 3 | Anthropique V5 |

**PROBLEME :** Opacites definies inline dans chaque composant, pas de constantes centralisees.

### 4.4 Z-Index (disperses)

| Z-Index | Occurrences | Contexte |
|---|---|---|
| 99999 | 1 | **ABERRANT** — a verifier |
| 10000 | 2 | Modals/overlays critiques |
| 1300 | 1 | Layer superieur |
| 1200 | 3 | Modals |
| 1100 | 4 | Popovers |
| 1000 | 6 | Navigation/toolbar |
| 400-460 | 8 | Layers carte BIONIC |
| 50-100 | 3 | Elements de base |

**PROBLEME :** z-index=99999 est un anti-pattern. Pas de schema global documente (seulement dans `layer_dump.json` du FREEZE).

---

## SECTION 5 — ANALYSE DES COMPOSANTS

### 5.1 Composants carte (COEUR BIONIC)

| Composant | Fichier | Lignes | Role | Statut |
|---|---|---|---|---|
| MonTerritoireBionicPage | pages/ | **1 759** | Page principale carte | **MONOLITHE CRITIQUE** |
| TerritoryMap | components/ | **5 117** | Carte territoire complete | **MONOLITHE** |
| CarteBionic | bionic/ | 1 163 | Carte BIONIC ancienne | LEGACY |
| BionicMicroZones | territoire/ | ~300 | Zones BIONIC | GELE V5 |
| ExclusionOverlayLayer | territoire/ | 152 | Overlays exclusion | GELE V5 |
| StructureContrastLayer | territoire/ | 229 | Anthropique V5 | GELE V5 |
| EcoforestryLayers | territoire/ | 1 245 | Couches ecoforesterie | ACTIF |
| HydrographyOverlayLayer | territoire/ | 108 | WMS hydro | GELE V5 |
| MovementCorridorsLayer | territoire/ | ~200 | Corridors fauniques | ACTIF |
| WindFlowLayer | territoire/ | ~150 | Flux de vent | ACTIF |
| CursorBionicLayer | territoire/ | ~100 | Curseur intelligent | ACTIF |
| TerritoryShell | territoire/ | ~150 | Contour territoire | GELE V5 |
| NdviOverlayLayer | territoire/ | ~200 | NDVI raster | ACTIF |

### 5.2 Composants UI avec chevauchement

| Concept | Source 1 | Source 2 | Source 3 |
|---|---|---|---|
| **Bouton** | `components/core/CoreButton.jsx` | `design-system/BionicButton.jsx` | `components/ui/button.jsx` (Shadcn) |
| **Carte (Card)** | `components/core/CoreCard.jsx` | `design-system/BionicCard.jsx` | `components/ui/card.jsx` (Shadcn) |
| **Navigation** | `components/core/CoreNavigation.jsx` | `design-system/BionicNavigation.jsx` | `components/navigation/ModularNavigation.jsx` |
| **Layout** | `components/core/CoreLayout.jsx` | `layouts/MainLayout.jsx` | — |
| **Loader** | `components/core/CoreLoader.jsx` | — | — |
| **Modal** | `components/core/CoreModal.jsx` | `components/ui/dialog.jsx` (Shadcn) | — |
| **Toast** | `core/hooks/useToast.js` | `hooks/use-toast.js` (doublon exact) | `components/ui/sonner.tsx` (Shadcn) |

**PROBLEME MAJEUR :** Triple source de composants de base (core/ + design-system/ + Shadcn/ui/).
`components/core/` a **0 imports** — entierement orphelin.

### 5.3 Fichiers monolithes (>1000 lignes)

| Fichier | Lignes | Diagnostic |
|---|---|---|
| TerritoryMap.jsx | 5 117 | **MONOLITHE CRITIQUE** |
| LanguageContext.jsx | 3 032 | **TROP GROS pour un contexte** |
| LandsRental.jsx | 1 951 | Gros composant |
| MonTerritoireBionicPage.jsx | 1 759 | **INTERDIT de refactoring par COPILOT MAITRE** |
| NetworkingHub.jsx | 1 539 | Gros composant |
| HuntMarketplace.jsx | 1 462 | Gros composant |
| PartnershipAdmin.jsx | 1 306 | Gros composant |
| EcoforestryLayers.jsx | 1 245 | Couches ecoforesterie |
| ProductDiscoveryAdmin.jsx | 1 197 | Admin produits |
| CarteBionic.jsx | 1 163 | Carte legacy |
| AdminPage.jsx | 1 125 | Page admin monolithique |
| BionicAnalyzer.jsx | 1 092 | Analyse bionic |
| TerritoryAdvanced.jsx | 1 047 | Territoire avance |
| WaypointMap.jsx | 1 013 | Carte waypoints |
| AdminSEO.jsx | 953 | Admin SEO |

---

## SECTION 6 — RECOMMANDATIONS

### A SUPPRIMER (Parasites + vides)

| Element | Raison |
|---|---|
| `components/social/` | Dossier vide |
| `ui/core/` | Dossier vide |
| `ui/metier/` | Dossier vide |
| `logos/custom/` | Dossier vide |
| `/app/backups/` | Dossier vide |
| `server_monolith_backup.py` | Backup explicite, 4 687 lignes mortes |
| `core/hooks/useToast.js` | Doublon exact de `hooks/use-toast.js` |
| `modules/phase-g/` (sauf contracts/) | 13 dossiers vides pour 3 fichiers |
| 16 modules squelettes | Seulement un index.js vide chacun |

### A ARCHIVER (hors depot ou branche archive)

| Element | Taille | Raison |
|---|---|---|
| `/app/sources/` (HUNTIQ-BASE/V2/V3/V4) | **74 MB** | Anciennes versions completes |
| `/app/docs/reports/` (150+ fichiers) | ~10 MB | Garder les 5 derniers |
| `public/reports/` | 39 KB | Documentation V5 historique |
| `public/V5_ULTIME_FUSION_COMPLETE.json` | 11 KB | Archive V5 |
| `public/canvas_donnees_terrain_bionic_v5.md` | 11 KB | Archive V5 |
| `/app/backup/` | ~4 fichiers | Logos originaux Phase B |

### A FUSIONNER

| Elements | Cible unique recommandee |
|---|---|
| `territory.py` + `territories.py` | Un seul fichier `territory_service.py` |
| `email_notifications.py` + `email_service.py` | Un seul `email_engine.py` |
| `master_switch/` + `global_master_switch/` | Un seul module switch |
| `components/core/` + `design-system/` | **SUPPRIMER les deux**, utiliser Shadcn/ui exclusivement |
| `sw.js` + `sw-v2.js` + `service-worker.js` | Un seul `sw.js` |
| `components/map/` + `components/maps/` | Fusionner en `components/map/` |
| 6 sources de couleurs | Centraliser dans `config/bionic-colors.js` + backend `zone_visual_layer_v2.py` |

### A GARDER (Sources officielles)

| Element | Role | Statut |
|---|---|---|
| `components/territoire/` (27 fichiers) | Composants carte BIONIC V5 | **SOURCE OFFICIELLE GELEE** |
| `components/ui/` (Shadcn) | Composants UI de base | **SOURCE OFFICIELLE** |
| `config/bionic-colors.js` | Palette couleurs frontend | **SOURCE OFFICIELLE** |
| `backend/modules/bionic_engine_p0/` | Moteur BIONIC V5 | **SOURCE OFFICIELLE GELEE** |
| `backend/data/freeze_baseline/` | Snapshots V5 FREEZE | **INTOUCHABLE** |
| `backend/tests/freeze/` | Tests non-regression 28/28 | **INTOUCHABLE** |
| `pages/MonTerritoireBionicPage.jsx` | Page carte principale | **INTERDIT de refactoring** |

---

## SECTION 7 — RESUME EXECUTIF

### Sante du depot

| Indicateur | Evaluation |
|---|---|
| Architecture BIONIC (bionic_engine_p0) | **EXCELLENT** — gele, teste, documente |
| Composants carte (territoire/) | **EXCELLENT** — 27 fichiers bien structures |
| Organisation globale | **MEDIOCRE** — doublons, parasites, archives melangees |
| Coherence des couleurs | **FAIBLE** — 6 sources differentes, 9 variantes de noir |
| Coherence des composants UI | **FAIBLE** — triple source (core/design-system/Shadcn) |
| Poids du depot | **EXCESSIF** — 74 MB d'archives dans /sources/ |
| Service Workers | **CONFUS** — 4 versions concurrentes |
| Modules frontend | **GONFLE** — 16 modules squelettes sans contenu |

### Chiffres cles doublons/parasites

| Type | Nombre |
|---|---|
| Dossiers vides | 6 |
| Modules squelettes (1-2 fichiers) | 16 |
| Fichiers backup/obsoletes identifies | 5 |
| Doublons exacts | 1 (useToast) |
| Doublons conceptuels (dossiers) | 4 paires |
| Sources multiples de couleurs | 6 |
| Service Workers concurrents | 4 |
| Variantes de fond sombre | 9 |
| Logos PNG surdimensionnes (1.8 MB chacun) | 5 |

### Gain potentiel nettoyage

| Action | Gain estime |
|---|---|
| Supprimer /app/sources/ | **-74 MB** |
| Supprimer parasites/vides | -100+ fichiers |
| Fusionner doublons | -10 fichiers, +coherence |
| Optimiser logos PNG -> WebP seul | **-7 MB** |
| Supprimer SW redondants | -3 fichiers |
| Purge docs/reports/ (garder 5) | -150 fichiers |
| **Total estime** | **~85 MB et ~280 fichiers** |

---

**FIN DU RAPPORT — Aucun fichier modifie.**
