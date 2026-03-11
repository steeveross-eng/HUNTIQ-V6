/**
 * DashboardPage - Core Dashboard wrapper page
 * BIONIC™ Global Container Applied
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { CoreDashboard } from '../modules/dashboard';
import { GlobalContainer } from '../core/layouts';

const DashboardPage = () => {
  const navigate = useNavigate();

  return (
    <main className="min-h-screen bg-background">
      <GlobalContainer className="pb-16">
        {/* Back Button */}
        <Button 
          variant="ghost" 
          onClick={() => navigate('/')}
          className="mb-4 text-gray-300 hover:text-white hover:bg-gray-800/50"
          data-testid="back-button-dashboard"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Retour à l'accueil
        </Button>

        {/* Core Dashboard */}
        <CoreDashboard 
          coordinates={{ lat: 46.8139, lng: -71.2082 }}
          species="deer"
          season="rut"
        />
      </GlobalContainer>
    </main>
  );
};

export default DashboardPage;
