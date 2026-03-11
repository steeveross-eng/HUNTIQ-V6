/**
 * OpportunityCard - Investment opportunity display card
 * BIONIC Design System compliant
 * Phase 11-15: Module Immobilier
 */
import React from 'react';
import { Card, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { 
  TrendingUp, TrendingDown, DollarSign, Target, ArrowRight, Award 
} from 'lucide-react';

const OPPORTUNITY_LEVELS = {
  excellent: {
    label: 'Excellent',
    className: 'bg-green-900/50 text-green-400 border-green-700',
    Icon: Award
  },
  very_good: {
    label: 'Très Bon',
    className: 'bg-emerald-900/50 text-emerald-400 border-emerald-700',
    Icon: TrendingUp
  },
  good: {
    label: 'Bon',
    className: 'bg-blue-900/50 text-blue-400 border-blue-700',
    Icon: TrendingUp
  },
  average: {
    label: 'Moyen',
    className: 'bg-amber-900/50 text-amber-400 border-amber-700',
    Icon: Target
  },
  below_average: {
    label: 'Sous la moyenne',
    className: 'bg-red-900/50 text-red-400 border-red-700',
    Icon: TrendingDown
  }
};

/**
 * Opportunity Card Component
 * 
 * @param {Object} props
 * @param {Object} props.opportunity - Opportunity data
 * @param {Function} props.onClick - Click handler
 * @param {number} props.rank - Opportunity ranking
 */
const OpportunityCard = ({ 
  opportunity = {},
  onClick = null,
  rank = null
}) => {
  const {
    property_title = 'Propriété',
    opportunity_level = 'average',
    price_per_m2 = 0,
    market_average_per_m2 = 0,
    bionic_score = 0,
    discount_percentage = 0,
    investment_potential = 'Moyen',
    recommended_actions = []
  } = opportunity;

  const levelConfig = OPPORTUNITY_LEVELS[opportunity_level] || OPPORTUNITY_LEVELS.average;
  const LevelIcon = levelConfig.Icon;

  return (
    <Card 
      className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)] cursor-pointer hover:border-[var(--bionic-gold-primary)] transition-colors"
      onClick={onClick}
    >
      <CardContent className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            {rank && (
              <span className="w-6 h-6 rounded-full bg-[var(--bionic-gold-muted)] text-[var(--bionic-gold-primary)] text-xs font-bold flex items-center justify-center">
                {rank}
              </span>
            )}
            <div>
              <h3 className="text-[var(--bionic-text-primary)] font-medium line-clamp-1">
                {property_title}
              </h3>
              <Badge className={`${levelConfig.className} border text-xs mt-1`}>
                <LevelIcon className="w-3 h-3 mr-1" />
                {levelConfig.label}
              </Badge>
            </div>
          </div>
          <div className="text-right">
            <span className={`text-lg font-bold ${bionic_score >= 70 ? 'text-[var(--bionic-green-primary)]' : 'text-[var(--bionic-gold-primary)]'}`}>
              {bionic_score}
            </span>
            <p className="text-[10px] text-[var(--bionic-text-muted)]">BIONIC Score</p>
          </div>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-3 gap-3 mb-3">
          <div className="text-center p-2 bg-[var(--bionic-bg-hover)] rounded">
            <DollarSign className="w-4 h-4 mx-auto text-[var(--bionic-text-muted)] mb-1" />
            <p className="text-xs text-[var(--bionic-text-primary)] font-medium">
              {price_per_m2.toFixed(2)}$/m²
            </p>
            <p className="text-[10px] text-[var(--bionic-text-muted)]">Prix</p>
          </div>
          <div className="text-center p-2 bg-[var(--bionic-bg-hover)] rounded">
            <Target className="w-4 h-4 mx-auto text-[var(--bionic-text-muted)] mb-1" />
            <p className="text-xs text-[var(--bionic-text-primary)] font-medium">
              {market_average_per_m2.toFixed(2)}$/m²
            </p>
            <p className="text-[10px] text-[var(--bionic-text-muted)]">Marché</p>
          </div>
          <div className="text-center p-2 bg-[var(--bionic-bg-hover)] rounded">
            {discount_percentage > 0 ? (
              <TrendingDown className="w-4 h-4 mx-auto text-[var(--bionic-green-primary)] mb-1" />
            ) : (
              <TrendingUp className="w-4 h-4 mx-auto text-[var(--bionic-red-primary)] mb-1" />
            )}
            <p className={`text-xs font-medium ${discount_percentage > 0 ? 'text-[var(--bionic-green-primary)]' : 'text-[var(--bionic-red-primary)]'}`}>
              {discount_percentage > 0 ? '-' : '+'}{Math.abs(discount_percentage).toFixed(1)}%
            </p>
            <p className="text-[10px] text-[var(--bionic-text-muted)]">Écart</p>
          </div>
        </div>

        {/* Investment Potential */}
        <div className="flex items-center justify-between p-2 bg-[var(--bionic-bg-hover)] rounded">
          <span className="text-xs text-[var(--bionic-text-muted)]">Potentiel d'investissement</span>
          <span className="text-xs font-medium text-[var(--bionic-gold-primary)]">
            {investment_potential}
          </span>
        </div>

        {/* Recommendations Preview */}
        {recommended_actions.length > 0 && (
          <div className="mt-3 pt-3 border-t border-[var(--bionic-border-secondary)]">
            <p className="text-[10px] text-[var(--bionic-text-muted)] mb-1">Recommandation:</p>
            <p className="text-xs text-[var(--bionic-text-secondary)] flex items-center gap-1">
              <ArrowRight className="w-3 h-3 text-[var(--bionic-gold-primary)]" />
              {recommended_actions[0]}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default OpportunityCard;
