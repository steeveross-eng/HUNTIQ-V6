/**
 * BionicLegend.jsx — Charte visuelle BIONIC™ 1000%
 * C14: Légende dynamique — positionnée au-dessus de la barre GPS.
 */

import React, { useState } from 'react';
import { ChevronRight, ChevronLeft, MapPin, Wind, Route } from 'lucide-react';

const ZONE_STYLES = [
  { label: 'Habitat', color: 'hsl(130, 70%, 45%)' },
  { label: 'Rut', color: 'hsl(30, 85%, 50%)' },
  { label: 'Repos', color: 'hsl(215, 70%, 50%)' },
  { label: 'Alim.', color: 'hsl(50, 80%, 45%)' },
];

const CORRIDOR_STYLES = [
  { label: 'Réel M', color: '#1565C0', dash: false },
  { label: 'Réel F', color: '#F472B6', dash: false },
  { label: 'IA M', color: '#38BDF8', dash: true },
  { label: 'IA F', color: '#C084FC', dash: true },
  { label: 'Accès WP', color: '#10B981', dash: false, width: 3 },
];

const STATE_MAP = {
  idle: { text: 'Attente', dot: 'bg-gray-500' },
  loading: { text: 'Analyse...', dot: 'bg-amber-400 animate-pulse' },
  success: { text: 'OK', dot: 'bg-emerald-400' },
  empty: { text: '0 zone', dot: 'bg-orange-400' },
  error: { text: 'Erreur', dot: 'bg-red-400' },
  timeout: { text: 'Timeout', dot: 'bg-red-400' },
};

export default function BionicLegend({ pipelineState, zoneCount = 0, corridorCount = 0, windDeg = 225 }) {
  const [isOpen, setIsOpen] = useState(false);

  const windLabel = windDeg >= 200 && windDeg <= 250 ? 'SO→NE' : `${Math.round(windDeg)}°`;
  const state = STATE_MAP[pipelineState] || STATE_MAP.idle;

  return (
    <div
      data-testid="bionic-legend"
      className="absolute bottom-14 left-2 z-[1000] select-none"
      style={{ pointerEvents: 'auto' }}
      onMouseDown={(e) => e.stopPropagation()}
      onClick={(e) => e.stopPropagation()}
      onDoubleClick={(e) => e.stopPropagation()}
    >
      {/* Collapsed: Compact pill */}
      {!isOpen && (
        <button
          data-testid="bionic-legend-toggle"
          onClick={() => setIsOpen(true)}
          className="flex items-center gap-1.5 px-2.5 py-1.5 bg-gray-950 border border-gray-600/60 rounded-lg shadow-lg hover:bg-gray-900 transition-colors"
        >
          <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${state.dot}`} />
          <span className="text-[9px] font-bold text-gray-300 tracking-wide">BIONIC™</span>
          <span className="text-[9px] text-gray-500">{zoneCount}z {corridorCount}c</span>
          <ChevronRight className="w-3 h-3 text-gray-500" />
        </button>
      )}

      {/* Expanded: Full legend */}
      {isOpen && (
        <div className="bg-gray-950 border border-gray-600/60 rounded-lg shadow-2xl text-white w-[220px]">
          {/* Header */}
          <button
            data-testid="bionic-legend-toggle"
            onClick={() => setIsOpen(false)}
            className="w-full flex items-center justify-between px-3 py-2 hover:bg-gray-800/40 transition-colors rounded-t-lg border-b border-gray-800/60"
          >
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full flex-shrink-0 ${state.dot}`} />
              <span className="text-[10px] font-bold tracking-wider text-gray-200">CHARTE BIONIC™</span>
            </div>
            <ChevronLeft className="w-3.5 h-3.5 text-gray-500" />
          </button>

          {/* Stats bar */}
          <div data-testid="bionic-pipeline-state" className="px-3 py-1.5 flex items-center gap-3 text-[10px] text-gray-400">
            <span className="flex items-center gap-0.5"><MapPin className="w-3 h-3" />{zoneCount}</span>
            <span className="flex items-center gap-0.5"><Route className="w-3 h-3" />{corridorCount}</span>
            <span className="flex items-center gap-0.5"><Wind className="w-3 h-3" />{windLabel}</span>
            <span className="ml-auto text-gray-500 text-[9px]">{state.text}</span>
          </div>

          {/* Zones + Corridors side by side */}
          <div className="px-3 pb-2.5 pt-1 grid grid-cols-2 gap-x-3 gap-y-0">
            <div>
              <div className="text-[8px] font-bold text-gray-500 mb-1 uppercase tracking-widest">Zones</div>
              {ZONE_STYLES.map((s) => (
                <div key={s.label} className="flex items-center gap-1.5 h-[16px]">
                  <div className="w-3.5 h-2.5 rounded-[2px] border-[1.5px] flex-shrink-0" style={{ borderColor: s.color }} />
                  <span className="text-[10px] text-gray-300 leading-none">{s.label}</span>
                </div>
              ))}
            </div>
            <div>
              <div className="text-[8px] font-bold text-gray-500 mb-1 uppercase tracking-widest">Corridors</div>
              {CORRIDOR_STYLES.map((s) => (
                <div key={s.label} className="flex items-center gap-1.5 h-[16px]">
                  <svg width="16" height="4" className="flex-shrink-0">
                    <line x1="0" y1="2" x2="16" y2="2"
                      stroke={s.color} strokeWidth={s.width || 1.5}
                      strokeDasharray={s.dash ? '3,1.5' : 'none'} />
                  </svg>
                  <span className="text-[10px] text-gray-300 leading-none">{s.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
