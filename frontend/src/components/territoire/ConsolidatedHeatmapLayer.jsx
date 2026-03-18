/**
 * ConsolidatedHeatmapLayer.jsx — Score consolidé multi-moteurs (data-only)
 * STEEVE-MAX: 100% transparent — zero rendu graphique, fetch + callback score uniquement
 * Intègre: CORRIDORS-V10 + ALIMENTATION-V2 + repos + pression
 */
import { useEffect, useRef, useCallback } from 'react';

const ConsolidatedHeatmapLayer = ({
  center,
  species = 'CERF',
  month = 10,
  enabled = true,
  onDataLoaded = null,
  includeCorridors = true,
}) => {
  const cacheRef = useRef(null);
  const lastKeyRef = useRef('');
  const abortRef = useRef(null);
  const onDataLoadedRef = useRef(onDataLoaded);
  onDataLoadedRef.current = onDataLoaded;

  const centerLat = center?.lat;
  const centerLng = center?.lng;

  const fetchData = useCallback(async () => {
    if (centerLat == null || centerLng == null || !enabled) return;

    const key = `${centerLat.toFixed(4)}:${centerLng.toFixed(4)}:${species}:${month}:${includeCorridors ? 1 : 0}`;

    if (lastKeyRef.current === key && cacheRef.current) {
      if (onDataLoadedRef.current) onDataLoadedRef.current(cacheRef.current);
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
        include_corridors: includeCorridors ? '1' : '0',
      });
      const res = await fetch(`${apiUrl}/api/v1/score-consolide/heatmap?${params}`, {
        signal: abortRef.current.signal,
      });
      if (!res.ok) return;
      const data = await res.json();
      cacheRef.current = data;

      if (lastKeyRef.current === key && onDataLoadedRef.current) {
        onDataLoadedRef.current(data);
      }
    } catch (err) {
      if (err.name !== 'AbortError') console.error('[HEATMAP]', err);
    }
  }, [centerLat, centerLng, species, month, enabled, includeCorridors]);

  useEffect(() => {
    fetchData();
    return () => { if (abortRef.current) abortRef.current.abort(); };
  }, [fetchData]);

  return null;
};

export default ConsolidatedHeatmapLayer;
