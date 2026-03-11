/**
 * Advanced Geospatial Data Layer - V5-ULTIME
 * ==========================================
 * 
 * Couche géospatiale avancée avec analyses.
 */

import React, { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { MapPin, Layers, Target, Navigation } from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Types d'analyses géospatiales
export const GEOSPATIAL_ANALYSIS_TYPES = {
  VIEWSHED: 'viewshed',
  SLOPE: 'slope',
  ASPECT: 'aspect',
  DISTANCE: 'distance',
  HOTSPOTS: 'hotspots',
};

export const GeospatialLayer = ({ 
  mapRef, 
  visible = true, 
  analysisType = 'viewshed',
  point = null
}) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!visible || !point) return;
    
    const runAnalysis = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE}/api/v1/advanced-geospatial/${analysisType}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ point, radius: 1000 })
        });
        const data = await response.json();
        setAnalysis(data);
      } catch (error) {
        console.error('Geospatial analysis error:', error);
      }
      setLoading(false);
    };
    
    runAnalysis();
  }, [visible, analysisType, point]);

  if (!visible) return null;

  return (
    <div className="geospatial-layer" data-testid="geospatial-layer">
      {loading && (
        <div className="absolute top-4 right-4 bg-black/80 px-3 py-2 rounded-lg">
          <span className="text-sm text-white flex items-center gap-2">
            <Navigation className="h-4 w-4 text-purple-500 animate-pulse" />
            Analyse géospatiale...
          </span>
        </div>
      )}
      {/* Analysis overlay would be rendered via map library */}
    </div>
  );
};

export const GeospatialOverlay = ({ 
  type = 'viewshed', 
  data,
  visible = true,
  opacity = 0.6 
}) => {
  const overlayColors = {
    viewshed: { visible: 'rgba(34, 197, 94, 0.4)', hidden: 'rgba(239, 68, 68, 0.3)' },
    slope: { low: '#22c55e', medium: '#f59e0b', high: '#ef4444' },
    hotspots: { hot: '#ef4444', warm: '#f59e0b', cold: '#3b82f6' },
  };

  if (!visible || !data) return null;

  return (
    <div 
      className="geospatial-overlay absolute inset-0 pointer-events-none"
      style={{ opacity }}
      data-testid={`geospatial-overlay-${type}`}
    >
      {/* Overlay visualization */}
    </div>
  );
};

export const GeospatialLegend = ({ analysisType = 'viewshed', className }) => {
  const legends = {
    viewshed: [
      { label: 'Zone visible', color: 'rgba(34, 197, 94, 0.6)' },
      { label: 'Zone masquée', color: 'rgba(239, 68, 68, 0.4)' },
    ],
    slope: [
      { label: 'Pente faible (0-15°)', color: '#22c55e' },
      { label: 'Pente moyenne (15-30°)', color: '#f59e0b' },
      { label: 'Pente forte (>30°)', color: '#ef4444' },
    ],
    hotspots: [
      { label: 'Activité élevée', color: '#ef4444' },
      { label: 'Activité moyenne', color: '#f59e0b' },
      { label: 'Activité faible', color: '#3b82f6' },
    ],
  };

  const items = legends[analysisType] || legends.viewshed;

  return (
    <div className={`bg-black/80 backdrop-blur-sm rounded-lg p-3 ${className}`}>
      <h4 className="text-white text-sm font-medium mb-2 flex items-center gap-2">
        <Target className="h-4 w-4 text-purple-500" />
        Analyse: {analysisType}
      </h4>
      <div className="space-y-1.5">
        {items.map((item, idx) => (
          <div key={idx} className="flex items-center gap-2">
            <div 
              className="w-4 h-3 rounded"
              style={{ backgroundColor: item.color }}
            />
            <span className="text-gray-300 text-xs">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default GeospatialLayer;
