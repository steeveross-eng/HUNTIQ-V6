/**
 * TerritoryInventory - Component for browsing and analyzing hunting territories
 * Integrates with AnalyzerModule under "Pourvoyeurs" category
 */

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import TerritoryAdvanced from './TerritoryAdvanced';
import { useLanguage } from '@/contexts/LanguageContext';
import {
  Search,
  MapPin,
  Target,
  Trees,
  Mountain,
  Building2,
  Star,
  TrendingUp,
  Filter,
  ChevronRight,
  ExternalLink,
  Phone,
  Mail,
  Globe,
  Loader2,
  CheckCircle,
  AlertTriangle,
  Users,
  Tent,
  Navigation,
  Award,
  Sparkles,
  Database,
  Handshake,
  BarChart3,
  Map,
  Compass,
  RefreshCw,
  Eye,
  Bookmark,
  Share2,
  Shield,
  Lock,
  CircleDot
} from 'lucide-react';
import { 
  TERRITORY_ICONS, 
  ANIMAL_ICONS 
} from '@/config/bionic-icons';
import { 
  TERRITORY_COLORS 
} from '@/config/bionic-colors';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// ============================================
// TYPE ICONS & LABELS - BIONIC Design System
// ============================================

const TYPE_CONFIG = {
  zec: { icon: Tent, label: 'ZEC', color: 'bg-[var(--bionic-green-muted)] text-[var(--bionic-green-primary)] border-[var(--bionic-green-primary)]/50' },
  sepaq: { icon: CircleDot, label: 'Sépaq', color: 'bg-[var(--bionic-blue-muted)] text-[var(--bionic-blue-light)] border-[var(--bionic-blue-light)]/50' },
  pourvoirie: { icon: Building2, label: 'Pourvoirie', color: 'bg-[var(--bionic-purple-muted)] text-[var(--bionic-purple-primary)] border-[var(--bionic-purple-primary)]/50' },
  club: { icon: Target, label: 'Club', color: 'bg-[var(--bionic-gold-muted)] text-[var(--bionic-gold-primary)] border-[var(--bionic-gold-primary)]/50' },
  outfitter: { icon: Compass, label: 'Outfitter', color: 'bg-[var(--bionic-gold-muted)] text-[var(--bionic-gold-light)] border-[var(--bionic-gold-light)]/50' },
  private: { icon: Lock, label: 'Privé', color: 'bg-[var(--bionic-gray-800)] text-[var(--bionic-gray-400)] border-[var(--bionic-gray-500)]/50' },
  anticosti: { icon: Mountain, label: 'Anticosti', color: 'bg-[var(--bionic-cyan-muted)] text-[var(--bionic-cyan-primary)] border-[var(--bionic-cyan-primary)]/50' },
  reserve: { icon: Trees, label: 'Réserve', color: 'bg-[var(--bionic-green-muted)] text-[var(--bionic-green-light)] border-[var(--bionic-green-light)]/50' },
  indigenous: { icon: Shield, label: 'Autochtone', color: 'bg-[var(--bionic-red-muted)] text-[var(--bionic-red-primary)] border-[var(--bionic-red-primary)]/50' }
};

const SPECIES_CONFIG = {
  orignal: { icon: CircleDot, label: 'Orignal' },
  chevreuil: { icon: CircleDot, label: 'Chevreuil' },
  ours: { icon: CircleDot, label: 'Ours' },
  caribou: { icon: CircleDot, label: 'Caribou' },
  wapiti: { icon: CircleDot, label: 'Wapiti' },
  cerf_mulet: { icon: CircleDot, label: 'Cerf mulet' },
  dindon: { icon: CircleDot, label: 'Dindon' },
  petit_gibier: { icon: CircleDot, label: 'Petit gibier' },
  sauvagine: { icon: CircleDot, label: 'Sauvagine' },
  grizzly: { icon: CircleDot, label: 'Grizzly' }
};

const PROVINCE_NAMES = {
  QC: 'Québec',
  ON: 'Ontario',
  NB: 'Nouveau-Brunswick',
  NS: 'Nouvelle-Écosse',
  PE: 'Î.-P.-É.',
  NL: 'Terre-Neuve',
  MB: 'Manitoba',
  SK: 'Saskatchewan',
  AB: 'Alberta',
  BC: 'Colombie-Britannique',
  YT: 'Yukon',
  NT: 'T.N.-O.'
};

