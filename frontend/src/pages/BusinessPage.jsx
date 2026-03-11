/**
 * BusinessPage - Business Dashboard wrapper page
 * Version: 1.0.2
 * Security: Role-based access control (P0 - 11 Feb 2026)
 * Access: business, admin roles only
 * BIONIC™ Global Container Applied
 */
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { ArrowLeft, ShieldAlert, Lock } from 'lucide-react';
import { BusinessDashboard } from '../modules/business';
import { useAuth } from '../components/GlobalAuth';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { GlobalContainer } from '../core/layouts';

const BusinessPage = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated, token, openLoginModal } = useAuth();
  const [accessDenied, setAccessDenied] = useState(false);
  const [loading, setLoading] = useState(true);

  // Role-based access control
  useEffect(() => {
    // Wait for auth state to be determined
    const checkAccess = () => {
      if (!isAuthenticated || !user) {
        // Not authenticated - redirect to home after short delay
        setLoading(false);
        setAccessDenied(true);
        return;
      }

      const userRole = user.role || localStorage.getItem('user_role');
      const allowedRoles = ['business', 'admin'];

      if (!allowedRoles.includes(userRole)) {
        // Authenticated but wrong role
        setAccessDenied(true);
        setLoading(false);
        return;
      }

      // Access granted
      setAccessDenied(false);
      setLoading(false);
    };

    // Small delay to allow auth state to hydrate
    const timer = setTimeout(checkAccess, 100);
    return () => clearTimeout(timer);
  }, [isAuthenticated, user, token]);

  // Loading state
  if (loading) {
    return (
      <main className="min-h-screen bg-background pt-20 pb-16 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-amber-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Vérification des accès...</p>
        </div>
      </main>
    );
  }

  // Access denied state
  if (accessDenied) {
    return (
      <main className="min-h-screen bg-background pt-20 pb-16">
        <div className="max-w-md mx-auto px-4">
          <Card className="bg-red-900/20 border-red-500/30">
            <CardHeader className="text-center">
              <div className="mx-auto w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mb-4">
                {isAuthenticated ? (
                  <ShieldAlert className="h-8 w-8 text-red-400" />
                ) : (
                  <Lock className="h-8 w-8 text-red-400" />
                )}
              </div>
              <CardTitle className="text-red-400">
                {isAuthenticated ? 'Accès Refusé' : 'Authentification Requise'}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-center space-y-4">
              {isAuthenticated ? (
                <>
                  <p className="text-gray-300">
                    Votre rôle actuel (<span className="text-amber-400 font-semibold">{user?.role || 'inconnu'}</span>) ne vous permet pas d'accéder au tableau de bord Business.
                  </p>
                  <p className="text-sm text-gray-500">
                    Cette section est réservée aux utilisateurs avec le rôle <span className="text-green-400">business</span> ou <span className="text-blue-400">admin</span>.
                  </p>
                </>
              ) : (
                <>
                  <p className="text-gray-300">
                    Vous devez être connecté avec un compte autorisé pour accéder au tableau de bord Business.
                  </p>
                  <Button
                    onClick={() => openLoginModal()}
                    className="bg-amber-600 hover:bg-amber-700 text-white"
                    data-testid="business-login-btn"
                  >
                    Se connecter
                  </Button>
                </>
              )}
              <div className="pt-4">
                <Button
                  variant="ghost"
                  onClick={() => navigate('/')}
                  className="text-gray-400 hover:text-white"
                  data-testid="business-back-home-btn"
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Retour à l'accueil
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    );
  }

  // Access granted - render dashboard
  return (
    <main className="min-h-screen bg-background">
      <GlobalContainer className="pb-16">
        {/* Back Button */}
        <Button 
          variant="ghost" 
          onClick={() => navigate('/')}
          className="mb-4 text-gray-400 hover:text-white hover:bg-gray-800/50"
          data-testid="back-button-business"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Retour à l'accueil
        </Button>

        {/* Business Dashboard */}
        <BusinessDashboard />
      </GlobalContainer>
    </main>
  );
};

export default BusinessPage;
