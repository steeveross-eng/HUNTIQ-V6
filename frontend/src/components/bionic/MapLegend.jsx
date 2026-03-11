/**
 * MapLegend - Légende de la Carte BIONIC avec Coloration Dynamique
 * ================================================================
 * BIONIC V5 ULTIME - PHASE 5.6
 * 
 * RESPONSABILITÉ UNIQUE:
 * - Afficher la légende des scores avec échelle de 10
 * - Coloration dynamique selon la palette BIONIC
 * - Indicateurs de qualité, légalité et distance
 * 
 * PALETTE BIONIC (obligatoire):
 * - 9-10 : Vert analytique (#00A676)
 * - 7-8  : Doré premium (#C9A86A)
 * - 5-6  : Bleu profond (#1E3A8A)
 * - 3-4  : Orange sobre (#C26A2E)
 * - 0-2  : Rouge scientifique (#B91C1C)
 * 
 * ISOLATION:
 * - Composant 100% présentationnel
 * - Aucune logique métier
 * - Données via props uniquement
 * 
 * Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  Map,
  Navigation,
  Scale,
  CheckCircle,
  XCircle,
  Target,
  Info
} from 'lucide-react';

import { BIONIC_COLORS } from '@/config/bionic-colors';

// =============================================================================
// CONSTANTS - PALETTE BIONIC OFFICIELLE
// =============================================================================

/**
 * Palette de couleurs BIONIC pour les scores
 * Notation sur échelle de 10
 */
export const SCORE_COLOR_PALETTE = {
  EXCELLENT: '#00A676',    // 9-10 : Vert analytique
  GOOD: '#C9A86A',         // 7-8  : Doré premium
  MODERATE: '#1E3A8A',     // 5-6  : Bleu profond
  POOR: '#C26A2E',         // 3-4  : Orange sobre
  CRITICAL: '#B91C1C'      // 0-2  : Rouge scientifique
};

/**
 * Configuration des niveaux de score
 */
export const SCORE_LEVELS = [
  { 
    range: '9-10', 
    rangeMin: 9, 
    rangeMax: 10,
    label: 'FAVORABLE', 
    sublabel: 'Excellent',
    color: SCORE_COLOR_PALETTE.EXCELLENT,
    description: 'Conditions optimales'
  },
  { 
    range: '7-8', 
    rangeMin: 7, 
    rangeMax: 8,
    label: 'FAVORABLE', 
    sublabel: 'Bon',
    color: SCORE_COLOR_PALETTE.GOOD,
    description: 'Conditions favorables'
  },
  { 
    range: '5-6', 
    rangeMin: 5, 
    rangeMax: 6,
    label: 'MODÉRÉ', 
    sublabel: 'Acceptable',
    color: SCORE_COLOR_PALETTE.MODERATE,
    description: 'Conditions acceptables'
  },
  { 
    range: '3-4', 
    rangeMin: 3, 
    rangeMax: 4,
    label: 'DÉFAVORABLE', 
    sublabel: 'Faible',
    color: SCORE_COLOR_PALETTE.POOR,
    description: 'Conditions défavorables'
  },
  { 
    range: '0-2', 
    rangeMin: 0, 
    rangeMax: 2,
    label: 'DÉFAVORABLE', 
    sublabel: 'Critique',
    color: SCORE_COLOR_PALETTE.CRITICAL,
    description: 'Conditions critiques'
  }
];

/**
 * Obtient la couleur pour un score donné (sur 10)
 */
export const getScoreColorFromPalette = (score10) => {
  if (score10 >= 9) return SCORE_COLOR_PALETTE.EXCELLENT;
  if (score10 >= 7) return SCORE_COLOR_PALETTE.GOOD;
  if (score10 >= 5) return SCORE_COLOR_PALETTE.MODERATE;
  if (score10 >= 3) return SCORE_COLOR_PALETTE.POOR;
  return SCORE_COLOR_PALETTE.CRITICAL;
};

/**
 * Obtient le niveau qualitatif pour un score donné (sur 10)
 */
