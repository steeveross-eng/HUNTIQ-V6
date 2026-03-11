/**
 * BIONIC™ Strategy Engine
 * Moteur de stratégie LIVE pour recommandations tactiques
 */

import { calculateHybridScore, generateRecommendations } from './bionicHybridModel';
import { getWindDirectionText } from './bionicWeatherEngine';

/**
 * Génère une stratégie complète pour un waypoint
 * @param {Object} waypoint - Données du waypoint
 * @param {Object} bionicScores - Scores BIONIC calculés
 * @param {Object} weather - Conditions météo actuelles
 * @param {Object} territoryContext - Contexte du territoire
 */
export const getStrategyForWaypoint = async (waypoint, bionicScores, weather, territoryContext = {}) => {
  // Calculer le score du stand actuel et projections
  const standScore = await calculateStandProjections(waypoint, bionicScores, weather);
  
  // Calculer le chemin d'approche optimal
  const approachPath = calculateApproachPath(waypoint, weather, territoryContext);
  
  // Analyser les mouvements probables du gibier
  const gameMovement = analyzeGameMovement(waypoint, weather, bionicScores, territoryContext);
  
  // Évaluer les risques
  const risks = evaluateRisks(waypoint, weather, territoryContext);
  
  // Recommandations produits
  const products = recommendProducts(waypoint, bionicScores, weather);
  
  // Flags LIVE
  const liveFlags = calculateLiveFlags(standScore, risks, gameMovement);
  
  return {
    timestamp: new Date().toISOString(),
    waypoint: {
      id: waypoint.id,
      name: waypoint.name,
      coordinates: [waypoint.latitude, waypoint.longitude]
    },
    
    // Score du stand
    stand: standScore,
    
    // Chemin d'approche
    approachPath,
    
    // Mouvement du gibier
    gameMovement,
    
    // Risques
    risks,
    
    // Produits recommandés
    products,
    
    // Flags LIVE
    liveFlags,
    
    // Résumé exécutif
    summary: generateSummary(standScore, gameMovement, risks, liveFlags)
  };
};

/**
 * Calcule les projections du score du stand
 */
const calculateStandProjections = async (waypoint, bionicScores, weather) => {
  const currentScore = bionicScores.score_Bionic_final || bionicScores.score_Bionic;
  
  // Projections basées sur l'évolution météo
  let score1h = currentScore;
  let score3h = currentScore;
  
  if (weather?.hourlyForecast) {
    // Ajustement pour +1h
    const forecast1h = weather.hourlyForecast[1];
    if (forecast1h) {
      score1h = adjustScoreForWeather(currentScore, forecast1h, weather);
    }
    
    // Ajustement pour +3h
    const forecast3h = weather.hourlyForecast[3];
    if (forecast3h) {
      score3h = adjustScoreForWeather(currentScore, forecast3h, weather);
    }
  }
  
  // Ajustement temporel (aube/crépuscule bonus)
  const hour = new Date().getHours();
  const timeMultiplier = getTimeMultiplier(hour);
  const timeMultiplier1h = getTimeMultiplier((hour + 1) % 24);
  const timeMultiplier3h = getTimeMultiplier((hour + 3) % 24);
  
  return {
    current: Math.round(currentScore * timeMultiplier),
    in1h: Math.round(score1h * timeMultiplier1h),
    in3h: Math.round(score3h * timeMultiplier3h),
    trend: score3h > currentScore ? 'improving' : score3h < currentScore ? 'degrading' : 'stable',
    peakTime: findPeakTime(weather?.hourlyForecast, currentScore)
  };
};

/**
 * Ajuste le score en fonction des conditions météo projetées
 */
