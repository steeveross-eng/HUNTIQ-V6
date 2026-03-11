/**
 * LandsRental - Module complet de location de terres de chasse
 * - Recherche avancée avec filtres
 * - Publication d'annonces
 * - Système d'ententes sécurisées
 * - Monétisation multi-niveaux
 */

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Progress } from '@/components/ui/progress';
import { useLanguage } from '@/contexts/LanguageContext';
import { 
  Search, 
  Plus, 
  Filter, 
  MapPin, 
  DollarSign,
  Heart,
  Eye,
  Star,
  Clock,
  ChevronRight,
  ChevronDown,
  User,
  LogIn,
  LogOut,
  Package,
  Trees,
  Mountain,
  Target,
  Camera,
  Loader2,
  X,
  Edit,
  Trash2,
  Crown,
  Sparkles,
  TrendingUp,
  Mail,
  Phone,
  CheckCircle,
  AlertCircle,
  FileText,
  Download,
  Shield,
  Zap,
  Building2,
  Compass,
  Map,
  Grid,
  List,
  CreditCard,
  Send,
  AlertTriangle,
  Check,
  Calendar,
  Users,
  Dog,
  Flame,
  Tent,
  Navigation,
  Award,
  Lock,
  ArrowLeft,
  Home,
  RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// ============================================
// GAME SPECIES ICONS
// ============================================

const SPECIES_CONFIG = {
  orignal: { icon: '🦌', name: 'Orignal', color: 'bg-amber-500/20 text-amber-400' },
  chevreuil: { icon: '🦌', name: 'Chevreuil', color: 'bg-orange-500/20 text-orange-400' },
  ours: { icon: '🐻', name: 'Ours', color: 'bg-stone-500/20 text-stone-400' },
  dindon: { icon: '🦃', name: 'Dindon', color: 'bg-red-500/20 text-red-400' },
  petit_gibier: { icon: '🐰', name: 'Petit gibier', color: 'bg-green-500/20 text-green-400' },
  multi_especes: { icon: '🎯', name: 'Multi-espèces', color: 'bg-purple-500/20 text-purple-400' }
};

const TERRAIN_ICONS = {
  foret: { icon: <Trees className="h-4 w-4" />, name: 'Forêt' },
  mixte: { icon: <Mountain className="h-4 w-4" />, name: 'Mixte' },
  agricole: { icon: <Grid className="h-4 w-4" />, name: 'Agricole' },
  montagne: { icon: <Mountain className="h-4 w-4" />, name: 'Montagne' },
  marecage: { icon: <Navigation className="h-4 w-4" />, name: 'Marécage' },
  prairie: { icon: <Compass className="h-4 w-4" />, name: 'Prairie' }
};

// ============================================
// AUTH STORAGE
// ============================================

const getStoredAuth = (type) => {
  const stored = localStorage.getItem(`lands_${type}_auth`);
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch {
      return null;
    }
  }
  return null;
};

const setStoredAuth = (type, auth) => {
  if (auth) {
    localStorage.setItem(`lands_${type}_auth`, JSON.stringify(auth));
  } else {
    localStorage.removeItem(`lands_${type}_auth`);
  }
};

// ============================================
// MAIN COMPONENT
// ============================================

