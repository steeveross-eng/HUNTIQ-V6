/**
 * LayerControlPanel - Panneau de Contrôle des Layers BIONIC V5
 * =============================================================
 * BIONIC V5 ULTIME - PHASE 6 - ACTION 4
 * 
 * RESPONSABILITÉ UNIQUE:
 * - Afficher les toggles pour activer/désactiver chaque layer
 * - Organiser par familles (5 familles, sous-layers individuelles)
 * - Synchroniser l'état de visibilité avec la carte
 * - Fournir des indicateurs visuels de l'état des layers
 * 
 * STRUCTURE DES LAYERS:
 * 1. behavioral_zones: bedding, feeding, rut, movement, pressure
 * 2. attraction_points: salines, water_sources, thermal_refuges, affuts
 * 3. terrain_analysis: slopes, altitude, orientation, solar, water, soil
 * 4. vegetation_analysis: ndvi, forest_stands, edge_transitions, cover
 * 5. hunt_planning: optimal_routes, stand_positions, accessibility, trails
 * 
 * ISOLATION:
 * - Composant 100% présentationnel
 * - Aucune logique métier
 * - Données et callbacks via props uniquement
 * 
 * Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
 */

import React, { useState, useCallback, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger
} from '@/components/ui/collapsible';
import {
  Layers,
  ChevronDown,
  ChevronRight,
  Eye,
  EyeOff,
  Circle,
  MapPin,
  Mountain,
  TreePine,
  Target,
  Home,
  Utensils,
  Heart,
  Move,
  AlertTriangle,
  Droplets,
  Thermometer,
  Navigation,
  TrendingUp,
  Sun,
  CloudRain,
  Compass,
  Leaf,
  Map,
  Route,
  Crosshair,
  Footprints,
  Baby,
  Activity
} from 'lucide-react';

import { BIONIC_COLORS, ZONE_COLORS } from '@/config/bionic-colors';

// =============================================================================
// TYPES & CONSTANTS
// =============================================================================

/**
 * Configuration des familles de layers avec leurs sous-layers
 * Chaque famille et sous-layer a un ID unique pour le contrôle de visibilité
 */
