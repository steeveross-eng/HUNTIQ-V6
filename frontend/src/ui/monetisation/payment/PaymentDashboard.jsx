/**
 * PaymentDashboard - V5-ULTIME Monétisation
 * ==========================================
 * 
 * Dashboard principal pour les paiements et abonnements.
 * Module isolé - aucun import croisé.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { 
  CreditCard, Crown, Check, X, Clock, 
  RefreshCw, AlertCircle, Sparkles
} from 'lucide-react';
import PricingCard from './PricingCard';
import PaymentService from './PaymentService';

const PaymentDashboard = ({ userId = 'current_user' }) => {
  const [loading, setLoading] = useState(true);
  const [packages, setPackages] = useState([]);
  const [billingPeriod, setBillingPeriod] = useState('monthly');
  const [processingPayment, setProcessingPayment] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState(null);

  // Charger les packages
  useEffect(() => {
    const fetchPackages = async () => {
      setLoading(true);
      const result = await PaymentService.getPackages();
      if (result.success) {
        setPackages(result.packages || []);
      }
      setLoading(false);
    };
    fetchPackages();
  }, []);

  // Vérifier si retour de Stripe
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    
    if (sessionId) {
      setPaymentStatus({ status: 'checking', message: 'Vérification du paiement...' });
      
      PaymentService.pollPaymentStatus(sessionId, (status) => {
        setPaymentStatus(status);
        
        if (status.status === 'success') {
          // Nettoyer l'URL
          window.history.replaceState({}, '', window.location.pathname);
        }
      });
    }
  }, []);

  // Gérer la sélection d'un plan
  const handleSelectPlan = useCallback(async (tier) => {
    const packageId = billingPeriod === 'monthly' 
      ? `${tier}_monthly` 
      : `${tier}_yearly`;

    setProcessingPayment(true);
    
    const result = await PaymentService.createCheckoutSession(packageId, userId);
    
    if (result.success && result.url) {
      window.location.href = result.url;
    } else {
      setPaymentStatus({ status: 'error', message: result.error || 'Erreur de paiement' });
      setProcessingPayment(false);
    }
  }, [billingPeriod, userId]);

  // Plans avec features
  const plans = [
    {
      tier: 'free',
      name: 'Gratuit',
      monthlyPrice: 0,
      yearlyPrice: 0,
      features: [
        '3 stratégies/jour',
        '2 zones de territoire',
        '7 jours d\'historique',
        '5 recommandations IA/jour'
      ]
    },
    {
      tier: 'premium',
      name: 'Premium',
      monthlyPrice: 9.99,
      yearlyPrice: 99.99,
      popular: true,
      features: [
        '50 stratégies/jour',
        '10 zones de territoire',
        '90 jours d\'historique',
        '50 recommandations IA/jour',
        'Règles personnalisées',
        'Export PDF/Excel',
        'Live Heading View',
        'Couches avancées'
      ]
    },
    {
      tier: 'pro',
      name: 'Pro',
      monthlyPrice: 19.99,
      yearlyPrice: 199.99,
      features: [
        'Stratégies illimitées',
        'Zones illimitées',
        '1 an d\'historique',
        'IA illimitée',
        'Support prioritaire',
        'Toutes les fonctionnalités',
        'API Access',
        'Analytics avancés'
      ]
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-[#F5A623]" />
      </div>
    );
  }

  return (
    <div data-testid="payment-dashboard" className="space-y-8 p-6">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-2">
          <Sparkles className="h-8 w-8 text-[#F5A623]" />
          <h1 className="text-3xl font-bold text-white">Choisissez votre plan</h1>
        </div>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Débloquez tout le potentiel de BIONIC HUNT/Chasse avec nos plans Premium et Pro.
          Optimisez vos sorties de chasse avec des fonctionnalités avancées.
        </p>
      </div>

      {/* Payment Status Alert */}
      {paymentStatus && (
        <Card className={`
          mx-auto max-w-md
          ${paymentStatus.status === 'success' ? 'bg-green-500/10 border-green-500' : ''}
          ${paymentStatus.status === 'error' ? 'bg-red-500/10 border-red-500' : ''}
          ${paymentStatus.status === 'checking' || paymentStatus.status === 'pending' ? 'bg-yellow-500/10 border-yellow-500' : ''}
        `}>
          <CardContent className="flex items-center gap-3 p-4">
            {paymentStatus.status === 'success' && (
              <>
                <Check className="h-6 w-6 text-green-500" />
                <div>
                  <p className="text-green-400 font-medium">Paiement réussi!</p>
                  <p className="text-gray-400 text-sm">Votre abonnement est maintenant actif.</p>
                </div>
              </>
            )}
            {paymentStatus.status === 'error' && (
              <>
                <X className="h-6 w-6 text-red-500" />
                <div>
                  <p className="text-red-400 font-medium">Erreur de paiement</p>
                  <p className="text-gray-400 text-sm">{paymentStatus.message}</p>
                </div>
              </>
            )}
            {(paymentStatus.status === 'checking' || paymentStatus.status === 'pending') && (
              <>
                <RefreshCw className="h-6 w-6 text-yellow-500 animate-spin" />
                <div>
                  <p className="text-yellow-400 font-medium">Vérification en cours...</p>
                  <p className="text-gray-400 text-sm">
                    {paymentStatus.attempt ? `Tentative ${paymentStatus.attempt}/10` : 'Patientez...'}
                  </p>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      )}

      {/* Billing Period Toggle */}
      <div className="flex justify-center">
        <Tabs value={billingPeriod} onValueChange={setBillingPeriod} className="w-auto">
          <TabsList className="bg-white/5">
            <TabsTrigger 
              value="monthly" 
              data-testid="billing-monthly"
              className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black"
            >
              Mensuel
            </TabsTrigger>
            <TabsTrigger 
              value="yearly" 
              data-testid="billing-yearly"
              className="data-[state=active]:bg-[#F5A623] data-[state=active]:text-black"
            >
              Annuel
              <Badge className="ml-2 bg-green-500 text-white text-xs">-17%</Badge>
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Pricing Cards */}
      <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
        {plans.map((plan) => (
          <PricingCard
            key={plan.tier}
            tier={plan.tier}
            name={plan.name}
            price={billingPeriod === 'monthly' ? plan.monthlyPrice : plan.yearlyPrice}
            period={billingPeriod === 'monthly' ? 'mois' : 'an'}
            features={plan.features}
            popular={plan.popular}
            onSelect={handleSelectPlan}
            loading={processingPayment}
          />
        ))}
      </div>

      {/* Features Comparison */}
      <Card className="bg-[#1a1a2e] border-white/10 max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Crown className="h-5 w-5 text-[#F5A623]" />
            Pourquoi passer à Premium?
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            {[
              { title: 'Live Heading View', desc: 'Navigation immersive avec boussole en temps réel' },
              { title: 'Couches avancées', desc: 'Visualisation 3D et simulation comportementale' },
              { title: 'Règles personnalisées', desc: 'Créez vos propres stratégies de chasse' },
              { title: 'Export de données', desc: 'Exportez vos rapports en PDF ou Excel' },
            ].map((feature, i) => (
              <div key={i} className="flex items-start gap-3 p-3 bg-white/5 rounded-lg">
                <Check className="h-5 w-5 text-green-500 shrink-0 mt-0.5" />
                <div>
                  <p className="text-white font-medium">{feature.title}</p>
                  <p className="text-gray-400 text-sm">{feature.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Security Badge */}
      <div className="text-center text-gray-500 text-sm flex items-center justify-center gap-2">
        <CreditCard className="h-4 w-4" />
        Paiement sécurisé par Stripe. Annulez à tout moment.
      </div>
    </div>
  );
};

export default PaymentDashboard;
