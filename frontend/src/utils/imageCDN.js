/**
 * Image CDN & Optimization - BRANCHE 3 (99% → 99.9%)
 * 
 * Module d'optimisation dynamique des images:
 * - Formats adaptatifs (AVIF > WebP > JPEG/PNG)
 * - Lazy loading avancé avec Intersection Observer
 * - Responsive images avec srcset
 * - Placeholder blur-up effect
 * - Préchargement intelligent
 * 
 * @module imageCDN
 * @version 1.0.0
 * @phase BRANCHE_3
 */

// Configuration
const IMAGE_CONFIG = {
  // Quality levels by connection type
  quality: {
    '4g': 85,
    '3g': 70,
    '2g': 50,
    'slow-2g': 30,
    'unknown': 80
  },
  // Breakpoints for responsive images
  breakpoints: [320, 480, 640, 768, 1024, 1280, 1536, 1920],
  // Placeholder dimensions
  placeholderSize: 20,
  // Intersection Observer config
  observerConfig: {
    rootMargin: '50px 0px', // Start loading 50px before visible
    threshold: 0.01
  }
};

// Supported formats detection
let supportedFormats = null;

/**
 * Detect supported image formats
 */
async function detectSupportedFormats() {
  if (supportedFormats) return supportedFormats;
  
  const formats = {
    avif: false,
    webp: false
  };
  
  // Test AVIF support
  try {
    const avifData = 'data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAAB0AAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAIAAAACAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQ0MAAAAABNjb2xybmNseAACAAIAAYAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAACVtZGF0EgAKBzgABpAABIyIgCARAA0gIA==';
    const img = new Image();
    await new Promise((resolve, reject) => {
      img.onload = resolve;
      img.onerror = reject;
      img.src = avifData;
    });
    formats.avif = true;
  } catch {
    formats.avif = false;
  }
  
  // Test WebP support
  try {
    const webpData = 'data:image/webp;base64,UklGRhoAAABXRUJQVlA4TA0AAAAvAAAAEAcQERGIiP4HAA==';
    const img = new Image();
    await new Promise((resolve, reject) => {
      img.onload = resolve;
      img.onerror = reject;
      img.src = webpData;
    });
    formats.webp = true;
  } catch {
    formats.webp = false;
  }
  
  supportedFormats = formats;
  return formats;
}

/**
 * Get optimal image format based on browser support
 */
export async function getOptimalFormat() {
  const formats = await detectSupportedFormats();
  
  if (formats.avif) return 'avif';
  if (formats.webp) return 'webp';
  return 'jpeg';
}

/**
 * Get connection quality for adaptive loading
 */
export function getConnectionQuality() {
  if (typeof navigator === 'undefined' || !('connection' in navigator)) {
    return 'unknown';
  }
  
  const connection = navigator.connection;
  
  if (connection.saveData) return 'slow-2g';
  return connection.effectiveType || 'unknown';
}

/**
 * Get optimal quality based on connection
 */
export function getOptimalQuality() {
  const connectionType = getConnectionQuality();
  return IMAGE_CONFIG.quality[connectionType] || IMAGE_CONFIG.quality.unknown;
}

/**
 * Generate optimized image URL
 * For use with image CDN services (Cloudinary, Imgix, etc.)
 */
export function generateOptimizedUrl(src, options = {}) {
  const {
    width,
    height,
    quality = getOptimalQuality(),
    format = 'auto'
  } = options;
  
  // If using a CDN, construct the optimized URL
  // Example for Cloudinary:
  // return `https://res.cloudinary.com/your-cloud/image/fetch/w_${width},q_${quality},f_${format}/${encodeURIComponent(src)}`;
  
  // For local images, return with format suffix if available
  if (src.startsWith('/logos/') || src.startsWith('/images/')) {
    const basePath = src.replace(/\.[^/.]+$/, '');
    const formats = supportedFormats || { avif: false, webp: false };
    
    if (formats.avif) return `${basePath}.avif`;
    if (formats.webp) return `${basePath}.webp`;
  }
  
  return src;
}

