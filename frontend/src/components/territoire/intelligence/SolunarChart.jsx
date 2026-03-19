/**
 * SolunarChart SUPRA-INTELLIGENT — Courbe lunaire 24h premium
 * =============================================================
 * Palette: vert foret, brun terre, sable, gris roche.
 * Effet WOW: "HEURE BIONIC DE CHASSE" bande orange animee,
 * pointeur temporel anime, marqueurs premium, intensite graduee.
 * STEEVE-MAX: zero pollution, hierarchie claire, terrain premium.
 */
import { useMemo, useState, useEffect } from 'react';

const W = 780, H = 220, PAD = 44;
const PW = W - PAD * 2, PH = H - 40;

// Terrain premium palette
const C = {
  forest: '#2D5016', forestLight: '#4A7A2E', forestDim: '#1A3A0A',
  earth: '#8B6F47', earthLight: '#A8885E', earthDim: '#5C4A30',
  sand: '#C2A97E', sandLight: '#D4C4A0', sandDim: '#9A8560',
  rock: '#6B7280', rockLight: '#9CA3AF', rockDim: '#4B5563',
  bionic: '#D97706', bionicGlow: '#F59E0B', bionicDim: '#92400E',
  curve: '#4A7A2E', curveGlow: '#6EAE42',
};

