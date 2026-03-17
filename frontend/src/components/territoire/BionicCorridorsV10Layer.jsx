/**
 * BionicCorridorsV10Layer.jsx — Couche corridors fauniques BIONIC
 * Norme CORRIDOR-V1/V10 officielle
 *
 * Palette normative obligatoire:
 *   CRITIQUE  #CC0000 (4m)  — rayé
 *   MAJEUR    #FF0000 (6m)
 *   FORT      #FF8C00 (11m)
 *   MODERE    #FFD700 (17m)
 *   FAIBLE    #BFBFBF (26m)
 *
 * Performance: caching, pré-rendu, throttling, simplification géométrique
 * Lissage contrôlé, continuité visible, aucune rupture.
 */
import { useEffect, useRef, useCallback, useState, useMemo } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const CORRIDOR_PALETTE = {
  CRITIQUE: { color: '#CC0000', weight: 6, dashArray: '10,4', label: 'Critique' },
  MAJEUR:   { color: '#FF0000', weight: 5, dashArray: null,   label: 'Majeur' },
  FORT:     { color: '#FF8C00', weight: 4, dashArray: null,   label: 'Fort' },
  MODERE:   { color: '#FFD700', weight: 3, dashArray: null,   label: 'Modéré' },
  FAIBLE:   { color: '#BFBFBF', weight: 2, dashArray: null,   label: 'Faible' },
};

const ZONE_COLORS = {
  alimentation: '#4CAF50',
  repos: '#2196F3',
  rut: '#FF5722',
  eau: '#00BCD4',
};

const SPECIES_MAP = {
  orignal: 'ORIGNAL',
  chevreuil: 'CERF',
  ours_noir: 'OURS',
  dindon_sauvage: 'DINDON',
  wapiti: 'WAPITI',
  tous: 'CERF',
};

// Z-index déterministe: FAIBLE → CRITIQUE → zones
const LEVEL_ZINDEX = { FAIBLE: 0, MODERE: 1, FORT: 2, MAJEUR: 3, CRITIQUE: 4 };

// Cache global pour éviter re-fetch
const _cache = new Map();
function cacheKey(lat, lng, sp, m) { return `${lat.toFixed(4)}:${lng.toFixed(4)}:${sp}:${m}`; }

// Douglas-Peucker simplifié côté client
function simplifyPath(coords, tolerance = 0.00003) {
  if (coords.length <= 4) return coords;
  const sqDist = (p, a, b) => {
    let dx = b[0] - a[0], dy = b[1] - a[1];
    if (dx !== 0 || dy !== 0) {
      const t = Math.min(1, Math.max(0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)));
      dx = a[0] + t * dx; dy = a[1] + t * dy;
    } else { dx = a[0]; dy = a[1]; }
    return (p[0] - dx) ** 2 + (p[1] - dy) ** 2;
  };
  const tol2 = tolerance * tolerance;
  const dp = (pts, first, last, result) => {
    let maxDist = 0, idx = 0;
    for (let i = first + 1; i < last; i++) {
      const d = sqDist(pts[i], pts[first], pts[last]);
      if (d > maxDist) { maxDist = d; idx = i; }
    }
    if (maxDist > tol2) {
      if (idx - first > 1) dp(pts, first, idx, result);
      result.push(pts[idx]);
      if (last - idx > 1) dp(pts, idx, last, result);
    }
  };
  const result = [coords[0]];
  dp(coords, 0, coords.length - 1, result);
  result.push(coords[coords.length - 1]);
  return result;
}

