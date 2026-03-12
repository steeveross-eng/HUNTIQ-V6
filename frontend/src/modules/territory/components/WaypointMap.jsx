/**
 * WaypointMap - Interactive Leaflet map for waypoints
 * Phase P3.2 - Interactive Map with Heatmap
 * Phase P6 - UNIFIED: Uses territory_waypoints as single source of truth
 * Phase P1-HOTSPOTS - Integration des overlays BIONIC
 * BIONIC Design System compliant
 */
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents, useMap } from 'react-leaflet';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Input } from '../../../components/ui/input';
import { toast } from 'sonner';
import { ExportService } from '../../../services/ExportService';
import { WaypointScoringService } from '../../../services/WaypointScoringService';
import { HeatmapLayer } from '../../../components/HeatmapLayer';
import { 
  Target, Camera, Eye, MapPin, Leaf, Tent, ParkingCircle, CircleDot,
  Map, Flame, FileDown, FileText, Trash2, Layers, Wind, TreePine, Crosshair, Route, Play, ArrowLeftRight, Clock, X
} from 'lucide-react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { MapInteractionLayer } from '../../map_interaction';
// P1-HOTSPOTS: Import overlays
import { HotspotOverlay, HotspotControlPanel } from '../../map_hotspots';
// P2-VENTUSKY: Wind flow visualization
import WindFlowLayer from '../../../components/territoire/WindFlowLayer';
// P2-NDVI: Vegetation overlay (Sentinel-2)
import NdviOverlayLayer from '../../../components/territoire/NdviOverlayLayer';
// P2-CURSOR: Habitat score at cursor + QuickAdd waypoint
import CursorBionicLayer from '../../../components/territoire/CursorBionicLayer';
// P2-ROUTE: Tactical route planner
import RoutePlannerLayer from '../../../components/territoire/RoutePlannerLayer';
// REPLAY: Route animation
import RouteReplayLayer from '../../../components/territoire/RouteReplayLayer';
// STEVE-MAX: MovementCorridorsLayer LEGACY V1 — SUPPRIME DEFINITIVEMENT (BCE-4X-UI-003)
// FUNCTIONAL ZONES: Organic zone polygons (semi-static)
import BionicMicroZones from '../../../components/territoire/BionicMicroZones';
import TerritoryShell from '../../../components/territoire/TerritoryShell';
import StructureContrastLayer from '../../../components/territoire/StructureContrastLayer';
import { generateBionicZonesV5 } from '../../../services/BionicZoneService';
import { BIONIC_MODULES } from '../../../core/bionic';
// CONTEXT MENU: Right-click on waypoints
import WaypointContextMenu from '../../../components/territoire/WaypointContextMenu';

// Fix Leaflet default icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Default user ID for unified waypoints system
const getDefaultUserId = () => {
  const user = localStorage.getItem('user');
  if (user) {
    try {
      const parsed = JSON.parse(user);
      return parsed.email || parsed.id || 'default_user';
    } catch (e) {
      return 'default_user';
    }
  }
  return 'default_user';
};

/**
 * Normalize waypoint from territory API format to internal format
 * Maps: latitude→lat, longitude→lng, waypoint_type→type
 */
const normalizeWaypoint = (wp) => ({
  id: wp.id || wp._id,
  name: wp.name,
  lat: wp.latitude ?? wp.lat,
  lng: wp.longitude ?? wp.lng,
  type: wp.waypoint_type || wp.type || 'custom',
  notes: wp.description || wp.notes || '',
  active: wp.active !== false,
  color: wp.color,
  icon: wp.icon,
  created_at: wp.created_at
});

// BIONIC Design System - Waypoint Types with Lucide icons
const WAYPOINT_TYPES = [
  { id: 'hunting', label: 'Spot de chasse', Icon: Target, color: '#f5a623' },
  { id: 'stand', label: 'Mirador/Affût', Icon: Tent, color: '#8b4513' },
  { id: 'camera', label: 'Caméra trail', Icon: Camera, color: '#3b82f6' },
  { id: 'feeder', label: 'Nourrisseur', Icon: Leaf, color: '#22c55e' },
  { id: 'sighting', label: 'Observation', Icon: Eye, color: '#8b5cf6' },
  { id: 'parking', label: 'Stationnement', Icon: ParkingCircle, color: '#6b7280' },
  { id: 'custom', label: 'Autre', Icon: MapPin, color: '#ef4444' }
];

