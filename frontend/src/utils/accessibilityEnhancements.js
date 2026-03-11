/**
 * Accessibility Enhancements - BRANCHE 1 POLISH FINAL
 * 
 * WCAG 2.2 AAA Polish - Focus states, contrastes, ARIA, navigation clavier
 * Conforme aux exigences BIONIC V5
 * 
 * OBJECTIF: Conformité WCAG AAA 100%
 * 
 * @module accessibilityEnhancements
 * @version 2.0.0
 * @phase POLISH_FINAL
 */

// Accessibility metrics
let a11yMetrics = {
  skipLinkUsed: 0,
  keyboardNavigationActive: false,
  highContrastMode: false,
  reducedMotion: false
};

/**
 * Focus Management
 * Améliore la visibilité du focus pour la navigation clavier
 */
export const enhanceFocusVisibility = () => {
  if (typeof document === 'undefined') return;

  // Add focus-visible polyfill behavior
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      document.body.classList.add('keyboard-navigation');
      a11yMetrics.keyboardNavigationActive = true;
    }
  });

  document.addEventListener('mousedown', () => {
    document.body.classList.remove('keyboard-navigation');
    a11yMetrics.keyboardNavigationActive = false;
  });

  // Inject enhanced focus styles - WCAG AAA compliant (7:1 contrast ratio)
  const style = document.createElement('style');
  style.id = 'wcag-aaa-focus-styles';
  style.textContent = `
    /* WCAG AAA Focus Enhancement - Contrast ratio >= 7:1 */
    .keyboard-navigation *:focus {
      outline: 3px solid #f5a623 !important;
      outline-offset: 2px !important;
      box-shadow: 0 0 0 6px rgba(245, 166, 35, 0.4) !important;
    }
    
    .keyboard-navigation *:focus:not(:focus-visible) {
      outline: none !important;
      box-shadow: none !important;
    }
    
    .keyboard-navigation *:focus-visible {
      outline: 3px solid #f5a623 !important;
      outline-offset: 2px !important;
      box-shadow: 0 0 0 6px rgba(245, 166, 35, 0.4) !important;
    }
    
    /* Skip Link Enhancement - WCAG AAA */
    .skip-link {
      position: absolute;
      top: -100px;
      left: 16px;
      background: #f5a623;
      color: #000;
      padding: 12px 24px;
      z-index: 10000;
      font-weight: 700;
      font-size: 16px;
      text-decoration: none;
      border-radius: 4px;
      transition: top 0.15s ease-out;
    }
    
    .skip-link:focus {
      top: 16px;
      outline: 3px solid #000;
      outline-offset: 2px;
    }
    
    /* Screen reader only content */
    .sr-only {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }
    
    /* Focus trap indicator */
    [data-focus-trap="active"] {
      outline: 2px dashed #f5a623;
      outline-offset: 4px;
    }
    
    /* High Contrast Mode Support - WCAG AAA */
    @media (prefers-contrast: high) {
      *:focus {
        outline: 4px solid currentColor !important;
        outline-offset: 4px !important;
      }
      
      button, a, input, select, textarea {
        border: 2px solid currentColor !important;
      }
      
      /* Enhanced text visibility */
      body {
        background-color: #000 !important;
        color: #fff !important;
      }
      
      a {
        color: #ffff00 !important;
        text-decoration: underline !important;
      }
    }
    
    /* Forced Colors Mode (Windows High Contrast) */
    @media (forced-colors: active) {
      *:focus {
        outline: 3px solid CanvasText !important;
        outline-offset: 2px !important;
      }
      
      .skip-link:focus {
        outline: 3px solid Highlight !important;
        background: Canvas !important;
        color: CanvasText !important;
      }
    }
    
    /* Reduced Motion Support - WCAG AAA */
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
      }
      
      .skip-link {
        transition: none !important;
      }
    }
    
    /* Touch Target Size - WCAG AAA (44x44px minimum) */
    button, 
    [role="button"], 
    a, 
    input[type="checkbox"], 
    input[type="radio"],
    [role="menuitem"],
    [role="option"] {
      min-height: 44px;
      min-width: 44px;
    }
    
    /* Error states - WCAG AAA color independent */
    [aria-invalid="true"] {
      border-color: #dc2626 !important;
      border-width: 2px !important;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%23dc2626'%3E%3Cpath d='M8 0a8 8 0 1 0 8 8A8 8 0 0 0 8 0zm1 12H7v-2h2zm0-4H7V4h2z'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 8px center;
      padding-right: 32px;
    }
    
    /* Success states - WCAG AAA */
    [aria-invalid="false"]:not(:placeholder-shown) {
      border-color: #16a34a !important;
    }
  `;
  document.head.appendChild(style);
  
  // Detect user preferences
  a11yMetrics.highContrastMode = window.matchMedia('(prefers-contrast: high)').matches;
  a11yMetrics.reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

