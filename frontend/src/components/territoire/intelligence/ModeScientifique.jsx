/**
 * Mode SCIENTIFIQUE — Pondérations, coefficients, formules, métadonnées BCE-4X
 */
import { useEffect, useState } from 'react';
import { FlaskConical, Database, Scale } from 'lucide-react';

export default function ModeScientifique({ location, species, month }) {
  const [data, setData] = useState(null);
  const API = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    if (!location) return;
    const params = new URLSearchParams({ lat: location.lat, lng: location.lng, species, month });
    fetch(`${API}/api/v3/intelligence/scientifique?${params}`)
      .then(r => r.json()).then(setData).catch(() => {});
  }, [location, species, month, API]);

  if (!data) return <div className="text-gray-600 text-sm py-8 text-center">Chargement...</div>;

  return (
    <div className="space-y-4" data-testid="mode-scientifique">
      {/* Score consolidé */}
      <div className="bg-[#12121e] border border-gray-800/50 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-3">
          <Scale className="w-4 h-4 text-cyan-400" />
          <span className="text-[10px] text-gray-400 uppercase tracking-wider">Consolidation</span>
        </div>
        <div className="text-3xl font-bold">{data.consolidated.score}<span className="text-sm text-gray-500">/100</span></div>
        <div className="text-[9px] text-gray-600 mt-1 font-mono">{data.formulas.consolidation}</div>
        <div className="text-[8px] text-gray-600 mt-0.5">{data.formulas.classification}</div>
      </div>

      {/* Moteurs détaillés */}
      <div className="space-y-2">
        {data.engines.map(eng => (
          <div key={eng.name} className="bg-[#12121e] border border-gray-800/50 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <div>
                <span className="text-xs font-medium text-gray-200">{eng.name}</span>
                <span className="text-[8px] text-gray-600 ml-2">v{eng.version} | {eng.domain} | {eng.engine_type}</span>
              </div>
              <span className="text-sm font-bold">{eng.score}</span>
            </div>
            <div className="flex gap-2 text-[8px] text-gray-500">
              <span>Poids: <span className="text-cyan-400 font-mono">{(eng.weight_in_consolidation * 100).toFixed(1)}%</span></span>
              <span>Défaut: {(eng.default_weight * 100).toFixed(0)}%</span>
              <span>Espèces: {eng.species_supported.length}</span>
              {eng.seasonal_modifiers && <span className="text-amber-500">Saisonnier</span>}
            </div>
            {Object.keys(eng.components).length > 0 && (
              <div className="mt-1.5 flex gap-2 flex-wrap">
                {Object.entries(eng.components).map(([k, v]) => {
                  // Handle nested objects (e.g., {score: 3.01, raw: 1.003, saison_mult: 0.6})
                  let displayValue;
                  if (typeof v === 'object' && v !== null) {
                    // Extract the score if it exists, otherwise stringify
                    displayValue = v.score != null ? v.score.toFixed?.(1) || v.score : JSON.stringify(v).slice(0, 20);
                  } else if (typeof v === 'number') {
                    displayValue = v.toFixed?.(1) || v;
                  } else {
                    displayValue = String(v);
                  }
                  return (
                    <span key={k} className="text-[7px] bg-gray-800 px-1.5 py-0.5 rounded font-mono">{k}: {displayValue}</span>
                  );
                })}
              </div>
            )}
            <div className="text-[7px] text-gray-700 mt-1">{eng.description}</div>
          </div>
        ))}
      </div>

      {/* BCE-4X Metadata */}
      <div className="bg-[#12121e] border border-gray-800/50 rounded-lg p-3">
        <div className="flex items-center gap-2 mb-2">
          <Database className="w-3.5 h-3.5 text-violet-400" />
          <span className="text-[10px] text-gray-400 uppercase tracking-wider">Métadonnées BCE-4X</span>
        </div>
        <div className="text-[8px] font-mono text-gray-500 space-y-0.5">
          <div>Version: {data.bce4x.version}</div>
          <div>Espèces: {data.bce4x.species_canonical.join(', ')}</div>
          <div>Consolidateur: {data.bce4x.tracability.consolidator}</div>
          <div>Moteurs actifs: {data.bce4x.tracability.engines_active.join(', ')}</div>
        </div>
      </div>
    </div>
  );
}