export const getScoreLevel = (score10) => {
  return SCORE_LEVELS.find(
    level => score10 >= level.rangeMin && score10 <= level.rangeMax
  ) || SCORE_LEVELS[SCORE_LEVELS.length - 1];
};

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

/**
 * Barre de gradient des scores
 */
const ScoreGradientBar = () => (
  <div className="relative">
    {/* Barre de gradient */}
    <div className="h-4 rounded-lg flex overflow-hidden">
      {SCORE_LEVELS.map((level, index) => (
        <div
          key={level.range}
          className="flex-1 relative"
          style={{ backgroundColor: level.color }}
        >
          {/* Séparateur entre niveaux */}
          {index < SCORE_LEVELS.length - 1 && (
            <div 
              className="absolute right-0 top-0 bottom-0 w-px"
              style={{ backgroundColor: 'rgba(0,0,0,0.3)' }}
            />
          )}
        </div>
      ))}
    </div>
    
    {/* Marqueurs numériques */}
    <div className="flex justify-between mt-1.5 px-0.5">
      <span className="text-[10px] text-gray-500">0</span>
      <span className="text-[10px] text-gray-500">2</span>
      <span className="text-[10px] text-gray-500">4</span>
      <span className="text-[10px] text-gray-500">6</span>
      <span className="text-[10px] text-gray-500">8</span>
      <span className="text-[10px] text-gray-500">10</span>
    </div>
  </div>
);

/**
 * Ligne de légende pour un niveau de score
 */
const ScoreLevelRow = ({ level, compact = false }) => (
  <div className="flex items-center gap-3 py-1.5">
    {/* Indicateur de couleur */}
    <div 
      className="w-4 h-4 rounded flex-shrink-0"
      style={{ backgroundColor: level.color }}
    />
    
    {/* Score range */}
    <div className="w-10 flex-shrink-0">
      <span className="text-sm font-mono text-white">{level.range}</span>
    </div>
    
    {/* Label et description */}
    <div className="flex-1 min-w-0">
      <div className="flex items-center gap-2">
        <span 
          className="text-xs font-semibold uppercase"
          style={{ color: level.color }}
        >
          {level.label}
        </span>
        {!compact && (
          <span className="text-xs text-gray-500">
            {level.sublabel}
          </span>
        )}
      </div>
      {!compact && (
        <p className="text-[10px] text-gray-500 mt-0.5">
          {level.description}
        </p>
      )}
    </div>
  </div>
);

/**
 * Section des indicateurs de qualité
 */
const QualityIndicators = () => (
  <div className="space-y-2">
    <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">
      Catégories de qualité
    </p>
    
    <div className="grid grid-cols-3 gap-2">
      {/* Favorable */}
      <div 
        className="p-2 rounded-lg text-center"
        style={{ backgroundColor: `${SCORE_COLOR_PALETTE.EXCELLENT}15` }}
      >
        <div 
          className="w-3 h-3 rounded-full mx-auto mb-1"
          style={{ backgroundColor: SCORE_COLOR_PALETTE.EXCELLENT }}
        />
        <span 
          className="text-[10px] font-semibold uppercase"
          style={{ color: SCORE_COLOR_PALETTE.EXCELLENT }}
        >
          Favorable
        </span>
        <p className="text-[9px] text-gray-500 mt-0.5">7-10</p>
      </div>
      
      {/* Modéré */}
      <div 
        className="p-2 rounded-lg text-center"
        style={{ backgroundColor: `${SCORE_COLOR_PALETTE.MODERATE}15` }}
      >
        <div 
          className="w-3 h-3 rounded-full mx-auto mb-1"
          style={{ backgroundColor: SCORE_COLOR_PALETTE.MODERATE }}
        />
        <span 
          className="text-[10px] font-semibold uppercase"
          style={{ color: SCORE_COLOR_PALETTE.MODERATE }}
        >
          Modéré
        </span>
        <p className="text-[9px] text-gray-500 mt-0.5">5-6</p>
      </div>
      
      {/* Défavorable */}
      <div 
        className="p-2 rounded-lg text-center"
        style={{ backgroundColor: `${SCORE_COLOR_PALETTE.CRITICAL}15` }}
      >
        <div 
          className="w-3 h-3 rounded-full mx-auto mb-1"
          style={{ backgroundColor: SCORE_COLOR_PALETTE.CRITICAL }}
        />
        <span 
          className="text-[10px] font-semibold uppercase"
          style={{ color: SCORE_COLOR_PALETTE.CRITICAL }}
        >
          Défavorable
        </span>
        <p className="text-[9px] text-gray-500 mt-0.5">0-4</p>
      </div>
    </div>
  </div>
);

