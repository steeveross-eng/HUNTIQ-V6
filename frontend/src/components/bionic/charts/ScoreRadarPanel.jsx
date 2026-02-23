/**
 * ScoreRadarPanel - Profil Analytique des 9 Scores BIONIC
 * ========================================================
 * BIONIC V5 ULTIME - PHASE 5.3
 * 
 * RESPONSABILITÉ UNIQUE:
 * - Afficher les 9 scores BIONIC sous forme de barres analytiques
 * - Notation qualitative sur échelle de 10
 * - Style scientifique, premium, minimaliste
 * 
 * DESIGN:
 * - Barres de progression épurées
 * - Indicateurs qualitatifs (X/10)
 * - Palette BIONIC sobre
 * - Icônes Lucide uniquement
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
  Target,
  Trees,
  Users,
  Thermometer,
  Brain,
  Activity,
  Gauge,
  Shield,
  Compass,
  TrendingUp,
  TrendingDown,
  Minus
} from 'lucide-react';

import { BIONIC_COLORS, getScoreColor } from '@/config/bionic-colors';

// =============================================================================
// CONSTANTS
// =============================================================================

const CATEGORY_CONFIG = {
  probability: { 
    icon: Target, 
    label: 'Probabilité',
    description: 'Chance de succès'
  },
  habitat: { 
    icon: Trees, 
    label: 'Habitat',
    description: 'Qualité du milieu'
  },
  pressure: { 
    icon: Users, 
    label: 'Pression',
    description: 'Activité humaine'
  },
  weather: { 
    icon: Thermometer, 
    label: 'Météo',
    description: 'Conditions climatiques'
  },
  behavior: { 
    icon: Brain, 
    label: 'Comportement',
    description: 'Activité animale'
  },
  multifactor: { 
    icon: Activity, 
    label: 'Multi-facteurs',
    description: 'Analyse combinée'
  },
  density: { 
    icon: Gauge, 
    label: 'Densité',
    description: 'Population locale'
  },
  risk: { 
    icon: Shield, 
    label: 'Risques',
    description: 'Niveau de sécurité'
  },
  mobility: { 
    icon: Compass, 
    label: 'Mobilité',
    description: 'Déplacement gibier'
  }
};

// Couleurs par niveau (échelle 10)
const getLevelColor = (score10) => {
  if (score10 >= 8) return BIONIC_COLORS.green.primary;
  if (score10 >= 6) return BIONIC_COLORS.gold.primary;
  if (score10 >= 4) return BIONIC_COLORS.blue.light;
  if (score10 >= 2) return '#F97316'; // Orange
  return BIONIC_COLORS.red.primary;
};

// Icône de tendance
const getTrendIcon = (trend) => {
  if (trend === 'up') return TrendingUp;
  if (trend === 'down') return TrendingDown;
  return Minus;
};

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

/**
 * Ligne de score individuelle
 */
const ScoreRow = ({ category, score, trend }) => {
  const config = CATEGORY_CONFIG[category] || CATEGORY_CONFIG.probability;
  const Icon = config.icon;
  
  // Convertir score 0-100 en échelle 0-10
  const score10 = Math.round(score / 10);
  const levelColor = getLevelColor(score10);
  const TrendIcon = getTrendIcon(trend);
  
  // Générer les segments de la barre (10 segments)
  const segments = Array.from({ length: 10 }, (_, i) => i < score10);
  
  return (
    <div className="flex items-center gap-3 py-2.5">
      {/* Icône de catégorie */}
      <div 
        className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
        style={{ backgroundColor: `${levelColor}15` }}
      >
        <Icon className="w-4 h-4" style={{ color: levelColor }} />
      </div>
      
      {/* Label et description */}
      <div className="w-28 flex-shrink-0">
        <p className="text-sm font-medium text-white leading-tight">
          {config.label}
        </p>
        <p className="text-xs text-gray-500 leading-tight">
          {config.description}
        </p>
      </div>
      
      {/* Barre segmentée */}
      <div className="flex-1 flex items-center gap-0.5">
        {segments.map((active, index) => (
          <div
            key={index}
            className="h-2 flex-1 rounded-sm transition-all duration-300"
            style={{ 
              backgroundColor: active ? levelColor : BIONIC_COLORS.gray[800],
              opacity: active ? 1 : 0.4
            }}
          />
        ))}
      </div>
      
      {/* Score sur 10 */}
      <div className="w-12 text-right flex-shrink-0">
        <span 
          className="text-sm font-bold"
          style={{ color: levelColor }}
        >
          {score10}
        </span>
        <span className="text-xs text-gray-500">/10</span>
      </div>
      
      {/* Tendance (optionnel) */}
      {trend && (
        <TrendIcon 
          className="w-3.5 h-3.5 flex-shrink-0"
          style={{ 
            color: trend === 'up' ? BIONIC_COLORS.green.primary : 
                   trend === 'down' ? BIONIC_COLORS.red.primary : 
                   BIONIC_COLORS.gray[500]
          }}
        />
      )}
    </div>
  );
};

