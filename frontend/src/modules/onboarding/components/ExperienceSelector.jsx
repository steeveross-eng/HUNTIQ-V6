/**
 * ExperienceSelector - Phase 10
 * 
 * Experience level selection step.
 */

import React from 'react';
import { Award } from 'lucide-react';
import { OnboardingStep } from './OnboardingStep';
import { ProfileSelector } from './ProfileSelector';
import { EXPERIENCE_LEVELS } from '../constants';

export const ExperienceSelector = ({
  selected,
  onSelect,
  onNext,
  onBack
}) => {
  return (
    <OnboardingStep
      title="Votre niveau d'expérience"
      subtitle="Depuis combien de temps chassez-vous?"
      icon={Award}
      onNext={onNext}
      onBack={onBack}
      canGoNext={selected !== null}
      canGoBack={true}
    >
      <ProfileSelector
        options={EXPERIENCE_LEVELS}
        selected={selected}
        onSelect={onSelect}
        multiSelect={false}
        columns={2}
      />
    </OnboardingStep>
  );
};

export default ExperienceSelector;
