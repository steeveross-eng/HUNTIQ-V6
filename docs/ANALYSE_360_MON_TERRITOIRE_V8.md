# ANALYSE 360° — PAGE MON TERRITOIRE BIONIC
## Version V8 — 12 Mars 2026
## Pre-requis P2: Refactoring du panneau droit

---

## 1. COMPOSANTS UTILISES

### 1.1 Composants rendus directement par `MonTerritoireBionicPage.jsx`

| # | Composant | Fichier | Role | Onglet/Condition | Statut |
|---|-----------|---------|------|------------------|--------|
| 1 | `TerritoireHeader` | ui/TerritoireHeader.jsx | Header: score, meteo, LIVE, bouton +WAYPOINT | Toujours visible | ACTIF |
| 2 | `BiologicalSeasonSelector` | ui/BiologicalSeasonSelector.jsx | Selecteur saison biologique dans toolbar | Visible hors Split | ACTIF |
| 3 | `BionicMapSelector` | maps/BionicMapSelector.jsx | Popover selection type de carte | Toolbar > Carte | ACTIF |
| 4 | `SplitViewContainer` | map/SplitViewContainer.jsx | Vue comparative 2 saisons | splitViewEnabled=true | ACTIF |
| 5 | `MapContent` | map/MapContent.jsx | Orchestrateur carte + couches | Mode normal | ACTIF |
| 6 | `BionicLegend` | BionicLegend.jsx | Legende BIONIC en overlay carte | Mode normal | ACTIF |
| 7 | `BionicZoneDiagnosticPanel` | BionicZoneDiagnosticPanel.jsx | Diagnostic zone selectionnee | selectedZone != null | ACTIF |
| 8 | `SidePanelZones` | ui/SidePanelZones.jsx | Panneau lateral carte (zoom, zones, corridors, ecologie) | activeTab='carte' | ACTIF |
| 9 | `WaypointUnifiedPanel` | WaypointUnifiedPanel.jsx | Panneau waypoints | activeTab='waypoints' | ACTIF |
| 10 | `PlacesSidePanel` | PlacesSidePanel.jsx | Panneau lieux | activeTab='lieux' | ACTIF |
| 11 | `GroupeTab` | modules/groupe | Panneau groupe | activeTab='groupe' | ACTIF |
| 12 | `AnalysisSidePanel` | AnalysisSidePanel.jsx | Panneau analyse/stats | activeTab='analyse' | ACTIF |
| 13 | `DiagnosticExclusionsPanel` | DiagnosticExclusionsPanel.jsx | Panneau exclusions/favoris/alertes | activeTab='exclusions' | ACTIF |
| 14 | `WaypointContextMenu` | WaypointContextMenu.jsx | Menu contextuel clic droit | contextMenuMT != null | ACTIF |
| 15 | `CompareWidget` | CompareWidget.jsx | Comparaison multi-waypoints | showCompareWidget=true | ACTIF |
| 16 | Dialogues (5) | ui/TerritoireDialogs.jsx | EditPlace, AddPlace, AddWaypoint, Share, GroupDashboard, CreateGroup | Conditionnels | ACTIF |

### 1.2 Composants rendus INDIRECTEMENT (via MapContent.jsx)

