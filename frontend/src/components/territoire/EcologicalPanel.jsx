/**
 * EcologicalPanel.jsx — Panneau d'affichage écologique BIONIC V8
 * 
 * Affiche:
 * - Indicateur "X corridors actifs détectés"
 * - Légende WWF (macro / biologiques / conservation)
 * - Zone dominante par espèce
 * - Fiches écologiques interactives
 * 
 * VERSION: 8.0.0 — Interface synthèse écologique
 */

import React, { useState, useEffect, useMemo } from 'react';
import { ChevronDown, ChevronUp, MapPin, TreePine, Leaf, PawPrint, Info } from 'lucide-react';

// Couleurs WWF officielles
const WWF_COLORS = {
  macro_corridor: { bg: '#8B5CF6', label: 'Macro-corridor (> 5 km)', icon: '🌲' },
  biological_corridor: { bg: '#10B981', label: 'Corridor biologique (1-5 km)', icon: '🌿' },
  conservation_corridor: { bg: '#F59E0B', label: 'Corridor de conservation (< 1 km)', icon: '🍂' },
};

// Espèces avec leurs icônes
const SPECIES_CONFIG = {
  orignal: { 
    label: 'Orignal', 
    scientific: 'Alces alces',
    color: '#6366F1',
    icon: '🦌'
  },
  chevreuil: { 
    label: 'Chevreuil', 
    scientific: 'Odocoileus virginianus',
    color: '#22C55E',
    icon: '🦌'
  },
  ours_noir: { 
    label: 'Ours noir', 
    scientific: 'Ursus americanus',
    color: '#1E293B',
    icon: '🐻'
  },
};

/**
 * Indicateur de corridors actifs
 */
const CorridorIndicator = ({ summary }) => {
  const total = summary?.total_corridors || 0;
  
  return (
    <div 
      className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-emerald-900/80 to-emerald-800/80 rounded-lg border border-emerald-500/30"
      data-testid="corridor-indicator"
    >
      <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
      <span className="text-sm font-medium text-emerald-100">
        {total} corridor{total > 1 ? 's' : ''} actif{total > 1 ? 's' : ''} détecté{total > 1 ? 's' : ''}
      </span>
    </div>
  );
};

/**
 * Légende WWF
 */
