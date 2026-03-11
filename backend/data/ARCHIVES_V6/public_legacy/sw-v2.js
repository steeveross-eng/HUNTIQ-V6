/**
 * Service Worker V2 - BRANCHE 3 (99% → 99.9%)
 * 
 * Stratégies de caching avancées pour performance optimale
 * - Stale-while-revalidate pour assets statiques
 * - Network-first avec cache fallback pour API
 * - Préchargement intelligent des routes critiques
 * - Background sync pour données hors-ligne
 * 
 * @version 2.0.0
 * @phase BRANCHE_3
 */

const SW_VERSION = '5.0.0';
const CACHE_PREFIX = 'huntiq-bionic-v5';

// Cache names with versioning — v5 forces FULL cache invalidation (fixes reload loop from v4)
const CACHES = {
  static: `${CACHE_PREFIX}-static-v5`,
  images: `${CACHE_PREFIX}-images-v5`,
  api: `${CACHE_PREFIX}-api-v5`,
  fonts: `${CACHE_PREFIX}-fonts-v5`,
  pages: `${CACHE_PREFIX}-pages-v5`
};

// Cache TTLs (in milliseconds)
const CACHE_TTL = {
  static: 7 * 24 * 60 * 60 * 1000, // 7 days
  images: 30 * 24 * 60 * 60 * 1000, // 30 days
  api: 5 * 60 * 1000, // 5 minutes
  fonts: 365 * 24 * 60 * 60 * 1000, // 1 year
  pages: 24 * 60 * 60 * 1000 // 1 day
};

// Critical assets to precache on install
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/logos/bionic-logo-official.avif',
  '/logos/bionic-logo-official.webp',
  '/logos/bionic-logo-official.png',
  '/logos/bionic-logo-main.avif',
  '/logos/bionic-logo-main.webp'
];

// Routes to prefetch after activation
const PREFETCH_ROUTES = [
  '/dashboard',
  '/shop'
];

// API routes for smart caching
const API_CACHE_CONFIG = {
  // Cache-first (rarely changes)
  cacheFirst: [
    '/api/v1/species',
    '/api/v1/config',
    '/api/v1/regulations'
  ],
  // Stale-while-revalidate (semi-static)
  staleWhileRevalidate: [
    '/api/v1/products',
    '/api/v1/lands',
    '/api/v1/outfitters'
  ],
  // Network-first (dynamic)
  networkFirst: [
    '/api/auth',
    '/api/user',
    '/api/v1/waypoint',
    '/api/v1/analytics'
  ]
};

// ============================================
// INSTALL EVENT - Precache Critical Assets
// ============================================
self.addEventListener('install', (event) => {
  console.log(`[SW V2] Installing Service Worker ${SW_VERSION}...`);
  
  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(CACHES.static).then((cache) => {
        console.log('[SW V2] Precaching critical assets');
        return cache.addAll(PRECACHE_ASSETS);
      }),
      // Cache fonts (if available)
      caches.open(CACHES.fonts)
    ])
    .then(() => {
      console.log('[SW V2] Precaching complete');
      return self.skipWaiting();
    })
    .catch((error) => {
      console.error('[SW V2] Precaching failed:', error);
    })
  );
});

// ============================================
// ACTIVATE EVENT - Clean Old Caches
// ============================================
self.addEventListener('activate', (event) => {
  console.log(`[SW V2] Activating Service Worker ${SW_VERSION}...`);
  
  event.waitUntil(
    Promise.all([
      // Clean old caches — supprime TOUTES les versions antérieures
      caches.keys().then((cacheNames) => {
        const validCaches = Object.values(CACHES);
        return Promise.all(
          cacheNames
            .filter((name) => name.startsWith(CACHE_PREFIX) && !validCaches.includes(name))
            .map((name) => {
              console.log('[SW V2] Deleting old cache:', name);
              return caches.delete(name);
            })
        );
      }),
      // Take control of all clients
      self.clients.claim()
    ])
    .then(() => {
      console.log(`[SW V2] Activation complete v${SW_VERSION} — clients notification (no forced reload)`);
      // BIONIC V5 300% FIX: Notification passive uniquement. Le rechargement est géré
      // par le listener controllerchange côté client (une seule fois par session).
      self.clients.matchAll({ type: 'window' }).then(clients => {
        clients.forEach(client => {
          client.postMessage({ type: 'SW_UPDATED', version: SW_VERSION });
        });
      });
      // Prefetch common routes
      prefetchRoutes();
    })
  );
});

