import React from "react";
import ReactDOM from "react-dom/client";

// BIONIC V7.3 — Suppress benign ResizeObserver loop error.
// This error is non-fatal: the browser caps the loop after one frame.
// Without this handler, React's error overlay displays it as a crash.
const RESIZE_OBSERVER_ERR = 'ResizeObserver loop';
window.addEventListener('error', (e) => {
  if (e.message?.includes(RESIZE_OBSERVER_ERR) || e.error?.message?.includes(RESIZE_OBSERVER_ERR)) {
    e.stopImmediatePropagation();
    e.preventDefault();
  }
});
// Also suppress the unhandledrejection variant (rare but possible)
window.addEventListener('unhandledrejection', (e) => {
  if (e.reason?.message?.includes(RESIZE_OBSERVER_ERR)) {
    e.preventDefault();
  }
});

// BRANCHE 2: Inject Critical CSS BEFORE main styles
import { injectCriticalCSS, removeCriticalCSS } from "@/utils/criticalCSS";
injectCriticalCSS();

import "@/index.css";
import App from "@/App";
import { initWebVitals } from "@/utils/webVitals";
import { initPerformanceOptimizations } from "@/utils/performanceOptimizations";
import { initAccessibilityEnhancements } from "@/utils/accessibilityEnhancements";
import * as serviceWorkerRegistration from "./serviceWorkerRegistration";

// BRANCHE 3: Import advanced optimizations
import { initImageOptimization } from "@/utils/imageCDN";
import { initHTTP3Optimization } from "@/utils/http3Optimization";
import { initSSRConfig } from "@/utils/ssrConfig";
import { preloadCriticalRoutes } from "@/utils/routePreloader";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

// BRANCHE 2: Remove Critical CSS after main styles load
removeCriticalCSS();

// PHASE D: Initialize Web Vitals reporting
initWebVitals();

// POLISH FINAL: Performance optimizations
initPerformanceOptimizations();

// POLISH FINAL: Accessibility enhancements (WCAG AAA)
initAccessibilityEnhancements();

// BRANCHE 3: Advanced optimizations
initImageOptimization();
initHTTP3Optimization();
initSSRConfig();
preloadCriticalRoutes();

// BRANCHE 3: Register Service Worker V2 for advanced caching
// BIONIC V5 300% FIX: Un seul mécanisme de reload (controllerchange dans serviceWorkerRegistration.js)
// Le message SW_UPDATED n'est plus utilisé pour recharger car il créait une boucle infinie
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SW_UPDATED') {
      console.log(`[App] Service Worker mis à jour (${event.data.version}) — notification reçue (pas de reload, géré par controllerchange)`);
    }
  });
}

serviceWorkerRegistration.register({
  onUpdate: (registration) => {
    console.log('[App] Nouvelle version détectée — activation en cours...');
  },
  onSuccess: (registration) => {
    console.log('[App] Contenu mis en cache pour utilisation hors-ligne.');
  }
});
