// Service Worker pour les notifications push BIONIC V5
// PHASE F — VAPID Natif — 100% Autonome

const CACHE_NAME = 'bionic-v5-cache-v1';

// Installation du Service Worker
self.addEventListener('install', (event) => {
  console.log('[BIONIC SW] Installing...');
  self.skipWaiting();
});

// Activation
self.addEventListener('activate', (event) => {
  console.log('[BIONIC SW] Activated');
  event.waitUntil(self.clients.claim());
});

// Réception d'une notification push
self.addEventListener('push', (event) => {
  console.log('[BIONIC SW] Push received');
  
  if (!event.data) {
    console.log('[BIONIC SW] No data in push event');
    return;
  }

  try {
    const data = event.data.json();
    const notification = data.notification;
    
    const options = {
      body: notification.body,
      icon: notification.icon || '/icons/bionic-alert.png',
      badge: notification.badge || '/icons/bionic-badge.png',
      tag: notification.tag,
      data: notification.data,
      actions: notification.actions || [
        { action: 'view', title: 'Voir' },
        { action: 'dismiss', title: 'Ignorer' }
      ],
      requireInteraction: notification.requireInteraction || false,
      vibrate: notification.vibrate || [100]
    };

    event.waitUntil(
      self.registration.showNotification(notification.title, options)
    );
    
    console.log('[BIONIC SW] Notification displayed:', notification.title);
    
  } catch (error) {
    console.error('[BIONIC SW] Error parsing push data:', error);
  }
});

// Clic sur une notification
self.addEventListener('notificationclick', (event) => {
  console.log('[BIONIC SW] Notification clicked:', event.action);
  
  event.notification.close();
  
  const data = event.notification.data || {};
  
  if (event.action === 'dismiss') {
    // Ignorer - notification déjà fermée
    return;
  }
  
  // Ouvrir l'URL associée ou la page par défaut
  const urlToOpen = data.url || '/';
  
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        // Chercher si une fenêtre est déjà ouverte
        for (const client of clientList) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            client.postMessage({
              type: 'NOTIFICATION_CLICKED',
              notification_id: data.notification_id,
              alert_type: data.alert_type,
              url: urlToOpen
            });
            return client.focus();
          }
        }
        // Sinon ouvrir une nouvelle fenêtre
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      })
  );
});

// Fermeture d'une notification
self.addEventListener('notificationclose', (event) => {
  console.log('[BIONIC SW] Notification closed');
  
  const data = event.notification.data || {};
  
  // Optionnel: envoyer une analytique
  if (data.notification_id) {
    console.log('[BIONIC SW] Notification dismissed:', data.notification_id);
  }
});

// Message du client principal
self.addEventListener('message', (event) => {
  console.log('[BIONIC SW] Message received:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

console.log('[BIONIC SW] Service Worker loaded - BIONIC V5 PHASE F');
