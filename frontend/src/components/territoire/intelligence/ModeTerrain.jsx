/**
 * Mode TERRAIN — Terrain Premium + Lisibilite Premium
 * Section X: polices agrandies, texte eclairci, espacement optimise.
 * Palette: cream #F2E9D8, sand-gray #C8BBA6, forest #4A7A2E, earth #A8885E.
 */
import { useEffect, useState } from 'react';
import { MapPin, AlertTriangle, CheckCircle } from 'lucide-react';

const P = {
  cream: '#F2E9D8', creamDim: '#C8BBA6',
  forestLight: '#4A7A2E',
  sand: '#C2A97E', sandLight: '#D4C4A0',
  rock: '#9CA3AF', rockDim: '#6B7280',
  bionic: '#D97706', bionicGlow: '#F59E0B',
};

const CLASSE_STYLES = {
  OPTIMAL: { color: P.bionicGlow, bg: 'rgba(217,119,6,0.12)' },
  BON: { color: P.forestLight, bg: 'rgba(74,122,46,0.12)' },
  MODERE: { color: P.sand, bg: 'rgba(194,169,126,0.1)' },
  FAIBLE: { color: P.rock, bg: 'rgba(156,163,175,0.08)' },
};

export default function ModeTerrain({ location, species, month }) {
  const [data, setData] = useState(null);
  const API = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    if (!location) return;
    const params = new URLSearchParams({ lat: location.lat, lng: location.lng, species, month });
    fetch(`${API}/api/v3/intelligence/summary?${params}`)
      .then(r => r.json()).then(setData).catch(() => {});
  }, [location, species, month, API]);

  if (!data) return <div className="text-base py-12 text-center font-medium" style={{ color: P.creamDim }}>Chargement...</div>;

  const c = data.consolidated;
  const cs = CLASSE_STYLES[c.classe] || CLASSE_STYLES.FAIBLE;

  return (
    <div className="space-y-5" data-testid="mode-terrain">
      {/* Score principal */}
      <div className="p-8 rounded-lg text-center" style={{ background: cs.bg }}>
        <div className="text-7xl font-black tracking-tighter" style={{ color: cs.color }}>{c.score}</div>
        <div className="text-2xl font-bold mt-2" style={{ color: cs.color }}>{c.label}</div>
        <div className="text-base mt-2 font-medium" style={{ color: P.creamDim }}>{species} | Mois {month}</div>
      </div>

      {/* Conditions essentielles */}
      <div className="grid grid-cols-2 gap-3">
        {Object.entries(data.domains).map(([domain, engines]) => {
          const avgScore = Math.round(engines.reduce((s, e) => s + e.score, 0) / engines.length);
          return (
            <div key={domain} className="rounded-lg p-5 text-center" style={{ background: 'rgba(45,80,22,0.07)', border: '1px solid rgba(139,111,71,0.12)' }}>
              <div className="text-3xl font-bold" style={{ color: P.cream }}>{avgScore}</div>
              <div className="text-sm uppercase font-medium mt-1" style={{ color: P.creamDim }}>{domain}</div>
            </div>
          );
        })}
      </div>

      {/* Recommandations */}
      {data.recommendations.length > 0 && (
        <div className="space-y-2">
          {data.recommendations.slice(0, 3).map((r, i) => (
            <div key={i} className="flex items-center gap-3 px-4 py-3.5 rounded-lg"
              style={r.priority === 'HAUTE'
                ? { border: '1px solid rgba(217,119,6,0.35)', background: 'rgba(217,119,6,0.1)', color: P.bionic }
                : { border: '1px solid rgba(139,111,71,0.2)', background: 'rgba(139,111,71,0.06)', color: P.creamDim }
              }
            >
              {r.priority === 'HAUTE' ? <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                : <CheckCircle className="w-5 h-5 flex-shrink-0" />}
              <span className="text-base font-medium">{r.action}</span>
            </div>
          ))}
        </div>
      )}

      {/* Position */}
      <div className="flex items-center gap-2 text-sm font-medium" style={{ color: P.creamDim }}>
        <MapPin className="w-4 h-4" />
        <span>{location?.lat?.toFixed(4)}, {location?.lng?.toFixed(4)}</span>
      </div>
    </div>
  );
}
