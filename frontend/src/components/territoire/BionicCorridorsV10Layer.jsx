/**
 * BionicCorridorsV10Layer.jsx — Couche corridors fauniques BIONIC
 * Norme CORRIDOR-V1/V10 officielle — BCE-4X / Steeve-MAX
 *
 * HIÉRARCHIE VISUELLE STEEVE-MAX (obligatoire):
 *   DOMINANT  → Zones (contours opaques, weight=3, fillOpacity=0)
 *   SECONDAIRE → Corridors (opacity réduite, weight réduit)
 *   TERTIAIRE  → Points centraux (radius réduit, opacité réduite)
 *
 * Palette normative:
 *   CRITIQUE  #B80000 (contour #660000) — micro-hachures, densité +20%
 *   MAJEUR    #FF0000 (contour #CC0000) — aucun pattern
 *   FORT      #FF8C00 (contour #CC7000)
 *   MODERE    #FFD700 (contour #CCAC00)
 *   FAIBLE    #BFBFBF (contour #999999)
 */
import { useEffect, useRef, useCallback, useState, useMemo } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const CORRIDOR_PALETTE = {
  CRITIQUE: { color: '#B80000', contour: '#660000', weight: 2, hasPattern: true, patternDash: '4,3', dashArray: null, label: 'Critique' },
  MAJEUR:   { color: '#FF0000', contour: '#CC0000', weight: 2, hasPattern: false, patternDash: null, dashArray: null, label: 'Majeur' },
  FORT:     { color: '#FF8C00', contour: '#CC7000', weight: 1.5, hasPattern: false, patternDash: null, dashArray: null, label: 'Fort' },
  MODERE:   { color: '#FFD700', contour: '#CCAC00', weight: 1.2, hasPattern: false, patternDash: null, dashArray: null, label: 'Modéré' },
  FAIBLE:   { color: '#BFBFBF', contour: '#999999', weight: 1, hasPattern: false, patternDash: null, dashArray: null, label: 'Faible' },
};

/**
 * Assombrir couleur hex (BCE-4X: contour 15-20% plus sombre)
 */
