/**
 * BIONIC DESIGN SYSTEM - Colors Configuration
 * Palette centralisée pour toute l'application
 * Version: 1.0.0
 * 
 * RÈGLES:
 * - Utiliser UNIQUEMENT ces couleurs
 * - Aucune couleur hardcodée dans les composants
 * - Importer ce fichier pour tous les styles dynamiques
 */

// ============================================
// PALETTE TACTIQUE PRINCIPALE
// ============================================

export const BIONIC_COLORS = {
  // Noir - Backgrounds
  black: {
    pure: '#000000',
    deep: '#0a0a0a',
    base: '#121212',
    elevated: '#1a1a1a',
  },
  
  // Gris Scientifique
  gray: {
    900: '#1a1a1a',
    800: '#2a2a2a',
    700: '#3a3a3a',
    600: '#4a4a4a',
    500: '#6a6a6a',
    400: '#8a8a8a',
    300: '#a0a0a0',
    200: '#b0b0b0',
    100: '#d0d0d0',
  },
  
  // Jaune Analytique (Accent Principal)
  gold: {
    primary: '#F5A623',
    light: '#FBBF24',
    lighter: '#FCD34D',
    dark: '#D4890E',
    muted: 'rgba(245, 166, 35, 0.1)',
    glow: 'rgba(245, 166, 35, 0.4)',
  },
  
  // Bleu Analytique
  blue: {
    primary: '#1E40AF',
    light: '#3B82F6',
    lighter: '#60A5FA',
    dark: '#1E3A8A',
    muted: 'rgba(59, 130, 246, 0.1)',
  },
  
  // Vert Tactique
  green: {
    primary: '#10B981',
    light: '#34D399',
    dark: '#059669',
    muted: 'rgba(16, 185, 129, 0.1)',
  },
  
  // Rouge Alerte
  red: {
    primary: '#EF4444',
    light: '#F87171',
    dark: '#DC2626',
    muted: 'rgba(239, 68, 68, 0.1)',
  },
  
  // Violet Analytique
  purple: {
    primary: '#8B5CF6',
    light: '#A78BFA',
    muted: 'rgba(139, 92, 246, 0.1)',
  },
  
  // Cyan Tactique
  cyan: {
    primary: '#06B6D4',
    light: '#22D3EE',
    muted: 'rgba(6, 182, 212, 0.1)',
  },
  
  // Blanc
  white: {
    pure: '#FFFFFF',
    muted: 'rgba(255, 255, 255, 0.8)',
  },
};

// ============================================
// COULEURS SÉMANTIQUES
// ============================================

export const SEMANTIC_COLORS = {
  // Backgrounds
  bg: {
    primary: BIONIC_COLORS.black.base,
    secondary: BIONIC_COLORS.black.elevated,
    card: BIONIC_COLORS.gray[900],
    hover: 'rgba(255, 255, 255, 0.05)',
    active: BIONIC_COLORS.gold.muted,
  },
  
  // Borders
  border: {
    primary: BIONIC_COLORS.gray[700],
    secondary: BIONIC_COLORS.gray[800],
    accent: BIONIC_COLORS.gold.primary,
  },
  
  // Text
  text: {
    primary: '#FFFFFF',
    secondary: BIONIC_COLORS.gray[400],
    muted: BIONIC_COLORS.gray[500],
    accent: BIONIC_COLORS.gold.primary,
  },
  
  // States
  state: {
    success: BIONIC_COLORS.green.primary,
    warning: BIONIC_COLORS.gold.primary,
    error: BIONIC_COLORS.red.primary,
    info: BIONIC_COLORS.blue.light,
  },
};

// ============================================
// COULEURS PAR TYPE DE TERRITOIRE
// ============================================

export const TERRITORY_COLORS = {
  zec: BIONIC_COLORS.green.primary,          // ZEC
  pourvoirie: BIONIC_COLORS.blue.light,      // Pourvoirie
  private: BIONIC_COLORS.gold.primary,       // Territoire privé
  reserve: BIONIC_COLORS.purple.primary,     // Réserve faunique
  stand: BIONIC_COLORS.red.primary,          // Affût / Cache
  salt_lick: BIONIC_COLORS.cyan.primary,     // Saline
  observation: BIONIC_COLORS.blue.lighter,   // Point d'observation
  parking: BIONIC_COLORS.gray[500],          // Stationnement
  camp: BIONIC_COLORS.green.light,           // Camp de chasse
  other: BIONIC_COLORS.purple.light,         // Autre lieu
};

