/**
 * NotificationService - API client for notification endpoints
 * Handles legal time alerts and push notification management
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export class NotificationService {
  /**
   * Get current legal time status for notifications
   */
  static async getLegalTimeStatus(lat = 46.8139, lng = -71.2080) {
    try {
      const params = new URLSearchParams({ lat, lng });
      const response = await fetch(`${API_URL}/api/v1/notification/legal-time/status?${params}`);
      if (!response.ok) return { success: false, warning_active: false };
      return response.json();
    } catch {
      return { success: false, warning_active: false };
    }
  }

  /**
   * Get upcoming legal time notifications
   */
  static async getUpcomingAlerts(lat = 46.8139, lng = -71.2080, hours = 24) {
    try {
      const params = new URLSearchParams({ lat, lng, hours });
      const response = await fetch(`${API_URL}/api/v1/notification/legal-time/upcoming?${params}`);
      if (!response.ok) return { success: false, notifications: [] };
      return response.json();
    } catch {
      return { success: false, notifications: [] };
    }
  }

  /**
   * Request browser notification permission
   */
  static async requestPermission() {
    if (!('Notification' in window)) {
      console.log('Browser does not support notifications');
      return 'unsupported';
    }

    if (Notification.permission === 'granted') {
      return 'granted';
    }

    if (Notification.permission !== 'denied') {
      const permission = await Notification.requestPermission();
      return permission;
    }

    return Notification.permission;
  }

  /**
   * Send a browser notification
   */
  static sendBrowserNotification(title, options = {}) {
    if (!('Notification' in window) || Notification.permission !== 'granted') {
      return null;
    }

    const defaultOptions = {
      icon: '/logo192.png',
      badge: '/logo192.png',
      vibrate: [200, 100, 200],
      tag: 'huntiq-alert',
      requireInteraction: true,
      ...options
    };

    return new Notification(title, defaultOptions);
  }

  /**
   * Send legal time warning notification (browser + in-app)
   */
  static sendLegalTimeWarning(minutesRemaining, legalEndTime) {
    const title = minutesRemaining <= 5 
      ? `URGENT: ${minutesRemaining} min restantes!`
      : `${minutesRemaining} min avant fin de chasse`;
    
    const body = `La période légale se termine à ${legalEndTime}. Préparez-vous à terminer votre chasse.`;
    
    // Send browser notification
    this.sendBrowserNotification(title, {
      body,
      tag: 'legal-time-warning',
      data: { type: 'legal_time_warning', minutesRemaining, legalEndTime }
    });

    return { title, body };
  }

  /**
   * Register service worker for push notifications
   */
  static async registerServiceWorker() {
    if (!('serviceWorker' in navigator)) {
      return null;
    }

    try {
      const registration = await navigator.serviceWorker.register('/sw.js');
      return registration;
    } catch (error) {
      console.error('Service worker registration failed:', error);
      return null;
    }
  }

  /**
   * Subscribe to push notifications
   */
  static async subscribeToPush(userId) {
    const registration = await this.registerServiceWorker();
    if (!registration) return null;

    try {
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.urlBase64ToUint8Array(process.env.REACT_APP_VAPID_PUBLIC_KEY)
      });

      // Send subscription to backend
      const response = await fetch(`${API_URL}/api/v1/notification/subscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          endpoint: subscription.endpoint,
          keys: {
            p256dh: btoa(String.fromCharCode(...new Uint8Array(subscription.getKey('p256dh')))),
            auth: btoa(String.fromCharCode(...new Uint8Array(subscription.getKey('auth'))))
          }
        })
      });

      return response.json();
    } catch (error) {
      console.error('Push subscription failed:', error);
      return null;
    }
  }

  /**
   * Helper to convert VAPID key
   */
  static urlBase64ToUint8Array(base64String) {
    if (!base64String) return new Uint8Array();
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    return Uint8Array.from([...rawData].map(char => char.charCodeAt(0)));
  }
}

export default NotificationService;
