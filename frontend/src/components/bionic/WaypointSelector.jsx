/**
 * WaypointSelector - Sélecteur de Waypoint BIONIC V5
 * ===================================================
 * BIONIC V5 ULTIME - PHASE 5.2
 * 
 * RESPONSABILITÉ UNIQUE:
 * - Afficher une liste de waypoints sélectionnables
 * - Permettre la sélection d'un waypoint
 * - Afficher les infos clés de chaque waypoint (nom, type, score)
 * - Composant PRÉSENTATIONNEL + interactions UI locales
 * 
 * FONCTIONNALITÉS:
 * - Liste scrollable des waypoints
 * - Recherche/filtrage local
 * - Indication visuelle du waypoint sélectionné
 * - Affichage du score et type de chaque waypoint
 * - Support des états vide et loading
 * 
 * ISOLATION:
 * - Nouveau fichier uniquement
 * - Communication via props
 * - Aucun appel API, aucun calcul métier
 * 
 * Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
 */

import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import {
  MapPin,
  Search,
  Check,
  ChevronRight,
  Loader2,
  Target,
  Camera,
  Crosshair,
  Eye,
  TreePine,
  Compass,
  Navigation,
  Map as MapIcon
} from 'lucide-react';

import { BIONIC_COLORS, getScoreColor } from '@/config/bionic-colors';

// =============================================================================
// CONSTANTS
// =============================================================================

const WAYPOINT_TYPE_CONFIG = {
  hunting: { 
    icon: Crosshair, 
    label: 'Chasse', 
    color: BIONIC_COLORS.gold.primary 
  },
  camera: { 
    icon: Camera, 
    label: 'Caméra', 
    color: BIONIC_COLORS.blue.light 
  },
  observation: { 
    icon: Eye, 
    label: 'Observation', 
    color: BIONIC_COLORS.purple.primary 
  },
  feeding: { 
    icon: TreePine, 
    label: 'Alimentation', 
    color: BIONIC_COLORS.green.primary 
  },
  blind: { 
    icon: Target, 
    label: 'Affût', 
    color: BIONIC_COLORS.red.primary 
  },
  custom: { 
    icon: MapPin, 
    label: 'Personnalisé', 
    color: BIONIC_COLORS.gray[400] 
  },
  default: { 
    icon: MapPin, 
    label: 'Waypoint', 
    color: BIONIC_COLORS.gray[400] 
  }
};

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

/**
 * Carte d'un waypoint individuel
 */
const WaypointCard = ({ 
  waypoint, 
  isSelected, 
  onSelect 
}) => {
  const typeConfig = WAYPOINT_TYPE_CONFIG[waypoint.type] || WAYPOINT_TYPE_CONFIG.default;
  const TypeIcon = typeConfig.icon;
  const scoreColor = waypoint.score !== undefined ? getScoreColor(waypoint.score) : BIONIC_COLORS.gray[500];
  
  return (
    <button
      onClick={() => onSelect(waypoint.id)}
      className={`
        w-full text-left p-3 rounded-lg transition-all duration-200
        ${isSelected 
          ? 'ring-2 ring-offset-2 ring-offset-black' 
          : 'hover:bg-white/5'
        }
      `}
      style={{ 
        backgroundColor: isSelected ? `${BIONIC_COLORS.gold.primary}15` : BIONIC_COLORS.gray[900],
        ringColor: isSelected ? BIONIC_COLORS.gold.primary : 'transparent'
      }}
    >
      <div className="flex items-start gap-3">
        {/* Icon du type */}
        <div 
          className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: `${typeConfig.color}20` }}
        >
          <TypeIcon className="w-5 h-5" style={{ color: typeConfig.color }} />
        </div>
        
        {/* Infos du waypoint */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span 
              className={`font-medium truncate ${isSelected ? 'text-white' : 'text-gray-200'}`}
            >
              {waypoint.name}
            </span>
            {isSelected && (
              <Check 
                className="w-4 h-4 flex-shrink-0" 
                style={{ color: BIONIC_COLORS.gold.primary }} 
              />
            )}
          </div>
          
          <div className="flex items-center gap-2 mt-1">
            <Badge 
              variant="outline" 
              className="text-xs px-1.5 py-0"
              style={{ 
                borderColor: typeConfig.color,
                color: typeConfig.color,
                backgroundColor: 'transparent'
              }}
            >
              {typeConfig.label}
            </Badge>
            
            {waypoint.species && (
              <span className="text-xs text-gray-500 truncate">
                {waypoint.species}
              </span>
            )}
          </div>
          
          {/* Coordonnées */}
          {(waypoint.latitude !== undefined && waypoint.longitude !== undefined) && (
            <div className="flex items-center gap-1 mt-1.5">
              <Navigation className="w-3 h-3 text-gray-500" />
              <span className="text-xs text-gray-500">
                {waypoint.latitude.toFixed(4)}, {waypoint.longitude.toFixed(4)}
              </span>
            </div>
          )}
        </div>
        
        {/* Score (si disponible) */}
        {waypoint.score !== undefined && (
          <div className="flex flex-col items-end">
            <span 
              className="text-lg font-bold"
              style={{ color: scoreColor }}
            >
              {Math.round(waypoint.score)}
            </span>
            <span className="text-xs text-gray-500">score</span>
          </div>
        )}
        
        {/* Chevron */}
        <ChevronRight 
          className="w-4 h-4 flex-shrink-0 mt-3"
          style={{ color: isSelected ? BIONIC_COLORS.gold.primary : BIONIC_COLORS.gray[600] }}
        />
      </div>
    </button>
  );
};

