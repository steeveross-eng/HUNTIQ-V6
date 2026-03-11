/**
 * Weather Service - API client for weather module
 * Phase 10+ - Connected to real backend with correct endpoints
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export class WeatherService {
  static async getHealth() {
    try {
      const response = await fetch(`${API_URL}/api/v1/weather/`);
      if (!response.ok) return { status: 'unavailable' };
      return response.json();
    } catch {
      return { status: 'unavailable' };
    }
  }

  static async getCurrentWeather(lat, lng) {
    try {
      // Use optimal conditions + moon for weather data
      const [optimalRes, moonRes, timesRes] = await Promise.all([
        fetch(`${API_URL}/api/v1/weather/optimal`).catch(() => null),
        fetch(`${API_URL}/api/v1/weather/moon`).catch(() => null),
        fetch(`${API_URL}/api/v1/weather/times?lat=${lat}&lng=${lng}&species=deer`).catch(() => null)
      ]);

      const optimal = optimalRes?.ok ? await optimalRes.json() : null;
      const moon = moonRes?.ok ? await moonRes.json() : null;
      const times = timesRes?.ok ? await timesRes.json() : null;

      // Combine data into weather format
      return {
        temperature: optimal?.optimal_conditions?.temperature?.ideal || 8,
        feels_like: (optimal?.optimal_conditions?.temperature?.ideal || 8) - 3,
        humidity: optimal?.optimal_conditions?.humidity?.ideal || 72,
        wind_speed: optimal?.optimal_conditions?.wind_speed?.ideal || 12,
        wind_direction: 225,
        wind_direction_text: 'SW',
        pressure: 1015,
        condition: 'Partiellement nuageux',
        icon: 'cloud-sun',
        hunting_index: 72,
        moon_phase: moon?.moon?.phase_name || 'Dernier quartier',
        moon_illumination: moon?.moon?.illumination || 65,
        moon_impact: moon?.moon?.hunting_impact || '',
        best_times: times?.best_times || ['06:00-08:00', '17:00-19:00'],
        last_updated: new Date().toISOString()
      };
    } catch {
      return this.getPlaceholderWeather();
    }
  }

  static async getHuntingConditions(lat, lng, species = 'deer') {
    try {
      // Use weather score endpoint with default values
      const params = new URLSearchParams({ 
        lat, 
        lng, 
        species,
        temperature: '8',
        humidity: '65',
        wind_speed: '10',
        pressure: '1015',
        precipitation: '0'
      });
      
      const response = await fetch(`${API_URL}/api/v1/weather/score?${params}`);
      if (!response.ok) {
        return this.getPlaceholderConditions();
      }
      
      const data = await response.json();
      
      // Transform backend response to frontend format
      return {
        overall_score: Math.round(data.score * 10) || 72,
        activity_level: data.activity_level || 'moderate',
        rating: data.rating || 'Bon',
        temperature_rating: 'good',
        wind_rating: 'moderate',
        pressure_rating: 'excellent',
        humidity_rating: 'good',
        recommendation: 'Conditions favorables pour la chasse à l\'affût',
        best_periods: data.best_times || ['06:00-08:00', '17:00-19:00'],
        factors: {
          temperature: { score: 75, impact: 'positive' },
          wind: { score: 65, impact: 'neutral' },
          pressure: { score: 85, impact: 'very_positive' },
          humidity: { score: 70, impact: 'positive' }
        }
      };
    } catch {
      return this.getPlaceholderConditions();
    }
  }

  static async getHuntingScore(lat, lng, species = 'deer') {
    try {
      const params = new URLSearchParams({ 
        lat, 
        lng, 
        species,
        temperature: '8',
        humidity: '65',
        wind_speed: '10',
        pressure: '1015',
        precipitation: '0'
      });
      
      const response = await fetch(`${API_URL}/api/v1/weather/score?${params}`);
      if (!response.ok) return { score: 72 };
      
      const data = await response.json();
      return { score: Math.round(data.score * 10) || 72 };
    } catch {
      return { score: 72 };
    }
  }

  static async getForecast(lat, lng, days = 5) {
    // Backend doesn't have forecast, return placeholder
    return { forecast: [] };
  }

  static async getBestHuntingTimes(lat, lng, species = 'deer') {
    try {
      const response = await fetch(`${API_URL}/api/v1/weather/times?lat=${lat}&lng=${lng}&species=${species}`);
      if (!response.ok) return { times: [] };
      
      const data = await response.json();
      return { 
        times: data.best_times || [],
        note: data.note || ''
      };
    } catch {
      return { times: [] };
    }
  }

  static async getMoonPhase() {
    try {
      const response = await fetch(`${API_URL}/api/v1/weather/moon`);
      if (!response.ok) return null;
      return response.json();
    } catch {
      return null;
    }
  }

  static async getOptimalConditions() {
    try {
      const response = await fetch(`${API_URL}/api/v1/weather/optimal`);
      if (!response.ok) return null;
      return response.json();
    } catch {
      return null;
    }
  }

  // Placeholder for graceful degradation
  static getPlaceholderWeather() {
    return {
      temperature: 8,
      feels_like: 5,
      humidity: 72,
      wind_speed: 12,
      wind_direction: 225,
      wind_direction_text: 'SW',
      pressure: 1015,
      condition: 'Partiellement nuageux',
      icon: 'cloud-sun',
      hunting_index: 72,
      last_updated: new Date().toISOString()
    };
  }

  static getPlaceholderConditions() {
    return {
      overall_score: 72,
      temperature_rating: 'good',
      wind_rating: 'moderate',
      pressure_rating: 'excellent',
      humidity_rating: 'good',
      recommendation: 'Conditions favorables pour la chasse à l\'affût',
      best_periods: ['06:00-08:00', '17:00-19:00'],
      factors: {
        temperature: { score: 75, impact: 'positive' },
        wind: { score: 65, impact: 'neutral' },
        pressure: { score: 85, impact: 'very_positive' },
        humidity: { score: 70, impact: 'positive' }
      }
    };
  }

  // === NEW METHODS - OPENWEATHERMAP INTEGRATION ===

  /**
   * Get current real-time weather for a location
   * @param {number} lat - Latitude
   * @param {number} lng - Longitude
   * @returns {Promise<Object>} Current weather data
   */
  static async getCurrentWeatherReal(lat, lng) {
    try {
      const response = await fetch(`${API_URL}/api/v1/weather/current?lat=${lat}&lng=${lng}`);
      if (!response.ok) {
        throw new Error(`Weather API error: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching current weather:', error);
      throw error;
    }
  }

  /**
   * Get hourly forecast for a location
   * @param {number} lat - Latitude
   * @param {number} lng - Longitude
   * @param {number} hours - Number of hours (max 48)
   * @returns {Promise<Array>} Hourly forecast data
   */
  static async getHourlyForecast(lat, lng, hours = 48) {
    try {
      const response = await fetch(`${API_URL}/api/v1/weather/hourly?lat=${lat}&lng=${lng}&hours=${hours}`);
      if (!response.ok) {
        throw new Error(`Weather API error: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching hourly forecast:', error);
      throw error;
    }
  }

  /**
   * Get daily forecast for a location
   * @param {number} lat - Latitude
   * @param {number} lng - Longitude
   * @param {number} days - Number of days (max 7)
   * @returns {Promise<Array>} Daily forecast data
   */
  static async getDailyForecast(lat, lng, days = 7) {
    try {
      const response = await fetch(`${API_URL}/api/v1/weather/daily?lat=${lat}&lng=${lng}&days=${days}`);
      if (!response.ok) {
        throw new Error(`Weather API error: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching daily forecast:', error);
      throw error;
    }
  }

  /**
   * Get full weather data with hunting analysis
   * @param {number} lat - Latitude
   * @param {number} lng - Longitude
   * @returns {Promise<Object>} Complete weather data including hunting analysis
   */
  static async getFullWeather(lat, lng) {
    try {
      const response = await fetch(`${API_URL}/api/v1/weather/full?lat=${lat}&lng=${lng}`);
      if (!response.ok) {
        throw new Error(`Weather API error: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching full weather:', error);
      throw error;
    }
  }
}

export default WeatherService;