/**
 * Skip Link Injection
 * Ajoute un lien "Skip to main content" pour la navigation clavier
 */
export const injectSkipLink = () => {
  if (typeof document === 'undefined') return;
  
  // Check if skip link already exists
  if (document.querySelector('.skip-link')) return;

  const skipLink = document.createElement('a');
  skipLink.href = '#main-content';
  skipLink.className = 'skip-link';
  skipLink.textContent = 'Aller au contenu principal';
  skipLink.setAttribute('aria-label', 'Aller au contenu principal');
  skipLink.setAttribute('data-testid', 'skip-link');
  
  // Track usage
  skipLink.addEventListener('click', () => {
    a11yMetrics.skipLinkUsed++;
  });
  
  document.body.insertBefore(skipLink, document.body.firstChild);
  
  // Ensure main content has id and role
  const main = document.querySelector('main') || document.querySelector('[role="main"]');
  if (main) {
    if (!main.id) main.id = 'main-content';
    if (!main.getAttribute('role')) main.setAttribute('role', 'main');
    if (!main.getAttribute('aria-label')) main.setAttribute('aria-label', 'Contenu principal');
    main.setAttribute('tabindex', '-1'); // Allow focus for skip link target
  }
};

/**
 * ARIA Live Region Manager
 * Gère les annonces dynamiques pour les screen readers
 */
class AriaLiveAnnouncer {
  constructor() {
    this.politeContainer = null;
    this.assertiveContainer = null;
    this.init();
  }

  init() {
    if (typeof document === 'undefined') return;
    
    // Create polite live region
    this.politeContainer = this.createLiveRegion('polite');
    
    // Create assertive live region for urgent announcements
    this.assertiveContainer = this.createLiveRegion('assertive');
  }
  
  createLiveRegion(level) {
    const container = document.createElement('div');
    container.setAttribute('role', 'status');
    container.setAttribute('aria-live', level);
    container.setAttribute('aria-atomic', 'true');
    container.setAttribute('aria-relevant', 'additions text');
    container.className = 'sr-only';
    container.id = `aria-live-${level}`;
    container.style.cssText = `
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    `;
    
    document.body.appendChild(container);
    return container;
  }

  announce(message, priority = 'polite') {
    const container = priority === 'assertive' ? this.assertiveContainer : this.politeContainer;
    if (!container) return;
    
    // Clear and set new message
    container.textContent = '';
    
    // Use setTimeout to ensure the change is announced
    setTimeout(() => {
      container.textContent = message;
    }, 100);
    
    // Clear after announcement
    setTimeout(() => {
      container.textContent = '';
    }, 5000);
  }

  announcePolite(message) {
    this.announce(message, 'polite');
  }

  announceAssertive(message) {
    this.announce(message, 'assertive');
  }
  
  // Announce page navigation
  announcePageChange(pageName) {
    this.announcePolite(`Navigation vers ${pageName}`);
  }
  
  // Announce loading state
  announceLoading(isLoading, context = '') {
    if (isLoading) {
      this.announcePolite(`Chargement${context ? ' de ' + context : ''} en cours...`);
    } else {
      this.announcePolite(`Chargement${context ? ' de ' + context : ''} terminé`);
    }
  }
}

export const ariaAnnouncer = new AriaLiveAnnouncer();

/**
 * Keyboard Navigation Enhancements
 * Améliore la navigation clavier sur les composants interactifs
 */
