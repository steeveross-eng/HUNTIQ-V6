const CACHE_NAME = 'bionic-hunt-cache-v4';
const OFFLINE_URL = '/offline.html';

// Assets to cache immediately on install
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/offline.html',
  '/manifest.json',
  '/logos/bionic-logo.svg'
];

// API routes to cache with network-first strategy
const API_CACHE_ROUTES = [
  '/api/user/waypoints',
  '/api/v1/waypoint-scoring/wqs',
  '/api/v1/waypoint-scoring/forecast/quick',
  '/api/v1/analytics/overview',
  '/api/v1/legal-time/legal-window'
];

// Background geolocation config
const GEOLOCATION_CONFIG = {
  interval: 5 * 60 * 1000, // 5 minutes
  enabled: false,
  lastPosition: null
};

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing Service Worker v2...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating Service Worker v2...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => {
            console.log('[SW] Deleting old cache:', name);
            return caches.delete(name);
          })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - handle requests
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') return;

  // Skip external requests
  if (url.origin !== location.origin) return;

  // API requests - Network first, cache fallback
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstStrategy(request));
    return;
  }

  // JavaScript and CSS bundles - ALWAYS network first (critical for code updates)
  if (url.pathname.startsWith('/static/js/') || url.pathname.startsWith('/static/css/')) {
    event.respondWith(networkFirstStrategy(request));
    return;
  }

  // Navigation requests - Network first (ensures fresh HTML)
  if (request.mode === 'navigate') {
    event.respondWith(networkFirstStrategy(request));
    return;
  }

  // Other static assets (images, fonts, logos) - Cache first, network fallback
  event.respondWith(cacheFirstStrategy(request));
});

// Cache-first strategy for static assets
async function cacheFirstStrategy(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      const offlineResponse = await caches.match(OFFLINE_URL);
      if (offlineResponse) return offlineResponse;
    }
    throw error;
  }
}

// Network-first strategy for API requests
async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      // Cache successful API responses
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    // Return cached response if network fails
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      console.log('[SW] Returning cached API response:', request.url);
      return cachedResponse;
    }
    
    // Return offline JSON for API requests
    return new Response(
      JSON.stringify({ 
        offline: true, 
        error: 'Vous êtes hors ligne',
        cached_at: null 
      }),
      { 
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Background sync for deferred actions
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync:', event.tag);
  if (event.tag === 'sync-waypoints') {
    event.waitUntil(syncWaypoints());
  }
  if (event.tag === 'sync-locations') {
    event.waitUntil(syncPendingLocations());
  }
});

// Sync waypoints when back online
async function syncWaypoints() {
  try {
    const db = await openIndexedDB();
    const pendingActions = await getPendingActions(db);
    
    for (const action of pendingActions) {
      try {
        await fetch(action.url, {
          method: action.method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(action.data)
        });
        await removePendingAction(db, action.id);
        console.log('[SW] Synced action:', action.id);
      } catch (error) {
        console.error('[SW] Failed to sync action:', action.id);
      }
    }
  } catch (error) {
    console.error('[SW] Sync error:', error);
  }
}

// Sync pending location updates
async function syncPendingLocations() {
  try {
    const db = await openIndexedDB();
    const pendingLocations = await getPendingLocations(db);
    
    for (const loc of pendingLocations) {
      try {
        const response = await fetch('/api/v1/geolocation/location', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(loc.data)
        });
        
        if (response.ok) {
          await removePendingLocation(db, loc.id);
          console.log('[SW] Synced location:', loc.id);
          
          // Check for alerts in response
          const result = await response.json();
          if (result.alerts && result.alerts.length > 0) {
            for (const alert of result.alerts) {
              await showProximityNotification(alert);
            }
          }
        }
      } catch (error) {
        console.error('[SW] Failed to sync location:', loc.id);
      }
    }
  } catch (error) {
    console.error('[SW] Location sync error:', error);
  }
}

// IndexedDB helpers
function openIndexedDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('huntiq-offline', 2);
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('pending-actions')) {
        db.createObjectStore('pending-actions', { keyPath: 'id', autoIncrement: true });
      }
      if (!db.objectStoreNames.contains('cached-data')) {
        db.createObjectStore('cached-data', { keyPath: 'key' });
      }
      if (!db.objectStoreNames.contains('pending-locations')) {
        db.createObjectStore('pending-locations', { keyPath: 'id', autoIncrement: true });
      }
      if (!db.objectStoreNames.contains('geolocation-config')) {
        db.createObjectStore('geolocation-config', { keyPath: 'key' });
      }
    };
  });
}

function getPendingActions(db) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction('pending-actions', 'readonly');
    const store = transaction.objectStore('pending-actions');
    const request = store.getAll();
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
  });
}

function removePendingAction(db, id) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction('pending-actions', 'readwrite');
    const store = transaction.objectStore('pending-actions');
    const request = store.delete(id);
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve();
  });
}

function getPendingLocations(db) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction('pending-locations', 'readonly');
    const store = transaction.objectStore('pending-locations');
    const request = store.getAll();
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
  });
}

function removePendingLocation(db, id) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction('pending-locations', 'readwrite');
    const store = transaction.objectStore('pending-locations');
    const request = store.delete(id);
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve();
  });
}

