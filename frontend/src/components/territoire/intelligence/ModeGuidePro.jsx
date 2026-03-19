/**
 * Mode GUIDE PRO — SUPRA-INTELLIGENT Terrain Premium
 * Section X: Lisibilite premium — polices agrandies, espacement, hierarchie.
 * Palette: cream #F2E9D8, sand-gray #C8BBA6, forest #4A7A2E, earth #A8885E.
 */
import { useEffect, useState, useRef } from 'react';
import { Crosshair, Moon, Wind, Target, Clock, Thermometer, Gauge, Activity, Mountain } from 'lucide-react';
import SolunarChart from './SolunarChart';
import useBionicStore from '@/stores/useBionicStore';

const P = {
  cream: '#F2E9D8', creamDim: '#C8BBA6',
  forest: '#4A7A2E', earth: '#A8885E',
  sand: '#C2A97E', sandLight: '#D4C4A0',
  rock: '#9CA3AF', rockDim: '#6B7280',
  bionic: '#D97706', bionicGlow: '#F59E0B',
};

const INT_CL = {
  'extreme': 'border-[#D97706]/40 bg-[#D97706]/12 text-[#F59E0B]',
  'fort': 'border-[#D97706]/30 bg-[#D97706]/8 text-[#D4C4A0]',
  'modere': 'border-[#8B6F47]/30 bg-[#8B6F47]/10 text-[#C2A97E]',
  'faible': 'border-[#6B7280]/30 bg-[#6B7280]/8 text-[#9CA3AF]',
};

function classifyLabel(score) {
  if (score >= 80) return 'extreme';
  if (score >= 60) return 'fort';
  if (score >= 40) return 'modere';
  return 'faible';
}

