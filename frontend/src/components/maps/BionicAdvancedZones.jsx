/**
 * BionicAdvancedZones.jsx
 * 
 * Rendu des 14 types de zones avancées BIONIC sur la carte
 * - Zones comportementales (4): Rut, Repos, Alimentation, Corridor
 * - Zones environnementales (6): Soleil, Pente, Hydro, Forêt, Thermique, Habitat
 * - Zones stratégiques (4): Affût, Hotspot, Pression, Accès
 * 
 * Version: 1.1.0 - BIONIC Design System Compliance
 * 
 * Caractéristiques:
 * - Polygones colorés avec opacité adaptative selon le type de carte
 * - Contours nets et précis
 * - Hiérarchie visuelle claire
 * - Compatible avec les 7 cartes premium
 * - Icônes Lucide via iconName property
 */

import React, { useMemo, useCallback } from 'react';
import { Polygon, Circle, Polyline, LayerGroup, Tooltip } from 'react-leaflet';

// ==================================================
// CONFIGURATION DES 14 ZONES BIONIC - DESIGN SYSTEM
// ==================================================

export const ZONE_CONFIG = {
  // ============================================
  // ZONES COMPORTEMENTALES (4)
  // ============================================
  rut: {
    id: 'rut',
    name: 'Zone de Rut',
    nameEn: 'Rut Zone',
    category: 'behavioral',
    color: '#FF4D6D',
    iconName: 'heart',
    priority: 1, // Plus haute priorité d'affichage
    description: 'Zone d\'activité reproductrice',
    descriptionEn: 'Breeding activity zone'
  },
  repos: {
    id: 'repos',
    name: 'Zone de Repos',
    nameEn: 'Rest Zone',
    category: 'behavioral',
    color: '#8B5CF6',
    iconName: 'moon',
    priority: 2,
    description: 'Zone de couche et remise',
    descriptionEn: 'Bedding and resting area'
  },
  alimentation: {
    id: 'alimentation',
    name: 'Zone d\'Alimentation',
    nameEn: 'Feeding Zone',
    category: 'behavioral',
    color: '#22C55E',
    iconName: 'leaf',
    priority: 3,
    description: 'Zone de gagnage',
    descriptionEn: 'Feeding area'
  },
  corridor: {
    id: 'corridor',
    name: 'Corridor Faunique',
    nameEn: 'Wildlife Corridor',
    category: 'behavioral',
    color: '#06B6D4',
    iconName: 'route',
    priority: 4,
    description: 'Passage régulier',
    descriptionEn: 'Regular travel route'
  },

  // ============================================
  // ZONES ENVIRONNEMENTALES (6)
  // ============================================
  habitat: {
    id: 'habitat',
    name: 'Habitat Optimal',
    nameEn: 'Optimal Habitat',
    category: 'environmental',
    color: '#10B981',
    iconName: 'trees',
    priority: 5,
    description: 'Zone de refuge idéale',
    descriptionEn: 'Ideal refuge area'
  },
  soleil: {
    id: 'soleil',
    name: 'Ensoleillement',
    nameEn: 'Sun Exposure',
    category: 'environmental',
    color: '#FCD34D',
    iconName: 'sun',
    priority: 10,
    description: 'Zone d\'exposition solaire',
    descriptionEn: 'Solar exposure zone'
  },
  pente: {
    id: 'pente',
    name: 'Orientation/Pentes',
    nameEn: 'Slope/Orientation',
    category: 'environmental',
    color: '#A78BFA',
    iconName: 'mountain',
    priority: 11,
    description: 'Relief et orientation',
    descriptionEn: 'Terrain relief'
  },
  hydro: {
    id: 'hydro',
    name: 'Hydrographie',
    nameEn: 'Hydrography',
    category: 'environmental',
    color: '#3B82F6',
    iconName: 'droplet',
    priority: 9,
    description: 'Points d\'eau',
    descriptionEn: 'Water sources'
  },
  foret: {
    id: 'foret',
    name: 'Couvert Forestier',
    nameEn: 'Forest Cover',
    category: 'environmental',
    color: '#15803D',
    iconName: 'tree-pine',
    priority: 12,
    description: 'Densité forestière',
    descriptionEn: 'Forest density'
  },
  thermique: {
    id: 'thermique',
    name: 'Zone Thermique',
    nameEn: 'Thermal Zone',
    category: 'environmental',
    color: '#EF4444',
    iconName: 'thermometer',
    priority: 8,
    description: 'Température favorable',
    descriptionEn: 'Favorable temperature'
  },

  // ============================================
  // ZONES STRATÉGIQUES (4)
  // ============================================
  affut: {
    id: 'affut',
    name: 'Affût Potentiel',
    nameEn: 'Potential Stand',
    category: 'strategic',
    color: '#F5A623',
    iconName: 'target',
    priority: 6,
    description: 'Position stratégique',
    descriptionEn: 'Strategic position'
  },
  hotspot: {
    id: 'hotspot',
    name: 'Point Chaud',
    nameEn: 'Hotspot',
    category: 'strategic',
    color: '#FF6B6B',
    iconName: 'flame',
    priority: 7,
    description: 'Activité très élevée',
    descriptionEn: 'Very high activity'
  },
  pression: {
    id: 'pression',
    name: 'Zone de Pression',
    nameEn: 'Pressure Zone',
    category: 'strategic',
    color: '#F97316',
    iconName: 'alert-triangle',
    priority: 13,
    description: 'Pression de chasse',
    descriptionEn: 'Hunting pressure'
  },
  acces: {
    id: 'acces',
    name: 'Point d\'Accès',
    nameEn: 'Access Point',
    category: 'strategic',
    color: '#8B5CF6',
    iconName: 'footprints',
    priority: 14,
    description: 'Accès au territoire',
    descriptionEn: 'Territory access'
  }
};

