import React, { useMemo } from 'react';
import { Polyline, CircleMarker, Tooltip, Pane } from 'react-leaflet';

/**
 * STEVE-MAX P3: Renders the optimal hunting path on the map.
 * - Orange dashed polyline connecting key zones
 * - Strategic waypoint markers (start, saline, cache, end)
 * - All rendered in a dedicated Pane above corridors (z-index 700)
 */
const HuntingPathLayer = ({ huntingPath }) => {
  const pathData = useMemo(() => {
    if (!huntingPath || !huntingPath.path || huntingPath.path.length < 2) return null;
    
    // Convert [lng, lat] to [lat, lng] for Leaflet
    const positions = huntingPath.path.map(c => [c[1], c[0]]);
    const style = huntingPath.style || { color: '#FF6B00', weight: 3, opacity: 0.9, dashArray: '12, 6' };
    const waypoints = huntingPath.waypoints || [];
    
    return { positions, style, waypoints };
  }, [huntingPath]);

  if (!pathData) return null;

  const MARKER_COLORS = {
    start: '#4CAF50',
    saline: '#FFEB3B',
    cache: '#795548',
    // ALIMENTATION-V2: alimentation_sec SUPPRIME — directive STEEVE-MAX
    end: '#F44336',
  };

  return (
    <Pane name="hunting-path-pane" style={{ zIndex: 700 }}>
      {/* Main path polyline */}
      <Polyline
        positions={pathData.positions}
        pathOptions={{
          color: pathData.style.color,
          weight: pathData.style.weight,
          opacity: pathData.style.opacity,
          dashArray: pathData.style.dashArray,
        }}
        data-testid="hunting-path-polyline"
      >
        <Tooltip sticky>
          Trajet de chasse optimal
        </Tooltip>
      </Polyline>

      {/* Strategic waypoints */}
      {pathData.waypoints.map((wp, idx) => (
        <CircleMarker
          key={`wp-${idx}`}
          center={[wp.position[1], wp.position[0]]}
          radius={wp.type === 'start' || wp.type === 'end' ? 7 : 5}
          pathOptions={{
            fillColor: MARKER_COLORS[wp.type] || '#FF6B00',
            fillOpacity: 0.9,
            color: '#fff',
            weight: 2,
          }}
          data-testid={`hunting-waypoint-${wp.type}`}
        >
          <Tooltip direction="top" offset={[0, -8]}>
            <span className="text-xs font-bold">{wp.label}</span>
          </Tooltip>
        </CircleMarker>
      ))}
    </Pane>
  );
};

export default HuntingPathLayer;
