/**
 * BIONIC™ Scoring Engine
 * Moteur de calcul des scores multi-couches ultra précis
 */

import { getBionicConfig } from './bionicConfig';

// ============================================
// FONCTIONS DE SCORING INDIVIDUELLES
// ============================================

/**
 * Score basé sur la pente du terrain
 * @param {number} slopeDegrees - Pente en degrés
 * @param {string} context - 'habitat' | 'movement' | 'resting'
 */
export const scoreSlope = (slopeDegrees, context = 'habitat') => {
  const config = getBionicConfig().topoCoefficients.slope;
  
  if (context === 'resting') {
    // Pour le repos, les zones plates sont préférées
    if (slopeDegrees < 3) return 1.0 + config.flatBonus;
    if (slopeDegrees < 8) return 0.9;
    if (slopeDegrees < 15) return 0.7;
    return Math.max(0.3, 1 - slopeDegrees * 0.03);
  }
  
  // Pour habitat/mouvement, pente modérée optimale
  if (slopeDegrees >= config.optimal.min && slopeDegrees <= config.optimal.max) {
    return 1.0;
  }
  
  if (slopeDegrees < config.optimal.min) {
    return 0.85 + (slopeDegrees / config.optimal.min) * 0.15;
  }
  
  // Pente trop forte
  const excess = slopeDegrees - config.optimal.max;
  return Math.max(0.3, 1 - excess * 0.02 - config.maxPenalty * (excess / 30));
};

/**
 * Score basé sur la distance à l'eau
 * @param {number} distanceMeters - Distance en mètres
 */
export const scoreWaterDistance = (distanceMeters) => {
  const config = getBionicConfig().hydroCoefficients.proximity;
  
  if (distanceMeters <= config.optimal) {
    return 1.0;
  }
  
  if (distanceMeters > config.maxDistance) {
    return 0.2;
  }
  
  // Décroissance exponentielle
  const decay = Math.exp(-config.decayRate * (distanceMeters - config.optimal));
  return 0.2 + 0.8 * decay;
};

/**
 * Score de complexité hydrographique
 * @param {Object} hydroFeatures - Caractéristiques hydro présentes
 */
export const scoreHydroComplexity = (hydroFeatures) => {
  const config = getBionicConfig().hydroCoefficients;
  let score = 0.5; // Score de base
  
  if (hydroFeatures.hasConfluence) score += config.complexity.confluence;
  if (hydroFeatures.hasMeander) score += config.complexity.meander;
  if (hydroFeatures.hasRiparianZone) score += config.complexity.riparian;
  if (hydroFeatures.waterType) {
    score += (config.types[hydroFeatures.waterType] || 0.5) * 0.3;
  }
  
  return Math.min(1.0, score);
};

/**
 * Score d'humidité du sol
 * @param {number} humidityPercent - Humidité en pourcentage (0-100)
 */
export const scoreHumidity = (humidityPercent) => {
  // Humidité modérée optimale (40-70%)
  if (humidityPercent >= 40 && humidityPercent <= 70) {
    return 1.0;
  }
  
  if (humidityPercent < 40) {
    return 0.5 + (humidityPercent / 40) * 0.5;
  }
  
  // Trop humide
  return Math.max(0.4, 1 - (humidityPercent - 70) * 0.015);
};

/**
 * Score NDVI (indice de végétation)
 * @param {number} ndvi - Valeur NDVI (-1 à 1)
 */
export const scoreNDVI = (ndvi) => {
  // NDVI optimal pour la faune : 0.4-0.7
  if (ndvi >= 0.4 && ndvi <= 0.7) {
    return 1.0;
  }
  
  if (ndvi < 0.4) {
    if (ndvi < 0) return 0.1; // Sol nu ou eau
    return 0.3 + (ndvi / 0.4) * 0.7;
  }
  
  // Végétation très dense (>0.7)
  return 0.85 - (ndvi - 0.7) * 0.5;
};

