/**
 * OptimalWindowsTimeline - Timeline des Fenêtres Optimales
 * =========================================================
 * BIONIC V5 ULTIME - PHASE 5.3
 * 
 * RESPONSABILITÉ UNIQUE:
 * - Afficher les fenêtres temporelles optimales de chasse
 * - Timeline visuelle avec indicateurs de qualité
 * - Respect des heures légales
 * 
 * DESIGN:
 * - Timeline horizontale épurée
 * - Cartes de période avec notation sur 10
 * - Indicateurs légaux clairs
 * - Style scientifique premium
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
  Clock,
  Sunrise,
  Sun,
  Sunset,
  Moon,
  CheckCircle,
  Scale
} from 'lucide-react';

import { BIONIC_COLORS } from '@/config/bionic-colors';

// =============================================================================
// CONSTANTS
// =============================================================================

const PERIOD_CONFIG = {
  dawn: { 
    icon: Sunrise, 
    label: 'Aube',
    color: '#F5A623',
    gradient: 'linear-gradient(135deg, #F5A623 0%, #E8952F 100%)'
  },
  morning: { 
    icon: Sun, 
    label: 'Matin',
    color: '#3B82F6',
    gradient: 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)'
  },
  afternoon: { 
    icon: Sun, 
    label: 'Après-midi',
    color: '#6B7280',
    gradient: 'linear-gradient(135deg, #6B7280 0%, #4B5563 100%)'
  },
  dusk: { 
    icon: Sunset, 
    label: 'Crépuscule',
    color: '#F97316',
    gradient: 'linear-gradient(135deg, #F97316 0%, #EA580C 100%)'
  },
  night: { 
    icon: Moon, 
    label: 'Nuit',
    color: '#EF4444',
    gradient: 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)'
  }
};

const QUALITY_LABELS = {
  excellent: { label: 'IDÉAL', color: BIONIC_COLORS.green.primary },
  good: { label: 'BON', color: BIONIC_COLORS.gold.primary },
  moderate: { label: 'MODÉRÉ', color: BIONIC_COLORS.blue.light },
  poor: { label: 'FAIBLE', color: '#F97316' }
};

// =============================================================================
// SUB-COMPONENTS
// =============================================================================

/**
 * Barre de progression temporelle
 */
const TimeProgressBar = ({ legalStart, legalEnd, windows }) => {
  return (
    <div className="relative">
      {/* Barre de fond (24h) */}
      <div 
        className="h-2 rounded-full w-full"
        style={{ backgroundColor: BIONIC_COLORS.gray[800] }}
      />
      
      {/* Zone légale */}
      <div 
        className="absolute top-0 h-2 rounded-full"
        style={{ 
          left: '20%',
          width: '60%',
          background: `linear-gradient(90deg, ${BIONIC_COLORS.green.muted} 0%, ${BIONIC_COLORS.green.primary}40 50%, ${BIONIC_COLORS.green.muted} 100%)`
        }}
      />
      
      {/* Marqueurs de temps */}
      <div className="flex justify-between mt-2">
        <span className="text-xs text-gray-500">00:00</span>
        <span className="text-xs font-medium" style={{ color: BIONIC_COLORS.green.primary }}>
          {legalStart}
        </span>
        <span className="text-xs text-gray-400">12:00</span>
        <span className="text-xs font-medium" style={{ color: BIONIC_COLORS.green.primary }}>
          {legalEnd}
        </span>
        <span className="text-xs text-gray-500">24:00</span>
      </div>
    </div>
  );
};

/**
 * Carte de période optimale
 */
