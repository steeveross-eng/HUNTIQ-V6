/**
 * EnrichedHotspotPopup - Popup Enrichi pour Hotspots BIONIC
 * ==========================================================
 * BIONIC V5 ULTIME - PHASE 5.4
 * 
 * RESPONSABILITÉ UNIQUE:
 * - Afficher les informations détaillées d'un hotspot
 * - Score, distance, direction, facteurs, risques
 * - Popup waypoint-centric (lié au waypoint sélectionné)
 * 
 * CONTENU:
 * - Score du hotspot (notation sur 10)
 * - Distance + direction depuis le waypoint
 * - Facteurs positifs / négatifs
 * - Habitat dominant
 * - Risques locaux
 * - Pression locale
 * - Recommandation contextuelle
 * - Badge de qualité
 * - Heures légales (liées au waypoint)
 * 
 * ISOLATION:
 * - Composant 100% présentationnel
 * - Aucune logique métier, aucun calcul
 * - Données via props uniquement
 * 
 * Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
 */

import React from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import {
  MapPin,
  Navigation,
  Compass,
  Target,
  Trees,
  Users,
  Shield,
  AlertTriangle,
  Clock,
  CheckCircle,
  XCircle,
  TrendingUp,
  TrendingDown,
  ChevronRight,
  Crosshair,
  Scale,
  X
} from 'lucide-react';

import { BIONIC_COLORS, getScoreColor } from '@/config/bionic-colors';

// =============================================================================
// CONSTANTS
// =============================================================================

const QUALITY_CONFIG = {
  favorable: { 
    label: 'FAVORABLE', 
    color: BIONIC_COLORS.green.primary,
    icon: TrendingUp
  },
  moderate: { 
    label: 'MODÉRÉ', 
    color: BIONIC_COLORS.gold.primary,
    icon: Target
  },
  unfavorable: { 
    label: 'DÉFAVORABLE', 
    color: BIONIC_COLORS.red.primary,
    icon: TrendingDown
  }
};

const HABITAT_CONFIG = {
  forest: { label: 'Forêt', icon: Trees, color: BIONIC_COLORS.green.primary },
  mixed: { label: 'Mixte', icon: Trees, color: BIONIC_COLORS.gold.primary },
  clearing: { label: 'Clairière', icon: Target, color: BIONIC_COLORS.blue.light },
  wetland: { label: 'Zone humide', icon: Trees, color: BIONIC_COLORS.blue.primary },
  edge: { label: 'Lisière', icon: Trees, color: '#F97316' },
  default: { label: 'Non défini', icon: MapPin, color: BIONIC_COLORS.gray[500] }
};

const RISK_LEVEL_CONFIG = {
  low: { label: 'Faible', color: BIONIC_COLORS.green.primary },
  moderate: { label: 'Modéré', color: BIONIC_COLORS.gold.primary },
  high: { label: 'Élevé', color: '#F97316' },
  critical: { label: 'Critique', color: BIONIC_COLORS.red.primary }
};

const PRESSURE_LEVEL_CONFIG = {
  low: { label: 'Faible', color: BIONIC_COLORS.green.primary },
  moderate: { label: 'Modérée', color: BIONIC_COLORS.gold.primary },
  high: { label: 'Élevée', color: '#F97316' },
  extreme: { label: 'Extrême', color: BIONIC_COLORS.red.primary }
};

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

/**
 * Header du popup avec score et badge de qualité
 */
const PopupHeader = ({ name, score, quality, onClose }) => {
  const score10 = Math.round(score / 10);
  const scoreColor = getScoreColor(score);
  const qualityConfig = QUALITY_CONFIG[quality] || QUALITY_CONFIG.moderate;
  const QualityIcon = qualityConfig.icon;
  
  return (
    <div className="flex items-start justify-between gap-3">
      <div className="flex items-start gap-3 flex-1 min-w-0">
        {/* Score circulaire */}
        <div 
          className="w-14 h-14 rounded-xl flex flex-col items-center justify-center flex-shrink-0"
          style={{ backgroundColor: `${scoreColor}20` }}
        >
          <span 
            className="text-xl font-bold leading-none"
            style={{ color: scoreColor }}
          >
            {score10}
          </span>
          <span className="text-xs text-gray-500">/10</span>
        </div>
        
        {/* Nom et badge */}
        <div className="flex-1 min-w-0">
          <h3 className="text-base font-semibold text-white truncate">
            {name}
          </h3>
          <div 
            className="inline-flex items-center gap-1.5 mt-1 px-2 py-0.5 rounded"
            style={{ backgroundColor: `${qualityConfig.color}20` }}
          >
            <QualityIcon className="w-3.5 h-3.5" style={{ color: qualityConfig.color }} />
            <span 
              className="text-xs font-semibold uppercase"
              style={{ color: qualityConfig.color }}
            >
              {qualityConfig.label}
            </span>
          </div>
        </div>
      </div>
      
      {/* Bouton fermer */}
      {onClose && (
        <button
          onClick={onClose}
          className="p-1 rounded-lg hover:bg-white/10 transition-colors"
        >
          <X className="w-4 h-4 text-gray-400" />
        </button>
      )}
    </div>
  );
};