| # | Composant | Fichier | Role | Condition | Statut |
|---|-----------|---------|------|-----------|--------|
| 1 | `EcoforestryLayers` | EcoforestryLayers.jsx | Fond de carte ecoforestier | Toujours (gere internement) | ACTIF |
| 2 | `HydrographyOverlayLayer` | HydrographyOverlayLayer.jsx | Couche hydrographie | enabled=false (desactive) | INACTIF |
| 3 | `ExclusionOverlayLayer` | ExclusionOverlayLayer.jsx | Zones d'exclusion anthropiques | showExclusionOverlay | ACTIF |
| 4 | `WindFlowLayer` | WindFlowLayer.jsx | Vent directionnel | showWindFlow | ACTIF |
| 5 | `BionicMicroZones` | BionicMicroZones.jsx | Micro-zones BIONIC | Toujours (rendu zones) | ACTIF |
| 6 | `BionicZone2km` | BionicZone2km.jsx | Perimetre analyse 2km² | selectedWaypoint | ACTIF |
| 7 | `BionicAntiDoublesGuard` | BionicAntiDoublesGuard.jsx | Garde anti-doublons rendu | Toujours | ACTIF |
| 8 | `CursorBionicLayer` | CursorBionicLayer.jsx | Curseur BIONIC interactif | showCursorBionic | ACTIF |
| 9 | `StructureContrastLayer` | StructureContrastLayer.jsx | Contraste structure (desactive) | Non rendu (commentaire) | INACTIF |
| 10 | `MovementCorridorsLayer` | MovementCorridorsLayer.jsx | Corridors V1 (deplacements) | showCorridorsV1 | ACTIF |

### 1.3 Composants rendus indirectement (via SidePanelZones.jsx)

| # | Composant | Fichier | Role | Statut |
|---|-----------|---------|------|--------|
| 1 | `CorridorStatsPanel` | CorridorStatsPanel.jsx | Stats corridors V7 | ACTIF |
| 2 | `EcologicalPanel` | EcologicalPanel.jsx | Panneau ecologique V8 (integre P1) | ACTIF |
| 3 | `RejectionDiagnosticsPanel` | (inline SidePanelZones) | Diagnostics rejets zones | ACTIF |
| 4 | `WeatherInfluencePanel` | (inline SidePanelZones) | Impact meteo sur scores | ACTIF |

---

## 2. HOOKS UTILISES

| # | Hook | Fichier | Role | Dependencies |
|---|------|---------|------|-------------|
| 1 | `useBionicSession` | hooks/useBionicSession.js | **SOURCE DE VERITE** — Persistence session complete | localStorage |
| 2 | `useZoneOrchestrator` | hooks/useZoneOrchestrator.js | Pipeline zones: cache → backend → verrouillage | selectedWaypoint, species, season |
| 3 | `useBionicLayers` | hooks/useBionicLayers.js | Etat visibilite des couches | session.layers |
| 4 | `useBionicWeather` | hooks/useBionicWeather.js | Meteo live (OWM + fallback) | mapCenter |
| 5 | `useBionicScoring` | hooks/useBionicScoring.js | Scores hybrides BIONIC | zones, weather |
| 6 | `useUserData` | hooks/useUserData.js | CRUD waypoints + lieux + sync backend | userId |
| 7 | `useWaypointActions` | hooks/useWaypointActions.js | Actions waypoints (add/delete/select) | useUserData |
| 8 | `useSpatialClipping` | hooks/useSpatialClipping.js | Clipping spatial 1km×1km + snapshot | selectedWaypoint |
| 9 | `useGeolocation` | hooks/useGeolocation.js | GPS utilisateur | mapRef |
| 10 | `useMapType` | hooks/useMapType.js | Type de carte + options | - |
| 11 | `useSplitViewZones` | hooks/useSplitViewZones.js | Zones pour Split View droite | splitEnabled, season |
| 12 | `useZoneFavorites` | components/territoire/ZoneFavorites.jsx | Favoris zones + alertes | userId |
| 13 | `useNotifications` | hooks/useSharing.js | Notifications partage | userId |
| 14 | `useHuntingGroups` | hooks/useSharing.js | Groupes de chasse | userId |
| 15 | `useGroupeTracking` | modules/groupe | Tracking GPS membres groupe | userId |
| 16 | `useEcoMapFallback` | components/territoire/EcoforestryLayers.jsx | Fallback carte ecoforestiere | isEcoMapSelected |
| 17 | `useAuth` | components/GlobalAuth.jsx | Authentification utilisateur | - |
| 18 | `useLanguage` | contexts/LanguageContext | Internationalisation | - |

---

## 3. COUCHES CARTOGRAPHIQUES

