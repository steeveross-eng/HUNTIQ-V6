/**
 * TripStatsDashboard - Statistics dashboard for hunting trips
 * BIONIC Design System compliant - No emojis
 * PHASE F: Migration vers LightCharts
 */
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LightPieChart, LightBarChart, ResponsiveChartContainer } from '@/components/charts/LightCharts';
import {
  Calendar, Clock, Target, Eye, TrendingUp, Award, MapPin,
  Sunrise, Sunset, Cloud, ThumbsUp
} from 'lucide-react';
import { getSpeciesName } from '@/config/speciesImages';

const COLORS = ['#f5a623', '#22c55e', '#3b82f6', '#8b5cf6', '#ef4444', '#06b6d4'];

const TripStatsDashboard = ({ statistics }) => {
  if (!statistics) {
    return (
      <Card className="bg-slate-800/30 border-slate-700">
        <CardContent className="p-12 text-center">
          <Target className="h-12 w-12 text-gray-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">Aucune statistique disponible</h3>
          <p className="text-gray-400">
            Commencez à enregistrer vos sorties pour voir vos statistiques
          </p>
        </CardContent>
      </Card>
    );
  }

  // Prepare data for charts
  const speciesData = statistics.species_breakdown ? 
    Object.entries(statistics.species_breakdown).map(([species, count]) => ({
      name: getSpeciesName(species),
      value: count,
      species
    })) : [];

  const monthlyData = statistics.monthly_breakdown ? 
    Object.entries(statistics.monthly_breakdown).map(([month, data]) => ({
      month: month.substring(5), // Get MM part from YYYY-MM
      trips: data.trips || 0,
      observations: data.observations || 0,
      success: data.successful || 0
    })) : [];

  const observationTypes = statistics.observation_types ?
    Object.entries(statistics.observation_types).map(([type, count]) => ({
      name: type,
      value: count
    })) : [];

  // Best performing stats
  const bestDay = statistics.best_day || 'N/A';
  const bestWeather = statistics.best_weather || 'N/A';
  const avgDuration = statistics.avg_duration_hours?.toFixed(1) || '0';

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title="Sorties totales"
          value={statistics.total_trips || 0}
          icon={Calendar}
          color="blue"
        />
        <StatCard
          title="Taux de succès"
          value={`${statistics.success_rate || 0}%`}
          icon={Target}
          color="emerald"
          subtitle={`${statistics.successful_trips || 0} réussites`}
        />
        <StatCard
          title="Heures de chasse"
          value={statistics.total_hours || 0}
          icon={Clock}
          color="amber"
          subtitle={`~${avgDuration}h/sortie`}
        />
        <StatCard
          title="Observations"
          value={statistics.total_observations || 0}
          icon={Eye}
          color="purple"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Species Breakdown */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Target className="h-5 w-5 text-[#f5a623]" />
              Répartition par espèce
            </CardTitle>
          </CardHeader>
          <CardContent>
            {speciesData.length > 0 ? (
              <div className="h-64 flex flex-col items-center justify-center">
                <LightPieChart
                  data={speciesData}
                  size={180}
                  innerRadius={0.5}
                  colors={COLORS}
                  showLabels={true}
                  showTooltip={true}
                />
                <div className="flex flex-wrap justify-center gap-2 mt-4">
                  {speciesData.map((entry, index) => (
                    <div key={index} className="flex items-center gap-1 text-xs text-gray-400">
                      <div 
                        className="w-2 h-2 rounded-full" 
                        style={{ backgroundColor: COLORS[index % COLORS.length] }}
                      />
                      {entry.name}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-400">
                Aucune donnée disponible
              </div>
            )}
          </CardContent>
        </Card>

        {/* Monthly Activity */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-emerald-400" />
              Activité mensuelle
            </CardTitle>
          </CardHeader>
          <CardContent>
            {monthlyData.length > 0 ? (
              <div className="h-64">
                <ResponsiveChartContainer width="100%" height={256}>
                  <LightBarChart
                    data={monthlyData.map(item => ({
                      name: item.month,
                      value: item.trips
                    }))}
                    dataKey="value"
                    nameKey="name"
                    color="#f5a623"
                    showGrid={true}
                  />
                </ResponsiveChartContainer>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-400">
                Aucune donnée disponible
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Insights Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Best Conditions */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-lg flex items-center gap-2">
              <Award className="h-5 w-5 text-amber-400" />
              Meilleures conditions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-gray-400">
                  <Calendar className="h-4 w-4" />
                  <span>Meilleur jour</span>
                </div>
                <Badge className="bg-amber-500/20 text-amber-400">
                  {bestDay}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-gray-400">
                  <Cloud className="h-4 w-4" />
                  <span>Meilleure météo</span>
                </div>
                <Badge className="bg-blue-500/20 text-blue-400">
                  {bestWeather}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-gray-400">
                  <Clock className="h-4 w-4" />
                  <span>Durée moyenne</span>
                </div>
                <Badge className="bg-purple-500/20 text-purple-400">
                  {avgDuration}h
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recent Performance */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-lg flex items-center gap-2">
              <ThumbsUp className="h-5 w-5 text-emerald-400" />
              Performance récente
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Dernières 5 sorties</span>
                  <span className="text-emerald-400">
                    {statistics.recent_success_rate || 0}% succès
                  </span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div 
                    className="bg-emerald-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${statistics.recent_success_rate || 0}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Obs. par sortie</span>
                  <span className="text-purple-400">
                    {statistics.avg_observations_per_trip?.toFixed(1) || 0}
                  </span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div 
                    className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min((statistics.avg_observations_per_trip || 0) * 10, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Top Species */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-lg flex items-center gap-2">
              <Eye className="h-5 w-5 text-purple-400" />
              Espèces les plus vues
            </CardTitle>
          </CardHeader>
          <CardContent>
            {speciesData.length > 0 ? (
              <div className="space-y-3">
                {speciesData.slice(0, 4).map((species, idx) => (
                  <div key={species.species} className="flex items-center gap-3">
                    <Target className="h-6 w-6" style={{ color: COLORS[idx % COLORS.length] }} />
                    <div className="flex-1">
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-300 capitalize">{species.species}</span>
                        <span className="text-[#f5a623]">{species.value}</span>
                      </div>
                      <div className="w-full bg-slate-700 rounded-full h-1.5">
                        <div 
                          className="h-1.5 rounded-full"
                          style={{ 
                            width: `${(species.value / (speciesData[0]?.value || 1)) * 100}%`,
                            backgroundColor: COLORS[idx % COLORS.length]
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center text-gray-400 py-4">
                Aucune observation
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Observation Types */}
      {observationTypes.length > 0 && (
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Eye className="h-5 w-5 text-purple-400" />
              Types d'observations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveChartContainer width="100%" height={256}>
                <LightBarChart
                  data={observationTypes}
                  dataKey="value"
                  nameKey="name"
                  color="#8b5cf6"
                  showGrid={true}
                  horizontal={true}
                />
              </ResponsiveChartContainer>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

// Stat Card Component
const StatCard = ({ title, value, icon: Icon, color, subtitle }) => {
  const colorClasses = {
    blue: 'bg-blue-500/20 text-blue-400',
    emerald: 'bg-emerald-500/20 text-emerald-400',
    amber: 'bg-amber-500/20 text-amber-400',
    purple: 'bg-purple-500/20 text-purple-400'
  };

  return (
    <Card className="bg-slate-800/50 border-slate-700">
      <CardContent className="p-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
            <Icon className="h-5 w-5" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{value}</p>
            <p className="text-xs text-gray-400">{title}</p>
            {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default TripStatsDashboard;
