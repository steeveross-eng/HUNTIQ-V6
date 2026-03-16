/**
 * speciesConfig.js — Configuration des espèces pour BIONIC V5
 *
 * Définit les espèces cibles, leurs couches BIONIC pertinentes,
 * et les préférences d'habitat pour le filtrage et l'alignement.
 *
 * CONFORME: BIONIC V5 — Alignement par espèce
 */

export const SPECIES = {
  orignal: {
    id: 'orignal',
    name: 'Orignal',
    scientificName: 'Alces americanus',
    iconName: 'TreePine',
    color: '#10B981',
    layers: [
      'habitats', 'alimentation', 'corridors', 'repos',
      'hydro', 'salines', 'rut', 'peuplements', 'pentes',
    ],
    habitatPrefs: {
      prefersWaterProximity: true,
      prefersConifer: true,
      prefersDenseForest: false,
      prefersEdges: false,
      prefersElevation: false,
    },
    scoreWeights: {
      habitats: 1.2, alimentation: 1.1, corridors: 1.0,
      repos: 0.9, hydro: 1.3, salines: 1.4, rut: 1.0,
      peuplements: 1.0, pentes: 0.7,
    },
  },
  chevreuil: {
    id: 'chevreuil',
    name: 'Chevreuil',
    scientificName: 'Odocoileus virginianus',
    iconName: 'Leaf',
    color: '#F5A623',
    layers: [
      'habitats', 'alimentation', 'corridors', 'rut',
      'affuts', 'repos', 'peuplements', 'ensoleillement',
    ],
    habitatPrefs: {
      prefersWaterProximity: false,
      prefersConifer: false,
      prefersDenseForest: false,
      prefersEdges: true,
      prefersElevation: false,
    },
    scoreWeights: {
      habitats: 1.1, alimentation: 1.2, corridors: 1.0,
      rut: 1.3, affuts: 1.1, repos: 0.9, peuplements: 0.8,
      ensoleillement: 0.7,
    },
  },
  ours_noir: {
    id: 'ours_noir',
    name: 'Ours noir',
    scientificName: 'Ursus americanus',
    iconName: 'Mountain',
    color: '#6B7280',
    layers: [
      'habitats', 'alimentation', 'corridors', 'repos',
      'hydro', 'peuplements', 'ndvi', 'pentes',
    ],
    habitatPrefs: {
      prefersWaterProximity: true,
      prefersConifer: false,
      prefersDenseForest: true,
      prefersEdges: false,
      prefersElevation: true,
    },
    scoreWeights: {
      habitats: 1.0, alimentation: 1.4, corridors: 0.8,
      repos: 1.1, hydro: 1.0, peuplements: 1.2,
      ndvi: 1.3, pentes: 0.6,
    },
  },
  dindon_sauvage: {
    id: 'dindon_sauvage',
    name: 'Dindon sauvage',
    scientificName: 'Meleagris gallopavo',
    iconName: 'Leaf',
    color: '#D97706',
    layers: [
      'habitats', 'alimentation', 'repos', 'affuts',
      'peuplements', 'ensoleillement', 'ndvi',
    ],
    habitatPrefs: {
      prefersWaterProximity: false,
      prefersConifer: false,
      prefersDenseForest: false,
      prefersEdges: true,
      prefersElevation: false,
    },
    scoreWeights: {
      habitats: 1.0, alimentation: 1.3, repos: 1.0,
      affuts: 1.2, peuplements: 1.1, ensoleillement: 0.9,
      ndvi: 1.0,
    },
  },
  wapiti: {
    id: 'wapiti',
    name: 'Wapiti',
    scientificName: 'Cervus canadensis',
    iconName: 'Mountain',
    color: '#B8860B',
    layers: [
      'habitats', 'alimentation', 'corridors', 'repos',
      'hydro', 'peuplements', 'pentes', 'ndvi',
    ],
    habitatPrefs: {
      prefersWaterProximity: true,
      prefersConifer: false,
      prefersDenseForest: false,
      prefersEdges: true,
      prefersElevation: false,
    },
    scoreWeights: {
      habitats: 1.1, alimentation: 1.3, corridors: 1.0,
      repos: 1.0, hydro: 0.9, peuplements: 1.1,
      pentes: 0.8, ndvi: 1.0,
    },
  },
  tous: {
    id: 'tous',
    name: 'Toutes les espèces',
    scientificName: '',
    iconName: 'Layers',
    color: '#8B5CF6',
    layers: null,
    habitatPrefs: null,
    scoreWeights: null,
  },
};

/**
 * Retourne la liste des couches BIONIC pertinentes pour une espèce.
 * Si 'tous', retourne null (pas de filtrage).
 */
export const getSpeciesLayers = (speciesId) => {
  const species = SPECIES[speciesId];
  return species?.layers || null;
};

/**
 * Retourne le poids d'un module pour une espèce donnée.
 */
export const getSpeciesWeight = (speciesId, moduleId) => {
  const species = SPECIES[speciesId];
  if (!species?.scoreWeights) return 1.0;
  return species.scoreWeights[moduleId] ?? 0.5;
};

/**
 * Liste des espèces pour le dropdown.
 */
export const SPECIES_LIST = Object.values(SPECIES);
