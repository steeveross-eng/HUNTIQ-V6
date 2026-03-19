/**
 * Mode SCIENTIFIQUE — Terrain Premium
 * =============================================
 * Ponderations, coefficients, formules, metadonnees BCE-4X.
 * Palette: vert foret, brun terre, sable, gris roche.
 * STEEVE-MAX: zero pollution, hierarchie terrain premium.
 */
import { useEffect, useState } from 'react';
import { FlaskConical, Database, Scale } from 'lucide-react';

const TP = {
  forestLight: '#4A7A2E',
  earth: '#8B6F47', earthLight: '#A8885E',
  sand: '#C2A97E', sandLight: '#D4C4A0',
  rock: '#6B7280', rockLight: '#9CA3AF', rockDim: '#4B5563',
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

  if (!data) return <div className="text-sm py-8 text-center font-mono" style={{ color: TP.rock }}>Chargement...</div>;

  return (
    <div className="space-y-4" data-testid="mode-scientifique">
      {/* Score consolide */}
      <div className="rounded-lg p-4" style={{ background: 'rgba(45,80,22,0.06)', border: '1px solid rgba(139,111,71,0.12)' }}>
        <div className="flex items-center gap-2 mb-3">
          <Scale className="w-4 h-4" style={{ color: TP.sand }} />
          <span className="text-[10px] uppercase tracking-wider" style={{ color: TP.earthLight }}>Consolidation</span>
        </div>
        <div className="text-3xl font-bold" style={{ color: TP.sandLight }}>{data.consolidated.score}<span className="text-sm" style={{ color: TP.rock }}>/100</span></div>
        <div className="text-[9px] mt-1 font-mono" style={{ color: TP.rockDim }}>{data.formulas.consolidation}</div>
        <div className="text-[8px] mt-0.5" style={{ color: TP.rockDim }}>{data.formulas.classification}</div>
      </div>

      {/* Moteurs detailles */}
      <div className="space-y-2">
        {data.engines.map(eng => (
          <div key={eng.name} className="rounded-lg p-3" style={{ background: 'rgba(139,111,71,0.04)', border: '1px solid rgba(139,111,71,0.1)' }}>
            <div className="flex items-center justify-between mb-2">
              <div>
                <span className="text-xs font-medium" style={{ color: TP.sandLight }}>{eng.name}</span>
                <span className="text-[8px] ml-2" style={{ color: TP.rockDim }}>v{eng.version} | {eng.domain} | {eng.engine_type}</span>
              </div>
              <span className="text-sm font-bold" style={{ color: TP.forestLight }}>{eng.score}</span>
            </div>
            <div className="flex gap-2 text-[8px]" style={{ color: TP.rock }}>
              <span>Poids: <span className="font-mono" style={{ color: TP.sand }}>{(eng.weight_in_consolidation * 100).toFixed(1)}%</span></span>
              <span>Defaut: {(eng.default_weight * 100).toFixed(0)}%</span>
              <span>Especes: {eng.species_supported.length}</span>
              {eng.seasonal_modifiers && <span style={{ color: TP.bionic }}>Saisonnier</span>}
            </div>
            {Object.keys(eng.components).length > 0 && (
              <div className="mt-1.5 flex gap-2 flex-wrap">
                {Object.entries(eng.components).map(([k, v]) => {
                  let displayValue;
                  if (typeof v === 'object' && v !== null) {
                    displayValue = v.score != null ? v.score.toFixed?.(1) || v.score : JSON.stringify(v).slice(0, 20);
                  } else if (typeof v === 'number') {
                    displayValue = v.toFixed?.(1) || v;
                  } else {
                    displayValue = String(v);
                  }
                  return (
                    <span key={k} className="text-[7px] px-1.5 py-0.5 rounded font-mono" style={{ background: 'rgba(45,80,22,0.08)', color: TP.rockLight }}>{k}: {displayValue}</span>
                  );
                })}
              </div>
            )}
            <div className="text-[7px] mt-1" style={{ color: TP.rockDim }}>{eng.description}</div>
          </div>
        ))}
      </div>

      {/* BCE-4X Metadata */}
      <div className="rounded-lg p-3" style={{ background: 'rgba(45,80,22,0.04)', border: '1px solid rgba(74,122,46,0.08)' }}>
        <div className="flex items-center gap-2 mb-2">
          <Database className="w-3.5 h-3.5" style={{ color: TP.earth }} />
          <span className="text-[10px] uppercase tracking-wider" style={{ color: TP.earthLight }}>Metadonnees BCE-4X</span>
        </div>
        <div className="text-[8px] font-mono space-y-0.5" style={{ color: TP.rock }}>
          <div>Version: {data.bce4x.version}</div>
          <div>Especes: {data.bce4x.species_canonical.join(', ')}</div>
          <div>Consolidateur: {data.bce4x.tracability.consolidator}</div>
          <div>Moteurs actifs: {data.bce4x.tracability.engines_active.join(', ')}</div>
        </div>
      </div>
    </div>
  );
}
