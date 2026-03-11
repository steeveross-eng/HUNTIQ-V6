/**
 * Hunt Marketplace - Main Component
 * Marketplace pour acheter, vendre ou louer des articles de chasse
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
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
import { useLanguage } from '@/contexts/LanguageContext';
import { 
  Search, 
  Plus, 
  Filter, 
  MapPin, 
  DollarSign,
  Heart,
  Eye,
  MessageCircle,
  Star,
  Clock,
  ChevronRight,
  ChevronDown,
  User,
  LogIn,
  LogOut,
  Settings,
  Package,
  ShoppingBag,
  Tag,
  Truck,
  Home,
  Trees,
  Target,
  Camera,
  Loader2,
  X,
  Edit,
  Trash2,
  RefreshCw,
  Crown,
  Sparkles,
  TrendingUp,
  Mail,
  Phone,
  CheckCircle,
  AlertCircle,
  Grid,
  List,
  Zap,
  CreditCard,
  ArrowLeft
} from 'lucide-react';
import { toast } from 'sonner';
import { 
  PackagesDisplay, 
  PaymentStatusChecker, 
  ProBadge, 
  FeaturedBadge,
  UpgradePromptModal,
  QuickBoostButton 
} from './MarketplacePayments';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// ============================================
// AUTH CONTEXT & STORAGE
// ============================================

const getStoredAuth = () => {
  try {
    const stored = localStorage.getItem('marketplace_auth');
    return stored ? JSON.parse(stored) : null;
  } catch {
    return null;
  }
};

const setStoredAuth = (auth) => {
  if (auth) {
    localStorage.setItem('marketplace_auth', JSON.stringify(auth));
  } else {
    localStorage.removeItem('marketplace_auth');
  }
};

// ============================================
// MAIN MARKETPLACE COMPONENT
// ============================================

const HuntMarketplace = () => {
  const navigate = useNavigate();
  
  // Auth state
  const [auth, setAuth] = useState(getStoredAuth());
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login'); // login or register
  
  // Listings state
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);
  const [listingTypes, setListingTypes] = useState([]);
  const [species, setSpecies] = useState([]);
  const [regions, setRegions] = useState([]);
  const [conditions, setConditions] = useState([]);
  
  // Filters state
  const [filters, setFilters] = useState({
    category: '',
    listing_type: '',
    species: '',
    min_price: '',
    max_price: '',
    region: '',
    condition: '',
    search: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [sortBy, setSortBy] = useState('recent');
  const [viewMode, setViewMode] = useState('grid'); // grid or list
  
  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalListings, setTotalListings] = useState(0);
  
  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showListingModal, setShowListingModal] = useState(false);
  const [selectedListing, setSelectedListing] = useState(null);
  const [showMyListings, setShowMyListings] = useState(false);
  const [myListings, setMyListings] = useState([]);
  
  // Stats
  const [stats, setStats] = useState({ total_listings: 0, total_sellers: 0 });

  // Payment state
  const [paymentSessionId, setPaymentSessionId] = useState(null);
  const [showPaymentResult, setShowPaymentResult] = useState(false);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [upgradeReason, setUpgradeReason] = useState('boost_listing');
  const [showPackagesModal, setShowPackagesModal] = useState(false);

  // ============================================
  // CHECK PAYMENT RETURN
  // ============================================

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    const payment = urlParams.get('payment');
    
    if (sessionId && payment === 'success') {
      setPaymentSessionId(sessionId);
      setShowPaymentResult(true);
      // Clean URL
      window.history.replaceState({}, '', window.location.pathname);
    } else if (payment === 'cancelled') {
      toast.info('Paiement annulé');
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);

  // ============================================
  // LOAD DATA
  // ============================================

  useEffect(() => {
    loadCategories();
    loadStats();
  }, []);

  useEffect(() => {
    loadListings();
  }, [filters, sortBy, page]);

  const loadCategories = async () => {
    try {
      const response = await axios.get(`${API}/marketplace/categories`);
      setCategories(response.data.categories || []);
      setListingTypes(response.data.listing_types || []);
      setSpecies(response.data.species || []);
      setRegions(response.data.regions || []);
      setConditions(response.data.conditions || []);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API}/marketplace/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const loadListings = async () => {
    setLoading(true);
    try {
      const params = { page, limit: 20, sort_by: sortBy };
      if (filters.category) params.category = filters.category;
      if (filters.listing_type) params.listing_type = filters.listing_type;
      if (filters.species) params.species = filters.species;
      if (filters.region) params.region = filters.region;
      if (filters.condition) params.condition = filters.condition;
      if (filters.min_price) params.min_price = parseFloat(filters.min_price);
      if (filters.max_price) params.max_price = parseFloat(filters.max_price);
      if (filters.search) params.search = filters.search;
      
      const response = await axios.get(`${API}/marketplace/listings`, { params });
      setListings(response.data.listings || []);
      setTotalPages(response.data.pages || 1);
      setTotalListings(response.data.total || 0);
    } catch (error) {
      console.error('Error loading listings:', error);
      toast.error('Erreur lors du chargement des annonces');
    } finally {
      setLoading(false);
    }
  };

  const loadMyListings = async () => {
    if (!auth?.token) return;
    try {
      const response = await axios.get(`${API}/marketplace/my-listings?token=${auth.token}`);
      setMyListings(response.data.listings || []);
    } catch (error) {
      console.error('Error loading my listings:', error);
    }
  };

  // ============================================
  // AUTH HANDLERS
  // ============================================

  const handleLogin = async (email, password) => {
    try {
      const response = await axios.post(`${API}/marketplace/auth/login`, { email, password });
      const authData = { token: response.data.token, seller: response.data.seller };
      setAuth(authData);
      setStoredAuth(authData);
      setShowAuthModal(false);
      toast.success(`Bienvenue ${response.data.seller.name}!`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur de connexion');
    }
  };

  const handleRegister = async (data) => {
    try {
      const response = await axios.post(`${API}/marketplace/auth/register`, data);
      const authData = { token: response.data.token, seller: response.data.seller };
      setAuth(authData);
      setStoredAuth(authData);
      setShowAuthModal(false);
      toast.success('Compte créé avec succès! Vous avez 3 annonces gratuites.');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'inscription');
    }
  };

  const handleLogout = () => {
    setAuth(null);
    setStoredAuth(null);
    setMyListings([]);
    toast.success('Déconnexion réussie');
  };

  // ============================================
  // LISTING HANDLERS
  // ============================================

  const handleCreateListing = async (data) => {
    if (!auth?.token) {
      setShowAuthModal(true);
      return;
    }
    try {
      const response = await axios.post(`${API}/marketplace/listings?token=${auth.token}`, data);
      toast.success('Annonce créée avec succès!');
      setShowCreateModal(false);
      loadListings();
      loadMyListings();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la création');
    }
  };

  const handleDeleteListing = async (listingId) => {
    if (!auth?.token) return;
    if (!confirm('Supprimer cette annonce?')) return;
    try {
      await axios.delete(`${API}/marketplace/listings/${listingId}?token=${auth.token}`);
      toast.success('Annonce supprimée');
      loadMyListings();
      loadListings();
    } catch (error) {
      toast.error('Erreur lors de la suppression');
    }
  };

  const handleViewListing = async (listing) => {
    try {
      const response = await axios.get(`${API}/marketplace/listings/${listing.id}`);
      setSelectedListing(response.data);
      setShowListingModal(true);
    } catch (error) {
      toast.error('Erreur lors du chargement');
    }
  };

  const handleToggleFavorite = async (listingId) => {
    if (!auth?.token) {
      setShowAuthModal(true);
      return;
    }
    try {
      const response = await axios.post(`${API}/marketplace/listings/${listingId}/favorite?token=${auth.token}`);
      toast.success(response.data.favorited ? '❤️ Ajouté aux favoris' : 'Retiré des favoris');
    } catch (error) {
      toast.error('Erreur');
    }
  };

  const resetFilters = () => {
    setFilters({
      category: '',
      listing_type: '',
      species: '',
      min_price: '',
      max_price: '',
      region: '',
      condition: '',
      search: ''
    });
    setPage(1);
  };

  // ============================================
  // RENDER HELPERS
  // ============================================

  const getCategoryIcon = (categoryId) => {
    const cat = categories.find(c => c.id === categoryId);
    return cat?.icon || '📦';
  };

  const getCategoryName = (categoryId) => {
    const cat = categories.find(c => c.id === categoryId);
    return cat?.name || categoryId;
  };

  const getListingTypeBadge = (type) => {
    const colors = {
      'a-vendre': 'bg-green-500/20 text-green-400 border-green-500',
      'a-louer': 'bg-blue-500/20 text-blue-400 border-blue-500',
      'forfait': 'bg-purple-500/20 text-purple-400 border-purple-500',
      'terre-a-louer': 'bg-amber-500/20 text-amber-400 border-amber-500',
      'service': 'bg-cyan-500/20 text-cyan-400 border-cyan-500'
    };
    const names = {
      'a-vendre': 'À vendre',
      'a-louer': 'À louer',
      'forfait': 'Forfait',
      'terre-a-louer': 'Terre à louer',
      'service': 'Service'
    };
    return { color: colors[type] || 'bg-gray-500/20 text-gray-400', name: names[type] || type };
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('fr-CA', { style: 'currency', currency: 'CAD' }).format(price);
  };

  // ============================================
  // RENDER
  // ============================================

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="bg-gradient-to-r from-[#1a1a2e] to-[#16213e] border-b border-border sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Back Button */}
            <Button 
              variant="ghost" 
              onClick={() => navigate('/')}
              className="text-gray-400 hover:text-white hover:bg-gray-800/50"
              data-testid="back-button-marketplace"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Retour
            </Button>

            <div className="flex items-center gap-3">
              <div className="bg-[#f5a623] p-2.5 rounded-xl">
                <ShoppingBag className="h-6 w-6 text-black" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Hunt Marketplace</h1>
                <p className="text-gray-400 text-xs">{stats.total_listings} annonces • {stats.total_sellers} vendeurs</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {auth ? (
                <>
                  <Button
                    onClick={() => setShowPackagesModal(true)}
                    variant="outline"
                    className="text-sm text-purple-400 border-purple-500/50 hover:bg-purple-500/10"
                  >
                    <Crown className="h-4 w-4 mr-2" />
                    {auth.seller?.is_pro ? 'Gérer PRO' : 'Passer PRO'}
                  </Button>
                  <Button
                    onClick={() => { loadMyListings(); setShowMyListings(true); }}
                    variant="outline"
                    className="text-sm"
                  >
                    <Package className="h-4 w-4 mr-2" />
                    Mes annonces
                  </Button>
                  <Button
                    onClick={() => {
                      // Check listing limit
                      if (!auth.seller?.is_pro && auth.seller?.free_listings_remaining <= 0) {
                        setUpgradeReason('listings_limit');
                        setShowUpgradeModal(true);
                        return;
                      }
                      setShowCreateModal(true);
                    }}
                    className="bg-[#f5a623] hover:bg-[#d4891c] text-black font-semibold"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Publier
                  </Button>
                  <div className="flex items-center gap-2 pl-3 border-l border-border">
                    <div className="text-right">
                      <div className="text-white text-sm font-medium flex items-center gap-1">
                        {auth.seller?.name}
                        {auth.seller?.is_pro && <ProBadge seller={auth.seller} />}
                      </div>
                      <div className="text-gray-500 text-xs">
                        {auth.seller?.is_pro ? 'Annonces illimitées' : `${auth.seller?.free_listings_remaining || 0} gratuites`}
                      </div>
                    </div>
                    <Button variant="ghost" size="icon" onClick={handleLogout}>
                      <LogOut className="h-4 w-4" />
                    </Button>
                  </div>
                </>
              ) : (
                <Button
                  onClick={() => setShowAuthModal(true)}
                  className="bg-[#f5a623] hover:bg-[#d4891c] text-black font-semibold"
                >
                  <LogIn className="h-4 w-4 mr-2" />
                  Connexion / Inscription
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Search & Filters Bar */}
      <div className="bg-card border-b border-border sticky top-[73px] z-40">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex flex-wrap gap-3 items-center">
            {/* Search */}
            <div className="flex-1 min-w-[250px] relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
              <Input
                placeholder="Rechercher équipement, véhicules, terres..."
                value={filters.search}
                onChange={(e) => setFilters(f => ({ ...f, search: e.target.value }))}
                onKeyDown={(e) => e.key === 'Enter' && loadListings()}
                className="pl-10 bg-background"
              />
            </div>

            {/* Quick Filters */}
            <Select value={filters.category || 'all'} onValueChange={(v) => setFilters(f => ({ ...f, category: v === 'all' ? '' : v }))}>
              <SelectTrigger className="w-[180px] bg-background">
                <SelectValue placeholder="Catégorie" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Toutes catégories</SelectItem>
                {categories.map(cat => (
                  <SelectItem key={cat.id} value={cat.id}>
                    {cat.icon} {cat.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={filters.listing_type || 'all'} onValueChange={(v) => setFilters(f => ({ ...f, listing_type: v === 'all' ? '' : v }))}>
              <SelectTrigger className="w-[150px] bg-background">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous types</SelectItem>
                {listingTypes.map(t => (
                  <SelectItem key={t.id} value={t.id}>{t.icon} {t.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
              className={showFilters ? 'bg-[#f5a623]/20 border-[#f5a623]' : ''}
            >
              <Filter className="h-4 w-4 mr-2" />
              Filtres
              {Object.values(filters).filter(v => v).length > 0 && (
                <Badge className="ml-2 bg-[#f5a623] text-black">{Object.values(filters).filter(v => v).length}</Badge>
              )}
            </Button>

            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-[140px] bg-background">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="recent">Plus récentes</SelectItem>
                <SelectItem value="price_asc">Prix croissant</SelectItem>
                <SelectItem value="price_desc">Prix décroissant</SelectItem>
                <SelectItem value="popular">Populaires</SelectItem>
              </SelectContent>
            </Select>

            <div className="flex border border-border rounded-lg overflow-hidden">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setViewMode('grid')}
                className={viewMode === 'grid' ? 'bg-[#f5a623]/20' : ''}
              >
                <Grid className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setViewMode('list')}
                className={viewMode === 'list' ? 'bg-[#f5a623]/20' : ''}
              >
                <List className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Extended Filters */}
          {showFilters && (
            <div className="mt-3 pt-3 border-t border-border grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
              <Select value={filters.species || 'all'} onValueChange={(v) => setFilters(f => ({ ...f, species: v === 'all' ? '' : v }))}>
                <SelectTrigger className="bg-background">
                  <SelectValue placeholder="Espèce" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Toutes espèces</SelectItem>
                  {species.map(s => (
                    <SelectItem key={s.id} value={s.id}>{s.emoji} {s.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={filters.region || 'all'} onValueChange={(v) => setFilters(f => ({ ...f, region: v === 'all' ? '' : v }))}>
                <SelectTrigger className="bg-background">
                  <SelectValue placeholder="Région" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Toutes régions</SelectItem>
                  {regions.map(r => (
                    <SelectItem key={r} value={r}>{r}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={filters.condition || 'all'} onValueChange={(v) => setFilters(f => ({ ...f, condition: v === 'all' ? '' : v }))}>
                <SelectTrigger className="bg-background">
                  <SelectValue placeholder="État" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tous états</SelectItem>
                  {conditions.map(c => (
                    <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Input
                placeholder="Prix min"
                type="number"
                value={filters.min_price}
                onChange={(e) => setFilters(f => ({ ...f, min_price: e.target.value }))}
                className="bg-background"
              />

              <Input
                placeholder="Prix max"
                type="number"
                value={filters.max_price}
                onChange={(e) => setFilters(f => ({ ...f, max_price: e.target.value }))}
                className="bg-background"
              />

              <Button variant="outline" onClick={resetFilters}>
                <RefreshCw className="h-4 w-4 mr-2" />
                {t('common_refresh')}
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Results Info */}
        <div className="flex items-center justify-between mb-4">
          <p className="text-gray-400 text-sm">
            {totalListings} annonce{totalListings !== 1 ? 's' : ''} trouvée{totalListings !== 1 ? 's' : ''}
          </p>
        </div>

        {/* Listings Grid/List */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
          </div>
        ) : listings.length === 0 ? (
          <Card className="bg-card border-border">
            <CardContent className="p-12 text-center">
              <ShoppingBag className="h-16 w-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-white text-lg font-semibold mb-2">Aucune annonce trouvée</h3>
              <p className="text-gray-400 mb-4">Modifiez vos filtres ou soyez le premier à publier!</p>
              <Button onClick={() => auth ? setShowCreateModal(true) : setShowAuthModal(true)} className="bg-[#f5a623] text-black">
                <Plus className="h-4 w-4 mr-2" />
                Publier une annonce
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4' : 'space-y-3'}>
            {listings.map((listing) => (
              <ListingCard
                key={listing.id}
                listing={listing}
                viewMode={viewMode}
                onView={() => handleViewListing(listing)}
                onFavorite={() => handleToggleFavorite(listing.id)}
                getCategoryIcon={getCategoryIcon}
                getListingTypeBadge={getListingTypeBadge}
                formatPrice={formatPrice}
              />
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-center gap-2 mt-8">
            <Button
              variant="outline"
              disabled={page === 1}
              onClick={() => setPage(p => p - 1)}
            >
              Précédent
            </Button>
            <span className="flex items-center px-4 text-gray-400">
              Page {page} sur {totalPages}
            </span>
            <Button
              variant="outline"
              disabled={page === totalPages}
              onClick={() => setPage(p => p + 1)}
            >
              Suivant
            </Button>
          </div>
        )}
      </div>

      {/* Auth Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        mode={authMode}
        setMode={setAuthMode}
        onLogin={handleLogin}
        onRegister={handleRegister}
        regions={regions}
      />

      {/* Create Listing Modal */}
      <CreateListingModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onCreate={handleCreateListing}
        categories={categories}
        listingTypes={listingTypes}
        species={species}
        regions={regions}
        conditions={conditions}
        auth={auth}
      />

      {/* Listing Detail Modal */}
      <ListingDetailModal
        isOpen={showListingModal}
        onClose={() => setShowListingModal(false)}
        listing={selectedListing}
        onFavorite={() => handleToggleFavorite(selectedListing?.id)}
        auth={auth}
        getCategoryName={getCategoryName}
        getListingTypeBadge={getListingTypeBadge}
        formatPrice={formatPrice}
      />

      {/* My Listings Modal */}
      <MyListingsModal
        isOpen={showMyListings}
        onClose={() => setShowMyListings(false)}
        listings={myListings}
        onDelete={handleDeleteListing}
        onRefresh={loadMyListings}
        auth={auth}
        formatPrice={formatPrice}
        getCategoryIcon={getCategoryIcon}
      />

      {/* Payment Result Modal */}
      <Dialog open={showPaymentResult} onOpenChange={setShowPaymentResult}>
        <DialogContent className="bg-card border-border max-w-md">
          <PaymentStatusChecker 
            sessionId={paymentSessionId} 
            onComplete={(data) => {
              // Refresh auth to get updated seller info
              setTimeout(() => {
                loadStats();
                if (auth?.token) loadMyListings();
              }, 1000);
            }}
          />
          <DialogFooter>
            <Button onClick={() => setShowPaymentResult(false)} className="w-full">
              Continuer sur le Marketplace
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Upgrade Modal */}
      <UpgradePromptModal
        isOpen={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
        auth={auth}
        reason={upgradeReason}
      />

      {/* Packages Modal */}
      <Dialog open={showPackagesModal} onOpenChange={setShowPackagesModal}>
        <DialogContent className="bg-card border-border max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Crown className="h-5 w-5 text-purple-400" />
              Forfaits & Abonnements
            </DialogTitle>
            <DialogDescription>
              Boostez vos ventes avec nos options premium
            </DialogDescription>
          </DialogHeader>
          <PackagesDisplay auth={auth} />
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPackagesModal(false)}>Fermer</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// ============================================
// LISTING CARD COMPONENT
// ============================================

const ListingCard = ({ listing, viewMode, onView, onFavorite, getCategoryIcon, getListingTypeBadge, formatPrice }) => {
  const typeBadge = getListingTypeBadge(listing.listing_type);
  
  if (viewMode === 'list') {
    return (
      <Card className="bg-card border-border hover:border-[#f5a623]/50 transition-all cursor-pointer" onClick={onView}>
        <CardContent className="p-4 flex gap-4">
          {/* Image */}
          <div className="w-32 h-24 bg-gray-800 rounded-lg overflow-hidden flex-shrink-0">
            {listing.photos?.[0] ? (
              <img src={listing.photos[0]} alt={listing.title} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-3xl">
                {getCategoryIcon(listing.category)}
              </div>
            )}
          </div>
          
          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div>
                <h3 className="text-white font-semibold truncate">{listing.title}</h3>
                <div className="flex items-center gap-2 mt-1">
                  <Badge className={`text-[10px] ${typeBadge.color}`}>{typeBadge.name}</Badge>
                  {listing.is_featured && <Badge className="bg-yellow-500/20 text-yellow-400 text-[10px]">⭐ Vedette</Badge>}
                  {listing.seller_is_pro && <Badge className="bg-purple-500/20 text-purple-400 text-[10px]">PRO</Badge>}
                </div>
              </div>
              <div className="text-right">
                <div className="text-[#f5a623] font-bold text-lg">{formatPrice(listing.price)}</div>
                {listing.price_negotiable && <span className="text-gray-500 text-xs">Négociable</span>}
              </div>
            </div>
            <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
              <span className="flex items-center gap-1"><MapPin className="h-3 w-3" />{listing.location}</span>
              <span className="flex items-center gap-1"><Eye className="h-3 w-3" />{listing.views}</span>
              <span className="flex items-center gap-1"><Heart className="h-3 w-3" />{listing.favorites}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card className="bg-card border-border hover:border-[#f5a623]/50 transition-all cursor-pointer group overflow-hidden" onClick={onView}>
      {/* Image */}
      <div className="relative h-48 bg-gray-800 overflow-hidden">
        {listing.photos?.[0] ? (
          <img src={listing.photos[0]} alt={listing.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-5xl">
            {getCategoryIcon(listing.category)}
          </div>
        )}
        {/* Badges */}
        <div className="absolute top-2 left-2 flex flex-wrap gap-1">
          <Badge className={`text-[10px] ${typeBadge.color}`}>{typeBadge.name}</Badge>
          {listing.is_featured && <Badge className="bg-yellow-500/20 text-yellow-400 text-[10px]">⭐</Badge>}
        </div>
        {/* Favorite Button */}
        <Button
          variant="ghost"
          size="icon"
          className="absolute top-2 right-2 bg-black/50 hover:bg-black/70"
          onClick={(e) => { e.stopPropagation(); onFavorite(); }}
        >
          <Heart className="h-4 w-4" />
        </Button>
        {/* Price */}
        <div className="absolute bottom-2 right-2 bg-black/80 px-2 py-1 rounded">
          <span className="text-[#f5a623] font-bold">{formatPrice(listing.price)}</span>
        </div>
      </div>
      
      <CardContent className="p-3">
        <h3 className="text-white font-semibold truncate mb-1">{listing.title}</h3>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span className="flex items-center gap-1"><MapPin className="h-3 w-3" />{listing.location}</span>
        </div>
        <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            {listing.seller_is_pro && <Crown className="h-3 w-3 text-purple-400" />}
            {listing.seller_name}
          </span>
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1"><Eye className="h-3 w-3" />{listing.views}</span>
            <span className="flex items-center gap-1"><Heart className="h-3 w-3" />{listing.favorites}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================
// AUTH MODAL COMPONENT
// ============================================

const AuthModal = ({ isOpen, onClose, mode, setMode, onLogin, onRegister, regions }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [location, setLocation] = useState('');
  const [isBusiness, setIsBusiness] = useState(false);
  const [businessName, setBusinessName] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (mode === 'login') {
        await onLogin(email, password);
      } else {
        await onRegister({ email, password, name, phone, location, is_business: isBusiness, business_name: businessName });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-card border-border max-w-md">
        <DialogHeader>
          <DialogTitle className="text-white text-xl">
            {mode === 'login' ? 'Connexion' : 'Créer un compte'}
          </DialogTitle>
          <DialogDescription>
            {mode === 'login' ? 'Accédez à votre espace vendeur' : 'Inscrivez-vous pour publier vos annonces'}
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <>
              <div>
                <Label>Nom complet *</Label>
                <Input value={name} onChange={(e) => setName(e.target.value)} required className="bg-background" />
              </div>
              <div>
                <Label>Téléphone</Label>
                <Input value={phone} onChange={(e) => setPhone(e.target.value)} className="bg-background" />
              </div>
              <div>
                <Label>Région</Label>
                <Select value={location} onValueChange={setLocation}>
                  <SelectTrigger className="bg-background">
                    <SelectValue placeholder="Sélectionner" />
                  </SelectTrigger>
                  <SelectContent>
                    {regions.map(r => <SelectItem key={r} value={r}>{r}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox checked={isBusiness} onCheckedChange={setIsBusiness} />
                <Label className="cursor-pointer">Je suis une entreprise/pourvoirie</Label>
              </div>
              {isBusiness && (
                <div>
                  <Label>Nom de l'entreprise</Label>
                  <Input value={businessName} onChange={(e) => setBusinessName(e.target.value)} className="bg-background" />
                </div>
              )}
            </>
          )}
          
          <div>
            <Label>Email *</Label>
            <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="bg-background" />
          </div>
          <div>
            <Label>Mot de passe *</Label>
            <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} className="bg-background" />
          </div>
          
          <Button type="submit" disabled={loading} className="w-full bg-[#f5a623] hover:bg-[#d4891c] text-black font-semibold">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : mode === 'login' ? 'Se connecter' : 'Créer mon compte'}
          </Button>
        </form>
        
        <div className="text-center text-sm text-gray-400">
          {mode === 'login' ? (
            <>Pas encore de compte? <button onClick={() => setMode('register')} className="text-[#f5a623] hover:underline">Inscrivez-vous</button></>
          ) : (
            <>Déjà inscrit? <button onClick={() => setMode('login')} className="text-[#f5a623] hover:underline">Connectez-vous</button></>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

// ============================================
// CREATE LISTING MODAL
// ============================================

const CreateListingModal = ({ isOpen, onClose, onCreate, categories, listingTypes, species, regions, conditions, auth }) => {
  const [form, setForm] = useState({
    title: '',
    description: '',
    price: '',
    price_negotiable: false,
    category: '',
    listing_type: 'a-vendre',
    condition: '',
    target_species: [],
    location: '',
    region: '',
    photos: [],
    contact_phone: '',
    contact_email: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title || !form.description || !form.price || !form.category || !form.location) {
      toast.error('Veuillez remplir tous les champs obligatoires');
      return;
    }
    setLoading(true);
    try {
      await onCreate({ ...form, price: parseFloat(form.price) });
      setForm({
        title: '', description: '', price: '', price_negotiable: false, category: '',
        listing_type: 'a-vendre', condition: '', target_species: [], location: '',
        region: '', photos: [], contact_phone: '', contact_email: ''
      });
    } finally {
      setLoading(false);
    }
  };

  const toggleSpecies = (speciesId) => {
    setForm(f => ({
      ...f,
      target_species: f.target_species.includes(speciesId)
        ? f.target_species.filter(s => s !== speciesId)
        : [...f.target_species, speciesId]
    }));
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-card border-border max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-white text-xl flex items-center gap-2">
            <Plus className="h-5 w-5 text-[#f5a623]" />
            Publier une annonce
          </DialogTitle>
          <DialogDescription>
            {auth?.seller?.is_pro ? 'Annonces illimitées (PRO)' : `${auth?.seller?.free_listings_remaining || 0} annonces gratuites restantes`}
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <Label>Titre *</Label>
              <Input 
                value={form.title} 
                onChange={(e) => setForm(f => ({ ...f, title: e.target.value }))}
                placeholder="Ex: Carabine Remington 30-06 comme neuve"
                className="bg-background"
                maxLength={100}
              />
            </div>
            
            <div>
              <Label>Catégorie *</Label>
              <Select value={form.category} onValueChange={(v) => setForm(f => ({ ...f, category: v }))}>
                <SelectTrigger className="bg-background">
                  <SelectValue placeholder="Sélectionner" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map(c => <SelectItem key={c.id} value={c.id}>{c.icon} {c.name}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>Type d'offre *</Label>
              <Select value={form.listing_type} onValueChange={(v) => setForm(f => ({ ...f, listing_type: v }))}>
                <SelectTrigger className="bg-background">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {listingTypes.map(t => <SelectItem key={t.id} value={t.id}>{t.icon} {t.name}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label>Prix ($) *</Label>
              <Input 
                type="number" 
                value={form.price}
                onChange={(e) => setForm(f => ({ ...f, price: e.target.value }))}
                placeholder="0.00"
                className="bg-background"
              />
            </div>
            
            <div>
              <Label>État</Label>
              <Select value={form.condition} onValueChange={(v) => setForm(f => ({ ...f, condition: v }))}>
                <SelectTrigger className="bg-background">
                  <SelectValue placeholder="Sélectionner" />
                </SelectTrigger>
                <SelectContent>
                  {conditions.map(c => <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>

            <div className="col-span-2 flex items-center gap-2">
              <Checkbox 
                checked={form.price_negotiable} 
                onCheckedChange={(v) => setForm(f => ({ ...f, price_negotiable: v }))}
              />
              <Label className="cursor-pointer">Prix négociable</Label>
            </div>
            
            <div className="col-span-2">
              <Label>Description *</Label>
              <Textarea 
                value={form.description}
                onChange={(e) => setForm(f => ({ ...f, description: e.target.value }))}
                placeholder="Décrivez votre article en détail..."
                className="bg-background min-h-[100px]"
                maxLength={5000}
              />
            </div>
            
            <div>
              <Label>Localisation *</Label>
              <Input 
                value={form.location}
                onChange={(e) => setForm(f => ({ ...f, location: e.target.value }))}
                placeholder="Ville ou code postal"
                className="bg-background"
              />
            </div>
            
            <div>
              <Label>Région</Label>
              <Select value={form.region} onValueChange={(v) => setForm(f => ({ ...f, region: v }))}>
                <SelectTrigger className="bg-background">
                  <SelectValue placeholder="Sélectionner" />
                </SelectTrigger>
                <SelectContent>
                  {regions.map(r => <SelectItem key={r} value={r}>{r}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            
            <div className="col-span-2">
              <Label>Espèces ciblées</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {species.map(s => (
                  <Badge
                    key={s.id}
                    className={`cursor-pointer transition-all ${
                      form.target_species.includes(s.id)
                        ? 'bg-[#f5a623] text-black'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                    onClick={() => toggleSpecies(s.id)}
                  >
                    {s.emoji} {s.name}
                  </Badge>
                ))}
              </div>
            </div>
            
            <div>
              <Label>Téléphone de contact</Label>
              <Input 
                value={form.contact_phone}
                onChange={(e) => setForm(f => ({ ...f, contact_phone: e.target.value }))}
                placeholder="514-555-1234"
                className="bg-background"
              />
            </div>
            
            <div>
              <Label>Email de contact</Label>
              <Input 
                type="email"
                value={form.contact_email}
                onChange={(e) => setForm(f => ({ ...f, contact_email: e.target.value }))}
                placeholder="votre@email.com"
                className="bg-background"
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>Annuler</Button>
            <Button type="submit" disabled={loading} className="bg-[#f5a623] hover:bg-[#d4891c] text-black font-semibold">
              {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Plus className="h-4 w-4 mr-2" />}
              Publier l'annonce
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

// ============================================
// LISTING DETAIL MODAL
// ============================================

const ListingDetailModal = ({ isOpen, onClose, listing, onFavorite, auth, getCategoryName, getListingTypeBadge, formatPrice }) => {
  if (!listing) return null;
  const typeBadge = getListingTypeBadge(listing.listing_type);
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-card border-border max-w-3xl max-h-[90vh] overflow-y-auto">
        <div className="space-y-4">
          {/* Image */}
          <div className="h-64 bg-gray-800 rounded-lg overflow-hidden">
            {listing.photos?.[0] ? (
              <img src={listing.photos[0]} alt={listing.title} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-6xl">📦</div>
            )}
          </div>
          
          {/* Header */}
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Badge className={typeBadge.color}>{typeBadge.name}</Badge>
                {listing.is_featured && <Badge className="bg-yellow-500/20 text-yellow-400">⭐ En vedette</Badge>}
                {listing.seller_is_pro && <Badge className="bg-purple-500/20 text-purple-400">PRO</Badge>}
              </div>
              <h2 className="text-2xl font-bold text-white">{listing.title}</h2>
              <p className="text-gray-400 mt-1">{getCategoryName(listing.category)}</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-[#f5a623]">{formatPrice(listing.price)}</div>
              {listing.price_negotiable && <span className="text-gray-500 text-sm">Prix négociable</span>}
            </div>
          </div>
          
          {/* Stats */}
          <div className="flex items-center gap-6 text-sm text-gray-400">
            <span className="flex items-center gap-1"><Eye className="h-4 w-4" /> {listing.views} vues</span>
            <span className="flex items-center gap-1"><Heart className="h-4 w-4" /> {listing.favorites} favoris</span>
            <span className="flex items-center gap-1"><MapPin className="h-4 w-4" /> {listing.location}</span>
            <span className="flex items-center gap-1"><Clock className="h-4 w-4" /> {new Date(listing.created_at).toLocaleDateString('fr-CA')}</span>
          </div>
          
          {/* Description */}
          <div>
            <h3 className="text-white font-semibold mb-2">Description</h3>
            <p className="text-gray-300 whitespace-pre-wrap">{listing.description}</p>
          </div>
          
          {/* Species */}
          {listing.target_species?.length > 0 && (
            <div>
              <h3 className="text-white font-semibold mb-2">Espèces ciblées</h3>
              <div className="flex flex-wrap gap-2">
                {listing.target_species.map(s => (
                  <Badge key={s} variant="outline">{s}</Badge>
                ))}
              </div>
            </div>
          )}
          
          {/* Seller Info */}
          <Card className="bg-gray-900/50 border-border">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-gray-700 flex items-center justify-center">
                    <User className="h-6 w-6 text-gray-400" />
                  </div>
                  <div>
                    <div className="text-white font-semibold flex items-center gap-2">
                      {listing.seller_name}
                      {listing.seller_is_pro && <Crown className="h-4 w-4 text-purple-400" />}
                    </div>
                    {listing.seller_rating > 0 && (
                      <div className="flex items-center gap-1 text-yellow-400 text-sm">
                        <Star className="h-3 w-3 fill-yellow-400" /> {listing.seller_rating}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    <MessageCircle className="h-4 w-4 mr-2" /> Message
                  </Button>
                  <Button onClick={onFavorite} variant="outline" size="sm">
                    <Heart className="h-4 w-4 mr-2" /> Favori
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// ============================================
// MY LISTINGS MODAL
// ============================================

const MyListingsModal = ({ isOpen, onClose, listings, onDelete, onRefresh, auth, formatPrice, getCategoryIcon }) => {
  const [showBoostModal, setShowBoostModal] = useState(false);
  const [selectedListingForBoost, setSelectedListingForBoost] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedListingForEdit, setSelectedListingForEdit] = useState(null);

  const handleBoost = (listing) => {
    setSelectedListingForBoost(listing);
    setShowBoostModal(true);
  };

  const isExpiringSoon = (listing) => {
    if (!listing.expires_at) return false;
    const expiresAt = new Date(listing.expires_at);
    const now = new Date();
    const daysUntilExpiry = (expiresAt - now) / (1000 * 60 * 60 * 24);
    return daysUntilExpiry < 7 && daysUntilExpiry > 0;
  };

  const isExpired = (listing) => {
    if (!listing.expires_at) return false;
    return new Date(listing.expires_at) < new Date();
  };

  return (
    <>
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="bg-card border-border max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-white text-xl flex items-center gap-2">
              <Package className="h-5 w-5 text-[#f5a623]" />
              Mes annonces
            </DialogTitle>
            <DialogDescription>
              {auth?.seller?.is_pro ? 'Annonces illimitées (PRO)' : `${auth?.seller?.free_listings_remaining || 0} annonces gratuites restantes`}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-3">
            {listings.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <Package className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>Vous n'avez pas encore d'annonces</p>
              </div>
            ) : (
              listings.map(listing => (
                <Card key={listing.id} className={`bg-gray-900/50 border-border ${isExpired(listing) ? 'border-red-500/50' : isExpiringSoon(listing) ? 'border-yellow-500/50' : ''}`}>
                  <CardContent className="p-3">
                    <div className="flex items-center gap-3">
                      <div className="w-16 h-16 bg-gray-800 rounded-lg flex items-center justify-center text-2xl flex-shrink-0 relative">
                        {listing.photos?.[0] ? (
                          <img src={listing.photos[0]} alt={listing.title || "Photo de l'annonce"} className="w-full h-full object-cover rounded-lg" />
                        ) : getCategoryIcon(listing.category)}
                        {listing.is_featured && (
                          <div className="absolute -top-1 -right-1 w-5 h-5 bg-yellow-500 rounded-full flex items-center justify-center">
                            <Star className="h-3 w-3 text-black fill-black" />
                          </div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="text-white font-medium truncate flex items-center gap-2">
                          {listing.title}
                          {listing.is_featured && <Badge className="bg-yellow-500/20 text-yellow-400 text-[10px]">Vedette</Badge>}
                          {listing.auto_bump_enabled && <Badge className="bg-green-500/20 text-green-400 text-[10px]">Auto-bump</Badge>}
                        </h4>
                        <div className="flex items-center gap-3 text-xs text-gray-400 mt-1">
                          <span className="text-[#f5a623] font-semibold">{formatPrice(listing.price)}</span>
                          <span><Eye className="h-3 w-3 inline mr-1" />{listing.views}</span>
                          <span><Heart className="h-3 w-3 inline mr-1" />{listing.favorites}</span>
                        </div>
                        {/* Expiry warning */}
                        {isExpired(listing) && (
                          <div className="flex items-center gap-1 text-red-400 text-xs mt-1">
                            <AlertCircle className="h-3 w-3" />
                            Annonce expirée - Renouvelez-la!
                          </div>
                        )}
                        {isExpiringSoon(listing) && !isExpired(listing) && (
                          <div className="flex items-center gap-1 text-yellow-400 text-xs mt-1">
                            <Clock className="h-3 w-3" />
                            Expire bientôt - Renouvelez-la!
                          </div>
                        )}
                      </div>
                      <div className="flex flex-col gap-1">
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="h-8 text-xs text-yellow-400 border-yellow-500/50 hover:bg-yellow-500/10"
                          onClick={() => handleBoost(listing)}
                        >
                          <Zap className="h-3 w-3 mr-1" />
                          Booster
                        </Button>
                        <div className="flex gap-1">
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon" className="h-8 w-8 text-red-400 hover:text-red-300" onClick={() => onDelete(listing.id)}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={onRefresh}>
              <RefreshCw className="h-4 w-4 mr-2" /> Rafraîchir
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Boost Modal */}
      <Dialog open={showBoostModal} onOpenChange={setShowBoostModal}>
        <DialogContent className="bg-card border-border max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Zap className="h-5 w-5 text-yellow-400" />
              Booster "{selectedListingForBoost?.title}"
            </DialogTitle>
            <DialogDescription>
              Choisissez une option pour augmenter la visibilité de votre annonce
            </DialogDescription>
          </DialogHeader>
          <PackagesDisplay auth={auth} listingId={selectedListingForBoost?.id} />
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowBoostModal(false)}>Annuler</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default HuntMarketplace;
