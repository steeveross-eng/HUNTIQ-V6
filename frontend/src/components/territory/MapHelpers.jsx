/**
 * TerritoryMap Helper Components - BIONIC V5
 * 
 * Extracted from TerritoryMap.jsx for better maintainability
 * @module territory/MapHelpers
 * @version 1.0.0
 */

import React, { useEffect, memo } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import { SVG_MARKER_ICONS, HEATMAP_GRADIENT, HEATMAP_DEFAULTS } from './constants';

/**
 * Create custom Leaflet marker icon
 * @param {string} color - Marker background color
 * @param {string} iconType - Type of icon (target, eye, camera, etc.)
 * @returns {L.DivIcon} Leaflet div icon
 */
export const createCustomIcon = (color, iconType = 'default') => {
  const svg = SVG_MARKER_ICONS[iconType] || SVG_MARKER_ICONS.default;
  
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="
      background: ${color};
      width: 36px;
      height: 36px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 3px solid white;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    ">${svg}</div>`,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -18]
  });
};

/**
 * HeatmapLayer - Displays heat visualization on map
 * Memoized for performance
 */
export const HeatmapLayer = memo(({ points, radius = HEATMAP_DEFAULTS.radius }) => {
  const map = useMap();
  
  useEffect(() => {
    if (!points || points.length === 0) return;
    
    let heatLayer = null;
    
    // Dynamic import for leaflet.heat
    import('leaflet.heat').then(() => {
      const heatData = points.map(p => [p.lat, p.lon, p.intensity * 0.5]);
      
      heatLayer = L.heatLayer(heatData, {
        radius: radius,
        blur: HEATMAP_DEFAULTS.blur,
        maxZoom: HEATMAP_DEFAULTS.maxZoom,
        gradient: HEATMAP_GRADIENT
      });
      
      heatLayer.addTo(map);
    });
    
    return () => {
      if (heatLayer) {
        map.removeLayer(heatLayer);
      }
    };
  }, [map, points, radius]);
  
  return null;
});

HeatmapLayer.displayName = 'HeatmapLayer';

/**
 * MapCenterController - Controls map center and zoom
 * Memoized for performance
 */
export const MapCenterController = memo(({ center, zoom }) => {
  const map = useMap();
  
  useEffect(() => {
    if (center) {
      map.setView(center, zoom || map.getZoom());
    }
  }, [map, center, zoom]);
  
  return null;
});

MapCenterController.displayName = 'MapCenterController';

/**
 * MapClickHandler - Handles map click events for tools
 * Memoized for performance
 */
export const MapClickHandler = memo(({ activeTool, onMapClick, onMouseMove }) => {
  const map = useMap();
  
  useEffect(() => {
    // Handle mouse move for GPS preview
    const handleMouseMove = (e) => {
      if (onMouseMove) {
        onMouseMove(e.latlng);
      }
    };
    
    map.on('mousemove', handleMouseMove);
    
    return () => {
      map.off('mousemove', handleMouseMove);
    };
  }, [map, onMouseMove]);
  
  useEffect(() => {
    if (!activeTool) return;
    
    const handleClick = (e) => {
      onMapClick(e.latlng, activeTool);
    };
    
    map.on('click', handleClick);
    
    // Change cursor based on tool
    const container = map.getContainer();
    if (activeTool === 'pin' || activeTool === 'route' || activeTool === 'measure') {
      container.style.cursor = 'crosshair';
    }
    
    return () => {
      map.off('click', handleClick);
      container.style.cursor = '';
    };
  }, [map, activeTool, onMapClick]);
  
  return null;
});

MapClickHandler.displayName = 'MapClickHandler';

/**
 * ZoomSyncComponent - Syncs mapZoom state with Leaflet map
 * Memoized for performance
 */
export const ZoomSyncComponent = memo(({ zoom }) => {
  const map = useMap();
  
  useEffect(() => {
    if (map && zoom !== map.getZoom()) {
      map.setZoom(zoom);
    }
  }, [map, zoom]);
  
  return null;
});

ZoomSyncComponent.displayName = 'ZoomSyncComponent';

/**
 * Convert DMS (Degrees Minutes Seconds) to Decimal
 * @param {number} deg - Degrees
 * @param {number} min - Minutes
 * @param {number} sec - Seconds
 * @param {string} dir - Direction (N, S, E, W)
 * @returns {number} Decimal degrees
 */
export const dmsToDecimal = (deg, min, sec, dir) => {
  const d = parseFloat(deg) || 0;
  const m = parseFloat(min) || 0;
  const s = parseFloat(sec) || 0;
  let decimal = d + (m / 60) + (s / 3600);
  if (dir === 'S' || dir === 'W') {
    decimal = -decimal;
  }
  return decimal;
};

/**
 * Convert Decimal to DMS string
 * @param {number} decimal - Decimal degrees
 * @param {boolean} isLat - Is latitude (true) or longitude (false)
 * @returns {string} DMS formatted string
 */
export const decimalToDms = (decimal, isLat) => {
  const dir = isLat ? (decimal >= 0 ? 'N' : 'S') : (decimal >= 0 ? 'E' : 'W');
  const abs = Math.abs(decimal);
  const deg = Math.floor(abs);
  const minFloat = (abs - deg) * 60;
  const min = Math.floor(minFloat);
  const sec = ((minFloat - min) * 60).toFixed(2);
  return `${deg}° ${min}' ${sec}" ${dir}`;
};