/**
 * Score par type de peuplement forestier
 * @param {string} standType - Type de peuplement
 * @param {string} context - 'habitat' | 'alimentation' | 'repos' | 'rut'
 */
export const scoreStandType = (standType, context = 'habitat') => {
  const config = getBionicConfig().standCoefficients;
  const coefs = config[standType];
  
  if (!coefs) return 0.5; // Type inconnu
  
  return coefs[context] || 0.5;
};

/**
 * Score des transitions entre peuplements (écotones)
 * @param {boolean} isTransition - Est-ce une zone de transition
 * @param {string[]} adjacentTypes - Types adjacents
 */
export const scoreStandTransition = (isTransition, adjacentTypes = []) => {
  if (!isTransition) return 0.6;
  
  // Bonus pour écotones
  let score = 0.85;
  
  // Bonus supplémentaire si transition feuillus-résineux
  const hasFeuillus = adjacentTypes.some(t => 
    ['erabliere', 'betulaire', 'chenaie', 'tremblais'].includes(t)
  );
  const hasResineux = adjacentTypes.some(t => 
    ['sapiniere', 'pessiereNoire', 'pessiereBouclier', 'pinede', 'cedriere'].includes(t)
  );
  
  if (hasFeuillus && hasResineux) score += 0.15;
  
  return Math.min(1.0, score);
};

/**
 * Score d'exposition au soleil
 * @param {number} aspectDegrees - Orientation en degrés (0=N, 90=E, 180=S, 270=W)
 * @param {string} season - 'spring' | 'summer' | 'fall' | 'winter'
 */
export const scoreSunExposure = (aspectDegrees, season = 'fall') => {
  const config = getBionicConfig().topoCoefficients.aspect;
  
  // Normaliser l'angle
  const aspect = ((aspectDegrees % 360) + 360) % 360;
  
  // En hiver, l'exposition sud est très importante
  const winterBonus = season === 'winter' ? 0.10 : 0;
  
  if (aspect >= 135 && aspect <= 225) {
    // Sud
    return 1.0 + config.southBonus + winterBonus;
  }
  
  if (aspect >= 45 && aspect < 135) {
    // Est
    return 0.85 + config.eastBonus;
  }
  
  if (aspect > 225 && aspect <= 315) {
    // Ouest
    return 0.80 + config.westBonus;
  }
  
  // Nord
  return Math.max(0.5, 0.75 - config.northPenalty - (season === 'winter' ? 0.10 : 0));
};

/**
 * Score de confort thermique
 * @param {Object} conditions - { temperature, wind, cover }
 */
export const scoreThermalComfort = (conditions) => {
  const { temperature, windSpeed, hasCover } = conditions;
  
  let score = 0.5;
  
  // Température optimale
  if (temperature >= 0 && temperature <= 15) {
    score += 0.3;
  } else if (temperature >= -10 && temperature < 0) {
    score += 0.2;
  } else if (temperature > 15 && temperature <= 25) {
    score += 0.15;
  }
  
  // Vent faible favorable
  if (windSpeed < 10) {
    score += 0.15;
  } else if (windSpeed < 20) {
    score += 0.05;
  } else {
    score -= 0.10;
  }
  
  // Couvert protecteur
  if (hasCover) score += 0.15;
  
  return Math.min(1.0, Math.max(0.2, score));
};

/**
 * Score de visibilité (pour affûts)
 * @param {number} visibilityMeters - Portée visuelle en mètres
 */
export const scoreVisibility = (visibilityMeters) => {
  // Visibilité optimale pour affût : 50-150m
  if (visibilityMeters >= 50 && visibilityMeters <= 150) {
    return 1.0;
  }
  
  if (visibilityMeters < 50) {
    return 0.5 + (visibilityMeters / 50) * 0.5;
  }
  
  // Trop de visibilité peut être problématique
  if (visibilityMeters > 200) {
    return Math.max(0.6, 1 - (visibilityMeters - 150) * 0.002);
  }
  
  return 0.9;
};

