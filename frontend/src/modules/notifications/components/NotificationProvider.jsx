/**
 * NotificationProvider - Context provider for app-wide notification management
 * Handles legal time alerts, push notifications, and in-app toasts
 */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { NotificationService } from '../NotificationService';
import { LegalTimeAlert } from './LegalTimeAlert';
import { toast } from 'sonner';

const NotificationContext = createContext(null);

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};

export const NotificationProvider = ({ 
  children, 
  coordinates = { lat: 46.8139, lng: -71.2080 },
  enabled = true,
  warningMinutes = 15
}) => {
  const [permissionStatus, setPermissionStatus] = useState('default');
  const [showLegalAlert, setShowLegalAlert] = useState(false);
  const [legalStatus, setLegalStatus] = useState(null);
  const [lastWarningTime, setLastWarningTime] = useState(null);

  // Check legal time status periodically
  const checkLegalTime = useCallback(async () => {
    if (!enabled) return;

    const status = await NotificationService.getLegalTimeStatus(
      coordinates.lat,
      coordinates.lng
    );

    if (status.success) {
      setLegalStatus(status);

      // Show alert if warning is active
      if (status.warning_active) {
        setShowLegalAlert(true);

        // Send toast notification if this is a new warning (not the same minute)
        const currentMinute = status.minutes_remaining;
        if (lastWarningTime !== currentMinute) {
          setLastWarningTime(currentMinute);
          
          // Show toast at specific intervals
          if ([15, 10, 5, 2, 1].includes(currentMinute)) {
            const urgency = currentMinute <= 5 ? 'error' : currentMinute <= 10 ? 'warning' : 'info';
            
            toast[urgency](
              currentMinute <= 5 
                ? `${currentMinute} min avant fin de chasse!`
                : `${currentMinute} min restantes`,
              {
                description: `Fin de période légale à ${status.legal_window?.end}`,
                duration: currentMinute <= 5 ? 10000 : 5000,
                action: {
                  label: 'OK',
                  onClick: () => {}
                }
              }
            );

            // Also send browser notification
            if (permissionStatus === 'granted') {
              NotificationService.sendLegalTimeWarning(
                currentMinute,
                status.legal_window?.end
              );
            }
          }
        }
      } else {
        setShowLegalAlert(false);
        setLastWarningTime(null);
      }
    }
  }, [enabled, coordinates, permissionStatus, lastWarningTime]);

  // Request notification permission
  const requestPermission = useCallback(async () => {
    const permission = await NotificationService.requestPermission();
    setPermissionStatus(permission);
    
    if (permission === 'granted') {
      toast.success('Notifications activées', {
        description: 'Vous recevrez des alertes 15 min avant la fin de période légale'
      });
    }
    
    return permission;
  }, []);

  // Initialize
  useEffect(() => {
    // Check initial permission status
    if ('Notification' in window) {
      setPermissionStatus(Notification.permission);
    }

    // Initial check
    checkLegalTime();

    // Check every minute
    const interval = setInterval(checkLegalTime, 60000);

    return () => clearInterval(interval);
  }, [checkLegalTime]);

  // Send custom notification
  const sendNotification = useCallback((title, options = {}) => {
    // In-app toast
    toast(title, {
      description: options.body,
      duration: options.duration || 5000
    });

    // Browser notification if permitted
    if (permissionStatus === 'granted') {
      NotificationService.sendBrowserNotification(title, options);
    }
  }, [permissionStatus]);

  const value = {
    permissionStatus,
    requestPermission,
    legalStatus,
    showLegalAlert,
    sendNotification,
    checkLegalTime
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
      
      {/* Global Legal Time Alert */}
      {enabled && showLegalAlert && (
        <LegalTimeAlert 
          coordinates={coordinates}
          warningMinutes={warningMinutes}
          onDismiss={() => setShowLegalAlert(false)}
        />
      )}
    </NotificationContext.Provider>
  );
};

export default NotificationProvider;
