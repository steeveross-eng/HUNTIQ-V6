/**
 * SolunarChart — Courbe lunaire 24h type LUNASOLCAL
 * Axe horizontal = 24h, ligne médiane = horizon.
 * Périodes majeures (rouge), mineures (orange), jour (jaune).
 */
import { useMemo } from 'react';

const W = 700, H = 180, PAD = 40;
const PLOT_W = W - PAD * 2, PLOT_H = H - 30;

export default function SolunarChart({ solunar }) {
  const curve = solunar?.curve_24h || [];
  const periods = solunar?.periods || {};
  const sun = solunar?.sun || {};

  const points = useMemo(() => {
    if (!curve.length) return '';
    const maxAlt = Math.max(...curve.map(p => Math.abs(p.moon_altitude)), 30);
    return curve.map((p, i) => {
      const x = PAD + (p.hour / 24) * PLOT_W;
      const y = H / 2 - (p.moon_altitude / maxAlt) * (PLOT_H / 2);
      return `${i === 0 ? 'M' : 'L'}${x},${y}`;
    }).join(' ');
  }, [curve]);

  const parseH = (t) => { if (!t) return null; const [h, m] = t.split(':'); return +h + m / 60; };
  const toX = (h) => PAD + (h / 24) * PLOT_W;

  const sunriseH = parseH(sun.rise) || 6;
  const sunsetH = parseH(sun.set) || 18;

  const renderPeriods = (list, color, opacity) =>
    (list || []).filter(p => p.start_h != null).map((p, i) => (
      <rect key={`${color}-${i}`} x={toX(p.start_h)} y={4} width={toX(p.end_h) - toX(p.start_h)}
        height={H - 8} fill={color} opacity={opacity} rx={2} />
    ));

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" data-testid="solunar-chart">
      {/* Fond jour */}
      <rect x={toX(sunriseH)} y={0} width={toX(sunsetH) - toX(sunriseH)} height={H}
        fill="#FBBF24" opacity={0.04} />

      {/* Périodes majeures / mineures */}
      {renderPeriods(periods.major, '#DC2626', 0.15)}
      {renderPeriods(periods.minor, '#F59E0B', 0.1)}

      {/* Horizon */}
      <line x1={PAD} y1={H / 2} x2={W - PAD} y2={H / 2} stroke="#374151" strokeWidth={1} strokeDasharray="4,4" />

      {/* Courbe lunaire */}
      <path d={points} fill="none" stroke="#60A5FA" strokeWidth={2} />

      {/* Axes heures */}
      {[0, 3, 6, 9, 12, 15, 18, 21, 24].map(h => (
        <g key={h}>
          <line x1={toX(h)} y1={H - 18} x2={toX(h)} y2={H - 22} stroke="#4B5563" strokeWidth={0.5} />
          <text x={toX(h)} y={H - 6} fill="#6B7280" fontSize={8} textAnchor="middle">{`${h}h`}</text>
        </g>
      ))}

      {/* Marqueurs events */}
      {solunar?.moon?.overhead && (
        <g>
          <circle cx={toX(parseH(solunar.moon.overhead))} cy={10} r={3} fill="#DC2626" />
          <text x={toX(parseH(solunar.moon.overhead))} y={20} fill="#EF4444" fontSize={7} textAnchor="middle">OH</text>
        </g>
      )}
      {solunar?.moon?.underfoot && (
        <g>
          <circle cx={toX(parseH(solunar.moon.underfoot))} cy={H - 26} r={3} fill="#DC2626" />
          <text x={toX(parseH(solunar.moon.underfoot))} y={H - 30} fill="#EF4444" fontSize={7} textAnchor="middle">UF</text>
        </g>
      )}
      {solunar?.moon?.rise && (
        <g>
          <circle cx={toX(parseH(solunar.moon.rise))} cy={H / 2} r={2.5} fill="#F59E0B" />
          <text x={toX(parseH(solunar.moon.rise))} y={H / 2 - 6} fill="#F59E0B" fontSize={7} textAnchor="middle">LV</text>
        </g>
      )}
      {solunar?.moon?.set && (
        <g>
          <circle cx={toX(parseH(solunar.moon.set))} cy={H / 2} r={2.5} fill="#F59E0B" />
          <text x={toX(parseH(solunar.moon.set))} y={H / 2 - 6} fill="#F59E0B" fontSize={7} textAnchor="middle">CO</text>
        </g>
      )}

      {/* Label */}
      <text x={PAD} y={12} fill="#9CA3AF" fontSize={8}>Altitude lune (°)</text>
    </svg>
  );
}