const LAYER_FAMILIES = {
  behavioral_zones: {
    id: 'behavioral_zones',
    label: 'Zones Comportementales',
    icon: Circle,
    color: BIONIC_COLORS.blue.primary,
    description: 'Zones de comportement animal',
    sublayers: [
      {
        id: 'bedding_zones',
        label: 'Zones de Repos',
        icon: Home,
        color: '#1E3A8A',
        description: 'Zones de couchage et repos'
      },
      {
        id: 'feeding_zones',
        label: 'Zones d\'Alimentation',
        icon: Utensils,
        color: '#00A676',
        description: 'Zones de gagnage'
      },
      {
        id: 'rut_zones',
        label: 'Zones de Rut',
        icon: Heart,
        color: '#E91E63',
        description: 'Zones d\'activité de rut'
      },
      {
        id: 'movement_corridors',
        label: 'Corridors de Mouvement',
        icon: Move,
        color: '#C9A86A',
        description: 'Corridors de déplacement'
      },
      {
        id: 'pressure_avoidance',
        label: 'Zones d\'Évitement',
        icon: AlertTriangle,
        color: '#B91C1C',
        description: 'Zones de pression à éviter'
      }
    ]
  },
  attraction_points: {
    id: 'attraction_points',
    label: 'Points d\'Attraction',
    icon: MapPin,
    color: BIONIC_COLORS.gold.primary,
    description: 'Points d\'intérêt pour le gibier',
    sublayers: [
      {
        id: 'salines',
        label: 'Salines',
        icon: Droplets,
        color: '#FFC107',
        description: 'Salines naturelles/artificielles'
      },
      {
        id: 'water_sources',
        label: 'Sources d\'Eau',
        icon: Droplets,
        color: '#2196F3',
        description: 'Points d\'eau'
      },
      {
        id: 'thermal_refuges',
        label: 'Refuges Thermiques',
        icon: Thermometer,
        color: '#00BCD4',
        description: 'Zones de confort thermique'
      },
      {
        id: 'affuts_potentiels',
        label: 'Affûts Potentiels',
        icon: Crosshair,
        color: '#FF9800',
        description: 'Positions d\'affût suggérées'
      }
    ]
  },
  terrain_analysis: {
    id: 'terrain_analysis',
    label: 'Analyse du Terrain',
    icon: Mountain,
    color: BIONIC_COLORS.purple.primary,
    description: 'Caractéristiques topographiques',
    sublayers: [
      {
        id: 'slopes',
        label: 'Pentes',
        icon: TrendingUp,
        color: '#FF7043',
        description: 'Analyse des pentes'
      },
      {
        id: 'altitude_relative',
        label: 'Altitude',
        icon: Mountain,
        color: '#78909C',
        description: 'Altitude relative'
      },
      {
        id: 'orientation',
        label: 'Orientation',
        icon: Compass,
        color: '#3F51B5',
        description: 'Exposition du terrain'
      },
      {
        id: 'solar_exposure',
        label: 'Ensoleillement',
        icon: Sun,
        color: '#FFEB3B',
        description: 'Exposition solaire'
      },
      {
        id: 'water_proximity',
        label: 'Proximité Eau',
        icon: Droplets,
        color: '#03A9F4',
        description: 'Distance aux sources d\'eau'
      },
      {
        id: 'soil_moisture',
        label: 'Humidité du Sol',
        icon: CloudRain,
        color: '#00BCD4',
        description: 'Index d\'humidité'
      }
    ]
  },
  vegetation_analysis: {
    id: 'vegetation_analysis',
    label: 'Analyse Végétation',
    icon: TreePine,
    color: BIONIC_COLORS.green.primary,
    description: 'Couverture et types de végétation',
    sublayers: [
      {
        id: 'ndvi',
        label: 'Index NDVI',
        icon: Leaf,
        color: '#4CAF50',
        description: 'Densité végétale'
      },
      {
        id: 'forest_stands',
        label: 'Peuplements',
        icon: TreePine,
        color: '#2E7D32',
        description: 'Types de forêt'
      },
      {
        id: 'edge_transitions',
        label: 'Lisières',
        icon: Map,
        color: '#8BC34A',
        description: 'Transitions de peuplements'
      },
      {
        id: 'cover_types',
        label: 'Types de Couvert',
        icon: TreePine,
        color: '#689F38',
        description: 'Classification du couvert'
      }
    ]
  },
  hunt_planning: {
    id: 'hunt_planning',
    label: 'Planification Chasse',
    icon: Target,
    color: BIONIC_COLORS.red.primary,
    description: 'Éléments de planification tactique',
    sublayers: [
      {
        id: 'optimal_routes',
        label: 'Routes Optimales',
        icon: Route,
        color: '#E91E63',
        description: 'Itinéraires recommandés'
      },
      {
        id: 'stand_positions',
        label: 'Positions d\'Affût',
        icon: Crosshair,
        color: '#F44336',
        description: 'Emplacements recommandés'
      },
      {
        id: 'accessibility',
        label: 'Accessibilité',
        icon: Navigation,
        color: '#FF5722',
        description: 'Analyse d\'accès'
      },
      {
        id: 'trails',
        label: 'Sentiers',
        icon: Footprints,
        color: '#795548',
        description: 'Réseau de sentiers'
      }
    ]
  },
  // NIVEAU 4 — Corridors de Déplacement
  corridors: {
    id: 'corridors',
    label: 'Corridors de Déplacement',
    icon: Route,
    color: '#FF8A00',
    description: 'Corridors de déplacement NIVEAU 4',
    sublayers: [
      {
        id: 'primary',
        label: 'Corridors Principaux',
        icon: Route,
        color: '#FF8A00',
        description: 'Corridors principaux - utilisation fréquente'
      },
      {
        id: 'secondary',
        label: 'Corridors Secondaires',
        icon: Route,
        color: '#FFC04D',
        description: 'Corridors alternatifs'
      },
      {
        id: 'seasonal',
        label: 'Corridors Saisonniers',
        icon: Route,
        color: '#4DA6FF',
        description: 'Corridors liés aux saisons (rut, etc.)'
      },
      {
        id: 'thermal',
        label: 'Corridors Thermiques',
        icon: Thermometer,
        color: '#FF4D4D',
        description: 'Vers refuges thermiques'
      },
      {
        id: 'risk',
        label: 'Corridors à Risque',
        icon: AlertTriangle,
        color: '#CC0000',
        description: 'Zones à éviter - pression humaine'
      }
    ]
  },
  // PHASE C — Facteurs Saisonniers
  seasonal_factors: {
    id: 'seasonal_factors',
    label: 'Facteurs Saisonniers',
    icon: Activity,
    color: '#EC4899',
    description: 'PHASE C — Modèles saisonniers avancés',
    sublayers: [
      {
        id: 'calving_zones',
        label: 'Zones de Mise bas',
        icon: Baby,
        color: '#EC4899',
        description: 'C.1 — Zones de mise bas actives'
      },
      {
        id: 'dispersal_zones',
        label: 'Dispersion Juvénile',
        icon: Footprints,
        color: '#8B5CF6',
        description: 'C.2 — Corridors de dispersion'
      },
      {
        id: 'thermal_stress_zones',
        label: 'Stress Thermique',
        icon: Thermometer,
        color: '#EF4444',
        description: 'C.3 — Zones de stress thermique'
      },
      {
        id: 'pressure_zones',
        label: 'Pression de Chasse',
        icon: Target,
        color: '#F59E0B',
        description: 'C.4 — Pression de chasse réelle'
      }
    ]
  }
};

