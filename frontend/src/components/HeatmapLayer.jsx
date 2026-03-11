/**
 * HeatmapLayer - Leaflet heatmap component for waypoint performance
 * Uses leaflet.heat for visualization
 */
import { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';

export const HeatmapLayer = ({ data, options = {} }) => {
  const map = useMap();

  useEffect(() => {
    if (!data || data.length === 0) return;

    // Convert data to heatmap format [lat, lng, intensity]
    const heatData = data.map(point => [
      point.lat,
      point.lng,
      point.intensity || 0.5
    ]);

    // Default options for hunting heatmap
    const defaultOptions = {
      radius: 30,
      blur: 20,
      maxZoom: 17,
      max: 1.0,
      gradient: {
        0.0: '#3b82f6',  // Blue - weak
        0.25: '#22c55e', // Green - standard
        0.5: '#f5a623',  // Orange - good
        0.75: '#ef4444', // Red - hotspot
        1.0: '#dc2626'   // Dark red - super hotspot
      }
    };

    const heatOptions = { ...defaultOptions, ...options };

    // Create and add heatmap layer
    const heatLayer = L.heatLayer(heatData, heatOptions);
    heatLayer.addTo(map);

    // Cleanup on unmount
    return () => {
      map.removeLayer(heatLayer);
    };
  }, [data, map, options]);

  return null;
};

export default HeatmapLayer;
