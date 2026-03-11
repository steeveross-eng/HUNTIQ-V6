/**
 * Edge Caching Configuration - BRANCHE 3 (99% → 99.9%)
 * 
 * Configuration pour le caching au niveau CDN/Edge
 * Compatible avec: Cloudflare, Vercel, Netlify, AWS CloudFront
 * 
 * @module edgeCaching
 * @version 1.0.0
 * @phase BRANCHE_3
 */

/**
 * Cache-Control headers configuration
 * Ces valeurs sont utilisées par les CDN pour le caching edge
 */
export const CACHE_HEADERS = {
  // HTML pages - short cache, revalidate often
  html: {
    'Cache-Control': 'public, max-age=0, s-maxage=3600, stale-while-revalidate=86400',
    'CDN-Cache-Control': 'max-age=3600',
    'Vercel-CDN-Cache-Control': 'max-age=3600',
    'Cloudflare-CDN-Cache-Control': 'max-age=3600'
  },
  
  // Static assets (JS, CSS) - long cache with immutable
  staticAssets: {
    'Cache-Control': 'public, max-age=31536000, immutable',
    'CDN-Cache-Control': 'max-age=31536000',
    'Vercel-CDN-Cache-Control': 'max-age=31536000',
    'Cloudflare-CDN-Cache-Control': 'max-age=31536000'
  },
  
  // Images - very long cache
  images: {
    'Cache-Control': 'public, max-age=31536000, immutable',
    'CDN-Cache-Control': 'max-age=31536000',
    'Vary': 'Accept' // For format negotiation (AVIF, WebP)
  },
  
  // Fonts - immutable, year-long cache
  fonts: {
    'Cache-Control': 'public, max-age=31536000, immutable',
    'CDN-Cache-Control': 'max-age=31536000',
    'Access-Control-Allow-Origin': '*'
  },
  
  // API responses - short cache
  api: {
    'Cache-Control': 'public, max-age=60, s-maxage=300, stale-while-revalidate=600',
    'CDN-Cache-Control': 'max-age=300',
    'Vary': 'Authorization, Accept-Language'
  },
  
  // API responses (dynamic, user-specific)
  apiPrivate: {
    'Cache-Control': 'private, no-cache, no-store, must-revalidate',
    'CDN-Cache-Control': 'no-store'
  },
  
  // Service Worker
  serviceWorker: {
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Service-Worker-Allowed': '/'
  },
  
  // Manifest and config files
  manifest: {
    'Cache-Control': 'public, max-age=86400, stale-while-revalidate=604800',
    'CDN-Cache-Control': 'max-age=86400'
  }
};

/**
 * Vercel configuration (_headers or vercel.json)
 */
export const VERCEL_HEADERS_CONFIG = {
  headers: [
    {
      source: '/(.*)',
      headers: [
        { key: 'X-Content-Type-Options', value: 'nosniff' },
        { key: 'X-Frame-Options', value: 'DENY' },
        { key: 'X-XSS-Protection', value: '1; mode=block' }
      ]
    },
    {
      source: '/static/(.*)',
      headers: [
        { key: 'Cache-Control', value: 'public, max-age=31536000, immutable' }
      ]
    },
    {
      source: '/:path*.(js|css)',
      headers: [
        { key: 'Cache-Control', value: 'public, max-age=31536000, immutable' }
      ]
    },
    {
      source: '/:path*.(png|jpg|jpeg|webp|avif|gif|ico|svg)',
      headers: [
        { key: 'Cache-Control', value: 'public, max-age=31536000, immutable' }
      ]
    },
    {
      source: '/:path*.(woff|woff2|ttf|otf|eot)',
      headers: [
        { key: 'Cache-Control', value: 'public, max-age=31536000, immutable' },
        { key: 'Access-Control-Allow-Origin', value: '*' }
      ]
    },
    {
      source: '/sw.js',
      headers: [
        { key: 'Cache-Control', value: 'no-cache, no-store, must-revalidate' },
        { key: 'Service-Worker-Allowed', value: '/' }
      ]
    },
    {
      source: '/sw-v2.js',
      headers: [
        { key: 'Cache-Control', value: 'no-cache, no-store, must-revalidate' },
        { key: 'Service-Worker-Allowed', value: '/' }
      ]
    }
  ]
};

