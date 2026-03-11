/**
 * BIONIC™ Weather Engine
 * Moteur météo LIVE pour analyse stratégique en temps réel
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * États thermiques possibles
 */
export const THERMAL_STATES = {
  STABLE: 'stable',
  ASCENDING: 'ascending',
  DESCENDING: 'descending'
};

/**
 * Types de fronts météo
 */
export const FRONT_TYPES = {
  NONE: 'none',
  COLD: 'cold',
  WARM: 'warm',
  UNSTABLE: 'unstable'
};

/**
 * Récupère les données météo depuis le backend V8.2 (OpenWeatherMap + cache 30min)
 * Fallback vers Open-Meteo si le backend est indisponible
 * @param {number} lat - Latitude
 * @param {number} lng - Longitude
 */
export const fetchWeatherData = async (lat, lng) => {
  // STRATEGIE: Backend OWM (cache 30min) → Fallback Open-Meteo
  try {
    return await fetchFromBackendOWM(lat, lng);
  } catch (backendErr) {
    console.warn('[Weather] Backend OWM indisponible, fallback Open-Meteo:', backendErr.message);
    return await fetchFromOpenMeteo(lat, lng);
  }
};

/**
 * Fetch depuis notre backend V8.2 (OpenWeatherMap + cache TTL 30min)
 */
const fetchFromBackendOWM = async (lat, lng) => {
  const [weatherResp, forecastResp, influenceResp] = await Promise.all([
    fetch(`${API_URL}/api/v1/weather/now?lat=${lat}&lng=${lng}`),
    fetch(`${API_URL}/api/v1/weather/forecast?lat=${lat}&lng=${lng}`),
    fetch(`${API_URL}/api/v1/weather/influence?lat=${lat}&lng=${lng}`),
  ]);

  if (!weatherResp.ok) throw new Error(`Backend weather: ${weatherResp.status}`);

  const weather = await weatherResp.json();
  const forecast = forecastResp.ok ? await forecastResp.json() : { forecasts: [] };
  const influence = influenceResp.ok ? await influenceResp.json() : null;

  // Build hourly forecast from backend forecast data
  const hourlyForecast = (forecast.forecasts || []).slice(0, 24).map(f => ({
    time: f.dt_txt,
    temperatureC: f.temperature_c,
    humidity: f.humidity_pct,
    precipitationProb: 0,
    precipitationMm: f.precipitation_3h_mm / 3,
    cloudCover: f.cloud_cover_pct,
    windSpeed: f.wind_speed_kmh,
    windDirection: f.wind_direction_deg,
  }));

  // Compute thermal state from forecast temps
  const now = new Date();
  const currentHour = now.getHours();
  const temps = hourlyForecast.map(h => h.temperatureC).filter(Boolean);
  let thermalState = THERMAL_STATES.STABLE;
  if (temps.length >= 3) {
    const trend = (temps[1] - temps[0]) + (temps[2] - temps[1]);
    if (trend > 1) thermalState = THERMAL_STATES.ASCENDING;
    else if (trend < -1) thermalState = THERMAL_STATES.DESCENDING;
  }

  // Build compatible current object for analyzeHuntingConditions
  const current = {
    wind_speed_10m: weather.wind_speed_kmh,
    wind_gusts_10m: weather.wind_gust_kmh,
    wind_direction_10m: weather.wind_direction_deg,
    temperature_2m: weather.temperature_c,
    apparent_temperature: weather.feels_like_c,
    relative_humidity_2m: weather.humidity_pct,
    surface_pressure: weather.pressure_hpa,
    precipitation: weather.precipitation_1h_mm,
    cloud_cover: weather.cloud_cover_pct,
    weather_code: mapOWMConditionToCode(weather.condition),
  };

  const thermalRiskLevel = calculateThermalRisk(current, thermalState);
  const frontType = determineFrontTypeFromForecast(hourlyForecast);
  const huntingConditions = analyzeHuntingConditions(current, thermalState, frontType);

  return {
    timestamp: weather.timestamp || new Date().toISOString(),
    source: weather.from_cache ? 'owm_cache' : 'owm_live',
    windDirectionDeg: weather.wind_direction_deg,
    windSpeedKmh: weather.wind_speed_kmh,
    windGustsKmh: weather.wind_gust_kmh,
    temperatureC: weather.temperature_c,
    apparentTemperatureC: weather.feels_like_c,
    humidityPercent: weather.humidity_pct,
    pressureHpa: weather.pressure_hpa,
    precipitationMm: weather.precipitation_1h_mm,
    cloudCoverPercent: weather.cloud_cover_pct,
    weatherCode: current.weather_code,
    conditionText: weather.condition_detail,
    conditionIcon: weather.condition_icon,
    sunrise: weather.sunrise ? new Date(weather.sunrise * 1000).toISOString() : null,
    sunset: weather.sunset ? new Date(weather.sunset * 1000).toISOString() : null,
    tempMaxC: weather.temp_max_c,
    tempMinC: weather.temp_min_c,
    thermalState,
    thermalRiskLevel,
    frontType,
    hourlyForecast,
    huntingConditions,
    weatherInfluence: influence?.influence_multipliers || null,
  };
};

