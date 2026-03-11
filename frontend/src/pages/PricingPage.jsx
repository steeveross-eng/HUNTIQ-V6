/**
 * PricingPage - V5-ULTIME Monétisation
 * =====================================
 * 
 * Page de tarification avec intégration Stripe.
 * BIONIC™ Global Container Applied
 */

import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { PaymentDashboard } from '@/ui/monetisation/payment';
import { useAuth } from '@/components/GlobalAuth';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { GlobalContainer } from '@/core/layouts';

const PricingPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user } = useAuth();

  // Get user ID or use session
  const userId = user?.id || localStorage.getItem('session_id') || 'guest_user';

  return (
    <main className="min-h-screen bg-background">
      <GlobalContainer className="pb-16">
        {/* Back Button */}
        <Button 
          variant="ghost" 
          onClick={() => navigate(-1)}
          className="mb-4 text-gray-300 hover:text-white hover:bg-gray-800/50"
          data-testid="back-button-pricing"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Retour
        </Button>

        {/* Payment Dashboard */}
        <PaymentDashboard userId={userId} />
      </GlobalContainer>
    </main>
  );
};

export default PricingPage;
