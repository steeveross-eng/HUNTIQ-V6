/**
 * SEO Head Component - PHASE E (SEO AVANCÉ)
 * 
 * Gère les balises meta, OpenGraph, Twitter Cards, Canonical et Schema.org JSON-LD
 * Conforme aux directives BIONIC V5 et aux standards Google 2026
 * 
 * @module SEOHead
 * @version 2.0.0
 * @phase E
 */

import { useEffect, useState, useCallback, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const SITE_URL = process.env.REACT_APP_SITE_URL || process.env.REACT_APP_BACKEND_URL || 'https://bionic-huntiq.com';
const SITE_NAME = 'Chasse Bionic TM';
const SITE_NAME_EN = 'Bionic Hunt TM';

/**
 * Organization Schema - JSON-LD
 * Représente l'entité légale derrière BIONIC HUNT/Chasse
 */
const ORGANIZATION_SCHEMA = {
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": `${SITE_URL}/#organization`,
  "name": SITE_NAME,
  "alternateName": [SITE_NAME_EN, "BIONIC HUNT/Chasse", "BIONIC Hunt"],
  "url": SITE_URL,
  "logo": {
    "@type": "ImageObject",
    "url": `${SITE_URL}/logos/bionic-logo.svg`,
    "width": 512,
    "height": 512
  },
  "sameAs": [
    "https://facebook.com/chassebionic",
    "https://instagram.com/chassebionic",
    "https://twitter.com/chassebionic"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "customer service",
    "availableLanguage": ["French", "English"]
  },
  "address": {
    "@type": "PostalAddress",
    "addressCountry": "CA",
    "addressRegion": "QC"
  }
};

/**
 * WebSite Schema - JSON-LD
 * Représente le site web avec SearchAction
 */
const WEBSITE_SCHEMA = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  "@id": `${SITE_URL}/#website`,
  "name": SITE_NAME,
  "alternateName": SITE_NAME_EN,
  "url": SITE_URL,
  "description": "Votre parcours guidé vers une chasse parfaite. Analysez, comparez et trouvez les meilleurs attractants avec la science BIONIC.",
  "inLanguage": ["fr-CA", "en-CA"],
  "publisher": {
    "@id": `${SITE_URL}/#organization`
  },
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": `${SITE_URL}/shop?search={search_term_string}`
    },
    "query-input": "required name=search_term_string"
  }
};

/**
 * Page-specific metadata configuration
 */