// ==================================================
// OPACITÉ ADAPTATIVE PAR TYPE DE CARTE
// ==================================================

/**
 * Obtenir l'opacité de remplissage selon le type de carte
 * Les cartes sombres nécessitent une opacité plus élevée
 */
export const getAdaptiveOpacity = (mapType, zoneCategory) => {
  // Cartes sombres (opacité plus élevée pour visibilité)
  const darkMaps = ['iqho', 'bathymetry'];
  const isDarkMap = darkMaps.includes(mapType);
  
  // Opacités de base par catégorie
  const baseOpacities = {
    behavioral: isDarkMap ? 0.40 : 0.30,
    environmental: isDarkMap ? 0.30 : 0.20,
    strategic: isDarkMap ? 0.45 : 0.35
  };
  
  return baseOpacities[zoneCategory] || (isDarkMap ? 0.35 : 0.25);
};

/**
 * Obtenir l'épaisseur de contour selon le type de carte
 */
export const getAdaptiveStrokeWeight = (mapType, zoneCategory) => {
  const baseWeights = {
    behavioral: 2.5,
    environmental: 2,
    strategic: 3
  };
  
  return baseWeights[zoneCategory] || 2;
};

// ==================================================
// COMPOSANTS DE RENDU DES ZONES
// ==================================================

/**
 * Rendu d'une zone polygonale
 */
