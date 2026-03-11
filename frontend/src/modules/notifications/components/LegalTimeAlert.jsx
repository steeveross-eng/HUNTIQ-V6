/**
 * LegalTimeAlert - In-app alert component for legal hunting time warnings
 * BIONIC Design System compliant - No emojis
 * Displays a prominent alert when approaching end of legal hunting period
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Alert, AlertDescription, AlertTitle } from '../../../components/ui/alert';
import { Button } from '../../../components/ui/button';
import { NotificationService } from '../NotificationService';
import { AlertTriangle, Clock, AlertOctagon, Bell, Lightbulb } from 'lucide-react';

export const LegalTimeAlert = ({ 
  coordinates = { lat: 46.8139, lng: -71.2080 },
  warningMinutes = 15,
  onDismiss,
  showAlways = false
}) => {
  const [status, setStatus] = useState(null);
  const [dismissed, setDismissed] = useState(false);
  const [permissionGranted, setPermissionGranted] = useState(false);

  const checkStatus = useCallback(async () => {
    const result = await NotificationService.getLegalTimeStatus(
      coordinates.lat, 
      coordinates.lng
    );
    
    if (result.success) {
      setStatus(result);
      
      // Send browser notification if warning is active
      if (result.warning_active && result.minutes_remaining <= warningMinutes && permissionGranted) {
        NotificationService.sendLegalTimeWarning(
          result.minutes_remaining,
          result.legal_window?.end
        );
      }
    }
  }, [coordinates, warningMinutes, permissionGranted]);

  useEffect(() => {
    // Request notification permission on mount
    NotificationService.requestPermission().then(permission => {
      setPermissionGranted(permission === 'granted');
    });

    // Initial check
    checkStatus();

    // Check every minute
    const interval = setInterval(checkStatus, 60000);

    return () => clearInterval(interval);
  }, [checkStatus]);

  const handleDismiss = () => {
    setDismissed(true);
    onDismiss?.();
  };

  const handleRequestPermission = async () => {
    const permission = await NotificationService.requestPermission();
    setPermissionGranted(permission === 'granted');
  };

  // Don't show if dismissed or no warning
  if (!status || (dismissed && !showAlways)) return null;
  if (!status.warning_active && !showAlways) return null;

  const { minutes_remaining, legal_window, alert } = status;

  // Determine alert style based on urgency
  const getAlertStyle = () => {
    if (minutes_remaining <= 5) {
      return 'bg-red-900/90 border-red-500 animate-pulse';
    } else if (minutes_remaining <= 10) {
      return 'bg-orange-900/80 border-orange-500';
    } else {
      return 'bg-amber-900/70 border-amber-500';
    }
  };

  const getIcon = () => {
    if (minutes_remaining <= 5) return <AlertOctagon className="w-8 h-8 text-red-400" />;
    if (minutes_remaining <= 10) return <AlertTriangle className="w-8 h-8 text-orange-400" />;
    return <Clock className="w-8 h-8 text-amber-400" />;
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-md" data-testid="legal-time-alert">
      <Alert className={`${getAlertStyle()} border-2 shadow-2xl`}>
        <div className="flex items-start gap-3">
          {getIcon()}
          <div className="flex-1">
            <AlertTitle className="text-white text-lg font-bold mb-1">
              {alert?.title || `${minutes_remaining} minutes restantes`}
            </AlertTitle>
            <AlertDescription className="text-slate-200">
              {alert?.body || `La période légale se termine à ${legal_window?.end}`}
            </AlertDescription>
            
            <div className="mt-3 flex items-center gap-2">
              <div className="flex-1 bg-slate-800/50 rounded-full h-2 overflow-hidden">
                <div 
                  className={`h-full transition-all duration-1000 ${
                    minutes_remaining <= 5 ? 'bg-red-500' : 
                    minutes_remaining <= 10 ? 'bg-orange-500' : 'bg-amber-500'
                  }`}
                  style={{ width: `${Math.max(0, (minutes_remaining / 30) * 100)}%` }}
                />
              </div>
              <span className="text-white font-mono text-sm min-w-[50px]">
                {minutes_remaining} min
              </span>
            </div>

            <div className="mt-3 flex gap-2">
              {!permissionGranted && (
                <Button 
                  size="sm" 
                  variant="outline"
                  className="text-white border-white/50 hover:bg-white/10"
                  onClick={handleRequestPermission}
                >
                  <Bell className="h-4 w-4 mr-1" /> Activer alertes
                </Button>
              )}
              <Button 
                size="sm" 
                variant="ghost"
                className="text-white/70 hover:text-white hover:bg-white/10"
                onClick={handleDismiss}
              >
                Fermer
              </Button>
            </div>
          </div>
        </div>
      </Alert>

      {/* Permission reminder if not granted */}
      {!permissionGranted && !dismissed && (
        <div className="mt-2 p-2 bg-blue-900/50 rounded-lg border border-blue-700/50 text-sm text-blue-300 flex items-center gap-2">
          <Lightbulb className="h-4 w-4" /> Activez les notifications pour ne jamais manquer la fin de période légale
        </div>
      )}
    </div>
  );
};

export default LegalTimeAlert;
