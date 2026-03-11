/**
 * BIONIC DESIGN SYSTEM - Centralized Configuration
 * Configuration unifiée pour tous les types, labels et options
 * Version: 1.0.0
 * 
 * RÈGLES:
 * - TOUS les types de waypoints, lieux, zones doivent utiliser cette config
 * - Aucune définition locale autorisée
 * - Les labels sont des clés i18n
 */

import { TERRITORY_COLORS, WAYPOINT_COLORS, ZONE_COLORS } from './bionic-colors';
import { TERRITORY_ICONS, WEATHER_ICONS, ANIMAL_ICONS } from './bionic-icons';

// ============================================
// TYPES DE LIEUX (PLACE_TYPES)
// Remplace les définitions hardcodées dans MonTerritoireBionicPage.jsx
// ============================================

export const PLACE_TYPES = [
  { 
    id: 'zec', 
    labelKey: 'place_zec', 
    Icon: TERRITORY_ICONS.zec, 
    color: TERRITORY_COLORS.zec 
  },
  { 
    id: 'pourvoirie', 
    labelKey: 'place_pourvoirie', 
    Icon: TERRITORY_ICONS.pourvoirie, 
    color: TERRITORY_COLORS.pourvoirie 
  },
  { 
    id: 'prive', 
    labelKey: 'place_private', 
    Icon: TERRITORY_ICONS.private, 
    color: TERRITORY_COLORS.private 
  },
  { 
    id: 'sepaq', 
    labelKey: 'place_reserve', 
    Icon: TERRITORY_ICONS.reserve, 
    color: TERRITORY_COLORS.reserve 
  },
  { 
    id: 'affut', 
    labelKey: 'place_stand', 
    Icon: TERRITORY_ICONS.stand, 
    color: TERRITORY_COLORS.stand 
  },
  { 
    id: 'saline', 
    labelKey: 'place_salt_lick', 
    Icon: TERRITORY_ICONS.salt_lick, 
    color: TERRITORY_COLORS.salt_lick 
  },
  { 
    id: 'observation', 
    labelKey: 'place_observation', 
    Icon: TERRITORY_ICONS.observation_point, 
    color: TERRITORY_COLORS.observation 
  },
  { 
    id: 'stationnement', 
    labelKey: 'place_parking', 
    Icon: TERRITORY_ICONS.parking, 
    color: TERRITORY_COLORS.parking 
  },
  { 
    id: 'camp', 
    labelKey: 'place_camp', 
    Icon: TERRITORY_ICONS.camp, 
    color: TERRITORY_COLORS.camp 
  },
  { 
    id: 'autre', 
    labelKey: 'place_other', 
    Icon: TERRITORY_ICONS.other, 
    color: TERRITORY_COLORS.other 
  },
];

// ============================================
// TYPES DE WAYPOINTS
// Remplace les définitions hardcodées dans WaypointMap.jsx, WaypointManager.jsx
// ============================================

export const WAYPOINT_TYPES = [
  { 
    id: 'hunting', 
    labelKey: 'waypoint_hunting', 
    Icon: TERRITORY_ICONS.hunting, 
    color: WAYPOINT_COLORS.hunting 
  },
  { 
    id: 'camera', 
    labelKey: 'waypoint_camera', 
    Icon: TERRITORY_ICONS.camera, 
    color: WAYPOINT_COLORS.camera 
  },
  { 
    id: 'feeding', 
    labelKey: 'waypoint_feeding', 
    Icon: TERRITORY_ICONS.feeding, 
    color: WAYPOINT_COLORS.feeding 
  },
  { 
    id: 'observation', 
    labelKey: 'waypoint_observation', 
    Icon: TERRITORY_ICONS.observation, 
    color: WAYPOINT_COLORS.observation 
  },
  { 
    id: 'blind', 
    labelKey: 'waypoint_blind', 
    Icon: TERRITORY_ICONS.blind, 
    color: WAYPOINT_COLORS.blind 
  },
  { 
    id: 'custom', 
    labelKey: 'waypoint_custom', 
    Icon: TERRITORY_ICONS.custom, 
    color: WAYPOINT_COLORS.custom 
  },
];