/**
 * État de visibilité par défaut (tout visible)
 */
const getDefaultVisibility = () => {
  const visibility = {};
  
  Object.entries(LAYER_FAMILIES).forEach(([familyId, family]) => {
    visibility[familyId] = {
      visible: true,
      sublayers: {}
    };
    
    family.sublayers.forEach(sublayer => {
      visibility[familyId].sublayers[sublayer.id] = true;
    });
  });
  
  return visibility;
};

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

/**
 * Toggle individuel pour une sous-layer
 */
const SublayerToggle = ({
  sublayer,
  isVisible,
  isParentVisible,
  onToggle,
  compact = false
}) => {
  const Icon = sublayer.icon;
  const isEffectivelyVisible = isParentVisible && isVisible;
  
  return (
    <div 
      className={`
        flex items-center justify-between py-2 px-3 rounded-lg
        transition-all duration-200
        ${isEffectivelyVisible ? 'bg-white/5' : 'bg-transparent opacity-60'}
      `}
      data-testid={`sublayer-toggle-${sublayer.id}`}
    >
      <div className="flex items-center gap-2 min-w-0 flex-1">
        {/* Indicateur de couleur */}
        <div 
          className="w-3 h-3 rounded-full flex-shrink-0 transition-opacity"
          style={{ 
            backgroundColor: sublayer.color,
            opacity: isEffectivelyVisible ? 1 : 0.4
          }}
        />
        
        {/* Icône */}
        <Icon 
          className="w-4 h-4 flex-shrink-0"
          style={{ color: isEffectivelyVisible ? sublayer.color : BIONIC_COLORS.gray[500] }}
        />
        
        {/* Label et description */}
        <div className="min-w-0 flex-1">
          <span 
            className={`text-sm block truncate ${isEffectivelyVisible ? 'text-white' : 'text-gray-500'}`}
          >
            {sublayer.label}
          </span>
          {!compact && (
            <span className="text-[10px] text-gray-500 block truncate">
              {sublayer.description}
            </span>
          )}
        </div>
      </div>
      
      {/* Toggle */}
      <Switch
        checked={isVisible}
        onCheckedChange={() => onToggle(sublayer.id)}
        disabled={!isParentVisible}
        className="flex-shrink-0 ml-2"
        data-testid={`sublayer-switch-${sublayer.id}`}
      />
    </div>
  );
};

/**
 * Section d'une famille de layers
 */
