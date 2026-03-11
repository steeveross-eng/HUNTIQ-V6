/**
 * CorridorsVisualLayer.jsx — Rendu visuel BIONIC des corridors V8
 * 
 * Style visuel officiel:
 * - Largeur variable selon utilisation (10-40m)
 * - Palette BIONIC: Gris → Jaune → Orange → Rouge → Stopover hachuré
 * - Rubans organiques avec bords diffus
 * - Stopovers: polygones rouges avec hachures 45°
 * 
 * VERSION: 8.0.0 — Style visuel BIONIC optimisé
 */

import React, { useMemo, useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

// =====================================================================
// PALETTE BIONIC OFFICIELLE
// =====================================================================

const CORRIDOR_PALETTE = {
  occasional: { 
    color: '#D0D0D0', 
    opacity: 0.22, 
    width: 10,
    label: 'Passage occasionnel',
    scoreRange: [0, 25]
  },
  low: { 
    color: '#F7E45A', 
    opacity: 0.30, 
    width: 18,
    label: 'Faible utilisation',
    scoreRange: [25, 35]
  },
  moderate: { 
    color: '#F5A623', 
    opacity: 0.38, 
    width: 28,
    label: 'Utilisation modérée',
    scoreRange: [35, 45]
  },
  high: { 
    color: '#D0021B', 
    opacity: 0.48, 
    width: 38,
    label: 'Forte utilisation',
    scoreRange: [45, 55]
  },
  stopover: { 
    color: '#D0021B', 
    opacity: 0.60, 
    width: 40,
    label: 'Stopover (zone critique)',
    scoreRange: [55, 100],
    hatched: true
  },
};

// =====================================================================
// UTILITAIRES
// =====================================================================

/**
 * Détermine le style visuel basé sur le score du corridor
 */
function getCorridorStyle(score) {
  for (const [key, style] of Object.entries(CORRIDOR_PALETTE)) {
    if (score >= style.scoreRange[0] && score < style.scoreRange[1]) {
      return { key, ...style };
    }
  }
  return { key: 'occasional', ...CORRIDOR_PALETTE.occasional };
}

/**
 * Convertit la largeur en mètres en pixels selon le zoom
 */
function metersToPixels(map, meters, lat) {
  const zoom = map.getZoom();
  const metersPerPixel = 40075016.686 * Math.abs(Math.cos(lat * Math.PI / 180)) / Math.pow(2, zoom + 8);
  return Math.max(2, meters / metersPerPixel);
}

/**
 * Lisse un chemin pour créer des bords organiques
 */
function smoothPath(points, tension = 0.3) {
  if (points.length < 3) return points;
  
  const smoothed = [points[0]];
  
  for (let i = 1; i < points.length - 1; i++) {
    const prev = points[i - 1];
    const curr = points[i];
    const next = points[i + 1];
    
    // Interpolation avec tension
    const lat = curr.lat * (1 - tension) + (prev.lat + next.lat) / 2 * tension;
    const lng = curr.lng * (1 - tension) + (prev.lng + next.lng) / 2 * tension;
    
    smoothed.push({ lat, lng });
  }
  
  smoothed.push(points[points.length - 1]);
  return smoothed;
}

// =====================================================================
// COMPOSANT PRINCIPAL
// =====================================================================

const CorridorsVisualLayer = ({ 
  corridors = [],
  stopovers = [],
  visible = true,
  onCorridorClick,
}) => {
  const map = useMap();
  const layerGroupRef = useRef(null);
  const canvasRendererRef = useRef(null);
  
  // Créer le renderer Canvas pour performance
  useEffect(() => {
    if (!canvasRendererRef.current) {
      canvasRendererRef.current = L.canvas({ padding: 0.5 });
    }
    
    if (!layerGroupRef.current) {
      layerGroupRef.current = L.layerGroup().addTo(map);
    }
    
    return () => {
      if (layerGroupRef.current) {
        layerGroupRef.current.clearLayers();
        map.removeLayer(layerGroupRef.current);
      }
    };
  }, [map]);
  
  // Rendu des corridors
  useEffect(() => {
    if (!layerGroupRef.current || !visible) {
      if (layerGroupRef.current) {
        layerGroupRef.current.clearLayers();
      }
      return;
    }
    
    layerGroupRef.current.clearLayers();
    
    // Rendu des corridors
    corridors.forEach((corridor, index) => {
      const positions = corridor.positions || corridor.path || [];
      if (positions.length < 2) return;
      
      const score = corridor.score || corridor.connectivity_score || 30;
      const style = getCorridorStyle(score);
      
      // Lisser le chemin pour un rendu organique
      const smoothedPositions = smoothPath(
        positions.map(p => ({ 
          lat: p.lat || p[0], 
          lng: p.lng || p[1] 
        }))
      );
      
      // Calculer la largeur en pixels
      const centerLat = smoothedPositions[Math.floor(smoothedPositions.length / 2)].lat;
      const widthPx = metersToPixels(map, style.width, centerLat);
      
      // Créer la polyline avec style BIONIC
      const polyline = L.polyline(
        smoothedPositions.map(p => [p.lat, p.lng]),
        {
          color: style.color,
          weight: Math.max(4, widthPx),
          opacity: style.opacity,
          lineCap: 'round',
          lineJoin: 'round',
          smoothFactor: 1.5,
          renderer: canvasRendererRef.current,
        }
      );
      
      // Ajouter un effet de bordure diffuse (corridor secondaire plus large et plus transparent)
      const outerPolyline = L.polyline(
        smoothedPositions.map(p => [p.lat, p.lng]),
        {
          color: style.color,
          weight: Math.max(6, widthPx * 1.5),
          opacity: style.opacity * 0.3,
          lineCap: 'round',
          lineJoin: 'round',
          smoothFactor: 1.5,
          renderer: canvasRendererRef.current,
        }
      );
      
      // Popup avec infos
      const popupContent = `
        <div class="p-2 min-w-[180px]">
          <div class="font-semibold text-sm mb-1">${corridor.name || `Corridor ${index + 1}`}</div>
          <div class="text-xs text-gray-600 space-y-1">
            <div>Type: ${style.label}</div>
            <div>Score: ${score}%</div>
            <div>WWF: ${corridor.wwf_type || 'N/A'}</div>
            <div>Longueur: ${corridor.length_m ? `${(corridor.length_m / 1000).toFixed(1)} km` : 'N/A'}</div>
          </div>
        </div>
      `;
      
      polyline.bindPopup(popupContent);
      
      if (onCorridorClick) {
        polyline.on('click', () => onCorridorClick(corridor));
      }
      
      // Ajouter au layer group (outer d'abord pour l'effet de halo)
      layerGroupRef.current.addLayer(outerPolyline);
      layerGroupRef.current.addLayer(polyline);
    });
    
    // Rendu des stopovers (zones critiques)
    stopovers.forEach((stopover, index) => {
      const positions = stopover.positions || stopover.polygon || [];
      if (positions.length < 3) return;
      
      const coords = positions.map(p => [p.lat || p[0], p.lng || p[1]]);
      
      // Polygone principal
      const polygon = L.polygon(coords, {
        color: CORRIDOR_PALETTE.stopover.color,
        weight: 2,
        opacity: 0.8,
        fillColor: CORRIDOR_PALETTE.stopover.color,
        fillOpacity: CORRIDOR_PALETTE.stopover.opacity,
        renderer: canvasRendererRef.current,
      });
      
      // Popup stopover
      const popupContent = `
        <div class="p-2 min-w-[160px]">
          <div class="font-semibold text-sm mb-1 text-red-600">
            ⬢ ${stopover.name || `Stopover ${index + 1}`}
          </div>
          <div class="text-xs text-gray-600 space-y-1">
            <div>Type: ${stopover.zone_type || 'Zone critique'}</div>
            <div>Espèce: ${stopover.species || 'Multi-espèces'}</div>
            <div>Importance: ${stopover.importance || 'Haute'}%</div>
          </div>
        </div>
      `;
      
      polygon.bindPopup(popupContent);
      layerGroupRef.current.addLayer(polygon);
    });
    
  }, [corridors, stopovers, visible, map, onCorridorClick]);
  
  // Pas de rendu React direct - tout est géré via Leaflet
  return null;
};

// =====================================================================
// LÉGENDE DES CORRIDORS
// =====================================================================

export const CorridorsLegend = ({ corridorCount = 0, expanded = false }) => {
  const [isExpanded, setIsExpanded] = React.useState(expanded);
  
  return (
    <div 
      className="bg-gray-900/95 rounded-lg border border-gray-700/50 overflow-hidden"
      data-testid="corridors-legend"
    >
      {/* Header avec compteur */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-3 py-2 hover:bg-gray-800/50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-sm font-medium text-white">
            Corridors actifs détectés: {corridorCount}
          </span>
        </div>
        <svg 
          className={`w-4 h-4 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      
      {/* Légende détaillée */}
      {isExpanded && (
        <div className="px-3 pb-3 space-y-2 border-t border-gray-700/30 pt-2">
          {Object.entries(CORRIDOR_PALETTE).map(([key, style]) => (
            <div key={key} className="flex items-center gap-2">
              <div 
                className={`w-6 h-2 rounded-full ${style.hatched ? 'bg-stripes' : ''}`}
                style={{ 
                  backgroundColor: style.color,
                  opacity: style.opacity + 0.3,
                }}
              />
              <span className="text-xs text-gray-300 flex-1">{style.label}</span>
              <span className="text-xs text-gray-500">{style.width}m</span>
            </div>
          ))}
          
          {/* Classification WWF */}
          <div className="border-t border-gray-700/30 pt-2 mt-2">
            <div className="text-xs text-gray-400 mb-1">Classification WWF:</div>
            <div className="space-y-1 text-xs text-gray-500">
              <div>• Macro-corridor: &gt; 5 km</div>
              <div>• Biologique: 1-5 km</div>
              <div>• Conservation: &lt; 1 km</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CorridorsVisualLayer;
export { CORRIDOR_PALETTE, getCorridorStyle };
