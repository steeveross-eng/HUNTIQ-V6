/**
 * PHASE G — CONTRATS D'API INTERNES
 * 
 * Définition des interfaces et contrats pour tous les modules PHASE G.
 * Ces contrats sont FIGÉS et ne peuvent être modifiés sans ordre du COPILOT MAÎTRE.
 * 
 * @module phase-g/contracts
 * @version G-CONTRACTS-v1.0.0
 * @phase G-P0
 * @status FIGÉ
 */

// ============================================
// TYPES DE BASE
// ============================================

/**
 * Coordonnées géographiques
 */
export const GeoCoordinates = {
  latitude: 'number', // -90 to 90
  longitude: 'number', // -180 to 180
  altitude: 'number|null', // meters, optional
  accuracy: 'number|null' // meters, optional
};

/**
 * Période temporelle
 */
export const TimePeriod = {
  start: 'Date',
  end: 'Date',
  timezone: 'string' // IANA timezone
};

/**
 * Espèce de gibier
 */
export const Species = {
  id: 'string',
  name: 'string',
  nameFr: 'string',
  nameEn: 'string',
  category: 'string', // 'cervidae', 'anatidae', 'galliformes', etc.
  subcategory: 'string|null',
  huntingSeason: 'SeasonDefinition',
  behaviorProfile: 'string' // reference to behavioral model
};

/**
 * Définition de saison de chasse
 */
export const SeasonDefinition = {
  zones: 'string[]', // Zone IDs
  startDate: 'string', // MM-DD format
  endDate: 'string', // MM-DD format
  restrictions: 'string[]',
  quotas: 'object|null'
};

// ============================================
// CONTRAT MOTEUR PRÉDICTIF (G-P0-MPT)
// ============================================

/**
 * Interface du Moteur Prédictif Territorial
 * Version: G-P0-MPT-v1.0.0
 */
export const PredictiveEngineContract = {
  // Identifiant du module
  moduleId: 'G-P0-MPT',
  version: '1.0.0',
  
  // Méthodes exposées
  methods: {
    /**
     * Génère une prédiction pour une zone et période données
     * @param {GeoCoordinates} location - Centre de la zone
     * @param {number} radius - Rayon en km
     * @param {TimePeriod} period - Période de prédiction
     * @param {string[]} speciesIds - IDs des espèces ciblées
     * @returns {PredictionResult}
     */
    generatePrediction: {
      input: {
        location: 'GeoCoordinates',
        radius: 'number',
        period: 'TimePeriod',
        speciesIds: 'string[]'
      },
      output: 'PredictionResult',
      async: true
    },
    
    /**
     * Calcule le score d'une zone
     * @param {GeoCoordinates} location - Centre de la zone
     * @param {string} speciesId - ID de l'espèce
     * @returns {ZoneScore}
     */
    calculateZoneScore: {
      input: {
        location: 'GeoCoordinates',
        speciesId: 'string'
      },
      output: 'ZoneScore',
      async: true
    },
    
    /**
     * Retourne les hotspots dans un rayon
     * @param {GeoCoordinates} center - Centre de recherche
     * @param {number} radius - Rayon en km
     * @param {string} speciesId - ID de l'espèce
     * @returns {Hotspot[]}
     */
    getHotspots: {
      input: {
        center: 'GeoCoordinates',
        radius: 'number',
        speciesId: 'string'
      },
      output: 'Hotspot[]',
      async: true
    }
  },
  
  // Types de sortie
  outputTypes: {
    PredictionResult: {
      id: 'string',
      timestamp: 'Date',
      location: 'GeoCoordinates',
      period: 'TimePeriod',
      predictions: 'SpeciesPrediction[]',
      confidence: 'number', // 0-1
      factors: 'PredictionFactor[]'
    },
    
    SpeciesPrediction: {
      speciesId: 'string',
      probability: 'number', // 0-1
      activityLevel: 'string', // 'low', 'moderate', 'high', 'peak'
      bestTimes: 'TimeWindow[]',
      confidence: 'number'
    },
    
    ZoneScore: {
      overall: 'number', // 0-100
      habitat: 'number',
      activity: 'number',
      accessibility: 'number',
      seasonality: 'number',
      weather: 'number'
    },
    
    Hotspot: {
      id: 'string',
      location: 'GeoCoordinates',
      score: 'number',
      speciesIds: 'string[]',
      type: 'string', // 'feeding', 'bedding', 'trail', 'water'
      radius: 'number'
    }
  }
};

// ============================================
// CONTRAT MODÈLES COMPORTEMENTAUX (G-P0-MCO)
// ============================================

