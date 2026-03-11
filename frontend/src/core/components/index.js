/**
 * Core Components - BIONIC™ V5
 * =============================
 * 
 * Barrel export for all core components.
 * These are generic, reusable components with NO business logic.
 * 
 * @module core/components
 */

// UI Feedback
export { OfflineIndicator } from './OfflineIndicator';
export { CookieConsent } from './CookieConsent';
export { RefreshButton } from './RefreshButton';
export { 
  LoadingSpinner, 
  LoadingSkeleton, 
  CardSkeleton, 
  TableSkeleton 
} from './LoadingSpinner';
export { 
  EmptyState, 
  NoResults, 
  ErrorState 
} from './EmptyState';
export { 
  ConfirmDialog, 
  useConfirmDialog 
} from './ConfirmDialog';

// Navigation
export { BackButton, PageHeaderWithBack } from './BackButton';
export { default as ScrollNavigator } from './ScrollNavigator';

// Branding
export { default as BionicLogo } from './BionicLogo';

// SEO
export { default as SEOHead } from './SEOHead';
