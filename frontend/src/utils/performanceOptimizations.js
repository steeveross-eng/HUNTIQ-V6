/**
 * Performance Optimizations - BRANCHE 1 POLISH FINAL
 * 
 * Micro-optimisations CPU Main Thread et détection des tâches longues
 * Conforme aux exigences BIONIC V5
 * 
 * OBJECTIF: Aucune tâche bloquante > 50ms
 * 
 * @module performanceOptimizations
 * @version 2.0.0
 * @phase POLISH_FINAL
 */

// Performance metrics tracking
let performanceMetrics = {
  longTaskCount: 0,
  totalBlockingTime: 0,
  lastReportTime: 0
};

/**
 * Long Task Observer
 * Détecte et rapporte les tâches > 50ms qui bloquent le main thread
 */
export const initLongTaskObserver = () => {
  if (typeof window === 'undefined' || !('PerformanceObserver' in window)) {
    return;
  }

  try {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        performanceMetrics.longTaskCount++;
        performanceMetrics.totalBlockingTime += entry.duration - 50; // Time over threshold
        
        // Log long tasks in development
        if (process.env.NODE_ENV === 'development') {
          console.warn('[Performance] Long task detected:', {
            duration: `${entry.duration.toFixed(2)}ms`,
            startTime: `${entry.startTime.toFixed(2)}ms`,
            name: entry.name,
            totalLongTasks: performanceMetrics.longTaskCount
          });
        }
      }
    });

    observer.observe({ entryTypes: ['longtask'] });
  } catch {
    // PerformanceObserver for longtask not supported
  }
};

/**
 * Yield to Main Thread
 * Permet au navigateur de traiter les événements utilisateur entre les tâches
 */
export const yieldToMain = () => {
  return new Promise(resolve => {
    if ('scheduler' in window && 'yield' in window.scheduler) {
      // Use modern scheduler.yield if available
      window.scheduler.yield().then(resolve);
    } else {
      // Fallback to setTimeout
      setTimeout(resolve, 0);
    }
  });
};

/**
 * Run Heavy Task in Chunks
 * Divise les tâches lourdes en morceaux pour éviter de bloquer le main thread
 */
export const runInChunks = async (items, processFn, chunkSize = 10) => {
  const results = [];
  
  for (let i = 0; i < items.length; i += chunkSize) {
    const chunk = items.slice(i, i + chunkSize);
    
    // Process chunk
    for (const item of chunk) {
      results.push(await processFn(item));
    }
    
    // Yield to main thread between chunks
    if (i + chunkSize < items.length) {
      await yieldToMain();
    }
  }
  
  return results;
};

/**
 * Passive Event Listeners
 * Améliore le scroll performance en rendant les listeners passifs
 */
export const upgradePassiveListeners = () => {
  if (typeof window === 'undefined') return;

  // Test passive support
  let supportsPassive = false;
  try {
    const opts = Object.defineProperty({}, 'passive', {
      get: function() {
        supportsPassive = true;
        return true;
      }
    });
    window.addEventListener('testPassive', null, opts);
    window.removeEventListener('testPassive', null, opts);
  } catch (e) {
    supportsPassive = false;
  }

  // Upgrade scroll, wheel, and touch listeners
  if (supportsPassive) {
    const originalAddEventListener = EventTarget.prototype.addEventListener;
    
    EventTarget.prototype.addEventListener = function(type, listener, options) {
      const passiveEvents = ['scroll', 'wheel', 'touchstart', 'touchmove', 'touchend'];
      
      if (passiveEvents.includes(type)) {
        const newOptions = typeof options === 'object' 
          ? { ...options, passive: options.passive !== false }
          : { passive: true, capture: options };
        
        return originalAddEventListener.call(this, type, listener, newOptions);
      }
      
      return originalAddEventListener.call(this, type, listener, options);
    };
  }
};

/**
 * Debounce with RAF
 * Utilise requestAnimationFrame pour les événements de resize/scroll
 */
export const rafDebounce = (fn) => {
  let rafId = null;
  
  return function(...args) {
    if (rafId) {
      cancelAnimationFrame(rafId);
    }
    
    rafId = requestAnimationFrame(() => {
      fn.apply(this, args);
      rafId = null;
    });
  };
};

/**
 * Throttle Function
 * Limite la fréquence d'exécution d'une fonction
 */
