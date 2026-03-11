/**
 * useBionicWeather Hook
 * Récupère et gère les données météo LIVE pour BIONIC
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { 
  fetchWeatherData, 
  findNextOptimalWindow,
  getWindDirectionText,
  getWeatherDescription 
} from '@/core/bionic';

const DEFAULT_POLL_INTERVAL = 10 * 60 * 1000; // 10 minutes par défaut

const useBionicWeather = (latitude, longitude, options = {}) => {
  const {
    autoFetch = true,
    pollInterval = DEFAULT_POLL_INTERVAL,
    enabled = true
  } = options;
  
  const [weather, setWeather] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  
  const intervalRef = useRef(null);
  const isMountedRef = useRef(true);
  
  /**
   * Récupère les données météo
   */
  const fetchWeather = useCallback(async () => {
    if (!latitude || !longitude || !enabled) return null;
    
    try {
      setIsLoading(true);
      setError(null);
      
      const data = await fetchWeatherData(latitude, longitude);
      
      if (isMountedRef.current) {
        setWeather(data);
        setLastUpdate(new Date().toISOString());
      }
      
      return data;
    } catch (err) {
      if (isMountedRef.current) {
        setError(err.message);
        console.error('Weather fetch error:', err);
      }
      return null;
    } finally {
      if (isMountedRef.current) {
        setIsLoading(false);
      }
    }
  }, [latitude, longitude, enabled]);
  
  /**
   * Démarre le polling automatique
   */
  const startPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    
    intervalRef.current = setInterval(() => {
      fetchWeather();
    }, pollInterval);
  }, [fetchWeather, pollInterval]);
  
  /**
   * Arrête le polling
   */
  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);
  
  /**
   * Force un rafraîchissement
   */
  const refresh = useCallback(() => {
    return fetchWeather();
  }, [fetchWeather]);
  
  // Effet pour le fetch initial et le polling
  useEffect(() => {
    isMountedRef.current = true;
    
    if (autoFetch && enabled && latitude && longitude) {
      fetchWeather();
      startPolling();
    }
    
    return () => {
      isMountedRef.current = false;
      stopPolling();
    };
  }, [autoFetch, enabled, latitude, longitude, fetchWeather, startPolling, stopPolling]);
  
  // Données dérivées
  const nextOptimalWindow = weather ? findNextOptimalWindow(weather) : null;
  
  const windInfo = weather ? {
    direction: getWindDirectionText(weather.windDirectionDeg),
    directionDeg: weather.windDirectionDeg,
    speed: weather.windSpeedKmh,
    gusts: weather.windGustsKmh
  } : null;
  
  const thermalInfo = weather ? {
    state: weather.thermalState,
    riskLevel: weather.thermalRiskLevel,
    stateLabel: weather.thermalState === 'ascending' ? 'Ascendants' :
                weather.thermalState === 'descending' ? 'Descendants' : 'Stables'
  } : null;
  
  const huntingScore = weather?.huntingConditions?.score || 0;
  const huntingRating = weather?.huntingConditions?.rating || 'unknown';
  
  return {
    // Données météo complètes
    weather,
    
    // État
    isLoading,
    error,
    lastUpdate,
    
    // Données simplifiées
    temperature: weather?.temperatureC,
    humidity: weather?.humidityPercent,
    pressure: weather?.pressureHpa,
    precipitation: weather?.precipitationMm,
    cloudCover: weather?.cloudCoverPercent,
    weatherCode: weather?.weatherCode,
    weatherDescription: weather ? getWeatherDescription(weather.weatherCode) : null,
    
    // Vent
    windInfo,
    
    // Thermiques
    thermalInfo,
    
    // Soleil
    sunrise: weather?.sunrise,
    sunset: weather?.sunset,
    
    // Front météo
    frontType: weather?.frontType,
    
    // Analyse chasse
    huntingScore,
    huntingRating,
    huntingFactors: weather?.huntingConditions?.factors || [],
    
    // Prochaine fenêtre optimale
    nextOptimalWindow,
    
    // Prévisions horaires
    hourlyForecast: weather?.hourlyForecast || [],
    
    // Actions
    refresh,
    startPolling,
    stopPolling,
    
    // Statut
    isEnabled: enabled,
    hasData: !!weather
  };
};

export default useBionicWeather;
