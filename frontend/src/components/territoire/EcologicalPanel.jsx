/**
 * EcologicalPanel.jsx — Panneau ecologique BIONIC V8
 * 
 * Affiche:
 * - Corridors actifs avec classification WWF
 * - Legende WWF (macro / biologiques / conservation)
 * - Methode de pathfinding (A* vs Bezier)
 * - Statistiques de connectivite
 * 
 * Props dynamiques (zero donnees mockees):
 * - corridors: Array de corridors issus de bionicZonesData.corridors
 * - species: string (espece selectionnee)
 */

import React, { useMemo } from 'react';
import { TreePine, Route, Compass, Activity } from 'lucide-react';

const WWF_COLORS = {
  macro_corridor: { bg: '#FF5722', label: 'Macro-corridor', desc: '> 2 km' },
  biological_corridor: { bg: '#FF9800', label: 'Corridor biologique', desc: '500m - 2 km' },
  conservation_corridor: { bg: '#FFC107', label: 'Corridor de conservation', desc: '< 500m' },
};

const EcologicalPanel = ({ corridors = [], species = 'tous', className = '' }) => {
  const stats = useMemo(() => {
    if (!corridors.length) return null;
    
    let totalDist = 0;
    let astarCount = 0;
    let bezierCount = 0;
    const byType = { macro_corridor: 0, biological_corridor: 0, conservation_corridor: 0 };
    const connections = new Set();
    let avgScore = 0;

    corridors.forEach(c => {
      totalDist += c.distanceM || 0;
      avgScore += c.score || 0;
      if (c.pathfinding === 'A*') astarCount++;
      else bezierCount++;
      const ctype = c.corridorType || 'conservation_corridor';
      byType[ctype] = (byType[ctype] || 0) + 1;
      connections.add(`${c.fromZoneType}-${c.toZoneType}`);
    });

    return {
      total: corridors.length,
      totalDistKm: (totalDist / 1000).toFixed(1),
      avgScore: corridors.length ? (avgScore / corridors.length).toFixed(0) : 0,
      astarCount,
      bezierCount,
      byType,
      uniqueConnections: connections.size,
    };
  }, [corridors]);

  if (!stats || stats.total === 0) {
    return (
      <div className={`p-3 ${className}`} data-testid="ecological-panel">
        <div className="flex items-center gap-2 text-gray-500 text-xs">
          <TreePine size={14} />
          <span>Aucune donnee ecologique disponible</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-2 ${className}`} data-testid="ecological-panel">
      {/* En-tete */}
      <div className="flex items-center justify-between px-2 py-1.5 bg-emerald-900/20 rounded border border-emerald-800/30">
        <div className="flex items-center gap-1.5">
          <TreePine size={13} className="text-emerald-400" />
          <span className="text-xs font-semibold text-emerald-300 uppercase tracking-wider">Ecologie V8</span>
        </div>
        <span className="text-[10px] text-emerald-400/70 font-mono">
          {stats.total} corridors | {stats.totalDistKm} km
        </span>
      </div>

      {/* Espece active */}
      {species && species !== 'tous' && (
        <div className="px-2">
          <span className="text-[10px] text-amber-400 font-medium capitalize">{species}</span>
        </div>
      )}

      {/* Classification WWF */}
      <div className="px-2 space-y-1">
        <div className="text-[10px] text-gray-500 uppercase tracking-wider font-medium">Classification WWF</div>
        {Object.entries(WWF_COLORS).map(([type, config]) => {
          const count = stats.byType[type] || 0;
          if (count === 0) return null;
          return (
            <div key={type} className="flex items-center gap-2 py-0.5" data-testid={`wwf-${type}`}>
              <div className="w-3 h-3 rounded-sm flex-shrink-0" style={{ backgroundColor: config.bg }} />
              <span className="text-xs text-gray-300 flex-1">{config.label}</span>
              <span className="text-[10px] text-gray-500">{config.desc}</span>
              <span className="text-xs font-bold text-white bg-white/10 px-1.5 rounded">{count}</span>
            </div>
          );
        })}
      </div>

      {/* Pathfinding Stats */}
      <div className="px-2 space-y-1">
        <div className="text-[10px] text-gray-500 uppercase tracking-wider font-medium">Pathfinding</div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1" data-testid="pathfinding-astar">
            <Route size={11} className="text-cyan-400" />
            <span className="text-xs text-gray-300">A*: <span className="text-cyan-300 font-bold">{stats.astarCount}</span></span>
          </div>
          <div className="flex items-center gap-1" data-testid="pathfinding-bezier">
            <Compass size={11} className="text-amber-400" />
            <span className="text-xs text-gray-300">Bezier: <span className="text-amber-300 font-bold">{stats.bezierCount}</span></span>
          </div>
        </div>
        {/* Bar de progression A* */}
        <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-cyan-500 to-emerald-500 rounded-full transition-all"
            style={{ width: `${(stats.astarCount / stats.total) * 100}%` }}
          />
        </div>
        <div className="text-[10px] text-gray-600 text-right">
          {((stats.astarCount / stats.total) * 100).toFixed(0)}% A* optimal
        </div>
      </div>

      {/* Connectivite */}
      <div className="px-2 py-1.5 bg-gray-800/30 rounded">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Activity size={11} className="text-violet-400" />
            <span className="text-xs text-gray-300">Score moyen</span>
          </div>
          <span className="text-xs font-bold text-violet-300" data-testid="ecological-avg-score">{stats.avgScore}/100</span>
        </div>
        <div className="flex items-center justify-between mt-1">
          <span className="text-[10px] text-gray-500">Connexions uniques</span>
          <span className="text-[10px] font-bold text-gray-400" data-testid="ecological-connections">{stats.uniqueConnections}</span>
        </div>
      </div>
    </div>
  );
};

export default EcologicalPanel;
