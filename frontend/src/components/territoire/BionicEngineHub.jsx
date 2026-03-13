/**
 * BionicEngineHub.jsx — Hub des 12 moteurs BIONIC V2
 * STEVE-MAX: Tous les moteurs actifs et integres.
 */

import React, { useState } from 'react';
import {
  Leaf, Clock, CloudSun, AlertTriangle, Route,
  Flower2, Users, Brain, Sprout, ChevronDown, ChevronUp,
  Wind, Mountain, Target, Gauge, ShieldCheck, Layers,
} from 'lucide-react';

const BIONIC_ENGINES_V2 = [
  { id: 'behavior', name: 'Behavior Engine', description: 'Patterns comportementaux: aube, crepuscule, repos, alimentation', icon: Clock, color: '#f59e0b', status: 'active', num: 1 },
  { id: 'keyzone_v2', name: 'KeyZone Engine V2', description: 'Detection zones cles amelioree (densite, score qualite)', icon: Target, color: '#ef4444', status: 'active', num: 2 },
  { id: 'food_deficit', name: 'Food Deficit Engine', description: 'Analyse deficit alimentaire (NDVI, saisons, pression)', icon: Leaf, color: '#22c55e', status: 'active', num: 3 },
  { id: 'wind_intelligence', name: 'Wind Intelligence Engine', description: 'Analyse vent strategique (direction optimale approche)', icon: Wind, color: '#06b6d4', status: 'active', num: 4 },
  { id: 'terrain', name: 'Terrain Engine', description: 'Pentes, orientation, couvert forestier, marchabilite', icon: Mountain, color: '#78909C', status: 'active', num: 5 },
  { id: 'human_pressure', name: 'Human Pressure Engine', description: 'Pression anthropique (routes, batiments, activites)', icon: AlertTriangle, color: '#FF5722', status: 'active', num: 6 },
  { id: 'corridor_continuity', name: 'Corridor Continuity Engine', description: 'Fusion/reparation automatique corridors', icon: Route, color: '#8b5cf6', status: 'active', num: 7 },
  { id: 'global_attractiveness', name: 'Global Attractiveness Engine', description: 'Score attractivite global du carre 2km', icon: Gauge, color: '#FF9800', status: 'active', num: 8 },
  { id: 'action_plan', name: 'Action Plan Engine', description: 'Generation plan d\'action chasse', icon: Flower2, color: '#ec4899', status: 'active', num: 9 },
  { id: 'predictive_ai', name: 'Predictive AI Engine', description: 'Predictions probabilistes de presence', icon: Brain, color: '#a855f7', status: 'active', num: 10 },
  { id: 'bce_compliance', name: 'BCE-4X Compliance Engine', description: 'Validation automatique conformite', icon: ShieldCheck, color: '#4CAF50', status: 'active', num: 11 },
  { id: 'rendering', name: 'Rendering Engine', description: 'Optimisation rendu carte', icon: Layers, color: '#2196F3', status: 'active', num: 12 },
];

const BionicEngineHub = () => {
  const [expanded, setExpanded] = useState(false);

  const activeCount = BIONIC_ENGINES_V2.filter(e => e.status === 'active').length;

  return (
    <div className="bg-[#111118] rounded-lg border border-[#1a1a2e] overflow-hidden" data-testid="bionic-engine-hub">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-3 py-2 hover:bg-white/5 transition-colors"
        data-testid="hub-toggle"
      >
        <div className="flex items-center gap-1.5">
          <Brain className="h-3.5 w-3.5 text-violet-400" />
          <span className="text-[10px] font-semibold text-violet-300 uppercase tracking-wider">Ecological Intelligence Hub</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            <span className="text-[9px] text-gray-500">{activeCount}</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-1.5 h-1.5 rounded-full bg-amber-400" />
            <span className="text-[9px] text-gray-500">{partialCount}</span>
          </div>
          <span className="text-[9px] text-gray-600">{BIONIC_ENGINES.length} moteurs</span>
          {expanded ? <ChevronUp className="h-3 w-3 text-gray-500" /> : <ChevronDown className="h-3 w-3 text-gray-500" />}
        </div>
      </button>

      {expanded && (
        <div className="px-3 pb-3 space-y-1.5" data-testid="hub-engines-list">
          {BIONIC_ENGINES.map((engine) => {
            const Icon = engine.icon;
            const status = STATUS_CONFIG[engine.status];
            return (
              <div
                key={engine.id}
                className="flex items-start gap-2 py-1.5 px-2 rounded bg-gray-900/30 hover:bg-gray-900/50 transition-colors"
                data-testid={`engine-${engine.id}`}
              >
                <Icon className="h-3.5 w-3.5 flex-shrink-0 mt-0.5" style={{ color: engine.color }} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span className="text-[10px] font-medium text-gray-200 truncate">{engine.name}</span>
                    <span className={`text-[8px] px-1 py-0 rounded ${status.bg} ${status.text}`}>
                      {status.label}
                    </span>
                  </div>
                  <p className="text-[8px] text-gray-600 leading-relaxed mt-0.5">{engine.description}</p>
                </div>
                <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 mt-1.5 ${status.dot}`} />
              </div>
            );
          })}

          {/* Hub roadmap summary */}
          <div className="pt-2 border-t border-gray-800/50">
            <div className="text-[8px] text-gray-600 leading-relaxed">
              Les 9 moteurs BIONIC formeront le coeur du Hub d'Intelligence Ecologique.
              Chaque moteur influencera le scoring, les predictions et les recommandations.
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BionicEngineHub;