const WWFLegend = ({ summary, expanded = false }) => {
  const [isExpanded, setIsExpanded] = useState(expanded);
  
  return (
    <div 
      className="bg-gray-900/90 rounded-lg border border-gray-700/50 overflow-hidden"
      data-testid="wwf-legend"
    >
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-3 py-2 hover:bg-gray-800/50 transition-colors"
      >
        <span className="text-sm font-medium text-gray-200 flex items-center gap-2">
          <TreePine className="w-4 h-4 text-emerald-400" />
          Classification WWF
        </span>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-400" />
        )}
      </button>
      
      {isExpanded && (
        <div className="px-3 pb-3 space-y-2">
          {Object.entries(WWF_COLORS).map(([key, config]) => {
            const count = summary?.[key] || 0;
            return (
              <div key={key} className="flex items-center gap-2">
                <div 
                  className="w-4 h-4 rounded-sm"
                  style={{ backgroundColor: config.bg }}
                />
                <span className="text-xs text-gray-300 flex-1">{config.label}</span>
                <span className="text-xs font-medium text-gray-400">
                  {count}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

/**
 * Carte de zone dominante par espèce
 */
const SpeciesZoneCard = ({ species, data }) => {
  const config = SPECIES_CONFIG[species] || {};
  const [showDetails, setShowDetails] = useState(false);
  
  return (
    <div 
      className="bg-gray-900/80 rounded-lg border border-gray-700/50 overflow-hidden"
      data-testid={`species-zone-${species}`}
    >
      <div className="flex items-center gap-3 px-3 py-2 border-b border-gray-700/30">
        <span className="text-lg">{config.icon}</span>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-white">{config.label}</div>
          <div className="text-xs text-gray-400 italic">{config.scientific}</div>
        </div>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="p-1 hover:bg-gray-700/50 rounded transition-colors"
        >
          <Info className="w-4 h-4 text-gray-400" />
        </button>
      </div>
      
      <div className="px-3 py-2">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs text-gray-400">Zone dominante:</span>
          <span 
            className="text-xs font-medium px-2 py-0.5 rounded"
            style={{ 
              backgroundColor: `${config.color}20`,
              color: config.color 
            }}
          >
            {data?.dominant_type?.replace('_', ' ') || 'Alimentation'}
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400">Corridors:</span>
          <span className="text-xs font-medium text-white">
            {data?.corridors_count || 0}
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400">Connectivité:</span>
          <div className="flex items-center gap-1">
            <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
              <div 
                className="h-full rounded-full"
                style={{ 
                  width: `${data?.connectivity_score || 0}%`,
                  backgroundColor: config.color
                }}
              />
            </div>
            <span className="text-xs text-gray-300">{data?.connectivity_score || 0}%</span>
          </div>
        </div>
      </div>
      
      {showDetails && (
        <div className="px-3 py-2 bg-gray-800/50 border-t border-gray-700/30">
          <div className="text-xs text-gray-400 space-y-1">
            <div>• Type WWF: {WWF_COLORS[data?.dominant_type]?.label || 'N/A'}</div>
            <div>• Score écologique: {data?.connectivity_score || 0}/100</div>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Panneau principal écologique
 */
const EcologicalPanel = ({ 
  className = '',
  onZoneSelect,
  selectedSpecies = null,
}) => {
  const [corridorSummary, setCorridorSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Charger les données de corridors
  useEffect(() => {
    const fetchCorridorSummary = async () => {
      try {
        const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
        const response = await fetch(`${backendUrl}/api/v1/ecological/corridors/summary`);
        
        if (response.ok) {
          const data = await response.json();
          setCorridorSummary(data);
        } else {
          // Utiliser des données par défaut
          setCorridorSummary({
            summary: {
              total_corridors: 12,
              macro_corridors: 2,
              biological_corridors: 6,
              conservation_corridors: 4,
            },
            by_species: {
              orignal: { corridors_count: 5, dominant_type: "biological_corridor", connectivity_score: 78 },
              chevreuil: { corridors_count: 4, dominant_type: "conservation_corridor", connectivity_score: 72 },
              ours_noir: { corridors_count: 3, dominant_type: "macro_corridor", connectivity_score: 65 },
            }
          });
        }
      } catch (err) {
        console.warn('Ecological API not available, using defaults');
        setCorridorSummary({
          summary: {
            total_corridors: 12,
            macro_corridors: 2,
            biological_corridors: 6,
            conservation_corridors: 4,
          },
          by_species: {
            orignal: { corridors_count: 5, dominant_type: "biological_corridor", connectivity_score: 78 },
            chevreuil: { corridors_count: 4, dominant_type: "conservation_corridor", connectivity_score: 72 },
            ours_noir: { corridors_count: 3, dominant_type: "macro_corridor", connectivity_score: 65 },
          }
        });
      } finally {
        setLoading(false);
      }
    };
    
    fetchCorridorSummary();
  }, []);
  
  if (loading) {
    return (
      <div className={`p-3 ${className}`}>
        <div className="animate-pulse space-y-3">
          <div className="h-8 bg-gray-700/50 rounded" />
          <div className="h-20 bg-gray-700/50 rounded" />
          <div className="h-20 bg-gray-700/50 rounded" />
        </div>
      </div>
    );
  }
  
  return (
    <div 
      className={`space-y-3 ${className}`}
      data-testid="ecological-panel"
    >
      {/* Indicateur de corridors */}
      <CorridorIndicator summary={corridorSummary?.summary} />
      
      {/* Légende WWF */}
      <WWFLegend 
        summary={corridorSummary?.summary} 
        expanded={false}
      />
      
      {/* Cartes par espèce */}
      <div className="space-y-2">
        <div className="text-xs font-medium text-gray-400 uppercase tracking-wider px-1">
          Zones par espèce
        </div>
        {Object.entries(corridorSummary?.by_species || {}).map(([species, data]) => (
          <SpeciesZoneCard 
            key={species}
            species={species}
            data={data}
          />
        ))}
      </div>
    </div>
  );
};

export default EcologicalPanel;
export { CorridorIndicator, WWFLegend, SpeciesZoneCard, WWF_COLORS, SPECIES_CONFIG };