/**
 * État de chargement
 */
const LoadingState = () => (
  <div className="flex flex-col items-center justify-center py-12 gap-4">
    <Loader2 
      className="w-8 h-8 animate-spin" 
      style={{ color: BIONIC_COLORS.gold.primary }} 
    />
    <p className="text-sm text-gray-400">Chargement des waypoints...</p>
  </div>
);

/**
 * État vide (pas de waypoints)
 */
const EmptyState = ({ searchQuery }) => (
  <div className="flex flex-col items-center justify-center py-12 gap-4">
    <div 
      className="w-16 h-16 rounded-full flex items-center justify-center"
      style={{ backgroundColor: BIONIC_COLORS.gray[800] }}
    >
      <MapIcon className="w-8 h-8" style={{ color: BIONIC_COLORS.gray[500] }} />
    </div>
    <div className="text-center">
      {searchQuery ? (
        <>
          <p className="text-white font-medium mb-1">Aucun résultat</p>
          <p className="text-sm text-gray-400">
            Aucun waypoint ne correspond à "{searchQuery}"
          </p>
        </>
      ) : (
        <>
          <p className="text-white font-medium mb-1">Aucun waypoint disponible</p>
          <p className="text-sm text-gray-400">
            Ajoutez des waypoints à votre territoire
          </p>
        </>
      )}
    </div>
  </div>
);

/**
 * Barre de recherche
 */
const SearchBar = ({ value, onChange, resultCount }) => (
  <div className="relative">
    <Search 
      className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4"
      style={{ color: BIONIC_COLORS.gray[500] }}
    />
    <Input
      type="text"
      placeholder="Rechercher un waypoint..."
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="pl-10 pr-16 h-10 border-0"
      style={{ 
        backgroundColor: BIONIC_COLORS.gray[900],
        color: 'white'
      }}
    />
    {value && (
      <span 
        className="absolute right-3 top-1/2 -translate-y-1/2 text-xs"
        style={{ color: BIONIC_COLORS.gray[500] }}
      >
        {resultCount} résultat{resultCount !== 1 ? 's' : ''}
      </span>
    )}
  </div>
);

/**
 * Header avec compteur
 */
const SelectorHeader = ({ totalCount, selectedName }) => (
  <div className="flex items-center justify-between">
    <div className="flex items-center gap-2">
      <Compass className="w-5 h-5" style={{ color: BIONIC_COLORS.gold.primary }} />
      <span className="text-white font-medium">Waypoints</span>
      <Badge 
        variant="outline" 
        className="text-xs"
        style={{ 
          borderColor: BIONIC_COLORS.gray[700],
          color: BIONIC_COLORS.gray[400]
        }}
      >
        {totalCount}
      </Badge>
    </div>
    
    {selectedName && (
      <div className="flex items-center gap-1.5">
        <Check className="w-3.5 h-3.5" style={{ color: BIONIC_COLORS.green.primary }} />
        <span className="text-xs text-gray-400 truncate max-w-[120px]">
          {selectedName}
        </span>
      </div>
    )}
  </div>
);

