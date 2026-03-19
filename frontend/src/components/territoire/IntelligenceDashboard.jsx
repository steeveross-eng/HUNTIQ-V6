/**
 * IntelligenceDashboard — Cockpit central flottant INTELLIGENCE
 * ==============================================================
 * Charte BIONIC Article 2: Deux etats uniquement — ferme / ouvert (cockpit complet).
 * BCE-4X: Superposition non-bloquante — la carte reste 100% interactive.
 * STEEVE-MAX: Palette terrain premium, fond topographique, verre depoli 78%.
 * Aucun PiP, widget, mini-tableau ou mode compact (Article 3).
 */
import { useState, useEffect, useCallback, useMemo } from 'react';
import {
  X, FlaskConical, Compass, Crosshair,
  TrendingUp, ClipboardList, Database, Activity,
  ChevronRight, AlertTriangle, Zap,
} from 'lucide-react';
import useBionicStore from '@/stores/useBionicStore';
import ModeScientifique from './intelligence/ModeScientifique';
import ModeTerrain from './intelligence/ModeTerrain';
import ModeGuidePro from './intelligence/ModeGuidePro';

// Palette terrain premium — coherente avec SolunarChart/ModeGuidePro
const TP = {
  forest: '#2D5016', forestLight: '#4A7A2E', forestDim: '#1A3A0A',
  earth: '#8B6F47', earthLight: '#A8885E', earthDim: '#5C4A30',
  sand: '#C2A97E', sandLight: '#D4C4A0', sandDim: '#9A8560',
  rock: '#6B7280', rockLight: '#9CA3AF', rockDim: '#4B5563',
  bionic: '#D97706', bionicGlow: '#F59E0B', bionicDim: '#92400E',
};

const MODES = [
  { id: 'guide', label: 'GUIDE PRO', Icon: Crosshair, color: TP.forestLight, activeBg: 'rgba(45,80,22,0.12)', activeBorder: 'rgba(74,122,46,0.3)' },
  { id: 'scientifique', label: 'SCIENTIFIQUE', Icon: FlaskConical, color: TP.sand, activeBg: 'rgba(194,169,126,0.1)', activeBorder: 'rgba(194,169,126,0.25)' },
  { id: 'terrain', label: 'TERRAIN', Icon: Compass, color: TP.earthLight, activeBg: 'rgba(139,111,71,0.1)', activeBorder: 'rgba(139,111,71,0.25)' },
];

const CL = {
  OPTIMAL: { color: TP.bionicGlow, bg: 'rgba(217,119,6,0.1)', border: 'rgba(217,119,6,0.2)' },
  BON: { color: TP.forestLight, bg: 'rgba(74,122,46,0.1)', border: 'rgba(74,122,46,0.2)' },
  MODERE: { color: TP.sand, bg: 'rgba(194,169,126,0.08)', border: 'rgba(194,169,126,0.15)' },
  FAIBLE: { color: TP.rock, bg: 'rgba(107,114,128,0.08)', border: 'rgba(107,114,128,0.15)' },
};

const URG = {
  CRITIQUE: { border: '1px solid rgba(217,119,6,0.4)', bg: 'rgba(217,119,6,0.1)', color: TP.bionicGlow },
  HAUTE: { border: '1px solid rgba(139,111,71,0.3)', bg: 'rgba(139,111,71,0.1)', color: TP.earthLight },
  MOYENNE: { border: '1px solid rgba(194,169,126,0.2)', bg: 'rgba(194,169,126,0.05)', color: TP.sand },
  FAIBLE: { border: '1px solid rgba(75,85,99,0.3)', bg: 'rgba(75,85,99,0.08)', color: TP.rock },
};

function getClasse(score) {
  if (score >= 80) return CL.OPTIMAL;
  if (score >= 60) return CL.BON;
  if (score >= 40) return CL.MODERE;
  return CL.FAIBLE;
}

