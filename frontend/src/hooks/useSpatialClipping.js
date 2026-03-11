/**
 * BIONIC V5 300% — INVARIANT: Spatial Clipping Hook
 * 
 * Calcule le AnalysisBoundingBox 1km × 1km centré sur le waypoint actif.
 * Applique le clipping géométrique strict côté client (rendu uniquement).
 * 
 * INVARIANT: Non modifiable, non surchargé, non influençable.
 */

import { useState, useCallback, useMemo, useRef } from 'react';

// Taille du carré d'analyse en mètres — BIONIC V8: unifié à 2km² (2000m)
// CRITIQUE: Cette valeur DOIT correspondre à BionicZone2km.jsx ZONE_SIZE_M
const ANALYSIS_BOX_SIZE_M = 2000;

/**
 * Calcule le bbox 1km × 1km en degrés décimaux
 */
function computeAnalysisBbox(lat, lng, sizeM = ANALYSIS_BOX_SIZE_M) {
  const halfM = sizeM / 2;
  const latRad = (lat * Math.PI) / 180;
  const metersPerDegLat = 111320;
  const metersPerDegLng = 111320 * Math.cos(latRad);
  
  const deltaLat = halfM / metersPerDegLat;
  const deltaLng = halfM / metersPerDegLng;
  
  return {
    north: lat + deltaLat,
    south: lat - deltaLat,
    east: lng + deltaLng,
    west: lng - deltaLng,
    centerLat: lat,
    centerLng: lng,
    sizeM,
  };
}

/**
 * Vérifie si un point [lat, lng] est dans le bbox
 */
function isPointInBbox(lat, lng, bbox) {
  return lat >= bbox.south && lat <= bbox.north && lng >= bbox.west && lng <= bbox.east;
}

/**
 * Clip un polygone (Sutherland-Hodgman) contre le bbox rectangulaire.
 * Entrée: coords = [[lat, lng], ...]
 * Sortie: coords clippées ou null si vide
 */
function clipPolygonToBbox(coords, bbox) {
  if (!coords || coords.length < 3) return null;
  
  let output = coords.map(c => [...c]);
  
  // Clip contre chaque bord du rectangle (Sutherland-Hodgman)
  const edges = [
    { inside: (p) => p[0] >= bbox.south, intersect: (a, b) => clipEdge(a, b, 0, bbox.south, true) },   // south
    { inside: (p) => p[0] <= bbox.north, intersect: (a, b) => clipEdge(a, b, 0, bbox.north, false) },   // north
    { inside: (p) => p[1] >= bbox.west,  intersect: (a, b) => clipEdge(a, b, 1, bbox.west, true) },     // west
    { inside: (p) => p[1] <= bbox.east,  intersect: (a, b) => clipEdge(a, b, 1, bbox.east, false) },    // east
  ];
  
  for (const edge of edges) {
    if (output.length === 0) return null;
    const input = output;
    output = [];
    
    for (let i = 0; i < input.length; i++) {
      const current = input[i];
      const prev = input[(i + input.length - 1) % input.length];
      const currInside = edge.inside(current);
      const prevInside = edge.inside(prev);
      
      if (currInside) {
        if (!prevInside) {
          output.push(edge.intersect(prev, current));
        }
        output.push(current);
      } else if (prevInside) {
        output.push(edge.intersect(prev, current));
      }
    }
  }
  
  return output.length >= 3 ? output : null;
}

function clipEdge(a, b, axis, value, isMin) {
  const t = (value - a[axis]) / (b[axis] - a[axis]);
  const result = [...a];
  result[0] = a[0] + t * (b[0] - a[0]);
  result[1] = a[1] + t * (b[1] - a[1]);
  return result;
}

/**
 * Clip une liste de zones et retourne les zones clippées.
 * Supporte les deux formats: 'positions' (Leaflet [lat,lng]) et 'coordinates' (GeoJSON [lng,lat]).
 */
