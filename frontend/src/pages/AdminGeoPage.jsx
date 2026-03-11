/**
 * AdminGeoPage - Global Geospatial Administration Dashboard
 * Phase P6.5 - Admin Dashboard
 * Version: 1.1.0 - BIONIC Design System Compliance
 * 
 * ADMIN ONLY - Cette page n'est jamais visible par les utilisateurs réguliers
 * 
 * Features:
 * - Global view of all geo entities (system only)
 * - Hotspots section (renamed from "Terre à louer")
 * - Advanced filtering by category
 * - "View on map" links for each hotspot
 * 
 * CONFIDENTIALITÉ: Les hotspots personnels des utilisateurs sont EXCLUS
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { toast } from 'sonner';
import { useLanguage } from '../contexts/LanguageContext';
import { 
  MapPin, ExternalLink, Filter, RefreshCw, Loader2, Star, 
  Home, Trees, EyeOff, BarChart3, Flame, Lock, AlertTriangle, PauseCircle
} from 'lucide-react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Hotspot category colors
const CATEGORY_COLORS = {
  standard: '#6b7280',      // Gray
  premium: '#f59e0b',       // Amber
  land_rental: '#10b981',   // Emerald
  environmental: '#3b82f6', // Blue
  inactive: '#ef4444'       // Red
};

// Category labels in French
const CATEGORY_LABELS = {
  standard: 'Hotspot standard',
  premium: 'Hotspot premium',
  land_rental: 'Hotspot Terre à louer',
  environmental: 'Hotspot environnemental',
  inactive: 'Hotspot inactif'
};

// Category icons - BIONIC Design System Lucide Icons
const CATEGORY_ICONS = {
  standard: MapPin,
  premium: Star,
  land_rental: Home,
  environmental: Trees,
  inactive: EyeOff
};

// Habitat labels
const HABITAT_LABELS = {
  forest_mixed: 'Forêt mixte',
  forest_coniferous: 'Forêt conifère',
  forest_deciduous: 'Forêt feuillue',
  clearing: 'Clairière',
  wetland: 'Zone humide',
  field: 'Champ',
  edge: 'Lisière',
  ridge: 'Crête',
  valley: 'Vallée',
  stream: 'Cours d\'eau'
};

const AdminGeoPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState(null);
  const [hotspots, setHotspots] = useState([]);
  const [hotspotStats, setHotspotStats] = useState({});
  const [categoryFilter, setCategoryFilter] = useState('');
  const [mapCenter] = useState([46.82, -71.21]);
  const [activeTab, setActiveTab] = useState('overview');

  // Load analytics
  const loadAnalytics = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/admin/geo/analytics/overview`);
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error('Error loading analytics:', error);
      toast.error('Erreur lors du chargement des analytics');
    }
  }, []);

  // Load hotspots (admin only - excludes user personal hotspots)
  const loadHotspots = useCallback(async () => {
    try {
      let url = `${API_URL}/api/admin/geo/hotspots?limit=200`;
      if (categoryFilter) {
        url += `&category=${categoryFilter}`;
      }
      
      const response = await fetch(url);
      const data = await response.json();
      setHotspots(data.hotspots || []);
      setHotspotStats(data.by_category || {});
    } catch (error) {
      console.error('Error loading hotspots:', error);
      toast.error('Erreur lors du chargement des hotspots');
    }
  }, [categoryFilter]);

  // Initial load
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([loadAnalytics(), loadHotspots()]);
      setLoading(false);
    };
    loadData();
  }, [loadAnalytics, loadHotspots]);

  // Reload hotspots when filter changes
  useEffect(() => {
    loadHotspots();
  }, [categoryFilter, loadHotspots]);

  // Navigate to map centered on hotspot
  const viewOnMap = (hotspot) => {
    if (hotspot.latitude && hotspot.longitude) {
      navigate(`/map?lat=${hotspot.latitude}&lng=${hotspot.longitude}&zoom=17`);
    } else {
      toast.error('Coordonnées non disponibles');
    }
  };

  // Get badge variant based on category
  const getCategoryBadgeClass = (category) => {
    const classes = {
      standard: 'bg-gray-500',
      premium: 'bg-amber-500',
      land_rental: 'bg-emerald-500',
      environmental: 'bg-blue-500',
      inactive: 'bg-red-500'
    };
    return classes[category] || 'bg-gray-500';
  };

  // Render stats card with icon component
  const StatsCard = ({ title, value, Icon, color = 'blue' }) => (
    <Card className="bg-slate-800/50 border-slate-700">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm">{title}</p>
            <p className={`text-2xl font-bold text-${color}-400`}>{value}</p>
          </div>
          <Icon className={`h-8 w-8 text-${color}-400`} />
        </div>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Chargement de l'espace admin...</div>
      </div>
    );
  }

  return (
    <div 
      className="fixed inset-0 bg-slate-900 flex flex-col overflow-hidden" 
      style={{ paddingTop: '64px' }}
      data-testid="admin-geo-page"
    >
      {/* Header Compact */}
      <div className="flex-shrink-0 px-4 py-2 border-b border-slate-700/50">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-white flex items-center gap-2">
              <Lock className="h-5 w-5 text-[#f5a623]" /> Espace Admin Géospatial
            </h1>
            <p className="text-slate-400 text-xs">
              Administration des hotspots système • Phase P6.5
            </p>
          </div>
          <p className="text-amber-400 text-xs flex items-center gap-1">
            <AlertTriangle className="h-3 w-3" /> Hotspots personnels exclus
          </p>
        </div>
      </div>

      {/* Quick Stats - Compact */}
      <div className="flex-shrink-0 px-4 py-2">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
          <StatsCard 
            title="Total Hotspots" 
            value={hotspots.length} 
            Icon={Flame}
            color="red"
          />
          <StatsCard 
            title="Premium" 
            value={hotspotStats.premium || 0} 
            Icon={Star}
            color="amber"
          />
          <StatsCard 
            title="Terre à louer" 
            value={hotspotStats.land_rental || 0} 
            Icon={Home}
            color="emerald"
          />
          <StatsCard 
            title="Environnemental" 
            value={hotspotStats.environmental || 0} 
            Icon={Trees}
            color="blue"
          />
          <StatsCard 
            title="Inactifs" 
            value={hotspotStats.inactive || 0} 
            Icon={PauseCircle}
            color="gray"
          />
        </div>
      </div>

      {/* Main Content Tabs - Full Height */}
      <div className="flex-1 overflow-hidden px-4 pb-4">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
          <TabsList className="bg-slate-800 mb-2 flex-shrink-0">
            <TabsTrigger value="overview" className="data-[state=active]:bg-blue-600">
              Vue d'ensemble
            </TabsTrigger>
            <TabsTrigger value="hotspots" className="data-[state=active]:bg-red-600 flex items-center gap-1">
              <Flame className="h-4 w-4" /> Hotspots
            </TabsTrigger>
            <TabsTrigger value="map" className="data-[state=active]:bg-emerald-600">
              Carte
            </TabsTrigger>
          </TabsList>

          <div className="flex-1 overflow-hidden">

        {/* Overview Tab */}
        <TabsContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* By Category Chart */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Répartition par catégorie</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(hotspotStats).map(([category, count]) => {
                    const IconComponent = CATEGORY_ICONS[category] || MapPin;
                    return (
                      <div key={category} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <IconComponent className="h-5 w-5 text-slate-400" />
                          <span className="text-slate-300">{CATEGORY_LABELS[category] || category}</span>
                        </div>
                        <Badge className={getCategoryBadgeClass(category)}>{count}</Badge>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Analytics Summary */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Statistiques globales</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Total entités système</span>
                    <span className="text-white font-bold">{analytics?.total_entities || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Auto-générés</span>
                    <span className="text-blue-400 font-bold">{analytics?.auto_generated_count || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Premium disponibles</span>
                    <span className="text-amber-400 font-bold">{analytics?.premium_hotspots || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Confiance moyenne</span>
                    <span className="text-emerald-400 font-bold">
                      {analytics?.avg_confidence ? `${(analytics.avg_confidence * 100).toFixed(0)}%` : 'N/A'}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Hotspots Tab (renamed from "Terre à louer") */}
        <TabsContent value="hotspots">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <Flame className="h-5 w-5 text-red-400" /> Hotspots Administratifs ({hotspots.length})
                </span>
                <div className="flex items-center gap-2">
                  <Filter className="h-4 w-4 text-slate-400" />
                  <select
                    className="bg-slate-700 text-white px-3 py-1 rounded text-sm"
                    value={categoryFilter}
                    onChange={(e) => setCategoryFilter(e.target.value)}
                  >
                    <option value="">Toutes catégories</option>
                    <option value="standard">Standard</option>
                    <option value="premium">Premium</option>
                    <option value="land_rental">Terre à louer</option>
                    <option value="environmental">Environnemental</option>
                    <option value="inactive">Inactif</option>
                  </select>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => loadHotspots()}
                  >
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-slate-700">
                      <th className="text-slate-400 pb-3 font-medium">Nom</th>
                      <th className="text-slate-400 pb-3 font-medium">Catégorie</th>
                      <th className="text-slate-400 pb-3 font-medium">Coordonnées GPS</th>
                      <th className="text-slate-400 pb-3 font-medium">Statut</th>
                      <th className="text-slate-400 pb-3 font-medium">Confiance</th>
                      <th className="text-slate-400 pb-3 font-medium">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {hotspots.map((hotspot) => {
                      const IconComponent = CATEGORY_ICONS[hotspot.category] || MapPin;
                      return (
                        <tr key={hotspot.id} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                          <td className="py-4">
                            <div className="flex items-center gap-2">
                              <IconComponent className="h-5 w-5 text-slate-400" />
                              <span className="text-white font-medium">{hotspot.name}</span>
                            </div>
                          </td>
                        <td className="py-4">
                          <Badge className={getCategoryBadgeClass(hotspot.category)}>
                            {hotspot.category_label}
                          </Badge>
                        </td>
                        <td className="py-4">
                          <div className="text-slate-300 font-mono text-sm">
                            <div>Lat: {hotspot.latitude?.toFixed(6) || 'N/A'}</div>
                            <div>Lng: {hotspot.longitude?.toFixed(6) || 'N/A'}</div>
                          </div>
                        </td>
                        <td className="py-4">
                          <span className={`text-sm ${hotspot.active ? 'text-emerald-400' : 'text-red-400'}`}>
                            {hotspot.status}
                          </span>
                        </td>
                        <td className="py-4">
                          {hotspot.confidence ? (
                            <Badge className={hotspot.confidence > 0.7 ? 'bg-emerald-500' : hotspot.confidence > 0.4 ? 'bg-amber-500' : 'bg-gray-500'}>
                              {(hotspot.confidence * 100).toFixed(0)}%
                            </Badge>
                          ) : (
                            <span className="text-slate-500">-</span>
                          )}
                        </td>
                        <td className="py-4">
                          <Button 
                            size="sm" 
                            variant="outline"
                            className="flex items-center gap-1 text-blue-400 hover:text-blue-300"
                            onClick={() => viewOnMap(hotspot)}
                          >
                            <MapPin className="h-4 w-4" />
                            Voir sur la carte
                            <ExternalLink className="h-3 w-3" />
                          </Button>
                        </td>
                      </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              
              {hotspots.length === 0 && (
                <div className="text-center py-12">
                  <p className="text-slate-500 text-lg">
                    Aucun hotspot administratif trouvé pour ce filtre.
                  </p>
                  <p className="text-slate-600 text-sm mt-2">
                    Les hotspots personnels des utilisateurs ne sont pas affichés (confidentialité).
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Map Tab */}
        <TabsContent value="map">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">
                Carte des Hotspots Administratifs
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[500px] rounded-lg overflow-hidden">
                <MapContainer
                  center={mapCenter}
                  zoom={10}
                  style={{ height: '100%', width: '100%' }}
                >
                  <TileLayer
                    attribution='&copy; OpenStreetMap'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  {hotspots.map((hotspot) => (
                    hotspot.latitude && hotspot.longitude && (
                      <CircleMarker
                        key={hotspot.id}
                        center={[hotspot.latitude, hotspot.longitude]}
                        radius={10}
                        pathOptions={{
                          fillColor: CATEGORY_COLORS[hotspot.category] || '#6b7280',
                          fillOpacity: 0.8,
                          color: '#fff',
                          weight: 2
                        }}
                      >
                        <Popup>
                          <div className="text-sm min-w-[200px]">
                            <strong className="text-base">{hotspot.name}</strong>
                            <hr className="my-2" />
                            <p><strong>Catégorie:</strong> {hotspot.category_label}</p>
                            <p><strong>Statut:</strong> {hotspot.status}</p>
                            <p><strong>Latitude:</strong> {hotspot.latitude?.toFixed(6)}</p>
                            <p><strong>Longitude:</strong> {hotspot.longitude?.toFixed(6)}</p>
                            {hotspot.confidence && (
                              <p><strong>Confiance:</strong> {(hotspot.confidence * 100).toFixed(0)}%</p>
                            )}
                            {hotspot.habitat && (
                              <p><strong>Habitat:</strong> {HABITAT_LABELS[hotspot.habitat] || hotspot.habitat}</p>
                            )}
                          </div>
                        </Popup>
                      </CircleMarker>
                    )
                  ))}
                </MapContainer>
              </div>
              {/* Legend */}
              <div className="mt-4 flex flex-wrap gap-4">
                {Object.entries(CATEGORY_COLORS).map(([category, color]) => (
                  <div key={category} className="flex items-center gap-2">
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: color }}
                    />
                    <span className="text-slate-400 text-sm">{CATEGORY_LABELS[category]}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
          </div>
      </Tabs>
      </div>
    </div>
  );
};

export default AdminGeoPage;
