/**
 * StructureContrastLayer.jsx — ANTHROPIQUE V5 — Phase 1
 *
 * Rendu différencié des structures anthropiques sur le terrain :
 *   - LIGNES (Polyline) : routes, chemins, sentiers, pistes, débardage
 *   - POLYGONES (Polygon) : zones urbanisées, infrastructures, surfaces anthropiques
 *
 * Palette ALPHA — couleurs validées :
 *   Routes majeures : #B71C1C (rouge foncé)
 *   Routes secondaires : #D84315 (orange foncé)
 *   Chemins/pistes : #6D4C41 (brun)
 *   Urbain (polygones) : #EF5350 (rouge)
 *   Infrastructure (polygones) : #546E7A (bleu-gris)
 *
 * z-index: entre territory.shell et behavior.cells
 * Contrainte: polygones clippés ≤ 1 km²
 *
 * AUCUN IMPACT sur : pipeline BIONIC, zones BIONIC, waypoints, P0/P1/P1.1, panneau ULTIME.
 */
import React, { useState, useEffect, useMemo, useRef } from 'react';
import { Polygon, Polyline, useMap } from 'react-leaflet';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

/* ═══════════════════════════════════════════════
   PALETTE ALPHA — ANTHROPIQUE V5
   ═══════════════════════════════════════════════ */
const PALETTE = {
  // LIGNES — Routes majeures (motorway, trunk, primary)
  road_major: { color: '#B71C1C', weight: 2.5, opacity: 0.85, dashArray: null },
  // LIGNES — Routes secondaires (secondary, tertiary, residential, service, unclassified)
  road_secondary: { color: '#D84315', weight: 2.0, opacity: 0.8, dashArray: null },
  // LIGNES — Chemins, sentiers, pistes, débardage (track, footway, path, cycleway)
  trail: { color: '#6D4C41', weight: 1.5, opacity: 0.7, dashArray: '6 4' },
  // LIGNES — Infrastructure linéaire (railway, aeroway, power line)
  infra_line: { color: '#546E7A', weight: 2.0, opacity: 0.7, dashArray: '4 6' },
  // POLYGONES — Zones urbanisées
  urban_fill: { color: '#EF5350', fillOpacity: 0.12, strokeWeight: 1.2, strokeOpacity: 0.6 },
  // POLYGONES — Infrastructure surfacique
  infra_fill: { color: '#546E7A', fillOpacity: 0.10, strokeWeight: 1.0, strokeOpacity: 0.5 },
};

const MAJOR_HIGHWAYS = new Set([
  'motorway', 'motorway_link', 'trunk', 'trunk_link', 'primary', 'primary_link',
]);
const SECONDARY_HIGHWAYS = new Set([
  'secondary', 'secondary_link', 'tertiary', 'tertiary_link',
  'residential', 'service', 'unclassified', 'living_street',
]);
// Tout le reste (track, footway, path, cycleway, pedestrian) → trail

const MAX_AREA_M2 = 1000000;
const METERS_PER_DEG = 111320;
const MAX_LINES = 200;
const MAX_POLYGONS = 80;

function polygonAreaM2(coords) {
  if (coords.length < 3) return 0;
  const cLat = coords.reduce((s, c) => s + c[1], 0) / coords.length;
  const cosLat = Math.cos((cLat * Math.PI) / 180);
  let area = 0;
  for (let i = 0; i < coords.length; i++) {
    const j = (i + 1) % coords.length;
    const xi = coords[i][0] * METERS_PER_DEG * cosLat;
    const yi = coords[i][1] * METERS_PER_DEG;
    const xj = coords[j][0] * METERS_PER_DEG * cosLat;
    const yj = coords[j][1] * METERS_PER_DEG;
    area += xi * yj - xj * yi;
  }
  return Math.abs(area) / 2;
}

function classifyLine(zone) {
  const st = zone.sub_type || '';
  if (zone.type === 'infrastructure') return 'infra_line';
  if (MAJOR_HIGHWAYS.has(st)) return 'road_major';
  if (SECONDARY_HIGHWAYS.has(st)) return 'road_secondary';
  return 'trail';
}

function classifyPolygon(zone) {
  if (zone.type === 'infrastructure') return 'infra_fill';
  return 'urban_fill';
}