/**
 * Score de position dominante
 * @param {number} relativeElevation - Élévation relative en mètres
 */
export const scoreDominantPosition = (relativeElevation) => {
  const config = getBionicConfig().topoCoefficients.elevation;
  
  if (relativeElevation >= config.relativeOptimal.min && 
      relativeElevation <= config.relativeOptimal.max) {
    return 1.0 + config.dominantBonus;
  }
  
  if (relativeElevation < config.relativeOptimal.min) {
    return 0.6 + (relativeElevation / config.relativeOptimal.min) * 0.4;
  }
  
  // Position très dominante (crête)
  return Math.max(0.7, 1 - (relativeElevation - config.relativeOptimal.max) * 0.005);
};

/**
 * Score des corridors fauniques
 * @param {boolean} isOnCorridor - Est-ce sur un corridor
 * @param {number} corridorWidth - Largeur du corridor en m
 */
export const scoreCorridors = (isOnCorridor, corridorWidth = 0) => {
  if (!isOnCorridor) return 0.4;
  
  // Corridors optimaux : 50-200m de large
  if (corridorWidth >= 50 && corridorWidth <= 200) {
    return 1.0;
  }
  
  if (corridorWidth < 50) {
    return 0.7 + (corridorWidth / 50) * 0.3;
  }
  
  // Corridor très large
  return Math.max(0.75, 1 - (corridorWidth - 200) * 0.001);
};

/**
 * Score des sentiers/pistes
 * @param {number} distanceToTrail - Distance au sentier en m
 * @param {string} trailType - 'game' | 'human' | 'atv'
 */
export const scoreTrails = (distanceToTrail, trailType = 'game') => {
  const optimalDistances = {
    game: { min: 5, max: 30 },
    human: { min: 100, max: 300 },
    atv: { min: 150, max: 400 }
  };
  
  const optimal = optimalDistances[trailType] || optimalDistances.game;
  
  if (distanceToTrail >= optimal.min && distanceToTrail <= optimal.max) {
    return 1.0;
  }
  
  if (distanceToTrail < optimal.min) {
    // Trop près (dérangement potentiel pour sentiers humains)
    return trailType === 'game' ? 0.9 : 0.5;
  }
  
  // Trop loin
  return Math.max(0.3, 1 - (distanceToTrail - optimal.max) * 0.002);
};

/**
 * Score de connectivité
 * @param {number} connectivityIndex - Indice de connectivité (0-1)
 */
export const scoreConnectivity = (connectivityIndex) => {
  return Math.min(1.0, Math.max(0.2, connectivityIndex * 1.2));
};

/**
 * Score de zone d'alimentation
 * @param {Object} feedingData - Données de zone d'alimentation
 */
export const scoreFeedingZone = (feedingData) => {
  const config = getBionicConfig().feedingCoefficients;
  let score = 0.3;
  
  // Proximité
  if (feedingData.distance !== undefined) {
    if (feedingData.distance <= config.proximity.optimal) {
      score += 0.35;
    } else {
      const decay = Math.exp(-config.proximity.decayRate * 
        (feedingData.distance - config.proximity.optimal));
      score += 0.35 * decay;
    }
  }
  
  // Densité
  if (feedingData.density === 'high') score += config.density.highDensity;
  else if (feedingData.density === 'medium') score += config.density.mediumDensity;
  else if (feedingData.density === 'low') score += config.density.lowDensity;
  
  // Type de nourriture
  if (feedingData.type && config.types[feedingData.type]) {
    score += config.types[feedingData.type] * 0.2;
  }
  
  return Math.min(1.0, score);
};

/**
 * Score de zone de repos
 * @param {Object} restingData - Données de zone de repos
 */
