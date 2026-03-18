/**
 * BIONIC HUNT/Chasse V3 - Route Configuration
 * Phase 7-8: Frontend Modular Architecture
 * 
 * Centralized route configuration for modular navigation.
 * Each route is associated with a module for lazy loading.
 * 
 * @version 2.0.0
 */

import { lazy } from 'react';
import {
  Home, BarChart3, Brain, TrendingUp, Target, Radar, Map, Globe,
  Crosshair, FlaskConical, Store, Briefcase, Route as RouteIcon,
  Settings, Users, Gift, Compass, Camera
} from 'lucide-react';

// Lazy load pages for code splitting
const HomePage = lazy(() => import('@/pages/HomePage'));
const DashboardPage = lazy(() => import('@/pages/DashboardPage'));
const AnalyticsPage = lazy(() => import('@/pages/intelligence/AnalyticsPage'));
const ForecastPage = lazy(() => import('@/pages/intelligence/ForecastPage'));
const PlanMaitrePage = lazy(() => import('@/pages/intelligence/PlanMaitrePage'));
const MapPage = lazy(() => import('@/pages/MapPage'));
const MonTerritoireBionicPage = lazy(() => import('@/pages/MonTerritoireBionicPage'));
const TripsPage = lazy(() => import('@/pages/TripsPage'));
const ShopPage = lazy(() => import('@/pages/ShopPage'));
const ComparePage = lazy(() => import('@/pages/ComparePage'));
const BusinessPage = lazy(() => import('@/pages/BusinessPage'));
const AdminPage = lazy(() => import('@/pages/AdminPage'));
const AdminGeoPage = lazy(() => import('@/pages/AdminGeoPage'));

// ============================================
// ROUTE CATEGORIES
// ============================================

export const ROUTE_CATEGORIES = {
  CORE: 'core',           // Essential routes (always visible)
  INTELLIGENCE: 'intel',  // Analytics, Forecast, Plan Maître
  TERRITORY: 'territory', // Map, Mon Territoire
  COMMERCE: 'commerce',   // Shop, Business
  ADMIN: 'admin',         // Admin routes (role-restricted)
  USER: 'user'            // User-specific routes
};

// ============================================
// ROUTE DEFINITIONS
// ============================================

