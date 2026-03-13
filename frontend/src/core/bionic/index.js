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
// STEVE-MAX++ HARMONISATION: Couleurs alignees 1:1 avec ZONE_COLORS normatives
export const BIONIC_LAYERS = [
  { id: 'habitats', name: 'Habitats optimaux', iconName: 'Home', color: '#10B981' },
  { id: 'rut', name: 'Rut potentiel', iconName: 'Heart', color: '#FF4D6D' },
  { id: 'salines', name: 'Salines potentielles', iconName: 'Droplets', color: '#FFFF00' },
  { id: 'affuts', name: 'Affuts potentiels', iconName: 'Target', color: '#F5A623' },
  { id: 'trajets', name: 'Trajets de chasse', iconName: 'Route', color: '#FF9800' },
  { id: 'peuplements', name: 'Peuplements forestiers', iconName: 'TreePine', color: '#15803D' },
  { id: 'ensoleillement', name: 'Ensoleillement', iconName: 'Sun', color: '#FCD34D' },
  { id: 'orientation', name: 'Orientation', iconName: 'Compass', color: '#2196F3' },
  { id: 'hydro', name: 'Hydrographie avancee', iconName: 'Waves', color: '#3B82F6' },
  { id: 'alimentation', name: 'Zones d\'alimentation', iconName: 'Leaf', color: '#22C55E' },
  { id: 'repos', name: 'Zones de repos', iconName: 'Moon', color: '#8B5CF6' },
  { id: 'ndvi', name: 'NDVI / Densite vegetale', iconName: 'Sprout', color: '#66BB6A' },
  { id: 'pentes', name: 'Pentes', iconName: 'Mountain', color: '#FF7043' },
  { id: 'altitude', name: 'Altitude relative', iconName: 'BarChart3', color: '#78909C' },
  { id: 'corridors', name: 'Corridors fauniques', iconName: 'Footprints', color: '#06B6D4' }
];

export const SCORE_CATEGORIES = [
  { id: 'habitat', key: 'score_H', name: 'Habitat', iconName: 'Home', weight: 0.25 },
  { id: 'rut', key: 'score_R', name: 'Rut', iconName: 'Heart', weight: 0.20 },
  { id: 'salines', key: 'score_S', name: 'Salines', iconName: 'Droplets', weight: 0.10 },
  { id: 'affuts', key: 'score_A', name: 'Affûts', iconName: 'Target', weight: 0.20 },
  { id: 'trajets', key: 'score_T', name: 'Trajets', iconName: 'Route', weight: 0.15 },
  { id: 'peuplements', key: 'score_P', name: 'Peuplements', iconName: 'TreePine', weight: 0.10 }
];
