/**
 * HotspotControlPanel - Panneau de controle des hotspots BIONIC
 * PHASE P1-HOTSPOTS V2 - REFONTE
 * 
 * Fonctionnalites UX (OBLIGATOIRES):
 * - Dropdown de selection d'espece
 * - Activation/desactivation individuelle par hotspot
 * - Activation par groupe en un clic
 * - ZERO rechargement de carte
 * - Etat instantane
 */
import React, { useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { 
  Eye, EyeOff, Flame, Leaf, Heart, Thermometer, Droplets,
  AlertTriangle, Snowflake, User, Diamond, Star,
  ArrowRight, CircleDot, Route, ChevronDown, ChevronUp, X,
  Filter, ToggleLeft
} from 'lucide-react';

// Couleurs par espece (conformes au backend)
const SPECIES_COLORS = {
  moose: '#FF6B00',       // Orange vif (Orignal)
  deer: '#8B4513',        // Brun (Chevreuil)
  bear: '#4A4A4A',        // Gris fonce (Ours)
  wild_turkey: '#DAA520', // Or fonce (Dindon)
  elk: '#CD853F'          // Peru (Wapiti)
};

// Types de hotspots avec icones et couleurs
const HOTSPOT_TYPES = [
  { id: 'activity_peak', label: "Pic d'activite", Icon: Flame, color: '#FFD700', group: 'activity' },
  { id: 'feeding_zone', label: 'Zone alimentation', Icon: Leaf, color: '#4CAF50', group: 'feeding' },
  { id: 'rut_zone', label: 'Zone de rut', Icon: Heart, color: '#E91E63', group: 'reproduction' },
  { id: 'thermal_refuge', label: 'Refuge thermique', Icon: Thermometer, color: '#00BCD4', group: 'environment' },
  { id: 'water_source', label: "Point d'eau", Icon: Droplets, color: '#2196F3', group: 'environment' },
  { id: 'predation_risk', label: 'Risque predation', Icon: AlertTriangle, color: '#F44336', group: 'risk' },
  { id: 'snow_impact', label: 'Impact neige', Icon: Snowflake, color: '#90A4AE', group: 'environment' },
  { id: 'human_avoidance', label: 'Evitement humain', Icon: User, color: '#795548', group: 'risk' },
  { id: 'mineral_site', label: 'Site mineral', Icon: Diamond, color: '#FFC107', group: 'feeding' },
  { id: 'composite_optimal', label: 'Zone optimale', Icon: Star, color: '#FF9800', group: 'optimal' }
];

// Types de zones comportementales
const ZONE_TYPES = [
  { id: 'feeding', label: 'Alimentation', color: '#4CAF50' },
  { id: 'bedding', label: 'Repos', color: '#3F51B5' },
  { id: 'rut_arena', label: 'Arene rut', color: '#E91E63' },
  { id: 'thermal_cover', label: 'Couvert thermique', color: '#00BCD4' },
  { id: 'water_access', label: 'Acces eau', color: '#2196F3' },
  { id: 'predation_zone', label: 'Zone predation', color: '#F44336' },
  { id: 'yarding_zone', label: 'Ravage hivernal', color: '#607D8B' }
];

// Types de corridors
const CORRIDOR_TYPES = [
  { id: 'movement', label: 'Deplacement', color: '#8BC34A' },
  { id: 'avoidance', label: 'Evitement', color: '#EF5350' },
  { id: 'preferred', label: 'Route preferee', color: '#4CAF50' },
  { id: 'feeding_transit', label: 'Transit alim.', color: '#FF9800' }
];

// Especes supportees avec couleurs
const SPECIES = [
  { id: 'moose', label: 'Orignal', color: SPECIES_COLORS.moose },
  { id: 'deer', label: 'Chevreuil', color: SPECIES_COLORS.deer },
  { id: 'bear', label: 'Ours', color: SPECIES_COLORS.bear },
  { id: 'wild_turkey', label: 'Dindon sauvage', color: SPECIES_COLORS.wild_turkey },
  { id: 'elk', label: 'Wapiti', color: SPECIES_COLORS.elk }
];

// Periodes temporelles
const TIME_RANGES = [
  { id: '24h', label: '24h' },
  { id: '72h', label: '72h' },
  { id: '7d', label: '7 jours' }
];

export const HotspotControlPanel = ({ 
  onSettingsChange,
  isOpen,
  onClose,
  defaultSettings = {},
  onTogglePanelOpen = () => {},  // Callback pour ouvrir le panneau ON/OFF
  hotspotsCount = 0  // Nombre de hotspots actuellement affichés
}) => {
  // Etats des hotspots
  const [showHotspots, setShowHotspots] = useState(defaultSettings.showHotspots ?? true);
  const [activeHotspotTypes, setActiveHotspotTypes] = useState(
    defaultSettings.hotspotTypes ?? ['activity_peak', 'feeding_zone', 'rut_zone']
  );
  
  // Etats des zones
  const [showZones, setShowZones] = useState(defaultSettings.showZones ?? false);
  const [activeZoneTypes, setActiveZoneTypes] = useState(
    defaultSettings.zoneTypes ?? ['feeding', 'bedding', 'water_access']
  );
  
  // Etats des corridors
  const [showCorridors, setShowCorridors] = useState(defaultSettings.showCorridors ?? false);
  const [activeCorridorTypes, setActiveCorridorTypes] = useState(
    defaultSettings.corridorTypes ?? ['movement', 'preferred', 'feeding_transit']
  );
  
  // Filtres
  const [selectedSpecies, setSelectedSpecies] = useState(
    defaultSettings.species ?? ['moose']
  );
  const [timeRange, setTimeRange] = useState(defaultSettings.timeRange ?? '24h');
  const [minScore, setMinScore] = useState(defaultSettings.minScoreThreshold ?? 50);
  
  // Sections collapsibles
  const [expandedSections, setExpandedSections] = useState({
    hotspots: true,
    zones: false,
    corridors: false,
    filters: false
  });

  // Notifier les changements
  const notifyChange = useCallback((updates) => {
    const settings = {
      showHotspots: updates.showHotspots ?? showHotspots,
      hotspotTypes: updates.hotspotTypes ?? activeHotspotTypes,
      showZones: updates.showZones ?? showZones,
      zoneTypes: updates.zoneTypes ?? activeZoneTypes,
      showCorridors: updates.showCorridors ?? showCorridors,
      corridorTypes: updates.corridorTypes ?? activeCorridorTypes,
      species: updates.species ?? selectedSpecies,
      timeRange: updates.timeRange ?? timeRange,
      minScoreThreshold: updates.minScore ?? minScore
    };
    onSettingsChange?.(settings);
  }, [showHotspots, activeHotspotTypes, showZones, activeZoneTypes, showCorridors, activeCorridorTypes, selectedSpecies, timeRange, minScore, onSettingsChange]);

  // Toggle section
  const toggleSection = (section) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  // Toggle hotspot type
  const toggleHotspotType = (typeId) => {
    const newTypes = activeHotspotTypes.includes(typeId)
      ? activeHotspotTypes.filter(t => t !== typeId)
      : [...activeHotspotTypes, typeId];
    setActiveHotspotTypes(newTypes);
    notifyChange({ hotspotTypes: newTypes });
  };

  // Toggle zone type
  const toggleZoneType = (typeId) => {
    const newTypes = activeZoneTypes.includes(typeId)
      ? activeZoneTypes.filter(t => t !== typeId)
      : [...activeZoneTypes, typeId];
    setActiveZoneTypes(newTypes);
    notifyChange({ zoneTypes: newTypes });
  };

  // Toggle corridor type
  const toggleCorridorType = (typeId) => {
    const newTypes = activeCorridorTypes.includes(typeId)
      ? activeCorridorTypes.filter(t => t !== typeId)
      : [...activeCorridorTypes, typeId];
    setActiveCorridorTypes(newTypes);
    notifyChange({ corridorTypes: newTypes });
  };

  // Toggle espece
  const toggleSpecies = (speciesId) => {
    const newSpecies = selectedSpecies.includes(speciesId)
      ? selectedSpecies.filter(s => s !== speciesId)
      : [...selectedSpecies, speciesId];
    setSelectedSpecies(newSpecies);
    notifyChange({ species: newSpecies });
  };

  // Groupes de hotspots pour activation rapide
  const hotspotGroups = {
    activity: ['activity_peak', 'composite_optimal'],
    feeding: ['feeding_zone', 'mineral_site'],
    reproduction: ['rut_zone'],
    environment: ['thermal_refuge', 'water_source', 'snow_impact'],
    risk: ['predation_risk', 'human_avoidance']
  };

  // Activer un groupe entier
  const toggleGroup = (groupName) => {
    const groupTypes = hotspotGroups[groupName] || [];
    const allActive = groupTypes.every(t => activeHotspotTypes.includes(t));
    
    let newTypes;
    if (allActive) {
      newTypes = activeHotspotTypes.filter(t => !groupTypes.includes(t));
    } else {
      newTypes = [...new Set([...activeHotspotTypes, ...groupTypes])];
    }
    setActiveHotspotTypes(newTypes);
    notifyChange({ hotspotTypes: newTypes });
  };

  // Tout activer/desactiver
  const toggleAllHotspots = () => {
    if (activeHotspotTypes.length === HOTSPOT_TYPES.length) {
      setActiveHotspotTypes([]);
      notifyChange({ hotspotTypes: [] });
    } else {
      const allTypes = HOTSPOT_TYPES.map(t => t.id);
      setActiveHotspotTypes(allTypes);
      notifyChange({ hotspotTypes: allTypes });
    }
  };

  if (!isOpen) return null;

  return (
    <div 
      className="absolute right-4 top-20 z-[1000] w-72 bg-slate-900/95 backdrop-blur-sm border border-slate-700/60 rounded-xl shadow-xl overflow-hidden"
      data-testid="hotspot-control-panel"
    >
      {/* Header */}
      <div className="px-4 py-3 bg-gradient-to-r from-amber-600/20 to-slate-800/50 border-b border-slate-700/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Eye className="h-4 w-4 text-amber-400" />
          <span className="font-semibold text-white text-sm">Overlays BIONIC</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={onClose}
          className="h-6 w-6 p-0 text-slate-400 hover:text-white"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
      
      <div className="max-h-[70vh] overflow-y-auto">
        {/* Section Hotspots */}
        <div className="border-b border-slate-800">
          <div
            className="w-full px-4 py-2 flex items-center justify-between hover:bg-slate-800/30 cursor-pointer"
          >
            <div 
              className="flex items-center gap-2 flex-1"
              onClick={() => toggleSection('hotspots')}
            >
              <CircleDot className="h-4 w-4 text-amber-400" />
              <span className="text-sm font-medium text-white">Hotspots</span>
              <Badge variant="outline" className="text-xs">
                {activeHotspotTypes.length}/{HOTSPOT_TYPES.length}
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              <Switch
                checked={showHotspots}
                onCheckedChange={(checked) => {
                  setShowHotspots(checked);
                  notifyChange({ showHotspots: checked });
                }}
              />
              <div 
                onClick={() => toggleSection('hotspots')}
                className="cursor-pointer p-1"
              >
                {expandedSections.hotspots ? 
                  <ChevronUp className="h-4 w-4 text-slate-400" /> : 
                  <ChevronDown className="h-4 w-4 text-slate-400" />
                }
              </div>
            </div>
          </div>
          
          {expandedSections.hotspots && showHotspots && (
            <div className="px-4 pb-3 space-y-2">
              {/* Bouton ON/OFF individuels */}
              {hotspotsCount > 0 && (
                <button
                  onClick={onTogglePanelOpen}
                  className="w-full px-3 py-2 flex items-center justify-between bg-amber-600/20 hover:bg-amber-600/30 border border-amber-600/40 rounded-lg transition-colors"
                  data-testid="open-toggle-panel-btn"
                >
                  <div className="flex items-center gap-2">
                    <ToggleLeft className="h-4 w-4 text-amber-400" />
                    <span className="text-sm text-amber-300 font-medium">ON/OFF Individuels</span>
                  </div>
                  <Badge className="bg-amber-600/30 text-amber-300 border-amber-600/50">
                    {hotspotsCount}
                  </Badge>
                </button>
              )}
              
              {/* Groupes rapides */}
              <div className="flex flex-wrap gap-1 pb-2 border-b border-slate-800">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={toggleAllHotspots}
                  className="h-6 text-xs px-2"
                >
                  {activeHotspotTypes.length === HOTSPOT_TYPES.length ? 'Aucun' : 'Tous'}
                </Button>
                {Object.keys(hotspotGroups).map(group => {
                  const groupTypes = hotspotGroups[group];
                  const allActive = groupTypes.every(t => activeHotspotTypes.includes(t));
                  return (
                    <Button
                      key={group}
                      variant={allActive ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => toggleGroup(group)}
                      className="h-6 text-xs px-2 capitalize"
                    >
                      {group}
                    </Button>
                  );
                })}
              </div>
              
              {/* Types individuels */}
              <div className="grid grid-cols-2 gap-1">
                {HOTSPOT_TYPES.map(({ id, label, Icon, color }) => (
                  <button
                    key={id}
                    onClick={() => toggleHotspotType(id)}
                    className={`flex items-center gap-1.5 px-2 py-1.5 rounded text-xs transition-all ${
                      activeHotspotTypes.includes(id)
                        ? 'bg-slate-700/60 text-white'
                        : 'bg-slate-800/30 text-slate-500 hover:text-slate-300'
                    }`}
                    data-testid={`hotspot-toggle-${id}`}
                  >
                    <div 
                      className="w-3 h-3 rounded-full flex-shrink-0" 
                      style={{ backgroundColor: activeHotspotTypes.includes(id) ? color : '#4a5568' }}
                    />
                    <span className="truncate">{label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
        
        {/* Section Zones */}
        <div className="border-b border-slate-800">
          <div
            className="w-full px-4 py-2 flex items-center justify-between hover:bg-slate-800/30 cursor-pointer"
          >
            <div 
              className="flex items-center gap-2 flex-1"
              onClick={() => toggleSection('zones')}
            >
              <ArrowRight className="h-4 w-4 text-emerald-400" />
              <span className="text-sm font-medium text-white">Zones</span>
              <Badge variant="outline" className="text-xs">
                {activeZoneTypes.length}/{ZONE_TYPES.length}
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              <Switch
                checked={showZones}
                onCheckedChange={(checked) => {
                  setShowZones(checked);
                  notifyChange({ showZones: checked });
                }}
              />
              <div 
                onClick={() => toggleSection('zones')}
                className="cursor-pointer p-1"
              >
                {expandedSections.zones ? 
                  <ChevronUp className="h-4 w-4 text-slate-400" /> : 
                  <ChevronDown className="h-4 w-4 text-slate-400" />
                }
              </div>
            </div>
          </div>
          
          {expandedSections.zones && showZones && (
            <div className="px-4 pb-3">
              <div className="grid grid-cols-2 gap-1">
                {ZONE_TYPES.map(({ id, label, color }) => (
                  <button
                    key={id}
                    onClick={() => toggleZoneType(id)}
                    className={`flex items-center gap-1.5 px-2 py-1.5 rounded text-xs transition-all ${
                      activeZoneTypes.includes(id)
                        ? 'bg-slate-700/60 text-white'
                        : 'bg-slate-800/30 text-slate-500 hover:text-slate-300'
                    }`}
                  >
                    <div 
                      className="w-3 h-3 rounded-full flex-shrink-0" 
                      style={{ backgroundColor: activeZoneTypes.includes(id) ? color : '#4a5568' }}
                    />
                    <span className="truncate">{label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
        
        {/* Section Corridors */}
        <div className="border-b border-slate-800">
          <div
            className="w-full px-4 py-2 flex items-center justify-between hover:bg-slate-800/30 cursor-pointer"
          >
            <div 
              className="flex items-center gap-2 flex-1"
              onClick={() => toggleSection('corridors')}
            >
              <Route className="h-4 w-4 text-lime-400" />
              <span className="text-sm font-medium text-white">Corridors</span>
              <Badge variant="outline" className="text-xs">
                {activeCorridorTypes.length}/{CORRIDOR_TYPES.length}
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              <Switch
                checked={showCorridors}
                onCheckedChange={(checked) => {
                  setShowCorridors(checked);
                  notifyChange({ showCorridors: checked });
                }}
              />
              <div 
                onClick={() => toggleSection('corridors')}
                className="cursor-pointer p-1"
              >
                {expandedSections.corridors ? 
                  <ChevronUp className="h-4 w-4 text-slate-400" /> : 
                  <ChevronDown className="h-4 w-4 text-slate-400" />
                }
              </div>
            </div>
          </div>
          
          {expandedSections.corridors && showCorridors && (
            <div className="px-4 pb-3">
              <div className="grid grid-cols-2 gap-1">
                {CORRIDOR_TYPES.map(({ id, label, color }) => (
                  <button
                    key={id}
                    onClick={() => toggleCorridorType(id)}
                    className={`flex items-center gap-1.5 px-2 py-1.5 rounded text-xs transition-all ${
                      activeCorridorTypes.includes(id)
                        ? 'bg-slate-700/60 text-white'
                        : 'bg-slate-800/30 text-slate-500 hover:text-slate-300'
                    }`}
                  >
                    <div 
                      className="w-3 h-3 rounded-full flex-shrink-0" 
                      style={{ backgroundColor: activeCorridorTypes.includes(id) ? color : '#4a5568' }}
                    />
                    <span className="truncate">{label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
        
        {/* Section Filtres */}
        <div>
          <button
            onClick={() => toggleSection('filters')}
            className="w-full px-4 py-2 flex items-center justify-between text-left hover:bg-slate-800/30"
          >
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-purple-400" />
              <span className="text-sm font-medium text-white">Filtres</span>
            </div>
            {expandedSections.filters ? 
              <ChevronUp className="h-4 w-4 text-slate-400" /> : 
              <ChevronDown className="h-4 w-4 text-slate-400" />
            }
          </button>
          
          {expandedSections.filters && (
            <div className="px-4 pb-3 space-y-3">
              {/* DROPDOWN ESPECE - Proéminent */}
              <div>
                <label className="text-xs text-slate-400 mb-1.5 block font-medium">
                  Espece cible
                </label>
                <select
                  value={selectedSpecies[0] || 'moose'}
                  onChange={(e) => {
                    const newSpecies = [e.target.value];
                    setSelectedSpecies(newSpecies);
                    notifyChange({ species: newSpecies });
                  }}
                  className="w-full bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                  data-testid="species-dropdown"
                >
                  {SPECIES.map(({ id, label, color }) => (
                    <option key={id} value={id} style={{ color }}>
                      {label}
                    </option>
                  ))}
                </select>
                <div className="mt-1.5 flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: SPECIES_COLORS[selectedSpecies[0]] || SPECIES_COLORS.moose }}
                  />
                  <span className="text-xs text-slate-500">
                    Couleur des contours: {SPECIES.find(s => s.id === selectedSpecies[0])?.label || 'Orignal'}
                  </span>
                </div>
              </div>
              
              {/* Multi-especes (optionnel) */}
              <div>
                <label className="text-xs text-slate-400 mb-1 block">
                  Ajouter d'autres especes (superposition)
                </label>
                <div className="flex flex-wrap gap-1">
                  {SPECIES.filter(s => s.id !== selectedSpecies[0]).map(({ id, label, color }) => (
                    <button
                      key={id}
                      onClick={() => {
                        const newSpecies = selectedSpecies.includes(id)
                          ? selectedSpecies.filter(s => s !== id)
                          : [...selectedSpecies, id];
                        setSelectedSpecies(newSpecies);
                        notifyChange({ species: newSpecies });
                      }}
                      className={`px-2 py-1 rounded text-xs transition-all flex items-center gap-1 ${
                        selectedSpecies.includes(id)
                          ? 'text-white border'
                          : 'bg-slate-800/50 text-slate-400 border border-slate-700'
                      }`}
                      style={{ 
                        backgroundColor: selectedSpecies.includes(id) ? `${color}30` : undefined,
                        borderColor: selectedSpecies.includes(id) ? `${color}80` : undefined 
                      }}
                    >
                      <div 
                        className="w-2 h-2 rounded-full" 
                        style={{ backgroundColor: color }}
                      />
                      {label}
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Periode */}
              <div>
                <label className="text-xs text-slate-400 mb-1 block">Periode</label>
                <div className="flex gap-1">
                  {TIME_RANGES.map(({ id, label }) => (
                    <button
                      key={id}
                      onClick={() => {
                        setTimeRange(id);
                        notifyChange({ timeRange: id });
                      }}
                      className={`px-3 py-1 rounded text-xs transition-all ${
                        timeRange === id
                          ? 'bg-cyan-600/30 text-cyan-300 border border-cyan-600/50'
                          : 'bg-slate-800/50 text-slate-400 border border-slate-700'
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Score minimum */}
              <div>
                <label className="text-xs text-slate-400 mb-1 block">
                  Score minimum: {minScore}
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={minScore}
                  onChange={(e) => {
                    const val = parseInt(e.target.value);
                    setMinScore(val);
                    notifyChange({ minScore: val });
                  }}
                  className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HotspotControlPanel;
