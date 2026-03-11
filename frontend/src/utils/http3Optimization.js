/**
 * HTTP/3 QUIC Optimization - BRANCHE 3 (99% → 99.9%)
 * 
 * Configuration et détection HTTP/3 QUIC pour latence optimale
 * - Détection du support HTTP/3
 * - Early hints (103)
 * - Connection coalescing
 * - 0-RTT support
 * 
 * @module http3Optimization
 * @version 1.0.0
 * @phase BRANCHE_3
 */

/**
 * HTTP/3 Feature Detection
 */
export const http3Support = {
  detected: null,
  protocol: null
};

/**
 * Detect if current connection uses HTTP/3
 */
export async function detectHTTP3() {
  if (http3Support.detected !== null) {
    return http3Support;
  }
  
  // Check using Navigation Timing API
  if (typeof performance !== 'undefined' && performance.getEntriesByType) {
    const navEntries = performance.getEntriesByType('navigation');
    if (navEntries.length > 0) {
      const nav = navEntries[0];
      
      // Check nextHopProtocol
      if (nav.nextHopProtocol) {
        http3Support.protocol = nav.nextHopProtocol;
        http3Support.detected = nav.nextHopProtocol.includes('h3') || 
                                 nav.nextHopProtocol.includes('quic');
        return http3Support;
      }
    }
  }
  
  // Fallback: Check Resource Timing for any HTTP/3 resources
  if (typeof performance !== 'undefined' && performance.getEntriesByType) {
    const resources = performance.getEntriesByType('resource');
    for (const resource of resources) {
      if (resource.nextHopProtocol) {
        if (resource.nextHopProtocol.includes('h3') || 
            resource.nextHopProtocol.includes('quic')) {
          http3Support.detected = true;
          http3Support.protocol = resource.nextHopProtocol;
          return http3Support;
        }
      }
    }
  }
  
  http3Support.detected = false;
  http3Support.protocol = 'h2'; // Assume HTTP/2 as fallback
  return http3Support;
}

/**
 * Get connection info
 */
export function getConnectionInfo() {
  const info = {
    protocol: http3Support.protocol || 'unknown',
    http3: http3Support.detected || false,
    rtt: null,
    downlink: null,
    effectiveType: null,
    saveData: false
  };
  
  if (typeof navigator !== 'undefined' && 'connection' in navigator) {
    const conn = navigator.connection;
    info.rtt = conn.rtt;
    info.downlink = conn.downlink;
    info.effectiveType = conn.effectiveType;
    info.saveData = conn.saveData || false;
  }
  
  return info;
}

/**
 * HTTP/3 Specific Optimizations
 */
export const HTTP3_OPTIMIZATIONS = {
  // Enable 0-RTT (early data) for faster connections
  zeroRTT: {
    enabled: true,
    // Routes safe for 0-RTT (idempotent, no side effects)
    safeRoutes: [
      '/api/v1/config',
      '/api/v1/species',
      '/api/v1/products',
      '/api/v1/lands'
    ]
  },
  
  // Connection coalescing (reuse connections across origins)
  connectionCoalescing: {
    enabled: true,
    // Origins that can share connections (same certificate)
    coalescableOrigins: [
      'fonts.googleapis.com',
      'fonts.gstatic.com'
    ]
  },
  
  // Early hints (103) resources to preload
  earlyHints: [
    { rel: 'preload', as: 'style', href: '/static/css/main.css' },
    { rel: 'preload', as: 'script', href: '/static/js/main.js' },
    { rel: 'preconnect', href: 'https://fonts.googleapis.com' }
  ],
  
  // Priority hints for resources
  priorityHints: {
    // High priority resources
    high: [
      '/logos/bionic-logo-official.avif',
      '/static/css/main.css'
    ],
    // Low priority resources (can be deferred)
    low: [
      '/api/v1/analytics',
      '/logos/*.svg'
    ]
  }
};

/**
 * Generate Link headers for HTTP/3 push/preload
 */
export function generateLinkHeaders() {
  const links = [];
  
  // Add early hints
  HTTP3_OPTIMIZATIONS.earlyHints.forEach(hint => {
    let link = `<${hint.href}>; rel=${hint.rel}`;
    if (hint.as) link += `; as=${hint.as}`;
    if (hint.crossorigin) link += `; crossorigin`;
    links.push(link);
  });
  
  return links.join(', ');
}

/**
 * Apply priority hints to fetch requests
 */
export function applyPriorityHint(url, options = {}) {
  const isHighPriority = HTTP3_OPTIMIZATIONS.priorityHints.high.some(
    pattern => url.includes(pattern) || new RegExp(pattern).test(url)
  );
  
  const isLowPriority = HTTP3_OPTIMIZATIONS.priorityHints.low.some(
    pattern => url.includes(pattern) || new RegExp(pattern).test(url)
  );
  
  if (isHighPriority) {
    return { ...options, priority: 'high' };
  }
  
  if (isLowPriority) {
    return { ...options, priority: 'low' };
  }
  
  return options;
}

/**
 * Check if request is safe for 0-RTT
 */
export function isSafeFor0RTT(url, method = 'GET') {
  if (method !== 'GET') return false;
  if (!HTTP3_OPTIMIZATIONS.zeroRTT.enabled) return false;
  
  return HTTP3_OPTIMIZATIONS.zeroRTT.safeRoutes.some(
    route => url.includes(route)
  );
}

/**
 * Initialize HTTP/3 optimizations
 */
export async function initHTTP3Optimization() {
  // Detect protocol
  await detectHTTP3();
  
  // Log connection info in development
  if (process.env.NODE_ENV === 'development') {
    const info = getConnectionInfo();
    console.log('[HTTP/3] Connection info:', info);
    
    if (info.http3) {
      console.log('[HTTP/3] HTTP/3 QUIC detected! Optimal performance enabled.');
    } else {
      console.log('[HTTP/3] Using HTTP/2. HTTP/3 not available on this connection.');
    }
  }
  
  return http3Support;
}

/**
 * Server configuration hints for HTTP/3
 * (To be applied at infrastructure level)
 */
export const SERVER_CONFIG_HINTS = {
  nginx: `
# HTTP/3 QUIC configuration for nginx
# Requires nginx with quiche or ngtcp2

# Enable HTTP/3
listen 443 quic reuseport;
listen 443 ssl;

# Alt-Svc header to advertise HTTP/3
add_header Alt-Svc 'h3=":443"; ma=86400, h3-29=":443"; ma=86400';

# HTTP/3 specific headers
add_header QUIC-Status $quic;

# Early hints
http2_push_preload on;
`,

  cloudflare: `
# Cloudflare automatically enables HTTP/3
# Additional optimizations:
# 1. Enable Early Hints in Cloudflare dashboard
# 2. Enable 0-RTT Connection Resumption
# 3. Enable Argo Smart Routing for optimal QUIC paths
`,

  vercel: `
// vercel.json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Alt-Svc",
          "value": "h3=\\":443\\"; ma=86400"
        }
      ]
    }
  ]
}
`
};

export default {
  detectHTTP3,
  getConnectionInfo,
  http3Support,
  HTTP3_OPTIMIZATIONS,
  generateLinkHeaders,
  applyPriorityHint,
  isSafeFor0RTT,
  initHTTP3Optimization,
  SERVER_CONFIG_HINTS
};
