/**
 * ZoneInfoPanel — Panneau d'information persistant des zones BIONIC
 * BIONIC V5 ULTIME 300% — zone_info_panel_v1
 *
 * Affiche en permanence les détails d'une zone ciblée :
 *  - Type de zone, score, interprétation
 *  - Superficie, coordonnées
 *  - Code couleur BIONIC
 *
 * Norme UI/UX BIONIC V5 300% :
 *  - Ancré, z-index élevé, jamais masqué
 *  - Scroll interne si nécessaire
 *  - Responsive desktop/mobile
 */

import React from 'react';
import { Target, MapPin, Ruler, Activity, ChevronRight } from 'lucide-react';
import { BIONIC_MODULES } from '@/core/bionic';

const getInterpretation = (moduleId, score) => {
  const mod = BIONIC_MODULES[moduleId];
  if (!mod) return 'Zone analysée';
  if (score >= 80) return mod.interpretation.high;
  if (score >= 60) return mod.interpretation.medium;
  return mod.interpretation.low;
};

const getScoreLabel = (score) => {
  if (score >= 85) return 'Excellent';
  if (score >= 70) return 'Bon';
  if (score >= 55) return 'Modéré';
  if (score >= 40) return 'Faible';
  return 'Très faible';
};

const ZoneInfoPanel = ({ zone, onClear }) => {
  if (!zone) {
    return (
      <div className="bg-gray-800/40 rounded-lg p-3 border border-gray-700/50" data-testid="zone-info-panel-empty">
        <div className="flex items-center gap-2 mb-1">
          <Target className="h-4 w-4 text-gray-500" />
          <span className="text-xs font-medium text-gray-500">Aucune zone ciblée</span>
        </div>
        <p className="text-[10px] text-gray-600 leading-relaxed">
          Survolez une zone organique sur la carte pour afficher ses détails ici.
        </p>
      </div>
    );
  }

  const mod = BIONIC_MODULES[zone.layerId] || BIONIC_MODULES.habitats;
  const zoneColor = zone.color || mod?.color || '#f5a623';
  const interpretation = getInterpretation(zone.layerId, zone.score);
  const scoreLabel = getScoreLabel(zone.score);

  return (
    <div
      className="bg-gray-800/60 rounded-lg border overflow-hidden"
      style={{ borderColor: `${zoneColor}40` }}
      data-testid="zone-info-panel"
    >
      {/* Header avec type de zone */}
      <div
        className="px-3 py-2 flex items-center justify-between"
        style={{ backgroundColor: `${zoneColor}15` }}
      >
        <div className="flex items-center gap-2">
          <div
            className="w-3 h-3 rounded-full border-2 flex-shrink-0"
            style={{ borderColor: zoneColor, backgroundColor: 'transparent' }}
          />
          <span className="text-xs font-bold text-white truncate">{mod?.label || 'Zone'}</span>
        </div>
        {onClear && (
          <button
            onClick={onClear}
            className="text-gray-500 hover:text-gray-300 text-[10px]"
            data-testid="zone-info-clear"
          >
            Effacer
          </button>
        )}
      </div>

      {/* Contenu — scroll interne */}
      <div className="p-3 space-y-2 max-h-[200px] overflow-y-auto">
        {/* Score principal */}
        <div className="flex items-center justify-between">
          <span className="text-[10px] text-gray-400 uppercase tracking-wider">Score</span>
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold" style={{ color: zoneColor }}>
              {zone.score}%
            </span>
            <span
              className="text-[9px] px-1.5 py-0.5 rounded"
              style={{
                backgroundColor: `${zoneColor}20`,
                color: zoneColor,
                border: `1px solid ${zoneColor}30`,
              }}
            >
              {scoreLabel}
            </span>
          </div>
        </div>

        {/* Barre de score */}
        <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-300"
            style={{ width: `${zone.score}%`, backgroundColor: zoneColor }}
          />
        </div>

        {/* Interprétation */}
        <div
          className="text-[10px] py-1.5 px-2 rounded text-center leading-relaxed"
          style={{
            backgroundColor: `${zoneColor}10`,
            color: zoneColor,
            border: `1px solid ${zoneColor}20`,
          }}
        >
          {interpretation}
        </div>

        {/* Détails */}
        <div className="space-y-1.5 pt-1">
          {zone.areaM2 && (
            <div className="flex items-center justify-between text-[10px]">
              <span className="text-gray-500 flex items-center gap-1">
                <Ruler className="h-3 w-3" /> Superficie
              </span>
              <span className="text-gray-300">~{zone.areaM2.toLocaleString('fr-FR')} m²</span>
            </div>
          )}

          {zone.center && (
            <div className="flex items-center justify-between text-[10px]">
              <span className="text-gray-500 flex items-center gap-1">
                <MapPin className="h-3 w-3" /> Position
              </span>
              <span className="text-gray-300">
                {zone.center[0]?.toFixed(4)}, {zone.center[1]?.toFixed(4)}
              </span>
            </div>
          )}

          <div className="flex items-center justify-between text-[10px]">
            <span className="text-gray-500 flex items-center gap-1">
              <Activity className="h-3 w-3" /> Module
            </span>
            <span className="text-gray-300">{mod?.category || 'behavioral'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ZoneInfoPanel;