| # | Couche | Composant | Type | Condition | Toggle Classification |
|---|--------|-----------|------|-----------|----------------------|
| 1 | Fond de carte | EcoforestryLayers | TileLayer | Toujours | - |
| 2 | Zones BIONIC | BionicMicroZones | Polygones | Filtre couches + classification | relief, foret, dominantes |
| 3 | Perimetre 2km² | BionicZone2km | Rectangle | selectedWaypoint | - |
| 4 | Corridors V8 (10X) | (dans BionicMicroZones) | Polylines | showCorridors + corridorsEstimes | corridorsEstimes |
| 5 | Corridors V1 | MovementCorridorsLayer | Polylines | showCorridorsV1 + corridorsReels | corridorsReels |
| 6 | Exclusions | ExclusionOverlayLayer | Polygones | showExclusionOverlay + pression | pression |
| 7 | Vent | WindFlowLayer | Canvas overlay | showWindFlow | meteo |
| 8 | Hydrographie | HydrographyOverlayLayer | Polylines | **DESACTIVE** (enabled=false) | hydro |
| 9 | Curseur BIONIC | CursorBionicLayer | Marqueur | showCursorBionic | curseurBionic |
| 10 | Anti-doublons | BionicAntiDoublesGuard | Guard | Toujours | - |
| 11 | Contraste structure | StructureContrastLayer | - | **DESACTIVE** (non rendu) | - |

---

## 4. PANNEAUX, OVERLAYS, TOGGLES ET INTERACTIONS

### 4.1 Toolbar (barre superieure)

| Position | Element | Action | Etat |
|----------|---------|--------|------|
| 1 | Saison biologique | Selecteur dropdown | selectedBiologicalSeason |
| 2 | Split | Toggle split view | splitViewEnabled |
| 3 | Carte | Popover selection fond | mapType |
| 4 | Espece | Dropdown selection espece | selectedSpecies |
| 5 | Observation | Menu: waypoints, lieux, groupe, exclusions | activeTab |
| 6 | Layers | Popover couches BIONIC + toggles secondaires | layersVisible + classificationToggles |
| 7 | Analyse | Toggle panneau analyse | activeTab='analyse' |
| 8 | Lock | Mode prive on/off | privacyMode |
| 9 | Outils | Popover: espece, corridors, seuil, curseur | Divers |

### 4.2 Classification Toggles

| Cle | Label | Couches controlees |
|-----|-------|--------------------|
| relief | Relief | altitude, pentes, orientation, ensoleillement |
| hydro | Hydrographie | hydro (filtre toujours a false) |
| foret | Foret | peuplements, ndvi |
| anthropique | Anthropique | (reserve futur) |
| dominantes | Dominantes | habitats, rut, repos, alimentation, salines, affuts, trajets, corridors |
| corridorsReels | Corridors reels | MovementCorridorsLayer V1 |
| meteo | Meteo | (reserve futur) |
| pression | Pression | ExclusionOverlayLayer |
| corridorsEstimes | Corridors estimes | Corridors 10X V8 |
| scoreHabitat | Score habitat | (reserve futur) |
| curseurBionic | Curseur BIONIC | CursorBionicLayer |
| waypoints | Waypoints | Marqueurs waypoints |

### 4.3 Panneaux lateraux (onglets)

| Onglet | Composant | Contenu principal |
|--------|-----------|-------------------|
| carte (defaut) | SidePanelZones | Zoom, zones count, weather influence, corridors stats, ecologie V8, waypoint cible |
| waypoints | WaypointUnifiedPanel | Liste waypoints, actions, position GPS, snapshot, compare |
| lieux | PlacesSidePanel | Liste lieux sauvegardes |
| groupe | GroupeTab | Module groupe chasse |
| analyse | AnalysisSidePanel | Score global, scores par categorie, stats zones |
| exclusions | DiagnosticExclusionsPanel | Zones exclues, favoris, alertes |

---

## 5. DEPENDANCES ENTRE MODULES

