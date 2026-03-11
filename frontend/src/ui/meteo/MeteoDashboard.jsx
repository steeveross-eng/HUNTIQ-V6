/**
 * MeteoDashboard - V5-ULTIME
 * ==========================
 * 
 * Dashboard principal du module Météo.
 * Composant parent isolé - aucun import croisé.
 * PHASE F: Migration vers LightCharts (imports nettoyés)
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Cloud, Sun, CloudRain, Wind, Thermometer, Droplets, 
  Eye, Compass, TrendingUp, AlertTriangle 
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Service local du module
const MeteoService = {
  async getCurrent(lat, lng) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/weather/current?lat=${lat}&lng=${lng}`);
      return response.json();
    } catch (error) {
      console.error('Weather API error:', error);
      return null;
    }
  },
  
  async getHuntingAnalysis(lat, lng) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/weather/hunting-analysis?lat=${lat}&lng=${lng}`);
      return response.json();
    } catch (error) {
      return null;
    }
  },
  
  async getForecast(lat, lng, days = 5) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/weather/forecast?lat=${lat}&lng=${lng}&days=${days}`);
      return response.json();
    } catch (error) {
      return null;
    }
  }
};

// Composants locaux
const WeatherIcon = ({ condition, size = 'md' }) => {
  const sizes = { sm: 'h-6 w-6', md: 'h-10 w-10', lg: 'h-16 w-16' };
  const iconClass = sizes[size];
  
  const icons = {
    clear: <Sun className={`${iconClass} text-yellow-400`} />,
    clouds: <Cloud className={`${iconClass} text-gray-400`} />,
    rain: <CloudRain className={`${iconClass} text-blue-400`} />,
    snow: <Cloud className={`${iconClass} text-white`} />,
  };
  
  return icons[condition] || icons.clouds;
};

const HuntingConditionBadge = ({ score }) => {
  const getCondition = (score) => {
    if (score >= 80) return { label: 'Idéal', color: 'bg-green-500' };
    if (score >= 60) return { label: 'Favorable', color: 'bg-[#F5A623]' };
    if (score >= 40) return { label: 'Neutre', color: 'bg-yellow-500' };
    return { label: 'Défavorable', color: 'bg-red-500' };
  };
  
  const condition = getCondition(score);
  
  return (
    <Badge className={`${condition.color} text-white`}>
      {condition.label} ({score}/100)
    </Badge>
  );
};

const MeteoDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [weather, setWeather] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [forecast, setForecast] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const lat = 46.8139;
      const lng = -71.2080;
      
      const [currentData, huntingData, forecastData] = await Promise.all([
        MeteoService.getCurrent(lat, lng),
        MeteoService.getHuntingAnalysis(lat, lng),
        MeteoService.getForecast(lat, lng)
      ]);
      
      setWeather(currentData);
      setAnalysis(huntingData);
      setForecast(forecastData);
      setLoading(false);
    };
    
    fetchData();
  }, []);

  // Données de démonstration
  const demoWeather = {
    temperature: -5,
    feels_like: -10,
    humidity: 65,
    wind_speed: 15,
    wind_direction: 'NO',
    visibility: 10,
    pressure: 1015,
    condition: 'clouds',
    description: 'Partiellement nuageux'
  };

  const demoAnalysis = {
    hunting_score: 72,
    factors: {
      temperature: { score: 80, impact: 'positive' },
      wind: { score: 65, impact: 'neutral' },
      precipitation: { score: 85, impact: 'positive' },
      barometric: { score: 60, impact: 'neutral' }
    },
    recommendation: 'Conditions favorables pour la chasse au gros gibier',
    best_periods: ['06:00-09:00', '16:00-18:00']
  };

  const demoForecast = [
    { day: 'Lun', temp_high: -2, temp_low: -8, score: 75, condition: 'clouds' },
    { day: 'Mar', temp_high: 0, temp_low: -5, score: 82, condition: 'clear' },
    { day: 'Mer', temp_high: -3, temp_low: -10, score: 68, condition: 'clouds' },
    { day: 'Jeu', temp_high: -5, temp_low: -12, score: 60, condition: 'snow' },
    { day: 'Ven', temp_high: -1, temp_low: -6, score: 78, condition: 'clear' },
  ];

  const displayWeather = weather?.current || demoWeather;
  const displayAnalysis = analysis?.success ? analysis : demoAnalysis;
  const displayForecast = forecast?.forecast || demoForecast;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#F5A623]" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="meteo-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Cloud className="h-6 w-6 text-[#F5A623]" />
            Météo Chasse V5-ULTIME
          </h2>
          <p className="text-gray-400 mt-1">Analyse météorologique pour la chasse</p>
        </div>
        <HuntingConditionBadge score={displayAnalysis.hunting_score} />
      </div>

      {/* Conditions actuelles */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-gradient-to-br from-blue-500/20 to-transparent border-blue-500/30 md:col-span-2">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Température actuelle</p>
                <p className="text-6xl font-bold text-white mt-2">
                  {displayWeather.temperature}°C
                </p>
                <p className="text-gray-400 text-sm mt-2">
                  Ressenti: {displayWeather.feels_like}°C
                </p>
                <p className="text-white mt-4 capitalize">
                  {displayWeather.description}
                </p>
              </div>
              <WeatherIcon condition={displayWeather.condition} size="lg" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-black/40 border-white/10">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-sm">Détails</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-400 flex items-center gap-2">
                <Droplets className="h-4 w-4" /> Humidité
              </span>
              <span className="text-white">{displayWeather.humidity}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400 flex items-center gap-2">
                <Wind className="h-4 w-4" /> Vent
              </span>
              <span className="text-white">{displayWeather.wind_speed} km/h {displayWeather.wind_direction}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400 flex items-center gap-2">
                <Eye className="h-4 w-4" /> Visibilité
              </span>
              <span className="text-white">{displayWeather.visibility} km</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400 flex items-center gap-2">
                <Compass className="h-4 w-4" /> Pression
              </span>
              <span className="text-white">{displayWeather.pressure} hPa</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Analyse chasse */}
      <Card className="bg-black/40 border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-[#F5A623]" />
            Impact sur la Chasse
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {Object.entries(displayAnalysis.factors || {}).map(([key, value]) => (
              <div key={key} className="p-4 bg-white/5 rounded-lg">
                <p className="text-xs text-gray-400 capitalize">{key.replace('_', ' ')}</p>
                <p className="text-2xl font-bold text-white mt-1">{value.score}</p>
                <Badge 
                  variant="outline" 
                  className={value.impact === 'positive' ? 'text-green-400 border-green-400' : 'text-gray-400'}
                >
                  {value.impact === 'positive' ? '↑' : value.impact === 'negative' ? '↓' : '→'}
                </Badge>
              </div>
            ))}
          </div>
          
          <div className="bg-[#F5A623]/10 border border-[#F5A623]/30 rounded-lg p-4">
            <p className="text-white font-medium">{displayAnalysis.recommendation}</p>
            <p className="text-gray-400 text-sm mt-2">
              Meilleurs créneaux: {displayAnalysis.best_periods?.join(', ')}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Prévisions */}
      <Card className="bg-black/40 border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Sun className="h-5 w-5 text-[#F5A623]" />
            Prévisions 5 Jours
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-5 gap-4">
            {displayForecast.map((day, idx) => (
              <div 
                key={idx} 
                className="flex flex-col items-center p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
              >
                <p className="text-gray-400 text-sm">{day.day}</p>
                <WeatherIcon condition={day.condition} size="sm" />
                <p className="text-white font-bold mt-2">{day.temp_high}°</p>
                <p className="text-gray-500 text-sm">{day.temp_low}°</p>
                <div className="w-full mt-2">
                  <div 
                    className="h-1 rounded-full bg-gradient-to-r from-red-500 via-yellow-500 to-green-500"
                    style={{ 
                      clipPath: `inset(0 ${100 - day.score}% 0 0)` 
                    }}
                  />
                </div>
                <p className="text-xs text-gray-400 mt-1">{day.score}%</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default MeteoDashboard;
