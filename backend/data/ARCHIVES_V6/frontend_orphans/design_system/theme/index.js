/**
 * BIONIC TACTICAL Theme Configuration
 * Central design tokens for BIONIC HUNT/Chasse V3
 */

export const colors = {
  // === BACKGROUNDS ===
  background: {
    primary: '#0A0A0A',
    secondary: '#121212',
    tertiary: '#1A1A1A',
    card: 'rgba(0, 0, 0, 0.6)',
    overlay: 'rgba(0, 0, 0, 0.8)',
  },
  
  // === BORDERS ===
  border: {
    default: '#262626',
    subtle: 'rgba(255, 255, 255, 0.1)',
    hover: 'rgba(255, 255, 255, 0.2)',
    active: 'rgba(245, 166, 35, 0.3)',
  },
  
  // === ACCENTS ===
  accent: {
    gold: '#F5A623',
    goldHover: '#FFB84D',
    goldMuted: 'rgba(245, 166, 35, 0.2)',
    tactical: '#10B981',
    tacticalMuted: 'rgba(16, 185, 129, 0.2)',
  },
  
  // === STATUS ===
  status: {
    success: '#22C55E',
    warning: '#F59E0B',
    danger: '#EF4444',
    info: '#3B82F6',
  },
  
  // === TEXT ===
  text: {
    primary: '#FAFAFA',
    secondary: '#A3A3A3',
    muted: '#6B7280',
    inverse: '#0A0A0A',
  },
  
  // === ZONES (CARTE) ===
  zones: {
    // Comportementales
    rut: '#FF4D6D',
    repos: '#8B5CF6',
    alimentation: '#22C55E',
    corridor: '#06B6D4',
    affut: '#F5A623',
    habitat: '#10B981',
    
    // Environnementales
    soleil: '#FBBF24',
    pente: '#A78BFA',
    hydro: '#3B82F6',
    foret: '#059669',
    thermique: '#EF4444',
    
    // Stratégiques
    hotspot: '#FF6B6B',
    pression: '#F59E0B',
    acces: '#6366F1',
  },
};

export const typography = {
  fontFamily: {
    heading: '"Barlow Condensed", sans-serif',
    body: '"Inter", sans-serif',
    data: '"JetBrains Mono", monospace',
  },
  
  fontSize: {
    xs: '0.75rem',
    sm: '0.875rem',
    base: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem',
    '3xl': '1.875rem',
    '4xl': '2.25rem',
    '5xl': '3rem',
    '6xl': '3.75rem',
  },
  
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    black: 900,
  },
  
  letterSpacing: {
    tight: '-0.025em',
    normal: '0',
    wide: '0.025em',
    wider: '0.05em',
    widest: '0.1em',
  },
};

export const spacing = {
  0: '0',
  1: '0.25rem',
  2: '0.5rem',
  3: '0.75rem',
  4: '1rem',
  5: '1.25rem',
  6: '1.5rem',
  8: '2rem',
  10: '2.5rem',
  12: '3rem',
  16: '4rem',
  20: '5rem',
};

export const borderRadius = {
  none: '0',
  sm: '0.125rem',
  default: '0.25rem',
  md: '0.375rem',
  lg: '0.5rem',
  xl: '0.75rem',
  full: '9999px',
};

export const shadows = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  default: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  glow: {
    gold: '0 0 20px rgba(245, 166, 35, 0.4)',
    tactical: '0 0 20px rgba(16, 185, 129, 0.4)',
    danger: '0 0 20px rgba(239, 68, 68, 0.4)',
  },
};

export const transitions = {
  fast: '150ms ease',
  default: '200ms ease',
  slow: '300ms ease',
  slower: '500ms ease',
};

export const zIndex = {
  base: 0,
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modalBackdrop: 1040,
  modal: 1050,
  popover: 1060,
  tooltip: 1070,
  
  // Map layers
  mapBase: 100,
  mapEnvironmental: 200,
  mapBehavioral: 300,
  mapCorridors: 400,
  mapActivity: 500,
  mapHotspots: 600,
  mapAffuts: 700,
  mapWaypoints: 800,
  mapGPS: 900,
};

// CSS Variables for Tailwind integration
export const cssVariables = `
  :root {
    /* Backgrounds */
    --bionic-bg: ${colors.background.primary};
    --bionic-bg-secondary: ${colors.background.secondary};
    --bionic-bg-card: ${colors.background.card};
    
    /* Borders */
    --bionic-border: ${colors.border.default};
    --bionic-border-subtle: ${colors.border.subtle};
    
    /* Accents */
    --bionic-gold: ${colors.accent.gold};
    --bionic-gold-hover: ${colors.accent.goldHover};
    --bionic-tactical: ${colors.accent.tactical};
    
    /* Status */
    --bionic-success: ${colors.status.success};
    --bionic-warning: ${colors.status.warning};
    --bionic-danger: ${colors.status.danger};
    --bionic-info: ${colors.status.info};
    
    /* Text */
    --bionic-text: ${colors.text.primary};
    --bionic-text-muted: ${colors.text.secondary};
    
    /* Zones */
    --zone-rut: ${colors.zones.rut};
    --zone-repos: ${colors.zones.repos};
    --zone-alimentation: ${colors.zones.alimentation};
    --zone-corridor: ${colors.zones.corridor};
    --zone-affut: ${colors.zones.affut};
    --zone-habitat: ${colors.zones.habitat};
    --zone-hotspot: ${colors.zones.hotspot};
  }
`;

export default {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  transitions,
  zIndex,
  cssVariables,
};
