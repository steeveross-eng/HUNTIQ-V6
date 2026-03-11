/**
 * AnalyticsDashboard - Main analytics dashboard component
 * Phase P3 - Advanced Analytics
 * BIONIC Design System compliant
 * PHASE F: Migration vers LightCharts
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../../components/ui/tabs';
import { 
  LightLineChart, LightPieChart, LightBarChart, LightRadarChart,
  ResponsiveChartContainer 
} from '../../../components/charts/LightCharts';
import { 
  BarChart3, TrendingUp, Target, Cloud, CircleDot, Download, RefreshCw,
  Clock, Eye, FileDown, FileText, Scroll, ClipboardList, CloudSun
} from 'lucide-react';
import { AnalyticsService } from '../AnalyticsService';
import { ExportService } from '../../../services/ExportService';
import { toast } from 'sonner';
import { useLanguage } from '../../../contexts/LanguageContext';

const TIME_RANGES = [
  { value: 'week', label: 'Semaine' },
  { value: 'month', label: 'Mois' },
  { value: 'season', label: 'Saison' },
  { value: 'year', label: 'Année' },
  { value: 'all', label: 'Tout' }
];

const SPECIES_COLORS = {
  deer: '#f5a623',
  moose: '#8b4513',
  bear: '#2d2d2d',
  wild_turkey: '#cd853f',
  duck: '#4682b4',
  wild_boar: '#696969',
  goose: '#708090'
};

const SPECIES_LABELS = {
  deer: 'Cerf',
  moose: 'Orignal',
  bear: 'Ours',
  wild_turkey: 'Dindon sauvage',
  duck: 'Canard',
  wild_boar: 'Sanglier',
  goose: 'Oie'
};

const WEATHER_COLORS = {
  'Ensoleillé': '#ffd700',
  'Nuageux': '#a9a9a9',
  'Pluvieux': '#4682b4',
  'Brumeux': '#d3d3d3',
  'Neigeux': '#e0ffff'
};

export const AnalyticsDashboard = () => {
  const { t } = useLanguage();
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('all');
  const [dashboard, setDashboard] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    try {
      const data = await AnalyticsService.getDashboard(timeRange);
      setDashboard(data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse bg-slate-700 rounded-lg h-48" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="animate-pulse bg-slate-700 rounded-lg h-32" />
          ))}
        </div>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-8 text-center">
          <BarChart3 className="h-12 w-12 text-[#f5a623] mx-auto" />
          <p className="text-slate-400 mt-4">Erreur lors du chargement des données</p>
          <Button onClick={loadDashboard} className="mt-4 bg-[#f5a623]">
            <RefreshCw className="h-4 w-4 mr-2" /> Réessayer
          </Button>
        </CardContent>
      </Card>
    );
  }

  const { overview, species_breakdown, weather_analysis, optimal_times, monthly_trends, recent_trips } = dashboard;

  // Export handlers
  const handleExportPDF = () => {
    try {
      ExportService.exportAnalyticsPDF(dashboard);
      toast.success('Rapport PDF exporté !');
    } catch (error) {
      toast.error('Erreur lors de l\'export PDF');
      console.error(error);
    }
  };

  const handleExportTripsCSV = () => {
    try {
      ExportService.exportTripsCSV(recent_trips);
      toast.success('Sorties exportées en CSV !');
    } catch (error) {
      toast.error('Erreur lors de l\'export CSV');
      console.error(error);
    }
  };

  const handleExportTripsPDF = () => {
    try {
      ExportService.exportTripsPDF(recent_trips);
      toast.success('Journal de chasse exporté en PDF !');
    } catch (error) {
      toast.error('Erreur lors de l\'export PDF');
      console.error(error);
    }
  };

  return (
    <div className="space-y-6" data-testid="analytics-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <BarChart3 className="h-8 w-8 text-[#f5a623]" />
            Dashboard Analytics
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Statistiques et KPIs de chasse • Phase P3
          </p>
        </div>
        
        {/* Export Buttons */}
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            className="border-green-600 text-green-400 hover:bg-green-600/20"
            onClick={handleExportTripsCSV}
            data-testid="export-csv-btn"
          >
            <FileDown className="h-4 w-4 mr-1" /> CSV
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="border-red-600 text-red-400 hover:bg-red-600/20"
            onClick={handleExportPDF}
            data-testid="export-pdf-btn"
          >
            <FileText className="h-4 w-4 mr-1" /> PDF
          </Button>
        </div>
      </div>
      
      {/* Time Range Filter */}
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-slate-400 text-sm">Période:</span>
        {TIME_RANGES.map(range => (
          <Button
            key={range.value}
            size="sm"
            variant={timeRange === range.value ? 'default' : 'outline'}
            className={timeRange === range.value 
              ? 'bg-[#f5a623] text-black hover:bg-[#e09000]' 
              : 'border-slate-600 text-slate-300'}
            onClick={() => setTimeRange(range.value)}
          >
            {range.label}
          </Button>
        ))}
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-[#f5a623]/20 to-slate-900 border-[#f5a623]/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Sorties totales</p>
                <p className="text-3xl font-bold text-white">{overview.total_trips}</p>
              </div>
              <Target className="h-10 w-10 text-[#f5a623]" />
            </div>
            <p className="text-[#f5a623] text-sm mt-2">
              {overview.avg_trip_duration}h en moyenne
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-900/30 to-slate-900 border-green-700/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Taux de succès</p>
                <p className="text-3xl font-bold text-green-400">{overview.success_rate}%</p>
              </div>
              <TrendingUp className="h-10 w-10 text-green-400" />
            </div>
            <p className="text-green-400 text-sm mt-2">
              {overview.successful_trips} réussites
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-900/30 to-slate-900 border-blue-700/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Heures de chasse</p>
                <p className="text-3xl font-bold text-blue-400">{overview.total_hours}h</p>
              </div>
              <Clock className="h-10 w-10 text-blue-400" />
            </div>
            <p className="text-blue-400 text-sm mt-2">
              Temps investi
            </p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-900/30 to-slate-900 border-purple-700/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Observations</p>
                <p className="text-3xl font-bold text-purple-400">{overview.total_observations}</p>
              </div>
              <Eye className="h-10 w-10 text-purple-400" />
            </div>
            <p className="text-purple-400 text-sm mt-2">
              {overview.most_active_species && `Plus actif: ${SPECIES_LABELS[overview.most_active_species] || overview.most_active_species}`}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="bg-[var(--bionic-bg-card)] border border-[var(--bionic-border-secondary)] w-full justify-start">
          <TabsTrigger value="overview" className="data-[state=active]:bg-[var(--bionic-gold-primary)] data-[state=active]:text-black gap-2">
            <TrendingUp className="h-4 w-4" /> {t('common_overview') || "Vue d'ensemble"}
          </TabsTrigger>
          <TabsTrigger value="species" className="data-[state=active]:bg-[var(--bionic-gold-primary)] data-[state=active]:text-black gap-2">
            <Target className="h-4 w-4" /> {t('analytics_by_species') || 'Par espèce'}
          </TabsTrigger>
          <TabsTrigger value="weather" className="data-[state=active]:bg-[var(--bionic-gold-primary)] data-[state=active]:text-black gap-2">
            <Cloud className="h-4 w-4" /> {t('common_weather') || 'Météo'}
          </TabsTrigger>
          <TabsTrigger value="times" className="data-[state=active]:bg-[var(--bionic-gold-primary)] data-[state=active]:text-black gap-2">
            <Clock className="h-4 w-4" /> {t('analytics_times') || 'Horaires'}
          </TabsTrigger>
          <TabsTrigger value="history" className="data-[state=active]:bg-[var(--bionic-gold-primary)] data-[state=active]:text-black gap-2">
            <FileText className="h-4 w-4" /> {t('common_history') || 'Historique'}
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Monthly Trends Chart */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg text-white flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-[#f5a623]" />
                  Tendances mensuelles
                </CardTitle>
              </CardHeader>
              <CardContent>
                {monthly_trends.length > 0 ? (
                  <div className="h-[300px]">
                    <ResponsiveChartContainer width="100%" height={300}>
                      <LightLineChart
                        data={monthly_trends.map(item => ({
                          name: item.month,
                          value: item.trips
                        }))}
                        dataKey="value"
                        nameKey="name"
                        color="#f5a623"
                        showGrid={true}
                        showDots={true}
                        showArea={false}
                      />
                    </ResponsiveChartContainer>
                  </div>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-slate-400">
                    Pas de données disponibles
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Species Pie Chart */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg text-white flex items-center gap-2">
                  <CircleDot className="h-5 w-5 text-[#f5a623]" />
                  Répartition par espèce
                </CardTitle>
              </CardHeader>
              <CardContent>
                {species_breakdown.length > 0 ? (
                  <div className="h-[300px] flex flex-col items-center justify-center">
                    <LightPieChart
                      data={species_breakdown.map(item => ({
                        name: SPECIES_LABELS[item.species] || item.species,
                        value: item.trips,
                        color: SPECIES_COLORS[item.species]
                      }))}
                      size={220}
                      innerRadius={0}
                      showLabels={true}
                      showTooltip={true}
                    />
                  </div>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-slate-400">
                    Pas de données disponibles
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Species Tab */}
        <TabsContent value="species" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Species Bar Chart */}
            <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg text-[var(--bionic-text-primary)] flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-[var(--bionic-gold-primary)]" />
                  {t('analytics_success_by_species') || 'Taux de succès par espèce'}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {species_breakdown.length > 0 ? (
                  <div className="h-[300px]">
                    <ResponsiveChartContainer width="100%" height={300}>
                      <LightBarChart
                        data={species_breakdown.map(item => ({
                          name: SPECIES_LABELS[item.species] || item.species,
                          value: item.success_rate,
                          color: SPECIES_COLORS[item.species]
                        }))}
                        dataKey="value"
                        nameKey="name"
                        color="#22c55e"
                        showGrid={true}
                      />
                    </ResponsiveChartContainer>
                  </div>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-slate-400">
                    Pas de données disponibles
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Species Details */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg text-white flex items-center gap-2">
                  <CircleDot className="h-5 w-5 text-[#f5a623]" />
                  Détails par espèce
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 max-h-[300px] overflow-y-auto">
                  {species_breakdown.map((species, index) => (
                    <div 
                      key={index}
                      className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <div 
                          className="w-4 h-4 rounded-full"
                          style={{ backgroundColor: SPECIES_COLORS[species.species] || '#666' }}
                        />
                        <div>
                          <p className="text-white font-medium">
                            {SPECIES_LABELS[species.species] || species.species}
                          </p>
                          <p className="text-slate-400 text-sm">
                            {species.trips} sorties • {species.total_observations} observations
                          </p>
                        </div>
                      </div>
                      <Badge className={species.success_rate >= 50 ? 'bg-green-600' : 'bg-slate-600'}>
                        {species.success_rate}%
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Weather Tab */}
        <TabsContent value="weather" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Weather Bar Chart */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg text-white flex items-center gap-2">
                  <CloudSun className="h-5 w-5 text-[#f5a623]" />
                  Impact de la météo
                </CardTitle>
              </CardHeader>
              <CardContent>
                {weather_analysis.length > 0 ? (
                  <div className="h-[300px]">
                    <ResponsiveChartContainer width="100%" height={300}>
                      <LightBarChart
                        data={weather_analysis.map(item => ({
                          name: item.condition,
                          value: item.success_rate,
                          color: WEATHER_COLORS[item.condition]
                        }))}
                        dataKey="value"
                        nameKey="name"
                        color="#f5a623"
                        showGrid={true}
                        horizontal={true}
                      />
                    </ResponsiveChartContainer>
                  </div>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-slate-400">
                    Pas de données météo disponibles
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Weather Insights */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg text-white flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-[#f5a623]" />
                  Insights météo
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {weather_analysis.slice(0, 5).map((weather, index) => (
                    <div key={index} className="p-3 bg-slate-700/50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-white font-medium">{weather.condition}</span>
                        <Badge className={weather.success_rate >= 40 ? 'bg-green-600' : 'bg-amber-600'}>
                          {weather.success_rate}% succès
                        </Badge>
                      </div>
                      <div className="flex justify-between text-sm text-slate-400">
                        <span>{weather.trips} sorties</span>
                        <span>{weather.avg_observations} obs. moy.</span>
                      </div>
                    </div>
                  ))}
                  {weather_analysis.length === 0 && (
                    <p className="text-slate-400 text-center py-8">
                      Enregistrez vos sorties avec les conditions météo pour voir ces insights
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Times Tab */}
        <TabsContent value="times" className="mt-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Optimal Times Radar */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg text-white flex items-center gap-2">
                  <Target className="h-5 w-5 text-[#f5a623]" />
                  Heures optimales
                </CardTitle>
              </CardHeader>
              <CardContent>
                {optimal_times.length > 0 ? (
                  <div className="h-[300px] flex items-center justify-center">
                    <LightRadarChart
                      data={optimal_times.map(item => ({
                        name: item.label,
                        value: item.success_rate
                      }))}
                      size={280}
                      color="#f5a623"
                      maxValue={100}
                      showLabels={true}
                    />
                  </div>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-slate-400">
                    Pas de données horaires disponibles
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Time Slots Bar */}
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg text-white flex items-center gap-2">
                  <Clock className="h-5 w-5 text-[#f5a623]" />
                  Activité par créneau
                </CardTitle>
              </CardHeader>
              <CardContent>
                {optimal_times.length > 0 ? (
                  <div className="h-[300px]">
                    <ResponsiveChartContainer width="100%" height={300}>
                      <LightBarChart
                        data={optimal_times.map(item => ({
                          name: `${item.hour}h`,
                          value: item.trips
                        }))}
                        dataKey="value"
                        nameKey="name"
                        color="#3b82f6"
                        showGrid={true}
                      />
                    </ResponsiveChartContainer>
                  </div>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-slate-400">
                    Pas de données horaires disponibles
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history" className="mt-6">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg text-white flex items-center gap-2">
                <Scroll className="h-5 w-5 text-[#f5a623]" />
                Dernières sorties
              </CardTitle>
            </CardHeader>
            <CardContent>
              {recent_trips.length > 0 ? (
                <div className="space-y-3">
                  {recent_trips.map((trip, index) => (
                    <div 
                      key={index}
                      className="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg"
                    >
                      <div className="flex items-center gap-4">
                        <div className={`w-3 h-3 rounded-full ${trip.success ? 'bg-green-500' : 'bg-slate-500'}`} />
                        <div>
                          <p className="text-white font-medium">
                            {SPECIES_LABELS[trip.species] || trip.species}
                          </p>
                          <p className="text-slate-400 text-sm">
                            {new Date(trip.date).toLocaleDateString('fr-CA')} • {trip.duration_hours}h
                            {trip.weather_conditions && ` • ${trip.weather_conditions}`}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-slate-400 text-sm">
                          {trip.observations} obs.
                        </span>
                        <Badge className={trip.success ? 'bg-green-600' : 'bg-slate-600'}>
                          {trip.success ? 'Succès' : 'Sans succès'}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <ClipboardList className="h-12 w-12 text-slate-500 mx-auto" />
                  <p className="text-slate-400 mt-4">Aucune sortie enregistrée</p>
                  <p className="text-slate-500 text-sm">Commencez à enregistrer vos sorties de chasse</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AnalyticsDashboard;
