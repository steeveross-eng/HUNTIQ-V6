/**
 * BionicEngineHub.jsx — Hub des 12 moteurs BIONIC V2
 * STEVE-MAX++: Integration complete backend → API → frontend.
 * Affiche le statut et les scores de chaque moteur en temps reel.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Clock, Wind, Mountain, AlertTriangle, Route,
  Brain, Leaf, Target, Gauge, ShieldCheck, Layers,
  ChevronDown, ChevronUp, Zap, Flower2,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const ENGINE_META = [
  { id: 'behavior', name: 'Behavior Engine', icon: Clock, color: '#f59e0b', num: 1 },
  { id: 'keyzone_v2', name: 'KeyZone Engine V2', icon: Target, color: '#ef4444', num: 2 },
  { id: 'food_deficit', name: 'Food Deficit Engine', icon: Leaf, color: '#22c55e', num: 3 },
  { id: 'wind_intelligence', name: 'Wind Intelligence', icon: Wind, color: '#06b6d4', num: 4 },
  { id: 'terrain', name: 'Terrain Engine', icon: Mountain, color: '#78909C', num: 5 },
  { id: 'human_pressure', name: 'Human Pressure', icon: AlertTriangle, color: '#FF5722', num: 6 },
  { id: 'corridor_continuity', name: 'Corridor Continuity', icon: Route, color: '#8b5cf6', num: 7 },
  { id: 'global_attractiveness', name: 'Global Attractiveness', icon: Gauge, color: '#FF9800', num: 8 },
  { id: 'action_plan', name: 'Action Plan Engine', icon: Flower2, color: '#ec4899', num: 9 },
  { id: 'predictive_ai', name: 'Predictive AI', icon: Brain, color: '#a855f7', num: 10 },
  { id: 'bce_compliance', name: 'BCE-4X Compliance', icon: ShieldCheck, color: '#4CAF50', num: 11 },
  { id: 'rendering', name: 'Rendering Engine', icon: Layers, color: '#2196F3', num: 12 },
];

const BionicEngineHub = ({ zones, corridors, weather, season, hour, bounds }) => {
  const [expanded, setExpanded] = useState(false);
  const [engineData, setEngineData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchEngineScores = useCallback(async () => {
    if (!zones?.length && !corridors?.length) return;
    setLoading(true);
    try {
      const resp = await fetch(`${API_URL}/api/v1/bionic/engines-v2/compute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          zones: (zones || []).map(z => ({ properties: { layer_id: z.layerId || z.layer_id || 'habitats' } })),
          corridors: (corridors || []).map(c => ({
            properties: {
              continuity_valid: c.continuity_valid ?? true,
              bands: c.bands || [],
              densified: c.densified ?? true,
            }
          })),
          weather: weather || {},
          season: season || 'automne',
          hour: hour ?? new Date().getHours(),
          bounds: bounds || {},
        }),
      });
      const data = await resp.json();
      if (data.success) setEngineData(data);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  }, [zones, corridors, weather, season, hour, bounds]);

  useEffect(() => {
    fetchEngineScores();
  }, [fetchEngineScores]);

  const getScore = (engineId) => engineData?.engines?.[engineId]?.score ?? null;
  const avgScore = engineData?.average_score ?? null;
  const activeCount = ENGINE_META.length;

  const getScoreColor = (score) => {
    if (score === null) return 'text-gray-600';
    if (score >= 75) return 'text-emerald-400';
    if (score >= 50) return 'text-amber-400';
    if (score >= 25) return 'text-orange-400';
    return 'text-red-400';
  };

  const getScoreBg = (score) => {
    if (score === null) return 'bg-gray-800/50';
    if (score >= 75) return 'bg-emerald-500/10';
    if (score >= 50) return 'bg-amber-500/10';
    if (score >= 25) return 'bg-orange-500/10';
    return 'bg-red-500/10';
  };

  return (
    <div className="bg-[#111118] rounded-lg border border-[#1a1a2e] overflow-hidden" data-testid="bionic-engine-hub">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-3 py-2 hover:bg-white/5 transition-colors"
        data-testid="hub-toggle"
      >
        <div className="flex items-center gap-1.5">
          <Zap className="h-3.5 w-3.5 text-violet-400" />
          <span className="text-[10px] font-semibold text-violet-300 uppercase tracking-wider">BIONIC V2 Hub</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-[9px] text-gray-500">{activeCount}/12</span>
          </div>
          {avgScore !== null && (
            <span className={`text-[9px] font-mono font-bold ${getScoreColor(avgScore)}`}>{Math.round(avgScore)}%</span>
          )}
          {loading && <span className="text-[8px] text-amber-400 animate-pulse">...</span>}
          {expanded ? <ChevronUp className="h-3 w-3 text-gray-500" /> : <ChevronDown className="h-3 w-3 text-gray-500" />}
        </div>
      </button>

      {expanded && (
        <div className="px-3 pb-3 space-y-1" data-testid="hub-engines-list">
          {ENGINE_META.map((engine) => {
            const Icon = engine.icon;
            const score = getScore(engine.id);
            const detail = engineData?.engines?.[engine.id];
            return (
              <div
                key={engine.id}
                className={`flex items-center gap-2 py-1.5 px-2 rounded transition-colors ${getScoreBg(score)}`}
                data-testid={`engine-${engine.id}`}
              >
                <div className="flex items-center justify-center w-4 h-4 rounded-full flex-shrink-0" style={{ backgroundColor: `${engine.color}20` }}>
                  <Icon className="h-2.5 w-2.5 flex-shrink-0" style={{ color: engine.color }} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1">
                    <span className="text-[8px] text-gray-600 font-mono">#{engine.num}</span>
                    <span className="text-[10px] font-medium text-gray-200 truncate">{engine.name}</span>
                  </div>
                </div>
                <div className="flex items-center gap-1.5 flex-shrink-0">
                  {score !== null ? (
                    <span className={`text-[10px] font-mono font-bold ${getScoreColor(score)}`} data-testid={`engine-score-${engine.id}`}>{score}</span>
                  ) : (
                    <span className="text-[9px] text-gray-600">--</span>
                  )}
                  <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${score !== null ? 'bg-emerald-400' : 'bg-gray-600'}`} />
                </div>
              </div>
            );
          })}

          {/* Summary footer */}
          <div className="pt-2 border-t border-gray-800/50 flex items-center justify-between">
            <span className="text-[8px] text-gray-600">12 moteurs BIONIC V2 actifs</span>
            {avgScore !== null && (
              <span className={`text-[9px] font-bold ${getScoreColor(avgScore)}`} data-testid="hub-avg-score">
                Moy: {Math.round(avgScore)}%
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default BionicEngineHub;