const adjustScoreForWeather = (baseScore, forecast, currentWeather) => {
  let adjusted = baseScore;
  
  // Impact du vent
  const windDiff = forecast.windSpeed - currentWeather.windSpeedKmh;
  if (windDiff > 10) adjusted -= 5;
  else if (windDiff < -10) adjusted += 3;
  
  // Impact température
  const tempDiff = forecast.temperatureC - currentWeather.temperatureC;
  if (Math.abs(tempDiff) > 5) adjusted -= 3;
  
  // Impact précipitations
  if (forecast.precipitationMm > 2) adjusted -= 8;
  else if (forecast.precipitationMm > 0 && forecast.precipitationMm < 2) adjusted += 2;
  
  return Math.max(0, Math.min(100, adjusted));
};

/**
 * Multiplicateur temporel (aube/crépuscule favorables)
 */
const getTimeMultiplier = (hour) => {
  if (hour >= 5 && hour <= 8) return 1.15; // Aube
  if (hour >= 17 && hour <= 20) return 1.12; // Crépuscule
  if (hour >= 9 && hour <= 16) return 0.95; // Milieu de journée
  return 0.85; // Nuit
};

/**
 * Trouve l'heure de pointe dans les prochaines heures
 */
const findPeakTime = (hourlyForecast, baseScore) => {
  if (!hourlyForecast || hourlyForecast.length === 0) return null;
  
  let peakScore = baseScore;
  let peakTime = null;
  
  hourlyForecast.slice(0, 12).forEach((forecast, index) => {
    const hour = new Date(forecast.time).getHours();
    const timeMultiplier = getTimeMultiplier(hour);
    const projectedScore = baseScore * timeMultiplier;
    
    if (projectedScore > peakScore) {
      peakScore = projectedScore;
      peakTime = forecast.time;
    }
  });
  
  return peakTime;
};

/**
 * Calcule le chemin d'approche optimal
 */
const calculateApproachPath = (waypoint, weather, context) => {
  if (!weather) {
    return {
      geometry: null,
      stealthScore: 70,
      scentRisk: 'medium',
      visualRisk: 'medium',
      distanceMeters: 0,
      recommendedDirection: 'N'
    };
  }
  
  // Direction d'approche opposée au vent
  const windDir = weather.windDirectionDeg;
  const approachDir = (windDir + 180) % 360;
  
  // Score de discrétion basé sur les conditions
  let stealthScore = 80;
  
  // Vent idéal pour masquer les bruits
  if (weather.windSpeedKmh >= 8 && weather.windSpeedKmh <= 18) {
    stealthScore += 10;
  } else if (weather.windSpeedKmh < 5) {
    stealthScore -= 15;
  }
  
  // Couverture nuageuse (affecte visibilité)
  if (weather.cloudCoverPercent > 60) stealthScore += 5;
  
  // Risque olfactif basé sur l'état thermique
  let scentRisk = 'low';
  if (weather.thermalState === 'ascending') {
    scentRisk = 'high';
    stealthScore -= 10;
  } else if (weather.thermalState === 'descending') {
    scentRisk = 'low';
    stealthScore += 5;
  } else {
    scentRisk = 'medium';
  }
  
  // Risque visuel basé sur l'heure et la couverture
  const hour = new Date().getHours();
  let visualRisk = 'medium';
  if (hour < 7 || hour > 18) {
    visualRisk = 'low';
    stealthScore += 5;
  } else if (weather.cloudCoverPercent < 30) {
    visualRisk = 'high';
    stealthScore -= 5;
  }
  
  return {
    geometry: null, // Serait calculé avec données terrain réelles
    stealthScore: Math.max(0, Math.min(100, stealthScore)),
    scentRisk,
    visualRisk,
    distanceMeters: context.approachDistance || 200,
    recommendedDirection: getWindDirectionText(approachDir),
    windInfo: {
      direction: getWindDirectionText(windDir),
      speed: weather.windSpeedKmh
    }
  };
};

/**
 * Analyse les mouvements probables du gibier
 */
