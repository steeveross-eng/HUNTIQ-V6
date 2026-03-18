/**
 * BionicCorridorsV10Layer.jsx — Couche corridors fauniques BIONIC
 * Norme CORRIDOR-V1/V10 officielle — BCE-4X / Steeve-MAX V3
 *
 * HIÉRARCHIE VISUELLE STEEVE-MAX (obligatoire):
 *   DOMINANT  → Zones (contours opaques, weight=3, fillOpacity=0)
 *   SECONDAIRE → Corridors (opacity réduite, weight réduit)
 *   TERTIAIRE  → Points centraux (radius réduit, opacité réduite)
 *
 * MODE ZONE D'ANALYSE (2km×2km):
 *   Éléments IN-ZONE  → style complet, interactions actives
 *   Éléments HORS-ZONE → atténués (opacity 0.10-0.20, weight 1-1.5)
 *   Corridors EXTREME  → toujours prioritaires, jamais atténués
 *
 * PERFORMANCE V3:
 *   - L.featureGroup pour batch rendering
 *   - interactive: false pour éléments atténués (zéro DOM overhead)
 *   - Pas de tooltip/hover sur éléments hors-zone
 *   - Cache global persistant (max 20 entrées)
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

// CSS animation: pulsation lente pour trails CRITIQUE (1.5s)
if (typeof document !== 'undefined' && !document.getElementById('corridor-critique-pulse-style')) {
  const style = document.createElement('style');
  style.id = 'corridor-critique-pulse-style';
  style.textContent = `
    @keyframes corridorCritiquePulse {
      0%, 100% { stroke-opacity: 0.85; }
      50% { stroke-opacity: 0.55; }
    }
    .corridor-critique-pulse {
      animation: corridorCritiquePulse 1.5s ease-in-out infinite;
    }
  `;
  document.head.appendChild(style);
}

const CORRIDOR_PALETTE = {
  CRITIQUE: { color: '#FF4500', contour: '#CC3700', weight: 4, hasPattern: true, patternDash: '4,3', dashArray: null, label: 'Critique', glow: true },
  MAJEUR:   { color: '#FF0000', contour: '#CC0000', weight: 2.5, hasPattern: false, patternDash: null, dashArray: null, label: 'Majeur', glow: false },
  FORT:     { color: '#FF8C00', contour: '#CC7000', weight: 2, hasPattern: false, patternDash: null, dashArray: null, label: 'Fort', glow: false },
  MODERE:   { color: '#FFA500', contour: '#CC8400', weight: 2, hasPattern: false, patternDash: null, dashArray: null, label: 'Modéré', glow: false },
  FAIBLE:   { color: '#FFD27F', contour: '#CCA963', weight: 1, hasPattern: false, patternDash: null, dashArray: null, label: 'Faible', glow: false },
};

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

// Z-index déterministe: FAIBLE → CRITIQUE
const LEVEL_ZINDEX = { FAIBLE: 0, MODERE: 1, FORT: 2, MAJEUR: 3, CRITIQUE: 4 };

// ═══ PERFORMANCE V3: Cache global persistant (max 20 entrées) ═══
const _cache = new Map();
function cacheKey(lat, lng, sp, m) { return `${lat.toFixed(4)}:${lng.toFixed(4)}:${sp}:${m}`; }

// ═══ PERFORMANCE V3: Douglas-Peucker simplifié côté client ═══
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

// ═══ MODE ZONE D'ANALYSE: Vérification inclusion dans bbox 2km×2km ═══
const D_LAT_KM = 0.009;  // ~1km en latitude à ~46°N
const D_LNG_KM = 0.013;  // ~1km en longitude à ~46°N

function isInAnalysisBox(lat, lng, box) {
  if (!box) return true;
  return lat >= box.south && lat <= box.north && lng >= box.west && lng <= box.east;
}

function ringsCentroid(rings) {
  let lat = 0, lng = 0;
  for (const [rlat, rlng] of rings) { lat += rlat; lng += rlng; }
  return [lat / rings.length, lng / rings.length];
}

function corridorMidpoint(coords) {
  if (coords.length === 0) return [0, 0];
  const mid = Math.floor(coords.length / 2);
  return coords[mid];
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
  zoneSubFilters = null,
  corridorSubFilters = null,
  pointSubFilters = null,
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

  // ═══ MODE ZONE D'ANALYSE: BBox 2km×2km centré sur le waypoint ═══
  // STABILITÉ: dépend de lat/lng primitives, pas de l'objet center (évite cascades)
  const centerLat = center?.lat;
  const centerLng = center?.lng;
  const analysisBox = useMemo(() => {
    if (centerLat == null || centerLng == null) return null;
    return {
      south: centerLat - D_LAT_KM,
      north: centerLat + D_LAT_KM,
      west: centerLng - D_LNG_KM,
      east: centerLng + D_LNG_KM,
    };
  }, [centerLat, centerLng]);

  // Pré-calculer les styles — Hiérarchie Visuelle STEEVE-MAX
  // CRITIQUE: glow externe 6-8px #FF4500 op0.65 + glow interne 2px #FFF op0.25 + pulsation
  const precomputedStyles = useMemo(() => {
    const corOp = 0.30;
    const styles = {};
    for (const [level, p] of Object.entries(CORRIDOR_PALETTE)) {
      const isExtreme = level === 'CRITIQUE';
      const w = p.weight;
      const op = isExtreme ? 0.85 : corOp;
      styles[level] = {
        // Glow externe: large + semi-transparent (CRITIQUE uniquement)
        glowOuter: isExtreme ? { color: '#FF4500', weight: w + 8, opacity: 0.15, lineCap: 'round', lineJoin: 'round', interactive: false } : null,
        glowMid: isExtreme ? { color: '#FF4500', weight: w + 4, opacity: 0.35, lineCap: 'round', lineJoin: 'round', interactive: false } : null,
        contour: { color: p.contour, weight: w + (isExtreme ? 2 : 0.5), opacity: isExtreme ? 0.65 : corOp * 0.4, lineCap: 'round', lineJoin: 'round', interactive: false },
        main: { color: p.color, weight: w, opacity: op, lineCap: 'round', lineJoin: 'round', dashArray: p.dashArray, className: isExtreme ? 'corridor-critique-pulse' : '' },
        // Glow interne: fin + blanc léger (CRITIQUE uniquement)
        glowInner: isExtreme ? { color: '#FFFFFF', weight: 2, opacity: 0.25, lineCap: 'round', lineJoin: 'round', interactive: false } : null,
        hachure: p.hasPattern ? { color: p.contour, weight: w - 0.5, opacity: isExtreme ? 0.45 : corOp * 0.5, lineCap: 'butt', lineJoin: 'round', dashArray: p.patternDash, interactive: false } : null,
        hover: { weight: w + 2, opacity: Math.min(1, op + 0.15) },
        restore: { weight: w, opacity: op },
      };
    }
    return styles;
  }, []);

  // ═══ SOUS-ÉLÉMENTS: Helpers de filtrage granulaire ═══
  const isZoneTypeVisible = useCallback((zoneType) => {
    if (!zoneSubFilters) return true;
    if (zoneSubFilters.multiEngines) return true; // Multi-Engines = tout afficher
    const map = {
      alimentation: zoneSubFilters.alimentation || zoneSubFilters.trajets,
      repos: zoneSubFilters.repos || zoneSubFilters.habitat,
      rut: zoneSubFilters.rut || zoneSubFilters.affuts,
      eau: zoneSubFilters.habitat,
    };
    return map[zoneType] ?? true;
  }, [zoneSubFilters]);

  const isCorridorLevelVisible = useCallback((niveau) => {
    if (!corridorSubFilters) return true;
    if (corridorSubFilters.saisonniers) return true; // Saisonniers = tout afficher
    switch (niveau) {
      case 'FAIBLE': case 'MODERE': return corridorSubFilters.normaux;
      case 'FORT': case 'MAJEUR': return corridorSubFilters.intenses;
      case 'CRITIQUE': return corridorSubFilters.extreme;
      default: return true;
    }
  }, [corridorSubFilters]);

  const isPointTypeVisible = useCallback((zoneType, isChaudMode) => {
    if (!pointSubFilters) return true;
    // Mode toggle: centroïdes (normal) vs individuels (chauds)
    if (isChaudMode && !pointSubFilters.individuels) return false;
    if (!isChaudMode && !pointSubFilters.centroides) return false;
    // Type filter
    const map = {
      alimentation: pointSubFilters.alimentation || pointSubFilters.trajets,
      repos: pointSubFilters.repos || pointSubFilters.habitat,
      rut: pointSubFilters.rut || pointSubFilters.affuts,
      eau: pointSubFilters.habitat,
    };
    return map[zoneType] ?? true;
  }, [pointSubFilters]);

  // ═══ RENDU PRINCIPAL — Zone d'analyse + Performance V3 ═══
  const renderData = useCallback((data, sp) => {
    clearLayers();
    // PERFORMANCE V3: L.featureGroup pour batch rendering + event delegation
    const group = L.featureGroup();
    const features = data.geojson?.features || [];

    const allCorridors = features
      .filter(f => f.geometry.type === 'LineString')
      .sort((a, b) => (LEVEL_ZINDEX[a.properties.niveau] || 0) - (LEVEL_ZINDEX[b.properties.niveau] || 0));

    const zonePolygons = features.filter(f => f.geometry.type === 'Polygon');
    const zonePoints = features.filter(f => f.geometry.type === 'Point');
    const box = analysisBox;

    // ═══ COUCHE 1 (Z-BAS): Zones polygonales organiques — BCE-4X protégées ═══
    if (showZones) {
      for (const feature of zonePolygons) {
        const props = feature.properties;
        // SOUS-ÉLÉMENT: Filtrage par type de zone
        if (!isZoneTypeVisible(props.zone_type)) continue;

        const rings = feature.geometry.coordinates[0].map(c => [c[1], c[0]]);
        const zc = ZONE_COLORS[props.zone_type] || '#9E9E9E';

        // MODE ZONE D'ANALYSE: vérifier si le centroïde est dans la bbox 2km×2km
        const [cLat, cLng] = ringsCentroid(rings);
        const inZone = isInAnalysisBox(cLat, cLng, box);

        const polygon = L.polygon(rings, {
          color: zc,
          weight: inZone ? 3 : 1.5,
          opacity: inZone ? 1.0 : 0.15,
          fillColor: 'transparent',
          fillOpacity: 0,
          lineCap: 'round',
          lineJoin: 'round',
          interactive: inZone,
        });

        // PERFORMANCE V3: Tooltips + hover uniquement pour éléments IN-ZONE
        if (inZone) {
          polygon.bindTooltip(
            `<div style="font-size:12px;font-weight:600;color:${zc}">
              ${props.zone_type.charAt(0).toUpperCase() + props.zone_type.slice(1)}
            </div>
            <div style="font-size:11px;color:#555">Score: ${props.score} | ${sp}</div>`,
            { sticky: true, opacity: 0.95 }
          );
          polygon.on('mouseover', function() { this.setStyle({ weight: 4, opacity: 1.0 }); });
          polygon.on('mouseout', function() { this.setStyle({ weight: 3, opacity: 1.0 }); });
        }
        group.addLayer(polygon);
      }

      // Fallback points si pas de polygones
      if (zonePolygons.length === 0) {
        for (const feature of zonePoints) {
          const [lng, lat] = feature.geometry.coordinates;
          const props = feature.properties;
          const zc = ZONE_COLORS[props.zone_type] || '#9E9E9E';
          const inZone = isInAnalysisBox(lat, lng, box);
          const c = L.circleMarker([lat, lng], {
            radius: inZone ? 6 : 3,
            fillColor: zc,
            color: darkenHex(zc, 0.82),
            weight: inZone ? 1.5 : 0.5,
            fillOpacity: inZone ? 0.8 : 0.15,
            opacity: inZone ? 0.9 : 0.15,
            interactive: inZone,
          });
          if (inZone) {
            c.bindTooltip(
              `<span style="font-size:11px;font-weight:600;color:${zc}">${
                props.zone_type.charAt(0).toUpperCase() + props.zone_type.slice(1)
              }</span>`,
              { sticky: true }
            );
          }
          group.addLayer(c);
        }
      }
    }

    // ═══ COUCHE 2 (Z-MILIEU): Corridors filtrés ═══
    const corridors = allCorridors.filter(f => (f.properties.score || 0) >= minPercentage);

    if (showCorridorsLayer) {
      for (const feature of corridors) {
        const props = feature.properties;
        // SOUS-ÉLÉMENT: Filtrage par niveau de corridor
        if (!isCorridorLevelVisible(props.niveau)) continue;

        const raw = feature.geometry.coordinates.map(c => [c[1], c[0]]);
        if (raw.length < 2) continue;

        const coords = simplifyPath(raw);
        const isExtreme = props.niveau === 'CRITIQUE';
        const style = precomputedStyles[props.niveau] || precomputedStyles.FORT;

        // MODE ZONE D'ANALYSE: EXTREME toujours visible, autres atténués hors-zone
        const [mLat, mLng] = corridorMidpoint(coords);
        const inZone = isExtreme || isInAnalysisBox(mLat, mLng, box);

        if (inZone) {
          // Glow externe (CRITIQUE uniquement)
          if (style.glowOuter) group.addLayer(L.polyline(coords, style.glowOuter));
          if (style.glowMid) group.addLayer(L.polyline(coords, style.glowMid));
          // Contour
          group.addLayer(L.polyline(coords, style.contour));
          // Ligne principale
          const line = L.polyline(coords, style.main);
          // Tooltip enrichi (CRITIQUE: badge + score gras + flèche)
          const pal = CORRIDOR_PALETTE[props.niveau] || CORRIDOR_PALETTE.FORT;
          const isCrit = props.niveau === 'CRITIQUE';
          line.bindTooltip(
            `<div style="display:flex;align-items:center;gap:6px;margin-bottom:2px">
              ${isCrit ? `<span style="background:#FF4500;color:white;font-size:9px;font-weight:800;padding:1px 5px;border-radius:3px;text-transform:uppercase;letter-spacing:0.5px">Critique</span>` : ''}
              <span style="font-size:12px;font-weight:${isCrit ? '800' : '600'};color:${pal.color}">
                ${pal.label} (${props.score}/100)
              </span>
            </div>
            <div style="font-size:11px;color:#555;display:flex;align-items:center;gap:4px">
              <span>${props.from_type}</span>
              <span style="font-size:14px;font-weight:bold;color:${isCrit ? '#FF4500' : '#888'}">→</span>
              <span>${props.to_type}</span>
              <span style="color:#888;margin-left:4px">| ${props.largeur_m}m</span>
            </div>`,
            { sticky: true, opacity: 0.95 }
          );
          line.on('mouseover', function() { this.setStyle(style.hover); });
          line.on('mouseout', function() { this.setStyle(style.restore); });
          group.addLayer(line);
          // Glow interne blanc (CRITIQUE uniquement)
          if (style.glowInner) group.addLayer(L.polyline(coords, style.glowInner));
          if (style.hachure) group.addLayer(L.polyline(coords, style.hachure));
        } else {
          // PERFORMANCE V3: Style atténué, zéro interaction, zéro tooltip
          group.addLayer(L.polyline(coords, {
            color: style.main.color,
            weight: 1,
            opacity: 0.12,
            lineCap: 'round',
            lineJoin: 'round',
            interactive: false,
          }));
        }
      }
    }

    // ═══ COUCHE 3 (Z-HAUT): Points centraux — BCE-4X protégés ═══
    if (showPoints) {
      const isChaud = pointsChaudsMode;

      for (const feature of zonePolygons) {
        const props = feature.properties;
        const zc = ZONE_COLORS[props.zone_type] || '#9E9E9E';
        const centers = props.all_centers || [];

        // SOUS-ÉLÉMENT: Filtrage par type de point
        if (!isPointTypeVisible(props.zone_type, isChaud)) continue;

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
          // Mode POINTS CHAUDS: TOUS les 64 centres, apparence antérieure (fine reading)
          for (const ct of centers) {
            if (!ct.lat || !ct.lng) continue;
            const inZone = isInAnalysisBox(ct.lat, ct.lng, box);
            const marker = L.circleMarker([ct.lat, ct.lng], {
              radius: inZone ? 4 : 2,
              fillColor: zc,
              color: '#FFFFFF',
              weight: inZone ? 1.5 : 0.5,
              fillOpacity: inZone ? 0.65 : 0.12,
              opacity: inZone ? 0.70 : 0.12,
              interactive: inZone,
            });
            if (inZone) {
              marker.bindTooltip(
                `<span style="font-size:11px;font-weight:600;color:${zc}">${
                  props.zone_type.charAt(0).toUpperCase() + props.zone_type.slice(1)
                } — ${Math.round((ct.score || 0) * 100)}%</span>`,
                { sticky: true }
              );
            }
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
            const inZone = isInAnalysisBox(representative.lat, representative.lng, box);
            const marker = L.circleMarker([representative.lat, representative.lng], {
              radius: inZone ? 5 : 2.5,
              fillColor: zc,
              color: '#FFFFFF',
              weight: inZone ? 1 : 0.5,
              fillOpacity: inZone ? 0.65 : 0.12,
              opacity: inZone ? 0.65 : 0.12,
              interactive: inZone,
            });
            if (inZone) {
              marker.bindTooltip(
                `<span style="font-size:11px;font-weight:600;color:${zc}">${
                  props.zone_type.charAt(0).toUpperCase() + props.zone_type.slice(1)
                } — ${Math.round((representative.score || 0) * 100)}% (${centers.length} pts)</span>`,
                { sticky: true }
              );
            }
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
  }, [map, clearLayers, precomputedStyles, minPercentage, onDataLoaded, showZones, showCorridorsLayer, showPoints, pointsChaudsMode, pointsChaudsFilter, analysisBox, isZoneTypeVisible, isCorridorLevelVisible, isPointTypeVisible]);

  // REF STABLE: renderData accessible sans cascade de dépendances dans fetchAndRender
  const renderDataRef = useRef(renderData);
  renderDataRef.current = renderData;

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
      // Skip re-fetch si mêmes données (renderData appelé par re-render effect séparé)
      if (lastRenderKey.current === key && layerGroupRef.current) return;
      lastRenderKey.current = key;

      // Check cache
      if (_cache.has(key)) {
        const cached = _cache.get(key);
        cachedDataRef.current = cached;
        cachedSpeciesRef.current = sp;
        renderDataRef.current(cached, sp);
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

        // PERFORMANCE V3: Cache persistant
        _cache.set(key, data);
        if (_cache.size > 20) {
          const firstKey = _cache.keys().next().value;
          _cache.delete(firstKey);
        }

        cachedDataRef.current = data;
        cachedSpeciesRef.current = sp;

        if (lastRenderKey.current === key) {
          renderDataRef.current(data, sp);
        }
      } catch (err) {
        if (err.name !== 'AbortError') console.error('[CORRIDORS-V10]', err);
      } finally {
        setLoading(false);
      }
    }, 200);
  }, [center, species, month, enabled, clearLayers]);

  // Re-render quand les contrôles visuels changent (séparé du fetch)
  useEffect(() => {
    if (cachedDataRef.current && cachedSpeciesRef.current) {
      renderData(cachedDataRef.current, cachedSpeciesRef.current);
    }
  }, [renderData]);

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