function darkenHex(hex, factor = 0.82) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `#${Math.round(r * factor).toString(16).padStart(2, '0')}${Math.round(g * factor).toString(16).padStart(2, '0')}${Math.round(b * factor).toString(16).padStart(2, '0')}`;
}

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
  opacity = 0.55,
  minPercentage = 30,
  onDataLoaded = null,
  showZones = true,
  showCorridorsLayer = true,
  showPoints = true,
  pointsChaudsMode = false,
  pointsChaudsFilter = 'tous',
}) => {
  const map = useMap();
  const layerGroupRef = useRef(null);
  const abortRef = useRef(null);
  const throttleRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const lastRenderKey = useRef('');
  const cachedDataRef = useRef(null);
  const cachedSpeciesRef = useRef('');

  const clearLayers = useCallback(() => {
    if (layerGroupRef.current) {
      map.removeLayer(layerGroupRef.current);
      layerGroupRef.current = null;
    }
  }, [map]);

  // Pré-calculer les styles — Hiérarchie Visuelle STEEVE-MAX
  // Corridors: SECONDAIRES (opacity et weight réduits vs zones DOMINANTES)
  const precomputedStyles = useMemo(() => {
    const corOp = 0.30; // Opacité corridors: secondaire
    const styles = {};
    for (const [level, p] of Object.entries(CORRIDOR_PALETTE)) {
      styles[level] = {
        contour: { color: p.contour, weight: p.weight + 0.5, opacity: corOp * 0.4, lineCap: 'round', lineJoin: 'round', interactive: false },
        main: { color: p.color, weight: p.weight, opacity: corOp, lineCap: 'round', lineJoin: 'round', dashArray: p.dashArray },
        hachure: p.hasPattern ? { color: p.contour, weight: p.weight - 0.5, opacity: corOp * 0.5, lineCap: 'butt', lineJoin: 'round', dashArray: p.patternDash, interactive: false } : null,
        hover: { weight: p.weight + 1, opacity: Math.min(1, corOp + 0.3) },
        restore: { weight: p.weight, opacity: corOp },
      };
    }
    return styles;
  }, []);

  const renderData = useCallback((data, sp) => {
    clearLayers();
    const group = L.layerGroup();
    const features = data.geojson?.features || [];

    const allCorridors = features
      .filter(f => f.geometry.type === 'LineString')
      .sort((a, b) => (LEVEL_ZINDEX[a.properties.niveau] || 0) - (LEVEL_ZINDEX[b.properties.niveau] || 0));

    const zonePolygons = features.filter(f => f.geometry.type === 'Polygon');
    const zonePoints = features.filter(f => f.geometry.type === 'Point');

    // ═══ COUCHE 1 (Z-BAS): Zones polygonales organiques — BCE-4X protégées ═══
    if (showZones) {
      for (const feature of zonePolygons) {
        const rings = feature.geometry.coordinates[0].map(c => [c[1], c[0]]);
        const props = feature.properties;
        const zc = ZONE_COLORS[props.zone_type] || '#9E9E9E';

        const polygon = L.polygon(rings, {
          color: zc,
          weight: 3,
          opacity: 1.0,
          fillColor: 'transparent',
          fillOpacity: 0,
          lineCap: 'round',
          lineJoin: 'round',
        });
        polygon.bindTooltip(
          `<div style="font-size:12px;font-weight:600;color:${zc}">
            ${props.zone_type.charAt(0).toUpperCase() + props.zone_type.slice(1)}
          </div>
          <div style="font-size:11px;color:#555">Score: ${props.score} | ${sp}</div>`,
          { sticky: true, opacity: 0.95 }
        );
        polygon.on('mouseover', function() {
          this.setStyle({ weight: 4, opacity: 1.0 });
        });
        polygon.on('mouseout', function() {
          this.setStyle({ weight: 3, opacity: 1.0 });
        });
        group.addLayer(polygon);
      }

      // Fallback points si pas de polygones
      if (zonePolygons.length === 0) {
        for (const feature of zonePoints) {
          const [lng, lat] = feature.geometry.coordinates;
          const props = feature.properties;
          const zc = ZONE_COLORS[props.zone_type] || '#9E9E9E';
          const c = L.circleMarker([lat, lng], {
            radius: 6, fillColor: zc, color: darkenHex(zc, 0.82),
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
      }
    }

    // ═══ COUCHE 2 (Z-MILIEU): Corridors filtrés ═══
    // Note: corridors declared outside block to avoid "corridors is not defined" error in callback
    const corridors = allCorridors.filter(f => (f.properties.score || 0) >= minPercentage);
    
    if (showCorridorsLayer) {
      for (const feature of corridors) {
        const raw = feature.geometry.coordinates.map(c => [c[1], c[0]]);
        if (raw.length < 2) continue;

        const coords = simplifyPath(raw);
        const props = feature.properties;
        const style = precomputedStyles[props.niveau] || precomputedStyles.FORT;

        group.addLayer(L.polyline(coords, style.contour));

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

        if (style.hachure) {
          group.addLayer(L.polyline(coords, style.hachure));
        }
      }
    }

    // ═══ COUCHE 3 (Z-HAUT): Points centraux — BCE-4X protégés ═══
    if (showPoints) {
      // MODE POINTS CHAUDS: tous les 64 points, style rétabli (version précédente)
      // MODE NORMAL: 16 centroïdes représentatifs, style overlay léger
      const isChaud = pointsChaudsMode;

      for (const feature of zonePolygons) {
        const props = feature.properties;
        const zc = ZONE_COLORS[props.zone_type] || '#9E9E9E';
        const centers = props.all_centers || [];

        // Filtrage par type en mode POINTS CHAUDS
        if (isChaud && pointsChaudsFilter !== 'tous') {
          const filterMap = {
            alimentation: 'alimentation',
            rut: 'rut',
            repos: 'repos',
            trajets: 'alimentation',
            affuts: 'rut',
            habitat: 'repos',
          };
          if (props.zone_type !== filterMap[pointsChaudsFilter]) continue;
        }

        if (isChaud) {
          // Mode POINTS CHAUDS: TOUS les 64 centres, style rétabli
          for (const center of centers) {
            if (!center.lat || !center.lng) continue;
            const marker = L.circleMarker([center.lat, center.lng], {
              radius: 5,
              fillColor: zc,
              color: '#FFFFFF',
              weight: 2,
              fillOpacity: 0.85,
              opacity: 1.0,
            });
            marker.bindTooltip(
              `<span style="font-size:11px;font-weight:600;color:${zc}">${
                props.zone_type.charAt(0).toUpperCase() + props.zone_type.slice(1)
              } — ${Math.round((center.score || 0) * 100)}%</span>`,
              { sticky: true }
            );
            group.addLayer(marker);
          }
        } else {
          // Mode NORMAL: 1 centroïde représentatif par polygone
          let representative = null;
          if (centers.length > 0) {
            representative = centers.reduce((best, c) =>
              (c.score || 0) > (best.score || 0) ? c : best, centers[0]
            );
          } else if (props.center_lat && props.center_lng) {
            representative = { lat: props.center_lat, lng: props.center_lng, score: props.score };
          }

          if (representative && representative.lat && representative.lng) {
            const marker = L.circleMarker([representative.lat, representative.lng], {
              radius: 4,
              fillColor: zc,
              color: '#FFFFFF',
              weight: 1,
              fillOpacity: 0.65,
              opacity: 0.70,
            });
            marker.bindTooltip(
              `<span style="font-size:11px;font-weight:600;color:${zc}">${
                props.zone_type.charAt(0).toUpperCase() + props.zone_type.slice(1)
              } — ${Math.round((representative.score || 0) * 100)}% (${centers.length} pts)</span>`,
              { sticky: true }
            );
            group.addLayer(marker);
          }
        }
      }
    }

    group.addTo(map);
    layerGroupRef.current = group;

    // Callback légende
    if (onDataLoaded) {
      onDataLoaded({
        niveauDistribution: data.niveau_distribution || {},
        totalCorridors: corridors.length,
        totalZones: zonePolygons.length || zonePoints.length,
        scoreCorridors: data.score_corridor,
        classeCorridors: data.classe_corridor,
        continuity: data.continuity,
        species: sp,
      });
    }
  }, [map, clearLayers, precomputedStyles, minPercentage, onDataLoaded, showZones, showCorridorsLayer, showPoints, pointsChaudsMode, pointsChaudsFilter]);

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

        // Store for re-render on seuil change
        cachedDataRef.current = data;
        cachedSpeciesRef.current = sp;

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

  // Re-render quand le seuil minimum ou les contrôles de visibilité changent
  useEffect(() => {
    if (cachedDataRef.current && cachedSpeciesRef.current) {
      renderData(cachedDataRef.current, cachedSpeciesRef.current);
    }
  }, [minPercentage, showZones, showCorridorsLayer, showPoints, pointsChaudsMode, pointsChaudsFilter, renderData]);

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
