/**
 * ExclusionOverlayLayer.jsx — Couche visuelle zones d'exclusion BIONIC V5 300%
 *
 * Overlay semi-transparent affichant les zones d'exclusion (eau, urbain, routes, infrastructure)
 * directement sur la carte. Source: API terrain-data (Overpass).
 *
 * Chaque type d'exclusion a une couleur distincte:
 *   - water: bleu (#2196F3)
 *   - urban: rouge (#F44336)
 *   - roads: orange (#FF9800)
 *   - infrastructure: gris (#9E9E9E)
 *
 * Rendu: polygones avec centre semi-transparent (20%) et contour 80%.
 * Fetch automatique sur moveend. Cache par bounds.
 */

import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Polygon, Tooltip, useMap } from 'react-leaflet';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const EXCLUSION_STYLES = {
  water: { color: '#5b9bd5', label: 'Eau', fillOpacity: 0.08, strokeOpacity: 0.25 },
  urban: { color: '#d4726a', label: 'Urbain', fillOpacity: 0.06, strokeOpacity: 0.22 },
  roads: { color: '#c9944a', label: 'Routes', fillOpacity: 0.05, strokeOpacity: 0.20 },
  infrastructure: { color: '#8a8a8a', label: 'Infrastructure', fillOpacity: 0.05, strokeOpacity: 0.20 },
};

const MAX_AREA_M2 = 1000000;
const METERS_PER_DEG = 111320;

function polygonAreaM2(coords) {
  if (coords.length < 3) return 0;
  const cLat = coords.reduce((s, c) => s + c[1], 0) / coords.length;
  const cosLat = Math.cos((cLat * Math.PI) / 180);
  let area = 0;
  for (let i = 0; i < coords.length; i++) {
    const j = (i + 1) % coords.length;
    const xi = coords[i][0] * METERS_PER_DEG * cosLat;
    const yi = coords[i][0 + 1] ? coords[i][1] * METERS_PER_DEG : 0;
    const xj = coords[j][0] * METERS_PER_DEG * cosLat;
    const yj = coords[j][1] * METERS_PER_DEG;
    area += xi * yj - xj * yi;
  }
  return Math.abs(area) / 2;
}

const ExclusionOverlayLayer = ({ enabled = true }) => {
  const map = useMap();
  const [zones, setZones] = useState([]);
  const lastFetchKey = useRef('');

  useEffect(() => {
    if (!enabled) { setZones([]); return; }

    const fetchExclusions = async () => {
      const b = map.getBounds();
      const bounds = {
        south: Math.max(40, b.getSouth()),
        north: Math.min(65, b.getNorth()),
        west: Math.max(-85, b.getWest()),
        east: Math.min(-50, b.getEast()),
      };

      // Clamp bbox to max 0.3° × 0.4°
      const latRange = bounds.north - bounds.south;
      const lngRange = bounds.east - bounds.west;
      if (latRange > 0.3 || lngRange > 0.4) {
        const cLat = (bounds.north + bounds.south) / 2;
        const cLng = (bounds.east + bounds.west) / 2;
        bounds.south = cLat - 0.15;
        bounds.north = cLat + 0.15;
        bounds.west = cLng - 0.2;
        bounds.east = cLng + 0.2;
      }

      const key = `excl_${bounds.south.toFixed(3)}_${bounds.west.toFixed(3)}_${bounds.north.toFixed(3)}_${bounds.east.toFixed(3)}`;
      if (key === lastFetchKey.current) return;
      lastFetchKey.current = key;

      try {
        const resp = await fetch(`${API_BASE}/api/v1/bionic/terrain/terrain-data`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            south: bounds.south,
            north: bounds.north,
            west: bounds.west,
            east: bounds.east,
            detail_level: 'medium',
          }),
        });
        if (!resp.ok) return;
        const data = await resp.json();
        const exclusionZones = (data.exclusion_zones || [])
          .filter(z => z.geometry_type === 'polygon' && z.coordinates && z.coordinates.length >= 3)
          // HYDRO FIX FINAL: hide ALL water and wetland polygons (100% transparent)
          .filter(z => z.type !== 'water' && z.type !== 'wetland')
          // HYDRO FIX FINAL: hide filtered_out polygons
          .filter(z => !z.filtered_out)
          // HYDRO FIX FINAL: security — hide polygons > 1 km²
          .filter(z => {
            const area = z.area_m2 || polygonAreaM2(z.coordinates);
            return area <= MAX_AREA_M2;
          })
          .slice(0, 100);
        setZones(exclusionZones);
      } catch {
        // Non-blocking
      }
    };

    fetchExclusions();
    map.on('moveend', fetchExclusions);
    return () => map.off('moveend', fetchExclusions);
  }, [enabled, map]);

  const renderedZones = useMemo(() => {
    return zones.map((zone, idx) => {
      const style = EXCLUSION_STYLES[zone.type] || EXCLUSION_STYLES.infrastructure;
      const positions = zone.coordinates.map(c => [c[1], c[0]]);
      return (
        <Polygon
          key={`excl-${idx}-${zone.type}`}
          positions={positions}
          pathOptions={{
            color: style.color,
            weight: 0.8,
            opacity: style.strokeOpacity,
            fillColor: style.color,
            fillOpacity: style.fillOpacity,
            lineCap: 'round',
            lineJoin: 'round',
          }}
        >
          <Tooltip sticky direction="top" offset={[0, -5]}>
            <div className="bg-gray-900/95 border border-gray-700 rounded px-2 py-1 shadow-xl">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-sm" style={{ backgroundColor: style.color }} />
                <span className="text-xs font-semibold text-white">{style.label}</span>
              </div>
              {zone.name && (
                <div className="text-[10px] text-gray-400 mt-0.5">{zone.name}</div>
              )}
              <div className="text-[10px] mt-0.5" style={{ color: style.color }}>
                Zone exclue P0
              </div>
            </div>
          </Tooltip>
        </Polygon>
      );
    });
  }, [zones]);

  if (!enabled || zones.length === 0) return null;

  return <>{renderedZones}</>;
};

export default ExclusionOverlayLayer;
