/**
 * CorridorStatsPanel — Panneau de statistiques des corridors V7
 * BIONIC V7.1 — corridor_stats_v1
 *
 * Affiche les statistiques des corridors fauniques :
 *  - Nombre total
 *  - Distance cumulee
 *  - Repartition male/femelle
 *  - Repartition reel/IA
 *  - Mini-graphe barres
 */

import React, { useMemo } from 'react';
import { Footprints, ArrowRight } from 'lucide-react';

const BAR_COLORS = {
  male_real: '#1565C0',
  male_ai: '#42A5F5',
  female_real: '#C62828',
  female_ai: '#EF5350',
};

const CorridorStatsPanel = ({ corridors = [] }) => {
  const stats = useMemo(() => {
    if (!corridors.length) return null;

    let totalDist = 0;
    let maleCount = 0;
    let femaleCount = 0;
    let realCount = 0;
    let aiCount = 0;
    let maleRealCount = 0;
    let maleAiCount = 0;
    let femaleRealCount = 0;
    let femaleAiCount = 0;

    for (const c of corridors) {
      totalDist += c.distanceM || 0;
      if (c.sex === 'male') {
        maleCount++;
        if (c.source === 'real') maleRealCount++;
        else maleAiCount++;
      } else {
        femaleCount++;
        if (c.source === 'real') femaleRealCount++;
        else femaleAiCount++;
      }
      if (c.source === 'real') realCount++;
      else aiCount++;
    }

    const maxBar = Math.max(maleRealCount, maleAiCount, femaleRealCount, femaleAiCount, 1);

    return {
      total: corridors.length,
      totalDistKm: (totalDist / 1000).toFixed(1),
      maleCount,
      femaleCount,
      realCount,
      aiCount,
      bars: [
        { label: 'M/Reel', count: maleRealCount, color: BAR_COLORS.male_real, pct: (maleRealCount / maxBar) * 100 },
        { label: 'M/IA', count: maleAiCount, color: BAR_COLORS.male_ai, pct: (maleAiCount / maxBar) * 100 },
        { label: 'F/Reel', count: femaleRealCount, color: BAR_COLORS.female_real, pct: (femaleRealCount / maxBar) * 100 },
        { label: 'F/IA', count: femaleAiCount, color: BAR_COLORS.female_ai, pct: (femaleAiCount / maxBar) * 100 },
      ],
    };
  }, [corridors]);

  if (!stats) {
    return (
      <div className="bg-gray-800/40 rounded-lg p-3 border border-gray-700/50" data-testid="corridor-stats-empty">
        <div className="flex items-center gap-2">
          <Footprints className="h-4 w-4 text-gray-500" />
          <span className="text-xs font-medium text-gray-500">Aucun corridor</span>
        </div>
        <p className="text-[10px] text-gray-600 mt-1 leading-relaxed">
          Les corridors fauniques V7 apparaitront ici lors de l'analyse.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800/60 rounded-lg p-3 border border-gray-700/50" data-testid="corridor-stats-panel">
      {/* Header */}
      <div className="flex items-center justify-between mb-2.5">
        <div className="flex items-center gap-2">
          <Footprints className="h-4 w-4 text-cyan-400" />
          <span className="text-xs font-semibold text-gray-200">Corridors V7</span>
        </div>
        <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-500/15 text-cyan-400 border border-cyan-500/20">
          {stats.total}
        </span>
      </div>

      {/* Metriques */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        <div className="bg-gray-900/50 rounded px-2 py-1.5" data-testid="corridor-stat-distance">
          <div className="text-[9px] text-gray-500 uppercase tracking-wider">Distance</div>
          <div className="text-sm font-bold text-gray-200">{stats.totalDistKm} km</div>
        </div>
        <div className="bg-gray-900/50 rounded px-2 py-1.5" data-testid="corridor-stat-total">
          <div className="text-[9px] text-gray-500 uppercase tracking-wider">Corridors</div>
          <div className="text-sm font-bold text-gray-200">{stats.total}</div>
        </div>
      </div>

      {/* Repartition Male/Femelle */}
      <div className="flex items-center gap-2 mb-2" data-testid="corridor-stat-sex">
        <div className="flex-1 flex items-center gap-1">
          <div className="w-2 h-2 rounded-full" style={{ backgroundColor: '#1565C0' }} />
          <span className="text-[10px] text-gray-400">Male</span>
          <span className="text-[10px] font-bold text-gray-300 ml-auto">{stats.maleCount}</span>
        </div>
        <ArrowRight className="h-3 w-3 text-gray-600" />
        <div className="flex-1 flex items-center gap-1">
          <div className="w-2 h-2 rounded-full" style={{ backgroundColor: '#C62828' }} />
          <span className="text-[10px] text-gray-400">Femelle</span>
          <span className="text-[10px] font-bold text-gray-300 ml-auto">{stats.femaleCount}</span>
        </div>
      </div>

      {/* Repartition Reel/IA */}
      <div className="flex items-center gap-2 mb-3" data-testid="corridor-stat-source">
        <div className="flex-1 flex items-center gap-1">
          <div className="w-2 h-2 rounded-sm bg-gray-300" />
          <span className="text-[10px] text-gray-400">Reel</span>
          <span className="text-[10px] font-bold text-emerald-400 ml-auto">{stats.realCount}</span>
        </div>
        <ArrowRight className="h-3 w-3 text-gray-600" />
        <div className="flex-1 flex items-center gap-1">
          <div className="w-2 h-2 rounded-sm border border-dashed border-gray-400" />
          <span className="text-[10px] text-gray-400">IA</span>
          <span className="text-[10px] font-bold text-amber-400 ml-auto">{stats.aiCount}</span>
        </div>
      </div>

      {/* Mini-graphe barres */}
      <div className="space-y-1" data-testid="corridor-stat-bars">
        {stats.bars.map((bar) => (
          <div key={bar.label} className="flex items-center gap-2">
            <span className="text-[9px] text-gray-500 w-10 text-right">{bar.label}</span>
            <div className="flex-1 h-2.5 bg-gray-900/60 rounded-sm overflow-hidden">
              <div
                className="h-full rounded-sm transition-all duration-500"
                style={{
                  width: `${Math.max(bar.count > 0 ? 8 : 0, bar.pct)}%`,
                  backgroundColor: bar.color,
                  opacity: 0.85,
                }}
              />
            </div>
            <span className="text-[9px] font-mono text-gray-400 w-4 text-right">{bar.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CorridorStatsPanel;
