/**
 * GPS Hotspots Component
 * BIONIC Design System compliant - No emojis
 * Displays a directory of the best GPS coordinates with high hunting probability
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { 
  MapPin, 
  Target, 
  Navigation,
  Star,
  TrendingUp,
  Filter,
  Search,
  ExternalLink,
  Crosshair,
  Compass,
  Mountain,
  Droplets,
  Trees,
  Clock,
  Calendar,
  CheckCircle,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Loader2,
  Eye,
  Map,
  Locate,
  RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';
import { useLanguage } from '@/contexts/LanguageContext';
import { SpeciesIcon } from '@/components/bionic/SpeciesIcon';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SPECIES_CONFIG = {
  orignal: { speciesId: 'moose', label: 'Orignal', color: 'text-amber-600 bg-amber-500/20' },
  chevreuil: { speciesId: 'deer', label: 'Chevreuil', color: 'text-orange-500 bg-orange-500/20' },
  ours: { speciesId: 'bear', label: 'Ours', color: 'text-gray-400 bg-gray-500/20' },
  caribou: { speciesId: 'caribou', label: 'Caribou', color: 'text-blue-400 bg-blue-500/20' }
};

const GpsHotspots = ({ onNavigateToMap }) => {
  const { t } = useLanguage();
  const [hotspots, setHotspots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({});
  const [refreshing, setRefreshing] = useState(false);
  const [filters, setFilters] = useState({
    species: '',
    region: '',
    minProbability: 60
  });
  const [availableFilters, setAvailableFilters] = useState({
    regions: [],
    species: [],
    minProbabilityOptions: []
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedHotspot, setExpandedHotspot] = useState(null);
  const [sortBy, setSortBy] = useState('max_probability');

  useEffect(() => {
    fetchHotspots();
  }, [filters]);

  const fetchHotspots = async () => {
    setLoading(true);
    try {
      const params = { min_probability: filters.minProbability };
      if (filters.species) params.species = filters.species;
      if (filters.region) params.region = filters.region;
      
      const response = await axios.get(`${API}/territory/hunting/hotspots`, { params });
      
      setHotspots(response.data.hotspots || []);
      setStats(response.data.stats || {});
      setAvailableFilters({
        regions: response.data.filters?.available_regions || [],
        species: response.data.filters?.available_species || [],
        minProbabilityOptions: response.data.filters?.min_probability_options || [50, 60, 70, 80, 90]
      });
    } catch (error) {
      console.error('Error fetching hotspots:', error);
      toast.error('Erreur lors du chargement des hotspots');
    } finally {
      setLoading(false);
    }
  };

  const getProbabilityColor = (prob) => {
    if (prob >= 80) return 'text-green-400 bg-green-500/20 border-green-500';
    if (prob >= 60) return 'text-yellow-400 bg-yellow-500/20 border-yellow-500';
    if (prob >= 40) return 'text-orange-400 bg-orange-500/20 border-orange-500';
    return 'text-red-400 bg-red-500/20 border-red-500';
  };

  const getProbabilityLabel = (prob) => {
    if (prob >= 90) return 'Exceptionnel';
    if (prob >= 80) return 'Excellent';
    if (prob >= 70) return 'Très bon';
    if (prob >= 60) return 'Bon';
    return 'Modéré';
  };

  const handleNavigateToSpot = (hotspot) => {
    if (onNavigateToMap) {
      onNavigateToMap(hotspot.coordinates.lat, hotspot.coordinates.lng);
      toast.success(`Navigation vers: ${hotspot.coordinates.lat.toFixed(4)}, ${hotspot.coordinates.lng.toFixed(4)}`);
    }
  };

  const copyCoordinates = (hotspot) => {
    const coords = `${hotspot.coordinates.lat}, ${hotspot.coordinates.lng}`;
    navigator.clipboard.writeText(coords);
    toast.success('Coordonnées copiées!', { description: coords });
  };

  const filteredHotspots = hotspots.filter(h => 
    h.territory?.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    h.territory?.region?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    h.dominant_species?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Reset/Refresh function
  const handleRefresh = async () => {
    setRefreshing(true);
    setFilters({
      species: '',
      region: '',
      minProbability: 60
    });
    setSearchQuery('');
    setSortBy('max_probability');
    await fetchHotspots();
    setRefreshing(false);
    toast.success(t('common_refresh') || 'Actualisé');
  };

  const sortedHotspots = [...filteredHotspots].sort((a, b) => {
    if (sortBy === 'max_probability') return b.max_probability - a.max_probability;
    if (sortBy === 'user_ratings') return (b.user_ratings?.avg_rating || 0) - (a.user_ratings?.avg_rating || 0);
    if (sortBy === 'recent') return new Date(b.last_activity) - new Date(a.last_activity);
    return 0;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Crosshair className="h-6 w-6 text-green-500" />
            Meilleurs Spots GPS
          </h2>
          <p className="text-gray-400 text-sm mt-1">
            Coordonnées GPS à fort potentiel de chasse • Cliquez pour localiser sur la carte
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            {t('common_refresh')}
          </Button>
          <Badge className="bg-green-500/20 text-green-400 border border-green-500/50 text-sm px-3 py-1">
            {stats.highest_probability || 0}% max
          </Badge>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-card border-border">
          <CardContent className="p-4 text-center">
            <div className="text-3xl font-bold text-green-400">{hotspots.length}</div>
            <div className="text-gray-500 text-xs uppercase mt-1">Spots analysés</div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-4 text-center">
            <div className="text-3xl font-bold text-yellow-400">{stats.average_probability || 0}%</div>
            <div className="text-gray-500 text-xs uppercase mt-1">Probabilité moy.</div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-4 text-center">
            <div className="text-3xl font-bold text-blue-400">{stats.verified_spots || 0}</div>
            <div className="text-gray-500 text-xs uppercase mt-1">Spots vérifiés</div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border">
          <CardContent className="p-4 text-center">
            <div className="flex justify-center gap-2">
              {Object.entries(stats.species_distribution || {}).slice(0, 3).map(([sp, count]) => (
                <div key={sp} className="text-center">
                  <span className="text-lg">{SPECIES_CONFIG[sp]?.emoji}</span>
                  <div className="text-xs text-gray-500">{count}</div>
                </div>
              ))}
            </div>
            <div className="text-gray-500 text-xs uppercase mt-1">Distribution</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card className="bg-card border-border">
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-4 items-end">
            {/* Search */}
            <div className="flex-1 min-w-[200px]">
              <label className="text-gray-400 text-xs mb-1 block">Rechercher</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
                <Input
                  placeholder="Territoire, région, espèce..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 bg-background border-border"
                />
              </div>
            </div>
            
            {/* Species Filter */}
            <div className="w-[160px]">
              <label className="text-gray-400 text-xs mb-1 block">Espèce cible</label>
              <Select value={filters.species || 'all'} onValueChange={(v) => setFilters(f => ({ ...f, species: v === 'all' ? '' : v }))}>
                <SelectTrigger className="bg-background border-border">
                  <SelectValue placeholder="Toutes" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Toutes espèces</SelectItem>
                  {availableFilters.species.map(s => (
                    <SelectItem key={s} value={s}>
                      {SPECIES_CONFIG[s]?.emoji} {SPECIES_CONFIG[s]?.label || s}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Region Filter */}
            <div className="w-[180px]">
              <label className="text-gray-400 text-xs mb-1 block">Région</label>
              <Select value={filters.region || 'all'} onValueChange={(v) => setFilters(f => ({ ...f, region: v === 'all' ? '' : v }))}>
                <SelectTrigger className="bg-background border-border">
                  <SelectValue placeholder="Toutes" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Toutes régions</SelectItem>
                  {availableFilters.regions.map(r => (
                    <SelectItem key={r} value={r}>{r}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Min Probability */}
            <div className="w-[140px]">
              <label className="text-gray-400 text-xs mb-1 block">Probabilité min.</label>
              <Select value={String(filters.minProbability)} onValueChange={(v) => setFilters(f => ({ ...f, minProbability: parseInt(v) }))}>
                <SelectTrigger className="bg-background border-border">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {availableFilters.minProbabilityOptions.map(p => (
                    <SelectItem key={p} value={String(p)}>{p}%+</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Sort */}
            <div className="w-[160px]">
              <label className="text-gray-400 text-xs mb-1 block">Trier par</label>
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="bg-background border-border">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="max_probability">Probabilité</SelectItem>
                  <SelectItem value="user_ratings">Note utilisateurs</SelectItem>
                  <SelectItem value="recent">Activité récente</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button
              variant="outline"
              onClick={() => {
                setFilters({ species: '', region: '', minProbability: 60 });
                setSearchQuery('');
              }}
              className="bg-background"
            >
              <Filter className="h-4 w-4 mr-2" />
              Réinitialiser
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Hotspots List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-green-500" />
          <span className="ml-3 text-gray-400">Analyse des meilleurs spots...</span>
        </div>
      ) : (
        <div className="space-y-3">
          {sortedHotspots.map((hotspot, index) => {
            const isExpanded = expandedHotspot === hotspot.id;
            const speciesConfig = SPECIES_CONFIG[hotspot.dominant_species] || {};
            
            return (
              <Card 
                key={hotspot.id}
                className={`bg-card border-border hover:border-green-500/50 transition-all ${
                  hotspot.max_probability >= 85 ? 'border-l-4 border-l-green-500' : ''
                }`}
              >
                <CardContent className="p-4">
                  {/* Main Row */}
                  <div className="flex items-center gap-4">
                    {/* Rank & Probability */}
                    <div className={`w-16 h-16 rounded-xl flex flex-col items-center justify-center border ${getProbabilityColor(hotspot.max_probability)}`}>
                      <div className="text-2xl font-bold">{hotspot.max_probability}%</div>
                      <div className="text-[8px] uppercase opacity-70">{getProbabilityLabel(hotspot.max_probability)}</div>
                    </div>

                    {/* Coordinates & Info */}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-lg">{speciesConfig.emoji}</span>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${speciesConfig.color}`}>
                          {speciesConfig.label} dominant
                        </span>
                        {hotspot.verified && (
                          <Badge className="bg-blue-500/20 text-blue-400 text-[10px]">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Vérifié
                          </Badge>
                        )}
                        {hotspot.max_probability >= 90 && (
                          <Badge className="bg-gradient-to-r from-yellow-500/30 to-orange-500/30 text-yellow-400 text-[10px] animate-pulse">
                            <Star className="h-3 w-3 mr-1 fill-yellow-400" />
                            Top Spot
                          </Badge>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-4 mt-2 text-sm">
                        <div className="flex items-center gap-1 text-green-400 font-mono">
                          <MapPin className="h-4 w-4" />
                          <span>{hotspot.coordinates.lat.toFixed(5)}, {hotspot.coordinates.lng.toFixed(5)}</span>
                        </div>
                        <div className="text-gray-500 text-xs">
                          {hotspot.coordinates.dms_lat} • {hotspot.coordinates.dms_lng}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
                        <span className="flex items-center gap-1">
                          <Trees className="h-3 w-3" />
                          {hotspot.territory?.name}
                        </span>
                        <span className="flex items-center gap-1">
                          <Mountain className="h-3 w-3" />
                          {hotspot.territory?.region}
                        </span>
                        <span className="flex items-center gap-1">
                          <Compass className="h-3 w-3" />
                          {hotspot.coordinates.altitude_m}m alt.
                        </span>
                      </div>
                    </div>

                    {/* Species Probabilities */}
                    <div className="hidden lg:flex items-center gap-3">
                      {Object.entries(hotspot.probabilities || {}).map(([sp, prob]) => (
                        <div key={sp} className="text-center w-14">
                          <div className="text-lg">{SPECIES_CONFIG[sp]?.emoji}</div>
                          <div className={`text-xs font-bold ${prob >= 70 ? 'text-green-400' : prob >= 50 ? 'text-yellow-400' : 'text-gray-500'}`}>
                            {prob}%
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* User Rating */}
                    <div className="hidden md:flex flex-col items-center">
                      <div className="flex items-center gap-1 text-yellow-400">
                        <Star className="h-4 w-4 fill-yellow-400" />
                        <span className="font-bold">{hotspot.user_ratings?.avg_rating}</span>
                      </div>
                      <div className="text-[10px] text-gray-500">{hotspot.user_ratings?.total_reviews} avis</div>
                    </div>

                    {/* Actions */}
                    <div className="flex flex-col gap-2">
                      <Button
                        onClick={() => handleNavigateToSpot(hotspot)}
                        className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white text-xs"
                        size="sm"
                      >
                        <Navigation className="h-3.5 w-3.5 mr-1" />
                        Voir sur carte
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setExpandedHotspot(isExpanded ? null : hotspot.id)}
                        className="text-xs"
                      >
                        {isExpanded ? <ChevronUp className="h-3.5 w-3.5 mr-1" /> : <ChevronDown className="h-3.5 w-3.5 mr-1" />}
                        Détails
                      </Button>
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {isExpanded && (
                    <div className="mt-4 pt-4 border-t border-border">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {/* Terrain Info */}
                        <div className="bg-gray-900/50 rounded-lg p-3">
                          <h4 className="text-white text-sm font-semibold mb-2 flex items-center gap-2">
                            <Mountain className="h-4 w-4 text-green-400" />
                            Terrain
                          </h4>
                          <div className="space-y-1 text-xs text-gray-400">
                            <p><span className="text-gray-500">Type:</span> {hotspot.terrain?.type}</p>
                            <p><span className="text-gray-500">Eau:</span> {hotspot.terrain?.water_distance_m}m</p>
                            <p><span className="text-gray-500">Route:</span> {hotspot.terrain?.road_distance_m}m</p>
                            <div className="mt-2 flex flex-wrap gap-1">
                              {hotspot.terrain?.features?.map((f, i) => (
                                <Badge key={i} variant="outline" className="text-[9px] border-gray-600">{f}</Badge>
                              ))}
                            </div>
                          </div>
                        </div>

                        {/* Recommendations */}
                        <div className="bg-gray-900/50 rounded-lg p-3">
                          <h4 className="text-white text-sm font-semibold mb-2 flex items-center gap-2">
                            <Target className="h-4 w-4 text-yellow-400" />
                            Recommandations
                          </h4>
                          <div className="space-y-1 text-xs text-gray-400">
                            <p className="flex items-center gap-2">
                              <Clock className="h-3 w-3 text-blue-400" />
                              {hotspot.recommendations?.best_time}
                            </p>
                            <p className="flex items-center gap-2">
                              <Calendar className="h-3 w-3 text-green-400" />
                              {hotspot.recommendations?.best_season}
                            </p>
                            <p className="flex items-center gap-2">
                              <Compass className="h-3 w-3 text-orange-400" />
                              {hotspot.recommendations?.approach}
                            </p>
                          </div>
                        </div>

                        {/* All Species Probabilities */}
                        <div className="bg-gray-900/50 rounded-lg p-3">
                          <h4 className="text-white text-sm font-semibold mb-2 flex items-center gap-2">
                            <TrendingUp className="h-4 w-4 text-purple-400" />
                            Probabilités détaillées
                          </h4>
                          <div className="space-y-2">
                            {Object.entries(hotspot.probabilities || {}).map(([sp, prob]) => (
                              <div key={sp} className="flex items-center gap-2">
                                <span className="text-sm w-6">{SPECIES_CONFIG[sp]?.emoji}</span>
                                <div className="flex-1">
                                  <Progress value={prob} className="h-2" />
                                </div>
                                <span className={`text-xs font-bold w-10 text-right ${prob >= 70 ? 'text-green-400' : prob >= 50 ? 'text-yellow-400' : 'text-gray-500'}`}>
                                  {prob}%
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex gap-2 mt-4">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => copyCoordinates(hotspot)}
                          className="text-xs"
                        >
                          <MapPin className="h-3.5 w-3.5 mr-1" />
                          Copier GPS
                        </Button>
                        {hotspot.territory?.website && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(hotspot.territory.website, '_blank')}
                            className="text-xs"
                          >
                            <ExternalLink className="h-3.5 w-3.5 mr-1" />
                            Site du territoire
                          </Button>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}

          {sortedHotspots.length === 0 && (
            <Card className="bg-card border-border">
              <CardContent className="p-12 text-center">
                <Crosshair className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">Aucun hotspot trouvé avec ces critères</p>
                <p className="text-gray-500 text-sm mt-1">Essayez de réduire la probabilité minimale ou de changer les filtres</p>
                <Button
                  variant="outline"
                  className="mt-4"
                  onClick={() => {
                    setFilters({ species: '', region: '', minProbability: 50 });
                    setSearchQuery('');
                  }}
                >
                  Réinitialiser les filtres
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* Info Card */}
      <Card className="bg-gradient-to-r from-green-900/30 to-emerald-900/30 border-green-500/30">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <Target className="h-5 w-5 text-green-400" />
            </div>
            <div>
              <h4 className="text-white text-sm font-semibold">Comment utiliser ces spots?</h4>
              <p className="text-gray-400 text-xs mt-1">
                Ces coordonnées GPS sont analysées selon la topographie, la végétation, la présence d'eau et les observations historiques. 
                Cliquez sur "Voir sur carte" pour localiser le spot et planifier votre approche. Les spots vérifiés ✓ ont été confirmés par des chasseurs.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default GpsHotspots;