const ZonePolygon = ({
  zone,
  coordinates,
  mapType,
  opacity: customOpacity,
  showTooltip = true,
  language = 'fr',
  onClick
}) => {
  const config = ZONE_CONFIG[zone.type] || {};
  
  const fillOpacity = customOpacity || getAdaptiveOpacity(mapType, config.category);
  const strokeWeight = getAdaptiveStrokeWeight(mapType, config.category);
  
  const pathOptions = useMemo(() => ({
    fillColor: config.color || '#888888',
    fillOpacity: fillOpacity,
    color: config.color || '#888888',
    weight: strokeWeight,
    opacity: 1,
    dashArray: zone.confirmed === false ? '5,5' : null // Tirets si non confirmé
  }), [config.color, fillOpacity, strokeWeight, zone.confirmed]);
  
  const tooltipContent = useMemo(() => {
    const name = language === 'fr' ? config.name : config.nameEn;
    const desc = language === 'fr' ? config.description : config.descriptionEn;
    return (
      <div className="text-xs">
        <div className="font-bold flex items-center gap-1">
          <span>{config.icon}</span>
          <span>{name}</span>
        </div>
        <div className="text-gray-400">{desc}</div>
        {zone.score && (
          <div className="mt-1 text-[#F5A623] font-medium">
            Score: {zone.score}%
          </div>
        )}
      </div>
    );
  }, [config, language, zone.score]);
  
  if (!coordinates || coordinates.length < 3) return null;
  
  return (
    <Polygon
      positions={coordinates}
      pathOptions={pathOptions}
      eventHandlers={{
        click: () => onClick?.(zone)
      }}
    >
      {showTooltip && (
        <Tooltip sticky>
          {tooltipContent}
        </Tooltip>
      )}
    </Polygon>
  );
};

/**
 * Rendu d'une zone circulaire (pour hotspots, affûts)
 */
const ZoneCircle = ({
  zone,
  center,
  radius,
  mapType,
  opacity: customOpacity,
  showTooltip = true,
  language = 'fr',
  onClick
}) => {
  const config = ZONE_CONFIG[zone.type] || {};
  
  const fillOpacity = customOpacity || getAdaptiveOpacity(mapType, config.category);
  const strokeWeight = getAdaptiveStrokeWeight(mapType, config.category);
  
  const pathOptions = useMemo(() => ({
    fillColor: config.color || '#888888',
    fillOpacity: fillOpacity,
    color: config.color || '#888888',
    weight: strokeWeight,
    opacity: 1
  }), [config.color, fillOpacity, strokeWeight]);
  
  if (!center) return null;
  
  return (
    <Circle
      center={center}
      radius={radius || 100}
      pathOptions={pathOptions}
      eventHandlers={{
        click: () => onClick?.(zone)
      }}
    >
      {showTooltip && (
        <Tooltip sticky>
          <div className="text-xs">
            <div className="font-bold flex items-center gap-1">
              <span>{config.icon}</span>
              <span>{language === 'fr' ? config.name : config.nameEn}</span>
            </div>
            {zone.score && (
              <div className="text-[#F5A623] font-medium">
                Score: {zone.score}%
              </div>
            )}
          </div>
        </Tooltip>
      )}
    </Circle>
  );
};

/**
 * Rendu d'un corridor (polyline avec buffer visuel)
 */
const ZoneCorridor = ({
  zone,
  coordinates,
  width = 50,
  mapType,
  opacity: customOpacity,
  showTooltip = true,
  language = 'fr',
  onClick
}) => {
  const config = ZONE_CONFIG.corridor;
  
  const fillOpacity = customOpacity || getAdaptiveOpacity(mapType, 'behavioral');
  
  const pathOptions = useMemo(() => ({
    color: config.color,
    weight: Math.max(4, width / 10),
    opacity: fillOpacity + 0.3,
    lineCap: 'round',
    lineJoin: 'round'
  }), [config.color, fillOpacity, width]);
  
  // Ligne de bordure plus large pour effet de buffer
  const bufferOptions = useMemo(() => ({
    color: config.color,
    weight: Math.max(8, width / 5),
    opacity: fillOpacity * 0.5,
    lineCap: 'round',
    lineJoin: 'round'
  }), [config.color, fillOpacity, width]);
  
  if (!coordinates || coordinates.length < 2) return null;
  
  return (
    <>
      {/* Buffer externe */}
      <Polyline
        positions={coordinates}
        pathOptions={bufferOptions}
      />
      {/* Ligne centrale */}
      <Polyline
        positions={coordinates}
        pathOptions={pathOptions}
        eventHandlers={{
          click: () => onClick?.(zone)
        }}
      >
        {showTooltip && (
          <Tooltip sticky>
            <div className="text-xs">
              <div className="font-bold flex items-center gap-1">
                <span>{config.icon}</span>
                <span>{language === 'fr' ? config.name : config.nameEn}</span>
              </div>
              {zone.distance && (
                <div className="text-gray-400">
                  Distance: {zone.distance}m
                </div>
              )}
            </div>
          </Tooltip>
        )}
      </Polyline>
    </>
  );
};

