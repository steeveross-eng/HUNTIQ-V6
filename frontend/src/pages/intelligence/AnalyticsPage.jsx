/**
 * INTELLIGENCE — Analytics Page
 * ================================
 * Vue consolidée multi-moteurs. Auto-adaptative via Engine Registry.
 * STEEVE-MAX: dark palette, micro-typography, modular.
 */
import { useEffect } from 'react';
import useBionicStore from '@/stores/useBionicStore';
import { BarChart3, AlertTriangle, CheckCircle, ArrowRight } from 'lucide-react';

const URGENCY_COLORS = {
  CRITIQUE: 'text-red-400 bg-red-500/10 border-red-500/20',
  HAUTE: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
  MOYENNE: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  FAIBLE: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
};

const CLASSE_COLORS = {
  OPTIMAL: 'text-red-400', BON: 'text-amber-400',
  MODERE: 'text-emerald-400', FAIBLE: 'text-blue-400',
};

export default function AnalyticsPage() {
  const { summary, registry, location, species, month, loading, fetchSummary, fetchRegistry } = useBionicStore();

  useEffect(() => {
    fetchRegistry();
  }, [fetchRegistry]);

  useEffect(() => {
    if (location) fetchSummary();
  }, [location, species, month, fetchSummary]);

  // Coordonnées par défaut si pas de localisation
  useEffect(() => {
    const store = useBionicStore.getState();
    if (!store.location) {
      store.setLocation({ lat: 46.8139, lng: -71.2080 });
    }
  }, []);

  return (
    <div className="min-h-screen bg-[#0c0c14] text-gray-200 p-6" data-testid="analytics-page">
      <div className="max-w-5xl mx-auto space-y-6">

        {/* Header */}
        <div className="flex items-center gap-3">
          <BarChart3 className="w-5 h-5 text-cyan-400" />
          <h1 className="text-lg font-semibold tracking-tight">Analytics</h1>
          <span className="text-[10px] text-gray-600 ml-auto">
            {species} | Mois {month} | {registry?.total_engines || 0} moteurs
          </span>
        </div>

        {loading && !summary && (
          <div className="text-center text-gray-600 text-sm py-12">Chargement...</div>
        )}

        {summary && (
          <>
            {/* Score consolidé */}
            <div className="bg-[#12121e] border border-gray-800/50 rounded-lg p-5" data-testid="analytics-consolidated">
              <div className="flex items-baseline gap-3">
                <span className={`text-4xl font-bold tracking-tight ${CLASSE_COLORS[summary.consolidated.classe]}`}>
                  {summary.consolidated.score}
                </span>
                <span className="text-gray-500 text-sm">/100</span>
                <span className={`text-xs px-2 py-0.5 rounded ${CLASSE_COLORS[summary.consolidated.classe]} bg-white/5`}>
                  {summary.consolidated.label}
                </span>
              </div>
              <div className="mt-3 flex gap-4 text-[10px] text-gray-500">
                <span>Fort: <span className="text-emerald-400">{summary.analysis.strongest_engine}</span> ({summary.analysis.strongest_score})</span>
                <span>Faible: <span className="text-orange-400">{summary.analysis.weakest_engine}</span> ({summary.analysis.weakest_score})</span>
              </div>
            </div>

            {/* Moteurs par domaine */}
            <div className="grid grid-cols-2 gap-3" data-testid="analytics-domains">
              {Object.entries(summary.domains).map(([domain, engines]) => (
                <div key={domain} className="bg-[#12121e] border border-gray-800/50 rounded-lg p-4">
                  <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">{domain}</div>
                  {engines.map(eng => (
                    <div key={eng.engine} className="flex items-center justify-between py-1.5">
                      <span className="text-xs text-gray-300">{eng.engine}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-20 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full bg-gradient-to-r from-blue-500 via-emerald-500 to-amber-500"
                            style={{ width: `${eng.score}%` }}
                          />
                        </div>
                        <span className="text-[10px] text-gray-400 w-8 text-right">{eng.score}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>

            {/* Recommandations */}
            {summary.recommendations.length > 0 && (
              <div className="space-y-2" data-testid="analytics-recommendations">
                <div className="text-[10px] text-gray-500 uppercase tracking-wider">Recommandations</div>
                {summary.recommendations.map((rec, i) => (
                  <div key={i} className={`flex items-center gap-3 px-3 py-2 rounded border ${URGENCY_COLORS[rec.priority]}`}>
                    {rec.priority === 'HAUTE' || rec.priority === 'CRITIQUE'
                      ? <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
                      : <CheckCircle className="w-3.5 h-3.5 flex-shrink-0" />}
                    <span className="text-xs flex-1">{rec.action}</span>
                    <ArrowRight className="w-3 h-3 opacity-40" />
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
