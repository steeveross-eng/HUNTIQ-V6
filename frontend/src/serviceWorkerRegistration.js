/**
 * Service Worker Registration - BRANCHE 3 (99% → 99.9%)
 * 
 * Enregistre le Service Worker V2 pour le caching avancé et le mode offline
 * 
 * @version 2.0.0
 * @phase BRANCHE_3
 */

const isLocalhost = Boolean(
  window.location.hostname === 'localhost' ||
  window.location.hostname === '[::1]' ||
  window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/)
);

// Service Worker version — incremented to force cache invalidation
const SW_VERSION = 'v6';

/**
 * Register Service Worker
 */
export function register(config) {
  if ('serviceWorker' in navigator) {
    const publicUrl = new URL(process.env.PUBLIC_URL || '', window.location.href);
    
    if (publicUrl.origin !== window.location.origin) {
      return;
    }

    window.addEventListener('load', () => {
      // Use SW V2 for advanced caching strategies
      const swUrl = `${process.env.PUBLIC_URL || ''}/sw-v2.js`;

      if (isLocalhost) {
        checkValidServiceWorker(swUrl, config);
        navigator.serviceWorker.ready.then(() => {
          console.log(`[SW ${SW_VERSION}] Service Worker ready (localhost)`);
        });
      } else {
        registerValidSW(swUrl, config);
      }
    });
  }
}

/**
 * Register valid Service Worker
 */
function registerValidSW(swUrl, config) {
  navigator.serviceWorker
    .register(swUrl)
    .then((registration) => {
      console.log(`[SW ${SW_VERSION}] Service Worker registered successfully`);
      
      // Check for updates periodically
      setInterval(() => {
        registration.update();
      }, 60 * 60 * 1000); // Check every hour
      
      registration.onupdatefound = () => {
        const installingWorker = registration.installing;
        
        if (installingWorker == null) {
          return;
        }
        
        installingWorker.onstatechange = () => {
          if (installingWorker.state === 'installed') {
            if (navigator.serviceWorker.controller) {
              console.log(`[SW ${SW_VERSION}] Nouveau code détecté — activation forcée`);
              
              // BIONIC V5 300%: Force le nouveau SW à prendre le contrôle IMMÉDIATEMENT
              installingWorker.postMessage({ type: 'SKIP_WAITING' });
              
              if (config && config.onUpdate) {
                config.onUpdate(registration);
              }
            } else {
              console.log(`[SW ${SW_VERSION}] Content cached for offline use.`);
              
              if (config && config.onSuccess) {
                config.onSuccess(registration);
              }
            }
          }
        };
      };
      
      // BIONIC V5 300% FIX: Rechargement unique garanti par sessionStorage
      // Empêche la boucle infinie de reload SW
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        const reloadKey = `sw_reload_${SW_VERSION}`;
        if (sessionStorage.getItem(reloadKey)) {
          console.log(`[SW ${SW_VERSION}] Reload déjà effectué pour cette session — ignoré`);
          return;
        }
        sessionStorage.setItem(reloadKey, Date.now().toString());
        console.log(`[SW ${SW_VERSION}] Nouveau Service Worker activé — rechargement unique`);
        window.location.reload();
      });
    })
    .catch((error) => {
      console.error(`[SW ${SW_VERSION}] Service Worker registration failed:`, error);
    });
}

/**
 * Check if Service Worker is valid (localhost)
 */
function checkValidServiceWorker(swUrl, config) {
  fetch(swUrl, {
    headers: { 'Service-Worker': 'script' }
  })
    .then((response) => {
      const contentType = response.headers.get('content-type');
      
      if (
        response.status === 404 ||
        (contentType != null && contentType.indexOf('javascript') === -1)
      ) {
        navigator.serviceWorker.ready.then((registration) => {
          registration.unregister().then(() => {
            window.location.reload();
          });
        });
      } else {
        registerValidSW(swUrl, config);
      }
    })
    .catch(() => {
      console.log(`[SW ${SW_VERSION}] No internet connection. Running in offline mode.`);
    });
}

/**
 * Unregister Service Worker
 */
export function unregister() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready
      .then((registration) => {
        registration.unregister();
        console.log(`[SW ${SW_VERSION}] Service Worker unregistered`);
      })
      .catch((error) => {
        console.error(`[SW ${SW_VERSION}] Service Worker unregistration failed:`, error);
      });
  }
}

/**
 * Check for Service Worker updates
 */
export function checkForUpdates() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then((registration) => {
      registration.update();
    });
  }
}

/**
 * Skip waiting and activate new Service Worker immediately
 */
export function skipWaiting() {
  if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
    // Send message to SW to skip waiting
    const messageChannel = new MessageChannel();
    navigator.serviceWorker.controller.postMessage(
      { type: 'SKIP_WAITING' },
      [messageChannel.port2]
    );
    
    // Reload after SW takes over
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      window.location.reload();
    });
  }
}

/**
 * Clear all caches
 */
export function clearCache() {
  if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
    return new Promise((resolve) => {
      const messageChannel = new MessageChannel();
      messageChannel.port1.onmessage = (event) => {
        resolve(event.data);
      };
      navigator.serviceWorker.controller.postMessage(
        { type: 'CLEAR_CACHE' },
        [messageChannel.port2]
      );
    });
  }
  return Promise.resolve({ success: false });
}

/**
 * Get cache statistics
 */
export function getCacheStats() {
  if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
    return new Promise((resolve) => {
      const messageChannel = new MessageChannel();
      messageChannel.port1.onmessage = (event) => {
        resolve(event.data);
      };
      navigator.serviceWorker.controller.postMessage(
        { type: 'GET_CACHE_STATS' },
        [messageChannel.port2]
      );
    });
  }
  return Promise.resolve(null);
}

/**
 * Pre-cache a specific route
 */
export function cacheRoute(url) {
  if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
    navigator.serviceWorker.controller.postMessage({
      type: 'CACHE_ROUTE',
      payload: { url }
    });
  }
}