// ============================================
// TYPES DE ZONES AVANCÉES
// Remplace les définitions hardcodées dans BionicAdvancedZones.jsx
// ============================================

export const ADVANCED_ZONE_TYPES = [
  { 
    id: 'rutting', 
    labelKey: 'zone_rutting', 
    color: ZONE_COLORS.rutting,
    priority: 1 
  },
  { 
    id: 'bedding', 
    labelKey: 'zone_bedding', 
    color: ZONE_COLORS.bedding,
    priority: 2 
  },
  { 
    id: 'feeding', 
    labelKey: 'zone_feeding', 
    color: ZONE_COLORS.feeding,
    priority: 3 
  },
  { 
    id: 'water', 
    labelKey: 'zone_water', 
    color: ZONE_COLORS.water,
    priority: 4 
  },
  { 
    id: 'observation', 
    labelKey: 'zone_observation', 
    color: ZONE_COLORS.observation,
    priority: 5 
  },
  { 
    id: 'blind', 
    labelKey: 'zone_blind', 
    color: ZONE_COLORS.blind,
    priority: 6 
  },
  { 
    id: 'trail', 
    labelKey: 'zone_trail', 
    color: ZONE_COLORS.trail,
    priority: 7 
  },
  { 
    id: 'scrape', 
    labelKey: 'zone_scrape', 
    color: ZONE_COLORS.scrape,
    priority: 8 
  },
  { 
    id: 'rub', 
    labelKey: 'zone_rub', 
    color: ZONE_COLORS.rub,
    priority: 9 
  },
  { 
    id: 'crossing', 
    labelKey: 'zone_crossing', 
    color: ZONE_COLORS.crossing,
    priority: 10 
  },
  { 
    id: 'funnel', 
    labelKey: 'zone_funnel', 
    color: ZONE_COLORS.funnel,
    priority: 11 
  },
  { 
    id: 'staging', 
    labelKey: 'zone_staging', 
    color: ZONE_COLORS.staging,
    priority: 12 
  },
  { 
    id: 'thermal', 
    labelKey: 'zone_thermal', 
    color: ZONE_COLORS.thermal,
    priority: 13 
  },
  { 
    id: 'sanctuary', 
    labelKey: 'zone_sanctuary', 
    color: ZONE_COLORS.sanctuary,
    priority: 14 
  },
];

// ============================================
// ESPÈCES ANIMALES
// ============================================

export const ANIMAL_SPECIES = [
  { 
    id: 'deer', 
    labelKey: 'animal_deer',
    Icon: ANIMAL_ICONS.deer,
  },
  { 
    id: 'moose', 
    labelKey: 'animal_moose',
    Icon: ANIMAL_ICONS.moose,
  },
  { 
    id: 'bear', 
    labelKey: 'animal_bear',
    Icon: ANIMAL_ICONS.bear,
  },
  { 
    id: 'wild_boar', 
    labelKey: 'animal_wild_boar',
    Icon: ANIMAL_ICONS.wild_boar,
  },
  { 
    id: 'turkey', 
    labelKey: 'animal_turkey',
    Icon: ANIMAL_ICONS.turkey,
  },
  { 
    id: 'duck', 
    labelKey: 'animal_duck',
    Icon: ANIMAL_ICONS.duck,
  },
  { 
    id: 'coyote', 
    labelKey: 'animal_coyote',
    Icon: ANIMAL_ICONS.coyote,
  },
  { 
    id: 'fox', 
    labelKey: 'animal_fox',
    Icon: ANIMAL_ICONS.fox,
  },
];

// ============================================
// CONDITIONS MÉTÉO
// ============================================

