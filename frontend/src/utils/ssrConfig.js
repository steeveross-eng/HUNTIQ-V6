/**
 * SSR/Pre-rendering Configuration - BRANCHE 3 (99% → 99.9%)
 * 
 * Configuration pour le pré-rendu des routes critiques
 * Compatible avec: react-snap, prerender.io, Vercel ISR
 * 
 * NOTE: Ce module configure le pré-rendu statique (SSG) plutôt que
 * le SSR dynamique pour maintenir la compatibilité avec CRA.
 * Aucune modification de logique métier.
 * 
 * @module ssrConfig
 * @version 1.0.0
 * @phase BRANCHE_3
 */

/**
 * Routes à pré-rendre statiquement
 * Ces routes sont importantes pour le SEO et le FCP
 */
export const PRERENDER_ROUTES = [
  '/',
  '/shop',
  '/pricing',
  '/about',
  '/contact',
  '/terms',
  '/privacy'
];

/**
 * Routes dynamiques (ne pas pré-rendre)
 */
export const DYNAMIC_ROUTES = [
  '/dashboard',
  '/admin',
  '/profile',
  '/cart',
  '/checkout',
  '/trips'
];

/**
 * Configuration react-snap pour le pré-rendu
 */
export const REACT_SNAP_CONFIG = {
  // Routes à capturer
  include: PRERENDER_ROUTES,
  
  // Routes à exclure
  exclude: [
    ...DYNAMIC_ROUTES,
    '/api',
    '/static',
    '/logos'
  ],
  
  // Options de rendu
  puppeteerArgs: ['--no-sandbox', '--disable-setuid-sandbox'],
  puppeteerExecutablePath: undefined,
  
  // Attendre que le réseau soit inactif
  waitFor: 2000,
  
  // Inline les styles critiques
  inlineCss: true,
  
  // Minifier le HTML
  minifyHtml: {
    collapseWhitespace: true,
    removeComments: true
  },
  
  // Capturer les liens pour le crawling
  crawl: true,
  
  // Source directory
  source: 'build',
  
  // Concurrence
  concurrency: 4
};

/**
 * Configuration Vercel pour ISR (Incremental Static Regeneration)
 */
export const VERCEL_ISR_CONFIG = {
  // Revalidation time in seconds
  revalidate: 3600, // 1 hour
  
  // Fallback behavior
  fallback: 'blocking',
  
  // Routes avec ISR
  routes: PRERENDER_ROUTES.map(route => ({
    path: route,
    revalidate: 3600
  }))
};

/**
 * Prerender.io configuration (pour les crawlers)
 */
export const PRERENDER_IO_CONFIG = {
  // Token (à remplacer en production)
  token: process.env.PRERENDER_TOKEN || '',
  
  // User agents à pré-rendre
  crawlerUserAgents: [
    'googlebot',
    'bingbot',
    'yandex',
    'baiduspider',
    'facebookexternalhit',
    'twitterbot',
    'linkedinbot',
    'whatsapp',
    'slackbot',
    'telegrambot'
  ],
  
  // Extensions à ignorer
  extensionsToIgnore: [
    '.js', '.css', '.xml', '.less', '.png', '.jpg', '.jpeg',
    '.gif', '.pdf', '.doc', '.txt', '.ico', '.rss', '.zip',
    '.mp3', '.rar', '.exe', '.wmv', '.doc', '.avi', '.ppt',
    '.mpg', '.mpeg', '.tif', '.wav', '.mov', '.psd', '.ai',
    '.xls', '.mp4', '.m4a', '.swf', '.dat', '.dmg', '.iso',
    '.flv', '.m4v', '.torrent', '.woff', '.woff2', '.ttf',
    '.svg', '.webp', '.avif'
  ],
  
  // Blacklist paths
  blacklistedPaths: [
    '/api/*',
    '/admin/*',
    '/dashboard/*'
  ]
};

