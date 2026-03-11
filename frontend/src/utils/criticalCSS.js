/**
 * Critical CSS Generator - BRANCHE 2 (98% → 99%)
 * 
 * Extrait et inline le CSS critique pour le rendu above-the-fold
 * Élimine le render-blocking CSS pour améliorer le LCP
 * 
 * @module criticalCSS
 * @version 1.0.0
 * @phase BRANCHE_2
 */

/**
 * Critical CSS pour le rendu initial (above-the-fold)
 * Ces styles sont essentiels pour éviter le FOUC (Flash of Unstyled Content)
 */
export const CRITICAL_CSS = `
/* Reset & Base - Critical */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{line-height:1.5;-webkit-text-size-adjust:100%;scroll-behavior:smooth;min-height:100%}
body{min-height:100%;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;-webkit-font-smoothing:antialiased;background-color:#0a0a0a;color:#fafafa}
#root{min-height:100vh;display:flex;flex-direction:column}

/* Layout - Critical */
.flex{display:flex}
.flex-col{flex-direction:column}
.items-center{align-items:center}
.justify-center{justify-content:center}
.justify-between{justify-content:space-between}
.gap-2{gap:0.5rem}
.gap-4{gap:1rem}
.w-full{width:100%}
.h-full{height:100%}
.min-h-screen{min-height:100vh}

/* Spacing - Critical */
.p-2{padding:0.5rem}
.p-4{padding:1rem}
.px-4{padding-left:1rem;padding-right:1rem}
.py-2{padding-top:0.5rem;padding-bottom:0.5rem}
.m-0{margin:0}
.mx-auto{margin-left:auto;margin-right:auto}

/* Typography - Critical */
.text-sm{font-size:0.875rem;line-height:1.25rem}
.text-base{font-size:1rem;line-height:1.5rem}
.text-lg{font-size:1.125rem;line-height:1.75rem}
.text-xl{font-size:1.25rem;line-height:1.75rem}
.text-2xl{font-size:1.5rem;line-height:2rem}
.text-4xl{font-size:2.25rem;line-height:2.5rem}
.font-medium{font-weight:500}
.font-semibold{font-weight:600}
.font-bold{font-weight:700}
.text-center{text-align:center}
.text-white{color:#fff}

/* Colors - Critical (BIONIC theme) */
.bg-black{background-color:#000}
.bg-zinc-900{background-color:#18181b}
.bg-zinc-950{background-color:#09090b}
.text-gray-300{color:#d1d5db}
.text-gray-400{color:#9ca3af}

/* BIONIC Gold Accent */
.text-amber-500{color:#f5a623}
.bg-amber-500{background-color:#f5a623}
.border-amber-500{border-color:#f5a623}

/* Borders - Critical */
.border{border-width:1px}
.border-zinc-800{border-color:#27272a}
.rounded{border-radius:0.25rem}
.rounded-lg{border-radius:0.5rem}
.rounded-full{border-radius:9999px}

/* Visibility - Critical */
.hidden{display:none}
.block{display:block}
.inline-flex{display:inline-flex}

/* Header/Nav - Critical */
.fixed{position:fixed}
.sticky{position:sticky}
.top-0{top:0}
.left-0{left:0}
.right-0{right:0}
.z-50{z-index:50}

/* Loading Spinner - Critical */
@keyframes spin{to{transform:rotate(360deg)}}
.animate-spin{animation:spin 1s linear infinite}

/* Suspense Fallback - Critical */
.loading-skeleton{background:linear-gradient(90deg,#27272a 25%,#3f3f46 50%,#27272a 75%);background-size:200% 100%;animation:shimmer 1.5s infinite}
@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}

/* WCAG Focus - Critical */
*:focus-visible{outline:2px solid #f5a623;outline-offset:2px}

/* Skip Link - Critical */
.skip-link{position:absolute;top:-100px;left:16px;background:#f5a623;color:#000;padding:12px 24px;z-index:10000;font-weight:700;transition:top 0.15s}
.skip-link:focus{top:16px}

/* Screen Reader Only - Critical */
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
`;

/**
 * Inject Critical CSS into document head
 * Should be called as early as possible in app lifecycle
 */
export const injectCriticalCSS = () => {
  if (typeof document === 'undefined') return;
  
  // Check if already injected
  if (document.getElementById('critical-css')) return;
  
  const style = document.createElement('style');
  style.id = 'critical-css';
  style.textContent = CRITICAL_CSS;
  
  // Insert at the beginning of head for priority
  const head = document.head;
  const firstChild = head.firstChild;
  head.insertBefore(style, firstChild);
};

/**
 * Remove Critical CSS after main styles load
 * Prevents duplicate CSS rules
 */
export const removeCriticalCSS = () => {
  if (typeof document === 'undefined') return;
  
  const criticalStyle = document.getElementById('critical-css');
  if (criticalStyle) {
    // Delay removal to ensure main CSS is parsed
    setTimeout(() => {
      criticalStyle.remove();
    }, 1000);
  }
};

/**
 * Generate Critical CSS string for SSR/static HTML injection
 */
export const getCriticalCSSString = () => {
  return `<style id="critical-css">${CRITICAL_CSS}</style>`;
};

export default {
  CRITICAL_CSS,
  injectCriticalCSS,
  removeCriticalCSS,
  getCriticalCSSString
};
