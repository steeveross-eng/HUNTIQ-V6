/**
 * Tutorial Constants - Phase 11
 * 
 * Configuration constants for tutorial system.
 */

// ============================================
// STORAGE KEYS
// ============================================

export const STORAGE_KEYS = {
  TUTORIAL_PROGRESS: 'huntiq_tutorial_progress',
  TUTORIAL_DISMISSED: 'huntiq_tutorial_dismissed',
  TUTORIAL_COMPLETED: 'huntiq_tutorial_completed',
  LAST_TUTORIAL: 'huntiq_last_tutorial'
};

// ============================================
// TUTORIAL STATUS
// ============================================

export const TUTORIAL_STATUS = {
  NOT_STARTED: 'not_started',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  SKIPPED: 'skipped',
  DISMISSED: 'dismissed'
};

// ============================================
// TUTORIAL POSITIONS
// ============================================

export const TOOLTIP_POSITIONS = {
  TOP: 'top',
  BOTTOM: 'bottom',
  LEFT: 'left',
  RIGHT: 'right',
  TOP_LEFT: 'top-left',
  TOP_RIGHT: 'top-right',
  BOTTOM_LEFT: 'bottom-left',
  BOTTOM_RIGHT: 'bottom-right',
  CENTER: 'center'
};

// ============================================
// TRIGGER CONDITIONS
// ============================================

export const TRIGGER_CONDITIONS = {
  ON_PAGE_LOAD: 'on_page_load',
  ON_FIRST_VISIT: 'on_first_visit',
  ON_FEATURE_USE: 'on_feature_use',
  ON_ONBOARDING_COMPLETE: 'on_onboarding_complete',
  MANUAL: 'manual'
};

// ============================================
// TUTORIAL CONTEXTS
// ============================================

export const TUTORIAL_CONTEXTS = {
  DASHBOARD: 'dashboard',
  MAP: 'map',
  TERRITORY: 'territory',
  ANALYTICS: 'analytics',
  SHOP: 'shop',
  PLAN_MAITRE: 'plan_maitre',
  GLOBAL: 'global'
};
