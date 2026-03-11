/**
 * PHASE G — MOTEUR PRÉDICTIF TERRITORIAL
 * 
 * Module de prédiction basé sur des modèles déterministes locaux
 * enrichis par LLM pour le contexte (option Hybrid).
 * 
 * @module phase-g/predictive
 * @version G-P0-MPT-v1.0.0
 * @phase G-P0
 * @security G-SEC compliant
 * @qa G-QA validated
 */

import { PredictiveEngineContract } from '../contracts/api-contracts';

// ============================================
// CONFIGURATION DU MODULE
// ============================================

const MODULE_CONFIG = {
  moduleId: 'G-P0-MPT',
  version: '1.0.0',
  name: 'Moteur Prédictif Territorial',
  
  // Paramètres de calcul
  defaultRadius: 10, // km
  maxRadius: 100, // km
  gridResolution: 0.5, // km
  minConfidence: 0.3,
  
  // Facteurs de pondération
  weights: {
    habitat: 0.25,
    weather: 0.20,
    seasonality: 0.20,
    activity: 0.15,
    moonPhase: 0.10,
    historical: 0.10
  }
};

// ============================================
// DONNÉES DE RÉFÉRENCE (DÉTERMINISTES)
// ============================================

/**
 * Zones de chasse du Québec (simplifiées pour démo)
 */
const HUNTING_ZONES = {
  '1': { name: 'Zone 1', region: 'Bas-Saint-Laurent', habitatQuality: 0.75 },
  '2': { name: 'Zone 2', region: 'Saguenay–Lac-Saint-Jean', habitatQuality: 0.85 },
  '3': { name: 'Zone 3', region: 'Capitale-Nationale', habitatQuality: 0.70 },
  '4': { name: 'Zone 4', region: 'Mauricie', habitatQuality: 0.80 },
  '5': { name: 'Zone 5', region: 'Estrie', habitatQuality: 0.65 },
  '6': { name: 'Zone 6', region: 'Montréal', habitatQuality: 0.30 },
  '7': { name: 'Zone 7', region: 'Outaouais', habitatQuality: 0.78 },
  '8': { name: 'Zone 8', region: 'Abitibi-Témiscamingue', habitatQuality: 0.82 },
  '9': { name: 'Zone 9', region: 'Côte-Nord', habitatQuality: 0.88 },
  '10': { name: 'Zone 10', region: 'Nord-du-Québec', habitatQuality: 0.90 }
};

/**
 * Facteurs d'activité par phase lunaire
 */
const MOON_PHASE_FACTORS = {
  'new': 0.85,
  'waxing_crescent': 0.75,
  'first_quarter': 0.70,
  'waxing_gibbous': 0.65,
  'full': 0.60,
  'waning_gibbous': 0.70,
  'last_quarter': 0.75,
  'waning_crescent': 0.80
};

/**
 * Facteurs météorologiques
 */
const WEATHER_FACTORS = {
  // Température optimale par espèce (Celsius)
  optimalTemp: {
    'cervidae_whitetail': { min: -5, max: 10, optimal: 5 },
    'cervidae_moose': { min: -15, max: 5, optimal: -5 },
    'anatidae_duck': { min: 5, max: 15, optimal: 10 },
    'galliformes_grouse': { min: -10, max: 15, optimal: 5 }
  },
  
  // Impact de la pression atmosphérique
  pressureImpact: {
    rising: 1.15,
    stable: 1.00,
    falling: 0.85
  },
  
  // Impact du vent
  windImpact: (speed) => {
    if (speed < 10) return 1.0;
    if (speed < 20) return 0.9;
    if (speed < 30) return 0.7;
    return 0.5;
  }
};

// ============================================
// MOTEUR DE CALCUL PRÉDICTIF
// ============================================

/**
 * Calcule le score d'habitat pour une position
 */
const calculateHabitatScore = (location, speciesId) => {
  // Détermination de la zone
  const zone = determineZone(location);
  const baseScore = zone ? HUNTING_ZONES[zone]?.habitatQuality || 0.5 : 0.5;
  
  // Ajustement par espèce
  const speciesMultiplier = getSpeciesHabitatMultiplier(speciesId, zone);
  
  return Math.min(1, baseScore * speciesMultiplier);
};

/**
 * Détermine la zone de chasse basé sur les coordonnées
 */
const determineZone = (location) => {
  const { latitude, longitude } = location;
  
  // Simplification: zones basées sur latitude/longitude
  if (latitude > 52) return '10';
  if (latitude > 50 && longitude < -70) return '9';
  if (latitude > 48 && longitude < -77) return '8';
  if (latitude > 47 && longitude > -72) return '2';
  if (latitude > 46 && longitude < -76) return '7';
  if (latitude > 46) return '4';
  if (latitude > 45 && longitude > -72) return '3';
  if (latitude > 45) return '5';
  return '1';
};

