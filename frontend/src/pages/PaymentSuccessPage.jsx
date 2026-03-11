/**
 * PaymentSuccessPage - V5-ULTIME Monétisation
 * ============================================
 * 
 * Page de confirmation de paiement.
 * BIONIC™ Global Container Applied
 */

import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Check, RefreshCw, X, Crown } from 'lucide-react';
import { PaymentService } from '@/ui/monetisation/payment';
import { GlobalContainer } from '@/core/layouts';

const PaymentSuccessPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');
  
  const [status, setStatus] = useState('checking');
  const [paymentData, setPaymentData] = useState(null);

  useEffect(() => {
    if (!sessionId) {
      setStatus('error');
      return;
    }

    PaymentService.pollPaymentStatus(sessionId, (result) => {
      if (result.status === 'success') {
        setStatus('success');
        setPaymentData(result.data);
      } else if (result.status === 'error' || result.status === 'expired' || result.status === 'timeout') {
        setStatus('error');
      }
    });
  }, [sessionId]);

  return (
    <main className="min-h-screen bg-background flex items-center justify-center">
      <GlobalContainer maxWidth="480px" centerContent fullHeight noTopPadding>
      <Card className="bg-[#1a1a2e] border-white/10 max-w-md w-full">
        <CardContent className="p-8 text-center">
          {status === 'checking' && (
            <>
              <RefreshCw className="h-16 w-16 text-[#F5A623] mx-auto mb-4 animate-spin" />
              <h1 className="text-2xl font-bold text-white mb-2">Vérification du paiement...</h1>
              <p className="text-gray-400">Veuillez patienter quelques instants.</p>
            </>
          )}

          {status === 'success' && (
            <>
              <div className="w-20 h-20 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-6">
                <Check className="h-10 w-10 text-green-500" />
              </div>
              <h1 className="text-2xl font-bold text-white mb-2">Paiement réussi!</h1>
              <p className="text-gray-400 mb-6">
                Votre abonnement est maintenant actif. Profitez de toutes les fonctionnalités Premium!
              </p>
              
              <div className="p-4 bg-white/5 rounded-lg mb-6">
                <div className="flex items-center justify-center gap-2 text-[#F5A623]">
                  <Crown className="h-5 w-5" />
                  <span className="font-medium">Premium activé</span>
                </div>
              </div>

              <Button
                onClick={() => navigate('/dashboard')}
                className="w-full bg-[#F5A623] hover:bg-[#F5A623]/90 text-black"
              >
                Accéder au Dashboard
              </Button>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="w-20 h-20 rounded-full bg-red-500/20 flex items-center justify-center mx-auto mb-6">
                <X className="h-10 w-10 text-red-500" />
              </div>
              <h1 className="text-2xl font-bold text-white mb-2">Erreur de paiement</h1>
              <p className="text-gray-400 mb-6">
                Le paiement n'a pas pu être confirmé. Veuillez réessayer ou contacter le support.
              </p>
              
              <div className="space-y-2">
                <Button
                  onClick={() => navigate('/pricing')}
                  className="w-full bg-[#F5A623] hover:bg-[#F5A623]/90 text-black"
                >
                  Réessayer
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => navigate('/')}
                  className="w-full text-gray-400 hover:text-white"
                >
                  Retour à l'accueil
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>
      </GlobalContainer>
    </main>
  );
};

export default PaymentSuccessPage;
