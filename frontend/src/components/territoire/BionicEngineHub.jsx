/**
 * BionicEngineHub.jsx — Hub BIONIC V3 complet
 * STEVE-MAX++: 27 engines (12 V2 + 12 V3 + 3 IA) + 3 modeles fauniques
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Clock, Wind, Mountain, AlertTriangle, Route,
  Brain, Leaf, Target, Gauge, ShieldCheck, Layers,
  ChevronDown, ChevronUp, Zap, Flower2,
  TreePine, Droplets, Footprints, Globe, Sparkles,
  BarChart3, Compass, Activity, Thermometer, Map,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const ENGINE_META = {
  v2: [
    { id: 'behavior', name: 'Behavior', icon: Clock, color: '#f59e0b' },
    { id: 'keyzone_v2', name: 'KeyZone V2', icon: Target, color: '#ef4444' },
    { id: 'food_deficit', name: 'Food Deficit', icon: Leaf, color: '#22c55e' },
    { id: 'wind_intelligence', name: 'Wind Intel', icon: Wind, color: '#06b6d4' },
    { id: 'terrain', name: 'Terrain', icon: Mountain, color: '#78909C' },
    { id: 'human_pressure', name: 'Human Press.', icon: AlertTriangle, color: '#FF5722' },
    { id: 'corridor_continuity', name: 'Corridor Cont.', icon: Route, color: '#8b5cf6' },
    { id: 'global_attractiveness', name: 'Attractiveness', icon: Gauge, color: '#FF9800' },
    { id: 'action_plan', name: 'Action Plan', icon: Flower2, color: '#ec4899' },
    { id: 'predictive_ai', name: 'Predictive AI', icon: Brain, color: '#a855f7' },
    { id: 'bce_compliance', name: 'BCE-4X', icon: ShieldCheck, color: '#4CAF50' },
    { id: 'rendering', name: 'Rendering', icon: Layers, color: '#2196F3' },
  ],
  v3: [
    { id: 'ecological_hierarchy', name: 'Eco Hierarchy', icon: TreePine, color: '#15803D' },
    { id: 'interaction', name: 'Interaction', icon: Globe, color: '#06B6D4' },
    { id: 'geopedology', name: 'GeoPedology', icon: Map, color: '#78909C' },
    { id: 'connectivity', name: 'Connectivity', icon: Footprints, color: '#8b5cf6' },
    { id: 'temporal_dynamics', name: 'Temporal Dyn.', icon: Clock, color: '#f59e0b' },
    { id: 'hotspot', name: 'Hotspot', icon: Target, color: '#ef4444' },
    { id: 'forest_structure_v2', name: 'Forest Struct.', icon: TreePine, color: '#66BB6A' },
    { id: 'food_score_v2', name: 'FoodScore V2', icon: Leaf, color: '#22C55E' },
    { id: 'wetness_v2', name: 'Wetness V2', icon: Droplets, color: '#3B82F6' },
    { id: 'geoform_v2', name: 'GeoForm V2', icon: Mountain, color: '#FF7043' },
    { id: 'behavior_v2', name: 'Behavior V2', icon: Activity, color: '#FF4D6D' },
    { id: 'attractiveness_v2', name: 'Attract. V2', icon: Sparkles, color: '#FCD34D' },
  ],
  ai: [
    { id: 'predictive_models', name: 'Pred. Models', icon: Brain, color: '#a855f7' },
    { id: 'dynamic_scoring', name: 'Dynamic Score', icon: Thermometer, color: '#ef4444' },
    { id: 'temporal_analysis', name: 'Temporal Anal.', icon: BarChart3, color: '#06b6d4' },
  ],
};

const SPECIES_META = [
  { id: 'moose', name: 'Orignal', emoji: 'M' },
  { id: 'deer', name: 'Cerf', emoji: 'C' },
  { id: 'bear', name: 'Ours', emoji: 'O' },
];

const BionicEngineHub = ({ zones, corridors, weather, season, hour, bounds, species }) => {
  const [expanded, setExpanded] = useState(false);
  const [section, setSection] = useState('v2');
  const [engineData, setEngineData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchV3Scores = useCallback(async () => {
    if (!zones?.length && !corridors?.length) return;
    setLoading(true);
    try {
      const resp = await fetch(`${API_URL}/api/v1/bionic/engines-v3/compute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          zones: (zones || []).map(z => ({ properties: { layer_id: z.layerId || z.layer_id || 'habitats' } })),
          corridors: (corridors || []).map(c => ({
            properties: {
              continuity_valid: c.continuity_valid ?? true,
              bands: c.bands || [],
              densified: c.densified ?? true,
              scoring: c.scoring || {},
            }
          })),
          weather: weather || {},
          season: season || 'automne',
          hour: hour ?? new Date().getHours(),
          species: species || 'moose',
          bounds: bounds || {},
        }),
      });
      const data = await resp.json();
      if (data.success) setEngineData(data);
    } catch { /* silent */ }
    finally { setLoading(false); }
  }, [zones, corridors, weather, season, hour, bounds, species]);

  useEffect(() => { fetchV3Scores(); }, [fetchV3Scores]);

  const getScore = (eid) => engineData?.engines?.[eid]?.score ?? null;
  const sc = (score) => score === null ? 'text-gray-600' : score >= 75 ? 'text-emerald-400' : score >= 50 ? 'text-amber-400' : score >= 25 ? 'text-orange-400' : 'text-red-400';
  const bg = (score) => score === null ? 'bg-gray-800/50' : score >= 75 ? 'bg-emerald-500/10' : score >= 50 ? 'bg-amber-500/10' : score >= 25 ? 'bg-orange-500/10' : 'bg-red-500/10';

  const totalEngines = 12 + 12 + 3;
  const finalScore = engineData?.final_score ?? null;
  const speciesScores = engineData?.species_scores ?? {};

  const renderEngine = (e) => {
    const Icon = e.icon;
    const score = getScore(e.id);
    return (
      <div key={e.id} className={`flex items-center gap-2 py-1 px-2 rounded transition-colors ${bg(score)}`} data-testid={`engine-${e.id}`}>
        <div className="flex items-center justify-center w-4 h-4 rounded-full flex-shrink-0" style={{ backgroundColor: `${e.color}20` }}>
          <Icon className="h-2.5 w-2.5 flex-shrink-0" style={{ color: e.color }} />
        </div>
        <span className="text-[10px] font-medium text-gray-200 truncate flex-1">{e.name}</span>
        {score !== null ? (
          <span className={`text-[10px] font-mono font-bold ${sc(score)}`} data-testid={`engine-score-${e.id}`}>{score}</span>
        ) : (
          <span className="text-[9px] text-gray-600">--</span>
        )}
        <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${score !== null ? 'bg-emerald-400' : 'bg-gray-600'}`} />
      </div>
    );
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
          <span className="text-[10px] font-semibold text-violet-300 uppercase tracking-wider">BIONIC V3</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-[9px] text-gray-500">{totalEngines}</span>
          </div>
          {finalScore !== null && (
            <span className={`text-[9px] font-mono font-bold ${sc(finalScore)}`} data-testid="hub-final-score">{finalScore}%</span>
          )}
          {loading && <span className="text-[8px] text-amber-400 animate-pulse">...</span>}
          {expanded ? <ChevronUp className="h-3 w-3 text-gray-500" /> : <ChevronDown className="h-3 w-3 text-gray-500" />}
        </div>
      </button>

      {expanded && (
        <div className="px-3 pb-3" data-testid="hub-engines-list">
          {/* Section tabs */}
          <div className="flex gap-1 mb-2">
            {[
              { key: 'v2', label: 'V2', count: 12 },
              { key: 'v3', label: 'V3', count: 12 },
              { key: 'ai', label: 'IA', count: 3 },
              { key: 'species', label: 'Faune', count: 3 },
            ].map(tab => (
              <button
                key={tab.key}
                onClick={() => setSection(tab.key)}
                className={`flex-1 py-1 text-[9px] font-semibold rounded transition-colors ${
                  section === tab.key ? 'bg-violet-500/20 text-violet-300' : 'bg-gray-800/50 text-gray-500 hover:text-gray-300'
                }`}
                data-testid={`tab-${tab.key}`}
              >
                {tab.label} ({tab.count})
              </button>
            ))}
          </div>

          {/* Engine lists */}
          <div className="space-y-0.5">
            {section === 'v2' && ENGINE_META.v2.map(renderEngine)}
            {section === 'v3' && ENGINE_META.v3.map(renderEngine)}
            {section === 'ai' && ENGINE_META.ai.map(renderEngine)}
            {section === 'species' && SPECIES_META.map(sp => {
              const data = speciesScores[sp.id] || {};
              const score = data.score ?? null;
              return (
                <div key={sp.id} className={`py-1.5 px-2 rounded ${bg(score)}`} data-testid={`species-${sp.id}`}>
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-medium text-gray-200">{sp.emoji} {sp.name}</span>
                    <span className={`text-[10px] font-mono font-bold ${sc(score)}`}>{score ?? '--'}</span>
                  </div>
                  {score !== null && (
                    <div className="flex gap-2 mt-1">
                      {[
                        { l: 'Alim', v: data.food_zone_score },
                        { l: 'Repos', v: data.rest_zone_score },
                        { l: 'Corr', v: data.corridor_influence },
                        { l: 'Hot', v: data.hotspot_influence },
                      ].map(d => (
                        <div key={d.l} className="flex items-center gap-0.5">
                          <span className="text-[8px] text-gray-600">{d.l}</span>
                          <span className={`text-[8px] font-mono ${sc(d.v)}`}>{d.v}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Footer */}
          <div className="pt-2 mt-2 border-t border-gray-800/50 flex items-center justify-between">
            <span className="text-[8px] text-gray-600">{totalEngines} engines + 3 especes</span>
            {finalScore !== null && (
              <span className={`text-[9px] font-bold ${sc(finalScore)}`} data-testid="hub-avg-score">Score: {finalScore}%</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default BionicEngineHub;
