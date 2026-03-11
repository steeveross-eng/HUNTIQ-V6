/**
 * BackgroundTracker - Component for managing background geolocation tracking
 * Phase P4 - PWA Mobile Features
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Progress } from '@/components/ui/progress';
import { toast } from 'sonner';
import { 
  MapPin, Navigation, Play, Square, Bell, BellOff, 
  Satellite, Activity, Clock, Route, Target, Loader2,
  CheckCircle, XCircle, AlertTriangle
} from 'lucide-react';
import { GeolocationService } from '@/services/GeolocationService';

const BackgroundTracker = ({ onProximityAlert }) => {
  const [isTracking, setIsTracking] = useState(false);
  const [isPushEnabled, setIsPushEnabled] = useState(false);
  const [currentPosition, setCurrentPosition] = useState(null);
  const [sessionStats, setSessionStats] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [permissionState, setPermissionState] = useState('prompt');

  // Check initial status
  useEffect(() => {
    checkStatus();
    checkPermission();
    
    // Set up callbacks
    GeolocationService.onPosition((pos) => {
      setCurrentPosition(pos);
    });

    GeolocationService.onAlert((alert) => {
      handleProximityAlert(alert);
    });

    // Listen for service worker messages
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('message', handleSWMessage);
    }

    return () => {
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.removeEventListener('message', handleSWMessage);
      }
    };
  }, []);

  const handleSWMessage = useCallback((event) => {
    const { type, alerts } = event.data || {};
    
    if (type === 'PROXIMITY_ALERTS' && alerts) {
      alerts.forEach(alert => handleProximityAlert(alert));
    }
    if (type === 'TRACKING_STARTED') {
      setIsTracking(true);
    }
    if (type === 'TRACKING_STOPPED') {
      setIsTracking(false);
    }
  }, []);

  const handleProximityAlert = (alert) => {
    // Show toast notification
    const isHotspot = alert.classification === 'hotspot';
    toast(isHotspot ? 'Hotspot Détecté!' : 'Waypoint Proche', {
      description: alert.message,
      duration: 10000,
      action: {
        label: 'Voir',
        onClick: () => window.location.href = `/map?highlight=${alert.waypoint_id}`
      }
    });

    // Call parent callback if provided
    if (onProximityAlert) {
      onProximityAlert(alert);
    }
  };

  const checkStatus = async () => {
    const statusData = await GeolocationService.getStatus();
    setStatus(statusData);
    // Only use backend tracking_active status, not local state
    setIsTracking(statusData.tracking_active);
    setIsPushEnabled(statusData.push_enabled);
  };

  const checkPermission = async () => {
    const result = await GeolocationService.requestPermission();
    setPermissionState(result.state || (result.granted ? 'granted' : 'denied'));
  };

  const handleStartTracking = async () => {
    setLoading(true);
    const result = await GeolocationService.startTracking();
    setLoading(false);

    if (result.success) {
      setIsTracking(true);
      setSessionStats(result.session);
      toast.success('Tracking démarré', {
        description: 'Votre position sera enregistrée toutes les 5 minutes'
      });
    } else {
      toast.error('Erreur', { description: result.error });
    }
  };

  const handleStopTracking = async () => {
    setLoading(true);
    const result = await GeolocationService.stopTracking();
    setLoading(false);

    if (result.success) {
      setIsTracking(false);
      if (result.session) {
        setSessionStats(result.session);
        toast.success('Tracking arrêté', {
          description: `Distance parcourue: ${result.session.distance_km} km`
        });
      }
    } else {
      toast.error('Erreur', { description: result.error });
    }
  };

  const handleTogglePush = async () => {
    setLoading(true);
    
    if (isPushEnabled) {
      const result = await GeolocationService.unsubscribeFromPush();
      if (result.success) {
        setIsPushEnabled(false);
        toast.success('Notifications désactivées');
      } else {
        toast.error('Erreur', { description: result.error });
      }
    } else {
      const result = await GeolocationService.subscribeToPush();
      if (result.success) {
        setIsPushEnabled(true);
        toast.success('Notifications activées', {
          description: 'Vous recevrez des alertes de proximité'
        });
      } else {
        toast.error('Erreur', { description: result.error });
      }
    }
    
    setLoading(false);
  };

  const handleGetCurrentPosition = async () => {
    setLoading(true);
    try {
      const pos = await GeolocationService.getCurrentPosition();
      setCurrentPosition(pos);
      toast.success('Position obtenue', {
        description: `${pos.latitude.toFixed(4)}, ${pos.longitude.toFixed(4)}`
      });
    } catch (error) {
      toast.error('Erreur', { description: error.message });
    }
    setLoading(false);
  };

  const PermissionBadge = () => {
    switch (permissionState) {
      case 'granted':
        return <Badge className="bg-green-600"><CheckCircle className="h-3 w-3 mr-1" /> Autorisé</Badge>;
      case 'denied':
        return <Badge className="bg-red-600"><XCircle className="h-3 w-3 mr-1" /> Refusé</Badge>;
      default:
        return <Badge className="bg-yellow-600"><AlertTriangle className="h-3 w-3 mr-1" /> En attente</Badge>;
    }
  };

  return (
    <Card className="bg-gray-900/50 border-gray-800" data-testid="background-tracker">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-white flex items-center gap-2">
              <Satellite className="h-5 w-5 text-cyan-400" />
              Tracking GPS
            </CardTitle>
            <CardDescription>Suivi en arrière-plan & alertes de proximité</CardDescription>
          </div>
          <PermissionBadge />
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Status Section */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-800/50 rounded-lg p-4">
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-2">
              <Navigation className="h-4 w-4" />
              Statut Tracking
            </div>
            <div className="flex items-center gap-2">
              {isTracking ? (
                <>
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-green-400 font-medium">Actif</span>
                </>
              ) : (
                <>
                  <div className="w-2 h-2 rounded-full bg-gray-500" />
                  <span className="text-gray-400">Inactif</span>
                </>
              )}
            </div>
          </div>

          <div className="bg-gray-800/50 rounded-lg p-4">
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-2">
              <Bell className="h-4 w-4" />
              Notifications Push
            </div>
            <div className="flex items-center gap-2">
              {isPushEnabled ? (
                <>
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <span className="text-green-400 font-medium">Activées</span>
                </>
              ) : (
                <>
                  <div className="w-2 h-2 rounded-full bg-gray-500" />
                  <span className="text-gray-400">Désactivées</span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Current Position */}
        {currentPosition && (
          <div className="bg-gray-800/50 rounded-lg p-4">
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-2">
              <MapPin className="h-4 w-4 text-cyan-400" />
              Position Actuelle
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Latitude:</span>
                <span className="text-white ml-2">{currentPosition.latitude.toFixed(6)}</span>
              </div>
              <div>
                <span className="text-gray-500">Longitude:</span>
                <span className="text-white ml-2">{currentPosition.longitude.toFixed(6)}</span>
              </div>
              {currentPosition.accuracy && (
                <div>
                  <span className="text-gray-500">Précision:</span>
                  <span className="text-white ml-2">{Math.round(currentPosition.accuracy)}m</span>
                </div>
              )}
              {currentPosition.speed && (
                <div>
                  <span className="text-gray-500">Vitesse:</span>
                  <span className="text-white ml-2">{(currentPosition.speed * 3.6).toFixed(1)} km/h</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Session Stats */}
        {sessionStats && (
          <div className="bg-gray-800/50 rounded-lg p-4">
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-2">
              <Route className="h-4 w-4 text-amber-400" />
              Session de Chasse
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Points:</span>
                <span className="text-white ml-2">{sessionStats.locations_count || 0}</span>
              </div>
              <div>
                <span className="text-gray-500">Distance:</span>
                <span className="text-white ml-2">{sessionStats.distance_km || 0} km</span>
              </div>
            </div>
          </div>
        )}

        {/* Controls */}
        <div className="space-y-4">
          {/* Tracking Toggle */}
          <div className="flex items-center justify-between bg-gray-800/50 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <Activity className="h-5 w-5 text-cyan-400" />
              <div>
                <div className="text-white font-medium">Tracking Arrière-plan</div>
                <div className="text-gray-400 text-sm">Mise à jour toutes les 5 min</div>
              </div>
            </div>
            <Button
              variant={isTracking ? "destructive" : "default"}
              size="sm"
              onClick={isTracking ? handleStopTracking : handleStartTracking}
              disabled={loading || permissionState === 'denied'}
              data-testid="toggle-tracking-btn"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : isTracking ? (
                <>
                  <Square className="h-4 w-4 mr-2" /> Arrêter
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" /> Démarrer
                </>
              )}
            </Button>
          </div>

          {/* Push Notifications Toggle */}
          <div className="flex items-center justify-between bg-gray-800/50 rounded-lg p-4">
            <div className="flex items-center gap-3">
              {isPushEnabled ? (
                <Bell className="h-5 w-5 text-amber-400" />
              ) : (
                <BellOff className="h-5 w-5 text-gray-400" />
              )}
              <div>
                <div className="text-white font-medium">Alertes de Proximité</div>
                <div className="text-gray-400 text-sm">Notifications waypoints proches</div>
              </div>
            </div>
            <Switch
              checked={isPushEnabled}
              onCheckedChange={handleTogglePush}
              disabled={loading}
              data-testid="toggle-push-switch"
            />
          </div>

          {/* Get Position Button */}
          <Button
            variant="outline"
            className="w-full"
            onClick={handleGetCurrentPosition}
            disabled={loading || permissionState === 'denied'}
            data-testid="get-position-btn"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Target className="h-4 w-4 mr-2" />
            )}
            Obtenir Ma Position
          </Button>
        </div>

        {/* Permission Warning */}
        {permissionState === 'denied' && (
          <div className="bg-red-900/30 border border-red-800 rounded-lg p-4 flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <div className="text-red-400 font-medium">Permission Refusée</div>
              <div className="text-gray-400 text-sm mt-1">
                Activez la géolocalisation dans les paramètres de votre navigateur pour utiliser le tracking GPS.
              </div>
            </div>
          </div>
        )}

        {/* Feature Info */}
        <div className="text-xs text-gray-500 space-y-1">
          <p>• Le tracking en arrière-plan enregistre votre position toutes les 5 minutes</p>
          <p>• Les alertes de proximité vous avertissent à 500m d'un waypoint</p>
          <p>• Les hotspots déclenchent une alerte à 700m</p>
        </div>
      </CardContent>
    </Card>
  );
};

export default BackgroundTracker;
