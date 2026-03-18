/**
 * IntelligenceDashboard — Tableau central INTELLIGENCE
 * ======================================================
 * Occupe toute la zone principale de MON TERRITOIRE.
 * 3 modes: Scientifique, Terrain, Guide Pro (solunaire).
 * Synchronisation bi-directionnelle carte ↔ intelligence.
 * STEEVE-MAX: cockpit analytique, dark, cartésien.
 */
import { useState, useEffect, useCallback } from 'react';
import { X, FlaskConical, Compass, Crosshair, BarChart3, TrendingUp, ClipboardList } from 'lucide-react';
import useBionicStore from '@/stores/useBionicStore';
import ModeScientifique from './intelligence/ModeScientifique';
import ModeTerrain from './intelligence/ModeTerrain';
import ModeGuidePro from './intelligence/ModeGuidePro';

const MODES = [
  { id: 'guide', label: 'Guide Pro', Icon: Crosshair, color: 'text-emerald-400' },
  { id: 'scientifique', label: 'Scientifique', Icon: FlaskConical, color: 'text-cyan-400' },
  { id: 'terrain', label: 'Terrain', Icon: Compass, color: 'text-amber-400' },
];

const TABS = [
  { id: 'dashboard', label: 'Tableau', Icon: BarChart3 },
  { id: 'forecast', label: 'Forecast', Icon: TrendingUp },
  { id: 'plan', label: 'Plan', Icon: ClipboardList },
];

