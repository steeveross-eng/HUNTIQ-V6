/**
 * TerritoryMap Constants - BIONIC V5
 * 
 * Extracted from TerritoryMap.jsx for better maintainability
 * @module territory/constants
 * @version 1.0.0
 */

import { BIONIC_COLORS } from '@/config/bionic-colors';
import { 
  Eye, Camera, Target, Tent, Droplet, Leaf, CircleDot 
} from 'lucide-react';

// Species configuration - BIONIC Design System compliant
export const SPECIES_CONFIG = {
  orignal: { 
    color: BIONIC_COLORS.gold.dark, 
    iconType: 'circle', 
    labelKey: 'animal_moose', 
    heatColor: 'brown', 
    Icon: CircleDot 
  },
  chevreuil: { 
    color: BIONIC_COLORS.gold.primary, 
    iconType: 'circle', 
    labelKey: 'animal_deer', 
    heatColor: 'orange', 
    Icon: CircleDot 
  },
  ours: { 
    color: BIONIC_COLORS.gray[600], 
    iconType: 'circle', 
    labelKey: 'animal_bear', 
    heatColor: 'darkslategray', 
    Icon: CircleDot 
  },
  autre: { 
    color: BIONIC_COLORS.gray[500], 
    iconType: 'default', 
    labelKey: 'common_other', 
    heatColor: 'gray', 
    Icon: CircleDot 
  }
};

// Event type configuration - BIONIC Design System compliant
export const EVENT_TYPE_CONFIG = {
  observation: { 
    color: BIONIC_COLORS.green.primary, 
    iconType: 'eye', 
    labelKey: 'waypoint_observation', 
    Icon: Eye 
  },
  camera_photo: { 
    color: BIONIC_COLORS.blue.light, 
    iconType: 'camera', 
    labelKey: 'waypoint_camera', 
    Icon: Camera 
  },
  tir: { 
    color: BIONIC_COLORS.red.primary, 
    iconType: 'target', 
    labelKey: 'event_shot', 
    Icon: Target 
  },
  cache: { 
    color: BIONIC_COLORS.purple.primary, 
    iconType: 'home', 
    labelKey: 'place_camp', 
    Icon: Tent 
  },
  saline: { 
    color: BIONIC_COLORS.cyan.primary, 
    iconType: 'droplet', 
    labelKey: 'place_salt_lick', 
    Icon: Droplet 
  },
  feeding_station: { 
    color: BIONIC_COLORS.gold.primary, 
    iconType: 'leaf', 
    labelKey: 'waypoint_feeding', 
    Icon: Leaf 
  }
};

// Scale to zoom mapping
export const SCALE_TO_ZOOM = {
  '1:1000': 18,
  '1:3000': 16,
  '1:5000': 15
};

// Default map center (Quebec)
export const DEFAULT_MAP_CENTER = [46.8139, -71.2080];
export const DEFAULT_MAP_ZOOM = 12;

// SVG icons for map markers
export const SVG_MARKER_ICONS = {
  target: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>`,
  eye: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`,
  camera: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>`,
  home: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`,
  droplet: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>`,
  leaf: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>`,
  circle: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg>`,
  pin: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>`,
  default: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><circle cx="12" cy="12" r="4"/></svg>`
};

// Heatmap gradient configuration
export const HEATMAP_GRADIENT = {
  0.2: '#ffffb2',
  0.4: '#fecc5c',
  0.6: '#fd8d3c',
  0.8: '#f03b20',
  1.0: '#bd0026'
};

// Heatmap default settings
export const HEATMAP_DEFAULTS = {
  radius: 25,
  blur: 15,
  maxZoom: 17
};
