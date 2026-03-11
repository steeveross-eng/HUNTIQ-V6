/**
 * AlertNotificationCenter - Centre de notifications temps réel
 * ============================================================
 * PHASE F — NOTIFICATIONS PUSH
 * 
 * Composant pour gérer les notifications push et temps réel:
 * - Enregistrement Service Worker
 * - Abonnement Web Push (VAPID natif)
 * - Affichage des alertes en temps réel
 * - Historique des notifications
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { toast } from 'sonner';
import { 
  Bell,
  BellOff,
  BellRing,
  AlertTriangle,
  Users,
  MapPin,
  Shield,
  X,
  Check,
  RefreshCw,
  Volume2,
  VolumeX,
  ChevronDown
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

// =============================================================================
// UTILITAIRES
// =============================================================================

// Convertir base64 URL-safe en Uint8Array
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

// Icône selon le type d'alerte
const getAlertIcon = (alertType) => {
  switch (alertType) {
    case 'danger':
      return AlertTriangle;
    case 'human_pressure':
      return Users;
    case 'corridor_risk':
      return MapPin;
    case 'safety_update':
      return Shield;
    default:
      return Bell;
  }
};

// Couleur selon la priorité
const getPriorityColor = (priority) => {
  switch (priority) {
    case 'critical':
      return '#EF4444';
    case 'high':
      return '#F59E0B';
    case 'medium':
      return '#3B82F6';
    case 'low':
      return '#6B7280';
    default:
      return '#6B7280';
  }
};

// =============================================================================
// COMPOSANT PRINCIPAL
// =============================================================================

const AlertNotificationCenter = ({ position = 'bottom-right' }) => {
  // États
  const [isOpen, setIsOpen] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [subscriptionId, setSubscriptionId] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [swRegistration, setSwRegistration] = useState(null);
  
  // Ref pour le son
  const audioRef = useRef(null);

  // ==========================================================================
  // SERVICE WORKER
  // ==========================================================================

  const registerServiceWorker = useCallback(async () => {
    if (!('serviceWorker' in navigator)) {
      console.warn('Service Worker not supported');
      return null;
    }

    try {
      const registration = await navigator.serviceWorker.register('/sw-push.js');
      console.log('Service Worker registered:', registration.scope);
      setSwRegistration(registration);
      
      // Vérifier si déjà abonné
      const subscription = await registration.pushManager.getSubscription();
      if (subscription) {
        setIsSubscribed(true);
        console.log('Already subscribed to push');
      }
      
      return registration;
    } catch (error) {
      console.error('Service Worker registration failed:', error);
      return null;
    }
  }, []);

  // ==========================================================================
  // ABONNEMENT PUSH
  // ==========================================================================

  const subscribeToPush = async () => {
    if (!swRegistration) {
      toast.error('Service Worker non disponible');
      return;
    }

    setLoading(true);

    try {
      // Obtenir la clé VAPID
      const vapidResponse = await fetch(`${API_URL}/api/v1/bionic/notifications/vapid-key`);
      if (!vapidResponse.ok) throw new Error('Impossible d\'obtenir la clé VAPID');
      
      const { vapid_public_key } = await vapidResponse.json();

      // Demander la permission
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        toast.error('Permission de notification refusée');
        setLoading(false);
        return;
      }

      // S'abonner
      const subscription = await swRegistration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapid_public_key)
      });

      const subscriptionData = subscription.toJSON();

      // Obtenir la position
      let lat = null;
      let lng = null;
      
      if ('geolocation' in navigator) {
        try {
          const position = await new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 5000 });
          });
          lat = position.coords.latitude;
          lng = position.coords.longitude;
        } catch (e) {
          console.warn('Géolocalisation non disponible:', e);
        }
      }

      // Enregistrer sur le serveur
      const registerResponse = await fetch(`${API_URL}/api/v1/bionic/notifications/subscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          endpoint: subscriptionData.endpoint,
          p256dh: subscriptionData.keys.p256dh,
          auth: subscriptionData.keys.auth,
          device_type: 'web',
          lat,
          lng,
          geofence_radius_km: 5.0,
          alert_types: ['danger', 'human_pressure', 'corridor_risk', 'safety_update'],
          min_priority: 'medium'
        })
      });

      if (!registerResponse.ok) throw new Error('Échec de l\'enregistrement');

      const result = await registerResponse.json();
      setSubscriptionId(result.subscription?.subscription_id);
      setIsSubscribed(true);
      toast.success('Notifications activées !');

    } catch (error) {
      console.error('Subscription error:', error);
      toast.error('Erreur lors de l\'activation des notifications');
    } finally {
      setLoading(false);
    }
  };

  const unsubscribeFromPush = async () => {
    if (!swRegistration || !subscriptionId) return;

    setLoading(true);

    try {
      // Se désabonner côté navigateur
      const subscription = await swRegistration.pushManager.getSubscription();
      if (subscription) {
        await subscription.unsubscribe();
      }

      // Se désabonner côté serveur
      await fetch(`${API_URL}/api/v1/bionic/notifications/unsubscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subscription_id: subscriptionId })
      });

      setIsSubscribed(false);
      setSubscriptionId(null);
      toast.success('Notifications désactivées');

    } catch (error) {
      console.error('Unsubscribe error:', error);
      toast.error('Erreur lors de la désactivation');
    } finally {
      setLoading(false);
    }
  };

  // ==========================================================================
  // HISTORIQUE
  // ==========================================================================

  const fetchHistory = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/bionic/notifications/history?limit=20`);
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
        setUnreadCount(data.notifications?.filter(n => !n.read).length || 0);
      }
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  }, []);

  // ==========================================================================
  // EFFETS
  // ==========================================================================

  useEffect(() => {
    registerServiceWorker();
    fetchHistory();

    // Écouter les messages du Service Worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data?.type === 'NOTIFICATION_CLICKED') {
          // Notification cliquée - rafraîchir l'historique
          fetchHistory();
        }
      });
    }

    // Rafraîchir l'historique périodiquement
    const interval = setInterval(fetchHistory, 60000);
    return () => clearInterval(interval);
  }, [registerServiceWorker, fetchHistory]);

  // ==========================================================================
  // RENDU
  // ==========================================================================

  const positionClasses = {
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-right': 'top-20 right-4',
    'top-left': 'top-20 left-4'
  };

  return (
    <div className={`fixed ${positionClasses[position]} z-50`} data-testid="alert-notification-center">
      {/* Bouton principal */}
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={`w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all
            ${isSubscribed 
              ? 'bg-emerald-500 hover:bg-emerald-600' 
              : 'bg-slate-700 hover:bg-slate-600'}`}
          data-testid="notification-toggle"
        >
          {isSubscribed ? (
            <BellRing className="w-6 h-6 text-white" />
          ) : (
            <BellOff className="w-6 h-6 text-white" />
          )}
          
          {/* Badge de notifications non lues */}
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </button>
      </div>

      {/* Panneau déroulant */}
      {isOpen && (
        <div 
          className="absolute bottom-16 right-0 w-80 bg-slate-800 border border-slate-700 rounded-xl shadow-xl overflow-hidden"
          data-testid="notification-panel"
        >
          {/* Header */}
          <div className="p-4 border-b border-slate-700 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bell className="w-5 h-5 text-emerald-400" />
              <span className="font-semibold text-white">Alertes BIONIC V5</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setSoundEnabled(!soundEnabled)}
                className="p-1 hover:bg-slate-700 rounded"
                title={soundEnabled ? 'Désactiver le son' : 'Activer le son'}
              >
                {soundEnabled ? (
                  <Volume2 className="w-4 h-4 text-slate-400" />
                ) : (
                  <VolumeX className="w-4 h-4 text-slate-400" />
                )}
              </button>
              <button
                onClick={fetchHistory}
                className="p-1 hover:bg-slate-700 rounded"
                title="Rafraîchir"
              >
                <RefreshCw className="w-4 h-4 text-slate-400" />
              </button>
            </div>
          </div>

          {/* Statut d'abonnement */}
          <div className="p-3 bg-slate-900/50 border-b border-slate-700">
            {isSubscribed ? (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-emerald-400 text-sm">
                  <Check className="w-4 h-4" />
                  <span>Notifications activées</span>
                </div>
                <button
                  onClick={unsubscribeFromPush}
                  disabled={loading}
                  className="text-xs text-slate-400 hover:text-red-400 transition-colors"
                >
                  Désactiver
                </button>
              </div>
            ) : (
              <button
                onClick={subscribeToPush}
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg py-2 text-sm font-medium transition-colors"
                data-testid="enable-notifications-btn"
              >
                {loading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Bell className="w-4 h-4" />
                )}
                Activer les notifications
              </button>
            )}
          </div>

          {/* Liste des notifications */}
          <div className="max-h-80 overflow-y-auto">
            {notifications.length > 0 ? (
              notifications.slice(0, 10).map((notif) => {
                const Icon = getAlertIcon(notif.alert_type);
                const color = getPriorityColor(notif.priority);
                
                return (
                  <div
                    key={notif.notification_id}
                    className="p-3 border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors cursor-pointer"
                    data-testid={`notification-${notif.notification_id}`}
                  >
                    <div className="flex gap-3">
                      <div 
                        className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                        style={{ backgroundColor: `${color}20` }}
                      >
                        <Icon className="w-4 h-4" style={{ color }} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-white truncate">
                          {notif.content?.title}
                        </p>
                        <p className="text-xs text-slate-400 line-clamp-2">
                          {notif.content?.body}
                        </p>
                        <p className="text-xs text-slate-500 mt-1">
                          {new Date(notif.timestamps?.created_at).toLocaleString('fr-FR', {
                            hour: '2-digit',
                            minute: '2-digit',
                            day: 'numeric',
                            month: 'short'
                          })}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="p-8 text-center text-slate-500">
                <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Aucune notification</p>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="p-2 bg-slate-900/50 text-center">
            <span className="text-xs text-slate-500">PHASE F — Safety Engine Integration</span>
          </div>
        </div>
      )}

      {/* Audio pour les sons d'alerte */}
      <audio ref={audioRef} src="/sounds/alert.mp3" preload="auto" />
    </div>
  );
};

export default AlertNotificationCenter;