export default function IntelligenceDashboard({ onClose, waypointCenter, selectedSpecies, currentMonth }) {
  const [activeMode, setActiveMode] = useState('guide');
  const [activeTab, setActiveTab] = useState('dashboard');
  const { summary, forecast, plan, fetchSummary, fetchForecast, fetchPlan, setLocation, setSpecies, setMonth } = useBionicStore();

  // Sync carte → intelligence
  useEffect(() => {
    if (waypointCenter) {
      setLocation({ lat: waypointCenter.lat, lng: waypointCenter.lng });
    }
  }, [waypointCenter, setLocation]);

  useEffect(() => { if (selectedSpecies) setSpecies(selectedSpecies); }, [selectedSpecies, setSpecies]);
  useEffect(() => { if (currentMonth) setMonth(currentMonth); }, [currentMonth, setMonth]);

  const location = waypointCenter ? { lat: waypointCenter.lat, lng: waypointCenter.lng } : null;
  const species = selectedSpecies || 'CHEVREUIL';
  const month = currentMonth || new Date().getMonth() + 1;

  // Fetch data pour tabs
  useEffect(() => {
    if (!location) return;
    if (activeTab === 'dashboard') fetchSummary();
    if (activeTab === 'forecast') fetchForecast();
    if (activeTab === 'plan') fetchPlan();
  }, [activeTab, location, species, month, fetchSummary, fetchForecast, fetchPlan]);

  const CLASSE_C = { OPTIMAL: 'text-red-400', BON: 'text-amber-400', MODERE: 'text-emerald-400', FAIBLE: 'text-blue-400' };

  return (
    <div className="absolute inset-0 z-[1000] bg-[#0a0a12]/98 backdrop-blur-sm overflow-auto" data-testid="intelligence-dashboard">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-[#0c0c14] border-b border-gray-800/50 px-4 py-2 flex items-center gap-3">
        <BarChart3 className="w-4 h-4 text-cyan-400" />
        <span className="text-sm font-semibold tracking-tight text-gray-200">Intelligence</span>

        {/* Mode selector */}
        <div className="flex gap-1 ml-4">
          {MODES.map(m => (
            <button key={m.id} onClick={() => setActiveMode(m.id)}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-[10px] transition-all ${
                activeMode === m.id ? `${m.color} bg-white/5 font-bold` : 'text-gray-500 hover:text-gray-300'
              }`} data-testid={`mode-${m.id}`}>
              <m.Icon className="w-3 h-3" />{m.label}
            </button>
          ))}
        </div>

        {/* Tabs */}
        <div className="flex gap-1 ml-auto mr-4">
          {TABS.map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)}
              className={`flex items-center gap-1 px-2 py-1 rounded text-[9px] transition-all ${
                activeTab === t.id ? 'text-gray-200 bg-white/5' : 'text-gray-600 hover:text-gray-400'
              }`} data-testid={`tab-${t.id}`}>
              <t.Icon className="w-3 h-3" />{t.label}
            </button>
          ))}
        </div>

        <button onClick={onClose} className="p-1 text-gray-500 hover:text-white transition-colors" data-testid="intelligence-close">
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content */}
      <div className="p-4 max-w-5xl mx-auto">
        {!location && (
          <div className="text-center text-gray-600 text-sm py-16">
            Sélectionnez un point sur la carte pour activer l'analyse Intelligence
          </div>
        )}

        {location && activeTab === 'dashboard' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Panneau mode actif (2/3) */}
            <div className="lg:col-span-2">
              {activeMode === 'guide' && <ModeGuidePro location={location} species={species} month={month} />}
              {activeMode === 'scientifique' && <ModeScientifique location={location} species={species} month={month} />}
              {activeMode === 'terrain' && <ModeTerrain location={location} species={species} month={month} />}
            </div>

            {/* Sidebar analytics (1/3) */}
            <div className="space-y-3">
              {summary && (
                <>
                  <div className="bg-[#12121e] border border-gray-800/50 rounded-lg p-3">
                    <div className="text-[9px] text-gray-500 uppercase mb-1">Score consolidé</div>
                    <div className={`text-2xl font-bold ${CLASSE_C[summary.consolidated.classe]}`}>
                      {summary.consolidated.score}<span className="text-xs text-gray-600">/100</span>
                    </div>
                    <div className="text-[9px] text-gray-500 mt-0.5">{summary.consolidated.label}</div>
                  </div>
                  {Object.entries(summary.domains).map(([domain, engines]) => (
                    <div key={domain} className="bg-[#12121e] border border-gray-800/50 rounded-lg p-2.5">
                      <div className="text-[8px] text-gray-500 uppercase mb-1">{domain}</div>
                      {engines.map(e => (
                        <div key={e.engine} className="flex justify-between py-0.5">
                          <span className="text-[9px] text-gray-400">{e.engine}</span>
                          <span className="text-[9px] font-mono">{e.score}</span>
                        </div>
                      ))}
                    </div>
                  ))}
                </>
              )}
            </div>
          </div>
        )}

        {location && activeTab === 'forecast' && forecast && (
          <div className="space-y-4">
            <div className="bg-[#12121e] border border-gray-800/50 rounded-lg p-4">
              <div className="text-xs text-gray-400 mb-3">Variation mensuelle — {species}</div>
              <div className="flex items-end gap-1.5 h-32">
                {forecast.monthly_data.map(m => {
                  const h = Math.max(4, (m.score / 100) * 100);
                  const isBest = m.month === forecast.best_month;
                  return (
                    <div key={m.month} className="flex-1 flex flex-col items-center gap-0.5">
                      <span className="text-[7px] text-gray-500">{m.score}</span>
                      <div className={`w-full rounded-t ${isBest ? 'bg-emerald-500' : 'bg-cyan-800/60'}`} style={{ height: `${h}%` }} />
                      <span className="text-[7px] text-gray-600">{m.month}</span>
                    </div>
                  );
                })}
              </div>
            </div>
            <div className="grid grid-cols-4 gap-2">
              {Object.entries(forecast.seasonal_scores).map(([s, score]) => (
                <div key={s} className="bg-[#12121e] border border-gray-800/50 rounded-lg p-3 text-center">
                  <div className="text-lg font-bold">{score}</div>
                  <div className="text-[8px] text-gray-500 uppercase">{s}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {location && activeTab === 'plan' && plan && (
          <div className="space-y-2">
            <div className="bg-[#12121e] border border-gray-800/50 rounded-lg p-4 mb-3">
              <span className={`text-3xl font-bold ${CLASSE_C[plan.overall_classe]}`}>{plan.overall_score}</span>
              <span className="text-xs text-gray-500 ml-2">{plan.critical_count} actions prioritaires</span>
            </div>
            {plan.actions.map(a => (
              <div key={a.rank} className={`flex items-center gap-3 px-3 py-2 rounded-lg border ${
                a.urgency === 'HAUTE' || a.urgency === 'CRITIQUE' ? 'border-orange-500/30 bg-orange-500/10' : 'border-gray-800/30 bg-[#12121e]'
              }`}>
                <span className="text-sm font-bold w-8">{a.score}</span>
                <div className="flex-1">
                  <div className="text-xs text-gray-300">{a.engine}</div>
                  <div className="text-[9px] text-gray-500">{a.action}</div>
                </div>
                <span className={`text-[8px] font-bold ${a.urgency === 'HAUTE' ? 'text-orange-400' : 'text-gray-500'}`}>{a.urgency}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