export default function SolunarChart({ solunar }) {
  const curve = solunar?.curve_24h || [];
  const periods = solunar?.periods || {};
  const sun = solunar?.sun || {};
  const moon = solunar?.moon || {};
  const [now, setNow] = useState(new Date());
  const [tooltip, setTooltip] = useState(null);

  // Real-time pointer update
  useEffect(() => {
    const iv = setInterval(() => setNow(new Date()), 60000);
    return () => clearInterval(iv);
  }, []);

  const currentH = now.getHours() + now.getMinutes() / 60;
  const parseH = (t) => { if (!t) return null; const p = t.split(':'); return +p[0] + (+p[1] || 0) / 60; };
  const toX = (h) => PAD + (h / 24) * PW;
  const sunriseH = parseH(sun.rise) || 6;
  const sunsetH = parseH(sun.set) || 18;

  const points = useMemo(() => {
    if (!curve.length) return '';
    const maxAlt = Math.max(...curve.map(p => Math.abs(p.moon_altitude)), 30);
    return curve.map((p, i) => {
      const x = PAD + (p.hour / 24) * PW;
      const y = H / 2 - (p.moon_altitude / maxAlt) * (PH / 2);
      return `${i === 0 ? 'M' : 'L'}${x},${y}`;
    }).join(' ');
  }, [curve]);

  // Find current altitude for pointer dot position
  const currentAlt = useMemo(() => {
    if (!curve.length) return 0;
    const maxAlt = Math.max(...curve.map(p => Math.abs(p.moon_altitude)), 30);
    const closest = curve.reduce((a, b) => Math.abs(b.hour - currentH) < Math.abs(a.hour - currentH) ? b : a);
    return H / 2 - (closest.moon_altitude / maxAlt) * (PH / 2);
  }, [curve, currentH]);

  // Best hunting window (for HEURE BIONIC band)
  const bestWindow = useMemo(() => {
    const majors = periods.major || [];
    if (majors.length > 0) {
      // Find daylight major window
      const dayMajor = majors.find(p => p.start_h >= sunriseH && p.end_h <= sunsetH);
      return dayMajor || majors[0];
    }
    return null;
  }, [periods, sunriseH, sunsetH]);

  const markers = useMemo(() => {
    const m = [];
    if (moon.overhead) m.push({ h: parseH(moon.overhead), type: 'OH', label: 'Overhead', icon: 'full', y: 14 });
    if (moon.underfoot) m.push({ h: parseH(moon.underfoot), type: 'UF', label: 'Underfoot', icon: 'inv', y: H - 32 });
    if (moon.rise) m.push({ h: parseH(moon.rise), type: 'LV', label: 'Lever lune', icon: 'rise', y: H / 2 });
    if (moon.set) m.push({ h: parseH(moon.set), type: 'CO', label: 'Coucher lune', icon: 'set', y: H / 2 });
    return m;
  }, [moon]);

  const intensity = solunar?.solunar_score || 0;

  return (
    <div className="relative" data-testid="solunar-chart">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ filter: 'drop-shadow(0 2px 8px rgba(0,0,0,0.3))' }}>
        <defs>
          {/* Topographic texture */}
          <pattern id="topo" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M0 20 Q10 15 20 20 T40 20" fill="none" stroke={C.forest} strokeWidth="0.3" opacity="0.15" />
            <path d="M0 30 Q10 25 20 30 T40 30" fill="none" stroke={C.earth} strokeWidth="0.2" opacity="0.1" />
          </pattern>
          {/* BIONIC glow gradient */}
          <linearGradient id="bionicBand" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={C.sand} stopOpacity="0.05" />
            <stop offset="30%" stopColor={C.bionic} stopOpacity="0.18" />
            <stop offset="70%" stopColor={C.bionic} stopOpacity="0.18" />
            <stop offset="100%" stopColor={C.earthDim} stopOpacity="0.05" />
          </linearGradient>
          {/* Curve glow */}
          <filter id="curveGlow">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
          {/* Pointer glow */}
          <radialGradient id="ptrGlow">
            <stop offset="0%" stopColor={C.curveGlow} stopOpacity="0.8" />
            <stop offset="100%" stopColor={C.curveGlow} stopOpacity="0" />
          </radialGradient>
          {/* Intensity gradient */}
          <linearGradient id="intensGrad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor={C.rockDim} />
            <stop offset="50%" stopColor={C.forest} />
            <stop offset="100%" stopColor={C.bionic} />
          </linearGradient>
        </defs>

        {/* Background with topo texture */}
        <rect x="0" y="0" width={W} height={H} fill="url(#topo)" rx="8" />

        {/* Day zone */}
        <rect x={toX(sunriseH)} y={0} width={toX(sunsetH) - toX(sunriseH)} height={H - 26} fill={C.sand} opacity={0.04} rx={2} />

        {/* Major periods — thick segments */}
        {(periods.major || []).filter(p => p.start_h != null).map((p, i) => (
          <rect key={`maj-${i}`} x={toX(p.start_h)} y={8} width={Math.max(2, toX(p.end_h) - toX(p.start_h))} height={H - 36} fill={C.bionic} opacity={0.12} rx={3} />
        ))}
        {/* Minor periods — thin segments */}
        {(periods.minor || []).filter(p => p.start_h != null).map((p, i) => (
          <rect key={`min-${i}`} x={toX(p.start_h)} y={20} width={Math.max(2, toX(p.end_h) - toX(p.start_h))} height={H - 48} fill={C.sand} opacity={0.08} rx={2} />
        ))}

        {/* HEURE BIONIC DE CHASSE — glowing band */}
        {bestWindow && (
          <g>
            <rect x={toX(bestWindow.start_h)} y={4} width={toX(bestWindow.end_h) - toX(bestWindow.start_h)} height={H - 30} fill="url(#bionicBand)" rx={4}>
              <animate attributeName="opacity" values="0.7;1;0.7" dur="3.5s" repeatCount="indefinite" />
            </rect>
            <rect x={toX(bestWindow.start_h)} y={4} width={toX(bestWindow.end_h) - toX(bestWindow.start_h)} height={H - 30} fill="none" stroke={C.bionic} strokeWidth="0.8" opacity="0.4" rx={4} strokeDasharray="3,3" />
          </g>
        )}

        {/* Horizon line */}
        <line x1={PAD} y1={H / 2} x2={W - PAD} y2={H / 2} stroke={C.earth} strokeWidth={0.6} strokeDasharray="6,4" opacity={0.4} />

        {/* Moon curve with glow */}
        <path d={points} fill="none" stroke={C.curveGlow} strokeWidth={3} opacity={0.2} filter="url(#curveGlow)" />
        <path d={points} fill="none" stroke={C.curve} strokeWidth={1.8} />

        {/* Hour ticks */}
        {[0, 3, 6, 9, 12, 15, 18, 21, 24].map(h => (
          <g key={h}>
            <line x1={toX(h)} y1={H - 24} x2={toX(h)} y2={H - 28} stroke={C.rock} strokeWidth={0.5} />
            <text x={toX(h)} y={H - 14} fill={C.rockLight} fontSize={7} textAnchor="middle" fontFamily="monospace">{`${h}h`}</text>
          </g>
        ))}

        {/* Solunar markers with tooltips */}
        {markers.map((m, i) => m.h != null && (
          <g key={i} style={{ cursor: 'pointer' }}
            onMouseEnter={() => setTooltip({ x: toX(m.h), text: `${m.label} ${Math.floor(m.h)}h${Math.round((m.h % 1) * 60).toString().padStart(2, '0')}` })}
            onMouseLeave={() => setTooltip(null)}
          >
            <line x1={toX(m.h)} y1={8} x2={toX(m.h)} y2={H - 26} stroke={C.earth} strokeWidth={0.4} strokeDasharray="2,3" opacity={0.5} />
            {m.icon === 'full' && <circle cx={toX(m.h)} cy={m.y} r={5} fill={C.sand} stroke={C.earth} strokeWidth={1} />}
            {m.icon === 'inv' && <><circle cx={toX(m.h)} cy={m.y} r={5} fill="none" stroke={C.earth} strokeWidth={1} /><circle cx={toX(m.h) + 1.5} cy={m.y} r={4} fill="#0a0a12" /></>}
            {m.icon === 'rise' && <polygon points={`${toX(m.h) - 4},${m.y + 3} ${toX(m.h)},${m.y - 4} ${toX(m.h) + 4},${m.y + 3}`} fill={C.bionic} opacity={0.7} />}
            {m.icon === 'set' && <polygon points={`${toX(m.h) - 4},${m.y - 3} ${toX(m.h)},${m.y + 4} ${toX(m.h) + 4},${m.y - 3}`} fill={C.bionic} opacity={0.7} />}
            <text x={toX(m.h)} y={m.y + (m.icon === 'full' ? -9 : m.icon === 'inv' ? 14 : -8)} fill={C.earthLight} fontSize={6.5} textAnchor="middle" fontWeight="bold">{m.type}</text>
          </g>
        ))}

        {/* ANIMATED: Current time pointer */}
        <line x1={toX(currentH)} y1={4} x2={toX(currentH)} y2={H - 26} stroke={C.curveGlow} strokeWidth={1.2} opacity={0.8}>
          <animate attributeName="opacity" values="0.5;1;0.5" dur="2s" repeatCount="indefinite" />
        </line>
        <circle cx={toX(currentH)} cy={currentAlt} r={8} fill="url(#ptrGlow)" />
        <circle cx={toX(currentH)} cy={currentAlt} r={3.5} fill={C.curveGlow} stroke="#fff" strokeWidth={0.8}>
          <animate attributeName="r" values="3;4;3" dur="2s" repeatCount="indefinite" />
        </circle>

        {/* Intensity bar */}
        <rect x={PAD} y={H - 8} width={PW} height={4} fill={C.rockDim} rx={2} opacity={0.3} />
        <rect x={PAD} y={H - 8} width={PW * (intensity / 100)} height={4} fill="url(#intensGrad)" rx={2} />
        <circle cx={PAD + PW * (intensity / 100)} cy={H - 6} r={3} fill={C.bionicGlow} stroke="#fff" strokeWidth={0.5} />

        {/* Tooltip */}
        {tooltip && (
          <g>
            <rect x={tooltip.x - 40} y={2} width={80} height={16} fill={C.earthDim} rx={3} opacity={0.95} />
            <text x={tooltip.x} y={13} fill={C.sandLight} fontSize={7} textAnchor="middle" fontWeight="bold">{tooltip.text}</text>
          </g>
        )}
      </svg>

      {/* HEURE BIONIC DE CHASSE label */}
      {bestWindow && (
        <div className="absolute top-0 left-1/2 -translate-x-1/2 flex items-center gap-1.5 px-3 py-0.5 rounded-b-lg" style={{ background: 'linear-gradient(135deg, rgba(217,119,6,0.15), rgba(146,64,14,0.1))', borderBottom: `1px solid rgba(217,119,6,0.25)` }}>
          <span className="text-[8px] font-bold tracking-[0.15em] uppercase" style={{ color: C.bionicGlow }}>HEURE BIONIC DE CHASSE</span>
        </div>
      )}
    </div>
  );
}
