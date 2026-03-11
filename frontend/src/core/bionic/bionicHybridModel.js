/**
 * BIONIC™ Hybrid Model
 * Modèle hybride entreprise-grade (règles + IA)
 * Niveau 1: Moteur de règles
 * Niveau 2: IA ajustant le score final
 */

import { getBionicConfig } from './bionicConfig';
import { getScoresForWaypoint } from './bionicScoring';

const API_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * Règles d'ajustement du moteur de règles (Niveau 1)
 */
const ADJUSTMENT_RULES = {
  // Bonus pour combinaisons favorables
  HABITAT_RUT_SYNERGY: {
    condition: (scores) => scores.score_H >= 70 && scores.score_R >= 70,
    adjustment: 8,
    description: 'Synergie habitat-rut optimale'
  },
  FEEDING_RESTING_PROXIMITY: {
    condition: (scores, data) => 
      data.feedingData?.distance < 200 && data.restingData?.distance < 300,
    adjustment: 6,
    description: 'Zone alimentation et repos proches'
  },
  CORRIDOR_AFFUT_COMBO: {
    condition: (scores) => scores.score_A >= 75 && scores.score_T >= 65,
    adjustment: 5,
    description: 'Position d\'affût sur corridor'
  },
  TRANSITION_ZONE_BONUS: {
    condition: (scores, data) => data.isTransition === true,
    adjustment: 7,
    description: 'Zone de transition écotone'
  },
  WATER_COMPLEX_BONUS: {
    condition: (scores, data) => 
      data.hydroFeatures?.hasConfluence || data.hydroFeatures?.hasMeander,
    adjustment: 5,
    description: 'Complexité hydrographique élevée'
  },
  
  // Pénalités pour conditions défavorables
  HIGH_PRESSURE_PENALTY: {
    condition: (scores, data) => data.humanPressure > 70,
    adjustment: -12,
    description: 'Forte pression humaine'
  },
  EXPOSED_POSITION_PENALTY: {
    condition: (scores, data) => data.coverDensity === 'sparse' && data.slope > 20,
    adjustment: -8,
    description: 'Position exposée sans couvert'
  },
  POOR_ACCESS_PENALTY: {
    condition: (scores) => scores.score_T < 40,
    adjustment: -5,
    description: 'Accès difficile'
  },
  
  // Ajustements contextuels
  OPTIMAL_STAND_TYPE: {
    condition: (scores, data) => 
      ['tremblais', 'cedriere', 'erabliere'].includes(data.standType),
    adjustment: 4,
    description: 'Peuplement forestier optimal'
  },
  DOMINANT_POSITION: {
    condition: (scores, data) => data.relativeElevation > 30,
    adjustment: 3,
    description: 'Position dominante'
  }
};

/**
 * Applique le moteur de règles (Niveau 1)
 * @param {Object} scores - Scores BIONIC calculés
 * @param {Object} data - Données brutes du waypoint
 */
export const applyRulesEngine = (scores, data) => {
  let adjustedScore = scores.score_Bionic;
  const appliedRules = [];
  
  Object.entries(ADJUSTMENT_RULES).forEach(([ruleName, rule]) => {
    try {
      if (rule.condition(scores, data)) {
        adjustedScore += rule.adjustment;
        appliedRules.push({
          rule: ruleName,
          adjustment: rule.adjustment,
          description: rule.description
        });
      }
    } catch (e) {
      // Règle non applicable (données manquantes)
    }
  });
  
  // Normaliser entre 0 et 100
  adjustedScore = Math.min(100, Math.max(0, adjustedScore));
  
  return {
    score: Math.round(adjustedScore),
    appliedRules,
    rulesAdjustment: adjustedScore - scores.score_Bionic
  };
};

/**
 * Appelle l'IA pour ajustement fin (Niveau 2)
 * @param {Object} scores - Scores après Niveau 1
 * @param {Object} data - Données contextuelles
 * @param {Object} weather - Conditions météo actuelles
 */
