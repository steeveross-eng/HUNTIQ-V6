# RAPPORT SUPRA STRICT — BIONIC V5 300%
## Diagnostic Complet de la Base Modulaire

**Version:** 1.0.0
**Date:** 2026-03-04
**Standard:** BIONIC_V5_300_STRICT
**Auteur:** Agent Technique Emergent

---

## TABLE DES MATIERES

1. [Cartographie Complete de l'Architecture](#1-cartographie-complete)
2. [Architecture Interne Detaillee](#2-architecture-interne)
3. [Logique Scientifique des Zones/Couches/Hotspots](#3-logique-scientifique)
4. [Comparatif V5 vs V5 300%](#4-comparatif)
5. [Analyse des Derives Observees](#5-derives)
6. [Diagnostic Service Worker / Cache](#6-service-worker)
7. [Barre d'Outils — Validation Complete](#7-toolbar)
8. [Pipeline de Donnees — Logs Complets](#8-pipeline-logs)

---

## 1. CARTOGRAPHIE COMPLETE DE L'ARCHITECTURE {#1-cartographie-complete}

### 1.1 Arbre de Fichiers Critique

```
/app/
  frontend/
    src/
      pages/
        MonTerritoireBionicPage.jsx        # PAGE PRINCIPALE (2074 lignes)
      hooks/
        useZoneOrchestrator.js             # ORCHESTRATEUR (190 lignes)
        useZonePreview.js                  # PREVIEW SCIENTIFIQUE V2 (472 lignes)
        useZoneCache.js                    # CACHE IndexedDB (108 lignes)
        useBionicLayers.js                 # TOGGLES DE COUCHES
        useBionicWeather.js                # DONNEES METEO
        useBionicScoring.js                # SCORING GLOBAL
        useSpatialClipping.js              # CLIPPING 1km x 1km
        useUserData.js                     # WAYPOINTS + LIEUX (backend sync)
        useMapType.js                      # SELECTION FOND DE CARTE
      services/
        BionicZoneService.js               # SERVICE BACKEND ZONES (187 lignes)
      components/territoire/
        MonTerritoireToolbar.jsx            # BARRE D'OUTILS (501 lignes)
        BionicMicroZones.jsx               # RENDU ZONES V5 300% (338 lignes)
        TerritoryShell.jsx                 # ENVELOPPE VERTE
        StructureContrastLayer.jsx         # ZONES ANTHROPIQUES
        ExclusionOverlayLayer.jsx          # ZONES EXCLUES
        MovementCorridorsLayer.jsx         # CORRIDORS V1
        CursorBionicLayer.jsx              # SCORE VISUEL CURSEUR
        EcoforestryLayers.jsx              # COUCHES ECOFORESTIERES
        DiagnosticExclusionsPanel.jsx      # PANNEAU EXCLUSIONS
        ZoneFavorites.jsx                  # FAVORIS + ALERTES
        WaypointUnifiedPanel.jsx           # PANNEAU WAYPOINT
        ZoneInfoPanel.jsx                  # INFO ZONE
      config/
        bionic-colors.js                   # PALETTE COULEURS
        bionic-config.js                   # CONFIGURATION BIONIC
        bionic-icons.js                    # ICONES
        mapSources.js                      # SOURCES DE CARTES
      serviceWorkerRegistration.js         # ENREGISTREMENT SW V5
    public/
      sw-v2.js                             # SERVICE WORKER V5.0.0
  backend/
    modules/bionic_engine_p0/
      routers/
        organic_zones_router.py            # API ZONES ORGANIQUES
      services/
        bionic_service.py                  # SERVICE CALCUL ZONES
    routes/
      bionic_engine_router.py              # API BIONIC ENGINE
```

### 1.2 Flux de Donnees Global

```
[UTILISATEUR]
     |
     v
[MonTerritoireBionicPage.jsx]
     |
     +-- [useUserData] --> /api/user-data/waypoints/{userId}
     |     (Charge waypoints + lieux depuis backend)
     |
     +-- [Auto-Selection] --> Selectionne premier waypoint actif
     |
     +-- [useZoneOrchestrator] --> PIPELINE 3 ETAPES
     |     |
     |     +-- ETAPE 1: [useZoneCache] --> IndexedDB
     |     |   (Cache hit? Affichage instantane, source='cache')
     |     |
     |     +-- ETAPE 2: [useZonePreview] --> Client-side
     |     |   (Si cache miss: preview scientifique <200ms, source='preview')
     |     |
     |     +-- ETAPE 3: [BionicZoneService] --> /api/v1/bionic/organic-zones
     |         (Backend complet ~14s, source='backend')
     |         (Remplace preview/cache si zones > 0)
     |         (Sauvegarde en IndexedDB pour prochaine visite)
     |
     +-- [useSpatialClipping] --> Clipping 1km x 1km autour du waypoint
     |
     +-- [Classification Toggles] --> Filtrage RENDU UNIQUEMENT
     |     (Les zones restent figees en memoire)
     |
     +-- [BionicMicroZones] --> RENDU LEAFLET
           (Polygones avec contours uniques, centres transparents)
```

---

## 2. ARCHITECTURE INTERNE DETAILLEE {#2-architecture-interne}

### 2.1 useZoneOrchestrator.js — Module ORCHESTRATION

**Fichier:** `/app/frontend/src/hooks/useZoneOrchestrator.js`
**Lignes:** 190
**Role:** Machine d'etat qui coordonne les 3 modules isoles

**Contrat:**
- **Input:** `selectedWaypointForZones`, `activeWaypoints`, `selectedSpecies`, `currentZoom`
- **Output:** `{ zonesData, isLoading, isPreview, zoneSource, reload, cacheKey }`

**Etats possibles (zoneSource):**
| Etat | Signification | Condition |
|------|--------------|-----------|
| `'none'` | Aucun waypoint selectionne | `cacheKey === null` |
| `'cache'` | Zones chargees depuis IndexedDB | Cache hit avec zones > 0 |
| `'preview'` | Apercu scientifique client | Cache miss, preview genere |
| `'backend'` | Zones organiques du serveur | Backend a retourne zones > 0 |

**Mecanismes de protection:**
1. **Cle de cache deterministe:** `{species}_wp_{lat}_{lng}` (4 decimales)
2. **State Locking:** Si `lockRef.locked && key === cacheKey && source === 'backend'` → pas de recalcul
3. **Stale Closure Guard:** `zoneSourceRef` (useRef) en miroir de `zoneSource` (useState) pour acces synchrone dans les handlers async
4. **Cancelled flag:** `let cancelled = false` avec cleanup dans le return du useEffect
5. **Cache guard:** Un cache avec 0 zones est traite comme un cache miss (pas de stockage de resultats vides)

**Flux detaille:**
```
useEffect([cacheKey, forceReload])
  |
  +-- cacheKey null? → reset zones, return
  |
  +-- State locked pour cette cle? → return (pas de recalcul)
  |
  +-- orchestrate() async:
       |
       +-- getCached(cacheKey) → IndexedDB lookup
       |   Si zones > 0: setZonesData, setZoneSource('cache'), lock
       |
       +-- Si cache miss: generatePreview(wp, LAYER_TYPES)
       |   Si zones > 0: setZonesData, setZoneSource('preview')
       |
       +-- generateWaypointZonesV5(wp, zoom, layers, species)
       |   Si zones > 0: setZonesData, setZoneSource('backend'), lock, setCached
       |   Si zones = 0 ET source = 'none': etat vide
       |   Si zones = 0 ET source != 'none': preview/cache preserve
       |
       +-- catch: si source = 'none' → etat vide
                  si source != 'none' → preserve preview/cache
```

### 2.2 useZonePreview.js — MOTEUR DE PREVIEW SCIENTIFIQUE V2

**Fichier:** `/app/frontend/src/hooks/useZonePreview.js`
**Lignes:** 472
**Role:** Generation de geometries organiques cote client en <200ms

**Algorithme:**
1. **PRNG deterministe (Mulberry32):** Memes coordonnees → memes zones
2. **5 morphologies distinctes:**
   | Morphologie | Forme | Couches associees |
   |------------|-------|-------------------|
   | `blob` | Amorphe irreguliere | habitats, alimentation, orientation, ndvi |
   | `elongated` | Ellipse orientee | rut, trajets, pentes |
   | `compact` | Arrondie petite | repos, salines, affuts |
   | `sinuous` | Ondulation naturelle | corridors, hydro, altitude |
   | `patch` | Parcelle a lobes | peuplements, ensoleillement |
3. **Subdivision Chaikin:** 2 iterations → 40-80+ vertices par zone (formes lisses)
4. **Placement radial deterministe:** Distance et angle bases sur le waypoint
5. **15 couches configurees:** Chacune a un `count`, `distMin/Max`, `radiusM/lengthM/widthM`, `score[]`

**Configuration scientifique par couche (extrait):**
| Couche | Morphologie | Count | Dist (m) | Taille (m) | Score |
|--------|------------|-------|----------|------------|-------|
| habitats | blob | 2 | 60-280 | R:100-180 | 40-65 |
| rut | elongated | 1 | 100-350 | L:180-280 W:80-140 | 35-55 |
| repos | compact | 2 | 30-200 | R:50-100 | 40-65 |
| corridors | sinuous | 1 | 60-300 | L:300-500 W:50-90 | 30-50 |
| hydro | sinuous | 1 | 100-450 | L:250-400 W:40-80 | 30-50 |

### 2.3 useZoneCache.js — CACHE PERSISTANT IndexedDB

**Fichier:** `/app/frontend/src/hooks/useZoneCache.js`
**Lignes:** 108
**Role:** Persistance des zones calculees entre sessions

**Implementation:**
- **Base IndexedDB:** `bionic_zone_cache`, version 1, store `zones`
- **Double couche:** Memoire (Map in-memory, instantane) + IndexedDB (<100ms)
- **Eviction:** Maximum 50 entrees, suppression FIFO des anciennes
- **Pas de TTL:** Le cache ne s'expire jamais (invalidation manuelle via `reload()`)

**Operations:**
| Methode | Temps | Description |
|---------|-------|-------------|
| `getCached(key)` | <1ms (memoire) ou <100ms (IDB) | Lecture double couche |
| `setCached(key, data)` | Async | Ecriture memoire + IDB |
| `invalidate(key)` | Async | Suppression memoire + IDB |

### 2.4 BionicZoneService.js — SERVICE BACKEND

**Fichier:** `/app/frontend/src/services/BionicZoneService.js`
**Lignes:** 187
**Role:** Interface unique vers l'API backend de zones

**Endpoint:** `POST /api/v1/bionic/organic-zones`

**Payload:**
```json
{
  "bounds": { "north": 47.41, "south": 47.39, "east": -70.69, "west": -70.71 },
  "species": "moose",
  "layers": ["habitats", "rut", "repos", "alimentation", "corridors"],
  "resolution": 80,
  "max_zones_per_layer": 8,
  "include_scoring": true
}
```

**Reponse (GeoJSON FeatureCollection):**
```json
{
  "type": "FeatureCollection",
  "features": [ ... ],  // 7-15 zones typiques
  "stats": {
    "layers_processed": 5,
    "total_zones": 7,
    "rejected_exclusion": 2,
    "exclusions_count": 8,
    "penalties_applied": 7,
    "computation_time_ms": 14175.6,
    "species": "moose"
  }
}
```

**Pipeline backend:**
1. Rasterisation de la zone (grille 50-100m)
2. Calcul des scores par pixel (OSM, DEM, hydrographie)
3. Marching Squares → polygones
4. Subdivision Chaikin → formes organiques
5. Exclusions Overpass (routes, batiments, eau permanente)
6. Scoring avec penalites

**15 couches structurelles:**
`habitats`, `rut`, `repos`, `alimentation`, `corridors`, `salines`, `affuts`, `trajets`, `peuplements`, `hydro`, `pentes`, `orientation`, `ensoleillement`, `altitude`, `ndvi`

---

## 3. LOGIQUE SCIENTIFIQUE DES ZONES/COUCHES/HOTSPOTS {#3-logique-scientifique}

### 3.1 Hierarchie Visuelle a 5 Couches

Le rendu carte utilise une hierarchie stricte de 5 couches empilees :

| # | Couche | Composant | Description | Z-Index |
|---|--------|-----------|-------------|---------|
| 0 | Exclusion Overlay | `ExclusionOverlayLayer` | Zones exclues (routes, batiments) semi-transparentes | Bas |
| 1 | Territory Shell | `TerritoryShell` | Enveloppe verte (#3CB371) englobant toutes les zones | - |
| 2 | Structure Contrast | `StructureContrastLayer` | Zones anthropiques (#A9A9A9, 20%) | - |
| 3 | Behavior Cells | `BionicMicroZones` (cells) | Zones comportementales (turquoise/violet) | - |
| 4 | Core Nodes | `BionicMicroZones` (nodes) | Noyaux strategiques (haute priorite) | Haut |

### 3.2 Classification des Zones

**Tier "behavior.cells":**
- Couches: `rut`, `repos`, `alimentation`, `corridors`
- Rendu: En arriere-plan, score < 80

**Tier "core.nodes":**
- Couches: `habitats`, `salines`, `affuts`, `trajets`
- OU: score >= 80 ET surface < 15000 m2
- Rendu: Au-dessus des cells

### 3.3 Normalisation Visuelle V5 300%

**Regles strictes:**
- Centre transparent: `fillOpacity <= 0.10` (0.08 normal, 0.15 au survol)
- Contour 100% opacite
- Couleur UNIQUE par zone (angle d'or 137.508 degres pour separation maximale)
- Epaisseur dynamique: score 30% → 1.5px, score 100% → 5.5px
- Aucun remplissage opaque

**Generation de couleur:**
```
Hue de base par type (habitats=130, rut=30, repos=215, etc.)
+ Decalage par index: (zoneIndex * 37) % 40 - 20 (variation +-20 degres)
→ HSL(hue, 80%, 58%)
```

### 3.4 Spatial Clipping 1km x 1km

Quand un waypoint est selectionne :
1. `useSpatialClipping` calcule un bbox de 1km x 1km centre sur le waypoint
2. `clipZonesClient()` filtre les zones pour ne garder que celles dans le bbox
3. Le rectangle pointille orange est affiche sur la carte

### 3.5 Classification Toggles (RENDU UNIQUEMENT)

12 toggles regroupes en 4 familles. **CRITIQUE**: Les toggles n'agissent que sur la VISIBILITE, pas sur le calcul. Les zones restent figees en memoire.

| Famille | Toggles | Type |
|---------|---------|------|
| STRUCTURE | relief, hydro, foret, anthropique | Statique |
| FONCTIONNEL | dominantes, corridorsReels | Semi-statique |
| CONDITIONS | meteo, pression, corridorsEstimes | Dynamique |
| INSTANTANE | scoreHabitat, curseurBionic, waypoints | Temps reel |

---

## 4. COMPARATIF V5 vs V5 300% {#4-comparatif}

### 4.1 Changements Architecturaux

| Aspect | V5 (avant) | V5 300% (actuel) |
|--------|-----------|------------------|
| **Orchestration** | Logique dispersee dans MonTerritoireBionicPage | Hook dedie `useZoneOrchestrator` |
| **Preview** | Cercles simples ou absent | 5 morphologies organiques (Chaikin) |
| **Cache** | `idb-keyval` library | IndexedDB natif avec eviction |
| **Service Worker** | v2/v3, pas de forced reload | v5.0.0 avec reload unique garanti |
| **State Locking** | Recalculs frequents | Verrou par cle, pas de recalcul inutile |
| **Spatial Clipping** | Pas de clipping | 1km x 1km strict autour du waypoint |
| **Classification** | Toggles recalculent | Toggles = RENDU uniquement |
| **Stale Closure** | Closures stale dans async | `zoneSourceRef` (useRef) synchrone |
| **Cache vide** | Stocke cache avec 0 zones | Cache miss si zones = 0 |

### 4.2 Corrections Appliquees (V5 300%)

1. **Auto-selection waypoint:** Le premier waypoint actif est auto-selectionne au chargement
2. **Indicateur "En attente":** Remplace "Organiques V5" trompeuse quand pas de donnees
3. **Cache garde:** Cache avec 0 zones = cache miss (pas de stockage vide)
4. **Stale Closure Guard:** `zoneSourceRef` evite les closures stale
5. **Preview V2:** 5 morphologies organiques au lieu de cercles
6. **React Keys:** IDs uniques par waypoint (plus de duplicatas)
7. **SW Reload Loop Fix (v5.0.0):** SessionStorage guard + mecanisme unique de reload

### 4.3 Regressions Connues

| Regression | Cause | Impact | Statut |
|-----------|-------|--------|--------|
| Service WMS MFFP 401 | Service externe | Couche ecoforestiere indisponible | EXTERNE (hors scope) |
| Boucle SW reload (v4.0.0) | Double mecanisme reload | Page en boucle infinie | CORRIGE (v5.0.0) |
| Zones 0 sans waypoint | Comportement normal | UX confuse | ATTENDU (design) |

---

## 5. ANALYSE DES DERIVES OBSERVEES {#5-derives}

### 5.1 Chronologie des Symptomes

| Phase | Symptome | Cause Diagnostiquee | Correction |
|-------|----------|-------------------|------------|
| 1 | "ZONES 0" au chargement | Pas d'auto-selection de waypoint | Auto-selection du 1er waypoint actif |
| 2 | Formes circulaires (blobs) | Preview V1 trop simple | Preview V2 avec 5 morphologies |
| 3 | "ZONES 0" persiste | Cache stockait resultats vides | Cache guard: 0 zones = miss |
| 4 | Agent OK, utilisateur KO | Boucle SW reload infinite | SW v5.0.0 avec sessionStorage guard |
| 5 | Erreurs 429 Rate Limit | Boucle SW cause rafales API | Corrige par fix SW |

### 5.2 Divergence Agent vs Utilisateur — Explication Technique

**Pourquoi l'agent voyait du succes et l'utilisateur voyait un echec:**

1. **Environnement de test de l'agent (Playwright):**
   - Navigateur EPHEMERE: pas de Service Worker pre-enregistre
   - Pas de cache IndexedDB persistant
   - Pas de `sessionStorage` residuel
   - Chaque test = session vierge
   - **Consequence:** Le code le plus recent est TOUJOURS execute

2. **Environnement de l'utilisateur (navigateur reel):**
   - Service Worker PERSISTANT: version ancienne active
   - Cache IndexedDB PERSISTANT: potentiellement des resultats vides stockes
   - Le SW v4.0.0 avait un double mecanisme de reload → boucle infinie
   - La page ne se stabilisait jamais → pipeline ne completait jamais
   - **Consequence:** Code ancien servi par le SW, boucle infinie

3. **Cause racine specifique:**
   - `index.js` ecoutait `SW_UPDATED` et faisait `window.location.reload()`
   - `serviceWorkerRegistration.js` ecoutait `controllerchange` et faisait `window.location.reload()`
   - Les DEUX se declenchaient a chaque chargement
   - Le flag `refreshing` ne protegeait que `controllerchange`, pas `SW_UPDATED`
   - → Boucle infinie de rechargement

### 5.3 Solution Appliquee

**SW v5.0.0 — Correction de la boucle de rechargement:**

1. **`index.js`:** Le listener `SW_UPDATED` ne fait PLUS de `window.location.reload()` — il log uniquement
2. **`serviceWorkerRegistration.js`:** Le listener `controllerchange` utilise desormais `sessionStorage` comme garde:
   ```javascript
   const reloadKey = `sw_reload_${SW_VERSION}`;
   if (sessionStorage.getItem(reloadKey)) return; // Deja recharge
   sessionStorage.setItem(reloadKey, Date.now());
   window.location.reload(); // Un seul reload par session
   ```
3. **`sw-v2.js`:** Version incrementee a 5.0.0, caches v5 pour invalidation complete

---

## 6. DIAGNOSTIC SERVICE WORKER / CACHE {#6-service-worker}

### 6.1 Architecture du Service Worker

**Fichier:** `/app/frontend/public/sw-v2.js`
**Version:** 5.0.0

**Strategies de caching:**
| Type | Strategie | TTL | Routes |
|------|-----------|-----|--------|
| API (cacheFirst) | Cache d'abord | 5 min | `/api/v1/species`, `/api/v1/config` |
| API (staleWhileRevalidate) | Cache + revalidation | 5 min | `/api/v1/products`, `/api/v1/lands` |
| API (networkFirst) | Reseau d'abord | 5 min | `/api/auth`, `/api/user`, `/api/v1/waypoint` |
| Assets JS/CSS | Reseau d'abord | 7 jours | `*.js`, `*.css` |
| Images | Cache d'abord | 30 jours | `*.png`, `*.jpg`, etc. |
| Fonts | Cache d'abord | 1 an | `*.woff2`, etc. |
| Pages HTML | Reseau d'abord + offline | 1 jour | `/`, routes SPA |

### 6.2 Cycle de Vie du SW

```
INSTALL:
  1. Precache assets critiques (index.html, manifest.json, logos)
  2. self.skipWaiting() → Prise de controle immediate

ACTIVATE:
  1. Suppression de TOUS les caches v4 et anterieurs
  2. self.clients.claim() → Controle de tous les onglets
  3. Notification passive SW_UPDATED aux clients (PAS de reload force)
  4. Prefetch des routes communes

FETCH:
  1. Skip non-GET et non-HTTP
  2. Route vers la strategie appropriee
  3. JS/CSS: networkFirst (code frais garanti)
  4. API: networkFirst avec fallback cache
```

### 6.3 Enregistrement et Mise a Jour

**Fichier:** `/app/frontend/src/serviceWorkerRegistration.js`

```
PAGE LOAD:
  1. Register SW (/sw-v2.js)
  2. Verification horaire des mises a jour
  3. Si mise a jour detectee:
     a. installingWorker.onstatechange = 'installed'
     b. Si controleur existant: SKIP_WAITING → SW prend le controle
     c. controllerchange → Un seul reload (sessionStorage guard)
```

### 6.4 Instructions de Depannage pour l'Utilisateur

**Si "ZONES 0" persiste apres cette mise a jour:**

1. **Ouvrir DevTools (F12) → Application → Service Workers**
   - Verifier que la version est `5.0.0`
   - Si version ancienne: cliquer "Update" puis "Unregister", puis recharger
   
2. **Vider le cache du navigateur:**
   - Chrome: `Ctrl+Shift+Delete` → Cocher "Images et fichiers en cache" → Supprimer
   - OU: DevTools → Application → Storage → Clear Site Data

3. **Hard Refresh:** `Ctrl+Shift+R` (ignore tous les caches)

4. **Verifier la console (F12):**
   - Chercher `[BIONIC V5 PIPELINE]` — doit montrer les 3 etapes
   - Chercher `[BIONIC V5 AUTO-SELECT]` — doit montrer le waypoint selectionne
   - Si `[SW v5] Nouveau Service Worker active — rechargement unique` → SW mis a jour

5. **Verifier le panneau ZONES:**
   - "Pipeline V3.1" doit etre visible
   - "Organiques V5" = zones du backend (succes)
   - "Preview" = zones du preview scientifique (en attente du backend)
   - "En attente" = aucun waypoint selectionne → CREER un waypoint

---

## 7. BARRE D'OUTILS — VALIDATION COMPLETE {#7-toolbar}

### 7.1 Architecture de la Barre d'Outils

**Fichier:** `/app/frontend/src/components/territoire/MonTerritoireToolbar.jsx`
**Position:** En ligne dans le header, visible uniquement quand `activeTab === 'carte'`
**Composant:** `<MonTerritoireToolbar />` — Popovers horizontaux

**CONFIRMATION: Il n'y a qu'UN SEUL systeme de barre d'outils actif. Aucun systeme parallele.**

### 7.2 Description de Chaque Outil

#### OUTIL 1: Fond de Carte (icone Map, couleur #f5a623)
| Attribut | Valeur |
|----------|--------|
| **Role** | Selection du type de fond de carte |
| **Module interne** | `useMapType` → `BionicMapSelector` |
| **Pipeline** | Aucun pipeline de donnees — changement visuel uniquement |
| **Dependances** | `mapSources.js` pour les configurations de tuiles |
| **Flags** | Aucun flag d'activation — toujours actif |
| **Options** | BIONIC Premium, Ecoforesterie, Satellite HD, IQHO, Bathymetrie, Routes forestieres, Topo avance |

#### OUTIL 2: Espece Cible (icone Binoculars, couleur #f59e0b)
| Attribut | Valeur |
|----------|--------|
| **Role** | Selection de l'espece pour le calcul des zones |
| **Module interne** | `selectedSpecies` (state) → `useZoneOrchestrator` |
| **Pipeline** | Changement d'espece → nouvelle cle de cache → recalcul pipeline complet |
| **Dependances** | `SPECIES_LIST` de `core/bionic/speciesConfig.js` |
| **Flags** | Aucun — toujours actif |
| **Impact** | Modifie les couches calculees (ex: orignal = hydro+salines, cerf = ensoleillement) |

#### OUTIL 3: Couches BIONIC (icone Layers, couleur #10b981, badge: nombre actif)
| Attribut | Valeur |
|----------|--------|
| **Role** | Activation/desactivation individuelle des 15 couches structurelles |
| **Module interne** | `useBionicLayers` → `layersVisible` (state) |
| **Pipeline** | Toggle → filtrage RENDU uniquement (pas de recalcul) |
| **Dependances** | `LAYER_TYPES` de `BionicZoneService.js` |
| **Flags** | Chaque couche a un toggle boolean |
| **Sous-element** | Toggle "Zones d'exclusion (overlay)" → `ExclusionOverlayLayer` |

#### OUTIL 4: Classification (icone Layers, couleur #14b8a6)
| Attribut | Valeur |
|----------|--------|
| **Role** | Activation/desactivation par FAMILLE de couches (4 groupes) |
| **Module interne** | `classificationToggles` (state local de MonTerritoireBionicPage) |
| **Pipeline** | Toggle → filtrage dans `bionicZones` useMemo (RENDU uniquement) |
| **Dependances** | `classificationToggles` + mapping couches→familles |
| **Flags** | 12 toggles regroupes en 4 familles |
| **IMPORTANT** | **NORME V5 300%**: Les toggles n'agissent que sur le rendu. Les zones structurelles restent figees en memoire. Aucun recalcul declenche. |

**Familles:**
- **Structure** (statique): relief, hydro, foret, anthropique
- **Fonctionnel** (semi-statique): dominantes, corridorsReels
- **Conditions** (dynamique): meteo, pression, corridorsEstimes
- **Instantane** (temps reel): scoreHabitat, curseurBionic, waypoints

#### OUTIL 5: Affichage Zones (icone Target, couleur #06b6d4, badge: zones visibles)
| Attribut | Valeur |
|----------|--------|
| **Role** | Controle de l'affichage des zones (seuil, corridors, temporel) |
| **Module interne** | Multiple states: `showCorridors`, `showCorridorsV1`, `temporalHourMT`, `minPercentageFilter`, `showCursorBionic` |
| **Pipeline** | Filtrage RENDU: `bionicZones.filter(z => z.score >= minPercentageFilter)` |
| **Dependances** | `MovementCorridorsLayer`, `CursorBionicLayer` |
| **Flags** | `showCorridors` (corridors estimes), `showCorridorsV1` (corridors reels), `showCursorBionic` |
| **Controles** | Seuil minimum (30-80%), Slider temporel (Auto/0h-23h) |

#### OUTIL 6: Facteurs Saisonniers (icone Activity, couleur #ec4899)
| Attribut | Valeur |
|----------|--------|
| **Role** | Affichage informatif des 4 facteurs saisonniers (Phase C) |
| **Module interne** | Aucun pipeline — informatif uniquement |
| **Pipeline** | Aucun — les facteurs sont integres dans le score backend |
| **Dependances** | Aucune dependance directe |
| **Flags** | Aucun toggle — affichage passif |
| **Facteurs** | C.1 Mise bas, C.2 Dispersion juvenile, C.3 Stress thermique, C.4 Pression de chasse |

#### OUTIL 7: Confidentialite (icone Lock/Unlock, couleur rouge/vert)
| Attribut | Valeur |
|----------|--------|
| **Role** | Masquer/afficher les donnees privees sur la carte |
| **Module interne** | `privacyMode` (state) → `isPrivateDataVisible` |
| **Pipeline** | Conditionne le rendu des Markers (waypoints, lieux) |
| **Dependances** | Aucune |
| **Flags** | `privacyMode` boolean |
| **Impact** | Si actif: waypoints et lieux invisibles sur la carte |

#### OUTIL 8: Statistiques (icone BarChart3, couleur #a855f7)
| Attribut | Valeur |
|----------|--------|
| **Role** | Affichage des metriques en temps reel |
| **Module interne** | Aucun pipeline — lecture seule |
| **Pipeline** | Aucun |
| **Dependances** | `visibleZonesCount`, `activeWaypointsCount`, `displayScore`, `currentZoom` |
| **Flags** | Aucun |
| **Metriques** | Zones visibles, Waypoints actifs, Score Global, Niveau Zoom |

### 7.3 Onglets de la Page (en dehors de la toolbar)

En plus de la toolbar (visible sur l'onglet "Carte"), la page a 5 onglets :

| Onglet | data-testid | Composant | Description |
|--------|-------------|-----------|-------------|
| Carte | `tab-carte` | MapContainer + toolbar | Carte BIONIC interactive |
| Waypoints | `tab-waypoints` | WaypointUnifiedPanel | Liste/gestion des waypoints |
| Lieux | `tab-lieux` | Dialog + liste | Lieux enregistres (ZEC, pourvoiries, etc.) |
| Groupe | `tab-groupe` | GroupeTab | Module collaboratif (tracking, chat, tir) |
| Diagnostic Exclusions | `tab-diagnostic-exclusions` | DiagnosticExclusionsPanel | Analyse des zones exclues |

### 7.4 Confirmation: Aucun Systeme Parallele

**Apres analyse complete du code:**

1. La toolbar est rendue par `<MonTerritoireToolbar />` UNIQUEMENT quand `activeTab === 'carte'`
2. Le pipeline de zones est gere par UN SEUL orchestrateur: `useZoneOrchestrator`
3. Le rendu des zones passe par UN SEUL composant: `<BionicMicroZones />`
4. Les couches supplementaires (ExclusionOverlay, TerritoryShell, StructureContrast, MovementCorridors) sont des overlays VISUELS, pas des systemes de calcul paralleles
5. Le scoring est UN SEUL hook: `useBionicScoring`
6. La meteo est UN SEUL hook: `useBionicWeather`

**VERDICT: Aucun systeme parallele n'est actif sur la carte. Un seul pipeline, un seul orchestrateur, un seul rendu.**

---

## 8. PIPELINE DE DONNEES — LOGS COMPLETS {#8-pipeline-logs}

### 8.1 Logs Console Attendus (Scenario Normal)

```
[BIONIC V5 AUTO-SELECT] Waypoint auto-selectionne: "Secteur Rural Quebec" (47.4, -70.7)
[BIONIC V5 PIPELINE] Demarrage — 1 waypoint(s), cle: tous_wp_47.4000_-70.7000
[BIONIC V5 PIPELINE] ETAPE 1 — Cache miss (vide ou inexistant)
[BIONIC V5 PIPELINE] ETAPE 2 — Preview: 17 zones en 45ms
[BIONIC V5 PIPELINE] ETAPE 3 — Calcul backend en cours...
[BIONIC V5 PIPELINE] ETAPE 3 — Backend: 13 zones organiques
[BIONIC V5 PIPELINE] Pipeline termine
```

### 8.2 Logs Console Attendus (Cache Hit)

```
[BIONIC V5 PIPELINE] Demarrage — 1 waypoint(s), cle: tous_wp_47.4000_-70.7000
[BIONIC V5 PIPELINE] ETAPE 1 — Cache hit: 13 zones
[BIONIC V5 PIPELINE] ETAPE 3 — Calcul backend en cours...
[BIONIC V5 PIPELINE] ETAPE 3 — Backend: 13 zones organiques
[BIONIC V5 PIPELINE] Pipeline termine
```

### 8.3 Logs Service Worker Attendus

```
[SW V2] Service Worker 5.0.0 loaded - HUNTIQ BIONIC V5 Ultimate
[SW V2] Installing Service Worker 5.0.0...
[SW V2] Precaching complete
[SW V2] Activating Service Worker 5.0.0...
[SW V2] Deleting old cache: huntiq-bionic-v5-static-v4
[SW V2] Deleting old cache: huntiq-bionic-v5-api-v4
[SW V2] Activation complete v5.0.0 — clients notification (no forced reload)
```

### 8.4 Test Backend Valide (2026-03-04)

```bash
POST /api/v1/bionic/organic-zones
Body: {bounds: {N:47.41, S:47.39, E:-70.69, W:-70.71}, species:"moose", layers:5}
Response: 7 features, computation_time: 14175ms
Stats: layers_processed:5, rejected:2, exclusions:8, penalties:7
```

---

## ANNEXE A — Glossaire

| Terme | Definition |
|-------|-----------|
| **State Locking** | Verrou empechant le recalcul des zones tant que la cle ne change pas |
| **Stale Closure** | Bug React ou une fonction async capture une variable obsolete |
| **Chaikin Subdivision** | Algorithme de lissage qui transforme N points en ~4N points |
| **PRNG Mulberry32** | Generateur pseudo-aleatoire deterministe (memes inputs → memes outputs) |
| **Spatial Clipping** | Decoupage des zones pour ne garder que celles dans un perimetre donne |
| **Classification Toggle** | Bouton ON/OFF qui masque/affiche une famille de couches (rendu uniquement) |
| **Service Worker** | Script cache par le navigateur qui intercepte les requetes reseau |
| **IndexedDB** | Base de donnees cle-valeur integree au navigateur (persistante) |
| **GeoJSON FeatureCollection** | Format standard pour les donnees geospatiales |

---

*Fin du Rapport Supra Strict — BIONIC V5 300%*
*Genere le 2026-03-04 — Agent Technique Emergent*