const BionicCorridorsV10Layer = ({
  center,
  species = 'cerf',
  month = 10,
  enabled = true,
  opacity = 0.85,
  onDataLoaded = null,
}) => {
  const map = useMap();
  const layerGroupRef = useRef(null);
  const abortRef = useRef(null);
  const throttleRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const lastRenderKey = useRef('');

  const clearLayers = useCallback(() => {
    if (layerGroupRef.current) {
      map.removeLayer(layerGroupRef.current);
      layerGroupRef.current = null;
    }
  }, [map]);

  // Pré-calculer les styles (pré-stylé, pré-classifié)
  const precomputedStyles = useMemo(() => {
    const styles = {};
    for (const [level, p] of Object.entries(CORRIDOR_PALETTE)) {
      styles[level] = {
        glow: { color: p.color, weight: p.weight + 3, opacity: opacity * 0.25, lineCap: 'round', lineJoin: 'round', interactive: false },
        main: { color: p.color, weight: p.weight, opacity, lineCap: 'round', lineJoin: 'round', dashArray: p.dashArray },
        hover: { weight: p.weight + 2, opacity: 1 },
        restore: { weight: p.weight, opacity },
      };
    }
    return styles;
  }, [opacity]);

  const renderData = useCallback((data, sp) => {
    clearLayers();
    const group = L.layerGroup();
    const features = data.geojson?.features || [];

    // Séparer et trier corridors par z-index
    const corridors = features
      .filter(f => f.geometry.type === 'LineString')
      .sort((a, b) => (LEVEL_ZINDEX[a.properties.niveau] || 0) - (LEVEL_ZINDEX[b.properties.niveau] || 0));

    const zones = features.filter(f => f.geometry.type === 'Point');

    // Rendu batch corridors (pré-stylé)
    for (const feature of corridors) {
      const raw = feature.geometry.coordinates.map(c => [c[1], c[0]]);
      if (raw.length < 2) continue;

      const coords = simplifyPath(raw);
      const props = feature.properties;
      const style = precomputedStyles[props.niveau] || precomputedStyles.FORT;

      // Glow
      group.addLayer(L.polyline(coords, style.glow));

      // Main
      const line = L.polyline(coords, style.main);
      line.bindTooltip(
        `<div style="font-size:12px;font-weight:600;color:${CORRIDOR_PALETTE[props.niveau]?.color || '#FF8C00'}">
          ${CORRIDOR_PALETTE[props.niveau]?.label || props.niveau} (${props.score}/100)
        </div>
        <div style="font-size:11px;color:#555">
          ${props.from_type} → ${props.to_type} | ${props.largeur_m}m
        </div>`,
        { sticky: true, opacity: 0.95 }
      );
      line.on('mouseover', function() { this.setStyle(style.hover); });
      line.on('mouseout', function() { this.setStyle(style.restore); });
      group.addLayer(line);
    }

    // Rendu zones
    for (const feature of zones) {
      const [lng, lat] = feature.geometry.coordinates;
      const props = feature.properties;
      const zc = ZONE_COLORS[props.zone_type] || '#9E9E9E';
      const c = L.circleMarker([lat, lng], {
        radius: 4, fillColor: zc, color: '#fff',
        weight: 1.5, fillOpacity: 0.8, opacity: 0.9,
      });
      c.bindTooltip(
        `<span style="font-size:11px;font-weight:600;color:${zc}">${
          props.zone_type.charAt(0).toUpperCase() + props.zone_type.slice(1)
        }</span>`,
        { sticky: true }
      );
      group.addLayer(c);
    }

    group.addTo(map);
    layerGroupRef.current = group;

    // Callback légende
    if (onDataLoaded) {
      onDataLoaded({
        niveauDistribution: data.niveau_distribution || {},
        totalCorridors: corridors.length,
        totalZones: zones.length,
        scoreCorridors: data.score_corridor,
        classeCorridors: data.classe_corridor,
        continuity: data.continuity,
        species: sp,
      });
    }
  }, [map, clearLayers, precomputedStyles, onDataLoaded]);

  const fetchAndRender = useCallback(async () => {
    if (!center || !enabled) {
      clearLayers();
      return;
    }

    const sp = SPECIES_MAP[species] || 'CERF';
    const key = cacheKey(center.lat, center.lng, sp, month);

    // Throttle: 200ms debounce
    if (throttleRef.current) clearTimeout(throttleRef.current);
    throttleRef.current = setTimeout(async () => {
      // Skip if same render key
      if (lastRenderKey.current === key && layerGroupRef.current) return;
      lastRenderKey.current = key;

      // Check cache
      if (_cache.has(key)) {
        renderData(_cache.get(key), sp);
        return;
      }

      if (abortRef.current) abortRef.current.abort();
      abortRef.current = new AbortController();

      setLoading(true);
      try {
        const apiUrl = process.env.REACT_APP_BACKEND_URL;
        const res = await fetch(`${apiUrl}/api/v10/corridors/analyze-full`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            center_lat: center.lat,
            center_lng: center.lng,
            species: sp,
            month,
          }),
          signal: abortRef.current.signal,
        });

        if (!res.ok) return;
        const data = await res.json();

        // Cache
        _cache.set(key, data);
        if (_cache.size > 20) {
          const firstKey = _cache.keys().next().value;
          _cache.delete(firstKey);
        }

        // Render only if still the latest request
        if (lastRenderKey.current === key) {
          renderData(data, sp);
        }
      } catch (err) {
        if (err.name !== 'AbortError') console.error('[CORRIDORS-V10]', err);
      } finally {
        setLoading(false);
      }
    }, 200);
  }, [center, species, month, enabled, clearLayers, renderData]);

  useEffect(() => {
    fetchAndRender();
    return () => {
      if (abortRef.current) abortRef.current.abort();
      if (throttleRef.current) clearTimeout(throttleRef.current);
      clearLayers();
    };
  }, [fetchAndRender]);

  useEffect(() => {
    if (!enabled) clearLayers();
  }, [enabled, clearLayers]);

  return loading ? (
    <div
      data-testid="corridors-v10-loading"
      style={{
        position: 'absolute', top: 12, right: 12, zIndex: 1000,
        background: 'rgba(0,0,0,0.7)', color: '#FF8C00',
        padding: '4px 10px', borderRadius: 6, fontSize: 11, fontWeight: 600,
      }}
    >
      Corridors V10...
    </div>
  ) : null;
};

export default BionicCorridorsV10Layer;
export { CORRIDOR_PALETTE };