// ============================================
// SCORE BADGE COMPONENT
// ============================================

const ScoreBadge = ({ score, size = 'md' }) => {
  const getScoreColor = (s) => {
    if (s >= 80) return 'bg-green-500 text-white';
    if (s >= 60) return 'bg-yellow-500 text-black';
    if (s >= 40) return 'bg-orange-500 text-white';
    return 'bg-red-500 text-white';
  };

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-lg px-4 py-2 font-bold'
  };

  return (
    <span className={`rounded-full ${getScoreColor(score)} ${sizeClasses[size]}`}>
      {score.toFixed(1)}
    </span>
  );
};

// ============================================
// TERRITORY CARD COMPONENT
// ============================================

const TerritoryCard = ({ territory, onClick }) => {
  const typeConfig = TYPE_CONFIG[territory.establishment_type] || TYPE_CONFIG.outfitter;
  const TypeIcon = typeConfig.icon;
  
  return (
    <Card 
      className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)] hover:border-[var(--bionic-gold-primary)]/50 transition-all cursor-pointer group"
      onClick={() => onClick(territory)}
      data-testid={`territory-card-${territory.id}`}
    >
      <CardContent className="p-2">
        <div className="flex items-start justify-between mb-1">
          <div className="flex items-center gap-1">
            <TypeIcon className="h-4 w-4 text-[var(--bionic-gold-primary)]" />
            <Badge variant="outline" className={`${typeConfig.color} text-[10px] px-1 py-0`}>
              {typeConfig.label}
            </Badge>
          </div>
          <ScoreBadge score={territory.scoring?.global_score || 0} />
        </div>
        
        <h3 className="text-[var(--bionic-text-primary)] font-semibold text-sm mb-0.5 group-hover:text-[var(--bionic-gold-primary)] transition-colors line-clamp-1">
          {territory.name}
        </h3>
        
        <div className="flex items-center gap-1 text-[var(--bionic-text-secondary)] text-xs mb-1">
          <MapPin className="h-2.5 w-2.5" />
          <span className="truncate">{territory.region || PROVINCE_NAMES[territory.province] || territory.province}</span>
          {territory.is_verified && (
            <CheckCircle className="h-3 w-3 text-[var(--bionic-green-primary)] ml-auto flex-shrink-0" />
          )}
        </div>
        
        {/* Species - Compact with Lucide icons */}
        <div className="flex flex-wrap gap-0.5 mb-1">
          {(territory.species || []).slice(0, 3).map(species => {
            const speciesConfig = SPECIES_CONFIG[species];
            const SpeciesIcon = speciesConfig?.icon || CircleDot;
            return (
              <SpeciesIcon 
                key={species} 
                className="h-3.5 w-3.5 text-[var(--bionic-gold-primary)]" 
                title={speciesConfig?.label} 
              />
            );
          })}
          {(territory.species || []).length > 3 && (
            <span className="text-[var(--bionic-text-muted)] text-[10px]">+{territory.species.length - 3}</span>
          )}
        </div>
        
        {/* Quick stats - Single line */}
        <div className="flex items-center gap-2 text-[10px] text-[var(--bionic-text-secondary)]">
          <span className="flex items-center gap-0.5">
            <Target className="h-2.5 w-2.5 text-[var(--bionic-green-primary)]" />
            {territory.success_rate ? `${territory.success_rate}%` : 'N/D'}
          </span>
          <span className="flex items-center gap-0.5">
            <Trees className="h-2.5 w-2.5 text-[var(--bionic-blue-light)]" />
            {territory.hunting_zones?.length || 0} zones
          </span>
          {territory.price_range && (
            <span className="text-[var(--bionic-gold-primary)] ml-auto">{territory.price_range}</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================
// TERRITORY DETAIL MODAL
// ============================================

const TerritoryDetailModal = ({ territory, open, onClose }) => {
  const { t } = useLanguage();
  if (!territory) return null;
  
  const typeConfig = TYPE_CONFIG[territory.establishment_type] || TYPE_CONFIG.outfitter;
  const TypeIcon = typeConfig.icon;
  const scoring = territory.scoring || {};
  
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <TypeIcon className="h-8 w-8 text-[var(--bionic-gold-primary)]" />
            <div>
              <DialogTitle className="text-[var(--bionic-text-primary)] text-xl">{territory.name}</DialogTitle>
              <DialogDescription className="flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                {territory.region}, {PROVINCE_NAMES[territory.province] || territory.province}
                {territory.is_verified && (
                  <Badge className="bg-[var(--bionic-green-muted)] text-[var(--bionic-green-primary)] text-xs ml-2">
                    <CheckCircle className="h-3 w-3 mr-1" /> {t('territory_verified')}
                  </Badge>
                )}
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>
        
        <div className="space-y-6 py-4">
          {/* Score Section */}
          <div className="bg-[var(--bionic-bg-primary)] p-4 rounded-lg border border-[var(--bionic-border-secondary)]">
            <h4 className="text-[var(--bionic-text-primary)] font-semibold mb-4 flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-[var(--bionic-gold-primary)]" />
              {t('territory_bionic_score')}
            </h4>
            
            <div className="flex items-center justify-center mb-6">
              <div className="text-center">
                <ScoreBadge score={scoring.global_score || 0} size="lg" />
                <p className="text-[var(--bionic-text-secondary)] text-sm mt-2">{t('global_score')}</p>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-[var(--bionic-text-secondary)]">{t('habitat_quality')} (H)</span>
                  <span className="text-[var(--bionic-text-primary)]">{scoring.habitat_index || 0}%</span>
                </div>
                <Progress value={scoring.habitat_index || 0} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-[var(--bionic-text-secondary)]">{t('hunting_pressure')} (P)</span>
                  <span className="text-[var(--bionic-text-primary)]">{scoring.pressure_index || 0}%</span>
                </div>
                <Progress value={scoring.pressure_index || 0} className="h-2 [&>div]:bg-[var(--bionic-gold-primary)]" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-[var(--bionic-text-secondary)]">{t('territory_success_rate')} (S)</span>
                  <span className="text-[var(--bionic-text-primary)]">{scoring.success_index || 0}%</span>
                </div>
                <Progress value={scoring.success_index || 0} className="h-2 [&>div]:bg-[var(--bionic-green-primary)]" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-[var(--bionic-text-secondary)]">{t('accessibility')} (A)</span>
                  <span className="text-[var(--bionic-text-primary)]">{scoring.accessibility_index || 0}%</span>
                </div>
                <Progress value={scoring.accessibility_index || 0} className="h-2 [&>div]:bg-[var(--bionic-blue-light)]" />
              </div>
            </div>
          </div>
          
          {/* Description */}
          {territory.description && (
            <div>
              <h4 className="text-[var(--bionic-text-primary)] font-semibold mb-2">Description</h4>
              <p className="text-[var(--bionic-text-secondary)]">{territory.description}</p>
            </div>
          )}
          
          {/* Species */}
          <div>
            <h4 className="text-[var(--bionic-text-primary)] font-semibold mb-2">{t('territory_species')}</h4>
            <div className="flex flex-wrap gap-2">
              {(territory.species || []).map(species => {
                const speciesConfig = SPECIES_CONFIG[species];
                const SpeciesIcon = speciesConfig?.icon || CircleDot;
                return (
                  <Badge key={species} variant="outline" className="text-[var(--bionic-text-primary)] border-[var(--bionic-border-primary)] flex items-center gap-1">
                    <SpeciesIcon className="h-3 w-3" /> {speciesConfig?.label || species}
                  </Badge>
                );
              })}
            </div>
          </div>
          
          {/* Hunting Zones */}
          {territory.hunting_zones && territory.hunting_zones.length > 0 && (
            <div>
              <h4 className="text-[var(--bionic-text-primary)] font-semibold mb-2">{t('territory_hunting_zones')}</h4>
              <div className="flex flex-wrap gap-2">
                {territory.hunting_zones.map((zone, idx) => (
                  <Badge key={idx} className="bg-[var(--bionic-gold-muted)] text-[var(--bionic-gold-primary)]">
                    {zone}
                  </Badge>
                ))}
              </div>
            </div>
          )}
          
          {/* Services */}
          {territory.services && Object.values(territory.services).some(v => v) && (
            <div>
              <h4 className="text-[var(--bionic-text-primary)] font-semibold mb-2">{t('territory_services')}</h4>
              <div className="grid grid-cols-2 gap-2">
                {territory.services.accommodation && (
                  <div className="flex items-center gap-2 text-[var(--bionic-text-secondary)] text-sm">
                    <Tent className="h-4 w-4 text-[var(--bionic-green-primary)]" /> {t('lands_features') || 'Hébergement'}
                  </div>
                )}
                {territory.services.guided_hunts && (
                  <div className="flex items-center gap-2 text-[var(--bionic-text-secondary)] text-sm">
                    <Users className="h-4 w-4 text-[var(--bionic-green-primary)]" /> {t('services_guided') || 'Chasse guidée'}
                  </div>
                )}
                {territory.services.meals_included && (
                  <div className="flex items-center gap-2 text-[var(--bionic-text-secondary)] text-sm">
                    <CheckCircle className="h-4 w-4 text-[var(--bionic-green-primary)]" /> {t('services_meals') || 'Repas inclus'}
                  </div>
                )}
                {territory.services.meat_processing && (
                  <div className="flex items-center gap-2 text-[var(--bionic-text-secondary)] text-sm">
                    <CheckCircle className="h-4 w-4 text-[var(--bionic-green-primary)]" /> {t('services_processing') || 'Traitement gibier'}
                  </div>
                )}
                {territory.services.transportation && (
                  <div className="flex items-center gap-2 text-[var(--bionic-text-secondary)] text-sm">
                    <Navigation className="h-4 w-4 text-[var(--bionic-green-primary)]" /> Transport
                  </div>
                )}
              </div>
            </div>
          )}
          
          {/* Contact Info */}
          <div className="bg-[var(--bionic-bg-primary)] p-4 rounded-lg border border-[var(--bionic-border-secondary)]">
            <h4 className="text-[var(--bionic-text-primary)] font-semibold mb-3">{t('territory_contact')}</h4>
            <div className="space-y-2">
              {territory.website && (
                <a 
                  href={territory.website} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-[var(--bionic-gold-primary)] hover:underline"
                >
                  <Globe className="h-4 w-4" />
                  {territory.website}
                  <ExternalLink className="h-3 w-3" />
                </a>
              )}
              {territory.email && (
                <a 
                  href={`mailto:${territory.email}`}
                  className="flex items-center gap-2 text-[var(--bionic-text-secondary)] hover:text-[var(--bionic-text-primary)]"
                >
                  <Mail className="h-4 w-4" />
                  {territory.email}
                </a>
              )}
              {territory.phone && (
                <a 
                  href={`tel:${territory.phone}`}
                  className="flex items-center gap-2 text-[var(--bionic-text-secondary)] hover:text-[var(--bionic-text-primary)]"
                >
                  <Phone className="h-4 w-4" />
                  {territory.phone}
                </a>
              )}
            </div>
          </div>
          
          {/* Internal ID */}
          <div className="text-xs text-[var(--bionic-text-muted)] text-center">
            ID: {territory.internal_id}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// ============================================
// MAIN COMPONENT
// ============================================

const TerritoryInventory = () => {
  const { t, language } = useLanguage();
  const [territories, setTerritories] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedTerritory, setSelectedTerritory] = useState(null);
  const [showDetail, setShowDetail] = useState(false);
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterProvince, setFilterProvince] = useState('all');
  const [filterSpecies, setFilterSpecies] = useState('all');
  const [sortBy, setSortBy] = useState('global_score');
  const [showFilters, setShowFilters] = useState(false);
  
  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  const loadTerritories = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '12',
        sort_by: sortBy
      });
      
      if (searchQuery) params.append('search', searchQuery);
      if (filterType !== 'all') params.append('establishment_type', filterType);
      if (filterProvince !== 'all') params.append('province', filterProvince);
      if (filterSpecies !== 'all') params.append('species', filterSpecies);
      
      const response = await axios.get(`${API}/territories?${params}`);
      
      if (response.data.success) {
        setTerritories(response.data.territories);
        setTotal(response.data.pagination.total);
        setTotalPages(response.data.pagination.pages);
      }
    } catch (error) {
      console.error('Error loading territories:', error);
      toast.error('Erreur lors du chargement des territoires');
    }
    setLoading(false);
  }, [page, searchQuery, filterType, filterProvince, filterSpecies, sortBy]);

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API}/territories/stats`);
      if (response.data.success) {
        setStats(response.data.stats);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  useEffect(() => {
    loadTerritories();
  }, [loadTerritories]);

  useEffect(() => {
    loadStats();
  }, []);

  const handleTerritoryClick = (territory) => {
    setSelectedTerritory(territory);
    setShowDetail(true);
  };

  const handleSearch = (e) => {
    if (e.key === 'Enter') {
      setPage(1);
      loadTerritories();
    }
  };

  const resetFilters = () => {
    setSearchQuery('');
    setFilterType('all');
    setFilterProvince('all');
    setFilterSpecies('all');
    setSortBy('global_score');
    setPage(1);
  };

  return (
    <div className="space-y-4">
      {/* Main Tabs - Inventory vs Advanced */}
      <Tabs defaultValue="inventory" className="w-full">
        <TabsList className="grid w-full max-w-md grid-cols-2 mb-4 bg-[var(--bionic-bg-card)] border border-[var(--bionic-border-secondary)]">
          <TabsTrigger 
            value="inventory" 
            className="data-[state=active]:bg-[var(--bionic-gold-primary)] data-[state=active]:text-black gap-2"
          >
            <Map className="h-4 w-4" />
            {t('territory_inventory') || 'Inventaire'}
          </TabsTrigger>
          <TabsTrigger 
            value="advanced" 
            className="data-[state=active]:bg-[var(--bionic-gold-primary)] data-[state=active]:text-black gap-2"
          >
            <Sparkles className="h-4 w-4" />
            {t('territory_ai_scraping') || 'IA & Scraping'}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="inventory" className="space-y-3">
          {/* Stats Overview - Compact */}
          {stats && (
            <div className="grid grid-cols-4 gap-2">
              <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
                <CardContent className="p-2 text-center">
                  <div className="text-xl font-bold text-[var(--bionic-gold-primary)]">{stats.total}</div>
                  <div className="text-[var(--bionic-text-secondary)] text-xs">{t('common_territories')}</div>
                </CardContent>
              </Card>
              <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
                <CardContent className="p-2 text-center">
                  <div className="text-xl font-bold text-[var(--bionic-green-primary)]">{stats.verified}</div>
                  <div className="text-[var(--bionic-text-secondary)] text-xs">{t('territory_verified')}</div>
                </CardContent>
              </Card>
              <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
                <CardContent className="p-2 text-center">
                  <div className="text-xl font-bold text-[var(--bionic-blue-light)]">{Object.keys(stats.by_province || {}).length}</div>
                  <div className="text-[var(--bionic-text-secondary)] text-xs">{t('common_provinces')}</div>
                </CardContent>
              </Card>
              <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
                <CardContent className="p-2 text-center">
                  <div className="text-xl font-bold text-[var(--bionic-purple-primary)]">{stats.avg_score}</div>
                  <div className="text-[var(--bionic-text-secondary)] text-xs">{t('territory_avg_score')}</div>
                </CardContent>
              </Card>
            </div>
          )}

      {/* Search & Filters - Compact */}
      <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
        <CardContent className="p-3">
          <div className="flex flex-col md:flex-row gap-2">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--bionic-text-muted)]" />
              <Input
                placeholder={t('territory_search_placeholder') || 'Rechercher un territoire, une région...'}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={handleSearch}
                className="pl-10 bg-[var(--bionic-bg-primary)] h-9 text-sm border-[var(--bionic-border-secondary)]"
                data-testid="territory-search"
              />
            </div>
            
            {/* Quick Filters - Compact */}
            <Select value={filterType} onValueChange={(v) => { setFilterType(v); setPage(1); }}>
              <SelectTrigger className="w-[130px] bg-[var(--bionic-bg-primary)] h-9 text-sm border-[var(--bionic-border-secondary)]">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t('filter_all_types') || 'Tous types'}</SelectItem>
                {Object.entries(TYPE_CONFIG).map(([key, config]) => {
                  const IconComponent = config.icon;
                  return (
                    <SelectItem key={key} value={key}>
                      <span className="flex items-center gap-2"><IconComponent className="h-3 w-3" /> {config.label}</span>
                    </SelectItem>
                  );
                })}
              </SelectContent>
            </Select>
            
            <Select value={filterProvince} onValueChange={(v) => { setFilterProvince(v); setPage(1); }}>
              <SelectTrigger className="w-[130px] bg-[var(--bionic-bg-primary)] h-9 text-sm border-[var(--bionic-border-secondary)]">
                <SelectValue placeholder={t('common_province') || 'Province'} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t('filter_all_provinces') || 'Toutes provinces'}</SelectItem>
                {Object.entries(PROVINCE_NAMES).map(([code, name]) => (
                  <SelectItem key={code} value={code}>{name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Select value={filterSpecies} onValueChange={(v) => { setFilterSpecies(v); setPage(1); }}>
              <SelectTrigger className="w-[130px] bg-[var(--bionic-bg-primary)] h-9 text-sm border-[var(--bionic-border-secondary)]">
                <SelectValue placeholder={t('common_species') || 'Espèce'} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t('filter_all_species') || 'Toutes espèces'}</SelectItem>
                {Object.entries(SPECIES_CONFIG).map(([key, config]) => {
                  const IconComponent = config.icon;
                  return (
                    <SelectItem key={key} value={key}>
                      <span className="flex items-center gap-2"><IconComponent className="h-3 w-3" /> {config.label}</span>
                    </SelectItem>
                  );
                })}
              </SelectContent>
            </Select>
            
            <Select value={sortBy} onValueChange={(v) => { setSortBy(v); setPage(1); }}>
              <SelectTrigger className="w-[120px] bg-[var(--bionic-bg-primary)] h-9 text-sm border-[var(--bionic-border-secondary)]">
                <SelectValue placeholder={t('common_sort') || 'Trier'} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="global_score">{t('sort_score') || 'Score'} ↓</SelectItem>
                <SelectItem value="name">{t('sort_name') || 'Nom'} A-Z</SelectItem>
                <SelectItem value="success_rate">{t('sort_success') || 'Succès'} ↓</SelectItem>
                <SelectItem value="created_at">{t('sort_recent') || 'Récent'}</SelectItem>
              </SelectContent>
            </Select>
            
            <Button variant="outline" size="sm" onClick={resetFilters} className="h-9 border-[var(--bionic-border-secondary)]" title={t('filter_reset') || 'Réinitialiser'}>
              <RefreshCw className="h-4 w-4 mr-1" />
              {t('common_refresh')}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Results - Compact */}
      <div className="flex items-center justify-between">
        <p className="text-[var(--bionic-text-secondary)] text-xs">
          {total} {t('territory_found_count') || 'territoire'}{total !== 1 ? 's' : ''} {t('territory_found') || 'trouvé'}{total !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Territory Grid - Compact 5 columns */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-[var(--bionic-gold-primary)]" />
        </div>
      ) : territories.length === 0 ? (
        <Card className="bg-[var(--bionic-bg-card)] border-[var(--bionic-border-secondary)]">
          <CardContent className="p-8 text-center">
            <Map className="h-12 w-12 text-[var(--bionic-gray-500)] mx-auto mb-3" />
            <h3 className="text-[var(--bionic-text-primary)] text-base font-semibold mb-1">{t('msg_no_results') || 'Aucun territoire trouvé'}</h3>
            <p className="text-[var(--bionic-text-secondary)] text-sm">{t('filter_hint') || 'Modifiez vos filtres ou essayez une autre recherche'}</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-2">
          {territories.map((territory) => (
            <TerritoryCard
              key={territory.id}
              territory={territory}
              onClick={handleTerritoryClick}
            />
          ))}
        </div>
      )}

      {/* Pagination - Compact */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="border-[var(--bionic-border-secondary)]"
          >
            ← {t('pagination_prev') || 'Préc'}
          </Button>
          <span className="text-[var(--bionic-text-secondary)] text-sm px-2">
            {page}/{totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="border-[var(--bionic-border-secondary)]"
          >
            {t('pagination_next') || 'Suiv'} →
          </Button>
        </div>
      )}

      {/* Detail Modal */}
      <TerritoryDetailModal
        territory={selectedTerritory}
        open={showDetail}
        onClose={() => setShowDetail(false)}
      />
        </TabsContent>

        {/* Advanced Tab - AI & Scraping */}
        <TabsContent value="advanced">
          <TerritoryAdvanced />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default TerritoryInventory;
