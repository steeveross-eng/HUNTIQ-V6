/**
 * PricingCard - V5-ULTIME Monétisation
 * =====================================
 * 
 * Carte de prix pour un package d'abonnement.
 */

import React from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Check, Crown, Zap, Star } from 'lucide-react';

const tierIcons = {
  free: <Zap className="h-6 w-6" />,
  premium: <Crown className="h-6 w-6" />,
  pro: <Star className="h-6 w-6" />
};

const tierColors = {
  free: 'text-gray-400 border-gray-600',
  premium: 'text-[#F5A623] border-[#F5A623]',
  pro: 'text-purple-400 border-purple-400'
};

const PricingCard = ({ 
  tier, 
  name, 
  price, 
  period = 'mois',
  features = [],
  popular = false,
  currentTier = false,
  onSelect,
  loading = false
}) => {
  const isUpgrade = !currentTier && tier !== 'free';

  return (
    <Card 
      data-testid={`pricing-card-${tier}`}
      className={`
        relative bg-[#1a1a2e] border-2 transition-all duration-300 hover:scale-105
        ${popular ? 'border-[#F5A623] shadow-lg shadow-[#F5A623]/20' : 'border-white/10'}
        ${currentTier ? 'ring-2 ring-green-500' : ''}
      `}
    >
      {popular && (
        <Badge 
          className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[#F5A623] text-black"
        >
          POPULAIRE
        </Badge>
      )}
      
      {currentTier && (
        <Badge 
          className="absolute -top-3 right-4 bg-green-500 text-white"
        >
          ACTUEL
        </Badge>
      )}

      <CardHeader className="text-center pb-2">
        <div className={`mx-auto mb-2 p-3 rounded-full bg-white/5 ${tierColors[tier]}`}>
          {tierIcons[tier]}
        </div>
        <CardTitle className="text-white text-xl">{name}</CardTitle>
      </CardHeader>

      <CardContent className="text-center">
        <div className="mb-6">
          <span className="text-4xl font-bold text-white">
            {price === 0 ? 'Gratuit' : `${price}$`}
          </span>
          {price > 0 && (
            <span className="text-gray-400 text-sm">/{period}</span>
          )}
        </div>

        <ul className="space-y-3 text-left">
          {features.map((feature, index) => (
            <li key={index} className="flex items-start gap-2">
              <Check className="h-5 w-5 text-green-500 shrink-0 mt-0.5" />
              <span className="text-gray-300 text-sm">{feature}</span>
            </li>
          ))}
        </ul>
      </CardContent>

      <CardFooter>
        <Button
          data-testid={`select-plan-${tier}`}
          className={`
            w-full transition-all
            ${popular 
              ? 'bg-[#F5A623] hover:bg-[#F5A623]/90 text-black' 
              : isUpgrade 
                ? 'bg-white/10 hover:bg-white/20 text-white'
                : 'bg-gray-700 text-gray-400 cursor-not-allowed'
            }
          `}
          disabled={currentTier || loading || tier === 'free'}
          onClick={() => onSelect && onSelect(tier)}
        >
          {loading ? (
            <span className="animate-pulse">Chargement...</span>
          ) : currentTier ? (
            'Plan actuel'
          ) : tier === 'free' ? (
            'Plan de base'
          ) : (
            'Choisir ce plan'
          )}
        </Button>
      </CardFooter>
    </Card>
  );
};

export default PricingCard;
