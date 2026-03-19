/**
 * IntelligenceDashboard — Cockpit central flottant INTELLIGENCE
 * ==============================================================
 * Charte BIONIC Article 2: Deux etats — ferme / ouvert (cockpit complet).
 * Section X: Lisibilite premium — texte eclairci +50%, polices agrandies,
 *   espacement optimise, hierarchie visuelle renforcee.
 * Palette: cream #F2E9D8, sand-gray #C8BBA6, forest #4A7A2E, earth #A8885E.
 * STEEVE-MAX: zero pollution, zero fatigue visuelle, cockpit premium.
 */
import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  X, FlaskConical, Compass, Crosshair,
  TrendingUp, ClipboardList, Database, Activity,
  ChevronRight, AlertTriangle, Brain,
} from 'lucide-react';
import useBionicStore from '@/stores/useBionicStore';
import ModeScientifique from './intelligence/ModeScientifique';
import ModeTerrain from './intelligence/ModeTerrain';
import ModeGuidePro from './intelligence/ModeGuidePro';

const TP = {
  cream: '#F2E9D8', creamDim: '#C8BBA6',
  forest: '#2D5016', forestLight: '#4A7A2E', forestDim: '#1A3A0A',
  earth: '#8B6F47', earthLight: '#A8885E', earthDim: '#5C4A30',
  sand: '#C2A97E', sandLight: '#D4C4A0', sandDim: '#9A8560',
  rock: '#9CA3AF', rockDim: '#6B7280',
  bionic: '#D97706', bionicGlow: '#F59E0B', bionicDim: '#92400E',
};

const MODES = [
  { id: 'guide', label: 'GUIDE PRO', Icon: Crosshair, color: TP.forestLight, activeBg: 'rgba(45,80,22,0.15)', activeBorder: 'rgba(74,122,46,0.35)' },
  { id: 'scientifique', label: 'SCIENTIFIQUE', Icon: FlaskConical, color: TP.sand, activeBg: 'rgba(194,169,126,0.12)', activeBorder: 'rgba(194,169,126,0.3)' },
  { id: 'terrain', label: 'TERRAIN', Icon: Compass, color: TP.earthLight, activeBg: 'rgba(139,111,71,0.12)', activeBorder: 'rgba(139,111,71,0.3)' },
];

const CL = {
  OPTIMAL: { color: TP.bionicGlow, bg: 'rgba(217,119,6,0.12)', border: 'rgba(217,119,6,0.25)' },
  BON: { color: TP.forestLight, bg: 'rgba(74,122,46,0.12)', border: 'rgba(74,122,46,0.25)' },
  MODERE: { color: TP.sand, bg: 'rgba(194,169,126,0.1)', border: 'rgba(194,169,126,0.2)' },
  FAIBLE: { color: TP.rock, bg: 'rgba(156,163,175,0.08)', border: 'rgba(156,163,175,0.15)' },
};

const URG = {
  CRITIQUE: { border: '1px solid rgba(217,119,6,0.45)', bg: 'rgba(217,119,6,0.12)', color: TP.bionicGlow },
  HAUTE: { border: '1px solid rgba(139,111,71,0.35)', bg: 'rgba(139,111,71,0.12)', color: TP.cream },
  MOYENNE: { border: '1px solid rgba(194,169,126,0.25)', bg: 'rgba(194,169,126,0.06)', color: TP.creamDim },
  FAIBLE: { border: '1px solid rgba(156,163,175,0.2)', bg: 'rgba(156,163,175,0.06)', color: TP.rock },
};

function getClasse(score) {
  if (score >= 80) return CL.OPTIMAL;
  if (score >= 60) return CL.BON;
  if (score >= 40) return CL.MODERE;
  return CL.FAIBLE;
}
function getUrg(u) { return URG[u] || URG.FAIBLE; }

const TOPO_BG = `url("data:image/svg+xml,%3Csvg width='80' height='80' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 40 Q20 30 40 40 T80 40' fill='none' stroke='rgba(74,122,46,0.06)' stroke-width='0.5'/%3E%3Cpath d='M0 60 Q20 50 40 60 T80 60' fill='none' stroke='rgba(139,111,71,0.04)' stroke-width='0.4'/%3E%3Cpath d='M0 20 Q20 12 40 20 T80 20' fill='none' stroke='rgba(74,122,46,0.04)' stroke-width='0.3'/%3E%3C/svg%3E")`;

