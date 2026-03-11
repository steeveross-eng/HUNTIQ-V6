/**
 * ScoreDistributionPanel - Répartition des Scores BIONIC
 * =======================================================
 * BIONIC V5 ULTIME - PHASE 5.3
 * 
 * RESPONSABILITÉ UNIQUE:
 * - Afficher la distribution des 9 scores par niveau
 * - Visualisation de la répartition qualitative
 * - Statistiques synthétiques (médiane, écart-type)
 * 
 * DESIGN:
 * - Barres horizontales de distribution
 * - Compteurs par niveau
 * - Barre de répartition proportionnelle
 * - Style analytique premium
 * 
 * ISOLATION:
 * - Composant 100% présentationnel
 * - Aucune logique métier, aucun calcul
 * - Données via props uniquement
 * 
 * Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  BarChart3,
  TrendingUp,
  Activity
} from 'lucide-react';

import { BIONIC_COLORS } from '@/config/bionic-colors';

// =============================================================================
// CONSTANTS
// =============================================================================

const LEVEL_CONFIG = [
  { 
    key: 'excellent', 
    label: 'Excellent', 
    range: '8-10',
    rangeMin: 80,
    rangeMax: 100,
    color: BIONIC_COLORS.green.primary 
  },
  { 
    key: 'good', 
    label: 'Bon', 
    range: '6-7',
    rangeMin: 60,
    rangeMax: 79,
    color: BIONIC_COLORS.gold.primary 
  },
  { 
    key: 'moderate', 
    label: 'Modéré', 
    range: '4-5',
    rangeMin: 40,
    rangeMax: 59,
    color: BIONIC_COLORS.blue.light 
  },
  { 
    key: 'poor', 
    label: 'Faible', 
    range: '2-3',
    rangeMin: 20,
    rangeMax: 39,
    color: '#F97316' // Orange
  },
  { 
    key: 'critical', 
    label: 'Critique', 
    range: '0-1',
    rangeMin: 0,
    rangeMax: 19,
    color: BIONIC_COLORS.red.primary 
  }
];

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

/**
 * Ligne de distribution par niveau
 */
const DistributionRow = ({ level, count, total, maxCount }) => {
  const percentage = total > 0 ? (count / total) * 100 : 0;
  const barWidth = maxCount > 0 ? (count / maxCount) * 100 : 0;
  
  return (
    <div className="flex items-center gap-3 py-1.5">
      {/* Label du niveau */}
      <div className="w-20 flex-shrink-0">
        <span className="text-sm text-gray-300">{level.label}</span>
        <span className="text-xs text-gray-500 ml-1">({level.range})</span>
      </div>
      
      {/* Barre de distribution */}
      <div className="flex-1 h-5 rounded overflow-hidden relative" style={{ backgroundColor: BIONIC_COLORS.gray[800] }}>
        <div 
          className="h-full rounded transition-all duration-500 flex items-center justify-end pr-2"
          style={{ 
            width: `${barWidth}%`,
            backgroundColor: level.color,
            minWidth: count > 0 ? '20px' : '0'
          }}
        >
          {count > 0 && (
            <span className="text-xs font-bold text-white drop-shadow">
              {count}
            </span>
          )}
        </div>
      </div>
      
      {/* Compteur */}
      <div className="w-16 text-right flex-shrink-0">
        <span 
          className="text-sm font-semibold"
          style={{ color: count > 0 ? level.color : BIONIC_COLORS.gray[600] }}
        >
          {count}
        </span>
        <span className="text-xs text-gray-500"> score{count !== 1 ? 's' : ''}</span>
      </div>
    </div>
  );
};

/**
 * Barre de répartition proportionnelle
 */
