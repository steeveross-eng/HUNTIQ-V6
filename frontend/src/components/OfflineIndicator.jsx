/**
 * OfflineIndicator - Shows offline/online status
 * Phase P3.4 - Mode Hors Ligne
 */
import React, { useState, useEffect } from 'react';
import { OfflineService } from '../services/OfflineService';

export const OfflineIndicator = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    // Initialize service worker
    OfflineService.registerServiceWorker();
    
    // Subscribe to online/offline changes
    const unsubscribe = OfflineService.subscribe((status) => {
      setIsOnline(status === 'online');
      setShowBanner(true);
      
      // Hide banner after 5 seconds if online
      if (status === 'online') {
        setTimeout(() => setShowBanner(false), 5000);
      }
    });

    return unsubscribe;
  }, []);

  if (!showBanner && isOnline) return null;

  return (
    <div 
      className={`fixed bottom-4 left-4 z-50 px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 transition-all duration-300 ${
        isOnline 
          ? 'bg-green-600 text-white' 
          : 'bg-amber-600 text-white'
      }`}
      data-testid="offline-indicator"
    >
      <span className={`w-3 h-3 rounded-full ${isOnline ? 'bg-green-300' : 'bg-amber-300 animate-pulse'}`} />
      <span className="font-medium">
        {isOnline ? 'Connexion rétablie' : 'Mode hors ligne'}
      </span>
      {!isOnline && (
        <span className="text-sm opacity-80">
          Données en cache disponibles
        </span>
      )}
    </div>
  );
};

export default OfflineIndicator;
