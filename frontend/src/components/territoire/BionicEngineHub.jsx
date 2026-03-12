/**
 * BionicEngineHub.jsx — Hub des 9 moteurs BIONIC
 * BIONIC V8 — Preparatoire pour Ecological Intelligence Hub (V9-V10)
 *
 * Composant autonome, tracable, testable, remplacable.
 * Chaque moteur: nom, icone, statut (actif/planifie), indicateur de donnees.
 *
 * Les 9 moteurs influencent:
 * - scoring des zones
 * - prediction des deplacements
 * - attractivite par espece
 * - lecture de terrain
 * - priorisation des corridors
 * - recommandations ecologiques
 * - fenetres d'activite
 * - zones critiques
 * - comportements saisonniers
 */

import React, { useState } from 'react';
import {
  Leaf, Clock, CloudSun, AlertTriangle, Route,
  Flower2, Users, Brain, Sprout, ChevronDown, ChevronUp,
} from 'lucide-react';

const BIONIC_ENGINES = [
  {
    id: 'nutrition',
    name: 'Nutrition Engine',
    description: 'Sol, Nutriments, Fourrage, Attractivite par espece',
    icon: Leaf,
    color: '#22c55e',
    status: 'planned',
    influences: ['scoring', 'attractivite', 'zones_critiques'],
  },
  {
    id: 'daily_routine',
    name: 'Daily Routine Engine',
    description: 'Rythmes journaliers: aube, crepuscule, repos, alimentation',
    icon: Clock,
    color: '#f59e0b',
    status: 'planned',
    influences: ['fenetres_activite', 'prediction_deplacements'],
  },
  {
    id: 'weather',
    name: 'Weather Engine',
    description: 'Vent, pression, temperature, precipitations, neige',
    icon: CloudSun,
    color: '#06b6d4',
    status: 'partial',
    influences: ['scoring', 'prediction_deplacements', 'comportements_saisonniers'],
  },
  {
    id: 'disturbance',
    name: 'Disturbance Engine',
    description: 'Routes, chalets, odeurs, pression humaine',
    icon: AlertTriangle,
    color: '#ef4444',
    status: 'planned',
    influences: ['scoring', 'zones_critiques', 'lecture_terrain'],
  },
  {
    id: 'movement',
    name: 'Movement Engine',
    description: 'Corridors A* + DEM + risques + nutrition',
    icon: Route,
    color: '#8b5cf6',
    status: 'active',
    influences: ['prediction_deplacements', 'priorisation_corridors'],
  },
  {
    id: 'phenology',
    name: 'Phenology Engine',
    description: 'Debourrement, floraison, senescence, qualite fourrage',
    icon: Flower2,
    color: '#ec4899',
    status: 'planned',
    influences: ['comportements_saisonniers', 'attractivite', 'recommandations'],
  },
  {
    id: 'typology',
    name: 'Typology Engine',
    description: 'Profils: conservateur, explorateur, nocturne, opportuniste',
    icon: Users,
    color: '#f97316',
    status: 'planned',
    influences: ['prediction_deplacements', 'fenetres_activite'],
  },
  {
    id: 'learning',
    name: 'Learning Engine',
    description: 'Ajustement modeles selon observations reelles',
    icon: Brain,
    color: '#a855f7',
    status: 'planned',
    influences: ['scoring', 'recommandations', 'prediction_deplacements'],
  },
  {
    id: 'habitat_enhancement',
    name: 'Habitat Enhancement',
    description: 'Analyse sol + recommandations: mineraux, chaux, semis',
    icon: Sprout,
    color: '#10b981',
    status: 'planned',
    influences: ['recommandations', 'lecture_terrain'],
  },
];

const STATUS_CONFIG = {
  active: { label: 'Actif', bg: 'bg-emerald-500/15', text: 'text-emerald-400', dot: 'bg-emerald-400' },
  partial: { label: 'Partiel', bg: 'bg-amber-500/15', text: 'text-amber-400', dot: 'bg-amber-400' },
  planned: { label: 'Planifie', bg: 'bg-gray-500/15', text: 'text-gray-500', dot: 'bg-gray-600' },
};

const BionicEngineHub = () => {
  const [expanded, setExpanded] = useState(false);

  const activeCount = BIONIC_ENGINES.filter(e => e.status === 'active').length;
  const partialCount = BIONIC_ENGINES.filter(e => e.status === 'partial').length;

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