const LayerFamilySection = ({
  family,
  visibility,
  onFamilyToggle,
  onSublayerToggle,
  defaultOpen = true,
  compact = false
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const Icon = family.icon;
  const isFamilyVisible = visibility?.visible ?? true;
  
  // Compter les sous-layers visibles
  const visibleSublayerCount = useMemo(() => {
    if (!visibility?.sublayers) return 0;
    return Object.values(visibility.sublayers).filter(Boolean).length;
  }, [visibility?.sublayers]);
  
  const totalSublayers = family.sublayers.length;
  
  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <div 
        className="rounded-xl overflow-hidden transition-all"
        style={{ 
          backgroundColor: isFamilyVisible 
            ? `${family.color}10` 
            : BIONIC_COLORS.gray[900]
        }}
      >
        {/* Header de la famille */}
        <div className="flex items-center justify-between p-3">
          <CollapsibleTrigger asChild>
            <button 
              className="flex items-center gap-2 flex-1 min-w-0 text-left"
              data-testid={`family-collapse-${family.id}`}
            >
              {/* Chevron */}
              {isOpen ? (
                <ChevronDown className="w-4 h-4 text-gray-400 flex-shrink-0" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0" />
              )}
              
              {/* Icône de la famille */}
              <div 
                className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: `${family.color}25` }}
              >
                <Icon 
                  className="w-4 h-4" 
                  style={{ color: isFamilyVisible ? family.color : BIONIC_COLORS.gray[500] }}
                />
              </div>
              
              {/* Titre et compteur */}
              <div className="min-w-0 flex-1">
                <span 
                  className={`text-sm font-medium block truncate ${isFamilyVisible ? 'text-white' : 'text-gray-500'}`}
                >
                  {family.label}
                </span>
                <span className="text-[10px] text-gray-500">
                  {visibleSublayerCount}/{totalSublayers} couches actives
                </span>
              </div>
            </button>
          </CollapsibleTrigger>
          
          {/* Toggle principal de la famille */}
          <div className="flex items-center gap-2 flex-shrink-0">
            {isFamilyVisible ? (
              <Eye className="w-4 h-4 text-gray-400" />
            ) : (
              <EyeOff className="w-4 h-4 text-gray-500" />
            )}
            <Switch
              checked={isFamilyVisible}
              onCheckedChange={() => onFamilyToggle(family.id)}
              data-testid={`family-switch-${family.id}`}
            />
          </div>
        </div>
        
        {/* Contenu des sous-layers */}
        <CollapsibleContent>
          <div className="px-3 pb-3 space-y-1">
            <Separator className="mb-2" style={{ backgroundColor: BIONIC_COLORS.gray[700] }} />
            {family.sublayers.map(sublayer => (
              <SublayerToggle
                key={sublayer.id}
                sublayer={sublayer}
                isVisible={visibility?.sublayers?.[sublayer.id] ?? true}
                isParentVisible={isFamilyVisible}
                onToggle={(sublayerId) => onSublayerToggle(family.id, sublayerId)}
                compact={compact}
              />
            ))}
          </div>
        </CollapsibleContent>
      </div>
    </Collapsible>
  );
};

/**
 * Barre d'actions rapides
 */
const QuickActions = ({
  onShowAll,
  onHideAll,
  onResetDefault,
  totalVisible,
  totalLayers
}) => (
  <div className="flex items-center justify-between gap-2 p-3 rounded-lg" style={{ backgroundColor: BIONIC_COLORS.gray[900] }}>
    <div className="flex items-center gap-2">
      <Badge 
        variant="outline" 
        className="text-xs"
        style={{ 
          borderColor: BIONIC_COLORS.gold.primary,
          color: BIONIC_COLORS.gold.primary
        }}
      >
        {totalVisible}/{totalLayers} couches
      </Badge>
    </div>
    
    <div className="flex items-center gap-1">
      <Button
        variant="ghost"
        size="sm"
        onClick={onShowAll}
        className="h-7 px-2 text-xs"
        data-testid="show-all-layers-btn"
      >
        <Eye className="w-3 h-3 mr-1" />
        Tout
      </Button>
      <Button
        variant="ghost"
        size="sm"
        onClick={onHideAll}
        className="h-7 px-2 text-xs"
        data-testid="hide-all-layers-btn"
      >
        <EyeOff className="w-3 h-3 mr-1" />
        Aucun
      </Button>
      <Button
        variant="ghost"
        size="sm"
        onClick={onResetDefault}
        className="h-7 px-2 text-xs"
        data-testid="reset-layers-btn"
      >
        Défaut
      </Button>
    </div>
  </div>
);

