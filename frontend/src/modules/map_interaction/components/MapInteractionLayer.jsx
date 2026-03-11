/**
 * MapInteractionLayer - Universal Map Interaction Module
 * ======================================================
 * 
 * Module d'interaction cartographique universel.
 * - Affichage coordonnées GPS LIVE (mousemove)
 * - Création waypoint sur double-clic
 * 
 * Compatible avec toutes les couches (Raster, Vector, WMS, WMTS, TMS, Heatmap, etc.)
 * Architecture LEGO V5 - Module métier isolé.
 * 
 * @module modules/map_interaction
 */
import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useMap, useMapEvents, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { MapPin, Navigation, Plus, Check, X } from 'lucide-react';
import { WaypointService } from '../services/WaypointService';

// Custom marker icon for new waypoints
const waypointIcon = L.divIcon({
  className: 'custom-waypoint-marker',
  html: `<div style="
    background: linear-gradient(135deg, #f5a623, #d4891c);
    width: 32px;
    height: 32px;
    border-radius: 50% 50% 50% 0;
    transform: rotate(-45deg);
    border: 3px solid white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    display: flex;
    align-items: center;
    justify-content: center;
  ">
    <svg style="transform: rotate(45deg); width: 16px; height: 16px; color: white;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
      <circle cx="12" cy="10" r="3"></circle>
    </svg>
  </div>`,
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32]
});

/**
 * GPS Coordinates Display Component
 */
const CoordinatesOverlay = ({ lat, lng, visible }) => {
  if (!visible || lat === null || lng === null) return null;

  return (
    <div 
      className="absolute bottom-4 left-4 z-[1000] bg-black/80 backdrop-blur-sm text-white px-4 py-2 rounded-lg shadow-lg border border-white/10"
      data-testid="coordinates-overlay"
    >
      <div className="flex items-center gap-3">
        <Navigation className="h-4 w-4 text-[#f5a623]" />
        <div className="font-mono text-sm">
          <span className="text-gray-400">LAT:</span>{' '}
          <span className="text-white font-semibold">{lat.toFixed(6)}</span>
          <span className="mx-2 text-gray-500">|</span>
          <span className="text-gray-400">LNG:</span>{' '}
          <span className="text-white font-semibold">{lng.toFixed(6)}</span>
        </div>
      </div>
    </div>
  );
};

/**
 * Double-click hint tooltip
 */
const InteractionHint = ({ visible }) => {
  if (!visible) return null;

  return (
    <div 
      className="absolute top-4 left-1/2 -translate-x-1/2 z-[1000] bg-[#f5a623]/90 text-black px-4 py-2 rounded-full shadow-lg text-sm font-medium flex items-center gap-2"
      data-testid="interaction-hint"
    >
      <Plus className="h-4 w-4" />
      Double-cliquez pour créer un waypoint
    </div>
  );
};

/**
 * Waypoint Creation Popup
 */
