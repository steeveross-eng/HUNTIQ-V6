/**
 * Tutorial Module - Phase 11
 * 
 * Interactive tutorial and guide system.
 * Integrates with Onboarding Engine.
 * 
 * @module tutorial
 * @version 1.0.0
 */

export const MODULE_NAME = 'tutorial';
export const MODULE_VERSION = '1.0.0';
export const MODULE_TYPE = 'monetization';

// Components
export { default as TutorialProvider } from './components/TutorialProvider';
export { TutorialOverlay } from './components/TutorialOverlay';
export { TutorialStep } from './components/TutorialStep';
export { TutorialTooltip } from './components/TutorialTooltip';
export { TutorialHighlight } from './components/TutorialHighlight';
export { TutorialProgress } from './components/TutorialProgress';

// Hooks
export { useTutorial } from './hooks/useTutorial';
export { useTutorialProgress } from './hooks/useTutorialProgress';
export { useTutorialTrigger } from './hooks/useTutorialTrigger';

// Constants & Data
export { 
  TUTORIALS,
  TUTORIAL_IDS,
  TUTORIAL_TRIGGERS,
  getTutorialById,
  getTutorialsByContext
} from './data/tutorials';

export {
  STORAGE_KEYS,
  TUTORIAL_STATUS
} from './constants';