/**
 * Netlify _headers file content
 */
export const NETLIFY_HEADERS = `
# Static assets - immutable
/static/*
  Cache-Control: public, max-age=31536000, immutable

/*.js
  Cache-Control: public, max-age=31536000, immutable

/*.css
  Cache-Control: public, max-age=31536000, immutable

# Images
/*.png
  Cache-Control: public, max-age=31536000, immutable

/*.jpg
  Cache-Control: public, max-age=31536000, immutable

/*.webp
  Cache-Control: public, max-age=31536000, immutable

/*.avif
  Cache-Control: public, max-age=31536000, immutable

# Fonts
/*.woff2
  Cache-Control: public, max-age=31536000, immutable
  Access-Control-Allow-Origin: *

# Service Worker - no cache
/sw.js
  Cache-Control: no-cache, no-store, must-revalidate

/sw-v2.js
  Cache-Control: no-cache, no-store, must-revalidate

# Security headers for all
/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: strict-origin-when-cross-origin
`;

/**
 * Cloudflare Page Rules configuration
 */
export const CLOUDFLARE_PAGE_RULES = [
  {
    target: '*.preview.emergentagent.com/static/*',
    actions: {
      cache_level: 'cache_everything',
      edge_cache_ttl: 31536000,
      browser_cache_ttl: 31536000
    }
  },
  {
    target: '*.preview.emergentagent.com/*.js',
    actions: {
      cache_level: 'cache_everything',
      edge_cache_ttl: 31536000
    }
  },
  {
    target: '*.preview.emergentagent.com/*.css',
    actions: {
      cache_level: 'cache_everything',
      edge_cache_ttl: 31536000
    }
  },
  {
    target: '*.preview.emergentagent.com/logos/*',
    actions: {
      cache_level: 'cache_everything',
      edge_cache_ttl: 31536000,
      polish: 'lossy' // Image optimization
    }
  },
  {
    target: '*.preview.emergentagent.com/sw*.js',
    actions: {
      cache_level: 'bypass'
    }
  },
  {
    target: '*.preview.emergentagent.com/api/*',
    actions: {
      cache_level: 'standard',
      edge_cache_ttl: 300
    }
  }
];

/**
 * Get appropriate cache headers for a resource type
 */
export function getCacheHeaders(resourceType) {
  return CACHE_HEADERS[resourceType] || CACHE_HEADERS.html;
}

/**
 * Check if resource is cacheable
 */
export function isCacheable(url) {
  const pathname = new URL(url, 'http://localhost').pathname;
  
  // Never cache
  if (pathname.startsWith('/api/auth')) return false;
  if (pathname.startsWith('/api/user')) return false;
  if (pathname.includes('sw.js')) return false;
  
  // Always cache
  if (pathname.startsWith('/static/')) return true;
  if (/\.(js|css|png|jpg|webp|avif|woff2)$/.test(pathname)) return true;
  
  // Default: cacheable with short TTL
  return true;
}

/**
 * Get cache TTL for a resource
 */
export function getCacheTTL(url) {
  const pathname = new URL(url, 'http://localhost').pathname;
  
  // Immutable assets (hashed filenames)
  if (pathname.startsWith('/static/') || pathname.includes('.chunk.')) {
    return 31536000; // 1 year
  }
  
  // Images
  if (/\.(png|jpg|webp|avif|gif|svg)$/.test(pathname)) {
    return 31536000; // 1 year
  }
  
  // Fonts
  if (/\.(woff|woff2|ttf|otf)$/.test(pathname)) {
    return 31536000; // 1 year
  }
  
  // API
  if (pathname.startsWith('/api/')) {
    return 300; // 5 minutes
  }
  
  // HTML/Pages
  return 3600; // 1 hour
}

export default {
  CACHE_HEADERS,
  VERCEL_HEADERS_CONFIG,
  NETLIFY_HEADERS,
  CLOUDFLARE_PAGE_RULES,
  getCacheHeaders,
  isCacheable,
  getCacheTTL
};
