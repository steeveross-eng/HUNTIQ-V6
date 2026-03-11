/**
 * HotspotListPanel - Panneau de Liste des Hotspots avec Tri/Filtrage
 * ===================================================================
 * BIONIC V5 ULTIME - PHASE 5.5
 * 
 * RESPONSABILITÉ UNIQUE:
 * - Afficher la liste des hotspots avec tri et filtrage
 * - Interactions UI locales (tri, filtres, recherche)
 * - Communication avec la carte via callbacks
 * 
 * FONCTIONNALITÉS:
 * - Liste des hotspots (notation sur 10)
 * - Tri dynamique (score, distance, habitat, pression, risques)
 * - Filtres intelligents (qualité, légalité, habitat, risques)
 * - Highlight du hotspot sélectionné
 * - ScrollArea premium
 * 
 * ISOLATION:
 * - Composant 100% présentationnel + interactions UI locales
 * - Aucune logique métier, aucun calcul de score
 * - Données via props uniquement
 * 
 * Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
 */

import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel
} from '@/components/ui/dropdown-menu';
import {
  MapPin,
  Search,
  SortAsc,
  SortDesc,
  Filter,
  Check,
  ChevronRight,
  Target,
  Navigation,
  Trees,
  Users,
  Shield,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  List,
  X
} from 'lucide-react';

import { BIONIC_COLORS, getScoreColor } from '@/config/bionic-colors';

// =============================================================================
// CONSTANTS
// =============================================================================

const SORT_OPTIONS = [
  { key: 'score', label: 'Score', icon: Target, desc: true },
  { key: 'distance', label: 'Distance', icon: Navigation, desc: false },
  { key: 'habitat', label: 'Habitat', icon: Trees, desc: true },
  { key: 'pressure', label: 'Pression', icon: Users, desc: true },
  { key: 'risk', label: 'Risques', icon: Shield, desc: true }
];

const QUALITY_FILTERS = [
  { key: 'favorable', label: 'Favorable', color: BIONIC_COLORS.green.primary },
  { key: 'moderate', label: 'Modéré', color: BIONIC_COLORS.gold.primary },
  { key: 'unfavorable', label: 'Défavorable', color: BIONIC_COLORS.red.primary }
];

const HABITAT_FILTERS = [
  { key: 'forest', label: 'Forêt' },
  { key: 'clearing', label: 'Clairière' },
  { key: 'edge', label: 'Lisière' },
  { key: 'wetland', label: 'Zone humide' },
  { key: 'mixed', label: 'Mixte' }
];

const RISK_FILTERS = [
  { key: 'low', label: 'Faible', color: BIONIC_COLORS.green.primary },
  { key: 'moderate', label: 'Modéré', color: BIONIC_COLORS.gold.primary },
  { key: 'high', label: 'Élevé', color: BIONIC_COLORS.red.primary }
];

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

/**
 * Barre de recherche
 */
const SearchBar = ({ value, onChange }) => (
  <div className="relative">
    <Search 
      className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4"
      style={{ color: BIONIC_COLORS.gray[500] }}
    />
    <Input
      type="text"
      placeholder="Rechercher un hotspot..."
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="pl-10 h-9 border-0 text-sm"
      style={{ 
        backgroundColor: BIONIC_COLORS.gray[900],
        color: 'white'
      }}
    />
    {value && (
      <button
        onClick={() => onChange('')}
        className="absolute right-3 top-1/2 -translate-y-1/2"
      >
        <X className="w-3.5 h-3.5 text-gray-500 hover:text-white" />
      </button>
    )}
  </div>
);

/**
 * Sélecteur de tri
 */