/**
 * Helmet meta tags for pre-rendered pages
 * Ces tags sont injectés lors du pré-rendu
 */
export const getMetaTagsForRoute = (route) => {
  const baseUrl = 'https://chassebionic.com';
  
  const defaultMeta = {
    title: 'Chasse Bionic™ | Bionic Hunt™',
    description: 'Votre parcours guidé vers une chasse parfaite. Analysez et comparez avec confiance votre territoire.',
    image: `${baseUrl}/logos/bionic-logo-official.png`,
    url: `${baseUrl}${route}`
  };
  
  const routeMeta = {
    '/': {
      title: 'Chasse Bionic™ | Bionic Hunt™ - Accueil',
      description: 'Bionic Hunt™ redéfinit l\'art de la chasse moderne. Analysez et comparez avec confiance votre territoire, ses hotspots, terres à louer et produits top performants.'
    },
    '/shop': {
      title: 'Boutique | Chasse Bionic™',
      description: 'Découvrez notre sélection de produits de chasse haut de gamme. Équipement vérifié et recommandé par les experts.'
    },
    '/pricing': {
      title: 'Tarifs | Chasse Bionic™',
      description: 'Découvrez nos offres Premium et accédez à toutes les fonctionnalités de Bionic Hunt™.'
    },
    '/about': {
      title: 'À propos | Chasse Bionic™',
      description: 'Découvrez l\'histoire et la mission de Chasse Bionic™. La science valide ce que le terrain confirme.'
    }
  };
  
  return {
    ...defaultMeta,
    ...(routeMeta[route] || {})
  };
};

/**
 * Generate structured data for pre-rendered pages
 */
export const getStructuredDataForRoute = (route) => {
  const baseData = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'Chasse Bionic™',
    url: 'https://chassebionic.com',
    potentialAction: {
      '@type': 'SearchAction',
      target: 'https://chassebionic.com/search?q={search_term_string}',
      'query-input': 'required name=search_term_string'
    }
  };
  
  if (route === '/shop') {
    return {
      ...baseData,
      '@type': 'Store',
      name: 'Boutique Chasse Bionic™'
    };
  }
  
  return baseData;
};

/**
 * Check if current request is from a crawler
 */
export const isCrawler = (userAgent) => {
  if (!userAgent) return false;
  
  const ua = userAgent.toLowerCase();
  return PRERENDER_IO_CONFIG.crawlerUserAgents.some(
    crawler => ua.includes(crawler)
  );
};

/**
 * Should prerender this route?
 */
export const shouldPrerender = (route) => {
  // Check if route is in prerender list
  if (PRERENDER_ROUTES.includes(route)) return true;
  
  // Check if route matches a pattern
  return PRERENDER_ROUTES.some(prerenderRoute => {
    if (prerenderRoute.endsWith('*')) {
      const prefix = prerenderRoute.slice(0, -1);
      return route.startsWith(prefix);
    }
    return false;
  });
};

/**
 * Initialize SSR/pre-rendering configuration
 */
export const initSSRConfig = () => {
  // Add prerender meta tag for react-snap
  if (typeof document !== 'undefined') {
    const existingTag = document.querySelector('meta[name="prerender-status-code"]');
    if (!existingTag) {
      const meta = document.createElement('meta');
      meta.name = 'prerender-status-code';
      meta.content = '200';
      document.head.appendChild(meta);
    }
  }
  
  if (process.env.NODE_ENV === 'development') {
    console.log('[SSR Config] Pre-render routes:', PRERENDER_ROUTES);
    console.log('[SSR Config] Dynamic routes:', DYNAMIC_ROUTES);
  }
};

export default {
  PRERENDER_ROUTES,
  DYNAMIC_ROUTES,
  REACT_SNAP_CONFIG,
  VERCEL_ISR_CONFIG,
  PRERENDER_IO_CONFIG,
  getMetaTagsForRoute,
  getStructuredDataForRoute,
  isCrawler,
  shouldPrerender,
  initSSRConfig
};
