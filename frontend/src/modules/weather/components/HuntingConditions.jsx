/**
 * HuntingConditions - Hunting conditions assessment widget
 * BIONIC Design System compliant
 * Version: 2.0.0 - Full BIONIC compliance (colors + i18n + Lucide icons) - Lot C Refactor
 */
import React from 'react';
import { useLanguage } from '../../../contexts/LanguageContext';
import { Target, ThumbsUp, Meh, AlertTriangle, Thermometer, Wind, BarChart3, Lightbulb, CircleDot } from 'lucide-react';

export const HuntingConditions = ({ 
  conditions = null,
  species = 'deer'
}) => {
  const { t } = useLanguage();
  
  // Handle null/undefined conditions
  const safeConditions = conditions || {};
  
  const {
    overall_score = 0,
    temperature_rating = 'N/A',
    wind_rating = 'N/A',
    pressure_rating = 'N/A',
    recommendation = ''
  } = safeConditions;

  const getScoreColor = (score) => {
    if (score >= 80) return { colorVar: 'var(--bionic-green-primary)', labelKey: 'hunting_score_excellent', Icon: Target };
    if (score >= 60) return { colorVar: 'var(--bionic-green-light)', labelKey: 'hunting_score_good', Icon: ThumbsUp };
    if (score >= 40) return { colorVar: 'var(--bionic-gold-primary)', labelKey: 'hunting_score_average', Icon: Meh };
    return { colorVar: 'var(--bionic-red-primary)', labelKey: 'hunting_score_poor', Icon: AlertTriangle };
  };

  const { colorVar, labelKey, Icon: ScoreIcon } = getScoreColor(overall_score);

  const factors = [
    { nameKey: 'hunting_factor_temperature', value: temperature_rating, Icon: Thermometer },
    { nameKey: 'hunting_factor_wind', value: wind_rating, Icon: Wind },
    { nameKey: 'hunting_factor_pressure', value: pressure_rating, Icon: BarChart3 }
  ];

  return (
    <div className="bg-[var(--bionic-bg-card)] rounded-lg p-4 border border-[var(--bionic-border-primary)]" data-testid="hunting-conditions">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-[var(--bionic-text-primary)] font-medium flex items-center gap-2">
          <CircleDot className="h-5 w-5 text-[var(--bionic-gold-primary)]" />
          {t('hunting_conditions_title')}
        </h3>
        <span className="text-xs text-[var(--bionic-text-secondary)] capitalize">{species}</span>
      </div>
      
      {/* Overall score */}
      <div className="text-center mb-4" data-testid="hunting-score">
        <div 
          className="inline-flex items-center justify-center w-20 h-20 rounded-full border-4"
          style={{ borderColor: colorVar, backgroundColor: `${colorVar}20` }}
        >
          <div className="text-center">
            <ScoreIcon className="h-6 w-6 mx-auto" style={{ color: colorVar }} />
            <div className="text-lg font-bold" style={{ color: colorVar }}>
              {overall_score}%
            </div>
          </div>
        </div>
        <p className="text-sm mt-2" style={{ color: colorVar }}>
          {t(labelKey)}
        </p>
      </div>
      
      {/* Factors */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        {factors.map(factor => (
          <div 
            key={factor.nameKey}
            className="text-center p-2 bg-[var(--bionic-gray-700)]/50 rounded-lg"
            data-testid={`factor-${factor.nameKey}`}
          >
            <factor.Icon className="h-5 w-5 mx-auto text-[var(--bionic-gold-primary)]" />
            <div className="text-xs text-[var(--bionic-text-secondary)] mt-1">{t(factor.nameKey)}</div>
            <div className="text-sm text-[var(--bionic-text-primary)] font-medium">{factor.value}</div>
          </div>
        ))}
      </div>
      
      {/* Recommendation */}
      {recommendation && (
        <div className="p-3 bg-[var(--bionic-blue-muted)] rounded-lg border border-[var(--bionic-blue-primary)]" data-testid="hunting-recommendation">
          <p className="text-sm text-[var(--bionic-blue-light)] flex items-start gap-2">
            <Lightbulb className="h-4 w-4 flex-shrink-0 mt-0.5" />
            {recommendation}
          </p>
        </div>
      )}
    </div>
  );
};

export default HuntingConditions;
