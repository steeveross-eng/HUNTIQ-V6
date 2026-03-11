/**
 * BIONIC™ Configuration Module
 * Configuration centrale pour le moteur de scoring BIONIC
 */

// Poids globaux par catégorie
const DEFAULT_CATEGORY_WEIGHTS = {
  habitat: 0.25,      // H - Habitats optimaux
  rut: 0.20,          // R - Zones de rut
  salines: 0.10,      // S - Salines potentielles
  affuts: 0.20,       // A - Affûts potentiels
  trajets: 0.15,      // T - Trajets de chasse
  peuplements: 0.10   // P - Peuplements forestiers
};

// Seuils de classification
const DEFAULT_THRESHOLDS = {
  excellent: 85,
  good: 70,
  moderate: 55,
  low: 40,
  poor: 0
};

// Coefficients par type de peuplement forestier
const DEFAULT_STAND_COEFFICIENTS = {
  // Feuillus
  erabliere: { habitat: 0.85, alimentation: 0.90, repos: 0.70, rut: 0.80 },
  betulaire: { habitat: 0.75, alimentation: 0.85, repos: 0.65, rut: 0.75 },
  chenaie: { habitat: 0.80, alimentation: 0.95, repos: 0.60, rut: 0.70 },
  tremblais: { habitat: 0.90, alimentation: 0.95, repos: 0.75, rut: 0.85 },
  
  // Résineux
  sapiniere: { habitat: 0.85, alimentation: 0.60, repos: 0.95, rut: 0.65 },
  pessiereNoire: { habitat: 0.70, alimentation: 0.50, repos: 0.90, rut: 0.55 },
  pessiereBouclier: { habitat: 0.75, alimentation: 0.55, repos: 0.85, rut: 0.60 },
  pinede: { habitat: 0.65, alimentation: 0.45, repos: 0.80, rut: 0.50 },
  cedriere: { habitat: 0.90, alimentation: 0.70, repos: 0.95, rut: 0.75 },
  
  // Mixtes
  mixteFeuillus: { habitat: 0.88, alimentation: 0.85, repos: 0.80, rut: 0.82 },
  mixteResineux: { habitat: 0.82, alimentation: 0.70, repos: 0.88, rut: 0.72 },
  
  // Autres
  friche: { habitat: 0.60, alimentation: 0.75, repos: 0.30, rut: 0.65 },
  coupe: { habitat: 0.55, alimentation: 0.80, repos: 0.25, rut: 0.70 },
  brulis: { habitat: 0.50, alimentation: 0.70, repos: 0.20, rut: 0.60 }
};

// Coefficients topographiques
const DEFAULT_TOPO_COEFFICIENTS = {
  slope: {
    optimal: { min: 5, max: 15 },  // Pente optimale en degrés
    maxPenalty: 0.3,               // Pénalité max pour pentes extrêmes
    flatBonus: 0.1                 // Bonus pour zones plates (repos)
  },
  elevation: {
    relativeOptimal: { min: 10, max: 50 },  // Altitude relative optimale en m
    dominantBonus: 0.15                      // Bonus position dominante
  },
  aspect: {
    southBonus: 0.20,   // Bonus exposition sud
    eastBonus: 0.10,    // Bonus exposition est
    westBonus: 0.05,    // Bonus exposition ouest
    northPenalty: 0.15  // Pénalité exposition nord
  }
};

// Coefficients zones d'alimentation
const DEFAULT_FEEDING_COEFFICIENTS = {
  proximity: {
    optimal: 100,      // Distance optimale en m
    maxDistance: 500,  // Distance max considérée
    decayRate: 0.002   // Taux de décroissance
  },
  density: {
    highDensity: 0.25,    // Bonus haute densité
    mediumDensity: 0.15,  // Bonus densité moyenne
    lowDensity: 0.05      // Bonus faible densité
  },
  types: {
    browse: 0.90,         // Broutage (ramilles, feuilles)
    mast: 0.95,           // Glands, noix, fruits
    forbs: 0.80,          // Plantes herbacées
    aquatic: 0.85         // Plantes aquatiques
  }
};

// Coefficients zones de repos
const DEFAULT_RESTING_COEFFICIENTS = {
  cover: {
    dense: 0.95,      // Couvert dense
    moderate: 0.75,   // Couvert modéré
    sparse: 0.45      // Couvert clairsemé
  },
  security: {
    escapeRoutes: 0.20,     // Bonus routes de fuite
    visualCover: 0.25,      // Bonus couvert visuel
    disturbanceFree: 0.30   // Bonus absence de dérangement
  },
  thermal: {
    winterShelter: 0.30,  // Abri hivernal
    summerShade: 0.25     // Ombrage estival
  }
};

