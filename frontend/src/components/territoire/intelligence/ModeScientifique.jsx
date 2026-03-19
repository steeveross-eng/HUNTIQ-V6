/**
 * Mode SCIENTIFIQUE — Terrain Premium + Lisibilite Premium
 * Section X: polices agrandies, texte eclairci, espacement optimise.
 * Palette: cream #F2E9D8, sand-gray #C8BBA6, forest #4A7A2E, earth #A8885E.
 */
import { useEffect, useState } from 'react';
import { Database, Scale } from 'lucide-react';

const P = {
  cream: '#F2E9D8', creamDim: '#C8BBA6',
  forestLight: '#4A7A2E',
  earth: '#8B6F47', earthLight: '#A8885E',
  sand: '#C2A97E', sandLight: '#D4C4A0',
  rock: '#9CA3AF', rockDim: '#6B7280',
  bionic: '#D97706',
};

export default function ModeScientifique({ location, species, month }) {
  const [data, setData] = useState(null);
  const API = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    if (!location) return;
    const params = new URLSearchParams({ lat: location.lat, lng: location.lng, species, month });
    fetch(`${API}/api/v3/intelligence/scientifique?${params}`)
      .then(r => r.json()).then(setData).catch(() => {});
  }, [location, species, month, API]);

  if (!data) return <div className="text-base py-12 text-center font-medium" style={{ color: P.creamDim }}>Chargement...</div>;

  return (
    <div className="space-y-5" data-testid="mode-scientifique">
      {/* Score consolide */}
      <div className="rounded-lg p-5" style={{ background: 'rgba(45,80,22,0.08)', border: '1px solid rgba(139,111,71,0.15)' }}>
        <div className="flex items-center gap-2.5 mb-3">
          <Scale className="w-5 h-5" style={{ color: P.sand }} />
          <span className="text-base uppercase tracking-wider font-bold" style={{ color: P.cream }}>Consolidation</span>
        </div>
        <div className="text-5xl font-black" style={{ color: P.cream }}>{data.consolidated.score}<span className="text-lg font-medium" style={{ color: P.rockDim }}>/100</span></div>
        <div className="text-sm mt-2 font-mono font-medium" style={{ color: P.creamDim }}>{data.formulas.consolidation}</div>
        <div className="text-sm mt-1 font-medium" style={{ color: P.creamDim }}>{data.formulas.classification}</div>
      </div>

      {/* Moteurs detailles */}
      <div className="space-y-3">
        {data.engines.map(eng => (
          <div key={eng.name} className="rounded-lg p-5" style={{ background: 'rgba(139,111,71,0.05)', border: '1px solid rgba(139,111,71,0.12)' }}>
            <div className="flex items-center justify-between mb-3">
              <div>
                <span className="text-lg font-semibold" style={{ color: P.cream }}>{eng.name}</span>
                <span className="text-sm ml-3 font-medium" style={{ color: P.creamDim }}>v{eng.version} | {eng.domain} | {eng.engine_type}</span>
              </div>
              <span className="text-2xl font-bold" style={{ color: P.forestLight }}>{eng.score}</span>
            </div>
            <div className="flex gap-4 text-sm font-medium" style={{ color: P.creamDim }}>
              <span>Poids: <span className="font-mono font-semibold" style={{ color: P.cream }}>{(eng.weight_in_consolidation * 100).toFixed(1)}%</span></span>
              <span>Defaut: {(eng.default_weight * 100).toFixed(0)}%</span>
              <span>Especes: {eng.species_supported.length}</span>
              {eng.seasonal_modifiers && <span style={{ color: P.bionic }}>Saisonnier</span>}
            </div>
            {Object.keys(eng.components).length > 0 && (
              <div className="mt-3 flex gap-2.5 flex-wrap">
                {Object.entries(eng.components).map(([k, v]) => {
                  let dv;
                  if (typeof v === 'object' && v !== null) {
                    dv = v.score != null ? v.score.toFixed?.(1) || v.score : JSON.stringify(v).slice(0, 20);
                  } else if (typeof v === 'number') {
                    dv = v.toFixed?.(1) || v;
                  } else {
                    dv = String(v);
                  }
                  return (
                    <span key={k} className="text-xs px-2.5 py-1 rounded font-mono font-medium" style={{ background: 'rgba(45,80,22,0.1)', color: P.cream }}>{k}: {dv}</span>
                  );
                })}
              </div>
            )}
            <div className="text-sm mt-2 font-medium" style={{ color: P.creamDim }}>{eng.description}</div>
          </div>
        ))}
      </div>

      {/* BCE-4X Metadata */}
      <div className="rounded-lg p-5" style={{ background: 'rgba(45,80,22,0.05)', border: '1px solid rgba(74,122,46,0.1)' }}>
        <div className="flex items-center gap-2.5 mb-3">
          <Database className="w-5 h-5" style={{ color: P.earth }} />
          <span className="text-base uppercase tracking-wider font-bold" style={{ color: P.cream }}>Metadonnees BCE-4X</span>
        </div>
        <div className="text-sm font-mono space-y-1.5 font-medium" style={{ color: P.creamDim }}>
          <div>Version: {data.bce4x.version}</div>
          <div>Especes: {data.bce4x.species_canonical.join(', ')}</div>
          <div>Consolidateur: {data.bce4x.tracability.consolidator}</div>
          <div>Moteurs actifs: {data.bce4x.tracability.engines_active.join(', ')}</div>
        </div>
      </div>
    </div>
  );
}
