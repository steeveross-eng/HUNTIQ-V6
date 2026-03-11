/**
 * SeasonalFactorsPanel - Panneau des Facteurs Saisonniers PHASE C
 * ================================================================
 * BIONIC V5 — PHASE C Frontend Integration
 * 
 * Affiche l'état des 4 modules saisonniers:
 * - C.1 Mise bas / Calving
 * - C.2 Dispersion juvénile
 * - C.3 Stress thermique
 * - C.4 Pression de chasse réelle
 * 
 * Composant 100% présentationnel.
 * Données via props (analysisData.scores.advanced_factors_details)
 * 
 * VERSION: 1.0.0
 * Conformité: BIONIC V5 PHASE C
 */

import React, { useMemo } from 'react';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  Baby,
  Footprints,
  Thermometer,
  Target,
  AlertTriangle,
  CheckCircle,
  XCircle,
  TrendingDown,
  TrendingUp,
  Activity
} from 'lucide-react';
import { BIONIC_COLORS } from '@/config/bionic-colors';

// Configuration des facteurs saisonniers PHASE C
const SEASONAL_FACTORS_CONFIG = {
  calving: {
    id: 'calving',
    label: 'Mise bas',
    code: 'C.1',
    icon: Baby,
    color: '#EC4899',
    activeColor: '#EC4899',
    description: 'Période de mise bas active',
    inactiveDescription: 'Hors période de mise bas'
  },
  dispersal_juvenile: {
    id: 'dispersal_juvenile',
    label: 'Dispersion juvénile',
    code: 'C.2',
    icon: Footprints,
    color: '#8B5CF6',
    activeColor: '#8B5CF6',
    description: 'Dispersion juvénile détectée',
    inactiveDescription: 'Aucune dispersion juvénile'
  },
  thermal_stress: {
    id: 'thermal_stress',
    label: 'Stress thermique',
    code: 'C.3',
    icon: Thermometer,
    color: '#EF4444',
    activeColor: '#EF4444',
    description: 'Stress thermique actif',
    inactiveDescription: 'Confort thermique normal'
  },
  hunting_pressure: {
    id: 'hunting_pressure',
    label: 'Pression de chasse',
    code: 'C.4',
    icon: Target,
    color: '#F59E0B',
    activeColor: '#F59E0B',
    description: 'Pression de chasse détectée',
    inactiveDescription: 'Aucune pression détectée'
  }
};

/**
 * Indicateur individuel pour un facteur saisonnier
 */
const FactorIndicator = ({ config, isActive, modifier, details }) => {
  const Icon = config.icon;
  const modifierPercent = modifier ? Math.round((1 - modifier) * 100) : 0;
  const hasImpact = modifier && modifier !== 1.0;

  return (
    <div
      className={`flex items-center gap-2.5 p-2 rounded-lg transition-all duration-200 ${
        isActive
          ? 'bg-white/5 border border-white/10'
          : 'bg-transparent opacity-60'
      }`}
      data-testid={`seasonal-factor-${config.id}`}
    >
      {/* Icone avec indicateur de statut */}
      <div
        className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 relative"
        style={{ backgroundColor: `${config.color}20` }}
      >
        <Icon
          className="w-4 h-4"
          style={{ color: isActive ? config.activeColor : BIONIC_COLORS.gray[500] }}
        />
        {/* Dot d'activité */}
        <div
          className={`absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border border-black ${
            isActive ? 'animate-pulse' : ''
          }`}
          style={{ backgroundColor: isActive ? config.activeColor : BIONIC_COLORS.gray[600] }}
        />
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5">
          <span className="text-[10px] font-mono text-gray-500">{config.code}</span>
          <span className={`text-xs font-medium truncate ${isActive ? 'text-white' : 'text-gray-500'}`}>
            {config.label}
          </span>
        </div>
        <span className="text-[10px] text-gray-500 block truncate">
          {isActive ? config.description : config.inactiveDescription}
        </span>
      </div>

      {/* Modificateur */}
      <div className="flex items-center gap-1 flex-shrink-0">
        {isActive && hasImpact ? (
          <Badge
            className="text-[10px] px-1.5 py-0 font-mono"
            style={{
              backgroundColor: `${config.activeColor}20`,
              color: config.activeColor,
              border: `1px solid ${config.activeColor}40`
            }}
          >
            {modifierPercent > 0 ? (
              <><TrendingDown className="w-2.5 h-2.5 mr-0.5" />-{modifierPercent}%</>
            ) : (
              <><TrendingUp className="w-2.5 h-2.5 mr-0.5" />+{Math.abs(modifierPercent)}%</>
            )}
          </Badge>
        ) : isActive ? (
          <CheckCircle className="w-3.5 h-3.5" style={{ color: config.activeColor }} />
        ) : (
          <XCircle className="w-3.5 h-3.5 text-gray-600" />
        )}
      </div>
    </div>
  );
};

