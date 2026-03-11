/**
 * Web Vitals Reporter - PHASE D Core Web Vitals
 * Reports performance metrics for monitoring
 * 
 * @module webVitals
 * @version 1.0.0
 */

// Only report in production
const isProduction = process.env.NODE_ENV === 'production';

/**
 * Report Web Vitals to console (dev) or analytics (prod)
 * @param {Object} metric - Web Vital metric
 */
const reportWebVitals = (metric) => {
  if (!isProduction) {
    // Development: log to console
    console.log(`[Web Vitals] ${metric.name}:`, metric.value.toFixed(2), metric.rating);
    return;
  }
  
  // Production: could send to analytics
  // Example: send to PostHog or custom endpoint
  // window.posthog?.capture('web_vitals', { ...metric });
};

/**
 * Initialize Web Vitals reporting
 */
export const initWebVitals = () => {
  if (typeof window === 'undefined') return;
  
  // Dynamic import to avoid blocking
  import('web-vitals').then(({ onCLS, onFCP, onLCP, onTTFB, onINP }) => {
    onCLS(reportWebVitals);
    onFCP(reportWebVitals);
    onLCP(reportWebVitals);
    onTTFB(reportWebVitals);
    onINP(reportWebVitals);
  }).catch(() => {
    // web-vitals not available, skip silently
  });
};

export default initWebVitals;
