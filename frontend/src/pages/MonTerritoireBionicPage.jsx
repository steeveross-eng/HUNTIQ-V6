/**
 * MonTerritoireBionicPage - Page dédiée Mon Territoire BIONIC™
 * VERSION: 7.3.0 — IM1 Refactorisation modulaire
 * 
 * Architecture: Composant orchestrateur qui delegue aux sous-composants:
 * - MapHelpers: composants Leaflet utilitaires
 * - TerritoireHeader: header score/meteo/LIVE
 * - TerritoireDialogs: toutes les modales
 * - IntelligenceDashboard: cockpit central flottant INTELLIGENCE
 * - useGeolocation: hook geolocalisation
 * - placeTypes: constantes types de lieux
 */

import React, { useState, useCallback, useMemo, useEffect, useLayoutEffect, useRef } from 'react';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { MapContainer } from 'react-leaflet';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Crosshair, Target, MapPin, Plus, X, LocateFixed,
  BookMarked, Users, Shield, SplitSquareHorizontal,
  Map, Binoculars, Layers, Lock, Unlock, BarChart3, CheckCircle, Flame, Droplets,
} from 'lucide-react';
import { useLanguage } from '@/contexts/LanguageContext';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/popover';
import { Switch } from '@/components/ui/switch';
import useBionicSession from '@/hooks/useBionicSession';
import useBionicLayers from '@/hooks/useBionicLayers';
import { TerritoireToolbar } from '@/components/territoire/ui/TerritoireToolbar';
import { NutritionPanel } from '@/components/territoire/ui/NutritionPanel';
import { TerritoireDialogs } from '@/components/territoire/ui/TerritoireDialogs';
import useBionicWeather from '@/hooks/useBionicWeather';
import useBionicScoring from '@/hooks/useBionicScoring';
import { useUserData } from '@/hooks/useUserData';
import { useNotifications, useHuntingGroups } from '@/hooks/useSharing';
import WaypointUnifiedPanel from '@/components/territoire/WaypointUnifiedPanel';
import { useAuth } from '@/components/GlobalAuth';
import DiagnosticExclusionsPanel from '@/components/territoire/DiagnosticExclusionsPanel';
import BionicZoneDiagnosticPanel from '@/components/territoire/BionicZoneDiagnosticPanel';
import PlacesSidePanel from '@/components/territoire/PlacesSidePanel';
import IntelligenceDashboard from '@/components/territoire/IntelligenceDashboard';
import useSpatialClipping from '@/hooks/useSpatialClipping';
import { BIONIC_MODULES } from '@/core/bionic';
import { SPECIES_LIST } from '@/core/bionic/speciesConfig';
import { useZoneOrchestrator } from '@/hooks/useZoneOrchestrator';
import { useZoneFavorites } from '@/components/territoire/ZoneFavorites';
import { GroupeTab, useGroupeTracking } from '@/modules/groupe';
// P2: EcologicalPanel — module gele (FROZEN)
import { 
  useEcoMapFallback,
} from '@/components/territoire/EcoforestryLayers';
// Import BIONIC Map Selector
import BionicMapSelector from '@/components/maps/BionicMapSelector';
import useMapType from '@/hooks/useMapType';
import { MAP_TYPES } from '@/config/mapSources';
import { BionicScoreBadge } from '@/components/territoire/BionicScoreBadge';

// P2: BIONIC_COLORS migrated to component-level CSS variables

// IM1 — Modules extraits
import { useGeolocation } from '@/hooks/useGeolocation';
import { useZoneToasts, useAmenagementEngine, useSnapshotExport, useCategoryScores } from '@/hooks/useTerritoireEffects';
import { PLACE_TYPES } from '@/config/placeTypes';
import { TerritoireHeader } from '@/components/territoire/ui/TerritoireHeader';
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

/**
 * BCE-4X: Point-in-polygon (ray casting) pour exclusion hydro
 * Vérifie si un point (lat, lng) est à l'intérieur d'un polygone
 */