/**
 * Section indicateur légal/illégal
 */
const LegalIndicator = ({ isLegal = true }) => (
  <div className="space-y-2">
    <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">
      Conformité légale
    </p>
    
    <div className="grid grid-cols-2 gap-2">
      {/* Légal */}
      <div 
        className={`p-2.5 rounded-lg flex items-center gap-2 ${isLegal ? 'ring-1' : ''}`}
        style={{ 
          backgroundColor: `${SCORE_COLOR_PALETTE.EXCELLENT}10`,
          ringColor: isLegal ? SCORE_COLOR_PALETTE.EXCELLENT : 'transparent'
        }}
      >
        <CheckCircle 
          className="w-4 h-4 flex-shrink-0" 
          style={{ color: SCORE_COLOR_PALETTE.EXCELLENT }} 
        />
        <div>
          <span 
            className="text-xs font-semibold uppercase block"
            style={{ color: SCORE_COLOR_PALETTE.EXCELLENT }}
          >
            Légal
          </span>
          <span className="text-[9px] text-gray-500">Heures autorisées</span>
        </div>
      </div>
      
      {/* Illégal */}
      <div 
        className={`p-2.5 rounded-lg flex items-center gap-2 ${!isLegal ? 'ring-1' : ''}`}
        style={{ 
          backgroundColor: `${SCORE_COLOR_PALETTE.CRITICAL}10`,
          ringColor: !isLegal ? SCORE_COLOR_PALETTE.CRITICAL : 'transparent'
        }}
      >
        <XCircle 
          className="w-4 h-4 flex-shrink-0" 
          style={{ color: SCORE_COLOR_PALETTE.CRITICAL }} 
        />
        <div>
          <span 
            className="text-xs font-semibold uppercase block"
            style={{ color: SCORE_COLOR_PALETTE.CRITICAL }}
          >
            Hors heures
          </span>
          <span className="text-[9px] text-gray-500">Non autorisé</span>
        </div>
      </div>
    </div>
  </div>
);

/**
 * Section indicateur de distance
 */
const DistanceIndicator = ({ maxDistance = 10 }) => (
  <div className="space-y-2">
    <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">
      Distance depuis le waypoint
    </p>
    
    <div 
      className="p-3 rounded-lg"
      style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
    >
      <div className="flex items-center gap-3">
        <Navigation 
          className="w-5 h-5 flex-shrink-0" 
          style={{ color: BIONIC_COLORS.gold.primary }} 
        />
        <div className="flex-1">
          {/* Barre de distance */}
          <div className="relative h-2 rounded-full overflow-hidden" style={{ backgroundColor: BIONIC_COLORS.gray[800] }}>
            <div 
              className="absolute left-0 top-0 bottom-0 rounded-full"
              style={{ 
                width: '100%',
                background: `linear-gradient(90deg, ${SCORE_COLOR_PALETTE.EXCELLENT} 0%, ${SCORE_COLOR_PALETTE.GOOD} 30%, ${SCORE_COLOR_PALETTE.MODERATE} 60%, ${SCORE_COLOR_PALETTE.POOR} 100%)`
              }}
            />
          </div>
          
          {/* Labels de distance */}
          <div className="flex justify-between mt-1">
            <span className="text-[10px] text-gray-500">0 km</span>
            <span className="text-[10px] text-gray-500">{Math.round(maxDistance / 2)} km</span>
            <span className="text-[10px] text-gray-500">{maxDistance} km</span>
          </div>
        </div>
      </div>
      
      <p className="text-[10px] text-gray-500 mt-2">
        Plus le hotspot est proche, plus il est accessible
      </p>
    </div>
  </div>
);