// ==================================================
// COMPOSANT PRINCIPAL
// ==================================================

/**
 * BionicAdvancedZones - Rendu de toutes les zones avancées
 * 
 * @param {object} props
 * @param {array} props.zones - Liste des zones à afficher
 * @param {object} props.visibility - Visibilité par type de zone
 * @param {string} props.mapType - Type de carte actuel
 * @param {number} props.globalOpacity - Opacité globale (0-100)
 * @param {string} props.language - Langue (fr/en)
 * @param {function} props.onZoneClick - Callback au clic sur une zone
 */
const BionicAdvancedZones = ({
  zones = [],
  visibility = {},
  mapType = 'ecoforestry',
  globalOpacity = 75,
  language = 'fr',
  onZoneClick
}) => {
  // Filtrer et trier les zones par priorité d'affichage
  const visibleZones = useMemo(() => {
    return zones
      .filter(zone => {
        // Vérifier si ce type de zone est visible
        const zoneType = zone.type || zone.zoneType;
        return visibility[zoneType] !== false;
      })
      .sort((a, b) => {
        // Trier par priorité (plus haute priorité = rendu en dernier = au-dessus)
        const configA = ZONE_CONFIG[a.type] || { priority: 99 };
        const configB = ZONE_CONFIG[b.type] || { priority: 99 };
        return configB.priority - configA.priority;
      });
  }, [zones, visibility]);
  
  // Calculer l'opacité effective
  const effectiveOpacity = useCallback((category) => {
    const baseOpacity = getAdaptiveOpacity(mapType, category);
    return baseOpacity * (globalOpacity / 100);
  }, [mapType, globalOpacity]);
  
  // Handler de clic
  const handleZoneClick = useCallback((zone) => {
    if (onZoneClick) {
      onZoneClick(zone);
    }
  }, [onZoneClick]);
  
  if (visibleZones.length === 0) return null;
  
  return (
    <LayerGroup>
      {visibleZones.map((zone, index) => {
        const zoneType = zone.type || zone.zoneType;
        const config = ZONE_CONFIG[zoneType];
        
        if (!config) return null;
        
        const opacity = effectiveOpacity(config.category);
        
        // Rendu selon le type de géométrie
        if (zone.geometry === 'corridor' || zoneType === 'corridor') {
          return (
            <ZoneCorridor
              key={zone.id || `corridor-${index}`}
              zone={{ ...zone, type: zoneType }}
              coordinates={zone.coordinates || zone.path}
              width={zone.width}
              mapType={mapType}
              opacity={opacity}
              language={language}
              onClick={handleZoneClick}
            />
          );
        }
        
        if (zone.geometry === 'circle' || zone.center) {
          return (
            <ZoneCircle
              key={zone.id || `circle-${index}`}
              zone={{ ...zone, type: zoneType }}
              center={zone.center || zone.coordinates}
              radius={zone.radius}
              mapType={mapType}
              opacity={opacity}
              language={language}
              onClick={handleZoneClick}
            />
          );
        }
        
        // Par défaut: polygone
        return (
          <ZonePolygon
            key={zone.id || `polygon-${index}`}
            zone={{ ...zone, type: zoneType }}
            coordinates={zone.coordinates || zone.polygon}
            mapType={mapType}
            opacity={opacity}
            language={language}
            onClick={handleZoneClick}
          />
        );
      })}
    </LayerGroup>
  );
};

export default BionicAdvancedZones;
export { ZonePolygon, ZoneCircle, ZoneCorridor };