// Coefficients hydrographiques
const DEFAULT_HYDRO_COEFFICIENTS = {
  proximity: {
    optimal: 200,      // Distance optimale à l'eau en m
    maxDistance: 1000, // Distance max considérée
    decayRate: 0.001   // Taux de décroissance
  },
  types: {
    lake: 0.85,
    river: 0.90,
    stream: 0.95,
    pond: 0.88,
    wetland: 0.92,
    spring: 0.98
  },
  complexity: {
    confluence: 0.25,     // Bonus confluence
    meander: 0.15,        // Bonus méandre
    riparian: 0.20        // Bonus zone riveraine
  }
};

// Coefficients météo
const DEFAULT_WEATHER_COEFFICIENTS = {
  wind: {
    optimal: { min: 5, max: 15 },  // km/h
    maxPenalty: 0.40
  },
  temperature: {
    optimal: { min: -5, max: 15 },  // °C
    extremePenalty: 0.30
  },
  pressure: {
    risingBonus: 0.15,
    fallingPenalty: 0.10,
    stableBonus: 0.05
  },
  precipitation: {
    lightRainBonus: 0.10,
    heavyRainPenalty: 0.25,
    snowBonus: 0.15
  }
};

// État de configuration (mutable via admin)
let currentConfig = {
  categoryWeights: { ...DEFAULT_CATEGORY_WEIGHTS },
  thresholds: { ...DEFAULT_THRESHOLDS },
  standCoefficients: { ...DEFAULT_STAND_COEFFICIENTS },
  topoCoefficients: { ...DEFAULT_TOPO_COEFFICIENTS },
  feedingCoefficients: { ...DEFAULT_FEEDING_COEFFICIENTS },
  restingCoefficients: { ...DEFAULT_RESTING_COEFFICIENTS },
  hydroCoefficients: { ...DEFAULT_HYDRO_COEFFICIENTS },
  weatherCoefficients: { ...DEFAULT_WEATHER_COEFFICIENTS }
};

/**
 * Récupère la configuration actuelle
 */
export const getBionicConfig = () => {
  return { ...currentConfig };
};

/**
 * Met à jour partiellement la configuration
 * @param {Object} updates - Objet contenant les mises à jour
 */
export const updateBionicConfig = (updates) => {
  currentConfig = {
    ...currentConfig,
    ...updates
  };
  
  // Sauvegarder dans localStorage pour persistance
  try {
    localStorage.setItem('bionicConfig', JSON.stringify(currentConfig));
  } catch (e) {
    console.warn('Could not save BIONIC config to localStorage:', e);
  }
  
  return currentConfig;
};

/**
 * Réinitialise la configuration aux valeurs par défaut
 */
export const resetBionicConfigToDefaults = () => {
  currentConfig = {
    categoryWeights: { ...DEFAULT_CATEGORY_WEIGHTS },
    thresholds: { ...DEFAULT_THRESHOLDS },
    standCoefficients: { ...DEFAULT_STAND_COEFFICIENTS },
    topoCoefficients: { ...DEFAULT_TOPO_COEFFICIENTS },
    feedingCoefficients: { ...DEFAULT_FEEDING_COEFFICIENTS },
    restingCoefficients: { ...DEFAULT_RESTING_COEFFICIENTS },
    hydroCoefficients: { ...DEFAULT_HYDRO_COEFFICIENTS },
    weatherCoefficients: { ...DEFAULT_WEATHER_COEFFICIENTS }
  };
  
  // Supprimer du localStorage
  try {
    localStorage.removeItem('bionicConfig');
  } catch (e) {
    console.warn('Could not remove BIONIC config from localStorage:', e);
  }
  
  return currentConfig;
};

/**
 * Charge la configuration depuis localStorage au démarrage
 */
export const loadBionicConfig = () => {
  try {
    const saved = localStorage.getItem('bionicConfig');
    if (saved) {
      currentConfig = { ...currentConfig, ...JSON.parse(saved) };
    }
  } catch (e) {
    console.warn('Could not load BIONIC config from localStorage:', e);
  }
  return currentConfig;
};

// Charger la config au démarrage du module
loadBionicConfig();

// Export des constantes par défaut pour référence
export const DEFAULTS = {
  categoryWeights: DEFAULT_CATEGORY_WEIGHTS,
  thresholds: DEFAULT_THRESHOLDS,
  standCoefficients: DEFAULT_STAND_COEFFICIENTS,
  topoCoefficients: DEFAULT_TOPO_COEFFICIENTS,
  feedingCoefficients: DEFAULT_FEEDING_COEFFICIENTS,
  restingCoefficients: DEFAULT_RESTING_COEFFICIENTS,
  hydroCoefficients: DEFAULT_HYDRO_COEFFICIENTS,
  weatherCoefficients: DEFAULT_WEATHER_COEFFICIENTS
};

export default {
  getBionicConfig,
  updateBionicConfig,
  resetBionicConfigToDefaults,
  loadBionicConfig,
  DEFAULTS
};