export const scoreRestingZone = (restingData) => {
  const config = getBionicConfig().restingCoefficients;
  let score = 0.3;
  
  // Couvert
  if (restingData.coverDensity === 'dense') score += config.cover.dense * 0.3;
  else if (restingData.coverDensity === 'moderate') score += config.cover.moderate * 0.3;
  else score += config.cover.sparse * 0.3;
  
  // Sécurité
  if (restingData.hasEscapeRoutes) score += config.security.escapeRoutes;
  if (restingData.hasVisualCover) score += config.security.visualCover;
  if (restingData.isDisturbanceFree) score += config.security.disturbanceFree;
  
  return Math.min(1.0, score);
};

// ============================================
// CALCUL DES SCORES PAR CATÉGORIE
// ============================================

/**
 * Calcule le score Habitat (H)
 */
export const calculateHabitatScore = (data) => {
  const weights = {
    slope: 0.12,
    water: 0.15,
    hydro: 0.10,
    ndvi: 0.15,
    stand: 0.18,
    thermal: 0.10,
    feeding: 0.10,
    resting: 0.10
  };
  
  let score = 0;
  
  if (data.slope !== undefined) score += weights.slope * scoreSlope(data.slope, 'habitat');
  if (data.waterDistance !== undefined) score += weights.water * scoreWaterDistance(data.waterDistance);
  if (data.hydroFeatures) score += weights.hydro * scoreHydroComplexity(data.hydroFeatures);
  if (data.ndvi !== undefined) score += weights.ndvi * scoreNDVI(data.ndvi);
  if (data.standType) score += weights.stand * scoreStandType(data.standType, 'habitat');
  if (data.thermalConditions) score += weights.thermal * scoreThermalComfort(data.thermalConditions);
  if (data.feedingData) score += weights.feeding * scoreFeedingZone(data.feedingData);
  if (data.restingData) score += weights.resting * scoreRestingZone(data.restingData);
  
  return Math.round(score * 100);
};

/**
 * Calcule le score Rut (R)
 */
export const calculateRutScore = (data) => {
  const weights = {
    transition: 0.25,
    habitat: 0.20,
    topo: 0.15,
    hydro: 0.15,
    feeding: 0.15,
    stand: 0.10
  };
  
  let score = 0;
  
  if (data.isTransition !== undefined) {
    score += weights.transition * scoreStandTransition(data.isTransition, data.adjacentTypes);
  }
  if (data.habitatScore !== undefined) score += weights.habitat * (data.habitatScore / 100);
  if (data.relativeElevation !== undefined) {
    score += weights.topo * scoreDominantPosition(data.relativeElevation);
  }
  if (data.hydroFeatures) score += weights.hydro * scoreHydroComplexity(data.hydroFeatures);
  if (data.feedingData) score += weights.feeding * scoreFeedingZone(data.feedingData);
  if (data.standType) score += weights.stand * scoreStandType(data.standType, 'rut');
  
  return Math.round(score * 100);
};

/**
 * Calcule le score Salines (S)
 */
export const calculateSalinesScore = (data) => {
  const weights = {
    humidity: 0.30,
    water: 0.25,
    access: 0.25,
    discretion: 0.20
  };
  
  let score = 0;
  
  if (data.humidity !== undefined) score += weights.humidity * scoreHumidity(data.humidity);
  if (data.waterDistance !== undefined) score += weights.water * scoreWaterDistance(data.waterDistance);
  if (data.trailDistance !== undefined) {
    score += weights.access * scoreTrails(data.trailDistance, 'game');
  }
  if (data.coverDensity) {
    const coverScore = data.coverDensity === 'dense' ? 0.9 : 
                       data.coverDensity === 'moderate' ? 0.7 : 0.4;
    score += weights.discretion * coverScore;
  }
  
  return Math.round(score * 100);
};

/**
 * Calcule le score Affûts (A)
 */
