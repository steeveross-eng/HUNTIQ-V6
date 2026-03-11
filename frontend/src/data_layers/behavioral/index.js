/**
 * Behavioral Data Layer - V5-ULTIME
 * ==================================
 * 
 * Couche de données comportementales de la faune.
 */

import React, { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { Activity, Eye } from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Types de comportement
export const BEHAVIOR_TYPES = {
  FEEDING: { label: 'Alimentation', color: '#22c55e', intensity: 'high' },
  RESTING: { label: 'Repos', color: '#3b82f6', intensity: 'low' },
  TRANSIT: { label: 'Déplacement', color: '#f59e0b', intensity: 'medium' },
  MATING: { label: 'Rut', color: '#ef4444', intensity: 'high' },
};

export const BehavioralLayer = ({ mapRef, visible = true, species = 'deer' }) => {
  const [patterns, setPatterns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!visible) return;
    
    const loadPatterns = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE}/api/v1/behavioral/patterns?species=${species}`);
        const data = await response.json();
        setPatterns(data?.patterns || []);
      } catch (error) {
        console.error('Behavioral data error:', error);
      }
      setLoading(false);
    };
    
    loadPatterns();
  }, [visible, species]);

  if (!visible) return null;

  return (
    <div className="behavioral-layer" data-testid="behavioral-layer">
      {loading && (
        <div className="absolute top-4 right-4 bg-black/80 px-3 py-2 rounded-lg">
          <span className="text-sm text-white flex items-center gap-2">
            <Activity className="h-4 w-4 text-blue-500 animate-pulse" />
            Analyse comportementale...
          </span>
        </div>
      )}
    </div>
  );
};

export const BehavioralHeatmap = ({ data, visible = true, intensity = 0.8 }) => {
  if (!visible || !data) return null;

  return (
    <div 
      className="behavioral-heatmap" 
      data-testid="behavioral-heatmap"
      style={{ opacity: intensity }}
    >
      {/* Heatmap would be rendered via map library */}
    </div>
  );
};

export const BehavioralLegend = ({ className }) => {
  return (
    <div className={`bg-black/80 backdrop-blur-sm rounded-lg p-3 ${className}`}>
      <h4 className="text-white text-sm font-medium mb-2 flex items-center gap-2">
        <Eye className="h-4 w-4 text-blue-500" />
        Comportement Faune
      </h4>
      <div className="space-y-1.5">
        {Object.entries(BEHAVIOR_TYPES).map(([key, type]) => (
          <div key={key} className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <div 
                className="w-4 h-3 rounded"
                style={{ backgroundColor: type.color }}
              />
              <span className="text-gray-300 text-xs">{type.label}</span>
            </div>
            <Badge variant="outline" className="text-[10px] px-1 py-0">
              {type.intensity}
            </Badge>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BehavioralLayer;