/**
 * Generate srcset for responsive images
 */
export function generateSrcset(src, options = {}) {
  const { breakpoints = IMAGE_CONFIG.breakpoints } = options;
  
  // For CDN-hosted images
  return breakpoints
    .map(width => `${generateOptimizedUrl(src, { width })} ${width}w`)
    .join(', ');
}

/**
 * Create placeholder data URL (blur-up effect)
 */
export function createPlaceholder(color = '#1a1a1a') {
  // Return a tiny SVG as placeholder
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"><rect fill="${color}" width="1" height="1"/></svg>`;
  return `data:image/svg+xml,${encodeURIComponent(svg)}`;
}

/**
 * Lazy load images with Intersection Observer
 */
export function initLazyLoading() {
  if (typeof window === 'undefined' || !('IntersectionObserver' in window)) {
    return;
  }
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        
        // Load actual image
        if (img.dataset.src) {
          img.src = img.dataset.src;
          delete img.dataset.src;
        }
        
        if (img.dataset.srcset) {
          img.srcset = img.dataset.srcset;
          delete img.dataset.srcset;
        }
        
        // Remove blur class after load
        img.addEventListener('load', () => {
          img.classList.add('loaded');
          img.classList.remove('lazy');
        }, { once: true });
        
        observer.unobserve(img);
      }
    });
  }, IMAGE_CONFIG.observerConfig);
  
  // Observe all lazy images
  document.querySelectorAll('img.lazy, img[data-src]').forEach(img => {
    observer.observe(img);
  });
  
  return observer;
}

/**
 * Preload critical images
 */
export function preloadCriticalImages(urls) {
  if (typeof document === 'undefined') return;
  
  urls.forEach(url => {
    // Check if already preloaded
    if (document.querySelector(`link[rel="preload"][href="${url}"]`)) return;
    
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = 'image';
    link.href = url;
    
    // Add type for modern formats
    if (url.endsWith('.avif')) link.type = 'image/avif';
    if (url.endsWith('.webp')) link.type = 'image/webp';
    
    document.head.appendChild(link);
  });
}

/**
 * Get native lazy loading support
 */
export function supportsNativeLazyLoading() {
  return 'loading' in HTMLImageElement.prototype;
}

/**
 * Initialize image optimization
 */
export async function initImageOptimization() {
  // Detect supported formats
  await detectSupportedFormats();
  
  // Initialize lazy loading
  if (!supportsNativeLazyLoading()) {
    initLazyLoading();
  }
  
  // Preload critical images
  preloadCriticalImages([
    '/logos/bionic-logo-official.avif',
    '/logos/bionic-logo-official.webp'
  ]);
  
  if (process.env.NODE_ENV === 'development') {
    console.log('[ImageCDN] Initialized with formats:', supportedFormats);
    console.log('[ImageCDN] Connection quality:', getConnectionQuality());
    console.log('[ImageCDN] Optimal quality:', getOptimalQuality());
  }
}

/**
 * Image CDN CSS styles for lazy loading
 */
export const IMAGE_CDN_STYLES = `
  img.lazy {
    opacity: 0;
    transition: opacity 0.3s ease-in;
  }
  
  img.lazy.loaded {
    opacity: 1;
  }
  
  /* Blur-up placeholder effect */
  .image-container {
    position: relative;
    overflow: hidden;
    background-color: #1a1a1a;
  }
  
  .image-container img {
    display: block;
    width: 100%;
    height: auto;
  }
  
  .image-container .placeholder {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    filter: blur(20px);
    transform: scale(1.1);
    transition: opacity 0.3s;
  }
  
  .image-container img.loaded + .placeholder {
    opacity: 0;
  }
`;

export default {
  getOptimalFormat,
  getConnectionQuality,
  getOptimalQuality,
  generateOptimizedUrl,
  generateSrcset,
  createPlaceholder,
  initLazyLoading,
  preloadCriticalImages,
  supportsNativeLazyLoading,
  initImageOptimization,
  IMAGE_CDN_STYLES
};
