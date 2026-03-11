/**
 * TerritoireDashboard - V5-ULTIME
 * ================================
 * 
 * Dashboard principal du module Territoire.
 * Composant parent isolé - aucun import croisé.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  MapPin, Layers, TreePine, Mountain, Droplets, 
  Compass, LocateFixed, Plus, Settings, Eye,
  ChevronRight, Activity, Target
} from 'lucide-react';
import { LightPieChart, ResponsiveChartContainer } from '@/components/charts/LightCharts';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// Service local du module
const TerritoireService = {
  async getZones(userId) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/territory/zones?user_id=${userId}`);
      return response.json();
    } catch (error) {
      console.error('Territory API error:', error);
      return null;
    }
  },
  
  async getWaypoints(userId) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/territory/waypoints?user_id=${userId}`);
      return response.json();
    } catch (error) {
      return null;
    }
  },
  
  async getAnalysis(zoneId) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/territory/analysis/${zoneId}`);
      return response.json();
    } catch (error) {
      return null;
    }
  }
};

// Composants locaux
const ZoneCard = ({ zone, onClick }) => {
  const typeColors = {
    hunting: '#F5A623',
    feeding: '#22c55e',
    resting: '#3b82f6',
    transit: '#8b5cf6',
  };

  return (
    <div 
      className="p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer border border-white/10"
      onClick={() => onClick?.(zone)}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div 
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: typeColors[zone.type] || '#F5A623' }}
          />
          <div>
            <h4 className="text-white font-medium">{zone.name}</h4>
            <p className="text-gray-500 text-xs capitalize">{zone.type}</p>
          </div>
        </div>
        <Badge variant="outline" className="text-xs">
          {zone.area_ha || 0} ha
        </Badge>
      </div>
      
      <div className="flex items-center justify-between text-xs text-gray-400">
        <span className="flex items-center gap-1">
          <MapPin className="h-3 w-3" />
          {zone.waypoints_count || 0} waypoints
        </span>
        <span className="flex items-center gap-1">
          <Activity className="h-3 w-3" />
          Score: {zone.score || 75}
        </span>
      </div>
    </div>
  );
};

const WaypointList = ({ waypoints }) => {
  const typeIcons = {
    stand: <Target className="h-4 w-4 text-[#F5A623]" />,
    trail: <Compass className="h-4 w-4 text-blue-400" />,
    water: <Droplets className="h-4 w-4 text-cyan-400" />,
    food: <TreePine className="h-4 w-4 text-green-400" />,
  };

  return (
    <div className="space-y-2 max-h-64 overflow-y-auto">
      {waypoints.map((wp, idx) => (
        <div 
          key={idx}
          className="flex items-center justify-between p-2 bg-white/5 rounded-lg hover:bg-white/10"
        >
          <div className="flex items-center gap-3">
            {typeIcons[wp.type] || <MapPin className="h-4 w-4 text-gray-400" />}
            <div>
              <p className="text-white text-sm">{wp.name}</p>
              <p className="text-gray-500 text-xs">{wp.lat?.toFixed(4)}, {wp.lng?.toFixed(4)}</p>
            </div>
          </div>
          <Button size="sm" variant="ghost" className="h-6 px-2">
            <Eye className="h-3 w-3" />
          </Button>
        </div>
      ))}
    </div>
  );
};

const TerritoireDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [zones, setZones] = useState([]);
  const [waypoints, setWaypoints] = useState([]);
  const [selectedZone, setSelectedZone] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      
      const [zonesData, waypointsData] = await Promise.all([
        TerritoireService.getZones('current_user'),
        TerritoireService.getWaypoints('current_user')
      ]);
      
      if (zonesData?.zones) setZones(zonesData.zones);
      if (waypointsData?.waypoints) setWaypoints(waypointsData.waypoints);
      
      setLoading(false);
    };
    
    fetchData();
  }, []);

  // Données de démonstration
  const demoZones = [
    { id: 1, name: 'Zone Nord', type: 'hunting', area_ha: 45, waypoints_count: 8, score: 82 },
    { id: 2, name: 'Ravine Est', type: 'feeding', area_ha: 12, waypoints_count: 4, score: 75 },
    { id: 3, name: 'Crête Principale', type: 'transit', area_ha: 28, waypoints_count: 6, score: 68 },
    { id: 4, name: 'Marais Sud', type: 'resting', area_ha: 18, waypoints_count: 3, score: 71 },
  ];

  const demoWaypoints = [
    { id: 1, name: 'Mirador Principal', type: 'stand', lat: 46.8139, lng: -71.2080 },
    { id: 2, name: 'Sentier Cerf', type: 'trail', lat: 46.8145, lng: -71.2095 },
    { id: 3, name: 'Point d\'eau', type: 'water', lat: 46.8130, lng: -71.2070 },
    { id: 4, name: 'Zone Nutrition', type: 'food', lat: 46.8155, lng: -71.2100 },
    { id: 5, name: 'Affût Secondaire', type: 'stand', lat: 46.8120, lng: -71.2060 },
  ];

  const demoStats = [
    { name: 'Chasse', value: 45, color: '#F5A623' },
    { name: 'Alimentation', value: 25, color: '#22c55e' },
    { name: 'Transit', value: 20, color: '#8b5cf6' },
    { name: 'Repos', value: 10, color: '#3b82f6' },
  ];

  const displayZones = zones.length > 0 ? zones : demoZones;
  const displayWaypoints = waypoints.length > 0 ? waypoints : demoWaypoints;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#F5A623]" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="territoire-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Layers className="h-6 w-6 text-[#F5A623]" />
            Mon Territoire V5-ULTIME
          </h2>
          <p className="text-gray-400 mt-1">Gestion et analyse de votre territoire de chasse</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="border-white/20">
            <Settings className="h-4 w-4 mr-2" />
            Paramètres
          </Button>
          <Button size="sm" className="bg-[#F5A623] text-black hover:bg-[#F5A623]/90">
            <Plus className="h-4 w-4 mr-2" />
            Nouvelle Zone
          </Button>
        </div>
      </div>

      {/* Stats globales */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-black/40 border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-xs">Surface Totale</p>
                <p className="text-2xl font-bold text-white">103 ha</p>
              </div>
              <Mountain className="h-8 w-8 text-[#F5A623]" />
            </div>
          </CardContent>
        </Card>
        <Card className="bg-black/40 border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-xs">Zones</p>
                <p className="text-2xl font-bold text-white">{displayZones.length}</p>
              </div>
              <Layers className="h-8 w-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>
        <Card className="bg-black/40 border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-xs">Waypoints</p>
                <p className="text-2xl font-bold text-white">{displayWaypoints.length}</p>
              </div>
              <MapPin className="h-8 w-8 text-green-400" />
            </div>
          </CardContent>
        </Card>
        <Card className="bg-black/40 border-white/10">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-xs">Score Moyen</p>
                <p className="text-2xl font-bold text-white">74</p>
              </div>
              <Target className="h-8 w-8 text-purple-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Zones */}
        <div className="lg:col-span-2">
          <Card className="bg-black/40 border-white/10">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-white flex items-center gap-2">
                <Layers className="h-5 w-5 text-[#F5A623]" />
                Mes Zones
              </CardTitle>
              <Button variant="ghost" size="sm" className="text-[#F5A623]">
                Voir tout <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {displayZones.map((zone) => (
                  <ZoneCard 
                    key={zone.id} 
                    zone={zone}
                    onClick={setSelectedZone}
                  />
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Répartition et waypoints */}
        <div className="space-y-6">
          {/* Répartition */}
          <Card className="bg-black/40 border-white/10">
            <CardHeader>
              <CardTitle className="text-white text-sm">Répartition des Zones</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-40 flex items-center justify-center">
                <LightPieChart
                  data={demoStats}
                  size={140}
                  innerRadius={0.5}
                  showLabels={true}
                  showTooltip={true}
                />
              </div>
              <div className="grid grid-cols-2 gap-2 mt-4">
                {demoStats.map((stat, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: stat.color }}
                    />
                    <span className="text-gray-400 text-xs">{stat.name}</span>
                    <span className="text-white text-xs ml-auto">{stat.value}%</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Waypoints récents */}
          <Card className="bg-black/40 border-white/10">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-white text-sm flex items-center gap-2">
                <MapPin className="h-4 w-4 text-[#F5A623]" />
                Waypoints
              </CardTitle>
              <Button variant="ghost" size="sm" className="h-6 px-2 text-[#F5A623]">
                <Plus className="h-3 w-3" />
              </Button>
            </CardHeader>
            <CardContent>
              <WaypointList waypoints={displayWaypoints} />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default TerritoireDashboard;
