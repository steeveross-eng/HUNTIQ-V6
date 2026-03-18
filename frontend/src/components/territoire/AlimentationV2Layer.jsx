/**
 * AlimentationV2Layer.jsx — Salines ALIMENTATION-V2
 * Affiche les salines optimales dans la zone d'analyse 2km×2km.
 * Points jaunes distincts. Conforme BCE-4X.
 */
import { useEffect, useRef, useCallback, useState } from 'react';
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
        radius: 7,
        fillColor: SALINE_COLOR,
        color: SALINE_BORDER,
        weight: 2,
        fillOpacity: 0.85,
        opacity: 1.0,
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

      marker.on('mouseover', function() { this.setStyle({ radius: 9, fillOpacity: 1.0 }); });
      marker.on('mouseout', function() { this.setStyle({ radius: 7, fillOpacity: 0.85 }); });

      group.addLayer(marker);
    }

    group.addTo(map);
    layerRef.current = group;
  }, [map, clearLayers, showSalines]);

  const renderDataRef = useRef(renderSalines);
  renderDataRef.current = renderSalines;

  const fetchData = useCallback(async () => {
    if (!center || !enabled) { clearLayers(); return; }

    const key = `${center.lat.toFixed(4)}:${center.lng.toFixed(4)}:${species}:${month}`;
    if (lastKeyRef.current === key && cacheRef.current) {
      renderDataRef.current(cacheRef.current);
      if (onDataLoaded) onDataLoaded(cacheRef.current);
      return;
    }
    lastKeyRef.current = key;

    try {
      const apiUrl = process.env.REACT_APP_BACKEND_URL;
      const res = await fetch(`${apiUrl}/api/v2/alimentation/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          center_lat: center.lat,
          center_lng: center.lng,
          species: species,
          month: month,
        }),
      });
      if (!res.ok) return;
      const data = await res.json();
      cacheRef.current = data;
      renderDataRef.current(data);
      if (onDataLoaded) onDataLoaded(data);
    } catch (err) {
      console.error('[ALIMENTATION-V2]', err);
    }
  }, [center, species, month, enabled, clearLayers, onDataLoaded]);

  useEffect(() => { fetchData(); }, [fetchData]);

  useEffect(() => {
    if (cacheRef.current) renderSalines(cacheRef.current);
  }, [renderSalines]);

  useEffect(() => {
    if (!enabled) clearLayers();
  }, [enabled, clearLayers]);

  return null;
};

export default AlimentationV2Layer;
