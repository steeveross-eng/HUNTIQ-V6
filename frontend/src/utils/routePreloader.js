/**
 * Route Preloader - BRANCHE 2 (98% → 99%)
 * 
 * Précharge intelligemment les routes basé sur:
 * - Probabilité de navigation (basée sur le comportement utilisateur)
 * - Ressources disponibles (idle time, network quality)
 * - Priorité de route
 * 
 * @module routePreloader
 * @version 1.0.0
 * @phase BRANCHE_2
 */

// Map of routes to their lazy import functions
const routeImportMap = {
  '/dashboard': () => import('@/pages/DashboardPage'),
  '/shop': () => import('@/pages').then(m => m.ShopPage),
  '/compare': () => import('@/pages').then(m => m.ComparePage),
  '/map': () => import('@/pages/MapPage'),
  '/analyze': () => import('@/components/AnalyzerModule'),
  '/admin': () => import('@/pages/AdminPage'),
  '/trips': () => import('@/pages/TripsPage'),
  '/territory': () => import('@/pages/MonTerritoireBionicPage'),
  '/pricing': () => import('@/pages/PricingPage'),
};

// Navigation probability based on current route
const navigationProbability = {
  '/': ['/dashboard', '/shop', '/analyze'],
  '/dashboard': ['/map', '/territory', '/trips'],
  '/shop': ['/compare', '/dashboard'],
  '/map': ['/territory', '/dashboard'],
  '/analyze': ['/shop', '/compare'],
};

// Cache of preloaded routes
const preloadedRoutes = new Set();

/**
 * Check if we should preload based on network conditions
 */
const shouldPreload = () => {
  if (typeof navigator === 'undefined') return false;
  
  // Don't preload on slow connections or data saver mode
  const connection = navigator.connection;
  if (connection) {
    if (connection.saveData) return false;
    if (connection.effectiveType === '2g' || connection.effectiveType === 'slow-2g') return false;
  }
  
  return true;
};

/**
 * Preload a single route
 */
const preloadRoute = async (route) => {
  if (preloadedRoutes.has(route)) return;
  if (!routeImportMap[route]) return;
  
  try {
    await routeImportMap[route]();
    preloadedRoutes.add(route);
    
    if (process.env.NODE_ENV === 'development') {
      console.log(`[RoutePreloader] Preloaded: ${route}`);
    }
  } catch (error) {
    // Silently fail - preloading is an optimization, not critical
    if (process.env.NODE_ENV === 'development') {
      console.warn(`[RoutePreloader] Failed to preload: ${route}`, error);
    }
  }
};

/**
 * Preload routes based on current location
 */
export const preloadProbableRoutes = (currentPath) => {
  if (!shouldPreload()) return;
  
  // Get probable next routes
  const probableRoutes = navigationProbability[currentPath] || [];
  
  // Use requestIdleCallback to preload during idle time
  if ('requestIdleCallback' in window) {
    probableRoutes.forEach((route, index) => {
      requestIdleCallback(
        () => preloadRoute(route),
        { timeout: 2000 + (index * 500) }
      );
    });
  } else {
    // Fallback for Safari
    probableRoutes.forEach((route, index) => {
      setTimeout(() => preloadRoute(route), 1000 + (index * 500));
    });
  }
};

/**
 * Preload on hover/focus (intent-based preloading)
 */
export const preloadOnIntent = (route) => {
  if (!shouldPreload()) return;
  if (!routeImportMap[route]) return;
  
  preloadRoute(route);
};

/**
 * Preload all critical routes (called after initial render)
 */
export const preloadCriticalRoutes = () => {
  if (!shouldPreload()) return;
  
  const criticalRoutes = ['/dashboard', '/shop'];
  
  // Defer to after initial render
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      criticalRoutes.forEach(route => preloadRoute(route));
    }, { timeout: 3000 });
  } else {
    setTimeout(() => {
      criticalRoutes.forEach(route => preloadRoute(route));
    }, 2000);
  }
};

/**
 * Get list of preloaded routes (for debugging)
 */
export const getPreloadedRoutes = () => {
  return Array.from(preloadedRoutes);
};

/**
 * Clear preload cache (for testing)
 */
export const clearPreloadCache = () => {
  preloadedRoutes.clear();
};

export default {
  preloadProbableRoutes,
  preloadOnIntent,
  preloadCriticalRoutes,
  getPreloadedRoutes,
  clearPreloadCache
};
