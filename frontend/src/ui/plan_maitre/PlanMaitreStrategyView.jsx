/**
 * PlanMaitreStrategyView - V5-ULTIME Plan Maître
 * ==============================================
 * 
 * Vue des stratégies générées par le Strategy Master Engine.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Compass, Target, MapPin, Clock, Zap, AlertTriangle,
  CheckCircle, Info, TrendingUp, RefreshCw
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const StrategyTypeIcons = {
  approach: Compass,
  ambush: Target,
  tracking: MapPin,
  call: Zap,
  mixed: TrendingUp
};

const AlertLevelColors = {
  positive: 'bg-green-500/20 border-green-500 text-green-400',
  info: 'bg-blue-500/20 border-blue-500 text-blue-400',
  warning: 'bg-yellow-500/20 border-yellow-500 text-yellow-400',
  danger: 'bg-red-500/20 border-red-500 text-red-400'
};

const AlertLevelIcons = {
  positive: CheckCircle,
  info: Info,
  warning: AlertTriangle,
  danger: AlertTriangle
};

const TimelineItem = ({ item }) => (
  <div className="flex items-start gap-3 py-2">
    <div className="w-16 text-xs text-[#F5A623] font-mono pt-0.5">
      {item.time}
    </div>
    <div className="flex-1">
      <p className="text-white text-sm">{item.action}</p>
    </div>
  </div>
);

const AlertCard = ({ alert }) => {
  const Icon = AlertLevelIcons[alert.level] || Info;
  const colorClass = AlertLevelColors[alert.level] || AlertLevelColors.info;
  
  return (
    <div className={`flex items-center gap-3 p-3 rounded-lg border ${colorClass}`}>
      <Icon className="h-5 w-5 flex-shrink-0" />
      <p className="text-sm">{alert.message}</p>
    </div>
  );
};

export const PlanMaitreStrategyView = ({ 
  userId, 
  location = { lat: 46.8139, lng: -71.2080 },
  species = 'deer'
}) => {
  const [strategy, setStrategy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStrategy = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE}/api/v1/strategy-master/strategy/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId || 'guest',
          location,
          species
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setStrategy(data);
      } else {
        setError('Échec de génération de stratégie');
      }
    } catch (err) {
      console.error('Strategy generation error:', err);
      setError('Erreur de connexion');
    }
    
    setLoading(false);
  };

  useEffect(() => {
    fetchStrategy();
  }, [userId, location?.lat, location?.lng, species]);

  if (loading) {
    return (
      <Card className="bg-black/40 border-white/10">
        <CardContent className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#F5A623] mx-auto mb-3" />
            <p className="text-gray-400 text-sm">Génération de la stratégie...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="bg-black/40 border-white/10">
        <CardContent className="flex items-center justify-center py-12">
          <div className="text-center">
            <AlertTriangle className="h-8 w-8 text-red-400 mx-auto mb-3" />
            <p className="text-red-400 text-sm">{error}</p>
            <Button 
              size="sm" 
              variant="outline" 
              className="mt-4"
              onClick={fetchStrategy}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Réessayer
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!strategy) return null;

  const StrategyIcon = StrategyTypeIcons[strategy.strategy?.primary_type] || Compass;

  return (
    <div className="space-y-6" data-testid="plan-maitre-strategy-view">
      {/* Strategy Header */}
      <Card className="bg-gradient-to-r from-[#F5A623]/20 to-transparent border-[#F5A623]/30">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-4 rounded-xl bg-[#F5A623]/20">
                <StrategyIcon className="h-8 w-8 text-[#F5A623]" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Stratégie recommandée</p>
                <h2 className="text-2xl font-bold text-white capitalize mt-1">
                  {strategy.strategy?.primary_type?.replace('_', ' ') || 'Adaptative'}
                </h2>
                <Badge 
                  className={`mt-2 ${
                    strategy.strategy?.confidence === 'high' ? 'bg-green-500' :
                    strategy.strategy?.confidence === 'medium' ? 'bg-yellow-500' : 'bg-gray-500'
                  } text-white`}
                >
                  Confiance: {strategy.strategy?.confidence}
                </Badge>
              </div>
            </div>
            <div className="text-right">
              <p className="text-gray-400 text-sm">Score conditions</p>
              <p className="text-4xl font-bold text-white">{strategy.strategy?.score}</p>
              <p className="text-gray-500 text-xs mt-1">
                Modificateur: x{strategy.strategy?.score_modifier}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Timeline */}
        <Card className="bg-black/40 border-white/10">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-white flex items-center gap-2">
              <Clock className="h-5 w-5 text-[#F5A623]" />
              Timeline
            </CardTitle>
            <Badge variant="outline" className="text-xs">
              {strategy.context?.time_of_day}
            </Badge>
          </CardHeader>
          <CardContent>
            <div className="divide-y divide-white/10">
              {strategy.timeline?.map((item, idx) => (
                <TimelineItem key={idx} item={item} />
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Context & Alerts */}
        <div className="space-y-6">
          {/* Weather Context */}
          <Card className="bg-black/40 border-white/10">
            <CardHeader>
              <CardTitle className="text-white text-sm">Contexte Météo</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-gray-500 text-xs">Température</p>
                  <p className="text-white font-semibold">{strategy.context?.weather?.temperature}°C</p>
                </div>
                <div>
                  <p className="text-gray-500 text-xs">Vent</p>
                  <p className="text-white font-semibold">{strategy.context?.weather?.wind_speed} km/h</p>
                </div>
                <div>
                  <p className="text-gray-500 text-xs">Pression</p>
                  <p className="text-white font-semibold">{strategy.context?.weather?.pressure_trend}</p>
                </div>
                <div>
                  <p className="text-gray-500 text-xs">Conditions</p>
                  <p className="text-white font-semibold capitalize">{strategy.context?.weather?.conditions}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Alerts */}
          {strategy.alerts && strategy.alerts.length > 0 && (
            <Card className="bg-black/40 border-white/10">
              <CardHeader>
                <CardTitle className="text-white text-sm">Alertes</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {strategy.alerts.map((alert, idx) => (
                  <AlertCard key={idx} alert={alert} />
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Tips */}
      {strategy.tips && strategy.tips.length > 0 && (
        <Card className="bg-black/40 border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Zap className="h-5 w-5 text-[#F5A623]" />
              Conseils
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {strategy.tips.map((tip, idx) => (
                <div 
                  key={idx}
                  className="flex items-center gap-3 p-3 bg-white/5 rounded-lg"
                >
                  <div className="w-6 h-6 rounded-full bg-[#F5A623]/20 flex items-center justify-center text-[#F5A623] text-xs font-bold">
                    {idx + 1}
                  </div>
                  <p className="text-white text-sm">{tip}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Refresh button */}
      <div className="flex justify-center">
        <Button 
          variant="outline" 
          className="border-white/20"
          onClick={fetchStrategy}
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser la stratégie
        </Button>
      </div>
    </div>
  );
};

export default PlanMaitreStrategyView;