/**
 * SeasonalFactorsPanel
 * 
 * Panneau affichant l'état des facteurs saisonniers PHASE C
 * à partir des données de l'API d'analyse.
 * 
 * @param {Object} analysisData - Réponse complète de l'API /analyze_waypoint
 * @param {boolean} compact - Mode compact (moins d'espacement)
 * @param {string} className - Classes CSS additionnelles
 */
const SeasonalFactorsPanel = ({ analysisData, compact = false, className = '' }) => {
  // Extraire les facteurs depuis la réponse API
  const factors = useMemo(() => {
    const details = analysisData?.scores?.advanced_factors_details?.factors || {};
    const phaseC = analysisData?.scores?.advanced_factors_details?.phase_c_modifier;

    return {
      calving: {
        active: false, // Calving n'a pas de champ direct dans la réponse mais est intégré dans le modèle saisonnier
        modifier: 1.0
      },
      dispersal_juvenile: {
        active: details?.dispersal_juvenile?.active || false,
        modifier: details?.dispersal_juvenile?.modifier || 1.0,
        details: details?.dispersal_juvenile
      },
      thermal_stress: {
        active: details?.thermal_stress?.active || false,
        modifier: details?.thermal_stress?.modifier || 1.0,
        details: details?.thermal_stress
      },
      hunting_pressure: {
        active: details?.hunting_pressure?.active || false,
        modifier: details?.hunting_pressure?.modifier || 1.0,
        details: details?.hunting_pressure?.details
      },
      phaseCModifier: phaseC || 1.0
    };
  }, [analysisData]);

  // Compter les facteurs actifs
  const activeCount = useMemo(() => {
    let count = 0;
    if (factors.calving.active) count++;
    if (factors.dispersal_juvenile.active) count++;
    if (factors.thermal_stress.active) count++;
    if (factors.hunting_pressure.active) count++;
    return count;
  }, [factors]);

  // Modificateur combiné Phase C
  const phaseCModifier = factors.phaseCModifier;
  const phaseCImpact = Math.round((1 - phaseCModifier) * 100);

  return (
    <div className={`space-y-2 ${className}`} data-testid="seasonal-factors-panel">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-[#f5a623]" />
          <span className="text-xs font-semibold text-white">Facteurs Saisonniers</span>
          <Badge
            variant="outline"
            className="text-[10px] px-1.5 py-0"
            style={{
              borderColor: activeCount > 0 ? '#f5a623' : BIONIC_COLORS.gray[600],
              color: activeCount > 0 ? '#f5a623' : BIONIC_COLORS.gray[500]
            }}
          >
            {activeCount}/4 actifs
          </Badge>
        </div>
      </div>

      {/* Facteurs individuels */}
      <div className={`space-y-1 ${compact ? '' : 'space-y-1.5'}`}>
        {Object.entries(SEASONAL_FACTORS_CONFIG).map(([key, config]) => (
          <FactorIndicator
            key={key}
            config={config}
            isActive={factors[key]?.active || false}
            modifier={factors[key]?.modifier}
            details={factors[key]?.details}
          />
        ))}
      </div>

      {/* Impact combiné PHASE C */}
      {phaseCModifier !== 1.0 && (
        <>
          <Separator style={{ backgroundColor: BIONIC_COLORS.gray[700] }} />
          <div
            className="flex items-center justify-between p-2 rounded-lg"
            style={{ backgroundColor: `${BIONIC_COLORS.gold.primary}10` }}
            data-testid="phase-c-combined-impact"
          >
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-3.5 h-3.5 text-[#f5a623]" />
              <span className="text-xs text-gray-300">Impact PHASE C combiné</span>
            </div>
            <Badge
              className="text-xs font-mono"
              style={{
                backgroundColor: phaseCImpact > 0 ? '#EF444420' : '#22C55E20',
                color: phaseCImpact > 0 ? '#EF4444' : '#22C55E',
                border: `1px solid ${phaseCImpact > 0 ? '#EF444440' : '#22C55E40'}`
              }}
            >
              {phaseCImpact > 0 ? `-${phaseCImpact}%` : phaseCImpact < 0 ? `+${Math.abs(phaseCImpact)}%` : '0%'}
            </Badge>
          </div>
        </>
      )}

      {/* Message si aucune donnée */}
      {!analysisData && (
        <div className="text-center py-2">
          <span className="text-[10px] text-gray-500">
            Lancez une analyse pour voir les facteurs saisonniers
          </span>
        </div>
      )}
    </div>
  );
};

export default SeasonalFactorsPanel;
export { SEASONAL_FACTORS_CONFIG };
