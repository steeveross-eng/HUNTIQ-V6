/**
 * SolunarChart SUPRA-INTELLIGENT — Version conceptuelle premium
 * ==============================================================
 * Section 6: HEURES HOT integrees (heures exactes, courbe coloree,
 *   badges premium, lecture immediate, halo temps reel, mini-legende).
 * Section 7: Profondeur 3D, animations, hierarchie visuelle premium.
 * Palette: sable clair #F2E9D8, vert foret #4A7A2E, brun terre #A8885E,
 *   orange/rouge pour HOT segments.
 * STEEVE-MAX: zero pollution, cockpit cartesien, terrain premium.
 */
import { useMemo, useState, useEffect } from 'react';

const W = 780, H = 240, PAD = 44;
const PW = W - PAD * 2, PH = H - 50;

const C = {
  cream: '#F2E9D8', creamDim: '#D4C4A0',
  forest: '#2D5016', forestLight: '#4A7A2E', forestGlow: '#6EAE42',
  earth: '#8B6F47', earthLight: '#A8885E', earthDim: '#5C4A30',
  sand: '#C2A97E', sandLight: '#D4C4A0', sandDim: '#9A8560',
  rock: '#6B7280', rockLight: '#9CA3AF', rockDim: '#4B5563',
  bionic: '#D97706', bionicGlow: '#F59E0B', bionicDim: '#92400E',
  curve: '#4A7A2E', curveGlow: '#6EAE42', curveShadow: '#1A3A0A',
};

const HOT_COLORS = {
  faible: { stroke: '#EAB308', glow: '#FDE047', badge: '#EAB308', factor: 0.4 },
  modere: { stroke: '#F59E0B', glow: '#FBBF24', badge: '#F59E0B', factor: 0.6 },
  'modéré': { stroke: '#F59E0B', glow: '#FBBF24', badge: '#F59E0B', factor: 0.6 },
  fort: { stroke: '#EA580C', glow: '#FB923C', badge: '#EA580C', factor: 0.8 },
  extreme: { stroke: '#DC2626', glow: '#F87171', badge: '#DC2626', factor: 0.95 },
  'extrême': { stroke: '#DC2626', glow: '#F87171', badge: '#DC2626', factor: 0.95 },
};

function getHot(intensity) {
  const k = (intensity || '').toLowerCase();
  return HOT_COLORS[k] || HOT_COLORS.faible;
}