export default function IntelligenceDashboard({
  onClose, waypointCenter, selectedSpecies, currentMonth,
  onNavigateToPosition, onHighlightZoneType, onShowApproachMarkers,
}) {
  const [activeMode, setActiveMode] = useState('guide');
  const {
    summary, forecast, plan, loading,
    fetchSummary, fetchForecast, fetchPlan,
    setLocation, setSpecies, setMonth,
  } = useBionicStore();

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

  const handleNavigate = useCallback((lat, lng) => {
    if (onNavigateToPosition) onNavigateToPosition(lat, lng);
  }, [onNavigateToPosition]);

  const handleDomainClick = useCallback((domain) => {
    if (onHighlightZoneType) onHighlightZoneType(domain.toLowerCase());
  }, [onHighlightZoneType]);

  const classeStyle = summary ? (CL[summary.consolidated?.classe] || CL.FAIBLE) : CL.FAIBLE;

  return (
    <div className="absolute inset-0 z-[900] pointer-events-none flex items-start justify-center p-4 pt-2" data-testid="intelligence-dashboard">
      <div
        className="pointer-events-auto w-full max-w-6xl max-h-full rounded-xl overflow-hidden flex flex-col shadow-2xl"
        style={{
          background: 'rgba(22, 18, 12, 0.78)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          border: '1px solid rgba(139, 111, 71, 0.2)',
          backgroundImage: TOPO_BG,
          backgroundRepeat: 'repeat',
        }}
        data-testid="intelligence-panel"
      >
        {/* ══ HEADER COCKPIT — Section X: tailles augmentees ══ */}
        <div className="flex-shrink-0 px-5 py-2.5 flex items-center gap-3"
          style={{ background: 'rgba(26, 22, 16, 0.6)', borderBottom: '1px solid rgba(139, 111, 71, 0.18)' }}
        >
          <Brain className="w-5 h-5" style={{ color: TP.forestLight }} />
          <span className="text-base font-bold tracking-tight" style={{ color: TP.cream }}>INTELLIGENCE</span>

          <div className="flex gap-1 ml-4 rounded-lg p-1" style={{ background: 'rgba(22, 18, 12, 0.5)', border: '1px solid rgba(139, 111, 71, 0.12)' }}>
            {MODES.map(m => (
              <button
                key={m.id}
                onClick={() => setActiveMode(m.id)}
                className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-md text-xs font-bold uppercase tracking-wider transition-all"
                style={activeMode === m.id
                  ? { color: m.color, background: m.activeBg, border: `1px solid ${m.activeBorder}` }
                  : { color: TP.rockDim, border: '1px solid transparent' }
                }
                data-testid={`mode-${m.id}`}
              >
                <m.Icon className="w-4 h-4" />{m.label}
              </button>
            ))}
          </div>

          <div className="ml-auto flex items-center gap-3">
            {location && (
              <span className="text-xs font-mono" style={{ color: TP.creamDim }}>{location.lat.toFixed(3)},{location.lng.toFixed(3)}</span>
            )}
            <span className="text-xs px-2 py-1 rounded font-mono" style={{ background: 'rgba(139,111,71,0.12)', color: TP.creamDim }}>{species}</span>
            <span className="text-xs px-2 py-1 rounded font-mono" style={{ background: 'rgba(139,111,71,0.12)', color: TP.creamDim }}>M{month}</span>
            <button onClick={onClose} className="p-1.5 rounded transition-colors hover:brightness-125" style={{ color: TP.creamDim }} data-testid="intelligence-close">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* ══ CONTENT — Section X: espacement + lisibilite premium ══ */}
        <div className="flex-1 overflow-auto min-h-0">
          {!location ? (
            <div className="flex flex-col items-center justify-center py-16 gap-3">
              <Crosshair className="w-8 h-8" style={{ color: TP.rockDim }} />
              <div className="text-base font-medium" style={{ color: TP.creamDim }}>Selectionnez un waypoint pour activer INTELLIGENCE</div>
            </div>
          ) : (
            <div className="p-5 space-y-5">
              {/* ══ BLOC 1: ANALYTICS — scores agrandis ══ */}
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-3" data-testid="block-analytics">
                <div className="rounded-lg p-5 flex flex-col justify-center items-center"
                  style={{ background: classeStyle.bg, border: `1px solid ${classeStyle.border}` }}
                >
                  <div className="text-sm uppercase tracking-wider font-medium mb-1" style={{ color: TP.creamDim }}>Score consolide</div>
                  <div className="text-6xl font-black tracking-tighter" style={{ color: classeStyle.color }}>{summary?.consolidated?.score ?? '--'}</div>
                  <div className="text-xl font-bold mt-1" style={{ color: classeStyle.color }}>{summary?.consolidated?.label || '--'}</div>
                  <div className="text-sm mt-1" style={{ color: TP.creamDim }}>{summary?.engines_count || 0} moteurs actifs</div>
                </div>
                <div className="lg:col-span-3 grid grid-cols-2 md:grid-cols-4 gap-2.5">
                  {summary?.domains ? Object.entries(summary.domains).map(([domain, engines]) => {
                    const avg = Math.round(engines.reduce((s, e) => s + e.score, 0) / engines.length);
                    const cl = getClasse(avg);
                    return (
                      <div key={domain} className="rounded-lg p-4 cursor-pointer transition-all hover:brightness-110"
                        style={{ background: 'rgba(45,80,22,0.07)', border: '1px solid rgba(139,111,71,0.12)' }}
                        onClick={() => handleDomainClick(domain)}
                        data-testid={`domain-${domain}`}
                      >
                        <div className="text-xs uppercase tracking-wider font-medium mb-1" style={{ color: TP.creamDim }}>{domain}</div>
                        <div className="text-3xl font-bold" style={{ color: cl.color }}>{avg}</div>
                        <div className="mt-2 space-y-1">
                          {engines.map(e => (
                            <div key={e.engine} className="flex justify-between text-sm">
                              <span className="font-medium" style={{ color: TP.creamDim }}>{e.engine}</span>
                              <span className="font-mono font-semibold" style={{ color: TP.cream }}>{e.score}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  }) : (
                    <div className="col-span-4 text-center text-base py-6 font-medium" style={{ color: TP.creamDim }}>
                      {loading ? 'Chargement...' : 'Aucune donnee'}
                    </div>
                  )}
                </div>
              </div>

              {/* ══ BLOC 2: CONDITIONS & ALERTES ══ */}
              {summary?.recommendations?.length > 0 && (
                <div className="rounded-lg p-5" style={{ background: 'rgba(139,111,71,0.05)', border: '1px solid rgba(139,111,71,0.12)' }} data-testid="block-conditions">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle className="w-5 h-5" style={{ color: TP.bionic }} />
                    <span className="text-base uppercase tracking-wider font-bold" style={{ color: TP.cream }}>Conditions & Alertes</span>
                  </div>
                  <div className="space-y-2">
                    {summary.recommendations.map((r, i) => {
                      const u = r.priority === 'HAUTE' ? getUrg('HAUTE') : getUrg('MOYENNE');
                      return (
                        <div key={i} className="flex items-center gap-3 px-4 py-3 rounded-lg"
                          style={{ border: u.border, background: u.bg, color: u.color }}
                        >
                          {r.priority === 'HAUTE' ? <AlertTriangle className="w-5 h-5 flex-shrink-0" /> : <Activity className="w-5 h-5 flex-shrink-0" />}
                          <span className="text-base font-medium flex-1">{r.action}</span>
                          <span className="text-sm font-bold uppercase tracking-wider">{r.priority}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* ══ BLOC 3: MODE ACTIF (2/3) + SIDEBAR (1/3) ══ */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4" data-testid="block-mode-content">
                <div className="lg:col-span-2 rounded-lg p-5" style={{ background: 'rgba(45,80,22,0.05)', border: '1px solid rgba(139,111,71,0.12)' }}>
                  <div className="flex items-center gap-2 mb-4">
                    {(() => { const M = MODES.find(m => m.id === activeMode); return M ? <M.Icon className="w-5 h-5" style={{ color: M.color }} /> : null; })()}
                    <span className="text-base uppercase tracking-wider font-bold" style={{ color: TP.cream }}>Mode {MODES.find(m => m.id === activeMode)?.label}</span>
                  </div>
                  {activeMode === 'guide' && <ModeGuidePro location={location} species={species} month={month} onNavigate={handleNavigate} onShowMarkers={onShowApproachMarkers} />}
                  {activeMode === 'scientifique' && <ModeScientifique location={location} species={species} month={month} />}
                  {activeMode === 'terrain' && <ModeTerrain location={location} species={species} month={month} />}
                </div>

                <div className="space-y-3">
                  {/* FORECAST */}
                  <div className="rounded-lg p-4" style={{ background: 'rgba(139,111,71,0.06)', border: '1px solid rgba(139,111,71,0.12)' }} data-testid="block-forecast">
                    <div className="flex items-center gap-2 mb-3">
                      <TrendingUp className="w-5 h-5" style={{ color: TP.forestLight }} />
                      <span className="text-sm uppercase tracking-wider font-bold" style={{ color: TP.cream }}>Forecast</span>
                    </div>
                    {forecast ? (
                      <>
                        <div className="flex items-end gap-1 h-20">
                          {forecast.monthly_data?.map(m => {
                            const h = Math.max(8, (m.score / 100) * 100);
                            const barColor = m.month === forecast.best_month ? TP.forestLight
                              : m.month === forecast.worst_month ? TP.bionicDim
                              : TP.earthDim;
                            return (
                              <div key={m.month} className="flex-1 flex flex-col items-center gap-0.5">
                                <span className="text-xs font-mono font-semibold" style={{ color: TP.creamDim }}>{m.score}</span>
                                <div className="w-full rounded-t" style={{ height: `${h}%`, background: barColor }} />
                                <span className="text-xs font-mono" style={{ color: TP.creamDim }}>{m.month}</span>
                              </div>
                            );
                          })}
                        </div>
                        <div className="grid grid-cols-2 gap-2 mt-3">
                          {forecast.seasonal_scores && Object.entries(forecast.seasonal_scores).map(([s, score]) => (
                            <div key={s} className="text-center rounded p-2" style={{ background: 'rgba(45,80,22,0.07)' }}>
                              <div className="text-xl font-bold" style={{ color: TP.cream }}>{score}</div>
                              <div className="text-xs uppercase font-medium" style={{ color: TP.creamDim }}>{s}</div>
                            </div>
                          ))}
                        </div>
                      </>
                    ) : <div className="text-sm py-4 text-center font-medium" style={{ color: TP.creamDim }}>{loading ? '...' : '--'}</div>}
                  </div>

                  {/* PLAN MAITRE */}
                  <div className="rounded-lg p-4" style={{ background: 'rgba(139,111,71,0.06)', border: '1px solid rgba(139,111,71,0.12)' }} data-testid="block-plan">
                    <div className="flex items-center gap-2 mb-3">
                      <ClipboardList className="w-5 h-5" style={{ color: TP.earth }} />
                      <span className="text-sm uppercase tracking-wider font-bold" style={{ color: TP.cream }}>Plan Maitre</span>
                    </div>
                    {plan ? (
                      <div className="space-y-2">
                        {plan.actions?.slice(0, 4).map(a => {
                          const u = getUrg(a.urgency);
                          return (
                            <div key={a.rank} onClick={() => handleNavigate(location.lat, location.lng)}
                              className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm cursor-pointer hover:brightness-110 transition-all"
                              style={{ border: u.border, background: u.bg, color: u.color }}
                              data-testid={`plan-action-${a.rank}`}
                            >
                              <span className="font-bold text-base w-8">{a.score}</span>
                              <div className="flex-1 truncate">
                                <div className="font-semibold">{a.engine}</div>
                                <div className="text-xs opacity-70 truncate">{a.action}</div>
                              </div>
                              <ChevronRight className="w-4 h-4 opacity-50" />
                            </div>
                          );
                        })}
                      </div>
                    ) : <div className="text-sm py-4 text-center font-medium" style={{ color: TP.creamDim }}>{loading ? '...' : '--'}</div>}
                  </div>

                  {/* DONNEES BRUTES */}
                  <div className="rounded-lg p-4" style={{ background: 'rgba(45,80,22,0.05)', border: '1px solid rgba(74,122,46,0.1)' }} data-testid="block-raw-data">
                    <div className="flex items-center gap-2 mb-2">
                      <Database className="w-4 h-4" style={{ color: TP.creamDim }} />
                      <span className="text-sm uppercase tracking-wider font-bold" style={{ color: TP.cream }}>Donnees brutes</span>
                    </div>
                    <div className="text-sm font-mono space-y-1" style={{ color: TP.creamDim }}>
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
