/**
 * AlimentationV2Layer.jsx — Salines ALIMENTATION-V2
 * Affiche les salines optimales dans la zone d'analyse 2km×2km.
 * Points jaunes distincts. Conforme BCE-4X.
 *
 * STABILITÉ V2: 
 *   - fetchData dépend UNIQUEMENT de primitives (lat, lng, species, month, enabled)
 *   - onDataLoaded via ref stable (pas dans les deps de fetchData)
 *   - renderSalines via ref stable (pas dans les deps de fetchData)
 *   - AbortController pour annuler les fetch en vol
 *   - Cache + guards pour éviter re-fetch inutile
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const SALINE_COLOR = '#FFD700';
const SALINE_BORDER = '#B8860B';

const AlimentationV2Layer = ({
  center,
  species = 'CERF',
  month = 10,
  enabled = true,
  showSalines = true,
  onDataLoaded = null,
}) => {
  const map = useMap();
  const layerRef = useRef(null);
  const cacheRef = useRef(null);
  const lastKeyRef = useRef('');
  const abortRef = useRef(null);

  // Primitives stables (pas de cascade via objet center)
  const centerLat = center?.lat;
  const centerLng = center?.lng;

  // Refs stables pour callbacks — évite cascades de dépendances
  const onDataLoadedRef = useRef(onDataLoaded);
  onDataLoadedRef.current = onDataLoaded;

  const clearLayers = useCallback(() => {
    if (layerRef.current) {
      map.removeLayer(layerRef.current);
      layerRef.current = null;
    }
  }, [map]);

  const renderSalines = useCallback((data) => {
    clearLayers();
    if (!showSalines || !data?.salines?.length) return;

    const group = L.featureGroup();

    for (const sal of data.salines) {
      const marker = L.circleMarker([sal.lat, sal.lng], {
        radius: 8,
        fillColor: SALINE_COLOR,
        color: SALINE_BORDER,
        weight: 2.5,
        fillOpacity: 0.90,
        opacity: 1.0,
        pane: 'markerPane',
      });

      const carences = sal.carences_zone?.join(', ') || 'Aucune';
      const justif = sal.justifications?.join(', ') || '';
      marker.bindTooltip(
        `<div style="font-size:12px;font-weight:700;color:${SALINE_COLOR}">
          ${sal.id} — Saline ${sal.type}
        </div>
        <div style="font-size:11px;color:#666">
          Score: ${sal.score}/100 | Distance: ${sal.distance_centre_m}m
        </div>
        <div style="font-size:10px;color:#888;max-width:200px">
          ${justif}
        </div>
        <div style="font-size:10px;color:#E57373;margin-top:2px">
          Carences: ${carences}
        </div>`,
        { sticky: true, opacity: 0.95 }
      );

      marker.on('mouseover', function() { this.setStyle({ radius: 10, fillOpacity: 1.0 }); });
      marker.on('mouseout', function() { this.setStyle({ radius: 8, fillOpacity: 0.90 }); });

      group.addLayer(marker);
    }

    group.addTo(map);
    layerRef.current = group;
  }, [map, clearLayers, showSalines]);

  // Ref stable pour renderSalines — évite cascade fetchData→renderSalines
  const renderRef = useRef(renderSalines);
  renderRef.current = renderSalines;

  // Fetch découplé — dépend UNIQUEMENT des primitives (AUCUN callback dans les deps)
  const fetchData = useCallback(async () => {
    if (centerLat == null || centerLng == null || !enabled) {
      clearLayers();
      return;
    }

    const key = `${centerLat.toFixed(4)}:${centerLng.toFixed(4)}:${species}:${month}`;

    // Skip si même clé ET layers existent déjà
    if (lastKeyRef.current === key && layerRef.current) return;

    // Données en cache — re-render sans fetch
    if (lastKeyRef.current === key && cacheRef.current) {
      renderRef.current(cacheRef.current);
      return;
    }
    lastKeyRef.current = key;

    // Abort previous fetch
    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();

    try {
      const apiUrl = process.env.REACT_APP_BACKEND_URL;
      const res = await fetch(`${apiUrl}/api/v2/alimentation/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          center_lat: centerLat,
          center_lng: centerLng,
          species: species,
          month: month,
        }),
        signal: abortRef.current.signal,
      });
      if (!res.ok) return;
      const data = await res.json();
      cacheRef.current = data;

      if (lastKeyRef.current === key) {
        renderRef.current(data);
        if (onDataLoadedRef.current) onDataLoadedRef.current(data);
      }
    } catch (err) {
      if (err.name !== 'AbortError') console.error('[ALIMENTATION-V2]', err);
    }
  }, [centerLat, centerLng, species, month, enabled, clearLayers]);

  // Fetch effect — ne se re-déclenche que sur changements réels de primitives
  useEffect(() => {
    fetchData();
    return () => {
      if (abortRef.current) abortRef.current.abort();
    };
  }, [fetchData]);

  // Re-render visuel quand showSalines change (sans re-fetch)
  useEffect(() => {
    if (cacheRef.current) renderSalines(cacheRef.current);
  }, [renderSalines]);

  useEffect(() => {
    if (!enabled) clearLayers();
  }, [enabled, clearLayers]);

  return null;
};

export default AlimentationV2Layer;