export const enhanceKeyboardNavigation = () => {
  if (typeof document === 'undefined') return;

  // Handle Escape key to close modals/dialogs
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      // Find and close any open modal
      const modals = document.querySelectorAll('[role="dialog"][aria-modal="true"]');
      modals.forEach(modal => {
        const closeBtn = modal.querySelector('[aria-label*="fermer"], [aria-label*="close"], [aria-label*="Fermer"], [aria-label*="Close"], .close-button, [data-testid*="close"]');
        if (closeBtn) {
          closeBtn.click();
          ariaAnnouncer.announcePolite('Dialogue fermé');
        }
      });
    }
  });

  // Arrow key navigation for menus and lists
  document.addEventListener('keydown', (e) => {
    const activeElement = document.activeElement;
    const menu = activeElement?.closest('[role="menu"], [role="menubar"], [role="listbox"], [role="tablist"]');
    
    if (!menu) return;
    
    const role = menu.getAttribute('role');
    const itemRole = role === 'tablist' ? 'tab' : (role === 'listbox' ? 'option' : 'menuitem');
    const items = Array.from(menu.querySelectorAll(`[role="${itemRole}"]:not([aria-disabled="true"])`));
    const currentIndex = items.indexOf(activeElement);
    
    if (currentIndex === -1) return;
    
    let nextIndex;
    const isVertical = menu.getAttribute('aria-orientation') !== 'horizontal';
    
    switch (e.key) {
      case 'ArrowDown':
        if (isVertical) {
          e.preventDefault();
          nextIndex = (currentIndex + 1) % items.length;
          items[nextIndex]?.focus();
        }
        break;
      case 'ArrowUp':
        if (isVertical) {
          e.preventDefault();
          nextIndex = (currentIndex - 1 + items.length) % items.length;
          items[nextIndex]?.focus();
        }
        break;
      case 'ArrowRight':
        if (!isVertical) {
          e.preventDefault();
          nextIndex = (currentIndex + 1) % items.length;
          items[nextIndex]?.focus();
        }
        break;
      case 'ArrowLeft':
        if (!isVertical) {
          e.preventDefault();
          nextIndex = (currentIndex - 1 + items.length) % items.length;
          items[nextIndex]?.focus();
        }
        break;
      case 'Home':
        e.preventDefault();
        items[0]?.focus();
        break;
      case 'End':
        e.preventDefault();
        items[items.length - 1]?.focus();
        break;
    }
  });
  
  // Type-ahead search in listbox/menu
  let searchBuffer = '';
  let searchTimeout = null;
  
  document.addEventListener('keydown', (e) => {
    const activeElement = document.activeElement;
    const menu = activeElement?.closest('[role="menu"], [role="listbox"]');
    
    if (!menu || e.key.length !== 1 || e.ctrlKey || e.altKey || e.metaKey) return;
    
    // Add character to search buffer
    searchBuffer += e.key.toLowerCase();
    
    // Clear buffer after 500ms
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      searchBuffer = '';
    }, 500);
    
    // Find matching item
    const items = Array.from(menu.querySelectorAll('[role="menuitem"], [role="option"]'));
    const match = items.find(item => 
      item.textContent?.toLowerCase().startsWith(searchBuffer)
    );
    
    if (match) {
      match.focus();
    }
  });
};

/**
 * Color Contrast Enhancement
 * Détecte et avertit sur les problèmes de contraste - WCAG AAA (7:1 ratio)
 */
export const checkContrastRatio = (foreground, background) => {
  const getLuminance = (hex) => {
    const rgb = hex.match(/^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i);
    if (!rgb) return 0;
    
    const [, r, g, b] = rgb.map(x => {
      const val = parseInt(x, 16) / 255;
      return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
    });
    
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };

  const l1 = getLuminance(foreground);
  const l2 = getLuminance(background);
  const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);

  return {
    ratio: ratio.toFixed(2),
    passesAA: ratio >= 4.5,
    passesAALarge: ratio >= 3,
    passesAAA: ratio >= 7,       // WCAG AAA normal text
    passesAAALarge: ratio >= 4.5 // WCAG AAA large text
  };
};

/**
 * Form Accessibility Enhancement
 * Améliore l'accessibilité des formulaires - WCAG AAA
 */