export const calculateAffutsScore = (data) => {
  const weights = {
    visibility: 0.20,
    position: 0.20,
    corridors: 0.18,
    sun: 0.12,
    feeding: 0.15,
    resting: 0.15
  };
  
  let score = 0;
  
  if (data.visibility !== undefined) score += weights.visibility * scoreVisibility(data.visibility);
  if (data.relativeElevation !== undefined) {
    score += weights.position * scoreDominantPosition(data.relativeElevation);
  }
  if (data.isOnCorridor !== undefined) {
    score += weights.corridors * scoreCorridors(data.isOnCorridor, data.corridorWidth);
  }
  if (data.aspect !== undefined) score += weights.sun * scoreSunExposure(data.aspect, data.season);
  if (data.feedingData) score += weights.feeding * scoreFeedingZone(data.feedingData);
  if (data.restingData) score += weights.resting * scoreRestingZone(data.restingData);
  
  return Math.round(score * 100);
};

/**
 * Calcule le score Trajets (T)
 */
export const calculateTrajetsScore = (data) => {
  const weights = {
    trails: 0.35,
    slope: 0.30,
    connectivity: 0.35
  };
  
  let score = 0;
  
  if (data.trailDistance !== undefined) {
    score += weights.trails * scoreTrails(data.trailDistance, data.trailType);
  }
  if (data.slope !== undefined) score += weights.slope * scoreSlope(data.slope, 'movement');
  if (data.connectivity !== undefined) score += weights.connectivity * scoreConnectivity(data.connectivity);
  
  return Math.round(score * 100);
};

/**
 * Calcule le score Peuplements (P)
 */
export const calculatePeuplementsScore = (data) => {
  const weights = {
    type: 0.50,
    structure: 0.30,
    transition: 0.20
  };
  
  let score = 0;
  
  if (data.standType) score += weights.type * scoreStandType(data.standType, data.context || 'habitat');
  if (data.structureScore !== undefined) score += weights.structure * (data.structureScore / 100);
  if (data.isTransition !== undefined) {
    score += weights.transition * scoreStandTransition(data.isTransition, data.adjacentTypes);
  }
  
  return Math.round(score * 100);
};

/**
 * Calcule le score BIONIC global
 * @param {Object} allScores - { score_H, score_R, score_S, score_A, score_T, score_P }
 */
export const calculateBionicScore = (allScores) => {
  const weights = getBionicConfig().categoryWeights;
  
  const score_Bionic = 
    (allScores.score_H || 0) * weights.habitat +
    (allScores.score_R || 0) * weights.rut +
    (allScores.score_S || 0) * weights.salines +
    (allScores.score_A || 0) * weights.affuts +
    (allScores.score_T || 0) * weights.trajets +
    (allScores.score_P || 0) * weights.peuplements;
  
  return Math.round(score_Bionic);
};

/**
 * Calcule tous les scores pour un waypoint
 * @param {Object} waypointData - Toutes les données du waypoint
 */
export const getScoresForWaypoint = (waypointData) => {
  const score_H = calculateHabitatScore(waypointData);
  const score_R = calculateRutScore({ ...waypointData, habitatScore: score_H });
  const score_S = calculateSalinesScore(waypointData);
  const score_A = calculateAffutsScore(waypointData);
  const score_T = calculateTrajetsScore(waypointData);
  const score_P = calculatePeuplementsScore(waypointData);
  
  const allScores = { score_H, score_R, score_S, score_A, score_T, score_P };
  const score_Bionic = calculateBionicScore(allScores);
  
  return {
    ...allScores,
    score_Bionic,
    breakdown: {
      habitat: score_H,
      rut: score_R,
      salines: score_S,
      affuts: score_A,
      trajets: score_T,
      peuplements: score_P,
      global: score_Bionic
    }
  };
};

export default {
  // Fonctions de scoring individuelles
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
  
  // Calculs par catégorie
  calculateHabitatScore,
  calculateRutScore,
  calculateSalinesScore,
  calculateAffutsScore,
  calculateTrajetsScore,
  calculatePeuplementsScore,
  calculateBionicScore,
  
  // Fonction principale
  getScoresForWaypoint
};