const analyzeGameMovement = (waypoint, weather, bionicScores, context) => {
  const corridorScore = bionicScores.score_T || 50;
  
  // Corridor principal basé sur les scores et la topographie
  const primaryDirection = calculatePrimaryCorridorDirection(waypoint, weather, context);
  
  // Fenêtre d'arrivée estimée
  const hour = new Date().getHours();
  let arrivalStart, arrivalEnd;
  
  if (hour >= 4 && hour < 9) {
    // Tôt le matin - gibier revient vers zones de repos
    arrivalStart = '05:30';
    arrivalEnd = '08:00';
  } else if (hour >= 15 && hour < 20) {
    // Fin d'après-midi - gibier vers zones d'alimentation
    arrivalStart = '16:30';
    arrivalEnd = '19:30';
  } else {
    // Autres heures - mouvement réduit
    arrivalStart = 'Variable';
    arrivalEnd = 'Variable';
  }
  
  // Impact du vent sur les mouvements
  let windImpact = 'neutral';
  if (weather) {
    if (weather.windSpeedKmh > 25) {
      windImpact = 'penalty';
    } else if (weather.windSpeedKmh >= 8 && weather.windSpeedKmh <= 18) {
      windImpact = 'boost';
    }
  }
  
  return {
    primaryCorridor: {
      directionDeg: primaryDirection,
      directionText: getWindDirectionText(primaryDirection),
      probability: Math.min(95, corridorScore + 20)
    },
    secondaryCorridor: {
      directionDeg: (primaryDirection + 90) % 360,
      directionText: getWindDirectionText((primaryDirection + 90) % 360),
      probability: Math.max(20, corridorScore - 20)
    },
    arrivalWindow: {
      start: arrivalStart,
      end: arrivalEnd
    },
    windImpact,
    activityLevel: getActivityLevel(hour, weather)
  };
};

/**
 * Calcule la direction du corridor principal
 */
const calculatePrimaryCorridorDirection = (waypoint, weather, context) => {
  // Logique simplifiée - serait basée sur données terrain réelles
  let baseDirection = 45; // Nord-Est par défaut
  
  // Ajuster selon l'aspect du terrain si disponible
  if (waypoint.aspect !== undefined) {
    baseDirection = (waypoint.aspect + 180) % 360; // Opposé à la pente
  }
  
  return baseDirection;
};

/**
 * Niveau d'activité du gibier
 */
const getActivityLevel = (hour, weather) => {
  let level = 'moderate';
  
  // Heures de pointe
  if ((hour >= 5 && hour <= 8) || (hour >= 17 && hour <= 20)) {
    level = 'high';
  } else if (hour >= 11 && hour <= 14) {
    level = 'low';
  }
  
  // Ajustement météo
  if (weather) {
    if (weather.frontType === 'cold') {
      level = level === 'high' ? 'very_high' : 'high';
    } else if (weather.precipitationMm > 5) {
      level = level === 'low' ? 'very_low' : 'low';
    }
  }
  
  return level;
};

/**
 * Évalue les risques
 */
const evaluateRisks = (waypoint, weather, context) => {
  const risks = [];
  
  // Pression humaine
  const humanPressure = context.humanPressure || 30;
  if (humanPressure > 60) {
    risks.push({
      type: 'humanPressure',
      level: 'high',
      value: humanPressure,
      description: 'Zone fréquentée - risque de dérangement'
    });
  } else if (humanPressure > 40) {
    risks.push({
      type: 'humanPressure',
      level: 'medium',
      value: humanPressure,
      description: 'Pression humaine modérée'
    });
  }
  
  // Risque d'inversion thermique
  if (weather) {
    const thermalRisk = weather.thermalRiskLevel || 0;
    if (thermalRisk > 50) {
      risks.push({
        type: 'thermalInversion',
        level: thermalRisk > 70 ? 'high' : 'medium',
        value: thermalRisk,
        description: 'Risque d\'inversion thermique - odeurs piégées'
      });
    }
    
    // Bruit (vent faible amplifie les bruits)
    if (weather.windSpeedKmh < 5) {
      risks.push({
        type: 'noise',
        level: 'high',
        value: 80,
        description: 'Vent très faible - bruits amplifiés'
      });
    }
  }
  
  // Heure de sortie recommandée
  const hour = new Date().getHours();
  let recommendedExitTime = null;
  
  if (hour >= 5 && hour <= 9) {
    recommendedExitTime = '10:00'; // Après activité matinale
  } else if (hour >= 15 && hour <= 19) {
    recommendedExitTime = '20:30'; // Après crépuscule
  }
  
  return {
    list: risks,
    overallLevel: risks.some(r => r.level === 'high') ? 'high' : 
                  risks.some(r => r.level === 'medium') ? 'medium' : 'low',
    recommendedExitTime
  };
};

