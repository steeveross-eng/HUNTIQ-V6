/**
 * CursorBionicLayer — Real-time Habitat Score Badge at Cursor
 * BIONIC V5 ULTIME 300% — cursor_bionic_v1
 *
 * Displays a dynamic habitat quality score (0-100%) badge near cursor.
 * Uses pre-computed grid from /api/v1/bionic/habitat-score/realtime.
 * Bilinear interpolation for smooth, instant updates.
 *
 * Includes Waypoint QuickAdd: right-click to save hotspot as waypoint.
 * Version: waypoint_quickadd_v1
 *
 * 0 impact on existing layers.
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

function bilinearInterp(grid, row, col) {
  const rows = grid.length;
  const cols = grid[0]?.length || 0;
  if (rows === 0 || cols === 0) return 0;
  const r0 = Math.max(0, Math.min(Math.floor(row), rows - 1));
  const c0 = Math.max(0, Math.min(Math.floor(col), cols - 1));
  const r1 = Math.min(r0 + 1, rows - 1);
  const c1 = Math.min(c0 + 1, cols - 1);
  const dr = row - r0;
  const dc = col - c0;
  return (
    grid[r0][c0] * (1 - dr) * (1 - dc) +
    grid[r0][c1] * (1 - dr) * dc +
    grid[r1][c0] * dr * (1 - dc) +
    grid[r1][c1] * dr * dc
  );
}

function scoreColor(score) {
  if (score < 25) return '#ef4444';
  if (score < 40) return '#f97316';
  if (score < 55) return '#eab308';
  if (score < 70) return '#84cc16';
  if (score < 85) return '#22c55e';
  return '#10b981';
}

function scoreBg(score) {
  if (score < 25) return 'rgba(239,68,68,0.15)';
  if (score < 40) return 'rgba(249,115,22,0.15)';
  if (score < 55) return 'rgba(234,179,8,0.15)';
  if (score < 70) return 'rgba(132,204,22,0.15)';
  if (score < 85) return 'rgba(34,197,94,0.15)';
  return 'rgba(16,185,129,0.15)';
}

export default function CursorBionicLayer({ species = 'moose', onQuickAddWaypoint }) {
  const map = useMap();
  const gridRef = useRef(null);
  const badgeRef = useRef(null);
  const menuRef = useRef(null);
  const lastScoreRef = useRef(null);
  const lastLatLngRef = useRef(null);
  const [quickAdd, setQuickAdd] = useState(null);

  const fetchGrid = useCallback(async () => {
    const b = map.getBounds();
    try {
      const res = await fetch(`${API}/v1/bionic/habitat-score/realtime`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bounds: { north: b.getNorth(), south: b.getSouth(), east: b.getEast(), west: b.getWest() },
          species,
          resolution: 30,
        }),
      });
      if (!res.ok) return;
      gridRef.current = await res.json();
    } catch (err) {
      console.warn('CursorBionic: grid fetch error', err);
    }
  }, [map, species]);

  useEffect(() => {
    fetchGrid();
    map.on('moveend', fetchGrid);
    map.on('zoomend', fetchGrid);
    return () => {
      map.off('moveend', fetchGrid);
      map.off('zoomend', fetchGrid);
    };
  }, [map, fetchGrid]);

  useEffect(() => {
    const container = map.getContainer();

    // Badge element — BIONIC V5: taille ×2 (flèche + score doublés)
    const badge = document.createElement('div');
    badge.className = 'cursor-bionic-badge';
    badge.style.cssText = `
      position: absolute; pointer-events: none; z-index: 1200;
      display: none; font-family: 'SF Mono', monospace;
      font-size: 24px; font-weight: 700; padding: 6px 16px;
      border-radius: 12px; backdrop-filter: blur(8px);
      border: 3px solid transparent; transition: opacity 0.1s;
      white-space: nowrap; line-height: 1.2;
    `;
    container.appendChild(badge);
    badgeRef.current = badge;

    // Context menu for QuickAdd
    const menu = document.createElement('div');
    menu.className = 'cursor-bionic-menu';
    menu.style.cssText = `
      position: absolute; z-index: 1300; display: none;
      background: rgba(10,15,25,0.92); backdrop-filter: blur(12px);
      border: 1px solid rgba(80,200,120,0.3); border-radius: 8px;
      padding: 6px 0; min-width: 180px; font-size: 12px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    `;
    container.appendChild(menu);
    menuRef.current = menu;

    let throttleTimer = null;

    const onMouseMove = (e) => {
      if (throttleTimer) return;
      throttleTimer = setTimeout(() => { throttleTimer = null; }, 40);

      const data = gridRef.current;
      if (!data || !data.scores || !data.bounds) {
        badge.style.display = 'none';
        return;
      }

      const { lat, lng } = e.latlng;
      lastLatLngRef.current = { lat, lng };
      const b = data.bounds;
      const rows = data.grid.rows;
      const cols = data.grid.cols;

      const rowF = ((b.north - lat) / (b.north - b.south)) * (rows - 1);
      const colF = ((lng - b.west) / (b.east - b.west)) * (cols - 1);

      if (rowF < 0 || rowF >= rows || colF < 0 || colF >= cols) {
        badge.style.display = 'none';
        return;
      }

      const score = Math.round(bilinearInterp(data.scores, rowF, colF));
      lastScoreRef.current = score;
      const color = scoreColor(score);

      // BIONIC V5: flèche ×2 + score ×2
      const arrow = score >= 70 ? '▲' : score >= 40 ? '►' : '▼';
      badge.innerHTML = `<span style="font-size:28px;vertical-align:middle;margin-right:4px;">${arrow}</span><span>${score}%</span>`;
      badge.style.color = color;
      badge.style.background = scoreBg(score);
      badge.style.borderColor = color + '60';
      badge.style.display = 'block';

      const pt = e.containerPoint;
      badge.style.left = (pt.x + 22) + 'px';
      badge.style.top = (pt.y - 18) + 'px';
    };

    const onMouseOut = () => {
      badge.style.display = 'none';
    };

    const onContextMenu = (e) => {
      L.DomEvent.preventDefault(e);
      const score = lastScoreRef.current;
      const latlng = lastLatLngRef.current;
      if (score == null || !latlng) return;

      const color = scoreColor(score);
      const pt = map.latLngToContainerPoint(L.latLng(latlng.lat, latlng.lng));

      menu.innerHTML = `
        <div style="padding:8px 14px; color: ${color}; font-weight:700; font-size:26px; border-bottom:1px solid rgba(255,255,255,0.1);">
          ${score >= 70 ? '▲' : score >= 40 ? '►' : '▼'} ${score}% — ${species}
        </div>
        <div style="padding:4px 14px; color: rgba(200,210,220,0.6); font-size:12px;">
          ${latlng.lat.toFixed(5)}, ${latlng.lng.toFixed(5)}
        </div>
        <div class="quickadd-btn" style="
          padding:8px 12px; color:#86efac; cursor:pointer; display:flex; align-items:center; gap:6px;
          transition: background 0.15s;
        " onmouseover="this.style.background='rgba(80,200,120,0.15)'" onmouseout="this.style.background='transparent'">
          <span style="font-size:14px;">+</span> Ajouter Waypoint ici
        </div>
      `;

      menu.style.left = (pt.x + 5) + 'px';
      menu.style.top = (pt.y + 5) + 'px';
      menu.style.display = 'block';

      const btn = menu.querySelector('.quickadd-btn');
      btn.onclick = () => {
        menu.style.display = 'none';
        if (onQuickAddWaypoint) {
          onQuickAddWaypoint({
            lat: latlng.lat,
            lng: latlng.lng,
            score,
            species,
            activeLayers: [],
            timestamp: new Date().toISOString(),
          });
        }
      };
    };

    const hideMenu = () => {
      menu.style.display = 'none';
    };

    map.on('mousemove', onMouseMove);
    map.on('mouseout', onMouseOut);
    map.getContainer().addEventListener('contextmenu', (e) => e.preventDefault());
    map.on('contextmenu', onContextMenu);
    map.on('click', hideMenu);
    map.on('movestart', hideMenu);

    return () => {
      map.off('mousemove', onMouseMove);
      map.off('mouseout', onMouseOut);
      map.off('contextmenu', onContextMenu);
      map.off('click', hideMenu);
      map.off('movestart', hideMenu);
      if (badge.parentNode) badge.parentNode.removeChild(badge);
      if (menu.parentNode) menu.parentNode.removeChild(menu);
    };
  }, [map, species, onQuickAddWaypoint]);

  return null;
}
