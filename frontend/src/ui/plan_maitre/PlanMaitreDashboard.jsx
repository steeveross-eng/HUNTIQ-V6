/**
 * PlanMaitreDashboard - V5-ULTIME (Phase 9 Préparation)
 * =====================================================
 * 
 * Dashboard principal du Plan Maître.
 * Composant parent isolé - aucun import croisé.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  Crown, Target, Calendar, Clock, MapPin, 
  CheckCircle2, Circle, AlertCircle, ChevronRight,
  TrendingUp, Compass, Settings
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Service local du module
const PlanMaitreService = {
  async getPlan(userId) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/plan-maitre/current?user_id=${userId}`);
      return response.json();
    } catch (error) {
      console.error('Plan Maitre API error:', error);
      return null;
    }
  },
  
  async getRecommendations() {
    try {
      const response = await fetch(`${API_BASE}/api/v1/recommendation/plan-maitre`);
      return response.json();
    } catch (error) {
      return null;
    }
  }
};

// Composants locaux
const PhaseIndicator = ({ phase, status }) => {
  const statusIcons = {
    completed: <CheckCircle2 className="h-5 w-5 text-green-500" />,
    active: <Circle className="h-5 w-5 text-[#F5A623] fill-[#F5A623]/30" />,
    pending: <Circle className="h-5 w-5 text-gray-500" />,
    warning: <AlertCircle className="h-5 w-5 text-yellow-500" />,
  };

  return (
    <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
      {statusIcons[status] || statusIcons.pending}
      <div className="flex-1">
        <p className="text-white text-sm font-medium">{phase.name}</p>
        <p className="text-gray-500 text-xs">{phase.description}</p>
      </div>
      {status === 'active' && (
        <Badge className="bg-[#F5A623] text-black">En cours</Badge>
      )}
    </div>
  );
};

const ObjectiveCard = ({ objective }) => (
  <div className="p-4 bg-white/5 rounded-lg border border-white/10">
    <div className="flex items-start justify-between mb-2">
      <h4 className="text-white font-medium">{objective.title}</h4>
      <Badge variant="outline" className={
        objective.priority === 'high' ? 'text-red-400 border-red-400' :
        objective.priority === 'medium' ? 'text-yellow-400 border-yellow-400' :
        'text-gray-400'
      }>
        {objective.priority}
      </Badge>
    </div>
    <p className="text-gray-400 text-sm mb-3">{objective.description}</p>
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2 text-xs text-gray-500">
        <Calendar className="h-3 w-3" />
        {objective.deadline || 'Pas de deadline'}
      </div>
      <Progress value={objective.progress || 0} className="w-24 h-1" />
    </div>
  </div>
);

const PlanMaitreDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [plan, setPlan] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const data = await PlanMaitreService.getPlan('current_user');
      setPlan(data);
      setLoading(false);
    };
    
    fetchData();
  }, []);

  // Données de démonstration
  const demoPlan = {
    name: 'Plan Maître Saison 2026',
    progress: 35,
    currentPhase: 'preparation',
    phases: [
      { id: 1, name: 'Préparation', description: 'Analyse et planification', status: 'completed' },
      { id: 2, name: 'Reconnaissance', description: 'Exploration du territoire', status: 'active' },
      { id: 3, name: 'Installation', description: 'Mise en place des postes', status: 'pending' },
      { id: 4, name: 'Exécution', description: 'Période de chasse active', status: 'pending' },
      { id: 5, name: 'Bilan', description: 'Analyse des résultats', status: 'pending' },
    ],
    objectives: [
      { id: 1, title: 'Identifier 5 zones de passage', description: 'Localiser les corridors principaux', priority: 'high', progress: 80 },
      { id: 2, title: 'Installer 3 caméras de trail', description: 'Surveillance des zones clés', priority: 'medium', progress: 33 },
      { id: 3, title: 'Repérer source de nutrition', description: 'Zones d\'alimentation naturelle', priority: 'high', progress: 60 },
      { id: 4, title: 'Définir postes de tir', description: 'Positions optimales selon vent', priority: 'medium', progress: 20 },
    ],
    nextActions: [
      'Vérifier les caméras installées',
      'Analyser les données météo de la semaine',
      'Planifier sortie de reconnaissance secteur Nord'
    ]
  };

  const displayPlan = plan?.success ? plan : demoPlan;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#F5A623]" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="plan-maitre-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Crown className="h-6 w-6 text-[#F5A623]" />
            Plan Maître V5-ULTIME
          </h2>
          <p className="text-gray-400 mt-1">Stratégie de chasse complète - Phase 9</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="border-white/20">
            <Settings className="h-4 w-4 mr-2" />
            Paramètres
          </Button>
          <Button size="sm" className="bg-[#F5A623] text-black hover:bg-[#F5A623]/90">
            <Target className="h-4 w-4 mr-2" />
            Nouvel Objectif
          </Button>
        </div>
      </div>

      {/* Progress global */}
      <Card className="bg-gradient-to-r from-[#F5A623]/20 to-transparent border-[#F5A623]/30">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-gray-400 text-sm">Plan en cours</p>
              <p className="text-2xl font-bold text-white mt-1">{displayPlan.name}</p>
            </div>
            <div className="text-right">
              <p className="text-4xl font-bold text-white">{displayPlan.progress}%</p>
              <p className="text-gray-400 text-sm">Complété</p>
            </div>
          </div>
          <Progress value={displayPlan.progress} className="h-2" />
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Phases */}
        <Card className="bg-black/40 border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Compass className="h-5 w-5 text-[#F5A623]" />
              Phases du Plan
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {displayPlan.phases.map((phase) => (
              <PhaseIndicator 
                key={phase.id} 
                phase={phase} 
                status={phase.status} 
              />
            ))}
          </CardContent>
        </Card>

        {/* Objectifs */}
        <div className="lg:col-span-2">
          <Card className="bg-black/40 border-white/10">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-white flex items-center gap-2">
                <Target className="h-5 w-5 text-[#F5A623]" />
                Objectifs
              </CardTitle>
              <Button variant="ghost" size="sm" className="text-[#F5A623]">
                Voir tout <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {displayPlan.objectives.map((objective) => (
                  <ObjectiveCard key={objective.id} objective={objective} />
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Actions suivantes */}
      <Card className="bg-black/40 border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-[#F5A623]" />
            Prochaines Actions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {displayPlan.nextActions.map((action, idx) => (
              <div 
                key={idx}
                className="flex items-center gap-3 p-3 bg-white/5 rounded-lg hover:bg-white/10 cursor-pointer"
              >
                <div className="w-6 h-6 rounded-full bg-[#F5A623]/20 flex items-center justify-center text-[#F5A623] text-xs font-bold">
                  {idx + 1}
                </div>
                <p className="text-white text-sm">{action}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PlanMaitreDashboard;
