/**
 * TerritoryAdvanced - Advanced Territory Features
 * - AI Recommendations by species/season
 * - Map integration with heatmaps
 * - Partnership integration
 * - Scraping admin panel
 */

import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap, Marker, LayerGroup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { useLanguage } from '@/contexts/LanguageContext';
import {
  Sparkles,
  Target,
  MapPin,
  TrendingUp,
  Calendar,
  Loader2,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Zap,
  Trophy,
  Compass,
  Thermometer,
  Users,
  Download,
  Play,
  Database,
  Globe,
  Handshake,
  Map,
  Layers,
  Filter,
  Eye
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// ============================================
// SPECIES CONFIG
// ============================================

const SPECIES_OPTIONS = [
  { id: 'orignal', icon: '🫎', label: 'Orignal' },
  { id: 'chevreuil', icon: '🦌', label: 'Chevreuil' },
  { id: 'ours', icon: '🐻', label: 'Ours noir' },
  { id: 'caribou', icon: '🦌', label: 'Caribou' },
  { id: 'dindon', icon: '🦃', label: 'Dindon sauvage' },
  { id: 'petit_gibier', icon: '🐰', label: 'Petit gibier' }
];

const MONTHS = [
  { value: 1, label: 'Janvier' },
  { value: 2, label: 'Février' },
  { value: 3, label: 'Mars' },
  { value: 4, label: 'Avril' },
  { value: 5, label: 'Mai' },
  { value: 6, label: 'Juin' },
  { value: 7, label: 'Juillet' },
  { value: 8, label: 'Août' },
  { value: 9, label: 'Septembre' },
  { value: 10, label: 'Octobre' },
  { value: 11, label: 'Novembre' },
  { value: 12, label: 'Décembre' }
];

// ============================================
// AI RECOMMENDATIONS COMPONENT
// ============================================

export const AIRecommendations = () => {
  const [species, setSpecies] = useState('orignal');
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [recommendations, setRecommendations] = useState([]);
  const [seasonInfo, setSeasonInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [pressure, setPressure] = useState(0);

  const loadRecommendations = useCallback(async () => {
    setLoading(true);
    try {
      const response = await axios.get(
        `${API}/territories/ai/recommendations/species/${species}?month=${month}&limit=8`
      );
      
      if (response.data.success) {
        setRecommendations(response.data.recommendations);
        setSeasonInfo(response.data.season_info);
        setPressure(response.data.current_pressure);
      }
    } catch (error) {
      console.error('Error loading recommendations:', error);
      toast.error('Erreur lors du chargement des recommandations');
    }
    setLoading(false);
  }, [species, month]);

  useEffect(() => {
    loadRecommendations();
  }, [loadRecommendations]);

  const speciesConfig = SPECIES_OPTIONS.find(s => s.id === species);

  return (
    <div className="space-y-6">
      {/* Filters */}
      <Card className="bg-card border-border">
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-[#f5a623]" />
              <span className="text-white font-semibold">Recommandations IA</span>
            </div>
            
            <Select value={species} onValueChange={setSpecies}>
              <SelectTrigger className="w-[180px] bg-background">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {SPECIES_OPTIONS.map(s => (
                  <SelectItem key={s.id} value={s.id}>
                    {s.icon} {s.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Select value={month.toString()} onValueChange={(v) => setMonth(parseInt(v))}>
              <SelectTrigger className="w-[150px] bg-background">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {MONTHS.map(m => (
                  <SelectItem key={m.value} value={m.value.toString()}>
                    {m.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button variant="outline" onClick={loadRecommendations} disabled={loading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Actualiser
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Season Info */}
      {seasonInfo && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="bg-gradient-to-br from-green-500/20 to-green-600/10 border-green-500/30">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="text-4xl">{speciesConfig?.icon}</div>
                <div>
                  <h4 className="text-white font-semibold">{speciesConfig?.label}</h4>
                  <p className="text-green-400 text-sm">
                    {seasonInfo.is_best_month ? '✨ Mois optimal!' : 'Saison disponible'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-card border-border">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <Calendar className="h-8 w-8 text-blue-400" />
                <div>
                  <h4 className="text-white font-semibold">
                    {seasonInfo.active_season ? 'Saison active' : 'Hors saison'}
                  </h4>
                  <p className="text-gray-400 text-sm">
                    {seasonInfo.active_season?.name || seasonInfo.upcoming_season?.name || 'À venir'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-card border-border">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <Thermometer className={`h-8 w-8 ${pressure > 70 ? 'text-red-400' : pressure > 40 ? 'text-yellow-400' : 'text-green-400'}`} />
                <div>
                  <h4 className="text-white font-semibold">Pression de chasse</h4>
                  <div className="flex items-center gap-2">
                    <Progress value={pressure} className="w-20 h-2" />
                    <span className="text-gray-400 text-sm">{pressure}%</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Recommendations Grid */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {recommendations.map((rec, idx) => (
            <Card 
              key={rec.id} 
              className={`bg-card border-border hover:border-[#f5a623]/50 transition-all ${idx === 0 ? 'ring-2 ring-[#f5a623]' : ''}`}
            >
              <CardContent className="p-4">
                {idx === 0 && (
                  <Badge className="bg-[#f5a623] text-black mb-2">
                    <Trophy className="h-3 w-3 mr-1" /> Top Recommandation
                  </Badge>
                )}
                
                <h4 className="text-white font-semibold mb-1">{rec.name}</h4>
                <p className="text-gray-400 text-sm mb-3">
                  <MapPin className="h-3 w-3 inline mr-1" />
                  {rec.region || rec.province}
                </p>
                
                <div className="flex items-center justify-between mb-3">
                  <span className="text-gray-400 text-xs">Score IA</span>
                  <span className={`text-lg font-bold ${
                    rec.recommendation_score >= 80 ? 'text-green-400' : 
                    rec.recommendation_score >= 60 ? 'text-yellow-400' : 'text-gray-400'
                  }`}>
                    {rec.recommendation_score}
                  </span>
                </div>
                
                {rec.recommendation_reasons && rec.recommendation_reasons.length > 0 && (
                  <div className="space-y-1">
                    {rec.recommendation_reasons.slice(0, 2).map((reason, i) => (
                      <div key={i} className="flex items-center gap-1 text-xs text-gray-400">
                        <CheckCircle className="h-3 w-3 text-green-400" />
                        {reason}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

// ============================================
// SCRAPING ADMIN PANEL
// ============================================

export const ScrapingAdmin = () => {
  const [sources, setSources] = useState([]);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState({});

  const loadData = async () => {
    setLoading(true);
    try {
      const [sourcesRes, statusRes] = await Promise.all([
        axios.get(`${API}/territories/scraping/sources`),
        axios.get(`${API}/territories/scraping/status`)
      ]);
      
      setSources(sourcesRes.data.sources || []);
      setStatus(statusRes.data.status);
    } catch (error) {
      console.error('Error loading scraping data:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  const runScraping = async (sourceId) => {
    setRunning(prev => ({ ...prev, [sourceId]: true }));
    try {
      await axios.post(`${API}/territories/scraping/run/${sourceId}?limit=50`);
      toast.success(`Scraping lancé: ${sourceId}`);
      
      // Wait and refresh
      setTimeout(() => {
        loadData();
        setRunning(prev => ({ ...prev, [sourceId]: false }));
      }, 5000);
    } catch (error) {
      toast.error('Erreur lors du lancement du scraping');
      setRunning(prev => ({ ...prev, [sourceId]: false }));
    }
  };

  const runFullSync = async () => {
    setRunning(prev => ({ ...prev, full: true }));
    try {
      await axios.post(`${API}/territories/scraping/sync/full`);
      toast.success('Synchronisation complète lancée');
      
      setTimeout(() => {
        loadData();
        setRunning(prev => ({ ...prev, full: false }));
      }, 10000);
    } catch (error) {
      toast.error('Erreur lors de la synchronisation');
      setRunning(prev => ({ ...prev, full: false }));
    }
  };

  return (
    <div className="space-y-6">
      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-card border-border">
          <CardContent className="p-4 text-center">
            <Database className="h-8 w-8 text-[#f5a623] mx-auto mb-2" />
            <div className="text-2xl font-bold text-white">{status?.total_territories || 0}</div>
            <div className="text-gray-400 text-sm">Territoires total</div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border">
          <CardContent className="p-4 text-center">
            <Globe className="h-8 w-8 text-blue-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-white">{status?.total_scraped || 0}</div>
            <div className="text-gray-400 text-sm">Scrapés</div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border">
          <CardContent className="p-4 text-center">
            <Button 
              onClick={runFullSync} 
              disabled={running.full}
              className="bg-[#f5a623] hover:bg-[#f5a623]/80 text-black"
            >
              {running.full ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Zap className="h-4 w-4 mr-2" />
              )}
              Sync complète
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Sources List */}
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Database className="h-5 w-5 text-[#f5a623]" />
            Sources de données
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {sources.map(source => (
              <div 
                key={source.id} 
                className="flex items-center justify-between p-3 bg-background rounded-lg border border-border"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${source.enabled ? 'bg-green-500' : 'bg-gray-500'}`} />
                  <div>
                    <h4 className="text-white font-medium">{source.name}</h4>
                    <p className="text-gray-400 text-xs">{source.url}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-white text-sm">{source.items_scraped || 0} items</div>
                    <div className="text-gray-500 text-xs">
                      {source.last_run ? new Date(source.last_run).toLocaleDateString() : 'Jamais'}
                    </div>
                  </div>
                  
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => runScraping(source.id)}
                    disabled={running[source.id]}
                  >
                    {running[source.id] ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Play className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            ))}
            
            {/* Quick Actions */}
            <div className="flex gap-2 pt-4 border-t border-border">
              <Button 
                variant="outline" 
                onClick={() => runScraping('sepaq')}
                disabled={running.sepaq}
              >
                {running.sepaq ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                Sépaq
              </Button>
              <Button 
                variant="outline" 
                onClick={() => runScraping('zec_quebec')}
                disabled={running.zec_quebec}
              >
                {running.zec_quebec ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                ZECs
              </Button>
              <Button 
                variant="outline" 
                onClick={() => runScraping('all')}
                disabled={running.all}
              >
                {running.all ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                Tout scraper
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// ============================================
// POTENTIAL PARTNERS COMPONENT
// ============================================

export const PotentialPartners = () => {
  const [partners, setPartners] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPartners();
  }, []);

  const loadPartners = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/territories/ai/potential-partners?min_score=50&limit=12`);
      if (response.data.success) {
        setPartners(response.data.potential_partners);
      }
    } catch (error) {
      console.error('Error loading potential partners:', error);
    }
    setLoading(false);
  };

  const convertToPartner = async (territoryId, name) => {
    try {
      await axios.post(`${API}/territories/ai/${territoryId}/convert-to-partner`);
      toast.success(`${name} converti en partenaire!`);
      loadPartners();
    } catch (error) {
      toast.error('Erreur lors de la conversion');
    }
  };

  return (
    <div className="space-y-6">
      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Handshake className="h-5 w-5 text-[#f5a623]" />
            Partenaires potentiels
          </CardTitle>
          <CardDescription>
            Territoires à fort potentiel pouvant devenir partenaires BIONIC™
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {partners.map(partner => (
                <div 
                  key={partner.id}
                  className="p-4 bg-background rounded-lg border border-border"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="text-white font-semibold">{partner.name}</h4>
                    <Badge className={`${
                      partner.partnership_potential === 'Élevé' 
                        ? 'bg-green-500/20 text-green-400' 
                        : 'bg-yellow-500/20 text-yellow-400'
                    }`}>
                      {partner.partnership_potential}
                    </Badge>
                  </div>
                  
                  <p className="text-gray-400 text-sm mb-3">
                    <MapPin className="h-3 w-3 inline mr-1" />
                    {partner.region || partner.province}
                  </p>
                  
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-gray-400 text-xs">Score partenariat</span>
                    <span className="text-[#f5a623] font-bold">{partner.partnership_score}</span>
                  </div>
                  
                  <div className="flex gap-2">
                    {partner.website && (
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="flex-1"
                        onClick={() => window.open(partner.website, '_blank')}
                      >
                        <Globe className="h-3 w-3 mr-1" />
                        Site
                      </Button>
                    )}
                    <Button 
                      size="sm"
                      className="flex-1 bg-[#f5a623] hover:bg-[#f5a623]/80 text-black"
                      onClick={() => convertToPartner(partner.id, partner.name)}
                    >
                      <Handshake className="h-3 w-3 mr-1" />
                      Convertir
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// ============================================
// TERRITORY MAP COMPONENT
// ============================================

// Custom marker icon helper
const createMarkerIcon = (color, type) => {
  const icons = {
    zec: '🏕️',
    sepaq: '🦌',
    pourvoirie: '🏠',
    club: '🎯',
    outfitter: '🦬',
    private: '🔒',
    anticosti: '🏝️',
    reserve: '🌲',
    indigenous: '🪶'
  };
  
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="
      width: 32px;
      height: 32px;
      background: ${color};
      border-radius: 50%;
      border: 3px solid white;
      box-shadow: 0 2px 8px rgba(0,0,0,0.4);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
    ">${icons[type] || '📍'}</div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -16]
  });
};

// Score-based color
const getScoreColor = (score) => {
  if (score >= 80) return '#22c55e'; // green
  if (score >= 60) return '#f5a623'; // orange
  if (score >= 40) return '#eab308'; // yellow
  return '#ef4444'; // red
};

// Map bounds controller
const MapBoundsController = ({ territories }) => {
  const map = useMap();
  
  useEffect(() => {
    if (territories && territories.length > 0) {
      const bounds = territories
        .filter(t => t.geometry?.coordinates)
        .map(t => [t.geometry.coordinates[1], t.geometry.coordinates[0]]);
      
      if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 8 });
      }
    }
  }, [territories, map]);
  
  return null;
};

export const TerritoryMapView = () => {
  const [geojson, setGeojson] = useState(null);
  const [heatmapData, setHeatmapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterProvince, setFilterProvince] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [filterSpecies, setFilterSpecies] = useState('all');
  const [viewMode, setViewMode] = useState('markers'); // 'markers' | 'heatmap'
  const [heatmapMetric, setHeatmapMetric] = useState('score');
  const [selectedTerritory, setSelectedTerritory] = useState(null);
  const mapRef = useRef(null);

  const PROVINCES = [
    { value: 'all', label: 'Toutes provinces' },
    { value: 'QC', label: 'Québec' },
    { value: 'ON', label: 'Ontario' },
    { value: 'NB', label: 'Nouveau-Brunswick' },
    { value: 'NS', label: 'Nouvelle-Écosse' },
    { value: 'NL', label: 'Terre-Neuve' },
    { value: 'MB', label: 'Manitoba' },
    { value: 'SK', label: 'Saskatchewan' },
    { value: 'AB', label: 'Alberta' },
    { value: 'BC', label: 'Colombie-Britannique' }
  ];

  const TYPES = [
    { value: 'all', label: 'Tous types' },
    { value: 'zec', label: '🏕️ ZEC' },
    { value: 'sepaq', label: '🦌 Sépaq' },
    { value: 'pourvoirie', label: '🏠 Pourvoirie' },
    { value: 'club', label: '🎯 Club' },
    { value: 'outfitter', label: '🦬 Outfitter' },
    { value: 'anticosti', label: '🏝️ Anticosti' }
  ];

  const SPECIES_LIST = [
    { value: 'all', label: 'Toutes espèces' },
    { value: 'orignal', label: '🫎 Orignal' },
    { value: 'chevreuil', label: '🦌 Chevreuil' },
    { value: 'ours', label: '🐻 Ours' },
    { value: 'caribou', label: '🦌 Caribou' },
    { value: 'dindon', label: '🦃 Dindon' },
    { value: 'petit_gibier', label: '🐰 Petit gibier' }
  ];

  const loadGeoJSON = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterProvince !== 'all') params.append('province', filterProvince);
      if (filterType !== 'all') params.append('establishment_type', filterType);
      if (filterSpecies !== 'all') params.append('species', filterSpecies);
      
      const response = await axios.get(`${API}/territories/ai/geojson?${params}`);
      setGeojson(response.data);
    } catch (error) {
      console.error('Error loading GeoJSON:', error);
      toast.error('Erreur lors du chargement des données cartographiques');
    }
    setLoading(false);
  }, [filterProvince, filterType, filterSpecies]);

  const loadHeatmap = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (filterProvince !== 'all') params.append('province', filterProvince);
      
      const response = await axios.get(`${API}/territories/ai/heatmap/${heatmapMetric}?${params}`);
      if (response.data.success) {
        setHeatmapData(response.data);
      }
    } catch (error) {
      console.error('Error loading heatmap:', error);
    }
  }, [heatmapMetric, filterProvince]);

  useEffect(() => {
    loadGeoJSON();
  }, [loadGeoJSON]);

  useEffect(() => {
    if (viewMode === 'heatmap') {
      loadHeatmap();
    }
  }, [viewMode, loadHeatmap]);

  // Filter territories
  const filteredFeatures = useMemo(() => {
    if (!geojson?.features) return [];
    return geojson.features;
  }, [geojson]);

  // Stats
  const stats = useMemo(() => {
    if (!filteredFeatures.length) return { total: 0, avgScore: 0, verified: 0, partners: 0 };
    
    const total = filteredFeatures.length;
    const avgScore = filteredFeatures.reduce((sum, f) => sum + (f.properties.global_score || 0), 0) / total;
    const verified = filteredFeatures.filter(f => f.properties.is_verified).length;
    const partners = filteredFeatures.filter(f => f.properties.is_partner).length;
    
    return { total, avgScore: avgScore.toFixed(1), verified, partners };
  }, [filteredFeatures]);

  return (
    <div className="space-y-4">
      {/* Map Controls */}
      <Card className="bg-card border-border">
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex items-center gap-2">
              <Map className="h-5 w-5 text-[#f5a623]" />
              <span className="text-white font-semibold">Carte Interactive</span>
            </div>
            
            {/* View Mode Toggle */}
            <div className="flex gap-1 bg-background rounded-lg p-1">
              <Button
                size="sm"
                variant={viewMode === 'markers' ? 'default' : 'ghost'}
                onClick={() => setViewMode('markers')}
                className={viewMode === 'markers' ? 'bg-[#f5a623] text-black' : ''}
              >
                <MapPin className="h-4 w-4 mr-1" />
                Marqueurs
              </Button>
              <Button
                size="sm"
                variant={viewMode === 'heatmap' ? 'default' : 'ghost'}
                onClick={() => setViewMode('heatmap')}
                className={viewMode === 'heatmap' ? 'bg-[#f5a623] text-black' : ''}
              >
                <Layers className="h-4 w-4 mr-1" />
                Heatmap
              </Button>
            </div>
            
            {/* Filters */}
            <Select value={filterProvince} onValueChange={setFilterProvince}>
              <SelectTrigger className="w-[150px] bg-background">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PROVINCES.map(p => (
                  <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-[150px] bg-background">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TYPES.map(t => (
                  <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Select value={filterSpecies} onValueChange={setFilterSpecies}>
              <SelectTrigger className="w-[150px] bg-background">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {SPECIES_LIST.map(s => (
                  <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            {viewMode === 'heatmap' && (
              <Select value={heatmapMetric} onValueChange={setHeatmapMetric}>
                <SelectTrigger className="w-[150px] bg-background">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="score">Score BIONIC™</SelectItem>
                  <SelectItem value="success">Taux de succès</SelectItem>
                  <SelectItem value="pressure">Pression</SelectItem>
                  <SelectItem value="density">Densité habitat</SelectItem>
                </SelectContent>
              </Select>
            )}
            
            <Button variant="outline" onClick={loadGeoJSON} disabled={loading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Actualiser
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Stats Bar */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="bg-card border-border">
          <CardContent className="p-3 text-center">
            <div className="text-2xl font-bold text-[#f5a623]">{stats.total}</div>
            <div className="text-gray-400 text-xs">Territoires</div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-3 text-center">
            <div className="text-2xl font-bold text-green-400">{stats.avgScore}</div>
            <div className="text-gray-400 text-xs">Score moyen</div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-3 text-center">
            <div className="text-2xl font-bold text-blue-400">{stats.verified}</div>
            <div className="text-gray-400 text-xs">Vérifiés</div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-3 text-center">
            <div className="text-2xl font-bold text-purple-400">{stats.partners}</div>
            <div className="text-gray-400 text-xs">Partenaires</div>
          </CardContent>
        </Card>
      </div>

      {/* Map Container */}
      <Card className="bg-card border-border overflow-hidden">
        <div className="h-[500px] w-full relative">
          {loading && (
            <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-[1000]">
              <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
            </div>
          )}
          
          <MapContainer
            ref={mapRef}
            center={[52, -90]}
            zoom={4}
            style={{ height: '100%', width: '100%' }}
            className="rounded-lg"
          >
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
              attribution='&copy; <a href="https://carto.com/">CARTO</a>'
            />
            
            {filteredFeatures.length > 0 && <MapBoundsController territories={filteredFeatures} />}
            
            {/* Markers View */}
            {viewMode === 'markers' && (
              <LayerGroup>
                {filteredFeatures.map((feature, idx) => {
                  const { coordinates } = feature.geometry;
                  const props = feature.properties;
                  const score = props.global_score || 0;
                  
                  return (
                    <Marker
                      key={props.id || idx}
                      position={[coordinates[1], coordinates[0]]}
                      icon={createMarkerIcon(getScoreColor(score), props.establishment_type)}
                      eventHandlers={{
                        click: () => setSelectedTerritory(props)
                      }}
                    >
                      <Popup className="territory-popup">
                        <div className="p-2 min-w-[200px]">
                          <h3 className="font-bold text-lg mb-1">{props.name}</h3>
                          <p className="text-sm text-gray-600 mb-2">
                            {props.region || props.province}
                          </p>
                          
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm">Score BIONIC™</span>
                            <span className={`font-bold text-lg ${
                              score >= 80 ? 'text-green-600' :
                              score >= 60 ? 'text-yellow-600' : 'text-red-600'
                            }`}>
                              {score}
                            </span>
                          </div>
                          
                          {props.success_rate && (
                            <div className="flex items-center justify-between text-sm mb-2">
                              <span>Taux de succès</span>
                              <span className="font-semibold">{props.success_rate}%</span>
                            </div>
                          )}
                          
                          {props.species && props.species.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-2">
                              {props.species.slice(0, 4).map((s, i) => (
                                <span key={i} className="text-lg" title={s}>
                                  {SPECIES_OPTIONS.find(sp => sp.id === s)?.icon || '🎯'}
                                </span>
                              ))}
                            </div>
                          )}
                          
                          <div className="flex gap-1 mt-2">
                            {props.is_verified && (
                              <Badge className="bg-green-100 text-green-800 text-xs">✓ Vérifié</Badge>
                            )}
                            {props.is_partner && (
                              <Badge className="bg-purple-100 text-purple-800 text-xs">Partenaire</Badge>
                            )}
                          </div>
                        </div>
                      </Popup>
                    </Marker>
                  );
                })}
              </LayerGroup>
            )}
            
            {/* Heatmap View (Circle Markers with intensity) */}
            {viewMode === 'heatmap' && heatmapData?.points && (
              <LayerGroup>
                {heatmapData.points.map((point, idx) => (
                  <CircleMarker
                    key={idx}
                    center={[point.lat, point.lon]}
                    radius={Math.max(8, point.value / 5)}
                    pathOptions={{
                      fillColor: getScoreColor(point.value),
                      fillOpacity: 0.7,
                      color: getScoreColor(point.value),
                      weight: 2
                    }}
                  >
                    <Popup>
                      <div className="p-2">
                        <h4 className="font-bold">{point.name}</h4>
                        <p className="text-sm">{heatmapData.legend}: <strong>{point.value}</strong></p>
                      </div>
                    </Popup>
                  </CircleMarker>
                ))}
              </LayerGroup>
            )}
          </MapContainer>
        </div>
      </Card>

      {/* Legend */}
      <Card className="bg-card border-border">
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-6">
            <span className="text-gray-400 text-sm font-medium">Légende des scores :</span>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-green-500" />
              <span className="text-sm text-gray-300">80-100 (Excellent)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-[#f5a623]" />
              <span className="text-sm text-gray-300">60-79 (Bon)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-yellow-500" />
              <span className="text-sm text-gray-300">40-59 (Moyen)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-red-500" />
              <span className="text-sm text-gray-300">0-39 (Faible)</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// ============================================
// MAIN ADVANCED PANEL
// ============================================

const TerritoryAdvanced = () => {
  return (
    <Tabs defaultValue="recommendations" className="w-full">
      <TabsList className="grid w-full max-w-2xl grid-cols-4 mb-6 bg-card border border-border">
        <TabsTrigger 
          value="recommendations" 
          className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black"
        >
          <Sparkles className="h-4 w-4 mr-2" />
          IA
        </TabsTrigger>
        <TabsTrigger 
          value="map" 
          className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black"
        >
          <Map className="h-4 w-4 mr-2" />
          Carte
        </TabsTrigger>
        <TabsTrigger 
          value="scraping" 
          className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black"
        >
          <Database className="h-4 w-4 mr-2" />
          Scraping
        </TabsTrigger>
        <TabsTrigger 
          value="partners" 
          className="data-[state=active]:bg-[#f5a623] data-[state=active]:text-black"
        >
          <Handshake className="h-4 w-4 mr-2" />
          Partenaires
        </TabsTrigger>
      </TabsList>
      
      <TabsContent value="recommendations">
        <AIRecommendations />
      </TabsContent>
      
      <TabsContent value="map">
        <TerritoryMapView />
      </TabsContent>
      
      <TabsContent value="scraping">
        <ScrapingAdmin />
      </TabsContent>
      
      <TabsContent value="partners">
        <PotentialPartners />
      </TabsContent>
    </Tabs>
  );
};

export default TerritoryAdvanced;