function _pointInPolygon(lat, lng, polygon) {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const pi = polygon[i], pj = polygon[j];
    const piLat = Array.isArray(pi) ? pi[0] : (pi.lat || 0);
    const piLng = Array.isArray(pi) ? pi[1] : (pi.lng || pi.lon || 0);
    const pjLat = Array.isArray(pj) ? pj[0] : (pj.lat || 0);
    const pjLng = Array.isArray(pj) ? pj[1] : (pj.lng || pj.lon || 0);
    if (((piLng > lng) !== (pjLng > lng)) &&
        (lat < (pjLat - piLat) * (lng - piLng) / (pjLng - piLng) + piLat)) {
      inside = !inside;
    }
  }
  return inside;
}

const MonTerritoireBionicPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { t } = useLanguage();

  // ═══ HOTSPOT DEEP LINK — lecture des query params ═══
  const hotspotDeepLink = useRef({
    lat: searchParams.get('lat') ? parseFloat(searchParams.get('lat')) : null,
    lng: searchParams.get('lng') ? parseFloat(searchParams.get('lng')) : null,
    zoom: searchParams.get('zoom') ? parseInt(searchParams.get('zoom'), 10) : null,
    layer: searchParams.get('layer') || null,
    hotspotId: searchParams.get('hotspot') || null,
  });
  const deepLinkAppliedRef = useRef(false);
  
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

  // ═══ HOTSPOT DEEP LINK — état du highlight ═══
  const [hotspotHighlight, setHotspotHighlight] = useState(null);
  const hotspotHighlightLayerRef = useRef(null);
  
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

    // Priorite ABSOLUE: Deep link hotspot depuis Admin
    const dl = hotspotDeepLink.current;
    if (!deepLinkAppliedRef.current && dl.lat && dl.lng) {
      deepLinkAppliedRef.current = true;
      initialCenterDoneRef.current = true;
      const dlZoom = dl.zoom || 15;
      mapRef.current.setView([dl.lat, dl.lng], dlZoom);

      // Activer fond Satellite si demandé
      if (dl.layer === 'satellite') {
        setMapType(MAP_TYPES.SATELLITE);
      }

      // Highlight du hotspot — cercle ~2km² + marker
      setHotspotHighlight({ lat: dl.lat, lng: dl.lng, id: dl.hotspotId });

      console.log(`[DEEP-LINK] Hotspot ${dl.hotspotId}: [${dl.lat}, ${dl.lng}] zoom ${dlZoom} layer=${dl.layer}`);
      return;
    }

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

  // ═══ HOTSPOT DEEP LINK — Rendu du highlight sur la carte ═══
  useEffect(() => {
    if (!hotspotHighlight || !mapRef.current) return;

    // Nettoyer l'ancien layer
    if (hotspotHighlightLayerRef.current) {
      mapRef.current.removeLayer(hotspotHighlightLayerRef.current);
    }

    const group = L.layerGroup();

    // Cercle externe pulsant ~2km² (rayon 800m)
    L.circle([hotspotHighlight.lat, hotspotHighlight.lng], {
      radius: 800,
      color: '#f5a623',
      fillColor: '#f5a623',
      fillOpacity: 0.08,
      weight: 2,
      dashArray: '10,6',
      className: 'hotspot-highlight-pulse',
    }).addTo(group);

    // Cercle interne
    L.circle([hotspotHighlight.lat, hotspotHighlight.lng], {
      radius: 200,
      color: '#FF6F00',
      fillColor: '#FF6F00',
      fillOpacity: 0.15,
      weight: 2,
    }).addTo(group);

    // Marker central
    L.circleMarker([hotspotHighlight.lat, hotspotHighlight.lng], {
      radius: 8,
      color: '#fff',
      fillColor: '#f5a623',
      fillOpacity: 1,
      weight: 3,
    }).bindPopup(
      `<div style="font-family:system-ui;color:#e5e5e5;background:#1a1a2e;padding:10px;border-radius:8px;min-width:180px;">
        <div style="font-weight:800;font-size:13px;color:#f5a623;margin-bottom:4px;">Hotspot ${hotspotHighlight.id || ''}</div>
        <div style="font-size:11px;color:#aaa;">${hotspotHighlight.lat.toFixed(5)}, ${hotspotHighlight.lng.toFixed(5)}</div>
        <div style="margin-top:6px;font-size:10px;color:#888;">Zone de 2 km² — Fond Satellite</div>
      </div>`,
      { className: 'bionic-popup', maxWidth: 250 }
    ).openPopup().addTo(group);

    group.addTo(mapRef.current);
    hotspotHighlightLayerRef.current = group;

    return () => {
      if (hotspotHighlightLayerRef.current && mapRef.current) {
        try { mapRef.current.removeLayer(hotspotHighlightLayerRef.current); } catch (e) {}
      }
    };
  }, [hotspotHighlight]);

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
  const showCorridors = true; // STEEVE-MAX: V10 layer permanent, contrôlé uniquement via ZONES
  const [corridorV10Data, setCorridorV10Data] = useState(null); // CORRIDORS-V10 niveau distribution
  const [minPercentageFilter, setMinPercentageFilter] = useState(30);
  
  // STEEVE-MAX UX: Contrôles couches et points chauds
  const [showZonesLayer, setShowZonesLayer] = useState(true);
  const [showCorridorsLayer, setShowCorridorsLayer] = useState(true);
  const [showPointsLayer, setShowPointsLayer] = useState(true);
  const [pointsChaudsMode, setPointsChaudsMode] = useState(false);
  const [pointsChaudsFilter, setPointsChaudsFilter] = useState('tous');

  // ALIMENTATION-V2: Salines + Recommandations
  const [showAlimentationV2, setShowAlimentationV2] = useState(true);
  const [showSalines, setShowSalines] = useState(true);
  const [showNutritionPanel, setShowNutritionPanel] = useState(false);
  const [alimentationV2Data, setAlimentationV2Data] = useState(null);
  const [nSalinesMax, setNSalinesMax] = useState(4);
  const [adminArchitecteMode, setAdminArchitecteMode] = useState(false);
  const [showHeatmapV10, setShowHeatmapV10] = useState(true);
  const [heatmapV10Data, setHeatmapV10Data] = useState(null);
  const [heatmapIncludeCorridors, setHeatmapIncludeCorridors] = useState(true);

  // STABILITÉ V2: Centre memoizé pour éviter re-render cascade dans les layers enfants
  const waypointCenter = useMemo(() => {
    if (!selectedWaypointForZones) return null;
    return {
      lat: selectedWaypointForZones.lat || selectedWaypointForZones.latitude,
      lng: selectedWaypointForZones.lng || selectedWaypointForZones.longitude,
    };
  }, [selectedWaypointForZones?.lat, selectedWaypointForZones?.lng, selectedWaypointForZones?.latitude, selectedWaypointForZones?.longitude]);

  // STEEVE-MAX V3: Sous-éléments granulaires par couche
  const [zoneSubFilters, setZoneSubFilters] = useState({
    alimentation: true, repos: true, rut: true, habitat: true, affuts: true, trajets: true, multiEngines: true,
  });
  const [corridorSubFilters, setCorridorSubFilters] = useState({
    normaux: true, intenses: true, extreme: true, saisonniers: true,
  });
  const [pointSubFilters, setPointSubFilters] = useState({
    alimentation: true, rut: true, repos: true, trajets: true, affuts: true, habitat: true, centroides: true, individuels: true,
  });
  const toggleZoneSub = (k) => setZoneSubFilters(p => ({ ...p, [k]: !p[k] }));
  const toggleCorridorSub = (k) => setCorridorSubFilters(p => ({ ...p, [k]: !p[k] }));
  const togglePointSub = (k) => setPointSubFilters(p => ({ ...p, [k]: !p[k] }));
  
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

  // Zone notifications + T4 coherence (extrait -> useTerritoireEffects)
  useZoneToasts(zeroZonesReason, isLoadingZones, bionicZonesData);

  // ============================================
  // BIONIC V5 300% — SPATIAL CLIPPING + STATE LOCKING
  // 1. Les zones sont calculées pour TOUTES les couches structurelles
  // 2. Le clipping 1km × 1km est appliqué quand un waypoint est actif
  // 3. La visibilité est appliquée au RENDU, pas au calcul
  // ============================================
  const rawZones = useMemo(() => {
    const zones = bionicZonesData?.zones || [];
    // BCE-4X: Séparer les zones hydro pour le masque d'exclusion
    const hydroZones = zones.filter(z => z.layerId === 'hydro');
    const nonHydroZones = zones.filter(z => z.layerId !== 'hydro');

    // BCE-4X: Exclure les affûts et salines dont le centroïde tombe dans une zone hydro
    // Un affût ne peut PAS être sur une surface d'eau
    if (hydroZones.length === 0) return nonHydroZones;

    const STRICT_EXCL_LAYERS = new Set(['affuts', 'salines', 'trajets']);

    return nonHydroZones.filter(z => {
      if (!STRICT_EXCL_LAYERS.has(z.layerId)) return true;
      if (!z.positions || z.positions.length === 0) return true;

      // Calculer le centroïde de la zone
      const flat = z.positions.flat ? z.positions.flat() : z.positions;
      if (flat.length === 0) return true;
      let cLat = 0, cLng = 0, count = 0;
      for (const pt of flat) {
        if (Array.isArray(pt) && pt.length >= 2) { cLat += pt[0]; cLng += pt[1]; count++; }
        else if (pt && pt.lat !== undefined) { cLat += pt.lat; cLng += (pt.lng || pt.lon); count++; }
      }
      if (count === 0) return true;
      cLat /= count; cLng /= count;

      // Vérifier si le centroïde est à l'intérieur d'une zone hydro (ray-casting simplifié)
      for (const hydro of hydroZones) {
        if (!hydro.positions || hydro.positions.length === 0) continue;
        const hFlat = hydro.positions.flat ? hydro.positions.flat() : hydro.positions;
        if (_pointInPolygon(cLat, cLng, hFlat)) {
          console.warn(`[BCE-4X] Zone ${z.layerId} exclue: centroïde sur eau [${cLat.toFixed(5)}, ${cLng.toFixed(5)}]`);
          return false;
        }
      }
      return true;
    });
  }, [bionicZonesData?.zones]);
  const bionicStats = bionicZonesData?.stats || {};
  
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
    const corridors = bionicZonesData?.corridors || [];
    
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
  }, [globalScore, bionicZones, bionicZonesData?.corridors]);
  
  const getScoreRating = (score) => {
    if (!score) return { label: 'En attente', color: 'bg-gray-700', textColor: 'text-gray-400' };
    if (score >= 85) return { label: 'Exceptionnel', color: 'bg-green-500', textColor: 'text-green-400' };
    if (score >= 70) return { label: 'Excellent', color: 'bg-lime-500', textColor: 'text-lime-400' };
    if (score >= 55) return { label: 'Bon', color: 'bg-yellow-500', textColor: 'text-yellow-400' };
    return { label: 'Modéré', color: 'bg-orange-500', textColor: 'text-orange-400' };
  };
  
  const rating = getScoreRating(displayScore);

  // Amenagement engine + hunting path (extrait -> useTerritoireEffects)
  const { huntingPathData, showHuntingPath } = useAmenagementEngine(bionicZones, selectedWaypointForZones, bionicZonesData);

  // Snapshot export (extrait -> useTerritoireEffects)
  const handleGenerateSnapshot = useSnapshotExport(selectedWaypointForZones, generateSnapshot, selectedSpecies, layersVisible, temporalHourMT, currentZoom);

  // Category scores (extrait -> useTerritoireEffects)
  const categoryScores = useCategoryScores(scores, currentMapCenter);

  return (
    <div className="fixed inset-0 bg-[#0a0a0f] overflow-hidden flex flex-col" style={{ paddingTop: '64px' }} data-testid="mon-territoire-bionic-page">
      {/* ═══ SECTION 1 — HEADER (composant extrait IM1) ═══ */}
      <TerritoireHeader
        navigate={navigate}
        liveMode={liveMode}
        setLiveMode={setLiveMode}
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
          P0 UX — TOOLBAR UNIFIEE (composant extrait STEEVE-MAX P0)
          ════════════════════════════════════════════════════════════════ */}
      <TerritoireToolbar
        activeTab={activeTab} setActiveTab={setActiveTab}
        splitViewEnabled={splitViewEnabled} toggleSplitView={toggleSplitView}
        selectedBiologicalSeason={selectedBiologicalSeason} setSelectedBiologicalSeason={setSelectedBiologicalSeason}
        selectedSpecies={selectedSpecies} setSelectedSpecies={setSelectedSpecies}
        mapType={mapType} mapOptions={mapOptions} setMapOptions={setMapOptions}
        cartePopoverOpen={cartePopoverOpen} setCartePopoverOpen={setCartePopoverOpen}
        handleMapTypeChangeAndClose={handleMapTypeChangeAndClose}
        showZonesLayer={showZonesLayer} setShowZonesLayer={setShowZonesLayer}
        showCorridorsLayer={showCorridorsLayer} setShowCorridorsLayer={setShowCorridorsLayer}
        showPointsLayer={showPointsLayer} setShowPointsLayer={setShowPointsLayer}
        zoneSubFilters={zoneSubFilters} toggleZoneSub={toggleZoneSub}
        corridorSubFilters={corridorSubFilters} toggleCorridorSub={toggleCorridorSub}
        pointSubFilters={pointSubFilters} togglePointSub={togglePointSub}
        showWindFlow={showWindFlow} setShowWindFlow={setShowWindFlow}
        windMode={windMode} setWindMode={setWindMode}
        showExclusionOverlay={showExclusionOverlay} setShowExclusionOverlay={setShowExclusionOverlay}
        showHeatmapV10={showHeatmapV10} setShowHeatmapV10={setShowHeatmapV10}
        heatmapV10Data={heatmapV10Data} heatmapIncludeCorridors={heatmapIncludeCorridors}
        setHeatmapIncludeCorridors={setHeatmapIncludeCorridors}
        showAlimentationV2={showAlimentationV2} setShowAlimentationV2={setShowAlimentationV2}
        showSalines={showSalines} setShowSalines={setShowSalines}
        nSalinesMax={nSalinesMax} setNSalinesMax={setNSalinesMax}
        showNutritionPanel={showNutritionPanel} setShowNutritionPanel={setShowNutritionPanel}
        alimentationV2Data={alimentationV2Data}
        pointsChaudsMode={pointsChaudsMode} setPointsChaudsMode={setPointsChaudsMode}
        pointsChaudsFilter={pointsChaudsFilter} setPointsChaudsFilter={setPointsChaudsFilter}
        minPercentageFilter={minPercentageFilter} setMinPercentageFilter={setMinPercentageFilter}
        showCursorBionic={showCursorBionic} setShowCursorBionic={setShowCursorBionic}
        adminArchitecteMode={adminArchitecteMode} setAdminArchitecteMode={setAdminArchitecteMode}
        privacyMode={privacyMode} setPrivacyMode={setPrivacyMode}
        activeWaypoints={activeWaypoints} savedPlaces={savedPlaces}
        selectedWaypointForZones={selectedWaypointForZones}
      />

      {/* ════════════════════════════════════════════════════════════════
          SECTION 4+5 — CARTE DOMINANTE + PANNEAU LATÉRAL
          La carte occupe toujours l'espace principal.
          Un panneau latéral s'ouvre selon l'onglet actif.
          BCE-4X R3/R7/R11: La carte est TOUJOURS rendue, jamais supprimée.
          ════════════════════════════════════════════════════════════════ */}
      <div className="flex-1 flex overflow-hidden min-h-0 relative">
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
              onCorridorDataLoaded={setCorridorV10Data}
              showZonesLayer={showZonesLayer}
              showCorridorsLayer={showCorridorsLayer}
              showPointsLayer={showPointsLayer}
              pointsChaudsMode={pointsChaudsMode}
              pointsChaudsFilter={pointsChaudsFilter}
              zoneSubFilters={zoneSubFilters}
              corridorSubFilters={corridorSubFilters}
              pointSubFilters={pointSubFilters}
              showAlimentationV2={showAlimentationV2}
              showSalines={showSalines}
              nSalinesMax={nSalinesMax}
              onAlimentationDataLoaded={setAlimentationV2Data}
              waypointCenter={waypointCenter}
              showHeatmapV10={showHeatmapV10}
              onHeatmapDataLoaded={setHeatmapV10Data}
              heatmapIncludeCorridors={heatmapIncludeCorridors}
            />
          </MapContainer>

          {/* BCE-4X: BionicLegend absorbee par INTELLIGENCE — carte epuree */}

          {/* ── Indicateur Zone d'Analyse — ADMIN PREMIUM uniquement ── */}
          {adminArchitecteMode && selectedWaypointForZones && (
            <div
              className="absolute bottom-[120px] left-2 z-[999] select-none pointer-events-none"
              data-testid="zone-analysis-indicator"
            >
              <div className="flex items-center gap-2 px-3 py-2 bg-[#0c0c14]/90 border border-[#f5a623]/30 rounded-lg backdrop-blur-sm shadow-lg">
                <div className="w-3 h-3 border-2 border-dashed rounded-sm flex-shrink-0" style={{ borderColor: '#f5a623' }} />
                <div>
                  <div className="text-[10px] font-bold text-white tracking-wide">Zone d'analyse</div>
                  <div className="text-[9px] text-gray-400">2 km × 2 km — {selectedWaypointForZones?.name || 'Waypoint'}</div>
                </div>
              </div>
            </div>
          )}

          {/* ── Indicateur Heatmap V10 — Discret bas-gauche ── */}
          {showHeatmapV10 && selectedWaypointForZones && heatmapV10Data && (
            <div
              className="absolute bottom-[60px] left-2 z-[999] select-none pointer-events-none"
              data-testid="heatmap-v10-indicator"
            >
              <div className="flex items-center gap-1.5 px-2 py-1 bg-[#0c0c14]/85 border border-gray-700/40 rounded backdrop-blur-sm">
                <div className="w-2 h-2 rounded-full bg-gradient-to-r from-blue-500 via-yellow-500 to-red-500 flex-shrink-0" />
                <span className="text-[8px] text-gray-400 font-medium">
                  Score V10{!heatmapIncludeCorridors && ' (sans corridors)'}
                </span>
                <span className="text-[8px] text-gray-500">{heatmapV10Data.score_avg}/100</span>
              </div>
            </div>
          )}


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
            SECTION 5 — PANNEAUX OPERATIONNELS (Waypoints, Lieux, Groupe, Exclusions)
            BCE-4X: Aucun panneau analytique lateral. INTELLIGENCE = seule source.
            Le panneau ne s'affiche QUE pour les onglets operationnels.
            ══════════════════════════════════════════════════════════════ */}
        {['waypoints', 'lieux', 'groupe', 'exclusions'].includes(activeTab) && (
        <div className="w-80 flex-shrink-0 bg-[#0d0d14] border-l border-[#1a1a2e] overflow-y-auto" data-testid="side-panel">
          {/* ── Zone diagnostic — panneau flottant sur clic zone (converti en overlay) ── */}
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
        )}

        {/* ═══ INTELLIGENCE DASHBOARD — Superposition flottante non-bloquante ═══ */}
        {/* BCE-4X R3/R7/R11/R18: La carte reste intacte, interactive, jamais supprimée */}
        {activeTab === 'intelligence' && (
          <IntelligenceDashboard
            onClose={() => setActiveTab('carte')}
            waypointCenter={waypointCenter}
            selectedSpecies={selectedSpecies}
            currentMonth={new Date().getMonth() + 1}
            onNavigateToPosition={(lat, lng) => {
              if (mapRef.current) {
                mapRef.current.setView([lat, lng], 15);
              }
            }}
            onHighlightZoneType={(type) => {
              // Intelligence -> Carte: highlight zones du type selectionne
              if (type === 'alimentation') { setShowZonesLayer(true); toggleZoneSub('alimentation'); }
              else if (type === 'repos') { setShowZonesLayer(true); toggleZoneSub('repos'); }
              else if (type === 'corridors') { setShowCorridorsLayer(true); }
              else if (type === 'pression') { setShowHeatmapV10(true); }
            }}
            onShowApproachMarkers={(markers) => {
              // Intelligence -> Carte: affiche marqueurs d'approche
              if (mapRef.current && markers?.idealPosition) {
                const L = window.L;
                if (L) {
                  // Nettoyer marqueurs precedents
                  mapRef.current.eachLayer(l => { if (l._isIntelMarker) mapRef.current.removeLayer(l); });
                  // Position ideale
                  const m = L.circleMarker([markers.idealPosition.lat, markers.idealPosition.lng], {
                    radius: 12, color: '#10b981', fillColor: '#10b981', fillOpacity: 0.3, weight: 2, dashArray: '4,4',
                  }).addTo(mapRef.current);
                  m._isIntelMarker = true;
                  m.bindTooltip('Position ideale', { permanent: true, className: 'intel-tooltip', offset: [0, -15] });
                  // Recentrer
                  mapRef.current.setView([markers.idealPosition.lat, markers.idealPosition.lng], 15);
                }
              }
            }}
          />
        )}
      </div>

      {/* ═══ PANNEAU RECOMMANDATIONS NUTRITIONNELLES — ALIMENTATION-V2 (composant extrait) ═══ */}
      {showNutritionPanel && alimentationV2Data && (
        <NutritionPanel alimentationV2Data={alimentationV2Data} onClose={() => setShowNutritionPanel(false)} />
      )}
      
      {/* ═══ DIALOGUES (composant extrait STEEVE-MAX) ═══ */}
      <TerritoireDialogs
        editingPlace={editingPlace} setEditingPlace={setEditingPlace} handleUpdatePlace={handleUpdatePlace}
        showAddPlaceDialog={showAddPlaceDialog} setShowAddPlaceDialog={setShowAddPlaceDialog}
        newPlace={newPlace} setNewPlace={setNewPlace} handleAddPlace={handleAddPlace}
        useCurrentPositionForNewPlace={useCurrentPositionForNewPlace}
        showAddWaypointDialog={showAddWaypointDialog} setShowAddWaypointDialog={setShowAddWaypointDialog}
        newWaypoint={newWaypoint} setNewWaypoint={setNewWaypoint}
        handleAddWaypointWithWind={handleAddWaypointWithWind}
        useCurrentPositionForNewWaypoint={useCurrentPositionForNewWaypoint}
        showShareDialog={showShareDialog} setShowShareDialog={setShowShareDialog}
        waypointToShare={waypointToShare} setWaypointToShare={setWaypointToShare} userId={userId}
        showCreateGroupDialog={showCreateGroupDialog} setShowCreateGroupDialog={setShowCreateGroupDialog}
        refreshGroups={refreshGroups}
        showGroupDashboard={showGroupDashboard} setShowGroupDashboard={setShowGroupDashboard}
        selectedGroup={selectedGroup} setSelectedGroup={setSelectedGroup}
        contextMenuMT={contextMenuMT} setContextMenuMT={setContextMenuMT}
        handleDeleteWaypoint={handleDeleteWaypoint} selectWaypointAsTarget={selectWaypointAsTarget}
        showCompareWidget={showCompareWidget} compareSelection={compareSelection}
        handleCloseCompare={handleCloseCompare} PLACE_TYPES={PLACE_TYPES}
      />
    </div>
  );
};

export default MonTerritoireBionicPage;
