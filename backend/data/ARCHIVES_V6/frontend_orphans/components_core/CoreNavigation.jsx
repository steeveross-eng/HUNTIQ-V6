/**
 * CoreNavigation - V5-ULTIME
 * ===========================
 * 
 * Navigation modulaire centrale.
 * Seul composant de navigation autorisé à être importé par les modules.
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';

// Navigation modulaire configuration
export const MODULE_ROUTES = {
  // UI Core
  home: { path: '/', label: 'Accueil', icon: 'Home', module: 'core' },
  dashboard: { path: '/dashboard', label: 'Tableau de bord', icon: 'LayoutDashboard', module: 'core' },
  
  // UI Métier
  shop: { path: '/shop', label: 'Boutique', icon: 'ShoppingBag', module: 'metier' },
  map: { path: '/map', label: 'Carte', icon: 'Map', module: 'metier' },
  trips: { path: '/trips', label: 'Sorties', icon: 'Compass', module: 'metier' },
  
  // UI Scoring
  scoring: { path: '/scoring', label: 'Scoring', icon: 'Target', module: 'scoring' },
  compare: { path: '/compare', label: 'Comparer', icon: 'GitCompare', module: 'scoring' },
  
  // UI Météo
  forecast: { path: '/forecast', label: 'Prévisions', icon: 'Cloud', module: 'meteo' },
  
  // UI Stratégie
  strategy: { path: '/strategy', label: 'Stratégie', icon: 'Lightbulb', module: 'strategie' },
  
  // UI Territoire
  territory: { path: '/mon-territoire', label: 'Mon Territoire', icon: 'MapPin', module: 'territoire' },
  
  // UI Plan Maître
  planMaitre: { path: '/plan-maitre', label: 'Plan Maître', icon: 'Crown', module: 'plan_maitre' },
  
  // Intelligence
  analytics: { path: '/analytics', label: 'Analytics', icon: 'BarChart3', module: 'intelligence' },
  
  // Admin
  admin: { path: '/admin', label: 'Admin', icon: 'Settings', module: 'admin' },
};

export const CoreNavigation = ({ className, variant = 'horizontal' }) => {
  const location = useLocation();
  
  const isActive = (path) => location.pathname === path;
  
  if (variant === 'sidebar') {
    return (
      <nav className={cn('flex flex-col gap-1 p-2', className)}>
        {Object.entries(MODULE_ROUTES).map(([key, route]) => (
          <Link
            key={key}
            to={route.path}
            className={cn(
              'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
              isActive(route.path)
                ? 'bg-[#F5A623] text-black'
                : 'text-gray-400 hover:text-white hover:bg-white/10'
            )}
            data-testid={`nav-${key}`}
          >
            <span>{route.label}</span>
          </Link>
        ))}
      </nav>
    );
  }
  
  return (
    <nav className={cn('flex items-center gap-2', className)}>
      {Object.entries(MODULE_ROUTES).slice(0, 6).map(([key, route]) => (
        <Link
          key={key}
          to={route.path}
          className={cn(
            'px-3 py-1.5 rounded text-sm font-medium transition-colors',
            isActive(route.path)
              ? 'bg-[#F5A623] text-black'
              : 'text-gray-400 hover:text-white'
          )}
          data-testid={`nav-${key}`}
        >
          {route.label}
        </Link>
      ))}
    </nav>
  );
};

export default CoreNavigation;