/**
 * Map OWM condition text to WMO weather code (for compatibility)
 */
const mapOWMConditionToCode = (condition) => {
  const map = {
    'Clear': 0, 'Clouds': 3, 'Fog': 45, 'Mist': 45, 'Haze': 45,
    'Drizzle': 51, 'Rain': 61, 'Snow': 71, 'Thunderstorm': 95,
  };
  return map[condition] || 2;
};

/**
 * Determine front type from forecast temperature trend
 */
const determineFrontTypeFromForecast = (hourlyForecast) => {
  if (!hourlyForecast || hourlyForecast.length < 3) return FRONT_TYPES.NONE;
  const temps = hourlyForecast.slice(0, 6).map(h => h.temperatureC).filter(Boolean);
  if (temps.length < 2) return FRONT_TYPES.NONE;
  const change = temps[temps.length - 1] - temps[0];
  if (change < -5) return FRONT_TYPES.COLD;
  if (change > 5) return FRONT_TYPES.WARM;
  const variations = temps.reduce((acc, t, i) => i === 0 ? 0 : acc + Math.abs(t - temps[i-1]), 0);
  if (variations > 8) return FRONT_TYPES.UNSTABLE;
  return FRONT_TYPES.NONE;
};

/**
 * Fallback: Récupère les données météo depuis Open-Meteo (API gratuite, sans clé)
 * @param {number} lat - Latitude
 * @param {number} lng - Longitude
 */
const fetchFromOpenMeteo = async (lat, lng) => {
  try {
    // Open-Meteo API - données actuelles + prévisions horaires
    const params = new URLSearchParams({
      latitude: lat,
      longitude: lng,
      current: [
        'temperature_2m',
        'relative_humidity_2m',
        'apparent_temperature',
        'precipitation',
        'weather_code',
        'cloud_cover',
        'surface_pressure',
        'wind_speed_10m',
        'wind_direction_10m',
        'wind_gusts_10m'
      ].join(','),
      hourly: [
        'temperature_2m',
        'relative_humidity_2m',
        'precipitation_probability',
        'precipitation',
        'cloud_cover',
        'wind_speed_10m',
        'wind_direction_10m'
      ].join(','),
      daily: [
        'sunrise',
        'sunset',
        'temperature_2m_max',
        'temperature_2m_min'
      ].join(','),
      timezone: 'America/Toronto',
      forecast_days: 2
    });

    const response = await fetch(
      `https://api.open-meteo.com/v1/forecast?${params}`
    );

    if (!response.ok) {
      throw new Error(`Weather API error: ${response.status}`);
    }

    const data = await response.json();
    return processWeatherData(data);
  } catch (error) {
    console.error('Error fetching weather data:', error);
    throw error;
  }
};

/**
 * Traite les données brutes de l'API météo
 */
const processWeatherData = (data) => {
  const current = data.current;
  const daily = data.daily;
  const hourly = data.hourly;
  
  const now = new Date();
  const currentHour = now.getHours();
  
  // Calculer l'état thermique
  const thermalState = calculateThermalState(hourly, currentHour);
  
  // Calculer le risque thermique
  const thermalRiskLevel = calculateThermalRisk(current, thermalState);
  
  // Déterminer le type de front
  const frontType = determineFrontType(hourly, currentHour);
  
  return {
    timestamp: new Date().toISOString(),
    
    // Données actuelles
    windDirectionDeg: current.wind_direction_10m,
    windSpeedKmh: current.wind_speed_10m,
    windGustsKmh: current.wind_gusts_10m,
    temperatureC: current.temperature_2m,
    apparentTemperatureC: current.apparent_temperature,
    humidityPercent: current.relative_humidity_2m,
    pressureHpa: current.surface_pressure,
    precipitationMm: current.precipitation,
    cloudCoverPercent: current.cloud_cover,
    weatherCode: current.weather_code,
    
    // Lever/coucher du soleil
    sunrise: daily.sunrise[0],
    sunset: daily.sunset[0],
    
    // Températures du jour
    tempMaxC: daily.temperature_2m_max[0],
    tempMinC: daily.temperature_2m_min[0],
    
    // États calculés
    thermalState,
    thermalRiskLevel,
    frontType,
    
    // Prévisions horaires (prochaines 24h)
    hourlyForecast: processHourlyForecast(hourly, currentHour),
    
    // Analyse de la qualité pour la chasse
    huntingConditions: analyzeHuntingConditions(current, thermalState, frontType)
  };
};