/**
 * Section distance et direction
 */
const LocationSection = ({ distance, direction, bearing, waypointName }) => (
  <div 
    className="p-3 rounded-lg"
    style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
  >
    <div className="flex items-center gap-2 mb-2">
      <Navigation className="w-4 h-4" style={{ color: BIONIC_COLORS.gold.primary }} />
      <span className="text-sm font-medium text-white">Position relative</span>
    </div>
    
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div>
          <p className="text-xs text-gray-500">Distance</p>
          <p className="text-lg font-bold text-white">{distance.toFixed(1)} km</p>
        </div>
        
        <div 
          className="w-px h-10"
          style={{ backgroundColor: BIONIC_COLORS.gray[700] }}
        />
        
        <div>
          <p className="text-xs text-gray-500">Direction</p>
          <div className="flex items-center gap-1">
            <Compass className="w-4 h-4" style={{ color: BIONIC_COLORS.blue.light }} />
            <p className="text-lg font-bold text-white">{direction}</p>
            <span className="text-xs text-gray-500">({bearing}°)</span>
          </div>
        </div>
      </div>
    </div>
    
    {waypointName && (
      <p className="text-xs text-gray-500 mt-2">
        Depuis: <span className="text-gray-400">{waypointName}</span>
      </p>
    )}
  </div>
);

/**
 * Section heures légales (liées au waypoint)
 */
const LegalHoursSection = ({ legalStart, legalEnd, isCurrentlyLegal, duration }) => (
  <div 
    className="p-3 rounded-lg"
    style={{ backgroundColor: isCurrentlyLegal ? `${BIONIC_COLORS.green.primary}10` : `${BIONIC_COLORS.red.primary}10` }}
  >
    <div className="flex items-center justify-between mb-2">
      <div className="flex items-center gap-2">
        <Scale className="w-4 h-4" style={{ color: isCurrentlyLegal ? BIONIC_COLORS.green.primary : BIONIC_COLORS.red.primary }} />
        <span className="text-sm font-medium text-white">Heures légales</span>
      </div>
      
      <div 
        className="flex items-center gap-1.5 px-2 py-0.5 rounded"
        style={{ 
          backgroundColor: isCurrentlyLegal ? BIONIC_COLORS.green.muted : BIONIC_COLORS.red.muted 
        }}
      >
        {isCurrentlyLegal ? (
          <CheckCircle className="w-3.5 h-3.5" style={{ color: BIONIC_COLORS.green.primary }} />
        ) : (
          <XCircle className="w-3.5 h-3.5" style={{ color: BIONIC_COLORS.red.primary }} />
        )}
        <span 
          className="text-xs font-semibold uppercase"
          style={{ color: isCurrentlyLegal ? BIONIC_COLORS.green.primary : BIONIC_COLORS.red.primary }}
        >
          {isCurrentlyLegal ? 'Légal' : 'Hors heures'}
        </span>
      </div>
    </div>
    
    <div className="flex items-center gap-4">
      <div>
        <p className="text-xs text-gray-500">Début</p>
        <p className="text-sm font-semibold text-white">{legalStart}</p>
      </div>
      <div>
        <p className="text-xs text-gray-500">Fin</p>
        <p className="text-sm font-semibold text-white">{legalEnd}</p>
      </div>
      {duration && (
        <div>
          <p className="text-xs text-gray-500">Durée</p>
          <p className="text-sm font-semibold text-white">{duration}</p>
        </div>
      )}
    </div>
  </div>
);

/**
 * Section habitat dominant
 */
