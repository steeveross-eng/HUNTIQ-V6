/**
 * ObjectivesSelector - Phase 10
 * 
 * Hunting objectives selection step (multi-select).
 */

import React from 'react';
import { Target } from 'lucide-react';
import { OnboardingStep } from './OnboardingStep';
import { ProfileSelector } from './ProfileSelector';
import { HUNTING_OBJECTIVES } from '../constants';

export const ObjectivesSelector = ({
  selected = [],
  onSelect,
  onNext,
  onBack
}) => {
  return (
    <OnboardingStep
      title="Vos objectifs de chasse"
      subtitle="Sélectionnez un ou plusieurs objectifs"
      icon={Target}
      onNext={onNext}
      onBack={onBack}
      canGoNext={selected.length > 0}
      canGoBack={true}
      nextLabel="Terminer"
    >
      <ProfileSelector
        options={HUNTING_OBJECTIVES}
        selected={selected}
        onSelect={onSelect}
        multiSelect={true}
        columns={2}
      />
      
      {/* Selection count */}
      <div className="text-center text-sm text-gray-500 mt-4">
        {selected.length === 0 
          ? 'Sélectionnez au moins un objectif'
          : `${selected.length} objectif${selected.length > 1 ? 's' : ''} sélectionné${selected.length > 1 ? 's' : ''}`
        }
      </div>
    </OnboardingStep>
  );
};

export default ObjectivesSelector;
