/**
 * PlanMaitrePage - Plan Maître Dashboard wrapper page
 * BIONIC™ Global Container Applied
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { PlanMaitreDashboard } from '../modules/planmaitre';
import { GlobalContainer } from '../core/layouts';

const PlanMaitrePage = () => {
  const navigate = useNavigate();

  return (
    <main className="min-h-screen bg-background">
      <GlobalContainer className="pb-16">
        {/* Back Button */}
        <Button 
          variant="ghost" 
          onClick={() => navigate('/')}
          className="mb-4 text-gray-400 hover:text-white hover:bg-gray-800/50"
          data-testid="back-button-planmaitre"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Retour à l'accueil
        </Button>

        {/* Plan Maître Dashboard */}
        <PlanMaitreDashboard 
          coordinates={{ lat: 46.8139, lng: -71.2082 }}
        />
      </GlobalContainer>
    </main>
  );
};

export default PlanMaitrePage;