/**
 * Recommandations de produits
 */
const recommendProducts = (waypoint, bionicScores, weather) => {
  const recommendations = [];
  
  // Score de saline élevé = recommander attractant
  if (bionicScores.score_S >= 60) {
    let attractantType = 'mineral';
    let quantity = 500;
    
    // Ajuster selon la saison
    const month = new Date().getMonth();
    if (month >= 8 && month <= 10) {
      // Automne - rut
      attractantType = 'urine_doe';
      quantity = 100;
    } else if (month >= 4 && month <= 7) {
      // Été - minéraux
      attractantType = 'mineral_block';
      quantity = 2000;
    }
    
    recommendations.push({
      attractantType,
      quantityGrams: quantity,
      placementOffsetMeters: 20,
      placementDirectionDeg: weather ? (weather.windDirectionDeg + 45) % 360 : 90,
      frequencyHours: attractantType.includes('urine') ? 48 : 168
    });
  }
  
  // Zone d'affût = recommander camouflage
  if (bionicScores.score_A >= 70) {
    recommendations.push({
      productType: 'cover_scent',
      usage: 'Appliquer avant l\'approche',
      importance: 'high'
    });
  }
  
  return recommendations;
};

/**
 * Calcule les flags LIVE
 */
const calculateLiveFlags = (standScore, risks, gameMovement) => {
  return {
    isOptimalNow: standScore.current >= 70 && 
                  risks.overallLevel !== 'high' && 
                  ['high', 'very_high'].includes(gameMovement.activityLevel),
    
    willDegradeSoon: standScore.trend === 'degrading' && 
                     standScore.in3h < standScore.current - 10,
    
    isRiskyNow: risks.overallLevel === 'high' || 
                risks.list.some(r => r.type === 'thermalInversion' && r.level === 'high'),
    
    peakWindowActive: gameMovement.activityLevel === 'high' || 
                      gameMovement.activityLevel === 'very_high'
  };
};

/**
 * Génère un résumé exécutif
 */
const generateSummary = (standScore, gameMovement, risks, liveFlags) => {
  const parts = [];
  
  // État actuel
  if (liveFlags.isOptimalNow) {
    parts.push('CONDITIONS OPTIMALES - Fenêtre de chasse active');
  } else if (liveFlags.isRiskyNow) {
    parts.push('RISQUES ÉLEVÉS - Prudence recommandée');
  } else {
    parts.push(`Score actuel: ${standScore.current}/100`);
  }
  
  // Tendance
  if (standScore.trend === 'improving') {
    parts.push(`Amélioration attendue (${standScore.in3h}/100 dans 3h)`);
  } else if (standScore.trend === 'degrading') {
    parts.push(`Dégradation prévue (${standScore.in3h}/100 dans 3h)`);
  }
  
  // Activité gibier
  parts.push(`Activité ${
    gameMovement.activityLevel === 'very_high' ? 'très forte' :
    gameMovement.activityLevel === 'high' ? 'forte' :
    gameMovement.activityLevel === 'moderate' ? 'modérée' :
    gameMovement.activityLevel === 'low' ? 'faible' : 'très faible'
  }`);
  
  // Risques principaux
  if (risks.list.length > 0) {
    const mainRisk = risks.list[0];
    parts.push(`${mainRisk.description}`);
  }
  
  return parts.join(' • ');
};

export default {
  getStrategyForWaypoint
};