// =============================================================================
// MAIN COMPONENT
// =============================================================================

/**
 * WaypointSelector
 * 
 * Sélecteur de waypoint pour l'analyse BIONIC.
 * Composant PRÉSENTATIONNEL + interactions UI locales (recherche).
 * 
 * @param {Array} waypoints - Liste des waypoints disponibles
 * @param {string} selectedWaypointId - ID du waypoint actuellement sélectionné
 * @param {function} onSelectWaypoint - Callback appelé lors de la sélection
 * @param {boolean} isLoading - État de chargement
 * @param {string} className - Classes CSS additionnelles
 */
const WaypointSelector = ({
  waypoints = [],
  selectedWaypointId = null,
  onSelectWaypoint,
  isLoading = false,
  className = ''
}) => {
  // État local pour la recherche (interaction UI locale autorisée)
  const [searchQuery, setSearchQuery] = useState('');
  
  // Filtrage des waypoints (logique UI locale, pas de calcul métier)
  const filteredWaypoints = useMemo(() => {
    if (!searchQuery.trim()) return waypoints;
    
    const query = searchQuery.toLowerCase().trim();
    return waypoints.filter(wp => 
      wp.name?.toLowerCase().includes(query) ||
      wp.type?.toLowerCase().includes(query) ||
      wp.species?.toLowerCase().includes(query)
    );
  }, [waypoints, searchQuery]);
  
  // Waypoint sélectionné
  const selectedWaypoint = waypoints.find(wp => wp.id === selectedWaypointId);
  
  // Handler de sélection
  const handleSelect = (waypointId) => {
    if (onSelectWaypoint) {
      onSelectWaypoint(waypointId);
    }
  };
  
  return (
    <Card 
      className={`border-0 overflow-hidden ${className}`}
      style={{ backgroundColor: BIONIC_COLORS.black.elevated }}
    >
      <CardHeader className="pb-3">
        <SelectorHeader 
          totalCount={waypoints.length}
          selectedName={selectedWaypoint?.name}
        />
      </CardHeader>
      
      <CardContent className="space-y-3">
        {/* Barre de recherche */}
        {waypoints.length > 0 && (
          <SearchBar 
            value={searchQuery}
            onChange={setSearchQuery}
            resultCount={filteredWaypoints.length}
          />
        )}
        
        {/* Contenu */}
        {isLoading ? (
          <LoadingState />
        ) : filteredWaypoints.length === 0 ? (
          <EmptyState searchQuery={searchQuery} />
        ) : (
          <ScrollArea className="h-[400px] pr-2">
            <div className="space-y-2">
              {filteredWaypoints.map((waypoint) => (
                <WaypointCard
                  key={waypoint.id}
                  waypoint={waypoint}
                  isSelected={waypoint.id === selectedWaypointId}
                  onSelect={handleSelect}
                />
              ))}
            </div>
          </ScrollArea>
        )}
        
        {/* Info sélection */}
        {selectedWaypoint && !isLoading && (
          <div 
            className="p-3 rounded-lg flex items-center gap-3"
            style={{ backgroundColor: `${BIONIC_COLORS.gold.primary}10` }}
          >
            <div 
              className="w-8 h-8 rounded-full flex items-center justify-center"
              style={{ backgroundColor: BIONIC_COLORS.gold.muted }}
            >
              <Target 
                className="w-4 h-4" 
                style={{ color: BIONIC_COLORS.gold.primary }} 
              />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">
                {selectedWaypoint.name}
              </p>
              <p className="text-xs text-gray-400">
                Centre de l'analyse waypoint-centric
              </p>
            </div>
            {selectedWaypoint.score !== undefined && (
              <div 
                className="text-lg font-bold"
                style={{ color: getScoreColor(selectedWaypoint.score) }}
              >
                {Math.round(selectedWaypoint.score)}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default WaypointSelector;
