/**
 * BIONIC_COLORS_CONFIG — Source unique de verite pour TOUTES les couleurs BIONIC
 * STEVE-MAX++: Harmonisation totale carte <-> panneau <-> core
 * 
 * REGLE: Aucune couleur ne doit etre definie en dur ailleurs.
 * Toutes les references doivent utiliser ce module.
 */

// ══════════════════════════════════════════
// 1. COULEURS NORMATIVES DES COUCHES (15 layers)
//    Identiques: backend BIONIC_COLORS, map ZONE_NORMATIVE_COLORS, panel LAYER_TYPES
// ══════════════════════════════════════════
export const ZONE_COLORS = {
  habitats:       '#10B981',
  rut:            '#FF4D6D',
  repos:          '#8B5CF6',
  alimentation:   '#22C55E',
  corridors:      '#06B6D4',
  peuplements:    '#15803D',
  ndvi:           '#66BB6A',
  hydro:          '#3B82F6',
  pentes:         '#FF7043',
  orientation:    '#2196F3',
  ensoleillement: '#FCD34D',
  salines:        '#FFFF00',
  affuts:         '#F5A623',
  trajets:        '#FF9800',
  altitude:       '#78909C',
};

// ══════════════════════════════════════════
// 2. COULEURS DES FACTEURS D'ANALYSE ECOLOGIQUE (radar chart)
//    Alignees 1:1 avec les couches normatives correspondantes
// ══════════════════════════════════════════
export const FACTOR_COLORS = {
  ndvi:       ZONE_COLORS.ndvi,         // #66BB6A — Vegetation / NDVI
  relief:     ZONE_COLORS.pentes,       // #FF7043 — Relief / Pentes
  eau:        ZONE_COLORS.hydro,        // #3B82F6 — Proximite eau / Hydrographie
  pression:   '#E91E63',                // Pression humaine (facteur analytique, pas de couche directe)
  structure:  ZONE_COLORS.peuplements,  // #15803D — Structure forestiere / Peuplements
  densite:    ZONE_COLORS.habitats,     // #10B981 — Densite couvert / Habitats
};

// ══════════════════════════════════════════
// 3. COULEURS DES CORRIDORS V9
// ══════════════════════════════════════════
export const CORRIDOR_COLORS = {
  rouge_raye: '#B71C1C',
  rouge:      '#F44336',
  orange:     '#FF9800',
  jaune:      '#FFC107',
  gris:       '#9E9E9E',
};

// ══════════════════════════════════════════
// 4. COULEURS DES MOTEURS V1 (corridor scoring)
// ══════════════════════════════════════════
export const ENGINE_V1_COLORS = {
  nutrition:             '#4CAF50',
  daily_routine:         '#FF9800',
  weather:               '#2196F3',
  disturbance:           '#F44336',
  movement:              '#9C27B0',
  phenology:             '#8BC34A',
  typology:              '#FF5722',
  learning:              '#607D8B',
  habitat_enhancement:   '#009688',
};

// ══════════════════════════════════════════
// 5. COULEURS DES CATEGORIES DE ZONES
// ══════════════════════════════════════════
export const CATEGORY_COLORS = {
  behavioral:    '#FF4D6D',   // Rose — zones comportementales
  environmental: '#10B981',   // Vert — zones ecologiques
  strategic:     '#F5A623',   // Orange — zones strategiques
};

// ══════════════════════════════════════════
// 6. COULEURS DONNEES TERRAIN (diagnostic panel)
//    Alignees avec les couches normatives
// ══════════════════════════════════════════
export const TERRAIN_DATA_COLORS = {
  superficie:    ZONE_COLORS.affuts,     // #F5A623
  altitude:      ZONE_COLORS.altitude,   // #78909C
  pente:         ZONE_COLORS.pentes,     // #FF7043
  distance_eau:  ZONE_COLORS.hydro,      // #3B82F6
  pression:      '#E91E63',              // Facteur analytique
};

// Helper: obtenir la couleur normative d'une couche (fallback gris)
export const getZoneColor = (layerId) => ZONE_COLORS[layerId] || '#9E9E9E';

// Helper: obtenir la couleur d'un facteur
export const getFactorColor = (factorKey) => FACTOR_COLORS[factorKey] || '#9E9E9E';
