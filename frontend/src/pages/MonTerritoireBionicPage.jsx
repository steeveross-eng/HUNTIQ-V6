/**
 * MonTerritoireBionicPage - Page dédiée Mon Territoire BIONIC™
 * VERSION: 7.3.0 — IM1 Refactorisation modulaire
 * 
 * Architecture: Composant orchestrateur qui délègue aux sous-composants:
 * - MapHelpers: composants Leaflet utilitaires
 * - TerritoireHeader: header score/météo/LIVE
 * - TerritoireDialogs: toutes les modales
 * - SidePanelZones: panneau latéral zones
 * - useGeolocation: hook géolocalisation
 * - placeTypes: constantes types de lieux
 */

import React, { useState, useCallback, useMemo, useEffect, useLayoutEffect, useRef } from 'react';
import 'leaflet/dist/leaflet.css';
import { MapContainer } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import {
  Crosshair, Target, MapPin, Plus, X, LocateFixed,
  BookMarked, Users, Shield, SplitSquareHorizontal,
  Map, Binoculars, Layers, Lock, Unlock, BarChart3, CheckCircle, Settings,
} from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/popover';
import { Switch } from '@/components/ui/switch';
import useBionicLayers from '@/hooks/useBionicLayers';
import useBionicSession from '@/hooks/useBionicSession';
import useBionicWeather from '@/hooks/useBionicWeather';
import useBionicScoring from '@/hooks/useBionicScoring';
import { useUserData } from '@/hooks/useUserData';
import { useNotifications, useHuntingGroups } from '@/hooks/useSharing';
import BionicLegend from '@/components/territoire/BionicLegend';
import WaypointContextMenu from '@/components/territoire/WaypointContextMenu';
import WaypointUnifiedPanel from '@/components/territoire/WaypointUnifiedPanel';
import { useAuth } from '@/components/GlobalAuth';
import DiagnosticExclusionsPanel from '@/components/territoire/DiagnosticExclusionsPanel';
import BionicZoneDiagnosticPanel from '@/components/territoire/BionicZoneDiagnosticPanel';
import PlacesSidePanel from '@/components/territoire/PlacesSidePanel';
import AnalysisSidePanel from '@/components/territoire/AnalysisSidePanel';
import useSpatialClipping from '@/hooks/useSpatialClipping';
import CompareWidget from '@/components/territoire/CompareWidget';
import { BIONIC_MODULES } from '@/core/bionic';
import { SPECIES_LIST } from '@/core/bionic/speciesConfig';
import { useZoneOrchestrator } from '@/hooks/useZoneOrchestrator';
import { useZoneFavorites } from '@/components/territoire/ZoneFavorites';
import { GroupeTab, useGroupeTracking } from '@/modules/groupe';
// P2: EcologicalPanel fusionne dans CorridorsEcologyPanel via SidePanelZones
import { 
  useEcoMapFallback,
} from '@/components/territoire/EcoforestryLayers';
import { toast } from 'sonner';
// Import BIONIC Map Selector
import BionicMapSelector from '@/components/maps/BionicMapSelector';
import useMapType from '@/hooks/useMapType';
import { MAP_TYPES } from '@/config/mapSources';

// P2: BIONIC_COLORS migrated to component-level CSS variables

// IM1 — Modules extraits
import { useGeolocation } from '@/hooks/useGeolocation';
import { PLACE_TYPES } from '@/config/placeTypes';
import { TerritoireHeader } from '@/components/territoire/ui/TerritoireHeader';
import { EditPlaceDialog, AddPlaceDialog, AddWaypointDialog, ShareDialog, GroupDashboardDialog } from '@/components/territoire/ui/TerritoireDialogs';
import { CreateGroupDialog } from '@/components/territoire/ui/TerritoireDialogs';
import { SidePanelZones } from '@/components/territoire/ui/SidePanelZones';
// IM1.2 — Modules extraits (Passe 2)
import { useWaypointActions } from '@/hooks/useWaypointActions';
import { MapContent } from '@/components/territoire/map/MapContent';
// V8.1 — Saisons biologiques
import { BiologicalSeasonSelector } from '@/components/territoire/ui/BiologicalSeasonSelector';
import { getCurrentBiologicalSeason } from '@/config/biologicalSeasons';
// V8.1 — Split View
import { SplitViewContainer } from '@/components/territoire/map/SplitViewContainer';
import { useSplitViewZones } from '@/hooks/useSplitViewZones';

// Cle localStorage pour le dernier waypoint actif (legacy fallback)
const LAST_WAYPOINT_KEY = 'bionic_last_active_waypoint_id';

