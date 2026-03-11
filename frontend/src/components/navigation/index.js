/**
 * Navigation Components - Phase 7-8
 * 
 * Centralized navigation exports.
 * 
 * @version 2.0.0
 */

export { default as ModularNavigation } from './ModularNavigation';

// Re-export route configuration
export { 
  ROUTES, 
  NAV_GROUPS, 
  ROUTE_CATEGORIES,
  getVisibleRoutes,
  getRoutesByCategory,
  getStandaloneRoutes,
  hasRouteAccess
} from '@/config/routes';