/**
 * Calcule l'état thermique (stable, ascendant, descendant)
 */
const calculateThermalState = (hourly, currentHour) => {
  if (!hourly || !hourly.temperature_2m) return THERMAL_STATES.STABLE;
  
  const temps = hourly.temperature_2m;
  const currentIdx = currentHour;
  
  // Comparer avec l'heure précédente et suivante
  const prevTemp = temps[Math.max(0, currentIdx - 1)];
  const currTemp = temps[currentIdx];
  const nextTemp = temps[Math.min(temps.length - 1, currentIdx + 1)];
  
  const trend = (currTemp - prevTemp) + (nextTemp - currTemp);
  
  if (trend > 1) return THERMAL_STATES.ASCENDING;
  if (trend < -1) return THERMAL_STATES.DESCENDING;
  return THERMAL_STATES.STABLE;
};

/**
 * Calcule le niveau de risque thermique (0-100)
 */
const calculateThermalRisk = (current, thermalState) => {
  let risk = 0;
  
  // Température extrême
  if (current.temperature_2m < -20 || current.temperature_2m > 30) {
    risk += 30;
  } else if (current.temperature_2m < -10 || current.temperature_2m > 25) {
    risk += 15;
  }
  
  // Vent fort
  if (current.wind_speed_10m > 30) {
    risk += 25;
  } else if (current.wind_speed_10m > 20) {
    risk += 15;
  } else if (current.wind_speed_10m > 15) {
    risk += 8;
  }
  
  // Rafales
  if (current.wind_gusts_10m > 50) {
    risk += 20;
  } else if (current.wind_gusts_10m > 35) {
    risk += 10;
  }
  
  // État thermique instable
  if (thermalState === THERMAL_STATES.ASCENDING) {
    risk += 15; // Thermiques ascendants = odeurs montent
  }
  
  // Couverture nuageuse (affecte les thermiques)
  if (current.cloud_cover < 20) {
    risk += 10; // Ciel dégagé = thermiques forts en journée
  }
  
  return Math.min(100, risk);
};

/**
 * Détermine le type de front météo
 */
const determineFrontType = (hourly, currentHour) => {
  if (!hourly || !hourly.temperature_2m) return FRONT_TYPES.NONE;
  
  const temps = hourly.temperature_2m;
  const pressures = hourly.surface_pressure || [];
  
  // Regarder les prochaines 6 heures
  const futureTemps = temps.slice(currentHour, currentHour + 6);
  const tempChange = futureTemps[futureTemps.length - 1] - futureTemps[0];
  
  // Chute de température > 5°C en 6h = front froid
  if (tempChange < -5) return FRONT_TYPES.COLD;
  
  // Hausse de température > 5°C en 6h = front chaud
  if (tempChange > 5) return FRONT_TYPES.WARM;
  
  // Variations importantes = instable
  const variations = futureTemps.reduce((acc, temp, i) => {
    if (i === 0) return 0;
    return acc + Math.abs(temp - futureTemps[i - 1]);
  }, 0);
  
  if (variations > 8) return FRONT_TYPES.UNSTABLE;
  
  return FRONT_TYPES.NONE;
};

/**
 * Traite les prévisions horaires
 */
const processHourlyForecast = (hourly, currentHour) => {
  const forecast = [];
  
  for (let i = currentHour; i < Math.min(currentHour + 24, hourly.time.length); i++) {
    forecast.push({
      time: hourly.time[i],
      temperatureC: hourly.temperature_2m[i],
      humidity: hourly.relative_humidity_2m[i],
      precipitationProb: hourly.precipitation_probability?.[i] || 0,
      precipitationMm: hourly.precipitation[i],
      cloudCover: hourly.cloud_cover[i],
      windSpeed: hourly.wind_speed_10m[i],
      windDirection: hourly.wind_direction_10m[i]
    });
  }
  
  return forecast;
};

/**
 * Analyse les conditions pour la chasse
 */
