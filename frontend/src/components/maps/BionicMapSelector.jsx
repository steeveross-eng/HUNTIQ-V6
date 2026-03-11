/**
 * BionicMapSelector - Sélecteur de cartes premium BIONIC TACTICAL
 * BIONIC Design System compliant
 * Version: 2.0.0 - Refactoring UX liste verticale
 * 
 * Permet de choisir parmi les 7 types de cartes disponibles
 * RÈGLE: Un seul basemap actif à la fois, couches superposables au-dessus
 */

import React, { useState } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { 
  Map, ChevronDown, ChevronUp, Check, 
  Satellite, Mountain, Droplets, TreePine, Route,
  Settings
} from 'lucide-react';
import { 
  MAP_TYPES, 
  MAP_CONFIGS, 
  MAP_DISPLAY_ORDER
} from '@/config/mapSources';

// Icônes personnalisées pour chaque type de carte
const MAP_ICONS = {
  [MAP_TYPES.ECOFORESTRY]: () => <TreePine className="w-5 h-5 text-[var(--bionic-green-primary)] flex-shrink-0" />,
  [MAP_TYPES.SATELLITE]: () => <Satellite className="w-5 h-5 text-[var(--bionic-blue-light)] flex-shrink-0" />,
  [MAP_TYPES.IQHO]: () => <Droplets className="w-5 h-5 text-[var(--bionic-cyan-primary)] flex-shrink-0" />,
  [MAP_TYPES.BATHYMETRY]: () => (
    <div className="w-5 h-5 rounded bg-gradient-to-b from-[var(--bionic-cyan-primary)] to-[var(--bionic-blue-primary)] flex items-center justify-center flex-shrink-0">
      <span className="text-white text-[10px] font-bold">~</span>
    </div>
  ),
  [MAP_TYPES.FOREST_ROADS]: () => <Route className="w-5 h-5 text-[var(--bionic-gold-primary)] flex-shrink-0" />,
};

/**
 * Item de liste pour un type de carte
 */
const MapTypeListItem = ({ 
  mapType, 
  config, 
  isSelected, 
  onClick
}) => {
  const { t } = useLanguage();
  const IconComponent = MAP_ICONS[mapType];
  
  return (
    <button
      onClick={() => onClick(mapType)}
      className={`
        w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200
        ${isSelected 
          ? 'bg-[var(--bionic-gold-muted)] border border-[var(--bionic-gold-primary)]/50' 
          : 'bg-[var(--bionic-bg-hover)] border border-transparent hover:border-[var(--bionic-border-secondary)] hover:bg-[var(--bionic-bg-card)]'
        }
      `}
      data-testid={`map-type-${mapType}`}
    >
      {/* Icône */}
      <div className="flex-shrink-0">
        {IconComponent && <IconComponent />}
      </div>
      
      {/* Contenu */}
      <div className="flex-1 min-w-0 text-left">
        <div className="flex items-center gap-2">
          <span className={`
            text-sm font-medium truncate
            ${isSelected ? 'text-[var(--bionic-gold-primary)]' : 'text-[var(--bionic-text-primary)]'}
          `}>
            {config.name}
          </span>
          
          {/* Badge PRO */}
          {config.isPremium && (
            <span className="flex-shrink-0 bg-gradient-to-r from-[var(--bionic-gold-primary)] to-[var(--bionic-gold-dark)] text-[var(--bionic-bg-primary)] text-[9px] font-bold px-1.5 py-0.5 rounded uppercase">
              Pro
            </span>
          )}
        </div>
        
        {/* Description courte */}
        {config.description && (
          <p className={`
            text-[11px] truncate mt-0.5
            ${isSelected ? 'text-[var(--bionic-gold-light)]' : 'text-[var(--bionic-text-muted)]'}
          `}>
            {config.description}
          </p>
        )}
      </div>
      
      {/* Checkmark pour sélection */}
      {isSelected && (
        <div className="flex-shrink-0">
          <Check className="w-4 h-4 text-[var(--bionic-gold-primary)]" />
        </div>
      )}
    </button>
  );
};

