/**
 * GeolocationService - Frontend service for background tracking and proximity alerts
 * Phase P4 - PWA Mobile Features
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

class GeolocationServiceClass {
  constructor() {
    this.watchId = null;
    this.isTracking = false;
    this.currentSession = null;
    this.lastPosition = null;
    this.trackingInterval = 5 * 60 * 1000; // 5 minutes
    this.intervalId = null;
    this.onAlertCallback = null;
    this.onPositionCallback = null;
  }

  /**
   * Check if geolocation is available
   */
  isSupported() {
    return 'geolocation' in navigator;
  }

  /**
   * Check if background sync is supported
   */
  isBackgroundSyncSupported() {
    return 'serviceWorker' in navigator && 'sync' in window.registration;
  }

  /**
   * Request permission for geolocation
   */
  async requestPermission() {
    if (!this.isSupported()) {
      return { granted: false, error: 'Géolocalisation non supportée' };
    }

    try {
      const result = await navigator.permissions.query({ name: 'geolocation' });
      return { 
        granted: result.state === 'granted',
        state: result.state,
        error: result.state === 'denied' ? 'Permission refusée' : null
      };
    } catch (error) {
      // Fallback for browsers that don't support permissions API
      return new Promise((resolve) => {
        navigator.geolocation.getCurrentPosition(
          () => resolve({ granted: true, state: 'granted' }),
          (err) => resolve({ 
            granted: false, 
            state: 'denied',
            error: err.message 
          })
        );
      });
    }
  }

  /**
   * Get current position
   */
  getCurrentPosition() {
    return new Promise((resolve, reject) => {
      if (!this.isSupported()) {
        reject(new Error('Géolocalisation non supportée'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const pos = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            altitude: position.coords.altitude,
            speed: position.coords.speed,
            heading: position.coords.heading,
            timestamp: new Date().toISOString()
          };
          this.lastPosition = pos;
          resolve(pos);
        },
        (error) => {
          reject(new Error(this._getGeolocationErrorMessage(error)));
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000
        }
      );
    });
  }

  /**
   * Start background tracking
   */
  async startTracking(options = {}) {
    if (this.isTracking) {
      console.log('[Geo] Already tracking');
      return { success: true, message: 'Tracking déjà actif' };
    }

    const permission = await this.requestPermission();
    if (!permission.granted) {
      return { success: false, error: permission.error };
    }

    try {
      // Start a tracking session on the server
      const sessionResponse = await fetch(`${API_URL}/api/v1/geolocation/session/start`, {
        method: 'POST'
      });
      
      if (sessionResponse.ok) {
        const data = await sessionResponse.json();
        this.currentSession = data.session;
      }

      // Start watching position
      this.watchId = navigator.geolocation.watchPosition(
        (position) => this._handlePositionUpdate(position),
        (error) => this._handlePositionError(error),
        {
          enableHighAccuracy: true,
          timeout: 30000,
          maximumAge: 0
        }
      );

      // Set up interval for periodic updates
      this.intervalId = setInterval(() => {
        this._sendPositionToServer();
      }, this.trackingInterval);

      this.isTracking = true;

      // Notify service worker
      this._notifyServiceWorker('START_TRACKING', {
        interval: this.trackingInterval,
        sessionId: this.currentSession?.id
      });

      console.log('[Geo] Background tracking started');
      return { 
        success: true, 
        session: this.currentSession,
        message: 'Tracking en arrière-plan démarré'
      };
    } catch (error) {
      console.error('[Geo] Error starting tracking:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Stop background tracking
   */
  async stopTracking() {
    if (!this.isTracking) {
      return { success: true, message: 'Tracking déjà arrêté' };
    }

    // Stop watching position
    if (this.watchId !== null) {
      navigator.geolocation.clearWatch(this.watchId);
      this.watchId = null;
    }

    // Clear interval
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }

    // End session on server
    let sessionStats = null;
    if (this.currentSession?.id) {
      try {
        const response = await fetch(
          `${API_URL}/api/v1/geolocation/session/${this.currentSession.id}/end`,
          { method: 'POST' }
        );
        if (response.ok) {
          const data = await response.json();
          sessionStats = data.session;
        }
      } catch (error) {
        console.error('[Geo] Error ending session:', error);
      }
    }

    this.isTracking = false;
    this.currentSession = null;

    // Notify service worker
    this._notifyServiceWorker('STOP_TRACKING');

    console.log('[Geo] Background tracking stopped');
    return { 
      success: true, 
      session: sessionStats,
      message: 'Tracking arrêté'
    };
  }

  /**
   * Get tracking status
   */
  async getStatus() {
    try {
      const response = await fetch(`${API_URL}/api/v1/geolocation/tracking-status`);
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error('[Geo] Error getting status:', error);
    }

    return {
      tracking_active: this.isTracking,
      session_id: this.currentSession?.id,
      push_enabled: await this._checkPushSubscription(),
      local_tracking: this.isTracking
    };
  }

  /**
   * Get location history
   */
  async getHistory(options = {}) {
    try {
      const params = new URLSearchParams();
      if (options.sessionId) params.append('session_id', options.sessionId);
      if (options.limit) params.append('limit', options.limit);

      const response = await fetch(`${API_URL}/api/v1/geolocation/history?${params}`);
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error('[Geo] Error getting history:', error);
    }
    return [];
  }

  /**
   * Get nearby hotspots
   */
  async getNearbyHotspots(lat, lng, radiusKm = 5) {
    try {
      const response = await fetch(
        `${API_URL}/api/v1/geolocation/nearby-hotspots?lat=${lat}&lng=${lng}&radius_km=${radiusKm}`
      );
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error('[Geo] Error getting nearby hotspots:', error);
    }
    return { hotspots: [], count: 0 };
  }

  /**
   * Manual proximity check
   */
  async checkProximity(lat, lng) {
    try {
      const response = await fetch(
        `${API_URL}/api/v1/geolocation/check-proximity?lat=${lat}&lng=${lng}`,
        { method: 'POST' }
      );
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error('[Geo] Error checking proximity:', error);
    }
    return { alerts: [], has_alerts: false };
  }

  /**
   * Subscribe to push notifications
   */
  async subscribeToPush() {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
      return { success: false, error: 'Push notifications non supportées' };
    }

    try {
      const registration = await navigator.serviceWorker.ready;
      
      // Get existing subscription or create new one
      let subscription = await registration.pushManager.getSubscription();
      
      if (!subscription) {
        // Real VAPID public key from backend
        subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: this._urlBase64ToUint8Array(
            'BKWDsiVqbayHSLkU66o-BXYFPBOprvye4JowMEcEGY2iwxShqB3IZrWYejj14kuloYiFN5jBbEqsDaDVz3EirjE'
          )
        });
      }

      // Send subscription to server
      const response = await fetch(`${API_URL}/api/v1/geolocation/subscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          endpoint: subscription.endpoint,
          keys: {
            p256dh: this._arrayBufferToBase64(subscription.getKey('p256dh')),
            auth: this._arrayBufferToBase64(subscription.getKey('auth'))
          }
        })
      });

      if (response.ok) {
        return { success: true, message: 'Notifications push activées' };
      }
    } catch (error) {
      console.error('[Geo] Push subscription error:', error);
      return { success: false, error: error.message };
    }

    return { success: false, error: 'Erreur d\'inscription' };
  }

  /**
   * Unsubscribe from push notifications
   */
  async unsubscribeFromPush() {
    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();
      
      if (subscription) {
        await subscription.unsubscribe();
      }

      await fetch(`${API_URL}/api/v1/geolocation/subscribe`, {
        method: 'DELETE'
      });

      return { success: true, message: 'Notifications désactivées' };
    } catch (error) {
      console.error('[Geo] Unsubscribe error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Set callback for proximity alerts
   */
  onAlert(callback) {
    this.onAlertCallback = callback;
  }

  /**
   * Set callback for position updates
   */
  onPosition(callback) {
    this.onPositionCallback = callback;
  }

  // Private methods

  _handlePositionUpdate(position) {
    const pos = {
      latitude: position.coords.latitude,
      longitude: position.coords.longitude,
      accuracy: position.coords.accuracy,
      altitude: position.coords.altitude,
      speed: position.coords.speed,
      heading: position.coords.heading,
      timestamp: new Date().toISOString()
    };

    this.lastPosition = pos;

    if (this.onPositionCallback) {
      this.onPositionCallback(pos);
    }

    // Notify service worker
    this._notifyServiceWorker('RECORD_LOCATION', pos);
  }

  _handlePositionError(error) {
    console.error('[Geo] Position error:', this._getGeolocationErrorMessage(error));
  }

  async _sendPositionToServer() {
    if (!this.lastPosition) return;

    try {
      const response = await fetch(`${API_URL}/api/v1/geolocation/location`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...this.lastPosition,
          session_id: this.currentSession?.id
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        // Handle proximity alerts
        if (data.alerts && data.alerts.length > 0 && this.onAlertCallback) {
          data.alerts.forEach(alert => this.onAlertCallback(alert));
        }
      }
    } catch (error) {
      console.error('[Geo] Error sending position:', error);
      // Service worker will handle offline sync
    }
  }

  _notifyServiceWorker(type, data = {}) {
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage({ type, data });
    }
  }

  async _checkPushSubscription() {
    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();
      return subscription !== null;
    } catch {
      return false;
    }
  }

  _getGeolocationErrorMessage(error) {
    switch (error.code) {
      case error.PERMISSION_DENIED:
        return 'Permission de géolocalisation refusée';
      case error.POSITION_UNAVAILABLE:
        return 'Position non disponible';
      case error.TIMEOUT:
        return 'Délai d\'attente dépassé';
      default:
        return 'Erreur de géolocalisation';
    }
  }

  _urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  _arrayBufferToBase64(buffer) {
    if (!buffer) return '';
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
  }
}

// Export singleton instance
export const GeolocationService = new GeolocationServiceClass();
export default GeolocationService;
