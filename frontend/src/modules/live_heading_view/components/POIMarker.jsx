/**
 * POIMarker - Point of Interest marker in heading view
 */
import React from 'react';
import { MapPin } from 'lucide-react';

export const POIMarker = ({ poi, index, heading, autoRotate }) => {
  // Position based on bearing and distance
  // Map the POI to screen coordinates based on relative angle
  const relativeAngle = poi.relative_angle || 0;
  const normalizedDistance = Math.min(poi.distance_m / 500, 1); // Normalize to cone range
  
  // Calculate position (centered at 50%, 60% from top)
  const angleRad = (relativeAngle) * Math.PI / 180;
  const x = 50 + Math.sin(angleRad) * (normalizedDistance * 35); // 35% max horizontal offset
  const y = 60 - Math.cos(angleRad) * (normalizedDistance * 40); // 40% max vertical offset (upward)
  
  // Scale marker size by distance
  const scale = 1 - (normalizedDistance * 0.4);
  
  return (
    <div
      className="absolute transform -translate-x-1/2 -translate-y-1/2 transition-all duration-300"
      style={{
        left: `${x}%`,
        top: `${y}%`,
        transform: `translate(-50%, -50%) scale(${scale}) ${autoRotate ? `rotate(${heading}deg)` : ''}`,
        zIndex: Math.round(100 - normalizedDistance * 50)
      }}
    >
      {/* Marker */}
      <div 
        className="relative group cursor-pointer"
        style={{ '--poi-color': poi.color || '#64748b' }}
      >
        {/* Pulse effect for high priority */}
        {poi.priority >= 8 && (
          <div 
            className="absolute inset-0 rounded-full animate-ping opacity-30"
            style={{ backgroundColor: poi.color }}
          />
        )}
        
        {/* Icon container */}
        <div 
          className="w-10 h-10 rounded-full flex items-center justify-center shadow-lg border-2"
          style={{ 
            backgroundColor: `${poi.color}20`,
            borderColor: poi.color
          }}
        >
          <MapPin className="h-5 w-5" style={{ color: poi.color }} />
        </div>
        
        {/* Distance label */}
        <div 
          className="absolute -bottom-5 left-1/2 transform -translate-x-1/2 whitespace-nowrap"
          style={{ transform: autoRotate ? `translateX(-50%) rotate(${-heading}deg)` : 'translateX(-50%)' }}
        >
          <span 
            className="text-xs font-bold px-1.5 py-0.5 rounded"
            style={{ 
              backgroundColor: poi.color,
              color: '#fff'
            }}
          >
            {poi.distance_m < 1000 
              ? `${Math.round(poi.distance_m)}m` 
              : `${(poi.distance_m/1000).toFixed(1)}km`
            }
          </span>
        </div>
        
        {/* Hover tooltip */}
        <div 
          className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"
          style={{ transform: autoRotate ? `translateX(-50%) rotate(${-heading}deg)` : 'translateX(-50%)' }}
        >
          <div className="bg-slate-800 rounded-lg px-3 py-2 shadow-lg border border-slate-600 whitespace-nowrap">
            <div className="text-white text-sm font-medium">{poi.name}</div>
            {poi.description && (
              <div className="text-slate-400 text-xs mt-1">{poi.description}</div>
            )}
            <div className="text-xs text-emerald-400 mt-1">
              Cap: {Math.round(poi.bearing)}°
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default POIMarker;