const analyzeHuntingConditions = (current, thermalState, frontType) => {
  let score = 50; // Score de base
  let factors = [];
  
  // Vent idéal : 5-15 km/h
  if (current.wind_speed_10m >= 5 && current.wind_speed_10m <= 15) {
    score += 15;
    factors.push({ type: 'positive', text: 'Vent idéal (5-15 km/h)' });
  } else if (current.wind_speed_10m < 5) {
    score -= 10;
    factors.push({ type: 'negative', text: 'Vent trop faible - odeurs stagnantes' });
  } else if (current.wind_speed_10m > 25) {
    score -= 20;
    factors.push({ type: 'negative', text: 'Vent trop fort' });
  }
  
  // Température
  if (current.temperature_2m >= -5 && current.temperature_2m <= 15) {
    score += 10;
    factors.push({ type: 'positive', text: 'Température favorable' });
  } else if (current.temperature_2m < -15 || current.temperature_2m > 25) {
    score -= 15;
    factors.push({ type: 'negative', text: 'Température extrême' });
  }
  
  // Précipitations
  if (current.precipitation > 0 && current.precipitation < 2) {
    score += 10;
    factors.push({ type: 'positive', text: 'Légère précipitation - masque les bruits' });
  } else if (current.precipitation > 5) {
    score -= 15;
    factors.push({ type: 'negative', text: 'Fortes précipitations' });
  }
  
  // État thermique
  if (thermalState === THERMAL_STATES.DESCENDING) {
    score += 10;
    factors.push({ type: 'positive', text: 'Thermiques descendants - odeurs au sol' });
  } else if (thermalState === THERMAL_STATES.ASCENDING) {
    score -= 10;
    factors.push({ type: 'negative', text: 'Thermiques ascendants - risque odeurs' });
  }
  
  // Front météo
  if (frontType === FRONT_TYPES.COLD) {
    score += 15;
    factors.push({ type: 'positive', text: 'Front froid - activité gibier accrue' });
  } else if (frontType === FRONT_TYPES.UNSTABLE) {
    score -= 10;
    factors.push({ type: 'negative', text: 'Conditions instables' });
  }
  
  // Pression barométrique
  if (current.surface_pressure > 1020) {
    score += 5;
    factors.push({ type: 'positive', text: 'Haute pression - conditions stables' });
  } else if (current.surface_pressure < 1000) {
    score -= 5;
    factors.push({ type: 'warning', text: 'Basse pression - changement météo possible' });
  }
  
  return {
    score: Math.min(100, Math.max(0, score)),
    rating: score >= 70 ? 'excellent' : score >= 50 ? 'good' : score >= 30 ? 'moderate' : 'poor',
    factors
  };
};

/**
 * Calcule la prochaine fenêtre optimale
 */
export const findNextOptimalWindow = (weather) => {
  if (!weather.hourlyForecast) return null;
  
  const windows = [];
  let currentWindow = null;
  
  weather.hourlyForecast.forEach((hour, index) => {
    const conditions = {
      wind_speed_10m: hour.windSpeed,
      temperature_2m: hour.temperatureC,
      precipitation: hour.precipitationMm,
      cloud_cover: hour.cloudCover
    };
    
    const analysis = analyzeHuntingConditions(conditions, THERMAL_STATES.STABLE, FRONT_TYPES.NONE);
    
    if (analysis.score >= 60) {
      if (!currentWindow) {
        currentWindow = {
          start: hour.time,
          end: hour.time,
          avgScore: analysis.score,
          scores: [analysis.score]
        };
      } else {
        currentWindow.end = hour.time;
        currentWindow.scores.push(analysis.score);
        currentWindow.avgScore = currentWindow.scores.reduce((a, b) => a + b, 0) / currentWindow.scores.length;
      }
    } else if (currentWindow) {
      windows.push(currentWindow);
      currentWindow = null;
    }
  });
  
  if (currentWindow) windows.push(currentWindow);
  
  // Retourner la meilleure fenêtre
  return windows.sort((a, b) => b.avgScore - a.avgScore)[0] || null;
};

/**
 * Direction du vent en texte
 */
export const getWindDirectionText = (degrees) => {
  const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 
                      'S', 'SSO', 'SO', 'OSO', 'O', 'ONO', 'NO', 'NNO'];
  const index = Math.round(degrees / 22.5) % 16;
  return directions[index];
};

/**
 * Code météo en description
 */
export const getWeatherDescription = (code) => {
  const descriptions = {
    0: 'Ciel dégagé',
    1: 'Principalement dégagé',
    2: 'Partiellement nuageux',
    3: 'Couvert',
    45: 'Brouillard',
    48: 'Brouillard givrant',
    51: 'Bruine légère',
    53: 'Bruine modérée',
    55: 'Bruine dense',
    61: 'Pluie légère',
    63: 'Pluie modérée',
    65: 'Pluie forte',
    71: 'Neige légère',
    73: 'Neige modérée',
    75: 'Neige forte',
    80: 'Averses légères',
    81: 'Averses modérées',
    82: 'Averses violentes',
    85: 'Averses de neige légères',
    86: 'Averses de neige fortes',
    95: 'Orage',
    96: 'Orage avec grêle légère',
    99: 'Orage avec grêle forte'
  };
  return descriptions[code] || 'Conditions variables';
};

export default {
  fetchWeatherData,
  findNextOptimalWindow,
  getWindDirectionText,
  getWeatherDescription,
  THERMAL_STATES,
  FRONT_TYPES
};
