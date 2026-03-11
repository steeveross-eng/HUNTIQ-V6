/**
 * Onboarding Module - Phase 10
 * 
 * User onboarding and profiling engine.
 * Integrates with modular navigation.
 * 
 * @module onboarding
 * @version 1.0.0
 */

export const MODULE_NAME = 'onboarding';
export const MODULE_VERSION = '1.0.0';
export const MODULE_TYPE = 'monetization';

// Components
export { default as OnboardingFlow } from './components/OnboardingFlow';
export { OnboardingStep } from './components/OnboardingStep';
export { ProfileSelector } from './components/ProfileSelector';
export { TerritorySelector } from './components/TerritorySelector';
export { ExperienceSelector } from './components/ExperienceSelector';
export { ObjectivesSelector } from './components/ObjectivesSelector';

// Hooks
export { useOnboarding } from './hooks/useOnboarding';
export { useUserProfile } from './hooks/useUserProfile';

// Constants
export { 
  ONBOARDING_STEPS,
  EXPERIENCE_LEVELS,
  HUNTING_OBJECTIVES,
  TERRITORY_TYPES
} from './constants';
