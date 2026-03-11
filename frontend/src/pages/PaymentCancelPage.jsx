/**
 * PaymentCancelPage - V5-ULTIME Monétisation
 * ===========================================
 * 
 * Page d'annulation de paiement.
 * BIONIC™ Global Container Applied
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { XCircle, ArrowLeft } from 'lucide-react';
import { GlobalContainer } from '@/core/layouts';

const PaymentCancelPage = () => {
  const navigate = useNavigate();

  return (
    <main className="min-h-screen bg-background flex items-center justify-center">
      <GlobalContainer maxWidth="480px" centerContent fullHeight noTopPadding>
      <Card className="bg-[#1a1a2e] border-white/10 max-w-md w-full">
        <CardContent className="p-8 text-center">
          <div className="w-20 h-20 rounded-full bg-yellow-500/20 flex items-center justify-center mx-auto mb-6">
            <XCircle className="h-10 w-10 text-yellow-500" />
          </div>
          
          <h1 className="text-2xl font-bold text-white mb-2">Paiement annulé</h1>
          <p className="text-gray-400 mb-6">
            Votre paiement a été annulé. Aucun montant n'a été prélevé.
          </p>
          
          <div className="space-y-2">
            <Button
              onClick={() => navigate('/pricing')}
              className="w-full bg-[#F5A623] hover:bg-[#F5A623]/90 text-black"
            >
              Voir les plans
            </Button>
            <Button
              variant="ghost"
              onClick={() => navigate('/')}
              className="w-full text-gray-400 hover:text-white"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Retour à l'accueil
            </Button>
          </div>
        </CardContent>
      </Card>
      </GlobalContainer>
    </main>
  );
};

export default PaymentCancelPage;