const PeriodCard = ({ period, startTime, endTime, quality, score, isLegal }) => {
  const config = PERIOD_CONFIG[period] || PERIOD_CONFIG.morning;
  const qualityConfig = QUALITY_LABELS[quality] || QUALITY_LABELS.moderate;
  const Icon = config.icon;
  
  // Score sur 10
  const score10 = Math.round((score || 50) / 10);
  
  return (
    <div 
      className="flex-1 min-w-0 p-3 rounded-lg relative overflow-hidden"
      style={{ backgroundColor: BIONIC_COLORS.gray[900] }}
    >
      {/* Barre de couleur en haut */}
      <div 
        className="absolute top-0 left-0 right-0 h-1"
        style={{ background: config.gradient }}
      />
      
      {/* Contenu */}
      <div className="pt-1">
        {/* Header avec icône */}
        <div className="flex items-center gap-2 mb-2">
          <Icon className="w-4 h-4" style={{ color: config.color }} />
          <span className="text-sm font-medium text-white">{config.label}</span>
        </div>
        
        {/* Horaires */}
        <div className="flex items-baseline gap-1 mb-2">
          <span className="text-lg font-bold text-white">{startTime}</span>
          <span className="text-xs text-gray-500">-</span>
          <span className="text-sm text-gray-400">{endTime}</span>
        </div>
        
        {/* Score et qualité */}
        <div className="flex items-center justify-between">
          <span 
            className="text-xs font-semibold uppercase px-2 py-0.5 rounded"
            style={{ 
              backgroundColor: `${qualityConfig.color}20`,
              color: qualityConfig.color
            }}
          >
            {qualityConfig.label}
          </span>
          
          <div className="flex items-center gap-1">
            <span 
              className="text-sm font-bold"
              style={{ color: qualityConfig.color }}
            >
              {score10}
            </span>
            <span className="text-xs text-gray-500">/10</span>
          </div>
        </div>
        
        {/* Badge légal */}
        {isLegal && (
          <div className="flex items-center gap-1 mt-2">
            <CheckCircle className="w-3 h-3" style={{ color: BIONIC_COLORS.green.primary }} />
            <span className="text-xs" style={{ color: BIONIC_COLORS.green.primary }}>
              Légal
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Info légale
 */
const LegalInfo = ({ legalStart, legalEnd, duration }) => (
  <div 
    className="flex items-center justify-between p-3 rounded-lg"
    style={{ backgroundColor: `${BIONIC_COLORS.green.primary}10` }}
  >
    <div className="flex items-center gap-2">
      <Scale className="w-4 h-4" style={{ color: BIONIC_COLORS.green.primary }} />
      <span className="text-sm text-gray-300">Heures légales</span>
    </div>
    
    <div className="flex items-center gap-3">
      <span className="text-sm font-medium text-white">
        {legalStart} - {legalEnd}
      </span>
      <span 
        className="text-xs px-2 py-0.5 rounded"
        style={{ 
          backgroundColor: BIONIC_COLORS.green.muted,
          color: BIONIC_COLORS.green.primary
        }}
      >
        {duration}
      </span>
    </div>
  </div>
);

// =============================================================================
// MAIN COMPONENT
// =============================================================================

/**
 * OptimalWindowsTimeline
 * 
 * Timeline des fenêtres optimales de chasse.
 * Affichage premium avec cartes de période et indicateurs légaux.
 * 
 * @param {Array} windows - Liste des fenêtres [{period, start, end, quality, score, isLegal}]
 * @param {string} legalStart - Heure de début légale (HH:MM)
 * @param {string} legalEnd - Heure de fin légale (HH:MM)
 * @param {string} legalDuration - Durée formatée (ex: "16h06")
 * @param {string} className - Classes CSS additionnelles
 */
const OptimalWindowsTimeline = ({
  windows = [],
  legalStart = '05:12',
  legalEnd = '21:18',
  legalDuration = '16h06',
  className = ''
}) => {
  return (
    <Card 
      className={`border-0 overflow-hidden ${className}`}
      style={{ backgroundColor: BIONIC_COLORS.black.elevated }}
    >
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-white text-base">
          <Clock className="w-5 h-5" style={{ color: BIONIC_COLORS.gold.primary }} />
          Fenêtres Optimales
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Info légale */}
        <LegalInfo 
          legalStart={legalStart}
          legalEnd={legalEnd}
          duration={legalDuration}
        />
        
        {/* Barre de progression */}
        <TimeProgressBar 
          legalStart={legalStart}
          legalEnd={legalEnd}
          windows={windows}
        />
        
        {/* Cartes de périodes */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {windows.map((window, index) => (
            <PeriodCard
              key={index}
              period={window.period}
              startTime={window.start_time || window.start}
              endTime={window.end_time || window.end}
              quality={window.quality}
              score={window.score || window.score_modifier * 100}
              isLegal={window.is_legal !== false}
            />
          ))}
        </div>
        
        {/* Message si aucune fenêtre */}
        {windows.length === 0 && (
          <div className="text-center py-6">
            <Clock className="w-8 h-8 mx-auto mb-2" style={{ color: BIONIC_COLORS.gray[600] }} />
            <p className="text-sm text-gray-400">
              Aucune fenêtre optimale disponible
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default OptimalWindowsTimeline;
