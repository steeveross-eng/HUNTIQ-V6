/**
 * NutritionPanel — Panneau recommandations nutritionnelles ALIMENTATION-V2
 * ========================================================================
 * Extrait de MonTerritoireBionicPage (STEEVE-MAX refactoring P0).
 */
import { X, Droplets } from 'lucide-react';

export function NutritionPanel({ alimentationV2Data, onClose }) {
  if (!alimentationV2Data) return null;
  return (
    <div className="fixed right-4 top-24 w-80 max-h-[70vh] bg-gray-950/95 backdrop-blur-md border border-gray-700/60 rounded-xl shadow-2xl shadow-black/50 overflow-hidden z-[1001]" data-testid="nutrition-panel">
      <div className="px-4 py-3 border-b border-gray-700/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Droplets className="h-4 w-4 text-yellow-400" />
          <span className="text-sm font-bold text-white">Recommandations</span>
        </div>
        <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors" data-testid="close-nutrition-panel"><X className="h-4 w-4" /></button>
      </div>
      <div className="p-3 overflow-y-auto max-h-[60vh] space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400">{alimentationV2Data.species_nom}</span>
          <span className="text-sm font-bold text-yellow-400">{alimentationV2Data.score_global}/100</span>
        </div>
        {alimentationV2Data.carences_detectees?.length > 0 && (
          <div className="space-y-1">
            <div className="text-[9px] font-bold uppercase tracking-wider text-red-400">Carences detectees</div>
            {alimentationV2Data.carences_detectees.map((c, i) => (
              <div key={i} className="flex items-center justify-between text-xs bg-red-500/10 rounded px-2 py-1">
                <span className="text-red-300">{c.element}</span>
                <span className="text-red-400 font-bold">-{c.deficit_pct}%</span>
              </div>
            ))}
          </div>
        )}
        <div className="space-y-1">
          <div className="text-[9px] font-bold uppercase tracking-wider text-green-400">Aliments recommandes</div>
          {alimentationV2Data.nutrition?.aliments_recommandes?.map((a, i) => (
            <div key={i} className="text-xs bg-gray-800/50 rounded px-2 py-1">
              <div className="flex items-center justify-between">
                <span className="text-white font-medium">{a.nom}</span>
                <span className={`text-[9px] px-1.5 rounded ${a.priorite === 'haute' ? 'bg-red-500/20 text-red-300' : 'bg-gray-700 text-gray-400'}`}>{a.priorite}</span>
              </div>
              <div className="text-[10px] text-gray-500">{a.saison} — {a.apport}</div>
            </div>
          ))}
        </div>
        {alimentationV2Data.nutrition?.proteines && (
          <div className="space-y-1">
            <div className="text-[9px] font-bold uppercase tracking-wider text-blue-400">Proteines</div>
            <div className="text-xs text-gray-300">Besoin: <span className="text-blue-300 font-bold">{alimentationV2Data.nutrition.proteines.besoin_pct}%</span></div>
            <div className="text-[10px] text-gray-500">{alimentationV2Data.nutrition.proteines.note}</div>
          </div>
        )}
        <div className="space-y-1">
          <div className="text-[9px] font-bold uppercase tracking-wider text-purple-400">Oligo-elements</div>
          {alimentationV2Data.nutrition?.oligo_elements?.map((o, i) => (
            <div key={i} className="flex items-center justify-between text-xs bg-gray-800/50 rounded px-2 py-1">
              <span className="text-gray-300">{o.nom}</span>
              <span className="text-purple-300 text-[10px]">{o.besoin_mg_jour} mg/j</span>
            </div>
          ))}
        </div>
        {alimentationV2Data.nutrition?.saline_composition && !alimentationV2Data.salines_disabled && (
          <div className="space-y-1">
            <div className="text-[9px] font-bold uppercase tracking-wider text-yellow-400">Composition saline recommandee</div>
            <div className="grid grid-cols-2 gap-1">
              {Object.entries(alimentationV2Data.nutrition.saline_composition).map(([k, v]) => (
                <div key={k} className="text-[10px] bg-yellow-500/10 rounded px-2 py-0.5">
                  <span className="text-gray-400">{k.replace('_pct', ' %').replace('_ppm', ' ppm').replace('_', ' ')}: </span>
                  <span className="text-yellow-300 font-bold">{v}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        {alimentationV2Data.salines_disabled && alimentationV2Data.salines_message && (
          <div className="px-3 py-2 bg-amber-900/20 border border-amber-700/30 rounded-lg" data-testid="nutrition-panel-salines-message">
            <div className="text-[10px] text-amber-300/90 leading-relaxed">{alimentationV2Data.salines_message}</div>
          </div>
        )}
        {alimentationV2Data.nutrition?.carences_locales?.length > 0 && (
          <div className="space-y-1">
            <div className="text-[9px] font-bold uppercase tracking-wider text-orange-400">Carences locales (Quebec)</div>
            {alimentationV2Data.nutrition.carences_locales.map((c, i) => (
              <div key={i} className="text-[10px] text-orange-300/80 pl-2 border-l border-orange-500/30">{c}</div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