export const ROUTES = [
  // ==========================================
  // CORE ROUTES
  // ==========================================
  {
    path: '/',
    name: 'home',
    label: 'Accueil',
    labelKey: 'common_home',
    icon: Home,
    category: ROUTE_CATEGORIES.CORE,
    module: null,
    showInNav: true,
    requiresAuth: false
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    label: 'Tableau de bord',
    labelKey: 'common_dashboard',
    icon: BarChart3,
    category: ROUTE_CATEGORIES.CORE,
    module: 'dashboard',
    showInNav: true,
    requiresAuth: false
  },
  
  // ==========================================
  // INTELLIGENCE ROUTES (Dropdown Group)
  // ==========================================
  {
    path: '/analytics',
    name: 'analytics',
    label: 'Analytics',
    labelKey: 'common_analytics',
    description: 'Statistiques et graphiques',
    descriptionKey: 'common_stats_charts',
    icon: TrendingUp,
    category: ROUTE_CATEGORIES.INTELLIGENCE,
    module: 'analytics',
    showInNav: true,
    navGroup: 'intelligence',
    requiresAuth: false
  },
  {
    path: '/forecast',
    name: 'forecast',
    label: 'Prévisions',
    labelKey: 'common_forecast',
    description: 'Météo et faune',
    descriptionKey: 'common_weather_wildlife',
    icon: Target,
    category: ROUTE_CATEGORIES.INTELLIGENCE,
    module: 'predictive',
    showInNav: true,
    navGroup: 'intelligence',
    requiresAuth: false
  },
  {
    path: '/plan-maitre',
    name: 'plan-maitre',
    label: 'Plan Maître',
    labelKey: 'common_plan_master',
    description: 'Stratégie complète',
    descriptionKey: 'common_full_strategy',
    icon: Radar,
    category: ROUTE_CATEGORIES.INTELLIGENCE,
    module: 'planmaitre',
    showInNav: true,
    navGroup: 'intelligence',
    requiresAuth: false
  },
  
  // ==========================================
  // TERRITORY ROUTES (Dropdown Group)
  // ==========================================
  {
    path: '/map',
    name: 'map',
    label: 'Carte Interactive',
    labelKey: 'common_interactive_map',
    description: 'GPS et waypoints',
    descriptionKey: 'common_gps_waypoints',
    icon: Globe,
    category: ROUTE_CATEGORIES.TERRITORY,
    module: 'geospatial',
    showInNav: true,
    navGroup: 'territory',
    requiresAuth: false
  },
  {
    path: '/territoire',
    name: 'territoire',
    label: 'Mon Territoire',
    labelKey: 'common_my_territory',
    description: 'Analyse BIONIC',
    descriptionKey: 'common_bionic_analysis',
    icon: Crosshair,
    category: ROUTE_CATEGORIES.TERRITORY,
    module: 'territory',
    showInNav: true,
    navGroup: 'territory',
    requiresAuth: false
  },
  
  // ==========================================
  // USER ROUTES
  // ==========================================
  {
    path: '/trips',
    name: 'trips',
    label: 'Sorties',
    labelKey: 'common_trips',
    icon: RouteIcon,
    category: ROUTE_CATEGORIES.USER,
    module: 'tracking',
    showInNav: true,
    requiresAuth: false
  },
  
  // ==========================================
  // COMMERCE ROUTES
  // ==========================================
  {
    path: '/shop',
    name: 'shop',
    label: 'Magasin',
    labelKey: 'nav_shop',
    icon: Store,
    category: ROUTE_CATEGORIES.COMMERCE,
    module: 'marketplace',
    showInNav: true,
    requiresAuth: false
  },
  {
    path: '/compare',
    name: 'compare',
    label: 'Comparez',
    labelKey: 'nav_compare',
    icon: FlaskConical,
    category: ROUTE_CATEGORIES.COMMERCE,
    module: 'products',
    showInNav: false,
    requiresAuth: false
  },
  {
    path: '/business',
    name: 'business',
    label: 'Business',
    labelKey: 'nav_business',
    icon: Briefcase,
    category: ROUTE_CATEGORIES.COMMERCE,
    module: 'business',
    showInNav: true,
    requiresAuth: true,
    requiredRoles: ['business', 'admin']
  },
  
  // ==========================================
  // ADMIN ROUTES
  // ==========================================
  {
    path: '/admin',
    name: 'admin',
    label: 'Admin',
    labelKey: 'nav_admin',
    icon: Settings,
    category: ROUTE_CATEGORIES.ADMIN,
    module: 'admin',
    showInNav: true,
    requiresAuth: true,
    requiredRoles: ['admin']
  },
  {
    path: '/admin/geo',
    name: 'admin-geo',
    label: 'Admin Geo',
    labelKey: 'nav_admin_geo',
    icon: Map,
    category: ROUTE_CATEGORIES.ADMIN,
    module: 'admin',
    showInNav: false,
    requiresAuth: true,
    requiredRoles: ['admin']
  }
];

// ============================================
// NAVIGATION GROUPS (for dropdown menus)
// ============================================

export const NAV_GROUPS = {
  intelligence: {
    name: 'intelligence',
    label: 'Intelligence',
    labelKey: 'common_intelligence',
    icon: Brain,
    routes: ROUTES.filter(r => r.navGroup === 'intelligence')
  },
  territory: {
    name: 'territory',
    label: 'Carte',
    labelKey: 'common_map',
    icon: Map,
    routes: ROUTES.filter(r => r.navGroup === 'territory')
  }
};

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Get routes visible in navigation for a user
 */
export function getVisibleRoutes(user = null) {
  return ROUTES.filter(route => {
    if (!route.showInNav) return false;
    if (!route.requiresAuth) return true;
    if (!user) return false;
    if (route.requiredRoles && !route.requiredRoles.includes(user.role)) return false;
    return true;
  });
}

/**
 * Get routes by category
 */
export function getRoutesByCategory(category) {
  return ROUTES.filter(route => route.category === category);
}

/**
 * Get standalone routes (not in dropdown groups)
 */
export function getStandaloneRoutes(user = null) {
  const visibleRoutes = getVisibleRoutes(user);
  return visibleRoutes.filter(route => !route.navGroup);
}

/**
 * Check if user has access to route
 */
export function hasRouteAccess(route, user = null) {
  if (!route.requiresAuth) return true;
  if (!user) return false;
  if (route.requiredRoles && !route.requiredRoles.includes(user.role)) return false;
  return true;
}

export default ROUTES;