// ============================================
// FETCH EVENT - Smart Caching Strategies
// ============================================
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') return;
  
  // Skip chrome-extension and other protocols
  if (!url.protocol.startsWith('http')) return;
  
  // Route to appropriate strategy
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request, url));
  } else if (isImageRequest(request)) {
    event.respondWith(handleImageRequest(request));
  } else if (isFontRequest(request)) {
    event.respondWith(handleFontRequest(request));
  } else if (isStaticAsset(request)) {
    event.respondWith(handleStaticRequest(request));
  } else {
    event.respondWith(handlePageRequest(request));
  }
});

// ============================================
// REQUEST HANDLERS
// ============================================

/**
 * Handle API requests
 * Network-first with intelligent cache fallback
 */
async function handleApiRequest(request, url) {
  const pathname = url.pathname;
  
  // Determine caching strategy
  if (API_CACHE_CONFIG.cacheFirst.some(p => pathname.startsWith(p))) {
    return cacheFirst(request, CACHES.api, CACHE_TTL.api);
  }
  
  if (API_CACHE_CONFIG.staleWhileRevalidate.some(p => pathname.startsWith(p))) {
    return staleWhileRevalidate(request, CACHES.api, CACHE_TTL.api);
  }
  
  // Default: Network-first
  return networkFirst(request, CACHES.api, CACHE_TTL.api);
}

/**
 * Handle image requests
 * Cache-first with long TTL + lazy revalidation
 */
async function handleImageRequest(request) {
  return cacheFirst(request, CACHES.images, CACHE_TTL.images);
}

/**
 * Handle font requests
 * Cache-first with very long TTL (fonts rarely change)
 */
async function handleFontRequest(request) {
  return cacheFirst(request, CACHES.fonts, CACHE_TTL.fonts);
}

/**
 * Handle static asset requests (JS, CSS)
 * Network-first to ensure fresh code after deployments
 * Falls back to cache only when offline
 */
async function handleStaticRequest(request) {
  return networkFirst(request, CACHES.static, CACHE_TTL.static);
}

/**
 * Handle page/HTML requests
 * Network-first with offline fallback
 */
async function handlePageRequest(request) {
  return networkFirstWithOffline(request, CACHES.pages);
}

// ============================================
// CACHING STRATEGIES
// ============================================

/**
 * Cache-first strategy
 * Best for: Images, fonts, rarely-changing assets
 */
async function cacheFirst(request, cacheName, ttl) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse && !isExpired(cachedResponse, ttl)) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const responseToCache = networkResponse.clone();
      cache.put(request, addTimestamp(responseToCache));
    }
    return networkResponse;
  } catch (error) {
    if (cachedResponse) {
      return cachedResponse; // Return stale if network fails
    }
    throw error;
  }
}

/**
 * Stale-while-revalidate strategy
 * Best for: Static assets, semi-dynamic content
 */
async function staleWhileRevalidate(request, cacheName, ttl) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);
  
  // Return cached immediately, revalidate in background
  const fetchPromise = fetch(request)
    .then((networkResponse) => {
      if (networkResponse.ok) {
        cache.put(request, addTimestamp(networkResponse.clone()));
      }
      return networkResponse;
    })
    .catch(() => cachedResponse);
  
  return cachedResponse || fetchPromise;
}

/**
 * Network-first strategy
 * Best for: API calls, dynamic content
 */