const PAGE_META_CONFIG = {
  '/': {
    title: 'Chasse Bionic TM | Votre parcours guidé vers une chasse parfaite',
    titleEn: 'Bionic Hunt TM | Your guided path to a perfect hunt',
    description: 'Analysez, comparez et trouvez les meilleurs attractants pour le chevreuil, orignal et ours. Science BIONIC validée sur le terrain.',
    descriptionEn: 'Analyze, compare and find the best attractants for deer, moose and bear. Field-validated BIONIC science.',
    type: 'website',
    priority: 1.0
  },
  '/shop': {
    title: 'Magasin | Attractants & Équipement de Chasse | Chasse Bionic',
    titleEn: 'Shop | Hunting Attractants & Equipment | Bionic Hunt',
    description: 'Découvrez notre sélection d\'attractants analysés scientifiquement. Orignal, chevreuil, ours - trouvez le meilleur pour votre territoire.',
    descriptionEn: 'Discover our scientifically analyzed attractant selection. Moose, deer, bear - find the best for your territory.',
    type: 'website',
    priority: 0.9
  },
  '/map': {
    title: 'Carte Interactive | GPS & Waypoints | Chasse Bionic',
    titleEn: 'Interactive Map | GPS & Waypoints | Bionic Hunt',
    description: 'Cartographiez votre territoire de chasse avec GPS haute précision. Waypoints, zones de chasse, corridors de gibier.',
    descriptionEn: 'Map your hunting territory with high precision GPS. Waypoints, hunting zones, game corridors.',
    type: 'website',
    priority: 0.8
  },
  '/territoire': {
    title: 'Mon Territoire BIONIC | Analyse IA | Chasse Bionic',
    titleEn: 'My BIONIC Territory | AI Analysis | Bionic Hunt',
    description: 'Analysez votre territoire avec l\'intelligence artificielle BIONIC. Zones d\'habitat, mouvements, points stratégiques.',
    descriptionEn: 'Analyze your territory with BIONIC artificial intelligence. Habitat zones, movements, strategic points.',
    type: 'website',
    priority: 0.8
  },
  '/forecast': {
    title: 'Prévisions de Chasse | Météo & Activité | Chasse Bionic',
    titleEn: 'Hunting Forecast | Weather & Activity | Bionic Hunt',
    description: 'Prévisions météo adaptées à la chasse. Score d\'activité du gibier, conditions optimales, phases lunaires.',
    descriptionEn: 'Hunting-adapted weather forecasts. Game activity score, optimal conditions, moon phases.',
    type: 'website',
    priority: 0.7
  },
  '/permis-chasse': {
    title: 'Permis de Chasse | Guide Complet Canada & USA | Chasse Bionic',
    titleEn: 'Hunting License | Complete Canada & USA Guide | Bionic Hunt',
    description: 'Guide complet des permis de chasse au Canada et aux États-Unis. Liens officiels par province et état.',
    descriptionEn: 'Complete hunting license guide for Canada and USA. Official links by province and state.',
    type: 'website',
    priority: 0.8
  },
  '/pricing': {
    title: 'Tarifs Premium | Plans & Abonnements | Chasse Bionic',
    titleEn: 'Premium Pricing | Plans & Subscriptions | Bionic Hunt',
    description: 'Découvrez nos forfaits Premium et Pro. Accédez à toutes les fonctionnalités BIONIC pour optimiser votre chasse.',
    descriptionEn: 'Discover our Premium and Pro plans. Access all BIONIC features to optimize your hunt.',
    type: 'website',
    priority: 0.7
  },
  '/dashboard': {
    title: 'Tableau de Bord | Mes Statistiques | Chasse Bionic',
    titleEn: 'Dashboard | My Statistics | Bionic Hunt',
    description: 'Votre tableau de bord personnalisé. Statistiques de chasse, historique, performances et recommandations.',
    descriptionEn: 'Your personalized dashboard. Hunting statistics, history, performance and recommendations.',
    type: 'website',
    priority: 0.5
  },
  '/trips': {
    title: 'Mes Sorties | Planification & Historique | Chasse Bionic',
    titleEn: 'My Trips | Planning & History | Bionic Hunt',
    description: 'Planifiez et suivez vos sorties de chasse. Historique complet, météo, observations et succès.',
    descriptionEn: 'Plan and track your hunting trips. Complete history, weather, observations and success.',
    type: 'website',
    priority: 0.7
  },
  '/analyze': {
    title: 'Analyseur BIONIC | Évaluation Scientifique | Chasse Bionic',
    titleEn: 'BIONIC Analyzer | Scientific Evaluation | Bionic Hunt',
    description: 'Analysez n\'importe quel attractant avec nos 13 critères scientifiques. Score BIONIC validé sur le terrain.',
    descriptionEn: 'Analyze any attractant with our 13 scientific criteria. Field-validated BIONIC score.',
    type: 'website',
    priority: 0.8
  },
  '/compare': {
    title: 'Comparateur | Comparez les Attractants | Chasse Bionic',
    titleEn: 'Comparator | Compare Attractants | Bionic Hunt',
    description: 'Comparez les attractants côte à côte. Analyse comparative sur 13 critères pour trouver le meilleur choix.',
    descriptionEn: 'Compare attractants side by side. Comparative analysis on 13 criteria to find the best choice.',
    type: 'website',
    priority: 0.8
  }
};

/**
 * SEOHead Component
 * Manages all SEO-related meta tags dynamically
 */
