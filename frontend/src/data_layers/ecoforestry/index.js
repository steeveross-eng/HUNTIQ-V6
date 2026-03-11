/**
 * Ecoforestry Data Layer - V5-ULTIME
 * ===================================
 * 
 * Couche de données écoforestières pour la carte.
 */

import React, { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { TreePine, Layers } from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Service local
const EcoforestryService = {
  async getForestData(bounds) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/ecoforestry/coverage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bounds)
      });
      return response.json();
    } catch (error) {
      return null;
    }
  }
};

// Types de couvert forestier
export const FOREST_TYPES = {
  CONIFEROUS: { label: 'Conifères', color: '#15803d' },
  DECIDUOUS: { label: 'Feuillus', color: '#65a30d' },
  MIXED: { label: 'Mixte', color: '#4ade80' },
  WETLAND: { label: 'Milieu humide', color: '#0ea5e9' },
  CLEARING: { label: 'Clairière', color: '#fbbf24' },
};

export const EcoforestryLayer = ({ mapRef, visible = true, opacity = 0.7 }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!visible) return;
    
    const loadData = async () => {
      setLoading(true);
      const bounds = mapRef?.getBounds?.() || {
        north: 47.0,
        south: 46.5,
        east: -71.0,
        west: -71.5
      };
      
      const result = await EcoforestryService.getForestData(bounds);
      setData(result);
      setLoading(false);
    };
    
    loadData();
  }, [visible, mapRef]);

  if (!visible) return null;

  return (
    <div className="ecoforestry-layer" data-testid="ecoforestry-layer">
      {loading && (
        <div className="absolute top-4 right-4 bg-black/80 px-3 py-2 rounded-lg">
          <span className="text-sm text-white flex items-center gap-2">
            <TreePine className="h-4 w-4 text-green-500 animate-pulse" />
            Chargement données forestières...
          </span>
        </div>
      )}
      {/* Layer overlay would be rendered via map library */}
    </div>
  );
};

export const EcoforestryLegend = ({ className }) => {
  return (
    <div className={`bg-black/80 backdrop-blur-sm rounded-lg p-3 ${className}`}>
      <h4 className="text-white text-sm font-medium mb-2 flex items-center gap-2">
        <Layers className="h-4 w-4 text-green-500" />
        Couvert Forestier
      </h4>
      <div className="space-y-1.5">
        {Object.entries(FOREST_TYPES).map(([key, type]) => (
          <div key={key} className="flex items-center gap-2">
            <div 
              className="w-4 h-3 rounded"
              style={{ backgroundColor: type.color }}
            />
            <span className="text-gray-300 text-xs">{type.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EcoforestryLayer;
