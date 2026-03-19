/**
 * Mode GUIDE PRO — SUPRA-INTELLIGENT Terrain Premium
 * ====================================================
 * Palette: vert foret, brun terre, sable, gris roche.
 * Blocs: Conditions, Solunaire (WOW), Plan d'approche.
 * STEEVE-MAX: zero pollution, hierarchie terrain premium.
 */
import { useEffect, useState } from 'react';
import { Crosshair, Moon, Wind, Target, Clock, Thermometer, Gauge, Activity } from 'lucide-react';
import SolunarChart from './SolunarChart';

const INT_CL = {
  'extrême': 'border-[#D97706]/40 bg-[#D97706]/10 text-[#F59E0B]',
  'fort': 'border-[#D97706]/30 bg-[#D97706]/8 text-[#D4C4A0]',
  'modéré': 'border-[#8B6F47]/30 bg-[#8B6F47]/10 text-[#C2A97E]',
  'faible': 'border-[#4B5563]/30 bg-[#4B5563]/8 text-[#6B7280]',
};

export default function ModeGuidePro({ location, species, month, onNavigate, onShowMarkers }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const API = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    if (!location) return;
    setLoading(true);
    const today = new Date().toISOString().split('T')[0];
    const params = new URLSearchParams({ lat: location.lat, lng: location.lng, species, month, date: today });
    fetch(`${API}/api/v3/intelligence/guide-pro?${params}`)
      .then(r => r.json()).then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [location, species, month, API]);

  if (loading) return <div className="text-[#6B7280] text-xs py-8 text-center font-mono">Analyse terrain en cours...</div>;
  if (!data) return <div className="text-[#6B7280] text-xs py-8 text-center">Position requise</div>;

  const s = data.solunar;
  const ap = data.approach_plan;
  const bt = data.best_time;
  const globalLabel = bt.score >= 80 ? 'EXTREME' : bt.score >= 60 ? 'FORT' : bt.score >= 40 ? 'MODERE' : 'FAIBLE';

  return (
    <div className="space-y-3" data-testid="mode-guide-pro">
      {/* ══ BLOC CONDITIONS ══ */}
      <div className="rounded-lg p-3" style={{ background: 'linear-gradient(135deg, rgba(45,80,22,0.08), rgba(139,111,71,0.06))', border: '1px solid rgba(139,111,71,0.15)' }}>
        <div className="flex items-center gap-2 mb-2">
          <Activity className="w-3.5 h-3.5" style={{ color: '#4A7A2E' }} />
          <span className="text-[9px] font-bold tracking-[0.12em] uppercase" style={{ color: '#A8885E' }}>Conditions actuelles</span>
          <span className={`ml-auto text-[8px] font-bold uppercase px-2 py-0.5 rounded border ${INT_CL[bt.label] || INT_CL['faible']}`}>{globalLabel}</span>
        </div>
        <div className="grid grid-cols-4 gap-2">
          <div className="rounded p-1.5 text-center" style={{ background: 'rgba(45,80,22,0.06)', border: '1px solid rgba(45,80,22,0.1)' }}>
            <Wind className="w-3 h-3 mx-auto mb-0.5" style={{ color: '#6B7280' }} />
            <div className="text-[8px]" style={{ color: '#9CA3AF' }}>Vent</div>
            <div className="text-xs font-bold" style={{ color: '#C2A97E' }}>{ap.vent.direction_deg}° {ap.vent.force}</div>
          </div>
          <div className="rounded p-1.5 text-center" style={{ background: 'rgba(45,80,22,0.06)', border: '1px solid rgba(45,80,22,0.1)' }}>
            <Gauge className="w-3 h-3 mx-auto mb-0.5" style={{ color: '#6B7280' }} />
            <div className="text-[8px]" style={{ color: '#9CA3AF' }}>Pression</div>
            <div className="text-xs font-bold" style={{ color: '#C2A97E' }}>1013 hPa</div>
          </div>
          <div className="rounded p-1.5 text-center" style={{ background: 'rgba(45,80,22,0.06)', border: '1px solid rgba(45,80,22,0.1)' }}>
            <Thermometer className="w-3 h-3 mx-auto mb-0.5" style={{ color: '#6B7280' }} />
            <div className="text-[8px]" style={{ color: '#9CA3AF' }}>Temperature</div>
            <div className="text-xs font-bold" style={{ color: '#C2A97E' }}>-8°C</div>
          </div>
          <div className="rounded p-1.5 text-center" style={{ background: 'rgba(45,80,22,0.06)', border: '1px solid rgba(45,80,22,0.1)' }}>
            <Target className="w-3 h-3 mx-auto mb-0.5" style={{ color: '#6B7280' }} />
            <div className="text-[8px]" style={{ color: '#9CA3AF' }}>Score</div>
            <div className="text-xs font-bold" style={{ color: '#D97706' }}>{bt.score}/100</div>
          </div>
        </div>
      </div>

      {/* ══ BLOC SOLUNAIRE (WOW) ══ */}
      <div className="rounded-lg p-3" style={{ background: 'linear-gradient(135deg, rgba(26,58,10,0.08), rgba(92,74,48,0.06))', border: '1px solid rgba(139,111,71,0.12)' }}>
        <div className="flex items-center gap-2 mb-2">
          <Moon className="w-3.5 h-3.5" style={{ color: '#C2A97E' }} />
          <span className="text-[9px] font-bold tracking-[0.12em] uppercase" style={{ color: '#A8885E' }}>
            {s.moon.phase_name} — {s.moon.illumination}%
          </span>
          <span className="ml-auto text-[7px] font-mono" style={{ color: '#6B7280' }}>Score solunaire: {s.solunar_score}</span>
        </div>
        <SolunarChart solunar={s} />
        <div className="flex gap-3 mt-2">
          <span className="flex items-center gap-1 text-[7px]" style={{ color: '#6B7280' }}>
            <span className="w-2 h-1.5 rounded-sm" style={{ background: 'rgba(217,119,6,0.3)' }} />Majeure
          </span>
          <span className="flex items-center gap-1 text-[7px]" style={{ color: '#6B7280' }}>
            <span className="w-2 h-1.5 rounded-sm" style={{ background: 'rgba(194,169,126,0.2)' }} />Mineure
          </span>
          <span className="flex items-center gap-1 text-[7px]" style={{ color: '#6B7280' }}>
            <span className="w-1.5 h-1.5 rounded-full" style={{ background: '#4A7A2E' }} />Pointeur temps reel
          </span>
        </div>
      </div>

      {/* ══ FENETRES DE CHASSE ══ */}
      <div className="rounded-lg p-3" style={{ background: 'rgba(45,80,22,0.04)', border: '1px solid rgba(139,111,71,0.1)' }}>
        <div className="flex items-center gap-2 mb-2">
          <Clock className="w-3.5 h-3.5" style={{ color: '#D97706' }} />
          <span className="text-[9px] font-bold tracking-[0.12em] uppercase" style={{ color: '#A8885E' }}>
            Fenetres de chasse ({s.sun?.rise} — {s.sun?.set})
          </span>
        </div>
        {data.hunting_windows?.length === 0 ? (
          <div className="text-[9px]" style={{ color: '#6B7280' }}>Aucune fenetre optimale aujourd'hui</div>
        ) : (
          <div className="space-y-1">
            {data.hunting_windows?.map((w, i) => (
              <div key={i} className={`flex items-center gap-2 px-2.5 py-1.5 rounded border ${INT_CL[w.intensity] || INT_CL['faible']}`}>
                <Clock className="w-3 h-3 flex-shrink-0" />
                <span className="text-[10px] font-mono font-bold">{w.start} — {w.end}</span>
                <span className="text-[8px] opacity-60">{w.duration_min}min</span>
                <span className="ml-auto text-[8px] font-bold uppercase">{w.intensity}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ══ BLOC PLAN D'APPROCHE ══ */}
      <div className="rounded-lg p-3" style={{ background: 'linear-gradient(135deg, rgba(45,80,22,0.06), rgba(139,111,71,0.04))', border: '1px solid rgba(74,122,46,0.15)' }}>
        <div className="flex items-center gap-2 mb-2">
          <Crosshair className="w-3.5 h-3.5" style={{ color: '#4A7A2E' }} />
          <span className="text-[9px] font-bold tracking-[0.12em] uppercase" style={{ color: '#A8885E' }}>Plan d'approche</span>
        </div>
        <div className="grid grid-cols-2 gap-1.5">
          <div className="rounded p-2 cursor-pointer hover:brightness-110 transition-all" style={{ background: 'rgba(26,58,10,0.08)', border: '1px solid rgba(45,80,22,0.12)' }}
            onClick={() => { if (onNavigate && location) onNavigate(location.lat, location.lng); if (onShowMarkers) onShowMarkers({ idealPosition: location }); }}
          >
            <div className="text-[7px] mb-0.5" style={{ color: '#6B7280' }}>Position ideale</div>
            <div className="text-xs font-bold" style={{ color: '#4A7A2E' }}>{location?.lat?.toFixed(4)}, {location?.lng?.toFixed(4)}</div>
          </div>
          <div className="rounded p-2" style={{ background: 'rgba(26,58,10,0.08)', border: '1px solid rgba(45,80,22,0.12)' }}>
            <div className="text-[7px] mb-0.5" style={{ color: '#6B7280' }}>Angle d'entree</div>
            <div className="text-xs font-bold" style={{ color: '#C2A97E' }}>{ap.angle_entree}°</div>
          </div>
          <div className="rounded p-2" style={{ background: 'rgba(26,58,10,0.08)', border: '1px solid rgba(45,80,22,0.12)' }}>
            <div className="text-[7px] mb-0.5" style={{ color: '#6B7280' }}>Affut recommande</div>
            <div className="text-xs font-bold" style={{ color: '#C2A97E' }}>{ap.affut_recommande?.type}</div>
          </div>
          <div className="rounded p-2" style={{ background: 'rgba(26,58,10,0.08)', border: '1px solid rgba(45,80,22,0.12)' }}>
            <div className="text-[7px] mb-0.5" style={{ color: '#6B7280' }}>Terrain</div>
            <div className="text-xs font-bold" style={{ color: '#D97706' }}>{data.terrain?.consolidated_score}/100</div>
          </div>
        </div>
        {ap.zones_a_eviter?.filter(z => z.active).length > 0 && (
          <div className="mt-2 space-y-0.5">
            {ap.zones_a_eviter.filter(z => z.active).map((z, i) => (
              <div key={i} className="text-[8px] flex items-center gap-1.5" style={{ color: '#D97706' }}>
                <span className="w-1.5 h-1.5 rounded-full" style={{ background: '#D97706' }} />{z.raison}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