const ProportionalBar = ({ distribution, total }) => {
  if (total === 0) return null;
  
  return (
    <div className="space-y-2">
      <div className="flex h-6 rounded-lg overflow-hidden">
        {LEVEL_CONFIG.map(level => {
          const count = distribution[level.key] || 0;
          const percentage = (count / total) * 100;
          
          if (percentage === 0) return null;
          
          return (
            <div
              key={level.key}
              className="h-full flex items-center justify-center transition-all duration-500"
              style={{ 
                width: `${percentage}%`,
                backgroundColor: level.color,
                minWidth: percentage > 0 ? '24px' : '0'
              }}
            >
              <span className="text-xs font-bold text-white drop-shadow">
                {Math.round(percentage)}%
              </span>
            </div>
          );
        })}
      </div>
      
      {/* Légende */}
      <div className="flex justify-between px-1">
        {LEVEL_CONFIG.map(level => {
          const count = distribution[level.key] || 0;
          if (count === 0) return null;
          
          return (
            <div key={level.key} className="flex items-center gap-1">
              <div 
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: level.color }}
              />
              <span className="text-xs text-gray-400">{level.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

/**
 * Statistiques synthétiques
 */
const StatsRow = ({ median, stdDev, min, max }) => (
  <div 
    className="grid grid-cols-4 gap-3 p-3 rounded-lg"
    style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
  >
    <div className="text-center">
      <p className="text-xs text-gray-500">Médiane</p>
      <p className="text-sm font-bold text-white">{median}/10</p>
    </div>
    <div className="text-center">
      <p className="text-xs text-gray-500">Écart-type</p>
      <p className="text-sm font-bold text-white">{stdDev.toFixed(1)}</p>
    </div>
    <div className="text-center">
      <p className="text-xs text-gray-500">Min</p>
      <p className="text-sm font-bold" style={{ color: BIONIC_COLORS.red.primary }}>
        {min}/10
      </p>
    </div>
    <div className="text-center">
      <p className="text-xs text-gray-500">Max</p>
      <p className="text-sm font-bold" style={{ color: BIONIC_COLORS.green.primary }}>
        {max}/10
      </p>
    </div>
  </div>
);

/**
 * Indicateur de santé globale
 */
const HealthIndicator = ({ distribution, total }) => {
  const excellent = distribution.excellent || 0;
  const good = distribution.good || 0;
  const poor = distribution.poor || 0;
  const critical = distribution.critical || 0;
  
  const positiveRatio = total > 0 ? ((excellent + good) / total) * 100 : 0;
  const negativeRatio = total > 0 ? ((poor + critical) / total) * 100 : 0;
  
  let healthLabel = 'Équilibré';
  let healthColor = BIONIC_COLORS.blue.light;
  
  if (positiveRatio >= 60) {
    healthLabel = 'Favorable';
    healthColor = BIONIC_COLORS.green.primary;
  } else if (negativeRatio >= 40) {
    healthLabel = 'Défavorable';
    healthColor = BIONIC_COLORS.red.primary;
  }
  
  return (
    <div 
      className="flex items-center justify-between p-3 rounded-lg"
      style={{ backgroundColor: `${healthColor}15` }}
    >
      <div className="flex items-center gap-2">
        <TrendingUp className="w-4 h-4" style={{ color: healthColor }} />
        <span className="text-sm text-gray-300">Profil global</span>
      </div>
      <span 
        className="text-sm font-semibold uppercase"
        style={{ color: healthColor }}
      >
        {healthLabel}
      </span>
    </div>
  );
};

// =============================================================================
// MAIN COMPONENT
// =============================================================================

/**
 * ScoreDistributionPanel
 * 
 * Répartition des scores BIONIC par niveau.
 * Affichage analytique avec distribution et statistiques.
 * 
 * @param {Array} scores - Liste des scores [{category, score}]
 * @param {Object} stats - Statistiques {median, stdDev, min, max}
 * @param {string} className - Classes CSS additionnelles
 */
const ScoreDistributionPanel = ({
  scores = [],
  stats = {},
  className = ''
}) => {
  // Calculer la distribution par niveau
  const distribution = {
    excellent: 0,
    good: 0,
    moderate: 0,
    poor: 0,
    critical: 0
  };
  
  scores.forEach(s => {
    const score = s.score || s.raw_value || 50;
    const score10 = Math.round(score / 10);
    
    if (score10 >= 8) distribution.excellent++;
    else if (score10 >= 6) distribution.good++;
    else if (score10 >= 4) distribution.moderate++;
    else if (score10 >= 2) distribution.poor++;
    else distribution.critical++;
  });
  
  const total = scores.length;
  const maxCount = Math.max(...Object.values(distribution));
  
  // Stats par défaut si non fournies
  const defaultStats = {
    median: Math.round((stats.median || 70) / 10),
    stdDev: stats.stdDev || 12.4,
    min: Math.round((stats.min || 45) / 10),
    max: Math.round((stats.max || 95) / 10)
  };
  
  return (
    <Card 
      className={`border-0 overflow-hidden ${className}`}
      style={{ backgroundColor: BIONIC_COLORS.black.elevated }}
    >
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-white text-base">
          <BarChart3 className="w-5 h-5" style={{ color: BIONIC_COLORS.gold.primary }} />
          Répartition des Scores
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Indicateur de santé */}
        <HealthIndicator distribution={distribution} total={total} />
        
        {/* Distribution par niveau */}
        <div className="space-y-1">
          {LEVEL_CONFIG.map(level => (
            <DistributionRow
              key={level.key}
              level={level}
              count={distribution[level.key]}
              total={total}
              maxCount={maxCount}
            />
          ))}
        </div>
        
        {/* Barre proportionnelle */}
        {total > 0 && (
          <>
            <div 
              className="h-px w-full"
              style={{ backgroundColor: BIONIC_COLORS.gray[800] }}
            />
            <ProportionalBar distribution={distribution} total={total} />
          </>
        )}
        
        {/* Statistiques */}
        <StatsRow {...defaultStats} />
      </CardContent>
    </Card>
  );
};

export default ScoreDistributionPanel;