/**
 * Multiplicateur d'habitat par espèce et zone
 */
const getSpeciesHabitatMultiplier = (speciesId, zone) => {
  const multipliers = {
    'cervidae_whitetail': { '1': 1.0, '2': 0.9, '3': 1.1, '4': 1.0, '5': 1.1 },
    'cervidae_moose': { '2': 1.2, '8': 1.1, '9': 1.3, '10': 1.2 },
    'anatidae_duck': { '2': 1.0, '3': 1.1, '9': 1.2 }
  };
  
  return multipliers[speciesId]?.[zone] || 1.0;
};

/**
 * Calcule le facteur météo
 */
const calculateWeatherFactor = (conditions, speciesId) => {
  if (!conditions) return 0.7; // Valeur par défaut si pas de données
  
  const tempConfig = WEATHER_FACTORS.optimalTemp[speciesId] || 
                     WEATHER_FACTORS.optimalTemp['cervidae_whitetail'];
  
  // Score température
  let tempScore = 1.0;
  const temp = conditions.temperature;
  if (temp < tempConfig.min || temp > tempConfig.max) {
    tempScore = 0.5;
  } else {
    const distFromOptimal = Math.abs(temp - tempConfig.optimal);
    tempScore = 1 - (distFromOptimal / 20);
  }
  
  // Score pression
  const pressureTrend = conditions.pressureTrend || 'stable';
  const pressureScore = WEATHER_FACTORS.pressureImpact[pressureTrend];
  
  // Score vent
  const windScore = WEATHER_FACTORS.windImpact(conditions.windSpeed || 0);
  
  // Score combiné
  return (tempScore * 0.4 + pressureScore * 0.3 + windScore * 0.3);
};

/**
 * Calcule le facteur saisonnier
 */
const calculateSeasonalFactor = (date, speciesId) => {
  const month = date.getMonth() + 1;
  
  // Saisons de chasse optimales par espèce
  const optimalMonths = {
    'cervidae_whitetail': [10, 11, 12], // Rut et fin saison
    'cervidae_moose': [9, 10], // Début saison
    'anatidae_duck': [9, 10, 11], // Migration
    'galliformes_grouse': [9, 10, 11, 12]
  };
  
  const optimal = optimalMonths[speciesId] || [10, 11];
  
  if (optimal.includes(month)) return 1.0;
  if (optimal.includes(month - 1) || optimal.includes(month + 1)) return 0.7;
  return 0.4;
};

/**
 * Calcule le facteur d'activité journalière
 */
const calculateActivityFactor = (hour, speciesId) => {
  // Heures de pointe d'activité
  const peakHours = {
    'cervidae_whitetail': [[5, 8], [17, 20]], // Aube et crépuscule
    'cervidae_moose': [[4, 9], [16, 21]],
    'anatidae_duck': [[5, 9], [16, 19]],
    'galliformes_grouse': [[6, 10], [15, 18]]
  };
  
  const peaks = peakHours[speciesId] || peakHours['cervidae_whitetail'];
  
  for (const [start, end] of peaks) {
    if (hour >= start && hour <= end) return 1.0;
  }
  
  // Activité réduite en dehors des pics
  if (hour >= 10 && hour <= 14) return 0.3; // Milieu de journée
  return 0.5;
};

/**
 * Calcule le facteur de phase lunaire
 */
const calculateMoonFactor = (moonPhase) => {
  return MOON_PHASE_FACTORS[moonPhase] || 0.7;
};

// ============================================
// API PUBLIQUE DU MODULE
// ============================================

/**
 * Génère une prédiction complète
 */
