/**
 * TerritoryShell.jsx — Couche territory.shell BIONIC V5
 *
 * Enveloppe organique élargie couvrant l'ensemble du secteur.
 * Convex hull + buffer dynamique + lissage Chaikin 4 itérations.
 * Centrage autour du waypoint utilisateur (user.anchor).
 * Contrainte: surface finale ≤ 1 km² (1 000 000 m²).
 *
 * z-index: couche de fond (rendu en premier)
 * Couleur: #3CB371 | Fill: 30%
 */
import React, { useMemo } from 'react';
import { Polygon } from 'react-leaflet';

const SHELL_COLOR = '#3CB371';
const SHELL_FILL_OPACITY = 0.05;    // Centre quasi-transparent — NORME V5 300%
const SHELL_STROKE_OPACITY = 1.0;   // Contour 100% — NORME V5 300%
const SHELL_STROKE_WIDTH = 2.5;
const MAX_AREA_M2 = 1000000; // 1 km²
const METERS_PER_DEG = 111320;
const CHAIKIN_ITERATIONS = 4; // 4 itérations pour forme organique arrondie

// Graham scan convex hull
function convexHull(points) {
  if (points.length < 3) return points;
  const pts = [...points].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const cross = (O, A, B) => (A[0] - O[0]) * (B[1] - O[1]) - (A[1] - O[1]) * (B[0] - O[0]);
  const lower = [];
  for (const p of pts) {
    while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], p) <= 0) lower.pop();
    lower.push(p);
  }
  const upper = [];
  for (let i = pts.length - 1; i >= 0; i--) {
    while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], pts[i]) <= 0) upper.pop();
    upper.push(pts[i]);
  }
  upper.pop();
  lower.pop();
  return lower.concat(upper);
}

// Buffer: expand hull outward from a given center point
function bufferHull(hull, bufferM, centerLat, centerPoint) {
  if (hull.length < 3) return hull;
  const cosLat = Math.cos((centerLat * Math.PI) / 180);
  const bufLat = bufferM / METERS_PER_DEG;
  const bufLng = bufferM / (METERS_PER_DEG * cosLat);
  const cx = centerPoint[0];
  const cy = centerPoint[1];

  return hull.map(([lat, lng]) => {
    const dx = lat - cx;
    const dy = lng - cy;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist < 1e-8) return [lat + bufLat, lng];
    const nx = dx / dist;
    const ny = dy / dist;
    return [lat + nx * bufLat, lng + ny * bufLng];
  });
}

// Chaikin corner-cutting smoothing
function chaikinSmooth(pts, iterations) {
  let result = [...pts];
  for (let iter = 0; iter < iterations; iter++) {
    const smoothed = [];
    for (let i = 0; i < result.length; i++) {
      const p0 = result[i];
      const p1 = result[(i + 1) % result.length];
      smoothed.push([0.75 * p0[0] + 0.25 * p1[0], 0.75 * p0[1] + 0.25 * p1[1]]);
      smoothed.push([0.25 * p0[0] + 0.75 * p1[0], 0.25 * p0[1] + 0.75 * p1[1]]);
    }
    result = smoothed;
  }
  return result;
}

// Approximate polygon area in m²
function polygonAreaM2(pts) {
  if (pts.length < 3) return 0;
  const cLat = pts.reduce((s, p) => s + p[0], 0) / pts.length;
  const cosLat = Math.cos((cLat * Math.PI) / 180);
  let area = 0;
  for (let i = 0; i < pts.length; i++) {
    const j = (i + 1) % pts.length;
    const xi = pts[i][1] * METERS_PER_DEG * cosLat;
    const yi = pts[i][0] * METERS_PER_DEG;
    const xj = pts[j][1] * METERS_PER_DEG * cosLat;
    const yj = pts[j][0] * METERS_PER_DEG;
    area += xi * yj - xj * yi;
  }
  return Math.abs(area) / 2;
}

/**
 * Props:
 *  - zones: zones BIONIC avec positions
 *  - waypointCenter: [lat, lng] du waypoint principal (optionnel)
 *    Si fourni, le shell est centré autour du waypoint.
 */
const TerritoryShell = ({ zones = [], waypointCenter = null }) => {
  const shellPositions = useMemo(() => {
    if (zones.length === 0) return null;

    // Collect all zone vertices
    const allPoints = [];
    zones.forEach(z => {
      if (z.positions && z.positions.length > 0) {
        z.positions.forEach(p => allPoints.push(p));
      }
    });

    // Include waypoint as a point to ensure it's inside the hull
    if (waypointCenter) {
      allPoints.push(waypointCenter);
    }

    if (allPoints.length < 3) return null;

    // Compute convex hull
    const hull = convexHull(allPoints);
    if (hull.length < 3) return null;

    // Center point: waypoint if provided, else hull centroid
    const hullCenterLat = hull.reduce((s, p) => s + p[0], 0) / hull.length;
    const hullCenterLng = hull.reduce((s, p) => s + p[1], 0) / hull.length;
    const center = waypointCenter || [hullCenterLat, hullCenterLng];
    const centerLat = center[0];

    // Dynamic buffer based on zone density (400-600m)
    const baseBuffer = 400;
    const densityBonus = Math.min(200, zones.length * 15);
    let bufferM = baseBuffer + densityBonus;

    // Apply buffer (centered on waypoint) + smooth (4 iterations)
    let shell = bufferHull(hull, bufferM, centerLat, center);
    shell = chaikinSmooth(shell, CHAIKIN_ITERATIONS);

    // Check 1km² constraint — reduce buffer if needed
    let area = polygonAreaM2(shell);
    while (area > MAX_AREA_M2 && bufferM > 50) {
      bufferM -= 50;
      shell = bufferHull(hull, bufferM, centerLat, center);
      shell = chaikinSmooth(shell, CHAIKIN_ITERATIONS);
      area = polygonAreaM2(shell);
    }

    return shell;
  }, [zones, waypointCenter]);

  if (!shellPositions || shellPositions.length < 3) return null;

  return (
    <Polygon
      positions={shellPositions}
      pathOptions={{
        color: SHELL_COLOR,
        weight: SHELL_STROKE_WIDTH,
        opacity: SHELL_STROKE_OPACITY,
        fillColor: SHELL_COLOR,
        fillOpacity: SHELL_FILL_OPACITY,
        lineCap: 'round',
        lineJoin: 'round',
      }}
      data-testid="territory-shell"
    />
  );
};

export default TerritoryShell;