const MonTerritoireBionicPage = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();
  
  // ============================================
  // BCE-MAX x4.1 — SESSION (SOURCE DE VERITE UNIQUE)
  // DOIT etre le PREMIER hook pour fournir l'etat initial a tout le reste
  // ============================================
  const {
    session: bionicSession,
    position: savedPosition,
    species: savedSpecies,
    layers: savedLayers,
    waypointId: savedWaypointId,
    biologicalSeason: savedBiologicalSeason,
    activeTab: savedActiveTab,
    classificationToggles: savedClassificationToggles,
    showCorridorsV1: savedShowCorridorsV1,
    showExclusionOverlay: savedShowExclusionOverlay,
    showWindFlow: savedShowWindFlow,
    windMode: savedWindMode,
    updatePosition,
    updateSpecies,
    updateLayers,
    updateWaypointId,
    updateBiologicalSeason,
    updateActiveTab,
    updateClassificationToggles,
    updateVisualOptions,
    hasPreviousSession,
  } = useBionicSession();
  
  // BIONIC V5 300% — Ref directe vers l'instance Leaflet map
  const mapRef = useRef(null);
  
  // Onglet actif — restaure depuis la session BCE-MAX
  const [activeTab, setActiveTab] = useState(savedActiveTab || 'carte');
  
  // Etat de la carte — restaure depuis la session BCE-MAX
  const [mapCenter, setMapCenter] = useState(
    savedPosition?.lat != null && savedPosition?.lng != null
      ? [savedPosition.lat, savedPosition.lng]
      : [46.8139, -71.2080]
  );
  const [mapZoom, setMapZoom] = useState(savedPosition?.zoom || 12);
  const [currentZoom, setCurrentZoom] = useState(savedPosition?.zoom || 12);
  const [currentMapCenter, setCurrentMapCenter] = useState(
    savedPosition?.lat != null
      ? { lat: savedPosition.lat, lng: savedPosition.lng }
      : { lat: 46.8139, lng: -71.2080 }
  );
  const [currentMapBounds, setCurrentMapBounds] = useState(null);
  
  // V8.1 — Saison biologique active (restauree depuis session BCE-MAX)
  const [selectedBiologicalSeason, setSelectedBiologicalSeason] = useState(() => savedBiologicalSeason || getCurrentBiologicalSeason().id);
  
  // BCE-MAX: Sync saison biologique vers session
  useEffect(() => {
    if (selectedBiologicalSeason) {
      updateBiologicalSeason(selectedBiologicalSeason);
    }
  }, [selectedBiologicalSeason, updateBiologicalSeason]);
  
  // V8.1 — Split View
  // V8.2 FIX: Capture du centre/zoom RÉEL de la carte au moment d'activer le SplitView
  // mapCenter/mapZoom sont les valeurs INITIALES (Québec City par défaut)
  // currentMapCenter/currentZoom sont les valeurs ACTUELLES (suivi en temps réel)
  const [splitViewEnabled, setSplitViewEnabled] = useState(false);

  // V8.2 FIX: Centre/zoom figés au moment de l'activation du Split View
  const [splitMapCenter, setSplitMapCenter] = useState(null);
  const [splitMapZoom, setSplitMapZoom] = useState(null);

  // V8.2 FIX: Handler d'activation du Split View — capture la position courante
  const toggleSplitView = useCallback(() => {
    setSplitViewEnabled(prev => {
      if (!prev) {
        // Activation: capturer la position RÉELLE de la carte principale
        if (mapRef.current) {
          const c = mapRef.current.getCenter();
          const z = mapRef.current.getZoom();
          setSplitMapCenter([c.lat, c.lng]);
          setSplitMapZoom(z);
        } else {
          setSplitMapCenter([currentMapCenter.lat, currentMapCenter.lng]);
          setSplitMapZoom(currentZoom);
        }
      } else {
        // P0 FIX: Désactivation — capturer position depuis split et mettre à jour
        // mapCenter/mapZoom pour que le nouveau MapContainer garde la même position
        if (mapRef.current) {
          const c = mapRef.current.getCenter();
          const z = mapRef.current.getZoom();
          setMapCenter([c.lat, c.lng]);
          setMapZoom(z);
        }
      }
      return !prev;
    });
  }, [currentMapCenter, currentZoom]);
  const [splitRightSeason, setSplitRightSeason] = useState('rut'); // Saison droite par défaut
  const [selectedZone, setSelectedZone] = useState(null);
  const [hoveredZone, setHoveredZone] = useState(null);
  const [showCorridorsV1, setShowCorridorsV1] = useState(savedShowCorridorsV1 ?? false);
  const [showExclusionOverlay, setShowExclusionOverlay] = useState(savedShowExclusionOverlay ?? false);
  const [showWindFlow, setShowWindFlow] = useState(savedShowWindFlow ?? false);
  const [windMode, setWindMode] = useState(savedWindMode || 'arrows');
  const [temporalHourMT, setTemporalHourMT] = useState(null);
  const [contextMenuMT, setContextMenuMT] = useState(null);
  
  // Géolocalisation (hook extrait IM1)
  const { userPosition, setUserPosition, watchingPosition, startWatchingPosition, stopWatchingPosition, centerOnUser } = useGeolocation(mapRef);
  
  // P0 FIX: Use auth context for userId instead of broken localStorage read
  const { user: authUser } = useAuth();
  const userId = useMemo(() => {
    if (authUser?.id) return authUser.id;
    if (authUser?.email) return authUser.email;
    return 'anonymous';
  }, [authUser]);
  
  // Hook pour les waypoints et lieux avec sync backend
  const {
    waypoints,
    places: savedPlaces,
    activeWaypoints,
    stats: userDataStats,
    loading: userDataLoading,
    syncing,
    isOnline,
    addWaypoint,
    updateWaypoint,
    deleteWaypoint,
    toggleWaypointActive,
    addPlace,
    updatePlace,
    deletePlace,
    syncToBackend
  } = useUserData(userId, { autoSync: true });
  
  // IM1.2 — Hook actions waypoints/lieux (extrait)
  const {
    selectedWaypointForZones, setSelectedWaypointForZones,
    mapClickMode, setMapClickMode,
    showAddWaypointDialog, setShowAddWaypointDialog,
    newWaypoint, setNewWaypoint,
    showAddPlaceDialog, setShowAddPlaceDialog,
    newPlace, setNewPlace,
    editingPlace, setEditingPlace,
    showShareDialog, setShowShareDialog,
    waypointToShare, setWaypointToShare,
    selectWaypointAsTarget,
    clearWaypointTarget,
    handleDeleteWaypoint,
    handleAddWaypoint,
    handleAddWaypointFromDialog,
    handleMapClickForWaypoint,
    useCurrentPositionForNewWaypoint,
    useCurrentPositionForNewPlace,
    handleAddPlace,
    handleUpdatePlace,
    openShareDialog,
    bindReloadZones,
  } = useWaypointActions({
    mapRef,
    mapCenter,
    addWaypoint,
    deleteWaypoint,
    addPlace,
    updatePlace,
    userPosition,
  });

  // BIONIC V5 300% INVARIANT: Spatial Clipping 1km × 1km (doit être après useWaypointActions)
  const { analysisBbox, bboxBounds, clipZonesClient, snapshotData, isGeneratingSnapshot, generateSnapshot, ANALYSIS_BOX_SIZE_M } = useSpatialClipping(selectedWaypointForZones);

  // BIONIC V5 300% — AUTO-SELECTION DU DERNIER WAYPOINT ACTIF
  // BCE-MAX x4.1: Priorite au waypointId de la session
  const autoSelectDoneRef = useRef(false);
  useLayoutEffect(() => {
    if (autoSelectDoneRef.current) return;
    if (!selectedWaypointForZones && activeWaypoints.length > 0) {
      const lastId = savedWaypointId || localStorage.getItem(LAST_WAYPOINT_KEY);
      const lastWp = lastId ? activeWaypoints.find(wp => wp.id === lastId) : null;
      const target = lastWp || activeWaypoints[0];
      if (target && (target.lat || target.latitude)) {
        const source = lastWp ? 'session BCE-MAX' : 'premier actif (fallback)';
        console.log(`[BCE-MAX x4.1] Auto-select: "${target.name}" (${source})`);
        autoSelectDoneRef.current = true;
        setSelectedWaypointForZones(target);
        localStorage.setItem(LAST_WAYPOINT_KEY, target.id);
        updateWaypointId(target.id);
      }
    }
  }, [selectedWaypointForZones, activeWaypoints]);

  // BCE-MAX x4.1: CENTRAGE MAP depuis session persistante
  const initialCenterDoneRef = useRef(false);
  useEffect(() => {
    if (initialCenterDoneRef.current) return;
    if (!mapRef.current) return;

    // Priorite 0: Session BCE-MAX x4.1 (position exacte de la derniere session)
    if (hasPreviousSession && savedPosition?.lat && savedPosition?.lng && savedPosition?.zoom) {
      initialCenterDoneRef.current = true;
      mapRef.current.setView([savedPosition.lat, savedPosition.lng], savedPosition.zoom);
      console.log(`[BCE-MAX x4.1] Session restauree: [${savedPosition.lat.toFixed(4)}, ${savedPosition.lng.toFixed(4)}] zoom ${savedPosition.zoom}`);
      return;
    }

    // Fallback: Waypoint selectionne (centrage classique)
    if (!selectedWaypointForZones) return;
    const lat = selectedWaypointForZones.lat || selectedWaypointForZones.latitude;
    const lng = selectedWaypointForZones.lng || selectedWaypointForZones.longitude;
    if (lat && lng) {
      initialCenterDoneRef.current = true;
      mapRef.current.setView([lat, lng], 14);
      console.log(`[BCE-MAX x4.1] Centrage initial: [${lat}, ${lng}] zoom 14`);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedWaypointForZones?.id, hasPreviousSession, savedPosition]);

  // BCE-MAX x4.1: Sauvegarde automatique UNIFIEE du contexte utilisateur
  const contextSaveTimerRef = useRef(null);
  useEffect(() => {
    if (contextSaveTimerRef.current) clearTimeout(contextSaveTimerRef.current);
    contextSaveTimerRef.current = setTimeout(() => {
      // Position carte
      if (currentMapCenter.lat && currentMapCenter.lng && currentZoom) {
        updatePosition(currentMapCenter.lat, currentMapCenter.lng, currentZoom);
      }
      // Waypoint
      if (selectedWaypointForZones?.id) {
        updateWaypointId(selectedWaypointForZones.id);
      }
      // Onglet
      updateActiveTab(activeTab);
      // Options visuelles
      updateVisualOptions({
        showCorridorsV1,
        showExclusionOverlay,
        showWindFlow,
        windMode,
      });
    }, 500);
    return () => { if (contextSaveTimerRef.current) clearTimeout(contextSaveTimerRef.current); };
  }, [currentMapCenter.lat, currentMapCenter.lng, currentZoom, selectedWaypointForZones?.id, activeTab, showCorridorsV1, showExclusionOverlay, showWindFlow, windMode, updatePosition, updateWaypointId, updateActiveTab, updateVisualOptions]);

  
  // Notifications
  const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotifications(userId);
  
  // Groupes de chasse
  const { allGroups: myGroups, loading: groupsLoading, refresh: refreshGroups } = useHuntingGroups(userId);
  
  // Dialog de partage
  const [showCreateGroupDialog, setShowCreateGroupDialog] = useState(false);
  const [showNotificationsPanel, setShowNotificationsPanel] = useState(false);
  
  // Tableau de bord de groupe (tracking live + chat)
  const [showGroupDashboard, setShowGroupDashboard] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState(null);
  
  // Session Heatmap - Phase 6 GROUPE Module
  // Hook pour obtenir les positions GPS des membres du groupe
  const {
    membersWithPositions: groupMembersPositions,
    isTracking: isGroupeTrackingActive
  } = useGroupeTracking(userId, 'territory_group', {
    autoStart: false,
    updateInterval: 30000
  });
  
  // Panneaux
  const [showLayersPanel, setShowLayersPanel] = useState(true);
  const [liveMode, setLiveMode] = useState(false);
  const [showCursorBionic, setShowCursorBionic] = useState(false); // P0 FIX: BBox debug caché par défaut
  
  // ============================================
  // CARTE PREMIUM BIONIC - Sélecteur de type de carte
  // ============================================
  const { 
    mapType, 
    setMapType, 
    mapOptions, 
    setMapOptions, 
    tileUrl, 
    attribution,
    isDarkOptimized,
    getZoneOpacityForCurrentMap
  } = useMapType(MAP_TYPES.SATELLITE);
  
  // Mode d'affichage des zones BIONIC
  const [zoneDisplayMode, setZoneDisplayMode] = useState('micro'); // 'micro' ou 'classic'
  const [showCorridors, setShowCorridors] = useState(true); // BCE-MAX: Corridors toujours visibles
  const [minPercentageFilter, setMinPercentageFilter] = useState(30);
  
  // BIONIC V5 300% — CLASSIFICATION TOGGLES (restaures depuis session BCE-MAX)
  const [classificationToggles, setClassificationToggles] = useState(() => {
    if (savedClassificationToggles && typeof savedClassificationToggles === 'object') {
      return savedClassificationToggles;
    }
    return {
      relief: true,
      hydro: true,
      foret: true,
      anthropique: true,
      dominantes: true,
      corridorsReels: true,
      meteo: true,
      pression: true,
      corridorsEstimes: true,
      scoreHabitat: true,
      curseurBionic: true,
      waypoints: true,
    };
  });
  const handleClassificationToggle = useCallback((key) => {
    setClassificationToggles(prev => {
      const updated = { ...prev, [key]: !prev[key] };
      updateClassificationToggles(updated);
      return updated;
    });
  }, [updateClassificationToggles]);
  
  // ============================================
  // BCE-MAX x4.1 — Espece selectionnee (restauree depuis session)
  // ============================================
  const [selectedSpecies, setSelectedSpecies] = useState(() => savedSpecies || 'tous');
  
  // Synchroniser l'espece avec la session
  useEffect(() => {
    if (selectedSpecies) {
      updateSpecies(selectedSpecies);
    }
  }, [selectedSpecies, updateSpecies]);
  
  // Les exclusions sont gérées 100% backend. Ces variables sont gardées pour compatibilité UI.
  const terrainExclusions = [];
  const isLoadingExclusions = false;
  
  // ============================================
  // CARTE ÉCOFORESTIÈRE - État des couches
  // ============================================
  const [activeEcoLayers, setActiveEcoLayers] = useState({
    baseMap: 'satellite_hd', // P0 FIX: Satellite par défaut, pas écoforestière
    peuplements: false,
    essences: false,
    perturbations: false,
    densite: false,
    hauteur: false,
    lidar_chm: false,
    lidar_volume: false,
    lidar_st: false,
    courbes_niveau: false
  });
  const [ecoLayerOpacities, setEcoLayerOpacities] = useState({});
  
  // Synchroniser le type de carte avec activeEcoLayers.baseMap
  useEffect(() => {
    // Mapper les types de carte BIONIC aux baseMap du système existant
    const mapTypeToBaseMap = {
      'ecoforestry': 'ecoforestry',
      'ecoforestry': 'ecoforestry',
      'satellite': 'satellite_hd',
      'iqho': 'iqho',
      'bathymetry': 'bathymetry',
      'forest-roads': 'forest-roads'
    };
    
    const newBaseMap = mapTypeToBaseMap[mapType] || 'terrain';
    setActiveEcoLayers(prev => ({ ...prev, baseMap: newBaseMap }));
  }, [mapType]);
  
  // ============================================
  // SYSTÈME DE FALLBACK - Carte écoforestière
  // ============================================
  const isEcoMapSelected = activeEcoLayers.baseMap === 'ecoforestry';
  const {
    status: ecoMapStatus,
    activeFallback,
    retryCount,
    lastCheck,
    isAvailable: isEcoMapAvailable,
    isUnavailable: isEcoMapUnavailable,
    forceCheck: forceEcoMapCheck,
    setFallbackMap
  } = useEcoMapFallback(isEcoMapSelected);
  
  // Gestionnaire de toggle des couches écoforestières
  const handleEcoLayerToggle = useCallback((layerId, value) => {
    if (layerId === 'baseMap') {
      setActiveEcoLayers(prev => ({ ...prev, baseMap: value }));
    } else {
      setActiveEcoLayers(prev => ({ ...prev, [layerId]: !prev[layerId] }));
    }
  }, []);
  
  // Gestionnaire d'opacité des couches
  const handleEcoOpacityChange = useCallback((layerId, opacity) => {
    setEcoLayerOpacities(prev => ({ ...prev, [layerId]: opacity }));
  }, []);
  
  // V8.3.A: Popover Carte — mode contrôlé pour fermeture auto après sélection
  const [cartePopoverOpen, setCartePopoverOpen] = useState(false);
  const handleMapTypeChangeAndClose = useCallback((type) => {
    setMapType(type);
    setCartePopoverOpen(false);
  }, [setMapType]);

  // V8.3.A: Compare Widget — sélection multi-waypoints
  const [compareSelection, setCompareSelection] = useState([]); // IDs des waypoints sélectionnés
  const [showCompareWidget, setShowCompareWidget] = useState(false);

  const handleToggleCompare = useCallback((wp) => {
    setCompareSelection(prev => {
      const exists = prev.find(w => w.id === wp.id);
      if (exists) return prev.filter(w => w.id !== wp.id);
      if (prev.length >= 3) return prev; // max 3
      return [...prev, wp];
    });
  }, []);

  const handleLaunchCompare = useCallback(() => {
    if (compareSelection.length >= 2) {
      setShowCompareWidget(true);
    }
  }, [compareSelection]);

  const handleCloseCompare = useCallback(() => {
    setShowCompareWidget(false);
  }, []);

  // V8.3.A: Auto-activation mode Particules lors de l'ajout d'un waypoint
  const handleAddWaypointWithWind = useCallback(() => {
    handleAddWaypointFromDialog();
    // Activer automatiquement le vent en mode particules
    setShowWindFlow(true);
    setWindMode('particles');
  }, [handleAddWaypointFromDialog]);

  // Mode confidentialité (seul l'utilisateur et l'admin peuvent voir les données privées)
  const [privacyMode, setPrivacyMode] = useState(false);
  const isPrivateDataVisible = !privacyMode; // Les waypoints, recherches, annotations sont visibles
  
  // ============================================
  // Hooks BIONIC — couches (initialisees depuis session BCE-MAX)
  const { 
    layersVisible, 
    toggleLayer, 
    showAllLayers, 
    hideAllLayers,
    activeCount,
    allLayers,
  } = useBionicLayers(savedLayers);
  
  // Synchroniser les couches avec la session BCE-MAX
  useEffect(() => {
    if (layersVisible && Object.keys(layersVisible).length > 0) {
      updateLayers(layersVisible);
    }
  }, [layersVisible, updateLayers]);
  
  const { 
    weather, 
    isLoading: weatherLoading,
    temperature,
    windInfo,
    thermalInfo,
    huntingScore,
    nextOptimalWindow,
    sunrise,
    sunset,
    refresh: refreshWeather
  } = useBionicWeather(mapCenter[0], mapCenter[1], { autoFetch: true, pollInterval: liveMode ? 60000 : 600000 });
  
  const { scores, calculateHybridScores, globalScore } = useBionicScoring();
  
  // Hook pour les zones favorites et alertes
  const {
    favorites,
    alerts,
    unreadAlertCount,
    loading: favoritesLoading,
    addFavorite,
    removeFavorite,
    updateAlertSettings,
    markAlertRead,
    markAllAlertsRead,
    checkOptimalConditions,
    getZoneConditions,
    refresh: refreshFavorites
  } = useZoneFavorites(userId);
  
  // Vérifier si une zone est favorite
  const isZoneFavorite = useCallback((zone) => {
    return favorites.some(f => 
      Math.abs(f.location.lat - zone.center[0]) < 0.0001 &&
      Math.abs(f.location.lng - zone.center[1]) < 0.0001 &&
      f.module_id === zone.moduleId
    );
  }, [favorites]);
  
  // Trouver l'ID du favori pour une zone
  const getFavoriteId = useCallback((zone) => {
    const fav = favorites.find(f => 
      Math.abs(f.location.lat - zone.center[0]) < 0.0001 &&
      Math.abs(f.location.lng - zone.center[1]) < 0.0001 &&
      f.module_id === zone.moduleId
    );
    return fav?.id;
  }, [favorites]);
  
  // Callback pour le changement de zoom
  const handleZoomChange = useCallback((newZoom) => {
    setCurrentZoom(newZoom);
  }, []);
  
  // Callback pour le déplacement de la carte
  const handleMapMove = useCallback((newCenter) => {
    setCurrentMapCenter(newCenter);
  }, []);
  
  // Callback pour le changement des limites visibles
  const handleBoundsChange = useCallback((newBounds) => {
    setCurrentMapBounds(newBounds);
  }, []);
  
  // ============================================
  // BIONIC V5 300% — PIPELINE WAYPOINT EXCLUSIF + ORCHESTRATEUR DE ZONES
  // 
  // Architecture modulaire stricte:
  //   1. useZoneOrchestrator: orchestration (cache → backend)
  //   2. useZoneCache: cache IndexedDB persistant (<100ms)
  //   3. generateWaypointZonesV5: calcul backend complet (~11s)
  //
  // Flux: Waypoint → Cache? → Loader → Backend (définitif) → Verrouillage
  // Zéro connexion croisée. Zéro bavure. Contrats explicites.
  // ============================================
  const {
    zonesData: bionicZonesData,
    isLoading: isLoadingZones,
    zoneSource,
    zeroZonesReason,
    pipelineState,
    reload: reloadZones,
    cacheKey: zoneLockKey,
    weatherMetadata,
  } = useZoneOrchestrator({
    selectedWaypointForZones,
    activeWaypoints,
    selectedSpecies,
    currentZoom,
    biologicalSeason: selectedBiologicalSeason,
  });

  // IM1.2: Late-bind reloadZones dans useWaypointActions
  useEffect(() => { bindReloadZones(reloadZones); }, [reloadZones, bindReloadZones]);

  // V8.1: Zones de la carte droite (Split View)
  const { zonesData: splitRightZonesData, isLoading: isSplitRightLoading } = useSplitViewZones({
    enabled: splitViewEnabled,
    selectedWaypointForZones,
    activeWaypoints,
    selectedSpecies,
    currentZoom,
    biologicalSeason: splitRightSeason,
  });

  // C13 BIONIC 1000% — Strict state feedback
  useEffect(() => {
    if (!zeroZonesReason || isLoadingZones) return;
    if (zeroZonesReason === 'timeout') {
      toast.error('Délai d\'analyse dépassé (30s)', {
        description: 'Le serveur n\'a pas répondu à temps. Veuillez réessayer avec un secteur plus petit.',
        duration: 8000,
      });
    } else if (zeroZonesReason === 'overpass_unavailable') {
      toast.warning('Service de cartographie temporairement indisponible', {
        description: 'Les données d\'exclusion n\'ont pas pu être récupérées. Réessayez dans quelques instants.',
        duration: 6000,
      });
    } else if (zeroZonesReason === 'all_filtered_by_exclusions') {
      toast.info('Aucune zone générée dans ce secteur', {
        description: 'Toutes les zones candidates ont été exclues par les filtres anthropiques (routes, bâtiments, infrastructures).',
        duration: 5000,
      });
    } else if (zeroZonesReason === 'backend_error') {
      toast.error('Erreur de calcul des zones', {
        description: 'Une erreur est survenue lors de l\'analyse. Veuillez réessayer.',
        duration: 5000,
      });
    }
  }, [zeroZonesReason, isLoadingZones]);

  // T4 COHERENCE: Warn if backend zone count mismatches frontend parsed count
  useEffect(() => {
    const stats = bionicZonesData.stats || {};
    if (stats.t4_mismatch) {
      console.error(
        `[T4-COHERENCE] Backend t4_zone_count=${stats.t4_backend_count}, ` +
        `frontend parsed=${stats.total}`
      );
      toast.warning('Incohérence de données détectée', {
        description: `Le backend a généré ${stats.t4_backend_count} zones mais ${stats.total} ont été rendues.`,
        duration: 8000,
      });
    }
  }, [bionicZonesData.stats]);

  // ============================================
  // BIONIC V5 300% — SPATIAL CLIPPING + STATE LOCKING
  // 1. Les zones sont calculées pour TOUTES les couches structurelles
  // 2. Le clipping 1km × 1km est appliqué quand un waypoint est actif
  // 3. La visibilité est appliquée au RENDU, pas au calcul
  // ============================================
  const rawZones = useMemo(() => {
    const zones = bionicZonesData.zones || [];
    return zones.filter(z => z.layerId !== 'hydro');
  }, [bionicZonesData.zones]);
  const bionicStats = bionicZonesData.stats || {};
  
  // SPATIAL CLIPPING: Appliquer le clipping 1km × 1km si un waypoint est sélectionné
  const allZones = useMemo(() => {
    if (!selectedWaypointForZones || !analysisBbox) return rawZones;
    return clipZonesClient(rawZones);
  }, [rawZones, selectedWaypointForZones, analysisBbox, clipZonesClient]);
  
  // STATE LOCKING + CLASSIFICATION: Filtrer les zones par visibilité (rendu uniquement, pas recalcul)
  // Les zones restent en mémoire (orchestrateur) même si une famille Classification est OFF.
  const bionicZones = useMemo(() => {
    const RELIEF_LAYERS = new Set(['altitude', 'pentes', 'orientation', 'ensoleillement']);
    const HYDRO_LAYERS = new Set(['hydro']);
    const FORET_LAYERS = new Set(['peuplements', 'ndvi']);
    const DOMINANT_LAYERS = new Set(['habitats', 'rut', 'repos', 'alimentation', 'salines', 'affuts', 'trajets', 'corridors']);
    
    return allZones.filter(z => {
      if (layersVisible[z.layerId] === false) return false;
      if (!classificationToggles.relief && RELIEF_LAYERS.has(z.layerId)) return false;
      if (HYDRO_LAYERS.has(z.layerId)) return false;
      if (!classificationToggles.foret && FORET_LAYERS.has(z.layerId)) return false;
      if (!classificationToggles.dominantes && DOMINANT_LAYERS.has(z.layerId)) return false;
      return true;
    });
  }, [allZones, layersVisible, classificationToggles]);
  
  // Compter les zones visibles
  const visibleZonesCount = useMemo(() => {
    return bionicZones.filter(z => z.score >= minPercentageFilter).length;
  }, [bionicZones, minPercentageFilter]);
  
  // Score global V9 — Integre zones (65%) + corridors V9 (35%)
  const displayScore = useMemo(() => {
    if (globalScore) return globalScore;
    const corridors = bionicZonesData.corridors || [];
    
    let zoneAvg = 0;
    if (bionicZones.length > 0) {
      const validScores = bionicZones.map(z => z.score || 0).filter(s => s > 0);
      if (validScores.length > 0) {
        zoneAvg = validScores.reduce((a, b) => a + b, 0) / validScores.length;
      }
    }
    
    let corridorAvg = 0;
    if (corridors.length > 0) {
      const corridorScores = corridors.map(c => c.score || 0).filter(s => s > 0);
      if (corridorScores.length > 0) {
        corridorAvg = corridorScores.reduce((a, b) => a + b, 0) / corridorScores.length;
      }
    }
    
    if (zoneAvg === 0 && corridorAvg === 0) return null;
    if (corridorAvg === 0) return Math.round(zoneAvg);
    if (zoneAvg === 0) return Math.round(corridorAvg);
    
    // V9: corridors weighted at 35% (up from 30%) due to 9-engine precision
    return Math.round(zoneAvg * 0.65 + corridorAvg * 0.35);
  }, [globalScore, bionicZones, bionicZonesData.corridors]);
  
  const getScoreRating = (score) => {
    if (!score) return { label: 'En attente', color: 'bg-gray-700', textColor: 'text-gray-400' };
    if (score >= 85) return { label: 'Exceptionnel', color: 'bg-green-500', textColor: 'text-green-400' };
    if (score >= 70) return { label: 'Excellent', color: 'bg-lime-500', textColor: 'text-lime-400' };
    if (score >= 55) return { label: 'Bon', color: 'bg-yellow-500', textColor: 'text-yellow-400' };
    return { label: 'Modéré', color: 'bg-orange-500', textColor: 'text-orange-400' };
  };
  
  const rating = getScoreRating(displayScore);

  // ============================================
  // STEVE-MAX: Hunting Path + Amenagement Engine
  // ============================================
  const [huntingPathData, setHuntingPathData] = useState(null);
  const [amenagementReport, setAmenagementReport] = useState(null);
  const [showHuntingPath, setShowHuntingPath] = useState(true);

  // Auto-fetch hunting path when zones are loaded
  useEffect(() => {
    if (!bionicZones.length || !selectedWaypointForZones) return;
    const corridors = bionicZonesData.corridors || [];
    const wp = selectedWaypointForZones;
    const wpc = { lat: wp.lat || wp.latitude, lng: wp.lng || wp.longitude };

    const API = process.env.REACT_APP_BACKEND_URL;
    // Build zone features for API
    const zoneFeatures = bionicZones.map(z => ({
      geometry: z.geometry || { type: 'Polygon', coordinates: z.coordinates ? [z.coordinates] : [] },
      properties: { layer_id: z.layerId, score: z.score, label: z.label },
    }));

    fetch(`${API}/api/v1/bionic/amenagement-report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        zones: zoneFeatures,
        corridors,
        waypoint_center: wpc,
      }),
    })
      .then(r => r.json())
      .then(data => {
        if (data.success) {
          setHuntingPathData(data.hunting_path);
          setAmenagementReport(data.amenagement_report);
        }
      })
      .catch(() => {});
  }, [bionicZones.length, selectedWaypointForZones, bionicZonesData.corridors]);

  // BIONIC V5 300% INVARIANT: Snapshot Territoire handler
  const handleGenerateSnapshot = useCallback(async (format) => {
    if (!selectedWaypointForZones) return;
    const snap = await generateSnapshot(selectedSpecies, layersVisible, {
      hour: temporalHourMT,
      zoom: currentZoom,
      timestamp: new Date().toISOString(),
    });
    if (!snap) return;
    
    if (format === 'json') {
      // Export JSON — téléchargement direct
      const blob = new Blob([JSON.stringify(snap, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${snap.snapshot_id || 'snapshot'}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } else if (format === 'pdf') {
      // Export PDF avec capture d'écran de la carte
      try {
        const { jsPDF } = await import('jspdf');
        const doc = new jsPDF('landscape', 'mm', 'a4');
        
        // Capture de la carte
        const mapEl = document.querySelector('.leaflet-container');
        if (mapEl) {
          const html2canvas = (await import('html2canvas')).default;
          const canvas = await html2canvas(mapEl, { useCORS: true, scale: 1, logging: false });
          const imgData = canvas.toDataURL('image/jpeg', 0.8);
          doc.addImage(imgData, 'JPEG', 10, 10, 180, 120);
        }
        
        // Métadonnées
        const y0 = 135;
        doc.setFontSize(14);
        doc.text(`Snapshot Territoire — BIONIC V5 300%`, 10, y0);
        doc.setFontSize(9);
        doc.text(`Waypoint: ${snap.waypoint?.name || 'N/A'}`, 10, y0 + 7);
        doc.text(`Coords: ${snap.waypoint?.lat?.toFixed(6)}, ${snap.waypoint?.lng?.toFixed(6)}`, 10, y0 + 12);
        doc.text(`Espece: ${snap.species} | Saison: ${snap.season}`, 10, y0 + 17);
        doc.text(`Perimetre: 1km x 1km | Zones: ${snap.structural_zones?.length || 0}`, 10, y0 + 22);
        doc.text(`Date: ${new Date(snap.timestamp).toLocaleString('fr-CA')}`, 10, y0 + 27);
        doc.text(`ID: ${snap.snapshot_id}`, 10, y0 + 32);
        
        // Zone summary
        if (snap.zone_summary) {
          let yOff = y0 + 40;
          doc.setFontSize(10);
          doc.text('Resume par couche:', 10, yOff);
          yOff += 5;
          doc.setFontSize(8);
          Object.entries(snap.zone_summary).forEach(([lid, info]) => {
            doc.text(`  ${lid}: ${info.count} zones, score moyen ${info.avg_score}`, 10, yOff);
            yOff += 4;
          });
        }
        
        doc.save(`${snap.snapshot_id || 'snapshot'}.pdf`);
      } catch (err) {
        console.error('[Snapshot PDF] Error:', err);
      }
    }
  }, [selectedWaypointForZones, generateSnapshot, selectedSpecies, layersVisible, temporalHourMT, currentZoom]);

  
  // Scores par catégorie (valeurs stables basées sur la position)
  const categoryScores = useMemo(() => {
    if (scores?.breakdown) return scores.breakdown;
    // Scores déterministes basés sur la position
    const baseSeed = Math.abs(Math.round(currentMapCenter.lat * 100 + currentMapCenter.lng * 50));
    return {
      habitat: 75 + (baseSeed % 15),
      rut: 68 + ((baseSeed + 1) % 20),
      salines: 60 + ((baseSeed + 2) % 25),
      affuts: 80 + ((baseSeed + 3) % 15),
      trajets: 65 + ((baseSeed + 4) % 20),
      peuplements: 70 + ((baseSeed + 5) % 15)
    };
  }, [scores?.breakdown, currentMapCenter.lat, currentMapCenter.lng]);

  return (
    <div className="fixed inset-0 bg-[#0a0a0f] overflow-hidden flex flex-col" style={{ paddingTop: '64px' }} data-testid="mon-territoire-bionic-page">
      {/* ═══ SECTION 1 — HEADER (composant extrait IM1) ═══ */}
      <TerritoireHeader
        navigate={navigate}
        displayScore={displayScore}
        rating={rating}
        weather={weather}
        temperature={temperature}
        windInfo={windInfo}
        huntingScore={huntingScore}
        liveMode={liveMode}
        setLiveMode={setLiveMode}
        isLoadingZones={isLoadingZones}
        selectedWaypointForZones={selectedWaypointForZones}
        mapClickMode={mapClickMode}
        setMapClickMode={setMapClickMode}
        setShowAddWaypointDialog={setShowAddWaypointDialog}
        onClearWaypoint={clearWaypointTarget}
        onDeleteWaypoint={handleDeleteWaypoint}
        onCenterWaypoint={() => {
          if (selectedWaypointForZones && mapRef.current) {
            mapRef.current.setView([selectedWaypointForZones.lat, selectedWaypointForZones.lng], 14);
          }
        }}
      />

      {/* ════════════════════════════════════════════════════════════════
          P0 UX — TOOLBAR UNIFIÉE SUR UNE SEULE LIGNE
          SAISON → SPLIT → CARTE → OBSERVATION → LAYERS → ANALYSE → LOCK → OUTILS
          Style BIONIC: bg-black/60, border-gray-700/40, rounded-lg, icônes Lucide
          ════════════════════════════════════════════════════════════════ */}
      <nav className="flex-shrink-0 h-[44px] bg-[#0d0d14] border-b border-[#1a1a2e] px-4 flex items-center relative z-40" data-testid="bionic-tabs">
        <div className="flex items-center gap-0.5 bg-black/60 backdrop-blur-sm rounded-lg border border-gray-700/40 p-1">
          {/* ═══ 1. SAISON — masqué en mode Split (chaque panneau a le sien) ═══ */}
          {!splitViewEnabled && (
            <>
              <BiologicalSeasonSelector
                selectedSeason={selectedBiologicalSeason}
                onSeasonChange={setSelectedBiologicalSeason}
              />
              <div className="w-px h-5 bg-gray-700/50 mx-0.5" />
            </>
          )}

          {/* ═══ 2. SPLIT ═══ */}
          <button
            onClick={toggleSplitView}
            className={`h-8 px-2.5 flex items-center gap-1.5 rounded-md text-[11px] font-bold uppercase tracking-wider transition-all duration-150 flex-shrink-0 ${
              splitViewEnabled
                ? 'bg-[#3CB371]/15 text-[#3CB371]'
                : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'
            }`}
            data-testid="split-view-toggle"
            title="Comparer deux saisons"
          >
            <SplitSquareHorizontal className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Split</span>
          </button>
          <div className="w-px h-5 bg-gray-700/50 mx-0.5" />

          {/* ═══ 3. CARTE — V8.3.A: fermeture auto après sélection ═══ */}
          <Popover open={cartePopoverOpen} onOpenChange={setCartePopoverOpen}>
            <PopoverTrigger asChild>
              <button className="h-8 px-2.5 flex items-center gap-1.5 rounded-md text-[11px] font-bold uppercase tracking-wider text-[#f5a623] hover:bg-white/5 transition-all" data-testid="toolbar-carte-btn" title="Fond de Carte">
                <Map className="h-3.5 w-3.5" />
                <span className="hidden sm:inline">Carte</span>
              </button>
            </PopoverTrigger>
            <PopoverContent align="start" sideOffset={8} className="w-80 bg-gray-950/95 backdrop-blur-md border-gray-700/60 p-3 shadow-xl shadow-black/40">
              <BionicMapSelector
                currentMapType={mapType}
                onMapTypeChange={handleMapTypeChangeAndClose}
                mapOptions={mapOptions}
                onOptionsChange={setMapOptions}
                variant="panel"
                showOptions={true}
              />
            </PopoverContent>
          </Popover>
          <div className="w-px h-5 bg-gray-700/50 mx-0.5" />

          {/* ═══ 3b. ESPÈCE — Sélecteur rapide ═══ */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className="h-8 px-2.5 flex items-center gap-1.5 rounded-md text-[11px] font-bold uppercase tracking-wider text-amber-400 hover:bg-white/5 transition-all"
                data-testid="toolbar-species-btn"
                title="Espèce cible"
              >
                <Target className="h-3.5 w-3.5" />
                <span className="hidden sm:inline">{SPECIES_LIST.find(s => s.id === selectedSpecies)?.name || 'Espèce'}</span>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="bg-gray-950 border-gray-700/60 shadow-xl" side="bottom" align="start">
              {SPECIES_LIST.map(sp => (
                <DropdownMenuItem
                  key={sp.id}
                  onClick={() => setSelectedSpecies(sp.id)}
                  className={`cursor-pointer ${selectedSpecies === sp.id ? 'text-amber-400 bg-amber-500/10' : 'text-white hover:bg-white/10'}`}
                  data-testid={`species-quick-${sp.id}`}
                >
                  <div className="w-2.5 h-2.5 rounded-full mr-2 flex-shrink-0" style={{ backgroundColor: sp.color }} />
                  {sp.name}
                  {selectedSpecies === sp.id && <CheckCircle className="h-3 w-3 ml-auto text-amber-400" />}
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
          <div className="w-px h-5 bg-gray-700/50 mx-0.5" />

          {/* ═══ 4. OBSERVATION ═══ */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className={`h-8 px-2.5 flex items-center gap-1.5 rounded-md text-[11px] font-bold uppercase tracking-wider transition-all ${
                  ['waypoints','lieux','groupe','exclusions'].includes(activeTab)
                    ? 'bg-white/10 text-white'
                    : 'text-[#FF9800] hover:bg-white/5'
                }`}
                data-testid="toolbar-observation-btn"
                title="Observation"
              >
                <Binoculars className="h-3.5 w-3.5" />
                <span className="hidden sm:inline">Observation</span>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="bg-gray-950 border-gray-700/60 shadow-xl" side="bottom" align="start">
              <DropdownMenuItem onClick={() => setActiveTab(prev => prev === 'waypoints' ? 'carte' : 'waypoints')} className="text-white hover:bg-white/10 cursor-pointer" data-testid="obs-waypoints-item">
                <MapPin className="h-4 w-4 mr-2 text-[#FF9800]" /> Waypoints
                {activeWaypoints.length > 0 && <span className="ml-auto text-[9px] bg-[#3CB371] text-black rounded-full px-1.5 py-0.5 font-bold">{activeWaypoints.length}</span>}
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setActiveTab(prev => prev === 'lieux' ? 'carte' : 'lieux')} className="text-white hover:bg-white/10 cursor-pointer" data-testid="obs-lieux-item">
                <BookMarked className="h-4 w-4 mr-2 text-[#3b82f6]" /> Lieux
                {savedPlaces.length > 0 && <span className="ml-auto text-[9px] bg-[#3b82f6] text-white rounded-full px-1.5 py-0.5 font-bold">{savedPlaces.length}</span>}
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-gray-700/50" />
              <DropdownMenuItem onClick={() => setActiveTab(prev => prev === 'groupe' ? 'carte' : 'groupe')} className="text-white hover:bg-white/10 cursor-pointer" data-testid="obs-groupe-item">
                <Users className="h-4 w-4 mr-2 text-[#f5a623]" /> Groupe
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setActiveTab(prev => prev === 'exclusions' ? 'carte' : 'exclusions')} className="text-white hover:bg-white/10 cursor-pointer" data-testid="obs-exclusions-item">
                <Shield className="h-4 w-4 mr-2 text-[#06b6d4]" /> Exclusions
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <div className="w-px h-5 bg-gray-700/50 mx-0.5" />

          {/* ═══ 5. LAYERS ═══ */}
          <Popover>
            <PopoverTrigger asChild>
              <button className="relative h-8 px-2.5 flex items-center gap-1.5 rounded-md text-[11px] font-bold uppercase tracking-wider text-[#10b981] hover:bg-white/5 transition-all" data-testid="toolbar-layers-btn" title="Couches">
                <Layers className="h-3.5 w-3.5" />
                <span className="hidden sm:inline">Layers</span>
                {activeCount > 0 && <span className="absolute -top-0.5 -right-0.5 min-w-[14px] h-[14px] rounded-full bg-[#f5a623] text-black text-[8px] font-bold flex items-center justify-center leading-none px-0.5">{activeCount}</span>}
              </button>
            </PopoverTrigger>
            <PopoverContent align="start" sideOffset={8} className="w-72 bg-gray-950/95 backdrop-blur-md border-gray-700/60 p-0 shadow-xl shadow-black/40">
              <div className="px-3 py-2 border-b border-gray-800 flex items-center gap-2">
                <Layers className="h-3.5 w-3.5 text-[#10b981]" />
                <span className="text-xs font-semibold text-white">Couches BIONIC</span>
              </div>
              <div className="p-3 max-h-[60vh] overflow-y-auto space-y-2">
                <div className="flex gap-1 mb-2">
                  <button onClick={showAllLayers} className="flex-1 text-xs h-7 px-2 rounded border border-gray-700 hover:bg-emerald-600/20 hover:text-emerald-400 text-gray-400 transition-colors">Tout</button>
                  <button onClick={hideAllLayers} className="flex-1 text-xs h-7 px-2 rounded border border-gray-700 hover:bg-red-600/20 hover:text-red-400 text-gray-400 transition-colors">Aucun</button>
                </div>
                <div className="space-y-1 max-h-48 overflow-y-auto">
                  {allLayers.map(layer => (
                    <button
                      key={layer.id}
                      onClick={() => toggleLayer(layer.id)}
                      className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-xs transition-all ${
                        layersVisible[layer.id]
                          ? 'bg-[#f5a623]/10 text-white border border-[#f5a623]/30'
                          : 'bg-gray-900/50 text-gray-400 hover:bg-gray-800/50'
                      }`}
                      data-testid={`layer-toggle-${layer.id}`}
                    >
                      <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: layersVisible[layer.id] ? layer.color : '#4b5563' }} />
                      <span className="flex-1 text-left truncate">{layer.name}</span>
                      {layersVisible[layer.id] && <CheckCircle className="h-3 w-3 text-[#f5a623]" />}
                    </button>
                  ))}
                </div>
                <div className="pt-2 border-t border-gray-700/50">
                  <button
                    onClick={() => setShowExclusionOverlay(!showExclusionOverlay)}
                    className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-xs transition-all ${
                      showExclusionOverlay
                        ? 'bg-red-500/10 text-white border border-red-500/30'
                        : 'bg-gray-900/50 text-gray-400 hover:bg-gray-800/50'
                    }`}
                    data-testid="layer-toggle-exclusion-overlay"
                  >
                    <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: showExclusionOverlay ? '#F44336' : '#4b5563' }} />
                    <span className="flex-1 text-left">Exclusions (debug)</span>
                    {showExclusionOverlay && <CheckCircle className="h-3 w-3 text-red-400" />}
                  </button>
                  <button
                    onClick={() => setShowWindFlow(!showWindFlow)}
                    className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-xs transition-all mt-1 ${
                      showWindFlow
                        ? 'bg-cyan-500/10 text-white border border-cyan-500/30'
                        : 'bg-gray-900/50 text-gray-400 hover:bg-gray-800/50'
                    }`}
                    data-testid="layer-toggle-wind-flow"
                  >
                    <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: showWindFlow ? '#06b6d4' : '#4b5563' }} />
                    <span className="flex-1 text-left">Vent directionnel</span>
                    {showWindFlow && <CheckCircle className="h-3 w-3 text-cyan-400" />}
                  </button>
                  {showWindFlow && (
                    <div className="flex gap-1 mt-1 ml-4">
                      <button
                        onClick={() => setWindMode('arrows')}
                        className={`px-2 py-0.5 rounded text-[9px] transition-all ${
                          windMode === 'arrows'
                            ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                            : 'bg-gray-900/50 text-gray-500 hover:text-gray-300'
                        }`}
                        data-testid="wind-mode-arrows"
                      >
                        Minimaliste
                      </button>
                      <button
                        onClick={() => setWindMode('particles')}
                        className={`px-2 py-0.5 rounded text-[9px] transition-all ${
                          windMode === 'particles'
                            ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                            : 'bg-gray-900/50 text-gray-500 hover:text-gray-300'
                        }`}
                        data-testid="wind-mode-particles"
                      >
                        Particules
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </PopoverContent>
          </Popover>
          <div className="w-px h-5 bg-gray-700/50 mx-0.5" />

          {/* ═══ 6. ANALYSE / STATS ═══ */}
          <button
            onClick={() => setActiveTab(prev => prev === 'analyse' ? 'carte' : 'analyse')}
            className={`h-8 px-2.5 flex items-center gap-1.5 rounded-md text-[11px] font-bold uppercase tracking-wider transition-all ${
              activeTab === 'analyse'
                ? 'bg-[#a855f7]/15 text-[#a855f7]'
                : 'text-[#a855f7] hover:bg-white/5'
            }`}
            data-testid="toolbar-analyse-btn"
            title="Analyse & Statistiques"
          >
            <BarChart3 className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Analyse</span>
          </button>
          <div className="w-px h-5 bg-gray-700/50 mx-0.5" />

          {/* ═══ 7. LOCK ═══ */}
          <button
            onClick={() => setPrivacyMode(!privacyMode)}
            className={`h-8 w-8 flex items-center justify-center rounded-md transition-all ${
              privacyMode ? 'bg-red-500/15 text-red-400' : 'text-green-500 hover:bg-white/5'
            }`}
            data-testid="toolbar-lock-btn"
            title={privacyMode ? 'Mode privé activé' : 'Mode public'}
          >
            {privacyMode ? <Lock className="h-3.5 w-3.5" /> : <Unlock className="h-3.5 w-3.5" />}
          </button>
          <div className="w-px h-5 bg-gray-700/50 mx-0.5" />

          {/* ═══ 8. OUTILS SECONDAIRES ═══ */}
          <Popover>
            <PopoverTrigger asChild>
              <button className="h-8 px-2.5 flex items-center gap-1.5 rounded-md text-[11px] font-bold uppercase tracking-wider text-gray-400 hover:text-white hover:bg-white/5 transition-all" data-testid="toolbar-outils-btn" title="Outils secondaires">
                <Settings className="h-3.5 w-3.5" />
                <span className="hidden sm:inline">Outils</span>
              </button>
            </PopoverTrigger>
            <PopoverContent align="end" sideOffset={8} className="w-80 bg-gray-950/95 backdrop-blur-md border-gray-700/60 p-0 shadow-xl shadow-black/40">
              <div className="px-3 py-2 border-b border-gray-800 flex items-center gap-2">
                <Settings className="h-3.5 w-3.5 text-gray-400" />
                <span className="text-xs font-semibold text-white">Outils secondaires</span>
              </div>
              <div className="p-3 max-h-[70vh] overflow-y-auto space-y-4">
                {/* Espèce cible */}
                <div>
                  <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Espèce cible</div>
                  <div className="space-y-1">
                    {SPECIES_LIST.map(sp => (
                      <button
                        key={sp.id}
                        onClick={() => setSelectedSpecies(sp.id)}
                        data-testid={`species-btn-${sp.id}`}
                        className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-xs transition-all ${
                          selectedSpecies === sp.id
                            ? 'bg-amber-500/20 text-white border border-amber-500/40'
                            : 'bg-gray-900/50 text-gray-400 hover:bg-gray-800/50'
                        }`}
                      >
                        <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: sp.color }} />
                        <span className="flex-1 text-left">{sp.name}</span>
                        {selectedSpecies === sp.id && <CheckCircle className="h-3 w-3 text-amber-400" />}
                      </button>
                    ))}
                  </div>
                </div>
                {/* Affichage */}
                <div>
                  <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-2">Affichage</div>
                  <div className="space-y-2 bg-gray-900/50 rounded-lg p-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-300">Corridors V9</span>
                      <Switch checked={showCorridors} onCheckedChange={setShowCorridors} className="scale-75 data-[state=checked]:bg-cyan-500" data-testid="toggle-corridors-v9" />
                    </div>
                    {/* LEGACY: Deplacements V1 — SUPPRIME definitvement. BCE-4X-UI-003 */}
                    <div className="space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-300">Seuil minimum</span>
                        <span className="text-xs font-semibold text-[#f5a623]">{minPercentageFilter}%</span>
                      </div>
                      <input
                        type="range" min="30" max="80" step="5"
                        value={minPercentageFilter}
                        onChange={(e) => setMinPercentageFilter(parseInt(e.target.value))}
                        className="w-full h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-[#f5a623]"
                        data-testid="min-percentage-slider"
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-300">Curseur BIONIC</span>
                      <Switch checked={showCursorBionic} onCheckedChange={setShowCursorBionic} className="scale-75 data-[state=checked]:bg-violet-500" />
                    </div>
                  </div>
                </div>
              </div>
            </PopoverContent>
          </Popover>
        </div>
      </nav>

      {/* ════════════════════════════════════════════════════════════════
          SECTION 4+5 — CARTE DOMINANTE + PANNEAU LATÉRAL
          La carte occupe toujours l'espace principal.
          Un panneau latéral s'ouvre selon l'onglet actif.
          ════════════════════════════════════════════════════════════════ */}
      <div className="flex-1 flex overflow-hidden min-h-0">
        {/* ── CARTE BIONIC — ZONE DOMINANTE (80%+ de l'écran) ── */}
        <div className="flex-1 relative">
          {/* Indicateur du mode création de waypoint */}
          {mapClickMode && (
            <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-[1000] bg-green-500 text-black px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 animate-pulse">
              <Crosshair className="h-5 w-5" />
              <span className="text-sm font-medium">Cliquez sur la carte pour placer votre waypoint</span>
              <button onClick={() => setMapClickMode(false)} className="ml-2 hover:bg-green-600 rounded p-0.5"><X className="h-4 w-4" /></button>
            </div>
          )}
            
          {/* V8.1: Mode Split View ou Mode normal */}
          {splitViewEnabled ? (
            <SplitViewContainer
              mapCenter={splitMapCenter || [currentMapCenter.lat, currentMapCenter.lng]}
              mapZoom={splitMapZoom || currentZoom}
              mapRef={mapRef}
              activeEcoLayers={activeEcoLayers}
              ecoLayerOpacities={ecoLayerOpacities}
              ecoMapStatus={ecoMapStatus}
              activeFallback={activeFallback}
              classificationToggles={classificationToggles}
              showExclusionOverlay={showExclusionOverlay}
              showWindFlow={showWindFlow}
              windMode={windMode}
              showCorridorsV1={showCorridorsV1}
              showCorridors={showCorridors}
              showCursorBionic={showCursorBionic}
              isPrivateDataVisible={isPrivateDataVisible}
              privacyMode={privacyMode}
              minPercentageFilter={minPercentageFilter}
              selectedSpecies={selectedSpecies}
              temporalHourMT={temporalHourMT}
              layersVisible={layersVisible}
              selectedWaypointForZones={selectedWaypointForZones}
              bboxBounds={bboxBounds}
              activeWaypoints={activeWaypoints}
              savedPlaces={savedPlaces}
              selectWaypointAsTarget={selectWaypointAsTarget}
              setContextMenuMT={setContextMenuMT}
              isZoneFavorite={isZoneFavorite}
              addFavorite={addFavorite}
              getFavoriteId={getFavoriteId}
              removeFavorite={removeFavorite}
              setSelectedZone={setSelectedZone}
              setHoveredZone={setHoveredZone}
              userPosition={userPosition}
              userId={userId}
              syncToBackend={syncToBackend}
              groupMembersPositions={groupMembersPositions}
              isGroupeTrackingActive={isGroupeTrackingActive}
              handleZoomChange={handleZoomChange}
              handleMapMove={handleMapMove}
              handleBoundsChange={handleBoundsChange}
              mapClickMode={mapClickMode}
              handleMapClickForWaypoint={handleMapClickForWaypoint}
              leftSeason={selectedBiologicalSeason}
              rightSeason={splitRightSeason}
              onLeftSeasonChange={setSelectedBiologicalSeason}
              onRightSeasonChange={setSplitRightSeason}
              leftZonesData={{ zones: bionicZones, corridors: bionicZonesData.corridors || [], stats: bionicZonesData.stats }}
              rightZonesData={splitRightZonesData}
              pipelineState={pipelineState}
            />
          ) : (
          <>
          {/* ── MapContainer — CARTE PRINCIPALE (composant extrait IM1.2) ── */}
          <MapContainer center={mapCenter} zoom={mapZoom} className={`absolute inset-0 w-full h-full ${mapClickMode ? 'cursor-crosshair' : ''}`} zoomControl={false} style={{ background: '#0a0a0f' }}>
            <MapContent
              activeEcoLayers={activeEcoLayers}
              ecoLayerOpacities={ecoLayerOpacities}
              ecoMapStatus={ecoMapStatus}
              activeFallback={activeFallback}
              mapRef={mapRef}
              handleZoomChange={handleZoomChange}
              handleMapMove={handleMapMove}
              handleBoundsChange={handleBoundsChange}
              mapClickMode={mapClickMode}
              handleMapClickForWaypoint={handleMapClickForWaypoint}
              classificationToggles={classificationToggles}
              showExclusionOverlay={showExclusionOverlay}
              showWindFlow={showWindFlow}
              windMode={windMode}
              showCorridorsV1={showCorridorsV1}
              showCorridors={showCorridors}
              showCursorBionic={showCursorBionic}
              isPrivateDataVisible={isPrivateDataVisible}
              privacyMode={privacyMode}
              bionicZones={bionicZones}
              bionicZonesData={bionicZonesData}
              minPercentageFilter={minPercentageFilter}
              selectedSpecies={selectedSpecies}
              temporalHourMT={temporalHourMT}
              layersVisible={layersVisible}
              selectedWaypointForZones={selectedWaypointForZones}
              bboxBounds={bboxBounds}
              activeWaypoints={activeWaypoints}
              savedPlaces={savedPlaces}
              selectWaypointAsTarget={selectWaypointAsTarget}
              setContextMenuMT={setContextMenuMT}
              isZoneFavorite={isZoneFavorite}
              addFavorite={addFavorite}
              getFavoriteId={getFavoriteId}
              removeFavorite={removeFavorite}
              setSelectedZone={setSelectedZone}
              setHoveredZone={setHoveredZone}
              userPosition={userPosition}
              userId={userId}
              syncToBackend={syncToBackend}
              groupMembersPositions={groupMembersPositions}
              isGroupeTrackingActive={isGroupeTrackingActive}
              huntingPathData={huntingPathData}
              showHuntingPath={showHuntingPath}
            />
          </MapContainer>

          {/* C14 BIONIC 1000%: Charte visuelle + état pipeline */}
          <BionicLegend
            pipelineState={pipelineState}
            zoneCount={bionicZones.length}
            corridorCount={(bionicZonesData.corridors || []).length}
            windDeg={225}
          />


          {/* ── Contrôles carte — gauche ── */}
          <div className="absolute top-4 left-3 z-[1000] flex flex-col gap-2">
            <button className="bg-[#111118]/90 text-white border border-[#1a1a2e] h-8 w-8 rounded-lg flex items-center justify-center hover:bg-[#1a1a2e] transition-colors" onClick={() => { if (mapRef.current) mapRef.current.setZoom(mapRef.current.getZoom() + 1); }}>+</button>
            <button className="bg-[#111118]/90 text-white border border-[#1a1a2e] h-8 w-8 rounded-lg flex items-center justify-center hover:bg-[#1a1a2e] transition-colors" onClick={() => { if (mapRef.current) mapRef.current.setZoom(Math.max(5, mapRef.current.getZoom() - 1)); }}>-</button>
            <button className={`${userPosition ? 'bg-blue-600' : 'bg-[#111118]/90'} text-white border border-[#1a1a2e] h-8 w-8 rounded-lg flex items-center justify-center hover:bg-[#1a1a2e] transition-colors`} onClick={centerOnUser}>
              <LocateFixed className="h-4 w-4" />
            </button>
          </div>

          {/* ── Bouton + Waypoint déplacé dans la toolbar (Passe 3 UX) ── */}
          </>
          )}
        </div>

        {/* ══════════════════════════════════════════════════════════════
            SECTION 5 — PANNEAUX LATÉRAUX (UN PAR ONGLET)
            ══════════════════════════════════════════════════════════════ */}
        <div className="w-80 flex-shrink-0 bg-[#0d0d14] border-l border-[#1a1a2e] overflow-y-auto" data-testid="side-panel">
          {/* ── BIONIC V5 300% — Panneau Diagnostique ULTIME (priorité absolue) ── */}
          {selectedZone && (
            <BionicZoneDiagnosticPanel
              zone={selectedZone}
              onClose={() => setSelectedZone(null)}
              onAddWaypoint={(zone) => {
                const name = prompt(`Nom pour ce waypoint (zone ${BIONIC_MODULES[zone.layerId]?.label || zone.layerId}) ?`, `Zone ${BIONIC_MODULES[zone.layerId]?.label}`);
                if (name && zone.positions?.[0]) {
                  const center = zone.positions.reduce((acc, p) => [acc[0] + p[0] / zone.positions.length, acc[1] + p[1] / zone.positions.length], [0, 0]);
                  handleMapClickForWaypoint({ latlng: { lat: center[0], lng: center[1] } });
                }
                setSelectedZone(null);
              }}
            />
          )}
          {/* ── Panneau Carte → Zones (composant extrait IM1) ── */}
          {activeTab === 'carte' && !selectedZone && (
            <SidePanelZones
              currentZoom={currentZoom}
              isLoadingZones={isLoadingZones}
              pipelineState={pipelineState}
              zoneSource={zoneSource}
              visibleZonesCount={visibleZonesCount}
              reloadZones={reloadZones}
              activeWaypoints={activeWaypoints}
              corridors={bionicZonesData.corridors || []}
              selectedWaypointForZones={selectedWaypointForZones}
              clearWaypointTarget={clearWaypointTarget}
              handleDeleteWaypoint={handleDeleteWaypoint}
              handleGenerateSnapshot={handleGenerateSnapshot}
              rejectionDiagnostics={bionicZonesData.rejection_diagnostics}
              weatherMetadata={weatherMetadata}
              zones={bionicZonesData.zones || []}
              species={selectedSpecies}
              displayScore={displayScore}
              rating={rating}
              amenagementReport={amenagementReport}
              showHuntingPath={showHuntingPath}
              setShowHuntingPath={setShowHuntingPath}
            />
          )}

          {/* ── Panneau Waypoints ── */}
          {activeTab === 'waypoints' && !selectedZone && (
            <WaypointUnifiedPanel
              waypoints={waypoints}
              activeWaypoints={activeWaypoints}
              selectedWaypoint={selectedWaypointForZones}
              onSelectWaypoint={(wp) => selectWaypointAsTarget(wp)}
              onDeselectWaypoint={() => setSelectedWaypointForZones(null)}
              onDeleteWaypoint={(id) => handleDeleteWaypoint(id)}
              onToggleActive={(id) => toggleWaypointActive(id)}
              onAnalyze={(wp) => { selectWaypointAsTarget(wp); setActiveTab('carte'); }}
              onShare={(wp) => openShareDialog(wp)}
              onCenterMap={(wp) => { if (mapRef.current) mapRef.current.setView([wp.lat, wp.lng], 14); setActiveTab('carte'); }}
              userPosition={userPosition}
              watchingPosition={watchingPosition}
              onStartWatching={startWatchingPosition}
              onStopWatching={stopWatchingPosition}
              layersVisible={layersVisible}
              currentMapCenter={currentMapCenter}
              PLACE_TYPES={PLACE_TYPES}
              onGenerateSnapshot={handleGenerateSnapshot}
              isGeneratingSnapshot={isGeneratingSnapshot}
              snapshotData={snapshotData}
              compareSelection={compareSelection}
              onToggleCompare={handleToggleCompare}
              onLaunchCompare={handleLaunchCompare}
            />
          )}

          {/* ── Panneau Lieux ── */}
          {activeTab === 'lieux' && !selectedZone && (
            <PlacesSidePanel
              savedPlaces={savedPlaces}
              PLACE_TYPES={PLACE_TYPES}
              onAddPlace={() => setShowAddPlaceDialog(true)}
              onAddPlaceWithType={(typeId) => { setNewPlace({ name: '', type: typeId, lat: '', lng: '', notes: '' }); setShowAddPlaceDialog(true); }}
              onCenterOnPlace={(place) => { if (mapRef.current) mapRef.current.setView([place.lat, place.lng], 13); setActiveTab('carte'); }}
              onEditPlace={(place) => setEditingPlace(place)}
              onDeletePlace={(id) => deletePlace(id)}
            />
          )}

          {/* ── Panneau Groupe ── */}
          {activeTab === 'groupe' && !selectedZone && (
            <div className="h-full" data-testid="panel-groupe">
              <GroupeTab groupId="territory_group" userId={userId} compact={true} />
            </div>
          )}

          {/* ── Panneau Analyse ── */}
          {activeTab === 'analyse' && !selectedZone && (
            <AnalysisSidePanel
              displayScore={displayScore}
              rating={rating}
              categoryScores={categoryScores}
              visibleZonesCount={visibleZonesCount}
              activeWaypointsCount={activeWaypoints.length}
              selectedSpecies={selectedSpecies}
              activeLayersCount={activeCount}
              selectedWaypointForZones={selectedWaypointForZones}
              onGenerateSnapshot={handleGenerateSnapshot}
            />
          )}

          {/* ── Panneau Exclusions ── */}
          {activeTab === 'exclusions' && !selectedZone && (
            <DiagnosticExclusionsPanel
              hoveredZone={hoveredZone}
              selectedZone={selectedZone}
              onClearZone={() => { setHoveredZone(null); setSelectedZone(null); }}
              activeWaypoints={activeWaypoints}
              visibleZonesCount={visibleZonesCount}
              isLoadingExclusions={isLoadingExclusions}
              terrainExclusions={terrainExclusions}
              currentMapCenter={currentMapCenter}
              alerts={alerts}
              unreadAlertCount={unreadAlertCount}
              markAlertRead={markAlertRead}
              markAllAlertsRead={markAllAlertsRead}
              checkOptimalConditions={checkOptimalConditions}
              favoritesLoading={favoritesLoading}
              favorites={favorites}
              removeFavorite={removeFavorite}
              updateAlertSettings={updateAlertSettings}
              getZoneConditions={getZoneConditions}
              displayScore={displayScore}
              categoryScores={categoryScores}
              bionicStats={bionicStats}
            />
          )}
        </div>
      </div>
      
      {/* ═══ DIALOGUES (composants extraits IM1) ═══ */}
      <EditPlaceDialog editingPlace={editingPlace} setEditingPlace={setEditingPlace} handleUpdatePlace={handleUpdatePlace} PLACE_TYPES={PLACE_TYPES} />
      <AddPlaceDialog open={showAddPlaceDialog} onOpenChange={setShowAddPlaceDialog} newPlace={newPlace} setNewPlace={setNewPlace} handleAddPlace={handleAddPlace} useCurrentPositionForNewPlace={useCurrentPositionForNewPlace} PLACE_TYPES={PLACE_TYPES} />
      <AddWaypointDialog open={showAddWaypointDialog} onOpenChange={setShowAddWaypointDialog} newWaypoint={newWaypoint} setNewWaypoint={setNewWaypoint} handleAddWaypointFromDialog={handleAddWaypointWithWind} useCurrentPositionForNewWaypoint={useCurrentPositionForNewWaypoint} PLACE_TYPES={PLACE_TYPES} />
      <ShareDialog open={showShareDialog} onOpenChange={setShowShareDialog} waypoint={waypointToShare} userId={userId} onShared={() => { setShowShareDialog(false); setWaypointToShare(null); }} />
      <CreateGroupDialog open={showCreateGroupDialog} onOpenChange={setShowCreateGroupDialog} userId={userId} onCreated={(group) => { toast.success(`Groupe "${group.name}" créé !`, { description: `Code d'invitation: ${group.invite_code}` }); refreshGroups(); }} />
      <GroupDashboardDialog open={showGroupDashboard} onOpenChange={setShowGroupDashboard} group={selectedGroup} userId={userId} onClose={() => { setShowGroupDashboard(false); setSelectedGroup(null); }} />

      {/* CONTEXT MENU: Right-click waypoint menu (Mon Territoire) */}
      {contextMenuMT && (
        <WaypointContextMenu
          position={contextMenuMT.position}
          waypoint={contextMenuMT.waypoint}
          onClose={() => setContextMenuMT(null)}
          onDelete={async (id) => {
            handleDeleteWaypoint(id);
          }}
          onAnalyze={(wp) => selectWaypointAsTarget(wp)}
          onEdit={(wp) => selectWaypointAsTarget(wp)}
        />
      )}

      {/* V8.3.A: Widget de comparaison multi-waypoints */}
      {showCompareWidget && compareSelection.length >= 2 && (
        <CompareWidget
          waypoints={compareSelection}
          onClose={handleCloseCompare}
        />
      )}
    </div>
  );
};

export default MonTerritoireBionicPage;