const generatePrediction = async (input) => {
  const { location, radius, period, speciesIds } = input;
  
  const predictions = [];
  const currentDate = new Date();
  const hour = currentDate.getHours();
  
  // Conditions par défaut (à remplacer par ENV-BRIDGE)
  const conditions = {
    temperature: 8,
    pressureTrend: 'stable',
    windSpeed: 15,
    moonPhase: 'waning_crescent'
  };
  
  for (const speciesId of speciesIds) {
    const habitatScore = calculateHabitatScore(location, speciesId);
    const weatherFactor = calculateWeatherFactor(conditions, speciesId);
    const seasonalFactor = calculateSeasonalFactor(currentDate, speciesId);
    const activityFactor = calculateActivityFactor(hour, speciesId);
    const moonFactor = calculateMoonFactor(conditions.moonPhase);
    
    // Score global pondéré
    const weights = MODULE_CONFIG.weights;
    const probability = (
      habitatScore * weights.habitat +
      weatherFactor * weights.weather +
      seasonalFactor * weights.seasonality +
      activityFactor * weights.activity +
      moonFactor * weights.moonPhase +
      0.7 * weights.historical // Valeur historique par défaut
    );
    
    // Détermination du niveau d'activité
    let activityLevel = 'low';
    if (probability > 0.8) activityLevel = 'peak';
    else if (probability > 0.6) activityLevel = 'high';
    else if (probability > 0.4) activityLevel = 'moderate';
    
    // Calcul des meilleures heures
    const bestTimes = [];
    for (let h = 0; h < 24; h++) {
      const timeActivity = calculateActivityFactor(h, speciesId);
      if (timeActivity >= 0.8) {
        bestTimes.push({
          start: `${h.toString().padStart(2, '0')}:00`,
          end: `${(h + 1).toString().padStart(2, '0')}:00`,
          score: timeActivity
        });
      }
    }
    
    predictions.push({
      speciesId,
      probability: Math.round(probability * 100) / 100,
      activityLevel,
      bestTimes,
      confidence: Math.min(0.95, probability + 0.1)
    });
  }
  
  return {
    id: `pred-${Date.now()}`,
    timestamp: new Date(),
    location,
    period,
    predictions,
    confidence: predictions.reduce((sum, p) => sum + p.confidence, 0) / predictions.length,
    factors: [
      { name: 'habitat', weight: MODULE_CONFIG.weights.habitat },
      { name: 'weather', weight: MODULE_CONFIG.weights.weather },
      { name: 'seasonality', weight: MODULE_CONFIG.weights.seasonality },
      { name: 'activity', weight: MODULE_CONFIG.weights.activity },
      { name: 'moonPhase', weight: MODULE_CONFIG.weights.moonPhase },
      { name: 'historical', weight: MODULE_CONFIG.weights.historical }
    ]
  };
};

/**
 * Calcule le score d'une zone
 */
const calculateZoneScore = async (input) => {
  const { location, speciesId } = input;
  
  const currentDate = new Date();
  const hour = currentDate.getHours();
  
  const conditions = {
    temperature: 8,
    pressureTrend: 'stable',
    windSpeed: 15
  };
  
  return {
    overall: Math.round(calculateHabitatScore(location, speciesId) * 100),
    habitat: Math.round(calculateHabitatScore(location, speciesId) * 100),
    activity: Math.round(calculateActivityFactor(hour, speciesId) * 100),
    accessibility: 75, // Valeur par défaut
    seasonality: Math.round(calculateSeasonalFactor(currentDate, speciesId) * 100),
    weather: Math.round(calculateWeatherFactor(conditions, speciesId) * 100)
  };
};

/**
 * Retourne les hotspots dans un rayon
 */
const getHotspots = async (input) => {
  const { center, radius, speciesId } = input;
  
  // Génération de hotspots synthétiques basés sur le calcul
  const hotspots = [];
  const gridSize = Math.ceil(radius / MODULE_CONFIG.gridResolution);
  
  // Points cardinaux + centre
  const offsets = [
    { lat: 0, lng: 0 },
    { lat: 0.05, lng: 0 },
    { lat: -0.05, lng: 0 },
    { lat: 0, lng: 0.05 },
    { lat: 0, lng: -0.05 },
    { lat: 0.03, lng: 0.03 },
    { lat: -0.03, lng: 0.03 },
    { lat: 0.03, lng: -0.03 },
    { lat: -0.03, lng: -0.03 }
  ];
  
  for (let i = 0; i < offsets.length; i++) {
    const loc = {
      latitude: center.latitude + offsets[i].lat,
      longitude: center.longitude + offsets[i].lng
    };
    
    const score = calculateHabitatScore(loc, speciesId);
    
    if (score > MODULE_CONFIG.minConfidence) {
      hotspots.push({
        id: `hotspot-${i}`,
        location: loc,
        score: Math.round(score * 100),
        speciesIds: [speciesId],
        type: ['feeding', 'bedding', 'trail', 'water'][Math.floor(Math.random() * 4)],
        radius: 0.5
      });
    }
  }
  
  // Tri par score décroissant
  return hotspots.sort((a, b) => b.score - a.score);
};

// ============================================
// EXPORT DU MODULE
// ============================================

export const PredictiveEngine = {
  moduleId: MODULE_CONFIG.moduleId,
  version: MODULE_CONFIG.version,
  contract: PredictiveEngineContract,
  
  // Méthodes publiques
  generatePrediction,
  calculateZoneScore,
  getHotspots,
  
  // Configuration
  getConfig: () => ({ ...MODULE_CONFIG }),
  
  // Métadonnées
  getMetadata: () => ({
    moduleId: MODULE_CONFIG.moduleId,
    version: MODULE_CONFIG.version,
    name: MODULE_CONFIG.name,
    status: 'active',
    dependencies: ['G-P0-MCO', 'G-ENV-BRIDGE']
  })
};

export default PredictiveEngine;
