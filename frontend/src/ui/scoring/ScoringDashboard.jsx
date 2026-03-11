/**
 * ScoringDashboard - V5-ULTIME
 * ============================
 * 
 * Dashboard principal du module Scoring.
 * Composant parent isolé - aucun import croisé.
 * PHASE F: Migration vers LightCharts
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Target, TrendingUp, Zap, Thermometer, Wind, Droplets } from 'lucide-react';
import { LightRadarChart, LightAreaChart, ResponsiveChartContainer } from '@/components/charts/LightCharts';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Service local du module (pas d'import externe)
const ScoringService = {
  async getOverview() {
    try {
      const response = await fetch(`${API_BASE}/api/v1/scoring/overview`);
      return response.json();
    } catch (error) {
      console.error('Scoring API error:', error);
      return null;
    }
  },
  
  async getWeatherImpact(lat, lng) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/scoring/weather-impact?lat=${lat}&lng=${lng}`);
      return response.json();
    } catch (error) {
      console.error('Weather impact error:', error);
      return null;
    }
  }
};

// Composants locaux du module
const ScoreGauge = ({ score, label, color = '#F5A623' }) => {
  const getScoreLevel = (score) => {
    if (score >= 85) return { label: 'Excellent', color: '#22c55e' };
    if (score >= 70) return { label: 'Bon', color: '#F5A623' };
    if (score >= 50) return { label: 'Moyen', color: '#eab308' };
    return { label: 'Faible', color: '#ef4444' };
  };
  
  const level = getScoreLevel(score);
  
  return (
    <div className="flex flex-col items-center p-4 bg-black/40 rounded-xl border border-white/10">
      <div className="relative w-24 h-24 mb-3">
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="48"
            cy="48"
            r="40"
            fill="none"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth="8"
          />
          <circle
            cx="48"
            cy="48"
            r="40"
            fill="none"
            stroke={level.color}
            strokeWidth="8"
            strokeDasharray={`${(score / 100) * 251.2} 251.2`}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold text-white">{score}</span>
        </div>
      </div>
      <span className="text-sm text-gray-400">{label}</span>
      <Badge 
        className="mt-1"
        style={{ backgroundColor: `${level.color}20`, color: level.color }}
      >
        {level.label}
      </Badge>
    </div>
  );
};

const ScoringDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [weatherImpact, setWeatherImpact] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      
      const [overview, weather] = await Promise.all([
        ScoringService.getOverview(),
        ScoringService.getWeatherImpact(46.8139, -71.2080) // Default: Quebec
      ]);
      
      setData(overview);
      setWeatherImpact(weather);
      setLoading(false);
    };
    
    fetchData();
  }, []);

  // Données de démonstration si l'API ne répond pas
  const demoData = {
    global_score: 78,
    categories: [
      { name: 'Nutrition', score: 85 },
      { name: 'Attractivité', score: 72 },
      { name: 'Météo', score: 68 },
      { name: 'Terrain', score: 82 },
      { name: 'Timing', score: 75 },
    ],
    trend: [
      { day: 'Lun', score: 72 },
      { day: 'Mar', score: 75 },
      { day: 'Mer', score: 68 },
      { day: 'Jeu', score: 78 },
      { day: 'Ven', score: 82 },
      { day: 'Sam', score: 85 },
      { day: 'Dim', score: 78 },
    ],
    radar: [
      { category: 'Protéines', value: 85 },
      { category: 'Minéraux', value: 72 },
      { category: 'Énergie', value: 68 },
      { category: 'Attractants', value: 90 },
      { category: 'Timing', value: 75 },
      { category: 'Météo', value: 65 },
    ]
  };

  const displayData = data?.success ? data : demoData;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#F5A623]" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="scoring-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Target className="h-6 w-6 text-[#F5A623]" />
            Scoring V5-ULTIME
          </h2>
          <p className="text-gray-400 mt-1">Évaluation multi-facteurs de chasse</p>
        </div>
        <Badge variant="outline" className="text-[#F5A623] border-[#F5A623]">
          Module UI Scoring
        </Badge>
      </div>

      {/* Score global */}
      <Card className="bg-gradient-to-r from-[#F5A623]/20 to-transparent border-[#F5A623]/30">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Score Global de Chasse</p>
              <p className="text-5xl font-bold text-white mt-2">
                {displayData.global_score}
                <span className="text-2xl text-gray-400">/100</span>
              </p>
              <p className="text-[#F5A623] text-sm mt-2 flex items-center gap-1">
                <TrendingUp className="h-4 w-4" />
                +5 pts vs semaine dernière
              </p>
            </div>
            <div className="h-32 w-32">
                <LightRadarChart 
                  data={(displayData.radar || demoData.radar).map(item => ({
                    name: item.category,
                    value: item.value
                  }))}
                  size={128}
                  color="#F5A623"
                  maxValue={100}
                  showLabels={false}
                />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Scores par catégorie */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {(displayData.categories || demoData.categories).map((cat, idx) => (
          <ScoreGauge key={idx} score={cat.score} label={cat.name} />
        ))}
      </div>

      {/* Tendance hebdomadaire */}
      <Card className="bg-black/40 border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-[#F5A623]" />
            Tendance Hebdomadaire
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveChartContainer width="100%" height={256}>
              <LightAreaChart 
                data={(displayData.trend || demoData.trend).map(item => ({
                  name: item.day,
                  value: item.score
                }))}
                dataKey="value"
                nameKey="name"
                color="#F5A623"
                showGrid={true}
                showDots={true}
                showArea={true}
              />
            </ResponsiveChartContainer>
          </div>
        </CardContent>
      </Card>

      {/* Impact météo */}
      <Card className="bg-black/40 border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Zap className="h-5 w-5 text-[#F5A623]" />
            Impact Météo sur le Score
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
              <Thermometer className="h-8 w-8 text-orange-400" />
              <div>
                <p className="text-xs text-gray-400">Température</p>
                <p className="text-lg font-semibold text-white">
                  {weatherImpact?.temperature_impact || '+8'}%
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
              <Wind className="h-8 w-8 text-blue-400" />
              <div>
                <p className="text-xs text-gray-400">Vent</p>
                <p className="text-lg font-semibold text-white">
                  {weatherImpact?.wind_impact || '-3'}%
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
              <Droplets className="h-8 w-8 text-cyan-400" />
              <div>
                <p className="text-xs text-gray-400">Humidité</p>
                <p className="text-lg font-semibold text-white">
                  {weatherImpact?.humidity_impact || '+2'}%
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ScoringDashboard;