const LandsRental = () => {
  const navigate = useNavigate();
  
  // Auth state
  const [ownerAuth, setOwnerAuth] = useState(getStoredAuth('owner'));
  const [renterAuth, setRenterAuth] = useState(getStoredAuth('renter'));
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authType, setAuthType] = useState('renter'); // owner or renter
  const [authMode, setAuthMode] = useState('login'); // login or register

  // Config & Data
  const [config, setConfig] = useState(null);
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalListings, setTotalListings] = useState(0);

  // Filters
  const [filters, setFilters] = useState({
    game_species: '',
    region: '',
    hunting_zone: '',
    terrain_type: '',
    min_price: '',
    max_price: '',
    min_surface: '',
    max_surface: '',
    has_blinds: false,
    has_cameras: false,
    dogs_allowed: false
  });
  const [showFilters, setShowFilters] = useState(false);
  const [sortBy, setSortBy] = useState('created_at');
  const [viewMode, setViewMode] = useState('grid');
  const [page, setPage] = useState(1);
  const [refreshing, setRefreshing] = useState(false);

  // Reset filters function
  const handleRefresh = async () => {
    setRefreshing(true);
    setFilters({
      game_species: '',
      region: '',
      hunting_zone: '',
      terrain_type: '',
      min_price: '',
      max_price: '',
      min_surface: '',
      max_surface: '',
      has_blinds: false,
      has_cameras: false,
      dogs_allowed: false
    });
    setPage(1);
    setSortBy('created_at');
    await loadConfig();
    setRefreshing(false);
    toast.success(t('common_refresh') || 'Actualisé');
  };

  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedListing, setSelectedListing] = useState(null);
  const [showAgreementModal, setShowAgreementModal] = useState(false);
  const [showPricingModal, setShowPricingModal] = useState(false);
  const [showContractModal, setShowContractModal] = useState(false);
  const [contractText, setContractText] = useState('');
  const [showMyListings, setShowMyListings] = useState(false);
  const [myListings, setMyListings] = useState([]);

  // Forms
  const [newListing, setNewListing] = useState({
    title: '',
    description: '',
    region: '',
    mrc: '',
    city: '',
    hunting_zones: [],
    surface_acres: '',
    terrain_types: [],
    access_types: [],
    game_species: [],
    has_blinds: false,
    has_salt_licks: false,
    has_cameras: false,
    game_history: '',
    photos: [],
    price_per_day: '',
    price_per_week: '',
    price_per_season: '',
    available_from: '',
    available_to: '',
    owner_rules: '',
    max_hunters: 4,
    dogs_allowed: false,
    camping_allowed: false,
    fire_allowed: false
  });

  const [agreementForm, setAgreementForm] = useState({
    start_date: '',
    end_date: '',
    total_price: '',
    num_hunters: 1,
    special_conditions: ''
  });

  // ============================================
  // LOAD DATA
  // ============================================

  const loadConfig = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/lands/config`);
      setConfig(response.data);
    } catch (error) {
      console.error('Error loading config:', error);
    }
  }, []);

  const loadListings = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value && value !== '' && value !== false) {
          params.append(key, value);
        }
      });
      params.append('page', page);
      params.append('sort_by', sortBy);
      params.append('limit', 20);
      
      if (renterAuth?.renter?.subscription_tier) {
        params.append('renter_tier', renterAuth.renter.subscription_tier);
      }

      const response = await axios.get(`${API}/lands/listings?${params.toString()}`);
      setListings(response.data.listings);
      setTotalListings(response.data.total);
    } catch (error) {
      console.error('Error loading listings:', error);
    } finally {
      setLoading(false);
    }
  }, [filters, page, sortBy, renterAuth]);

  const loadMyListings = async () => {
    if (!ownerAuth?.owner?.id) return;
    try {
      const response = await axios.get(`${API}/lands/listings?owner_id=${ownerAuth.owner.id}`);
      setMyListings(response.data.listings || []);
    } catch (error) {
      console.error('Error loading my listings:', error);
    }
  };

  useEffect(() => {
    loadConfig();
  }, [loadConfig]);

  useEffect(() => {
    if (config) {
      loadListings();
    }
  }, [config, loadListings]);

  // ============================================
  // AUTH HANDLERS
  // ============================================

  const handleLogin = async (type, credentials) => {
    try {
      const endpoint = type === 'owner' ? '/lands/owners/login' : '/lands/renters/login';
      const response = await axios.post(`${API}${endpoint}?email=${encodeURIComponent(credentials.email)}&password=${encodeURIComponent(credentials.password)}`);
      
      if (type === 'owner') {
        setOwnerAuth(response.data);
        setStoredAuth('owner', response.data);
      } else {
        setRenterAuth(response.data);
        setStoredAuth('renter', response.data);
      }
      
      toast.success('Connexion réussie!');
      setShowAuthModal(false);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur de connexion');
    }
  };

  const handleRegister = async (type, data) => {
    try {
      const endpoint = type === 'owner' ? '/lands/owners/register' : '/lands/renters/register';
      const params = new URLSearchParams(data);
      const response = await axios.post(`${API}${endpoint}?${params.toString()}`);
      
      if (type === 'owner') {
        setOwnerAuth(response.data);
        setStoredAuth('owner', response.data);
      } else {
        setRenterAuth(response.data);
        setStoredAuth('renter', response.data);
      }
      
      toast.success('Inscription réussie!');
      setShowAuthModal(false);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur d\'inscription');
    }
  };

  const handleLogout = (type) => {
    if (type === 'owner') {
      setOwnerAuth(null);
      setStoredAuth('owner', null);
    } else {
      setRenterAuth(null);
      setStoredAuth('renter', null);
    }
    toast.success('Déconnexion réussie');
  };

  // ============================================
  // LISTING HANDLERS
  // ============================================

  const handleCreateListing = async () => {
    if (!ownerAuth?.owner?.id) {
      setAuthType('owner');
      setShowAuthModal(true);
      return;
    }

    try {
      const listingData = {
        ...newListing,
        surface_acres: parseFloat(newListing.surface_acres) || 0,
        price_per_day: parseFloat(newListing.price_per_day) || null,
        price_per_week: parseFloat(newListing.price_per_week) || null,
        price_per_season: parseFloat(newListing.price_per_season) || null,
        max_hunters: parseInt(newListing.max_hunters) || 4
      };

      const response = await axios.post(
        `${API}/lands/listings?owner_id=${ownerAuth.owner.id}`,
        listingData
      );

      toast.success(`Annonce créée! Frais de publication: ${response.data.payment_required}$`);
      setShowCreateModal(false);
      
      // Reset form
      setNewListing({
        title: '', description: '', region: '', mrc: '', city: '',
        hunting_zones: [], surface_acres: '', terrain_types: [],
        access_types: [], game_species: [], has_blinds: false,
        has_salt_licks: false, has_cameras: false, game_history: '',
        photos: [], price_per_day: '', price_per_week: '',
        price_per_season: '', available_from: '', available_to: '',
        owner_rules: '', max_hunters: 4, dogs_allowed: false,
        camping_allowed: false, fire_allowed: false
      });

      // Offer to pay
      if (response.data.payment_required > 0) {
        handlePurchase('listing_basic', response.data.listing.id);
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la création');
    }
  };

  const handleViewListing = async (listing) => {
    try {
      const response = await axios.get(`${API}/lands/listings/${listing.id}`);
      setSelectedListing(response.data);
      setShowDetailModal(true);
    } catch (error) {
      toast.error('Erreur lors du chargement');
    }
  };

  // ============================================
  // AGREEMENT HANDLERS
  // ============================================

  const handleCreateAgreement = async () => {
    if (!renterAuth?.renter?.id) {
      setAuthType('renter');
      setShowAuthModal(true);
      return;
    }

    if (!agreementForm.start_date || !agreementForm.end_date || !agreementForm.total_price) {
      toast.error('Veuillez remplir tous les champs obligatoires');
      return;
    }

    try {
      const response = await axios.post(
        `${API}/lands/agreements?renter_id=${renterAuth.renter.id}`,
        {
          land_id: selectedListing.listing.id,
          ...agreementForm,
          total_price: parseFloat(agreementForm.total_price),
          num_hunters: parseInt(agreementForm.num_hunters)
        }
      );

      toast.success('Demande de location envoyée!');
      setShowAgreementModal(false);
      
      // Show contract
      const contractResponse = await axios.get(`${API}/lands/agreements/${response.data.agreement.id}/contract`);
      setContractText(contractResponse.data.contract_text);
      setShowContractModal(true);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la demande');
    }
  };

  // ============================================
  // PURCHASE HANDLERS
  // ============================================

  const handlePurchase = async (serviceId, listingId = null) => {
    const userType = ownerAuth ? 'owner' : 'renter';
    const userId = ownerAuth?.owner?.id || renterAuth?.renter?.id;

    if (!userId) {
      setAuthType(listingId ? 'owner' : 'renter');
      setShowAuthModal(true);
      return;
    }

    try {
      const params = new URLSearchParams({
        service_id: serviceId,
        user_type: userType,
        user_id: userId,
        origin_url: window.location.origin
      });
      if (listingId) params.append('listing_id', listingId);

      const response = await axios.post(`${API}/lands/purchase?${params.toString()}`);
      
      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur de paiement');
    }
  };

  // ============================================
  // RENDER HELPERS
  // ============================================

  const formatPrice = (price) => {
    if (!price) return 'N/A';
    return new Intl.NumberFormat('fr-CA', { style: 'currency', currency: 'CAD' }).format(price);
  };

  const getSpeciesIcon = (species) => {
    return SPECIES_CONFIG[species]?.icon || '🎯';
  };

  // ============================================
  // RENDER
  // ============================================

  return (
    <div className="min-h-screen bg-[#0a0a0a] pt-20 pb-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Back Button */}
        <Button 
          variant="ghost" 
          onClick={() => navigate('/')}
          className="mb-4 text-gray-400 hover:text-white hover:bg-gray-800/50"
          data-testid="back-button-lands"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Retour à l'accueil
        </Button>

        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                <Trees className="h-8 w-8 text-green-500" />
                Terres à Louer
              </h1>
              <p className="text-gray-400 mt-1">
                Location de terrains privés pour la chasse au Québec
              </p>
            </div>

            {/* Auth & Actions */}
            <div className="flex flex-wrap items-center gap-3">
              {/* Renter Account */}
              {renterAuth ? (
                <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-green-500/10 border border-green-500/30">
                  <Target className="h-4 w-4 text-green-400" />
                  <span className="text-green-400 text-sm">{renterAuth.renter?.name}</span>
                  {renterAuth.renter?.subscription_tier !== 'free' && (
                    <Badge className="bg-purple-500/20 text-purple-400 text-[10px]">
                      {renterAuth.renter?.subscription_tier?.toUpperCase()}
                    </Badge>
                  )}
                  <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => handleLogout('renter')}>
                    <LogOut className="h-3 w-3" />
                  </Button>
                </div>
              ) : (
                <Button
                  variant="outline"
                  className="text-green-400 border-green-500/50"
                  onClick={() => { setAuthType('renter'); setShowAuthModal(true); }}
                >
                  <Target className="h-4 w-4 mr-2" />
                  Espace Chasseur
                </Button>
              )}

              {/* Owner Account */}
              {ownerAuth ? (
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    className="text-amber-400 border-amber-500/50"
                    onClick={() => { loadMyListings(); setShowMyListings(true); }}
                  >
                    <Package className="h-4 w-4 mr-2" />
                    Mes Terres
                  </Button>
                  <Button
                    className="bg-[#f5a623] hover:bg-[#d4891c] text-black"
                    onClick={() => setShowCreateModal(true)}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Publier
                  </Button>
                  <Button variant="ghost" size="icon" onClick={() => handleLogout('owner')}>
                    <LogOut className="h-4 w-4" />
                  </Button>
                </div>
              ) : (
                <Button
                  className="bg-amber-500 hover:bg-amber-600 text-black"
                  onClick={() => { setAuthType('owner'); setShowAuthModal(true); }}
                >
                  <Building2 className="h-4 w-4 mr-2" />
                  Espace Propriétaire
                </Button>
              )}

              {/* Pricing */}
              <Button
                variant="outline"
                onClick={() => setShowPricingModal(true)}
              >
                <DollarSign className="h-4 w-4 mr-2" />
                Tarifs
              </Button>
            </div>
          </div>

          {/* Stats */}
          <div className="flex items-center gap-6 mt-4 text-sm text-gray-400">
            <span><Trees className="h-4 w-4 inline mr-1" />{totalListings} terres disponibles</span>
          </div>
        </div>

        {/* Filters Bar */}
        <Card className="bg-card border-border mb-6">
          <CardContent className="p-4">
            <div className="flex flex-wrap gap-4 items-center">
              {/* Quick Species Filter */}
              <div className="flex gap-2">
                {Object.entries(SPECIES_CONFIG).slice(0, 4).map(([key, cfg]) => (
                  <Button
                    key={key}
                    variant={filters.game_species === key ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setFilters(f => ({ ...f, game_species: f.game_species === key ? '' : key }))}
                    className={filters.game_species === key ? 'bg-[#f5a623] text-black' : ''}
                  >
                    <span className="mr-1">{cfg.icon}</span>
                    {cfg.name}
                  </Button>
                ))}
              </div>

              {/* Region Select */}
              {config?.regions && (
                <Select 
                  value={filters.region || "all"} 
                  onValueChange={(v) => setFilters(f => ({ ...f, region: v === "all" ? '' : v }))}
                >
                  <SelectTrigger className="w-48 bg-gray-900 border-gray-700">
                    <SelectValue placeholder="Région" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Toutes les régions</SelectItem>
                    {Object.entries(config.regions).map(([key, region]) => (
                      <SelectItem key={key} value={key}>{region.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}

              {/* Zone Select */}
              <Select 
                value={filters.hunting_zone || "all"} 
                onValueChange={(v) => setFilters(f => ({ ...f, hunting_zone: v === "all" ? '' : v }))}
              >
                <SelectTrigger className="w-32 bg-gray-900 border-gray-700">
                  <SelectValue placeholder="Zone" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Toutes zones</SelectItem>
                  {config?.hunting_zones?.map(zone => (
                    <SelectItem key={zone} value={zone}>Zone {zone}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* More Filters Toggle */}
              <Button
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
                className={showFilters ? 'bg-gray-800' : ''}
              >
                <Filter className="h-4 w-4 mr-2" />
                Plus de filtres
                <ChevronDown className={`h-4 w-4 ml-2 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
              </Button>

              {/* Sort */}
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-40 bg-gray-900 border-gray-700">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="created_at">Plus récentes</SelectItem>
                  <SelectItem value="price_per_day">Prix croissant</SelectItem>
                  <SelectItem value="surface_acres">Superficie</SelectItem>
                  <SelectItem value="views">Popularité</SelectItem>
                </SelectContent>
              </Select>

              {/* Refresh Button */}
              <Button 
                variant="outline" 
                onClick={handleRefresh}
                disabled={refreshing}
                title={t('common_refresh')}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                {t('common_refresh')}
              </Button>

              {/* View Mode */}
              <div className="flex gap-1 ml-auto">
                <Button
                  variant={viewMode === 'grid' ? 'default' : 'ghost'}
                  size="icon"
                  onClick={() => setViewMode('grid')}
                >
                  <Grid className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'ghost'}
                  size="icon"
                  onClick={() => setViewMode('list')}
                >
                  <List className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Extended Filters */}
            {showFilters && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 pt-4 border-t border-border">
                <div>
                  <Label className="text-gray-400 text-xs">Prix min ($)</Label>
                  <Input
                    type="number"
                    value={filters.min_price}
                    onChange={(e) => setFilters(f => ({ ...f, min_price: e.target.value }))}
                    placeholder="0"
                    className="bg-gray-900 border-gray-700"
                  />
                </div>
                <div>
                  <Label className="text-gray-400 text-xs">Prix max ($)</Label>
                  <Input
                    type="number"
                    value={filters.max_price}
                    onChange={(e) => setFilters(f => ({ ...f, max_price: e.target.value }))}
                    placeholder="10000"
                    className="bg-gray-900 border-gray-700"
                  />
                </div>
                <div>
                  <Label className="text-gray-400 text-xs">Surface min (acres)</Label>
                  <Input
                    type="number"
                    value={filters.min_surface}
                    onChange={(e) => setFilters(f => ({ ...f, min_surface: e.target.value }))}
                    placeholder="0"
                    className="bg-gray-900 border-gray-700"
                  />
                </div>
                <div>
                  <Label className="text-gray-400 text-xs">Surface max (acres)</Label>
                  <Input
                    type="number"
                    value={filters.max_surface}
                    onChange={(e) => setFilters(f => ({ ...f, max_surface: e.target.value }))}
                    placeholder="1000"
                    className="bg-gray-900 border-gray-700"
                  />
                </div>
                
                {/* Boolean Filters */}
                <div className="flex items-center gap-2">
                  <Checkbox
                    checked={filters.has_blinds}
                    onCheckedChange={(c) => setFilters(f => ({ ...f, has_blinds: c }))}
                  />
                  <Label className="text-gray-400 text-sm">Avec caches</Label>
                </div>
                <div className="flex items-center gap-2">
                  <Checkbox
                    checked={filters.has_cameras}
                    onCheckedChange={(c) => setFilters(f => ({ ...f, has_cameras: c }))}
                  />
                  <Label className="text-gray-400 text-sm">Avec caméras</Label>
                </div>
                <div className="flex items-center gap-2">
                  <Checkbox
                    checked={filters.dogs_allowed}
                    onCheckedChange={(c) => setFilters(f => ({ ...f, dogs_allowed: c }))}
                  />
                  <Label className="text-gray-400 text-sm">Chiens permis</Label>
                </div>

                <Button
                  variant="outline"
                  onClick={() => setFilters({
                    game_species: '', region: '', hunting_zone: '', terrain_type: '',
                    min_price: '', max_price: '', min_surface: '', max_surface: '',
                    has_blinds: false, has_cameras: false, dogs_allowed: false
                  })}
                >
                  Réinitialiser
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Listings Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
          </div>
        ) : listings.length === 0 ? (
          <div className="text-center py-20">
            <Trees className="h-16 w-16 mx-auto text-gray-600 mb-4" />
            <h3 className="text-xl text-white mb-2">Aucune terre trouvée</h3>
            <p className="text-gray-400">Essayez de modifier vos filtres</p>
          </div>
        ) : (
          <div className={viewMode === 'grid' 
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' 
            : 'space-y-4'
          }>
            {listings.map(listing => (
              <LandCard
                key={listing.id}
                listing={listing}
                onView={() => handleViewListing(listing)}
                formatPrice={formatPrice}
                viewMode={viewMode}
              />
            ))}
          </div>
        )}

        {/* ============================================ */}
        {/* MODALS */}
        {/* ============================================ */}

        {/* Auth Modal */}
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          type={authType}
          mode={authMode}
          setMode={setAuthMode}
          onLogin={(creds) => handleLogin(authType, creds)}
          onRegister={(data) => handleRegister(authType, data)}
        />

        {/* Create Listing Modal */}
        <CreateListingModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          config={config}
          form={newListing}
          setForm={setNewListing}
          onSubmit={handleCreateListing}
        />

        {/* Listing Detail Modal */}
        <ListingDetailModal
          isOpen={showDetailModal}
          onClose={() => setShowDetailModal(false)}
          listing={selectedListing}
          formatPrice={formatPrice}
          onRent={() => { setShowDetailModal(false); setShowAgreementModal(true); }}
          onPurchase={handlePurchase}
          renterAuth={renterAuth}
        />

        {/* Agreement Modal */}
        <AgreementModal
          isOpen={showAgreementModal}
          onClose={() => setShowAgreementModal(false)}
          listing={selectedListing}
          form={agreementForm}
          setForm={setAgreementForm}
          onSubmit={handleCreateAgreement}
          pricing={config?.pricing}
        />

        {/* Contract Modal */}
        <ContractModal
          isOpen={showContractModal}
          onClose={() => setShowContractModal(false)}
          contractText={contractText}
        />

        {/* Pricing Modal */}
        <PricingModal
          isOpen={showPricingModal}
          onClose={() => setShowPricingModal(false)}
          pricing={config?.pricing}
          onPurchase={handlePurchase}
        />

        {/* My Listings Modal */}
        <MyListingsModal
          isOpen={showMyListings}
          onClose={() => setShowMyListings(false)}
          listings={myListings}
          formatPrice={formatPrice}
          onPurchase={handlePurchase}
        />
      </div>
    </div>
  );
};

