/**
 * BionicZone2km.jsx — Zone carrée 2 km² centrée sur le waypoint actif
 * VERSION: 1.0.0 — Norme officielle BIONIC
 *
 * SPÉCIFICATIONS:
 *   - Carré unique 2 km × 2 km (2 km²)
 *   - Centré EXACTEMENT sur le waypoint actif
 *   - Contour pointillé orangé BIONIC (#f5a623, faible intensité)
 *   - Sans remplissage (fillOpacity = 0)
 *   - Affiché en permanence pour tous les waypoints actifs
 *   - Sans latence, sans flash, sans disparition
 *
 * NE PAS utiliser la grille multi-cellules 5x5.
 * Objectif: repère spatial constant, précis, non intrusif.
 */

import React, { useMemo } from 'react';
import { Rectangle, Tooltip } from 'react-leaflet';

// Constantes BIONIC
const ZONE_SIZE_M = 2000; // 2 km = 2000 mètres
const METERS_PER_DEG_LAT = 111320; // Mètres par degré de latitude

/**
 * Calcule les bornes d'un carré de 2km × 2km centré sur un point
 * @param {number} lat - Latitude du centre
 * @param {number} lng - Longitude du centre
 * @returns {[[number, number], [number, number]]} Bornes [[sud, ouest], [nord, est]]
 */
function calculateBounds(lat, lng) {
  // Calcul précis tenant compte de la déformation latitude
  const halfSizeM = ZONE_SIZE_M / 2;
  
  // Degrés de latitude pour la moitié de la zone
  const latOffset = halfSizeM / METERS_PER_DEG_LAT;
  
  // Degrés de longitude (ajusté par le cosinus de la latitude)
  const cosLat = Math.cos((lat * Math.PI) / 180);
  const lngOffset = halfSizeM / (METERS_PER_DEG_LAT * cosLat);
  
  return [
    [lat - latOffset, lng - lngOffset], // Sud-Ouest
    [lat + latOffset, lng + lngOffset], // Nord-Est
  ];
}

/**
 * BionicZone2km — Composant pour afficher la zone 2 km² centrée sur un waypoint
 */
const BionicZone2km = ({ 
  waypoint,
  showTooltip = false,  // STEEVE-MAX: tooltip remplacé par indicateur fixe bas-gauche
  opacity = 0.7,
}) => {
  // Extraction des coordonnées (support lat/latitude, lng/longitude)
  const lat = waypoint?.lat ?? waypoint?.latitude;
  const lng = waypoint?.lng ?? waypoint?.longitude;
  
  // Calcul des bornes mémorisé
  const bounds = useMemo(() => {
    if (lat == null || lng == null) return null;
    return calculateBounds(lat, lng);
  }, [lat, lng]);
  
  // Ne rien rendre si pas de coordonnées valides
  if (!bounds) return null;
  
  // Style BIONIC officiel
  const pathOptions = {
    color: '#f5a623',           // Orangé BIONIC
    weight: 2,                   // Épaisseur moyenne
    opacity: opacity,            // Opacité configurable
    fillColor: 'transparent',    // Pas de remplissage
    fillOpacity: 0,              // Transparence totale
    dashArray: '8, 6',           // Pointillé officiel
    dashOffset: '0',
    lineCap: 'round',
    lineJoin: 'round',
  };
  
  // Calcul de la surface en km²
  const areaKm2 = (ZONE_SIZE_M / 1000) * (ZONE_SIZE_M / 1000);
  
  return (
    <Rectangle
      bounds={bounds}
      pathOptions={pathOptions}
      data-testid="bionic-zone-2km"
    >
      {showTooltip && (
        <Tooltip 
          permanent={false} 
          direction="top" 
          offset={[0, -10]}
          className="bionic-zone-tooltip"
        >
          <div className="bg-gray-900/95 border border-[#f5a623]/40 rounded-lg p-2 min-w-[160px]">
            <div className="flex items-center gap-2 mb-1">
              <div 
                className="w-3 h-3 border-2 border-dashed" 
                style={{ borderColor: '#f5a623' }}
              />
              <span className="text-white font-semibold text-sm">Zone d'analyse</span>
            </div>
            <div className="text-xs text-gray-400">
              {ZONE_SIZE_M / 1000} km × {ZONE_SIZE_M / 1000} km = {areaKm2} km²
            </div>
            <div className="text-xs text-[#f5a623] mt-1">
              Centrée sur: {waypoint?.name || 'Waypoint'}
            </div>
          </div>
        </Tooltip>
      )}
    </Rectangle>
  );
};

/**
 * BionicZone2kmLayer — Wrapper pour afficher la zone 2km² pour TOUS les waypoints actifs
 * Alternative: afficher uniquement pour le waypoint sélectionné
 */
export const BionicZone2kmLayer = ({ 
  waypoints = [],
  selectedWaypoint = null,
  showForAll = false,
  showTooltip = false,  // STEEVE-MAX: tooltip DÉSACTIVÉ mode usager (admin only)
  opacity = 0.7,
}) => {
  const waypointsToRender = showForAll 
    ? waypoints.filter(wp => wp.isActive !== false)
    : (selectedWaypoint ? [selectedWaypoint] : []);
  
  return (
    <>
      {waypointsToRender.map((wp) => (
        <BionicZone2km 
          key={wp.id || `zone-2km-${wp.lat}-${wp.lng}`}
          waypoint={wp}
          opacity={opacity}
          showTooltip={showTooltip}
        />
      ))}
    </>
  );
};

export default BionicZone2km;
