/**
 * BIONIC™ Data Adapter
 * Adaptateur pour transformer les données brutes en format BIONIC
 */

import { getBionicConfig } from './bionicConfig';

/**
 * Adapte les données d'un waypoint pour le scoring BIONIC
 * @param {Object} rawWaypoint - Données brutes du waypoint
 * @param {Object} contextData - Données contextuelles (terrain, hydro, etc.)
 */
export const adaptWaypointData = (rawWaypoint, contextData = {}) => {
  return {
    // Coordonnées
    latitude: rawWaypoint.lat || rawWaypoint.latitude,
    longitude: rawWaypoint.lng || rawWaypoint.longitude,
    
    // Topographie
    elevation: contextData.elevation || rawWaypoint.elevation || 100,
    relativeElevation: contextData.relativeElevation || 20,
    slope: contextData.slope || rawWaypoint.slope || 5,
    aspect: contextData.aspect || rawWaypoint.aspect || 180,
    
    // Hydrographie
    waterDistance: contextData.waterDistance || rawWaypoint.waterDistance || 500,
    hydroFeatures: {
      hasConfluence: contextData.hasConfluence || false,
      hasMeander: contextData.hasMeander || false,
      hasRiparianZone: contextData.hasRiparianZone || false,
      waterType: contextData.waterType || 'stream'
    },
    
    // Végétation
    ndvi: contextData.ndvi || rawWaypoint.ndvi || 0.45,
    standType: contextData.standType || rawWaypoint.standType || 'mixteFeuillus',
    isTransition: contextData.isTransition || false,
    adjacentTypes: contextData.adjacentTypes || [],
    coverDensity: contextData.coverDensity || 'moderate',
    
    // Conditions
    humidity: contextData.humidity || 50,
    thermalConditions: {
      temperature: contextData.temperature || 10,
      windSpeed: contextData.windSpeed || 10,
      hasCover: contextData.hasCover !== undefined ? contextData.hasCover : true
    },
    
    // Corridors et sentiers
    isOnCorridor: contextData.isOnCorridor || false,
    corridorWidth: contextData.corridorWidth || 0,
    trailDistance: contextData.trailDistance || 100,
    trailType: contextData.trailType || 'game',
    connectivity: contextData.connectivity || 0.6,
    
    // Zones spéciales
    feedingData: {
      distance: contextData.feedingDistance || 200,
      density: contextData.feedingDensity || 'medium',
      type: contextData.feedingType || 'browse'
    },
    restingData: {
      distance: contextData.restingDistance || 300,
      coverDensity: contextData.restingCover || 'moderate',
      hasEscapeRoutes: contextData.hasEscapeRoutes !== undefined ? contextData.hasEscapeRoutes : true,
      hasVisualCover: contextData.hasVisualCover !== undefined ? contextData.hasVisualCover : true,
      isDisturbanceFree: contextData.isDisturbanceFree || false
    },
    
    // Visibilité et position
    visibility: contextData.visibility || 80,
    
    // Contexte
    humanPressure: contextData.humanPressure || 30,
    structureScore: contextData.structureScore || 70,
    season: getCurrentSeason(),
    context: contextData.context || 'habitat'
  };
};

/**
 * Adapte les données de terrain depuis une API externe
 */
export const adaptTerrainData = (apiResponse) => {
  if (!apiResponse) return {};
  
  return {
    elevation: apiResponse.elevation || apiResponse.ele || 0,
    slope: calculateSlopeFromNeighbors(apiResponse.neighbors),
    aspect: apiResponse.aspect || calculateAspect(apiResponse),
    relativeElevation: apiResponse.relativeElevation || 
      calculateRelativeElevation(apiResponse.elevation, apiResponse.neighbors)
  };
};

/**
 * Adapte les données de végétation (NDVI, peuplements)
 */
export const adaptVegetationData = (ndviData, forestData = null) => {
  const adapted = {
    ndvi: ndviData?.ndvi || ndviData?.value || 0.4
  };
  
  if (forestData) {
    adapted.standType = mapForestType(forestData.type || forestData.cover);
    adapted.coverDensity = mapCoverDensity(forestData.density || forestData.canopy);
    adapted.isTransition = forestData.isEdge || forestData.isTransition || false;
    adapted.adjacentTypes = (forestData.adjacent || []).map(mapForestType);
  }
  
  return adapted;
};

/**
 * Adapte les données hydrographiques
 */