const HabitatSection = ({ habitat, coverage }) => {
  const config = HABITAT_CONFIG[habitat] || HABITAT_CONFIG.default;
  const HabitatIcon = config.icon;
  
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div 
          className="w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: `${config.color}20` }}
        >
          <HabitatIcon className="w-4 h-4" style={{ color: config.color }} />
        </div>
        <div>
          <p className="text-xs text-gray-500">Habitat dominant</p>
          <p className="text-sm font-medium text-white">{config.label}</p>
        </div>
      </div>
      
      {coverage !== undefined && (
        <div className="text-right">
          <p className="text-xs text-gray-500">Couverture</p>
          <p className="text-sm font-semibold" style={{ color: config.color }}>
            {coverage}%
          </p>
        </div>
      )}
    </div>
  );
};

/**
 * Section risques locaux
 */
const RiskSection = ({ riskLevel, risks }) => {
  const config = RISK_LEVEL_CONFIG[riskLevel] || RISK_LEVEL_CONFIG.moderate;
  
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4" style={{ color: config.color }} />
          <span className="text-sm text-gray-400">Risques locaux</span>
        </div>
        <span 
          className="text-xs font-semibold px-2 py-0.5 rounded"
          style={{ 
            backgroundColor: `${config.color}20`,
            color: config.color
          }}
        >
          {config.label}
        </span>
      </div>
      
      {risks && risks.length > 0 && (
        <div className="space-y-1">
          {risks.slice(0, 2).map((risk, index) => (
            <div 
              key={index}
              className="flex items-center gap-2 text-xs text-gray-400"
            >
              <AlertTriangle className="w-3 h-3" style={{ color: config.color }} />
              <span>{risk}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

/**
 * Section pression locale
 */
const PressureSection = ({ pressureLevel, pressureScore }) => {
  const config = PRESSURE_LEVEL_CONFIG[pressureLevel] || PRESSURE_LEVEL_CONFIG.moderate;
  const score10 = Math.round((pressureScore || 50) / 10);
  
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <Users className="w-4 h-4" style={{ color: config.color }} />
        <div>
          <p className="text-xs text-gray-500">Pression de chasse</p>
          <p className="text-sm font-medium" style={{ color: config.color }}>
            {config.label}
          </p>
        </div>
      </div>
      
      <div className="flex items-center gap-1">
        <span className="text-sm font-bold" style={{ color: config.color }}>
          {score10}
        </span>
        <span className="text-xs text-gray-500">/10</span>
      </div>
    </div>
  );
};

/**
 * Section facteurs positifs/négatifs
 */
const FactorsSection = ({ positiveFactors, negativeFactors }) => (
  <div className="space-y-3">
    {/* Facteurs positifs */}
    {positiveFactors && positiveFactors.length > 0 && (
      <div>
        <div className="flex items-center gap-2 mb-1.5">
          <TrendingUp className="w-3.5 h-3.5" style={{ color: BIONIC_COLORS.green.primary }} />
          <span className="text-xs font-medium text-gray-400">Points forts</span>
        </div>
        <div className="space-y-1">
          {positiveFactors.slice(0, 2).map((factor, index) => (
            <div 
              key={index}
              className="flex items-start gap-2 text-xs"
            >
              <ChevronRight 
                className="w-3 h-3 mt-0.5 flex-shrink-0" 
                style={{ color: BIONIC_COLORS.green.primary }} 
              />
              <span className="text-gray-300">{factor}</span>
            </div>
          ))}
        </div>
      </div>
    )}
    
    {/* Facteurs négatifs */}
    {negativeFactors && negativeFactors.length > 0 && (
      <div>
        <div className="flex items-center gap-2 mb-1.5">
          <TrendingDown className="w-3.5 h-3.5" style={{ color: BIONIC_COLORS.red.primary }} />
          <span className="text-xs font-medium text-gray-400">Points faibles</span>
        </div>
        <div className="space-y-1">
          {negativeFactors.slice(0, 2).map((factor, index) => (
            <div 
              key={index}
              className="flex items-start gap-2 text-xs"
            >
              <ChevronRight 
                className="w-3 h-3 mt-0.5 flex-shrink-0" 
                style={{ color: BIONIC_COLORS.red.primary }} 
              />
              <span className="text-gray-300">{factor}</span>
            </div>
          ))}
        </div>
      </div>
    )}
  </div>
);

/**
 * Section recommandation contextuelle
 */
const RecommendationSection = ({ recommendation }) => {
  if (!recommendation) return null;
  
  return (
    <div 
      className="p-3 rounded-lg"
      style={{ backgroundColor: `${BIONIC_COLORS.blue.light}10` }}
    >
      <div className="flex items-start gap-2">
        <Target 
          className="w-4 h-4 mt-0.5 flex-shrink-0" 
          style={{ color: BIONIC_COLORS.blue.light }} 
        />
        <div>
          <p className="text-xs font-medium text-gray-400 mb-1">Recommandation</p>
          <p className="text-sm text-gray-200">{recommendation}</p>
        </div>
      </div>
    </div>
  );
};

/**
 * Bouton d'action
 */
const ActionButton = ({ onClick, label }) => (
  <Button
    onClick={onClick}
    className="w-full"
    style={{ 
      backgroundColor: BIONIC_COLORS.gold.primary,
      color: BIONIC_COLORS.black.base
    }}
  >
    <Crosshair className="w-4 h-4 mr-2" />
    {label || 'Analyser ce hotspot'}
  </Button>
);

// =============================================================================
// MAIN COMPONENT
// =============================================================================

/**
 * EnrichedHotspotPopup
 * 
 * Popup enrichi pour afficher les détails d'un hotspot.
 * 100% waypoint-centric - toutes les données sont relatives au waypoint sélectionné.
 * 
 * @param {Object} hotspot - Données du hotspot
 * @param {Object} waypointContext - Contexte du waypoint (heures légales, nom)
 * @param {function} onClose - Callback pour fermer le popup
 * @param {function} onAnalyze - Callback pour analyser le hotspot
 * @param {string} className - Classes CSS additionnelles
 */
const EnrichedHotspotPopup = ({
  hotspot = {},
  waypointContext = {},
  onClose,
  onAnalyze,
  className = ''
}) => {
  // Extraire les données du hotspot
  const {
    name = 'Hotspot inconnu',
    score = 50,
    quality = 'moderate',
    distance = 0,
    direction = 'N',
    bearing = 0,
    habitat = 'default',
    habitatCoverage,
    riskLevel = 'moderate',
    risks = [],
    pressureLevel = 'moderate',
    pressureScore = 50,
    positiveFactors = [],
    negativeFactors = [],
    recommendation
  } = hotspot;
  
  // Extraire le contexte du waypoint
  const {
    waypointName,
    legalStart = '05:12',
    legalEnd = '21:18',
    legalDuration = '16h06',
    isCurrentlyLegal = true
  } = waypointContext;
  
  return (
    <Card 
      className={`border-0 overflow-hidden w-80 ${className}`}
      style={{ backgroundColor: BIONIC_COLORS.black.elevated }}
    >
      <CardHeader className="pb-3">
        <PopupHeader 
          name={name}
          score={score}
          quality={quality}
          onClose={onClose}
        />
      </CardHeader>
      
      <CardContent className="space-y-3 pt-0">
        {/* Position relative au waypoint */}
        <LocationSection 
          distance={distance}
          direction={direction}
          bearing={bearing}
          waypointName={waypointName}
        />
        
        {/* Heures légales du waypoint */}
        <LegalHoursSection 
          legalStart={legalStart}
          legalEnd={legalEnd}
          duration={legalDuration}
          isCurrentlyLegal={isCurrentlyLegal}
        />
        
        <Separator style={{ backgroundColor: BIONIC_COLORS.gray[800] }} />
        
        {/* Habitat dominant */}
        <HabitatSection 
          habitat={habitat}
          coverage={habitatCoverage}
        />
        
        {/* Pression locale */}
        <PressureSection 
          pressureLevel={pressureLevel}
          pressureScore={pressureScore}
        />
        
        {/* Risques locaux */}
        <RiskSection 
          riskLevel={riskLevel}
          risks={risks}
        />
        
        <Separator style={{ backgroundColor: BIONIC_COLORS.gray[800] }} />
        
        {/* Facteurs positifs/négatifs */}
        <FactorsSection 
          positiveFactors={positiveFactors}
          negativeFactors={negativeFactors}
        />
        
        {/* Recommandation contextuelle */}
        {recommendation && (
          <RecommendationSection recommendation={recommendation} />
        )}
        
        {/* Bouton d'action */}
        {onAnalyze && (
          <ActionButton 
            onClick={() => onAnalyze(hotspot)}
            label="Analyser ce hotspot"
          />
        )}
      </CardContent>
    </Card>
  );
};

export default EnrichedHotspotPopup;
