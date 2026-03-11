/**
 * Territory Rankings Component
 * Displays a ranked list of hunting territories with performance metrics
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { 
  Trophy, 
  TrendingUp, 
  Star, 
  MapPin, 
  Users, 
  Target,
  Filter,
  Search,
  ExternalLink,
  ChevronUp,
  ChevronDown,
  Award,
  Mountain,
  Trees,
  Loader2,
  Medal
} from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const TerritoryRankings = () => {
  const [rankings, setRankings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [filters, setFilters] = useState({
    species: '',
    region: '',
    type: ''
  });
  const [availableFilters, setAvailableFilters] = useState({
    regions: [],
    types: [],
    species: []
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('performance_score');
  const [sortOrder, setSortOrder] = useState('desc');

  useEffect(() => {
    fetchRankings();
  }, [filters]);

  const fetchRankings = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.species) params.species = filters.species;
      if (filters.region) params.region = filters.region;
      if (filters.type) params.territory_type = filters.type;
      
      const response = await axios.get(`${API}/territory/hunting/rankings`, { params });
      
      setRankings(response.data.rankings || []);
      setTotalCount(response.data.total_count || 0);
      setAvailableFilters({
        regions: response.data.filters?.available_regions || [],
        types: response.data.filters?.available_types || [],
        species: response.data.filters?.available_species || []
      });
    } catch (error) {
      console.error('Error fetching rankings:', error);
      toast.error('Erreur lors du chargement des classements');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-400 bg-green-500/20';
    if (score >= 60) return 'text-yellow-400 bg-yellow-500/20';
    if (score >= 40) return 'text-orange-400 bg-orange-500/20';
    return 'text-red-400 bg-red-500/20';
  };

  const getRankBadge = (rank) => {
    if (rank === 1) return { icon: <Trophy className="h-4 w-4 text-yellow-500" />, color: 'bg-yellow-500/30 text-yellow-300 border-yellow-500' };
    if (rank === 2) return { icon: <Medal className="h-4 w-4 text-gray-300" />, color: 'bg-gray-400/30 text-gray-300 border-gray-400' };
    if (rank === 3) return { icon: <Medal className="h-4 w-4 text-amber-400" />, color: 'bg-amber-600/30 text-amber-400 border-amber-600' };
    return { icon: `#${rank}`, color: 'bg-gray-700/50 text-gray-400 border-gray-600' };
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'ZEC': return <Trees className="h-4 w-4" />;
      case 'Réserve faunique': return <Mountain className="h-4 w-4" />;
      case 'Pourvoirie': return <Target className="h-4 w-4" />;
      default: return <MapPin className="h-4 w-4" />;
    }
  };

  const filteredRankings = rankings.filter(t => 
    t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    t.region?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const sortedRankings = [...filteredRankings].sort((a, b) => {
    let aVal = a[sortBy];
    let bVal = b[sortBy];
    
    if (sortBy === 'stats.avg_success_rate') {
      aVal = a.stats?.avg_success_rate || 0;
      bVal = b.stats?.avg_success_rate || 0;
    } else if (sortBy === 'stats.visitor_rating') {
      aVal = a.stats?.visitor_rating || 0;
      bVal = b.stats?.visitor_rating || 0;
    }
    
    if (sortOrder === 'asc') return aVal > bVal ? 1 : -1;
    return aVal < bVal ? 1 : -1;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Trophy className="h-6 w-6 text-yellow-500" />
            Classement des Territoires
          </h2>
          <p className="text-gray-400 text-sm mt-1">
            Les meilleurs territoires de chasse du Québec classés par performance
          </p>
        </div>
        <Badge className="bg-[#f5a623]/20 text-[#f5a623] border border-[#f5a623]/50">
          {totalCount} territoires
        </Badge>
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
                  placeholder="Nom ou région..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 bg-background border-border"
                />
              </div>
            </div>
            
            {/* Species Filter */}
            <div className="w-[180px]">
              <label className="text-gray-400 text-xs mb-1 block">Espèce</label>
              <Select value={filters.species || 'all'} onValueChange={(v) => setFilters(f => ({ ...f, species: v === 'all' ? '' : v }))}>
                <SelectTrigger className="bg-background border-border">
                  <SelectValue placeholder="Toutes" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Toutes les espèces</SelectItem>
                  {availableFilters.species.map(s => (
                    <SelectItem key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Region Filter */}
            <div className="w-[200px]">
              <label className="text-gray-400 text-xs mb-1 block">Région</label>
              <Select value={filters.region || 'all'} onValueChange={(v) => setFilters(f => ({ ...f, region: v === 'all' ? '' : v }))}>
                <SelectTrigger className="bg-background border-border">
                  <SelectValue placeholder="Toutes" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Toutes les régions</SelectItem>
                  {availableFilters.regions.map(r => (
                    <SelectItem key={r} value={r}>{r}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Type Filter */}
            <div className="w-[180px]">
              <label className="text-gray-400 text-xs mb-1 block">Type</label>
              <Select value={filters.type || 'all'} onValueChange={(v) => setFilters(f => ({ ...f, type: v === 'all' ? '' : v }))}>
                <SelectTrigger className="bg-background border-border">
                  <SelectValue placeholder="Tous" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tous les types</SelectItem>
                  {availableFilters.types.map(t => (
                    <SelectItem key={t} value={t}>{t}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Sort */}
            <div className="w-[180px]">
              <label className="text-gray-400 text-xs mb-1 block">Trier par</label>
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="bg-background border-border">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="performance_score">Score global</SelectItem>
                  <SelectItem value="stats.avg_success_rate">Taux de succès</SelectItem>
                  <SelectItem value="stats.visitor_rating">Note visiteurs</SelectItem>
                  <SelectItem value="rank">Classement</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button
              variant="outline"
              size="icon"
              onClick={() => setSortOrder(o => o === 'asc' ? 'desc' : 'asc')}
              className="bg-background"
            >
              {sortOrder === 'desc' ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
            </Button>

            <Button
              variant="outline"
              onClick={() => {
                setFilters({ species: '', region: '', type: '' });
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

      {/* Rankings List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
          <span className="ml-3 text-gray-400">Chargement des classements...</span>
        </div>
      ) : (
        <div className="space-y-3">
          {sortedRankings.map((territory) => {
            const rankBadge = getRankBadge(territory.rank);
            return (
              <Card 
                key={`${territory.type}-${territory.name}`}
                className={`bg-card border-border hover:border-[#f5a623]/50 transition-all cursor-pointer ${
                  territory.rank <= 3 ? 'border-l-4 border-l-yellow-500' : ''
                }`}
              >
                <CardContent className="p-4">
                  <div className="flex items-center gap-4">
                    {/* Rank Badge */}
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center border ${rankBadge.color} font-bold text-lg`}>
                      {typeof rankBadge.icon === 'string' ? rankBadge.icon : rankBadge.icon}
                    </div>

                    {/* Main Info */}
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="text-white font-semibold">{territory.name}</h3>
                        {territory.trending && (
                          <Badge className="bg-red-500/20 text-red-400 text-[10px]">
                            <TrendingUp className="h-3 w-3 mr-1" />
                            Tendance
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-3 text-sm text-gray-400 mt-1">
                        <span className="flex items-center gap-1">
                          {getTypeIcon(territory.type)}
                          {territory.type}
                        </span>
                        <span className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {territory.region}
                        </span>
                      </div>
                      {territory.highlight && (
                        <p className="text-xs text-[#f5a623] mt-1 flex items-center gap-1">
                          <Award className="h-3 w-3" />
                          {territory.highlight}
                        </p>
                      )}
                    </div>

                    {/* Species */}
                    <div className="hidden md:flex flex-wrap gap-1 max-w-[200px]">
                      {territory.species?.slice(0, 4).map(s => (
                        <Badge key={s} variant="outline" className="text-[10px] border-gray-600 text-gray-400">
                          {s}
                        </Badge>
                      ))}
                    </div>

                    {/* Stats */}
                    <div className="hidden lg:flex items-center gap-4 text-center">
                      <div>
                        <div className="text-gray-500 text-[10px] uppercase">Succès</div>
                        <div className="text-green-400 font-bold">{territory.stats?.avg_success_rate}%</div>
                      </div>
                      <div>
                        <div className="text-gray-500 text-[10px] uppercase">Note</div>
                        <div className="text-yellow-400 font-bold flex items-center gap-1">
                          <Star className="h-3 w-3 fill-yellow-400" />
                          {territory.stats?.visitor_rating}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-500 text-[10px] uppercase">Permis/an</div>
                        <div className="text-blue-400 font-bold">{territory.stats?.annual_permits?.toLocaleString()}</div>
                      </div>
                    </div>

                    {/* Performance Score */}
                    <div className={`w-16 h-16 rounded-xl flex flex-col items-center justify-center ${getScoreColor(territory.performance_score)}`}>
                      <div className="text-2xl font-bold">{territory.performance_score}</div>
                      <div className="text-[9px] uppercase opacity-70">Score</div>
                    </div>

                    {/* Action */}
                    {territory.website && (
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => window.open(territory.website, '_blank')}
                        className="text-gray-400 hover:text-[#f5a623]"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}

          {sortedRankings.length === 0 && (
            <Card className="bg-card border-border">
              <CardContent className="p-12 text-center">
                <Target className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">Aucun territoire trouvé avec ces critères</p>
                <Button
                  variant="outline"
                  className="mt-4"
                  onClick={() => {
                    setFilters({ species: '', region: '', type: '' });
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

      {/* Legend */}
      <Card className="bg-card border-border">
        <CardContent className="p-4">
          <h4 className="text-white text-sm font-semibold mb-3">Légende des scores</h4>
          <div className="flex flex-wrap gap-4 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-green-500/20 flex items-center justify-center text-green-400 font-bold">80+</div>
              <span className="text-gray-400">Excellent</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-yellow-500/20 flex items-center justify-center text-yellow-400 font-bold">60+</div>
              <span className="text-gray-400">Très bon</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-orange-500/20 flex items-center justify-center text-orange-400 font-bold">40+</div>
              <span className="text-gray-400">Bon</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-red-500/20 flex items-center justify-center text-red-400 font-bold">&lt;40</div>
              <span className="text-gray-400">À améliorer</span>
            </div>
          </div>
          <p className="text-gray-500 text-[10px] mt-3">
            * Les scores sont calculés selon la diversité des espèces, le taux de succès, la note des visiteurs et la popularité.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default TerritoryRankings;