/**
 * Interface des Modèles Comportementaux
 * Version: G-P0-MCO-v1.0.0
 */
export const BehavioralModelsContract = {
  moduleId: 'G-P0-MCO',
  version: '1.0.0',
  
  methods: {
    /**
     * Retourne le profil comportemental d'une espèce
     * @param {string} speciesId - ID de l'espèce
     * @returns {BehaviorProfile}
     */
    getSpeciesProfile: {
      input: { speciesId: 'string' },
      output: 'BehaviorProfile',
      async: false
    },
    
    /**
     * Calcule l'activité prévue selon les conditions
     * @param {string} speciesId - ID de l'espèce
     * @param {EnvironmentalConditions} conditions - Conditions actuelles
     * @returns {ActivityPrediction}
     */
    predictActivity: {
      input: {
        speciesId: 'string',
        conditions: 'EnvironmentalConditions'
      },
      output: 'ActivityPrediction',
      async: true
    },
    
    /**
     * Retourne les patterns saisonniers
     * @param {string} speciesId - ID de l'espèce
     * @param {string} season - Saison ('spring', 'summer', 'fall', 'winter')
     * @returns {SeasonalPattern}
     */
    getSeasonalPattern: {
      input: {
        speciesId: 'string',
        season: 'string'
      },
      output: 'SeasonalPattern',
      async: false
    }
  },
  
  outputTypes: {
    BehaviorProfile: {
      speciesId: 'string',
      activityPeaks: 'TimeWindow[]', // Dawn, dusk, etc.
      feedingHabits: 'FeedingPattern',
      movementPatterns: 'MovementPattern',
      socialBehavior: 'string', // 'solitary', 'herd', 'family'
      sensitivityFactors: 'SensitivityFactor[]'
    },
    
    ActivityPrediction: {
      speciesId: 'string',
      timestamp: 'Date',
      activityLevel: 'number', // 0-1
      confidence: 'number',
      dominantBehavior: 'string',
      recommendations: 'string[]'
    },
    
    SeasonalPattern: {
      speciesId: 'string',
      season: 'string',
      rutPeriod: 'TimePeriod|null',
      migrationPattern: 'MigrationInfo|null',
      feedingIntensity: 'number',
      territorialBehavior: 'number'
    }
  }
};

// ============================================
// CONTRAT ENV-BRIDGE (APIs Externes)
// ============================================

/**
 * Interface ENV-BRIDGE pour APIs externes
 * Version: G-ENV-BRIDGE-v1.0.0
 */
export const EnvBridgeContract = {
  moduleId: 'G-ENV-BRIDGE',
  version: '1.0.0',
  
  methods: {
    /**
     * Récupère les données météo
     * @param {GeoCoordinates} location - Position
     * @returns {WeatherData}
     */
    getWeather: {
      input: { location: 'GeoCoordinates' },
      output: 'WeatherData',
      async: true,
      fallback: 'getWeatherFallback'
    },
    
    /**
     * Récupère les prévisions météo
     * @param {GeoCoordinates} location - Position
     * @param {number} days - Nombre de jours
     * @returns {WeatherForecast[]}
     */
    getForecast: {
      input: {
        location: 'GeoCoordinates',
        days: 'number'
      },
      output: 'WeatherForecast[]',
      async: true,
      fallback: 'getForecastFallback'
    },
    
    /**
     * Récupère les données de réglementation
     * @param {string} zoneId - ID de la zone
     * @param {string} speciesId - ID de l'espèce
     * @returns {RegulationData}
     */
    getRegulations: {
      input: {
        zoneId: 'string',
        speciesId: 'string'
      },
      output: 'RegulationData',
      async: true,
      fallback: 'getRegulationsFallback'
    }
  },
  
  // Configuration obligatoire
  config: {
    timeout: 5000, // ms
    retries: 3,
    cacheEnabled: true,
    cacheTTL: 300, // seconds
    auditLogging: true
  },
  
  outputTypes: {
    WeatherData: {
      timestamp: 'Date',
      temperature: 'number', // Celsius
      humidity: 'number', // %
      pressure: 'number', // hPa
      windSpeed: 'number', // km/h
      windDirection: 'number', // degrees
      precipitation: 'number', // mm
      cloudCover: 'number', // %
      visibility: 'number', // km
      moonPhase: 'string',
      sunriseTime: 'Date',
      sunsetTime: 'Date'
    }
  }
};

// ============================================
// EXPORTS
// ============================================

export default {
  GeoCoordinates,
  TimePeriod,
  Species,
  SeasonDefinition,
  PredictiveEngineContract,
  BehavioralModelsContract,
  EnvBridgeContract
};
