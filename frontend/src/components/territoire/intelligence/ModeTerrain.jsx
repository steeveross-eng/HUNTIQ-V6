/**
 * Mode TERRAIN — Terrain Premium
 * ======================================
 * Vue simplifiee, ultra-lisible, optimisee mobile/hors reseau.
 * Palette: vert foret, brun terre, sable, gris roche.
 * STEEVE-MAX: zero pollution, hierarchie terrain premium.
 */
import { useEffect, useState } from 'react';
import { MapPin, AlertTriangle, CheckCircle } from 'lucide-react';

const TP = {
  forestLight: '#4A7A2E',
  earth: '#8B6F47', earthLight: '#A8885E',
  sand: '#C2A97E', sandLight: '#D4C4A0',
  rock: '#6B7280', rockDim: '#4B5563',
  bionic: '#D97706', bionicGlow: '#F59E0B',
};

const CLASSE_STYLES = {
  OPTIMAL: { color: TP.bionicGlow, bg: 'rgba(217,119,6,0.1)' },
  BON: { color: TP.forestLight, bg: 'rgba(74,122,46,0.1)' },
  MODERE: { color: TP.sand, bg: 'rgba(194,169,126,0.08)' },
  FAIBLE: { color: TP.rock, bg: 'rgba(107,114,128,0.08)' },
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

  if (!data) return <div className="text-sm py-8 text-center font-mono" style={{ color: TP.rock }}>Chargement...</div>;

  const c = data.consolidated;
  const cs = CLASSE_STYLES[c.classe] || CLASSE_STYLES.FAIBLE;

  return (
    <div className="space-y-4" data-testid="mode-terrain">
      {/* Score principal */}
      <div className="p-6 rounded-lg text-center" style={{ background: cs.bg }}>
        <div className="text-6xl font-black tracking-tighter" style={{ color: cs.color }}>{c.score}</div>
        <div className="text-lg font-bold mt-1" style={{ color: cs.color }}>{c.label}</div>
        <div className="text-[10px] mt-1" style={{ color: TP.rock, opacity: 0.6 }}>{species} | Mois {month}</div>
      </div>

      {/* Conditions essentielles */}
      <div className="grid grid-cols-2 gap-2">
        {Object.entries(data.domains).map(([domain, engines]) => {
          const avgScore = Math.round(engines.reduce((s, e) => s + e.score, 0) / engines.length);
          return (
            <div key={domain} className="rounded-lg p-3 text-center" style={{ background: 'rgba(45,80,22,0.06)', border: '1px solid rgba(139,111,71,0.1)' }}>
              <div className="text-2xl font-bold" style={{ color: TP.sandLight }}>{avgScore}</div>
              <div className="text-[9px] uppercase mt-0.5" style={{ color: TP.rock }}>{domain}</div>
            </div>
          );
        })}
      </div>

      {/* Recommandations essentielles */}
      {data.recommendations.length > 0 && (
        <div className="space-y-1.5">
          {data.recommendations.slice(0, 3).map((r, i) => (
            <div key={i} className="flex items-center gap-2 px-3 py-2.5 rounded-lg"
              style={r.priority === 'HAUTE'
                ? { border: '1px solid rgba(217,119,6,0.3)', background: 'rgba(217,119,6,0.08)', color: TP.bionic }
                : { border: '1px solid rgba(139,111,71,0.15)', background: 'rgba(139,111,71,0.05)', color: TP.rock }
              }
            >
              {r.priority === 'HAUTE' ? <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                : <CheckCircle className="w-4 h-4 flex-shrink-0" />}
              <span className="text-xs">{r.action}</span>
            </div>
          ))}
        </div>
      )}

      {/* Position */}
      <div className="flex items-center gap-2 text-[9px]" style={{ color: TP.rockDim }}>
        <MapPin className="w-3 h-3" />
        <span>{location?.lat?.toFixed(4)}, {location?.lng?.toFixed(4)}</span>
      </div>
    </div>
  );
}
