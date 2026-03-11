/**
 * MovementCorridorsLayer — Corridors de déplacement réels vs estimés
 * BIONIC V5 ULTIME 300% — movement_corridors_v1
 *
 * - Lignes continues pleines = déplacements réels, confirmés, structurels
 * - Lignes pointillées = déplacements estimés, influencés par conditions actuelles
 *
 * Module isolé, zéro impact sur les couches existantes.
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function MovementCorridorsLayer({ species = 'moose', showReal = true, showEstimated = true, timeOfDay = null }) {
  const map = useMap();
  const layerGroupRef = useRef(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchCorridors = useCallback(async () => {
    const b = map.getBounds();
    setLoading(true);
    try {
      const body = {
        bounds: { north: b.getNorth(), south: b.getSouth(), east: b.getEast(), west: b.getWest() },
        species,
      };
      if (timeOfDay !== null) body.time_of_day = timeOfDay;
      const res = await fetch(`${API}/v1/bionic/movement-corridors/compute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) return;
      setData(await res.json());
    } catch (err) {
      console.warn('MovementCorridors: fetch error', err);
    } finally {
      setLoading(false);
    }
  }, [map, species, timeOfDay]);

  useEffect(() => {
    fetchCorridors();
    map.on('moveend', fetchCorridors);
    return () => { map.off('moveend', fetchCorridors); };
  }, [map, fetchCorridors]);

  // Render corridors on the map
  useEffect(() => {
    if (layerGroupRef.current) {
      layerGroupRef.current.clearLayers();
      map.removeLayer(layerGroupRef.current);
    }
    if (!data) return;

    const group = L.layerGroup();
    layerGroupRef.current = group;

    const renderCorridor = (corridor) => {
      const latlngs = corridor.points.map(p => [p.lat, p.lng]);
      if (latlngs.length < 2) return;

      const s = corridor.style;
      const line = L.polyline(latlngs, {
        color: s.color,
        weight: s.weight,
        opacity: s.opacity,
        dashArray: s.dashArray || undefined,
        lineCap: s.lineCap || 'round',
        lineJoin: s.lineJoin || 'round',
      });

      const isReal = corridor.category === 'real';
      const catLabel = isReal ? 'Confirmé' : 'Estimé';
      const catIcon = isReal ? '\u2501\u2501\u2501' : '\u2504\u2504\u2504';

      // Build factors HTML
      const factorsHtml = Object.entries(corridor.factors || {})
        .map(([k, v]) => `<div style="display:flex;justify-content:space-between;font-size:10px;"><span style="color:#9ca3af">${k.replace(/_/g, ' ')}</span><span style="color:#e0e8f0">${typeof v === 'number' ? v.toFixed?.(1) ?? v : v}</span></div>`)
        .join('');

      line.bindPopup(`
        <div style="font-size:12px;line-height:1.6;min-width:180px;background:#0f1525;color:#e0e8f0;padding:10px;border-radius:8px;">
          <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
            <span style="color:${s.color};font-weight:700;font-size:14px;">${catIcon}</span>
            <span style="font-weight:700;font-size:13px;">${corridor.name}</span>
          </div>
          <div style="font-size:10px;color:${isReal ? '#4CAF50' : '#FF9800'};margin-bottom:6px;padding:2px 6px;background:${isReal ? 'rgba(76,175,80,0.15)' : 'rgba(255,152,0,0.15)'};border-radius:4px;display:inline-block;">
            ${catLabel}
          </div>
          ${!isReal ? '<div style="font-size:9px;color:#FF9800;margin-bottom:6px;padding:3px 6px;background:rgba(255,152,0,0.08);border:1px solid rgba(255,152,0,0.2);border-radius:4px;font-style:italic;">Recalculé selon les conditions actuelles</div>' : ''}
          <div style="font-size:11px;color:#9ca3af;margin-bottom:8px;">${corridor.description}</div>
          <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
            <span style="font-size:11px;">Score</span>
            <span style="color:${s.color};font-weight:700;">${corridor.score}%</span>
          </div>
          <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
            <span style="font-size:11px;">Probabilité</span>
            <span style="font-weight:600;">${(corridor.probability * 100).toFixed(0)}%</span>
          </div>
          ${factorsHtml ? `<div style="border-top:1px solid rgba(255,255,255,0.1);padding-top:6px;margin-top:4px;">${factorsHtml}</div>` : ''}
        </div>
      `, { className: 'bionic-popup' });

      group.addLayer(line);

      // Start/end markers
      const startIcon = L.divIcon({
        className: 'corridor-start',
        html: `<div style="width:8px;height:8px;border-radius:50%;background:${s.color};border:2px solid #fff;box-shadow:0 0 6px ${s.color}80;"></div>`,
        iconSize: [12, 12], iconAnchor: [6, 6],
      });
      const endIcon = L.divIcon({
        className: 'corridor-end',
        html: `<div style="width:6px;height:6px;border-radius:50%;background:${s.color};opacity:0.7;border:1px solid #fff;"></div>`,
        iconSize: [8, 8], iconAnchor: [4, 4],
      });
      group.addLayer(L.marker(latlngs[0], { icon: startIcon, interactive: false }));
      group.addLayer(L.marker(latlngs[latlngs.length - 1], { icon: endIcon, interactive: false }));
    };

    // Render based on visibility toggles
    if (showReal && data.real_corridors) {
      data.real_corridors.forEach(renderCorridor);
    }
    if (showEstimated && data.estimated_corridors) {
      data.estimated_corridors.forEach(renderCorridor);
    }

    group.addTo(map);

    return () => {
      if (layerGroupRef.current) {
        layerGroupRef.current.clearLayers();
        map.removeLayer(layerGroupRef.current);
      }
    };
  }, [data, map, showReal, showEstimated]);

  return (
    <>
      {loading && (
        <div style={{
          position: 'absolute', top: '70px', left: '50%', transform: 'translateX(-50%)',
          zIndex: 1100, background: 'rgba(10,15,25,0.85)', color: '#a5d6a7',
          padding: '6px 16px', borderRadius: '8px', fontSize: '12px',
          border: '1px solid rgba(76,175,80,0.3)', backdropFilter: 'blur(8px)',
        }}>
          Calcul des corridors...
        </div>
      )}
      {data && (
        <div
          data-testid="movement-corridors-legend"
          style={{
            position: 'absolute', bottom: '16px', left: '16px', zIndex: 1100,
            background: 'rgba(10,15,25,0.92)', backdropFilter: 'blur(12px)',
            borderRadius: '10px', padding: '10px 14px', color: '#e0e8f0',
            fontSize: '11px', lineHeight: '1.6', pointerEvents: 'auto',
            border: '1px solid rgba(76,175,80,0.25)', minWidth: '180px',
          }}
        >
          <div style={{ fontWeight: 700, fontSize: '11px', marginBottom: '8px', color: '#a5d6a7', letterSpacing: '0.5px' }}>
            DÉPLACEMENTS <span style={{ opacity: 0.5, fontSize: '9px' }}>v1</span>
          </div>

          {/* Légende réels */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px', opacity: showReal ? 1 : 0.4 }}>
            <div style={{ width: '24px', height: '3px', background: '#4CAF50', borderRadius: '2px' }} />
            <span>Réels ({data.real_corridors?.length || 0})</span>
          </div>

          {/* Légende estimés */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px', opacity: showEstimated ? 1 : 0.4 }}>
            <div style={{
              width: '24px', height: '3px', borderRadius: '2px',
              background: 'repeating-linear-gradient(90deg, #FF9800 0px, #FF9800 4px, transparent 4px, transparent 8px)',
            }} />
            <span>Estimés ({data.estimated_corridors?.length || 0})</span>
          </div>

          <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '4px', marginTop: '2px', fontSize: '10px', color: '#9ca3af' }}>
            Total: {(data.real_corridors?.length || 0) + (data.estimated_corridors?.length || 0)} corridors
          </div>
        </div>
      )}
    </>
  );
}
