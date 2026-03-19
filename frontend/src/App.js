import { useEffect, useState, useCallback, lazy, Suspense } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Link, useLocation, useNavigate, Navigate } from "react-router-dom";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";

// BLOC 2 OPTIMIZATION: Critical path components (loaded synchronously)
import CookieConsent from "@/components/CookieConsent";
import SEOHead from "@/components/SEOHead";
import { AuthProvider, UserMenu, useAuth } from "@/components/GlobalAuth";
import { OfflineIndicator } from "@/components/OfflineIndicator";
import { LanguageProvider, useLanguage, LanguageSwitcher } from "@/contexts/LanguageContext";
import BionicLogo, { BionicLogoGlobal } from "@/components/BionicLogo";
import ScrollNavigator from "@/components/ScrollNavigator";
import { NotificationProvider } from "@/modules/notifications";
// PHASE F: Centre de notifications push temps réel
import AlertNotificationCenter from "@/components/AlertNotificationCenter";

// BLOC 2 OPTIMIZATION: Lazy-loaded components (non-critical path)
const AnalyzerModule = lazy(() => import("@/components/AnalyzerModule"));
const TerritoryMap = lazy(() => import("@/components/TerritoryMap"));
const HuntMarketplace = lazy(() => import("@/components/HuntMarketplace"));
const ContentDepot = lazy(() => import("@/components/ContentDepot"));
const SiteAccessControl = lazy(() => import("@/components/SiteAccessControl"));
const MaintenancePage = lazy(() => import("@/components/MaintenancePage"));
const LandsRental = lazy(() => import("@/components/LandsRental"));
const LandsPricingAdmin = lazy(() => import("@/components/LandsPricingAdmin"));
const NetworkingHub = lazy(() => import("@/components/NetworkingHub"));
const NetworkingAdmin = lazy(() => import("@/components/NetworkingAdmin"));
const NotificationCenter = lazy(() => import("@/components/NotificationCenter"));
const EmailAdmin = lazy(() => import("@/components/EmailAdmin"));
const FeatureControlsAdmin = lazy(() => import("@/components/FeatureControlsAdmin"));
const ResetPasswordPage = lazy(() => import("@/components/ResetPasswordPage"));
const BecomePartner = lazy(() => import("@/components/BecomePartner"));
const PartnerDashboard = lazy(() => import("@/components/PartnerDashboard"));
const MonTerritoireBionic = lazy(() => import("@/components/territoire/MonTerritoireBionic"));
const ProductDiscoveryAdmin = lazy(() => import("@/components/ProductDiscoveryAdmin"));
const ReferralModule = lazy(() => import("@/components/ReferralModule"));
const ReferralAdminPanel = lazy(() => import("@/components/ReferralAdminPanel"));
const DynamicReferralWidget = lazy(() => import("@/components/DynamicReferralWidget"));
const GoogleOAuthCallback = lazy(() => import("@/components/GoogleOAuthCallback"));

