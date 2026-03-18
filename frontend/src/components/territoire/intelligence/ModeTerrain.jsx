/**
 * Mode TERRAIN — Vue simplifiée, ultra-lisible, optimisée mobile/hors réseau
 */
import { useEffect, useState } from 'react';
import { Compass, Wind, MapPin, AlertTriangle, CheckCircle } from 'lucide-react';

const CLASSE_STYLES = {
  OPTIMAL: 'text-red-400 bg-red-500/10', BON: 'text-amber-400 bg-amber-500/10',
  MODERE: 'text-emerald-400 bg-emerald-500/10', FAIBLE: 'text-blue-400 bg-blue-500/10',
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

  if (!data) return <div className="text-gray-600 text-sm py-8 text-center">Chargement...</div>;

  const c = data.consolidated;

  return (
    <div className="space-y-4" data-testid="mode-terrain">
      {/* Score principal - GROS */}
      <div className={`p-6 rounded-lg text-center ${CLASSE_STYLES[c.classe]}`}>
        <div className="text-6xl font-black tracking-tighter">{c.score}</div>
        <div className="text-lg font-bold mt-1">{c.label}</div>
        <div className="text-[10px] opacity-60 mt-1">{species} | Mois {month}</div>
      </div>

      {/* Conditions essentielles */}
      <div className="grid grid-cols-2 gap-2">
        {Object.entries(data.domains).map(([domain, engines]) => {
          const avgScore = Math.round(engines.reduce((s, e) => s + e.score, 0) / engines.length);
          return (
            <div key={domain} className="bg-[#12121e] border border-gray-800/50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold">{avgScore}</div>
              <div className="text-[9px] text-gray-500 uppercase mt-0.5">{domain}</div>
            </div>
          );
        })}
      </div>

      {/* Recommandations essentielles */}
      {data.recommendations.length > 0 && (
        <div className="space-y-1.5">
          {data.recommendations.slice(0, 3).map((r, i) => (
            <div key={i} className={`flex items-center gap-2 px-3 py-2.5 rounded-lg border ${
              r.priority === 'HAUTE' ? 'border-orange-500/30 bg-orange-500/10' : 'border-gray-700/30 bg-gray-800/30'
            }`}>
              {r.priority === 'HAUTE' ? <AlertTriangle className="w-4 h-4 text-orange-400 flex-shrink-0" />
                : <CheckCircle className="w-4 h-4 text-gray-500 flex-shrink-0" />}
              <span className="text-xs">{r.action}</span>
            </div>
          ))}
        </div>
      )}

      {/* Position */}
      <div className="flex items-center gap-2 text-[9px] text-gray-600">
        <MapPin className="w-3 h-3" />
        <span>{location?.lat?.toFixed(4)}, {location?.lng?.toFixed(4)}</span>
      </div>
    </div>
  );
}
