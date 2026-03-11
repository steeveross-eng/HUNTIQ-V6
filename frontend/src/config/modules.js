/**
 * BIONIC HUNT/Chasse V3 - Module Registry
 * Phase 7-8: Frontend Modular Architecture
 * 
 * Central registry of all frontend modules.
 * Used for dynamic loading and module status tracking.
 * 
 * @version 2.0.0
 */

// ============================================
// MODULE STATUS CONSTANTS
// ============================================

export const MODULE_STATUS = {
  ACTIVE: 'active',
  DEPRECATED: 'deprecated',
  EXPERIMENTAL: 'experimental',
  LOCKED: 'locked'
};

export const MODULE_TYPE = {
  CORE: 'core',
  ADVANCED: 'advanced',
  BUSINESS: 'business',
  ADMIN: 'admin',
  SPECIAL: 'special'
};

// ============================================
// MODULE REGISTRY
// ============================================

export const MODULES = {
  // ==========================================
  // CORE MODULES (Phase 2)
  // ==========================================
  weather: {
    name: 'weather',
    version: '1.1.0',
    type: MODULE_TYPE.CORE,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/weather',
    description: 'Weather display and forecast widgets',
    backendEndpoint: '/api/v1/weather'
  },
  scoring: {
    name: 'scoring',
    version: '1.0.0',
    type: MODULE_TYPE.CORE,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/scoring',
    description: 'Score visualization components',
    backendEndpoint: '/api/v1/scoring'
  },
  strategy: {
    name: 'strategy',
    version: '1.0.0',
    type: MODULE_TYPE.CORE,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/strategy',
    description: 'Hunting strategy components',
    backendEndpoint: '/api/v1/strategy'
  },
  geospatial: {
    name: 'geospatial',
    version: '1.0.0',
    type: MODULE_TYPE.CORE,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/geospatial',
    description: 'Map layers and geospatial UI',
    backendEndpoint: '/api/v1/geospatial'
  },
  ai: {
    name: 'ai',
    version: '1.0.0',
    type: MODULE_TYPE.CORE,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/ai',
    description: 'AI analysis UI components',
    backendEndpoint: '/api/v1/ai'
  },
  wms: {
    name: 'wms',
    version: '1.0.0',
    type: MODULE_TYPE.CORE,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/wms',
    description: 'WMS layer management',
    backendEndpoint: '/api/v1/wms'
  },
  marketplace: {
    name: 'marketplace',
    version: '1.0.0',
    type: MODULE_TYPE.CORE,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/marketplace',
    description: 'E-commerce components',
    backendEndpoint: '/api/v1/marketplace'
  },
  tracking: {
    name: 'tracking',
    version: '1.0.0',
    type: MODULE_TYPE.CORE,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/tracking',
    description: 'Live tracking UI',
    backendEndpoint: '/api/v1/tracking'
  },
  
  // ==========================================
  // ADVANCED MODULES (Phase 4)
  // ==========================================
  ecoforestry: {
    name: 'ecoforestry',
    version: '1.0.0',
    type: MODULE_TYPE.ADVANCED,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/ecoforestry',
    description: 'Ecoforestry visualization',
    backendEndpoint: '/api/v1/ecoforestry'
  },
  advanced_geospatial: {
    name: 'advanced_geospatial',
    version: '1.0.0',
    type: MODULE_TYPE.ADVANCED,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/advanced_geospatial',
    description: 'Advanced geospatial UI',
    backendEndpoint: '/api/v1/geospatial-advanced'
  },
  engine_3d: {
    name: 'engine_3d',
    version: '1.0.0',
    type: MODULE_TYPE.ADVANCED,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/engine_3d',
    description: '3D terrain viewer',
    backendEndpoint: '/api/v1/3d'
  },
  wildlife_behavior: {
    name: 'wildlife_behavior',
    version: '1.0.0',
    type: MODULE_TYPE.ADVANCED,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/wildlife_behavior',
    description: 'Wildlife behavior patterns',
    backendEndpoint: '/api/v1/wildlife-behavior'
  },
  simulation: {
    name: 'simulation',
    version: '1.0.0',
    type: MODULE_TYPE.ADVANCED,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/simulation',
    description: 'Simulation controls',
    backendEndpoint: '/api/v1/simulation'
  },
  adaptive_strategy: {
    name: 'adaptive_strategy',
    version: '1.0.0',
    type: MODULE_TYPE.ADVANCED,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/adaptive_strategy',
    description: 'Adaptive strategy UI',
    backendEndpoint: '/api/v1/adaptive-strategy'
  },
  recommendation: {
    name: 'recommendation',
    version: '1.0.0',
    type: MODULE_TYPE.ADVANCED,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/recommendation',
    description: 'Recommendation widgets',
    backendEndpoint: '/api/v1/recommendation'
  },
  progression: {
    name: 'progression',
    version: '1.0.0',
    type: MODULE_TYPE.ADVANCED,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/progression',
    description: 'User progression UI',
    backendEndpoint: '/api/v1/progression'
  },
  collaborative: {
    name: 'collaborative',
    version: '1.0.0',
    type: MODULE_TYPE.ADVANCED,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/collaborative',
    description: 'Collaboration features',
    backendEndpoint: '/api/v1/collaborative'
  },
  
  // ==========================================
  // BUSINESS MODULES (Phase 5)
  // ==========================================
  products: {
    name: 'products',
    version: '1.0.0',
    type: MODULE_TYPE.BUSINESS,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/products',
    description: 'Product display components',
    backendEndpoint: '/api/v1/products'
  },
  orders: {
    name: 'orders',
    version: '1.0.0',
    type: MODULE_TYPE.BUSINESS,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/orders',
    description: 'Order management UI',
    backendEndpoint: '/api/v1/orders'
  },
  cart: {
    name: 'cart',
    version: '1.0.0',
    type: MODULE_TYPE.BUSINESS,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/cart',
    description: 'Shopping cart widget',
    backendEndpoint: '/api/v1/cart'
  },
  affiliate: {
    name: 'affiliate',
    version: '1.0.0',
    type: MODULE_TYPE.BUSINESS,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/affiliate',
    description: 'Affiliate program UI',
    backendEndpoint: '/api/v1/affiliate'
  },
  
  // ==========================================
  // SPECIAL MODULES (Phase 6)
  // ==========================================
  live_heading_view: {
    name: 'live_heading_view',
    version: '1.0.0',
    type: MODULE_TYPE.SPECIAL,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/live_heading_view',
    description: 'Immersive live heading navigation',
    backendEndpoint: '/api/v1/live-heading'
  },
  analytics: {
    name: 'analytics',
    version: '1.0.0',
    type: MODULE_TYPE.SPECIAL,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/analytics',
    description: 'Analytics dashboard',
    backendEndpoint: '/api/v1/analytics'
  },
  predictive: {
    name: 'predictive',
    version: '1.0.0',
    type: MODULE_TYPE.SPECIAL,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/predictive',
    description: 'Predictive analysis UI',
    backendEndpoint: '/api/v1/predictive'
  },
  
  // ==========================================
  // ADMIN MODULE
  // ==========================================
  admin: {
    name: 'admin',
    version: '1.0.0',
    type: MODULE_TYPE.ADMIN,
    status: MODULE_STATUS.ACTIVE,
    path: '@/modules/admin',
    description: 'Admin dashboard',
    backendEndpoint: '/api/admin'
  }
};

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Get all modules by type
 */