// BLOC 2 OPTIMIZATION: Lazy-loaded pages
const AdminPage = lazy(() => import("@/pages/AdminPage"));
const MonTerritoireBionicPage = lazy(() => import("@/pages/MonTerritoireBionicPage"));
const TripsPage = lazy(() => import("@/pages/TripsPage"));
const ShopPage = lazy(() => import("@/pages").then(m => ({ default: m.ShopPage })));
const ComparePage = lazy(() => import("@/pages").then(m => ({ default: m.ComparePage })));
const DashboardPage = lazy(() => import("@/pages/DashboardPage"));
const BusinessPage = lazy(() => import("@/pages/BusinessPage"));
const PlanMaitrePage = lazy(() => import("@/pages/intelligence/PlanMaitrePage"));
const AnalyticsPage = lazy(() => import("@/pages/intelligence/AnalyticsPage"));
const MapPage = lazy(() => import("@/pages/MapPage"));
const ForecastPage = lazy(() => import("@/pages/intelligence/ForecastPage"));
const AdminGeoPage = lazy(() => import("@/pages/AdminGeoPage"));
const OnboardingPage = lazy(() => import("@/pages/OnboardingPage"));
const PricingPage = lazy(() => import("@/pages/PricingPage"));
const PaymentSuccessPage = lazy(() => import("@/pages/PaymentSuccessPage"));
const PaymentCancelPage = lazy(() => import("@/pages/PaymentCancelPage"));
const AdminPremiumPage = lazy(() => import("@/pages/AdminPremiumPage"));
const MarketingCalendarPage = lazy(() => import("@/pages/MarketingCalendarPage"));
const HuntingLicensePage = lazy(() => import("@/pages/HuntingLicensePage"));
const BionicAnalysisDemoPage = lazy(() => import("@/pages/BionicAnalysisDemoPage"));
// PHASE F: Interface d'observations terrain
const FieldObservationForm = lazy(() => import("@/pages/FieldObservationForm"));
// CALIBRATION MASTER: Dashboard de calibration
const CalibrationDashboard = lazy(() => import("@/pages/CalibrationDashboard"));
const ReportsPage = lazy(() => import("@/pages/ReportsPage"));
const SpeciesComparisonPage = lazy(() => import("@/pages/SpeciesComparisonPage"));
const AdminHotspotsPage = lazy(() => import("@/ui/administration/admin_hotspots/AdminHotspots"));
import { 
  ShoppingCart, FlaskConical, GitCompare, Star, DollarSign, ThumbsUp, Heart, Eye,
  Shield, MousePointer, TrendingUp, CheckCircle, ChevronRight, Menu, X, ArrowLeft,
  Package, Users, Store, Percent, BarChart3, Award, Info, Lock, Clock, AlertTriangle,
  ExternalLink, Trash2, Edit, Plus, Loader2, GraduationCap, BookOpen, Brain,
  Map, Globe, Construction, Power, Mail, Handshake, XCircle, Moon, Sun, Bot,
  Radar, Share2, Gift, Home, Target, Crosshair, Route as RouteIcon, Briefcase, Cloud,
  Crown
} from "lucide-react";
import {
  Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle
} from "@/components/ui/sheet";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger
} from "@/components/ui/dropdown-menu";
import { Progress } from "@/components/ui/progress";
import { Toaster, toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// BLOC 2 OPTIMIZATION: Lazy loading fallback component
const LazyLoadFallback = () => (
  <div className="min-h-screen bg-background flex items-center justify-center">
    <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
  </div>
);

// Session ID helper
const getSessionId = () => {
  let sessionId = localStorage.getItem("session_id");
  if (!sessionId) {
    sessionId = "sess_" + Math.random().toString(36).substr(2, 9);
    localStorage.setItem("session_id", sessionId);
  }
  return sessionId;
};

// Logo Component
const Logo = ({ size = "default" }) => {
  const { brand } = useLanguage();
  return (
    <div className={`flex items-center gap-2 ${size === "large" ? "scale-125" : ""}`}>
      <BionicLogo className={size === "large" ? "h-10 w-10" : "h-8 w-8"} />
      <span className={`font-bold text-white ${size === "large" ? "text-2xl" : "text-xl"}`}>
        {brand.short}
      </span>
    </div>
  );
};

// Navigation Component - BIONIC TACTICAL Design System
const Navigation = ({ cartCount, onCartOpen }) => {
  const { t } = useLanguage();
  const { user } = useAuth();
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);

  // Role-based navigation visibility
  const isBusinessOrAdmin = user && ['business', 'admin'].includes(user.role);
  const isAdmin = user && user.role === 'admin';

  // Check if route is active
  const isActive = (path) => location.pathname === path;

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-xl border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo retiré du header - Logo global BionicLogoGlobal utilisé à la place */}
          
          {/* Desktop Navigation - BIONIC TACTICAL Style */}
          <nav className="hidden lg:flex items-center gap-1">
            {/* Home */}
            <Link 
              to="/" 
              className={`flex items-center gap-2 px-3 py-2 text-sm font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 ${isActive('/') ? 'text-[#F5A623] bg-[#F5A623]/10' : 'text-gray-300 hover:text-white'}`}
              data-testid="nav-home"
            >
              <Home className="h-4 w-4" />
              {t('common_home')}
            </Link>
            
            {/* Dashboard */}
            <Link 
              to="/dashboard" 
              className={`flex items-center gap-2 px-3 py-2 text-sm font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 ${isActive('/dashboard') ? 'text-[#F5A623] bg-[#F5A623]/10' : 'text-gray-300 hover:text-white'}`}
              data-testid="nav-dashboard"
            >
              <BarChart3 className="h-4 w-4" />
              {t('common_dashboard')}
            </Link>
            
            {/* Carte & Territoire Dropdown */}
            <div className="relative group">
              <button 
                className={`flex items-center gap-2 px-3 py-2 text-sm font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 ${['/map', '/territoire'].includes(location.pathname) ? 'text-[#F5A623] bg-[#F5A623]/10' : 'text-gray-300 hover:text-white'}`}
                data-testid="nav-carte"
              >
                <Map className="h-4 w-4" />
                {t('common_map')}
                <ChevronRight className="h-3 w-3 rotate-90 group-hover:rotate-180 transition-transform" />
              </button>
              <div className="absolute top-full left-0 mt-1 min-w-[220px] bg-black/95 backdrop-blur-xl border border-white/10 rounded-md shadow-xl py-1 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                <Link to="/map" className="flex items-start gap-3 px-4 py-2 hover:bg-white/5 group/item">
                  <Globe className="h-4 w-4 mt-0.5 text-gray-300 group-hover/item:text-[#F5A623]" />
                  <div>
                    <div className="text-sm font-medium text-white group-hover/item:text-[#F5A623]">{t('common_interactive_map')}</div>
                    <div className="text-xs text-gray-500">{t('common_gps_waypoints')}</div>
                  </div>
                </Link>
                <Link to="/territoire" className="flex items-start gap-3 px-4 py-2 hover:bg-white/5 group/item">
                  <Crosshair className="h-4 w-4 mt-0.5 text-gray-300 group-hover/item:text-[#F5A623]" />
                  <div>
                    <div className="text-sm font-medium text-white group-hover/item:text-[#F5A623]">{t('common_my_territory')}</div>
                    <div className="text-xs text-gray-500">{t('common_bionic_analysis')}</div>
                  </div>
                </Link>
              </div>
            </div>
            
            {/* Permis de chasse - Module Stratégique Indépendant */}
            <Link 
              to="/permis-chasse" 
              className={`flex items-center gap-2 px-3 py-2 text-sm font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 ${isActive('/permis-chasse') ? 'text-[#F5A623] bg-[#F5A623]/10' : 'text-gray-300 hover:text-white'}`}
              data-testid="nav-permis-chasse"
            >
              <Shield className="h-4 w-4" />
              Permis
            </Link>
            
            {/* Sorties */}
            <Link 
              to="/trips" 
              className={`flex items-center gap-2 px-3 py-2 text-sm font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 ${isActive('/trips') ? 'text-[#F5A623] bg-[#F5A623]/10' : 'text-gray-300 hover:text-white'}`}
              data-testid="nav-trips"
            >
              <RouteIcon className="h-4 w-4" />
              {t('common_trips')}
            </Link>
            
            {/* Magasin */}
            <Link 
              to="/shop" 
              className={`flex items-center gap-2 px-3 py-2 text-sm font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 ${isActive('/shop') ? 'text-[#F5A623] bg-[#F5A623]/10' : 'text-gray-300 hover:text-white'}`}
              data-testid="nav-shop"
            >
              <Store className="h-4 w-4" />
              {t('nav_shop')}
            </Link>
            
            {/* Business (Conditionnel) */}
            {isBusinessOrAdmin && (
              <Link 
                to="/business" 
                className={`flex items-center gap-2 px-3 py-2 text-sm font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 ${isActive('/business') ? 'text-[#10B981] bg-[#10B981]/10' : 'text-[#10B981]/70 hover:text-[#10B981]'}`}
                data-testid="nav-business"
              >
                <Briefcase className="h-4 w-4" />
                Business
              </Link>
            )}
          </nav>
          
          {/* Right Content */}
          <div className="flex items-center gap-2 lg:gap-3">
            {/* Premium CTA - Hidden on mobile */}
            <Link to="/pricing" className="hidden lg:block">
              <Button 
                size="sm" 
                className="bg-gradient-to-r from-[#F5A623] to-yellow-500 hover:from-[#F5A623]/90 hover:to-yellow-500/90 text-black font-semibold"
                data-testid="nav-premium"
              >
                <Crown className="h-4 w-4 mr-1" />
                Premium
              </Button>
            </Link>
            
            {/* Hidden on mobile, visible on desktop */}
            <div className="hidden lg:block">
              <LanguageSwitcher />
            </div>
            
            {/* Admin Dropdown - Hidden on mobile */}
            <div className="hidden lg:block relative group">
              <Button variant="ghost" size="sm" className="text-gray-300 hover:text-[#F5A623] hover:bg-white/5" data-testid="admin-link" aria-label="Menu administration">
                <Lock className="h-4 w-4" />
              </Button>
              <div className="absolute top-full right-0 mt-1 min-w-[200px] bg-black/95 backdrop-blur-xl border border-white/10 rounded-md shadow-xl py-1 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                <Link to="/admin" className="flex items-center gap-3 px-4 py-2 hover:bg-white/5 group/item">
                  <Shield className="h-4 w-4 text-gray-300 group-hover/item:text-[#F5A623]" />
                  <div>
                    <div className="text-sm font-medium text-white group-hover/item:text-[#F5A623]">Administration</div>
                    <div className="text-xs text-gray-500">Gestion classique</div>
                  </div>
                </Link>
                <Link to="/admin-premium" className="flex items-center gap-3 px-4 py-2 hover:bg-white/5 group/item">
                  <Crown className="h-4 w-4 text-[#F5A623] group-hover/item:text-[#F5A623]" />
                  <div>
                    <div className="text-sm font-medium text-[#F5A623]">Admin Premium</div>
                    <div className="text-xs text-gray-500">Tableau Ultime V5</div>
                  </div>
                </Link>
              </div>
            </div>
            
            {/* User Menu - Compact on mobile */}
            <div className="hidden lg:block">
              <UserMenu />
            </div>
            
            {/* Cart Button - Always visible */}
            <Button 
              variant="outline" 
              onClick={onCartOpen} 
              className="relative border-white/20 hover:border-[#F5A623]/50 hover:bg-[#F5A623]/10 transition-all" 
              data-testid="cart-button"
              aria-label={t('nav_cart')}
            >
              <ShoppingCart className="h-5 w-5" />
              {cartCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-[#F5A623] text-black text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold shadow-[0_0_10px_rgba(245,166,35,0.4)]" aria-label={`${cartCount} items`}>
                  {cartCount}
                </span>
              )}
            </Button>
            
            {/* Mobile Menu Button */}
            <button 
              className="lg:hidden p-2 text-gray-300 hover:text-white hover:bg-white/5 rounded-sm transition-colors" 
              onClick={() => setIsOpen(!isOpen)}
              data-testid="mobile-menu-btn"
              aria-label={isOpen ? t('common_close') : t('common_menu')}
              aria-expanded={isOpen}
            >
              {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>
      
      {/* Mobile Navigation */}
      {isOpen && (
        <div className="lg:hidden border-t border-white/10 bg-black/95 backdrop-blur-xl">
          <div className="px-4 py-4 space-y-2">
            <Link to="/" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-gray-300 hover:text-white">
              <Home className="h-4 w-4" /> {t('common_home')}
            </Link>
            <Link to="/dashboard" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-gray-300 hover:text-white">
              <BarChart3 className="h-4 w-4" /> {t('common_dashboard')}
            </Link>
            <Link to="/map" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-gray-300 hover:text-white">
              <Globe className="h-4 w-4" /> {t('common_map')}
            </Link>
            <Link to="/territoire" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-gray-300 hover:text-white">
              <Crosshair className="h-4 w-4" /> {t('nav_territory')}
            </Link>
            <Link to="/permis-chasse" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-[#F5A623]" data-testid="mobile-nav-permis-chasse">
              <Shield className="h-4 w-4" /> Permis de chasse
            </Link>
            <Link to="/trips" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-gray-300 hover:text-white">
              <RouteIcon className="h-4 w-4" /> {t('common_trips')}
            </Link>
            <Link to="/shop" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-gray-300 hover:text-white">
              <Store className="h-4 w-4" /> {t('nav_shop')}
            </Link>
            {isBusinessOrAdmin && (
              <Link to="/business" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-[#10B981]">
                <Briefcase className="h-4 w-4" /> Business
              </Link>
            )}
            
            {/* Divider */}
            <div className="border-t border-white/10 my-2" />
            
            {/* Admin links on mobile */}
            <Link to="/admin" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-gray-300 hover:text-white">
              <Lock className="h-4 w-4" /> Administration
            </Link>
            <Link to="/admin-premium" onClick={() => setIsOpen(false)} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-[#F5A623]">
              <Crown className="h-4 w-4" /> Admin Premium (Ultime)
            </Link>
            
            {/* Language Switcher on mobile */}
            <div className="px-3 py-2">
              <LanguageSwitcher />
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

// Footer Component - Hidden on full-viewport pages
const FULL_VIEWPORT_ROUTES = ['/map', '/territoire', '/forecast', '/admin-geo', '/admin-premium'];

const Footer = () => {
  const location = useLocation();
  const isFullViewportPage = FULL_VIEWPORT_ROUTES.some(route => 
    location.pathname === route || location.pathname.startsWith(route + '/')
  );
  
  if (isFullViewportPage) return null;
  
  return (
    <footer className="bg-black py-8 border-t border-border">
      <div className="max-w-7xl mx-auto px-4 text-center">
        <p className="text-gray-300">© 2024 BIONIC HUNT/Chasse - Chasse BIONIC™</p>
      </div>
    </footer>
  );
};

// HeroSection Component
const HeroSection = () => {
  const { t, brand } = useLanguage();
  return (
    <section className="hero-bg min-h-screen flex flex-col items-center justify-center text-center px-4 pt-24" data-testid="hero-section">
      <h1 className="text-4xl md:text-5xl golden-text font-bold mb-8 max-w-4xl leading-tight">
        {brand.tagline}
      </h1>
      <div className="flex flex-wrap items-center justify-center gap-4 mb-8">
        <Link to="/analytics">
          <Button className="btn-golden text-black font-semibold px-6 py-3 rounded-full flex items-center gap-2">
            <BarChart3 className="h-5 w-5" /> Intelligence
          </Button>
        </Link>
        <ChevronRight className="text-[#f5a623] h-6 w-6 hidden md:block" />
        <Link to="/compare">
          <Button className="btn-golden text-black font-semibold px-6 py-3 rounded-full flex items-center gap-2">
            <GitCompare className="h-5 w-5" /> {t('nav_compare')}
          </Button>
        </Link>
        <ChevronRight className="text-[#f5a623] h-6 w-6 hidden md:block" />
        <Link to="/shop">
          <Button className="btn-golden text-black font-semibold px-6 py-3 rounded-full flex items-center gap-2">
            <ShoppingCart className="h-5 w-5" /> {t('hero_order')}
          </Button>
        </Link>
      </div>
      <div className="max-w-3xl mx-auto space-y-4">
        <p className="text-gray-300">{t('hero_description')}</p>
        <p className="text-[#f5a623] font-medium">{t('hero_highlight')}</p>
        <p className="text-[#f5a623] font-semibold text-xl mt-6">{brand.slogan}</p>
      </div>
    </section>
  );
};

// ProductCard Component
const ProductCard = ({ product, onAddToCart }) => (
  <Card className="product-card bg-card border-border overflow-hidden" data-testid={`product-card-${product.rank}`}>
    <div className="relative">
      <div className="absolute top-3 left-3 z-10">
        <Badge className="rank-badge text-white font-bold px-3 py-1">#{product.rank}</Badge>
      </div>
      {/* PHASE D: Lazy loading for non-LCP images */}
      <img 
        src={product.image_url} 
        alt={product.name} 
        className="w-full aspect-square object-cover" 
        loading="lazy"
        decoding="async"
      />
    </div>
    <CardContent className="p-4">
      <p className="text-[#f5a623] text-sm">{product.brand}</p>
      <h3 className="text-white font-semibold mb-2 truncate">{product.name}</h3>
      <div className="flex items-center gap-2 mb-4">
        <Badge className="bg-[#f5a623] text-black">Score: {product.score}</Badge>
      </div>
      <p className="text-[#f5a623] font-bold text-xl mb-4">${product.price}</p>
      <Button className="w-full btn-golden text-black font-semibold" onClick={() => onAddToCart(product)}>
        <ShoppingCart className="h-4 w-4 mr-2" /> Ajouter
      </Button>
    </CardContent>
  </Card>
);

// ProductsSection Component
const ProductsSection = ({ products, onAddToCart }) => {
  const { t, brand } = useLanguage();
  return (
    <section className="py-16 px-4 bg-background" data-testid="products-section">
      <div className="max-w-7xl mx-auto">
        <h2 className="golden-text text-3xl md:text-4xl font-bold text-center mb-8 italic">
          {t('page_best_choices')} {brand.short}
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} onAddToCart={onAddToCart} />
          ))}
        </div>
      </div>
    </section>
  );
};

// FeaturesSection Component
const FeaturesSection = () => {
  const { t } = useLanguage();
  const features = [
    { icon: BarChart3, titleKey: "common_intelligence", descKey: "feature_analyze_desc" },
    { icon: GitCompare, titleKey: "nav_compare", descKey: "feature_compare_desc" },
    { icon: ShoppingCart, titleKey: "hero_order", descKey: "feature_order_desc" },
  ];
  return (
    <section className="py-16 px-4 bg-black/50" data-testid="features-section">
      <div className="max-w-5xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="feature-card rounded-xl p-8 text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#f5a623]/20 flex items-center justify-center">
                <feature.icon className="h-8 w-8 text-[#f5a623]" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">{t(feature.titleKey)}</h3>
              <p className="text-gray-300">{t(feature.descKey)}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// CartSheet Component
const CartSheet = ({ isOpen, onOpenChange, cartItems, onUpdateQuantity, onRemoveItem }) => {
  const { t } = useLanguage();
  const total = cartItems.reduce((sum, item) => sum + (item.product?.price || 0) * item.quantity, 0);
  return (
    <Sheet open={isOpen} onOpenChange={onOpenChange}>
      <SheetContent className="bg-card border-border w-full sm:max-w-md">
        <SheetHeader>
          <SheetTitle className="text-white flex items-center gap-2">
            <ShoppingCart className="h-5 w-5 text-[#f5a623]" /> {t('nav_cart')}
          </SheetTitle>
        </SheetHeader>
        <div className="mt-6 space-y-4 flex-1 overflow-auto">
          {cartItems.length === 0 ? (
            <p className="text-gray-300 text-center py-8">{t('cart_empty')}</p>
          ) : (
            cartItems.map((item) => (
              <div key={item.id} className="flex items-center gap-4 p-4 bg-background rounded-lg">
                <img src={item.product?.image_url} alt={item.product?.name} className="w-16 h-16 object-cover rounded" />
                <div className="flex-1">
                  <p className="text-white font-medium">{item.product?.name}</p>
                  <p className="text-[#f5a623]">${item.product?.price}</p>
                </div>
                <Button variant="ghost" size="sm" onClick={() => onRemoveItem(item.id)} aria-label={`${t('cart_remove')} ${item.product?.name}`}>
                  <Trash2 className="h-4 w-4 text-red-400" />
                </Button>
              </div>
            ))
          )}
        </div>
        {cartItems.length > 0 && (
          <div className="border-t border-border pt-4 mt-4">
            <div className="flex justify-between items-center mb-4">
              <span className="text-white font-medium">Total</span>
              <span className="text-[#f5a623] text-xl font-bold">${total.toFixed(2)}</span>
            </div>
            <Button className="w-full btn-golden text-black font-semibold">{t('cart_checkout')}</Button>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
};

// HomePage Component
const HomePage = ({ products, onAddToCart }) => (
  <main>
    <HeroSection />
    <ProductsSection products={products} onAddToCart={onAddToCart} />
    <FeaturesSection />
  </main>
);

// AnalyzePage Component
const AnalyzePage = ({ products }) => (
  <main className="pt-20 min-h-screen bg-background">
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="golden-text text-4xl font-bold mb-4">Analysez</h1>
      <p className="text-gray-300 mb-8">Analysez en profondeur chaque attractant avec nos critères scientifiques.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {products.map((product) => (
          <Card key={product.id} className="bg-card border-border p-6">
            <div className="flex items-start gap-4">
              {/* PHASE D: Lazy loading */}
              <img 
                src={product.image_url} 
                alt={product.name} 
                className="w-24 h-24 object-cover rounded-lg" 
                loading="lazy"
                decoding="async"
              />
              <div className="flex-1">
                <p className="text-[#f5a623] text-sm">{product.brand}</p>
                <h3 className="text-white font-semibold mb-2">{product.name}</h3>
                <Badge className="bg-[#f5a623]">Score: {product.score}</Badge>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  </main>
);

// TerritoryPage Component
const TerritoryPage = () => (
  <main className="pt-16 min-h-screen bg-background">
    <MonTerritoireBionicPage />
  </main>
);

// MarketplacePage Component
const MarketplacePage = () => (
  <main className="pt-16 min-h-screen bg-background">
    <HuntMarketplace />
  </main>
);

// FormationsPage Component
const FormationsPage = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();
  
  // Formations FédéCP officielles
  const fedecpFormations = [
    {
      id: "securite",
      title: "Initiation à la chasse avec arme à feu",
      description: "Formation obligatoire pour obtenir le certificat du chasseur au Québec",
      Icon: Crosshair,
      duration: "8 heures (2 jours)",
      type: "Obligatoire",
      price: "Environ 75$",
      link: "https://fedecp.com/la-chasse/japprends/initiation-des-chasseurs/",
      topics: ["Sécurité et manipulation des armes", "Réglementation provinciale", "Éthique de chasse", "Identification du gibier", "Examen théorique et pratique"]
    },
    {
      id: "arc",
      title: "Initiation à la chasse à l'arc",
      description: "Formation pour la chasse à l'arc et à l'arbalète",
      Icon: Target,
      duration: "4 heures",
      type: "Obligatoire pour arc/arbalète",
      price: "Environ 50$",
      link: "https://fedecp.com/la-chasse/japprends/initiation-des-chasseurs/",
      topics: ["Sécurité avec arc et arbalète", "Choix de l'équipement", "Techniques de tir", "Réglementation spécifique"]
    },
    {
      id: "piegeage",
      title: "Formation au piégeage",
      description: "Cours obligatoire pour obtenir le certificat de piégeur",
      Icon: Package,
      duration: "8 heures",
      type: "Obligatoire",
      price: "Environ 60$",
      link: "https://fedecp.com/le-piegeage/formation-au-piegeage/",
      topics: ["Réglementation sur le piégeage", "Types de pièges autorisés", "Éthique et bien-être animal", "Techniques de capture", "Traitement des fourrures"]
    },
    {
      id: "orignal",
      title: "Formation chasse à l'orignal",
      description: "Techniques avancées pour la chasse au roi de nos forêts",
      Icon: Target,
      duration: "4 heures",
      type: "Facultatif",
      price: "Environ 40$",
      link: "https://fedecp.com/la-chasse/orignal/",
      topics: ["Comportement de l'orignal", "Appels et leurres", "Stratégies de chasse", "Débitage et conservation"]
    }
  ];
  
  // Formations BIONIC™ exclusives
  const bionicFormations = [
    {
      id: "analyse-territoire",
      title: "Analyse de territoire BIONIC™",
      description: "Maîtrisez les outils d'analyse GPS et cartographique pour optimiser votre territoire de chasse",
      Icon: Map,
      duration: "Auto-formation",
      type: "Exclusif BIONIC™",
      modules: ["Lecture de cartes topographiques", "Identification des corridors", "Placement stratégique des caches", "Analyse des points d'eau"]
    },
    {
      id: "attractants",
      title: "Science des attractants",
      description: "Comprenez la chimie et la biologie derrière les leurres et attractants",
      Icon: BarChart3,
      duration: "Auto-formation",
      type: "Exclusif BIONIC™",
      modules: ["Composés olfactifs", "Phéromones et comportement", "Timing et application", "13 critères d'évaluation"]
    },
    {
      id: "meteo",
      title: "Météo et mouvement du gibier",
      description: "Apprenez à prédire le comportement du gibier selon les conditions météo",
      Icon: Cloud,
      duration: "Auto-formation",
      type: "Exclusif BIONIC™",
      modules: ["Pression atmosphérique", "Phases lunaires", "Front météo et activité", "Prévisions optimales"]
    }
  ];
  
  // Types de territoires au Québec
  const territoireTypes = [
    {
      type: "Terres publiques",
      description: "Territoires libres gérés par le MFFP",
      color: "#22c55e",
      features: ["Accès gratuit avec permis", "Tirage au sort pour certaines zones", "Règles de capacité de support"]
    },
    {
      type: "ZEC",
      description: "Zones d'exploitation contrôlée",
      color: "#3b82f6",
      features: ["Droit d'accès requis", "Gestion par associations", "Quotas et enregistrement obligatoire"]
    },
    {
      type: "Pourvoiries",
      description: "Territoires privés avec services",
      color: "#f59e0b",
      features: ["Hébergement et guidage", "Droits exclusifs", "Forfaits tout inclus"]
    },
    {
      type: "Réserves fauniques",
      description: "Territoires protégés par la SÉPAQ",
      color: "#8b5cf6",
      features: ["Réservation obligatoire", "Secteurs contingentés", "Haute qualité de chasse"]
    },
    {
      type: "Terres privées",
      description: "Propriétés privées avec permission",
      color: "#ef4444",
      features: ["Autorisation du propriétaire", "Ententes de chasse", "Location possible"]
    }
  ];

  return (
    <main className="min-h-screen bg-background pt-20 pb-16">
      <div className="max-w-7xl mx-auto px-4">
        {/* Back Button */}
        <Button 
          variant="ghost" 
          onClick={() => navigate('/')}
          className="mb-4 text-gray-300 hover:text-white hover:bg-gray-800/50"
          data-testid="back-button-formations"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Retour à l'accueil
        </Button>
        
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <GraduationCap className="h-8 w-8 text-[#f5a623]" />
              Centre de Formations
            </h1>
            <p className="text-gray-300">FédéCP & BIONIC™ - Devenez un chasseur expert</p>
          </div>
        </div>

        {/* FédéCP Section */}
        <section className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <BookOpen className="h-6 w-6 text-blue-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Formations FédéCP officielles</h2>
              <p className="text-gray-300 text-sm">Fédération québécoise des chasseurs et pêcheurs</p>
            </div>
            <a 
              href="https://fedecp.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="ml-auto"
            >
              <Badge className="bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 cursor-pointer">
                <ExternalLink className="h-3 w-3 mr-1" /> fedecp.com
              </Badge>
            </a>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {fedecpFormations.map((formation) => (
              <Card key={formation.id} className="bg-card border-border hover:border-blue-500/50 transition-all">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <formation.Icon className="h-8 w-8 text-blue-400" />
                    <Badge className={formation.type === 'Obligatoire' || formation.type.includes('Obligatoire') ? 'bg-red-500/20 text-red-400' : 'bg-gray-500/20 text-gray-300'}>
                      {formation.type}
                    </Badge>
                  </div>
                  <CardTitle className="text-white text-lg">{formation.title}</CardTitle>
                  <CardDescription className="text-xs">{formation.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2 text-xs text-gray-300 mb-2">
                    <Clock className="h-3 w-3" />
                    <span>{formation.duration}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-300 mb-3">
                    <DollarSign className="h-3 w-3" />
                    <span>{formation.price}</span>
                  </div>
                  <ul className="space-y-1 mb-4">
                    {formation.topics.slice(0, 3).map((topic, idx) => (
                      <li key={idx} className="text-xs text-gray-300 flex items-center gap-1">
                        <CheckCircle className="h-3 w-3 text-green-500" />
                        {topic}
                      </li>
                    ))}
                    {formation.topics.length > 3 && (
                      <li className="text-xs text-gray-500">+{formation.topics.length - 3} autres...</li>
                    )}
                  </ul>
                  <a href={formation.link} target="_blank" rel="noopener noreferrer">
                    <Button size="sm" className="w-full bg-blue-600 hover:bg-blue-700">
                      <ExternalLink className="h-3 w-3 mr-1" /> S'inscrire
                    </Button>
                  </a>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* BIONIC Section */}
        <section className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-[#f5a623]/20 rounded-lg">
              <Brain className="h-6 w-6 text-[#f5a623]" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Formations BIONIC™</h2>
              <p className="text-gray-300 text-sm">Maîtrisez les outils d'analyse de territoire</p>
            </div>
            <Badge className="ml-auto bg-[#f5a623]/20 text-[#f5a623]">Exclusif</Badge>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {bionicFormations.map((formation) => (
              <Card key={formation.id} className="bg-card border-border hover:border-[#f5a623]/50 transition-all">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <formation.Icon className="h-8 w-8 text-[#f5a623]" />
                    <Badge className="bg-[#f5a623]/20 text-[#f5a623]">{formation.type}</Badge>
                  </div>
                  <CardTitle className="text-white text-lg">{formation.title}</CardTitle>
                  <CardDescription className="text-xs">{formation.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2 text-xs text-gray-300 mb-3">
                    <Clock className="h-3 w-3" />
                    <span>{formation.duration}</span>
                  </div>
                  <ul className="space-y-1 mb-4">
                    {formation.modules.map((module, idx) => (
                      <li key={idx} className="text-xs text-gray-300 flex items-center gap-1">
                        <CheckCircle className="h-3 w-3 text-[#f5a623]" />
                        {module}
                      </li>
                    ))}
                  </ul>
                  <Button size="sm" className="w-full btn-golden text-black">
                    Commencer
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Territoire Types Section */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <Map className="h-6 w-6 text-green-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Types de Territoires au Québec</h2>
              <p className="text-gray-300 text-sm">Connaissez les différentes zones de chasse</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {territoireTypes.map((territoire) => (
              <Card key={territoire.type} className="bg-card border-border" style={{ borderLeftColor: territoire.color, borderLeftWidth: '4px' }}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg" style={{ color: territoire.color }}>{territoire.type}</CardTitle>
                  <CardDescription className="text-xs">{territoire.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-1">
                    {territoire.features.map((feature, idx) => (
                      <li key={idx} className="text-xs text-gray-300 flex items-center gap-1">
                        <CheckCircle className="h-3 w-3" style={{ color: territoire.color }} />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
};

// Main App Component
function App() {
  const [products, setProducts] = useState([]);
  const [cartItems, setCartItems] = useState([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const sessionId = getSessionId();

  const fetchProducts = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/products/top?limit=10`);
      setProducts(response.data);
    } catch (error) {
      console.error("Error fetching products:", error);
    }
  }, []);

  const handleAddToCart = async (product) => {
    try {
      await axios.post(`${API}/cart`, {
        session_id: sessionId,
        product_id: product.id,
        quantity: 1
      });
      // Fetch updated cart
      const cartResponse = await axios.get(`${API}/cart/${sessionId}`);
      setCartItems(cartResponse.data.items || cartResponse.data || []);
      toast.success("Produit ajouté au panier!");
    } catch (error) {
      console.error("Cart error:", error);
      toast.error("Erreur lors de l'ajout au panier");
    }
  };

  const handleRemoveItem = async (itemId) => {
    try {
      const response = await axios.delete(`${API}/cart/${sessionId}/item/${itemId}`);
      setCartItems(response.data.items || []);
      toast.success("Produit retiré du panier");
    } catch (error) {
      toast.error("Erreur lors de la suppression");
    }
  };

  const handleUpdateQuantity = async (itemId, quantity) => {
    try {
      const response = await axios.put(`${API}/cart/${sessionId}/item/${itemId}`, { quantity });
      setCartItems(response.data.items || []);
    } catch (error) {
      toast.error("Erreur lors de la mise à jour");
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const cartCount = cartItems.reduce((sum, item) => sum + item.quantity, 0);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  return (
    <LanguageProvider>
      <AuthProvider>
        <NotificationProvider 
          coordinates={{ lat: 46.8139, lng: -71.2080 }}
          enabled={true}
          warningMinutes={15}
        >
        <div className="App min-h-screen bg-background">
          <BrowserRouter>
            <SEOHead />
            {/* Logo BIONIC Global - Visible sur toutes les pages (desktop) */}
            <BionicLogoGlobal />
            <Navigation cartCount={cartCount} onCartOpen={() => setIsCartOpen(true)} />
            <CartSheet 
              isOpen={isCartOpen} 
              onOpenChange={setIsCartOpen} 
              cartItems={cartItems} 
              onUpdateQuantity={handleUpdateQuantity}
              onRemoveItem={handleRemoveItem}
            />
            {/* BLOC 2 OPTIMIZATION: Suspense wrapper for lazy-loaded routes */}
            <Suspense fallback={<LazyLoadFallback />}>
              <Routes>
                <Route path="/" element={<HomePage products={products} onAddToCart={handleAddToCart} />} />
                <Route path="/onboarding" element={<OnboardingPage />} />
                <Route path="/analyze" element={<Navigate to="/analytics" replace />} />
                <Route path="/compare" element={<ComparePage products={products} />} />
                <Route path="/shop" element={<ShopPage products={products} onAddToCart={handleAddToCart} />} />
                <Route path="/territoire" element={<TerritoryPage />} />
                <Route path="/mon-territoire-bionic" element={<MonTerritoireBionicPage />} />
                {/* Redirection pour URL simplifiée */}
                <Route path="/mon-territoire" element={<MonTerritoireBionicPage />} />
                <Route path="/marketplace" element={<MarketplacePage />} />
                <Route path="/formations" element={<FormationsPage />} />
                {/* Module Permis de chasse */}
                <Route path="/permis-chasse" element={<HuntingLicensePage />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/business" element={<BusinessPage />} />
                <Route path="/plan-maitre" element={<PlanMaitrePage />} />
                {/* V5-ULTIME: Analytics réactivé */}
                <Route path="/analytics" element={<AnalyticsPage />} />
                <Route path="/map" element={<MapPage />} />
                <Route path="/forecast" element={<ForecastPage />} />
                <Route path="/trips" element={<TripsPage />} />
                <Route path="/referral" element={<ReferralModule />} />
                <Route path="/admin" element={<AdminPage onProductsUpdate={fetchProducts} />} />
                <Route path="/admin/geo" element={<AdminGeoPage />} />
                <Route path="/admin/hotspots" element={<AdminHotspotsPage />} />
                <Route path="/networking" element={<NetworkingHub />} />
                <Route path="/lands" element={<LandsRental />} />
                <Route path="/reset-password" element={<ResetPasswordPage />} />
                <Route path="/become-partner" element={<BecomePartner />} />
                <Route path="/partner/dashboard" element={<PartnerDashboard />} />
                <Route path="/auth/google/callback" element={<GoogleOAuthCallback />} />
                {/* V5-ULTIME P3: Routes Monétisation */}
                <Route path="/pricing" element={<PricingPage />} />
                <Route path="/payment/success" element={<PaymentSuccessPage />} />
                <Route path="/payment/cancel" element={<PaymentCancelPage />} />
                {/* V5-ULTIME: Administration Premium */}
                <Route path="/admin-premium" element={<AdminPremiumPage />} />
                {/* Marketing Calendar V2 */}
                <Route path="/marketing-calendar" element={<MarketingCalendarPage />} />
                {/* BIONIC V5 Demo Page */}
                <Route path="/bionic-demo" element={<BionicAnalysisDemoPage />} />
                {/* PHASE F: Interface d'observations terrain */}
                <Route path="/observations" element={<FieldObservationForm />} />
                {/* CALIBRATION MASTER: Dashboard de calibration */}
                <Route path="/calibration" element={<CalibrationDashboard />} />
                <Route path="/reports" element={<ReportsPage />} />
                <Route path="/comparaison-especes" element={<SpeciesComparisonPage />} />
              </Routes>
            </Suspense>
            <Footer />
            <ScrollNavigator />
            <Toaster position="bottom-right" richColors />
            <CookieConsent />
            <OfflineIndicator />
            {/* PHASE F: Centre de notifications push temps réel */}
            <AlertNotificationCenter position="bottom-right" />
          </BrowserRouter>
        </div>
        </NotificationProvider>
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;