const SEOHead = () => {
  const location = useLocation();
  const [serverMeta, setServerMeta] = useState(null);

  // Get page-specific config or default
  const pageConfig = useMemo(() => {
    return PAGE_META_CONFIG[location.pathname] || PAGE_META_CONFIG['/'];
  }, [location.pathname]);

  // Fetch server-side meta if available
  useEffect(() => {
    const fetchMeta = async () => {
      try {
        const path = location.pathname.replace(/^\//, '') || '';
        const response = await axios.get(`${API}/seo/meta/${path}`);
        if (response.data) {
          setServerMeta(response.data);
        }
      } catch {
        // Use client-side config
        setServerMeta(null);
      }
    };
    fetchMeta();
  }, [location.pathname]);

  // Update meta tags
  const updateMetaTags = useCallback((config, server) => {
    const data = server || config;
    const canonicalUrl = `${SITE_URL}${location.pathname}`;

    // Helper to update or create meta tags
    const setMeta = (name, content, isProperty = false) => {
      if (!content) return;
      const attr = isProperty ? 'property' : 'name';
      let el = document.querySelector(`meta[${attr}="${name}"]`);
      if (!el) {
        el = document.createElement('meta');
        el.setAttribute(attr, name);
        document.head.appendChild(el);
      }
      el.setAttribute('content', content);
    };

    // Helper to update or create link tags
    const setLink = (rel, href, attrs = {}) => {
      if (!href) return;
      let el = document.querySelector(`link[rel="${rel}"]${attrs.hreflang ? `[hreflang="${attrs.hreflang}"]` : ''}`);
      if (!el) {
        el = document.createElement('link');
        el.setAttribute('rel', rel);
        document.head.appendChild(el);
      }
      el.setAttribute('href', href);
      Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, value));
    };

    // ===== TITLE =====
    document.title = data.title || config.title;

    // ===== BASIC META =====
    setMeta('description', data.description || config.description);
    setMeta('keywords', 'chasse, hunting, attractant, orignal, moose, chevreuil, deer, ours, bear, Québec, Quebec, BIONIC, territoire, territory, GPS, waypoints');
    setMeta('author', SITE_NAME);
    setMeta('robots', 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1');
    setMeta('googlebot', 'index, follow');

    // ===== OPEN GRAPH =====
    setMeta('og:title', data.title || config.title, true);
    setMeta('og:description', data.description || config.description, true);
    setMeta('og:type', data.type || config.type || 'website', true);
    setMeta('og:url', canonicalUrl, true);
    setMeta('og:site_name', SITE_NAME, true);
    setMeta('og:locale', 'fr_CA', true);
    setMeta('og:locale:alternate', 'en_CA', true);
    setMeta('og:image', `${SITE_URL}/og-image.jpg`, true);
    setMeta('og:image:width', '1200', true);
    setMeta('og:image:height', '630', true);
    setMeta('og:image:alt', 'Chasse Bionic - Votre parcours guidé vers une chasse parfaite', true);

    // ===== TWITTER CARDS =====
    setMeta('twitter:card', 'summary_large_image');
    setMeta('twitter:site', '@chassebionic');
    setMeta('twitter:creator', '@chassebionic');
    setMeta('twitter:title', data.title || config.title);
    setMeta('twitter:description', data.description || config.description);
    setMeta('twitter:image', `${SITE_URL}/og-image.jpg`);
    setMeta('twitter:image:alt', 'Chasse Bionic - Votre parcours guidé vers une chasse parfaite');

    // ===== CANONICAL & HREFLANG =====
    setLink('canonical', canonicalUrl);
    setLink('alternate', canonicalUrl, { hreflang: 'fr-CA' });
    setLink('alternate', canonicalUrl, { hreflang: 'en-CA' });
    setLink('alternate', canonicalUrl, { hreflang: 'x-default' });

    // ===== JSON-LD SCHEMAS =====
    // Remove existing JSON-LD scripts
    document.querySelectorAll('script[type="application/ld+json"][data-seo-head]').forEach(el => el.remove());

    // WebPage Schema
    const webPageSchema = {
      "@context": "https://schema.org",
      "@type": "WebPage",
      "@id": `${canonicalUrl}#webpage`,
      "url": canonicalUrl,
      "name": data.title || config.title,
      "description": data.description || config.description,
      "isPartOf": {
        "@id": `${SITE_URL}/#website`
      },
      "about": {
        "@id": `${SITE_URL}/#organization`
      },
      "inLanguage": "fr-CA",
      "potentialAction": {
        "@type": "ReadAction",
        "target": [canonicalUrl]
      }
    };

    // BreadcrumbList Schema
    const breadcrumbs = generateBreadcrumbs(location.pathname);
    const breadcrumbSchema = {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": breadcrumbs
    };

    // Inject all schemas
    const schemas = [ORGANIZATION_SCHEMA, WEBSITE_SCHEMA, webPageSchema, breadcrumbSchema];
    schemas.forEach((schema, index) => {
      const script = document.createElement('script');
      script.type = 'application/ld+json';
      script.setAttribute('data-seo-head', `schema-${index}`);
      script.textContent = JSON.stringify(schema);
      document.head.appendChild(script);
    });

  }, [location.pathname]);

  // Apply meta tags on config or server data change
  useEffect(() => {
    updateMetaTags(pageConfig, serverMeta);
  }, [pageConfig, serverMeta, updateMetaTags]);

  return null;
};

/**
 * Generate breadcrumb items for BreadcrumbList schema
 * @param {string} pathname - Current page path
 * @returns {Array} Breadcrumb items
 */
function generateBreadcrumbs(pathname) {
  const items = [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Accueil",
      "item": SITE_URL
    }
  ];

  if (pathname === '/') return items;

  const pathParts = pathname.split('/').filter(Boolean);
  let currentPath = SITE_URL;

  const pathNames = {
    'shop': 'Magasin',
    'map': 'Carte Interactive',
    'territoire': 'Mon Territoire',
    'forecast': 'Prévisions',
    'permis-chasse': 'Permis de Chasse',
    'pricing': 'Tarifs',
    'dashboard': 'Tableau de Bord',
    'trips': 'Sorties',
    'analyze': 'Analyseur',
    'compare': 'Comparateur',
    'analytics': 'Analytics',
    'business': 'Business'
  };

  pathParts.forEach((part, index) => {
    currentPath += `/${part}`;
    items.push({
      "@type": "ListItem",
      "position": index + 2,
      "name": pathNames[part] || part.charAt(0).toUpperCase() + part.slice(1),
      "item": currentPath
    });
  });

  return items;
}

export default SEOHead;
