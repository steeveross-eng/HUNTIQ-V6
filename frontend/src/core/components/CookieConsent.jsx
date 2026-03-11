/**
 * CookieConsent - Core Component
 * ===============================
 * RGPD/Loi 25 compliant cookie consent banner.
 * Architecture LEGO V5 - Core Component (no business logic)
 * 
 * @module core/components
 */
import React, { useState, useEffect } from 'react';
import { X, Cookie, Shield, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

const CONSENT_KEY = 'bionic_cookie_consent';
const CONSENT_VERSION = '1.0';

export const CookieConsent = ({ 
  onConsentChange,
  showDelay = 1000,
  brandColor = '#f5a623'
}) => {
  const [showBanner, setShowBanner] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [preferences, setPreferences] = useState({
    necessary: true,
    analytics: false,
    marketing: false
  });

  useEffect(() => {
    const consent = localStorage.getItem(CONSENT_KEY);
    if (!consent) {
      const timer = setTimeout(() => setShowBanner(true), showDelay);
      return () => clearTimeout(timer);
    } else {
      try {
        const parsed = JSON.parse(consent);
        if (parsed.version !== CONSENT_VERSION) {
          setShowBanner(true);
        } else if (onConsentChange) {
          onConsentChange(parsed.preferences);
        }
      } catch {
        setShowBanner(true);
      }
    }
  }, [showDelay, onConsentChange]);

  const saveConsent = (acceptAll = false) => {
    const consentPrefs = acceptAll 
      ? { necessary: true, analytics: true, marketing: true }
      : preferences;
      
    const consentData = {
      version: CONSENT_VERSION,
      timestamp: new Date().toISOString(),
      preferences: consentPrefs
    };
    
    localStorage.setItem(CONSENT_KEY, JSON.stringify(consentData));
    setShowBanner(false);
    
    if (onConsentChange) {
      onConsentChange(consentPrefs);
    }
  };

  if (!showBanner) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-[9999] p-4 animate-in slide-in-from-bottom duration-300">
      <div className="max-w-4xl mx-auto bg-[#1a1a2e] border border-white/10 rounded-xl shadow-2xl overflow-hidden">
        <div className="p-5">
          <div className="flex items-start gap-4">
            <div className="hidden sm:flex p-3 bg-white/10 rounded-xl">
              <Cookie className="h-6 w-6" style={{ color: brandColor }} />
            </div>
            
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Shield className="h-5 w-5 text-green-500" />
                <h3 className="text-white font-semibold">Respect de votre vie privée</h3>
              </div>
              
              <p className="text-gray-400 text-sm leading-relaxed">
                Nous utilisons des cookies pour améliorer votre expérience. 
                Vos données restent au Québec et ne sont jamais vendues.
                <button 
                  onClick={() => setShowDetails(!showDetails)}
                  className="hover:underline ml-1"
                  style={{ color: brandColor }}
                >
                  {showDetails ? 'Masquer' : 'En savoir plus'}
                </button>
              </p>

              {showDetails && (
                <div className="mt-4 p-4 bg-black/30 rounded-lg space-y-3">
                  <CookieOption
                    label="Cookies essentiels"
                    description="Nécessaires au fonctionnement du site"
                    checked={true}
                    disabled={true}
                    required={true}
                  />
                  <CookieOption
                    label="Cookies analytiques"
                    description="Nous aident à comprendre l'utilisation du site"
                    checked={preferences.analytics}
                    onChange={(v) => setPreferences(p => ({ ...p, analytics: v }))}
                    brandColor={brandColor}
                  />
                  <CookieOption
                    label="Cookies marketing"
                    description="Permettent d'afficher des publicités pertinentes"
                    checked={preferences.marketing}
                    onChange={(v) => setPreferences(p => ({ ...p, marketing: v }))}
                    brandColor={brandColor}
                  />
                  <div className="pt-2 border-t border-gray-700">
                    <p className="text-gray-500 text-[10px]">
                      🇨🇦 Conforme à la Loi 25 du Québec et au RGPD.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 mt-4 sm:ml-[52px]">
            <Button
              onClick={() => saveConsent(true)}
              className="font-semibold px-6 text-black"
              style={{ backgroundColor: brandColor }}
            >
              Tout accepter
            </Button>
            
            {showDetails ? (
              <Button
                onClick={() => saveConsent(false)}
                variant="outline"
                className="border-white/20"
                style={{ color: brandColor, borderColor: `${brandColor}50` }}
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
              onClick={() => {
                setPreferences({ necessary: true, analytics: false, marketing: false });
                saveConsent(false);
              }}
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

const CookieOption = ({ 
  label, 
  description, 
  checked, 
  onChange, 
  disabled = false, 
  required = false,
  brandColor = '#f5a623'
}) => (
  <div className="flex items-center justify-between">
    <div>
      <div className="flex items-center gap-2">
        {required && <CheckCircle className="h-4 w-4 text-green-500" />}
        <span className="text-white text-sm font-medium">{label}</span>
        {required && (
          <span className="text-[10px] bg-green-500/20 text-green-400 px-2 py-0.5 rounded">
            Requis
          </span>
        )}
      </div>
      <p className="text-gray-500 text-xs mt-1 ml-6">{description}</p>
    </div>
    <button
      onClick={() => !disabled && onChange?.(!checked)}
      disabled={disabled}
      className={`w-12 h-6 rounded-full flex items-center px-1 transition-all ${
        checked 
          ? 'justify-end' 
          : 'bg-gray-700 justify-start'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      style={checked ? { backgroundColor: `${brandColor}30` } : {}}
    >
      <div 
        className={`w-4 h-4 rounded-full transition-all ${!checked && 'bg-gray-500'}`}
        style={checked ? { backgroundColor: brandColor } : {}}
      />
    </button>
  </div>
);

export default CookieConsent;
