/**
 * AnalysisSidePanel — Panneau latéral d'analyse du territoire
 * Extrait de MonTerritoireBionicPage.jsx (Phase 3 refactoring)
 */

import React from 'react';
import { BarChart3 } from 'lucide-react';
import { Badge } from '../ui/badge';
import { ZONE_COLORS } from '@/core/bionic/bionicColorsConfig';

const AnalysisSidePanel = ({
  displayScore,
  rating,
  categoryScores,
  visibleZonesCount,
  activeWaypointsCount,
  selectedSpecies,
  activeLayersCount,
  selectedWaypointForZones,
  onGenerateSnapshot,
}) => (
  <div className="p-4 space-y-4" data-testid="panel-analyse">
    <h2 className="text-sm font-semibold text-white flex items-center gap-2">
      <BarChart3 className="h-4 w-4 text-[#9B4DFF]" /> Analyse du territoire
    </h2>
    {/* Score global */}
    <div className="bg-[#111118] rounded-lg p-4 border border-[#1a1a2e]">
      <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Score global</div>
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-bold text-white">{displayScore ?? '—'}</span>
        <span className="text-gray-600">/100</span>
        <Badge className={`${rating.color} text-white text-[9px] px-1.5 py-0`}>{rating.label}</Badge>
      </div>
    </div>
    {/* Scores par categorie */}
    <div className="space-y-2">
      <div className="text-[10px] text-gray-500 uppercase tracking-wider">Scores par categorie</div>
      {Object.entries(categoryScores).map(([key, value]) => {
        const barColor = ZONE_COLORS[key] || (value >= 80 ? '#3CB371' : value >= 60 ? '#f5a623' : '#ef4444');
        return (
        <div key={key} className="bg-[#111118] rounded-lg p-2.5 border border-[#1a1a2e]">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-gray-300 capitalize">{key}</span>
            <span className="text-xs font-bold text-white">{Math.min(100, value)}%</span>
          </div>
          <div className="h-1.5 bg-[#1a1a2e] rounded-full overflow-hidden">
            <div className="h-full rounded-full transition-all" style={{ width: `${Math.min(100, value)}%`, backgroundColor: barColor }} />
          </div>
        </div>
        );
      })}
    </div>
    {/* Stats zones */}
    <div className="bg-[#111118] rounded-lg p-3 border border-[#1a1a2e]">
      <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Statistiques</div>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div><span className="text-gray-500">Zones visibles:</span> <span className="text-white font-medium">{visibleZonesCount}</span></div>
        <div><span className="text-gray-500">Waypoints:</span> <span className="text-white font-medium">{activeWaypointsCount}</span></div>
        <div><span className="text-gray-500">Espece:</span> <span className="text-white font-medium capitalize">{selectedSpecies}</span></div>
        <div><span className="text-gray-500">Couches:</span> <span className="text-white font-medium">{activeLayersCount}/15</span></div>
      </div>
    </div>
    {/* Snapshot export */}
    {selectedWaypointForZones && (
      <div className="space-y-2">
        <div className="text-[10px] text-gray-500 uppercase tracking-wider">Export snapshot</div>
        <div className="flex gap-2">
          <button onClick={() => onGenerateSnapshot('json')} className="flex-1 text-xs px-3 py-2 rounded-lg bg-[#111118] border border-[#1a1a2e] text-gray-400 hover:text-white hover:border-gray-600 transition-colors" data-testid="export-json-btn">JSON</button>
          <button onClick={() => onGenerateSnapshot('pdf')} className="flex-1 text-xs px-3 py-2 rounded-lg bg-[#111118] border border-[#1a1a2e] text-gray-400 hover:text-white hover:border-gray-600 transition-colors" data-testid="export-pdf-btn">PDF</button>
        </div>
      </div>
    )}
  </div>
);

export default AnalysisSidePanel;
