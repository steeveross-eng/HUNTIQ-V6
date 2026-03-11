/**
 * OfflineIndicator - Core Component
 * ==================================
 * Shows offline/online connectivity status.
 * Architecture LEGO V5 - Core Component (no business logic)
 * 
 * @module core/components
 */
import React, { useState, useEffect } from 'react';
import { Wifi, WifiOff } from 'lucide-react';

// Simple connectivity service (no external dependencies)
const connectivityService = {
  subscribers: [],
  
  subscribe(callback) {
    this.subscribers.push(callback);
    return () => {
      this.subscribers = this.subscribers.filter(cb => cb !== callback);
    };
  },
  
  notify(status) {
    this.subscribers.forEach(cb => cb(status));
  },
  
  init() {
    window.addEventListener('online', () => this.notify('online'));
    window.addEventListener('offline', () => this.notify('offline'));
  }
};

export const OfflineIndicator = ({ 
  position = 'bottom-left',
  autoHide = true,
  autoHideDelay = 5000 
}) => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    connectivityService.init();
    
    const unsubscribe = connectivityService.subscribe((status) => {
      setIsOnline(status === 'online');
      setShowBanner(true);
      
      if (status === 'online' && autoHide) {
        setTimeout(() => setShowBanner(false), autoHideDelay);
      }
    });

    return unsubscribe;
  }, [autoHide, autoHideDelay]);

  if (!showBanner && isOnline) return null;

  const positionClasses = {
    'bottom-left': 'bottom-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'top-left': 'top-20 left-4',
    'top-right': 'top-20 right-4'
  };

  return (
    <div 
      className={`fixed ${positionClasses[position]} z-50 px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 transition-all duration-300 ${
        isOnline 
          ? 'bg-green-600 text-white' 
          : 'bg-amber-600 text-white'
      }`}
      data-testid="offline-indicator"
    >
      {isOnline ? (
        <Wifi className="h-5 w-5" />
      ) : (
        <WifiOff className="h-5 w-5 animate-pulse" />
      )}
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