function getUrg(urgency) {
  return URG[urgency] || URG.FAIBLE;
}

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
        {/* HEADER COCKPIT */}
        <div className="flex-shrink-0 px-3 py-1.5 flex items-center gap-2"
          style={{ background: 'rgba(26, 22, 16, 0.6)', borderBottom: '1px solid rgba(139, 111, 71, 0.15)' }}
        >
          <Zap className="w-3.5 h-3.5" style={{ color: TP.bionic }} />
          <span className="text-xs font-bold tracking-tight" style={{ color: TP.sandLight }}>INTELLIGENCE</span>

          <div className="flex gap-0.5 ml-3 rounded-lg p-0.5" style={{ background: 'rgba(22, 18, 12, 0.5)', border: '1px solid rgba(139, 111, 71, 0.1)' }}>
            {MODES.map(m => (
              <button
                key={m.id}
                onClick={() => setActiveMode(m.id)}
                className="flex items-center gap-1 px-2.5 py-1 rounded-md text-[9px] font-bold uppercase tracking-wider transition-all"
                style={activeMode === m.id
                  ? { color: m.color, background: m.activeBg, border: `1px solid ${m.activeBorder}` }
                  : { color: TP.rockDim, border: '1px solid transparent' }
                }
                data-testid={`mode-${m.id}`}
              >
                <m.Icon className="w-3 h-3" />{m.label}
              </button>
            ))}
          </div>

          <div className="ml-auto flex items-center gap-2">
            {location && (
              <span className="text-[8px] font-mono" style={{ color: TP.rockDim }}>{location.lat.toFixed(3)},{location.lng.toFixed(3)}</span>
            )}
            <span className="text-[8px] px-1.5 py-0.5 rounded font-mono" style={{ background: 'rgba(139,111,71,0.1)', color: TP.rock }}>{species}</span>
            <span className="text-[8px] px-1.5 py-0.5 rounded font-mono" style={{ background: 'rgba(139,111,71,0.1)', color: TP.rock }}>M{month}</span>
            <button onClick={onClose} className="p-1 rounded transition-colors hover:brightness-125" style={{ color: TP.rock }} data-testid="intelligence-close">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* CONTENT — Cockpit complet uniquement (Article 2 Charte) */}
        <div className="flex-1 overflow-auto min-h-0">
          {!location ? (
            <div className="flex flex-col items-center justify-center py-12 gap-2">
              <Crosshair className="w-6 h-6" style={{ color: TP.rockDim }} />
              <div className="text-xs" style={{ color: TP.rock }}>Selectionnez un waypoint pour activer INTELLIGENCE</div>
            </div>
          ) : (
            <div className="p-3 space-y-3">
              {/* BLOC 1: ANALYTICS */}
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-2" data-testid="block-analytics">
                <div className="rounded-lg p-3 flex flex-col justify-center items-center"
                  style={{ background: classeStyle.bg, border: `1px solid ${classeStyle.border}` }}
                >
                  <div className="text-[8px] uppercase tracking-wider mb-0.5" style={{ color: TP.rock }}>Score consolide</div>
                  <div className="text-4xl font-black tracking-tighter" style={{ color: classeStyle.color }}>{summary?.consolidated?.score ?? '--'}</div>
                  <div className="text-xs font-bold mt-0.5" style={{ color: classeStyle.color }}>{summary?.consolidated?.label || '--'}</div>
                  <div className="text-[7px] mt-0.5" style={{ color: TP.rockDim }}>{summary?.engines_count || 0} moteurs actifs</div>
                </div>
                <div className="lg:col-span-3 grid grid-cols-2 md:grid-cols-4 gap-1.5">
                  {summary?.domains ? Object.entries(summary.domains).map(([domain, engines]) => {
                    const avg = Math.round(engines.reduce((s, e) => s + e.score, 0) / engines.length);
                    const cl = getClasse(avg);
                    return (
                      <div key={domain} className="rounded-lg p-2 cursor-pointer transition-all hover:brightness-110"
                        style={{ background: 'rgba(45,80,22,0.06)', border: '1px solid rgba(139,111,71,0.1)' }}
                        onClick={() => handleDomainClick(domain)}
                        data-testid={`domain-${domain}`}
                      >
                        <div className="text-[7px] uppercase tracking-wider mb-0.5" style={{ color: TP.rock }}>{domain}</div>
                        <div className="text-xl font-bold" style={{ color: cl.color }}>{avg}</div>
                        <div className="mt-1 space-y-0.5">
                          {engines.map(e => (
                            <div key={e.engine} className="flex justify-between text-[7px]">
                              <span style={{ color: TP.rock }}>{e.engine}</span>
                              <span className="font-mono" style={{ color: TP.rockLight }}>{e.score}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  }) : (
                    <div className="col-span-4 text-center text-[9px] py-3" style={{ color: TP.rockDim }}>
                      {loading ? 'Chargement...' : 'Aucune donnee'}
                    </div>
                  )}
                </div>
              </div>

              {/* BLOC 2: CONDITIONS */}
              {summary?.recommendations?.length > 0 && (
                <div className="rounded-lg p-2.5" style={{ background: 'rgba(139,111,71,0.04)', border: '1px solid rgba(139,111,71,0.1)' }} data-testid="block-conditions">
                  <div className="flex items-center gap-1.5 mb-1.5">
                    <AlertTriangle className="w-3 h-3" style={{ color: TP.bionic }} />
                    <span className="text-[9px] uppercase tracking-wider font-bold" style={{ color: TP.earthLight }}>Conditions & Alertes</span>
                  </div>
                  <div className="space-y-1">
                    {summary.recommendations.map((r, i) => {
                      const u = r.priority === 'HAUTE' ? getUrg('HAUTE') : getUrg('MOYENNE');
                      return (
                        <div key={i} className="flex items-center gap-2 px-2 py-1.5 rounded-lg"
                          style={{ border: u.border, background: u.bg, color: u.color }}
                        >
                          {r.priority === 'HAUTE' ? <AlertTriangle className="w-3 h-3 flex-shrink-0" /> : <Activity className="w-3 h-3 flex-shrink-0" />}
                          <span className="text-[10px] flex-1">{r.action}</span>
                          <span className="text-[7px] font-bold uppercase">{r.priority}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* BLOC 3: MODE ACTIF (2/3) + SIDEBAR (1/3) */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-3" data-testid="block-mode-content">
                <div className="lg:col-span-2 rounded-lg p-3" style={{ background: 'rgba(45,80,22,0.04)', border: '1px solid rgba(139,111,71,0.1)' }}>
                  <div className="flex items-center gap-1.5 mb-2">
                    {(() => { const M = MODES.find(m => m.id === activeMode); return M ? <M.Icon className="w-3.5 h-3.5" style={{ color: M.color }} /> : null; })()}
                    <span className="text-[9px] uppercase tracking-wider font-bold" style={{ color: TP.earthLight }}>Mode {MODES.find(m => m.id === activeMode)?.label}</span>
                  </div>
                  {activeMode === 'guide' && <ModeGuidePro location={location} species={species} month={month} onNavigate={handleNavigate} onShowMarkers={onShowApproachMarkers} />}
                  {activeMode === 'scientifique' && <ModeScientifique location={location} species={species} month={month} />}
                  {activeMode === 'terrain' && <ModeTerrain location={location} species={species} month={month} />}
                </div>

                <div className="space-y-2">
                  {/* FORECAST */}
                  <div className="rounded-lg p-2.5" style={{ background: 'rgba(139,111,71,0.05)', border: '1px solid rgba(139,111,71,0.1)' }} data-testid="block-forecast">
                    <div className="flex items-center gap-1.5 mb-1.5">
                      <TrendingUp className="w-3 h-3" style={{ color: TP.forestLight }} />
                      <span className="text-[9px] uppercase tracking-wider font-bold" style={{ color: TP.earthLight }}>Forecast</span>
                    </div>
                    {forecast ? (
                      <>
                        <div className="flex items-end gap-0.5 h-16">
                          {forecast.monthly_data?.map(m => {
                            const h = Math.max(8, (m.score / 100) * 100);
                            const barColor = m.month === forecast.best_month ? TP.forestLight
                              : m.month === forecast.worst_month ? TP.bionicDim
                              : TP.earthDim;
                            return (
                              <div key={m.month} className="flex-1 flex flex-col items-center gap-0.5">
                                <span className="text-[5px]" style={{ color: TP.rockDim }}>{m.score}</span>
                                <div className="w-full rounded-t" style={{ height: `${h}%`, background: barColor }} />
                                <span className="text-[5px]" style={{ color: TP.rockDim }}>{m.month}</span>
                              </div>
                            );
                          })}
                        </div>
                        <div className="grid grid-cols-2 gap-1 mt-1.5">
                          {forecast.seasonal_scores && Object.entries(forecast.seasonal_scores).map(([s, score]) => (
                            <div key={s} className="text-center rounded p-1" style={{ background: 'rgba(45,80,22,0.06)' }}>
                              <div className="text-xs font-bold" style={{ color: TP.sandLight }}>{score}</div>
                              <div className="text-[6px] uppercase" style={{ color: TP.rockDim }}>{s}</div>
                            </div>
                          ))}
                        </div>
                      </>
                    ) : <div className="text-[8px] py-3 text-center" style={{ color: TP.rockDim }}>{loading ? '...' : '--'}</div>}
                  </div>

                  {/* PLAN MAITRE */}
                  <div className="rounded-lg p-2.5" style={{ background: 'rgba(139,111,71,0.05)', border: '1px solid rgba(139,111,71,0.1)' }} data-testid="block-plan">
                    <div className="flex items-center gap-1.5 mb-1.5">
                      <ClipboardList className="w-3 h-3" style={{ color: TP.earth }} />
                      <span className="text-[9px] uppercase tracking-wider font-bold" style={{ color: TP.earthLight }}>Plan Maitre</span>
                    </div>
                    {plan ? (
                      <div className="space-y-1">
                        {plan.actions?.slice(0, 4).map(a => {
                          const u = getUrg(a.urgency);
                          return (
                            <div key={a.rank} onClick={() => handleNavigate(location.lat, location.lng)}
                              className="flex items-center gap-1.5 px-2 py-1 rounded text-[8px] cursor-pointer hover:brightness-110 transition-all"
                              style={{ border: u.border, background: u.bg, color: u.color }}
                              data-testid={`plan-action-${a.rank}`}
                            >
                              <span className="font-bold w-5">{a.score}</span>
                              <div className="flex-1 truncate">
                                <div className="font-medium">{a.engine}</div>
                                <div className="text-[7px] opacity-60 truncate">{a.action}</div>
                              </div>
                              <ChevronRight className="w-2.5 h-2.5 opacity-40" />
                            </div>
                          );
                        })}
                      </div>
                    ) : <div className="text-[8px] py-3 text-center" style={{ color: TP.rockDim }}>{loading ? '...' : '--'}</div>}
                  </div>

                  {/* DONNEES BRUTES */}
                  <div className="rounded-lg p-2.5" style={{ background: 'rgba(45,80,22,0.04)', border: '1px solid rgba(74,122,46,0.08)' }} data-testid="block-raw-data">
                    <div className="flex items-center gap-1.5 mb-1">
                      <Database className="w-3 h-3" style={{ color: TP.rockDim }} />
                      <span className="text-[9px] uppercase tracking-wider font-bold" style={{ color: TP.earthLight }}>Donnees brutes</span>
                    </div>
                    <div className="text-[7px] font-mono space-y-0.5" style={{ color: TP.rockDim }}>
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
