/**
 * GuidedRouteLayer.jsx — Guided Route / Parcours Guide
 * 
 * Renders the guided hunting route on the map: main line,
 * colored segment overlays, numbered markers with popups.
 * 
 * Phase 2 extraction from TerritoryMap.jsx
 * @module territory/GuidedRouteLayer
 */

import React from 'react';
import L from 'leaflet';
import { Polyline, Marker, Popup } from 'react-leaflet';

const GuidedRouteLayer = ({ route }) => {
  if (!route) return null;

  return (
    <>
      {/* Main route line connecting all points */}
      <Polyline
        positions={route.waypoint_order.map(p => [p.lat, p.lng])}
        color="#22c55e"
        weight={4}
        opacity={0.8}
      />

      {/* Segment color overlays showing probability */}
      {route.segments.map((segment, idx) => (
        <Polyline
          key={`segment-${idx}`}
          positions={[
            [segment.from_waypoint.lat, segment.from_waypoint.lng],
            [segment.to_waypoint.lat, segment.to_waypoint.lng]
          ]}
          color={segment.color}
          weight={6}
          opacity={0.6}
        />
      ))}

      {/* Route point markers with numbers */}
      {route.waypoint_order.map((point, idx) => (
        <Marker
          key={`guided-${point.id}`}
          position={[point.lat, point.lng]}
          icon={L.divIcon({
            className: 'guided-route-marker',
            html: `<div style="
              background: ${point.color};
              width: 28px;
              height: 28px;
              border-radius: 50%;
              border: 3px solid white;
              box-shadow: 0 2px 8px rgba(0,0,0,0.4);
              display: flex;
              align-items: center;
              justify-content: center;
              font-weight: bold;
              font-size: 12px;
              color: white;
            ">${idx + 1}</div>`,
            iconSize: [28, 28],
            iconAnchor: [14, 14]
          })}
        >
          <Popup>
            <div className="text-sm min-w-40">
              <div className="flex items-center justify-between mb-1">
                <p className="font-bold">{point.name}</p>
                <span
                  className="px-2 py-0.5 rounded text-white text-xs font-bold"
                  style={{ backgroundColor: point.color }}
                >
                  {point.probability}%
                </span>
              </div>
              <p className="text-gray-500 text-xs">Etape {idx + 1} du parcours</p>
              <p className="text-gray-400 text-[10px] mt-1">
                {point.lat.toFixed(5)}, {point.lng.toFixed(5)}
              </p>
              {route.segments[idx] && (
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <p className="text-xs text-gray-600">
                    -> {route.segments[idx].distance_km} km vers suivant
                  </p>
                </div>
              )}
            </div>
          </Popup>
        </Marker>
      ))}
    </>
  );
};

export default GuidedRouteLayer;