export const WEATHER_CONDITIONS = [
  { 
    id: 'clear', 
    labelKey: 'weather_clear',
    Icon: WEATHER_ICONS.clear,
  },
  { 
    id: 'cloudy', 
    labelKey: 'weather_cloudy',
    Icon: WEATHER_ICONS.cloudy,
  },
  { 
    id: 'partly_cloudy', 
    labelKey: 'weather_partly_cloudy',
    Icon: WEATHER_ICONS.partly_cloudy,
  },
  { 
    id: 'rain', 
    labelKey: 'weather_rain',
    Icon: WEATHER_ICONS.rain,
  },
  { 
    id: 'snow', 
    labelKey: 'weather_snow',
    Icon: WEATHER_ICONS.snow,
  },
  { 
    id: 'fog', 
    labelKey: 'weather_fog',
    Icon: WEATHER_ICONS.fog,
  },
  { 
    id: 'wind', 
    labelKey: 'weather_wind',
    Icon: WEATHER_ICONS.wind,
  },
];

// ============================================
// SAISONS DE CHASSE
// ============================================

export const HUNTING_SEASONS = [
  { id: 'pre_rut', labelKey: 'season_pre_rut' },
  { id: 'rut', labelKey: 'season_rut' },
  { id: 'post_rut', labelKey: 'season_post_rut' },
  { id: 'spring', labelKey: 'season_spring' },
  { id: 'summer', labelKey: 'season_summer' },
  { id: 'fall', labelKey: 'season_fall' },
  { id: 'winter', labelKey: 'season_winter' },
];

// ============================================
// CATÉGORIES DE PRODUITS
// ============================================

export const PRODUCT_CATEGORIES = [
  { id: 'urine', labelKey: 'category_urine' },
  { id: 'gel', labelKey: 'category_gel' },
  { id: 'granules', labelKey: 'category_granules' },
  { id: 'bloc', labelKey: 'category_block' },
  { id: 'liquide', labelKey: 'category_liquid' },
  { id: 'poudre', labelKey: 'category_powder' },
  { id: 'spray', labelKey: 'category_spray' },
];

// ============================================
// TYPES D'INSIGHTS AI
// ============================================

export const AI_INSIGHT_TYPES = [
  { 
    id: 'tip', 
    labelKey: 'insight_tip',
    color: ZONE_COLORS.feeding,
  },
  { 
    id: 'trend', 
    labelKey: 'insight_trend',
    color: ZONE_COLORS.water,
  },
  { 
    id: 'warning', 
    labelKey: 'insight_warning',
    color: ZONE_COLORS.rutting,
  },
  { 
    id: 'recommendation', 
    labelKey: 'insight_recommendation',
    color: ZONE_COLORS.blind,
  },
];

// ============================================
// FONCTIONS UTILITAIRES
// ============================================

/**
 * Obtenir un type de lieu par ID
 */
export const getPlaceType = (id) => {
  return PLACE_TYPES.find(p => p.id === id) || PLACE_TYPES[PLACE_TYPES.length - 1];
};

/**
 * Obtenir un type de waypoint par ID
 */
export const getWaypointType = (id) => {
  return WAYPOINT_TYPES.find(w => w.id === id) || WAYPOINT_TYPES[WAYPOINT_TYPES.length - 1];
};

/**
 * Obtenir un type de zone par ID
 */
export const getZoneType = (id) => {
  return ADVANCED_ZONE_TYPES.find(z => z.id === id) || ADVANCED_ZONE_TYPES[0];
};

/**
 * Obtenir une espèce animale par ID
 */
export const getAnimalSpecies = (id) => {
  return ANIMAL_SPECIES.find(a => a.id === id) || ANIMAL_SPECIES[0];
};

export default {
  PLACE_TYPES,
  WAYPOINT_TYPES,
  ADVANCED_ZONE_TYPES,
  ANIMAL_SPECIES,
  WEATHER_CONDITIONS,
  HUNTING_SEASONS,
  PRODUCT_CATEGORIES,
  AI_INSIGHT_TYPES,
};
