/**
 * BIONIC™ Territory Map Component
 * Leaflet-based map for wildlife tracking and territory analysis
 * 
 * BLOC 3 REFACTORING:
 * - Constants extracted to ./territory/constants.js
 * - Helper components extracted to ./territory/MapHelpers.jsx
 * - Added memo and useMemo for performance optimization
 * 
 * @module TerritoryMap
 * @version 2.0.0 (BLOC 3)
 */

import React, { useState, useEffect, useCallback, useRef, useMemo, memo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap, LayersControl, LayerGroup, Polyline, WMSTileLayer, Rectangle, Polygon, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
import { useLanguage } from '@/contexts/LanguageContext';
// Import BIONIC Analyzer
import BionicAnalyzer from './BionicAnalyzer';
// Import BIONIC Layer Panel from Design System
import { BionicLayerPanel, LAYER_GROUPS, ZONE_COLORS as DS_ZONE_COLORS } from '@/design-system';
// Import extracted sub-components
import { 
  TerritoryHeader, 
  SpeciesFilter, 
  GPSNavigationPanel,
  AnalysisResultsPanel,
  TERRITORY_TYPES,
  SPECIES_CONFIG as IMPORTED_SPECIES_CONFIG,
  downloadGPX,
  // Phase 1 — extracted constants & helpers
  SCALE_TO_ZOOM,
  BIONIC_MODULE_CONFIG,
  TERRITORY_TYPES_LOCAL,
  TERRITORY_DATABASE,
  WMS_LAYERS,
  createCustomIcon,
  HeatmapLayer,
  MapCenterController,
  MapClickHandler,
  ZoomSyncComponent,
  calculateDistance,
  calculateTotalDistance,
  convertDmsToDecimal as dmsToDecimal,
  convertDecimalToDms as decimalToDms,
} from './territory';
import { 
  Camera, 
  MapPin, 
  Target, 
  Eye, 
  Crosshair,
  Layers,
  Filter,
  Upload,
  RefreshCw,
  ChevronRight,
  Activity,
  TreePine,
  Droplets,
  LogOut,
  User,
  Route,
  Ruler,
  Mountain,
  Plus,
  X,
  Move,
  Locate,
  Navigation,
  Play,
  Square,
  Flag,
  Thermometer,
  Map,
  Waves,
  Trees,
  TrendingUp,
  CircleDot,
  Bookmark,
  Trash2,
  Download,
  Info,
  ArrowLeft,
  ShoppingCart,
  Package,
  Check,
  Send,
  ArrowRight,
  EyeOff,
  Loader2,
  RotateCcw,
  Brain,
  Zap,
  Droplet,
  Leaf,
  Users,
  Compass,
  Shield,
  Tent,
  Globe,
  Satellite,
  Star,
  Car,
  Lightbulb,
  Search,
  Wind
} from 'lucide-react';

// ============================================
// WIND FLOW LAYER (Ventusky-like)
// ============================================
import WindFlowLayer from './territoire/WindFlowLayer';
// Phase 2 — Extracted map layer components
import BionicPrecisionZonesLayer from './territory/BionicPrecisionZonesLayer';
import GuidedRouteLayer from './territory/GuidedRouteLayer';
import GuidedRoutePanel from './territory/GuidedRoutePanel';
import TerritoryAnalysisPanel from './territory/TerritoryAnalysisPanel';
import NutritionAnalysisModal from './territory/NutritionAnalysisModal';
import { CartModal, OrderFormModal } from './territory/CartModals';

// ============================================
// BIONIC DESIGN SYSTEM IMPORTS
// ============================================
import { 
  BIONIC_COLORS, 
  TERRITORY_COLORS, 
  WAYPOINT_COLORS, 
  ZONE_COLORS,
  getScoreColor 
} from '@/config/bionic-colors';
import { 
  TERRITORY_ICONS, 
  WEATHER_ICONS, 
  AI_ICONS,
  BIONIC_ICONS 
} from '@/config/bionic-icons';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Fix Leaflet default icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Species configuration - BIONIC Design System compliant (Lucide icons only)
const SPECIES_CONFIG = {
  orignal: { color: BIONIC_COLORS.gold.dark, iconType: 'circle', labelKey: 'animal_moose', heatColor: 'brown', Icon: CircleDot },
  chevreuil: { color: BIONIC_COLORS.gold.primary, iconType: 'circle', labelKey: 'animal_deer', heatColor: 'orange', Icon: CircleDot },
  ours: { color: BIONIC_COLORS.gray[600], iconType: 'circle', labelKey: 'animal_bear', heatColor: 'darkslategray', Icon: CircleDot },
  autre: { color: BIONIC_COLORS.gray[500], iconType: 'default', labelKey: 'common_other', heatColor: 'gray', Icon: CircleDot }
};

// Event type configuration - BIONIC Design System compliant (Lucide icons only)
const EVENT_TYPE_CONFIG = {
  observation: { color: BIONIC_COLORS.green.primary, iconType: 'eye', labelKey: 'waypoint_observation', Icon: Eye },
  camera_photo: { color: BIONIC_COLORS.blue.light, iconType: 'camera', labelKey: 'waypoint_camera', Icon: Camera },
  tir: { color: BIONIC_COLORS.red.primary, iconType: 'target', labelKey: 'event_shot', Icon: Target },
  cache: { color: BIONIC_COLORS.purple.primary, iconType: 'home', labelKey: 'place_camp', Icon: Tent },
  saline: { color: BIONIC_COLORS.cyan.primary, iconType: 'droplet', labelKey: 'place_salt_lick', Icon: Droplet },
  feeding_station: { color: BIONIC_COLORS.gold.primary, iconType: 'leaf', labelKey: 'waypoint_feeding', Icon: Leaf }
};

// Phase 1: Sub-components moved to ./territory/MapHelpers.jsx
// HeatmapLayer, MapCenterController, MapClickHandler, ZoomSyncComponent
// are now imported from './territory'

// Main Territory Map Component
const TerritoryMap = ({ userId, userName, onLogout, navigateToCoords, onNavigationComplete }) => {
  const [events, setEvents] = useState([]);
  const [cameras, setCameras] = useState([]);
  const [heatmapData, setHeatmapData] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [selectedSpecies, setSelectedSpecies] = useState('all');
  const [timeWindow, setTimeWindow] = useState(72);
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [showEvents, setShowEvents] = useState(true);
  const [showCameras, setShowCameras] = useState(true);
  const [showForestTrails, setShowForestTrails] = useState(true);
  
  // Map state
  const [mapCenter, setMapCenter] = useState([46.8139, -71.2080]); // Quebec default
  const [mapZoom, setMapZoom] = useState(12);
  
  // GPS Input
  const [gpsFormat, setGpsFormat] = useState('decimal'); // 'decimal' or 'dms'
  const [gpsLatitude, setGpsLatitude] = useState('');
  const [gpsLongitude, setGpsLongitude] = useState('');
  // DMS fields
  const [dmsLatDeg, setDmsLatDeg] = useState('');
  const [dmsLatMin, setDmsLatMin] = useState('');
  const [dmsLatSec, setDmsLatSec] = useState('');
  const [dmsLatDir, setDmsLatDir] = useState('N');
  const [dmsLonDeg, setDmsLonDeg] = useState('');
  const [dmsLonMin, setDmsLonMin] = useState('');
  const [dmsLonSec, setDmsLonSec] = useState('');
  const [dmsLonDir, setDmsLonDir] = useState('W');
  const [mapScale, setMapScale] = useState('1:5000');
  
  // Phase 1: SCALE_TO_ZOOM, dmsToDecimal, decimalToDms imported from './territory'
  
  // Photo upload
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);
  
  // Map tools state
  const [activeTool, setActiveTool] = useState(null); // 'pin', 'route', 'measure', null
  const [routePoints, setRoutePoints] = useState([]);
  const [measurePoints, setMeasurePoints] = useState([]);
  const [showLayersPanel, setShowLayersPanel] = useState(false);
  const [selectedBaseLayer, setSelectedBaseLayer] = useState('carte');
  const [showForestLayer, setShowForestLayer] = useState(false);
  const [showWaterLayer, setShowWaterLayer] = useState(false);
  const [showReliefLayer, setShowReliefLayer] = useState(false);
  const [showRoadsLayer, setShowRoadsLayer] = useState(false);
  const [showWindFlow, setShowWindFlow] = useState(false);
  const [pendingMarker, setPendingMarker] = useState(null);
  const [selectedSpeciesForMarker, setSelectedSpeciesForMarker] = useState('orignal');

  // GPS Tracking state
  const [isTracking, setIsTracking] = useState(false);
  const [currentPosition, setCurrentPosition] = useState(null);
  const [activeTrack, setActiveTrack] = useState(null);
  const [trackPoints, setTrackPoints] = useState([]);
  const [waypoints, setWaypoints] = useState([]);
  const [showWaypointModal, setShowWaypointModal] = useState(false);
  const [pendingWaypoint, setPendingWaypoint] = useState(null);
  const [waypointName, setWaypointName] = useState('');
  const [waypointType, setWaypointType] = useState('custom');
  const watchIdRef = useRef(null);
  const bionicZonesSectionRef = useRef(null); // Ref pour scroll auto vers section BIONIC
  
  // Mouse GPS Preview state (for waypoint placement)
  const [mouseGpsPreview, setMouseGpsPreview] = useState(null);
  const [waypointToolActive, setWaypointToolActive] = useState(false);
  
  // Dynamic GPS Flow State
  const [gpsFlowMode, setGpsFlowMode] = useState(false); // Active during waypoint movement
  const [draggingWaypoint, setDraggingWaypoint] = useState(null);
  const [liveGpsCoords, setLiveGpsCoords] = useState(null);
  const [autoAnalyzeOnConfirm, setAutoAnalyzeOnConfirm] = useState(true);

  // Advanced layers state
  const [showAdvancedLayers, setShowAdvancedLayers] = useState(false);
  const [layerForet, setLayerForet] = useState(false);
  const [layerHydro, setLayerHydro] = useState(false);
  const [layerTopo, setLayerTopo] = useState(false);
  const [layerRoutes, setLayerRoutes] = useState(false);
  const [layerProbability, setLayerProbability] = useState(false);
  const [layerRefuge, setLayerRefuge] = useState(false);
  const [layerCooling, setLayerCooling] = useState(false);
  const [selectedAnalysisSpecies, setSelectedAnalysisSpecies] = useState('orignal');
  const [probabilityData, setProbabilityData] = useState(null);
  const [coolingZones, setCoolingZones] = useState(null);
  
  // Probability zones for map display (Green, Yellow, Red)
  const [probabilityZones, setProbabilityZones] = useState([]);
  const [loadingZones, setLoadingZones] = useState(false);

  // Guided Route / Parcours Guidé State
  const [guidedRoute, setGuidedRoute] = useState(null);
  const [showGuidedRoutePanel, setShowGuidedRoutePanel] = useState(false);
  const [loadingGuidedRoute, setLoadingGuidedRoute] = useState(false);
  const [guidedRouteOptimization, setGuidedRouteOptimization] = useState('balanced');

  // Shopping Cart State
  const [cart, setCart] = useState([]);
  const [showCartModal, setShowCartModal] = useState(false);
  const [showOrderForm, setShowOrderForm] = useState(false);
  const [orderName, setOrderName] = useState('');
  const [orderEmail, setOrderEmail] = useState('');
  const [orderPhone, setOrderPhone] = useState('');
  const [orderNotes, setOrderNotes] = useState('');
  const [submittingOrder, setSubmittingOrder] = useState(false);

  // BIONIC Analyzer State
  const [showBionicAnalyzer, setShowBionicAnalyzer] = useState(false);
  const [selectedTerritoryType, setSelectedTerritoryType] = useState('');
  const [selectedZoneNumber, setSelectedZoneNumber] = useState('');
  const [territoryAnalysis, setTerritoryAnalysis] = useState(null);
  const [loadingTerritory, setLoadingTerritory] = useState(false);
  const [huntingTerritories, setHuntingTerritories] = useState([]);
  const [showHuntingMarkers, setShowHuntingMarkers] = useState(false);
  const [nearbyTerritories, setNearbyTerritories] = useState([]);
  
  // BIONIC Layers State - Pour affichage sur la carte
  const [bionicAnalysisResult, setBionicAnalysisResult] = useState(null);
  const [bionicLayersVisible, setBionicLayersVisible] = useState({
    thermal: true,
    wetness: true,
    food: true,
    pressure: true,
    access: true,
    corridor: true,
    canopy: true,
    geoform: true
  });
  
  // BIONIC TACTICAL Advanced Layer Panel State
  const [showBionicLayerPanel, setShowBionicLayerPanel] = useState(false);
  const [bionicLayerPanelMinimized, setBionicLayerPanelMinimized] = useState(false);
  const [advancedZoneVisibility, setAdvancedZoneVisibility] = useState({
    rut: false,
    repos: false,
    alimentation: false,
    corridor: false,
    affut: false,
    habitat: false,
    soleil: false,
    pente: false,
    hydro: false,
    foret: false,
    thermique: false,
    hotspot: false,
    pression: false,
    acces: false,
    wms_foret: false,
    wms_hydro: false,
    wms_topo: false,
    wms_routes: false,
  });
  const [advancedZoneOpacity, setAdvancedZoneOpacity] = useState(75);
  
  // Phase 1: BIONIC_MODULE_CONFIG, TERRITORY_TYPES_LOCAL, TERRITORY_DATABASE, WMS_LAYERS
  // imported from './territory/constants'

  // Handle GPS navigation
  const handleGpsNavigate = () => {
    let lat, lon;
    
    if (gpsFormat === 'decimal') {
      lat = parseFloat(gpsLatitude);
      lon = parseFloat(gpsLongitude);
    } else {
      // DMS format
      lat = dmsToDecimal(dmsLatDeg, dmsLatMin, dmsLatSec, dmsLatDir);
      lon = dmsToDecimal(dmsLonDeg, dmsLonMin, dmsLonSec, dmsLonDir);
    }
    
    if (isNaN(lat) || isNaN(lon)) {
      toast.error('Veuillez entrer des coordonnées GPS valides');
      return;
    }
    
    if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      toast.error('Coordonnées GPS hors limites');
      return;
    }
    
    setMapCenter([lat, lon]);
    setMapZoom(SCALE_TO_ZOOM[mapScale]);
    
    // Display in the appropriate format
    const displayCoords = gpsFormat === 'decimal' 
      ? `${lat.toFixed(4)}, ${lon.toFixed(4)}`
      : `${decimalToDms(lat, true)} ${decimalToDms(lon, false)}`;
    toast.success(`Navigation vers ${displayCoords} (Échelle ${mapScale})`);
  };

  // Handle scale change
  const handleScaleChange = (newScale) => {
    setMapScale(newScale);
    setMapZoom(SCALE_TO_ZOOM[newScale]);
  };

  // Load data
  const loadData = useCallback(async () => {
    if (!userId) return;
    
    setLoading(true);
    try {
      const [eventsRes, camerasRes, heatmapRes, statsRes] = await Promise.all([
        axios.get(`${API}/territory/events/recent`, {
          params: { user_id: userId, hours: timeWindow, limit: 500 }
        }),
        axios.get(`${API}/territory/cameras`, {
          params: { user_id: userId }
        }),
        axios.get(`${API}/territory/layers/heatmap_activite`, {
          params: { 
            user_id: userId, 
            hours: timeWindow,
            species: selectedSpecies !== 'all' ? selectedSpecies : undefined
          }
        }),
        axios.get(`${API}/territory/stats`, {
          params: { user_id: userId }
        })
      ]);
      
      setEvents(eventsRes.data || []);
      setCameras(camerasRes.data || []);
      setHeatmapData(heatmapRes.data?.points || []);
      setStats(statsRes.data);
      
      // Center map on first event or camera if available
      if (eventsRes.data?.length > 0) {
        const firstEvent = eventsRes.data[0];
        setMapCenter([firstEvent.latitude, firstEvent.longitude]);
      } else if (camerasRes.data?.length > 0) {
        const firstCam = camerasRes.data[0];
        if (firstCam.latitude && firstCam.longitude) {
          setMapCenter([firstCam.latitude, firstCam.longitude]);
        }
      }
      
    } catch (error) {
      console.error('Error loading territory data:', error);
      toast.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  }, [userId, timeWindow, selectedSpecies]);

  // Load hunting territories from API
  const loadHuntingTerritories = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/territory/hunting/territories`);
      setHuntingTerritories(response.data?.territories || []);
    } catch (error) {
      console.error('Error loading hunting territories:', error);
    }
  }, []);

  // Search nearby hunting territories
  const searchNearbyTerritories = async (lat, lng, radiusKm = 100, species = null) => {
    try {
      setLoadingTerritory(true);
      const params = { lat, lng, radius_km: radiusKm };
      if (species) params.species = species;
      
      const response = await axios.get(`${API}/territory/hunting/search`, { params });
      setNearbyTerritories(response.data?.all_results || []);
      return response.data;
    } catch (error) {
      console.error('Error searching nearby territories:', error);
      toast.error('Erreur lors de la recherche des territoires');
      return null;
    } finally {
      setLoadingTerritory(false);
    }
  };

  useEffect(() => {
    loadData();
    loadHuntingTerritories();
  }, [loadData, loadHuntingTerritories]);

  // Filter events by species
  const filteredEvents = events.filter(e => 
    selectedSpecies === 'all' || e.species === selectedSpecies
  );

  // Handle photo upload
  const handlePhotoUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    
    try {
      const response = await axios.post(`${API}/territory/photos/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      toast.success('Photo uploadée! Analyse IA en cours...');
      
      // Poll for AI result
      const photoId = response.data.id;
      let attempts = 0;
      const pollInterval = setInterval(async () => {
        attempts++;
        try {
          const statusRes = await axios.get(`${API}/territory/photos/${photoId}`);
          if (statusRes.data.processing_status === 'completed') {
            clearInterval(pollInterval);
            const species = statusRes.data.species;
            const confidence = (statusRes.data.species_confidence * 100).toFixed(0);
            toast.success(`Analyse terminée: ${SPECIES_CONFIG[species]?.label || species} (${confidence}% confiance)`);
            loadData(); // Refresh data
          } else if (statusRes.data.processing_status === 'failed' || attempts > 30) {
            clearInterval(pollInterval);
            toast.error('Erreur lors de l\'analyse');
          }
        } catch (e) {
          clearInterval(pollInterval);
        }
      }, 2000);
      
    } catch (error) {
      toast.error('Erreur lors de l\'upload');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  // Create new observation
  const handleAddObservation = async (latlng, species) => {
    try {
      await axios.post(`${API}/territory/events`, {
        event_type: 'observation',
        latitude: latlng.lat,
        longitude: latlng.lng,
        species: species,
        species_confidence: 0.9,
        count_estimate: 1,
        source: 'app'
      }, { params: { user_id: userId } });
      
      toast.success('Observation ajoutée!');
      loadData();
    } catch (error) {
      toast.error('Erreur lors de l\'ajout');
    }
  };

  // Handle map click based on active tool
  const handleMapClick = useCallback((latlng, tool) => {
    if (tool === 'pin') {
      // Show species selection and add marker
      setPendingMarker(latlng);
    } else if (tool === 'waypoint') {
      // Waypoint placement
      setPendingWaypoint({ lat: latlng.lat, lng: latlng.lng });
      setShowWaypointModal(true);
      setMouseGpsPreview(null);
    } else if (tool === 'route') {
      setRoutePoints(prev => [...prev, latlng]);
      toast.info(`Point ${routePoints.length + 1} ajouté au chemin`);
    } else if (tool === 'measure') {
      setMeasurePoints(prev => {
        const newPoints = [...prev, latlng];
        if (newPoints.length >= 2) {
          // Calculate distance
          const totalDistance = calculateTotalDistance(newPoints);
          toast.info(`Distance totale: ${totalDistance.toFixed(2)} km`);
        }
        return newPoints;
      });
    }
  }, [routePoints.length]);

  // Phase 1: calculateTotalDistance, calculateDistance imported from './territory/helpers'

  // Confirm adding marker with species
  const confirmAddMarker = async () => {
    if (pendingMarker) {
      await handleAddObservation(pendingMarker, selectedSpeciesForMarker);
      setPendingMarker(null);
      setActiveTool(null);
    }
  };

  // Clear route/measure points
  const clearToolPoints = () => {
    setRoutePoints([]);
    setMeasurePoints([]);
  };

  // ==========================================
  // GPS TRACKING FUNCTIONS
  // ==========================================

  // Load waypoints
  const loadWaypoints = async () => {
    try {
      const response = await axios.get(`${API}/territory/waypoints`, { params: { user_id: userId } });
      setWaypoints(response.data);
    } catch (error) {
      console.error('Error loading waypoints:', error);
    }
  };

  // Start GPS tracking
  const startTracking = async () => {
    if (!navigator.geolocation) {
      toast.error('Géolocalisation non supportée par votre navigateur');
      return;
    }

    try {
      // Create a new track in the backend
      const response = await axios.post(`${API}/territory/tracks`, {
        name: `Tracé ${new Date().toLocaleDateString('fr-CA')} ${new Date().toLocaleTimeString('fr-CA')}`,
        description: 'Tracé GPS automatique'
      }, { params: { user_id: userId } });

      setActiveTrack(response.data);
      setTrackPoints([]);
      setIsTracking(true);

      // Start watching position
      watchIdRef.current = navigator.geolocation.watchPosition(
        async (position) => {
          const newPoint = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            alt: position.coords.altitude,
            accuracy: position.coords.accuracy,
            speed: position.coords.speed,
            timestamp: new Date()
          };

          setCurrentPosition(newPoint);
          setTrackPoints(prev => [...prev, newPoint]);

          // Send to backend
          try {
            await axios.post(`${API}/territory/tracks/${response.data.id}/points`, {
              latitude: newPoint.lat,
              longitude: newPoint.lng,
              altitude: newPoint.alt,
              accuracy: newPoint.accuracy,
              speed: newPoint.speed
            }, { params: { user_id: userId } });
          } catch (e) {
            console.error('Error saving track point:', e);
          }
        },
        (error) => {
          toast.error('Erreur GPS: ' + error.message);
        },
        {
          enableHighAccuracy: true,
          maximumAge: 5000,
          timeout: 10000
        }
      );

      toast.success('Enregistrement GPS démarré');
    } catch (error) {
      toast.error('Erreur lors du démarrage du tracking');
    }
  };

  // Stop GPS tracking
  const stopTracking = async () => {
    if (watchIdRef.current) {
      navigator.geolocation.clearWatch(watchIdRef.current);
      watchIdRef.current = null;
    }

    if (activeTrack) {
      try {
        await axios.post(`${API}/territory/tracks/${activeTrack.id}/stop`, {}, { params: { user_id: userId } });
        toast.success(`Tracé enregistré: ${trackPoints.length} points, ${calculateTotalDistance(trackPoints).toFixed(2)} km`);
      } catch (error) {
        console.error('Error stopping track:', error);
      }
    }

    setIsTracking(false);
    setActiveTrack(null);
  };

  // Add waypoint
  const addWaypoint = async () => {
    if (!pendingWaypoint || !waypointName) {
      toast.error('Veuillez nommer le waypoint');
      return;
    }

    // ============================================
    // EXCLUSION EAU — DÉSACTIVÉ FRONTEND (Audit V1)
    // Les exclusions sont gérées exclusivement par le backend
    // (zone_engine_core_v2 via Overpass API)
    // ============================================

    try {
      await axios.post(`${API}/territory/waypoints`, {
        latitude: pendingWaypoint.lat,
        longitude: pendingWaypoint.lng,
        name: waypointName,
        waypoint_type: waypointType
      }, { params: { user_id: userId } });

      toast.success('Waypoint confirmé et enregistré!');
      
      // Intégration automatique dans le module Analyse GPS
      if (gpsFormat === 'decimal') {
        setGpsLatitude(pendingWaypoint.lat.toFixed(6));
        setGpsLongitude(pendingWaypoint.lng.toFixed(6));
      } else {
        const lat = pendingWaypoint.lat;
        const lon = pendingWaypoint.lng;
        
        setDmsLatDir(lat >= 0 ? 'N' : 'S');
        const absLat = Math.abs(lat);
        setDmsLatDeg(Math.floor(absLat).toString());
        const latMinFloat = (absLat - Math.floor(absLat)) * 60;
        setDmsLatMin(Math.floor(latMinFloat).toString());
        setDmsLatSec(((latMinFloat - Math.floor(latMinFloat)) * 60).toFixed(2));
        
        setDmsLonDir(lon >= 0 ? 'E' : 'W');
        const absLon = Math.abs(lon);
        setDmsLonDeg(Math.floor(absLon).toString());
        const lonMinFloat = (absLon - Math.floor(absLon)) * 60;
        setDmsLonMin(Math.floor(lonMinFloat).toString());
        setDmsLonSec(((lonMinFloat - Math.floor(lonMinFloat)) * 60).toFixed(2));
      }
      
      // Centrer la carte sur le waypoint
      setMapCenter([pendingWaypoint.lat, pendingWaypoint.lng]);
      
      // Désactiver le mode flux GPS
      deactivateGpsFlowMode();
      
      setShowWaypointModal(false);
      setPendingWaypoint(null);
      setWaypointName('');
      
      toast.info('Coordonnées GPS intégrées automatiquement');
      
      // DÉCLENCHEMENT AUTOMATIQUE DE L'ANALYSE
      if (autoAnalyzeOnConfirm) {
        setTimeout(() => {
          toast.info(t('analysis_auto_starting'));
          handleAnalyzeGPS();
        }, 600);
      }
      
      loadWaypoints();
    } catch (error) {
      toast.error('Erreur lors de l\'ajout du waypoint');
    }
  };

  // Delete waypoint
  const deleteWaypoint = async (waypointId) => {
    try {
      // Optimistic update - remove from local state immediately
      setWaypoints(prev => prev.filter(wp => wp.id !== waypointId));
      
      // Call API to delete
      await axios.delete(`${API}/territory/waypoints/${waypointId}`, { params: { user_id: userId } });
      
      // Show success confirmation
      toast.success(t('waypoint_deleted'), {
        description: t('waypoint_deleted_desc'),
        duration: 3000
      });
      
      // Force refresh from server to ensure sync
      setTimeout(() => {
        loadWaypoints();
      }, 500);
      
    } catch (error) {
      console.error('Error deleting waypoint:', error);
      // Reload waypoints to restore state if delete failed
      loadWaypoints();
      toast.error('Erreur lors de la suppression', {
        description: 'Le waypoint n\'a pas pu être supprimé. Veuillez réessayer.'
      });
    }
  };

  // Delete event (gibier/observation)
  const deleteEvent = async (eventId) => {
    try {
      // Optimistic update - remove from local state immediately
      setEvents(prev => prev.filter(e => e.id !== eventId));
      
      await axios.delete(`${API}/territory/events/${eventId}`, { params: { user_id: userId } });
      
      toast.success(t('observation_deleted'), {
        description: t('observation_deleted_desc'),
        duration: 3000
      });
    } catch (error) {
      // Keep removed from local state even if API fails
      toast.success(t('observation_deleted'), {
        description: t('observation_removed_display')
      });
    }
  };

  // Delete ALL waypoints and reset search
  const deleteAllWaypoints = async () => {
    if (waypoints.length === 0) {
      toast.info('Aucun waypoint à supprimer');
      return;
    }
    
    try {
      // Delete all waypoints one by one
      await Promise.all(
        waypoints.map(wp => 
          axios.delete(`${API}/territory/waypoints/${wp.id}`, { params: { user_id: userId } })
        )
      );
      
      // Clear local state
      setWaypoints([]);
      setGuidedRoute(null);
      setShowGuidedRoutePanel(false);
      setProbabilityZones([]);
      setProbabilityData(null);
      setTerritoryAnalysis(null);
      
      // Reset GPS fields
      setGpsLatitude('');
      setGpsLongitude('');
      setDmsLatDeg('');
      setDmsLatMin('');
      setDmsLatSec('');
      setDmsLonDeg('');
      setDmsLonMin('');
      setDmsLonSec('');
      
      toast.success(t('all_waypoints_cleared'));
    } catch (error) {
      toast.error(t('error_deleting_waypoints'));
    }
  };

  // Get current position for waypoint
  const getCurrentPositionForWaypoint = () => {
    if (currentPosition) {
      setPendingWaypoint(currentPosition);
      setShowWaypointModal(true);
    } else if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setPendingWaypoint({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          });
          setShowWaypointModal(true);
        },
        (error) => toast.error('Impossible d\'obtenir la position')
      );
    }
  };

  // Activate waypoint placement tool
  const activateWaypointTool = () => {
    setWaypointToolActive(true);
    setActiveTool('waypoint');
    setGpsFlowMode(true);
    toast.info(t('gps_flow_mode_active'));
  };

  // Deactivate GPS flow mode
  const deactivateGpsFlowMode = () => {
    setGpsFlowMode(false);
    setWaypointToolActive(false);
    setActiveTool(null);
    setMouseGpsPreview(null);
    setLiveGpsCoords(null);
  };

  // Handle mouse move for GPS preview - CONTINUOUS FLOW
  const handleMouseMove = useCallback((latlng) => {
    // TOUJOURS capturer les coordonnées du curseur en temps réel
    const coords = {
      lat: latlng.lat,
      lng: latlng.lng,
      latDms: decimalToDms(latlng.lat, true),
      lngDms: decimalToDms(latlng.lng, false),
      altitude: Math.round(200 + Math.random() * 300), // Simulated altitude
      precision: Math.round(3 + Math.random() * 5), // Simulated precision in meters
      timestamp: new Date().toISOString()
    };
    
    setMouseGpsPreview(coords);
    
    // Mode actif (waypoint tool, GPS flow, dragging) - injection dans Analyse GPS
    if (waypointToolActive || activeTool === 'waypoint' || gpsFlowMode || draggingWaypoint) {
      setLiveGpsCoords(coords);
      
      // Update GPS Analysis fields in real-time
      if (gpsFormat === 'decimal') {
        setGpsLatitude(latlng.lat.toFixed(6));
        setGpsLongitude(latlng.lng.toFixed(6));
      } else {
        // Update DMS fields
        const lat = latlng.lat;
        const lon = latlng.lng;
        
        setDmsLatDir(lat >= 0 ? 'N' : 'S');
        const absLat = Math.abs(lat);
        setDmsLatDeg(Math.floor(absLat).toString());
        const latMinFloat = (absLat - Math.floor(absLat)) * 60;
        setDmsLatMin(Math.floor(latMinFloat).toString());
        setDmsLatSec(((latMinFloat - Math.floor(latMinFloat)) * 60).toFixed(2));
        
        setDmsLonDir(lon >= 0 ? 'E' : 'W');
        const absLon = Math.abs(lon);
        setDmsLonDeg(Math.floor(absLon).toString());
        const lonMinFloat = (absLon - Math.floor(absLon)) * 60;
        setDmsLonMin(Math.floor(lonMinFloat).toString());
        setDmsLonSec(((lonMinFloat - Math.floor(lonMinFloat)) * 60).toFixed(2));
      }
    }
  }, [waypointToolActive, activeTool, gpsFlowMode, draggingWaypoint, gpsFormat]);

  // Fonction pour injecter les coordonnées et lancer l'analyse automatique
  const injectGpsAndAnalyze = useCallback(async (lat, lng) => {
    // 1. Injecter les coordonnées dans Analyse GPS
    setGpsLatitude(lat.toFixed(6));
    setGpsLongitude(lng.toFixed(6));
    
    // Mettre à jour aussi les coordonnées DMS
    setDmsLatDir(lat >= 0 ? 'N' : 'S');
    const absLat = Math.abs(lat);
    setDmsLatDeg(Math.floor(absLat).toString());
    const latMinFloat = (absLat - Math.floor(absLat)) * 60;
    setDmsLatMin(Math.floor(latMinFloat).toString());
    setDmsLatSec(((latMinFloat - Math.floor(latMinFloat)) * 60).toFixed(2));
    
    setDmsLonDir(lng >= 0 ? 'E' : 'W');
    const absLon = Math.abs(lng);
    setDmsLonDeg(Math.floor(absLon).toString());
    const lonMinFloat = (absLon - Math.floor(absLon)) * 60;
    setDmsLonMin(Math.floor(lonMinFloat).toString());
    setDmsLonSec(((lonMinFloat - Math.floor(lonMinFloat)) * 60).toFixed(2));
    
    // 2. Mettre à jour les coordonnées live
    setLiveGpsCoords({
      lat: lat,
      lng: lng,
      latDms: decimalToDms(lat, true),
      lngDms: decimalToDms(lng, false)
    });
    
    // 3. Centrer la carte sur le point
    setMapCenter([lat, lng]);
    
    // 4. Lancer automatiquement l'analyse du territoire
    toast.info(t('analysis_auto_starting'), { duration: 2000 });
    
    try {
      // Appeler l'API d'analyse
      const analysisRes = await axios.post(`${API}/territory/analysis/probability`, {
        latitude: lat,
        longitude: lng,
        radius_km: 5,
        species: selectedSpecies !== 'all' ? selectedSpecies : 'orignal'
      });
      
      // Rechercher les territoires de chasse à proximité
      const huntingRes = await axios.get(`${API}/territory/hunting/search`, {
        params: { lat, lng, radius_km: 50 }
      });
      
      if (huntingRes.data?.all_results) {
        setNearbyTerritories(huntingRes.data.all_results);
        setShowHuntingMarkers(true);
      }
      
      // Générer les zones de probabilité
      generateProbabilityZones();
      
      toast.success(`Analyse complète: ${lat.toFixed(4)}, ${lng.toFixed(4)}`, {
        description: `${huntingRes.data?.total_count || 0} territoires de chasse trouvés à proximité`
      });
      
    } catch (error) {
      console.error('Auto-analysis error:', error);
      // Même si l'API échoue, on garde les coordonnées injectées
      toast.success(`Coordonnées capturées: ${lat.toFixed(6)}, ${lng.toFixed(6)}`);
    }
  }, [selectedSpecies]); // eslint-disable-line react-hooks/exhaustive-deps

  // Handle waypoint drag start
  const handleWaypointDragStart = (waypoint) => {
    setDraggingWaypoint(waypoint);
    setGpsFlowMode(true);
    toast.info(t('gps_live_flow_active'));
  };

  // Handle waypoint drag end - AUTO INTEGRATION
  const handleWaypointDragEnd = async (waypoint, newPosition) => {
    setDraggingWaypoint(null);
    setGpsFlowMode(false);
    
    // Update waypoint position in database
    try {
      await axios.put(`${API}/territory/waypoints/${waypoint.id}`, {
        latitude: newPosition.lat,
        longitude: newPosition.lng
      }, { params: { user_id: userId } });
      
      // Final GPS integration
      if (gpsFormat === 'decimal') {
        setGpsLatitude(newPosition.lat.toFixed(6));
        setGpsLongitude(newPosition.lng.toFixed(6));
      } else {
        const lat = newPosition.lat;
        const lon = newPosition.lng;
        
        setDmsLatDir(lat >= 0 ? 'N' : 'S');
        const absLat = Math.abs(lat);
        setDmsLatDeg(Math.floor(absLat).toString());
        const latMinFloat = (absLat - Math.floor(absLat)) * 60;
        setDmsLatMin(Math.floor(latMinFloat).toString());
        setDmsLatSec(((latMinFloat - Math.floor(latMinFloat)) * 60).toFixed(2));
        
        setDmsLonDir(lon >= 0 ? 'E' : 'W');
        const absLon = Math.abs(lon);
        setDmsLonDeg(Math.floor(absLon).toString());
        const lonMinFloat = (absLon - Math.floor(absLon)) * 60;
        setDmsLonMin(Math.floor(lonMinFloat).toString());
        setDmsLonSec(((lonMinFloat - Math.floor(lonMinFloat)) * 60).toFixed(2));
      }
      
      setMapCenter([newPosition.lat, newPosition.lng]);
      
      toast.success('Coordonnées GPS intégrées automatiquement');
      
      // Auto-trigger analysis if enabled
      if (autoAnalyzeOnConfirm) {
        setTimeout(() => {
          toast.info(t('analysis_territory_progress'));
          handleAnalyzeGPS();
        }, 500);
      }
      
      loadWaypoints();
    } catch (error) {
      toast.error('Erreur lors de la mise à jour du waypoint');
    }
  };

  // Handle map click for waypoint placement
  const handleWaypointClick = useCallback((latlng) => {
    if (waypointToolActive || activeTool === 'waypoint') {
      setPendingWaypoint({ lat: latlng.lat, lng: latlng.lng });
      setShowWaypointModal(true);
      // Keep flow mode active until confirmation
    }
  }, [waypointToolActive, activeTool]);

  // ==========================================
  // BIONIC ANALYSIS LAYER FUNCTIONS (v2.0)
  // ==========================================

  /**
   * Génère des micro-zones ultra-précises pour chaque module BIONIC
   * VERSION 3.0 - Zones micro-délimitées transparentes
   * - Contours nets avec remplissage quasi-invisible
   * - Terrain 100% visible sous les zones
   * - Focus sur les zones à haute probabilité (>= 60%)
   * - Grille ultra-fine pour précision maximale
   */
  const generatePrecisionBionicZones = useCallback((analysisResult, centerLat, centerLng, radiusKm = 5) => {
    if (!analysisResult?.modules) return [];

    const allZones = [];
    const gridResolution = 25; // Grille ultra-fine pour micro-délimitation
    const moduleKeys = Object.keys(analysisResult.modules);
    const probabilityThreshold = 60; // Seuil élevé pour zones vraiment pertinentes
    
    // Générer une grille de micro-zones
    for (let gridX = -gridResolution; gridX <= gridResolution; gridX++) {
      for (let gridY = -gridResolution; gridY <= gridResolution; gridY++) {
        // Vérifier si le point est dans le rayon circulaire
        const distanceFromCenter = Math.sqrt(gridX * gridX + gridY * gridY);
        if (distanceFromCenter > gridResolution) continue;
        
        // Calculer la position de la cellule - plus petite pour micro-délimitation
        const cellSize = radiusKm / gridResolution;
        const cellCenterLat = centerLat + (gridY * cellSize / 111);
        const cellCenterLng = centerLng + (gridX * cellSize / (111 * Math.cos(centerLat * Math.PI / 180)));
        
        // Trouver le module dominant pour cette cellule
        let dominantModule = null;
        let highestProbability = 0;
        
        moduleKeys.forEach((moduleKey) => {
          const moduleData = analysisResult.modules[moduleKey];
          const config = BIONIC_MODULE_CONFIG[moduleKey];
          if (!config || !moduleData) return;
          
          const baseScore = moduleData.score || 50;
          
          // Variation spatiale plus réaliste
          const spatialVariation = calculateSpatialVariation(
            moduleKey, gridX, gridY, moduleData.factors,
            distanceFromCenter, gridResolution
          );
          
          const probability = Math.min(100, Math.max(0, baseScore * spatialVariation));
          
          // Seuil plus élevé pour zones vraiment pertinentes
          if (probability > highestProbability && probability >= probabilityThreshold) {
            highestProbability = probability;
            dominantModule = {
              key: moduleKey,
              ...config,
              probability: Math.round(probability),
              rating: getProbabilityRating(probability),
              factors: moduleData.factors,
              recommendations: moduleData.recommendations
            };
          }
        });
        
        // Créer la zone si un module dominant existe
        if (dominantModule) {
          // Micro-cellule ultra-compacte pour délimitation fine
          const cellPolygon = generateMicroCell(cellCenterLat, cellCenterLng, cellSize * 0.55);
          
          // Opacité ULTRA-LÉGÈRE - terrain toujours 100% visible
          // 60% -> 0.02, 100% -> 0.08 (presque invisible sauf contours)
          const baseOpacity = 0.02;
          const maxOpacity = 0.08;
          const fillOpacity = baseOpacity + ((dominantModule.probability - probabilityThreshold) / (100 - probabilityThreshold)) * (maxOpacity - baseOpacity);
          
          // Contours nets et visibles (l'élément principal de visualisation)
          // Plus la probabilité est haute, plus le contour est épais et visible
          const strokeWeight = dominantModule.probability >= 85 ? 2.5 : 
                              dominantModule.probability >= 75 ? 2 : 
                              dominantModule.probability >= 65 ? 1.5 : 1;
          const strokeOpacity = dominantModule.probability >= 80 ? 0.9 : 
                               dominantModule.probability >= 70 ? 0.75 : 0.6;
          
          allZones.push({
            id: `${dominantModule.key}_${gridX}_${gridY}`,
            moduleKey: dominantModule.key,
            name: dominantModule.name,
            label: dominantModule.label,
            color: dominantModule.color,
            icon: dominantModule.icon,
            probability: dominantModule.probability,
            rating: dominantModule.rating,
            polygon: cellPolygon,
            center: [cellCenterLat, cellCenterLng],
            factors: dominantModule.factors,
            recommendations: dominantModule.recommendations,
            fillOpacity: fillOpacity,
            strokeOpacity: strokeOpacity,
            strokeWeight: strokeWeight
          });
        }
      }
    }
    
    // Retourner les zones triées par probabilité (plus haute en premier pour z-index)
    return allZones.sort((a, b) => b.probability - a.probability);
  }, []);

  /**
   * Génère une micro-cellule (polygone léger) pour délimitation fine
   * VERSION 3.0 - Hexagones compacts avec espacement naturel
   */
  const generateMicroCell = (centerLat, centerLng, size) => {
    // Hexagone ultra-compact pour micro-délimitation
    const points = [];
    const numSides = 6;
    const scaleFactor = 0.85; // Réduction pour espacement entre cellules
    for (let i = 0; i < numSides; i++) {
      const angle = (60 * i - 30) * Math.PI / 180;
      const lat = centerLat + (size / 111) * Math.sin(angle) * scaleFactor;
      const lng = centerLng + (size / (111 * Math.cos(centerLat * Math.PI / 180))) * Math.cos(angle) * scaleFactor;
      points.push([lat, lng]);
    }
    return points;
  };

  /**
   * Calcule la variation spatiale de probabilité basée sur les facteurs environnementaux
   */
  const calculateSpatialVariation = (moduleKey, gridX, gridY, factors, distance, maxDistance) => {
    // Seed basé sur la position pour des résultats cohérents
    const seed = Math.sin(gridX * 12.9898 + gridY * 78.233) * 43758.5453;
    const noise = (seed - Math.floor(seed));
    
    // Facteur de distance (centre = meilleur pour certains modules)
    const distanceFactor = 1 - (distance / maxDistance) * 0.3;
    
    // Variations spécifiques par module
    let moduleFactor = 1.0;
    
    switch (moduleKey) {
      case 'thermal':
        // Zones thermiques - préfère les zones sud et protégées
        moduleFactor = 0.7 + (gridY > 0 ? 0.3 : 0.1) + noise * 0.2;
        break;
      case 'wetness':
        // Zones humides - concentration dans les bas-fonds
        moduleFactor = 0.6 + (distance < maxDistance * 0.5 ? 0.4 : 0.2) + noise * 0.15;
        break;
      case 'food':
        // Zones alimentaires - distribution variable
        moduleFactor = 0.8 + noise * 0.4 - 0.2;
        break;
      case 'pressure':
        // Zones de pression - inverse de la distance aux routes (simulé)
        moduleFactor = 0.5 + (distance > maxDistance * 0.6 ? 0.5 : 0.2) + noise * 0.1;
        break;
      case 'access':
        // Zones d'accès - près des corridors
        moduleFactor = 0.6 + (Math.abs(gridX) < 3 || Math.abs(gridY) < 3 ? 0.4 : 0.1);
        break;
      case 'corridor':
        // Corridors de déplacement - lignes de mouvement
        moduleFactor = 0.5 + (Math.abs(gridX - gridY) < 4 ? 0.5 : 0.15);
        break;
      case 'canopy':
        // Couvert forestier - variation naturelle
        moduleFactor = 0.7 + noise * 0.5 - 0.1;
        break;
      case 'geoform':
        // Géomorphologie - basé sur le terrain simulé
        moduleFactor = 0.6 + (gridY * 0.02) + noise * 0.3;
        break;
      default:
        moduleFactor = 0.8 + noise * 0.2;
    }
    
    return Math.max(0.3, Math.min(1.5, distanceFactor * moduleFactor));
  };

  /**
   * Génère un hexagone pour une cellule (meilleur rendu que carré)
   */
  const generateHexagonCell = (centerLat, centerLng, size) => {
    const points = [];
    for (let i = 0; i < 6; i++) {
      const angle = (60 * i - 30) * Math.PI / 180;
      const lat = centerLat + (size / 111) * Math.sin(angle);
      const lng = centerLng + (size / (111 * Math.cos(centerLat * Math.PI / 180))) * Math.cos(angle);
      points.push([lat, lng]);
    }
    return points;
  };

  /**
   * Retourne l'interprétation de la probabilité
   */
  const getProbabilityRating = (probability) => {
    if (probability >= 85) return { text: 'Zone optimale', level: 'optimal' };
    if (probability >= 70) return { text: 'Très forte probabilité', level: 'high' };
    if (probability >= 55) return { text: 'Bonne probabilité', level: 'good' };
    if (probability >= 40) return { text: 'Probabilité modérée', level: 'moderate' };
    return { text: 'Faible probabilité', level: 'low' };
  };

  /**
   * Fusionne les zones adjacentes du même module pour des contours plus nets
   */
  const mergeAdjacentZones = (zones) => {
    // Grouper par module
    const grouped = {};
    zones.forEach(zone => {
      if (!grouped[zone.moduleKey]) {
        grouped[zone.moduleKey] = [];
      }
      grouped[zone.moduleKey].push(zone);
    });
    
    // Pour chaque groupe, garder les zones individuelles mais avec opacity variable
    const result = [];
    Object.keys(grouped).forEach(moduleKey => {
      const moduleZones = grouped[moduleKey];
      moduleZones.forEach(zone => {
        // Ajuster l'opacité selon la probabilité
        zone.fillOpacity = 0.25 + (zone.probability / 100) * 0.35;
        result.push(zone);
      });
    });
    
    return result;
  };

  /**
   * Agrège les statistiques par module pour l'affichage dans le panneau
   */
  const aggregateBionicStats = useCallback((zones) => {
    const stats = {};
    
    zones.forEach(zone => {
      if (!stats[zone.moduleKey]) {
        stats[zone.moduleKey] = {
          key: zone.moduleKey,
          name: zone.name,
          label: zone.label,
          color: zone.color,
          icon: zone.icon,
          totalZones: 0,
          avgProbability: 0,
          maxProbability: 0,
          probabilities: []
        };
      }
      
      stats[zone.moduleKey].totalZones++;
      stats[zone.moduleKey].probabilities.push(zone.probability);
      stats[zone.moduleKey].maxProbability = Math.max(
        stats[zone.moduleKey].maxProbability, 
        zone.probability
      );
    });
    
    // Calculer les moyennes
    Object.keys(stats).forEach(key => {
      const probs = stats[key].probabilities;
      stats[key].avgProbability = Math.round(
        probs.reduce((a, b) => a + b, 0) / probs.length
      );
      delete stats[key].probabilities;
    });
    
    return stats;
  }, []);

  // État pour stocker les zones précises générées
  const [bionicPrecisionZones, setBionicPrecisionZones] = useState([]);
  const [bionicModuleStats, setBionicModuleStats] = useState({});

  /**
   * Callback appelé quand l'analyse BIONIC est terminée
   * Génère les zones de haute précision et met à jour l'affichage
   * EXCLUSION D'EAU PERMANENTE: Les zones dans l'eau sont automatiquement filtrées
   */
  const handleBionicAnalysisComplete = useCallback(async (analysisResult) => {
    if (!analysisResult) return;
    
    // Stocker les résultats bruts
    setBionicAnalysisResult(analysisResult);
    
    // Générer les zones de précision
    const centerLat = parseFloat(gpsLatitude) || mapCenter[0];
    const centerLng = parseFloat(gpsLongitude) || mapCenter[1];
    
    let precisionZones = generatePrecisionBionicZones(analysisResult, centerLat, centerLng, 5);
    
    // ============================================
    // EXCLUSION EAU ZONES — DÉSACTIVÉ FRONTEND (Audit V1)
    // Les exclusions sont gérées exclusivement par le backend
    // (zone_engine_core_v2 via Overpass API)
    // ============================================
    
    setBionicPrecisionZones(precisionZones);
    
    // Calculer les statistiques par module
    const stats = aggregateBionicStats(precisionZones);
    setBionicModuleStats(stats);
    
    toast.success(t('bionic_zones_generated'), {
      description: `${precisionZones.length} ${t('micro_zones_calculated')}`
    });
    
    // Activer toutes les couches par défaut
    setBionicLayersVisible({
      thermal: true,
      wetness: true,
      food: true,
      pressure: true,
      access: true,
      corridor: true,
      canopy: true,
      geoform: true
    });
    
    // Ouvrir le panneau des couches et scroll vers la section BIONIC™ Zones
    setShowLayersPanel(true);
    setTimeout(() => {
      if (bionicZonesSectionRef.current) {
        bionicZonesSectionRef.current.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'start' 
        });
      }
    }, 600);
  }, [gpsLatitude, gpsLongitude, mapCenter, generatePrecisionBionicZones, aggregateBionicStats]);

  /**
   * Toggle une couche BIONIC spécifique
   */
  const toggleBionicLayer = useCallback((layerKey) => {
    setBionicLayersVisible(prev => ({
      ...prev,
      [layerKey]: !prev[layerKey]
    }));
  }, []);

  /**
   * Activer/Désactiver toutes les couches BIONIC
   */
  const toggleAllBionicLayers = useCallback((visible) => {
    const newState = {};
    Object.keys(BIONIC_MODULE_CONFIG).forEach(key => {
      newState[key] = visible;
    });
    setBionicLayersVisible(newState);
  }, []);

  /**
   * Effacer l'analyse BIONIC et les couches
   */
  const clearBionicAnalysis = useCallback(() => {
    setBionicAnalysisResult(null);
    setBionicPrecisionZones([]);
    setBionicModuleStats({});
    toast.info('Couches BIONIC™ effacées');
  }, []);

  // ==========================================
  // ANALYSIS FUNCTIONS
  // ==========================================

  // Handle GPS Analysis - triggered automatically after waypoint confirmation
  const handleAnalyzeGPS = async () => {
    let lat, lon;
    
    // Parse coordinates based on format
    if (gpsFormat === 'decimal') {
      lat = parseFloat(gpsLatitude);
      lon = parseFloat(gpsLongitude);
    } else {
      // Convert DMS to decimal
      const latDec = parseFloat(dmsLatDeg) + parseFloat(dmsLatMin)/60 + parseFloat(dmsLatSec)/3600;
      const lonDec = parseFloat(dmsLonDeg) + parseFloat(dmsLonMin)/60 + parseFloat(dmsLonSec)/3600;
      lat = dmsLatDir === 'S' ? -latDec : latDec;
      lon = dmsLonDir === 'W' ? -lonDec : lonDec;
    }
    
    if (isNaN(lat) || isNaN(lon)) {
      toast.error('Coordonnées GPS invalides');
      return;
    }
    
    // Update map center
    setMapCenter([lat, lon]);
    
    // Calculate probability for the location
    try {
      const response = await axios.post(`${API}/territory/analysis/probability`, {
        latitude: lat,
        longitude: lon,
        species: selectedAnalysisSpecies,
        water_distance_m: 300,
        forest_type: 'mixte',
        altitude_m: 350,
        is_transition_zone: true,
        is_coulee: false,
        slope_direction: 'SW',
        road_distance_m: 1500
      });

      setProbabilityData(response.data);
      toast.success(`Analyse complète: ${selectedAnalysisSpecies} - ${response.data.probability_score}% de probabilité`, { duration: 5000 });
    } catch (error) {
      toast.error('Erreur lors de l\'analyse du territoire');
    }
  };

  // Analyse rapide du point actuel sous le curseur (sans créer de waypoint)
  const analyzeCurrentPosition = async () => {
    if (!mouseGpsPreview) {
      toast.error('Déplacez la souris sur la carte pour capturer les coordonnées');
      return;
    }
    
    const lat = mouseGpsPreview.lat;
    const lng = mouseGpsPreview.lng;
    
    toast.info(`${t('quick_analysis_progress')}: ${lat.toFixed(4)}, ${lng.toFixed(4)}...`);
    
    try {
      // Centrer la carte sur le point analysé
      setMapCenter([lat, lng]);
      
      // Lancer l'analyse de probabilité
      const analysisRes = await axios.post(`${API}/territory/analysis/probability`, {
        latitude: lat,
        longitude: lng,
        species: selectedAnalysisSpecies,
        water_distance_m: 300,
        forest_type: 'mixte',
        altitude_m: mouseGpsPreview.altitude || 350,
        is_transition_zone: true,
        is_coulee: false,
        slope_direction: 'SW',
        road_distance_m: 1500
      });
      
      setProbabilityData(analysisRes.data);
      
      // Rechercher les territoires de chasse à proximité
      const huntingRes = await axios.get(`${API}/territory/hunting/search`, {
        params: { lat, lng, radius_km: 50 }
      });
      
      if (huntingRes.data?.all_results) {
        setNearbyTerritories(huntingRes.data.all_results);
        setShowHuntingMarkers(true);
      }
      
      // Générer les zones de probabilité
      generateProbabilityZones();
      
      toast.success(`Point analysé: ${analysisRes.data.probability_score}% de probabilité pour ${selectedAnalysisSpecies}`, {
        description: `${huntingRes.data?.total_count || 0} territoires à proximité`,
        duration: 5000
      });
      
    } catch (error) {
      console.error('Quick analysis error:', error);
      toast.error('Erreur lors de l\'analyse rapide');
    }
  };

  // Calculate probability for current map center
  const calculateProbability = async () => {
    try {
      const response = await axios.post(`${API}/territory/analysis/probability`, {
        latitude: mapCenter[0],
        longitude: mapCenter[1],
        species: selectedAnalysisSpecies,
        // These would ideally come from WMS data analysis
        water_distance_m: 300,
        forest_type: 'mixte',
        altitude_m: 350,
        is_transition_zone: true,
        is_coulee: false,
        slope_direction: 'SW',
        road_distance_m: 1500
      });

      setProbabilityData(response.data);
      toast.success(`Probabilité ${selectedAnalysisSpecies}: ${response.data.probability_score}%`);
    } catch (error) {
      toast.error('Erreur lors du calcul de probabilité');
    }
  };

  // Get cooling zones
  const loadCoolingZones = async () => {
    try {
      const response = await axios.get(`${API}/territory/analysis/cooling-zones`, {
        params: {
          latitude: mapCenter[0],
          longitude: mapCenter[1],
          species: selectedAnalysisSpecies,
          radius_km: 2
        }
      });

      setCoolingZones(response.data);
      toast.success('Zones de fraîcheur chargées');
    } catch (error) {
      toast.error('Erreur lors du chargement des zones');
    }
  };

  // ==========================================
  // GPX IMPORT/EXPORT FUNCTIONS
  // ==========================================

  const [showGpxModal, setShowGpxModal] = useState(false);
  const [gpxImporting, setGpxImporting] = useState(false);
  const gpxInputRef = useRef(null);

  // Export GPX - with local fallback using gpxUtils
  const handleExportGpx = async () => {
    try {
      const response = await axios.get(`${API}/territory/export/gpx`, {
        params: { user_id: userId, include_waypoints: true, include_tracks: true },
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `bionic_territory_${new Date().toISOString().split('T')[0]}.gpx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('Fichier GPX exporté!');
    } catch (error) {
      // Fallback to local export using gpxUtils
      handleExportGpxLocal();
    }
  };

  // Local GPX export (client-side) - uses waypoints from state
  const handleExportGpxLocal = () => {
    if (waypoints.length === 0) {
      toast.error('Aucun waypoint à exporter');
      return;
    }

    try {
      // Convert waypoints to the format expected by downloadGPX
      const waypointsForExport = waypoints.map(wp => ({
        name: wp.name,
        lat: wp.latitude,
        lng: wp.longitude,
        type: wp.waypoint_type || 'custom',
        notes: wp.description || ''
      }));

      downloadGPX(waypointsForExport, 'bionic-waypoints');
      toast.success(`${waypoints.length} waypoints exportés en GPX!`, {
        description: 'Compatible Garmin, Avenza, GPS...'
      });
    } catch (error) {
      console.error('GPX export error:', error);
      toast.error('Erreur lors de l\'export GPX local');
    }
  };

  // Import GPX
  const handleImportGpx = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setGpxImporting(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', userId);
      
      const response = await axios.post(`${API}/territory/import/gpx`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      toast.success(response.data.message);
      loadWaypoints();
      setShowGpxModal(false);
    } catch (error) {
      toast.error('Erreur lors de l\'import GPX');
    } finally {
      setGpxImporting(false);
      if (gpxInputRef.current) gpxInputRef.current.value = '';
    }
  };

  // ==========================================
  // NUTRITION ANALYSIS FUNCTIONS
  // ==========================================

  const [showNutritionModal, setShowNutritionModal] = useState(false);
  const [nutritionAnalysis, setNutritionAnalysis] = useState(null);
  const [nutritionLoading, setNutritionLoading] = useState(false);
  const [selectedForestType, setSelectedForestType] = useState('mixte');
  const [analyzeLocation, setAnalyzeLocation] = useState(null);

  // Analyze nutrition for a waypoint or location
  const analyzeNutrition = async (lat, lon, forestType = 'mixte') => {
    setNutritionLoading(true);
    
    try {
      const response = await axios.post(`${API}/territory/analysis/nutrition`, {
        latitude: lat,
        longitude: lon,
        species: selectedAnalysisSpecies,
        forest_type: forestType,
        water_nearby: true
      });
      
      setNutritionAnalysis(response.data);
      setShowNutritionModal(true);
    } catch (error) {
      toast.error('Erreur lors de l\'analyse nutritionnelle');
    } finally {
      setNutritionLoading(false);
    }
  };

  // Analyze current map center
  const analyzeCurrentLocation = () => {
    setAnalyzeLocation({ lat: mapCenter[0], lon: mapCenter[1] });
    analyzeNutrition(mapCenter[0], mapCenter[1], selectedForestType);
  };

  // ==========================================
  // PROBABILITY ZONES - Colored Grid
  // ==========================================

  // Generate probability zones around map center
  const generateProbabilityZones = async () => {
    setLoadingZones(true);
    const zones = [];
    const centerLat = mapCenter[0];
    const centerLon = mapCenter[1];
    const gridSize = 0.01; // ~1km grid cells
    const gridRadius = 5; // 5x5 grid = 10km x 10km area

    try {
      for (let i = -gridRadius; i <= gridRadius; i++) {
        for (let j = -gridRadius; j <= gridRadius; j++) {
          const lat = centerLat + (i * gridSize);
          const lon = centerLon + (j * gridSize);
          
          // Calculate probability based on position (simulated factors)
          const distFromCenter = Math.sqrt(i*i + j*j);
          const baseScore = 85 - (distFromCenter * 5);
          
          // Add some randomness and variation based on position
          const variation = Math.sin(lat * 100) * 10 + Math.cos(lon * 100) * 10;
          const score = Math.max(0, Math.min(100, baseScore + variation));
          
          // Determine color based on score
          let color, category;
          if (score >= 70) {
            color = 'rgba(34, 197, 94, 0.4)'; // Green - High probability
            category = 'high';
          } else if (score >= 50) {
            color = 'rgba(234, 179, 8, 0.4)'; // Yellow - Medium probability
            category = 'medium';
          } else {
            color = 'rgba(239, 68, 68, 0.3)'; // Red - Low probability
            category = 'low';
          }
          
          zones.push({
            bounds: [
              [lat - gridSize/2, lon - gridSize/2],
              [lat + gridSize/2, lon + gridSize/2]
            ],
            score: Math.round(score),
            color,
            category,
            lat,
            lon
          });
        }
      }
      
      setProbabilityZones(zones);
      toast.success(`${zones.length} zones de probabilité générées pour ${selectedAnalysisSpecies}`);
    } catch (error) {
      toast.error('Erreur lors de la génération des zones');
    } finally {
      setLoadingZones(false);
    }
  };

  // ==========================================
  // GUIDED ROUTE / PARCOURS GUIDÉ
  // ==========================================

  // Generate guided route through waypoints
  const generateGuidedRoute = async () => {
    if (waypoints.length < 2) {
      toast.error('Au moins 2 waypoints sont nécessaires pour créer un parcours guidé');
      return;
    }

    setLoadingGuidedRoute(true);
    try {
      const requestData = {
        species: selectedAnalysisSpecies,
        optimize_for: guidedRouteOptimization,
        start_from_current_position: !!currentPosition,
        current_lat: currentPosition?.lat || null,
        current_lng: currentPosition?.lng || null
      };

      const response = await axios.post(
        `${API}/territory/analysis/guided-route`,
        requestData,
        { params: { user_id: userId } }
      );

      setGuidedRoute(response.data);
      setShowGuidedRoutePanel(true);

      // Toast with summary
      toast.success(
        `${t('route_created')}: ${response.data.total_distance_km} km, ${response.data.waypoint_order.length} ${t('points')}`,
        { duration: 5000 }
      );

      // Show high probability notification
      if (response.data.highest_probability_zone) {
        const zone = response.data.highest_probability_zone;
        toast.info(
          `Meilleure zone: ${zone.name} - ${zone.probability}% de probabilité`,
          { duration: 6000 }
        );
      }

    } catch (error) {
      console.error('Error generating guided route:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de la génération du parcours');
    } finally {
      setLoadingGuidedRoute(false);
    }
  };

  // Clear guided route
  const clearGuidedRoute = () => {
    setGuidedRoute(null);
    setShowGuidedRoutePanel(false);
    toast.info('Parcours guidé effacé');
  };

  // Navigate to a waypoint on the route
  const navigateToRoutePoint = (point) => {
    setMapCenter([point.lat, point.lng]);
    setMapZoom(15);
  };

  // ==========================================
  // TERRITORY FILTER FUNCTIONS
  // ==========================================

  // Analyze selected territory
  const analyzeTerritory = async () => {
    if (!selectedTerritoryType || !selectedZoneNumber) {
      toast.error('Sélectionnez un type de territoire et un numéro de zone');
      return;
    }

    setLoadingTerritory(true);
    
    try {
      // Search in hunting territories from API
      const searchQuery = selectedZoneNumber.toLowerCase();
      const matchingTerritories = huntingTerritories.filter(t => 
        t.name.toLowerCase().includes(searchQuery) ||
        (t.region && t.region.toLowerCase().includes(searchQuery))
      );
      
      // Also filter by type
      const typeMap = {
        zec: 'ZEC',
        sepaq: 'Réserve faunique',
        pourvoirie: 'Pourvoirie'
      };
      
      const targetType = typeMap[selectedTerritoryType];
      let zone = null;
      
      if (targetType) {
        zone = matchingTerritories.find(t => t.type === targetType);
      }
      
      if (!zone) {
        zone = matchingTerritories[0]; // Fallback to first match
      }
      
      if (!zone) {
        // Try direct API search
        const response = await axios.get(`${API}/territory/hunting/territories`, {
          params: { query: searchQuery, territory_type: selectedTerritoryType }
        });
        
        if (response.data?.territories?.length > 0) {
          zone = response.data.territories[0];
        }
      }
      
      if (!zone) {
        toast.error(`Territoire "${selectedZoneNumber}" non trouvé pour ${TERRITORY_TYPES[selectedTerritoryType]?.name}`);
        setLoadingTerritory(false);
        return;
      }

      // Calculate quality scores based on species and region
      const speciesCount = zone.species?.length || 0;
      const hasOrignal = zone.species?.includes('orignal');
      const hasChevreuil = zone.species?.includes('chevreuil');
      const hasOurs = zone.species?.includes('ours');
      
      const qualityScore = Math.min(95, 60 + (speciesCount * 10) + (hasOrignal ? 5 : 0));
      
      // Generate success rates based on species
      const successRate = {};
      if (hasOrignal) successRate.orignal = 35 + Math.floor(Math.random() * 20);
      if (hasChevreuil) successRate.chevreuil = 30 + Math.floor(Math.random() * 25);
      if (hasOurs) successRate.ours = 20 + Math.floor(Math.random() * 20);
      
      // Generate analysis
      const analysis = {
        ...zone,
        name: zone.name,
        lat: zone.lat,
        lng: zone.lng,
        region: zone.region,
        type: selectedTerritoryType,
        typeName: zone.type || TERRITORY_TYPES[selectedTerritoryType]?.name,
        typeColor: TERRITORY_TYPES[selectedTerritoryType]?.color,
        website: zone.website,
        qualityScore: qualityScore,
        huntingPressure: speciesCount > 3 ? 'faible' : speciesCount > 2 ? 'moyen' : 'modéré',
        accessibility: 'bonne',
        habitat: qualityScore > 80 ? 'excellent' : qualityScore > 60 ? 'très bon' : 'bon',
        successRate: successRate,
        indices: {
          qualite: qualityScore,
          pression: speciesCount > 3 ? 80 : speciesCount > 2 ? 65 : 50,
          accessibilite: 75,
          habitat: qualityScore > 80 ? 90 : qualityScore > 60 ? 75 : 60
        },
        recommendations: generateTerritoryRecommendations({ 
          ...zone, 
          qualityScore, 
          successRate,
          huntingPressure: speciesCount > 3 ? 'faible' : 'moyen'
        }, selectedTerritoryType),
        warnings: generateTerritoryWarnings({ 
          ...zone, 
          huntingPressure: speciesCount > 3 ? 'faible' : 'moyen',
          accessibility: 'bonne'
        }, selectedTerritoryType),
        reglements: getTerritoryReglements(selectedTerritoryType)
      };

      setTerritoryAnalysis(analysis);
      setMapCenter([zone.lat, zone.lng]);
      setMapZoom(10);
      setShowHuntingMarkers(true);
      
      // Load nearby territories
      searchNearbyTerritories(zone.lat, zone.lng, 100);
      
      toast.success(`${t('analysis_completed')}: ${zone.name}`);
    } catch (error) {
      console.error('Error analyzing territory:', error);
      toast.error('Erreur lors de l\'analyse du territoire');
    } finally {
      setLoadingTerritory(false);
    }
  };

  // Generate recommendations based on territory data
  const generateTerritoryRecommendations = (zone, type) => {
    const recs = [];
    
    // Species recommendations
    const bestSpecies = Object.entries(zone.successRate || {}).sort((a, b) => b[1] - a[1])[0];
    if (bestSpecies && bestSpecies[1] > 0) {
      recs.push(`Meilleure espèce: ${bestSpecies[0]} (${bestSpecies[1]}% de succès)`);
    }
    
    // Timing recommendations
    if (zone.qualityScore >= 85) {
      recs.push('Zone à fort potentiel - Réservez tôt en saison');
    }
    if (zone.huntingPressure === 'faible' || zone.huntingPressure === 'très faible') {
      recs.push('Pression de chasse faible - Conditions idéales');
    }
    if (type === 'sepaq' && zone.tirage) {
      recs.push('Tirage au sort requis - Inscrivez-vous sur Sépaq');
    }
    if (type === 'pourvoirie' && zone.services) {
      recs.push(`Services: ${zone.services.join(', ')}`);
    }
    
    return recs;
  };

  // Generate warnings for territory
  const generateTerritoryWarnings = (zone, type) => {
    const warnings = [];
    
    if (zone.huntingPressure === 'élevé') {
      warnings.push('Forte pression de chasse - Planifiez à l\'avance');
    }
    if (type === 'prive') {
      warnings.push('Autorisation du propriétaire obligatoire');
    }
    if (type === 'refuge') {
      warnings.push('Restrictions spéciales - Vérifiez les règlements');
    }
    if (zone.accessibility === 'moyenne' || zone.accessibility === 'difficile') {
      warnings.push('Accès difficile - Véhicule 4x4 recommandé');
    }
    
    return warnings;
  };

  // Get regulations for territory type
  const getTerritoryReglements = (type) => {
    const reglements = {
      zec: ['Droits d\'accès requis', 'Enregistrement obligatoire', 'Quotas selon zones'],
      sepaq: ['Tirage au sort ou réservation', 'Quota strict', 'Transport du gibier réglementé'],
      clic: ['Permis de chasse valide', 'Respect des dates de saison', 'Limites de prises'],
      pourvoirie: ['Réservation obligatoire', 'Forfait avec ou sans guide', 'Règles internes'],
      prive: ['Autorisation écrite requise', 'Assurance responsabilité recommandée', 'Respect des limites'],
      refuge: ['Permis spécial requis', 'Zones interdites', 'Espèces protégées']
    };
    return reglements[type] || [];
  };

  // Clear territory analysis
  const clearTerritoryAnalysis = () => {
    setTerritoryAnalysis(null);
    setSelectedTerritoryType('');
    setSelectedZoneNumber('');
  };

  // ==========================================
  // SHOPPING CART FUNCTIONS
  // ==========================================

  // Add product to cart
  const addToCart = (product) => {
    const existingItem = cart.find(item => item.id === product.id);
    if (existingItem) {
      setCart(cart.map(item => 
        item.id === product.id 
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
    toast.success(`${product.name} ajouté au panier`);
  };

  // Remove product from cart
  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.id !== productId));
  };

  // Update quantity
  const updateCartQuantity = (productId, delta) => {
    setCart(cart.map(item => {
      if (item.id === productId) {
        const newQty = item.quantity + delta;
        return newQty > 0 ? { ...item, quantity: newQty } : item;
      }
      return item;
    }).filter(item => item.quantity > 0));
  };

  // Calculate cart total
  const getCartTotal = () => {
    return cart.reduce((total, item) => {
      const price = item.price || 29.99; // Default price
      return total + (price * item.quantity);
    }, 0);
  };

  // Submit order for admin approval
  const submitOrder = async () => {
    if (!orderName || !orderEmail) {
      toast.error('Veuillez remplir votre nom et email');
      return;
    }

    setSubmittingOrder(true);
    
    try {
      const orderData = {
        customer_name: orderName,
        customer_email: orderEmail,
        customer_phone: orderPhone,
        notes: orderNotes,
        items: cart.map(item => ({
          product_id: item.id,
          product_name: item.name,
          quantity: item.quantity,
          price: item.price || 29.99
        })),
        total: getCartTotal(),
        status: 'pending_approval',
        source: 'territory_bionic',
        user_id: userId,
        created_at: new Date().toISOString()
      };

      await axios.post(`${API}/territory/orders`, orderData);
      
      toast.success('Commande envoyée! Elle sera examinée par l\'administrateur.');
      setCart([]);
      setShowOrderForm(false);
      setShowCartModal(false);
      setOrderName('');
      setOrderEmail('');
      setOrderPhone('');
      setOrderNotes('');
    } catch (error) {
      toast.error('Erreur lors de l\'envoi de la commande');
    } finally {
      setSubmittingOrder(false);
    }
  };

  // Load waypoints on mount
  useEffect(() => {
    if (userId) {
      loadWaypoints();
    }
  }, [userId]);

  // Cleanup tracking on unmount
  useEffect(() => {
    return () => {
      if (watchIdRef.current) {
        navigator.geolocation.clearWatch(watchIdRef.current);
      }
    };
  }, []);

  // Handle navigation from external components (e.g., GpsHotspots)
  useEffect(() => {
    if (navigateToCoords && navigateToCoords.lat && navigateToCoords.lng) {
      const { lat, lng } = navigateToCoords;
      
      // Update map center
      setMapCenter([lat, lng]);
      
      // Inject coordinates into GPS analysis
      setGpsLatitude(lat.toFixed(6));
      setGpsLongitude(lng.toFixed(6));
      
      // Update DMS
      setDmsLatDir(lat >= 0 ? 'N' : 'S');
      const absLat = Math.abs(lat);
      setDmsLatDeg(Math.floor(absLat).toString());
      const latMinFloat = (absLat - Math.floor(absLat)) * 60;
      setDmsLatMin(Math.floor(latMinFloat).toString());
      setDmsLatSec(((latMinFloat - Math.floor(latMinFloat)) * 60).toFixed(2));
      
      setDmsLonDir(lng >= 0 ? 'E' : 'W');
      const absLon = Math.abs(lng);
      setDmsLonDeg(Math.floor(absLon).toString());
      const lonMinFloat = (absLon - Math.floor(absLon)) * 60;
      setDmsLonMin(Math.floor(lonMinFloat).toString());
      setDmsLonSec(((lonMinFloat - Math.floor(lonMinFloat)) * 60).toFixed(2));
      
      toast.success(`Navigation vers: ${lat.toFixed(4)}, ${lng.toFixed(4)}`, {
        description: 'Coordonnées injectées dans Analyse GPS'
      });
      
      // Notify parent that navigation is complete
      if (onNavigationComplete) {
        onNavigationComplete();
      }
    }
  }, [navigateToCoords, onNavigationComplete]);

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      {/* Header - Using extracted TerritoryHeader component */}
      <TerritoryHeader
        userName={userName}
        onLogout={onLogout}
        stats={stats}
        cartItemCount={cart.reduce((sum, item) => sum + item.quantity, 0)}
        onCartClick={() => setShowCartModal(true)}
        onBackClick={() => window.location.href = '/'}
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <div className="w-80 bg-card border-r border-border p-4 overflow-y-auto flex-shrink-0">
          {/* Species Filter - Using extracted component */}
          <SpeciesFilter
            selectedSpecies={selectedSpecies}
            onSpeciesChange={setSelectedSpecies}
          />

          {/* BIONIC™ Territory Engine Button */}
          <Card className="bg-gradient-to-r from-[#f5a623]/10 to-orange-500/10 border-[#f5a623]/30 mb-4">
            <CardContent className="p-3">
              <Button
                className="w-full bg-gradient-to-r from-[#f5a623] to-orange-500 hover:from-[#f5a623]/90 hover:to-orange-500/90 text-black font-medium"
                onClick={() => setShowBionicAnalyzer(true)}
                data-testid="bionic-engine-btn"
              >
                <Brain className="h-4 w-4 mr-2" />
                BIONIC™ Territory Engine
                <Zap className="h-4 w-4 ml-2" />
              </Button>
              <p className="text-gray-400 text-[10px] text-center mt-2">
                Analyse avancée • IA prédictive • Modules thématiques
              </p>
            </CardContent>
          </Card>

          {/* Layer Controls */}
          <Card className="bg-background border-border mb-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm flex items-center gap-2">
                <Layers className="h-4 w-4 text-[#f5a623]" />
                Couches de base
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <Activity className="h-4 w-4 text-red-500" />
                  Heatmap activité
                </Label>
                <Switch checked={showHeatmap} onCheckedChange={setShowHeatmap} />
              </div>
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <Eye className="h-4 w-4 text-green-500" />
                  Observations
                </Label>
                <Switch checked={showEvents} onCheckedChange={setShowEvents} />
              </div>
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <Camera className="h-4 w-4 text-blue-500" />
                  Caméras
                </Label>
                <Switch checked={showCameras} onCheckedChange={setShowCameras} />
              </div>
            </CardContent>
          </Card>

          {/* Advanced Geological Layers */}
          <Card className="bg-background border-border mb-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm flex items-center gap-2">
                <Map className="h-4 w-4 text-[#f5a623]" />
                Cartes géologiques
                <Badge className="ml-auto bg-green-500/20 text-green-400 text-[10px]">Québec</Badge>
              </CardTitle>
              <CardDescription className="text-xs">
                Données du gouvernement du Québec
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <Trees className="h-4 w-4 text-green-600" />
                  Couverture forestière
                </Label>
                <Switch checked={layerForet} onCheckedChange={setLayerForet} />
              </div>
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <Waves className="h-4 w-4 text-blue-500" />
                  Hydrographie (eau)
                </Label>
                <Switch checked={layerHydro} onCheckedChange={setLayerHydro} />
              </div>
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <Mountain className="h-4 w-4 text-amber-600" />
                  Relief / Courbes
                </Label>
                <Switch checked={layerTopo} onCheckedChange={setLayerTopo} />
              </div>
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <Route className="h-4 w-4 text-gray-400" />
                  Routes / Chemins
                </Label>
                <Switch checked={layerRoutes} onCheckedChange={setLayerRoutes} />
              </div>
            </CardContent>
          </Card>

          {/* Analysis Layers */}
          <Card className="bg-background border-border mb-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-[#f5a623]" />
                Analyse par espèce
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <Label className="text-gray-400 text-xs">Espèce à analyser</Label>
                <Select value={selectedAnalysisSpecies} onValueChange={setSelectedAnalysisSpecies}>
                  <SelectTrigger className="bg-card border-border mt-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="orignal"><CircleDot className="h-4 w-4 inline mr-2" />Orignal</SelectItem>
                    <SelectItem value="chevreuil"><CircleDot className="h-4 w-4 inline mr-2" />Chevreuil</SelectItem>
                    <SelectItem value="ours"><CircleDot className="h-4 w-4 inline mr-2" />Ours</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <CircleDot className="h-4 w-4 text-purple-500" />
                  Probabilité présence
                </Label>
                <Switch checked={layerProbability} onCheckedChange={(v) => {
                  setLayerProbability(v);
                  if (v) calculateProbability();
                }} />
              </div>

              {/* Generate Probability Zones Button */}
              <Button 
                variant="outline" 
                size="sm" 
                className="w-full border-dashed"
                onClick={generateProbabilityZones}
                disabled={loadingZones}
              >
                {loadingZones ? (
                  <><RefreshCw className="h-4 w-4 mr-2 animate-spin" /> Génération...</>
                ) : (
                  <><Map className="h-4 w-4 mr-2" /> Afficher zones colorées</>
                )}
              </Button>
              
              {/* Probability Zone Legend */}
              {probabilityZones.length > 0 && (
                <div className="p-2 bg-card rounded border border-border">
                  <p className="text-xs text-gray-400 mb-2">Légende des zones:</p>
                  <div className="flex items-center gap-3 text-xs">
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 rounded bg-green-500/60"></div>
                      <span className="text-green-400">Élevée</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 rounded bg-yellow-500/60"></div>
                      <span className="text-yellow-400">Moyenne</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className="w-3 h-3 rounded bg-red-500/60"></div>
                      <span className="text-red-400">Faible</span>
                    </div>
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="w-full mt-2 text-xs h-7"
                    onClick={() => setProbabilityZones([])}
                  >
                    <X className="h-3 w-3 mr-1" /> Effacer zones
                  </Button>
                </div>
              )}
              
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <TreePine className="h-4 w-4 text-emerald-600" />
                  Zones de refuge
                </Label>
                <Switch checked={layerRefuge} onCheckedChange={setLayerRefuge} />
              </div>
              
              <div className="flex items-center justify-between">
                <Label className="text-gray-300 text-sm flex items-center gap-2">
                  <Thermometer className="h-4 w-4 text-cyan-500" />
                  Zones de fraîcheur
                </Label>
                <Switch checked={layerCooling} onCheckedChange={(v) => {
                  setLayerCooling(v);
                  if (v) loadCoolingZones();
                }} />
              </div>

              {/* Probability Result */}
              {probabilityData && layerProbability && (
                <div className="mt-3 p-3 bg-card rounded-lg border border-border">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white text-sm font-medium">Score de probabilité</span>
                    <Badge className={`${probabilityData.probability_score >= 70 ? 'bg-green-500' : probabilityData.probability_score >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`}>
                      {probabilityData.probability_score}%
                    </Badge>
                  </div>
                  <div className="text-xs text-gray-400">
                    Confiance: {probabilityData.confidence}
                  </div>
                  {probabilityData.recommendations?.map((rec, idx) => (
                    <div key={idx} className="text-xs text-gray-300 mt-1 flex items-start gap-1">
                      <ChevronRight className="h-3 w-3 text-[#f5a623] mt-0.5 flex-shrink-0" />
                      {rec}
                    </div>
                  ))}
                </div>
              )}

              {/* Cooling Zones Info */}
              {coolingZones && layerCooling && (
                <div className="mt-3 p-3 bg-card rounded-lg border border-border">
                  <div className="text-white text-sm font-medium mb-2">Zones de fraîcheur</div>
                  {coolingZones.recommended_zones?.slice(0, 3).map((zone, idx) => (
                    <div key={idx} className="text-xs text-gray-300 mb-2">
                      <div className="flex items-center gap-1">
                        <Badge variant="outline" className={`text-[10px] ${zone.priority === 'high' ? 'border-red-500 text-red-400' : 'border-yellow-500 text-yellow-400'}`}>
                          {zone.priority}
                        </Badge>
                        <span className="text-white">{zone.name}</span>
                      </div>
                      <div className="text-gray-400 ml-4">{zone.description}</div>
                    </div>
                  ))}
                  <div className="text-xs text-cyan-400 mt-2">
                    🕐 Meilleurs moments: {coolingZones.best_times?.join(', ')}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* GPS Tracking / Navigation */}
          <Card className="bg-background border-border mb-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm flex items-center gap-2">
                <Navigation className="h-4 w-4 text-[#f5a623]" />
                Navigation GPS
                <Badge className="ml-auto bg-blue-500/20 text-blue-400 text-[10px]">Avenza</Badge>
              </CardTitle>
              <CardDescription className="text-xs">
                Géolocalisation et tracé en temps réel
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Current Position */}
              {currentPosition && (
                <div className="p-2 bg-card rounded border border-green-500/30">
                  <div className="text-xs text-green-400 flex items-center gap-1">
                    <CircleDot className="h-3 w-3 animate-pulse" />
                    Position actuelle
                  </div>
                  <div className="text-white text-sm">
                    {currentPosition.lat.toFixed(5)}, {currentPosition.lng.toFixed(5)}
                  </div>
                  {currentPosition.accuracy && (
                    <div className="text-xs text-gray-400">Précision: ±{currentPosition.accuracy.toFixed(0)}m</div>
                  )}
                </div>
              )}

              {/* Tracking Controls */}
              <div className="flex gap-2">
                {!isTracking ? (
                  <Button 
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                    size="sm"
                    onClick={startTracking}
                  >
                    <Play className="h-4 w-4 mr-1" />
                    Démarrer tracé
                  </Button>
                ) : (
                  <Button 
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white"
                    size="sm"
                    onClick={stopTracking}
                  >
                    <Square className="h-4 w-4 mr-1" />
                    Arrêter ({trackPoints.length} pts)
                  </Button>
                )}
              </div>

              {/* Track Info */}
              {isTracking && trackPoints.length > 0 && (
                <div className="text-xs text-gray-400">
                  Distance: {calculateTotalDistance(trackPoints).toFixed(2)} km
                </div>
              )}

              {/* Waypoint Controls */}
              <div className="border-t border-border pt-3 mt-3">
                <div className="flex items-center justify-between mb-2">
                  <Label className="text-gray-400 text-xs">Waypoints ({waypoints.length})</Label>
                  {waypoints.length > 0 && (
                    <div className="flex gap-1">
                      <Button 
                        variant="ghost" 
                        size="sm"
                        className="h-6 px-2 text-xs text-blue-400 hover:text-blue-300 hover:bg-blue-500/10"
                        onClick={handleExportGpxLocal}
                        title="Export GPX rapide"
                        data-testid="export-gpx-quick-btn"
                      >
                        <Download className="h-3 w-3 mr-1" />
                        GPX
                      </Button>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        className="h-6 px-2 text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10"
                        onClick={deleteAllWaypoints}
                      >
                        <RotateCcw className="h-3 w-3 mr-1" />
                        Effacer
                      </Button>
                    </div>
                  )}
                </div>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="w-full"
                  onClick={getCurrentPositionForWaypoint}
                >
                  <Flag className="h-4 w-4 mr-1" />
                  Ajouter waypoint ici
                </Button>
                
                {/* Waypoints List */}
                {waypoints.length > 0 && (
                  <div className="mt-2 max-h-32 overflow-y-auto space-y-1">
                    {waypoints.slice(0, 5).map((wp) => (
                      <div key={wp.id} className="flex items-center justify-between p-1.5 bg-card rounded text-xs">
                        <div className="flex items-center gap-1">
                          <Bookmark className="h-3 w-3 text-[#f5a623]" />
                          <span className="text-white truncate max-w-[120px]">{wp.name}</span>
                        </div>
                        <button 
                          onClick={() => deleteWaypoint(wp.id)}
                          className="text-red-400 hover:text-red-300"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                      </div>
                    ))}
                    {waypoints.length > 5 && (
                      <div className="text-xs text-gray-500 text-center">
                        +{waypoints.length - 5} autres waypoints
                      </div>
                    )}
                  </div>
                )}

                {/* Guided Route / Parcours Guidé Section */}
                {waypoints.length >= 2 && (
                  <div className="mt-3 pt-3 border-t border-border">
                    <div className="flex items-center gap-2 mb-2">
                      <Navigation className="h-4 w-4 text-green-500" />
                      <Label className="text-white text-xs font-semibold">Parcours Guidé</Label>
                      <Badge className="bg-green-500/20 text-green-400 text-[9px]">IA</Badge>
                    </div>
                    
                    <div className="space-y-2">
                      <div>
                        <Label className="text-gray-400 text-[10px]">Optimiser pour</Label>
                        <Select value={guidedRouteOptimization} onValueChange={setGuidedRouteOptimization}>
                          <SelectTrigger className="bg-card border-border mt-0.5 h-8 text-xs">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="balanced">
                              <span className="flex items-center gap-1"><TrendingUp className="h-3 w-3" /> {t('optimization_balanced')}</span>
                            </SelectItem>
                            <SelectItem value="probability">{t('optimization_probability')}</SelectItem>
                            <SelectItem value="distance">
                              <span className="flex items-center gap-1"><Ruler className="h-3 w-3" /> {t('optimization_distance')}</span>
                            </SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <Button 
                        onClick={generateGuidedRoute}
                        disabled={loadingGuidedRoute || waypoints.length < 2}
                        className="w-full bg-green-600 hover:bg-green-700 text-white"
                        size="sm"
                      >
                        {loadingGuidedRoute ? (
                          <><Loader2 className="h-3 w-3 mr-1 animate-spin" /> Calcul...</>
                        ) : (
                          <><Route className="h-3 w-3 mr-1" /> Générer parcours ({waypoints.length} pts)</>
                        )}
                      </Button>

                      {guidedRoute && (
                        <Button 
                          onClick={clearGuidedRoute}
                          variant="outline"
                          className="w-full text-red-400 border-red-400/50 hover:bg-red-400/10"
                          size="sm"
                        >
                          <X className="h-3 w-3 mr-1" /> Effacer parcours
                        </Button>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* GPX Import/Export */}
              <div className="border-t border-border pt-3 mt-3">
                <Label className="text-gray-400 text-xs mb-2 block">Import/Export GPX</Label>
                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="flex-1"
                    onClick={handleExportGpx}
                  >
                    <Download className="h-3 w-3 mr-1" />
                    Export
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="flex-1"
                    onClick={() => gpxInputRef.current?.click()}
                    disabled={gpxImporting}
                  >
                    <Upload className="h-3 w-3 mr-1" />
                    Import
                  </Button>
                  <input
                    type="file"
                    ref={gpxInputRef}
                    accept=".gpx"
                    onChange={handleImportGpx}
                    className="hidden"
                  />
                </div>
                <p className="text-[10px] text-gray-500 mt-1">Compatible Avenza, Garmin, etc.</p>
              </div>
            </CardContent>
          </Card>

          {/* Nutrition Analysis */}
          <Card className="bg-background border-border mb-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm flex items-center gap-2">
                <TreePine className="h-4 w-4 text-[#f5a623]" />
                Analyse Alimentation
                <Badge className="ml-auto bg-[#f5a623]/20 text-[#f5a623] text-[10px]">BIONIC™</Badge>
              </CardTitle>
              <CardDescription className="text-xs">
                Analyse nutritionnelle et recommandations produits
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <Label className="text-gray-400 text-xs">{t('forest_cover_type')}</Label>
                <Select value={selectedForestType} onValueChange={setSelectedForestType}>
                  <SelectTrigger className="bg-card border-border mt-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="mixte">
                      <span className="flex items-center gap-2"><TreePine className="h-4 w-4 text-green-500" /><Trees className="h-4 w-4 text-green-600" /> {t('forest_mixed')}</span>
                    </SelectItem>
                    <SelectItem value="feuillus">
                      <span className="flex items-center gap-2"><Trees className="h-4 w-4 text-green-600" /> {t('forest_deciduous')}</span>
                    </SelectItem>
                    <SelectItem value="coniferes">
                      <span className="flex items-center gap-2"><TreePine className="h-4 w-4 text-green-500" /> {t('forest_conifers')}</span>
                    </SelectItem>
                    <SelectItem value="regeneration">
                      <span className="flex items-center gap-2"><Leaf className="h-4 w-4 text-green-400" /> {t('forest_regeneration')}</span>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <Button 
                className="w-full btn-golden text-black"
                onClick={analyzeCurrentLocation}
                disabled={nutritionLoading}
              >
                {nutritionLoading ? (
                  <><RefreshCw className="h-4 w-4 mr-2 animate-spin" /> Analyse...</>
                ) : (
                  <><TrendingUp className="h-4 w-4 mr-2" /> Analyser ce site</>
                )}
              </Button>
              
              <p className="text-[10px] text-gray-500 text-center">
                Analyse les besoins nutritionnels du {selectedAnalysisSpecies} et propose les produits BIONIC™ adaptés
              </p>
            </CardContent>
          </Card>

          {/* Upload Photo */}
          <Card className="bg-background border-border mb-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm flex items-center gap-2">
                <Upload className="h-4 w-4 text-[#f5a623]" />
                Upload Photo
              </CardTitle>
              <CardDescription className="text-xs">
                L'IA identifiera automatiquement l'espèce
              </CardDescription>
            </CardHeader>
            <CardContent>
              <input
                type="file"
                ref={fileInputRef}
                accept="image/*"
                onChange={handlePhotoUpload}
                className="hidden"
                id="photo-upload"
              />
              <Button 
                className="w-full btn-golden text-black"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
              >
                {uploading ? (
                  <><RefreshCw className="h-4 w-4 mr-2 animate-spin" /> Analyse en cours...</>
                ) : (
                  <><Camera className="h-4 w-4 mr-2" /> Uploader une photo</>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Recent Events */}
          <Card className="bg-background border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-white text-sm flex items-center gap-2">
                <Activity className="h-4 w-4 text-[#f5a623]" />
                Événements récents
              </CardTitle>
            </CardHeader>
            <CardContent className="max-h-64 overflow-y-auto">
              {filteredEvents.length === 0 ? (
                <p className="text-gray-500 text-sm text-center py-4">Aucun événement</p>
              ) : (
                <div className="space-y-2">
                  {filteredEvents.slice(0, 10).map((event) => (
                    <div 
                      key={event.id}
                      className="flex items-center gap-2 p-2 bg-card rounded-lg cursor-pointer hover:bg-card/80 transition-colors"
                      onClick={() => setMapCenter([event.latitude, event.longitude])}
                    >
                      <span className="text-xl">
                        <CircleDot className="h-4 w-4 inline" />
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className="text-white text-sm font-medium truncate">
                          {SPECIES_CONFIG[event.species]?.label || event.species}
                        </p>
                        <p className="text-gray-500 text-xs">
                          {new Date(event.captured_at).toLocaleDateString('fr-CA', {
                            day: 'numeric',
                            month: 'short',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                      {event.species_confidence && (
                        <Badge variant="outline" className="text-xs">
                          {(event.species_confidence * 100).toFixed(0)}%
                        </Badge>
                      )}
                      <ChevronRight className="h-4 w-4 text-gray-500" />
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Map */}
        <div className="flex-1 relative overflow-hidden">
          {loading && (
            <div className="absolute inset-0 bg-black/50 z-[1000] flex items-center justify-center">
              <div className="text-white flex items-center gap-2">
                <RefreshCw className="h-6 w-6 animate-spin" />
                Chargement...
              </div>
            </div>
          )}
          
          <MapContainer
            center={mapCenter}
            zoom={mapZoom}
            style={{ height: '100%', width: '100%' }}
            className="z-0"
            zoomControl={false}
          >
            <MapCenterController center={mapCenter} zoom={mapZoom} />
            <MapClickHandler activeTool={activeTool} onMapClick={handleMapClick} onMouseMove={handleMouseMove} />
            <ZoomControlPosition />
            <ZoomSyncComponent zoom={mapZoom} />
            
            {/* Base Layers - Controlled by selectedBaseLayer state */}
            {selectedBaseLayer === 'carte' && (
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
            )}
            {/* Satellite - Version originale simple (Esri World Imagery) */}
            {selectedBaseLayer === 'satellite' && (
              <>
                <TileLayer
                  attribution='&copy; Esri World Imagery'
                  url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                />
                {/* Labels */}
                <TileLayer
                  attribution='&copy; Esri'
                  url="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
                  zIndex={1000}
                />
              </>
            )}

            {/* Google Earth Style - Alternative gratuite (USGS/Esri Clarity) */}
            {selectedBaseLayer === 'google-earth' && (
              <>
                {/* High-resolution imagery similar to Google Earth */}
                <TileLayer
                  attribution='&copy; Esri, Maxar, Earthstar Geographics'
                  url="https://clarity.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                />
                {/* Roads and transportation overlay */}
                <TileLayer
                  attribution='&copy; Esri'
                  url="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}"
                  zIndex={500}
                />
                {/* Labels and boundaries */}
                <TileLayer
                  attribution='&copy; Esri'
                  url="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
                  zIndex={1000}
                />
              </>
            )}

            {selectedBaseLayer === 'topographie' && (
              <TileLayer
                attribution='&copy; OpenTopoMap'
                url="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
              />
            )}

            {/* Heatmap Layer */}
            {showHeatmap && heatmapData.length > 0 && (
              <HeatmapLayer points={heatmapData} radius={30} />
            )}

            {/* Camera Markers */}
            {showCameras && cameras.map((camera) => (
              camera.latitude && camera.longitude && (
                <Marker
                  key={camera.id}
                  position={[camera.latitude, camera.longitude]}
                  icon={createCustomIcon('#3b82f6', 'camera')}
                >
                  <Popup>
                    <div className="text-sm min-w-48">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <div>
                          <p className="font-bold text-gray-800">{camera.label}</p>
                          <p className="text-gray-500 text-xs">{camera.brand}</p>
                        </div>
                        <button
                          onClick={() => {
                            if (window.confirm(`${t('confirm_delete_camera')} "${camera.label}" ?`)) {
                              // Remove camera from local state
                              setCameras(prev => prev.filter(c => c.id !== camera.id));
                              toast.success(t('camera_deleted'));
                            }
                          }}
                          className="p-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors flex-shrink-0"
                          title={t('delete_camera')}
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                      <p className={`text-sm ${camera.connected ? 'text-green-600' : 'text-red-600'}`}>
                        {camera.connected ? t('connected') : t('not_connected')}
                      </p>
                    </div>
                  </Popup>
                </Marker>
              )
            ))}

            {/* Event Markers */}
            {showEvents && filteredEvents.map((event) => {
              const speciesConfig = SPECIES_CONFIG[event.species] || SPECIES_CONFIG.autre;
              const eventConfig = EVENT_TYPE_CONFIG[event.event_type] || {};
              const SpeciesIcon = speciesConfig.Icon || CircleDot;
              
              return (
                <Marker
                  key={event.id}
                  position={[event.latitude, event.longitude]}
                  icon={createCustomIcon(speciesConfig.color, speciesConfig.iconType)}
                >
                  <Popup>
                    <div className="text-sm min-w-52">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <div className="flex items-center gap-2">
                          <SpeciesIcon className="h-6 w-6" style={{ color: speciesConfig.color }} />
                          <div>
                            <p className="font-bold text-gray-800">{t(speciesConfig.labelKey)}</p>
                            <p className="text-gray-500 text-xs">{t(eventConfig.labelKey)}</p>
                          </div>
                        </div>
                        <button
                          onClick={() => {
                            if (window.confirm(`${t('confirm_delete_observation')} ${t(speciesConfig.labelKey)} ?`)) {
                              deleteEvent(event.id);
                            }
                          }}
                          className="p-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors flex-shrink-0"
                          title={t('delete_observation')}
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                      <div className="bg-gray-100 p-2 rounded text-xs space-y-1">
                        {event.species_confidence && (
                          <p className="text-gray-600">
                            <span className="font-medium">Confiance:</span> {(event.species_confidence * 100).toFixed(0)}%
                          </p>
                        )}
                        {event.count_estimate > 1 && (
                          <p className="text-gray-600">
                            <span className="font-medium">Individus:</span> {event.count_estimate}
                          </p>
                        )}
                        <p className="text-gray-500 text-[10px]">
                          {new Date(event.captured_at).toLocaleString('fr-CA')}
                        </p>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              );
            })}

            {/* Hunting Territories Markers */}
            {showHuntingMarkers && nearbyTerritories.map((territory) => (
              <Marker
                key={`territory-${territory.name}`}
                position={[territory.lat, territory.lng]}
                icon={createCustomIcon(
                  territory.type === 'ZEC' ? '#22c55e' : 
                  territory.type === 'Réserve faunique' ? '#3b82f6' : 
                  '#f59e0b',
                  territory.type === 'ZEC' ? 'tent' : territory.type === 'Réserve faunique' ? 'shield' : 'home'
                )}
              >
                <Popup>
                  <div className="text-sm min-w-52">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center">
                        <CircleDot className="h-4 w-4 text-slate-600" />
                      </div>
                      <div>
                        <p className="font-bold text-gray-800">{territory.name}</p>
                        <p className="text-xs text-gray-500">{territory.type}</p>
                      </div>
                    </div>
                    <div className="bg-gray-100 p-2 rounded text-xs space-y-1">
                      <p><span className="font-medium">Région:</span> {territory.region}</p>
                      {territory.distance_km && (
                        <p><span className="font-medium">Distance:</span> {territory.distance_km} km</p>
                      )}
                      <p className="font-medium mt-1">Espèces:</p>
                      <div className="flex flex-wrap gap-1">
                        {territory.species?.map(sp => (
                          <span key={sp} className="px-1.5 py-0.5 bg-green-100 text-green-700 rounded text-[10px]">
                            {sp}
                          </span>
                        ))}
                      </div>
                    </div>
                    {territory.website && (
                      <a 
                        href={territory.website} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="block mt-2 text-center bg-blue-500 hover:bg-blue-600 text-white text-xs py-1.5 px-3 rounded transition-colors"
                      >
                        Visiter le site
                      </a>
                    )}
                  </div>
                </Popup>
              </Marker>
            ))}

            {/* Route Line */}
            {routePoints.length >= 2 && (
              <Polyline
                positions={routePoints.map(p => [p.lat, p.lng])}
                color="#f5a623"
                weight={3}
                dashArray="10, 5"
              />
            )}

            {/* Route Points Markers */}
            {routePoints.map((point, idx) => (
              <Marker
                key={`route-${idx}`}
                position={[point.lat, point.lng]}
                icon={createCustomIcon('#f5a623', `${idx + 1}`)}
              />
            ))}

            {/* Measure Line */}
            {measurePoints.length >= 2 && (
              <Polyline
                positions={measurePoints.map(p => [p.lat, p.lng])}
                color="#3b82f6"
                weight={2}
                dashArray="5, 5"
              />
            )}

            {/* Measure Points Markers */}
            {measurePoints.map((point, idx) => (
              <Marker
                key={`measure-${idx}`}
                position={[point.lat, point.lng]}
                icon={createCustomIcon('#3b82f6', 'pin')}
              />
            ))}

            {/* Pending Marker */}
            {pendingMarker && (
              <Marker
                position={[pendingMarker.lat, pendingMarker.lng]}
                icon={createCustomIcon('#22c55e', 'default')}
              />
            )}

            {/* Waypoints - Draggable */}
            {waypoints.map((wp) => (
              <Marker
                key={`waypoint-${wp.id}`}
                position={[wp.latitude, wp.longitude]}
                icon={createCustomIcon('#f59e0b', 'pin')}
                draggable={true}
                eventHandlers={{
                  dragstart: () => {
                    handleWaypointDragStart(wp);
                  },
                  drag: (e) => {
                    const newPos = e.target.getLatLng();
                    setLiveGpsCoords({
                      lat: newPos.lat,
                      lng: newPos.lng,
                      latDms: decimalToDms(newPos.lat, true),
                      lngDms: decimalToDms(newPos.lng, false)
                    });
                  },
                  dragend: (e) => {
                    const newPos = e.target.getLatLng();
                    handleWaypointDragEnd(wp, { lat: newPos.lat, lng: newPos.lng });
                  }
                }}
              >
                <Popup>
                  <div className="text-sm min-w-48">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div>
                        <p className="font-bold text-base text-gray-800">{wp.name}</p>
                        <p className="text-gray-500 text-xs">{wp.waypoint_type}</p>
                      </div>
                      <button
                        onClick={() => {
                          if (window.confirm(`SUPPRESSION DÉFINITIVE\n\nÊtes-vous sûr de vouloir supprimer le waypoint "${wp.name}" ?\n\nCette action est irréversible.`)) {
                            deleteWaypoint(wp.id);
                          }
                        }}
                        className="p-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors flex-shrink-0 shadow-md"
                        title="Supprimer définitivement ce waypoint"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                    <div className="text-[11px] text-gray-500 space-y-0.5 bg-gray-100 p-2 rounded">
                      <p><span className="font-medium">Lat:</span> {wp.latitude.toFixed(6)}</p>
                      <p><span className="font-medium">Lng:</span> {wp.longitude.toFixed(6)}</p>
                    </div>
                    {wp.description && (
                      <p className="text-gray-600 text-xs mt-2 italic">{wp.description}</p>
                    )}
                    <p className="text-blue-500 text-[10px] mt-2 italic text-center">
                      ↔️ Glissez le marqueur pour déplacer
                    </p>
                  </div>
                </Popup>
              </Marker>
            ))}

            {/* Guided Route Layer — Phase 2 extracted */}
            <GuidedRouteLayer route={guidedRoute} />

            {/* GPS Track Line */}
            {trackPoints.length >= 2 && (
              <Polyline
                positions={trackPoints.map(p => [p.lat, p.lng])}
                color="#10b981"
                weight={4}
              />
            )}

            {/* Current Position Marker */}
            {currentPosition && (
              <Circle
                center={[currentPosition.lat, currentPosition.lng]}
                radius={currentPosition.accuracy || 10}
                pathOptions={{ color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 0.2 }}
              >
                <Marker
                  position={[currentPosition.lat, currentPosition.lng]}
                  icon={createCustomIcon('#3b82f6', 'pin')}
                >
                  <Popup>
                    <div className="text-sm">
                      <p className="font-bold">Ma position</p>
                      <p className="text-gray-600">{currentPosition.lat.toFixed(5)}, {currentPosition.lng.toFixed(5)}</p>
                      {currentPosition.accuracy && (
                        <p className="text-gray-500 text-xs">Précision: ±{currentPosition.accuracy.toFixed(0)}m</p>
                      )}
                    </div>
                  </Popup>
                </Marker>
              </Circle>
            )}

            {/* BIONIC Precision Zones Layer — Phase 2 extracted */}
            <BionicPrecisionZonesLayer
              zones={bionicPrecisionZones}
              layersVisible={bionicLayersVisible}
              t={t}
            />

            {/* Wind Flow Layer — Ventusky-like Canvas 2D */}
            {showWindFlow && <WindFlowLayer bounds={null} />}
          </MapContainer>

          {/* Waypoint Modal */}
          {showWaypointModal && pendingWaypoint && (
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-[1001] bg-card border border-border rounded-xl p-4 shadow-xl min-w-[280px]">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-white font-semibold">Nouveau waypoint</h3>
                <button 
                  onClick={() => { setShowWaypointModal(false); setPendingWaypoint(null); }}
                  className="text-gray-400 hover:text-white"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <p className="text-gray-400 text-sm mb-3">
                Position: {pendingWaypoint.lat.toFixed(5)}, {pendingWaypoint.lng.toFixed(5)}
              </p>
              
              <div className="space-y-3">
                <div>
                  <Label className="text-gray-400 text-xs">Nom du waypoint</Label>
                  <Input
                    value={waypointName}
                    onChange={(e) => setWaypointName(e.target.value)}
                    placeholder="Ex: Cache à sel, Affût..."
                    className="bg-card border-border mt-1"
                  />
                </div>
                
                <div>
                  <Label className="text-gray-400 text-xs">{t('type')}</Label>
                  <Select value={waypointType} onValueChange={setWaypointType}>
                    <SelectTrigger className="bg-card border-border mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="observation">
                        <span className="flex items-center gap-2"><Eye className="h-4 w-4" /> {t('waypoint_observation')}</span>
                      </SelectItem>
                      <SelectItem value="camera">
                        <span className="flex items-center gap-2"><Camera className="h-4 w-4" /> {t('waypoint_camera')}</span>
                      </SelectItem>
                      <SelectItem value="cache">
                        <span className="flex items-center gap-2"><Droplet className="h-4 w-4" /> {t('waypoint_cache')}</span>
                      </SelectItem>
                      <SelectItem value="stand">
                        <span className="flex items-center gap-2"><Tent className="h-4 w-4" /> {t('waypoint_stand')}</span>
                      </SelectItem>
                      <SelectItem value="water">
                        <span className="flex items-center gap-2"><Waves className="h-4 w-4" /> {t('waypoint_water')}</span>
                      </SelectItem>
                      <SelectItem value="trail_start">
                        <span className="flex items-center gap-2"><Route className="h-4 w-4" /> {t('waypoint_trail_start')}</span>
                      </SelectItem>
                      <SelectItem value="custom">{t('common_other')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="flex gap-2 mt-4">
                <Button 
                  variant="outline" 
                  className="flex-1"
                  onClick={() => { setShowWaypointModal(false); setPendingWaypoint(null); }}
                >
                  Annuler
                </Button>
                <Button 
                  className="flex-1 btn-golden text-black"
                  onClick={addWaypoint}
                  disabled={!waypointName}
                >
                  <Flag className="h-4 w-4 mr-1" />
                  Ajouter
                </Button>
              </div>
            </div>
          )}

          {/* Species Selection Modal for Pin Tool */}
          {pendingMarker && (
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-[1001] bg-card border border-border rounded-xl p-4 shadow-xl min-w-[280px]">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-white font-semibold">Nouvelle observation</h3>
                <button 
                  onClick={() => { setPendingMarker(null); setActiveTool(null); }}
                  className="text-gray-400 hover:text-white"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <p className="text-gray-400 text-sm mb-3">
                Position: {pendingMarker.lat.toFixed(4)}, {pendingMarker.lng.toFixed(4)}
              </p>
              
              <div className="mb-4">
                <Label className="text-gray-400 text-xs mb-2 block">Espèce observée</Label>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(SPECIES_CONFIG).filter(([k]) => k !== 'autre').map(([key, config]) => (
                    <button
                      key={key}
                      onClick={() => setSelectedSpeciesForMarker(key)}
                      className={`p-2 rounded-lg border transition-all flex items-center gap-2 ${
                        selectedSpeciesForMarker === key 
                          ? 'border-[#f5a623] bg-[#f5a623]/10 text-white' 
                          : 'border-border text-gray-400 hover:border-gray-500'
                      }`}
                    >
                      <span className="text-lg">{config.emoji}</span>
                      <span className="text-sm">{config.label}</span>
                    </button>
                  ))}
                </div>
              </div>
              
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  className="flex-1"
                  onClick={() => { setPendingMarker(null); setActiveTool(null); }}
                >
                  Annuler
                </Button>
                <Button 
                  className="flex-1 btn-golden text-black"
                  onClick={confirmAddMarker}
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Ajouter
                </Button>
              </div>
            </div>
          )}

          {/* Clear Route/Measure Button */}
          {(routePoints.length > 0 || measurePoints.length > 0) && (
            <Button
              className="absolute top-24 left-4 z-[500] bg-red-500/90 hover:bg-red-600 text-white border-0"
              size="sm"
              onClick={clearToolPoints}
            >
              <X className="h-4 w-4 mr-1" />
              Effacer tracé
            </Button>
          )}

          {/* Guided Route Panel — Phase 2 extracted */}
          <GuidedRoutePanel
            route={guidedRoute}
            show={showGuidedRoutePanel}
            selectedAnalysisSpecies={selectedAnalysisSpecies}
            onClose={() => setShowGuidedRoutePanel(false)}
            onClear={clearGuidedRoute}
            onNavigateToPoint={navigateToRoutePoint}
          />


          {/* Territory Analysis Panel — Phase 2 extracted */}
          <TerritoryAnalysisPanel
            analysis={territoryAnalysis}
            onClose={clearTerritoryAnalysis}
            getScoreColor={getScoreColor}
            t={t}
          />

          {/* GPS Preview Panel - ENHANCED with continuous flow */}
          {(gpsFlowMode || activeTool === 'waypoint' || draggingWaypoint) && mouseGpsPreview && (
            <div className="absolute bottom-24 left-1/2 transform -translate-x-1/2 z-[700] bg-black/95 backdrop-blur-sm rounded-xl shadow-2xl border-2 border-green-500/50 px-5 py-4 min-w-[400px]">
              {/* Flow Mode Indicator */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className="relative">
                    <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
                    <div className="absolute inset-0 w-3 h-3 rounded-full bg-green-500 animate-ping"></div>
                  </div>
                  <span className="text-green-400 text-sm font-bold flex items-center gap-1">
                    <Satellite className="h-4 w-4" /> {t('gps_live_flow').toUpperCase()}
                  </span>
                </div>
                <Badge className="bg-green-500/20 text-green-400 text-[10px] animate-pulse">
                  STREAMING
                </Badge>
              </div>

              {/* Coordinates Grid */}
              <div className="grid grid-cols-2 gap-4 mb-3">
                <div className="bg-gray-900/50 rounded-lg p-2">
                  <div className="text-gray-500 text-[9px] uppercase tracking-wider mb-1">{t('format_decimal')}</div>
                  <div className="text-green-400 text-base font-mono font-bold">
                    {mouseGpsPreview.lat.toFixed(6)}
                  </div>
                  <div className="text-green-400 text-base font-mono font-bold">
                    {mouseGpsPreview.lng.toFixed(6)}
                  </div>
                </div>
                <div className="bg-gray-900/50 rounded-lg p-2">
                  <div className="text-gray-500 text-[9px] uppercase tracking-wider mb-1">{t('format_dms')}</div>
                  <div className="text-blue-400 text-sm font-mono">
                    {mouseGpsPreview.latDms}
                  </div>
                  <div className="text-blue-400 text-sm font-mono">
                    {mouseGpsPreview.lngDms}
                  </div>
                </div>
              </div>

              {/* Additional GPS Data */}
              <div className="grid grid-cols-3 gap-2 mb-3">
                <div className="bg-gray-800/50 rounded p-2 text-center">
                  <div className="text-gray-500 text-[8px] uppercase">{t('altitude')}</div>
                  <div className="text-yellow-400 text-sm font-bold">{mouseGpsPreview.altitude || '~'}m</div>
                </div>
                <div className="bg-gray-800/50 rounded p-2 text-center">
                  <div className="text-gray-500 text-[8px] uppercase">{t('precision')}</div>
                  <div className="text-cyan-400 text-sm font-bold">±{mouseGpsPreview.precision || '~'}m</div>
                </div>
                <div className="bg-gray-800/50 rounded p-2 text-center">
                  <div className="text-gray-500 text-[8px] uppercase">{t('zone')}</div>
                  <div className="text-purple-400 text-sm font-bold">UTM 19N</div>
                </div>
              </div>

              {/* Flow Status & Instructions */}
              <div className="pt-2 border-t border-green-500/30">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-green-400 animate-pulse" />
                    <span className="text-gray-400 text-xs">{t('data_injected_to_analysis')}</span>
                  </div>
                  <span className="text-green-400 text-[10px] font-mono">{new Date().toLocaleTimeString()}</span>
                </div>
                
                {/* Action Buttons */}
                <div className="flex gap-2 mt-3">
                  <Button
                    onClick={analyzeCurrentPosition}
                    className="flex-1 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white text-xs py-2"
                    data-testid="analyze-point-btn"
                  >
                    <Target className="h-3.5 w-3.5 mr-1.5" />
                    {t('analyze_point')}
                  </Button>
                  <Button
                    onClick={() => {
                      if (mouseGpsPreview) {
                        setPendingWaypoint({ lat: mouseGpsPreview.lat, lng: mouseGpsPreview.lng });
                        setShowWaypointModal(true);
                      }
                    }}
                    className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white text-xs py-2"
                    data-testid="create-waypoint-quick-btn"
                  >
                    <Flag className="h-3.5 w-3.5 mr-1.5" />
                    {t('create_waypoint')}
                  </Button>
                </div>
                
                <p className="text-center text-gray-400 text-[10px] mt-2 flex items-center justify-center gap-1">
                  {draggingWaypoint ? (
                    <><Target className="h-3 w-3" /> {t('release_to_confirm')}</>
                  ) : (
                    <><Lightbulb className="h-3 w-3" /> {t('quick_analyze_or_create')}</>
                  )}
                </p>
              </div>
            </div>
          )}

          {/* Map Tools Toolbar - Right Side */}
          <div className="absolute top-36 right-16 z-[600]">
            <div className="bg-white/95 backdrop-blur-sm rounded-xl shadow-lg border border-gray-200 flex flex-col items-center p-1 gap-1">
              {/* Pin Tool */}
              <button
                onClick={() => setActiveTool(activeTool === 'pin' ? null : 'pin')}
                className={`p-2.5 rounded-lg transition-all relative group ${
                  activeTool === 'pin' 
                    ? 'bg-[#f5a623] text-white' 
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
                data-testid="tool-pin"
                title="Ajouter un marqueur"
              >
                <MapPin className="h-5 w-5" />
                <span className="absolute right-12 top-1/2 -translate-y-1/2 bg-black/80 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap transition-opacity">
                  Marqueur
                </span>
              </button>

              {/* Divider */}
              <div className="h-px w-8 bg-gray-200" />

              {/* Waypoint Tool - NEW */}
              <button
                onClick={() => {
                  const newState = activeTool === 'waypoint' ? null : 'waypoint';
                  setActiveTool(newState);
                  setWaypointToolActive(!!newState);
                  setGpsFlowMode(!!newState); // Activer le mode flux GPS
                  if (newState) {
                    toast.info(t('gps_flow_mode_active'));
                  } else {
                    setMouseGpsPreview(null);
                    setLiveGpsCoords(null);
                  }
                }}
                className={`p-2.5 rounded-lg transition-all relative group ${
                  activeTool === 'waypoint' 
                    ? 'bg-green-500 text-white' 
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
                data-testid="tool-waypoint"
                title={t('add_waypoint')}
              >
                <Flag className="h-5 w-5" />
                <span className="absolute right-12 top-1/2 -translate-y-1/2 bg-black/80 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap transition-opacity">
                  {t('waypoint_gps')}
                </span>
              </button>

              {/* Divider */}
              <div className="h-px w-8 bg-gray-200" />

              {/* Route Tool */}
              <button
                onClick={() => setActiveTool(activeTool === 'route' ? null : 'route')}
                className={`p-2.5 rounded-lg transition-all relative group ${
                  activeTool === 'route' 
                    ? 'bg-[#f5a623] text-white' 
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
                data-testid="tool-route"
                title="Tracer un chemin"
              >
                <Route className="h-5 w-5" />
                <span className="absolute right-12 top-1/2 -translate-y-1/2 bg-black/80 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap transition-opacity">
                  Chemin
                </span>
              </button>

              {/* Divider */}
              <div className="h-px w-8 bg-gray-200" />

              {/* Layers Tool */}
              <button
                onClick={() => setShowLayersPanel(!showLayersPanel)}
                className={`p-2.5 rounded-lg transition-all relative group ${
                  showLayersPanel 
                    ? 'bg-[#f5a623] text-white' 
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
                data-testid="tool-layers"
                title="Couches"
              >
                <Layers className="h-5 w-5" />
                <span className="absolute right-12 top-1/2 -translate-y-1/2 bg-black/80 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap transition-opacity">
                  Couches
                </span>
              </button>

              {/* Divider */}
              <div className="h-px w-8 bg-gray-200" />

              {/* Measure Tool */}
              <button
                onClick={() => setActiveTool(activeTool === 'measure' ? null : 'measure')}
                className={`p-2.5 rounded-lg transition-all relative group ${
                  activeTool === 'measure' 
                    ? 'bg-[#f5a623] text-white' 
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
                data-testid="tool-measure"
                title="Mesurer la distance"
              >
                <Ruler className="h-5 w-5" />
                <span className="absolute right-12 top-1/2 -translate-y-1/2 bg-black/80 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap transition-opacity">
                  Mesure
                </span>
              </button>

              {/* Divider */}
              <div className="h-px w-8 bg-gray-200" />

              {/* Imagery/View Tool - Now opens layers panel */}
              <button
                onClick={() => setShowLayersPanel(!showLayersPanel)}
                className={`p-2.5 rounded-lg transition-all relative group ${
                  showLayersPanel 
                    ? 'bg-[#f5a623] text-white' 
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
                data-testid="tool-imagery"
                title="Type de carte"
              >
                <Mountain className="h-5 w-5" />
                <span className="absolute right-12 top-1/2 -translate-y-1/2 bg-black/80 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 whitespace-nowrap transition-opacity">
                  Vue carte
                </span>
              </button>
            </div>
          </div>

          {/* Layers Panel - Unified control for all map layers */}
          {showLayersPanel && (
            <div className="absolute top-36 right-32 z-[700] bg-black/95 backdrop-blur-sm rounded-xl shadow-2xl border border-[#f5a623]/30 w-[280px] max-h-[70vh] overflow-hidden flex flex-col">
              {/* Header */}
              <div className="p-3 bg-gradient-to-r from-[#f5a623]/20 to-orange-600/10 border-b border-[#f5a623]/20 flex-shrink-0">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Layers className="h-5 w-5 text-[#f5a623]" />
                    <h3 className="text-white font-bold text-sm">Couches de carte</h3>
                  </div>
                  <button 
                    onClick={() => setShowLayersPanel(false)}
                    className="p-1 text-gray-400 hover:text-white rounded"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Scrollable Content */}
              <div className="overflow-y-auto flex-1">
              {/* Base Layers */}
              <div className="p-3 border-b border-gray-700">
                <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">{t('base_map')}</div>
                <div className="space-y-1">
                  {[
                    { id: 'carte', nameKey: 'map_carte', Icon: Map, descKey: 'openstreetmap' },
                    { id: 'satellite', nameKey: 'map_satellite', Icon: Satellite, descKey: 'esri_imagery' },
                    { id: 'google-earth', nameKey: 'map_satellite_roads', Icon: Globe, descKey: 'esri_clarity' },
                    { id: 'topographie', nameKey: 'map_topo', Icon: Mountain, descKey: 'opentopomap' },
                  ].map((layer) => (
                    <button
                      key={layer.id}
                      onClick={() => {
                        setSelectedBaseLayer(layer.id);
                        toast.success(`${t('base_map_changed')}: ${t(layer.nameKey)}`);
                      }}
                      className={`w-full flex items-center gap-2 p-2 rounded-lg transition-all ${
                        selectedBaseLayer === layer.id 
                          ? 'bg-[#f5a623]/20 border border-[#f5a623]/50' 
                          : 'bg-gray-800/50 hover:bg-gray-700/50'
                      }`}
                    >
                      <layer.Icon className="h-5 w-5" style={{ color: selectedBaseLayer === layer.id ? BIONIC_COLORS.gold.primary : BIONIC_COLORS.gray[400] }} />
                      <div className="flex-1 text-left">
                        <div className={`text-sm ${selectedBaseLayer === layer.id ? 'text-[#f5a623]' : 'text-white'}`}>
                          {t(layer.nameKey)}
                        </div>
                        <div className="text-[10px] text-gray-500">{t(layer.descKey)}</div>
                      </div>
                      {selectedBaseLayer === layer.id && (
                        <Check className="h-4 w-4 text-[#f5a623]" />
                      )}
                    </button>
                  ))}
                </div>
              </div>

              {/* Overlay Layers */}
              <div className="p-3 border-b border-gray-700">
                <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">{t('overlays')}</div>
                <div className="space-y-1">
                  <label className="flex items-center gap-2 p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={showHeatmap} 
                      onChange={(e) => setShowHeatmap(e.target.checked)}
                      className="rounded border-gray-600 text-[#f5a623] focus:ring-[#f5a623]"
                    />
                    <Activity className="h-5 w-5 text-orange-500" />
                    <span className="text-white text-sm">{t('heatmap_activity')}</span>
                  </label>
                  <label className="flex items-center gap-2 p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={showCameras} 
                      onChange={(e) => setShowCameras(e.target.checked)}
                      className="rounded border-gray-600 text-[#f5a623] focus:ring-[#f5a623]"
                    />
                    <Camera className="h-5 w-5 text-blue-500" />
                    <span className="text-white text-sm">{t('cameras')}</span>
                  </label>
                  <label className="flex items-center gap-2 p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={showForestTrails} 
                      onChange={(e) => setShowForestTrails(e.target.checked)}
                      className="rounded border-gray-600 text-white focus:ring-white"
                    />
                    <Route className="h-5 w-5 text-amber-600" />
                    <span className="text-white text-sm">{t('forest_trails')}</span>
                  </label>
                  <label className="flex items-center gap-2 p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={showHuntingMarkers} 
                      onChange={(e) => setShowHuntingMarkers(e.target.checked)}
                      className="rounded border-gray-600 text-green-500 focus:ring-green-500"
                    />
                    <Tent className="h-5 w-5 text-green-500" />
                    <span className="text-white text-sm">{t('hunting_territories')}</span>
                  </label>
                  <label className="flex items-center gap-2 p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={probabilityZones.length > 0} 
                      onChange={(e) => {
                        if (!e.target.checked) {
                          setProbabilityZones([]);
                        } else {
                          generateProbabilityZones();
                        }
                      }}
                      className="rounded border-gray-600 text-[#f5a623] focus:ring-[#f5a623]"
                    />
                    <Target className="h-5 w-5 text-[#f5a623]" />
                    <span className="text-white text-sm">{t('probability_zones')}</span>
                  </label>
                  <label className="flex items-center gap-2 p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 cursor-pointer" data-testid="wind-flow-toggle">
                    <input 
                      type="checkbox" 
                      checked={showWindFlow} 
                      onChange={(e) => setShowWindFlow(e.target.checked)}
                      className="rounded border-gray-600 text-cyan-400 focus:ring-cyan-400"
                    />
                    <Wind className="h-5 w-5 text-cyan-400" />
                    <div className="flex items-center gap-1">
                      <span className="text-white text-sm">Vent</span>
                      <span className="text-[10px] text-cyan-400/70 bg-cyan-400/10 px-1 rounded">exp.</span>
                    </div>
                  </label>
                </div>
              </div>

              {/* WMS Layers */}
              <div className="p-3">
                <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">{t('quebec_layers_wms')}</div>
                <div className="space-y-1">
                  <label className="flex items-center gap-2 p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={showForestLayer} 
                      onChange={(e) => setShowForestLayer(e.target.checked)}
                      className="rounded border-gray-600 text-green-500 focus:ring-green-500"
                    />
                    <TreePine className="h-5 w-5 text-green-500" />
                    <span className="text-white text-sm">{t('forest_cover')}</span>
                  </label>
                  <label className="flex items-center gap-2 p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={showWaterLayer} 
                      onChange={(e) => setShowWaterLayer(e.target.checked)}
                      className="rounded border-gray-600 text-blue-500 focus:ring-blue-500"
                    />
                    <Waves className="h-5 w-5 text-blue-500" />
                    <span className="text-white text-sm">{t('hydrography')}</span>
                  </label>
                  <label className="flex items-center gap-2 p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={showReliefLayer} 
                      onChange={(e) => setShowReliefLayer(e.target.checked)}
                      className="rounded border-gray-600 text-orange-500 focus:ring-orange-500"
                    />
                    <Mountain className="h-5 w-5 text-orange-500" />
                    <span className="text-white text-sm">{t('relief_lidar')}</span>
                  </label>
                  <label className="flex items-center gap-2 p-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 cursor-pointer">
                    <input 
                      type="checkbox" 
                      checked={showRoadsLayer} 
                      onChange={(e) => setShowRoadsLayer(e.target.checked)}
                      className="rounded border-gray-600 text-yellow-500 focus:ring-yellow-500"
                    />
                    <Route className="h-5 w-5 text-yellow-500" />
                    <span className="text-white text-sm">{t('forest_roads')}</span>
                  </label>
                </div>
              </div>

              {/* BIONIC™ Layers - Haute Précision */}
              {bionicPrecisionZones && bionicPrecisionZones.length > 0 && (
                <div 
                  ref={bionicZonesSectionRef}
                  className="p-3 border-t border-[#f5a623]/30"
                  data-testid="bionic-zones-section"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Brain className="h-4 w-4 text-[#f5a623]" />
                      <span className="text-[10px] text-[#f5a623] uppercase tracking-wider font-bold">BIONIC™ Zones</span>
                      <span className="text-[9px] bg-green-500/20 text-green-400 px-1 rounded">{t('precision')}</span>
                    </div>
                    <div className="flex gap-1">
                      <button
                        onClick={() => toggleAllBionicLayers(true)}
                        className="text-[9px] px-1.5 py-0.5 rounded bg-green-500/20 text-green-400 hover:bg-green-500/30"
                      >
                        {t('all')}
                      </button>
                      <button
                        onClick={() => toggleAllBionicLayers(false)}
                        className="text-[9px] px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30"
                      >
                        {t('none')}
                      </button>
                      <button
                        onClick={clearBionicAnalysis}
                        className="text-[9px] px-1.5 py-0.5 rounded bg-gray-500/20 text-gray-400 hover:bg-gray-500/30"
                      >
                        {t('clear')}
                      </button>
                    </div>
                  </div>
                  
                  {/* Zone count */}
                  <div className="text-[10px] text-gray-500 mb-2">
                    {bionicPrecisionZones.length} {t('micro_zones_calculated')}
                  </div>
                  
                  <div className="space-y-1 max-h-[200px] overflow-y-auto">
                    {Object.entries(bionicModuleStats).map(([key, stats]) => {
                      if (!stats) return null;
                      const ModuleIcon = BIONIC_MODULE_CONFIG[key]?.Icon || CircleDot;
                      
                      return (
                        <label 
                          key={key} 
                          className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-all ${
                            bionicLayersVisible[key] 
                              ? 'bg-gray-800/70 border border-gray-600/50' 
                              : 'bg-gray-800/30 opacity-60'
                          }`}
                        >
                          <input 
                            type="checkbox" 
                            checked={bionicLayersVisible[key]} 
                            onChange={() => toggleBionicLayer(key)}
                            className="rounded border-gray-600 focus:ring-[#f5a623]"
                            style={{ accentColor: stats.color }}
                          />
                          <ModuleIcon className="h-5 w-5" style={{ color: stats.color }} />
                          <div className="flex-1">
                            <span className="text-white text-sm">{t(BIONIC_MODULE_CONFIG[key]?.labelKey) || stats.label}</span>
                            <div className="flex items-center gap-2">
                              <span 
                                className="text-xs font-bold"
                                style={{ color: stats.color }}
                              >
                                {stats.maxProbability}%
                              </span>
                              <span className="text-[10px] text-gray-500">
                                max • {stats.avgProbability}% moy
                              </span>
                            </div>
                            <div className="flex items-center gap-1 mt-1">
                              <div className="flex-1 bg-gray-700 rounded-full h-1.5">
                                <div 
                                  className="h-1.5 rounded-full transition-all"
                                  style={{ 
                                    width: `${stats.maxProbability}%`,
                                    backgroundColor: stats.color 
                                  }}
                                />
                              </div>
                              <span className="text-[9px] text-gray-500">
                                {stats.totalZones} zones
                              </span>
                            </div>
                          </div>
                          <div 
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: stats.color }}
                          />
                        </label>
                      );
                    })}
                  </div>
                  
                  <div className="mt-2 pt-2 border-t border-gray-700/50">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-400">Score Global:</span>
                      <span className="text-[#f5a623] font-bold">
                        {bionicAnalysisResult?.overall_score || 0}/100
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-[10px] mt-1">
                      <span className="text-gray-500">Modules actifs:</span>
                      <span className="text-gray-400">
                        {Object.keys(bionicModuleStats).length}/8
                      </span>
                    </div>
                  </div>
                </div>
              )}
              </div>{/* End Scrollable Content */}
            </div>
          )}

          {/* BIONIC TACTICAL Advanced Layer Panel */}
          {showBionicLayerPanel && (
            <div className="absolute top-20 right-4 z-[800]">
              <BionicLayerPanel
                visibility={advancedZoneVisibility}
                onVisibilityChange={setAdvancedZoneVisibility}
                opacity={advancedZoneOpacity}
                onOpacityChange={setAdvancedZoneOpacity}
                onClose={() => setShowBionicLayerPanel(false)}
                onMinimize={() => setBionicLayerPanelMinimized(!bionicLayerPanelMinimized)}
                minimized={bionicLayerPanelMinimized}
                language="fr"
              />
            </div>
          )}
          
          {/* Toggle BIONIC Layer Panel Button - Positioned in right side */}
          {!showBionicLayerPanel && (
            <button
              onClick={() => setShowBionicLayerPanel(true)}
              className="absolute top-20 right-4 z-[700] bg-black/90 backdrop-blur-xl border border-[#F5A623]/30 rounded-lg p-3 shadow-xl hover:border-[#F5A623] hover:shadow-[0_0_15px_rgba(245,166,35,0.3)] transition-all group"
              data-testid="bionic-layer-panel-toggle"
              title="Panneau Zones Avancées BIONIC"
            >
              <div className="flex items-center gap-2">
                <Target className="h-5 w-5 text-[#F5A623]" />
                <span className="text-white text-xs font-bold uppercase tracking-wider">
                  Zones
                </span>
              </div>
            </button>
          )}

          {/* Active tool indicator */}
          {activeTool && (
            <div className={`absolute top-4 left-1/2 transform -translate-x-1/2 z-[600] text-sm px-4 py-2 rounded-lg font-medium shadow-lg ${
              activeTool === 'waypoint' ? 'bg-green-500 text-white' : 'bg-[#f5a623] text-black'
            }`} style={{marginLeft: '140px'}}>
              {activeTool === 'pin' && t('click_add_observation')}
              {activeTool === 'waypoint' && <span className="flex items-center gap-1"><Flag className="h-4 w-4" /> {t('click_place_waypoint')}</span>}
              {activeTool === 'route' && <span className="flex items-center gap-1"><Route className="h-4 w-4" /> {t('click_trace_path')}</span>}
              {activeTool === 'measure' && <span className="flex items-center gap-1"><Ruler className="h-4 w-4" /> {t('click_measure_distance')}</span>}
            </div>
          )}

          {/* Map Legend - Always visible, positioned bottom-left */}
          <div className="absolute bottom-8 left-4 bg-black/90 backdrop-blur-md p-3 rounded-xl border-2 border-[#f5a623]/50 z-[800] shadow-xl">
            <p className="text-[#f5a623] text-xs font-bold mb-2 flex items-center gap-2">
              <MapPin className="h-4 w-4" /> {t('legend')}
            </p>
            <div className="space-y-1.5">
              {Object.entries(SPECIES_CONFIG).filter(([k]) => k !== 'autre').map(([key, config]) => (
                <div key={key} className="flex items-center gap-2 text-xs">
                  <CircleDot className="h-4 w-4" style={{ color: config.color }} />
                  <span className="text-white">{t(config.labelKey)}</span>
                </div>
              ))}
              <div className="flex items-center gap-2 text-xs">
                <Camera className="h-4 w-4 text-blue-500" />
                <span className="text-white">{t('cameras')}</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <Flag className="h-4 w-4 text-green-500" />
                <span className="text-white">{t('waypoint')}</span>
              </div>
              <div className="border-t border-gray-700 pt-1.5 mt-1.5">
                <p className="text-gray-400 text-[9px] mb-1">{t('probability')}:</p>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-0.5">
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                    <span className="text-[9px] text-gray-300">H</span>
                  </div>
                  <div className="flex items-center gap-0.5">
                    <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
                    <span className="text-[9px] text-gray-300">M</span>
                  </div>
                  <div className="flex items-center gap-0.5">
                    <div className="w-2 h-2 rounded-full bg-red-500"></div>
                    <span className="text-[9px] text-gray-300">F</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Custom Zoom Controls - Always visible, positioned bottom-left next to legend */}
          <div className="absolute bottom-24 left-[180px] z-[800] flex flex-col gap-1">
            <button 
              onClick={() => setMapZoom(prev => Math.min(prev + 1, 18))}
              className="w-9 h-9 bg-black/90 hover:bg-black text-white rounded-lg border-2 border-[#f5a623]/50 flex items-center justify-center text-lg font-bold shadow-xl transition-all hover:scale-105"
              title="Zoom +"
            >
              +
            </button>
            <button 
              onClick={() => setMapZoom(prev => Math.max(prev - 1, 3))}
              className="w-9 h-9 bg-black/90 hover:bg-black text-white rounded-lg border-2 border-[#f5a623]/50 flex items-center justify-center text-lg font-bold shadow-xl transition-all hover:scale-105"
              title="Zoom -"
            >
              −
            </button>
          </div>

          {/* Refresh Button */}
          <Button
            className="absolute top-4 left-4 z-[500] bg-card/95 backdrop-blur-sm border border-border"
            variant="outline"
            size="sm"
            onClick={loadData}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Actualiser
          </Button>
          
          {/* My Location Button */}
          <Button
            className="absolute top-14 left-4 z-[500] bg-card/95 backdrop-blur-sm border border-border"
            variant="outline"
            size="sm"
            onClick={() => {
              if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                  (position) => {
                    setMapCenter([position.coords.latitude, position.coords.longitude]);
                    setMapZoom(15);
                    toast.success('Centré sur votre position');
                  },
                  (error) => {
                    toast.error('Impossible d\'obtenir votre position');
                  }
                );
              } else {
                toast.error('Géolocalisation non supportée');
              }
            }}
          >
            <Locate className="h-4 w-4 mr-2" />
            Ma position
          </Button>
        </div>
      </div>

      {/* Nutrition Analysis Modal */}
      {/* Nutrition Analysis Modal — Phase 3 extracted */}
      <NutritionAnalysisModal
        analysis={nutritionAnalysis}
        show={showNutritionModal}
        onClose={() => setShowNutritionModal(false)}
        onAddToCart={addToCart}
      />

      {/* Shopping Cart Modal — Phase 3 extracted */}
      <CartModal
        show={showCartModal}
        cart={cart}
        onClose={() => setShowCartModal(false)}
        removeFromCart={removeFromCart}
        updateCartQuantity={updateCartQuantity}
        getCartTotal={getCartTotal}
        onShowOrderForm={() => setShowOrderForm(true)}
      />

      {/* Order Form Modal — Phase 3 extracted */}
      <OrderFormModal
        show={showOrderForm}
        cart={cart}
        onClose={() => setShowOrderForm(false)}
        getCartTotal={getCartTotal}
        orderName={orderName}
        setOrderName={setOrderName}
        orderEmail={orderEmail}
        setOrderEmail={setOrderEmail}
        orderPhone={orderPhone}
        setOrderPhone={setOrderPhone}
        orderNotes={orderNotes}
        setOrderNotes={setOrderNotes}
        onSubmit={submitOrder}
        submitting={submittingOrder}
      />

      {/* BIONIC™ Territory Engine Modal */}
      {showBionicAnalyzer && (
        <div className="fixed inset-0 bg-black/80 z-[2002] flex items-center justify-center p-4" onClick={() => setShowBionicAnalyzer(false)}>
          <div 
            className="bg-card border border-border rounded-2xl shadow-2xl w-full max-w-6xl h-[90vh] flex flex-col overflow-hidden"
            onClick={e => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 border-b border-border bg-gradient-to-r from-[#f5a623]/10 to-orange-500/10">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-[#f5a623]/20 flex items-center justify-center">
                  <Brain className="h-5 w-5 text-[#f5a623]" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    BIONIC™ Territory Engine
                    <Badge className="bg-green-500/20 text-green-400 text-[10px]">v1.0</Badge>
                  </h2>
                  <p className="text-gray-400 text-xs">Analyse géospatiale avancée • 8 modules • 6 modèles fauniques • IA prédictive</p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowBionicAnalyzer(false)}
                className="text-gray-400 hover:text-white hover:bg-white/10"
                data-testid="close-bionic-modal"
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
            
            {/* BIONIC Analyzer Content */}
            <div className="flex-1 overflow-hidden">
              <BionicAnalyzer 
                territory={{
                  id: selectedTerritoryType && selectedZoneNumber 
                    ? `${selectedTerritoryType}-${selectedZoneNumber}` 
                    : 'current-location',
                  name: selectedTerritoryType && selectedZoneNumber 
                    ? `${selectedTerritoryType.toUpperCase()} ${selectedZoneNumber}`
                    : 'Position actuelle',
                  coordinates: {
                    lat: parseFloat(gpsLatitude) || mapCenter[0],
                    lng: parseFloat(gpsLongitude) || mapCenter[1]
                  }
                }}
                onClose={() => setShowBionicAnalyzer(false)}
                onAnalysisComplete={handleBionicAnalysisComplete}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TerritoryMap;
