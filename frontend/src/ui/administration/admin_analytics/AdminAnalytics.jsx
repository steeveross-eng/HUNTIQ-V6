/**
 * AdminAnalytics - V5-ULTIME Administration Premium
 * ==================================================
 * 
 * Module d'administration Analytics intégré à la Vitrine Admin Premium.
 * Réutilise l'Analytics Engine existant avec interface admin.
 * 
 * Module isolé - Architecture LEGO V5.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import {
  BarChart3, TrendingUp, Target, Cloud, Clock, Eye,
  RefreshCw, Download, FileText, Users, Activity,
  Calendar, Zap, PieChart, ArrowUp, ArrowDown,
  Settings, Database, Play, Trash2, AlertTriangle
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

const TIME_RANGES = [
  { value: 'week', label: 'Semaine' },
  { value: 'month', label: 'Mois' },
  { value: 'season', label: 'Saison' },
  { value: 'year', label: 'Année' },
  { value: 'all', label: 'Tout' }
];

const SPECIES_LABELS = {
  deer: 'Cerf',
  moose: 'Orignal',
  bear: 'Ours',
  wild_turkey: 'Dindon',
  duck: 'Canard',
  elk: 'Wapiti'
};

const AdminAnalytics = () => {
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [timeRange, setTimeRange] = useState('all');
  const [dashboard, setDashboard] = useState(null);
  const [trips, setTrips] = useState([]);
  const [moduleInfo, setModuleInfo] = useState(null);

  useEffect(() => {
    loadData();
  }, [activeTab, timeRange]);

  const loadData = async () => {
    setLoading(true);
    try {
      // Module info
      const infoRes = await fetch(`${API_BASE}/api/v1/analytics/`);
      const infoData = await infoRes.json();
      setModuleInfo(infoData);

      if (activeTab === 'dashboard' || activeTab === 'overview') {
        const dashRes = await fetch(`${API_BASE}/api/v1/analytics/dashboard?time_range=${timeRange}`);
        const dashData = await dashRes.json();
        setDashboard(dashData);
      }

      if (activeTab === 'trips') {
        const tripsRes = await fetch(`${API_BASE}/api/v1/analytics/trips?time_range=${timeRange}&limit=100`);
        const tripsData = await tripsRes.json();
        setTrips(tripsData || []);
      }
    } catch (error) {
      console.error('Error loading analytics data:', error);
    }
    setLoading(false);
  };

  const seedDemoData = async () => {
    if (!window.confirm('Générer des données de démonstration ?')) return;
    
    try {
      const res = await fetch(`${API_BASE}/api/v1/analytics/seed`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        alert(`${data.count} sorties de démonstration créées !`);
        loadData();
      }
    } catch (error) {
      console.error('Error seeding data:', error);
    }
  };

  const deleteTrip = async (tripId) => {
    if (!window.confirm('Supprimer cette sortie ?')) return;
    
    try {
      await fetch(`${API_BASE}/api/v1/analytics/trips/${tripId}`, { method: 'DELETE' });
      loadData();
    } catch (error) {
      console.error('Error deleting trip:', error);
    }
  };

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'overview', label: 'KPIs', icon: Target },
    { id: 'species', label: 'Espèces', icon: PieChart },
    { id: 'weather', label: 'Météo', icon: Cloud },
    { id: 'times', label: 'Horaires', icon: Clock },
    { id: 'trips', label: 'Sorties', icon: Calendar },
    { id: 'admin', label: 'Admin', icon: Settings }
  ];

  const getSuccessRateColor = (rate) => {
    if (rate >= 70) return 'text-green-400';
    if (rate >= 40) return 'text-yellow-400';
    return 'text-red-400';
  };

  // ============ DASHBOARD TAB ============
  const renderDashboard = () => {
    if (!dashboard) return <LoadingState />;

    const { overview } = dashboard;

    return (
      <div className="space-y-6">
        {/* KPIs principaux */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Total sorties</p>
                <p className="text-2xl font-bold text-white">{overview?.total_trips || 0}</p>
              </div>
              <Calendar className="h-8 w-8 text-[#F5A623]" />
            </div>
          </Card>

          <Card className="bg-[#0f0f1a] border-green-500/20 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Taux de succès</p>
                <p className={`text-2xl font-bold ${getSuccessRateColor(overview?.success_rate || 0)}`}>
                  {(overview?.success_rate || 0).toFixed(1)}%
                </p>
              </div>
              <Target className="h-8 w-8 text-green-400" />
            </div>
          </Card>

          <Card className="bg-[#0f0f1a] border-blue-500/20 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Heures totales</p>
                <p className="text-2xl font-bold text-blue-400">{overview?.total_hours || 0}h</p>
              </div>
              <Clock className="h-8 w-8 text-blue-400" />
            </div>
          </Card>

          <Card className="bg-[#0f0f1a] border-purple-500/20 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">Observations</p>
                <p className="text-2xl font-bold text-purple-400">{overview?.total_observations || 0}</p>
              </div>
              <Eye className="h-8 w-8 text-purple-400" />
            </div>
          </Card>
        </div>

        {/* Graphiques */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Répartition par espèce */}
          <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
            <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
              <PieChart className="h-5 w-5 text-[#F5A623]" />
              Répartition par espèce
            </h3>
            <div className="space-y-3">
              {dashboard?.species_breakdown?.map((species, idx) => (
                <div key={idx} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-[#F5A623]" style={{ opacity: 1 - idx * 0.15 }} />
                    <span className="text-gray-300">{SPECIES_LABELS[species.species] || species.species}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-gray-400 text-sm">{species.trip_count} sorties</span>
                    <Badge className={`${getSuccessRateColor(species.success_rate)} bg-transparent`}>
                      {species.success_rate?.toFixed(0)}%
                    </Badge>
                  </div>
                </div>
              )) || <p className="text-gray-500">Aucune donnée</p>}
            </div>
          </Card>

          {/* Analyse météo */}
          <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
            <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
              <Cloud className="h-5 w-5 text-[#F5A623]" />
              Impact météo
            </h3>
            <div className="space-y-3">
              {dashboard?.weather_analysis?.map((weather, idx) => (
                <div key={idx} className="flex items-center justify-between">
                  <span className="text-gray-300">{weather.condition}</span>
                  <div className="flex items-center gap-4">
                    <span className="text-gray-400 text-sm">{weather.trip_count} sorties</span>
                    <Badge className={`${getSuccessRateColor(weather.success_rate)} bg-transparent`}>
                      {weather.success_rate?.toFixed(0)}%
                    </Badge>
                  </div>
                </div>
              )) || <p className="text-gray-500">Aucune donnée</p>}
            </div>
          </Card>
        </div>

        {/* Tendances */}
        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
          <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-[#F5A623]" />
            Tendances mensuelles
          </h3>
          <div className="flex flex-wrap gap-4">
            {dashboard?.monthly_trends?.map((month, idx) => (
              <div key={idx} className="p-3 bg-[#1a1a2e] rounded-lg text-center min-w-[80px]">
                <p className="text-gray-400 text-xs">{month.month}</p>
                <p className="text-white font-bold">{month.trip_count}</p>
                <p className={`text-xs ${getSuccessRateColor(month.success_rate)}`}>
                  {month.success_rate?.toFixed(0)}%
                </p>
              </div>
            )) || <p className="text-gray-500">Aucune donnée</p>}
          </div>
        </Card>
      </div>
    );
  };

  // ============ TRIPS TAB ============
  const renderTrips = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-white font-semibold">Historique des sorties</h3>
        <Badge className="bg-[#F5A623]/20 text-[#F5A623] border border-[#F5A623]/30">
          {trips.length} sorties
        </Badge>
      </div>

      {trips.length > 0 ? (
        <div className="space-y-2">
          {trips.map((trip, idx) => (
            <Card key={idx} className="bg-[#0f0f1a] border-[#F5A623]/20 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`p-2 rounded-lg ${trip.success ? 'bg-green-500/20' : 'bg-gray-700'}`}>
                    <Target className={`h-5 w-5 ${trip.success ? 'text-green-400' : 'text-gray-400'}`} />
                  </div>
                  <div>
                    <p className="text-white font-medium">
                      {SPECIES_LABELS[trip.species] || trip.species}
                    </p>
                    <p className="text-gray-400 text-sm">
                      {new Date(trip.date).toLocaleDateString('fr-CA')} • {trip.duration_hours}h
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-gray-400 text-sm">{trip.observations} obs.</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => deleteTrip(trip.id)}
                    className="text-red-400 hover:text-red-300"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-8 text-center">
          <Calendar className="h-12 w-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">Aucune sortie enregistrée</p>
          <Button onClick={seedDemoData} className="mt-4 bg-[#F5A623] text-black">
            <Play className="h-4 w-4 mr-2" />
            Générer données démo
          </Button>
        </Card>
      )}
    </div>
  );

  // ============ ADMIN TAB ============
  const renderAdmin = () => (
    <div className="space-y-6">
      {/* Module Info */}
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Database className="h-5 w-5 text-[#F5A623]" />
          Information Module
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-gray-400 text-sm">Module</p>
            <p className="text-white">{moduleInfo?.module || 'analytics_engine'}</p>
          </div>
          <div>
            <p className="text-gray-400 text-sm">Version</p>
            <p className="text-white">{moduleInfo?.version || '1.0.0'}</p>
          </div>
        </div>
      </Card>

      {/* Endpoints */}
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Zap className="h-5 w-5 text-[#F5A623]" />
          Endpoints disponibles
        </h3>
        <div className="space-y-2">
          {moduleInfo?.endpoints?.map((endpoint, idx) => (
            <div key={idx} className="p-2 bg-[#1a1a2e] rounded text-gray-300 text-sm font-mono">
              {endpoint}
            </div>
          ))}
        </div>
      </Card>

      {/* Actions Admin */}
      <Card className="bg-[#0f0f1a] border-[#F5A623]/20 p-6">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Settings className="h-5 w-5 text-[#F5A623]" />
          Actions administrateur
        </h3>
        <div className="flex flex-wrap gap-3">
          <Button onClick={seedDemoData} className="bg-green-500/20 text-green-400 hover:bg-green-500/30">
            <Play className="h-4 w-4 mr-2" />
            Générer données démo
          </Button>
          <Button onClick={loadData} variant="outline" className="border-[#F5A623]/30 text-[#F5A623]">
            <RefreshCw className="h-4 w-4 mr-2" />
            Rafraîchir données
          </Button>
        </div>
      </Card>

      {/* Warning */}
      <Card className="bg-[#0f0f1a] border-yellow-500/20 p-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-yellow-400 mt-0.5" />
          <div>
            <p className="text-white font-medium">Module Analytics V1</p>
            <p className="text-gray-400 text-sm mt-1">
              Ce module fait partie de l'Analytics Engine existant. Les données sont stockées dans MongoDB
              et partagées avec le dashboard public `/analytics`.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );

  const LoadingState = () => (
    <div className="flex items-center justify-center py-12">
      <RefreshCw className="h-8 w-8 text-[#F5A623] animate-spin" />
    </div>
  );

  return (
    <div data-testid="admin-analytics-module" className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <BarChart3 className="h-8 w-8 text-[#F5A623]" />
          <div>
            <h2 className="text-2xl font-bold text-white">Analytics Engine</h2>
            <p className="text-gray-400 text-sm">Statistiques et KPIs de chasse</p>
          </div>
        </div>
        <Badge className="bg-[#F5A623]/20 text-[#F5A623] border border-[#F5A623]/30 px-4 py-2">
          LEGO V5 Isolé
        </Badge>
      </div>

      {/* Time Range Filter */}
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-gray-400 text-sm">Période:</span>
        {TIME_RANGES.map(range => (
          <Button
            key={range.value}
            size="sm"
            variant={timeRange === range.value ? 'default' : 'outline'}
            onClick={() => setTimeRange(range.value)}
            className={timeRange === range.value 
              ? 'bg-[#F5A623] text-black hover:bg-[#F5A623]/80' 
              : 'border-gray-600 text-gray-400'}
          >
            {range.label}
          </Button>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-[#F5A623]/10 pb-2">
        {tabs.map((tab) => (
          <Button
            key={tab.id}
            data-testid={`analytics-tab-${tab.id}`}
            variant="ghost"
            onClick={() => setActiveTab(tab.id)}
            className={`
              ${activeTab === tab.id
                ? 'bg-[#F5A623]/10 text-[#F5A623] border-b-2 border-[#F5A623]'
                : 'text-gray-400 hover:text-white'
              }
            `}
          >
            <tab.icon className="h-4 w-4 mr-2" />
            {tab.label}
          </Button>
        ))}
      </div>

      {/* Content */}
      {loading ? (
        <LoadingState />
      ) : (
        <>
          {activeTab === 'dashboard' && renderDashboard()}
          {activeTab === 'overview' && renderDashboard()}
          {activeTab === 'species' && renderDashboard()}
          {activeTab === 'weather' && renderDashboard()}
          {activeTab === 'times' && renderDashboard()}
          {activeTab === 'trips' && renderTrips()}
          {activeTab === 'admin' && renderAdmin()}
        </>
      )}
    </div>
  );
};

export { AdminAnalytics };
export default AdminAnalytics;