export const adaptHydroData = (hydroData) => {
  if (!hydroData) return {};
  
  const features = hydroData.features || hydroData;
  let nearestWater = Infinity;
  let waterType = null;
  const hydroFeatures = {
    hasConfluence: false,
    hasMeander: false,
    hasRiparianZone: false
  };
  
  if (Array.isArray(features)) {
    features.forEach(feature => {
      const dist = feature.distance || feature.dist || Infinity;
      if (dist < nearestWater) {
        nearestWater = dist;
        waterType = mapWaterType(feature.type);
      }
      
      if (feature.type === 'confluence') hydroFeatures.hasConfluence = true;
      if (feature.isMeander || feature.type === 'meander') hydroFeatures.hasMeander = true;
      if (feature.riparian || feature.isRiparian) hydroFeatures.hasRiparianZone = true;
    });
  }
  
  return {
    waterDistance: nearestWater === Infinity ? 1000 : nearestWater,
    waterType,
    hydroFeatures
  };
};

/**
 * Adapte les données de couches BIONIC pour affichage sur carte
 */
export const adaptLayerData = (layerType, rawData) => {
  const adapters = {
    habitats: adaptHabitatLayer,
    rut: adaptRutLayer,
    salines: adaptSalinesLayer,
    affuts: adaptAffutsLayer,
    trajets: adaptTrajetsLayer,
    peuplements: adaptPeuplementsLayer,
    ensoleillement: adaptSunLayer,
    orientation: adaptOrientationLayer,
    hydro: adaptHydroLayer,
    alimentation: adaptFeedingLayer,
    repos: adaptRestingLayer,
    ndvi: adaptNDVILayer,
    pentes: adaptSlopeLayer,
    altitude: adaptAltitudeLayer,
    corridors: adaptCorridorsLayer
  };
  
  const adapter = adapters[layerType];
  return adapter ? adapter(rawData) : rawData;
};

// Adaptateurs de couches spécifiques
const adaptHabitatLayer = (data) => ({
  ...data,
  color: getColorForScore(data.score),
  opacity: 0.6,
  label: `Habitat: ${data.score}%`
});

const adaptRutLayer = (data) => ({
  ...data,
  color: '#e91e63',
  opacity: 0.5,
  label: `Rut: ${data.score}%`
});

const adaptSalinesLayer = (data) => ({
  ...data,
  color: '#00bcd4',
  opacity: 0.5,
  label: `Saline: ${data.score}%`
});

const adaptAffutsLayer = (data) => ({
  ...data,
  color: '#9c27b0',
  opacity: 0.6,
  icon: 'crosshair',
  label: `Affût: ${data.score}%`
});

const adaptTrajetsLayer = (data) => ({
  ...data,
  color: '#ff9800',
  weight: 3,
  dashArray: '10, 5',
  label: 'Trajet'
});

const adaptPeuplementsLayer = (data) => ({
  ...data,
  color: getStandColor(data.standType),
  opacity: 0.4,
  label: data.standType
});

const adaptSunLayer = (data) => ({
  ...data,
  color: getColorForValue(data.exposure, 0, 100, '#2196f3', '#ffeb3b'),
  opacity: 0.5
});

const adaptOrientationLayer = (data) => ({
  ...data,
  color: getAspectColor(data.aspect),
  opacity: 0.4
});

const adaptHydroLayer = (data) => ({
  ...data,
  color: '#1976d2',
  weight: data.type === 'river' ? 4 : 2,
  opacity: 0.8
});

const adaptFeedingLayer = (data) => ({
  ...data,
  color: '#4caf50',
  opacity: 0.5,
  icon: 'leaf'
});

const adaptRestingLayer = (data) => ({
  ...data,
  color: '#795548',
  opacity: 0.5,
  icon: 'moon'
});

const adaptNDVILayer = (data) => ({
  ...data,
  color: getNDVIColor(data.ndvi),
  opacity: 0.6
});

const adaptSlopeLayer = (data) => ({
  ...data,
  color: getSlopeColor(data.slope),
  opacity: 0.5
});

const adaptAltitudeLayer = (data) => ({
  ...data,
  color: getAltitudeColor(data.elevation, data.minElevation, data.maxElevation),
  opacity: 0.4
});

const adaptCorridorsLayer = (data) => ({
  ...data,
  color: '#ff5722',
  weight: 4,
  opacity: 0.7,
  dashArray: null
});

// Fonctions utilitaires
const getCurrentSeason = () => {
  const month = new Date().getMonth();
  if (month >= 2 && month <= 4) return 'spring';
  if (month >= 5 && month <= 7) return 'summer';
  if (month >= 8 && month <= 10) return 'fall';
  return 'winter';
};

