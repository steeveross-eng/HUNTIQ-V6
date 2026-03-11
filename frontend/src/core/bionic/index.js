/**
 * BIONIC™ Core Module Index
 * Exports centralisés pour le système BIONIC
 */

// Configuration
export { 
  getBionicConfig, 
  updateBionicConfig, 
  resetBionicConfigToDefaults,
  loadBionicConfig,
  DEFAULTS as BIONIC_DEFAULTS 
} from './bionicConfig';

// Scoring
export {
  scoreSlope,
  scoreWaterDistance,
  scoreHydroComplexity,
  scoreHumidity,
  scoreNDVI,
  scoreStandType,
  scoreStandTransition,
  scoreSunExposure,
  scoreThermalComfort,
  scoreVisibility,
  scoreDominantPosition,
  scoreCorridors,
  scoreTrails,
  scoreConnectivity,
  scoreFeedingZone,
  scoreRestingZone,
  calculateHabitatScore,
  calculateRutScore,
  calculateSalinesScore,
  calculateAffutsScore,
  calculateTrajetsScore,
  calculatePeuplementsScore,
  calculateBionicScore,
  getScoresForWaypoint
} from './bionicScoring';

// Modèle hybride
export {
  applyRulesEngine,
  applyAIAdjustment,
  calculateHybridScore,
  generateRecommendations
} from './bionicHybridModel';

// Météo
export {
  fetchWeatherData,
  findNextOptimalWindow,
  getWindDirectionText,
  getWeatherDescription,
  THERMAL_STATES,
  FRONT_TYPES
} from './bionicWeatherEngine';

// Stratégie
export { getStrategyForWaypoint } from './bionicStrategyEngine';

// Data Adapter
export {
  adaptWaypointData,
  adaptTerrainData,
  adaptVegetationData,
  adaptHydroData,
  adaptLayerData
} from './bionicDataAdapter';

// Modules BIONIC — Source de vérité pour couleurs, catégories, interprétations
export { BIONIC_MODULES } from './bionicModules';

// Configuration des espèces — BIONIC V5
export { SPECIES, SPECIES_LIST, getSpeciesLayers, getSpeciesWeight } from './speciesConfig';

// Types et constantes - BIONIC Design System compliant (iconName for Lucide icons)
export const BIONIC_LAYERS = [
  { id: 'habitats', name: 'Habitats optimaux', iconName: 'Home', color: '#22c55e' },
  { id: 'rut', name: 'Rut potentiel', iconName: 'Heart', color: '#e91e63' },
  { id: 'salines', name: 'Salines potentielles', iconName: 'Droplets', color: '#00bcd4' },
  { id: 'affuts', name: 'Affûts potentiels', iconName: 'Target', color: '#9c27b0' },
  { id: 'trajets', name: 'Trajets de chasse', iconName: 'Route', color: '#ff9800' },
  { id: 'peuplements', name: 'Peuplements forestiers', iconName: 'TreePine', color: '#4caf50' },
  { id: 'ensoleillement', name: 'Ensoleillement', iconName: 'Sun', color: '#ffeb3b' },
  { id: 'orientation', name: 'Orientation', iconName: 'Compass', color: '#2196f3' },
  { id: 'hydro', name: 'Hydrographie avancée', iconName: 'Waves', color: '#1976d2' },
  { id: 'alimentation', name: 'Zones d\'alimentation', iconName: 'Leaf', color: '#8bc34a' },
  { id: 'repos', name: 'Zones de repos', iconName: 'Moon', color: '#795548' },
  { id: 'ndvi', name: 'NDVI / Densité végétale', iconName: 'Sprout', color: '#66bb6a' },
  { id: 'pentes', name: 'Pentes', iconName: 'Mountain', color: '#ff7043' },
  { id: 'altitude', name: 'Altitude relative', iconName: 'BarChart3', color: '#78909c' },
  { id: 'corridors', name: 'Corridors fauniques', iconName: 'Footprints', color: '#ff5722' }
];

export const SCORE_CATEGORIES = [
  { id: 'habitat', key: 'score_H', name: 'Habitat', iconName: 'Home', weight: 0.25 },
  { id: 'rut', key: 'score_R', name: 'Rut', iconName: 'Heart', weight: 0.20 },
  { id: 'salines', key: 'score_S', name: 'Salines', iconName: 'Droplets', weight: 0.10 },
  { id: 'affuts', key: 'score_A', name: 'Affûts', iconName: 'Target', weight: 0.20 },
  { id: 'trajets', key: 'score_T', name: 'Trajets', iconName: 'Route', weight: 0.15 },
  { id: 'peuplements', key: 'score_P', name: 'Peuplements', iconName: 'TreePine', weight: 0.10 }
];