// =============================================================================
// MAIN COMPONENT
// =============================================================================

/**
 * LayerControlPanel
 * 
 * Panneau de contrôle pour activer/désactiver les layers sur la carte BIONIC.
 * Permet le contrôle individuel de chaque famille et sous-layer.
 * Inclut le toggle de mode d'analyse (LIVE, PRE_RUT, RUT, POST_RUT).
 * 
 * @param {Object} layerVisibility - État de visibilité actuel des layers
 * @param {Function} onLayerVisibilityChange - Callback lors du changement de visibilité
 * @param {string} analysisMode - Mode d'analyse actuel ('live', 'pre_rut', 'rut', 'post_rut')
 * @param {Function} onAnalysisModeChange - Callback lors du changement de mode
 * @param {boolean} compact - Mode compact (moins de détails)
 * @param {boolean} showQuickActions - Afficher les actions rapides
 * @param {boolean} defaultAllOpen - Toutes les familles ouvertes par défaut
 * @param {string} className - Classes CSS additionnelles
 */
const LayerControlPanel = ({
  layerVisibility,
  onLayerVisibilityChange,
  analysisMode = 'rut',
  onAnalysisModeChange,
  compact = false,
  showQuickActions = true,
  defaultAllOpen = false,
  className = ''
}) => {
  // État local si non contrôlé
  const [localVisibility, setLocalVisibility] = useState(getDefaultVisibility);
  const [localMode, setLocalMode] = useState(analysisMode);
  
  // Utiliser l'état fourni ou local
  const visibility = layerVisibility ?? localVisibility;
  const setVisibility = onLayerVisibilityChange ?? setLocalVisibility;
  
  const currentMode = onAnalysisModeChange ? analysisMode : localMode;
  const setMode = onAnalysisModeChange ?? setLocalMode;
  
  // Configuration des modes biologiques
  const BIOLOGICAL_MODES = [
    { id: 'live', label: 'LIVE', color: '#22C55E', description: 'Score temps réel (contexte actuel)' },
    { id: 'pre_rut', label: 'PRÉ-RUT', color: '#F59E0B', description: 'Période pré-rut (marquage territorial)' },
    { id: 'rut', label: 'RUT', color: '#EF4444', description: 'Pic du rut (activité maximale)' },
    { id: 'post_rut', label: 'POST-RUT', color: '#8B5CF6', description: 'Post-rut (récupération, alimentation)' }
  ];
  
  // Handler pour changement de mode
  const handleModeChange = useCallback((modeId) => {
    setMode(modeId);
  }, [setMode]);
  
  // Toggle une famille entière
  const handleFamilyToggle = useCallback((familyId) => {
    setVisibility(prev => {
      const newVisibility = { ...prev };
      const currentFamily = newVisibility[familyId];
      const newVisible = !currentFamily.visible;
      
      newVisibility[familyId] = {
        ...currentFamily,
        visible: newVisible
      };
      
      return newVisibility;
    });
  }, [setVisibility]);
  
  // Toggle une sous-layer spécifique
  const handleSublayerToggle = useCallback((familyId, sublayerId) => {
    setVisibility(prev => {
      const newVisibility = { ...prev };
      const currentFamily = newVisibility[familyId];
      
      newVisibility[familyId] = {
        ...currentFamily,
        sublayers: {
          ...currentFamily.sublayers,
          [sublayerId]: !currentFamily.sublayers[sublayerId]
        }
      };
      
      return newVisibility;
    });
  }, [setVisibility]);
  
  // Afficher toutes les layers
  const handleShowAll = useCallback(() => {
    const allVisible = {};
    
    Object.entries(LAYER_FAMILIES).forEach(([familyId, family]) => {
      allVisible[familyId] = {
        visible: true,
        sublayers: {}
      };
      
      family.sublayers.forEach(sublayer => {
        allVisible[familyId].sublayers[sublayer.id] = true;
      });
    });
    
    setVisibility(allVisible);
  }, [setVisibility]);
  
  // Masquer toutes les layers
  const handleHideAll = useCallback(() => {
    const allHidden = {};
    
    Object.entries(LAYER_FAMILIES).forEach(([familyId, family]) => {
      allHidden[familyId] = {
        visible: false,
        sublayers: {}
      };
      
      family.sublayers.forEach(sublayer => {
        allHidden[familyId].sublayers[sublayer.id] = false;
      });
    });
    
    setVisibility(allHidden);
  }, [setVisibility]);
  
  // Réinitialiser par défaut
  const handleResetDefault = useCallback(() => {
    setVisibility(getDefaultVisibility());
  }, [setVisibility]);
  
  // Calculer les statistiques
  const stats = useMemo(() => {
    let totalVisible = 0;
    let totalLayers = 0;
    
    Object.entries(LAYER_FAMILIES).forEach(([familyId, family]) => {
      const familyVis = visibility[familyId];
      
      family.sublayers.forEach(sublayer => {
        totalLayers++;
        if (familyVis?.visible && familyVis?.sublayers?.[sublayer.id]) {
          totalVisible++;
        }
      });
    });
    
    return { totalVisible, totalLayers };
  }, [visibility]);
  
  // Get current mode config
  const currentModeConfig = BIOLOGICAL_MODES.find(m => m.id === currentMode) || BIOLOGICAL_MODES[2];
  
  return (
    <Card 
      className={`border-0 overflow-hidden ${className}`}
      style={{ backgroundColor: BIONIC_COLORS.black.elevated }}
      data-testid="layer-control-panel"
    >
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-white text-base">
          <Layers className="w-5 h-5" style={{ color: BIONIC_COLORS.gold.primary }} />
          Contrôle des Couches
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-3">
        {/* Sélecteur de Mode d'Analyse Biologique */}
        <div 
          className="p-3 rounded-lg"
          style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
          data-testid="analysis-mode-selector"
        >
          <div className="flex items-center gap-2 mb-2">
            <div 
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: currentModeConfig.color }}
            />
            <span className="text-sm font-medium text-white">
              Mode d'Analyse
            </span>
          </div>
          
          {/* Boutons de sélection du mode */}
          <div className="grid grid-cols-4 gap-1">
            {BIOLOGICAL_MODES.map((mode) => (
              <button
                key={mode.id}
                onClick={() => handleModeChange(mode.id)}
                className={`px-2 py-1.5 rounded text-xs font-medium transition-all ${
                  currentMode === mode.id 
                    ? 'text-white shadow-lg' 
                    : 'text-gray-400 hover:text-white'
                }`}
                style={{
                  backgroundColor: currentMode === mode.id ? mode.color : 'transparent',
                  border: `1px solid ${currentMode === mode.id ? mode.color : BIONIC_COLORS.gray[700]}`
                }}
                data-testid={`mode-btn-${mode.id}`}
              >
                {mode.label}
              </button>
            ))}
          </div>
        </div>
        
        {/* Description du mode actif */}
        <div 
          className="text-xs p-2 rounded"
          style={{ 
            backgroundColor: `${currentModeConfig.color}15`,
            color: currentModeConfig.color,
            borderLeft: `3px solid ${currentModeConfig.color}`
          }}
          data-testid="mode-description"
        >
          <strong>Mode {currentModeConfig.label}:</strong> {currentModeConfig.description}
        </div>
        
        <Separator style={{ backgroundColor: BIONIC_COLORS.gray[700] }} />
        
        {/* Actions rapides */}
        {showQuickActions && (
          <QuickActions
            onShowAll={handleShowAll}
            onHideAll={handleHideAll}
            onResetDefault={handleResetDefault}
            totalVisible={stats.totalVisible}
            totalLayers={stats.totalLayers}
          />
        )}
        
        {/* Familles de layers */}
        <div className="space-y-2">
          {Object.entries(LAYER_FAMILIES).map(([familyId, family], index) => (
            <LayerFamilySection
              key={familyId}
              family={family}
              visibility={visibility[familyId]}
              onFamilyToggle={handleFamilyToggle}
              onSublayerToggle={handleSublayerToggle}
              defaultOpen={defaultAllOpen || index === 0}
              compact={compact}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// =============================================================================
// EXPORTS
// =============================================================================

export default LayerControlPanel;

// Export des constantes et utilitaires pour réutilisation
export { 
  LAYER_FAMILIES, 
  getDefaultVisibility 
};