const calculateSlopeFromNeighbors = (neighbors) => {
  if (!neighbors || neighbors.length < 2) return 5;
  const elevDiff = Math.max(...neighbors.map(n => n.elevation)) - 
                   Math.min(...neighbors.map(n => n.elevation));
  return Math.min(45, elevDiff / 10); // Approximation
};

const calculateAspect = (data) => {
  return data.aspect || 180; // Sud par défaut
};

const calculateRelativeElevation = (elevation, neighbors) => {
  if (!neighbors || neighbors.length === 0) return 20;
  const avgNeighbor = neighbors.reduce((sum, n) => sum + n.elevation, 0) / neighbors.length;
  return elevation - avgNeighbor;
};

const mapForestType = (type) => {
  const typeMap = {
    'maple': 'erabliere',
    'birch': 'betulaire',
    'oak': 'chenaie',
    'aspen': 'tremblais',
    'poplar': 'tremblais',
    'fir': 'sapiniere',
    'spruce_black': 'pessiereNoire',
    'spruce': 'pessiereBouclier',
    'pine': 'pinede',
    'cedar': 'cedriere',
    'mixed_hardwood': 'mixteFeuillus',
    'mixed_softwood': 'mixteResineux',
    'clearcut': 'coupe',
    'regeneration': 'friche'
  };
  return typeMap[type?.toLowerCase()] || type || 'mixteFeuillus';
};

const mapCoverDensity = (density) => {
  if (typeof density === 'number') {
    if (density > 70) return 'dense';
    if (density > 40) return 'moderate';
    return 'sparse';
  }
  return density || 'moderate';
};

const mapWaterType = (type) => {
  const typeMap = {
    'lac': 'lake',
    'riviere': 'river',
    'ruisseau': 'stream',
    'etang': 'pond',
    'marecage': 'wetland',
    'source': 'spring'
  };
  return typeMap[type?.toLowerCase()] || type || 'stream';
};

const getColorForScore = (score) => {
  if (score >= 80) return '#22c55e';
  if (score >= 60) return '#84cc16';
  if (score >= 40) return '#eab308';
  if (score >= 20) return '#f97316';
  return '#ef4444';
};

const getColorForValue = (value, min, max, colorLow, colorHigh) => {
  const ratio = (value - min) / (max - min);
  // Interpolation simple - retourne colorHigh pour ratio élevé
  return ratio > 0.5 ? colorHigh : colorLow;
};

const getStandColor = (standType) => {
  const colors = {
    erabliere: '#ff8a65',
    betulaire: '#a1887f',
    chenaie: '#8d6e63',
    tremblais: '#ffb74d',
    sapiniere: '#4caf50',
    pessiereNoire: '#2e7d32',
    pessiereBouclier: '#388e3c',
    pinede: '#558b2f',
    cedriere: '#1b5e20',
    mixteFeuillus: '#aed581',
    mixteResineux: '#7cb342',
    friche: '#d4e157',
    coupe: '#fdd835'
  };
  return colors[standType] || '#9e9e9e';
};

const getAspectColor = (aspect) => {
  if (aspect >= 135 && aspect <= 225) return '#ffeb3b'; // Sud
  if (aspect >= 45 && aspect < 135) return '#90caf9';   // Est
  if (aspect > 225 && aspect <= 315) return '#ffcc80';  // Ouest
  return '#b3e5fc'; // Nord
};

const getNDVIColor = (ndvi) => {
  if (ndvi > 0.6) return '#1b5e20';
  if (ndvi > 0.4) return '#4caf50';
  if (ndvi > 0.2) return '#8bc34a';
  if (ndvi > 0) return '#cddc39';
  return '#795548';
};

const getSlopeColor = (slope) => {
  if (slope < 5) return '#e8f5e9';
  if (slope < 15) return '#a5d6a7';
  if (slope < 25) return '#ffa726';
  if (slope < 35) return '#ef5350';
  return '#b71c1c';
};

const getAltitudeColor = (elevation, min = 0, max = 500) => {
  const ratio = (elevation - min) / (max - min);
  if (ratio > 0.8) return '#5d4037';
  if (ratio > 0.6) return '#8d6e63';
  if (ratio > 0.4) return '#a1887f';
  if (ratio > 0.2) return '#d7ccc8';
  return '#efebe9';
};

export default {
  adaptWaypointData,
  adaptTerrainData,
  adaptVegetationData,
  adaptHydroData,
  adaptLayerData
};
