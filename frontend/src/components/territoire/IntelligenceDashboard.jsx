/**
 * IntelligenceDashboard — Tableau central INTELLIGENCE
 * ======================================================
 * Occupe toute la zone principale de MON TERRITOIRE.
 * 6 blocs: Analytics, Conditions, Forecast, Plan Maitre, Carte analytique, Donnees brutes.
 * 3 modes: Scientifique, Terrain, Guide Pro (solunaire).
 * Synchronisation bi-directionnelle carte <-> intelligence.
 * STEEVE-MAX: cockpit analytique, dark, cartesien, hierarchise.
 * BCE-4X: tracabilite, zero duplication, zero ambiguite.
 */
import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  X, FlaskConical, Compass, Crosshair, BarChart3,
  TrendingUp, ClipboardList, Layers, Database, Activity,
  MapPin, ChevronRight, AlertTriangle, CheckCircle, Zap,
} from 'lucide-react';
import useBionicStore from '@/stores/useBionicStore';
import ModeScientifique from './intelligence/ModeScientifique';
import ModeTerrain from './intelligence/ModeTerrain';
import ModeGuidePro from './intelligence/ModeGuidePro';

const MODES = [
  { id: 'guide', label: 'GUIDE PRO', Icon: Crosshair, color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
  { id: 'scientifique', label: 'SCIENTIFIQUE', Icon: FlaskConical, color: 'text-cyan-400', bg: 'bg-cyan-500/10 border-cyan-500/20' },
  { id: 'terrain', label: 'TERRAIN', Icon: Compass, color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20' },
];

const CLASSE_C = {
  OPTIMAL: { text: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/20' },
  BON: { text: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20' },
  MODERE: { text: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' },
  FAIBLE: { text: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/20' },
};

const URGENCY_C = {
  CRITIQUE: 'border-red-500/40 bg-red-500/10 text-red-300',
  HAUTE: 'border-orange-500/30 bg-orange-500/10 text-orange-300',
  MOYENNE: 'border-yellow-500/20 bg-yellow-500/5 text-yellow-300',
  FAIBLE: 'border-gray-700/30 bg-gray-800/30 text-gray-400',
};

export default function IntelligenceDashboard({ onClose, waypointCenter, selectedSpecies, currentMonth, onNavigateToPosition }) {
  const [activeMode, setActiveMode] = useState('guide');
  const [activeBlock, setActiveBlock] = useState('analytics');
  const {
    summary, forecast, plan, loading,
    fetchSummary, fetchForecast, fetchPlan,
    setLocation, setSpecies, setMonth,
  } = useBionicStore();

  // Sync carte -> intelligence
  useEffect(() => {
    if (waypointCenter) {
      setLocation({ lat: waypointCenter.lat, lng: waypointCenter.lng });
    }
  }, [waypointCenter, setLocation]);

  useEffect(() => { if (selectedSpecies) setSpecies(selectedSpecies); }, [selectedSpecies, setSpecies]);
  useEffect(() => { if (currentMonth) setMonth(currentMonth); }, [currentMonth, setMonth]);

  const location = useMemo(() => (
    waypointCenter ? { lat: waypointCenter.lat, lng: waypointCenter.lng } : null
  ), [waypointCenter]);

  const species = selectedSpecies || 'CHEVREUIL';
  const month = currentMonth || new Date().getMonth() + 1;

  // Fetch data based on active block
  useEffect(() => {
    if (!location) return;
    fetchSummary();
    fetchForecast();
    fetchPlan();
  }, [location, species, month, fetchSummary, fetchForecast, fetchPlan]);

  // Intelligence -> Carte : navigation vers position recommandee
  const handleNavigateToRecommendation = useCallback((lat, lng) => {
    if (onNavigateToPosition) onNavigateToPosition(lat, lng);
  }, [onNavigateToPosition]);

  const classeStyle = summary ? (CLASSE_C[summary.consolidated?.classe] || CLASSE_C.FAIBLE) : CLASSE_C.FAIBLE;

  return (
    <div className="flex-1 z-[1000] bg-[#0a0a12] overflow-hidden flex flex-col" data-testid="intelligence-dashboard">
      {/* ══ HEADER COCKPIT ══ */}
      <div className="flex-shrink-0 bg-[#0c0c16] border-b border-gray-800/40 px-4 py-2 flex items-center gap-3">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-cyan-400" />
          <span className="text-sm font-bold tracking-tight text-gray-100">INTELLIGENCE</span>
        </div>

        {/* Mode selector */}
        <div className="flex gap-0.5 ml-4 bg-[#080810] rounded-lg p-0.5 border border-gray-800/30">
          {MODES.map(m => (
            <button
              key={m.id}
              onClick={() => setActiveMode(m.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[10px] font-bold uppercase tracking-wider transition-all ${
                activeMode === m.id
                  ? `${m.color} ${m.bg} border`
                  : 'text-gray-500 hover:text-gray-300 border border-transparent'
              }`}
              data-testid={`mode-${m.id}`}
            >
              <m.Icon className="w-3 h-3" />{m.label}
            </button>
          ))}
        </div>

        {/* Location + Species badge */}
        <div className="ml-auto flex items-center gap-3 mr-3">
          {location && (
            <div className="flex items-center gap-1.5 text-[9px] text-gray-500">
              <MapPin className="w-3 h-3" />
              <span>{location.lat.toFixed(4)}, {location.lng.toFixed(4)}</span>
            </div>
          )}
          <span className="text-[9px] bg-gray-800/60 text-gray-400 px-2 py-0.5 rounded font-mono">{species}</span>
          <span className="text-[9px] bg-gray-800/60 text-gray-400 px-2 py-0.5 rounded font-mono">M{month}</span>
        </div>

        <button onClick={onClose} className="p-1.5 text-gray-500 hover:text-white transition-colors rounded hover:bg-white/5" data-testid="intelligence-close">
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* ══ MAIN CONTENT ══ */}
      <div className="flex-1 overflow-auto">
        {!location ? (
          <div className="flex flex-col items-center justify-center h-full gap-3">
            <Crosshair className="w-8 h-8 text-gray-600" />
            <div className="text-gray-500 text-sm">Selectionnez un waypoint pour activer INTELLIGENCE</div>
            <div className="text-gray-700 text-[10px]">Utilisez la carte pour cibler une position d'analyse</div>
          </div>
        ) : (
          <div className="p-4 max-w-7xl mx-auto space-y-4">
            {/* ══ BLOC 1: ANALYTICS — Score consolide + Domaines ══ */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-3" data-testid="block-analytics">
              {/* Score principal */}
              <div className={`${classeStyle.bg} border ${classeStyle.border} rounded-lg p-4 flex flex-col justify-center items-center`}>
                <div className="text-[9px] text-gray-500 uppercase tracking-wider mb-1">Score consolide</div>
                <div className={`text-5xl font-black tracking-tighter ${classeStyle.text}`}>
                  {summary?.consolidated?.score ?? '--'}
                </div>
                <div className={`text-sm font-bold mt-1 ${classeStyle.text}`}>
                  {summary?.consolidated?.label || '--'}
                </div>
                <div className="text-[8px] text-gray-600 mt-1">{summary?.engines_count || 0} moteurs actifs</div>
              </div>

              {/* Domaines */}
              <div className="lg:col-span-3 grid grid-cols-2 md:grid-cols-4 gap-2">
                {summary?.domains && Object.entries(summary.domains).map(([domain, engines]) => {
                  const avg = Math.round(engines.reduce((s, e) => s + e.score, 0) / engines.length);
                  const cl = avg >= 80 ? CLASSE_C.OPTIMAL : avg >= 60 ? CLASSE_C.BON : avg >= 40 ? CLASSE_C.MODERE : CLASSE_C.FAIBLE;
                  return (
                    <div key={domain} className="bg-[#12121e] border border-gray-800/40 rounded-lg p-3">
                      <div className="text-[8px] text-gray-500 uppercase tracking-wider mb-1">{domain}</div>
                      <div className={`text-2xl font-bold ${cl.text}`}>{avg}</div>
                      <div className="mt-1.5 space-y-0.5">
                        {engines.map(e => (
                          <div key={e.engine} className="flex justify-between text-[8px]">
                            <span className="text-gray-500">{e.engine}</span>
                            <span className="text-gray-400 font-mono">{e.score}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
                {!summary?.domains && (
                  <div className="col-span-4 text-center text-gray-600 text-xs py-4">
                    {loading ? 'Chargement...' : 'Aucune donnee'}
                  </div>
                )}
              </div>
            </div>

            {/* ══ BLOC 2: CONDITIONS — Recommandations + Alertes ══ */}
            {summary?.recommendations?.length > 0 && (
              <div className="bg-[#0e0e18] border border-gray-800/30 rounded-lg p-3" data-testid="block-conditions">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-3.5 h-3.5 text-orange-400" />
                  <span className="text-[10px] text-gray-400 uppercase tracking-wider font-bold">Conditions & Alertes</span>
                </div>
                <div className="space-y-1.5">
                  {summary.recommendations.map((r, i) => (
                    <div key={i} className={`flex items-center gap-3 px-3 py-2 rounded-lg border ${
                      r.priority === 'HAUTE' ? URGENCY_C.HAUTE : URGENCY_C.MOYENNE
                    }`}>
                      {r.priority === 'HAUTE'
                        ? <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
                        : <Activity className="w-3.5 h-3.5 flex-shrink-0" />
                      }
                      <span className="text-xs flex-1">{r.action}</span>
                      <span className="text-[8px] font-bold uppercase">{r.priority}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ══ BLOC 3: MODE ACTIF (2/3) + FORECAST sidebar (1/3) ══ */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4" data-testid="block-mode-content">
              {/* Mode actif */}
              <div className="lg:col-span-2 bg-[#0e0e18] border border-gray-800/30 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-3">
                  {MODES.find(m => m.id === activeMode)?.Icon && (() => {
                    const M = MODES.find(m => m.id === activeMode);
                    return <M.Icon className={`w-4 h-4 ${M.color}`} />;
                  })()}
                  <span className="text-[10px] text-gray-400 uppercase tracking-wider font-bold">
                    Mode {MODES.find(m => m.id === activeMode)?.label}
                  </span>
                </div>
                {activeMode === 'guide' && <ModeGuidePro location={location} species={species} month={month} />}
                {activeMode === 'scientifique' && <ModeScientifique location={location} species={species} month={month} />}
                {activeMode === 'terrain' && <ModeTerrain location={location} species={species} month={month} />}
              </div>

              {/* Sidebar: Forecast + Plan */}
              <div className="space-y-3">
                {/* FORECAST mini */}
                <div className="bg-[#12121e] border border-gray-800/40 rounded-lg p-3" data-testid="block-forecast">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp className="w-3.5 h-3.5 text-cyan-400" />
                    <span className="text-[10px] text-gray-400 uppercase tracking-wider font-bold">Forecast</span>
                  </div>
                  {forecast ? (
                    <>
                      <div className="flex items-end gap-1 h-20">
                        {forecast.monthly_data?.map(m => {
                          const h = Math.max(8, (m.score / 100) * 100);
                          const isBest = m.month === forecast.best_month;
                          const isWorst = m.month === forecast.worst_month;
                          return (
                            <div key={m.month} className="flex-1 flex flex-col items-center gap-0.5">
                              <span className="text-[6px] text-gray-600">{m.score}</span>
                              <div
                                className={`w-full rounded-t transition-all ${
                                  isBest ? 'bg-emerald-500' : isWorst ? 'bg-red-500/60' : 'bg-cyan-800/50'
                                }`}
                                style={{ height: `${h}%` }}
                              />
                              <span className="text-[6px] text-gray-600">{m.month}</span>
                            </div>
                          );
                        })}
                      </div>
                      <div className="grid grid-cols-2 gap-1 mt-2">
                        {forecast.seasonal_scores && Object.entries(forecast.seasonal_scores).map(([s, score]) => (
                          <div key={s} className="text-center bg-[#0c0c14] rounded p-1.5">
                            <div className="text-sm font-bold text-gray-300">{score}</div>
                            <div className="text-[7px] text-gray-600 uppercase">{s}</div>
                          </div>
                        ))}
                      </div>
                      <div className="mt-2 text-[8px] text-gray-500">
                        Meilleur mois: <span className="text-emerald-400 font-bold">{forecast.best_month}</span> |
                        Moyenne: <span className="text-cyan-400 font-bold">{forecast.annual_average}</span>
                      </div>
                    </>
                  ) : (
                    <div className="text-[9px] text-gray-600 py-4 text-center">{loading ? 'Chargement...' : '--'}</div>
                  )}
                </div>

                {/* PLAN MAITRE mini */}
                <div className="bg-[#12121e] border border-gray-800/40 rounded-lg p-3" data-testid="block-plan">
                  <div className="flex items-center gap-2 mb-2">
                    <ClipboardList className="w-3.5 h-3.5 text-violet-400" />
                    <span className="text-[10px] text-gray-400 uppercase tracking-wider font-bold">Plan Maitre</span>
                    {plan && (
                      <span className="ml-auto text-[8px] text-gray-600">
                        {plan.critical_count} prioritaire{plan.critical_count > 1 ? 's' : ''}
                      </span>
                    )}
                  </div>
                  {plan ? (
                    <div className="space-y-1">
                      {plan.actions?.slice(0, 5).map(a => (
                        <div
                          key={a.rank}
                          className={`flex items-center gap-2 px-2 py-1.5 rounded border text-[9px] cursor-pointer hover:brightness-110 transition-all ${
                            URGENCY_C[a.urgency] || URGENCY_C.FAIBLE
                          }`}
                          onClick={() => handleNavigateToRecommendation(location.lat, location.lng)}
                          data-testid={`plan-action-${a.rank}`}
                        >
                          <span className="font-bold w-6">{a.score}</span>
                          <div className="flex-1 truncate">
                            <div className="text-[9px] font-medium">{a.engine}</div>
                            <div className="text-[7px] opacity-60 truncate">{a.action}</div>
                          </div>
                          <ChevronRight className="w-3 h-3 flex-shrink-0 opacity-40" />
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-[9px] text-gray-600 py-4 text-center">{loading ? 'Chargement...' : '--'}</div>
                  )}
                </div>

                {/* Donnees brutes */}
                <div className="bg-[#12121e] border border-gray-800/40 rounded-lg p-3" data-testid="block-raw-data">
                  <div className="flex items-center gap-2 mb-2">
                    <Database className="w-3.5 h-3.5 text-gray-500" />
                    <span className="text-[10px] text-gray-400 uppercase tracking-wider font-bold">Donnees brutes</span>
                  </div>
                  <div className="text-[8px] font-mono text-gray-600 space-y-0.5">
                    <div>Position: {location?.lat.toFixed(6)}, {location?.lng.toFixed(6)}</div>
                    <div>Espece: {species} | Mois: {month}</div>
                    <div>Score: {summary?.consolidated?.score ?? '--'} | Classe: {summary?.consolidated?.classe ?? '--'}</div>
                    <div>Moteurs: {summary?.engines_count || 0} | Fort: {summary?.analysis?.strongest_engine || '--'} ({summary?.analysis?.strongest_score || '--'})</div>
                    <div>Faible: {summary?.analysis?.weakest_engine || '--'} ({summary?.analysis?.weakest_score || '--'})</div>
                    {forecast && <div>Avg annuel: {forecast.annual_average} | Best: M{forecast.best_month} | Saison: {forecast.best_season}</div>}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
