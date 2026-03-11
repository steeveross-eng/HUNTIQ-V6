/**
 * TerritoryMap Constants - BIONIC V5
 * 
 * Extracted from TerritoryMap.jsx for better maintainability
 * @module territory/constants
 * @version 1.0.0
 */

import { BIONIC_COLORS, TERRITORY_COLORS } from '@/config/bionic-colors';
import { BIONIC_ICONS } from '@/config/bionic-icons';
import { 
  Eye, Camera, Target, Tent, Droplet, Leaf, CircleDot,
  Thermometer, Route, Compass, TreePine, Mountain, Users,
  Shield, Flag
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

// BIONIC Module Configuration (analysis scoring modules)
export const BIONIC_MODULE_CONFIG = {
  thermal: { name: 'ThermalScore', labelKey: 'module_thermal', color: BIONIC_COLORS.red.primary, Icon: Thermometer },
  wetness: { name: 'WetnessScore', labelKey: 'module_wetness', color: BIONIC_COLORS.blue.light, Icon: Droplet },
  food: { name: 'FoodScore', labelKey: 'module_food', color: BIONIC_COLORS.green.primary, Icon: Leaf },
  pressure: { name: 'PressureScore', labelKey: 'module_pressure', color: BIONIC_COLORS.gold.primary, Icon: Users },
  access: { name: 'AccessScore', labelKey: 'module_access', color: BIONIC_COLORS.purple.primary, Icon: Route },
  corridor: { name: 'CorridorScore', labelKey: 'module_corridor', color: BIONIC_COLORS.cyan.primary, Icon: Compass },
  canopy: { name: 'CanopyScore', labelKey: 'module_canopy', color: BIONIC_COLORS.green.light, Icon: TreePine },
  geoform: { name: 'GeoFormScore', labelKey: 'module_geoform', color: BIONIC_COLORS.purple.light, Icon: Mountain }
};

// Territory Types Configuration - Local (for territory filter/display)
export const TERRITORY_TYPES_LOCAL = {
  zec: { nameKey: 'territory_zec', color: TERRITORY_COLORS.zec, Icon: Tent },
  sepaq: { nameKey: 'territory_reserve', color: TERRITORY_COLORS.reserve, Icon: Shield },
  clic: { nameKey: 'territory_clic', color: BIONIC_COLORS.gold.primary, Icon: Target },
  pourvoirie: { nameKey: 'territory_pourvoirie', color: TERRITORY_COLORS.pourvoirie, Icon: Flag },
  prive: { nameKey: 'territory_private', color: TERRITORY_COLORS.private, Icon: BIONIC_ICONS.lock },
  refuge: { nameKey: 'territory_refuge', color: BIONIC_COLORS.cyan.primary, Icon: Shield }
};

// Mock Territory Database (ZEC, Sepaq examples)
export const TERRITORY_DATABASE = {
  zec: {
    '086': { name: 'ZEC des Martres', lat: 47.5, lng: -72.8, region: 'Mauricie', qualityScore: 78, huntingPressure: 'moyen', accessibility: 'bonne', habitat: 'excellent', successRate: { orignal: 42, chevreuil: 38, ours: 25 } },
    '027': { name: 'ZEC Tawachiche', lat: 46.8, lng: -72.5, region: 'Mauricie', qualityScore: 85, huntingPressure: 'faible', accessibility: 'moyenne', habitat: 'excellent', successRate: { orignal: 48, chevreuil: 35, ours: 30 } },
    '037': { name: 'ZEC Jeannotte', lat: 46.4, lng: -73.2, region: 'Lanaudiere', qualityScore: 72, huntingPressure: 'eleve', accessibility: 'bonne', habitat: 'bon', successRate: { orignal: 35, chevreuil: 42, ours: 18 } },
  },
  sepaq: {
    '13': { name: 'Reserve faunique Mastigouche', lat: 46.65, lng: -73.35, region: 'Mauricie', qualityScore: 92, huntingPressure: 'controle', accessibility: 'excellente', habitat: 'exceptionnel', successRate: { orignal: 55, chevreuil: 40, ours: 35 }, tirage: true },
    '08': { name: 'Reserve faunique La Verendrye', lat: 47.5, lng: -77.0, region: 'Outaouais', qualityScore: 88, huntingPressure: 'faible', accessibility: 'bonne', habitat: 'excellent', successRate: { orignal: 52, chevreuil: 32, ours: 40 }, tirage: true },
    '04': { name: 'Reserve faunique Portneuf', lat: 47.0, lng: -72.2, region: 'Capitale-Nationale', qualityScore: 82, huntingPressure: 'moyen', accessibility: 'excellente', habitat: 'tres bon', successRate: { orignal: 45, chevreuil: 38, ours: 28 }, tirage: true },
  },
  clic: {
    '27': { name: 'Zone 27 - Estrie', lat: 45.4, lng: -71.9, region: 'Estrie', qualityScore: 65, huntingPressure: 'eleve', accessibility: 'excellente', habitat: 'bon', successRate: { orignal: 0, chevreuil: 55, ours: 15 } },
    '10': { name: 'Zone 10 - Laurentides', lat: 46.2, lng: -74.5, region: 'Laurentides', qualityScore: 75, huntingPressure: 'moyen', accessibility: 'bonne', habitat: 'tres bon', successRate: { orignal: 38, chevreuil: 48, ours: 22 } },
  },
  pourvoirie: {
    'domaine-shannon': { name: 'Domaine Shannon', lat: 47.2, lng: -73.8, region: 'Mauricie', qualityScore: 95, huntingPressure: 'tres faible', accessibility: 'excellente', habitat: 'exceptionnel', successRate: { orignal: 75, chevreuil: 60, ours: 50 }, services: ['guide', 'hebergement', 'repas'] },
    'club-triton': { name: 'Club Triton', lat: 48.1, lng: -74.2, region: 'Saguenay', qualityScore: 90, huntingPressure: 'faible', accessibility: 'bonne', habitat: 'excellent', successRate: { orignal: 68, chevreuil: 45, ours: 55 }, services: ['guide', 'hebergement'] },
  }
};

// WMS Layer URLs (Quebec Government - Real endpoints)
export const WMS_LAYERS = {
  foret: {
    url: "https://servicescarto.mffp.gouv.qc.ca/pes/services/Territoire/Couvert_forestier/MapServer/WMSServer",
    layers: "0",
    name: "Couverture forestiere",
    attribution: "MFFP Quebec"
  },
  hydro: {
    url: "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/GRHQ/MapServer/WMSServer",
    layers: "0,1,2",
    name: "Hydrographie",
    attribution: "MERN Quebec"
  },
  topo: {
    url: "https://servicescarto.mern.gouv.qc.ca/pes/services/Imagerie/LIDAR_Elevation/MapServer/WMSServer",
    layers: "0",
    name: "Relief LiDAR",
    attribution: "MERN Quebec"
  },
  routes: {
    url: "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/SDA_WMS/MapServer/WMSServer",
    layers: "5,6,7",
    name: "Routes et chemins",
    attribution: "MERN Quebec"
  },
  cadastre: {
    url: "https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/Cadastre_Quebec/MapServer/WMSServer",
    layers: "0",
    name: "Cadastre",
    attribution: "MERN Quebec"
  }
};
