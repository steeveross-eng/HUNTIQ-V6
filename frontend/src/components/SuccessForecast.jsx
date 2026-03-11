/**
 * SuccessForecast - Display success probability and best waypoint recommendations
 * Phase P3 - WQS & Success Forecast
 * BIONIC Design System compliant
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { WaypointScoringService } from '../services/WaypointScoringService';
import { 
  CircleDot, Sun, Cloud, CloudRain, CloudFog, Snowflake, 
  Flame, ThumbsUp, MapPin, AlertTriangle, Target, Clock, Trophy, BarChart3, Eye, Bot, Lightbulb
} from 'lucide-react';

// BIONIC Design System - Species config with Lucide icons
const SPECIES_OPTIONS = [
  { id: 'deer', label: 'Cerf', Icon: CircleDot, color: '#D2691E' },
  { id: 'moose', label: 'Orignal', Icon: CircleDot, color: '#8B4513' },
  { id: 'bear', label: 'Ours', Icon: CircleDot, color: '#2F4F4F' },
  { id: 'wild_turkey', label: 'Dindon', Icon: CircleDot, color: '#ef4444' },
  { id: 'duck', label: 'Canard', Icon: CircleDot, color: '#3b82f6' }
];

// BIONIC Design System - Weather config with Lucide icons
const WEATHER_OPTIONS = [
  { id: 'Ensoleillé', label: 'Ensoleillé', Icon: Sun, color: '#f5a623' },
  { id: 'Nuageux', label: 'Nuageux', Icon: Cloud, color: '#9ca3af' },
  { id: 'Pluvieux', label: 'Pluvieux', Icon: CloudRain, color: '#3b82f6' },
  { id: 'Brumeux', label: 'Brumeux', Icon: CloudFog, color: '#6b7280' },
  { id: 'Neigeux', label: 'Neigeux', Icon: Snowflake, color: '#06b6d4' }
];

const getClassificationColor = (classification) => {
  switch (classification) {
    case 'hotspot': return 'bg-green-600';
    case 'good': return 'bg-blue-600';
    case 'standard': return 'bg-yellow-600';
    case 'weak': return 'bg-red-600';
    default: return 'bg-slate-600';
  }
};

const getClassificationIcon = (classification) => {
  switch (classification) {
    case 'hotspot': return { Icon: Flame, color: '#22c55e', label: 'Hotspot' };
    case 'good': return { Icon: ThumbsUp, color: '#3b82f6', label: 'Bon' };
    case 'standard': return { Icon: MapPin, color: '#eab308', label: 'Standard' };
    case 'weak': return { Icon: AlertTriangle, color: '#ef4444', label: 'Faible' };
    default: return { Icon: Target, color: '#6b7280', label: classification };
  }
};

export const SuccessForecast = () => {
  const [loading, setLoading] = useState(true);
  const [forecast, setForecast] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [wqsRankings, setWqsRankings] = useState([]);
  
  // Filters
  const [selectedSpecies, setSelectedSpecies] = useState('deer');
  const [selectedWeather, setSelectedWeather] = useState('Nuageux');
  const [targetHour, setTargetHour] = useState(new Date().getHours());

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [forecastData, recommendationsData, rankingsData] = await Promise.all([
        WaypointScoringService.getSuccessForecast({
          species: selectedSpecies,
          weather: selectedWeather,
          hour: targetHour
        }),
        WaypointScoringService.getRecommendations(selectedSpecies, selectedWeather),
        WaypointScoringService.getAllWQS()
      ]);
      
      setForecast(forecastData);
      setRecommendations(recommendationsData);
      setWqsRankings(rankingsData);
    } catch (error) {
      console.error('Error loading forecast data:', error);
    } finally {
      setLoading(false);
    }
  }, [selectedSpecies, selectedWeather, targetHour]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse bg-slate-700 rounded-lg h-48" />
        <div className="animate-pulse bg-slate-700 rounded-lg h-64" />
      </div>
    );
  }

  const probabilityColor = forecast?.probability >= 70 ? 'text-green-400' 
    : forecast?.probability >= 40 ? 'text-yellow-400' 
    : 'text-red-400';

  return (
    <div className="space-y-6" data-testid="success-forecast">
      {/* Main Forecast Card */}
      <Card className="bg-gradient-to-br from-[#f5a623]/20 to-slate-900 border-[#f5a623]/50">
        <CardHeader className="pb-2">
          <CardTitle className="text-xl text-white flex items-center gap-3">
            <Target className="h-8 w-8 text-[#f5a623]" />
            Success Forecast
            <Badge className="bg-[#f5a623] text-black ml-auto">
              {forecast?.confidence === 'high' ? 'Confiance élevée' : 
               forecast?.confidence === 'medium' ? 'Confiance moyenne' : 'Confiance faible'}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Probability Display */}
          <div className="text-center mb-6">
            <div className={`text-6xl font-bold ${probabilityColor}`}>
              {forecast?.probability || 0}%
            </div>
            <p className="text-slate-400 mt-2">Probabilité de succès</p>
          </div>
          
          {/* Progress Bar */}
          <div className="mb-6">
            <Progress 
              value={forecast?.probability || 0} 
              className="h-3 bg-slate-700"
            />
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {/* Species */}
            <div>
              <label className="text-slate-400 text-sm block mb-2">Espèce ciblée</label>
              <div className="flex flex-wrap gap-2">
                {SPECIES_OPTIONS.map(species => (
                  <Button
                    key={species.id}
                    size="sm"
                    variant={selectedSpecies === species.id ? 'default' : 'outline'}
                    className={selectedSpecies === species.id 
                      ? 'bg-[#f5a623] text-black' 
                      : 'border-slate-600'}
                    onClick={() => setSelectedSpecies(species.id)}
                  >
                    <species.Icon className="h-4 w-4" style={{ color: selectedSpecies === species.id ? 'inherit' : species.color }} />
                  </Button>
                ))}
              </div>
            </div>
            
            {/* Weather */}
            <div>
              <label className="text-slate-400 text-sm block mb-2">Météo prévue</label>
              <div className="flex flex-wrap gap-2">
                {WEATHER_OPTIONS.map(weather => (
                  <Button
                    key={weather.id}
                    size="sm"
                    variant={selectedWeather === weather.id ? 'default' : 'outline'}
                    className={selectedWeather === weather.id 
                      ? 'bg-blue-600' 
                      : 'border-slate-600'}
                    onClick={() => setSelectedWeather(weather.id)}
                  >
                    <weather.Icon className="h-4 w-4" style={{ color: selectedWeather === weather.id ? 'inherit' : weather.color }} />
                  </Button>
                ))}
              </div>
            </div>
            
            {/* Hour */}
            <div>
              <label className="text-slate-400 text-sm block mb-2">Heure prévue: {targetHour}h</label>
              <input
                type="range"
                min="0"
                max="23"
                value={targetHour}
                onChange={(e) => setTargetHour(parseInt(e.target.value))}
                className="w-full accent-[#f5a623]"
              />
              <div className="flex justify-between text-xs text-slate-500">
                <span>0h</span>
                <span>6h</span>
                <span>12h</span>
                <span>18h</span>
                <span>23h</span>
              </div>
            </div>
          </div>

          {/* Best Waypoint */}
          {forecast?.best_waypoint && (
            <div className="bg-slate-800/50 rounded-lg p-4 mb-4">
              <h4 className="text-white font-medium mb-2 flex items-center gap-2">
                <MapPin className="h-5 w-5 text-[#f5a623]" />
                Meilleur waypoint recommandé
              </h4>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-[#f5a623] font-bold text-lg">
                    {forecast.best_waypoint.waypoint_name}
                  </p>
                  <p className="text-slate-400 text-sm">
                    WQS: {forecast.best_waypoint.total_score}% • {forecast.best_waypoint.total_visits} visites
                  </p>
                </div>
                <Badge className={`${getClassificationColor(forecast.best_waypoint.classification)} flex items-center gap-1`}>
                  {(() => {
                    const { Icon, label } = getClassificationIcon(forecast.best_waypoint.classification);
                    return <><Icon className="h-3 w-3" /> {label}</>;
                  })()}
                </Badge>
              </div>
            </div>
          )}

          {/* Conditions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Favorable */}
            {forecast?.favorable_conditions?.length > 0 && (
              <div className="bg-green-900/20 rounded-lg p-3 border border-green-700/50">
                <h5 className="text-green-400 font-medium mb-2 flex items-center gap-1">
                  <ThumbsUp className="h-4 w-4" /> Conditions favorables
                </h5>
                <ul className="text-sm text-slate-300 space-y-1">
                  {forecast.favorable_conditions.map((cond, i) => (
                    <li key={i}>• {cond}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Unfavorable */}
            {forecast?.unfavorable_conditions?.length > 0 && (
              <div className="bg-red-900/20 rounded-lg p-3 border border-red-700/50">
                <h5 className="text-red-400 font-medium mb-2 flex items-center gap-1">
                  <AlertTriangle className="h-4 w-4" /> Conditions défavorables
                </h5>
                <ul className="text-sm text-slate-300 space-y-1">
                  {forecast.unfavorable_conditions.map((cond, i) => (
                    <li key={i}>• {cond}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Optimal Window */}
          {forecast?.optimal_time_window && (
            <div className="mt-4 text-center">
              <p className="text-slate-400 flex items-center justify-center gap-2">
                <Clock className="h-4 w-4" /> Fenêtre horaire optimale: <span className="text-[#f5a623] font-bold">{forecast.optimal_time_window}</span>
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* WQS Rankings */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg text-white flex items-center gap-2">
            <Trophy className="h-5 w-5 text-[#f5a623]" />
            Classement WQS des Waypoints
          </CardTitle>
        </CardHeader>
        <CardContent>
          {wqsRankings.length > 0 ? (
            <div className="space-y-3">
              {wqsRankings.map((wp, index) => (
                <div 
                  key={wp.waypoint_id}
                  className="flex items-center gap-4 p-3 bg-slate-700/50 rounded-lg"
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                    index === 0 ? 'bg-yellow-500 text-black' :
                    index === 1 ? 'bg-slate-400 text-black' :
                    index === 2 ? 'bg-amber-700 text-white' :
                    'bg-slate-600 text-white'
                  }`}>
                    {index + 1}
                  </div>
                  
                  <div className="flex-1">
                    <p className="text-white font-medium">{wp.waypoint_name}</p>
                    <div className="flex gap-4 text-sm text-slate-400">
                      <span className="flex items-center gap-1"><BarChart3 className="h-3 w-3" /> Succès: {wp.success_rate}%</span>
                      <span className="flex items-center gap-1"><Eye className="h-3 w-3" /> {wp.total_visits} visites</span>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="text-2xl font-bold text-[#f5a623]">{wp.total_score}%</div>
                    <Badge className={`${getClassificationColor(wp.classification)} flex items-center gap-1`}>
                      {(() => {
                        const { Icon, label } = getClassificationIcon(wp.classification);
                        return <><Icon className="h-3 w-3" /> {label}</>;
                      })()}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <MapPin className="h-10 w-10 text-[#f5a623] mx-auto" />
              <p className="text-slate-400 mt-2">Aucun waypoint avec données</p>
              <p className="text-slate-500 text-sm">Enregistrez des sorties pour voir le classement</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* AI Recommendations */}
      {recommendations.length > 0 && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg text-white flex items-center gap-2">
              <Bot className="h-5 w-5 text-[#f5a623]" />
              Recommandations IA
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recommendations.slice(0, 3).map((rec, index) => (
                <div 
                  key={rec.waypoint_id}
                  className="p-4 bg-gradient-to-r from-slate-700/50 to-transparent rounded-lg border-l-4 border-[#f5a623]"
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-white font-medium">{rec.waypoint_name}</h4>
                    <Badge className="bg-green-600">
                      {rec.success_probability}% probabilité
                    </Badge>
                  </div>
                  
                  <p className="text-slate-400 text-sm mb-3">{rec.reasoning}</p>
                  
                  <div className="flex flex-wrap gap-2 mb-3">
                    <Badge variant="outline" className="border-blue-500 text-blue-400 flex items-center gap-1">
                      <Cloud className="h-3 w-3" /> Météo: {rec.weather_match}%
                    </Badge>
                    <Badge variant="outline" className="border-purple-500 text-purple-400 flex items-center gap-1">
                      <Clock className="h-3 w-3" /> Horaire: {rec.time_match}%
                    </Badge>
                    <Badge variant="outline" className="border-green-500 text-green-400 flex items-center gap-1">
                      <CircleDot className="h-3 w-3" /> Espèce: {rec.species_match}%
                    </Badge>
                  </div>
                  
                  {rec.tips.length > 0 && (
                    <div className="bg-slate-800/50 rounded p-2">
                      <p className="text-xs text-slate-500 mb-1 flex items-center gap-1"><Lightbulb className="h-3 w-3" /> Tips:</p>
                      <ul className="text-sm text-slate-300">
                        {rec.tips.map((tip, i) => (
                          <li key={i}>• {tip}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SuccessForecast;
