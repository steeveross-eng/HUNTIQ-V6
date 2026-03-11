/**
 * ModularNavigation - Phase 7-8 Navigation Component
 * 
 * Centralized navigation using route configuration.
 * Supports dropdown groups, role-based visibility, and i18n.
 * 
 * @version 2.0.0
 */

import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/components/GlobalAuth';
import { useLanguage } from '@/contexts/LanguageContext';
import { ChevronRight, Menu, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle
} from '@/components/ui/sheet';
import { ROUTES, NAV_GROUPS, getStandaloneRoutes, hasRouteAccess } from '@/config/routes';

// ============================================
// NAVIGATION LINK COMPONENT
// ============================================

const NavLink = ({ route, isActive, onClick }) => {
  const { t } = useLanguage();
  const Icon = route.icon;
  
  return (
    <Link
      to={route.path}
      onClick={onClick}
      className={`flex items-center gap-2 px-3 py-2 text-sm font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 ${
        isActive 
          ? 'text-[#F5A623] bg-[#F5A623]/10' 
          : 'text-gray-400 hover:text-white'
      }`}
      data-testid={`nav-${route.name}`}
    >
      {Icon && <Icon className="h-4 w-4" />}
      {t(route.labelKey) || route.label}
    </Link>
  );
};

// ============================================
// DROPDOWN GROUP COMPONENT
// ============================================

const NavDropdown = ({ group, currentPath }) => {
  const { t } = useLanguage();
  const Icon = group.icon;
  const isGroupActive = group.routes.some(r => r.path === currentPath);
  
  return (
    <div className="relative group">
      <button
        className={`flex items-center gap-2 px-3 py-2 text-sm font-medium uppercase tracking-wider rounded-sm transition-all duration-200 hover:bg-white/5 ${
          isGroupActive 
            ? 'text-[#F5A623] bg-[#F5A623]/10' 
            : 'text-gray-400 hover:text-white'
        }`}
        data-testid={`nav-${group.name}`}
      >
        {Icon && <Icon className="h-4 w-4" />}
        {t(group.labelKey) || group.label}
        <ChevronRight className="h-3 w-3 rotate-90 group-hover:rotate-180 transition-transform" />
      </button>
      
      <div className="absolute top-full left-0 mt-1 min-w-[220px] bg-black/95 backdrop-blur-xl border border-white/10 rounded-md shadow-xl py-1 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
        {group.routes.map(route => {
          const RouteIcon = route.icon;
          return (
            <Link
              key={route.path}
              to={route.path}
              className="flex items-start gap-3 px-4 py-2 hover:bg-white/5 group/item"
            >
              {RouteIcon && (
                <RouteIcon className="h-4 w-4 mt-0.5 text-gray-400 group-hover/item:text-[#F5A623]" />
              )}
              <div>
                <div className="text-sm font-medium text-white group-hover/item:text-[#F5A623]">
                  {t(route.labelKey) || route.label}
                </div>
                {route.description && (
                  <div className="text-xs text-gray-500">
                    {t(route.descriptionKey) || route.description}
                  </div>
                )}
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
};

// ============================================
// MOBILE NAVIGATION
// ============================================

const MobileNav = ({ isOpen, onClose }) => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const location = useLocation();
  
  const visibleRoutes = ROUTES.filter(route => {
    if (!route.showInNav) return false;
    return hasRouteAccess(route, user);
  });
  
  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent side="left" className="w-[300px] bg-black/95 border-white/10">
        <SheetHeader>
          <SheetTitle className="text-white">Menu</SheetTitle>
        </SheetHeader>
        
        <nav className="flex flex-col gap-1 mt-6">
          {visibleRoutes.map(route => {
            const Icon = route.icon;
            const isActive = location.pathname === route.path;
            
            return (
              <Link
                key={route.path}
                to={route.path}
                onClick={onClose}
                className={`flex items-center gap-3 px-4 py-3 rounded-md transition-all ${
                  isActive
                    ? 'bg-[#F5A623]/10 text-[#F5A623]'
                    : 'text-gray-400 hover:bg-white/5 hover:text-white'
                }`}
              >
                {Icon && <Icon className="h-5 w-5" />}
                <span className="font-medium">
                  {t(route.labelKey) || route.label}
                </span>
              </Link>
            );
          })}
        </nav>
      </SheetContent>
    </Sheet>
  );
};

// ============================================
// MAIN NAVIGATION COMPONENT
// ============================================

const ModularNavigation = () => {
  const { user } = useAuth();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  // Get standalone routes (not in dropdown groups)
  const standaloneRoutes = getStandaloneRoutes(user);
  
  // Filter standalone routes to exclude grouped ones
  const topLevelRoutes = standaloneRoutes.filter(route => 
    !['intelligence', 'territory'].includes(route.navGroup) &&
    route.category !== 'admin'
  );
  
  // Check if user can see admin routes
  const canSeeAdmin = user && user.role === 'admin';
  
  return (
    <>
      {/* Desktop Navigation */}
      <nav className="hidden lg:flex items-center gap-1">
        {/* Core routes (Home, Dashboard) */}
        {topLevelRoutes
          .filter(r => r.category === 'core')
          .map(route => (
            <NavLink
              key={route.path}
              route={route}
              isActive={location.pathname === route.path}
            />
          ))}
        
        {/* Intelligence Dropdown */}
        <NavDropdown 
          group={NAV_GROUPS.intelligence} 
          currentPath={location.pathname}
        />
        
        {/* Territory Dropdown */}
        <NavDropdown 
          group={NAV_GROUPS.territory} 
          currentPath={location.pathname}
        />
        
        {/* User routes (Trips, Analyze) */}
        {topLevelRoutes
          .filter(r => r.category === 'user')
          .map(route => (
            <NavLink
              key={route.path}
              route={route}
              isActive={location.pathname === route.path}
            />
          ))}
        
        {/* Commerce routes (Shop) */}
        {topLevelRoutes
          .filter(r => r.category === 'commerce' && hasRouteAccess(r, user))
          .map(route => (
            <NavLink
              key={route.path}
              route={route}
              isActive={location.pathname === route.path}
            />
          ))}
        
        {/* Admin route (conditional) */}
        {canSeeAdmin && (
          <NavLink
            route={ROUTES.find(r => r.name === 'admin')}
            isActive={location.pathname.startsWith('/admin')}
          />
        )}
      </nav>
      
      {/* Mobile Menu Button */}
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden text-white"
        onClick={() => setMobileMenuOpen(true)}
        data-testid="mobile-menu-button"
      >
        <Menu className="h-6 w-6" />
      </Button>
      
      {/* Mobile Navigation */}
      <MobileNav 
        isOpen={mobileMenuOpen} 
        onClose={() => setMobileMenuOpen(false)} 
      />
    </>
  );
};

export default ModularNavigation;