export function getModulesByType(type) {
  return Object.values(MODULES).filter(m => m.type === type);
}

/**
 * Get all active modules
 */
export function getActiveModules() {
  return Object.values(MODULES).filter(m => m.status === MODULE_STATUS.ACTIVE);
}

/**
 * Get module by name
 */
export function getModule(name) {
  return MODULES[name] || null;
}

/**
 * Get module stats
 */
export function getModuleStats() {
  const modules = Object.values(MODULES);
  return {
    total: modules.length,
    byType: {
      core: modules.filter(m => m.type === MODULE_TYPE.CORE).length,
      advanced: modules.filter(m => m.type === MODULE_TYPE.ADVANCED).length,
      business: modules.filter(m => m.type === MODULE_TYPE.BUSINESS).length,
      admin: modules.filter(m => m.type === MODULE_TYPE.ADMIN).length,
      special: modules.filter(m => m.type === MODULE_TYPE.SPECIAL).length
    },
    byStatus: {
      active: modules.filter(m => m.status === MODULE_STATUS.ACTIVE).length,
      deprecated: modules.filter(m => m.status === MODULE_STATUS.DEPRECATED).length,
      experimental: modules.filter(m => m.status === MODULE_STATUS.EXPERIMENTAL).length,
      locked: modules.filter(m => m.status === MODULE_STATUS.LOCKED).length
    }
  };
}

export default MODULES;
