/**
 * ConsolidatedHeatmapLayer.jsx — Heatmap consolidée multi-moteurs
 * Intègre: CORRIDORS-V10 + ALIMENTATION-V2 + repos + pression
 * STEEVE-MAX: palette thermique, stabilité via primitives, cache
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';

const ConsolidatedHeatmapLayer = ({
  center,
  species = 'CERF',
  month = 10,
  enabled = true,
  opacity = 0.45,
  onDataLoaded = null,
}) => {
  const map = useMap();
  const layerRef = useRef(null);
  const cacheRef = useRef(null);
  const lastKeyRef = useRef('');
  const abortRef = useRef(null);
  const onDataLoadedRef = useRef(onDataLoaded);
  onDataLoadedRef.current = onDataLoaded;

  const centerLat = center?.lat;
  const centerLng = center?.lng;

  const clearLayers = useCallback(() => {
    if (layerRef.current) {
      map.removeLayer(layerRef.current);
      layerRef.current = null;
    }
  }, [map]);

  const renderHeatmap = useCallback((data) => {
    clearLayers();
    if (!data?.points?.length) return;

    const maxScore = Math.max(...data.points.map(p => p.score), 1);
    const heatData = data.points
      .filter(p => p.score > 0)
      .map(p => [p.lat, p.lng, p.score / maxScore]);

    const heat = L.heatLayer(heatData, {
      radius: 30,
      blur: 20,
      maxZoom: 17,
      max: 1.0,
      minOpacity: opacity * 0.4,
      gradient: {
        0.0: '#1a1a2e',
        0.2: '#3B82F6',
        0.4: '#22C55E',
        0.6: '#F59E0B',
        0.8: '#EF4444',
        1.0: '#DC2626',
      },
    });

    heat.addTo(map);
    layerRef.current = heat;
  }, [map, clearLayers, opacity]);

  const renderRef = useRef(renderHeatmap);
  renderRef.current = renderHeatmap;

  const fetchData = useCallback(async () => {
    if (centerLat == null || centerLng == null || !enabled) {
      clearLayers();
      return;
    }

    const key = `${centerLat.toFixed(4)}:${centerLng.toFixed(4)}:${species}:${month}`;

    if (lastKeyRef.current === key && layerRef.current) return;
    if (lastKeyRef.current === key && cacheRef.current) {
      renderRef.current(cacheRef.current);
      return;
    }
    lastKeyRef.current = key;

    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();

    try {
      const apiUrl = process.env.REACT_APP_BACKEND_URL;
      const params = new URLSearchParams({
        lat: centerLat, lng: centerLng,
        species, month, grid_size: 20,
      });
      const res = await fetch(`${apiUrl}/api/v1/score-consolide/heatmap?${params}`, {
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
      if (err.name !== 'AbortError') console.error('[HEATMAP]', err);
    }
  }, [centerLat, centerLng, species, month, enabled, clearLayers]);

  useEffect(() => {
    fetchData();
    return () => { if (abortRef.current) abortRef.current.abort(); };
  }, [fetchData]);

  useEffect(() => {
    if (cacheRef.current) renderHeatmap(cacheRef.current);
  }, [renderHeatmap]);

  useEffect(() => {
    if (!enabled) clearLayers();
  }, [enabled, clearLayers]);

  return null;
};

export default ConsolidatedHeatmapLayer;
