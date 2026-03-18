/**
 * AlimentationV2Layer.jsx — Salines ALIMENTATION-V2
 * Affiche les salines optimales dans la zone d'analyse 2km×2km.
 * Points jaunes = sélectionnés, gris = candidats non retenus.
 * Conforme BCE-4X + STEEVE-MAX (diversification spatiale 300m).
 *
 * STABILITÉ V2:
 *   - fetchData dépend UNIQUEMENT de primitives
 *   - onDataLoaded via ref stable
 *   - AbortController pour annuler les fetch en vol
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const SALINE_SELECTED = '#FFD700';
const SALINE_SELECTED_BORDER = '#B8860B';
const SALINE_CANDIDATE = '#9CA3AF';
const SALINE_CANDIDATE_BORDER = '#6B7280';

const AlimentationV2Layer = ({
  center,
  species = 'CERF',
  month = 10,
  enabled = true,
  showSalines = true,
  maxSalines = 4,
  onDataLoaded = null,
}) => {
  const map = useMap();
  const layerRef = useRef(null);
  const cacheRef = useRef(null);
  const lastKeyRef = useRef('');
  const abortRef = useRef(null);

  const centerLat = center?.lat;
  const centerLng = center?.lng;

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
      const isSelected = sal.selected;
      const fillColor = isSelected ? SALINE_SELECTED : SALINE_CANDIDATE;
      const borderColor = isSelected ? SALINE_SELECTED_BORDER : SALINE_CANDIDATE_BORDER;
      const radius = isSelected ? 9 : 5;
      const fillOpacity = isSelected ? 0.92 : 0.35;
      const weight = isSelected ? 2.5 : 1.5;

      const marker = L.circleMarker([sal.lat, sal.lng], {
        radius,
        fillColor,
        color: borderColor,
        weight,
        fillOpacity,
        opacity: isSelected ? 1.0 : 0.5,
        pane: 'markerPane',
      });

      const carences = sal.carences_zone?.join(', ') || 'Aucune';
      const justif = sal.justifications?.join(', ') || '';
      const rankLabel = isSelected ? `#${sal.rank}` : 'Candidat';
      const statusLabel = isSelected ? 'SÉLECTIONNÉE' : 'Non retenue';

      marker.bindTooltip(
        `<div style="font-size:12px;font-weight:700;color:${fillColor}">
          ${sal.id} — ${rankLabel} ${sal.type}
        </div>
        <div style="font-size:11px;color:${isSelected ? '#FFD700' : '#999'};font-weight:600">
          ${statusLabel}
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

      if (isSelected) {
        marker.on('mouseover', function () { this.setStyle({ radius: 11, fillOpacity: 1.0 }); });
        marker.on('mouseout', function () { this.setStyle({ radius: 9, fillOpacity: 0.92 }); });
      }

      group.addLayer(marker);
    }

    group.addTo(map);
    layerRef.current = group;
  }, [map, clearLayers, showSalines]);

  const renderRef = useRef(renderSalines);
  renderRef.current = renderSalines;

  const fetchData = useCallback(async () => {
    if (centerLat == null || centerLng == null || !enabled) {
      clearLayers();
      return;
    }

    const key = `${centerLat.toFixed(4)}:${centerLng.toFixed(4)}:${species}:${month}:${maxSalines}`;

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
      const res = await fetch(`${apiUrl}/api/v2/alimentation/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          center_lat: centerLat,
          center_lng: centerLng,
          species,
          month,
          max_salines: maxSalines,
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
  }, [centerLat, centerLng, species, month, enabled, maxSalines, clearLayers]);

  useEffect(() => {
    fetchData();
    return () => {
      if (abortRef.current) abortRef.current.abort();
    };
  }, [fetchData]);

  useEffect(() => {
    if (cacheRef.current) renderSalines(cacheRef.current);
  }, [renderSalines]);

  useEffect(() => {
    if (!enabled) clearLayers();
  }, [enabled, clearLayers]);

  return null;
};

export default AlimentationV2Layer;
