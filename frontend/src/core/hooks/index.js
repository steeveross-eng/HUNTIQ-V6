/**
 * Core Hooks - BIONIC™ V5
 * ========================
 * 
 * Barrel export for all core hooks.
 * These are generic, reusable hooks with NO business logic.
 * 
 * @module core/hooks
 */

// Toast (from Shadcn)
export { useToast, toast } from './useToast';

// State management
export { useLocalStorage } from './useLocalStorage';

// Performance
export { 
  useDebounce, 
  useDebouncedCallback, 
  useThrottle 
} from './useDebounce';

// Responsive
export { 
  useMediaQuery, 
  useBreakpoint, 
  useIsMobile, 
  useIsDesktop,
  usePrefersDarkMode,
  usePrefersReducedMotion
} from './useMediaQuery';
