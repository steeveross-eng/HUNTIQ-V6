/**
 * V5-ULTIME Frontend Module Registry
 * ===================================
 * 
 * Registre central de tous les modules frontend.
 * Structure modulaire stricte LEGO.
 * 
 * Règles:
 * 1. Un module = un dossier = une page = un composant parent
 * 2. Aucun composant partagé hors /components/core
 * 3. Aucun import croisé entre modules
 * 4. Aucun helper global
 * 5. Navigation modulaire obligatoire
 */

// ==============================================
// UI MODULES
// ==============================================

export const UI_MODULES = {
  // UI Core
  core: {
    path: '/components/core',
    components: ['CoreNavigation', 'CoreLayout', 'CoreButton', 'CoreCard', 'CoreLoader', 'CoreError', 'CoreModal'],
    description: 'Composants de base réutilisables'
  },
  
  // UI Scoring
  scoring: {
    path: '/ui/scoring',
    components: ['ScoringDashboard', 'ScoringCard', 'ScoringGauge', 'ScoringRadar'],
    description: 'Module UI pour le système de scoring'
  },
  
  // UI Météo
  meteo: {
    path: '/ui/meteo',
    components: ['MeteoDashboard', 'MeteoCard', 'MeteoForecast'],
    description: 'Module UI pour les données météorologiques'
  },
  
  // UI Stratégie
  strategie: {
    path: '/ui/strategie',
    components: ['StrategieDashboard', 'StrategieCard', 'StrategieTimeline'],
    description: 'Module UI pour les stratégies de chasse'
  },
  
  // UI Territoire
  territoire: {
    path: '/ui/territoire',
    components: ['TerritoireDashboard', 'TerritoireMap', 'TerritoireStats'],
    description: 'Module UI pour la gestion du territoire'
  },
  
  // UI Plan Maître (Phase 9)
  plan_maitre: {
    path: '/ui/plan_maitre',
    components: ['PlanMaitreDashboard', 'PlanMaitreTimeline', 'PlanMaitreRules', 'PlanMaitreStrategyView', 'PlanMaitreStats'],
    description: 'Module UI complet du Plan Maître (Phase 9)'
  }
};

// ==============================================
// DATA LAYERS
// ==============================================

export const DATA_LAYERS = {
  ecoforestry: {
    path: '/data_layers/ecoforestry',
    components: ['EcoforestryLayer', 'EcoforestryLegend'],
    description: 'Couche de données écoforestières'
  },
  
  behavioral: {
    path: '/data_layers/behavioral',
    components: ['BehavioralLayer', 'BehavioralHeatmap', 'BehavioralLegend'],
    description: 'Couche de données comportementales'
  },
  
  simulation: {
    path: '/data_layers/simulation',
    components: ['SimulationLayer', 'SimulationControls'],
    description: 'Couche de simulation de mouvements'
  },
  
  layers_3d: {
    path: '/data_layers/layers_3d',
    components: ['Layers3D', 'Layers3DControls'],
    description: 'Couche de données 3D'
  },
  
  advanced_geospatial: {
    path: '/data_layers/advanced_geospatial',
    components: ['GeospatialLayer', 'GeospatialOverlay', 'GeospatialLegend'],
    description: 'Couche géospatiale avancée'
  }
};

// ==============================================
// BUSINESS MODULES
// ==============================================

export const BUSINESS_MODULES = {
  live_heading_view: {
    path: '/modules/live_heading_view',
    phase: 'P6',
    version: '2.0.0',
    components: ['LiveHeadingView', 'CompassWidget', 'ForwardCone', 'WindIndicator', 'POIMarker', 'AlertToast', 'SessionControls', 'SessionStats'],
    description: 'Navigation immersive Live Heading'
  },
  
  analytics: {
    path: '/modules/analytics',
    phase: 'P3',
    version: '1.0.0',
    components: ['AnalyticsDashboard'],
    description: 'Statistiques et KPIs'
  },
  
  scoring: {
    path: '/modules/scoring',
    phase: 'P2',
    version: '1.0.0',
    components: ['ScoringView'],
    description: 'Évaluation des produits'
  },
  
  weather: {
    path: '/modules/weather',
    phase: 'P2',
    version: '1.0.0',
    components: ['WeatherWidget'],
    description: 'Analyse météorologique'
  },
  
  territory: {
    path: '/modules/territory',
    phase: 'P3',
    version: '1.0.0',
    components: ['TerritoryManager'],
    description: 'Gestion du territoire'
  },
  
  strategy: {
    path: '/modules/strategy',
    phase: 'P2',
    version: '1.0.0',
    components: ['StrategyRecommendations'],
    description: 'Recommandations stratégiques'
  }
};

// ==============================================
// MODULE VALIDATION
// ==============================================

/**
 * Valide qu'un module respecte la structure LEGO
 */
export const validateModule = (moduleName, moduleConfig) => {
  const errors = [];
  
  if (!moduleConfig.path) {
    errors.push(`Module ${moduleName}: path manquant`);
  }
  
  if (!moduleConfig.components || moduleConfig.components.length === 0) {
    errors.push(`Module ${moduleName}: aucun composant défini`);
  }
  
  if (!moduleConfig.description) {
    errors.push(`Module ${moduleName}: description manquante`);
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
};

/**
 * Obtient tous les modules enregistrés
 */
export const getAllModules = () => ({
  ui: UI_MODULES,
  dataLayers: DATA_LAYERS,
  business: BUSINESS_MODULES
});

/**
 * Compte le nombre total de modules
 */
export const getModuleCount = () => {
  return (
    Object.keys(UI_MODULES).length +
    Object.keys(DATA_LAYERS).length +
    Object.keys(BUSINESS_MODULES).length
  );
};

export default {
  UI_MODULES,
  DATA_LAYERS,
  BUSINESS_MODULES,
  validateModule,
  getAllModules,
  getModuleCount
};
