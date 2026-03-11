/**
 * TerritoryAnalysisPanel.jsx — Territory Analysis Results Panel
 * 
 * Shows quality score, indices, success rates, recommendations,
 * warnings and regulatory summary for a selected territory.
 * 
 * Phase 2 extraction from TerritoryMap.jsx
 * @module territory/TerritoryAnalysisPanel
 */

import React from 'react';
import { Target, Car, TreePine, Star, CircleDot, Check, Info, X } from 'lucide-react';
import { BIONIC_COLORS } from '@/config/bionic-colors';

const SPECIES_COLORS = {
  orignal: BIONIC_COLORS.gold.dark,
  chevreuil: BIONIC_COLORS.gold.primary,
  ours: BIONIC_COLORS.gray[600],
  autre: BIONIC_COLORS.gray[500],
};

const TerritoryAnalysisPanel = ({ analysis, onClose, getScoreColor, t = (k) => k }) => {
  if (!analysis) return null;

  return (
    <div
      className="absolute top-4 right-[280px] z-[700] bg-black/95 backdrop-blur-sm rounded-xl shadow-2xl border border-green-500/30 w-[380px] max-h-[80vh] overflow-hidden"
      data-testid="territory-analysis-panel"
    >
      {/* Header */}
      <div className="p-3 border-b border-green-500/30" style={{ backgroundColor: `${analysis.typeColor}20` }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg" style={{ backgroundColor: `${analysis.typeColor}30` }}>
              <Target className="h-5 w-5" style={{ color: analysis.typeColor }} />
            </div>
            <div>
              <h3 className="text-white font-bold text-sm">{analysis.name}</h3>
              <p className="text-xs" style={{ color: analysis.typeColor }}>{analysis.typeName} - {analysis.region}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 text-gray-400 hover:text-white rounded">
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Score Global */}
      <div className="p-3 border-b border-green-500/20">
        <div className="flex items-center justify-between mb-2">
          <span className="text-gray-400 text-xs">{t('global_quality_score')}</span>
          <span className="text-2xl font-bold" style={{ color: getScoreColor(analysis.qualityScore) }}>
            {analysis.qualityScore}/100
          </span>
        </div>
        <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
          <div className="h-full rounded-full transition-all" style={{
            width: `${analysis.qualityScore}%`,
            backgroundColor: getScoreColor(analysis.qualityScore)
          }} />
        </div>
      </div>

      {/* Indices */}
      <div className="p-3 border-b border-green-500/20">
        <div className="text-xs text-gray-500 uppercase mb-2">{t('analysis_indices')}</div>
        <div className="grid grid-cols-2 gap-2">
          {[
            { label: t('hunting_pressure'), value: analysis.indices.pression, Icon: Target },
            { label: t('accessibility'), value: analysis.indices.accessibilite, Icon: Car },
            { label: t('habitat_quality'), value: analysis.indices.habitat, Icon: TreePine },
            { label: t('global_score'), value: analysis.indices.qualite, Icon: Star }
          ].map((indice, idx) => (
            <div key={idx} className="bg-card/50 p-2 rounded-lg">
              <div className="flex items-center gap-1 text-[10px] text-gray-400 mb-1">
                <indice.Icon className="h-3 w-3" />
                <span>{indice.label}</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                  <div className="h-full rounded-full" style={{
                    width: `${indice.value}%`,
                    backgroundColor: getScoreColor(indice.value)
                  }} />
                </div>
                <span className="text-white text-xs font-bold">{indice.value}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Success Rate by species */}
      {analysis.successRate && (
        <div className="p-3 border-b border-green-500/20">
          <div className="text-xs text-gray-500 uppercase mb-2">{t('historical_success_rate')}</div>
          <div className="flex gap-2">
            {Object.entries(analysis.successRate).map(([species, rate]) => (
              <div
                key={species}
                className={`flex-1 text-center p-2 rounded-lg ${rate > 0 ? 'bg-green-500/10 border border-green-500/30' : 'bg-gray-700/30'}`}
              >
                <div className="text-lg mb-0.5 flex justify-center">
                  <CircleDot className="h-5 w-5" style={{ color: SPECIES_COLORS[species] || BIONIC_COLORS.gray[500] }} />
                </div>
                <div className={`text-sm font-bold ${rate > 0 ? 'text-green-400' : 'text-gray-500'}`}>
                  {rate > 0 ? `${rate}%` : 'N/A'}
                </div>
                <div className="text-[9px] text-gray-500 capitalize">{t(`animal_${species}`) || species}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {analysis.recommendations?.length > 0 && (
        <div className="p-3 border-b border-green-500/20">
          <div className="text-xs text-gray-500 uppercase mb-2">Recommandations</div>
          <ul className="space-y-1.5">
            {analysis.recommendations.map((rec, idx) => (
              <li key={idx} className="text-xs text-green-300 flex items-start gap-1.5">
                <Check className="h-3 w-3 mt-0.5 flex-shrink-0" />
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Warnings */}
      {analysis.warnings?.length > 0 && (
        <div className="p-3 border-b border-green-500/20 bg-red-500/5">
          <div className="text-xs text-red-400 uppercase mb-2">Avertissements</div>
          <ul className="space-y-1.5">
            {analysis.warnings.map((warn, idx) => (
              <li key={idx} className="text-xs text-red-300 flex items-start gap-1.5">
                <Info className="h-3 w-3 mt-0.5 flex-shrink-0" />
                <span>{warn}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Regulations */}
      <div className="p-3">
        <div className="text-xs text-gray-500 uppercase mb-2">Synthese reglementaire</div>
        <ul className="space-y-1">
          {analysis.reglements?.map((reg, idx) => (
            <li key={idx} className="text-[10px] text-gray-400 flex items-center gap-1.5">
              <div className="w-1 h-1 rounded-full bg-gray-500" />
              {reg}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default TerritoryAnalysisPanel;
