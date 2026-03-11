/**
 * BionicHeader - Phase 8 Modular Header Component
 * 
 * Extracted and modularized header from App.js.
 * Uses centralized route configuration.
 * 
 * @version 2.0.0
 */

import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useLanguage } from '@/contexts/LanguageContext';
import { useAuth } from '@/components/GlobalAuth';
import { Button } from '@/components/ui/button';
import BionicLogo from '@/components/BionicLogo';
import { LanguageSwitcher } from '@/contexts/LanguageContext';
import { UserMenu } from '@/components/GlobalAuth';
import {
  Home, BarChart3, Brain, TrendingUp, Target, Radar, Map, Globe,
  Crosshair, FlaskConical, Store, Briefcase, Lock, ShoppingCart,
  ChevronRight, Menu, X, Route as RouteIcon
} from 'lucide-react';

// ============================================
// NAV LINK COMPONENT
// ============================================

const NavLink = ({ to, icon: Icon, label, isActive, testId }) => (
  <Link 
    to={to} 
    className={`flex items-center gap-2 px-3 py-2 text-sm font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 ${
      isActive ? 'text-[#F5A623] bg-[#F5A623]/10' : 'text-gray-400 hover:text-white'
    }`}
    data-testid={testId}
  >
    {Icon && <Icon className="h-4 w-4" />}
    {label}
  </Link>
);

// ============================================
// DROPDOWN COMPONENT
// ============================================

const NavDropdown = ({ icon: Icon, label, items, isActive, testId }) => (
  <div className="relative group">
    <button 
      className={`flex items-center gap-2 px-3 py-2 text-sm font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 ${
        isActive ? 'text-[#F5A623] bg-[#F5A623]/10' : 'text-gray-400 hover:text-white'
      }`}
      data-testid={testId}
    >
      {Icon && <Icon className="h-4 w-4" />}
      {label}
      <ChevronRight className="h-3 w-3 rotate-90 group-hover:rotate-180 transition-transform" />
    </button>
    <div className="absolute top-full left-0 mt-1 min-w-[220px] bg-black/95 backdrop-blur-xl border border-white/10 rounded-md shadow-xl py-1 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
      {items.map(item => (
        <Link 
          key={item.to}
          to={item.to} 
          className="flex items-start gap-3 px-4 py-2 hover:bg-white/5 group/item"
        >
          {item.icon && <item.icon className="h-4 w-4 mt-0.5 text-gray-400 group-hover/item:text-[#F5A623]" />}
          <div>
            <div className="text-sm font-medium text-white group-hover/item:text-[#F5A623]">{item.label}</div>
            {item.description && (
              <div className="text-xs text-gray-500">{item.description}</div>
            )}
          </div>
        </Link>
      ))}
    </div>
  </div>
);

// ============================================
// MOBILE NAV COMPONENT
// ============================================

