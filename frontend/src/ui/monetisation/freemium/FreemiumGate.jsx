/**
 * FreemiumGate - V5-ULTIME Monétisation
 * ======================================
 * 
 * Composant wrapper pour bloquer/autoriser l'accès aux features.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Lock, Crown, ArrowRight } from 'lucide-react';
import FreemiumService from './FreemiumService';

const FreemiumGate = ({
  feature,
  userId = 'current_user',
  children,
  fallback = null,
  onUpgradeClick,
  showPreview = false
}) => {
  const [loading, setLoading] = useState(true);
  const [canAccess, setCanAccess] = useState(false);
  const [accessInfo, setAccessInfo] = useState(null);

  useEffect(() => {
    const checkAccess = async () => {
      setLoading(true);
      const result = await FreemiumService.checkAccess(userId, feature);
      
      if (result.success) {
        setCanAccess(result.can_access);
        setAccessInfo(result);
      }
      setLoading(false);
    };

    checkAccess();
  }, [userId, feature]);

  if (loading) {
    return (
      <div className="animate-pulse bg-white/5 rounded-lg h-32" />
    );
  }

  if (canAccess) {
    return <>{children}</>;
  }

  // Afficher le fallback ou l'écran de blocage
  if (fallback) {
    return fallback;
  }

  return (
    <Card 
      data-testid={`freemium-gate-${feature}`}
      className="bg-[#1a1a2e] border-[#F5A623]/30 relative overflow-hidden"
    >
      {/* Preview flou */}
      {showPreview && (
        <div className="absolute inset-0 opacity-20 blur-sm pointer-events-none">
          {children}
        </div>
      )}

      <CardContent className="flex flex-col items-center justify-center p-8 text-center relative z-10">
        <div className="w-16 h-16 rounded-full bg-[#F5A623]/20 flex items-center justify-center mb-4">
          <Lock className="h-8 w-8 text-[#F5A623]" />
        </div>

        <h3 className="text-xl font-bold text-white mb-2">
          Fonctionnalité Premium
        </h3>

        <p className="text-gray-400 mb-6 max-w-sm">
          Cette fonctionnalité est réservée aux membres Premium. 
          Débloquez-la pour améliorer votre expérience de chasse.
        </p>

        <Button
          data-testid="upgrade-button"
          onClick={onUpgradeClick}
          className="bg-[#F5A623] hover:bg-[#F5A623]/90 text-black font-semibold"
        >
          <Crown className="h-4 w-4 mr-2" />
          Passer à Premium
          <ArrowRight className="h-4 w-4 ml-2" />
        </Button>

        {accessInfo?.tier && (
          <p className="text-xs text-gray-500 mt-4">
            Plan actuel: <span className="text-gray-400">{accessInfo.tier}</span>
          </p>
        )}
      </CardContent>
    </Card>
  );
};

export default FreemiumGate;