```
useBionicSession (SOURCE DE VERITE)
  ├── → mapCenter, mapZoom, selectedSpecies, layersVisible, waypointId
  ├── → biologicalSeason, activeTab, classificationToggles
  └── → showCorridorsV1, showExclusionOverlay, showWindFlow, windMode

useUserData(userId)
  ├── → waypoints, places, activeWaypoints
  └── → addWaypoint, deleteWaypoint, addPlace, updatePlace

useWaypointActions(mapRef, addWaypoint, deleteWaypoint...)
  ├── → selectedWaypointForZones ← CIBLE ACTIVE
  └── → mapClickMode, showDialogs

useZoneOrchestrator(selectedWaypoint, species, season)
  ├── → bionicZonesData { zones, corridors, stats }
  ├── → isLoadingZones, pipelineState, zoneSource
  └── → weatherMetadata

useSpatialClipping(selectedWaypoint)
  ├── → analysisBbox, bboxBounds
  └── → clipZonesClient()

useBionicLayers(savedLayers)
  └── → layersVisible, toggleLayer, activeCount

useBionicWeather(lat, lng)
  └── → weather, temperature, windInfo, huntingScore

useBionicScoring()
  └── → scores, globalScore
```

### Flux de donnees critiques:
1. **Session → Orchestrateur → Zones → Carte + Panneau droit**
2. **Waypoint selection → Spatial Clipping → Zones filtrees → Rendu carte**
3. **Corridors backend → EcologicalPanel + CorridorStatsPanel**
4. **BCE validation → Scores → Header + Analyse**

---

## 6. ELEMENTS OBSOLETES / REDONDANTS

### 6.1 Composants NON UTILISES (candidats Phase E decommission)

| Composant | Raison d'obsolescence |
|-----------|----------------------|
| `MonTerritoireBionic.jsx` | Ancienne version de la page (remplacee par MonTerritoireBionicPage) |
| `MonTerritoireToolbar.jsx` | Toolbar legacy (inline dans la page maintenant) |
| `BionicMapOverlay.jsx` | Overlay non reference |
| `CorridorsVisualLayer.jsx` | Remplace par corridors 10X dans BionicMicroZones |
| `NdviOverlayLayer.jsx` | Non importe |
| `RoutePlannerLayer.jsx` | Non importe |
| `RouteReplayLayer.jsx` | Non importe |
| `SeasonalConditionsWidget.jsx` | Non importe |
| `SmartMapTooltip.jsx` | Non importe |
| `TerritoryShell.jsx` | Non importe |
| `ZoneInfoPanel.jsx` | Non importe |
| `GroupDashboard.jsx` | Non importe directement (GroupDashboardDialog est utilise) |

### 6.2 Imports INUTILISES dans MonTerritoireBionicPage.jsx

| Import | Module | Action recommandee |
|--------|--------|--------------------|
| `useGroupeSafety` | modules/groupe | Supprimer import |
| `NotificationBell` | ShareComponents | Supprimer import |
| `fetchTerrainExclusions` | BionicZoneService | Supprimer import |
| `ZONE_LIMITS` | BionicZoneService | Supprimer import |
| `LAYER_TYPES` | BionicZoneService | Supprimer import |
| `AddToFavoritesButton` | ZoneFavorites | Supprimer import |
| `AlertsPanel` | ZoneFavorites | Supprimer import |
| `FavoritesList` | ZoneFavorites | Supprimer import |
| `getBiologicalSeason` | biologicalSeasons | Supprimer import |
| `mapToBackendSeason` | biologicalSeasons | Supprimer import |
| `getScoresForWaypoint` | core/bionic | Supprimer import |
| `adaptWaypointData` | core/bionic | Supprimer import |
| `getWindDirectionText` | core/bionic | Supprimer import |
| `getWeatherDescription` | core/bionic | Supprimer import |
| `BIONIC_LAYERS` | core/bionic | Supprimer import |
| `SCORE_CATEGORIES` | core/bionic | Supprimer import |
| `Edit2` | lucide-react | Supprimer import |
| `getMapConfig` | mapSources | Supprimer import |
| `BIONIC_COLORS` | bionic-colors | Supprimer import |
| `EcoforestryLayerControl` | EcoforestryLayers | Supprimer import |
| `EcoMapFallbackNotification` | EcoforestryLayers | Supprimer import |
| `BASE_MAPS` | EcoforestryLayers | Supprimer import |
| `ECOFORESTRY_LAYERS` | EcoforestryLayers | Supprimer import |
| `EcoMapStatus` | EcoforestryLayers | Supprimer import |

