/**
 * MapHelpers.jsx — Composants utilitaires Leaflet pour Mon Territoire BIONIC
 * 
 * Extraits de MonTerritoireBionicPage.jsx (IM1 Refactorisation)
 * - createCustomIcon: Icônes SVG pour les markers
 * - MapRefCapture: Capture de l'instance Leaflet map
 * - ZoomHandler: Détection zoom/position
 * - MapResizer: Recalcul taille conteneur
 * - MapClickHandler: Clics carte → waypoints
 */
import { useEffect, useLayoutEffect } from 'react';
import { useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';

// Fix for default markers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Custom icons - BIONIC Design System compliant (SVG icons)
export const createCustomIcon = (color, iconType = 'default') => {
  const svgIcon = iconType === 'user' 
    ? '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>'
    : iconType === 'waypoint'
    ? '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>'
    : '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>';
  
  const iconHtml = `
    <div style="
      background-color: ${color};
      width: 32px;
      height: 32px;
      border-radius: 50% 50% 50% 0;
      transform: rotate(-45deg);
      border: 3px solid white;
      box-shadow: 0 2px 5px rgba(0,0,0,0.3);
      display: flex;
      align-items: center;
      justify-content: center;
    ">
      <div style="transform: rotate(45deg); color: white; font-size: 14px; display: flex; align-items: center; justify-content: center;">
        ${svgIcon}
      </div>
    </div>
  `;
  return L.divIcon({
    html: iconHtml,
    className: 'custom-marker',
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32]
  });
};

// Capture de l'instance Leaflet map via ref
export const MapRefCapture = ({ mapRefProp }) => {
  const map = useMap();
  useLayoutEffect(() => { mapRefProp.current = map; }, [map, mapRefProp]);
  return null;
};

// Détection des changements de zoom et position
export const ZoomHandler = ({ onZoomChange, onMapMove, onBoundsChange }) => {
  const map = useMap();
  
  useEffect(() => {
    const timer = setTimeout(() => { map.invalidateSize(); }, 100);
    const timer2 = setTimeout(() => { map.invalidateSize(); }, 500);
    
    const handleZoomEnd = () => {
      const center = map.getCenter();
      const bounds = map.getBounds();
      onZoomChange(map.getZoom());
      if (onMapMove) onMapMove({ lat: center.lat, lng: center.lng });
      if (onBoundsChange) {
        onBoundsChange({
          north: bounds.getNorth(),
          south: bounds.getSouth(),
          east: bounds.getEast(),
          west: bounds.getWest()
        });
      }
    };
    
    const handleMoveEnd = () => {
      const center = map.getCenter();
      const bounds = map.getBounds();
      if (onMapMove) onMapMove({ lat: center.lat, lng: center.lng });
      if (onBoundsChange) {
        onBoundsChange({
          north: bounds.getNorth(),
          south: bounds.getSouth(),
          east: bounds.getEast(),
          west: bounds.getWest()
        });
      }
    };
    
    map.on('zoomend', handleZoomEnd);
    map.on('moveend', handleMoveEnd);
    handleZoomEnd();
    
    return () => {
      clearTimeout(timer);
      clearTimeout(timer2);
      map.off('zoomend', handleZoomEnd);
      map.off('moveend', handleMoveEnd);
    };
  }, [map, onZoomChange, onMapMove, onBoundsChange]);
  
  return null;
};

// Force Leaflet à recalculer sa taille quand le conteneur change
// BIONIC V7.3 FIX: Debounce via requestAnimationFrame
export const MapResizer = () => {
  const map = useMap();
  
  useEffect(() => {
    const container = map.getContainer();
    let rafId = null;
    
    const observer = new ResizeObserver(() => {
      if (rafId) cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(() => {
        if (map && map.getContainer()) {
          map.invalidateSize({ animate: false, pan: false });
        }
        rafId = null;
      });
    });
    observer.observe(container);
    
    const handleTransitionEnd = () => {
      if (rafId) cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(() => {
        if (map && map.getContainer()) {
          map.invalidateSize({ animate: false, pan: false });
        }
        rafId = null;
      });
    };
    container.parentElement?.addEventListener('transitionend', handleTransitionEnd);
    
    return () => {
      if (rafId) cancelAnimationFrame(rafId);
      observer.disconnect();
      container.parentElement?.removeEventListener('transitionend', handleTransitionEnd);
    };
  }, [map]);
  
  return null;
};

// Capture des clics sur la carte pour créer des waypoints
export const MapClickHandler = ({ onMapClick }) => {
  useMapEvents({
    click: (e) => {
      console.log('[MapClickHandler] Click detected at:', e.latlng.lat, e.latlng.lng);
      if (onMapClick) onMapClick(e.latlng.lat, e.latlng.lng);
    }
  });
  return null;
};