const WaypointPopup = ({ position, onConfirm, onCancel, saving }) => {
  const [name, setName] = useState('');

  const handleConfirm = () => {
    onConfirm(name || `Waypoint ${new Date().toLocaleDateString('fr-CA')}`);
  };

  return (
    <Popup 
      position={position} 
      closeButton={false}
      className="waypoint-creation-popup"
    >
      <div className="p-2 min-w-[200px]">
        <div className="flex items-center gap-2 mb-3 text-[#f5a623]">
          <MapPin className="h-5 w-5" />
          <span className="font-semibold">Nouveau Waypoint</span>
        </div>
        
        <input
          type="text"
          placeholder="Nom du waypoint (optionnel)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm mb-3 focus:outline-none focus:border-[#f5a623]"
          autoFocus
          disabled={saving}
        />
        
        <div className="text-xs text-gray-400 mb-3">
          <div>Lat: {position[0].toFixed(6)}</div>
          <div>Lng: {position[1].toFixed(6)}</div>
        </div>

        <div className="flex gap-2">
          <button
            onClick={handleConfirm}
            disabled={saving}
            className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-[#f5a623] hover:bg-[#d4891c] text-black rounded-lg text-sm font-medium disabled:opacity-50"
          >
            {saving ? (
              <span className="animate-spin">⏳</span>
            ) : (
              <Check className="h-4 w-4" />
            )}
            {saving ? 'Création...' : 'Créer'}
          </button>
          <button
            onClick={onCancel}
            disabled={saving}
            className="flex items-center justify-center px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
    </Popup>
  );
};

/**
 * Pending Waypoint Marker with auto-open popup
 */
const PendingWaypointMarker = ({ position, icon, onConfirm, onCancel, saving }) => {
  const markerRef = useRef(null);

  // Auto-open popup when marker is rendered (with delay for DOM readiness)
  useEffect(() => {
    const timer = setTimeout(() => {
      if (markerRef.current) {
        markerRef.current.openPopup();
      }
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  return (
    <Marker
      ref={markerRef}
      position={position}
      icon={icon}
    >
      <WaypointPopup
        position={position}
        onConfirm={onConfirm}
        onCancel={onCancel}
        saving={saving}
      />
    </Marker>
  );
};

/**
 * Map Event Handler Component
 */
const MapEventHandler = ({ 
  onMouseMove, 
  onDoubleClick, 
  onMouseEnter, 
  onMouseLeave 
}) => {
  useMapEvents({
    mousemove: (e) => {
      onMouseMove(e.latlng.lat, e.latlng.lng);
    },
    dblclick: (e) => {
      L.DomEvent.stopPropagation(e);
      onDoubleClick(e.latlng.lat, e.latlng.lng);
    },
    mouseout: () => {
      onMouseLeave();
    },
    mouseover: () => {
      onMouseEnter();
    }
  });

  return null;
};

/**
 * MapInteractionLayer - Main Component
 * 
 * @param {Object} props
 * @param {boolean} props.showCoordinates - Show GPS coordinates overlay (default: true)
 * @param {boolean} props.enableWaypointCreation - Enable waypoint creation on double-click (default: true)
 * @param {boolean} props.showHint - Show interaction hint (default: true, auto-hides after 5s)
 * @param {function} props.onWaypointCreated - Callback when waypoint is created
 * @param {string} props.userId - User ID for waypoint ownership
 */
export const MapInteractionLayer = ({
  showCoordinates = true,
  enableWaypointCreation = true,
  showHint = true,
  onWaypointCreated,
  userId
}) => {
  // State
  const [mousePosition, setMousePosition] = useState({ lat: null, lng: null });
  const [isMouseOnMap, setIsMouseOnMap] = useState(false);
  const [pendingWaypoint, setPendingWaypoint] = useState(null);
  const [createdWaypoints, setCreatedWaypoints] = useState([]);
  const [saving, setSaving] = useState(false);
  const [hintVisible, setHintVisible] = useState(showHint);

  // Auto-hide hint after 5 seconds
  useEffect(() => {
    if (showHint) {
      const timer = setTimeout(() => setHintVisible(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [showHint]);

  // Handlers
  const handleMouseMove = useCallback((lat, lng) => {
    setMousePosition({ lat, lng });
  }, []);

  const handleMouseEnter = useCallback(() => {
    setIsMouseOnMap(true);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsMouseOnMap(false);
    setMousePosition({ lat: null, lng: null });
  }, []);

  const handleDoubleClick = useCallback((lat, lng) => {
    if (!enableWaypointCreation) return;
    setPendingWaypoint({ lat, lng });
  }, [enableWaypointCreation]);

  const handleConfirmWaypoint = useCallback(async (name) => {
    if (!pendingWaypoint) return;

    setSaving(true);
    try {
      const waypointData = {
        lat: pendingWaypoint.lat,
        lng: pendingWaypoint.lng,
        name,
        timestamp: new Date().toISOString(),
        source: 'user_double_click',
        user_id: userId
      };

      const result = await WaypointService.createWaypoint(waypointData);

      if (result.success) {
        // Add to local state for immediate display
        setCreatedWaypoints(prev => [...prev, {
          ...waypointData,
          id: result.waypoint?.id || Date.now().toString()
        }]);

        // Callback
        if (onWaypointCreated) {
          onWaypointCreated(result.waypoint || waypointData);
        }
      }
    } catch (error) {
      console.error('Error creating waypoint:', error);
    } finally {
      setSaving(false);
      setPendingWaypoint(null);
    }
  }, [pendingWaypoint, userId, onWaypointCreated]);

  const handleCancelWaypoint = useCallback(() => {
    setPendingWaypoint(null);
  }, []);

  return (
    <>
      {/* Event Handler */}
      <MapEventHandler
        onMouseMove={handleMouseMove}
        onDoubleClick={handleDoubleClick}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      />

      {/* Coordinates Overlay */}
      {showCoordinates && (
        <CoordinatesOverlay
          lat={mousePosition.lat}
          lng={mousePosition.lng}
          visible={isMouseOnMap}
        />
      )}

      {/* Interaction Hint */}
      {enableWaypointCreation && (
        <InteractionHint visible={hintVisible && isMouseOnMap} />
      )}

      {/* Pending Waypoint Marker + Popup (auto-open) */}
      {pendingWaypoint && (
        <PendingWaypointMarker
          position={[pendingWaypoint.lat, pendingWaypoint.lng]}
          icon={waypointIcon}
          onConfirm={handleConfirmWaypoint}
          onCancel={handleCancelWaypoint}
          saving={saving}
        />
      )}

      {/* Created Waypoints */}
      {createdWaypoints.map((wp) => (
        <Marker
          key={wp.id}
          position={[wp.lat, wp.lng]}
          icon={waypointIcon}
        >
          <Popup>
            <div className="p-2">
              <div className="font-semibold text-[#f5a623]">{wp.name}</div>
              <div className="text-xs text-gray-500 mt-1">
                {new Date(wp.timestamp).toLocaleString('fr-CA')}
              </div>
              <div className="text-xs text-gray-400 mt-1">
                {wp.lat.toFixed(6)}, {wp.lng.toFixed(6)}
              </div>
            </div>
          </Popup>
        </Marker>
      ))}
    </>
  );
};

export default MapInteractionLayer;