export const applyAIAdjustment = async (scores, data, weather = null) => {
  try {
    const response = await fetch(`${API_URL}/api/bionic/hybrid/ai-adjust`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scores,
        waypointData: {
          latitude: data.latitude,
          longitude: data.longitude,
          standType: data.standType,
          slope: data.slope,
          aspect: data.aspect,
          elevation: data.elevation,
          relativeElevation: data.relativeElevation,
          waterDistance: data.waterDistance,
          ndvi: data.ndvi,
          isTransition: data.isTransition,
          coverDensity: data.coverDensity,
          humanPressure: data.humanPressure
        },
        weather: weather ? {
          temperature: weather.temperatureC,
          windSpeed: weather.windSpeedKmh,
          windDirection: weather.windDirectionDeg,
          humidity: weather.humidityPercent,
          pressure: weather.pressureHpa,
          thermalState: weather.thermalState,
          frontType: weather.frontType
        } : null,
        context: {
          season: getCurrentSeason(),
          timeOfDay: getTimeOfDay(),
          moonPhase: getMoonPhase()
        }
      })
    });
    
    if (!response.ok) {
      console.warn('AI adjustment failed, using rules-only score');
      return {
        finalScore: scores.score,
        aiAdjustment: 0,
        aiRecommendations: [],
        aiConfidence: 0
      };
    }
    
    const result = await response.json();
    return {
      finalScore: Math.min(100, Math.max(0, result.adjusted_score)),
      aiAdjustment: result.adjustment || 0,
      aiRecommendations: result.recommendations || [],
      aiConfidence: result.confidence || 0,
      aiReasoning: result.reasoning || ''
    };
  } catch (error) {
    console.error('AI adjustment error:', error);
    return {
      finalScore: scores.score,
      aiAdjustment: 0,
      aiRecommendations: [],
      aiConfidence: 0
    };
  }
};

/**
 * Calcule le score BIONIC final avec le modèle hybride complet
 * @param {Object} waypointData - Données du waypoint
 * @param {Object} weather - Conditions météo (optionnel)
 * @param {boolean} useAI - Utiliser l'ajustement IA (défaut: true)
 */
export const calculateHybridScore = async (waypointData, weather = null, useAI = true) => {
  // Étape 1: Calcul des scores BIONIC de base
  const baseScores = getScoresForWaypoint(waypointData);
  
  // Étape 2: Application du moteur de règles (Niveau 1)
  const rulesResult = applyRulesEngine(baseScores, waypointData);
  
  // Étape 3: Ajustement IA si activé (Niveau 2)
  let aiResult = null;
  if (useAI) {
    aiResult = await applyAIAdjustment(rulesResult, waypointData, weather);
  }
  
  // Score final
  const finalScore = aiResult?.finalScore ?? rulesResult.score;
  
  // Construire le résultat complet
  return {
    // Scores de base
    ...baseScores,
    
    // Score après règles
    scoreAfterRules: rulesResult.score,
    appliedRules: rulesResult.appliedRules,
    rulesAdjustment: rulesResult.rulesAdjustment,
    
    // Score final après IA
    score_Bionic_final: finalScore,
    aiAdjustment: aiResult?.aiAdjustment || 0,
    aiRecommendations: aiResult?.aiRecommendations || [],
    aiConfidence: aiResult?.aiConfidence || 0,
    aiReasoning: aiResult?.aiReasoning || '',
    
    // Métadonnées
    metadata: {
      calculatedAt: new Date().toISOString(),
      useAI,
      weatherIncluded: !!weather,
      season: getCurrentSeason(),
      timeOfDay: getTimeOfDay()
    },
    
    // Rating final
    rating: getRating(finalScore)
  };
};

/**
 * Classification du score
 */
