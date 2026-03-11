/**
 * TerritoryHeader - Map header with stats, user info and actions
 * BIONIC Design System compliant - No emojis
 * Extracted from TerritoryMap.jsx for better maintainability
 */

import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useLanguage } from '@/contexts/LanguageContext';
import { 
  ArrowLeft, 
  Target, 
  Activity, 
  Camera, 
  ShoppingCart, 
  User, 
  LogOut 
} from 'lucide-react';
import { SpeciesIcon } from '@/components/bionic/SpeciesIcon';

const TerritoryHeader = ({
  userName,
  onLogout,
  stats,
  cartItemCount,
  onCartClick,
  onBackClick
}) => {
  const { t } = useLanguage();
  
  return (
    <div className="bg-card border-b border-border p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {/* Back Button */}
          <button 
            onClick={onBackClick}
            className="p-2 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
            title={t('territory_back')}
            data-testid="territory-back-btn"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          
          <div className="bg-[#f5a623] p-2 rounded-lg">
            <Target className="h-6 w-6 text-black" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">BIONIC™ {t('territory_title')}</h1>
            <p className="text-sm text-gray-400">{t('territory_subtitle')}</p>
          </div>
        </div>
        
        {/* Stats badges + User info */}
        <div className="flex items-center gap-3">
          {stats && (
            <>
              <Badge variant="outline" className="text-[#f5a623] border-[#f5a623]">
                <Activity className="h-3 w-3 mr-1" />
                {stats.total_events} {t('territory_events')}
              </Badge>
              <Badge variant="outline" className="text-green-500 border-green-500">
                <Camera className="h-3 w-3 mr-1" />
                {stats.cameras?.total || 0} {t('territory_cameras')}
              </Badge>
              <Badge variant="outline" className="text-blue-500 border-blue-500 flex items-center gap-1">
                <SpeciesIcon species="moose" size="xs" rounded /> {stats.species_counts?.orignal || 0}
              </Badge>
              <Badge variant="outline" className="text-orange-500 border-orange-500 flex items-center gap-1">
                <SpeciesIcon species="deer" size="xs" rounded /> {stats.species_counts?.chevreuil || 0}
              </Badge>
              <Badge variant="outline" className="text-gray-500 border-gray-500 flex items-center gap-1">
                <SpeciesIcon species="bear" size="xs" rounded /> {stats.species_counts?.ours || 0}
              </Badge>
            </>
          )}
          
          {/* Shopping Cart Button */}
          <button
            onClick={onCartClick}
            className="relative p-2 rounded-lg hover:bg-white/10 text-gray-400 hover:text-[#f5a623] transition-colors"
            title={t('territory_cart')}
            data-testid="territory-cart-btn"
          >
            <ShoppingCart className="h-5 w-5" />
            {cartItemCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-[#f5a623] text-black text-xs w-5 h-5 rounded-full flex items-center justify-center font-bold">
                {cartItemCount}
              </span>
            )}
          </button>
          
          {/* Separator */}
          <div className="w-px h-8 bg-border mx-2" />
          
          {/* User info and logout */}
          {userName && (
            <Badge className="bg-[#f5a623] text-black">
              <User className="h-3 w-3 mr-1" />
              {userName}
            </Badge>
          )}
          {onLogout && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={onLogout}
              className="border-red-500/50 text-red-400 hover:bg-red-500/10"
              data-testid="territory-logout-btn"
            >
              <LogOut className="h-4 w-4 mr-1" />
              {t('territory_logout')}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default TerritoryHeader;