// Custom marker icons - BIONIC Design System (SVG)
const createCustomIcon = (type) => {
  const typeInfo = WAYPOINT_TYPES.find(t => t.id === type) || WAYPOINT_TYPES[6];
  
  // SVG path for the icon
  const svgIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" width="18" height="18"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>';
  
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="
      background: ${typeInfo.color};
      width: 36px;
      height: 36px;
      border-radius: 50% 50% 50% 0;
      transform: rotate(-45deg);
      display: flex;
      align-items: center;
      justify-content: center;
      border: 2px solid white;
      box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    ">
      <span style="transform: rotate(45deg); display: flex; align-items: center; justify-content: center;">${svgIcon}</span>
    </div>`,
    iconSize: [36, 36],
    iconAnchor: [18, 36],
    popupAnchor: [0, -36]
  });
};

// Map click handler component
const MapClickHandler = ({ onMapClick, isAddingMode }) => {
  useMapEvents({
    click: (e) => {
      if (isAddingMode) {
        onMapClick(e.latlng);
      }
    }
  });
  return null;
};

// Center map on location component (with zoom support)
const CenterOnLocation = ({ center, zoom }) => {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, zoom || 13);
    }
  }, [center, zoom, map]);
  return null;
};

// Set view from URL params component
const SetViewFromProps = ({ initialCenter, initialZoom }) => {
  const map = useMap();
  const hasSet = React.useRef(false);
  
  useEffect(() => {
    if (initialCenter && !hasSet.current) {
      map.setView(initialCenter, initialZoom || 17);
      hasSet.current = true;
    }
  }, [initialCenter, initialZoom, map]);
  
  return null;
};

export const WaypointMap = ({ 
  defaultCenter = { lat: 46.8139, lng: -71.2080 },
  initialCenter = null,  // [lat, lng] from URL params
  initialZoom = null,    // zoom level from URL params
  children = null        // BIONIC V5: Couches additionnelles (BionicMapOverlay)
}) => {
  const [waypoints, setWaypoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isAddingMode, setIsAddingMode] = useState(false);
  const [newWaypointLocation, setNewWaypointLocation] = useState(null);
  const [newWaypointName, setNewWaypointName] = useState('');
  const [newWaypointType, setNewWaypointType] = useState('hunting');
  const [selectedWaypoint, setSelectedWaypoint] = useState(null);
  const [mapCenter, setMapCenter] = useState([defaultCenter.lat, defaultCenter.lng]);
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [heatmapData, setHeatmapData] = useState([]);
  const [wqsScores, setWqsScores] = useState({});
  const mapRef = useRef(null);
  
  // P2-VENTUSKY: Wind flow overlay state
  const [showWindFlow, setShowWindFlow] = useState(false);
  // P2-NDVI: Vegetation overlay state
  const [showNdviOverlay, setShowNdviOverlay] = useState(false);
  // P2-CURSOR: Habitat score cursor mode
  const [showCursorBionic, setShowCursorBionic] = useState(false);
  // P2-ROUTE: Tactical route planner
  const [showRoutePlanner, setShowRoutePlanner] = useState(false);
  // REPLAY: Route replay animation
  const [showRouteReplay, setShowRouteReplay] = useState(false);
  // MOVEMENT CORRIDORS: Real vs Estimated
  const [showMovementCorridors, setShowMovementCorridors] = useState(false);
  // TEMPORAL SCENE: Hour slider for estimated corridors
  const [temporalHour, setTemporalHour] = useState(null);
  // FUNCTIONAL ZONES: Semi-static organic zones — TOUJOURS ACTIVES (BIONIC V5 300%)
  const [showFunctionalZones, setShowFunctionalZones] = useState(true);
  const [functionalZones, setFunctionalZones] = useState([]);
  const [loadingZones, setLoadingZones] = useState(false);
  // CONTEXT MENU: Right-click on waypoints
  const [contextMenu, setContextMenu] = useState(null);

  // Waypoint QuickAdd handler (cursor_bionic → waypoint system)
  const handleQuickAddWaypoint = useCallback(async (data) => {
    try {
      const userId = getDefaultUserId();
      const name = `Hotspot ${data.score}% — ${data.species}`;
      const response = await fetch(`${API_URL}/api/territory/waypoints?user_id=${encodeURIComponent(userId)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          latitude: data.lat,
          longitude: data.lng,
          waypoint_type: 'sighting',  // Use 'sighting' (observation) for habitat hotspots
          description: `Score habitat: ${data.score}% | Espece: ${data.species} | ${data.timestamp}`,
        }),
      });
      if (!response.ok) {
        const errText = await response.text();
        console.error('QuickAdd API error:', response.status, errText);
        toast.error('Erreur lors de la création du waypoint');
        return;
      }
      const result = await response.json();
      if (result.id || (result.success && result.waypoint)) {
        const wp = result.id ? result : result.waypoint;
        toast.success(`Waypoint "${name}" ajouté !`);
        setWaypoints(prev => [normalizeWaypoint(wp), ...prev]);
      } else {
        toast.error('Erreur lors de la création du waypoint');
      }
    } catch (err) {
      console.error('QuickAdd error:', err);
      toast.error('Erreur réseau');
    }
  }, []);
  
  // P1-HOTSPOTS: Etats pour les overlays BIONIC
  const [showHotspotPanel, setShowHotspotPanel] = useState(false);
  const [showTogglePanel, setShowTogglePanel] = useState(false);  // Panneau ON/OFF individuels
  const [hotspotsCount, setHotspotsCount] = useState(0);  // Compteur de hotspots
  const [hotspotSettings, setHotspotSettings] = useState({
    showHotspots: false,
    hotspotTypes: ['activity_peak', 'feeding_zone', 'rut_zone'],
    showZones: false,
    zoneTypes: ['feeding', 'bedding', 'water_access'],
    showCorridors: false,
    corridorTypes: ['movement', 'preferred', 'feeding_transit'],
    species: ['moose'],
    timeRange: '24h',
    minScoreThreshold: 50  // Seuil réduit pour plus de résultats
  });

  // Load waypoints and heatmap data - UNIFIED API (territory_waypoints)
  const hasShownErrorRef = useRef(false);
  const isInitialLoadRef = useRef(true);
  const loadWaypoints = useCallback(async () => {
    try {
      const userId = getDefaultUserId();
      
      const [waypointsResponse, heatmapResponse, wqsResponse] = await Promise.all([
        // UNIFIED: Use territory API as single source of truth
        fetch(`${API_URL}/api/territory/waypoints?user_id=${encodeURIComponent(userId)}`),
        WaypointScoringService.getHeatmapData(),
        WaypointScoringService.getAllWQS()
      ]);
      
      const waypointsData = await waypointsResponse.json();
      
      // Territory API returns array directly, normalize the format
      if (Array.isArray(waypointsData)) {
        setWaypoints(waypointsData.map(normalizeWaypoint));
      } else if (waypointsData.success && waypointsData.waypoints) {
        // Legacy format fallback
        setWaypoints(waypointsData.waypoints.map(normalizeWaypoint));
      } else {
        setWaypoints([]);
      }
      
      setHeatmapData(heatmapResponse);
      
      // Create WQS lookup by waypoint id
      const wqsLookup = {};
      if (Array.isArray(wqsResponse)) {
        wqsResponse.forEach(wqs => {
          wqsLookup[wqs.waypoint_id] = wqs;
        });
      }
      setWqsScores(wqsLookup);
      hasShownErrorRef.current = false;
      
    } catch (error) {
      console.error('Error loading waypoints:', error);
      // Only show toast on initial load, not during polling
      if (isInitialLoadRef.current && !hasShownErrorRef.current) {
        toast.error('Erreur lors du chargement des waypoints');
        hasShownErrorRef.current = true;
      }
    } finally {
      setLoading(false);
      isInitialLoadRef.current = false;
    }
  }, []);

  useEffect(() => {
    loadWaypoints();
  }, [loadWaypoints]);

  // BIONIC V5: Synchronisation bidirectionnelle instantanée des waypoints
  // Polling toutes les 3s — un waypoint créé/supprimé dans Mon Territoire
  // apparaît immédiatement dans Carte Interactive et vice versa.
  useEffect(() => {
    const syncInterval = setInterval(loadWaypoints, 3000);
    return () => clearInterval(syncInterval);
  }, [loadWaypoints]);

  // Handle map click for adding waypoint
  const handleMapClick = (latlng) => {
    setNewWaypointLocation(latlng);
    setNewWaypointName('');
    toast.info('Cliquez sur "Enregistrer" pour créer le waypoint');
  };

  // Save new waypoint - UNIFIED API (territory_waypoints)
  const handleSaveWaypoint = async () => {
    if (!newWaypointLocation) {
      toast.error('Cliquez sur la carte pour placer le waypoint');
      return;
    }
    if (!newWaypointName.trim()) {
      toast.error('Veuillez entrer un nom');
      return;
    }

    try {
      const userId = getDefaultUserId();
      
      // UNIFIED: Use territory API with correct field names
      const response = await fetch(`${API_URL}/api/territory/waypoints?user_id=${encodeURIComponent(userId)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newWaypointName,
          latitude: newWaypointLocation.lat,
          longitude: newWaypointLocation.lng,
          waypoint_type: newWaypointType,
          description: ''
        })
      });

      const data = await response.json();
      
      // Territory API returns the waypoint directly
      if (data.id) {
        toast.success('Waypoint créé !');
        setWaypoints(prev => [normalizeWaypoint(data), ...prev]);
        setNewWaypointLocation(null);
        setNewWaypointName('');
        setIsAddingMode(false);
      } else if (data.success && data.waypoint) {
        // Legacy format fallback
        toast.success('Waypoint créé !');
        setWaypoints(prev => [normalizeWaypoint(data.waypoint), ...prev]);
        setNewWaypointLocation(null);
        setNewWaypointName('');
        setIsAddingMode(false);
      } else {
        toast.error(data.error || data.detail || 'Erreur lors de la création');
      }
    } catch (error) {
      console.error('Error creating waypoint:', error);
      toast.error('Erreur de connexion');
    }
  };

  // Delete waypoint - UNIFIED API (territory_waypoints)
  const handleDeleteWaypoint = async (waypointId) => {
    try {
      const userId = getDefaultUserId();
      
      // UNIFIED: Use territory API for deletion
      const response = await fetch(`${API_URL}/api/territory/waypoints/${waypointId}?user_id=${encodeURIComponent(userId)}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      
      // Territory API returns {status: 'deleted'} on success
      if (data.status === 'deleted' || data.success) {
        toast.success('Waypoint supprimé');
        setWaypoints(prev => prev.filter(w => w.id !== waypointId));
        setSelectedWaypoint(null);
      } else {
        toast.error(data.error || data.detail || 'Erreur lors de la suppression');
      }
    } catch (error) {
      console.error('Error deleting waypoint:', error);
      toast.error('Erreur de connexion');
    }
  };

  // Export handlers
  const handleExportCSV = () => {
    if (waypoints.length === 0) {
      toast.error('Aucun waypoint à exporter');
      return;
    }
    try {
      ExportService.exportWaypointsCSV(waypoints);
      toast.success('Waypoints exportés en CSV !');
    } catch (error) {
      toast.error('Erreur lors de l\'export');
    }
  };

  const handleExportPDF = () => {
    if (waypoints.length === 0) {
      toast.error('Aucun waypoint à exporter');
      return;
    }
    try {
      ExportService.exportWaypointsPDF(waypoints);
      toast.success('Waypoints exportés en PDF !');
    } catch (error) {
      toast.error('Erreur lors de l\'export');
    }
  };

  // Center on waypoint
  const centerOnWaypoint = (waypoint) => {
    setMapCenter([waypoint.lat, waypoint.lng]);
    setSelectedWaypoint(waypoint);
  };

  // Get type info
  const getTypeInfo = (typeId) => {
    return WAYPOINT_TYPES.find(t => t.id === typeId) || WAYPOINT_TYPES[6];
  };

  // Get WQS for a waypoint
  const getWQS = (waypointId) => {
    return wqsScores[waypointId] || null;
  };

  // Get classification color
  const getClassificationColor = (classification) => {
    switch (classification) {
      case 'hotspot': return 'bg-green-600';
      case 'good': return 'bg-blue-600';
      case 'standard': return 'bg-yellow-600';
      case 'weak': return 'bg-red-600';
      default: return 'bg-slate-600';
    }
  };

  // FUNCTIONAL ZONES: Load zones when toggled on (semi-static, map-based)
  // BIONIC V5 P0: layers par défaut pour que le toggle "Zones" génère réellement des zones
  const DEFAULT_ZONE_LAYERS = {
    habitats: true, rut: true, repos: true, alimentation: true,
    corridors: true, peuplements: true,
  };

  useEffect(() => {
    if (!showFunctionalZones || !mapRef.current) return;
    let cancelled = false;
    const loadZones = async () => {
      setLoadingZones(true);
      try {
        const map = mapRef.current;
        const b = map.getBounds();
        const bounds = { north: b.getNorth(), south: b.getSouth(), east: b.getEast(), west: b.getWest() };
        const zoom = map.getZoom();
        const result = await generateBionicZonesV5(bounds, zoom, DEFAULT_ZONE_LAYERS, 'moose');
        if (!cancelled && result?.zones) {
          setFunctionalZones(result.zones);
        }
      } catch (err) {
        console.warn('Functional zones error:', err);
      } finally {
        if (!cancelled) setLoadingZones(false);
      }
    };
    loadZones();

    // STATE LOCKING: Les zones structurelles sont calculées une fois.
    // Pas de rechargement sur moveend pour garantir la stabilité.

    return () => { cancelled = true; };
  }, [showFunctionalZones]);

  return (
    <div className="flex flex-col lg:flex-row gap-0 h-full w-full" data-testid="waypoint-map">
      {/* Map - PLEINE GRANDEUR */}
      <div className="flex-1 min-h-0 min-w-0">
        <Card className="bg-black border-[#f5a623]/20 overflow-hidden h-full flex flex-col rounded-none">
          <CardHeader className="pb-1 flex-shrink-0 bg-black/95 border-b border-gray-800">
            {/* Titre */}
            <div className="flex items-center justify-between mb-1.5">
              <CardTitle className="text-sm text-white flex items-center gap-2">
                <Map className="h-4 w-4 text-[#f5a623]" />
                <span className="text-xs font-medium">Carte Tactique BIONIC V5</span>
              </CardTitle>
              {isAddingMode && (
                <span className="text-[10px] text-[#f5a623] flex items-center gap-1">
                  <MapPin className="h-3 w-3" /> Mode ajout actif
                </span>
              )}
            </div>

            {/* TOOLBAR — 3 Groupes hiérarchisés */}
            <div className="flex items-center gap-1 flex-wrap" data-testid="bionic-toolbar">

              {/* ═══ GROUPE 1 — Analyse Prioritaire ═══ */}
              <div className="flex items-center gap-1 pr-2 border-r border-gray-700/50" data-testid="toolbar-group-analysis">
                {/* HOTSPOTS BIONIC — Vedette */}
                <Button
                  size="sm"
                  className={`relative ${(hotspotSettings.showHotspots || hotspotSettings.showZones || hotspotSettings.showCorridors)
                    ? 'bg-teal-500 hover:bg-teal-400 text-black font-bold shadow-lg shadow-teal-500/30' 
                    : 'bg-gray-800 hover:bg-gray-700 text-white border border-teal-500/40'}`}
                  onClick={() => setShowHotspotPanel(!showHotspotPanel)}
                  data-testid="toggle-hotspots-panel"
                  title="Hotspots BIONIC — Analyse terrain prioritaire"
                >
                  <Layers className="h-4 w-4 mr-1" /> Hotspots
                </Button>
                <Button
                  size="sm"
                  variant={showCursorBionic ? 'default' : 'outline'}
                  className={`h-7 text-[11px] ${showCursorBionic 
                    ? 'bg-emerald-600 hover:bg-emerald-700 text-white' 
                    : 'border-gray-600 text-gray-400 hover:bg-gray-800'}`}
                  onClick={() => setShowCursorBionic(!showCursorBionic)}
                  data-testid="cursor-bionic-toggle"
                  title="Score habitat temps réel"
                >
                  <Crosshair className="h-3.5 w-3.5 mr-0.5" /> Score
                </Button>
                <Button
                  size="sm"
                  variant={showNdviOverlay ? 'default' : 'outline'}
                  className={`h-7 text-[11px] ${showNdviOverlay 
                    ? 'bg-green-600 hover:bg-green-700 text-white' 
                    : 'border-gray-600 text-gray-400 hover:bg-gray-800'}`}
                  onClick={() => setShowNdviOverlay(!showNdviOverlay)}
                  data-testid="ndvi-overlay-toggle"
                  title="Végétation Sentinel-2 NDVI"
                >
                  <TreePine className="h-3.5 w-3.5 mr-0.5" /> NDVI
                </Button>
                <Button
                  size="sm"
                  variant={showMovementCorridors ? 'default' : 'outline'}
                  className={`h-7 text-[11px] ${showMovementCorridors 
                    ? 'bg-teal-600 hover:bg-teal-700 text-white' 
                    : 'border-gray-600 text-gray-400 hover:bg-gray-800'}`}
                  onClick={() => setShowMovementCorridors(!showMovementCorridors)}
                  data-testid="movement-corridors-toggle"
                  title="Corridors réels vs estimés"
                >
                  <ArrowLeftRight className="h-3.5 w-3.5 mr-0.5" /> Déplac.
                </Button>
                {/* Slider temporel conditionnel */}
                {showMovementCorridors && (
                  <div className="flex items-center gap-1 px-1.5 py-0.5 rounded bg-gray-800/80 border border-gray-700/50" data-testid="temporal-scene-slider">
                    <Clock className="h-3 w-3 text-orange-400" />
                    <span className="text-[9px] text-orange-400 font-semibold w-6">{temporalHour !== null ? `${temporalHour}h` : 'Auto'}</span>
                    <input
                      type="range" min="-1" max="23"
                      value={temporalHour !== null ? temporalHour : -1}
                      onChange={(e) => { const v = parseInt(e.target.value); setTemporalHour(v === -1 ? null : v); }}
                      className="w-16 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-orange-400"
                      data-testid="temporal-hour-input"
                    />
                  </div>
                )}
              </div>

              {/* ═══ GROUPE 2 — Conditions & Environnement ═══ */}
              <div className="flex items-center gap-1 pr-2 border-r border-gray-700/50" data-testid="toolbar-group-conditions">
                <Button
                  size="sm"
                  variant={showWindFlow ? 'default' : 'outline'}
                  className={`h-7 text-[11px] ${showWindFlow 
                    ? 'bg-cyan-600 hover:bg-cyan-700 text-white' 
                    : 'border-gray-600 text-gray-400 hover:bg-gray-800'}`}
                  onClick={() => setShowWindFlow(!showWindFlow)}
                  data-testid="wind-flow-toggle"
                  title="Flux de vent"
                >
                  <Wind className="h-3.5 w-3.5 mr-0.5" /> Vent
                </Button>
                <Button
                  size="sm"
                  variant={showFunctionalZones ? 'default' : 'outline'}
                  className={`h-7 text-[11px] ${showFunctionalZones 
                    ? 'bg-emerald-600 hover:bg-emerald-700 text-white' 
                    : 'border-gray-600 text-gray-400 hover:bg-gray-800'}`}
                  onClick={() => setShowFunctionalZones(!showFunctionalZones)}
                  data-testid="functional-zones-toggle"
                  title="Zones fonctionnelles organiques"
                >
                  <TreePine className="h-3.5 w-3.5 mr-0.5" /> Zones
                </Button>
                <Button
                  size="sm"
                  variant={showHeatmap ? 'default' : 'outline'}
                  className={`h-7 text-[11px] ${showHeatmap 
                    ? 'bg-purple-600 hover:bg-purple-700 text-white' 
                    : 'border-gray-600 text-gray-400 hover:bg-gray-800'}`}
                  onClick={() => setShowHeatmap(!showHeatmap)}
                  data-testid="toggle-heatmap"
                  title="Carte de chaleur"
                >
                  <Flame className="h-3.5 w-3.5 mr-0.5" /> Heat
                </Button>
                <Button
                  size="sm"
                  variant={showRouteReplay ? 'default' : 'outline'}
                  className={`h-7 text-[11px] ${showRouteReplay 
                    ? 'bg-indigo-600 hover:bg-indigo-700 text-white' 
                    : 'border-gray-600 text-gray-400 hover:bg-gray-800'}`}
                  onClick={() => setShowRouteReplay(!showRouteReplay)}
                  data-testid="route-replay-toggle"
                  title="Animation du parcours"
                >
                  <Play className="h-3.5 w-3.5 mr-0.5" /> Replay
                </Button>
              </div>

              {/* ═══ GROUPE 3 — Actions & Export ═══ */}
              <div className="flex items-center gap-1" data-testid="toolbar-group-actions">
                <Button
                  size="sm"
                  className={`h-7 text-[11px] ${isAddingMode 
                    ? 'bg-red-600 hover:bg-red-700 text-white' 
                    : 'bg-[#f5a623]/90 hover:bg-[#f5a623] text-black'}`}
                  onClick={() => { setIsAddingMode(!isAddingMode); setNewWaypointLocation(null); }}
                  data-testid="toggle-add-mode"
                  title="Ajouter un waypoint"
                >
                  {isAddingMode ? '✕' : '+'}
                </Button>
                <Button
                  size="sm"
                  variant={showRoutePlanner ? 'default' : 'outline'}
                  className={`h-7 text-[11px] ${showRoutePlanner 
                    ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                    : 'border-gray-600 text-gray-400 hover:bg-gray-800'}`}
                  onClick={() => setShowRoutePlanner(!showRoutePlanner)}
                  data-testid="route-planner-toggle"
                  title="Planificateur de parcours A*"
                >
                  <Route className="h-3.5 w-3.5 mr-0.5" /> Parcours
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="h-7 text-[11px] border-gray-600 text-gray-400 hover:bg-gray-800"
                  onClick={handleExportCSV}
                  title="Exporter en CSV"
                >
                  <FileDown className="h-3.5 w-3.5" />
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="h-7 text-[11px] border-gray-600 text-gray-400 hover:bg-gray-800"
                  onClick={handleExportPDF}
                  title="Exporter en PDF"
                >
                  <FileText className="h-3.5 w-3.5" />
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent className="p-0 flex-1 min-h-0 relative">
            <div className="absolute inset-0">
              {/* P1-HOTSPOTS: Panneau de controle */}
              <HotspotControlPanel 
                isOpen={showHotspotPanel}
                onClose={() => setShowHotspotPanel(false)}
                defaultSettings={hotspotSettings}
                onSettingsChange={(settings) => setHotspotSettings(settings)}
                onTogglePanelOpen={() => setShowTogglePanel(true)}
                hotspotsCount={hotspotsCount}
              />
              
              {loading ? (
                <div className="absolute inset-0 flex items-center justify-center bg-black">
                  <div className="text-gray-400">Chargement de la carte...</div>
                </div>
              ) : (
                <MapContainer
                  center={initialCenter || mapCenter}
                  zoom={initialZoom || 12}
                  className="absolute inset-0 w-full h-full z-0"
                  ref={mapRef}
                  style={{ background: '#000' }}
                >
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  {/* Handle URL params for centering (from Admin) */}
                  {initialCenter && <SetViewFromProps initialCenter={initialCenter} initialZoom={initialZoom} />}
                  <CenterOnLocation center={mapCenter} zoom={12} />
                  <MapClickHandler 
                    onMapClick={handleMapClick} 
                    isAddingMode={isAddingMode} 
                  />

                  {/* Heatmap layer */}
                  {showHeatmap && heatmapData.length > 0 && (
                    <HeatmapLayer data={heatmapData} />
                  )}

                  {/* Existing waypoints — clic ouvre mini-fiche (bas-droite) */}
                  {waypoints.map(waypoint => (
                    <Marker
                      key={waypoint.id}
                      position={[waypoint.lat, waypoint.lng]}
                      icon={createCustomIcon(waypoint.type)}
                      eventHandlers={{
                        click: () => setSelectedWaypoint(waypoint),
                        contextmenu: (e) => {
                          e.originalEvent.preventDefault();
                          setContextMenu({
                            position: { x: e.originalEvent.clientX, y: e.originalEvent.clientY },
                            waypoint,
                          });
                        }
                      }}
                    />
                  ))}

                  {/* New waypoint marker */}
                  {newWaypointLocation && (
                    <Marker
                      position={[newWaypointLocation.lat, newWaypointLocation.lng]}
                      icon={createCustomIcon(newWaypointType)}
                    >
                      <Popup>
                        <div className="text-center p-2">
                          <strong>Nouveau waypoint</strong>
                          <p className="text-sm text-gray-600">
                            {newWaypointLocation.lat.toFixed(4)}, {newWaypointLocation.lng.toFixed(4)}
                          </p>
                        </div>
                      </Popup>
                    </Marker>
                  )}
                  
                  {/* Module d'Interaction Cartographique Universel */}
                  <MapInteractionLayer
                    showCoordinates={true}
                    enableWaypointCreation={!isAddingMode}
                    showHint={!isAddingMode}
                    onWaypointCreated={(waypoint) => {
                      toast.success(`Waypoint "${waypoint.name}" créé !`);
                      loadWaypoints();
                    }}
                    userId={getDefaultUserId()}
                  />
                  
                  {/* P1-HOTSPOTS: Overlays BIONIC */}
                  {(hotspotSettings.showHotspots || hotspotSettings.showZones || hotspotSettings.showCorridors) && (
                    <HotspotOverlay 
                      showHotspots={hotspotSettings.showHotspots}
                      showZones={hotspotSettings.showZones}
                      showCorridors={hotspotSettings.showCorridors}
                      species={hotspotSettings.species}
                      hotspotTypes={hotspotSettings.hotspotTypes}
                      zoneTypes={hotspotSettings.zoneTypes}
                      corridorTypes={hotspotSettings.corridorTypes}
                      minScoreThreshold={hotspotSettings.minScoreThreshold}
                      timeRange={hotspotSettings.timeRange}
                      showTogglePanel={showTogglePanel}
                      onTogglePanelClose={() => setShowTogglePanel(false)}
                      onHotspotsLoaded={(count) => setHotspotsCount(count)}
                    />
                  )}
                  
                  {/* FUNCTIONAL ZONES: 5-layer harmonized visual hierarchy */}
                  {showFunctionalZones && (
                    <>
                      {/* COUCHE 1: territory.shell — Enveloppe verte #3CB371, 30% */}
                      {functionalZones.length > 0 && (
                        <TerritoryShell
                          zones={functionalZones}
                          waypointCenter={waypoints.length > 0 ? [waypoints[0].lat, waypoints[0].lng] : null}
                        />
                      )}

                      {/* COUCHE 2: structure.contrast — Zones anthropisées #A9A9A9, 20% */}
                      <StructureContrastLayer enabled={true} />

                      {/* COUCHES 3+4: behavior.cells + core.nodes — Turquoise/Violet */}
                      {functionalZones.length > 0 && (
                        <BionicMicroZones
                          zones={functionalZones}
                          corridors={[]}
                          minPercentage={50}
                          showCorridors={false}
                          onZoneClick={() => {}}
                          onZoneHover={() => {}}
                        />
                      )}
                    </>
                  )}
                  
                  {/* P2-VENTUSKY: Wind flow animation layer */}
                  {showWindFlow && <WindFlowLayer bounds={null} />}
                  
                  {/* P2-NDVI: Vegetation overlay layer */}
                  {showNdviOverlay && <NdviOverlayLayer bounds={null} />}
                  
                  {/* P2-CURSOR: Habitat score at cursor + QuickAdd */}
                  {showCursorBionic && (
                    <CursorBionicLayer
                      species="moose"
                      onQuickAddWaypoint={handleQuickAddWaypoint}
                    />
                  )}
                  
                  {/* P2-ROUTE: Tactical route planner */}
                  {showRoutePlanner && (
                    <RoutePlannerLayer
                      species="moose"
                      anchorWaypoints={waypoints.filter(w => w.latitude && w.longitude).map(w => ({
                        lat: w.latitude, lng: w.longitude, name: w.name
                      }))}
                    />
                  )}
                  
                  {/* REPLAY: Route animation layer */}
                  {showRouteReplay && (
                    <RouteReplayLayer species="moose" />
                  )}
                  
                  {/* STEVE-MAX: Legacy MovementCorridorsLayer PURGE — BCE-4X-UI-003 */}
                  
                  {/* BIONIC V5: Couches organiques injectées par le parent */}
                  {children}
                </MapContainer>
              )}
            </div>

            {/* Add waypoint form */}
            {isAddingMode && newWaypointLocation && (
              <div className="p-4 bg-slate-700/50 border-t border-slate-600">
                <div className="flex flex-wrap gap-3 items-end">
                  <div className="flex-1 min-w-[200px]">
                    <label className="text-slate-400 text-sm block mb-1">Nom du waypoint</label>
                    <Input
                      placeholder="Ex: Mon spot favori"
                      value={newWaypointName}
                      onChange={(e) => setNewWaypointName(e.target.value)}
                      className="bg-slate-700 border-slate-600"
                      data-testid="new-waypoint-name"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400 text-sm block mb-1">Type</label>
                    <select
                      value={newWaypointType}
                      onChange={(e) => setNewWaypointType(e.target.value)}
                      className="bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-white"
                    >
                      {WAYPOINT_TYPES.map(type => (
                        <option key={type.id} value={type.id}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <Button
                    onClick={handleSaveWaypoint}
                    className="bg-green-600 hover:bg-green-700"
                    data-testid="save-map-waypoint"
                  >
                    Enregistrer
                  </Button>
                </div>
              </div>
            )}

            {/* BIONIC V5 300%: Panneau latéral = seule source de vérité waypoint */}
            {selectedWaypoint && (
              <div className="absolute bottom-3 right-3 z-[1000] bg-black/90 backdrop-blur-sm rounded-lg border border-[#f5a623]/30 p-3 max-w-[200px]" data-testid="waypoint-selected-indicator">
                <div className="flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-[#f5a623] flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="text-white text-xs font-medium truncate">{selectedWaypoint.name}</div>
                    <div className="text-[9px] text-gray-500 font-mono">{selectedWaypoint.lat?.toFixed(4)}, {selectedWaypoint.lng?.toFixed(4)}</div>
                  </div>
                  <button onClick={() => setSelectedWaypoint(null)} className="p-1 rounded hover:bg-gray-800 text-gray-500 hover:text-gray-300" data-testid="waypoint-deselect">
                    <X className="h-3 w-3" />
                  </button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Waypoints list — Panneau compact rétractable */}
      <div className="hidden lg:flex lg:w-48 flex-shrink-0 min-h-0">
        <Card className="bg-black/95 border-[#f5a623]/20 h-full flex flex-col w-full rounded-none">
          <CardHeader className="py-2 px-3 flex-shrink-0 border-b border-gray-800">
            <CardTitle className="text-xs text-white flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <MapPin className="h-3.5 w-3.5 text-[#f5a623]" />
                Waypoints
              </span>
              <Badge className="bg-[#f5a623]/20 text-[#f5a623] text-[10px] px-1.5 py-0">{waypoints.length}</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 min-h-0 overflow-hidden p-1.5">
            <div className="space-y-0.5 h-full overflow-y-auto">
              {waypoints.length > 0 ? (
                waypoints.map(waypoint => {
                  const typeInfo = getTypeInfo(waypoint.type);
                  const isSelected = selectedWaypoint?.id === waypoint.id;
                  return (
                    <div
                      key={waypoint.id}
                      className={`px-2 py-1.5 rounded cursor-pointer transition-all group ${
                        isSelected
                          ? 'bg-[#f5a623]/15 border border-[#f5a623]/40'
                          : 'hover:bg-gray-800/50 border border-transparent'
                      }`}
                      onClick={() => centerOnWaypoint(waypoint)}
                      onContextMenu={(e) => {
                        e.preventDefault();
                        setContextMenu({
                          position: { x: e.clientX, y: e.clientY },
                          waypoint,
                        });
                      }}
                      data-testid={`waypoint-item-${waypoint.id}`}
                    >
                      {/* Mini-fiche : icône + nom + actions */}
                      <div className="flex items-center gap-1.5">
                        {(() => {
                          const TypeIcon = typeInfo.Icon || MapPin;
                          return <TypeIcon className="h-3 w-3 flex-shrink-0" style={{ color: typeInfo.color }} />;
                        })()}
                        <span className="text-white text-[11px] font-medium truncate flex-1">{waypoint.name}</span>
                        {/* Actions rapides — visible au hover ou quand sélectionné */}
                        <div className={`flex items-center gap-0.5 ${isSelected ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'} transition-opacity`}>
                          <button
                            onClick={(e) => { e.stopPropagation(); setMapCenter([waypoint.lat, waypoint.lng]); setSelectedWaypoint(waypoint); }}
                            className="p-0.5 rounded hover:bg-[#f5a623]/20 text-gray-500 hover:text-[#f5a623] transition-colors"
                            title="Analyser"
                            data-testid={`waypoint-analyze-${waypoint.id}`}
                          >
                            <Target className="h-3 w-3" />
                          </button>
                          <button
                            onClick={(e) => { e.stopPropagation(); handleDeleteWaypoint(waypoint.id); }}
                            className="p-0.5 rounded hover:bg-red-500/20 text-gray-500 hover:text-red-400 transition-colors"
                            title="Supprimer"
                            data-testid={`waypoint-delete-${waypoint.id}`}
                          >
                            <Trash2 className="h-3 w-3" />
                          </button>
                        </div>
                      </div>
                      {/* Sous-info : type + coords (compact) */}
                      <div className="text-[9px] text-gray-600 mt-0.5 pl-4">
                        {typeInfo.label} — {waypoint.lat.toFixed(3)}, {waypoint.lng.toFixed(3)}
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="text-center py-4">
                  <MapPin className="h-5 w-5 text-[#f5a623]/50 mx-auto" />
                  <p className="text-gray-500 mt-1 text-[10px]">Aucun waypoint</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* CONTEXT MENU: Right-click waypoint menu */}
      {contextMenu && (
        <WaypointContextMenu
          position={contextMenu.position}
          waypoint={contextMenu.waypoint}
          onClose={() => setContextMenu(null)}
          onDelete={async (id) => {
            await handleDeleteWaypoint(id);
            loadWaypoints();
          }}
          onAnalyze={(wp) => setSelectedWaypoint(wp)}
          onEdit={(wp) => setSelectedWaypoint(wp)}
        />
      )}
    </div>
  );
};

export default WaypointMap;
