/**
 * BionicLayerPanel - BIONIC TACTICAL Design System
 * Advanced layer control panel for map visualization
 */

import React, { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import {
  Layers,
  ChevronDown,
  ChevronRight,
  Eye,
  EyeOff,
  X,
  Minus,
  Target,
  TreePine,
  Crosshair,
  Database,
  MapPin,
  Star,
  Home,
  Droplets,
  Sun,
  Mountain,
  Thermometer,
  Flame,
  Users,
  DoorOpen,
  Route,
  PauseCircle,
} from 'lucide-react';
import { Slider } from '@/components/ui/slider';

// Zone type icons mapping
const ZONE_ICONS = {
  rut: Flame,
  repos: Home,
  alimentation: TreePine,
  corridor: Route,
  affut: Target,
  habitat: MapPin,
  soleil: Sun,
  pente: Mountain,
  hydro: Droplets,
  foret: TreePine,
  thermique: Thermometer,
  hotspot: Star,
  pression: Users,
  acces: DoorOpen,
};

// Zone colors
const ZONE_COLORS = {
  rut: '#FF4D6D',
  repos: '#8B5CF6',
  alimentation: '#22C55E',
  corridor: '#06B6D4',
  affut: '#F5A623',
  habitat: '#10B981',
  soleil: '#FBBF24',
  pente: '#A78BFA',
  hydro: '#3B82F6',
  foret: '#059669',
  thermique: '#EF4444',
  hotspot: '#FF6B6B',
  pression: '#F59E0B',
  acces: '#6366F1',
};

// Layer groups configuration
const LAYER_GROUPS = {
  behavioral: {
    id: 'behavioral',
    label: 'Zones Comportementales',
    labelEn: 'Behavioral Zones',
    icon: Target,
    defaultExpanded: true,
    layers: [
      { id: 'rut', label: 'Zone de Rut', labelEn: 'Rut Zone' },
      { id: 'repos', label: 'Zone de Repos', labelEn: 'Rest Zone' },
      { id: 'alimentation', label: 'Zone d\'Alimentation', labelEn: 'Feeding Zone' },
      { id: 'corridor', label: 'Corridors', labelEn: 'Corridors' },
      { id: 'affut', label: 'Affûts Potentiels', labelEn: 'Potential Ambush' },
      { id: 'habitat', label: 'Habitats Optimaux', labelEn: 'Optimal Habitats' },
    ],
  },
  environmental: {
    id: 'environmental',
    label: 'Zones Environnementales',
    labelEn: 'Environmental Zones',
    icon: TreePine,
    defaultExpanded: false,
    layers: [
      { id: 'soleil', label: 'Ensoleillement', labelEn: 'Sunlight' },
      { id: 'pente', label: 'Orientation/Pentes', labelEn: 'Slope/Orientation' },
      { id: 'hydro', label: 'Hydrographie', labelEn: 'Hydrography' },
      { id: 'foret', label: 'Couvert Forestier', labelEn: 'Forest Cover' },
      { id: 'thermique', label: 'Zones Thermiques', labelEn: 'Thermal Zones' },
    ],
  },
  strategic: {
    id: 'strategic',
    label: 'Zones Stratégiques',
    labelEn: 'Strategic Zones',
    icon: Crosshair,
    defaultExpanded: true,
    layers: [
      { id: 'hotspot', label: 'Points Chauds', labelEn: 'Hotspots' },
      { id: 'pression', label: 'Zones de Pression', labelEn: 'Pressure Zones' },
      { id: 'acces', label: 'Points d\'Accès', labelEn: 'Access Points' },
    ],
  },
  external: {
    id: 'external',
    label: 'Données Externes',
    labelEn: 'External Data',
    icon: Database,
    defaultExpanded: false,
    layers: [
      { id: 'wms_foret', label: 'WMS Forêt', labelEn: 'WMS Forest' },
      { id: 'wms_hydro', label: 'WMS Hydro', labelEn: 'WMS Hydro' },
      { id: 'wms_topo', label: 'WMS Topo', labelEn: 'WMS Topo' },
      { id: 'wms_routes', label: 'WMS Routes', labelEn: 'WMS Roads' },
    ],
  },
};

// Presets configuration
const PRESETS = [
  { id: 'rut', label: 'Rut', layers: ['rut', 'corridor', 'hotspot'] },
  { id: 'repos', label: 'Repos', layers: ['repos', 'habitat', 'foret'] },
  { id: 'alimentation', label: 'Alim.', layers: ['alimentation', 'hydro', 'habitat'] },
  { id: 'all', label: 'Tous', layers: 'all' },
  { id: 'none', label: 'Aucun', layers: [] },
];

// Layer item component
const LayerItem = ({ layer, isVisible, onToggle, language = 'fr' }) => {
  const Icon = ZONE_ICONS[layer.id] || MapPin;
  const color = ZONE_COLORS[layer.id] || '#666';
  const label = language === 'en' ? (layer.labelEn || layer.label) : layer.label;
  
  return (
    <div
      className={cn(
        'flex items-center gap-2 px-3 py-1.5 rounded-sm',
        'hover:bg-white/5 transition-colors cursor-pointer group'
      )}
      onClick={() => onToggle(layer.id)}
    >
      {/* Toggle indicator */}
      <div
        className={cn(
          'w-3 h-3 rounded-full border-2 transition-colors',
          isVisible ? 'bg-current' : 'bg-transparent'
        )}
        style={{ borderColor: color, color: isVisible ? color : 'transparent' }}
      />
      
      {/* Icon */}
      <Icon
        className="h-4 w-4 transition-colors"
        style={{ color: isVisible ? color : '#6B7280' }}
      />
      
      {/* Label */}
      <span className={cn(
        'flex-1 text-xs font-medium',
        isVisible ? 'text-white' : 'text-gray-500'
      )}>
        {label}
      </span>
      
      {/* Color indicator bar */}
      <div
        className={cn(
          'w-16 h-1 rounded-full transition-opacity',
          isVisible ? 'opacity-100' : 'opacity-30'
        )}
        style={{ backgroundColor: color }}
      />
      
      {/* Visibility toggle */}
      <button
        className={cn(
          'p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity',
          'hover:bg-white/10'
        )}
        onClick={(e) => {
          e.stopPropagation();
          onToggle(layer.id);
        }}
      >
        {isVisible ? (
          <Eye className="h-3 w-3 text-gray-400" />
        ) : (
          <EyeOff className="h-3 w-3 text-gray-500" />
        )}
      </button>
    </div>
  );
};

// Layer group component
const LayerGroup = ({
  group,
  visibility,
  onToggle,
  onToggleGroup,
  language = 'fr',
}) => {
  const [expanded, setExpanded] = useState(group.defaultExpanded);
  const Icon = group.icon;
  const label = language === 'en' ? (group.labelEn || group.label) : group.label;
  
  const allVisible = group.layers.every((l) => visibility[l.id]);
  const someVisible = group.layers.some((l) => visibility[l.id]);
  
  return (
    <div className="mb-2">
      {/* Group header */}
      <div
        className={cn(
          'flex items-center gap-2 px-2 py-2 rounded-sm',
          'hover:bg-white/5 transition-colors cursor-pointer'
        )}
        onClick={() => setExpanded(!expanded)}
      >
        {expanded ? (
          <ChevronDown className="h-4 w-4 text-gray-400" />
        ) : (
          <ChevronRight className="h-4 w-4 text-gray-400" />
        )}
        
        <Icon className="h-4 w-4 text-[#F5A623]" />
        
        <span className="flex-1 text-xs font-semibold text-white uppercase tracking-wider">
          {label}
        </span>
        
        {/* Toggle all button */}
        <button
          className={cn(
            'flex items-center gap-1 px-2 py-0.5 rounded text-xs',
            'transition-colors',
            allVisible
              ? 'bg-[#F5A623]/20 text-[#F5A623]'
              : someVisible
              ? 'bg-white/10 text-gray-400'
              : 'bg-transparent text-gray-500 hover:text-gray-400'
          )}
          onClick={(e) => {
            e.stopPropagation();
            onToggleGroup(group.id, !allVisible);
          }}
        >
          <Eye className="h-3 w-3" />
          {language === 'en' ? 'ALL' : 'TOUT'}
        </button>
      </div>
      
      {/* Group layers */}
      {expanded && (
        <div className="ml-4 border-l border-white/10 pl-2">
          {group.layers.map((layer) => (
            <LayerItem
              key={layer.id}
              layer={layer}
              isVisible={visibility[layer.id]}
              onToggle={onToggle}
              language={language}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// Main BionicLayerPanel component
export const BionicLayerPanel = ({
  visibility = {},
  onVisibilityChange,
  opacity = 75,
  onOpacityChange,
  onClose,
  onMinimize,
  minimized = false,
  language = 'fr',
  className,
}) => {
  // Toggle single layer
  const handleToggle = useCallback((layerId) => {
    onVisibilityChange?.({
      ...visibility,
      [layerId]: !visibility[layerId],
    });
  }, [visibility, onVisibilityChange]);
  
  // Toggle all layers in a group
  const handleToggleGroup = useCallback((groupId, visible) => {
    const group = LAYER_GROUPS[groupId];
    if (!group) return;
    
    const newVisibility = { ...visibility };
    group.layers.forEach((layer) => {
      newVisibility[layer.id] = visible;
    });
    onVisibilityChange?.(newVisibility);
  }, [visibility, onVisibilityChange]);
  
  // Apply preset
  const handlePreset = useCallback((preset) => {
    if (preset.layers === 'all') {
      const newVisibility = {};
      Object.values(LAYER_GROUPS).forEach((group) => {
        group.layers.forEach((layer) => {
          newVisibility[layer.id] = true;
        });
      });
      onVisibilityChange?.(newVisibility);
    } else if (Array.isArray(preset.layers)) {
      const newVisibility = {};
      Object.values(LAYER_GROUPS).forEach((group) => {
        group.layers.forEach((layer) => {
          newVisibility[layer.id] = preset.layers.includes(layer.id);
        });
      });
      onVisibilityChange?.(newVisibility);
    }
  }, [onVisibilityChange]);
  
  if (minimized) {
    return (
      <button
        className={cn(
          'bg-black/80 backdrop-blur-xl border border-white/10 rounded-md',
          'p-3 shadow-xl',
          'hover:border-[#F5A623]/30 transition-colors',
          className
        )}
        onClick={onMinimize}
      >
        <Layers className="h-5 w-5 text-[#F5A623]" />
      </button>
    );
  }
  
  return (
    <div
      className={cn(
        'bg-black/80 backdrop-blur-xl border border-white/10 rounded-md',
        'w-80 shadow-xl',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-white/10">
        <div className="flex items-center gap-2">
          <Layers className="h-4 w-4 text-[#F5A623]" />
          <span className="text-sm font-semibold text-white uppercase tracking-wider">
            {language === 'en' ? 'BIONIC Layers' : 'Couches BIONIC'}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            className="p-1 rounded hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
            onClick={onMinimize}
          >
            <Minus className="h-4 w-4" />
          </button>
          <button
            className="p-1 rounded hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
            onClick={onClose}
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
      
      {/* Content */}
      <div className="p-2 max-h-[50vh] overflow-y-auto">
        {Object.values(LAYER_GROUPS).map((group) => (
          <LayerGroup
            key={group.id}
            group={group}
            visibility={visibility}
            onToggle={handleToggle}
            onToggleGroup={handleToggleGroup}
            language={language}
          />
        ))}
      </div>
      
      {/* Footer controls */}
      <div className="border-t border-white/10 p-3 space-y-3">
        {/* Opacity slider */}
        <div>
          <label className="text-xs text-gray-400 uppercase tracking-wider block mb-2">
            {language === 'en' ? 'Global Opacity' : 'Opacité globale'}
          </label>
          <div className="flex items-center gap-3">
            <Slider
              value={[opacity]}
              onValueChange={([val]) => onOpacityChange?.(val)}
              max={100}
              step={5}
              className="flex-1"
            />
            <span className="text-white text-sm font-mono w-12 text-right">
              {opacity}%
            </span>
          </div>
        </div>
        
        {/* Presets */}
        <div>
          <label className="text-xs text-gray-400 uppercase tracking-wider block mb-2">
            {language === 'en' ? 'Presets' : 'Préréglages'}
          </label>
          <div className="flex flex-wrap gap-1">
            {PRESETS.map((preset) => (
              <button
                key={preset.id}
                className={cn(
                  'px-2 py-1 text-xs font-medium uppercase tracking-wide rounded',
                  'border border-white/10',
                  'hover:bg-white/10 hover:border-white/20 transition-colors',
                  'text-gray-400 hover:text-white'
                )}
                onClick={() => handlePreset(preset)}
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Export layer configuration for use in map
export { LAYER_GROUPS, ZONE_COLORS, ZONE_ICONS };

export default BionicLayerPanel;
