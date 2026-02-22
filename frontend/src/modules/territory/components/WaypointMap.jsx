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
  Map, Flame, FileDown, FileText, Trash2, Layers
} from 'lucide-react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { MapInteractionLayer } from '../../map_interaction';
// P1-HOTSPOTS: Import overlays
import { HotspotOverlay, HotspotControlPanel } from '../../map_hotspots';

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
  initialZoom = null     // zoom level from URL params
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
      wqsResponse.forEach(wqs => {
        wqsLookup[wqs.waypoint_id] = wqs;
      });
      setWqsScores(wqsLookup);
      
    } catch (error) {
      console.error('Error loading waypoints:', error);
      toast.error('Erreur lors du chargement des waypoints');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadWaypoints();
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

  return (
    <div className="flex flex-col lg:flex-row gap-4 h-full" data-testid="waypoint-map">
      {/* Map */}
      <div className="flex-1 lg:flex-[3] min-h-0">
        <Card className="bg-slate-800 border-slate-700 overflow-hidden h-full flex flex-col">
          <CardHeader className="pb-2 flex-shrink-0">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Map className="h-5 w-5 text-[#f5a623]" />
                Carte des Waypoints
              </CardTitle>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant={showHeatmap ? 'default' : 'outline'}
                  className={showHeatmap 
                    ? 'bg-purple-600 hover:bg-purple-700' 
                    : 'border-purple-600 text-purple-400 hover:bg-purple-600/20'}
                  onClick={() => setShowHeatmap(!showHeatmap)}
                  data-testid="toggle-heatmap"
                >
                  <Flame className="h-4 w-4 mr-1" /> {showHeatmap ? 'Masquer' : 'Heatmap'}
                </Button>
                {/* P1-HOTSPOTS: Bouton Overlays BIONIC */}
                <Button
                  size="sm"
                  className={`${(hotspotSettings.showHotspots || hotspotSettings.showZones || hotspotSettings.showCorridors)
                    ? 'bg-amber-600 hover:bg-amber-700' 
                    : 'bg-slate-700 hover:bg-slate-600'}`}
                  onClick={() => setShowHotspotPanel(!showHotspotPanel)}
                  data-testid="toggle-hotspots-panel"
                >
                  <Layers className="h-4 w-4 mr-1" /> Hotspots BIONIC
                </Button>
                <Button
                  size="sm"
                  className={isAddingMode 
                    ? 'bg-red-600 hover:bg-red-700' 
                    : 'bg-[#f5a623] hover:bg-[#e09000] text-black'}
                  onClick={() => {
                    setIsAddingMode(!isAddingMode);
                    setNewWaypointLocation(null);
                  }}
                  data-testid="toggle-add-mode"
                >
                  {isAddingMode ? '✕ Annuler' : '+ Ajouter'}
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="border-green-600 text-green-400 hover:bg-green-600/20"
                  onClick={handleExportCSV}
                >
                  <FileDown className="h-4 w-4 mr-1" /> CSV
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="border-red-600 text-red-400 hover:bg-red-600/20"
                  onClick={handleExportPDF}
                >
                  <FileText className="h-4 w-4 mr-1" /> PDF
                </Button>
              </div>
            </div>
            {isAddingMode && (
              <p className="text-amber-400 text-sm mt-2 flex items-center gap-2">
                <MapPin className="h-4 w-4" /> Mode ajout actif - Cliquez sur la carte pour placer un waypoint
              </p>
            )}
          </CardHeader>
          <CardContent className="p-0 flex-1 min-h-0">
            <div className="h-full relative">
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
                <div className="h-full flex items-center justify-center bg-slate-900">
                  <div className="text-slate-400">Chargement de la carte...</div>
                </div>
              ) : (
                <MapContainer
                  center={initialCenter || mapCenter}
                  zoom={initialZoom || 12}
                  className="h-full w-full"
                  ref={mapRef}
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

                  {/* Existing waypoints */}
                  {waypoints.map(waypoint => {
                    const wqs = getWQS(waypoint.id);
                    return (
                    <Marker
                      key={waypoint.id}
                      position={[waypoint.lat, waypoint.lng]}
                      icon={createCustomIcon(waypoint.type)}
                      eventHandlers={{
                        click: () => setSelectedWaypoint(waypoint)
                      }}
                    >
                      <Popup>
                        <div className="p-2 min-w-[220px]">
                          <div className="flex items-center gap-2 mb-2">
                            {(() => {
                              const typeInfo = getTypeInfo(waypoint.type);
                              const TypeIcon = typeInfo.Icon || MapPin;
                              return <TypeIcon className="h-5 w-5" style={{ color: typeInfo.color }} />;
                            })()}
                            <strong>{waypoint.name}</strong>
                          </div>
                          
                          {/* WQS Score */}
                          {wqs && (
                            <div className="bg-slate-100 rounded p-2 mb-2">
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">WQS Score</span>
                                <span className="text-lg font-bold text-orange-500">{wqs.total_score}%</span>
                              </div>
                              <div className="flex items-center justify-between text-xs text-gray-500">
                                <span>{wqs.total_visits} visites</span>
                                <span className={`px-2 py-0.5 rounded text-white ${
                                  wqs.classification === 'hotspot' ? 'bg-green-500' :
                                  wqs.classification === 'good' ? 'bg-blue-500' :
                                  wqs.classification === 'standard' ? 'bg-yellow-500' : 'bg-red-500'
                                }`}>
                                  {wqs.classification === 'hotspot' ? 'Hotspot' :
                                   wqs.classification === 'good' ? 'Bon' :
                                   wqs.classification === 'standard' ? 'Standard' : 'Faible'}
                                </span>
                              </div>
                            </div>
                          )}
                          
                          <p className="text-sm text-gray-600 mb-2">
                            {waypoint.lat.toFixed(4)}, {waypoint.lng.toFixed(4)}
                          </p>
                          {waypoint.notes && (
                            <p className="text-sm text-gray-500 mb-2">{waypoint.notes}</p>
                          )}
                          <div className="flex gap-2">
                            <span className="px-2 py-1 rounded text-xs text-white" style={{ backgroundColor: getTypeInfo(waypoint.type).color }}>
                              {getTypeInfo(waypoint.type).label}
                            </span>
                            <button
                              className="px-2 py-1 rounded text-xs bg-red-500 text-white hover:bg-red-600 flex items-center gap-1"
                              onClick={() => handleDeleteWaypoint(waypoint.id)}
                            >
                              <Trash2 className="h-3 w-3" />
                            </button>
                          </div>
                        </div>
                      </Popup>
                    </Marker>
                  )})}

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
                      fetchWaypoints();
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
          </CardContent>
        </Card>
      </div>

      {/* Waypoints list */}
      <div className="lg:flex-1 min-h-0">
        <Card className="bg-slate-800 border-slate-700 h-full flex flex-col">
          <CardHeader className="pb-2 flex-shrink-0">
            <CardTitle className="text-lg text-white flex items-center justify-between">
              <span className="flex items-center gap-2">
                <MapPin className="h-5 w-5 text-[#f5a623]" />
                Mes Waypoints
              </span>
              <Badge className="bg-slate-700">{waypoints.length}</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 min-h-0 overflow-hidden">
            <div className="space-y-2 h-full overflow-y-auto">
              {waypoints.length > 0 ? (
                waypoints.map(waypoint => {
                  const typeInfo = getTypeInfo(waypoint.type);
                  return (
                    <div
                      key={waypoint.id}
                      className={`p-3 rounded-lg cursor-pointer transition-all ${
                        selectedWaypoint?.id === waypoint.id
                          ? 'bg-[#f5a623]/20 border border-[#f5a623]'
                          : 'bg-slate-700/50 hover:bg-slate-700 border border-transparent'
                      }`}
                      onClick={() => centerOnWaypoint(waypoint)}
                    >
                      <div className="flex items-center gap-2">
                        {(() => {
                          const TypeIcon = typeInfo.Icon || MapPin;
                          return <TypeIcon className="h-5 w-5" style={{ color: typeInfo.color }} />;
                        })()}
                        <div className="flex-1 min-w-0">
                          <p className="text-white font-medium truncate">{waypoint.name}</p>
                          <p className="text-slate-400 text-xs">
                            {waypoint.lat.toFixed(4)}, {waypoint.lng.toFixed(4)}
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="text-center py-8">
                  <MapPin className="h-8 w-8 text-[#f5a623] mx-auto" />
                  <p className="text-slate-400 mt-2 text-sm">Aucun waypoint</p>
                  <p className="text-slate-500 text-xs">Utilisez la carte pour en ajouter</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default WaypointMap;