export default function SolunarChart({ solunar }) {
  const curve = solunar?.curve_24h || [];
  const periods = solunar?.periods || {};
  const sun = solunar?.sun || {};
  const moon = solunar?.moon || {};
  const hw = solunar?.hunting_windows || [];
  const sScore = solunar?.solunar_score || 0;
  const [now, setNow] = useState(new Date());
  const [tooltip, setTooltip] = useState(null);

  useEffect(() => {
    const iv = setInterval(() => setNow(new Date()), 60000);
    return () => clearInterval(iv);
  }, []);

  const currentH = now.getHours() + now.getMinutes() / 60;
  const parseH = (t) => { if (!t) return null; const p = t.split(':'); return +p[0] + (+p[1] || 0) / 60; };
  const toX = (h) => PAD + (h / 24) * PW;
  const sunriseH = parseH(sun.rise) || 6;
  const sunsetH = parseH(sun.set) || 18;
  const maxAlt = useMemo(() => Math.max(...curve.map(p => Math.abs(p.moon_altitude)), 30), [curve]);

  const getYAt = (hour) => {
    if (!curve.length) return H / 2;
    const cl = curve.reduce((a, b) => Math.abs(b.hour - hour) < Math.abs(a.hour - hour) ? b : a);
    return H / 2 + 5 - (cl.moon_altitude / maxAlt) * (PH / 2);
  };

  const points = useMemo(() => {
    if (!curve.length) return '';
    return curve.map((p, i) => {
      const x = PAD + (p.hour / 24) * PW;
      const y = H / 2 + 5 - (p.moon_altitude / maxAlt) * (PH / 2);
      return `${i === 0 ? 'M' : 'L'}${x},${y}`;
    }).join(' ');
  }, [curve, maxAlt]);

  const currentAlt = useMemo(() => getYAt(currentH), [curve, currentH, maxAlt]);

  const bestWindow = useMemo(() => {
    const majors = periods.major || [];
    if (majors.length > 0) {
      const day = majors.find(p => p.start_h >= sunriseH && p.end_h <= sunsetH);
      return day || majors[0];
    }
    return null;
  }, [periods, sunriseH, sunsetH]);

  const markers = useMemo(() => {
    const m = [];
    if (moon.overhead) m.push({ h: parseH(moon.overhead), label: 'OH', y: 18 });
    if (moon.underfoot) m.push({ h: parseH(moon.underfoot), label: 'UF', y: H - 42 });
    if (moon.rise) m.push({ h: parseH(moon.rise), label: 'LV', y: H / 2 + 5 });
    if (moon.set) m.push({ h: parseH(moon.set), label: 'CO', y: H / 2 + 5 });
    return m;
  }, [moon]);

  const currentHotWin = useMemo(() => {
    return hw.find(w => {
      const s = parseH(w.start), e = parseH(w.end);
      return s != null && e != null && currentH >= s && currentH <= e;
    });
  }, [hw, currentH]);

  return (
    <div className="relative" data-testid="solunar-chart">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ filter: 'drop-shadow(0 4px 12px rgba(0,0,0,0.4))' }}>
        <defs>
          {/* Topographic background pattern */}
          <pattern id="topoPat" width="60" height="60" patternUnits="userSpaceOnUse">
            <path d="M0 30 Q15 22 30 30 T60 30" fill="none" stroke={C.forest} strokeWidth="0.3" opacity="0.12" />
            <path d="M0 45 Q15 38 30 45 T60 45" fill="none" stroke={C.earth} strokeWidth="0.2" opacity="0.08" />
            <path d="M0 15 Q15 9 30 15 T60 15" fill="none" stroke={C.forest} strokeWidth="0.2" opacity="0.06" />
          </pattern>
          {/* Glass container gradient */}
          <linearGradient id="glassGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="rgba(22,18,12,0.82)" />
            <stop offset="100%" stopColor="rgba(16,14,10,0.78)" />
          </linearGradient>
          {/* Bionic band gradient */}
          <linearGradient id="bionicBand" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={C.sand} stopOpacity="0.03" />
            <stop offset="25%" stopColor={C.bionic} stopOpacity="0.14" />
            <stop offset="75%" stopColor={C.bionic} stopOpacity="0.14" />
            <stop offset="100%" stopColor={C.earthDim} stopOpacity="0.03" />
          </linearGradient>
          {/* 3D curve shadow filter */}
          <filter id="curveShadow3D">
            <feGaussianBlur stdDeviation="2.5" />
          </filter>
          {/* Curve glow filter */}
          <filter id="curveGlow">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
          {/* Pointer glow (normal) */}
          <radialGradient id="ptrGlow">
            <stop offset="0%" stopColor={C.curveGlow} stopOpacity="0.85" />
            <stop offset="100%" stopColor={C.curveGlow} stopOpacity="0" />
          </radialGradient>
          {/* Pointer glow (HOT) */}
          {currentHotWin && (
            <radialGradient id="ptrGlowHot">
              <stop offset="0%" stopColor={getHot(currentHotWin.intensity).glow} stopOpacity="0.95" />
              <stop offset="40%" stopColor={getHot(currentHotWin.intensity).stroke} stopOpacity="0.4" />
              <stop offset="100%" stopColor={getHot(currentHotWin.intensity).stroke} stopOpacity="0" />
            </radialGradient>
          )}
          {/* Intensity gradient bar */}
          <linearGradient id="intensGrad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor={C.rockDim} />
            <stop offset="40%" stopColor={C.forest} />
            <stop offset="70%" stopColor={C.bionic} />
            <stop offset="100%" stopColor="#DC2626" />
          </linearGradient>
          {/* Curve fill gradient (3D depth) */}
          <linearGradient id="curveFillGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={C.forestLight} stopOpacity="0.12" />
            <stop offset="100%" stopColor={C.forestLight} stopOpacity="0" />
          </linearGradient>
          {/* HOT clip paths */}
          {hw.map((w, i) => {
            const sx = toX(parseH(w.start) || 0);
            const ex = toX(parseH(w.end) || 0);
            return (
              <clipPath key={`hc-${i}`} id={`hc-${i}`}>
                <rect x={sx} y={0} width={Math.max(3, ex - sx)} height={H} />
              </clipPath>
            );
          })}
        </defs>

        {/* ══ CONTAINER GLASS ══ */}
        <rect x="0" y="0" width={W} height={H} fill="url(#glassGrad)" rx="10" />
        <rect x="0" y="0" width={W} height={H} fill="url(#topoPat)" rx="10" />
        <rect x="0" y="0" width={W} height={H} fill="none" stroke={C.earth} strokeWidth="0.6" opacity="0.15" rx="10" />

        {/* ══ HIERARCHY: Moon phase (top-left) + Score (top-right) ══ */}
        <g>
          <circle cx={PAD - 8} cy={16} r={5} fill="none" stroke={C.sand} strokeWidth="1" opacity="0.7" />
          <circle cx={PAD - 6} cy={16} r={4} fill={C.earth} opacity="0.15" />
          <text x={PAD + 4} y={19} fill={C.cream} fontSize={8.5} fontWeight="bold" letterSpacing="0.08em">{(moon.phase_name || 'LUNE').toUpperCase()} — {moon.illumination || 0}%</text>
        </g>
        <text x={W - PAD} y={19} fill={C.earthLight} fontSize={8} textAnchor="end" fontWeight="bold" letterSpacing="0.05em">Score solunaire: {sScore.toFixed?.(1) || sScore}</text>

        {/* ══ DAY ZONE ══ */}
        <rect x={toX(sunriseH)} y={24} width={toX(sunsetH) - toX(sunriseH)} height={H - 54} fill={C.sand} opacity={0.035} rx={3} />

        {/* ══ MAJOR PERIODS (background) ══ */}
        {(periods.major || []).filter(p => p.start_h != null).map((p, i) => (
          <rect key={`maj-${i}`} x={toX(p.start_h)} y={26} width={Math.max(3, toX(p.end_h) - toX(p.start_h))} height={H - 56} fill={C.bionic} opacity={0.07} rx={4} />
        ))}
        {(periods.minor || []).filter(p => p.start_h != null).map((p, i) => (
          <rect key={`min-${i}`} x={toX(p.start_h)} y={32} width={Math.max(3, toX(p.end_h) - toX(p.start_h))} height={H - 64} fill={C.sand} opacity={0.05} rx={3} />
        ))}

        {/* ══ HEURE BIONIC DE CHASSE — glowing band ══ */}
        {bestWindow && (
          <g>
            <rect x={toX(bestWindow.start_h)} y={26} width={toX(bestWindow.end_h) - toX(bestWindow.start_h)} height={H - 56} fill="url(#bionicBand)" rx={4}>
              <animate attributeName="opacity" values="0.65;1;0.65" dur="3.5s" repeatCount="indefinite" />
            </rect>
            <rect x={toX(bestWindow.start_h)} y={26} width={toX(bestWindow.end_h) - toX(bestWindow.start_h)} height={H - 56} fill="none" stroke={C.bionic} strokeWidth="0.7" opacity="0.35" rx={4} strokeDasharray="4,3" />
          </g>
        )}

        {/* ══ HORIZON ══ */}
        <line x1={PAD} y1={H / 2 + 5} x2={W - PAD} y2={H / 2 + 5} stroke={C.earth} strokeWidth={0.5} strokeDasharray="6,5" opacity={0.3} />

        {/* ══ 3D DEPTH: Shadow copy of curve (Section 7a) ══ */}
        <path d={points} fill="none" stroke={C.curveShadow} strokeWidth={3.5} opacity={0.25} transform="translate(1.2, 2.5)" filter="url(#curveShadow3D)" />

        {/* ══ CURVE FILL (depth gradient) ══ */}
        {points && (
          <path d={`${points} L${W - PAD},${H / 2 + 5} L${PAD},${H / 2 + 5} Z`} fill="url(#curveFillGrad)" opacity={0.6} />
        )}

        {/* ══ MAIN CURVE — glow + line with breathing animation ══ */}
        <path d={points} fill="none" stroke={C.curveGlow} strokeWidth={4} opacity={0.15} filter="url(#curveGlow)" />
        <path d={points} fill="none" stroke={C.curve} strokeWidth={2}>
          <animate attributeName="stroke-width" values="1.8;2.2;1.8" dur="4s" repeatCount="indefinite" />
        </path>

        {/* ══ SECTION 6: HEURES HOT — Colored curve segments + badges + hours ══ */}
        {hw.map((w, i) => {
          const hs = getHot(w.intensity);
          const startH2 = parseH(w.start) || 0;
          const endH2 = parseH(w.end) || 0;
          const midH = (startH2 + endH2) / 2;
          const sx = toX(startH2);
          const ex = toX(endH2);
          const midX = toX(midH);
          const startY = getYAt(startH2);
          const endY = getYAt(endH2);
          const midY = getYAt(midH);
          const badgeScore = Math.round(sScore * hs.factor);
          return (
            <g key={`hot-${i}`}
              onMouseEnter={() => setTooltip({ x: midX, text: `${w.start}-${w.end} | ${w.intensity} | ${w.source} | ${w.duration_min}min` })}
              onMouseLeave={() => setTooltip(null)}
              style={{ cursor: 'pointer' }}
            >
              {/* 6b: Colored curve segment — thick, following curve */}
              <path d={points} fill="none" stroke={hs.glow} strokeWidth={10} clipPath={`url(#hc-${i})`} opacity={0.12} filter="url(#curveGlow)" />
              <path d={points} fill="none" stroke={hs.stroke} strokeWidth={4.5} clipPath={`url(#hc-${i})`} opacity={0.9}>
                <animate attributeName="opacity" values="0.75;1;0.75" dur="2s" repeatCount="indefinite" />
              </path>

              {/* Vertical markers — start + end */}
              <line x1={sx} y1={28} x2={sx} y2={H - 30} stroke={hs.stroke} strokeWidth={0.8} strokeDasharray="3,2" opacity={0.5} />
              <line x1={ex} y1={28} x2={ex} y2={H - 30} stroke={hs.stroke} strokeWidth={0.8} strokeDasharray="3,2" opacity={0.5} />

              {/* 6a: Exact hours — visible immediately, positioned near curve */}
              <text x={sx + 2} y={startY > H / 2 ? startY - 6 : startY + 12} fill={C.cream} fontSize={7} fontWeight="bold" textAnchor="start" opacity={0.9}>{w.start}</text>
              <text x={ex - 2} y={endY > H / 2 ? endY - 6 : endY + 12} fill={C.cream} fontSize={7} fontWeight="bold" textAnchor="end" opacity={0.9}>{w.end}</text>

              {/* 6c: Premium badge — HOT score above peak */}
              <rect x={midX - 22} y={midY - 26} width={44} height={17} rx={4} fill="rgba(22,18,12,0.75)" stroke={hs.stroke} strokeWidth={0.8} opacity={0.9} />
              <text x={midX} y={midY - 14} fill={hs.badge} fontSize={7.5} textAnchor="middle" fontWeight="bold">HOT {badgeScore}/100</text>
            </g>
          );
        })}

        {/* ══ HOUR TICKS ══ */}
        {[0, 3, 6, 9, 12, 15, 18, 21, 24].map(h => (
          <g key={h}>
            <line x1={toX(h)} y1={H - 30} x2={toX(h)} y2={H - 34} stroke={C.rock} strokeWidth={0.5} />
            <text x={toX(h)} y={H - 20} fill={C.rockLight} fontSize={7} textAnchor="middle" fontFamily="monospace">{`${h}h`}</text>
          </g>
        ))}

        {/* ══ SOLUNAR MARKERS ══ */}
        {markers.map((m, i) => m.h != null && (
          <g key={i} style={{ cursor: 'pointer' }}
            onMouseEnter={() => setTooltip({ x: toX(m.h), text: `${m.label} ${Math.floor(m.h)}h${Math.round((m.h % 1) * 60).toString().padStart(2, '0')}` })}
            onMouseLeave={() => setTooltip(null)}
          >
            <line x1={toX(m.h)} y1={28} x2={toX(m.h)} y2={H - 32} stroke={C.earth} strokeWidth={0.3} strokeDasharray="2,4" opacity={0.4} />
            <text x={toX(m.h)} y={m.y} fill={C.earthLight} fontSize={6.5} textAnchor="middle" fontWeight="bold">{m.label}</text>
          </g>
        ))}

        {/* ══ CURRENT TIME POINTER — animated (Section 6e + 7c) ══ */}
        {currentHotWin ? (
          <g>
            <line x1={toX(currentH)} y1={26} x2={toX(currentH)} y2={H - 30} stroke={getHot(currentHotWin.intensity).glow} strokeWidth={2} opacity={0.85}>
              <animate attributeName="opacity" values="0.5;1;0.5" dur="0.8s" repeatCount="indefinite" />
            </line>
            <circle cx={toX(currentH)} cy={currentAlt} r={14} fill="url(#ptrGlowHot)">
              <animate attributeName="r" values="12;16;12" dur="0.8s" repeatCount="indefinite" />
            </circle>
            <circle cx={toX(currentH)} cy={currentAlt} r={4.5} fill={getHot(currentHotWin.intensity).glow} stroke={C.cream} strokeWidth={1}>
              <animate attributeName="r" values="4;5.5;4" dur="0.8s" repeatCount="indefinite" />
            </circle>
            <text x={toX(currentH)} y={currentAlt - 10} fill={getHot(currentHotWin.intensity).glow} fontSize={7} fontWeight="bold" textAnchor="middle">{Math.floor(currentH)}h{Math.round((currentH % 1) * 60).toString().padStart(2, '0')}</text>
          </g>
        ) : (
          <g>
            <line x1={toX(currentH)} y1={26} x2={toX(currentH)} y2={H - 30} stroke={C.curveGlow} strokeWidth={1.2} opacity={0.7}>
              <animate attributeName="opacity" values="0.4;0.9;0.4" dur="2s" repeatCount="indefinite" />
            </line>
            <circle cx={toX(currentH)} cy={currentAlt} r={9} fill="url(#ptrGlow)" />
            <circle cx={toX(currentH)} cy={currentAlt} r={3.5} fill={C.curveGlow} stroke={C.cream} strokeWidth={0.8}>
              <animate attributeName="r" values="3;4;3" dur="2s" repeatCount="indefinite" />
            </circle>
            <text x={toX(currentH)} y={currentAlt - 8} fill={C.curveGlow} fontSize={6.5} fontWeight="bold" textAnchor="middle">{Math.floor(currentH)}h{Math.round((currentH % 1) * 60).toString().padStart(2, '0')}</text>
          </g>
        )}

        {/* ══ INTENSITY BAR ══ */}
        <rect x={PAD} y={H - 14} width={PW} height={5} fill={C.rockDim} rx={2.5} opacity={0.25} />
        <rect x={PAD} y={H - 14} width={PW * (sScore / 100)} height={5} fill="url(#intensGrad)" rx={2.5} />
        <circle cx={PAD + PW * (sScore / 100)} cy={H - 11.5} r={3.5} fill={C.bionicGlow} stroke={C.cream} strokeWidth={0.6} />

        {/* ══ TOOLTIP ══ */}
        {tooltip && (
          <g>
            <rect x={Math.max(5, Math.min(tooltip.x - 65, W - 135))} y={H - 50} width={130} height={18} fill="rgba(22,18,12,0.9)" rx={4} stroke={C.earth} strokeWidth="0.5" opacity="0.95" />
            <text x={Math.max(70, Math.min(tooltip.x, W - 70))} y={H - 38} fill={C.cream} fontSize={7} textAnchor="middle" fontWeight="bold">{tooltip.text}</text>
          </g>
        )}
      </svg>

      {/* ══ HEURE BIONIC DE CHASSE — central premium label ══ */}
      {bestWindow && (
        <div className="absolute top-1 left-1/2 -translate-x-1/2 flex items-center gap-1.5 px-4 py-1 rounded-b-lg"
          style={{
            background: 'linear-gradient(135deg, rgba(217,119,6,0.18), rgba(146,64,14,0.12))',
            borderBottom: `1px solid rgba(217,119,6,0.3)`,
            backdropFilter: 'blur(8px)',
          }}
        >
          <span className="text-[9px] font-bold tracking-[0.18em] uppercase" style={{ color: C.bionicGlow }}>HEURE BIONIC DE CHASSE</span>
        </div>
      )}

      {/* ══ SECTION 6f: Mini-legende premium ══ */}
      <div className="flex items-center gap-3 mt-2 px-1 flex-wrap">
        <span className="flex items-center gap-1 text-[7px] font-bold" style={{ color: C.rock }}>
          <span className="w-4 h-1.5 rounded-sm" style={{ background: HOT_COLORS.faible.stroke }} />Faible
        </span>
        <span className="flex items-center gap-1 text-[7px] font-bold" style={{ color: C.rock }}>
          <span className="w-4 h-1.5 rounded-sm" style={{ background: HOT_COLORS.modere.stroke }} />Modere
        </span>
        <span className="flex items-center gap-1 text-[7px] font-bold" style={{ color: C.rock }}>
          <span className="w-4 h-1.5 rounded-sm" style={{ background: HOT_COLORS.fort.stroke }} />Fort
        </span>
        <span className="flex items-center gap-1 text-[7px] font-bold" style={{ color: C.rock }}>
          <span className="w-4 h-1.5 rounded-sm" style={{ background: HOT_COLORS.extreme.stroke }} />Extreme
        </span>
        <span className="text-[6px] mx-1" style={{ color: C.rockDim }}>|</span>
        <span className="flex items-center gap-1 text-[7px]" style={{ color: C.rock }}>
          <span className="w-3 h-0.5" style={{ background: 'rgba(217,119,6,0.5)' }} />Bionic
        </span>
        <span className="flex items-center gap-1 text-[7px]" style={{ color: C.rock }}>
          <span className="w-2 h-2 rounded-full" style={{ background: C.curveGlow }} />Temps reel
        </span>
      </div>
    </div>
  );
}