const StructureContrastLayer = ({ enabled = true }) => {
  const map = useMap();
  const [zones, setZones] = useState([]);
  const lastFetchKey = useRef('');
  const structureLockRef = useRef({ locked: false, data: [] });

  useEffect(() => {
    if (!enabled || !map) return;

    const fetchStructures = async () => {
      const b = map.getBounds();
      const bounds = {
        south: Math.max(40, b.getSouth()),
        north: Math.min(65, b.getNorth()),
        west: Math.max(-85, b.getWest()),
        east: Math.min(-50, b.getEast()),
      };

      const latRange = bounds.north - bounds.south;
      const lngRange = bounds.east - bounds.west;
      if (latRange > 0.3 || lngRange > 0.4) {
        const cLat = (bounds.north + bounds.south) / 2;
        const cLng = (bounds.east + bounds.west) / 2;
        // Use 0.149 and 0.199 to ensure strict < 0.3 and < 0.4 after rounding
        bounds.south = cLat - 0.149;
        bounds.north = cLat + 0.149;
        bounds.west = cLng - 0.199;
        bounds.east = cLng + 0.199;
      }

      const key = `${bounds.south.toFixed(3)}_${bounds.west.toFixed(3)}_${bounds.north.toFixed(3)}_${bounds.east.toFixed(3)}`;
      if (key === lastFetchKey.current) return;
      if (structureLockRef.current.locked && structureLockRef.current.data.length > 0) return;
      lastFetchKey.current = key;

      try {
        console.log('[StructureContrastLayer] Fetching terrain data for bounds:', bounds);
        const resp = await fetch(`${API_BASE}/api/v1/bionic/terrain/terrain-data`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            south: bounds.south,
            north: bounds.north,
            west: bounds.west,
            east: bounds.east,
            exclude_types: ['water', 'roads', 'urban', 'infrastructure'],
            detail_level: 'low',
          }),
        });
        if (!resp.ok) {
          console.warn('[StructureContrastLayer] API response not OK:', resp.status);
          return;
        }
        const data = await resp.json();
        const allZones = data.exclusion_zones || [];
        console.log('[StructureContrastLayer] Received zones:', allZones.length);

        const lines = allZones
          .filter(z => z.geometry_type === 'line' && z.coordinates && z.coordinates.length >= 2)
          .slice(0, MAX_LINES);

        const polys = allZones
          .filter(z => z.geometry_type === 'polygon' && z.coordinates && z.coordinates.length >= 3)
          .filter(z => polygonAreaM2(z.coordinates) <= MAX_AREA_M2)
          .slice(0, MAX_POLYGONS);

        console.log('[StructureContrastLayer] Processed - Lines:', lines.length, 'Polygons:', polys.length);
        const combined = [...lines, ...polys];
        structureLockRef.current = { locked: true, data: combined };
        setZones(combined);
      } catch (err) {
        console.error('[StructureContrastLayer] Fetch error:', err);
      }
    };

    fetchStructures();
    map.on('moveend', fetchStructures);
    return () => map.off('moveend', fetchStructures);
  }, [enabled, map]);

  const { lineElements, polygonElements } = useMemo(() => {
    const lineEls = [];
    const polyEls = [];

    for (const z of zones) {
      const positions = z.coordinates.map(c => [c[1], c[0]]);
      if (z.geometry_type === 'line') {
        lineEls.push({ positions, paletteKey: classifyLine(z) });
      } else {
        polyEls.push({ positions, paletteKey: classifyPolygon(z) });
      }
    }
    return { lineElements: lineEls, polygonElements: polyEls };
  }, [zones]);

  if (!enabled || (lineElements.length === 0 && polygonElements.length === 0)) return null;

  return (
    <>
      {/* POLYGONES — Zones urbanisées et infrastructures surfaciques */}
      {polygonElements.map((poly, idx) => {
        const style = PALETTE[poly.paletteKey];
        return (
          <Polygon
            key={`anthro-poly-${idx}`}
            data-testid={`anthro-polygon-${idx}`}
            positions={poly.positions}
            pathOptions={{
              color: style.color,
              weight: style.strokeWeight,
              opacity: style.strokeOpacity,
              fillColor: style.color,
              fillOpacity: style.fillOpacity,
              lineCap: 'round',
              lineJoin: 'round',
            }}
          />
        );
      })}
      {/* LIGNES — Routes, chemins, sentiers, pistes */}
      {lineElements.map((line, idx) => {
        const style = PALETTE[line.paletteKey];
        return (
          <Polyline
            key={`anthro-line-${idx}`}
            data-testid={`anthro-line-${idx}`}
            positions={line.positions}
            pathOptions={{
              color: style.color,
              weight: style.weight,
              opacity: style.opacity,
              dashArray: style.dashArray,
              lineCap: 'round',
              lineJoin: 'round',
            }}
          />
        );
      })}
    </>
  );
};

export default StructureContrastLayer;