export default function ModeGuidePro({ location, species, month, onNavigate, onShowMarkers }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const API = process.env.REACT_APP_BACKEND_URL;
  const setIntelligenceWeather = useBionicStore(s => s.setIntelligenceWeather);
  const weatherUpdated = useRef(false);

  useEffect(() => {
    if (!location) return;
    setLoading(true);
    weatherUpdated.current = false;
    const today = new Date().toISOString().split('T')[0];
    const params = new URLSearchParams({ lat: location.lat, lng: location.lng, species, month, date: today });
    fetch(`${API}/api/v3/intelligence/guide-pro?${params}`)
      .then(r => r.json()).then(d => {
        setData(d);
        setLoading(false);
        if (d.weather_official && !weatherUpdated.current) {
          setIntelligenceWeather(d.weather_official);
          weatherUpdated.current = true;
        }
      })
      .catch(() => setLoading(false));
  }, [location, species, month, API, setIntelligenceWeather]);

  if (loading) return <div style={{ color: P.creamDim }} className="text-base py-12 text-center font-medium">Analyse terrain en cours...</div>;
  if (!data) return <div style={{ color: P.creamDim }} className="text-base py-12 text-center font-medium">Position requise</div>;

  const s = data.solunar;
  const ap = data.approach_plan;
  const bt = data.best_time;
  const terrain = data.terrain;
  const wo = data.weather_official || {};
  const terrainLabel = classifyLabel(terrain.consolidated_score);
  const chasseLabel = classifyLabel(bt.score);

  return (
    <div className="space-y-5" data-testid="mode-guide-pro">
      {/* ══ SCORE TERRAIN — Conditions Actuelles ══ */}
      <div className="rounded-lg p-5" style={{ background: 'linear-gradient(135deg, rgba(45,80,22,0.12), rgba(139,111,71,0.1))', border: '1px solid rgba(74,122,46,0.22)' }}>
        <div className="flex items-center gap-2.5 mb-4">
          <Mountain className="w-5 h-5" style={{ color: P.forest }} />
          <span className="text-base font-bold tracking-wider uppercase" style={{ color: P.cream }}>Score Terrain — Conditions Actuelles</span>
        </div>
        <div className="flex items-center gap-6">
          <div className="flex-1">
            <div className="flex items-baseline gap-3">
              <span className="text-5xl font-black tracking-tight" style={{ color: P.cream }}>{Math.round(terrain.consolidated_score)}</span>
              <span className="text-lg font-medium" style={{ color: P.rockDim }}>/100</span>
              <span className={`text-sm font-bold uppercase px-3 py-1 rounded border ml-3 ${INT_CL[terrainLabel]}`}>{terrain.classe}</span>
            </div>
            <div className="grid grid-cols-4 gap-3 mt-4">
              {[
                { val: terrain.pression, label: 'Pression' },
                { val: terrain.alimentation, label: 'Alimentation' },
                { val: terrain.repos, label: 'Repos' },
                { val: terrain.corridors, label: 'Corridors' },
              ].map(item => (
                <div key={item.label} className="text-center rounded-lg p-3" style={{ background: 'rgba(45,80,22,0.08)' }}>
                  <div className="text-xl font-bold" style={{ color: P.sandLight }}>{Math.round(item.val)}</div>
                  <div className="text-xs uppercase font-medium mt-0.5" style={{ color: P.creamDim }}>{item.label}</div>
                </div>
              ))}
            </div>
          </div>
          {/* Score Chasse */}
          <div className="text-center px-5 py-4 rounded-lg" style={{ background: 'rgba(217,119,6,0.1)', border: '1px solid rgba(217,119,6,0.2)' }}>
            <div className="text-xs uppercase tracking-wider font-medium mb-1" style={{ color: P.creamDim }}>Score Chasse</div>
            <div className="text-4xl font-black" style={{ color: P.bionicGlow }}>{Math.round(bt.score)}</div>
            <span className={`text-xs font-bold uppercase px-2 py-0.5 rounded border mt-1 inline-block ${INT_CL[chasseLabel]}`}>{chasseLabel}</span>
          </div>
        </div>
      </div>

      {/* ══ CONDITIONS (Section 5: meteo officielle) ══ */}
      <div className="rounded-lg p-5" style={{ background: 'linear-gradient(135deg, rgba(45,80,22,0.1), rgba(139,111,71,0.07))', border: '1px solid rgba(139,111,71,0.18)' }}>
        <div className="flex items-center gap-2.5 mb-3">
          <Activity className="w-5 h-5" style={{ color: P.forest }} />
          <span className="text-base font-bold tracking-wider uppercase" style={{ color: P.cream }}>Conditions actuelles</span>
        </div>
        <div className="grid grid-cols-4 gap-3">
          {[
            { icon: Wind, label: 'Vent', value: `${ap.vent.direction_deg}° ${wo.wind_force || ap.vent.force}` },
            { icon: Gauge, label: 'Vent km/h', value: wo.wind_speed_kmh || '--' },
            { icon: Thermometer, label: 'Temperature', value: wo.temperature != null ? `${wo.temperature}°C` : '--' },
            { icon: Target, label: 'Intensite', value: `${Math.round(s.solunar_score)}/100` },
          ].map(item => (
            <div key={item.label} className="rounded-lg p-3 text-center" style={{ background: 'rgba(45,80,22,0.07)', border: '1px solid rgba(45,80,22,0.12)' }}>
              <item.icon className="w-5 h-5 mx-auto mb-1.5" style={{ color: P.rockDim }} />
              <div className="text-xs font-medium" style={{ color: P.creamDim }}>{item.label}</div>
              <div className="text-base font-bold mt-0.5" style={{ color: P.cream }}>{item.value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ══ BLOC SOLUNAIRE (WOW) ══ */}
      <div className="rounded-lg p-5" style={{ background: 'linear-gradient(135deg, rgba(26,58,10,0.1), rgba(92,74,48,0.08))', border: '1px solid rgba(139,111,71,0.15)' }}>
        <div className="flex items-center gap-2.5 mb-3">
          <Moon className="w-5 h-5" style={{ color: P.sand }} />
          <span className="text-base font-bold tracking-wider uppercase" style={{ color: P.cream }}>
            {s.moon.phase_name} — {s.moon.illumination}%
          </span>
          <span className="ml-auto text-sm font-mono font-medium" style={{ color: P.creamDim }}>Score: {s.solunar_score}</span>
        </div>
        <SolunarChart solunar={s} />
      </div>

      {/* ══ FENETRES DE CHASSE ══ */}
      <div className="rounded-lg p-5" style={{ background: 'rgba(45,80,22,0.05)', border: '1px solid rgba(139,111,71,0.12)' }}>
        <div className="flex items-center gap-2.5 mb-3">
          <Clock className="w-5 h-5" style={{ color: P.bionic }} />
          <span className="text-base font-bold tracking-wider uppercase" style={{ color: P.cream }}>
            Fenetres de chasse ({s.sun?.rise} — {s.sun?.set})
          </span>
        </div>
        {data.hunting_windows?.length === 0 ? (
          <div className="text-base font-medium" style={{ color: P.creamDim }}>Aucune fenetre optimale aujourd'hui</div>
        ) : (
          <div className="space-y-2">
            {data.hunting_windows?.map((w, i) => {
              const cl = classifyLabel(w.intensity === 'fort' ? 70 : w.intensity === 'extreme' ? 90 : w.intensity === 'modere' || w.intensity === 'modéré' ? 50 : 20);
              return (
                <div key={i} className={`flex items-center gap-3 px-4 py-3 rounded-lg border ${INT_CL[cl]}`}>
                  <Clock className="w-5 h-5 flex-shrink-0" />
                  <span className="text-base font-mono font-bold">{w.start} — {w.end}</span>
                  <span className="text-sm font-medium opacity-70">{w.duration_min}min</span>
                  <span className="ml-auto text-sm font-bold uppercase">{w.intensity}</span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* ══ PLAN D'APPROCHE ══ */}
      <div className="rounded-lg p-5" style={{ background: 'linear-gradient(135deg, rgba(45,80,22,0.08), rgba(139,111,71,0.06))', border: '1px solid rgba(74,122,46,0.18)' }}>
        <div className="flex items-center gap-2.5 mb-3">
          <Crosshair className="w-5 h-5" style={{ color: P.forest }} />
          <span className="text-base font-bold tracking-wider uppercase" style={{ color: P.cream }}>Plan d'approche</span>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-lg p-4 cursor-pointer hover:brightness-110 transition-all" style={{ background: 'rgba(26,58,10,0.1)', border: '1px solid rgba(45,80,22,0.15)' }}
            onClick={() => { if (onNavigate && location) onNavigate(location.lat, location.lng); if (onShowMarkers) onShowMarkers({ idealPosition: location }); }}
          >
            <div className="text-xs font-medium mb-1" style={{ color: P.creamDim }}>Position ideale</div>
            <div className="text-base font-bold" style={{ color: P.forest }}>{location?.lat?.toFixed(4)}, {location?.lng?.toFixed(4)}</div>
          </div>
          <div className="rounded-lg p-4" style={{ background: 'rgba(26,58,10,0.1)', border: '1px solid rgba(45,80,22,0.15)' }}>
            <div className="text-xs font-medium mb-1" style={{ color: P.creamDim }}>Angle d'entree</div>
            <div className="text-base font-bold" style={{ color: P.sandLight }}>{ap.angle_entree}°</div>
          </div>
          <div className="rounded-lg p-4" style={{ background: 'rgba(26,58,10,0.1)', border: '1px solid rgba(45,80,22,0.15)' }}>
            <div className="text-xs font-medium mb-1" style={{ color: P.creamDim }}>Affut recommande</div>
            <div className="text-base font-bold" style={{ color: P.sandLight }}>{ap.affut_recommande?.type}</div>
          </div>
          <div className="rounded-lg p-4" style={{ background: 'rgba(26,58,10,0.1)', border: '1px solid rgba(45,80,22,0.15)' }}>
            <div className="text-xs font-medium mb-1" style={{ color: P.creamDim }}>Terrain consolide</div>
            <div className="text-base font-bold" style={{ color: P.bionic }}>{Math.round(terrain.consolidated_score)}/100</div>
          </div>
        </div>
        {ap.zones_a_eviter?.filter(z => z.active).length > 0 && (
          <div className="mt-3 space-y-1">
            {ap.zones_a_eviter.filter(z => z.active).map((z, i) => (
              <div key={i} className="text-sm flex items-center gap-2 font-medium" style={{ color: P.bionic }}>
                <span className="w-2 h-2 rounded-full" style={{ background: P.bionic }} />{z.raison}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