### 6.3 Doublons detectes

| Element | Localisation 1 | Localisation 2 | Recommandation |
|---------|----------------|----------------|----------------|
| Score global | TerritoireHeader | AnalysisSidePanel | Garder les deux (contexte different) |
| Corridors V7 stats | CorridorStatsPanel | EcologicalPanel (WWF) | **Fusionner** — CorridorStatsPanel et EcologicalPanel couvrent des aspects complementaires |
| Espece selector | Toolbar (dropdown rapide) | Outils (popover) | **Dupliquer intentionnel** — acces rapide + acces detaille |

---

## 7. ELEMENTS A MIGRER VERS LE FUTUR HUB

| Element actuel | Module Hub cible | Justification |
|----------------|------------------|---------------|
| EcologicalPanel (corridors WWF) | BIONIC Movement Engine | Corridors = mouvement |
| WeatherInfluencePanel | BIONIC Weather Engine | Impact meteo |
| CorridorStatsPanel (male/femelle/reel/IA) | BIONIC Movement Engine | Stats corridors |
| Score global + categories | BIONIC Scoring Hub | Score composite |
| Saison biologique | BIONIC Phenology Engine | Phenologie |
| Exclusions anthropiques | BIONIC Disturbance Engine | Pression humaine |
| Favoris + alertes zones | BIONIC Learning Engine | Apprentissage |
| Classification toggles | Ecological Intelligence Hub (UI) | Filtres couches |

---

## 8. ELEMENTS A RETIRER OU FUSIONNER

### A retirer (Phase E):
1. `MonTerritoireBionic.jsx` — Ancienne page complete
2. `MonTerritoireToolbar.jsx` — Toolbar legacy inlinee
3. `BionicMapOverlay.jsx` — Overlay non utilise
4. `CorridorsVisualLayer.jsx` — Remplace par corridors 10X
5. `NdviOverlayLayer.jsx` — Non utilise
6. `RoutePlannerLayer.jsx` — Non utilise
7. `RouteReplayLayer.jsx` — Non utilise
8. `SeasonalConditionsWidget.jsx` — Non utilise
9. `SmartMapTooltip.jsx` — Non utilise
10. `TerritoryShell.jsx` — Non utilise
11. `ZoneInfoPanel.jsx` — Non utilise
12. `StructureContrastLayer.jsx` — Deja desactive

### A fusionner:
1. **CorridorStatsPanel + EcologicalPanel** → Un seul panneau "Corridors & Ecologie V8" unifie
2. **Imports inutilises** → Nettoyage des ~25 imports morts dans MonTerritoireBionicPage.jsx

---

## 9. RESUME EXECUTIF

### Chiffres cles:
- **16** composants rendus directement
- **10** couches cartographiques (dont 2 desactivees)
- **18** hooks actifs
- **6** panneaux lateraux (onglets)
- **12** composants non utilises (candidats decommission)
- **25** imports inutilises a nettoyer
- **38** variables d'etat dans le composant principal (1508 lignes)

### Sante du code:
- Architecture modulaire solide (extraction IM1/IM1.2 reussie)
- Session persistante unifiee (useBionicSession)
- Pipeline zones robuste (useZoneOrchestrator)
- **Points d'attention**: Fichier principal encore volumineux (1508 lignes), imports morts accumulés

### Pret pour le refactoring P2:
L'analyse confirme que le refactoring du panneau droit peut se faire en toute securite en suivant les recommandations de `/app/docs/AUDIT_MON_TERRITOIRE_V8.md` et cette analyse complementaire.

---

**Analyse realisee le**: 12 Mars 2026
**Version BIONIC**: V8 (Certifiee)
**Auteur**: Emergent AI