async function networkFirst(request, cacheName, ttl) {
  const cache = await caches.open(cacheName);
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, addTimestamp(networkResponse.clone()));
    }
    return networkResponse;
  } catch (error) {
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

/**
 * Network-first with offline fallback
 * Best for: HTML pages
 */
async function networkFirstWithOffline(request, cacheName) {
  const cache = await caches.open(cacheName);
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    // Return index.html for SPA navigation
    const indexResponse = await cache.match('/index.html');
    if (indexResponse) {
      return indexResponse;
    }
    return new Response('Offline', { status: 503 });
  }
}

// ============================================
// HELPER FUNCTIONS
// ============================================

function isImageRequest(request) {
  const url = new URL(request.url);
  return /\.(png|jpg|jpeg|gif|webp|avif|svg|ico)$/i.test(url.pathname) ||
         request.destination === 'image';
}

function isFontRequest(request) {
  const url = new URL(request.url);
  return /\.(woff|woff2|ttf|otf|eot)$/i.test(url.pathname) ||
         url.hostname.includes('fonts.gstatic.com') ||
         request.destination === 'font';
}

function isStaticAsset(request) {
  const url = new URL(request.url);
  return /\.(js|css|json)$/i.test(url.pathname);
}

function addTimestamp(response) {
  const headers = new Headers(response.headers);
  headers.set('sw-cache-timestamp', Date.now().toString());
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: headers
  });
}

function isExpired(response, ttl) {
  const timestamp = response.headers.get('sw-cache-timestamp');
  if (!timestamp) return true;
  return (Date.now() - parseInt(timestamp, 10)) > ttl;
}

/**
 * Prefetch common routes after activation
 */
async function prefetchRoutes() {
  const cache = await caches.open(CACHES.pages);
  
  for (const route of PREFETCH_ROUTES) {
    try {
      const response = await fetch(route);
      if (response.ok) {
        cache.put(route, response);
        console.log(`[SW V2] Prefetched: ${route}`);
      }
    } catch (error) {
      // Silently fail - prefetching is optional
    }
  }
}

// ============================================
// MESSAGE HANDLING
// ============================================

self.addEventListener('message', (event) => {
  const { type, payload } = event.data || {};
  
  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
      
    case 'CLEAR_CACHE':
      clearAllCaches().then(() => {
        event.ports[0]?.postMessage({ success: true });
      });
      break;
      
    case 'CACHE_ROUTE':
      if (payload?.url) {
        cacheRoute(payload.url);
      }
      break;
      
    case 'GET_CACHE_STATS':
      getCacheStats().then((stats) => {
        event.ports[0]?.postMessage(stats);
      });
      break;
  }
});

async function clearAllCaches() {
  const cacheNames = await caches.keys();
  await Promise.all(
    cacheNames
      .filter((name) => name.startsWith(CACHE_PREFIX))
      .map((name) => caches.delete(name))
  );
  console.log('[SW V2] All caches cleared');
}

async function cacheRoute(url) {
  const cache = await caches.open(CACHES.pages);
  try {
    const response = await fetch(url);
    if (response.ok) {
      cache.put(url, response);
      console.log(`[SW V2] Cached route: ${url}`);
    }
  } catch (error) {
    console.error(`[SW V2] Failed to cache route: ${url}`, error);
  }
}

async function getCacheStats() {
  const stats = {};
  
  for (const [name, cacheName] of Object.entries(CACHES)) {
    const cache = await caches.open(cacheName);
    const keys = await cache.keys();
    stats[name] = {
      count: keys.length,
      cacheName
    };
  }
  
  return stats;
}

// ============================================
// BACKGROUND SYNC (if supported)
// ============================================

self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-analytics') {
    event.waitUntil(syncAnalytics());
  }
});

async function syncAnalytics() {
  // Sync any offline analytics when back online
  console.log('[SW V2] Syncing offline analytics...');
}

console.log(`[SW V2] Service Worker ${SW_VERSION} loaded - BIONIC HUNT/Chasse V5 Ultimate`);