export const throttle = (fn, limit = 16) => {
  let lastRun = 0;
  let pending = false;
  
  return function(...args) {
    const now = performance.now();
    
    if (now - lastRun >= limit) {
      fn.apply(this, args);
      lastRun = now;
    } else if (!pending) {
      pending = true;
      setTimeout(() => {
        fn.apply(this, args);
        lastRun = performance.now();
        pending = false;
      }, limit - (now - lastRun));
    }
  };
};

/**
 * Defer Non-Critical Scripts
 * Utilise requestIdleCallback pour les scripts non critiques
 */
export const deferNonCritical = (callback, timeout = 2000) => {
  if (typeof window === 'undefined') {
    return callback();
  }

  if ('requestIdleCallback' in window) {
    return window.requestIdleCallback(callback, { timeout });
  } else {
    return setTimeout(callback, 1);
  }
};

/**
 * Preload Critical Resources
 * Précharge dynamiquement les ressources critiques (optimisées AVIF/WebP)
 */
export const preloadCriticalResources = () => {
  if (typeof document === 'undefined') return;

  const criticalResources = [
    // Priorité aux formats optimisés
    { href: '/logos/bionic-logo-official.avif', as: 'image', type: 'image/avif' },
    { href: '/logos/bionic-logo-official.webp', as: 'image', type: 'image/webp' },
  ];

  criticalResources.forEach(({ href, as, type }) => {
    // Vérifier si le preload existe déjà
    if (document.querySelector(`link[rel="preload"][href="${href}"]`)) return;
    
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = href;
    link.as = as;
    if (type) link.type = type;
    document.head.appendChild(link);
  });
};

/**
 * Image Loading Optimization
 * Applique le lazy loading natif aux images non-critiques
 */
export const optimizeImageLoading = () => {
  if (typeof document === 'undefined') return;

  // Find all images without explicit loading attribute
  const images = document.querySelectorAll('img:not([loading])');
  
  images.forEach((img, index) => {
    // First 3 images are considered above-the-fold
    if (index < 3) {
      img.setAttribute('loading', 'eager');
      img.setAttribute('fetchpriority', 'high');
    } else {
      img.setAttribute('loading', 'lazy');
      img.setAttribute('decoding', 'async');
    }
  });
};

/**
 * Optimize DOM Operations
 * Batch DOM reads/writes to avoid layout thrashing
 */
export const batchDOMOperations = (readFn, writeFn) => {
  // Read phase
  const readResult = readFn();
  
  // Write phase in next frame
  requestAnimationFrame(() => {
    writeFn(readResult);
  });
};

/**
 * Connection-Aware Loading
 * Adapte le chargement selon la connexion
 */
export const getConnectionQuality = () => {
  if (typeof navigator === 'undefined' || !('connection' in navigator)) {
    return 'unknown';
  }

  const connection = navigator.connection;
  
  if (connection.saveData) return 'save-data';
  if (connection.effectiveType === '4g' && connection.downlink > 5) return 'fast';
  if (connection.effectiveType === '4g') return 'good';
  if (connection.effectiveType === '3g') return 'moderate';
  return 'slow';
};

/**
 * Reduce Motion Check
 * Respecte les préférences utilisateur pour les animations
 */
export const prefersReducedMotion = () => {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

/**
 * Get Performance Metrics
 * Retourne les métriques de performance collectées
 */
export const getPerformanceMetrics = () => {
  return { ...performanceMetrics };
};

/**
 * Initialize All Performance Optimizations
 */
export const initPerformanceOptimizations = () => {
  // Critical optimizations immediately
  upgradePassiveListeners();
  
  // Defer non-critical optimizations
  deferNonCritical(() => {
    initLongTaskObserver();
    optimizeImageLoading();
    preloadCriticalResources();
  });

  // Log connection quality in development
  if (process.env.NODE_ENV === 'development') {
    console.log('[Performance] Connection quality:', getConnectionQuality());
    console.log('[Performance] Prefers reduced motion:', prefersReducedMotion());
  }
};

export default {
  initLongTaskObserver,
  upgradePassiveListeners,
  yieldToMain,
  runInChunks,
  rafDebounce,
  throttle,
  deferNonCritical,
  preloadCriticalResources,
  optimizeImageLoading,
  batchDOMOperations,
  getConnectionQuality,
  prefersReducedMotion,
  getPerformanceMetrics,
  initPerformanceOptimizations
};
