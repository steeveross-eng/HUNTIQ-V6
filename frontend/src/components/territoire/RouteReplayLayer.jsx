/**
 * RouteReplayLayer — Animation tactique du parcours optimisé
 * BIONIC V5 ULTIME 300% — route_replay_v1
 *
 * Module isolé, zéro dépendance circulaire.
 * Utilise le parcours calculé par RoutePlannerLayer pour animer un marqueur mobile.
 * Affiche : vitesse ajustable, points clés en temps réel, progression.
 */

import { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

function scoreToColor(score) {
  if (score < 40) return '#ef4444';
  if (score < 55) return '#f97316';
  if (score < 65) return '#eab308';
  if (score < 75) return '#84cc16';
  return '#22c55e';
}

function haversineKm(lat1, lng1, lat2, lng2) {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

export default function RouteReplayLayer({ species = 'moose' }) {
  const map = useMap();
  const markerRef = useRef(null);
  const trailRef = useRef(null);
  const rafRef = useRef(null);
  const startTimeRef = useRef(null);

  const [routeData, setRouteData] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [progress, setProgress] = useState(0);
  const [currentInfo, setCurrentInfo] = useState(null);
  const [loading, setLoading] = useState(false);

  // Build a flat list of coordinates from all segments
  const flatPath = useMemo(() => {
    if (!routeData?.route?.segments) return [];
    const coords = [];
    const { segments, points } = routeData.route;
    segments.forEach((seg) => {
      if (!seg.path || seg.path.length < 2) return;
      seg.path.forEach((p, i) => {
        // Avoid duplicates at junctions
        if (coords.length > 0 && i === 0) {
          const last = coords[coords.length - 1];
          if (Math.abs(last.lat - p.lat) < 0.00001 && Math.abs(last.lng - p.lng) < 0.00001) return;
        }
        coords.push({
          lat: p.lat,
          lng: p.lng,
          score: seg.avg_score_along_path,
          segIndex: seg.from_point,
        });
      });
    });
    // Pre-compute cumulative distances
    let cumDist = 0;
    coords.forEach((c, i) => {
      if (i > 0) {
        cumDist += haversineKm(coords[i - 1].lat, coords[i - 1].lng, c.lat, c.lng);
      }
      c.cumDist = cumDist;
    });
    return coords;
  }, [routeData]);

  const totalDist = useMemo(() => {
    if (flatPath.length === 0) return 0;
    return flatPath[flatPath.length - 1].cumDist;
  }, [flatPath]);

  // Waypoint names for current info
  const routePoints = routeData?.route?.points || [];

  // Fetch route data
  const fetchRoute = useCallback(async () => {
    const b = map.getBounds();
    setLoading(true);
    try {
      const res = await fetch(`${API}/v1/bionic/route-planner/compute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bounds: { north: b.getNorth(), south: b.getSouth(), east: b.getEast(), west: b.getWest() },
          species,
          resolution: 30,
          hotspot_threshold: 70,
        }),
      });
      if (!res.ok) return;
      const data = await res.json();
      setRouteData(data);
    } catch (err) {
      console.warn('RouteReplay: fetch error', err);
    } finally {
      setLoading(false);
    }
  }, [map, species]);

  useEffect(() => {
    fetchRoute();
  }, [fetchRoute]);

  // Interpolate position along path at a given fraction (0-1)
  const getPositionAt = useCallback(
    (fraction) => {
      if (flatPath.length < 2) return null;
      const targetDist = fraction * totalDist;
      for (let i = 1; i < flatPath.length; i++) {
        if (flatPath[i].cumDist >= targetDist) {
          const prev = flatPath[i - 1];
          const curr = flatPath[i];
          const segLen = curr.cumDist - prev.cumDist;
          const t = segLen > 0 ? (targetDist - prev.cumDist) / segLen : 0;
          return {
            lat: prev.lat + (curr.lat - prev.lat) * t,
            lng: prev.lng + (curr.lng - prev.lng) * t,
            score: curr.score,
            distKm: targetDist,
          };
        }
      }
      const last = flatPath[flatPath.length - 1];
      return { lat: last.lat, lng: last.lng, score: last.score, distKm: totalDist };
    },
    [flatPath, totalDist]
  );

  // Find nearest route point for info display
  const findNearestPoint = useCallback(
    (lat, lng) => {
      if (routePoints.length === 0) return null;
      let closest = null;
      let minD = Infinity;
      routePoints.forEach((pt) => {
        const d = haversineKm(lat, lng, pt.lat, pt.lng);
        if (d < minD) {
          minD = d;
          closest = pt;
        }
      });
      return minD < 0.5 ? closest : null;
    },
    [routePoints]
  );

  // Create / update animated marker
  useEffect(() => {
    if (markerRef.current) {
      map.removeLayer(markerRef.current);
      markerRef.current = null;
    }
    if (trailRef.current) {
      map.removeLayer(trailRef.current);
      trailRef.current = null;
    }
    if (flatPath.length === 0) return;

    const icon = L.divIcon({
      className: 'replay-marker',
      html: `<div style="
        width:20px; height:20px; border-radius:50%;
        background: radial-gradient(circle at 40% 40%, #60a5fa, #1d4ed8);
        border:3px solid #ffffff; box-shadow: 0 0 12px rgba(59,130,246,0.7);
        transition: transform 0.05s linear;
      "></div>`,
      iconSize: [26, 26],
      iconAnchor: [13, 13],
    });
    const marker = L.marker([flatPath[0].lat, flatPath[0].lng], { icon, zIndexOffset: 2000 });
    marker.addTo(map);
    markerRef.current = marker;

    const trail = L.polyline([], {
      color: '#3b82f6',
      weight: 3,
      opacity: 0.5,
      dashArray: '4,6',
    });
    trail.addTo(map);
    trailRef.current = trail;

    return () => {
      if (markerRef.current) map.removeLayer(markerRef.current);
      if (trailRef.current) map.removeLayer(trailRef.current);
    };
  }, [flatPath, map]);

  // Animation loop
  useEffect(() => {
    if (!isPlaying || flatPath.length < 2) return;

    const TOTAL_DURATION_MS = 30000; // 30s for x1 speed
    startTimeRef.current = performance.now() - (progress * TOTAL_DURATION_MS) / speed;

    const animate = (now) => {
      const elapsed = now - startTimeRef.current;
      const rawFraction = (elapsed * speed) / TOTAL_DURATION_MS;
      const fraction = Math.min(rawFraction, 1);
      setProgress(fraction);

      const pos = getPositionAt(fraction);
      if (pos && markerRef.current) {
        markerRef.current.setLatLng([pos.lat, pos.lng]);
        // Update trail
        if (trailRef.current) {
          const trailCoords = [];
          for (let i = 0; i < flatPath.length; i++) {
            if (flatPath[i].cumDist <= pos.distKm) {
              trailCoords.push([flatPath[i].lat, flatPath[i].lng]);
            } else break;
          }
          trailCoords.push([pos.lat, pos.lng]);
          trailRef.current.setLatLngs(trailCoords);
        }
        // Update current info
        const nearest = findNearestPoint(pos.lat, pos.lng);
        setCurrentInfo({
          score: pos.score,
          distKm: pos.distKm,
          nearestPoint: nearest,
        });
      }

      if (fraction >= 1) {
        setIsPlaying(false);
        return;
      }
      rafRef.current = requestAnimationFrame(animate);
    };

    rafRef.current = requestAnimationFrame(animate);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [isPlaying, speed, flatPath, getPositionAt, findNearestPoint, progress]);

  const handlePlayPause = () => {
    if (progress >= 1) setProgress(0);
    setIsPlaying(!isPlaying);
  };

  const handleReset = () => {
    setIsPlaying(false);
    setProgress(0);
    setCurrentInfo(null);
    if (markerRef.current && flatPath.length > 0) {
      markerRef.current.setLatLng([flatPath[0].lat, flatPath[0].lng]);
    }
    if (trailRef.current) trailRef.current.setLatLngs([]);
  };

  const handleProgressClick = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const fraction = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    setProgress(fraction);
    const pos = getPositionAt(fraction);
    if (pos && markerRef.current) {
      markerRef.current.setLatLng([pos.lat, pos.lng]);
      const nearest = findNearestPoint(pos.lat, pos.lng);
      setCurrentInfo({ score: pos.score, distKm: pos.distKm, nearestPoint: nearest });
    }
    if (isPlaying) {
      startTimeRef.current = performance.now() - (fraction * 30000) / speed;
    }
  };

  if (!routeData?.route) {
    return loading ? (
      <div
        style={{
          position: 'absolute', bottom: '80px', left: '50%', transform: 'translateX(-50%)',
          zIndex: 1200, background: 'rgba(10,15,25,0.9)', color: '#93c5fd',
          padding: '6px 16px', borderRadius: '8px', fontSize: '12px',
          border: '1px solid rgba(59,130,246,0.3)', backdropFilter: 'blur(8px)',
        }}
      >
        Chargement du parcours...
      </div>
    ) : null;
  }

  return (
    <div
      data-testid="route-replay-controls"
      style={{
        position: 'absolute',
        bottom: '16px',
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 1200,
        background: 'rgba(10,15,25,0.92)',
        backdropFilter: 'blur(12px)',
        borderRadius: '12px',
        padding: '10px 16px',
        color: '#e0e8f0',
        fontSize: '12px',
        border: '1px solid rgba(59,130,246,0.3)',
        minWidth: '340px',
        maxWidth: '480px',
        pointerEvents: 'auto',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
        <div style={{ fontWeight: 700, fontSize: '11px', color: '#93c5fd', letterSpacing: '0.5px' }}>
          REPLAY PARCOURS <span style={{ opacity: 0.5, fontSize: '9px' }}>v1</span>
        </div>
        {currentInfo?.nearestPoint && (
          <div style={{ fontSize: '10px', color: scoreToColor(currentInfo.nearestPoint.score) }}>
            {currentInfo.nearestPoint.name} — {currentInfo.nearestPoint.score}%
          </div>
        )}
      </div>

      {/* Progress bar */}
      <div
        onClick={handleProgressClick}
        data-testid="replay-progress-bar"
        style={{
          height: '8px',
          background: 'rgba(255,255,255,0.1)',
          borderRadius: '4px',
          cursor: 'pointer',
          marginBottom: '10px',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${progress * 100}%`,
            background: 'linear-gradient(90deg, #3b82f6, #22c55e)',
            borderRadius: '4px',
            transition: isPlaying ? 'none' : 'width 0.15s',
          }}
        />
      </div>

      {/* Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
          {/* Play / Pause */}
          <button
            onClick={handlePlayPause}
            data-testid="replay-play-pause"
            style={{
              width: '30px', height: '30px', borderRadius: '50%',
              background: isPlaying ? '#ef4444' : '#3b82f6',
              border: 'none', color: '#fff', cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '14px', fontWeight: 700,
              transition: 'background 0.2s',
            }}
          >
            {isPlaying ? '||' : '\u25B6'}
          </button>

          {/* Reset */}
          <button
            onClick={handleReset}
            data-testid="replay-reset"
            style={{
              width: '28px', height: '28px', borderRadius: '6px',
              background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.15)',
              color: '#9ca3af', cursor: 'pointer', fontSize: '12px',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}
          >
            &#8634;
          </button>

          {/* Speed selector */}
          <div style={{ display: 'flex', gap: '3px' }}>
            {[1, 2, 5, 10].map((s) => (
              <button
                key={s}
                data-testid={`replay-speed-${s}`}
                onClick={() => {
                  setSpeed(s);
                  if (isPlaying) startTimeRef.current = performance.now() - (progress * 30000) / s;
                }}
                style={{
                  padding: '3px 8px', borderRadius: '4px', fontSize: '10px', fontWeight: 600,
                  border: speed === s ? '1px solid #3b82f6' : '1px solid rgba(255,255,255,0.15)',
                  background: speed === s ? 'rgba(59,130,246,0.25)' : 'transparent',
                  color: speed === s ? '#93c5fd' : '#6b7280',
                  cursor: 'pointer', transition: 'all 0.15s',
                }}
              >
                x{s}
              </button>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div style={{ fontSize: '10px', textAlign: 'right', color: '#9ca3af' }}>
          <div>
            {currentInfo ? currentInfo.distKm.toFixed(1) : '0.0'} / {totalDist.toFixed(1)} km
          </div>
          <div style={{ color: currentInfo ? scoreToColor(currentInfo.score) : '#6b7280' }}>
            Score: {currentInfo?.score ?? '—'}%
          </div>
        </div>
      </div>
    </div>
  );
}
