/**
 * PlanMaitreStats - V5-ULTIME Plan Maître
 * =======================================
 * 
 * Statistiques et métriques du Plan Maître.
 * PHASE F: Migration vers LightCharts
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  BarChart3, Target, CheckCircle2, Clock, TrendingUp, Award,
  Calendar, Compass
} from 'lucide-react';
import { LightAreaChart, LightPieChart, ResponsiveChartContainer } from '@/components/charts/LightCharts';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const StatCard = ({ icon: Icon, label, value, subValue, color = '#F5A623' }) => (
  <Card className="bg-black/40 border-white/10">
    <CardContent className="p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-xs">{label}</p>
          <p className="text-2xl font-bold text-white mt-1">{value}</p>
          {subValue && (
            <p className="text-gray-500 text-xs mt-1">{subValue}</p>
          )}
        </div>
        <div className="p-3 rounded-xl" style={{ backgroundColor: `${color}20` }}>
          <Icon className="h-6 w-6" style={{ color }} />
        </div>
      </div>
    </CardContent>
  </Card>
);

export const PlanMaitreStats = ({ userId }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_BASE}/api/v1/strategy-master/progress/${userId || 'guest'}`);
        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
      setLoading(false);
    };
    
    fetchStats();
  }, [userId]);

  // Demo data
  const demoStats = {
    stats: {
      total_plans: 3,
      completed_plans: 1,
      active_plans: 2,
      total_objectives: 15,
      completed_objectives: 8,
      completion_rate: 53.3
    }
  };

  const demoTrend = [
    { week: 'S1', score: 65 },
    { week: 'S2', score: 72 },
    { week: 'S3', score: 68 },
    { week: 'S4', score: 78 },
    { week: 'S5', score: 82 },
    { week: 'S6', score: 75 },
  ];

  const demoStrategyBreakdown = [
    { name: 'Affût', value: 45, color: '#F5A623' },
    { name: 'Approche', value: 30, color: '#22c55e' },
    { name: 'Traque', value: 15, color: '#3b82f6' },
    { name: 'Appel', value: 10, color: '#8b5cf6' },
  ];

  const displayStats = stats?.stats || demoStats.stats;

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#F5A623]" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="plan-maitre-stats">
      {/* Main stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard 
          icon={Calendar} 
          label="Plans créés" 
          value={displayStats.total_plans}
          subValue={`${displayStats.completed_plans} terminés`}
          color="#F5A623"
        />
        <StatCard 
          icon={Target} 
          label="Objectifs" 
          value={displayStats.total_objectives}
          subValue={`${displayStats.completed_objectives} complétés`}
          color="#22c55e"
        />
        <StatCard 
          icon={TrendingUp} 
          label="Taux de réussite" 
          value={`${displayStats.completion_rate}%`}
          color="#3b82f6"
        />
        <StatCard 
          icon={Clock} 
          label="Plans actifs" 
          value={displayStats.active_plans}
          color="#8b5cf6"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Progress trend */}
        <Card className="bg-black/40 border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-[#F5A623]" />
              Tendance des Scores
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-48">
              <ResponsiveChartContainer width="100%" height={192}>
                <LightAreaChart 
                  data={demoTrend.map(item => ({
                    name: item.week,
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

        {/* Strategy breakdown */}
        <Card className="bg-black/40 border-white/10">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Compass className="h-5 w-5 text-[#F5A623]" />
              Répartition Stratégies
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-6">
              <div className="h-40 w-40">
                <LightPieChart
                  data={demoStrategyBreakdown}
                  size={160}
                  innerRadius={0.5}
                  showLabels={false}
                  showTooltip={true}
                />
              </div>
              <div className="flex-1 space-y-2">
                {demoStrategyBreakdown.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: item.color }}
                      />
                      <span className="text-gray-400 text-sm">{item.name}</span>
                    </div>
                    <span className="text-white font-semibold">{item.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Achievements preview */}
      <Card className="bg-black/40 border-white/10">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Award className="h-5 w-5 text-[#F5A623]" />
            Accomplissements Récents
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { name: 'Premier Plan', desc: 'Créer votre premier plan', completed: true },
              { name: 'Stratège', desc: '5 stratégies générées', completed: true },
              { name: 'Météorologue', desc: '10 analyses météo', completed: false },
              { name: 'Maître', desc: 'Compléter un plan entier', completed: false },
            ].map((achievement, idx) => (
              <div 
                key={idx}
                className={`p-4 rounded-lg border ${
                  achievement.completed 
                    ? 'bg-[#F5A623]/10 border-[#F5A623]/30' 
                    : 'bg-white/5 border-white/10 opacity-50'
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  {achievement.completed ? (
                    <CheckCircle2 className="h-5 w-5 text-[#F5A623]" />
                  ) : (
                    <div className="h-5 w-5 rounded-full border-2 border-gray-500" />
                  )}
                  <span className="text-white font-medium text-sm">{achievement.name}</span>
                </div>
                <p className="text-gray-500 text-xs">{achievement.desc}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PlanMaitreStats;
