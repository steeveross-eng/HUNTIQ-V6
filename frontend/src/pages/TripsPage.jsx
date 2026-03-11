/**
 * TripsPage - Hunting Trip Management Page
 * Phase P4+ - Real Data Logging
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { useLanguage } from '@/contexts/LanguageContext';
import {
  Plus, Play, Square, CheckCircle, XCircle, Clock, MapPin,
  Eye, Footprints, Volume2, Leaf, Target, Calendar, Thermometer,
  Wind, Cloud, BarChart3, TrendingUp, Activity, Loader2,
  ChevronRight, AlertTriangle
} from 'lucide-react';
import TripService from '@/services/TripService';
import CreateTripModal from '@/components/trips/CreateTripModal';
import ActiveTripPanel from '@/components/trips/ActiveTripPanel';
import TripStatsDashboard from '@/components/trips/TripStatsDashboard';
import TripHistory from '@/components/trips/TripHistory';
import { GlobalContainer } from '@/core/layouts';

const TripsPage = () => {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState('active');
  const [activeTrip, setActiveTrip] = useState(null);
  const [trips, setTrips] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Load data on mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [activeTripRes, tripsRes, statsRes] = await Promise.all([
        TripService.getActiveTrip(),
        TripService.listTrips(null, 50),
        TripService.getStatistics()
      ]);

      if (activeTripRes.active && activeTripRes.trip) {
        setActiveTrip(activeTripRes.trip);
        setActiveTab('active');
      } else {
        setActiveTrip(null);
      }

      setTrips(Array.isArray(tripsRes) ? tripsRes : []);
      
      if (statsRes.success && statsRes.statistics) {
        setStatistics(statsRes.statistics);
      }
    } catch (error) {
      console.error('Error loading trip data:', error);
      toast.error('Erreur de chargement des données');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleTripCreated = (trip) => {
    setShowCreateModal(false);
    setTrips(prev => [trip, ...prev]);
    toast.success('Sortie créée avec succès!');
  };

  const handleTripStarted = (trip) => {
    setActiveTrip(trip);
    setActiveTab('active');
    loadData();
    toast.success('Sortie démarrée! Bonne chasse!');
  };

  const handleTripEnded = () => {
    setActiveTrip(null);
    loadData();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 pt-20 pb-12 px-4 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-[#f5a623] animate-spin mx-auto mb-4" />
          <p className="text-gray-400">{t('common_loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900" data-testid="trips-page">
      <GlobalContainer className="pb-12">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-3">
              <Target className="h-7 w-7 text-[#f5a623]" />
              {t('trips_title')}
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              {t('trips_stats')} • Phase P4+
            </p>
          </div>
          
          {!activeTrip && (
            <Button
              onClick={() => setShowCreateModal(true)}
              className="bg-[#f5a623] hover:bg-[#d4890e] text-black font-semibold"
              data-testid="create-trip-btn"
            >
              <Plus className="h-4 w-4 mr-2" />
              {t('trips_start_new')}
            </Button>
          )}
        </div>

        {/* Active Trip Alert */}
        {activeTrip && (
          <div className="mb-6 bg-emerald-900/30 border border-emerald-700 rounded-lg p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse" />
              <div>
                <p className="text-emerald-400 font-medium">{t('trips_active')}</p>
                <p className="text-gray-400 text-sm">{activeTrip.title} - {activeTrip.target_species}</p>
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setActiveTab('active')}
              className="border-emerald-600 text-emerald-400 hover:bg-emerald-900/50"
            >
              {t('common_view')}
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        )}

        {/* Quick Stats */}
        {statistics && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-500/20 rounded-lg">
                    <Calendar className="h-5 w-5 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white">{statistics.total_trips}</p>
                    <p className="text-xs text-gray-400">{t('trips_total_trips')}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-slate-800/50 border-slate-700">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-emerald-500/20 rounded-lg">
                    <Target className="h-5 w-5 text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white">{statistics.success_rate}%</p>
                    <p className="text-xs text-gray-400">Taux de succès</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-slate-800/50 border-slate-700">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-amber-500/20 rounded-lg">
                    <Clock className="h-5 w-5 text-amber-400" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white">{statistics.total_hours}h</p>
                    <p className="text-xs text-gray-400">Heures totales</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-slate-800/50 border-slate-700">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-500/20 rounded-lg">
                    <Eye className="h-5 w-5 text-purple-400" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white">{statistics.total_observations}</p>
                    <p className="text-xs text-gray-400">Observations</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="bg-slate-800/50 mb-6">
            <TabsTrigger 
              value="active" 
              className="data-[state=active]:bg-emerald-600"
              data-testid="tab-active"
            >
              <Activity className="h-4 w-4 mr-2" />
              Sortie Active
              {activeTrip && <span className="ml-2 w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />}
            </TabsTrigger>
            <TabsTrigger 
              value="history" 
              className="data-[state=active]:bg-blue-600"
              data-testid="tab-history"
            >
              <Calendar className="h-4 w-4 mr-2" />
              Historique
            </TabsTrigger>
            <TabsTrigger 
              value="statistics" 
              className="data-[state=active]:bg-purple-600"
              data-testid="tab-statistics"
            >
              <BarChart3 className="h-4 w-4 mr-2" />
              Statistiques
            </TabsTrigger>
          </TabsList>

          <TabsContent value="active" className="mt-0">
            {activeTrip ? (
              <ActiveTripPanel 
                trip={activeTrip} 
                onTripEnded={handleTripEnded}
                onRefresh={loadData}
              />
            ) : (
              <Card className="bg-slate-800/30 border-slate-700">
                <CardContent className="p-12 text-center">
                  <div className="w-16 h-16 bg-slate-700/50 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Target className="h-8 w-8 text-gray-500" />
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-2">Aucune sortie en cours</h3>
                  <p className="text-gray-400 mb-6">
                    Créez une nouvelle sortie pour commencer à logger vos observations
                  </p>
                  <Button
                    onClick={() => setShowCreateModal(true)}
                    className="bg-[#f5a623] hover:bg-[#d4890e] text-black font-semibold"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Créer une sortie
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="history" className="mt-0">
            <TripHistory 
              trips={trips} 
              onTripStarted={handleTripStarted}
              onRefresh={loadData}
            />
          </TabsContent>

          <TabsContent value="statistics" className="mt-0">
            <TripStatsDashboard statistics={statistics} />
          </TabsContent>
        </Tabs>

        {/* Create Trip Modal */}
        <CreateTripModal
          open={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onTripCreated={handleTripCreated}
        />
      </GlobalContainer>
    </div>
  );
};

export default TripsPage;