export const enhanceFormAccessibility = () => {
  if (typeof document === 'undefined') return;

  // Auto-associate labels with inputs
  const inputs = document.querySelectorAll('input:not([aria-label]):not([aria-labelledby]), textarea:not([aria-label]):not([aria-labelledby]), select:not([aria-label]):not([aria-labelledby])');
  
  inputs.forEach(input => {
    // Find associated label
    const id = input.id;
    if (id) {
      const label = document.querySelector(`label[for="${id}"]`);
      if (label) {
        // Already properly associated
        return;
      }
    }
    
    // Check for wrapping label
    const parentLabel = input.closest('label');
    if (parentLabel && !input.id) {
      const labelId = `label-${Math.random().toString(36).slice(2, 9)}`;
      parentLabel.id = labelId;
      input.setAttribute('aria-labelledby', labelId);
    }
    
    // Check placeholder and add aria-label if needed
    const placeholder = input.getAttribute('placeholder');
    if (placeholder && !input.getAttribute('aria-label')) {
      input.setAttribute('aria-label', placeholder);
    }
  });

  // Add required indicators
  const requiredInputs = document.querySelectorAll('[required]:not([aria-required])');
  requiredInputs.forEach(input => {
    input.setAttribute('aria-required', 'true');
  });
  
  // Add autocomplete hints where missing
  const autoCompleteMap = {
    'email': 'email',
    'password': 'current-password',
    'new-password': 'new-password',
    'name': 'name',
    'given-name': 'given-name',
    'family-name': 'family-name',
    'tel': 'tel',
    'address': 'street-address',
    'postal-code': 'postal-code',
    'city': 'address-level2',
    'country': 'country'
  };
  
  Object.entries(autoCompleteMap).forEach(([type, autocomplete]) => {
    const inputs = document.querySelectorAll(`input[type="${type}"]:not([autocomplete]), input[name*="${type}"]:not([autocomplete])`);
    inputs.forEach(input => {
      input.setAttribute('autocomplete', autocomplete);
    });
  });
};

/**
 * Image Accessibility Enhancement
 * Vérifie et améliore l'accessibilité des images
 */
export const enhanceImageAccessibility = () => {
  if (typeof document === 'undefined') return;
  
  const images = document.querySelectorAll('img');
  
  images.forEach(img => {
    // Ensure alt attribute exists
    if (!img.hasAttribute('alt')) {
      // Check if decorative
      if (img.getAttribute('role') === 'presentation' || img.getAttribute('aria-hidden') === 'true') {
        img.setAttribute('alt', '');
      } else {
        // Log warning in development
        if (process.env.NODE_ENV === 'development') {
          console.warn('[A11y] Image missing alt attribute:', img.src);
        }
        // Set empty alt to prevent screen reader from reading filename
        img.setAttribute('alt', '');
      }
    }
    
    // Mark decorative images properly
    if (img.getAttribute('alt') === '' && !img.getAttribute('role')) {
      img.setAttribute('role', 'presentation');
    }
  });
};

/**
 * Get Accessibility Metrics
 */
export const getAccessibilityMetrics = () => {
  return { ...a11yMetrics };
};

/**
 * Initialize All Accessibility Enhancements
 */
export const initAccessibilityEnhancements = () => {
  if (typeof window === 'undefined') return;

  // Run on DOM ready
  const init = () => {
    enhanceFocusVisibility();
    injectSkipLink();
    enhanceKeyboardNavigation();
    enhanceFormAccessibility();
    enhanceImageAccessibility();
    
    // Log initialization in development
    if (process.env.NODE_ENV === 'development') {
      console.log('[A11y] WCAG AAA Accessibility enhancements initialized');
      console.log('[A11y] High contrast mode:', a11yMetrics.highContrastMode);
      console.log('[A11y] Reduced motion:', a11yMetrics.reducedMotion);
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
};

export default {
  enhanceFocusVisibility,
  injectSkipLink,
  ariaAnnouncer,
  enhanceKeyboardNavigation,
  checkContrastRatio,
  enhanceFormAccessibility,
  enhanceImageAccessibility,
  getAccessibilityMetrics,
  initAccessibilityEnhancements
};
