/**
 * Marketplace Monetization Components
 * - Payment packages display
 * - Checkout flow
 * - PRO subscription management
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  Crown,
  Sparkles,
  TrendingUp,
  Star,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
  CreditCard,
  Zap,
  Gift,
  Shield,
  Rocket,
  Building2,
  RefreshCw
} from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// ============================================
// PACKAGES DISPLAY COMPONENT
// ============================================

export const PackagesDisplay = ({ auth, listingId, onPurchaseComplete }) => {
  const [packages, setPackages] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedPackage, setSelectedPackage] = useState(null);
  const [purchasing, setPurchasing] = useState(false);

  useEffect(() => {
    loadPackages();
  }, []);

  const loadPackages = async () => {
    try {
      const response = await axios.get(`${API}/payments/packages`);
      setPackages(response.data);
    } catch (error) {
      console.error('Error loading packages:', error);
      toast.error('Erreur lors du chargement des forfaits');
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (pkg) => {
    if (!auth?.token) {
      toast.error('Veuillez vous connecter pour effectuer un achat');
      return;
    }

    setPurchasing(true);
    setSelectedPackage(pkg.id);

    try {
      const response = await axios.post(`${API}/payments/checkout`, {
        package_id: pkg.id,
        origin_url: window.location.origin,
        listing_id: listingId || null,
        seller_id: auth.seller?.id
      });

      // Redirect to Stripe checkout
      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (error) {
      console.error('Checkout error:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de la création du paiement');
      setPurchasing(false);
      setSelectedPackage(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-[#f5a623]" />
      </div>
    );
  }

  if (!packages) return null;

  return (
    <Tabs defaultValue="featured" className="w-full">
      <TabsList className="w-full justify-start bg-gray-900 mb-4">
        <TabsTrigger value="featured" className="flex items-center gap-1">
          <Star className="h-4 w-4" /> Mise en vedette
        </TabsTrigger>
        <TabsTrigger value="boost" className="flex items-center gap-1">
          <TrendingUp className="h-4 w-4" /> Boost
        </TabsTrigger>
        <TabsTrigger value="renewal" className="flex items-center gap-1">
          <RefreshCw className="h-4 w-4" /> Renouveler
        </TabsTrigger>
        <TabsTrigger value="pro" className="flex items-center gap-1">
          <Crown className="h-4 w-4" /> PRO
        </TabsTrigger>
        <TabsTrigger value="outfitter" className="flex items-center gap-1">
          <Building2 className="h-4 w-4" /> Pourvoyeurs
        </TabsTrigger>
      </TabsList>

      {/* Featured Listings */}
      <TabsContent value="featured">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {packages.categories.featured?.map(pkg => (
            <PackageCard
              key={pkg.id}
              pkg={pkg}
              icon={<Star className="h-6 w-6 text-yellow-400" />}
              onPurchase={() => handlePurchase(pkg)}
              isPurchasing={purchasing && selectedPackage === pkg.id}
              highlight={pkg.id === 'featured_30days'}
            />
          ))}
        </div>
      </TabsContent>

      {/* Auto-bump */}
      <TabsContent value="boost">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {packages.categories.auto_bump?.map(pkg => (
            <PackageCard
              key={pkg.id}
              pkg={pkg}
              icon={<TrendingUp className="h-6 w-6 text-green-400" />}
              onPurchase={() => handlePurchase(pkg)}
              isPurchasing={purchasing && selectedPackage === pkg.id}
            />
          ))}
        </div>
      </TabsContent>

      {/* Renewal */}
      <TabsContent value="renewal">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {packages.categories.renewal?.map(pkg => (
            <PackageCard
              key={pkg.id}
              pkg={pkg}
              icon={<RefreshCw className="h-6 w-6 text-blue-400" />}
              onPurchase={() => handlePurchase(pkg)}
              isPurchasing={purchasing && selectedPackage === pkg.id}
            />
          ))}
        </div>
      </TabsContent>

      {/* PRO Subscriptions */}
      <TabsContent value="pro">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {packages.categories.subscriptions?.map(pkg => (
            <PackageCard
              key={pkg.id}
              pkg={pkg}
              icon={<Crown className="h-6 w-6 text-purple-400" />}
              onPurchase={() => handlePurchase(pkg)}
              isPurchasing={purchasing && selectedPackage === pkg.id}
              highlight={pkg.id === 'pro_yearly'}
              isPro
            />
          ))}
        </div>
      </TabsContent>

      {/* Outfitter Packages */}
      <TabsContent value="outfitter">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {packages.categories.outfitter?.map(pkg => (
            <PackageCard
              key={pkg.id}
              pkg={pkg}
              icon={<Building2 className="h-6 w-6 text-amber-400" />}
              onPurchase={() => handlePurchase(pkg)}
              isPurchasing={purchasing && selectedPackage === pkg.id}
              highlight={pkg.id === 'outfitter_premium'}
              isOutfitter
            />
          ))}
        </div>
      </TabsContent>
    </Tabs>
  );
};

