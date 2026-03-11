/**
 * useUpsell Hook - V5-ULTIME Monétisation
 * ========================================
 * 
 * Hook pour gérer les upsells de manière réactive.
 */

import { useState, useCallback } from 'react';
import UpsellService from './UpsellService';

export const useUpsell = (userId = 'current_user') => {
  const [currentUpsell, setCurrentUpsell] = useState(null);
  const [isOpen, setIsOpen] = useState(false);

  /**
   * Déclencher un upsell sur quota atteint
   */
  const triggerQuotaReached = useCallback(async (feature) => {
    const result = await UpsellService.triggerUpsell(userId, 'quota_reached', { feature });
    
    if (result.success && result.upsell) {
      setCurrentUpsell(result.upsell);
      setIsOpen(true);
    }
  }, [userId]);

  /**
   * Déclencher un upsell sur feature bloquée
   */
  const triggerFeatureLocked = useCallback(async (feature) => {
    const result = await UpsellService.triggerUpsell(userId, 'feature_locked', { feature });
    
    if (result.success && result.upsell) {
      setCurrentUpsell(result.upsell);
      setIsOpen(true);
    }
  }, [userId]);

  /**
   * Déclencher un upsell sur action
   */
  const triggerAction = useCallback(async (action) => {
    const result = await UpsellService.triggerUpsell(userId, 'action_based', { action });
    
    if (result.success && result.upsell) {
      setCurrentUpsell(result.upsell);
      setIsOpen(true);
    }
  }, [userId]);

  /**
   * Fermer et enregistrer le dismiss
   */
  const dismiss = useCallback(async () => {
    if (currentUpsell?.campaign_name) {
      await UpsellService.dismissCampaign(userId, currentUpsell.campaign_name);
    }
    setIsOpen(false);
    setCurrentUpsell(null);
  }, [currentUpsell, userId]);

  /**
   * Clic sur CTA
   */
  const handleClick = useCallback(async (onNavigate) => {
    if (currentUpsell?.campaign_name) {
      await UpsellService.recordClick(userId, currentUpsell.campaign_name);
    }
    setIsOpen(false);
    
    if (onNavigate) {
      onNavigate('/pricing');
    }
  }, [currentUpsell, userId]);

  return {
    currentUpsell,
    isOpen,
    triggerQuotaReached,
    triggerFeatureLocked,
    triggerAction,
    dismiss,
    handleClick
  };
};

export default useUpsell;