function clipZones(zones, bbox) {
  const clipped = [];
  for (const zone of zones) {
    // Supporter les deux formats de coordonnées
    let coords = zone.positions || zone.coordinates;
    if (!coords || coords.length < 3) continue;
    
    // Normaliser le format: si premier élément semble être lng (< -50), convertir [lng,lat] → [lat,lng]
    // Québec: lat ~45-50, lng ~-75 à -70
    const firstCoord = coords[0];
    const isGeoJSONFormat = Array.isArray(firstCoord) && firstCoord[0] < -50;
    if (isGeoJSONFormat) {
      coords = coords.map(c => [c[1], c[0]]);  // [lng,lat] → [lat,lng]
    }
    
    const clippedCoords = clipPolygonToBbox(coords, bbox);
    if (clippedCoords) {
      const lats = clippedCoords.map(c => c[0]);
      const lngs = clippedCoords.map(c => c[1]);
      // Recalcul areaM2 à partir de la géométrie CLIPPÉE (coords = [lat, lng])
      const cLat = lats.reduce((a, b) => a + b, 0) / lats.length;
      const cosLat = Math.cos((cLat * Math.PI) / 180);
      const mPerDegLat = 111320;
      const mPerDegLng = 111320 * cosLat;
      let area = 0;
      for (let i = 0; i < clippedCoords.length; i++) {
        const j = (i + 1) % clippedCoords.length;
        const xi = clippedCoords[i][1] * mPerDegLng;
        const yi = clippedCoords[i][0] * mPerDegLat;
        const xj = clippedCoords[j][1] * mPerDegLng;
        const yj = clippedCoords[j][0] * mPerDegLat;
        area += xi * yj - xj * yi;
      }
      const clippedAreaM2 = Math.abs(area) / 2;
      clipped.push({
        ...zone,
        positions: clippedCoords,
        coordinates: clippedCoords,
        center: [lats.reduce((a, b) => a + b, 0) / lats.length, lngs.reduce((a, b) => a + b, 0) / lngs.length],
        areaM2: clippedAreaM2,
        clipped: true,
      });
    }
  }
  return clipped;
}

/**
 * Hook principal de clipping spatial
 */
const useSpatialClipping = (waypoint) => {
  const [snapshotData, setSnapshotData] = useState(null);
  const [isGeneratingSnapshot, setIsGeneratingSnapshot] = useState(false);
  const API_BASE = process.env.REACT_APP_BACKEND_URL;
  
  // Bbox 2km × 2km — BIONIC V8 (unifié avec BionicZone2km)
  // calculé uniquement quand le waypoint change
  const analysisBbox = useMemo(() => {
    if (!waypoint) return null;
    // Support lat/latitude et lng/longitude
    const wpLat = waypoint.lat ?? waypoint.latitude;
    const wpLng = waypoint.lng ?? waypoint.longitude;
    if (!wpLat || !wpLng) return null;
    return computeAnalysisBbox(wpLat, wpLng);
  }, [waypoint?.lat, waypoint?.lng, waypoint?.latitude, waypoint?.longitude]);
  
  // Bbox Leaflet bounds pour l'overlay visuel
  const bboxBounds = useMemo(() => {
    if (!analysisBbox) return null;
    return [
      [analysisBbox.south, analysisBbox.west],
      [analysisBbox.north, analysisBbox.east],
    ];
  }, [analysisBbox]);
  
  // Clipping côté client (pour les zones déjà chargées)
  const clipZonesClient = useCallback((zones) => {
    if (!analysisBbox || !zones) return zones;
    return clipZones(zones, analysisBbox);
  }, [analysisBbox]);
  
  // Générer un snapshot via le backend
  const generateSnapshot = useCallback(async (species, layersVisible, activeParams) => {
    if (!waypoint) return null;
    setIsGeneratingSnapshot(true);
    try {
      const resp = await fetch(`${API_BASE}/api/v1/bionic/snapshot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lat: waypoint.lat,
          lng: waypoint.lng,
          species,
          waypoint_name: waypoint.name,
          layers_visible: layersVisible,
          active_params: activeParams,
        }),
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      setSnapshotData(data);
      return data;
    } catch (err) {
      console.error('[Snapshot] Error:', err);
      return null;
    } finally {
      setIsGeneratingSnapshot(false);
    }
  }, [waypoint, API_BASE]);
  
  return {
    analysisBbox,
    bboxBounds,
    clipZonesClient,
    snapshotData,
    isGeneratingSnapshot,
    generateSnapshot,
    ANALYSIS_BOX_SIZE_M,
  };
};

export default useSpatialClipping;
export { computeAnalysisBbox, clipPolygonToBbox, clipZones, ANALYSIS_BOX_SIZE_M };