/**
 * Indicateur de score global (cercles)
 */
const GlobalScoreIndicator = ({ score }) => {
  const score10 = Math.round(score / 10);
  const levelColor = getLevelColor(score10);
  
  // Générer les 10 cercles
  const circles = Array.from({ length: 10 }, (_, i) => i < score10);
  
  // Label qualitatif
  const getQualityLabel = (s10) => {
    if (s10 >= 8) return 'EXCELLENT';
    if (s10 >= 6) return 'BON';
    if (s10 >= 4) return 'MODÉRÉ';
    if (s10 >= 2) return 'FAIBLE';
    return 'CRITIQUE';
  };
  
  return (
    <div 
      className="p-4 rounded-lg flex items-center justify-between"
      style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
    >
      <div className="flex items-center gap-3">
        <div 
          className="w-12 h-12 rounded-full flex items-center justify-center"
          style={{ backgroundColor: `${levelColor}20` }}
        >
          <span 
            className="text-xl font-bold"
            style={{ color: levelColor }}
          >
            {score10}
          </span>
        </div>
        <div>
          <p className="text-sm text-gray-400">Score Global</p>
          <p 
            className="text-sm font-semibold uppercase"
            style={{ color: levelColor }}
          >
            {getQualityLabel(score10)}
          </p>
        </div>
      </div>
      
      {/* Cercles indicateurs */}
      <div className="flex gap-1">
        {circles.map((active, index) => (
          <div
            key={index}
            className="w-2.5 h-2.5 rounded-full transition-all duration-300"
            style={{ 
              backgroundColor: active ? levelColor : BIONIC_COLORS.gray[700]
            }}
          />
        ))}
      </div>
    </div>
  );
};

// =============================================================================
// MAIN COMPONENT
// =============================================================================

/**
 * ScoreRadarPanel
 * 
 * Profil analytique des 9 scores BIONIC.
 * Affichage premium avec barres segmentées et notation sur 10.
 * 
 * @param {Array} scores - Liste des scores [{category, score, trend?}]
 * @param {number} globalScore - Score global 0-100
 * @param {string} className - Classes CSS additionnelles
 */
const ScoreRadarPanel = ({
  scores = [],
  globalScore = 0,
  className = ''
}) => {
  // Ordre d'affichage des catégories
  const categoryOrder = [
    'probability', 'habitat', 'pressure', 'weather', 'behavior',
    'multifactor', 'density', 'risk', 'mobility'
  ];
  
  // Mapper les scores par catégorie
  const scoreMap = {};
  scores.forEach(s => {
    scoreMap[s.category] = s;
  });
  
  return (
    <Card 
      className={`border-0 overflow-hidden ${className}`}
      style={{ backgroundColor: BIONIC_COLORS.black.elevated }}
    >
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-white text-base">
          <Activity className="w-5 h-5" style={{ color: BIONIC_COLORS.gold.primary }} />
          Profil Analytique
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Score global */}
        <GlobalScoreIndicator score={globalScore} />
        
        {/* Séparateur */}
        <div 
          className="h-px w-full"
          style={{ backgroundColor: BIONIC_COLORS.gray[800] }}
        />
        
        {/* Liste des 9 scores */}
        <div className="space-y-1">
          {categoryOrder.map(category => {
            const scoreData = scoreMap[category];
            if (!scoreData) return null;
            
            return (
              <ScoreRow
                key={category}
                category={category}
                score={scoreData.score || scoreData.raw_value || 50}
                trend={scoreData.trend}
              />
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default ScoreRadarPanel;
