/**
 * UpsellPopup - V5-ULTIME Monétisation
 * =====================================
 * 
 * Popup de vente incitative intelligent.
 */

import React, { useState, useEffect } from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle,
  DialogDescription,
  DialogFooter
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { 
  Crown, Zap, Compass, Layers, Settings, 
  TrendingUp, Gift, Download, X
} from 'lucide-react';

const iconMap = {
  zap: Zap,
  compass: Compass,
  layers: Layers,
  settings: Settings,
  'trending-up': TrendingUp,
  gift: Gift,
  download: Download,
  crown: Crown
};

const UpsellPopup = ({
  open,
  onClose,
  onUpgrade,
  content = {},
  type = 'popup',
  campaignName
}) => {
  const IconComponent = iconMap[content.icon] || Crown;

  const handleUpgrade = () => {
    onUpgrade && onUpgrade(campaignName);
  };

  const handleDismiss = () => {
    onClose && onClose(campaignName);
  };

  if (type === 'toast') {
    return (
      <div 
        data-testid="upsell-toast"
        className={`
          fixed bottom-4 right-4 z-50 
          bg-[#1a1a2e] border border-[#F5A623]/30 rounded-lg shadow-xl
          p-4 max-w-sm transform transition-all duration-300
          ${open ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
        `}
      >
        <button 
          onClick={handleDismiss}
          className="absolute top-2 right-2 text-gray-500 hover:text-white"
        >
          <X className="h-4 w-4" />
        </button>
        
        <div className="flex items-start gap-3">
          <div className="p-2 bg-[#F5A623]/20 rounded-lg">
            <IconComponent className="h-5 w-5 text-[#F5A623]" />
          </div>
          <div className="flex-1">
            <h4 className="text-white font-medium text-sm">{content.title}</h4>
            <p className="text-gray-400 text-xs mt-1">{content.description}</p>
            <Button
              size="sm"
              onClick={handleUpgrade}
              className="mt-3 bg-[#F5A623] hover:bg-[#F5A623]/90 text-black text-xs"
            >
              {content.cta || 'En savoir plus'}
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (type === 'banner') {
    return (
      <div 
        data-testid="upsell-banner"
        className={`
          bg-gradient-to-r from-[#F5A623]/20 to-purple-500/20 
          border-y border-[#F5A623]/30 py-3 px-4
          ${open ? 'block' : 'hidden'}
        `}
      >
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <div className="flex items-center gap-3">
            <IconComponent className="h-5 w-5 text-[#F5A623]" />
            <div>
              <span className="text-white font-medium text-sm">{content.title}</span>
              <span className="text-gray-400 text-sm ml-2">{content.description}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              onClick={handleUpgrade}
              className="bg-[#F5A623] hover:bg-[#F5A623]/90 text-black"
            >
              {content.cta || 'Voir l\'offre'}
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={handleDismiss}
              className="text-gray-400 hover:text-white"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    );
  }

  // Default popup
  return (
    <Dialog open={open} onOpenChange={handleDismiss}>
      <DialogContent 
        data-testid="upsell-popup"
        className="bg-[#1a1a2e] border-[#F5A623]/30 text-white max-w-md"
      >
        <DialogHeader className="text-center">
          <div className="mx-auto w-16 h-16 rounded-full bg-[#F5A623]/20 flex items-center justify-center mb-4">
            <IconComponent className="h-8 w-8 text-[#F5A623]" />
          </div>
          <DialogTitle className="text-xl">{content.title}</DialogTitle>
          <DialogDescription className="text-gray-400">
            {content.description}
          </DialogDescription>
        </DialogHeader>

        <DialogFooter className="flex flex-col gap-2 sm:flex-col">
          <Button
            onClick={handleUpgrade}
            className="w-full bg-[#F5A623] hover:bg-[#F5A623]/90 text-black font-semibold"
          >
            <Crown className="h-4 w-4 mr-2" />
            {content.cta || 'Passer à Premium'}
          </Button>
          <Button
            variant="ghost"
            onClick={handleDismiss}
            className="w-full text-gray-400 hover:text-white"
          >
            Plus tard
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default UpsellPopup;