// ============================================
// LAND CARD COMPONENT
// ============================================

const LandCard = ({ listing, onView, formatPrice, viewMode }) => {
  const speciesIcons = listing.game_species?.map(s => SPECIES_CONFIG[s]?.icon || '🎯').join(' ');

  if (viewMode === 'list') {
    return (
      <Card className="bg-card border-border hover:border-[#f5a623]/50 transition-all cursor-pointer" onClick={onView}>
        <CardContent className="p-4 flex items-center gap-4">
          <div className="w-32 h-24 bg-gray-800 rounded-lg flex items-center justify-center text-3xl flex-shrink-0">
            {listing.photos?.[0] ? (
              <img src={listing.photos[0]} alt={listing.title || "Photo du terrain de chasse"} className="w-full h-full object-cover rounded-lg" />
            ) : speciesIcons}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-white font-semibold truncate flex items-center gap-2">
                  {listing.is_featured && <Star className="h-4 w-4 text-yellow-400 fill-yellow-400" />}
                  {listing.title}
                </h3>
                <p className="text-gray-400 text-sm flex items-center gap-1 mt-1">
                  <MapPin className="h-3 w-3" />
                  {config?.regions?.[listing.region]?.name || listing.region}
                  {listing.hunting_zones?.length > 0 && ` • Zone ${listing.hunting_zones[0]}`}
                </p>
              </div>
              <div className="text-right">
                <div className="text-[#f5a623] font-bold">{formatPrice(listing.price_per_day)}/jour</div>
                <div className="text-gray-500 text-xs">{listing.surface_acres} acres</div>
              </div>
            </div>
            <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
              <span className="text-lg">{speciesIcons}</span>
              <span><Eye className="h-3 w-3 inline" /> {listing.views}</span>
              {listing.has_blinds && <span>🏠 Caches</span>}
              {listing.has_cameras && <span>📷 Caméras</span>}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-card border-border hover:border-[#f5a623]/50 transition-all overflow-hidden cursor-pointer group" onClick={onView}>
      {/* Image */}
      <div className="relative h-48 bg-gray-800 flex items-center justify-center">
        {listing.photos?.[0] ? (
          <img src={listing.photos[0]} alt={listing.title || "Photo du terrain de chasse"} className="w-full h-full object-cover" />
        ) : (
          <div className="text-5xl">{speciesIcons || '🌲'}</div>
        )}
        
        {/* Badges */}
        <div className="absolute top-2 left-2 flex flex-col gap-1">
          {listing.is_featured && (
            <Badge className="bg-yellow-500/90 text-black text-[10px]">
              <Star className="h-3 w-3 mr-1 fill-black" /> VEDETTE
            </Badge>
          )}
          {listing.is_premium && (
            <Badge className="bg-purple-500/90 text-white text-[10px]">
              <Crown className="h-3 w-3 mr-1" /> PREMIUM
            </Badge>
          )}
          {listing.vip_only && (
            <Badge className="bg-amber-500/90 text-black text-[10px]">
              <Lock className="h-3 w-3 mr-1" /> VIP
            </Badge>
          )}
        </div>

        {/* Species badges */}
        <div className="absolute bottom-2 left-2 flex gap-1">
          {listing.game_species?.slice(0, 3).map((species, i) => (
            <Badge key={i} className={`${SPECIES_CONFIG[species]?.color || 'bg-gray-500/50'} text-[10px]`}>
              {SPECIES_CONFIG[species]?.icon} {SPECIES_CONFIG[species]?.name}
            </Badge>
          ))}
        </div>
      </div>

      <CardContent className="p-4">
        <h3 className="text-white font-semibold truncate group-hover:text-[#f5a623] transition-colors">
          {listing.title}
        </h3>
        
        <p className="text-gray-400 text-sm flex items-center gap-1 mt-1">
          <MapPin className="h-3 w-3" />
          {listing.region} {listing.hunting_zones?.length > 0 && `• Zone ${listing.hunting_zones[0]}`}
        </p>

        <div className="flex items-center justify-between mt-3 pt-3 border-t border-border">
          <div>
            <span className="text-[#f5a623] font-bold text-lg">{formatPrice(listing.price_per_day)}</span>
            <span className="text-gray-500 text-sm">/jour</span>
          </div>
          <div className="text-right text-sm">
            <div className="text-gray-400">{listing.surface_acres} acres</div>
            <div className="text-gray-500 text-xs flex items-center gap-2">
              <span><Eye className="h-3 w-3 inline" /> {listing.views}</span>
            </div>
          </div>
        </div>

        {/* Amenities */}
        <div className="flex gap-2 mt-3 text-xs text-gray-500">
          {listing.has_blinds && <span className="flex items-center gap-1">🏠 Caches</span>}
          {listing.has_cameras && <span className="flex items-center gap-1">📷 Caméras</span>}
          {listing.dogs_allowed && <span className="flex items-center gap-1">🐕 Chiens</span>}
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================
// AUTH MODAL
// ============================================

const AuthModal = ({ isOpen, onClose, type, mode, setMode, onLogin, onRegister }) => {
  const [form, setForm] = useState({
    name: '', email: '', phone: '', password: '', hunting_license: '', address: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (mode === 'login') {
        await onLogin({ email: form.email, password: form.password });
      } else {
        await onRegister(form);
      }
    } finally {
      setLoading(false);
    }
  };

  const isOwner = type === 'owner';

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-card border-border max-w-md">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            {isOwner ? <Building2 className="h-5 w-5 text-amber-400" /> : <Target className="h-5 w-5 text-green-400" />}
            {isOwner ? 'Espace Propriétaire' : 'Espace Chasseur'}
          </DialogTitle>
          <DialogDescription>
            {mode === 'login' ? 'Connectez-vous à votre compte' : 'Créez votre compte'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <>
              <div>
                <Label>Nom complet</Label>
                <Input
                  value={form.name}
                  onChange={(e) => setForm(f => ({ ...f, name: e.target.value }))}
                  required
                  className="bg-gray-900 border-gray-700"
                />
              </div>
              <div>
                <Label>Téléphone</Label>
                <Input
                  value={form.phone}
                  onChange={(e) => setForm(f => ({ ...f, phone: e.target.value }))}
                  required
                  className="bg-gray-900 border-gray-700"
                />
              </div>
              {!isOwner && (
                <div>
                  <Label>Numéro de permis de chasse (optionnel)</Label>
                  <Input
                    value={form.hunting_license}
                    onChange={(e) => setForm(f => ({ ...f, hunting_license: e.target.value }))}
                    className="bg-gray-900 border-gray-700"
                  />
                </div>
              )}
              {isOwner && (
                <div>
                  <Label>Adresse (optionnel)</Label>
                  <Input
                    value={form.address}
                    onChange={(e) => setForm(f => ({ ...f, address: e.target.value }))}
                    className="bg-gray-900 border-gray-700"
                  />
                </div>
              )}
            </>
          )}
          
          <div>
            <Label>Courriel</Label>
            <Input
              type="email"
              value={form.email}
              onChange={(e) => setForm(f => ({ ...f, email: e.target.value }))}
              required
              className="bg-gray-900 border-gray-700"
            />
          </div>
          <div>
            <Label>Mot de passe</Label>
            <Input
              type="password"
              value={form.password}
              onChange={(e) => setForm(f => ({ ...f, password: e.target.value }))}
              required
              className="bg-gray-900 border-gray-700"
            />
          </div>

          <Button type="submit" className="w-full bg-[#f5a623] hover:bg-[#d4891c] text-black" disabled={loading}>
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : (mode === 'login' ? 'Connexion' : 'Inscription')}
          </Button>
        </form>

        <div className="text-center text-sm text-gray-400">
          {mode === 'login' ? (
            <p>Pas de compte? <button onClick={() => setMode('register')} className="text-[#f5a623] hover:underline">Inscrivez-vous</button></p>
          ) : (
            <p>Déjà un compte? <button onClick={() => setMode('login')} className="text-[#f5a623] hover:underline">Connectez-vous</button></p>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

// ============================================
// CREATE LISTING MODAL
// ============================================

const CreateListingModal = ({ isOpen, onClose, config, form, setForm, onSubmit }) => {
  const [step, setStep] = useState(1);

  const toggleArrayItem = (field, item) => {
    setForm(f => ({
      ...f,
      [field]: f[field].includes(item) 
        ? f[field].filter(i => i !== item)
        : [...f[field], item]
    }));
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-card border-border max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <Plus className="h-5 w-5 text-[#f5a623]" />
            Publier une terre
          </DialogTitle>
          <DialogDescription>
            Étape {step}/3 - {step === 1 ? 'Informations générales' : step === 2 ? 'Détails du terrain' : 'Tarification'}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {step === 1 && (
            <>
              <div>
                <Label>Titre de l'annonce *</Label>
                <Input
                  value={form.title}
                  onChange={(e) => setForm(f => ({ ...f, title: e.target.value }))}
                  placeholder="Ex: 200 acres pour orignal - Laurentides"
                  className="bg-gray-900 border-gray-700"
                />
              </div>
              <div>
                <Label>Description *</Label>
                <Textarea
                  value={form.description}
                  onChange={(e) => setForm(f => ({ ...f, description: e.target.value }))}
                  placeholder="Décrivez votre terrain, son historique de chasse, les installations..."
                  className="bg-gray-900 border-gray-700 min-h-[120px]"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Région *</Label>
                  <Select value={form.region} onValueChange={(v) => setForm(f => ({ ...f, region: v }))}>
                    <SelectTrigger className="bg-gray-900 border-gray-700">
                      <SelectValue placeholder="Sélectionner" />
                    </SelectTrigger>
                    <SelectContent>
                      {config?.regions && Object.entries(config.regions).map(([key, region]) => (
                        <SelectItem key={key} value={key}>{region.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>MRC / Ville</Label>
                  <Input
                    value={form.city}
                    onChange={(e) => setForm(f => ({ ...f, city: e.target.value }))}
                    className="bg-gray-900 border-gray-700"
                  />
                </div>
              </div>
              <div>
                <Label>Zones de chasse</Label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {config?.hunting_zones?.map(zone => (
                    <Button
                      key={zone}
                      type="button"
                      variant={form.hunting_zones.includes(zone) ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => toggleArrayItem('hunting_zones', zone)}
                      className={form.hunting_zones.includes(zone) ? 'bg-[#f5a623] text-black' : ''}
                    >
                      Zone {zone}
                    </Button>
                  ))}
                </div>
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Superficie (acres) *</Label>
                  <Input
                    type="number"
                    value={form.surface_acres}
                    onChange={(e) => setForm(f => ({ ...f, surface_acres: e.target.value }))}
                    className="bg-gray-900 border-gray-700"
                  />
                </div>
                <div>
                  <Label>Nb max de chasseurs</Label>
                  <Input
                    type="number"
                    value={form.max_hunters}
                    onChange={(e) => setForm(f => ({ ...f, max_hunters: e.target.value }))}
                    className="bg-gray-900 border-gray-700"
                  />
                </div>
              </div>

              <div>
                <Label>Gibier présent *</Label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {Object.entries(SPECIES_CONFIG).map(([key, cfg]) => (
                    <Button
                      key={key}
                      type="button"
                      variant={form.game_species.includes(key) ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => toggleArrayItem('game_species', key)}
                      className={form.game_species.includes(key) ? `${cfg.color}` : ''}
                    >
                      {cfg.icon} {cfg.name}
                    </Button>
                  ))}
                </div>
              </div>

              <div>
                <Label>Type de terrain</Label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {config?.terrain_types?.map(t => (
                    <Button
                      key={t.id}
                      type="button"
                      variant={form.terrain_types.includes(t.id) ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => toggleArrayItem('terrain_types', t.id)}
                    >
                      {t.name}
                    </Button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-2">
                  <Checkbox checked={form.has_blinds} onCheckedChange={(c) => setForm(f => ({ ...f, has_blinds: c }))} />
                  <Label>Caches disponibles</Label>
                </div>
                <div className="flex items-center gap-2">
                  <Checkbox checked={form.has_salt_licks} onCheckedChange={(c) => setForm(f => ({ ...f, has_salt_licks: c }))} />
                  <Label>Salines installées</Label>
                </div>
                <div className="flex items-center gap-2">
                  <Checkbox checked={form.has_cameras} onCheckedChange={(c) => setForm(f => ({ ...f, has_cameras: c }))} />
                  <Label>Caméras de trail</Label>
                </div>
                <div className="flex items-center gap-2">
                  <Checkbox checked={form.dogs_allowed} onCheckedChange={(c) => setForm(f => ({ ...f, dogs_allowed: c }))} />
                  <Label>Chiens permis</Label>
                </div>
                <div className="flex items-center gap-2">
                  <Checkbox checked={form.camping_allowed} onCheckedChange={(c) => setForm(f => ({ ...f, camping_allowed: c }))} />
                  <Label>Camping permis</Label>
                </div>
                <div className="flex items-center gap-2">
                  <Checkbox checked={form.fire_allowed} onCheckedChange={(c) => setForm(f => ({ ...f, fire_allowed: c }))} />
                  <Label>Feu permis</Label>
                </div>
              </div>

              <div>
                <Label>Historique de gibier</Label>
                <Textarea
                  value={form.game_history}
                  onChange={(e) => setForm(f => ({ ...f, game_history: e.target.value }))}
                  placeholder="Décrivez les prises des dernières années..."
                  className="bg-gray-900 border-gray-700"
                />
              </div>
            </>
          )}

          {step === 3 && (
            <>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label>Prix / jour ($)</Label>
                  <Input
                    type="number"
                    value={form.price_per_day}
                    onChange={(e) => setForm(f => ({ ...f, price_per_day: e.target.value }))}
                    className="bg-gray-900 border-gray-700"
                  />
                </div>
                <div>
                  <Label>Prix / semaine ($)</Label>
                  <Input
                    type="number"
                    value={form.price_per_week}
                    onChange={(e) => setForm(f => ({ ...f, price_per_week: e.target.value }))}
                    className="bg-gray-900 border-gray-700"
                  />
                </div>
                <div>
                  <Label>Prix / saison ($)</Label>
                  <Input
                    type="number"
                    value={form.price_per_season}
                    onChange={(e) => setForm(f => ({ ...f, price_per_season: e.target.value }))}
                    className="bg-gray-900 border-gray-700"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Disponible du</Label>
                  <Input
                    type="date"
                    value={form.available_from}
                    onChange={(e) => setForm(f => ({ ...f, available_from: e.target.value }))}
                    className="bg-gray-900 border-gray-700"
                  />
                </div>
                <div>
                  <Label>Disponible jusqu'au</Label>
                  <Input
                    type="date"
                    value={form.available_to}
                    onChange={(e) => setForm(f => ({ ...f, available_to: e.target.value }))}
                    className="bg-gray-900 border-gray-700"
                  />
                </div>
              </div>

              <div>
                <Label>Règles du propriétaire</Label>
                <Textarea
                  value={form.owner_rules}
                  onChange={(e) => setForm(f => ({ ...f, owner_rules: e.target.value }))}
                  placeholder="Vos règles spécifiques pour les locataires..."
                  className="bg-gray-900 border-gray-700"
                />
              </div>

              <Card className="bg-yellow-500/10 border-yellow-500/30">
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="h-5 w-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-yellow-400 font-medium">Frais de publication</p>
                      <p className="text-gray-400 text-sm mt-1">
                        Des frais de {config?.pricing?.listing_basic?.price || 4.99}$ s'appliquent pour activer votre annonce.
                        Vous serez redirigé vers le paiement après la création.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>

        <DialogFooter className="flex justify-between">
          {step > 1 ? (
            <Button variant="outline" onClick={() => setStep(s => s - 1)}>Précédent</Button>
          ) : (
            <div />
          )}
          {step < 3 ? (
            <Button onClick={() => setStep(s => s + 1)} className="bg-[#f5a623] text-black">Suivant</Button>
          ) : (
            <Button onClick={onSubmit} className="bg-[#f5a623] text-black">
              <CreditCard className="h-4 w-4 mr-2" />
              Publier (4,99$)
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// ============================================
// LISTING DETAIL MODAL
// ============================================

const ListingDetailModal = ({ isOpen, onClose, listing, formatPrice, onRent, onPurchase, renterAuth }) => {
  if (!listing) return null;
  
  const land = listing.listing;
  const owner = listing.owner;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-card border-border max-w-3xl max-h-[90vh] overflow-y-auto">
        <div className="space-y-6">
          {/* Header */}
          <div>
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-2xl font-bold text-white">{land.title}</h2>
                <p className="text-gray-400 flex items-center gap-2 mt-1">
                  <MapPin className="h-4 w-4" />
                  {land.region} {land.city && `• ${land.city}`}
                  {land.hunting_zones?.length > 0 && ` • Zone ${land.hunting_zones.join(', ')}`}
                </p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-[#f5a623]">{formatPrice(land.price_per_day)}<span className="text-base font-normal text-gray-400">/jour</span></div>
                {land.price_per_week && <div className="text-sm text-gray-400">{formatPrice(land.price_per_week)}/semaine</div>}
                {land.price_per_season && <div className="text-sm text-gray-400">{formatPrice(land.price_per_season)}/saison</div>}
              </div>
            </div>

            {/* Badges */}
            <div className="flex flex-wrap gap-2 mt-4">
              {land.game_species?.map(species => (
                <Badge key={species} className={SPECIES_CONFIG[species]?.color}>
                  {SPECIES_CONFIG[species]?.icon} {SPECIES_CONFIG[species]?.name}
                </Badge>
              ))}
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="bg-gray-900/50">
              <CardContent className="p-3 text-center">
                <Trees className="h-5 w-5 mx-auto text-green-400 mb-1" />
                <div className="text-white font-semibold">{land.surface_acres} acres</div>
                <div className="text-gray-500 text-xs">Superficie</div>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50">
              <CardContent className="p-3 text-center">
                <Users className="h-5 w-5 mx-auto text-blue-400 mb-1" />
                <div className="text-white font-semibold">{land.max_hunters}</div>
                <div className="text-gray-500 text-xs">Chasseurs max</div>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50">
              <CardContent className="p-3 text-center">
                <Eye className="h-5 w-5 mx-auto text-purple-400 mb-1" />
                <div className="text-white font-semibold">{land.views}</div>
                <div className="text-gray-500 text-xs">Vues</div>
              </CardContent>
            </Card>
            <Card className="bg-gray-900/50">
              <CardContent className="p-3 text-center">
                <Star className="h-5 w-5 mx-auto text-yellow-400 mb-1" />
                <div className="text-white font-semibold">{owner?.rating || 5.0}</div>
                <div className="text-gray-500 text-xs">Note proprio</div>
              </CardContent>
            </Card>
          </div>

          {/* Description */}
          <div>
            <h3 className="text-white font-semibold mb-2">Description</h3>
            <p className="text-gray-400 whitespace-pre-line">{land.description}</p>
          </div>

          {/* Amenities */}
          <div>
            <h3 className="text-white font-semibold mb-2">Équipements & règles</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              <div className={`flex items-center gap-2 p-2 rounded ${land.has_blinds ? 'bg-green-500/10 text-green-400' : 'bg-gray-800 text-gray-500'}`}>
                {land.has_blinds ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />} Caches
              </div>
              <div className={`flex items-center gap-2 p-2 rounded ${land.has_salt_licks ? 'bg-green-500/10 text-green-400' : 'bg-gray-800 text-gray-500'}`}>
                {land.has_salt_licks ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />} Salines
              </div>
              <div className={`flex items-center gap-2 p-2 rounded ${land.has_cameras ? 'bg-green-500/10 text-green-400' : 'bg-gray-800 text-gray-500'}`}>
                {land.has_cameras ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />} Caméras
              </div>
              <div className={`flex items-center gap-2 p-2 rounded ${land.dogs_allowed ? 'bg-green-500/10 text-green-400' : 'bg-gray-800 text-gray-500'}`}>
                {land.dogs_allowed ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />} Chiens
              </div>
              <div className={`flex items-center gap-2 p-2 rounded ${land.camping_allowed ? 'bg-green-500/10 text-green-400' : 'bg-gray-800 text-gray-500'}`}>
                {land.camping_allowed ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />} Camping
              </div>
              <div className={`flex items-center gap-2 p-2 rounded ${land.fire_allowed ? 'bg-green-500/10 text-green-400' : 'bg-gray-800 text-gray-500'}`}>
                {land.fire_allowed ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />} Feu
              </div>
            </div>
          </div>

          {/* Owner Rules */}
          {land.owner_rules && (
            <div>
              <h3 className="text-white font-semibold mb-2">Règles du propriétaire</h3>
              <Card className="bg-gray-900/50 border-border">
                <CardContent className="p-4">
                  <p className="text-gray-400 whitespace-pre-line">{land.owner_rules}</p>
                </CardContent>
              </Card>
            </div>
          )}

          {/* CTA */}
          <div className="flex gap-3">
            <Button onClick={onRent} className="flex-1 bg-[#f5a623] hover:bg-[#d4891c] text-black font-semibold">
              <FileText className="h-4 w-4 mr-2" />
              Demander une location
            </Button>
            <Button variant="outline" onClick={() => onPurchase('ai_analysis', land.id)}>
              <Sparkles className="h-4 w-4 mr-2" />
              Analyse IA (19,99$)
            </Button>
          </div>

          {/* Disclaimer */}
          <p className="text-xs text-gray-500 text-center">
            ⚠️ La plateforme met en relation propriétaires et chasseurs. Elle n'est pas partie aux ententes 
            et n'assume aucune responsabilité.
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// ============================================
// AGREEMENT MODAL
// ============================================

const AgreementModal = ({ isOpen, onClose, listing, form, setForm, onSubmit, pricing }) => {
  if (!listing) return null;
  
  const land = listing.listing;
  const ownerFee = pricing?.owner_fee_percent?.price || 10;
  const renterFee = pricing?.renter_fee_percent?.price || 10;
  const platformFee = form.total_price ? (parseFloat(form.total_price) * (renterFee / 100)).toFixed(2) : 0;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-card border-border max-w-lg">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <FileText className="h-5 w-5 text-[#f5a623]" />
            Demande de location
          </DialogTitle>
          <DialogDescription>
            {land.title}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Date de début *</Label>
              <Input
                type="date"
                value={form.start_date}
                onChange={(e) => setForm(f => ({ ...f, start_date: e.target.value }))}
                className="bg-gray-900 border-gray-700"
              />
            </div>
            <div>
              <Label>Date de fin *</Label>
              <Input
                type="date"
                value={form.end_date}
                onChange={(e) => setForm(f => ({ ...f, end_date: e.target.value }))}
                className="bg-gray-900 border-gray-700"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Prix total convenu ($) *</Label>
              <Input
                type="number"
                value={form.total_price}
                onChange={(e) => setForm(f => ({ ...f, total_price: e.target.value }))}
                placeholder={land.price_per_day?.toString()}
                className="bg-gray-900 border-gray-700"
              />
            </div>
            <div>
              <Label>Nombre de chasseurs</Label>
              <Input
                type="number"
                value={form.num_hunters}
                onChange={(e) => setForm(f => ({ ...f, num_hunters: e.target.value }))}
                max={land.max_hunters}
                className="bg-gray-900 border-gray-700"
              />
            </div>
          </div>

          <div>
            <Label>Conditions spéciales (optionnel)</Label>
            <Textarea
              value={form.special_conditions}
              onChange={(e) => setForm(f => ({ ...f, special_conditions: e.target.value }))}
              placeholder="Ajoutez des conditions particulières..."
              className="bg-gray-900 border-gray-700"
            />
          </div>

          {/* Fee Breakdown */}
          <Card className="bg-gray-900/50 border-border">
            <CardContent className="p-4">
              <h4 className="text-white font-medium mb-3">Récapitulatif</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between text-gray-400">
                  <span>Prix convenu</span>
                  <span>{form.total_price || 0} $</span>
                </div>
                <div className="flex justify-between text-gray-400">
                  <span>Frais de mise en relation ({renterFee}%)</span>
                  <span>{platformFee} $</span>
                </div>
                <div className="flex justify-between text-white font-semibold pt-2 border-t border-border">
                  <span>Total à payer (locataire)</span>
                  <span>{(parseFloat(form.total_price || 0) + parseFloat(platformFee)).toFixed(2)} $</span>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-3">
                Le paiement au propriétaire ({form.total_price}$) est effectué directement entre vous.
                La plateforme ne gère pas cette transaction.
              </p>
            </CardContent>
          </Card>

          {/* Legal Notice */}
          <Card className="bg-amber-500/10 border-amber-500/30">
            <CardContent className="p-3">
              <p className="text-amber-400 text-sm flex items-start gap-2">
                <Shield className="h-4 w-4 mt-0.5 flex-shrink-0" />
                Une entente légale sera générée. Les deux parties devront accepter les conditions.
                La plateforme n'est pas partie au contrat.
              </p>
            </CardContent>
          </Card>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Annuler</Button>
          <Button onClick={onSubmit} className="bg-[#f5a623] text-black">
            <Send className="h-4 w-4 mr-2" />
            Envoyer la demande
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// ============================================
// CONTRACT MODAL
// ============================================

const ContractModal = ({ isOpen, onClose, contractText }) => {
  const handleDownload = () => {
    const blob = new Blob([contractText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'entente-location-chasse.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-card border-border max-w-2xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <FileText className="h-5 w-5 text-[#f5a623]" />
            Entente de location
          </DialogTitle>
        </DialogHeader>

        <div className="bg-gray-900 rounded-lg p-4 max-h-[60vh] overflow-y-auto">
          <pre className="text-gray-300 text-sm whitespace-pre-wrap font-mono">{contractText}</pre>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleDownload}>
            <Download className="h-4 w-4 mr-2" />
            Télécharger
          </Button>
          <Button onClick={onClose} className="bg-[#f5a623] text-black">Fermer</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// ============================================
// PRICING MODAL
// ============================================

const PricingModal = ({ isOpen, onClose, pricing, onPurchase }) => {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-card border-border max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-[#f5a623]" />
            Tarifs & Abonnements
          </DialogTitle>
          <DialogDescription>
            Toutes nos options pour propriétaires et chasseurs
          </DialogDescription>
        </DialogHeader>

        <Tabs defaultValue="owners" className="w-full">
          <TabsList className="w-full grid grid-cols-3">
            <TabsTrigger value="owners">Propriétaires</TabsTrigger>
            <TabsTrigger value="hunters">Chasseurs</TabsTrigger>
            <TabsTrigger value="extras">Options</TabsTrigger>
          </TabsList>

          {/* Owners Tab */}
          <TabsContent value="owners" className="space-y-4">
            <h3 className="text-white font-semibold mt-4">Publication & Visibilité</h3>
            <div className="grid gap-3">
              {['listing_basic', 'listing_featured_7', 'listing_featured_30', 'listing_auto_bump'].map(key => {
                const item = pricing?.[key];
                if (!item) return null;
                return (
                  <Card key={key} className="bg-gray-900/50 border-border">
                    <CardContent className="p-4 flex items-center justify-between">
                      <div>
                        <h4 className="text-white font-medium">{item.name}</h4>
                        <p className="text-gray-400 text-sm">{item.description}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-[#f5a623] font-bold">{item.price} $</div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            <Card className="bg-blue-500/10 border-blue-500/30">
              <CardContent className="p-4">
                <p className="text-blue-400 text-sm">
                  <strong>Frais de mise en relation:</strong> {pricing?.owner_fee_percent?.price || 10}% 
                  du montant de la location (prélevé uniquement lors d'une transaction confirmée)
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Hunters Tab */}
          <TabsContent value="hunters" className="space-y-4">
            <h3 className="text-white font-semibold mt-4">Abonnements Chasseur</h3>
            <div className="grid md:grid-cols-3 gap-4">
              {['renter_basic', 'renter_pro', 'renter_vip'].map(key => {
                const item = pricing?.[key];
                if (!item) return null;
                const isVip = key === 'renter_vip';
                return (
                  <Card key={key} className={`border-border ${isVip ? 'border-amber-500 bg-amber-500/5' : 'bg-gray-900/50'}`}>
                    {isVip && (
                      <div className="bg-amber-500 text-black text-xs font-bold text-center py-1">
                        ⭐ POPULAIRE
                      </div>
                    )}
                    <CardContent className="p-4 text-center">
                      <Crown className={`h-8 w-8 mx-auto mb-2 ${isVip ? 'text-amber-400' : 'text-purple-400'}`} />
                      <h4 className="text-white font-bold">{item.name}</h4>
                      <div className="text-2xl font-bold text-[#f5a623] my-2">
                        {item.price} $<span className="text-sm text-gray-400">/mois</span>
                      </div>
                      <p className="text-gray-400 text-sm mb-4">{item.description}</p>
                      <Button 
                        onClick={() => onPurchase(key)}
                        className={isVip ? 'w-full bg-amber-500 text-black' : 'w-full'}
                      >
                        S'abonner
                      </Button>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            <Card className="bg-blue-500/10 border-blue-500/30">
              <CardContent className="p-4">
                <p className="text-blue-400 text-sm">
                  <strong>Frais de mise en relation:</strong> {pricing?.renter_fee_percent?.price || 10}% 
                  du montant de la location (prélevé uniquement lors d'une transaction confirmée)
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Extras Tab */}
          <TabsContent value="extras" className="space-y-4">
            <h3 className="text-white font-semibold mt-4">Options à la carte</h3>
            <div className="grid md:grid-cols-2 gap-3">
              {['boost_24h', 'badge_premium', 'send_to_hunters', 'generate_agreement', 'ai_analysis'].map(key => {
                const item = pricing?.[key];
                if (!item) return null;
                return (
                  <Card key={key} className="bg-gray-900/50 border-border">
                    <CardContent className="p-4 flex items-center justify-between">
                      <div>
                        <h4 className="text-white font-medium">{item.name}</h4>
                        <p className="text-gray-400 text-sm">{item.description}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-[#f5a623] font-bold">{item.price} $</div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </TabsContent>
        </Tabs>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Fermer</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// ============================================
// MY LISTINGS MODAL
// ============================================

const MyListingsModal = ({ isOpen, onClose, listings, formatPrice, onPurchase }) => {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-card border-border max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <Package className="h-5 w-5 text-amber-400" />
            Mes terres
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-3">
          {listings.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <Trees className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p>Vous n'avez pas encore de terres publiées</p>
            </div>
          ) : (
            listings.map(listing => (
              <Card key={listing.id} className="bg-gray-900/50 border-border">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-white font-medium flex items-center gap-2">
                        {listing.title}
                        {listing.status === 'pending' && <Badge className="bg-yellow-500/20 text-yellow-400">En attente</Badge>}
                        {listing.status === 'active' && <Badge className="bg-green-500/20 text-green-400">Active</Badge>}
                        {listing.is_featured && <Badge className="bg-purple-500/20 text-purple-400">Vedette</Badge>}
                      </h4>
                      <p className="text-gray-400 text-sm">{formatPrice(listing.price_per_day)}/jour • {listing.surface_acres} acres</p>
                      <p className="text-gray-500 text-xs mt-1">
                        <Eye className="h-3 w-3 inline mr-1" />{listing.views} vues
                      </p>
                    </div>
                    <div className="flex flex-col gap-2">
                      {listing.status === 'pending' && !listing.listing_fee_paid && (
                        <Button size="sm" onClick={() => onPurchase('listing_basic', listing.id)} className="bg-[#f5a623] text-black">
                          Activer (4,99$)
                        </Button>
                      )}
                      {listing.status === 'active' && !listing.is_featured && (
                        <Button size="sm" variant="outline" onClick={() => onPurchase('listing_featured_7', listing.id)}>
                          <Star className="h-3 w-3 mr-1" /> Vedette
                        </Button>
                      )}
                      {listing.status === 'active' && !listing.auto_bump_enabled && (
                        <Button size="sm" variant="outline" onClick={() => onPurchase('listing_auto_bump', listing.id)}>
                          <Zap className="h-3 w-3 mr-1" /> Auto-bump
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Fermer</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default LandsRental;
