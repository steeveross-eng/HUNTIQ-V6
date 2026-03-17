/**
 * WindFlowLayer — BIONIC V8.2.1 Vent Optimisé
 *
 * 2 modes visuels :
 *   - "particles" : Particules Canvas 2D discrètes (intensité réduite 60%, opacité 0.15-0.25)
 *   - "arrows"    : Flèches directionnelles minimalistes (sans particules, sans saturation)
 *
 * Toggle ON/OFF dans LAYERS. État par défaut : ON mode "arrows" (minimaliste).
 * Synchronisé avec OWM + cache 30 min via /api/v1/bionic/weather-shadow/windfield.
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// V8.2.1 OPTIMISÉ → V8.3.B +15% intensité visuelle (STEEVE-MAX UX)
const PARTICLE_COUNT = 1000;        // inchangé
const PARTICLE_MAX_AGE = 100;       // vie longue, trajectoires douces (inchangé)
const PARTICLE_LINE_WIDTH = 0.86;   // +15% (était 0.75)
const SPEED_SCALE = 0.00024;        // INCHANGÉ — vitesse d'animation préservée
const FADE_ALPHA = 0.955;           // traînées légèrement plus persistantes (+15%)

// Palette discrète bleu → vert pâle — V8.3.B +15% opacité (cap 0.345)
function speedToColor(speed, maxSpeed) {
  const t = Math.min(speed / (maxSpeed || 1), 1);
  if (t < 0.4) return `rgba(140, 190, 220, ${Math.min(0.196 + t * 0.253, 0.345)})`;
  if (t < 0.7) return `rgba(150, 200, 180, ${Math.min(0.230 + t * 0.161, 0.345)})`;
  return `rgba(170, 210, 190, ${Math.min(0.265 + t * 0.081, 0.345)})`;
}

function bilinearInterpolate(grid, row, col) {
  const rows = grid.length;
  const cols = grid[0]?.length || 0;
  const r0 = Math.floor(row);
  const c0 = Math.floor(col);
  const r1 = Math.min(r0 + 1, rows - 1);
  const c1 = Math.min(c0 + 1, cols - 1);
  const dr = row - r0;
  const dc = col - c0;
  return (grid[r0]?.[c0] ?? 0) * (1 - dr) * (1 - dc)
       + (grid[r0]?.[c1] ?? 0) * (1 - dr) * dc
       + (grid[r1]?.[c0] ?? 0) * dr * (1 - dc)
       + (grid[r1]?.[c1] ?? 0) * dr * dc;
}

export default function WindFlowLayer({ mode = 'arrows' }) {
  const map = useMap();
  const canvasRef = useRef(null);
  const animRef = useRef(null);
  const windDataRef = useRef(null);
  const particlesRef = useRef([]);
  const [legendData, setLegendData] = useState(null);
  const modeRef = useRef(mode);
  modeRef.current = mode;

  const fetchWindData = useCallback(async (b) => {
    try {
      const res = await fetch(`${API}/v1/bionic/weather-shadow/windfield`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bounds: { north: b.north, south: b.south, east: b.east, west: b.west },
          resolution: 30,
        }),
      });
      if (!res.ok) return;
      const data = await res.json();
      windDataRef.current = data;
      if (data.metadata) {
        setLegendData({
          speed: data.metadata.base_wind_speed_kmh,
          dir: data.metadata.base_wind_direction_deg,
          mean: data.metadata.mean_speed_ms,
          max: data.metadata.max_speed_ms,
          gust: data.metadata.base_gust_kmh,
        });
      }
    } catch (err) {
      console.warn('WindFlowLayer: fetch error', err);
    }
  }, []);

  // Canvas setup + data fetch
  useEffect(() => {
    const container = map.getContainer();
    const canvas = L.DomUtil.create('canvas', 'wind-flow-canvas');
    canvas.style.position = 'absolute';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '400';
    container.appendChild(canvas);
    canvasRef.current = canvas;

    const resize = () => {
      const size = map.getSize();
      canvas.width = size.x;
      canvas.height = size.y;
    };
    resize();
    map.on('resize', resize);

    const getBounds = () => ({
      north: map.getBounds().getNorth(),
      south: map.getBounds().getSouth(),
      east: map.getBounds().getEast(),
      west: map.getBounds().getWest(),
    });
    fetchWindData(getBounds());

    const onMoveEnd = () => fetchWindData(getBounds());
    map.on('moveend', onMoveEnd);

    return () => {
      map.off('resize', resize);
      map.off('moveend', onMoveEnd);
      if (animRef.current) cancelAnimationFrame(animRef.current);
      if (canvas.parentNode) canvas.parentNode.removeChild(canvas);
    };
  }, [map, fetchWindData]);

  // Animation loop (mode-dependent)
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Init particles for particle mode
    const initParticles = () => {
      const particles = [];
      for (let i = 0; i < PARTICLE_COUNT; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          age: Math.floor(Math.random() * PARTICLE_MAX_AGE),
        });
      }
      particlesRef.current = particles;
    };
    initParticles();

    const resetParticle = (p) => {
      p.x = Math.random() * canvas.width;
      p.y = Math.random() * canvas.height;
      p.age = 0;
    };

    // Draw arrow at position — V8.3.B +15% épaisseur & opacité (STEEVE-MAX UX)
    const drawArrow = (cx, cy, angle, length, opacity) => {
      const headLen = Math.max(5, length * 0.3);
      const ex = cx + Math.cos(angle) * length;
      const ey = cy + Math.sin(angle) * length;

      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(ex, ey);
      ctx.strokeStyle = `rgba(150, 200, 210, ${opacity})`;
      ctx.lineWidth = 1.15;
      ctx.stroke();

      // Arrowhead
      ctx.beginPath();
      ctx.moveTo(ex, ey);
      ctx.lineTo(ex - headLen * Math.cos(angle - 0.4), ey - headLen * Math.sin(angle - 0.4));
      ctx.moveTo(ex, ey);
      ctx.lineTo(ex - headLen * Math.cos(angle + 0.4), ey - headLen * Math.sin(angle + 0.4));
      ctx.strokeStyle = `rgba(150, 200, 210, ${opacity * 0.8})`;
      ctx.lineWidth = 1.15;
      ctx.stroke();
    };

    const drawArrowsMode = () => {
      const wd = windDataRef.current;
      if (!wd || !wd.u10 || !wd.v10) return;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const rows = wd.grid.rows;
      const cols = wd.grid.cols;
      const maxSpeed = wd.metadata?.max_speed_ms || 10;

      // Draw arrows on a grid
      const stepX = canvas.width / 16;
      const stepY = canvas.height / 12;
      const mapBounds = map.getBounds();
      const north = mapBounds.getNorth();
      const south = mapBounds.getSouth();
      const west = mapBounds.getWest();
      const east = mapBounds.getEast();

      for (let px = stepX / 2; px < canvas.width; px += stepX) {
        for (let py = stepY / 2; py < canvas.height; py += stepY) {
          const point = map.containerPointToLatLng(L.point(px, py));
          const rowF = ((north - point.lat) / (north - south)) * (rows - 1);
          const colF = ((point.lng - west) / (east - west)) * (cols - 1);

          if (rowF < 0 || rowF >= rows || colF < 0 || colF >= cols) continue;

          const u = bilinearInterpolate(wd.u10, rowF, colF);
          const v = bilinearInterpolate(wd.v10, rowF, colF);
          const speed = Math.sqrt(u * u + v * v);

          if (speed < 0.3) continue;

          const angle = Math.atan2(-v, u); // screen coords: y inverted
          const t = Math.min(speed / maxSpeed, 1);
          const length = 11.5 + t * 28.75; // V8.3.B +15% (était 10+t*25)
          const opacity = Math.min(0.207 + t * 0.138, 0.345); // V8.3.B +15% cap 0.345

          drawArrow(px, py, angle, length, opacity);
        }
      }
    };

    const animateParticles = () => {
      const wd = windDataRef.current;
      if (!wd || !wd.u10 || !wd.v10) {
        animRef.current = requestAnimationFrame(animateParticles);
        return;
      }

      const rows = wd.grid.rows;
      const cols = wd.grid.cols;
      const mapBounds = map.getBounds();
      const north = mapBounds.getNorth();
      const south = mapBounds.getSouth();
      const west = mapBounds.getWest();
      const east = mapBounds.getEast();
      const maxSpeed = wd.metadata?.max_speed_ms || 10;

      ctx.globalCompositeOperation = 'destination-in';
      ctx.fillStyle = `rgba(0, 0, 0, ${FADE_ALPHA})`;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.globalCompositeOperation = 'lighter';

      const particles = particlesRef.current;
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        if (p.age >= PARTICLE_MAX_AGE) { resetParticle(p); continue; }

        const point = map.containerPointToLatLng(L.point(p.x, p.y));
        const rowF = ((north - point.lat) / (north - south)) * (rows - 1);
        const colF = ((point.lng - west) / (east - west)) * (cols - 1);

        if (rowF < 0 || rowF >= rows || colF < 0 || colF >= cols) { resetParticle(p); continue; }

        const u = bilinearInterpolate(wd.u10, rowF, colF);
        const v = bilinearInterpolate(wd.v10, rowF, colF);
        const speed = Math.sqrt(u * u + v * v);

        const dx = u * SPEED_SCALE * canvas.width;
        const dy = -v * SPEED_SCALE * canvas.height;
        const nx = p.x + dx;
        const ny = p.y + dy;

        ctx.beginPath();
        ctx.moveTo(p.x, p.y);
        ctx.lineTo(nx, ny);
        ctx.strokeStyle = speedToColor(speed, maxSpeed);
        ctx.lineWidth = PARTICLE_LINE_WIDTH;
        ctx.stroke();

        p.x = nx;
        p.y = ny;
        p.age++;

        if (p.x < 0 || p.x > canvas.width || p.y < 0 || p.y > canvas.height) resetParticle(p);
      }

      animRef.current = requestAnimationFrame(animateParticles);
    };

    // Main loop dispatches by mode
    let arrowInterval = null;

    const startMode = () => {
      if (animRef.current) cancelAnimationFrame(animRef.current);
      if (arrowInterval) clearInterval(arrowInterval);
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      if (modeRef.current === 'arrows') {
        drawArrowsMode();
        // Redraw on move/zoom
        arrowInterval = null;
      } else {
        initParticles();
        animateParticles();
      }
    };

    startMode();

    const onMove = () => {
      if (animRef.current) cancelAnimationFrame(animRef.current);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      initParticles();
      // Restart after short delay
      setTimeout(startMode, 100);
    };
    map.on('moveend', onMove);
    map.on('zoomend', onMove);

    return () => {
      if (animRef.current) cancelAnimationFrame(animRef.current);
      if (arrowInterval) clearInterval(arrowInterval);
      map.off('moveend', onMove);
      map.off('zoomend', onMove);
    };
  }, [map, mode]);

  const dirLabel = (deg) => {
    if (deg == null) return '?';
    const dirs = ['N','NE','E','SE','S','SO','O','NO'];
    return dirs[Math.round(deg / 45) % 8];
  };

  return legendData ? (
    <div
      data-testid="wind-legend"
      style={{
        position: 'absolute', bottom: '24px', right: '12px', zIndex: 1000,
        background: 'rgba(10,15,25,0.85)', backdropFilter: 'blur(10px)',
        borderRadius: '8px', padding: '8px 12px', color: '#c0d0e0',
        fontSize: '10px', lineHeight: '1.5', pointerEvents: 'auto',
        border: '1px solid rgba(150,200,210,0.15)', minWidth: '120px',
      }}
    >
      <div style={{ fontWeight: 600, fontSize: '10px', marginBottom: '4px', color: '#96c8d2', letterSpacing: '0.4px' }}>
        VENT <span style={{ opacity: 0.4, fontSize: '8px' }}>v2.0 {mode === 'arrows' ? 'min' : 'flow'}</span>
      </div>

      {mode === 'particles' && (
        <div style={{ display: 'flex', gap: '3px', marginBottom: '4px', height: '4px', borderRadius: '2px', overflow: 'hidden' }}>
          <div style={{ flex: 1, background: 'rgba(140,190,220,0.5)' }} />
          <div style={{ flex: 1, background: 'rgba(150,200,180,0.5)' }} />
        </div>
      )}

      <div style={{ borderTop: mode === 'particles' ? '1px solid rgba(255,255,255,0.06)' : 'none', paddingTop: '3px' }}>
        <div>{legendData.speed?.toFixed(1)} km/h — {dirLabel(legendData.dir)}</div>
        {legendData.gust > 0 && (
          <div style={{ opacity: 0.5 }}>Raf. {legendData.gust?.toFixed(0)} km/h</div>
        )}
      </div>
      <div style={{ marginTop: '4px', display: 'flex', alignItems: 'center', gap: '5px' }}>
        <div style={{
          width: '16px', height: '16px', border: '1px solid rgba(150,200,210,0.3)',
          borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '10px', transform: `rotate(${(legendData.dir || 0) + 180}deg)`,
          color: '#96c8d2',
        }}>
          &#8593;
        </div>
        <span style={{ opacity: 0.4, fontSize: '9px' }}>{legendData.dir?.toFixed(0)}°</span>
      </div>
    </div>
  ) : null;
}
