/**
 * INTELLIGENCE — Plan Maitre Page
 * ==================================
 * Actions recommandées pour optimiser le territoire.
 * STEEVE-MAX: dark palette, priorisé, auto-adaptatif.
 */
import { useEffect } from 'react';
import useBionicStore from '@/stores/useBionicStore';
import { ClipboardList, AlertTriangle, CheckCircle, Shield, TrendingDown } from 'lucide-react';

const URGENCY_STYLES = {
  CRITIQUE: { color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/30', Icon: AlertTriangle },
  HAUTE: { color: 'text-orange-400', bg: 'bg-orange-500/10', border: 'border-orange-500/30', Icon: TrendingDown },
  MOYENNE: { color: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', Icon: Shield },
  FAIBLE: { color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', Icon: CheckCircle },
};

const CLASSE_COLORS = {
  OPTIMAL: 'text-red-400', BON: 'text-amber-400',
  MODERE: 'text-emerald-400', FAIBLE: 'text-blue-400',
};

export default function PlanMaitrePage() {
  const { plan, location, species, month, loading, fetchPlan, fetchRegistry } = useBionicStore();

  useEffect(() => { fetchRegistry(); }, [fetchRegistry]);

  useEffect(() => {
    if (location) fetchPlan();
  }, [location, species, month, fetchPlan]);

  useEffect(() => {
    const store = useBionicStore.getState();
    if (!store.location) store.setLocation({ lat: 46.8139, lng: -71.2080 });
  }, []);

  return (
    <div className="min-h-screen bg-[#0c0c14] text-gray-200 p-6" data-testid="plan-maitre-page">
      <div className="max-w-5xl mx-auto space-y-6">

        {/* Header */}
        <div className="flex items-center gap-3">
          <ClipboardList className="w-5 h-5 text-violet-400" />
          <h1 className="text-lg font-semibold tracking-tight">Plan Maitre</h1>
          <span className="text-[10px] text-gray-600 ml-auto">{species} | Mois {month}</span>
        </div>

        {loading && !plan && (
          <div className="text-center text-gray-600 text-sm py-12">Chargement du plan...</div>
        )}

        {plan && (
          <>
            {/* Score global */}
            <div className="bg-[#12121e] border border-gray-800/50 rounded-lg p-5" data-testid="plan-overall">
              <div className="flex items-baseline gap-3">
                <span className={`text-4xl font-bold tracking-tight ${CLASSE_COLORS[plan.overall_classe]}`}>
                  {plan.overall_score}
                </span>
                <span className="text-gray-500 text-sm">/100</span>
                <span className="text-xs text-gray-500">{plan.overall_classe}</span>
              </div>
              <div className="mt-2 text-[10px] text-gray-500">
                {plan.critical_count} action{plan.critical_count > 1 ? 's' : ''} prioritaire{plan.critical_count > 1 ? 's' : ''} sur {plan.total_actions}
              </div>
            </div>

            {/* Actions ordonnées */}
            <div className="space-y-2" data-testid="plan-actions">
              {plan.actions.map((action) => {
                const style = URGENCY_STYLES[action.urgency] || URGENCY_STYLES.FAIBLE;
                const { Icon } = style;
                return (
                  <div
                    key={action.rank}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg border ${style.bg} ${style.border}`}
                  >
                    <div className={`flex items-center justify-center w-6 h-6 rounded-full ${style.bg} ${style.color}`}>
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className={`text-xs font-medium ${style.color}`}>{action.engine}</span>
                        <span className="text-[8px] text-gray-600">{action.domain}</span>
                      </div>
                      <div className="text-[10px] text-gray-400 mt-0.5">{action.action}</div>
                    </div>
                    <div className="text-right flex-shrink-0">
                      <div className="text-sm font-bold">{action.score}</div>
                      <div className={`text-[8px] ${style.color}`}>{action.urgency}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
