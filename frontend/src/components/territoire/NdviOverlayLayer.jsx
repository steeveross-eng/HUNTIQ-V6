/**
 * NdviOverlayLayer — NDVI Vegetation Overlay (Sentinel-2)
 * BIONIC V5 ULTIME 300% — ndvi_layer_v1
 *
 * Renders an NDVI heatmap overlay on a Leaflet map using Canvas 2D.
 * Color scale: red (bare) -> yellow -> green (dense vegetation).
 * Fetches real NDVI from /api/v1/bionic/ndvi-shadow/analyze.
 *
 * Lazy-loaded: only active when user enables the toggle.
 * 0 impact on existing map layers.
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

function ndviToColor(ndvi) {
  if (ndvi < -0.1) return [80, 80, 80, 60];
  if (ndvi < 0.05) return [180, 100, 60, 120];
  if (ndvi < 0.15) return [210, 150, 50, 130];
  if (ndvi < 0.25) return [230, 200, 60, 130];
  if (ndvi < 0.35) return [200, 220, 50, 130];
  if (ndvi < 0.45) return [140, 200, 50, 135];
  if (ndvi < 0.55) return [80, 180, 50, 140];
  if (ndvi < 0.65) return [40, 160, 50, 145];
  if (ndvi < 0.75) return [20, 140, 40, 150];
  if (ndvi < 0.85) return [10, 120, 30, 155];
  return [5, 100, 20, 160];
}

export default function NdviOverlayLayer({ bounds: propBounds }) {
  const map = useMap();
  const canvasRef = useRef(null);
  const ndviDataRef = useRef(null);
  const [legendData, setLegendData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchNdvi = useCallback(async (b) => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/v1/bionic/ndvi-shadow/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bounds: { north: b.north, south: b.south, east: b.east, west: b.west },
          species: 'moose',
          resolution: 60,
        }),
      });
      if (!res.ok) return;
      const data = await res.json();
      ndviDataRef.current = data;
      if (data.stats) {
        setLegendData({
          mean: data.stats.mean,
          min: data.stats.min,
          max: data.stats.max,
          vegPct: data.stats.vegetation_pct,
          densePct: data.stats.dense_vegetation_pct,
          barePct: data.stats.bare_soil_pct,
          source: data.source,
          cached: data.cache_status === 'hit',
        });
      }
    } catch (err) {
      console.warn('NdviOverlayLayer: fetch error', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const renderNdvi = useCallback(() => {
    const canvas = canvasRef.current;
    const data = ndviDataRef.current;
    if (!canvas || !data) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const size = map.getSize();
    canvas.width = size.x;
    canvas.height = size.y;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const field = data.ndvi_field;
    if (!field || !field.length) return;

    const rows = field.length;
    const cols = field[0].length;
    const bounds = data.bounds;
    if (!bounds) return;

    const nw = map.latLngToContainerPoint(L.latLng(bounds.north, bounds.west));
    const se = map.latLngToContainerPoint(L.latLng(bounds.south, bounds.east));
    const pixW = (se.x - nw.x) / cols;
    const pixH = (se.y - nw.y) / rows;

    if (pixW < 0.5 || pixH < 0.5) return;

    const imgData = ctx.createImageData(cols, rows);
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const [red, green, blue, alpha] = ndviToColor(field[r][c]);
        const idx = (r * cols + c) * 4;
        imgData.data[idx] = red;
        imgData.data[idx + 1] = green;
        imgData.data[idx + 2] = blue;
        imgData.data[idx + 3] = alpha;
      }
    }

    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = cols;
    tempCanvas.height = rows;
    tempCanvas.getContext('2d').putImageData(imgData, 0, 0);

    ctx.imageSmoothingEnabled = true;
    ctx.drawImage(tempCanvas, nw.x, nw.y, se.x - nw.x, se.y - nw.y);
  }, [map]);

  useEffect(() => {
    const container = map.getContainer();
    const canvas = L.DomUtil.create('canvas', 'ndvi-overlay-canvas');
    canvas.style.position = 'absolute';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '440';
    container.appendChild(canvas);
    canvasRef.current = canvas;

    const b = propBounds || {
      north: map.getBounds().getNorth(),
      south: map.getBounds().getSouth(),
      east: map.getBounds().getEast(),
      west: map.getBounds().getWest(),
    };
    fetchNdvi(b);

    const onMove = () => renderNdvi();
    map.on('moveend', onMove);
    map.on('zoomend', onMove);
    map.on('resize', () => {
      const size = map.getSize();
      canvas.width = size.x;
      canvas.height = size.y;
      renderNdvi();
    });

    return () => {
      map.off('moveend', onMove);
      map.off('zoomend', onMove);
      if (canvas.parentNode) canvas.parentNode.removeChild(canvas);
    };
  }, [map, propBounds, fetchNdvi, renderNdvi]);

  useEffect(() => {
    if (ndviDataRef.current) renderNdvi();
  }, [renderNdvi]);

  return (
    <>
      {loading && (
        <div style={{
          position: 'absolute', top: '70px', left: '50%', transform: 'translateX(-50%)',
          zIndex: 1100, background: 'rgba(10,15,25,0.85)', color: '#86efac',
          padding: '6px 16px', borderRadius: '8px', fontSize: '12px',
          border: '1px solid rgba(80,200,120,0.3)', backdropFilter: 'blur(8px)',
        }}>
          Chargement NDVI Sentinel-2...
        </div>
      )}
      {legendData && (
        <div
          data-testid="ndvi-legend"
          style={{
            position: 'absolute', bottom: '24px', left: '12px', zIndex: 1000,
            background: 'rgba(10,15,25,0.88)', backdropFilter: 'blur(12px)',
            borderRadius: '10px', padding: '10px 14px', color: '#e0e8f0',
            fontSize: '11px', lineHeight: '1.6', pointerEvents: 'auto',
            border: '1px solid rgba(80,200,120,0.25)', minWidth: '155px',
          }}
        >
          <div style={{ fontWeight: 600, fontSize: '11px', marginBottom: '6px', color: '#86efac', letterSpacing: '0.5px' }}>
            NDVI <span style={{ opacity: 0.5, fontSize: '9px' }}>Sentinel-2</span>
          </div>
          <div style={{ display: 'flex', gap: '2px', marginBottom: '4px', height: '10px', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ flex: 1, background: '#b4643c' }} />
            <div style={{ flex: 1, background: '#d29632' }} />
            <div style={{ flex: 1, background: '#e6d83c' }} />
            <div style={{ flex: 1, background: '#8cc832' }} />
            <div style={{ flex: 1, background: '#28a032' }} />
            <div style={{ flex: 1, background: '#0a7814' }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '9px', opacity: 0.6, marginBottom: '6px' }}>
            <span>Sol nu</span><span>Dense</span>
          </div>
          <div style={{ borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '5px' }}>
            <div>NDVI moy: <b style={{ color: '#86efac' }}>{legendData.mean?.toFixed(3)}</b></div>
            <div style={{ opacity: 0.7 }}>Min: {legendData.min?.toFixed(3)} / Max: {legendData.max?.toFixed(3)}</div>
            <div style={{ marginTop: '4px' }}>
              <span style={{ color: '#4ade80' }}>{legendData.vegPct}%</span> veg.
              {legendData.densePct > 0 && <span style={{ opacity: 0.6 }}> ({legendData.densePct}% dense)</span>}
            </div>
            <div style={{ opacity: 0.5, fontSize: '9px', marginTop: '2px' }}>
              {legendData.source === 'sentinel2_real' ? 'Donnees reelles' : 'Synthetique'}
              {legendData.cached && ' (cache)'}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