const MobileNav = ({ isOpen, onClose, t, user, isBusinessOrAdmin }) => {
  if (!isOpen) return null;
  
  return (
    <div className="lg:hidden border-t border-white/10 bg-black/95 backdrop-blur-xl">
      <div className="px-4 py-4 space-y-2">
        <Link to="/" onClick={onClose} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-gray-400 hover:text-white">
          <Home className="h-4 w-4" /> {t('common_home')}
        </Link>
        <Link to="/dashboard" onClick={onClose} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-gray-400 hover:text-white">
          <BarChart3 className="h-4 w-4" /> {t('common_dashboard')}
        </Link>
        
        {/* Intelligence Section */}
        <div className="border-t border-white/5 pt-2 mt-2">
          <div className="px-3 py-1 text-xs text-gray-500 uppercase tracking-wider">{t('common_intelligence')}</div>
          <Link to="/analytics" onClick={onClose} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-gray-400 hover:text-white">
            <TrendingUp className="h-4 w-4" /> {t('common_analytics')}
          </Link>
          <Link to="/forecast" onClick={onClose} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-gray-400 hover:text-white">
            <Target className="h-4 w-4" /> {t('common_forecast')}
          </Link>
          <Link to="/plan-maitre" onClick={onClose} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-gray-400 hover:text-white">
            <Radar className="h-4 w-4" /> {t('common_plan_master')}
          </Link>
        </div>
        
        {/* Map Section */}
        <div className="border-t border-white/5 pt-2 mt-2">
          <div className="px-3 py-1 text-xs text-gray-500 uppercase tracking-wider">{t('common_map')}</div>
          <Link to="/map" onClick={onClose} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-gray-400 hover:text-white">
            <Globe className="h-4 w-4" /> {t('common_interactive_map')}
          </Link>
          <Link to="/territoire" onClick={onClose} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-gray-400 hover:text-white">
            <Crosshair className="h-4 w-4" /> {t('common_my_territory')}
          </Link>
        </div>
        
        {/* Other Links */}
        <div className="border-t border-white/5 pt-2 mt-2">
          <Link to="/trips" onClick={onClose} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-gray-400 hover:text-white">
            <RouteIcon className="h-4 w-4" /> {t('common_trips')}
          </Link>
          <Link to="/analyze" onClick={onClose} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-gray-400 hover:text-white">
            <FlaskConical className="h-4 w-4" /> {t('nav_analyze')}
          </Link>
          <Link to="/shop" onClick={onClose} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-gray-400 hover:text-white">
            <Store className="h-4 w-4" /> {t('nav_shop')}
          </Link>
          {isBusinessOrAdmin && (
            <Link to="/business" onClick={onClose} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-[#10B981]/70 hover:text-[#10B981]">
              <Briefcase className="h-4 w-4" /> Business
            </Link>
          )}
        </div>
        
        {/* User Section */}
        <div className="border-t border-white/5 pt-2 mt-2">
          <Link to="/admin" onClick={onClose} className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-sm hover:bg-white/5 text-gray-400 hover:text-white">
            <Lock className="h-4 w-4" /> Admin
          </Link>
          <div className="px-3 py-2">
            <LanguageSwitcher />
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================
// MAIN HEADER COMPONENT
// ============================================

const BionicHeader = ({ cartCount = 0, onCartOpen }) => {
  const { t } = useLanguage();
  const { user } = useAuth();
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);

  // Role-based navigation visibility
  const isBusinessOrAdmin = user && ['business', 'admin'].includes(user.role);

  // Check if route is active
  const isActive = (path) => location.pathname === path;
  const isActiveGroup = (paths) => paths.includes(location.pathname);

  // Intelligence dropdown items
  const intelligenceItems = [
    { to: '/analytics', icon: TrendingUp, label: t('common_analytics'), description: t('common_stats_charts') },
    { to: '/forecast', icon: Target, label: t('common_forecast'), description: t('common_weather_wildlife') },
    { to: '/plan-maitre', icon: Radar, label: t('common_plan_master'), description: t('common_full_strategy') }
  ];

  // Map dropdown items
  const mapItems = [
    { to: '/map', icon: Globe, label: t('common_interactive_map'), description: t('common_gps_waypoints') },
    { to: '/territoire', icon: Crosshair, label: t('common_my_territory'), description: t('common_bionic_analysis') }
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-xl border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <BionicLogo />
          </Link>
          
          {/* Desktop Navigation - BIONIC TACTICAL Style */}
          <nav className="hidden lg:flex items-center gap-1">
            {/* Home */}
            <NavLink 
              to="/" 
              icon={Home} 
              label={t('common_home')} 
              isActive={isActive('/')} 
              testId="nav-home" 
            />
            
            {/* Dashboard */}
            <NavLink 
              to="/dashboard" 
              icon={BarChart3} 
              label={t('common_dashboard')} 
              isActive={isActive('/dashboard')} 
              testId="nav-dashboard" 
            />
            
            {/* Intelligence Dropdown */}
            <NavDropdown 
              icon={Brain}
              label={t('common_intelligence')}
              items={intelligenceItems}
              isActive={isActiveGroup(['/analytics', '/forecast', '/plan-maitre'])}
              testId="nav-intelligence"
            />
            
            {/* Map Dropdown */}
            <NavDropdown 
              icon={Map}
              label={t('common_map')}
              items={mapItems}
              isActive={isActiveGroup(['/map', '/territoire'])}
              testId="nav-carte"
            />
            
            {/* Trips */}
            <NavLink 
              to="/trips" 
              icon={RouteIcon} 
              label={t('common_trips')} 
              isActive={isActive('/trips')} 
              testId="nav-trips" 
            />
            
            {/* Analyze */}
            <NavLink 
              to="/analyze" 
              icon={FlaskConical} 
              label={t('nav_analyze')} 
              isActive={isActive('/analyze')} 
              testId="nav-analyze" 
            />
            
            {/* Shop */}
            <NavLink 
              to="/shop" 
              icon={Store} 
              label={t('nav_shop')} 
              isActive={isActive('/shop')} 
              testId="nav-shop" 
            />
            
            {/* Business (Conditional) */}
            {isBusinessOrAdmin && (
              <Link 
                to="/business" 
                className={`flex items-center gap-2 px-3 py-2 text-sm font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 ${
                  isActive('/business') ? 'text-[#10B981] bg-[#10B981]/10' : 'text-[#10B981]/70 hover:text-[#10B981]'
                }`}
                data-testid="nav-business"
              >
                <Briefcase className="h-4 w-4" />
                Business
              </Link>
            )}
          </nav>
          
          {/* Right Content */}
          <div className="flex items-center gap-2 lg:gap-3">
            {/* Language Switcher - Desktop only */}
            <div className="hidden lg:block">
              <LanguageSwitcher />
            </div>
            
            {/* Admin Link - Desktop only */}
            <Link to="/admin" className="hidden lg:block">
              <Button 
                variant="ghost" 
                size="sm" 
                className="text-gray-400 hover:text-[#F5A623] hover:bg-white/5" 
                data-testid="admin-link"
              >
                <Lock className="h-4 w-4" />
              </Button>
            </Link>
            
            {/* User Menu - Desktop only */}
            <div className="hidden lg:block">
              <UserMenu />
            </div>
            
            {/* Cart Button - Always visible */}
            <Button 
              variant="outline" 
              onClick={onCartOpen} 
              className="relative border-white/20 hover:border-[#F5A623]/50 hover:bg-[#F5A623]/10 transition-all" 
              data-testid="cart-button"
            >
              <ShoppingCart className="h-5 w-5" />
              {cartCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-[#F5A623] text-black text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold shadow-[0_0_10px_rgba(245,166,35,0.4)]">
                  {cartCount}
                </span>
              )}
            </Button>
            
            {/* Mobile Menu Button */}
            <button 
              className="lg:hidden p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-sm transition-colors" 
              onClick={() => setIsOpen(!isOpen)}
              data-testid="mobile-menu-btn"
            >
              {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>
      
      {/* Mobile Navigation */}
      <MobileNav 
        isOpen={isOpen} 
        onClose={() => setIsOpen(false)}
        t={t}
        user={user}
        isBusinessOrAdmin={isBusinessOrAdmin}
      />
    </header>
  );
};

export default BionicHeader;