const getRating = (score) => {
  const thresholds = getBionicConfig().thresholds;
  if (score >= thresholds.excellent) return { level: 'excellent', label: 'Zone exceptionnelle', color: '#22c55e' };
  if (score >= thresholds.good) return { level: 'good', label: 'Très bon potentiel', color: '#84cc16' };
  if (score >= thresholds.moderate) return { level: 'moderate', label: 'Potentiel correct', color: '#eab308' };
  if (score >= thresholds.low) return { level: 'low', label: 'Potentiel limité', color: '#f97316' };
  return { level: 'poor', label: 'Zone défavorable', color: '#ef4444' };
};

/**
 * Utilitaires temporels
 */
const getCurrentSeason = () => {
  const month = new Date().getMonth();
  if (month >= 2 && month <= 4) return 'spring';
  if (month >= 5 && month <= 7) return 'summer';
  if (month >= 8 && month <= 10) return 'fall';
  return 'winter';
};

const getTimeOfDay = () => {
  const hour = new Date().getHours();
  if (hour >= 5 && hour < 9) return 'dawn';
  if (hour >= 9 && hour < 17) return 'day';
  if (hour >= 17 && hour < 21) return 'dusk';
  return 'night';
};

const getMoonPhase = () => {
  // Calcul simplifié de la phase lunaire
  const date = new Date();
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const day = date.getDate();
  
  // Formule de calcul approximatif
  let c = Math.floor((year - 1900) / 100);
  let y = year - 1900 - 100 * c;
  let m = month;
  let d = day;
  
  if (m < 3) { m += 12; y -= 1; }
  
  let n = d + Math.floor(2.6 * m - 5.39) + y + Math.floor(y / 4) + Math.floor(c / 4) - 2 * c - 3;
  n = ((n % 29) + 29) % 29;
  
  if (n < 4) return 'new';
  if (n < 11) return 'waxing';
  if (n < 18) return 'full';
  if (n < 25) return 'waning';
  return 'new';
};

/**
 * Génère des recommandations basées sur le score hybride
 */
export const generateRecommendations = (hybridResult, weather = null) => {
  const recommendations = [];
  const scores = hybridResult;
  
  // Recommandations basées sur les scores par catégorie
  if (scores.score_H >= 75) {
    recommendations.push({
      type: 'positive',
      category: 'habitat',
      text: 'Habitat de qualité supérieure - présence probable de gibier'
    });
  }
  
  if (scores.score_R >= 70) {
    recommendations.push({
      type: 'positive',
      category: 'rut',
      text: 'Zone propice au rut - activité accrue en automne'
    });
  }
  
  if (scores.score_A >= 75) {
    recommendations.push({
      type: 'positive',
      category: 'affut',
      text: 'Position d\'affût favorable - bonne visibilité et couvert'
    });
  }
  
  if (scores.score_S >= 70) {
    recommendations.push({
      type: 'action',
      category: 'saline',
      text: 'Potentiel pour installation de saline'
    });
  }
  
  // Alertes
  if (scores.score_T < 40) {
    recommendations.push({
      type: 'warning',
      category: 'access',
      text: 'Accès difficile - prévoir plus de temps'
    });
  }
  
  // Recommandations météo
  if (weather) {
    if (weather.thermalState === 'ascending') {
      recommendations.push({
        type: 'warning',
        category: 'weather',
        text: 'Thermiques ascendants - approcher par le bas'
      });
    }
    
    if (weather.windSpeedKmh > 20) {
      recommendations.push({
        type: 'info',
        category: 'weather',
        text: `Vent de ${Math.round(weather.windSpeedKmh)} km/h - gibier moins mobile`
      });
    }
  }
  
  // Ajouter les recommandations IA si présentes
  if (hybridResult.aiRecommendations?.length > 0) {
    recommendations.push(...hybridResult.aiRecommendations.map(rec => ({
      type: 'ai',
      category: 'strategy',
      text: rec
    })));
  }
  
  return recommendations;
};

export default {
  applyRulesEngine,
  applyAIAdjustment,
  calculateHybridScore,
  generateRecommendations
};