/**
 * Composant principal du sélecteur de cartes
 */
const BionicMapSelector = ({
  currentMapType,
  onMapTypeChange,
  mapOptions = {},
  onOptionsChange,
  variant = 'panel', // 'panel' | 'dropdown' | 'compact'
  showOptions = true,
  className = ''
}) => {
  const { t } = useLanguage();
  const [isExpanded, setIsExpanded] = useState(variant === 'panel');
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);

  const currentConfig = MAP_CONFIGS[currentMapType];

  // Rendu en mode dropdown (liste déroulante)
  if (variant === 'dropdown') {
    return (
      <div className={`relative ${className}`}>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 px-3 py-2 bg-[var(--bionic-bg-card)] border border-[var(--bionic-border-primary)] rounded-lg hover:border-[var(--bionic-gold-primary)]/50 transition-colors"
          data-testid="map-selector-dropdown"
        >
          {MAP_ICONS[currentMapType] && React.createElement(MAP_ICONS[currentMapType])}
          <span className="text-[var(--bionic-text-primary)] text-sm font-medium">{currentConfig?.shortName}</span>
          <ChevronDown className={`w-4 h-4 text-[var(--bionic-text-secondary)] transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
        </button>
        
        {isExpanded && (
          <div className="absolute top-full left-0 mt-2 w-72 bg-[var(--bionic-bg-secondary)] border border-[var(--bionic-border-primary)] rounded-lg shadow-xl z-50 p-2 space-y-1">
            {MAP_DISPLAY_ORDER.map(mapType => (
              <MapTypeListItem
                key={mapType}
                mapType={mapType}
                config={MAP_CONFIGS[mapType]}
                isSelected={currentMapType === mapType}
                onClick={(type) => {
                  onMapTypeChange(type);
                  setIsExpanded(false);
                }}
              />
            ))}
          </div>
        )}
      </div>
    );
  }

  // Rendu en mode compact (barre horizontale avec icônes)
  if (variant === 'compact') {
    return (
      <div className={`flex items-center gap-1 p-1 bg-[var(--bionic-bg-card)] border border-[var(--bionic-border-primary)] rounded-lg ${className}`}>
        {MAP_DISPLAY_ORDER.map(mapType => {
          const IconComponent = MAP_ICONS[mapType];
          return (
            <button
              key={mapType}
              onClick={() => onMapTypeChange(mapType)}
              className={`
                p-2 rounded transition-all
                ${currentMapType === mapType 
                  ? 'bg-[var(--bionic-gold-muted)] border border-[var(--bionic-gold-primary)]/50' 
                  : 'hover:bg-[var(--bionic-bg-hover)]'
                }
              `}
              title={MAP_CONFIGS[mapType].name}
              data-testid={`map-compact-${mapType}`}
            >
              {IconComponent && <IconComponent />}
            </button>
          );
        })}
      </div>
    );
  }

  // Rendu en mode panel (liste verticale complète)
  return (
    <div className={`bg-[var(--bionic-bg-card)] border border-[var(--bionic-border-primary)] rounded-lg ${className}`}>
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3 border-b border-[var(--bionic-border-secondary)] hover:bg-[var(--bionic-bg-hover)] transition-colors rounded-t-lg"
      >
        <div className="flex items-center gap-2">
          <Map className="w-4 h-4 text-[var(--bionic-gold-primary)]" />
          <span className="text-[var(--bionic-text-primary)] text-sm font-semibold uppercase tracking-wider">
            {t('map_selector_title')}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[var(--bionic-gold-primary)] text-xs font-medium">
            {currentConfig?.shortName}
          </span>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-[var(--bionic-text-secondary)]" />
          ) : (
            <ChevronDown className="w-4 h-4 text-[var(--bionic-text-secondary)]" />
          )}
        </div>
      </button>

      {/* Contenu expandable - Liste verticale */}
      {isExpanded && (
        <div className="p-3 space-y-3">
          {/* Liste des types de cartes */}
          <div className="space-y-1">
            {MAP_DISPLAY_ORDER.map(mapType => (
              <MapTypeListItem
                key={mapType}
                mapType={mapType}
                config={MAP_CONFIGS[mapType]}
                isSelected={currentMapType === mapType}
                onClick={onMapTypeChange}
              />
            ))}
          </div>

          {/* Note architecture */}
          <div className="px-2 py-1.5 bg-[var(--bionic-blue-muted)] rounded border border-[var(--bionic-blue-primary)]/30">
            <p className="text-[var(--bionic-blue-light)] text-[10px]">
              {t('map_selector_basemap_note')}
            </p>
          </div>

          {/* Options */}
          {showOptions && (
            <>
              <div className="border-t border-[var(--bionic-border-secondary)] pt-3">
                <button
                  onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
                  className="flex items-center gap-2 text-[var(--bionic-text-secondary)] hover:text-[var(--bionic-text-primary)] transition-colors"
                >
                  <Settings className="w-3 h-3" />
                  <span className="text-[10px] uppercase tracking-wider">{t('map_selector_options')}</span>
                  <ChevronDown className={`w-3 h-3 transition-transform ${showAdvancedOptions ? 'rotate-180' : ''}`} />
                </button>
              </div>

              {showAdvancedOptions && (
                <div className="space-y-2 pt-2">
                  {/* Labels */}
                  <label className="flex items-center justify-between cursor-pointer group">
                    <span className="text-[var(--bionic-text-secondary)] text-[11px] group-hover:text-[var(--bionic-text-primary)] transition-colors">
                      {t('map_option_labels')}
                    </span>
                    <button
                      onClick={() => onOptionsChange?.({ showLabels: !mapOptions.showLabels })}
                      className={`w-8 h-4 rounded-full transition-colors ${
                        mapOptions.showLabels ? 'bg-[var(--bionic-gold-primary)]' : 'bg-[var(--bionic-gray-600)]'
                      }`}
                    >
                      <div className={`w-3 h-3 rounded-full bg-white shadow transition-transform ${
                        mapOptions.showLabels ? 'translate-x-4' : 'translate-x-0.5'
                      }`} />
                    </button>
                  </label>

                  {/* Coordonnées */}
                  <label className="flex items-center justify-between cursor-pointer group">
                    <span className="text-[var(--bionic-text-secondary)] text-[11px] group-hover:text-[var(--bionic-text-primary)] transition-colors">
                      {t('map_option_coordinates')}
                    </span>
                    <button
                      onClick={() => onOptionsChange?.({ showCoordinates: !mapOptions.showCoordinates })}
                      className={`w-8 h-4 rounded-full transition-colors ${
                        mapOptions.showCoordinates ? 'bg-[var(--bionic-gold-primary)]' : 'bg-[var(--bionic-gray-600)]'
                      }`}
                    >
                      <div className={`w-3 h-3 rounded-full bg-white shadow transition-transform ${
                        mapOptions.showCoordinates ? 'translate-x-4' : 'translate-x-0.5'
                      }`} />
                    </button>
                  </label>

                  {/* Auto-opacité zones */}
                  <label className="flex items-center justify-between cursor-pointer group">
                    <span className="text-[var(--bionic-text-secondary)] text-[11px] group-hover:text-[var(--bionic-text-primary)] transition-colors">
                      {t('map_option_auto_opacity')}
                    </span>
                    <button
                      onClick={() => onOptionsChange?.({ autoZoneOpacity: !mapOptions.autoZoneOpacity })}
                      className={`w-8 h-4 rounded-full transition-colors ${
                        mapOptions.autoZoneOpacity ? 'bg-[var(--bionic-gold-primary)]' : 'bg-[var(--bionic-gray-600)]'
                      }`}
                    >
                      <div className={`w-3 h-3 rounded-full bg-white shadow transition-transform ${
                        mapOptions.autoZoneOpacity ? 'translate-x-4' : 'translate-x-0.5'
                      }`} />
                    </button>
                  </label>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default BionicMapSelector;
export { MapTypeListItem, MAP_ICONS };