// ============================================
// PACKAGE CARD COMPONENT
// ============================================

const PackageCard = ({ pkg, icon, onPurchase, isPurchasing, highlight, isPro, isOutfitter }) => {
  const formatPrice = (amount) => {
    return new Intl.NumberFormat('fr-CA', { style: 'currency', currency: 'CAD' }).format(amount);
  };

  return (
    <Card className={`bg-card border-border transition-all ${
      highlight 
        ? 'border-[#f5a623] ring-2 ring-[#f5a623]/20' 
        : 'hover:border-gray-600'
    }`}>
      {highlight && (
        <div className="bg-[#f5a623] text-black text-xs font-bold text-center py-1">
          <Star className="h-3 w-3 inline mr-1" /> MEILLEUR CHOIX
        </div>
      )}
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="p-2 rounded-lg bg-gray-800">
            {icon}
          </div>
          {(isPro || isOutfitter) && (
            <Badge className="bg-purple-500/20 text-purple-400">
              {isOutfitter ? 'Pourvoyeur' : 'Abonnement'}
            </Badge>
          )}
        </div>
        <CardTitle className="text-white text-lg mt-3">{pkg.name}</CardTitle>
        <CardDescription className="text-gray-400">{pkg.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <span className="text-3xl font-bold text-[#f5a623]">{formatPrice(pkg.amount)}</span>
          {pkg.type === 'subscription' && (
            <span className="text-gray-500 text-sm ml-1">/{pkg.duration_days === 365 ? 'an' : 'mois'}</span>
          )}
        </div>
        
        <ul className="space-y-2 mb-4">
          {pkg.features?.map((feature, i) => (
            <li key={i} className="flex items-center gap-2 text-sm text-gray-300">
              <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
              {feature}
            </li>
          ))}
        </ul>

        <Button 
          onClick={onPurchase}
          disabled={isPurchasing}
          className={`w-full ${
            highlight 
              ? 'bg-[#f5a623] hover:bg-[#d4891c] text-black' 
              : 'bg-gray-700 hover:bg-gray-600'
          }`}
        >
          {isPurchasing ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
              Redirection...
            </>
          ) : (
            <>
              <CreditCard className="h-4 w-4 mr-2" />
              Acheter
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
};

// ============================================
// PAYMENT SUCCESS HANDLER
// ============================================

export const PaymentStatusChecker = ({ sessionId, onComplete }) => {
  const [status, setStatus] = useState('checking');
  const [attempts, setAttempts] = useState(0);
  const maxAttempts = 10;

  useEffect(() => {
    if (!sessionId) return;
    checkStatus();
  }, [sessionId]);

  const checkStatus = async () => {
    if (attempts >= maxAttempts) {
      setStatus('timeout');
      return;
    }

    try {
      const response = await axios.get(`${API}/payments/status/${sessionId}`);
      
      if (response.data.payment_status === 'paid') {
        setStatus('success');
        toast.success('Paiement réussi!');
        if (onComplete) {
          onComplete(response.data);
        }
      } else if (response.data.status === 'expired') {
        setStatus('expired');
        toast.error('Session de paiement expirée');
      } else {
        // Continue polling
        setAttempts(a => a + 1);
        setTimeout(checkStatus, 2000);
      }
    } catch (error) {
      console.error('Status check error:', error);
      setStatus('error');
    }
  };

  if (status === 'checking') {
    return (
      <div className="flex flex-col items-center justify-center py-12 space-y-4">
        <Loader2 className="h-12 w-12 animate-spin text-[#f5a623]" />
        <p className="text-white font-medium">Vérification du paiement...</p>
        <Progress value={(attempts / maxAttempts) * 100} className="w-48" />
      </div>
    );
  }

  if (status === 'success') {
    return (
      <div className="flex flex-col items-center justify-center py-12 space-y-4">
        <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center">
          <CheckCircle className="h-8 w-8 text-green-500" />
        </div>
        <h3 className="text-xl font-bold text-white">Paiement réussi!</h3>
        <p className="text-gray-400 text-center">
          Votre achat a été confirmé. Les avantages ont été appliqués à votre compte.
        </p>
      </div>
    );
  }

  if (status === 'expired' || status === 'timeout' || status === 'error') {
    return (
      <div className="flex flex-col items-center justify-center py-12 space-y-4">
        <div className="w-16 h-16 rounded-full bg-red-500/20 flex items-center justify-center">
          <AlertCircle className="h-8 w-8 text-red-500" />
        </div>
        <h3 className="text-xl font-bold text-white">
          {status === 'expired' ? 'Session expirée' : 'Erreur de vérification'}
        </h3>
        <p className="text-gray-400 text-center">
          {status === 'expired' 
            ? 'Votre session de paiement a expiré. Veuillez réessayer.'
            : 'Nous n\'avons pas pu vérifier votre paiement. Si vous avez été débité, contactez-nous.'}
        </p>
        <Button onClick={() => window.location.href = '/marketplace'}>
          Retour au Marketplace
        </Button>
      </div>
    );
  }

  return null;
};

// ============================================
// PRO BADGE COMPONENT
// ============================================

export const ProBadge = ({ seller }) => {
  if (!seller?.is_pro) return null;

  const isOutfitter = seller.is_outfitter;
  const tier = seller.outfitter_tier;

  if (isOutfitter) {
    return (
      <Badge className={`${
        tier === 'premium' 
          ? 'bg-gradient-to-r from-amber-500 to-yellow-500 text-black' 
          : 'bg-amber-500/20 text-amber-400 border-amber-500'
      }`}>
        <Building2 className="h-3 w-3 mr-1" />
        {tier === 'premium' ? 'Pourvoyeur Premium' : 'Pourvoyeur'}
      </Badge>
    );
  }

  return (
    <Badge className="bg-gradient-to-r from-purple-500 to-pink-500 text-white">
      <Crown className="h-3 w-3 mr-1" />
      PRO
    </Badge>
  );
};

// ============================================
// FEATURED BADGE COMPONENT
// ============================================

export const FeaturedBadge = ({ listing }) => {
  if (!listing?.is_featured) return null;

  const featuredUntil = listing.featured_until 
    ? new Date(listing.featured_until).toLocaleDateString('fr-CA')
    : null;

  return (
    <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500">
      <Star className="h-3 w-3 mr-1 fill-yellow-400" />
      En vedette {featuredUntil && `jusqu'au ${featuredUntil}`}
    </Badge>
  );
};

// ============================================
// UPGRADE PROMPT MODAL
// ============================================

export const UpgradePromptModal = ({ isOpen, onClose, auth, reason }) => {
  const reasons = {
    listings_limit: {
      title: "Limite d'annonces atteinte",
      description: "Vous avez atteint votre limite de 3 annonces gratuites.",
      recommendation: "Passez à PRO pour des annonces illimitées!"
    },
    boost_listing: {
      title: "Boostez votre annonce",
      description: "Obtenez plus de visibilité pour vendre plus vite.",
      recommendation: "Mettez votre annonce en vedette ou activez l'auto-bump!"
    },
    renew_listing: {
      title: "Annonce expirée",
      description: "Votre annonce a expiré ou va bientôt expirer.",
      recommendation: "Renouvelez-la pour continuer à recevoir des contacts!"
    }
  };

  const info = reasons[reason] || reasons.boost_listing;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-card border-border max-w-lg">
        <DialogHeader>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-3 rounded-full bg-[#f5a623]/20">
              <Rocket className="h-6 w-6 text-[#f5a623]" />
            </div>
            <div>
              <DialogTitle className="text-white">{info.title}</DialogTitle>
              <DialogDescription>{info.description}</DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 border border-purple-500/30 rounded-lg p-4 my-4">
          <p className="text-white font-medium flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-400" />
            {info.recommendation}
          </p>
        </div>

        <PackagesDisplay auth={auth} />

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>Plus tard</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// ============================================
// QUICK BOOST BUTTON
// ============================================

export const QuickBoostButton = ({ listing, auth, onBoost }) => {
  const [showOptions, setShowOptions] = useState(false);

  if (!auth?.token) return null;

  return (
    <>
      <Button
        variant="outline"
        size="sm"
        onClick={() => setShowOptions(true)}
        className="text-yellow-400 border-yellow-500/50 hover:bg-yellow-500/10"
      >
        <Zap className="h-4 w-4 mr-1" />
        Booster
      </Button>

      <Dialog open={showOptions} onOpenChange={setShowOptions}>
        <DialogContent className="bg-card border-border max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Zap className="h-5 w-5 text-yellow-400" />
              Booster "{listing?.title}"
            </DialogTitle>
            <DialogDescription>
              Choisissez une option pour augmenter la visibilité de votre annonce
            </DialogDescription>
          </DialogHeader>

          <PackagesDisplay auth={auth} listingId={listing?.id} />

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowOptions(false)}>Annuler</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default PackagesDisplay;
