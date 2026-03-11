/**
 * StrategieDashboard - V5-ULTIME
 * ==============================
 * 
 * Dashboard principal du module Stratégie.
 * Composant parent isolé - aucun import croisé.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Lightbulb, Target, Clock, MapPin, Compass, 
  ChevronRight, Star, Zap, TrendingUp, Check
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Service local du module
const StrategieService = {
  async getRecommendations(params = {}) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/strategy/recommendations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      return response.json();
    } catch (error) {
      console.error('Strategy API error:', error);
      return null;
    }
  },
  
  async getAdaptiveStrategy(conditions) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/adaptive-strategy/analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(conditions)
      });
      return response.json();
    } catch (error) {
      return null;
    }
  }
};

// Composants locaux
const StrategyCard = ({ strategy, isRecommended = false }) => {
  const typeIcons = {
    approach: <Compass className="h-5 w-5" />,
    ambush: <Target className="h-5 w-5" />,
    tracking: <MapPin className="h-5 w-5" />,
    call: <Zap className="h-5 w-5" />,
  };

  return (
    <Card className={`bg-black/40 border-white/10 hover:border-[#F5A623]/50 transition-colors ${isRecommended ? 'ring-2 ring-[#F5A623]' : ''}`}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-[#F5A623]/20 text-[#F5A623]">
              {typeIcons[strategy.type] || <Lightbulb className="h-5 w-5" />}
            </div>
            <div>
              <h3 className="text-white font-semibold">{strategy.name}</h3>
              <p className="text-gray-400 text-xs capitalize">{strategy.type}</p>
            </div>
          </div>
          {isRecommended && (
            <Badge className="bg-[#F5A623] text-black">
              <Star className="h-3 w-3 mr-1" /> Recommandé
            </Badge>
          )}
        </div>
        
        <p className="text-gray-400 text-sm mb-4">{strategy.description}</p>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {strategy.duration || '2-4h'}
            </span>
            <span className="flex items-center gap-1">
              <Target className="h-3 w-3" />
              {strategy.success_rate || '75'}%
            </span>
          </div>
          <Button size="sm" variant="ghost" className="text-[#F5A623]">
            Détails <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

const TimelineStep = ({ step, isActive, isCompleted }) => (
  <div className={`flex items-start gap-4 ${isCompleted ? 'opacity-60' : ''}`}>
    <div className={`
      w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0
      ${isCompleted ? 'bg-green-500' : isActive ? 'bg-[#F5A623]' : 'bg-white/10'}
    `}>
      {isCompleted ? (
        <Check className="h-4 w-4 text-white" />
      ) : (
        <span className="text-white text-sm">{step.order}</span>
      )}
    </div>
    <div className="flex-1 pb-6 border-l border-white/10 pl-4 -ml-4">
      <h4 className="text-white font-medium">{step.title}</h4>
      <p className="text-gray-400 text-sm mt-1">{step.description}</p>
      {step.time && (
        <p className="text-gray-500 text-xs mt-2 flex items-center gap-1">
          <Clock className="h-3 w-3" /> {step.time}
        </p>
      )}
    </div>
  </div>
);

const StrategieDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [strategies, setStrategies] = useState([]);
  const [activeStrategy, setActiveStrategy] = useState(null);
  const [timeline, setTimeline] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      
      const data = await StrategieService.getRecommendations({
        species: 'deer',
        terrain: 'forest',
        weather: 'cloudy'
      });
      
      if (data?.strategies) {
        setStrategies(data.strategies);
        setActiveStrategy(data.recommended);
      }
      
      setLoading(false);
    };
    
    fetchData();
  }, []);

  // Données de démonstration
  const demoStrategies = [
    {
      id: 1,
      name: 'Approche Silencieuse',
      type: 'approach',
      description: 'Progression lente contre le vent vers la zone d\'alimentation identifiée.',
      duration: '2-3h',
      success_rate: 78
    },
    {
      id: 2,
      name: 'Affût Stratégique',
      type: 'ambush',
      description: 'Position fixe près du sentier de passage principal avec couverture optimale.',
      duration: '3-5h',
      success_rate: 82
    },
    {
      id: 3,
      name: 'Traque Active',
      type: 'tracking',
      description: 'Suivi des indices frais (pistes, frottages) pour localiser le gibier.',
      duration: '4-6h',
      success_rate: 65
    },
    {
      id: 4,
      name: 'Appel Territorial',
      type: 'call',
      description: 'Utilisation d\'appels pour attirer le gibier pendant la période de rut.',
      duration: '1-2h',
      success_rate: 70
    }
  ];

  const demoTimeline = [
    { order: 1, title: 'Préparation', description: 'Vérification équipement et météo', time: '05:30', completed: true },
    { order: 2, title: 'Déplacement', description: 'Arrivée sur zone 30 min avant l\'aube', time: '06:00', completed: true },
    { order: 3, title: 'Positionnement', description: 'Installation de l\'affût face au vent', time: '06:30', active: true },
    { order: 4, title: 'Observation', description: 'Période d\'activité maximale du gibier', time: '07:00-09:00' },
    { order: 5, title: 'Ajustement', description: 'Repositionnement si nécessaire', time: '09:30' },
  ];

  const displayStrategies = strategies.length > 0 ? strategies : demoStrategies;
  const displayTimeline = timeline.length > 0 ? timeline : demoTimeline;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#F5A623]" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="strategie-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Lightbulb className="h-6 w-6 text-[#F5A623]" />
            Stratégies V5-ULTIME
          </h2>
          <p className="text-gray-400 mt-1">Recommandations adaptatives de chasse</p>
        </div>
        <Badge variant="outline" className="text-[#F5A623] border-[#F5A623]">
          Module UI Stratégie
        </Badge>
      </div>

      {/* Score de conditions */}
      <Card className="bg-gradient-to-r from-[#F5A623]/20 to-transparent border-[#F5A623]/30">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Conditions Actuelles</p>
              <p className="text-4xl font-bold text-white mt-2">
                Favorables
              </p>
              <p className="text-[#F5A623] text-sm mt-2 flex items-center gap-1">
                <TrendingUp className="h-4 w-4" />
                Score stratégique: 78/100
              </p>
            </div>
            <div className="text-right">
              <p className="text-gray-400 text-sm">Stratégie recommandée</p>
              <p className="text-xl font-semibold text-white mt-1">Affût Stratégique</p>
              <p className="text-gray-400 text-xs mt-1">82% de réussite historique</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Stratégies disponibles */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="text-lg font-semibold text-white">Stratégies Disponibles</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {displayStrategies.map((strategy, idx) => (
              <StrategyCard 
                key={strategy.id || idx}
                strategy={strategy}
                isRecommended={idx === 1}
              />
            ))}
          </div>
        </div>

        {/* Timeline de la journée */}
        <div>
          <Card className="bg-black/40 border-white/10">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Clock className="h-5 w-5 text-[#F5A623]" />
                Timeline du Jour
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-0">
                {displayTimeline.map((step, idx) => (
                  <TimelineStep
                    key={idx}
                    step={step}
                    isActive={step.active}
                    isCompleted={step.completed}
                  />
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default StrategieDashboard;