// ============================================
// COULEURS PAR TYPE DE WAYPOINT
// ============================================

export const WAYPOINT_COLORS = {
  hunting: BIONIC_COLORS.gold.primary,       // Spot de chasse
  camera: BIONIC_COLORS.blue.light,          // Caméra
  feeding: BIONIC_COLORS.green.primary,      // Zone alimentation
  observation: BIONIC_COLORS.purple.primary, // Observation
  blind: BIONIC_COLORS.red.primary,          // Affût
  custom: BIONIC_COLORS.gray[500],           // Autre
};

// ============================================
// COULEURS DE SCORE
// ============================================

export const SCORE_COLORS = {
  excellent: BIONIC_COLORS.green.primary,  // 80-100
  good: BIONIC_COLORS.gold.primary,        // 60-79
  average: BIONIC_COLORS.blue.light,       // 40-59
  poor: BIONIC_COLORS.red.primary,         // 0-39
};

/**
 * Obtenir la couleur selon le score
 * @param {number} score - Score entre 0 et 100
 * @returns {string} - Couleur hexadécimale
 */
export const getScoreColor = (score) => {
  if (score >= 80) return SCORE_COLORS.excellent;
  if (score >= 60) return SCORE_COLORS.good;
  if (score >= 40) return SCORE_COLORS.average;
  return SCORE_COLORS.poor;
};

/**
 * Obtenir le label selon le score
 * @param {number} score - Score entre 0 et 100
 * @returns {string} - Label descriptif
 */
export const getScoreLabel = (score) => {
  if (score >= 80) return 'excellent';
  if (score >= 60) return 'good';
  if (score >= 40) return 'average';
  return 'poor';
};

// ============================================
// COULEURS DE CATÉGORIE ADMIN
// ============================================

export const CATEGORY_COLORS = {
  standard: BIONIC_COLORS.gray[500],
  premium: BIONIC_COLORS.gold.primary,
  land_rental: BIONIC_COLORS.green.primary,
  environmental: BIONIC_COLORS.blue.light,
  inactive: BIONIC_COLORS.red.primary,
};

// ============================================
// COULEURS DE ZONES AVANCÉES
// ============================================

export const ZONE_COLORS = {
  rutting: BIONIC_COLORS.red.primary,
  bedding: BIONIC_COLORS.blue.primary,
  feeding: BIONIC_COLORS.green.primary,
  water: BIONIC_COLORS.cyan.primary,
  observation: BIONIC_COLORS.purple.primary,
  blind: BIONIC_COLORS.gold.primary,
  trail: BIONIC_COLORS.gray[500],
  scrape: BIONIC_COLORS.gold.dark,
  rub: BIONIC_COLORS.gold.light,
  crossing: BIONIC_COLORS.blue.light,
  funnel: BIONIC_COLORS.purple.light,
  staging: BIONIC_COLORS.green.light,
  thermal: BIONIC_COLORS.cyan.light,
  sanctuary: BIONIC_COLORS.blue.dark,
};

// ============================================
// GRADIENTS
// ============================================

export const BIONIC_GRADIENTS = {
  gold: `linear-gradient(135deg, ${BIONIC_COLORS.gold.primary} 0%, ${BIONIC_COLORS.gold.light} 100%)`,
  blue: `linear-gradient(135deg, ${BIONIC_COLORS.blue.primary} 0%, ${BIONIC_COLORS.blue.light} 100%)`,
  green: `linear-gradient(135deg, ${BIONIC_COLORS.green.dark} 0%, ${BIONIC_COLORS.green.primary} 100%)`,
  dark: `linear-gradient(180deg, ${BIONIC_COLORS.black.base} 0%, ${BIONIC_COLORS.black.pure} 100%)`,
};

export default BIONIC_COLORS;
