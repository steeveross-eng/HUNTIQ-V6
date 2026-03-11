/**
 * TerritorySelector - Phase 10
 * 
 * Territory type selection step.
 */

import React from 'react';
import { Map } from 'lucide-react';
import { OnboardingStep } from './OnboardingStep';
import { ProfileSelector } from './ProfileSelector';
import { TERRITORY_TYPES } from '../constants';

export const TerritorySelector = ({
  selected,
  onSelect,
  onNext,
  onBack
}) => {
  return (
    <OnboardingStep
      title="Votre territoire de chasse"
      subtitle="Quel type de territoire chassez-vous principalement?"
      icon={Map}
      onNext={onNext}
      onBack={onBack}
      canGoNext={selected !== null}
      canGoBack={true}
    >
      <ProfileSelector
        options={TERRITORY_TYPES}
        selected={selected}
        onSelect={onSelect}
        multiSelect={false}
        columns={2}
      />
    </OnboardingStep>
  );
};

export default TerritorySelector;
