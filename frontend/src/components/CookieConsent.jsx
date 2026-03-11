/**
 * Cookie Consent Banner
 * Bannière de consentement conforme RGPD/Loi 25
 * - Sans ralentissement du site
 * - Sans complexité technique
 * - Sans stockage de données à l'étranger (localStorage uniquement)
 */

import React, { useState, useEffect } from 'react';
import { X, Cookie, Shield, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

const CONSENT_KEY = 'bionic_cookie_consent';
const CONSENT_VERSION = '1.0';

const CookieConsent = () => {
  const [showBanner, setShowBanner] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [preferences, setPreferences] = useState({
    necessary: true, // Toujours activé
    analytics: false,
    marketing: false
  });

  useEffect(() => {
    // Vérifier si le consentement a déjà été donné
    const consent = localStorage.getItem(CONSENT_KEY);
    if (!consent) {
      // Délai court pour ne pas bloquer le rendu initial
      const timer = setTimeout(() => setShowBanner(true), 1000);
      return () => clearTimeout(timer);
    } else {
      try {
        const parsed = JSON.parse(consent);
        if (parsed.version !== CONSENT_VERSION) {
          setShowBanner(true);
        }
      } catch {
        setShowBanner(true);
      }
    }
  }, []);

  const saveConsent = (acceptAll = false) => {
    const consentData = {
      version: CONSENT_VERSION,
      timestamp: new Date().toISOString(),
      preferences: acceptAll 
        ? { necessary: true, analytics: true, marketing: true }
        : preferences
    };
    
    localStorage.setItem(CONSENT_KEY, JSON.stringify(consentData));
    setShowBanner(false);
  };

  const handleAcceptAll = () => {
    saveConsent(true);
  };

  const handleAcceptSelected = () => {
    saveConsent(false);
  };

  const handleRejectAll = () => {
    setPreferences({ necessary: true, analytics: false, marketing: false });
    saveConsent(false);
  };

  if (!showBanner) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-[9999] p-4 animate-in slide-in-from-bottom duration-300">
      <div className="max-w-4xl mx-auto bg-[#1a1a2e] border border-[#f5a623]/30 rounded-xl shadow-2xl overflow-hidden">
        {/* Main Banner */}
        <div className="p-5">
          <div className="flex items-start gap-4">
            {/* Icon */}
            <div className="hidden sm:flex p-3 bg-[#f5a623]/20 rounded-xl">
              <Cookie className="h-6 w-6 text-[#f5a623]" />
            </div>
            
            {/* Content */}
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Shield className="h-5 w-5 text-green-500" />
                <h3 className="text-white font-semibold">Respect de votre vie privée</h3>
              </div>
              
              <p className="text-gray-400 text-sm leading-relaxed">
                Nous utilisons des cookies pour améliorer votre expérience sur BIONIC™. 
                Vos données restent au Québec et ne sont jamais vendues à des tiers.
                <button 
                  onClick={() => setShowDetails(!showDetails)}
                  className="text-[#f5a623] hover:underline ml-1"
                >
                  {showDetails ? 'Masquer les détails' : 'En savoir plus'}
                </button>
              </p>

              {/* Details Panel */}
              {showDetails && (
                <div className="mt-4 p-4 bg-black/30 rounded-lg space-y-3">
                  {/* Necessary Cookies */}
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <span className="text-white text-sm font-medium">Cookies essentiels</span>
                        <span className="text-[10px] bg-green-500/20 text-green-400 px-2 py-0.5 rounded">Requis</span>
                      </div>
                      <p className="text-gray-500 text-xs mt-1 ml-6">
                        Nécessaires au fonctionnement du site (authentification, panier, préférences)
                      </p>
                    </div>
                    <div className="w-12 h-6 bg-green-500/30 rounded-full flex items-center justify-end px-1">
                      <div className="w-4 h-4 bg-green-500 rounded-full"></div>
                    </div>
                  </div>

                  {/* Analytics Cookies */}
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-white text-sm font-medium">Cookies analytiques</span>
                      </div>
                      <p className="text-gray-500 text-xs mt-1">
                        Nous aident à comprendre comment vous utilisez le site
                      </p>
                    </div>
                    <button
                      onClick={() => setPreferences(p => ({ ...p, analytics: !p.analytics }))}
                      className={`w-12 h-6 rounded-full flex items-center px-1 transition-all ${
                        preferences.analytics ? 'bg-[#f5a623]/30 justify-end' : 'bg-gray-700 justify-start'
                      }`}
                    >
                      <div className={`w-4 h-4 rounded-full transition-all ${
                        preferences.analytics ? 'bg-[#f5a623]' : 'bg-gray-500'
                      }`}></div>
                    </button>
                  </div>

                  {/* Marketing Cookies */}
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-white text-sm font-medium">Cookies marketing</span>
                      </div>
                      <p className="text-gray-500 text-xs mt-1">
                        Permettent d'afficher des publicités pertinentes
                      </p>
                    </div>
                    <button
                      onClick={() => setPreferences(p => ({ ...p, marketing: !p.marketing }))}
                      className={`w-12 h-6 rounded-full flex items-center px-1 transition-all ${
                        preferences.marketing ? 'bg-[#f5a623]/30 justify-end' : 'bg-gray-700 justify-start'
                      }`}
                    >
                      <div className={`w-4 h-4 rounded-full transition-all ${
                        preferences.marketing ? 'bg-[#f5a623]' : 'bg-gray-500'
                      }`}></div>
                    </button>
                  </div>

                  <div className="pt-2 border-t border-gray-700">
                    <p className="text-gray-500 text-[10px]">
                      🇨🇦 Conforme à la Loi 25 du Québec et au RGPD. Données stockées localement sur votre appareil.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Buttons */}
          <div className="flex flex-wrap items-center gap-3 mt-4 sm:ml-[52px]">
            <Button
              onClick={handleAcceptAll}
              className="bg-[#f5a623] hover:bg-[#d4891c] text-black font-semibold px-6"
            >
              Tout accepter
            </Button>
            
            {showDetails ? (
              <Button
                onClick={handleAcceptSelected}
                variant="outline"
                className="border-[#f5a623]/50 text-[#f5a623] hover:bg-[#f5a623]/10"
              >
                Accepter la sélection
              </Button>
            ) : (
              <Button
                onClick={() => setShowDetails(true)}
                variant="outline"
                className="border-gray-600 text-gray-300 hover:bg-gray-800"
              >
                Personnaliser
              </Button>
            )}
            
            <Button
              onClick={handleRejectAll}
              variant="ghost"
              className="text-gray-400 hover:text-white"
            >
              Refuser tout
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CookieConsent;
