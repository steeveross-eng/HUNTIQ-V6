/**
 * bionicSpecies.js — Configuration des espèces BIONIC V5
 * 
 * Définit les profils d'espèces pour l'alignement des couches.
 * Chaque espèce a des préférences d'habitat et des poids par couche.
 * 
 * CONFORME: BIONIC V5 — Structure modulaire
 */

export const SPECIES = {
  chevreuil: {
    id: 'chevreuil',
    name: 'Chevreuil',
    scientificName: 'Odocoileus virginianus',
    icon: 'deer',
    layers: {
      habitats:        { weight: 0.90, active: true },
      rut:             { weight: 0.85, active: true },
      repos:           { weight: 0.80, active: true },
      alimentation:    { weight: 0.90, active: true },
      corridors:       { weight: 0.75, active: true },
      salines:         { weight: 0.70, active: true },
      affuts:          { weight: 0.80, active: true },
      trajets:         { weight: 0.65, active: true },
      ensoleillement:  { weight: 0.50, active: true },
      orientation:     { weight: 0.45, active: true },
      hydro:           { weight: 0.60, active: true },
      peuplements:     { weight: 0.85, active: true },
      ndvi:            { weight: 0.70, active: true },
      pentes:          { weight: 0.55, active: true },
      altitude:        { weight: 0.40, active: true },
    },
    habitPreferences: {
      forestDensity: 0.7,
      waterProximity: 0.5,
      edgePreference: 0.9,
      elevationRange: [100, 600],
      slopeMax: 35,
    }
  },

  orignal: {
    id: 'orignal',
    name: 'Orignal',
    scientificName: 'Alces americanus',
    icon: 'moose',
    layers: {
      habitats:        { weight: 0.95, active: true },
      rut:             { weight: 0.90, active: true },
      repos:           { weight: 0.85, active: true },
      alimentation:    { weight: 0.95, active: true },
      corridors:       { weight: 0.80, active: true },
      salines:         { weight: 0.90, active: true },
      affuts:          { weight: 0.75, active: true },
      trajets:         { weight: 0.70, active: true },
      ensoleillement:  { weight: 0.35, active: true },
      orientation:     { weight: 0.40, active: true },
      hydro:           { weight: 0.90, active: true },
      peuplements:     { weight: 0.95, active: true },
      ndvi:            { weight: 0.80, active: true },
      pentes:          { weight: 0.50, active: true },
      altitude:        { weight: 0.55, active: true },
    },
    habitPreferences: {
      forestDensity: 0.9,
      waterProximity: 0.9,
      edgePreference: 0.4,
      elevationRange: [50, 800],
      slopeMax: 40,
    }
  },

  ours_noir: {
    id: 'ours_noir',
    name: 'Ours noir',
    scientificName: 'Ursus americanus',
    icon: 'bear',
    layers: {
      habitats:        { weight: 0.90, active: true },
      rut:             { weight: 0.30, active: false },
      repos:           { weight: 0.85, active: true },
      alimentation:    { weight: 0.95, active: true },
      corridors:       { weight: 0.85, active: true },
      salines:         { weight: 0.40, active: false },
      affuts:          { weight: 0.70, active: true },
      trajets:         { weight: 0.80, active: true },
      ensoleillement:  { weight: 0.55, active: true },
      orientation:     { weight: 0.50, active: true },
      hydro:           { weight: 0.75, active: true },
      peuplements:     { weight: 0.90, active: true },
      ndvi:            { weight: 0.85, active: true },
      pentes:          { weight: 0.60, active: true },
      altitude:        { weight: 0.65, active: true },
    },
    habitPreferences: {
      forestDensity: 0.85,
      waterProximity: 0.6,
      edgePreference: 0.5,
      elevationRange: [50, 1000],
      slopeMax: 50,
    }
  },

  dindon_sauvage: {
    id: 'dindon_sauvage',
    name: 'Dindon sauvage',
    scientificName: 'Meleagris gallopavo',
    icon: 'turkey',
    layers: {
      habitats:        { weight: 0.85, active: true },
      rut:             { weight: 0.40, active: false },
      repos:           { weight: 0.80, active: true },
      alimentation:    { weight: 0.90, active: true },
      corridors:       { weight: 0.50, active: true },
      salines:         { weight: 0.30, active: false },
      affuts:          { weight: 0.85, active: true },
      trajets:         { weight: 0.55, active: true },
      ensoleillement:  { weight: 0.75, active: true },
      orientation:     { weight: 0.60, active: true },
      hydro:           { weight: 0.45, active: true },
      peuplements:     { weight: 0.80, active: true },
      ndvi:            { weight: 0.70, active: true },
      pentes:          { weight: 0.70, active: true },
      altitude:        { weight: 0.50, active: true },
    },
    habitPreferences: {
      forestDensity: 0.5,
      waterProximity: 0.3,
      edgePreference: 0.8,
      elevationRange: [50, 500],
      slopeMax: 30,
    }
  }
};

export const SPECIES_LIST = Object.values(SPECIES);
export const DEFAULT_SPECIES = 'chevreuil';

/**
 * Retourne les couches actives pour une espèce donnée
 */
export const getActiveLayersForSpecies = (speciesId) => {
  const species = SPECIES[speciesId];
  if (!species) return {};
  
  const activeLayers = {};
  Object.entries(species.layers).forEach(([layerId, config]) => {
    if (config.active) {
      activeLayers[layerId] = config.weight;
    }
  });
  return activeLayers;
};

/**
 * Retourne le poids d'une couche pour une espèce donnée
 */
export const getLayerWeight = (speciesId, layerId) => {
  const species = SPECIES[speciesId];
  if (!species) return 0.5;
  return species.layers[layerId]?.weight ?? 0;
};
