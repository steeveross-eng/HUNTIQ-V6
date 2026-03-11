/**
 * OpportunityList - List of investment opportunities
 * BIONIC Design System compliant
 * Phase 11-15: Module Immobilier
 */
import React from 'react';
import { ScrollArea } from '../../../components/ui/scroll-area';
import OpportunityCard from './OpportunityCard';
import { TrendingUp, Loader2 } from 'lucide-react';

/**
 * Opportunity List Component
 * 
 * @param {Object} props
 * @param {Array} props.opportunities - Array of opportunity objects
 * @param {boolean} props.loading - Loading state
 * @param {Function} props.onSelect - Selection callback
 */
const OpportunityList = ({ 
  opportunities = [],
  loading = false,
  onSelect = null
}) => {
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Loader2 className="w-8 h-8 text-[var(--bionic-gold-primary)] animate-spin mb-3" />
        <p className="text-[var(--bionic-text-muted)] text-sm">Analyse en cours...</p>
      </div>
    );
  }

  if (opportunities.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <TrendingUp className="w-12 h-12 text-[var(--bionic-text-muted)] mb-3 opacity-50" />
        <p className="text-[var(--bionic-text-secondary)]">Aucune opportunité trouvée</p>
        <p className="text-[var(--bionic-text-muted)] text-sm mt-1">
          Ajustez vos filtres ou élargissez votre recherche
        </p>
      </div>
    );
  }

  return (
    <ScrollArea className="h-[500px]">
      <div className="space-y-3 pr-3">
        {opportunities.map((opportunity, index) => (
          <OpportunityCard
            key={opportunity.property_id || index}
            opportunity={opportunity}
            onClick={() => onSelect?.(opportunity)}
            rank={index + 1}
          />
        ))}
      </div>
    </ScrollArea>
  );
};

export default OpportunityList;
