/**
 * IntelligenceDashboard — Tableau central flottant INTELLIGENCE
 * ==============================================================
 * BCE-4X: Superposition non-bloquante — la carte reste 100% interactive.
 * pointer-events-none sur le conteneur, pointer-events-auto sur le panneau.
 * 6 blocs: Analytics, Conditions, Mode actif, Forecast, Plan Maitre, Donnees brutes.
 * 3 modes: Scientifique, Terrain, Guide Pro (solunaire).
 * Synchronisation bi-directionnelle carte <-> intelligence.
 */
import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  X, FlaskConical, Compass, Crosshair, BarChart3,
  TrendingUp, ClipboardList, Database, Activity,
  MapPin, ChevronRight, AlertTriangle, Zap, Minimize2, Maximize2,
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

const CL = {
  OPTIMAL: { text: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/20' },
  BON: { text: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20' },
  MODERE: { text: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20' },
  FAIBLE: { text: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/20' },
};

const URG = {
  CRITIQUE: 'border-red-500/40 bg-red-500/10 text-red-300',
  HAUTE: 'border-orange-500/30 bg-orange-500/10 text-orange-300',
  MOYENNE: 'border-yellow-500/20 bg-yellow-500/5 text-yellow-300',
  FAIBLE: 'border-gray-700/30 bg-gray-800/30 text-gray-400',
};

function getClasse(score) {
  if (score >= 80) return CL.OPTIMAL;
  if (score >= 60) return CL.BON;
  if (score >= 40) return CL.MODERE;
  return CL.FAIBLE;
}

export default function IntelligenceDashboard({
  onClose, waypointCenter, selectedSpecies, currentMonth,
  onNavigateToPosition, onHighlightZoneType, onShowApproachMarkers,
}) {
  const [activeMode, setActiveMode] = useState('guide');
  const [isCompact, setIsCompact] = useState(false);
  const {
    summary, forecast, plan, loading,
    fetchSummary, fetchForecast, fetchPlan,
    setLocation, setSpecies, setMonth,
  } = useBionicStore();

  // Sync carte -> intelligence
  useEffect(() => {
    if (waypointCenter) setLocation({ lat: waypointCenter.lat, lng: waypointCenter.lng });
  }, [waypointCenter, setLocation]);
  useEffect(() => { if (selectedSpecies) setSpecies(selectedSpecies); }, [selectedSpecies, setSpecies]);
  useEffect(() => { if (currentMonth) setMonth(currentMonth); }, [currentMonth, setMonth]);

  const location = useMemo(() => (
    waypointCenter ? { lat: waypointCenter.lat, lng: waypointCenter.lng } : null
  ), [waypointCenter]);
  const species = selectedSpecies || 'CHEVREUIL';
  const month = currentMonth || new Date().getMonth() + 1;

  useEffect(() => {
    if (!location) return;
    fetchSummary(); fetchForecast(); fetchPlan();
  }, [location, species, month, fetchSummary, fetchForecast, fetchPlan]);

  // Intelligence -> Carte: navigation + highlight
  const handleNavigate = useCallback((lat, lng) => {
    if (onNavigateToPosition) onNavigateToPosition(lat, lng);
  }, [onNavigateToPosition]);

  const handleDomainClick = useCallback((domain) => {
    if (onHighlightZoneType) onHighlightZoneType(domain.toLowerCase());
  }, [onHighlightZoneType]);

  const classeStyle = summary ? (CL[summary.consolidated?.classe] || CL.FAIBLE) : CL.FAIBLE;

  return (
    /* BCE-4X: pointer-events-none = clics passent a la carte */
    <div className="absolute inset-0 z-[900] pointer-events-none flex items-start justify-center p-4 pt-2" data-testid="intelligence-dashboard">
      {/* Panneau flottant central — pointer-events-auto */}
      <div className={`pointer-events-auto ${isCompact ? 'w-[420px]' : 'w-full max-w-6xl'} max-h-full bg-[#0a0a12]/97 backdrop-blur-lg rounded-xl border border-gray-700/40 shadow-2xl shadow-black/60 overflow-hidden flex flex-col transition-all duration-300`}
        data-testid="intelligence-panel"
      >
        {/* ══ HEADER COCKPIT ══ */}
        <div className="flex-shrink-0 bg-[#0c0c16]/95 border-b border-gray-800/40 px-3 py-1.5 flex items-center gap-2">
          <Zap className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-xs font-bold tracking-tight text-gray-100">INTELLIGENCE</span>

          {/* Mode selector */}
          {!isCompact && (
            <div className="flex gap-0.5 ml-3 bg-[#080810] rounded-lg p-0.5 border border-gray-800/30">
              {MODES.map(m => (
                <button
                  key={m.id}
                  onClick={() => setActiveMode(m.id)}
                  className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-[9px] font-bold uppercase tracking-wider transition-all ${
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
          )}

          <div className="ml-auto flex items-center gap-2">
            {location && (
              <span className="text-[8px] text-gray-500 font-mono">{location.lat.toFixed(3)},{location.lng.toFixed(3)}</span>
            )}
            <span className="text-[8px] bg-gray-800/60 text-gray-400 px-1.5 py-0.5 rounded font-mono">{species}</span>
            <span className="text-[8px] bg-gray-800/60 text-gray-400 px-1.5 py-0.5 rounded font-mono">M{month}</span>
            <button onClick={() => setIsCompact(!isCompact)} className="p-1 text-gray-500 hover:text-white transition-colors rounded hover:bg-white/5" data-testid="intelligence-compact-toggle">
              {isCompact ? <Maximize2 className="w-3 h-3" /> : <Minimize2 className="w-3 h-3" />}
            </button>
            <button onClick={onClose} className="p-1 text-gray-500 hover:text-white transition-colors rounded hover:bg-white/5" data-testid="intelligence-close">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* ══ CONTENT ══ */}
        <div className="flex-1 overflow-auto min-h-0">
          {!location ? (
            <div className="flex flex-col items-center justify-center py-12 gap-2">
              <Crosshair className="w-6 h-6 text-gray-600" />
              <div className="text-gray-500 text-xs">Selectionnez un waypoint pour activer INTELLIGENCE</div>
            </div>
          ) : isCompact ? (
            /* ══ MODE COMPACT — Score + Plan rapide ══ */
            <div className="p-3 space-y-2">
              <div className="flex items-center gap-3">
                <div className={`text-3xl font-black ${classeStyle.text}`}>{summary?.consolidated?.score ?? '--'}</div>
                <div>
                  <div className={`text-xs font-bold ${classeStyle.text}`}>{summary?.consolidated?.label || '--'}</div>
                  <div className="text-[8px] text-gray-600">{summary?.engines_count || 0} moteurs</div>
                </div>
              </div>
              {plan?.actions?.slice(0, 3).map(a => (
                <div key={a.rank} onClick={() => handleNavigate(location.lat, location.lng)}
                  className={`flex items-center gap-2 px-2 py-1.5 rounded border text-[9px] cursor-pointer hover:brightness-110 ${URG[a.urgency] || URG.FAIBLE}`}
                  data-testid={`plan-action-${a.rank}`}
                >
                  <span className="font-bold w-5">{a.score}</span>
                  <span className="flex-1 truncate">{a.engine}: {a.action}</span>
                  <ChevronRight className="w-3 h-3 opacity-40" />
                </div>
              ))}
            </div>
          ) : (
            /* ══ MODE FULL — 6 blocs ══ */
            <div className="p-3 space-y-3">
              {/* BLOC 1: ANALYTICS */}
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-2" data-testid="block-analytics">
                <div className={`${classeStyle.bg} border ${classeStyle.border} rounded-lg p-3 flex flex-col justify-center items-center`}>
                  <div className="text-[8px] text-gray-500 uppercase tracking-wider mb-0.5">Score consolide</div>
                  <div className={`text-4xl font-black tracking-tighter ${classeStyle.text}`}>{summary?.consolidated?.score ?? '--'}</div>
                  <div className={`text-xs font-bold mt-0.5 ${classeStyle.text}`}>{summary?.consolidated?.label || '--'}</div>
                  <div className="text-[7px] text-gray-600 mt-0.5">{summary?.engines_count || 0} moteurs actifs</div>
                </div>
                <div className="lg:col-span-3 grid grid-cols-2 md:grid-cols-4 gap-1.5">
                  {summary?.domains ? Object.entries(summary.domains).map(([domain, engines]) => {
                    const avg = Math.round(engines.reduce((s, e) => s + e.score, 0) / engines.length);
                    const cl = getClasse(avg);
                    return (
                      <div key={domain} className="bg-[#12121e] border border-gray-800/40 rounded-lg p-2 cursor-pointer hover:border-gray-600/50 transition-colors"
                        onClick={() => handleDomainClick(domain)}
                        data-testid={`domain-${domain}`}
                      >
                        <div className="text-[7px] text-gray-500 uppercase tracking-wider mb-0.5">{domain}</div>
                        <div className={`text-xl font-bold ${cl.text}`}>{avg}</div>
                        <div className="mt-1 space-y-0.5">
                          {engines.map(e => (
                            <div key={e.engine} className="flex justify-between text-[7px]">
                              <span className="text-gray-500">{e.engine}</span>
                              <span className="text-gray-400 font-mono">{e.score}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  }) : (
                    <div className="col-span-4 text-center text-gray-600 text-[9px] py-3">
                      {loading ? 'Chargement...' : 'Aucune donnee'}
                    </div>
                  )}
                </div>
              </div>

              {/* BLOC 2: CONDITIONS */}
              {summary?.recommendations?.length > 0 && (
                <div className="bg-[#0e0e18] border border-gray-800/30 rounded-lg p-2.5" data-testid="block-conditions">
                  <div className="flex items-center gap-1.5 mb-1.5">
                    <AlertTriangle className="w-3 h-3 text-orange-400" />
                    <span className="text-[9px] text-gray-400 uppercase tracking-wider font-bold">Conditions & Alertes</span>
                  </div>
                  <div className="space-y-1">
                    {summary.recommendations.map((r, i) => (
                      <div key={i} className={`flex items-center gap-2 px-2 py-1.5 rounded-lg border ${r.priority === 'HAUTE' ? URG.HAUTE : URG.MOYENNE}`}>
                        {r.priority === 'HAUTE' ? <AlertTriangle className="w-3 h-3 flex-shrink-0" /> : <Activity className="w-3 h-3 flex-shrink-0" />}
                        <span className="text-[10px] flex-1">{r.action}</span>
                        <span className="text-[7px] font-bold uppercase">{r.priority}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* BLOC 3: MODE ACTIF (2/3) + SIDEBAR (1/3) */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-3" data-testid="block-mode-content">
                <div className="lg:col-span-2 bg-[#0e0e18] border border-gray-800/30 rounded-lg p-3">
                  <div className="flex items-center gap-1.5 mb-2">
                    {(() => { const M = MODES.find(m => m.id === activeMode); return M ? <M.Icon className={`w-3.5 h-3.5 ${M.color}`} /> : null; })()}
                    <span className="text-[9px] text-gray-400 uppercase tracking-wider font-bold">Mode {MODES.find(m => m.id === activeMode)?.label}</span>
                  </div>
                  {activeMode === 'guide' && <ModeGuidePro location={location} species={species} month={month} onNavigate={handleNavigate} onShowMarkers={onShowApproachMarkers} />}
                  {activeMode === 'scientifique' && <ModeScientifique location={location} species={species} month={month} />}
                  {activeMode === 'terrain' && <ModeTerrain location={location} species={species} month={month} />}
                </div>

                {/* Sidebar: Forecast + Plan + Raw */}
                <div className="space-y-2">
                  {/* FORECAST */}
                  <div className="bg-[#12121e] border border-gray-800/40 rounded-lg p-2.5" data-testid="block-forecast">
                    <div className="flex items-center gap-1.5 mb-1.5">
                      <TrendingUp className="w-3 h-3 text-cyan-400" />
                      <span className="text-[9px] text-gray-400 uppercase tracking-wider font-bold">Forecast</span>
                    </div>
                    {forecast ? (
                      <>
                        <div className="flex items-end gap-0.5 h-16">
                          {forecast.monthly_data?.map(m => {
                            const h = Math.max(8, (m.score / 100) * 100);
                            return (
                              <div key={m.month} className="flex-1 flex flex-col items-center gap-0.5">
                                <span className="text-[5px] text-gray-600">{m.score}</span>
                                <div className={`w-full rounded-t ${m.month === forecast.best_month ? 'bg-emerald-500' : m.month === forecast.worst_month ? 'bg-red-500/60' : 'bg-cyan-800/50'}`} style={{ height: `${h}%` }} />
                                <span className="text-[5px] text-gray-600">{m.month}</span>
                              </div>
                            );
                          })}
                        </div>
                        <div className="grid grid-cols-2 gap-1 mt-1.5">
                          {forecast.seasonal_scores && Object.entries(forecast.seasonal_scores).map(([s, score]) => (
                            <div key={s} className="text-center bg-[#0c0c14] rounded p-1">
                              <div className="text-xs font-bold text-gray-300">{score}</div>
                              <div className="text-[6px] text-gray-600 uppercase">{s}</div>
                            </div>
                          ))}
                        </div>
                      </>
                    ) : <div className="text-[8px] text-gray-600 py-3 text-center">{loading ? '...' : '--'}</div>}
                  </div>

                  {/* PLAN MAITRE */}
                  <div className="bg-[#12121e] border border-gray-800/40 rounded-lg p-2.5" data-testid="block-plan">
                    <div className="flex items-center gap-1.5 mb-1.5">
                      <ClipboardList className="w-3 h-3 text-violet-400" />
                      <span className="text-[9px] text-gray-400 uppercase tracking-wider font-bold">Plan Maitre</span>
                    </div>
                    {plan ? (
                      <div className="space-y-1">
                        {plan.actions?.slice(0, 4).map(a => (
                          <div key={a.rank} onClick={() => handleNavigate(location.lat, location.lng)}
                            className={`flex items-center gap-1.5 px-2 py-1 rounded border text-[8px] cursor-pointer hover:brightness-110 transition-all ${URG[a.urgency] || URG.FAIBLE}`}
                            data-testid={`plan-action-${a.rank}`}
                          >
                            <span className="font-bold w-5">{a.score}</span>
                            <div className="flex-1 truncate">
                              <div className="font-medium">{a.engine}</div>
                              <div className="text-[7px] opacity-60 truncate">{a.action}</div>
                            </div>
                            <ChevronRight className="w-2.5 h-2.5 opacity-40" />
                          </div>
                        ))}
                      </div>
                    ) : <div className="text-[8px] text-gray-600 py-3 text-center">{loading ? '...' : '--'}</div>}
                  </div>

                  {/* DONNEES BRUTES */}
                  <div className="bg-[#12121e] border border-gray-800/40 rounded-lg p-2.5" data-testid="block-raw-data">
                    <div className="flex items-center gap-1.5 mb-1">
                      <Database className="w-3 h-3 text-gray-500" />
                      <span className="text-[9px] text-gray-400 uppercase tracking-wider font-bold">Donnees brutes</span>
                    </div>
                    <div className="text-[7px] font-mono text-gray-600 space-y-0.5">
                      <div>Pos: {location?.lat.toFixed(5)}, {location?.lng.toFixed(5)}</div>
                      <div>Score: {summary?.consolidated?.score ?? '--'} | {summary?.consolidated?.classe ?? '--'}</div>
                      <div>Fort: {summary?.analysis?.strongest_engine || '--'} ({summary?.analysis?.strongest_score || '--'})</div>
                      {forecast && <div>Best: M{forecast.best_month} | Avg: {forecast.annual_average}</div>}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
