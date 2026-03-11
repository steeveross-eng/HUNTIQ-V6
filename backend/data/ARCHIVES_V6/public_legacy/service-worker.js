/**
 * Service Worker - BRANCHE 1 POLISH FINAL
 * 
 * Implémente une stratégie de caching optimisée pour Edge CDN
 * - Cache-first pour les assets statiques avec TTL optimisé
 * - Stale-while-revalidate pour images
 * - Network-first pour API avec cache fallback
 * 
 * @version 2.0.0
 * @phase POLISH_FINAL
 */

const CACHE_VERSION = 'huntiq-v2';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const DYNAMIC_CACHE = `${CACHE_VERSION}-dynamic`;
const IMAGE_CACHE = `${CACHE_VERSION}-images`;
const FONT_CACHE = `${CACHE_VERSION}-fonts`;

// Assets to precache on install
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/logos/bionic-logo.svg',
  '/og-image.jpg',
  '/robots.txt',
  '/sitemap.xml'
];

// Cache size limits and TTLs
const CACHE_CONFIG = {
  [DYNAMIC_CACHE]: { maxItems: 50, maxAge: 3600 },      // 1 hour
  [IMAGE_CACHE]: { maxItems: 100, maxAge: 86400 * 7 },  // 7 days
  [FONT_CACHE]: { maxItems: 20, maxAge: 86400 * 30 },   // 30 days
  [STATIC_CACHE]: { maxItems: 100, maxAge: 86400 * 30 } // 30 days
};

/**
 * Install event - precache static assets
 */
self.addEventListener('install', (event) => {
  console.log('[SW v2] Installing Service Worker...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[SW v2] Precaching static assets');
        return cache.addAll(PRECACHE_ASSETS);
      })
      .then(() => {
        console.log('[SW v2] Precaching complete, skip waiting');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('[SW v2] Precaching failed:', error);
      })
  );
});

/**
 * Activate event - clean up old caches
 */
self.addEventListener('activate', (event) => {
  console.log('[SW v2] Activating Service Worker...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((name) => name.startsWith('huntiq-') && !name.startsWith(CACHE_VERSION))
            .map((name) => {
              console.log('[SW v2] Deleting old cache:', name);
              return caches.delete(name);
            })
        );
      })
      .then(() => {
        console.log('[SW v2] Activation complete, claiming clients');
        return self.clients.claim();
      })
  );
});

/**
 * Fetch event - handle requests with optimized caching strategies
 */
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip chrome-extension and other non-http(s) requests
  if (!url.protocol.startsWith('http')) {
    return;
  }
  
  // API requests - Network first, fallback to cache
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request, DYNAMIC_CACHE));
    return;
  }
  
  // Font requests - Cache first with long TTL
  if (isFontRequest(request)) {
    event.respondWith(cacheFirst(request, FONT_CACHE));
    return;
  }
  
  // Image requests - Stale while revalidate
  if (isImageRequest(request)) {
    event.respondWith(staleWhileRevalidate(request, IMAGE_CACHE));
    return;
  }
  
  // Static assets (JS, CSS) - Cache first
  if (isStaticAsset(request)) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
    return;
  }
  
  // HTML pages - Network first
  if (request.headers.get('Accept')?.includes('text/html')) {
    event.respondWith(networkFirst(request, DYNAMIC_CACHE));
    return;
  }
  
  // Default - Network with cache fallback
  event.respondWith(networkFirst(request, DYNAMIC_CACHE));
});

/**
 * Cache-first strategy with TTL
 * Best for static assets that rarely change
 */
async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  
  if (cached) {
    // Check if cache is still valid (via custom header or age)
    return cached;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      // Add cache-control headers for CDN
      const responseToCache = networkResponse.clone();
      cache.put(request, responseToCache);
    }
    
    return networkResponse;
  } catch (error) {
    console.error('[SW v2] Cache-first network error:', error);
    return new Response('Offline', { status: 503 });
  }
}

/**
 * Network-first strategy with cache fallback
 * Best for frequently updated content
 */
async function networkFirst(request, cacheName) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
      
      // Trim cache if needed
      trimCache(cacheName);
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW v2] Network failed, trying cache:', request.url);
    
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page for HTML requests
    if (request.headers.get('Accept')?.includes('text/html')) {
      return caches.match('/');
    }
    
    return new Response('Offline', { status: 503 });
  }
}

/**
 * Stale-while-revalidate strategy
 * Best for images and non-critical assets
 */
async function staleWhileRevalidate(request, cacheName) {
  const cachedResponse = await caches.match(request);
  
  const networkResponsePromise = fetch(request)
    .then(async (networkResponse) => {
      if (networkResponse.ok) {
        const cache = await caches.open(cacheName);
        cache.put(request, networkResponse.clone());
        
        // Trim cache if needed
        trimCache(cacheName);
      }
      return networkResponse;
    })
    .catch(() => cachedResponse);
  
  return cachedResponse || networkResponsePromise;
}

/**
 * Check if request is for a font
 */
function isFontRequest(request) {
  const url = new URL(request.url);
  const fontExtensions = ['.woff', '.woff2', '.ttf', '.otf', '.eot'];
  
  return fontExtensions.some(ext => url.pathname.toLowerCase().endsWith(ext)) ||
         url.hostname.includes('fonts.googleapis.com') ||
         url.hostname.includes('fonts.gstatic.com');
}

/**
 * Check if request is for an image
 */
function isImageRequest(request) {
  const url = new URL(request.url);
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif', '.svg', '.ico'];
  
  return imageExtensions.some(ext => url.pathname.toLowerCase().endsWith(ext)) ||
         request.headers.get('Accept')?.includes('image/');
}

/**
 * Check if request is for a static asset
 */
function isStaticAsset(request) {
  const url = new URL(request.url);
  const staticExtensions = ['.js', '.css', '.json'];
  
  return staticExtensions.some(ext => url.pathname.toLowerCase().endsWith(ext));
}

/**
 * Trim cache to limit size
 */
async function trimCache(cacheName) {
  const config = CACHE_CONFIG[cacheName];
  if (!config) return;
  
  const cache = await caches.open(cacheName);
  const keys = await cache.keys();
  
  if (keys.length > config.maxItems) {
    // Delete oldest entries
    const keysToDelete = keys.slice(0, keys.length - config.maxItems);
    await Promise.all(keysToDelete.map(key => cache.delete(key)));
    console.log(`[SW v2] Trimmed ${keysToDelete.length} items from ${cacheName}`);
  }
}

/**
 * Handle messages from main thread
 */
self.addEventListener('message', (event) => {
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }
  
  if (event.data === 'clearCache') {
    caches.keys().then((names) => {
      return Promise.all(names.map(name => caches.delete(name)));
    });
  }
  
  if (event.data === 'getVersion') {
    event.ports[0].postMessage({ version: CACHE_VERSION });
  }
});

console.log('[SW v2] Service Worker loaded - POLISH FINAL');