async function savePendingLocation(location) {
  try {
    const db = await openIndexedDB();
    return new Promise((resolve, reject) => {
      const transaction = db.transaction('pending-locations', 'readwrite');
      const store = transaction.objectStore('pending-locations');
      const request = store.add({
        data: location,
        timestamp: new Date().toISOString()
      });
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  } catch (error) {
    console.error('[SW] Error saving pending location:', error);
  }
}

// Push notifications - Enhanced for proximity alerts
self.addEventListener('push', (event) => {
  if (!event.data) return;
  
  let data;
  try {
    data = event.data.json();
  } catch (e) {
    data = { title: 'BIONIC HUNT/Chasse', body: event.data.text() };
  }
  
  const options = {
    body: data.body || 'Nouvelle notification BIONIC HUNT/Chasse',
    icon: data.icon || '/logos/bionic-logo.svg',
    badge: '/logos/bionic-logo.svg',
    vibrate: data.vibrate || [200, 100, 200],
    tag: data.tag || 'huntiq-notification',
    renotify: true,
    requireInteraction: data.requireInteraction || false,
    data: data,
    actions: data.actions || [
      { action: 'open', title: 'Ouvrir', icon: '/logos/bionic-logo.svg' },
      { action: 'dismiss', title: 'Fermer' }
    ]
  };
  
  // Add image for proximity alerts
  if (data.type === 'proximity' && data.image) {
    options.image = data.image;
  }
  
  event.waitUntil(
    self.registration.showNotification(data.title || 'BIONIC HUNT/Chasse', options)
  );
});

// Show proximity notification
async function showProximityNotification(alert) {
  const options = {
    body: alert.message,
    icon: '/logos/bionic-logo.svg',
    badge: '/logos/bionic-logo.svg',
    vibrate: alert.classification === 'hotspot' ? [200, 100, 200, 100, 200] : [200, 100, 200],
    tag: `proximity-${alert.waypoint_id}`,
    renotify: true,
    requireInteraction: alert.classification === 'hotspot',
    data: {
      type: 'proximity',
      waypoint_id: alert.waypoint_id,
      waypoint_name: alert.waypoint_name,
      url: `/map?highlight=${alert.waypoint_id}`
    },
    actions: [
      { action: 'navigate', title: 'Voir sur carte' },
      { action: 'dismiss', title: 'Ignorer' }
    ]
  };
  
  await self.registration.showNotification(
    alert.classification === 'hotspot' ? '🔥 Hotspot Détecté!' : '📍 Waypoint Proche',
    options
  );
}

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  const data = event.notification.data || {};
  let targetUrl = '/';
  
  if (event.action === 'navigate' || event.action === 'open') {
    targetUrl = data.url || '/';
  } else if (event.action === 'dismiss') {
    return; // Just close
  } else {
    // Default click - open the relevant page
    targetUrl = data.url || '/';
  }
  
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((windowClients) => {
        // Check if there's already a window open
        for (const client of windowClients) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            client.navigate(targetUrl);
            return client.focus();
          }
        }
        // Open new window if none exists
        if (clients.openWindow) {
          return clients.openWindow(targetUrl);
        }
      })
  );
});

// Message handler for communication with main app
self.addEventListener('message', (event) => {
  const { type, data } = event.data || {};
  
  switch (type) {
    case 'START_TRACKING':
      startBackgroundTracking(data);
      break;
    case 'STOP_TRACKING':
      stopBackgroundTracking();
      break;
    case 'RECORD_LOCATION':
      handleLocationUpdate(data);
      break;
    case 'CHECK_TRACKING_STATUS':
      event.ports[0].postMessage({
        tracking: GEOLOCATION_CONFIG.enabled,
        lastPosition: GEOLOCATION_CONFIG.lastPosition
      });
      break;
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
    default:
      console.log('[SW] Unknown message type:', type);
  }
});

// Background tracking control
function startBackgroundTracking(config = {}) {
  GEOLOCATION_CONFIG.enabled = true;
  GEOLOCATION_CONFIG.interval = config.interval || 5 * 60 * 1000;
  console.log('[SW] Background tracking started');
  
  // Notify all clients
  notifyClients({ type: 'TRACKING_STARTED' });
}

function stopBackgroundTracking() {
  GEOLOCATION_CONFIG.enabled = false;
  console.log('[SW] Background tracking stopped');
  
  // Notify all clients
  notifyClients({ type: 'TRACKING_STOPPED' });
}

// Handle location update from main app
async function handleLocationUpdate(location) {
  if (!GEOLOCATION_CONFIG.enabled) return;
  
  GEOLOCATION_CONFIG.lastPosition = {
    ...location,
    timestamp: new Date().toISOString()
  };
  
  try {
    // Try to send to server
    const response = await fetch('/api/v1/geolocation/location', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        latitude: location.latitude,
        longitude: location.longitude,
        accuracy: location.accuracy,
        altitude: location.altitude,
        speed: location.speed,
        heading: location.heading,
        timestamp: new Date().toISOString()
      })
    });
    
    if (response.ok) {
      const result = await response.json();
      
      // Handle proximity alerts
      if (result.alerts && result.alerts.length > 0) {
        for (const alert of result.alerts) {
          await showProximityNotification(alert);
        }
        
        // Notify main app about alerts
        notifyClients({
          type: 'PROXIMITY_ALERTS',
          alerts: result.alerts
        });
      }
    }
  } catch (error) {
    console.log('[SW] Offline - saving location for later sync');
    await savePendingLocation(location);
    
    // Request background sync when online
    if ('sync' in self.registration) {
      await self.registration.sync.register('sync-locations');
    }
  }
}

// Notify all clients
async function notifyClients(message) {
  const allClients = await clients.matchAll({ includeUncontrolled: true });
  for (const client of allClients) {
    client.postMessage(message);
  }
}

// Periodic background sync (if supported)
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'background-location-sync') {
    event.waitUntil(syncPendingLocations());
  }
});

console.log('[SW] Service Worker v2 loaded - BIONIC HUNT/Chasse V3 PWA with Geolocation');