/**
 * Section info waypoint-centric
 */
const WaypointCentricInfo = ({ waypointName }) => (
  <div 
    className="p-3 rounded-lg flex items-start gap-2"
    style={{ backgroundColor: `${BIONIC_COLORS.gold.primary}10` }}
  >
    <Target 
      className="w-4 h-4 flex-shrink-0 mt-0.5" 
      style={{ color: BIONIC_COLORS.gold.primary }} 
    />
    <div>
      <p className="text-xs font-medium text-white">
        Analyse waypoint-centric
      </p>
      <p className="text-[10px] text-gray-400 mt-0.5">
        Toutes les distances et directions sont calculées depuis:
      </p>
      {waypointName && (
        <p 
          className="text-xs font-medium mt-1"
          style={{ color: BIONIC_COLORS.gold.primary }}
        >
          {waypointName}
        </p>
      )}
    </div>
  </div>
);

// =============================================================================
// MAIN COMPONENT
// =============================================================================

/**
 * MapLegend
 * 
 * Légende de la carte BIONIC avec coloration dynamique.
 * Affiche l'échelle de scores, les catégories de qualité,
 * les indicateurs légaux et de distance.
 * 
 * @param {boolean} isLegal - État légal actuel (heures de chasse)
 * @param {string} waypointName - Nom du waypoint de référence
 * @param {number} maxDistance - Distance maximale affichée (km)
 * @param {boolean} compact - Mode compact (moins de détails)
 * @param {boolean} showDistanceScale - Afficher l'échelle de distance
 * @param {boolean} showLegalIndicator - Afficher l'indicateur légal
 * @param {boolean} showWaypointInfo - Afficher l'info waypoint-centric
 * @param {string} className - Classes CSS additionnelles
 */
const MapLegend = ({
  isLegal = true,
  waypointName = null,
  maxDistance = 10,
  compact = false,
  showDistanceScale = true,
  showLegalIndicator = true,
  showWaypointInfo = true,
  className = ''
}) => {
  return (
    <Card 
      className={`border-0 overflow-hidden ${className}`}
      style={{ backgroundColor: BIONIC_COLORS.black.elevated }}
    >
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-white text-base">
          <Map className="w-5 h-5" style={{ color: BIONIC_COLORS.gold.primary }} />
          Légende
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Barre de gradient */}
        <div>
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">
            Échelle des scores (0-10)
          </p>
          <ScoreGradientBar />
        </div>
        
        <Separator style={{ backgroundColor: BIONIC_COLORS.gray[800] }} />
        
        {/* Détail des niveaux */}
        {!compact && (
          <>
            <div className="space-y-0.5">
              {SCORE_LEVELS.map(level => (
                <ScoreLevelRow key={level.range} level={level} compact={compact} />
              ))}
            </div>
            
            <Separator style={{ backgroundColor: BIONIC_COLORS.gray[800] }} />
          </>
        )}
        
        {/* Catégories de qualité */}
        <QualityIndicators />
        
        {/* Indicateur légal */}
        {showLegalIndicator && (
          <>
            <Separator style={{ backgroundColor: BIONIC_COLORS.gray[800] }} />
            <LegalIndicator isLegal={isLegal} />
          </>
        )}
        
        {/* Échelle de distance */}
        {showDistanceScale && (
          <>
            <Separator style={{ backgroundColor: BIONIC_COLORS.gray[800] }} />
            <DistanceIndicator maxDistance={maxDistance} />
          </>
        )}
        
        {/* Info waypoint-centric */}
        {showWaypointInfo && waypointName && (
          <>
            <Separator style={{ backgroundColor: BIONIC_COLORS.gray[800] }} />
            <WaypointCentricInfo waypointName={waypointName} />
          </>
        )}
      </CardContent>
    </Card>
  );
};

// =============================================================================
// EXPORTS
// =============================================================================

export default MapLegend;
