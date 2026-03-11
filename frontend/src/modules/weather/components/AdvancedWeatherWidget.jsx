/**
 * AdvancedWeatherWidget - Widget météo avancé pour Dashboard BIONIC
 * Version: 1.0.0
 * 
 * Affiche les données météo en temps réel avec:
 * - Conditions actuelles détaillées
 * - Prévisions horaires (24h)
 * - Prévisions 7 jours
 * - Score de chasse et recommandations
 * - Phase lunaire
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { 
  Cloud, Sun, CloudRain, Wind, Droplets, Thermometer, Eye, 
  Moon, RefreshCw, MapPin, Clock, Calendar, Target, ChevronLeft, ChevronRight
} from 'lucide-react';
import WeatherService from '../WeatherService';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Weather icon mapping
const getWeatherIcon = (iconCode, size = 'h-8 w-8') => {
  const iconMap = {
    '01d': <Sun className={`${size} text-yellow-400`} />,
    '01n': <Moon className={`${size} text-blue-300`} />,
    '02d': <Cloud className={`${size} text-gray-300`} />,
    '02n': <Cloud className={`${size} text-gray-400`} />,
    '03d': <Cloud className={`${size} text-gray-400`} />,
    '03n': <Cloud className={`${size} text-gray-500`} />,
    '04d': <Cloud className={`${size} text-gray-500`} />,
    '04n': <Cloud className={`${size} text-gray-600`} />,
    '09d': <CloudRain className={`${size} text-blue-400`} />,
    '09n': <CloudRain className={`${size} text-blue-500`} />,
    '10d': <CloudRain className={`${size} text-blue-400`} />,
    '10n': <CloudRain className={`${size} text-blue-500`} />,
    '11d': <CloudRain className={`${size} text-purple-400`} />,
    '11n': <CloudRain className={`${size} text-purple-500`} />,
    '13d': <Cloud className={`${size} text-blue-200`} />,
    '13n': <Cloud className={`${size} text-blue-300`} />,
    '50d': <Cloud className={`${size} text-gray-400`} />,
    '50n': <Cloud className={`${size} text-gray-500`} />,
  };
  return iconMap[iconCode] || <Cloud className={`${size} text-gray-400`} />;
};

// Activity level colors
const getActivityColor = (level) => {
  const colors = {
    peak: 'bg-green-500',
    high: 'bg-emerald-500',
    moderate: 'bg-yellow-500',
    low: 'bg-red-500'
  };
  return colors[level] || 'bg-gray-500';
};

const getActivityLabel = (level) => {
  const labels = {
    peak: 'Optimale',
    high: 'Élevée',
    moderate: 'Modérée',
    low: 'Faible'
  };
  return labels[level] || level;
};

const AdvancedWeatherWidget = ({ 
  lat = 46.8139, 
  lng = -71.2080,
  showHourly = true,
  showDaily = true,
  compact = false 
}) => {
  const [weatherData, setWeatherData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hourlyScrollIndex, setHourlyScrollIndex] = useState(0);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Fetch weather data
  const fetchWeather = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await WeatherService.getFullWeather(lat, lng);
      setWeatherData(data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Weather fetch error:', err);
      setError('Impossible de charger les données météo');
    } finally {
      setLoading(false);
    }
  }, [lat, lng]);

  useEffect(() => {
    fetchWeather();
    // Refresh every 30 minutes
    const interval = setInterval(fetchWeather, 30 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchWeather]);

  // Scroll hourly forecast
  const scrollHourly = (direction) => {
    const maxIndex = Math.max(0, (weatherData?.hourly?.length || 0) - 8);
    setHourlyScrollIndex(prev => {
      if (direction === 'left') return Math.max(0, prev - 4);
      return Math.min(maxIndex, prev + 4);
    });
  };

  if (loading) {
    return (
      <Card className="bg-gray-900/50 border-gray-700" data-testid="weather-widget-loading">
        <CardContent className="p-6 flex items-center justify-center">
          <RefreshCw className="h-8 w-8 text-amber-500 animate-spin" />
          <span className="ml-3 text-gray-400">Chargement météo...</span>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="bg-gray-900/50 border-red-500/30" data-testid="weather-widget-error">
        <CardContent className="p-6 text-center">
          <Cloud className="h-12 w-12 text-red-400 mx-auto mb-3" />
          <p className="text-red-400">{error}</p>
          <Button 
            variant="ghost" 
            onClick={fetchWeather}
            className="mt-4 text-amber-400"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Réessayer
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!weatherData) return null;

  const { current, hourly, daily, hunting_analysis, location } = weatherData;

  return (
    <Card className="bg-gray-900/50 border-gray-700" data-testid="advanced-weather-widget">
      {/* Header */}
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {getWeatherIcon(current.condition.icon, 'h-10 w-10')}
            <div>
              <CardTitle className="text-2xl text-white flex items-center gap-2">
                {Math.round(current.temperature)}°C
                <span className="text-base text-gray-400 font-normal">
                  Ressenti {Math.round(current.feels_like)}°C
                </span>
              </CardTitle>
              <p className="text-gray-400 capitalize">{current.condition.description}</p>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-1 text-gray-400 text-sm">
              <MapPin className="h-4 w-4" />
              <span>{location.city || `${lat.toFixed(2)}, ${lng.toFixed(2)}`}</span>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={fetchWeather}
              className="text-gray-500 hover:text-amber-400 p-1"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Current Details Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-gray-800/50 rounded-lg p-3 flex items-center gap-2">
            <Wind className="h-5 w-5 text-blue-400" />
            <div>
              <p className="text-xs text-gray-500">Vent</p>
              <p className="text-white font-medium">
                {current.wind.speed} km/h {current.wind.direction_text}
              </p>
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-3 flex items-center gap-2">
            <Droplets className="h-5 w-5 text-cyan-400" />
            <div>
              <p className="text-xs text-gray-500">Humidité</p>
              <p className="text-white font-medium">{current.humidity}%</p>
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-3 flex items-center gap-2">
            <Thermometer className="h-5 w-5 text-orange-400" />
            <div>
              <p className="text-xs text-gray-500">Pression</p>
              <p className="text-white font-medium">{current.pressure} hPa</p>
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-3 flex items-center gap-2">
            <Eye className="h-5 w-5 text-gray-400" />
            <div>
              <p className="text-xs text-gray-500">Visibilité</p>
              <p className="text-white font-medium">{(current.visibility / 1000).toFixed(0)} km</p>
            </div>
          </div>
        </div>

        {/* Hunting Analysis */}
        <div className="bg-amber-900/20 border border-amber-500/30 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5 text-amber-400" />
              <span className="text-amber-400 font-semibold">Conditions de Chasse</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold text-white">{hunting_analysis.overall_score}</span>
              <span className="text-gray-400">/10</span>
              <Badge className={`${getActivityColor(hunting_analysis.activity_level)} text-white ml-2`}>
                {getActivityLabel(hunting_analysis.activity_level)}
              </Badge>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-gray-500 mb-1">Meilleurs moments</p>
              <div className="flex flex-wrap gap-2">
                {hunting_analysis.best_times_today.map((time, i) => (
                  <Badge key={i} variant="outline" className="border-amber-500/50 text-amber-300">
                    <Clock className="h-3 w-3 mr-1" />
                    {time}
                  </Badge>
                ))}
              </div>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">Phase lunaire</p>
              <div className="flex items-center gap-2">
                <Moon className="h-4 w-4 text-blue-300" />
                <span className="text-white">{hunting_analysis.moon.phase_name}</span>
                <span className="text-gray-500 text-sm">({hunting_analysis.moon.illumination}%)</span>
              </div>
            </div>
          </div>
          
          {hunting_analysis.recommendations.length > 0 && (
            <div className="mt-3 pt-3 border-t border-amber-500/20">
              <p className="text-xs text-gray-500 mb-1">Recommandations</p>
              <ul className="text-sm text-gray-300 space-y-1">
                {hunting_analysis.recommendations.slice(0, 3).map((rec, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-amber-400 mt-1">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Hourly Forecast */}
        {showHourly && hourly && hourly.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-400 flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Prévisions horaires
              </h3>
              <div className="flex gap-1">
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => scrollHourly('left')}
                  disabled={hourlyScrollIndex === 0}
                  className="p-1 h-6 w-6"
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => scrollHourly('right')}
                  disabled={hourlyScrollIndex >= hourly.length - 8}
                  className="p-1 h-6 w-6"
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div className="flex gap-2 overflow-hidden">
              {hourly.slice(hourlyScrollIndex, hourlyScrollIndex + 8).map((hour, i) => (
                <div 
                  key={i} 
                  className="flex-1 min-w-[60px] bg-gray-800/30 rounded-lg p-2 text-center"
                >
                  <p className="text-xs text-gray-500">
                    {new Date(hour.timestamp).toLocaleTimeString('fr-CA', { hour: '2-digit', minute: '2-digit' })}
                  </p>
                  <div className="my-1 flex justify-center">
                    {getWeatherIcon(hour.condition.icon, 'h-6 w-6')}
                  </div>
                  <p className="text-white font-medium">{Math.round(hour.temperature)}°</p>
                  <p className="text-xs text-blue-400">{Math.round(hour.precipitation_probability)}%</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Daily Forecast */}
        {showDaily && daily && daily.length > 0 && !compact && (
          <div>
            <h3 className="text-sm font-medium text-gray-400 flex items-center gap-2 mb-2">
              <Calendar className="h-4 w-4" />
              Prévisions 7 jours
            </h3>
            <div className="space-y-2">
              {daily.map((day, i) => (
                <div 
                  key={i}
                  className="flex items-center justify-between bg-gray-800/30 rounded-lg px-3 py-2"
                >
                  <div className="flex items-center gap-3 w-1/3">
                    <span className="text-gray-400 text-sm w-20">
                      {i === 0 ? "Aujourd'hui" : new Date(day.date).toLocaleDateString('fr-CA', { weekday: 'short', day: 'numeric' })}
                    </span>
                    {getWeatherIcon(day.condition.icon, 'h-6 w-6')}
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-blue-400 text-sm">
                      {Math.round(day.precipitation_probability)}%
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="text-gray-500">{Math.round(day.temperature.min)}°</span>
                      <div className="w-16 h-1 bg-gray-700 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-blue-400 to-orange-400 rounded-full"
                          style={{ 
                            width: `${((day.temperature.max - day.temperature.min) / 30) * 100}%`,
                            marginLeft: `${((day.temperature.min + 20) / 50) * 100}%`
                          }}
                        />
                      </div>
                      <span className="text-white font-medium">{Math.round(day.temperature.max)}°</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Last Updated */}
        {lastUpdated && (
          <p className="text-xs text-gray-600 text-right">
            Mis à jour : {lastUpdated.toLocaleTimeString('fr-CA')}
          </p>
        )}
      </CardContent>
    </Card>
  );
};

export default AdvancedWeatherWidget;
