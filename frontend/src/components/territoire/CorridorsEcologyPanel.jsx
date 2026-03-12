/**
 * CorridorsEcologyPanel.jsx — Panneau unifie Corridors & Ecologie V8
 * BIONIC V8 — Fusion de CorridorStatsPanel + EcologicalPanel
 *
 * Composant autonome, tracable, testable, remplacable.
 * Zero donnees mockees. Zero duplication.
 *
 * Props:
 * - corridors: Array flat corridor objects from bionicZonesData.corridors
 * - species: string (espece selectionnee)
 */

import React, { useMemo, useState } from 'react';
import { Route, Compass, Activity, ArrowRight, ChevronDown, ChevronUp } from 'lucide-react';

const WWF_COLORS = {
  macro_corridor: { bg: '#FF5722', label: 'Macro-corridor', desc: '> 2 km' },
  biological_corridor: { bg: '#FF9800', label: 'Biologique', desc: '500m - 2 km' },
  conservation_corridor: { bg: '#FFC107', label: 'Conservation', desc: '< 500m' },
};

const BAR_COLORS = {
  male_real: '#1565C0',
  male_ai: '#42A5F5',
  female_real: '#C62828',
  female_ai: '#EF5350',
};

const CorridorsEcologyPanel = ({ corridors = [], species = 'tous' }) => {
  const [detailsExpanded, setDetailsExpanded] = useState(false);

  const stats = useMemo(() => {
    if (!corridors.length) return null;

    let totalDist = 0;
    let astarCount = 0;
    let bezierCount = 0;
    let maleCount = 0;
    let femaleCount = 0;
    let realCount = 0;
    let aiCount = 0;
    let avgScore = 0;
    const byType = { macro_corridor: 0, biological_corridor: 0, conservation_corridor: 0 };
    const connections = new Set();

    for (const c of corridors) {
      totalDist += c.distanceM || 0;
      avgScore += c.score || 0;
      if (c.pathfinding === 'A*') astarCount++;
      else bezierCount++;
      const ctype = c.corridorType || 'conservation_corridor';
      byType[ctype] = (byType[ctype] || 0) + 1;
      connections.add(`${c.fromZoneType}-${c.toZoneType}`);
      if (c.sex === 'male') maleCount++;
      else femaleCount++;
      if (c.source === 'real') realCount++;
      else aiCount++;
    }

    const maxBar = Math.max(1, maleCount, femaleCount);

    return {
      total: corridors.length,
      totalDistKm: (totalDist / 1000).toFixed(1),
      avgScore: corridors.length ? Math.round(avgScore / corridors.length) : 0,
      astarCount,
      bezierCount,
      astarPct: Math.round((astarCount / corridors.length) * 100),
      byType,
      uniqueConnections: connections.size,
      maleCount,
      femaleCount,
      realCount,
      aiCount,
      bars: [
        { label: 'Male', count: maleCount, color: BAR_COLORS.male_real, pct: (maleCount / maxBar) * 100 },
        { label: 'Femelle', count: femaleCount, color: BAR_COLORS.female_real, pct: (femaleCount / maxBar) * 100 },
      ],
    };
  }, [corridors]);

  if (!stats) {
    return (
      <div className="bg-[#111118] rounded-lg p-3 border border-[#1a1a2e]" data-testid="corridors-ecology-panel">
        <div className="flex items-center gap-2">
          <Route className="h-3.5 w-3.5 text-gray-500" />
          <span className="text-xs text-gray-500">Corridors & Ecologie</span>
        </div>
        <p className="text-[10px] text-gray-600 mt-1">En attente d'analyse...</p>
      </div>
    );
  }

  return (
    <div className="bg-[#111118] rounded-lg border border-cyan-900/30 overflow-hidden" data-testid="corridors-ecology-panel">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 bg-cyan-900/15 border-b border-cyan-900/20">
        <div className="flex items-center gap-1.5">
          <Route className="h-3.5 w-3.5 text-cyan-400" />
          <span className="text-xs font-semibold text-cyan-300 uppercase tracking-wider">Corridors & Ecologie V8</span>
        </div>
        <span className="text-[10px] font-mono text-cyan-400/70">
          {stats.total} | {stats.totalDistKm} km
        </span>
      </div>

      <div className="p-3 space-y-2.5">
        {/* Espece */}
        {species && species !== 'tous' && (
          <div className="text-[10px] text-amber-400 font-medium capitalize">{species}</div>
        )}

        {/* Metriques principales */}
        <div className="grid grid-cols-3 gap-1.5">
          <div className="bg-gray-900/50 rounded px-2 py-1.5 text-center" data-testid="ce-stat-total">
            <div className="text-[8px] text-gray-500 uppercase">Corridors</div>
            <div className="text-sm font-bold text-white">{stats.total}</div>
          </div>
          <div className="bg-gray-900/50 rounded px-2 py-1.5 text-center" data-testid="ce-stat-distance">
            <div className="text-[8px] text-gray-500 uppercase">Distance</div>
            <div className="text-sm font-bold text-white">{stats.totalDistKm} km</div>
          </div>
          <div className="bg-gray-900/50 rounded px-2 py-1.5 text-center" data-testid="ce-stat-score">
            <div className="text-[8px] text-gray-500 uppercase">Score</div>
            <div className="text-sm font-bold text-violet-300">{stats.avgScore}</div>
          </div>
        </div>

        {/* Classification WWF */}
        <div className="space-y-1">
          <div className="text-[9px] text-gray-500 uppercase tracking-wider font-medium">Classification WWF</div>
          {Object.entries(WWF_COLORS).map(([type, config]) => {
            const count = stats.byType[type] || 0;
            if (count === 0) return null;
            return (
              <div key={type} className="flex items-center gap-2" data-testid={`wwf-${type}`}>
                <div className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ backgroundColor: config.bg }} />
                <span className="text-[10px] text-gray-300 flex-1">{config.label}</span>
                <span className="text-[9px] text-gray-600">{config.desc}</span>
                <span className="text-[10px] font-bold text-white bg-white/10 px-1.5 rounded">{count}</span>
              </div>
            );
          })}
        </div>

        {/* Pathfinding A* */}
        <div className="space-y-1">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1" data-testid="pathfinding-astar">
                <Route size={10} className="text-cyan-400" />
                <span className="text-[10px] text-gray-300">A*: <span className="text-cyan-300 font-bold">{stats.astarCount}</span></span>
              </div>
              <div className="flex items-center gap-1" data-testid="pathfinding-bezier">
                <Compass size={10} className="text-amber-400" />
                <span className="text-[10px] text-gray-300">Bezier: <span className="text-amber-300 font-bold">{stats.bezierCount}</span></span>
              </div>
            </div>
            <span className="text-[9px] text-cyan-400/60 font-mono">{stats.astarPct}%</span>
          </div>
          <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-cyan-500 to-emerald-500 rounded-full transition-all"
              style={{ width: `${stats.astarPct}%` }}
            />
          </div>
        </div>

        {/* Connectivite */}
        <div className="flex items-center justify-between py-1 border-t border-gray-800/50">
          <div className="flex items-center gap-1.5">
            <Activity size={10} className="text-violet-400" />
            <span className="text-[10px] text-gray-400">Connexions uniques</span>
          </div>
          <span className="text-[10px] font-bold text-violet-300" data-testid="ce-connections">{stats.uniqueConnections}</span>
        </div>

        {/* Details expandable: male/femelle, reel/IA */}
        <button
          onClick={() => setDetailsExpanded(!detailsExpanded)}
          className="w-full flex items-center justify-between py-1 text-[9px] text-gray-500 hover:text-gray-300 transition-colors"
          data-testid="ce-details-toggle"
        >
          <span className="uppercase tracking-wider">Details corridors</span>
          {detailsExpanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
        </button>

        {detailsExpanded && (
          <div className="space-y-2 pt-1" data-testid="ce-details-content">
            {/* Repartition Male/Femelle */}
            <div className="flex items-center gap-2" data-testid="ce-stat-sex">
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
            <div className="flex items-center gap-2" data-testid="ce-stat-source">
              <div className="flex-1 flex items-center gap-1">
                <div className="w-2 h-2 rounded-sm bg-emerald-400" />
                <span className="text-[10px] text-gray-400">Reel</span>
                <span className="text-[10px] font-bold text-emerald-400 ml-auto">{stats.realCount}</span>
              </div>
              <ArrowRight className="h-3 w-3 text-gray-600" />
              <div className="flex-1 flex items-center gap-1">
                <div className="w-2 h-2 rounded-sm border border-dashed border-amber-400" />
                <span className="text-[10px] text-gray-400">IA</span>
                <span className="text-[10px] font-bold text-amber-400 ml-auto">{stats.aiCount}</span>
              </div>
            </div>
            {/* Mini barres */}
            <div className="space-y-1">
              {stats.bars.map((bar) => (
                <div key={bar.label} className="flex items-center gap-2">
                  <span className="text-[8px] text-gray-500 w-12 text-right">{bar.label}</span>
                  <div className="flex-1 h-2 bg-gray-900/60 rounded-sm overflow-hidden">
                    <div
                      className="h-full rounded-sm transition-all duration-500"
                      style={{ width: `${Math.max(bar.count > 0 ? 8 : 0, bar.pct)}%`, backgroundColor: bar.color, opacity: 0.85 }}
                    />
                  </div>
                  <span className="text-[8px] font-mono text-gray-400 w-4 text-right">{bar.count}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CorridorsEcologyPanel;
