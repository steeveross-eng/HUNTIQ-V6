/**
 * INTELLIGENCE — Forecast Page
 * ================================
 * Prévisions écologiques — variation saisonnière sur 12 mois.
 * STEEVE-MAX: dark palette, micro-typography, chart bars.
 */
import { useEffect } from 'react';
import useBionicStore from '@/stores/useBionicStore';
import { TrendingUp, Sun, Snowflake, Leaf, Flower2 } from 'lucide-react';

const SEASON_ICONS = {
  printemps: Flower2, ete: Sun, automne: Leaf, hiver: Snowflake,
};
const SEASON_COLORS = {
  printemps: 'text-green-400', ete: 'text-amber-400', automne: 'text-orange-400', hiver: 'text-blue-400',
};
const MONTH_LABELS = ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec'];

export default function ForecastPage() {
  const { forecast, location, species, loading, fetchForecast, fetchRegistry } = useBionicStore();

  useEffect(() => { fetchRegistry(); }, [fetchRegistry]);

  useEffect(() => {
    if (location) fetchForecast();
  }, [location, species, fetchForecast]);

  useEffect(() => {
    const store = useBionicStore.getState();
    if (!store.location) store.setLocation({ lat: 46.8139, lng: -71.2080 });
  }, []);

  return (
    <div className="min-h-screen bg-[#0c0c14] text-gray-200 p-6" data-testid="forecast-page">
      <div className="max-w-5xl mx-auto space-y-6">

        {/* Header */}
        <div className="flex items-center gap-3">
          <TrendingUp className="w-5 h-5 text-amber-400" />
          <h1 className="text-lg font-semibold tracking-tight">Forecast</h1>
          <span className="text-[10px] text-gray-600 ml-auto">{species}</span>
        </div>

        {loading && !forecast && (
          <div className="text-center text-gray-600 text-sm py-12">Chargement des previsions...</div>
        )}

        {forecast && (
          <>
            {/* Résumé annuel */}
            <div className="bg-[#12121e] border border-gray-800/50 rounded-lg p-5" data-testid="forecast-annual">
              <div className="flex items-baseline gap-3">
                <span className="text-3xl font-bold tracking-tight text-amber-400">{forecast.annual_average}</span>
                <span className="text-gray-500 text-sm">/100 moyenne annuelle</span>
              </div>
              <div className="mt-2 flex gap-4 text-[10px] text-gray-500">
                <span>Meilleur: <span className="text-emerald-400">Mois {forecast.best_month}</span></span>
                <span>Pire: <span className="text-red-400">Mois {forecast.worst_month}</span></span>
                <span>Saison: <span className="text-cyan-400">{forecast.best_season}</span></span>
              </div>
            </div>

            {/* Graphique barres 12 mois */}
            <div className="bg-[#12121e] border border-gray-800/50 rounded-lg p-5" data-testid="forecast-chart">
              <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-4">Variation mensuelle</div>
              <div className="flex items-end gap-1.5 h-40">
                {forecast.monthly_data.map((m) => {
                  const h = Math.max(4, (m.score / 100) * 100);
                  const isBest = m.month === forecast.best_month;
                  const isWorst = m.month === forecast.worst_month;
                  return (
                    <div key={m.month} className="flex-1 flex flex-col items-center gap-1">
                      <span className="text-[8px] text-gray-500">{m.score}</span>
                      <div
                        className={`w-full rounded-t transition-all ${
                          isBest ? 'bg-emerald-500' : isWorst ? 'bg-red-500/80' : 'bg-cyan-800/60'
                        }`}
                        style={{ height: `${h}%` }}
                      />
                      <span className={`text-[8px] ${isBest ? 'text-emerald-400' : isWorst ? 'text-red-400' : 'text-gray-600'}`}>
                        {MONTH_LABELS[m.month - 1]}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Saisons */}
            <div className="grid grid-cols-4 gap-3" data-testid="forecast-seasons">
              {Object.entries(forecast.seasonal_scores).map(([season, score]) => {
                const Icon = SEASON_ICONS[season] || Sun;
                const color = SEASON_COLORS[season] || 'text-gray-400';
                const isBest = season === forecast.best_season;
                return (
                  <div key={season} className={`bg-[#12121e] border rounded-lg p-4 text-center ${
                    isBest ? 'border-cyan-600/40' : 'border-gray-800/50'
                  }`}>
                    <Icon className={`w-4 h-4 mx-auto mb-2 ${color}`} />
                    <div className="text-xl font-bold">{score}</div>
                    <div className="text-[9px] text-gray-500 uppercase mt-1">{season}</div>
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
