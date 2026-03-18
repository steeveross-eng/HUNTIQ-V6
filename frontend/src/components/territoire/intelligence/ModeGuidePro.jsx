/**
 * Mode GUIDE PRO — Tableau solunaire + fenêtres de chasse + plan d'approche
 */
import { useEffect, useState } from 'react';
import { Crosshair, Moon, Sun, Wind, Target, Clock } from 'lucide-react';
import SolunarChart from './SolunarChart';

const INTENSITY_COLORS = { extrême: 'bg-red-500/20 text-red-400 border-red-500/30',
  fort: 'bg-orange-500/15 text-orange-400 border-orange-500/30',
  modéré: 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30',
  faible: 'bg-gray-500/15 text-gray-400 border-gray-500/30' };

export default function ModeGuidePro({ location, species, month }) {
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

  if (loading) return <div className="text-gray-600 text-sm py-8 text-center">Chargement Guide Pro...</div>;
  if (!data) return <div className="text-gray-600 text-sm py-8 text-center">Sélectionnez une position sur la carte</div>;

  const s = data.solunar;
  const ap = data.approach_plan;
  const bt = data.best_time;

  return (
    <div className="space-y-4" data-testid="mode-guide-pro">
      {/* Meilleur temps */}
      <div className={`p-4 rounded-lg border ${INTENSITY_COLORS[bt.label]}`}>
        <div className="flex items-center gap-2 mb-1">
          <Target className="w-4 h-4" />
          <span className="text-xs font-bold uppercase tracking-wider">Meilleur temps de chasse</span>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold">{bt.score}</span>
          <span className="text-xs opacity-60">/100</span>
          <span className="text-sm font-semibold ml-2 uppercase">{bt.label}</span>
        </div>
        <div className="flex gap-4 mt-1 text-[9px] opacity-60">
          <span>Solunaire: {bt.solunar_contribution}</span>
          <span>Terrain: {bt.terrain_contribution}</span>
        </div>
      </div>

      {/* Courbe solunaire */}
      <div className="bg-[#12121e] border border-gray-800/50 rounded-lg p-3">
        <div className="flex items-center gap-2 mb-2">
          <Moon className="w-3.5 h-3.5 text-blue-400" />
          <span className="text-[10px] text-gray-400 uppercase tracking-wider">
            {s.moon.phase_name} — {s.moon.illumination}% illumination
          </span>
        </div>
        <SolunarChart solunar={s} />
        <div className="flex gap-3 mt-2 text-[8px] text-gray-500">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500/40" />Majeure</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-amber-500/40" />Mineure</span>
          <span>OH=Overhead UF=Underfoot LV=Lever CO=Coucher</span>
        </div>
      </div>

      {/* Fenêtres de chasse */}
      <div className="bg-[#12121e] border border-gray-800/50 rounded-lg p-3">
        <div className="flex items-center gap-2 mb-2">
          <Sun className="w-3.5 h-3.5 text-amber-400" />
          <span className="text-[10px] text-gray-400 uppercase tracking-wider">
            Fenêtres de chasse ({s.sun.rise} — {s.sun.set})
          </span>
        </div>
        {data.hunting_windows.length === 0 ? (
          <div className="text-[10px] text-gray-600">Aucune fenêtre optimale aujourd'hui</div>
        ) : (
          <div className="space-y-1.5">
            {data.hunting_windows.map((w, i) => (
              <div key={i} className={`flex items-center gap-3 px-3 py-2 rounded border ${INTENSITY_COLORS[w.intensity]}`}>
                <Clock className="w-3.5 h-3.5 flex-shrink-0" />
                <span className="text-xs font-mono font-bold">{w.start} — {w.end}</span>
                <span className="text-[9px] opacity-60">{w.duration_min}min</span>
                <span className="ml-auto text-[9px] font-semibold uppercase">{w.intensity}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Plan d'approche */}
      <div className="bg-[#12121e] border border-gray-800/50 rounded-lg p-3">
        <div className="flex items-center gap-2 mb-2">
          <Crosshair className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-[10px] text-gray-400 uppercase tracking-wider">Plan d'approche</span>
        </div>
        <div className="grid grid-cols-2 gap-2 text-[10px]">
          <div className="bg-[#0c0c14] rounded p-2">
            <div className="text-gray-500 mb-0.5">Angle d'entrée</div>
            <div className="text-sm font-bold">{ap.angle_entree}°</div>
          </div>
          <div className="bg-[#0c0c14] rounded p-2">
            <div className="text-gray-500 mb-0.5">Vent</div>
            <div className="text-sm font-bold flex items-center gap-1">
              <Wind className="w-3 h-3" />{ap.vent.direction_deg}° {ap.vent.force}
            </div>
          </div>
          <div className="bg-[#0c0c14] rounded p-2">
            <div className="text-gray-500 mb-0.5">Affût</div>
            <div className="text-sm font-bold">{ap.affut_recommande.type}</div>
          </div>
          <div className="bg-[#0c0c14] rounded p-2">
            <div className="text-gray-500 mb-0.5">Terrain</div>
            <div className="text-sm font-bold">{data.terrain.consolidated_score}/100</div>
          </div>
        </div>
        {ap.zones_a_eviter.filter(z => z.active).length > 0 && (
          <div className="mt-2 space-y-1">
            {ap.zones_a_eviter.filter(z => z.active).map((z, i) => (
              <div key={i} className="text-[9px] text-red-400/70 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-red-500" />{z.raison}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