const SortSelector = ({ sortBy, sortDesc, onSortChange }) => {
  const currentSort = SORT_OPTIONS.find(s => s.key === sortBy) || SORT_OPTIONS[0];
  const SortIcon = currentSort.icon;
  
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="outline" 
          size="sm"
          className="h-9 border-0 gap-2"
          style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
        >
          <SortIcon className="w-4 h-4" style={{ color: BIONIC_COLORS.gold.primary }} />
          <span className="text-sm text-gray-300">{currentSort.label}</span>
          {sortDesc ? (
            <SortDesc className="w-3.5 h-3.5 text-gray-500" />
          ) : (
            <SortAsc className="w-3.5 h-3.5 text-gray-500" />
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent 
        align="end"
        style={{ backgroundColor: BIONIC_COLORS.black.elevated }}
      >
        <DropdownMenuLabel className="text-gray-400">Trier par</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {SORT_OPTIONS.map(option => {
          const Icon = option.icon;
          const isActive = sortBy === option.key;
          return (
            <DropdownMenuItem 
              key={option.key}
              onClick={() => onSortChange(option.key, isActive ? !sortDesc : option.desc)}
              className="gap-2"
            >
              <Icon className="w-4 h-4" style={{ color: isActive ? BIONIC_COLORS.gold.primary : BIONIC_COLORS.gray[500] }} />
              <span className={isActive ? 'text-white' : 'text-gray-400'}>{option.label}</span>
              {isActive && (
                <Check className="w-3.5 h-3.5 ml-auto" style={{ color: BIONIC_COLORS.gold.primary }} />
              )}
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

/**
 * Panneau de filtres
 */
const FilterPanel = ({ filters, onFilterChange }) => {
  const activeFiltersCount = 
    filters.qualities.length + 
    filters.habitats.length + 
    filters.risks.length + 
    (filters.legalOnly ? 1 : 0);
  
  const toggleFilter = (category, value) => {
    const current = filters[category];
    const newValues = current.includes(value)
      ? current.filter(v => v !== value)
      : [...current, value];
    onFilterChange({ ...filters, [category]: newValues });
  };
  
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="outline" 
          size="sm"
          className="h-9 border-0 gap-2"
          style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
        >
          <Filter className="w-4 h-4" style={{ color: BIONIC_COLORS.gold.primary }} />
          <span className="text-sm text-gray-300">Filtres</span>
          {activeFiltersCount > 0 && (
            <Badge 
              className="h-5 px-1.5 text-xs"
              style={{ backgroundColor: BIONIC_COLORS.gold.primary, color: BIONIC_COLORS.black.base }}
            >
              {activeFiltersCount}
            </Badge>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent 
        align="end"
        className="w-56"
        style={{ backgroundColor: BIONIC_COLORS.black.elevated }}
      >
        {/* Qualité */}
        <DropdownMenuLabel className="text-gray-400">Qualité</DropdownMenuLabel>
        {QUALITY_FILTERS.map(option => (
          <DropdownMenuItem 
            key={option.key}
            onClick={() => toggleFilter('qualities', option.key)}
            className="gap-2"
          >
            <div 
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: option.color }}
            />
            <span className="text-gray-300">{option.label}</span>
            {filters.qualities.includes(option.key) && (
              <Check className="w-3.5 h-3.5 ml-auto" style={{ color: BIONIC_COLORS.gold.primary }} />
            )}
          </DropdownMenuItem>
        ))}
        
        <DropdownMenuSeparator />
        
        {/* Légalité */}
        <DropdownMenuLabel className="text-gray-400">Légalité</DropdownMenuLabel>
        <DropdownMenuItem 
          onClick={() => onFilterChange({ ...filters, legalOnly: !filters.legalOnly })}
          className="gap-2"
        >
          <Clock className="w-4 h-4" style={{ color: BIONIC_COLORS.green.primary }} />
          <span className="text-gray-300">Heures légales uniquement</span>
          {filters.legalOnly && (
            <Check className="w-3.5 h-3.5 ml-auto" style={{ color: BIONIC_COLORS.gold.primary }} />
          )}
        </DropdownMenuItem>
        
        <DropdownMenuSeparator />
        
        {/* Habitat */}
        <DropdownMenuLabel className="text-gray-400">Habitat</DropdownMenuLabel>
        {HABITAT_FILTERS.map(option => (
          <DropdownMenuItem 
            key={option.key}
            onClick={() => toggleFilter('habitats', option.key)}
            className="gap-2"
          >
            <Trees className="w-4 h-4 text-gray-500" />
            <span className="text-gray-300">{option.label}</span>
            {filters.habitats.includes(option.key) && (
              <Check className="w-3.5 h-3.5 ml-auto" style={{ color: BIONIC_COLORS.gold.primary }} />
            )}
          </DropdownMenuItem>
        ))}
        
        <DropdownMenuSeparator />
        
        {/* Risques */}
        <DropdownMenuLabel className="text-gray-400">Niveau de risque</DropdownMenuLabel>
        {RISK_FILTERS.map(option => (
          <DropdownMenuItem 
            key={option.key}
            onClick={() => toggleFilter('risks', option.key)}
            className="gap-2"
          >
            <Shield className="w-4 h-4" style={{ color: option.color }} />
            <span className="text-gray-300">{option.label}</span>
            {filters.risks.includes(option.key) && (
              <Check className="w-3.5 h-3.5 ml-auto" style={{ color: BIONIC_COLORS.gold.primary }} />
            )}
          </DropdownMenuItem>
        ))}
        
        {/* Reset */}
        {activeFiltersCount > 0 && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuItem 
              onClick={() => onFilterChange({ qualities: [], habitats: [], risks: [], legalOnly: false })}
              className="text-red-400"
            >
              <X className="w-4 h-4 mr-2" />
              Réinitialiser les filtres
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

/**
 * Badges de filtres actifs
 */
const ActiveFilterBadges = ({ filters, onRemoveFilter }) => {
  const badges = [];
  
  filters.qualities.forEach(q => {
    const config = QUALITY_FILTERS.find(f => f.key === q);
    if (config) {
      badges.push({
        key: `quality-${q}`,
        label: config.label,
        color: config.color,
        onRemove: () => onRemoveFilter('qualities', q)
      });
    }
  });
  
  filters.habitats.forEach(h => {
    const config = HABITAT_FILTERS.find(f => f.key === h);
    if (config) {
      badges.push({
        key: `habitat-${h}`,
        label: config.label,
        color: BIONIC_COLORS.blue.light,
        onRemove: () => onRemoveFilter('habitats', h)
      });
    }
  });
  
  filters.risks.forEach(r => {
    const config = RISK_FILTERS.find(f => f.key === r);
    if (config) {
      badges.push({
        key: `risk-${r}`,
        label: `Risque ${config.label}`,
        color: config.color,
        onRemove: () => onRemoveFilter('risks', r)
      });
    }
  });
  
  if (filters.legalOnly) {
    badges.push({
      key: 'legal',
      label: 'Légal uniquement',
      color: BIONIC_COLORS.green.primary,
      onRemove: () => onRemoveFilter('legalOnly', true)
    });
  }
  
  if (badges.length === 0) return null;
  
  return (
    <div className="flex flex-wrap gap-1.5 px-1">
      {badges.map(badge => (
        <button
          key={badge.key}
          onClick={badge.onRemove}
          className="flex items-center gap-1 px-2 py-0.5 rounded text-xs group"
          style={{ backgroundColor: `${badge.color}20` }}
        >
          <span style={{ color: badge.color }}>{badge.label}</span>
          <X className="w-3 h-3 opacity-50 group-hover:opacity-100" style={{ color: badge.color }} />
        </button>
      ))}
    </div>
  );
};

/**
 * Carte de hotspot dans la liste
 */
const HotspotCard = ({ hotspot, isSelected, onClick, onHover }) => {
  const score10 = Math.round(hotspot.score / 10);
  const scoreColor = getScoreColor(hotspot.score);
  
  const qualityConfig = {
    favorable: { color: BIONIC_COLORS.green.primary },
    moderate: { color: BIONIC_COLORS.gold.primary },
    unfavorable: { color: BIONIC_COLORS.red.primary }
  }[hotspot.quality] || { color: BIONIC_COLORS.gray[500] };
  
  return (
    <button
      onClick={() => onClick(hotspot)}
      onMouseEnter={() => onHover?.(hotspot)}
      onMouseLeave={() => onHover?.(null)}
      className={`
        w-full text-left p-3 rounded-lg transition-all duration-200
        ${isSelected ? 'ring-2 ring-offset-2 ring-offset-black' : 'hover:bg-white/5'}
      `}
      style={{ 
        backgroundColor: isSelected ? `${BIONIC_COLORS.gold.primary}15` : BIONIC_COLORS.gray[900],
        ringColor: isSelected ? BIONIC_COLORS.gold.primary : 'transparent'
      }}
    >
      <div className="flex items-start gap-3">
        {/* Score */}
        <div 
          className="w-10 h-10 rounded-lg flex flex-col items-center justify-center flex-shrink-0"
          style={{ backgroundColor: `${scoreColor}20` }}
        >
          <span 
            className="text-sm font-bold leading-none"
            style={{ color: scoreColor }}
          >
            {score10}
          </span>
          <span className="text-[10px] text-gray-500">/10</span>
        </div>
        
        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-white truncate">
              {hotspot.name}
            </span>
            {isSelected && (
              <Check className="w-3.5 h-3.5 flex-shrink-0" style={{ color: BIONIC_COLORS.gold.primary }} />
            )}
          </div>
          
          <div className="flex items-center gap-3 mt-1">
            {/* Distance */}
            <div className="flex items-center gap-1">
              <Navigation className="w-3 h-3 text-gray-500" />
              <span className="text-xs text-gray-400">{hotspot.distance?.toFixed(1)} km</span>
            </div>
            
            {/* Direction */}
            <span className="text-xs text-gray-500">{hotspot.direction}</span>
            
            {/* Légalité */}
            {hotspot.isLegal !== undefined && (
              hotspot.isLegal ? (
                <CheckCircle className="w-3 h-3" style={{ color: BIONIC_COLORS.green.primary }} />
              ) : (
                <XCircle className="w-3 h-3" style={{ color: BIONIC_COLORS.red.primary }} />
              )
            )}
          </div>
          
          {/* Tags */}
          <div className="flex items-center gap-1.5 mt-1.5">
            {/* Habitat */}
            <Badge 
              variant="outline" 
              className="text-[10px] px-1.5 py-0 h-4"
              style={{ borderColor: BIONIC_COLORS.gray[700], color: BIONIC_COLORS.gray[400] }}
            >
              {hotspot.habitat || 'N/A'}
            </Badge>
            
            {/* Qualité indicator */}
            <div 
              className="w-1.5 h-1.5 rounded-full"
              style={{ backgroundColor: qualityConfig.color }}
            />
          </div>
        </div>
        
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
 * État vide
 */
const EmptyState = ({ hasFilters }) => (
  <div className="flex flex-col items-center justify-center py-12 gap-3">
    <div 
      className="w-12 h-12 rounded-full flex items-center justify-center"
      style={{ backgroundColor: BIONIC_COLORS.gray[800] }}
    >
      <MapPin className="w-6 h-6" style={{ color: BIONIC_COLORS.gray[500] }} />
    </div>
    <div className="text-center">
      <p className="text-sm text-white font-medium">
        {hasFilters ? 'Aucun résultat' : 'Aucun hotspot'}
      </p>
      <p className="text-xs text-gray-500">
        {hasFilters 
          ? 'Modifiez vos filtres pour voir plus de résultats'
          : 'Aucun hotspot disponible dans cette zone'
        }
      </p>
    </div>
  </div>
);

/**
 * État de chargement
 */
const LoadingState = () => (
  <div className="flex flex-col items-center justify-center py-12 gap-3">
    <Loader2 className="w-6 h-6 animate-spin" style={{ color: BIONIC_COLORS.gold.primary }} />
    <p className="text-sm text-gray-400">Chargement des hotspots...</p>
  </div>
);

// =============================================================================
// MAIN COMPONENT
// =============================================================================

/**
 * HotspotListPanel
 * 
 * Panneau de liste des hotspots avec tri et filtrage intelligent.
 * Interactions UI locales (tri, filtres, recherche).
 * 
 * @param {Array} hotspots - Liste des hotspots
 * @param {string} selectedHotspotId - ID du hotspot sélectionné
 * @param {function} onSelectHotspot - Callback de sélection
 * @param {function} onHoverHotspot - Callback de survol (pour la carte)
 * @param {boolean} isLoading - État de chargement
 * @param {string} className - Classes CSS additionnelles
 */
const HotspotListPanel = ({
  hotspots = [],
  selectedHotspotId = null,
  onSelectHotspot,
  onHoverHotspot,
  isLoading = false,
  className = ''
}) => {
  // États locaux pour le tri, les filtres et la recherche
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('score');
  const [sortDesc, setSortDesc] = useState(true);
  const [filters, setFilters] = useState({
    qualities: [],
    habitats: [],
    risks: [],
    legalOnly: false
  });
  
  // Filtrage et tri des hotspots
  const filteredAndSortedHotspots = useMemo(() => {
    let result = [...hotspots];
    
    // Recherche
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(h => 
        h.name?.toLowerCase().includes(query) ||
        h.habitat?.toLowerCase().includes(query)
      );
    }
    
    // Filtres de qualité
    if (filters.qualities.length > 0) {
      result = result.filter(h => filters.qualities.includes(h.quality));
    }
    
    // Filtres d'habitat
    if (filters.habitats.length > 0) {
      result = result.filter(h => filters.habitats.includes(h.habitat));
    }
    
    // Filtres de risque
    if (filters.risks.length > 0) {
      result = result.filter(h => filters.risks.includes(h.riskLevel));
    }
    
    // Filtre légalité
    if (filters.legalOnly) {
      result = result.filter(h => h.isLegal !== false);
    }
    
    // Tri
    result.sort((a, b) => {
      let valueA, valueB;
      
      switch (sortBy) {
        case 'score':
          valueA = a.score || 0;
          valueB = b.score || 0;
          break;
        case 'distance':
          valueA = a.distance || 0;
          valueB = b.distance || 0;
          break;
        case 'habitat':
          valueA = a.habitatCoverage || 0;
          valueB = b.habitatCoverage || 0;
          break;
        case 'pressure':
          valueA = a.pressureScore || 0;
          valueB = b.pressureScore || 0;
          break;
        case 'risk':
          const riskOrder = { low: 3, moderate: 2, high: 1, critical: 0 };
          valueA = riskOrder[a.riskLevel] ?? 2;
          valueB = riskOrder[b.riskLevel] ?? 2;
          break;
        default:
          valueA = 0;
          valueB = 0;
      }
      
      return sortDesc ? valueB - valueA : valueA - valueB;
    });
    
    return result;
  }, [hotspots, searchQuery, sortBy, sortDesc, filters]);
  
  // Gestion des filtres
  const handleSortChange = (key, desc) => {
    setSortBy(key);
    setSortDesc(desc);
  };
  
  const handleRemoveFilter = (category, value) => {
    if (category === 'legalOnly') {
      setFilters({ ...filters, legalOnly: false });
    } else {
      setFilters({
        ...filters,
        [category]: filters[category].filter(v => v !== value)
      });
    }
  };
  
  const hasActiveFilters = 
    filters.qualities.length > 0 || 
    filters.habitats.length > 0 || 
    filters.risks.length > 0 || 
    filters.legalOnly;
  
  return (
    <Card 
      className={`border-0 overflow-hidden ${className}`}
      style={{ backgroundColor: BIONIC_COLORS.black.elevated }}
    >
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-white text-base">
            <List className="w-5 h-5" style={{ color: BIONIC_COLORS.gold.primary }} />
            Hotspots
            <Badge 
              variant="outline" 
              className="text-xs ml-1"
              style={{ borderColor: BIONIC_COLORS.gray[700], color: BIONIC_COLORS.gray[400] }}
            >
              {filteredAndSortedHotspots.length}
            </Badge>
          </CardTitle>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-3 pt-0">
        {/* Barre de recherche */}
        <SearchBar value={searchQuery} onChange={setSearchQuery} />
        
        {/* Contrôles de tri et filtrage */}
        <div className="flex items-center gap-2">
          <SortSelector 
            sortBy={sortBy}
            sortDesc={sortDesc}
            onSortChange={handleSortChange}
          />
          <FilterPanel 
            filters={filters}
            onFilterChange={setFilters}
          />
        </div>
        
        {/* Badges des filtres actifs */}
        <ActiveFilterBadges 
          filters={filters}
          onRemoveFilter={handleRemoveFilter}
        />
        
        <Separator style={{ backgroundColor: BIONIC_COLORS.gray[800] }} />
        
        {/* Liste des hotspots */}
        {isLoading ? (
          <LoadingState />
        ) : filteredAndSortedHotspots.length === 0 ? (
          <EmptyState hasFilters={hasActiveFilters || searchQuery.length > 0} />
        ) : (
          <ScrollArea className="h-[400px] pr-2">
            <div className="space-y-2">
              {filteredAndSortedHotspots.map(hotspot => (
                <HotspotCard
                  key={hotspot.id}
                  hotspot={hotspot}
                  isSelected={hotspot.id === selectedHotspotId}
                  onClick={onSelectHotspot}
                  onHover={onHoverHotspot}
                />
              ))}
            </div>
          </ScrollArea>
        )}
        
        {/* Résumé */}
        {!isLoading && filteredAndSortedHotspots.length > 0 && (
          <div 
            className="text-center py-2 rounded"
            style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
          >
            <p className="text-xs text-gray-500">
              {filteredAndSortedHotspots.length} hotspot{filteredAndSortedHotspots.length > 1 ? 's' : ''} 
              {hasActiveFilters ? ' (filtré)' : ''} 
              {' '} trié par {SORT_OPTIONS.find(s => s.key === sortBy)?.label.toLowerCase()}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default HotspotListPanel;
