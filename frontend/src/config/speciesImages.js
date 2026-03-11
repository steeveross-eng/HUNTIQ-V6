/**
 * BIONIC Species Image System
 * Design System BIONIC™ - Species Images & Icons
 * Version: 1.0.0
 * 
 * Centralise toutes les images et icônes d'espèces pour garantir
 * la conformité au Design System BIONIC™.
 * 
 * IMPORTANT: Aucun emoji n'est autorisé. Toutes les espèces utilisent
 * des images réelles professionnelles.
 */

// URLs des images professionnelles d'espèces (Unsplash/BIONIC CDN)
export const SPECIES_IMAGES = {
  // Gros gibier
  deer: {
    id: 'deer',
    name: 'Cerf de Virginie',
    name_en: 'White-tailed Deer',
    category: 'big_game',
    images: {
      primary: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/b9d0w2sg_image.png',
      thumbnail: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/b9d0w2sg_image.png',
      full: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/b9d0w2sg_image.png'
    },
    color: '#D2691E',
    colorVar: 'var(--bionic-orange-primary)'
  },
  moose: {
    id: 'moose',
    name: 'Orignal',
    name_en: 'Moose',
    category: 'big_game',
    images: {
      primary: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/1ncu18um_image.png',
      thumbnail: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/1ncu18um_image.png',
      full: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/1ncu18um_image.png'
    },
    color: '#4A3728',
    colorVar: 'var(--bionic-brown-primary)'
  },
  bear: {
    id: 'bear',
    name: 'Ours noir',
    name_en: 'Black Bear',
    category: 'big_game',
    images: {
      primary: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      thumbnail: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      full: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png'
    },
    color: '#2F4F4F',
    colorVar: 'var(--bionic-gray-dark)'
  },
  boar: {
    id: 'boar',
    name: 'Sanglier',
    name_en: 'Wild Boar',
    category: 'big_game',
    images: {
      primary: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      thumbnail: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      full: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png'
    },
    color: '#5C4033',
    colorVar: 'var(--bionic-brown-dark)'
  },
  wild_boar: {
    id: 'wild_boar',
    name: 'Sanglier',
    name_en: 'Wild Boar',
    category: 'big_game',
    images: {
      primary: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      thumbnail: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      full: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png'
    },
    color: '#5C4033',
    colorVar: 'var(--bionic-brown-dark)'
  },
  
  // Petit gibier
  turkey: {
    id: 'turkey',
    name: 'Dindon sauvage',
    name_en: 'Wild Turkey',
    category: 'small_game',
    images: {
      primary: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      thumbnail: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      full: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png'
    },
    color: '#8B4513',
    colorVar: 'var(--bionic-brown-primary)'
  },
  hare: {
    id: 'hare',
    name: 'Lièvre',
    name_en: 'Snowshoe Hare',
    category: 'small_game',
    images: {
      primary: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      thumbnail: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      full: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png'
    },
    color: '#E8E8E8',
    colorVar: 'var(--bionic-gray-light)'
  },
  rabbit: {
    id: 'rabbit',
    name: 'Lièvre',
    name_en: 'Snowshoe Hare',
    category: 'small_game',
    images: {
      primary: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      thumbnail: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      full: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png'
    },
    color: '#E8E8E8',
    colorVar: 'var(--bionic-gray-light)'
  },
  coyote: {
    id: 'coyote',
    name: 'Coyote',
    name_en: 'Coyote',
    category: 'small_game',
    images: {
      primary: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      thumbnail: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      full: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png'
    },
    color: '#A0522D',
    colorVar: 'var(--bionic-brown-medium)'
  },
  
  // Sauvagine
  duck: {
    id: 'duck',
    name: 'Canard',
    name_en: 'Mallard Duck',
    category: 'waterfowl',
    images: {
      primary: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      thumbnail: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      full: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png'
    },
    color: '#228B22',
    colorVar: 'var(--bionic-green-primary)'
  },
  goose: {
    id: 'goose',
    name: 'Oie du Canada',
    name_en: 'Canada Goose',
    category: 'waterfowl',
    images: {
      primary: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      thumbnail: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      full: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png'
    },
    color: '#696969',
    colorVar: 'var(--bionic-gray-medium)'
  },
  
  // Alias pour compatibilité
  chevreuil: {
    id: 'chevreuil',
    name: 'Chevreuil',
    name_en: 'White-tailed Deer',
    category: 'big_game',
    images: {
      primary: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/b9d0w2sg_image.png',
      thumbnail: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/b9d0w2sg_image.png',
      full: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/b9d0w2sg_image.png'
    },
    color: '#D2691E',
    colorVar: 'var(--bionic-orange-primary)'
  },
  ours: {
    id: 'ours',
    name: 'Ours noir',
    name_en: 'Black Bear',
    category: 'big_game',
    images: {
      primary: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      thumbnail: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png',
      full: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/187hi1a1_image.png'
    },
    color: '#2F4F4F',
    colorVar: 'var(--bionic-gray-dark)'
  },
  caribou: {
    id: 'caribou',
    name: 'Caribou',
    name_en: 'Caribou',
    category: 'big_game',
    images: {
      primary: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/hrz22aqh_image.png',
      thumbnail: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/hrz22aqh_image.png',
      full: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/hrz22aqh_image.png'
    },
    color: '#8B7355',
    colorVar: 'var(--bionic-brown-light)'
  },
  
  // Catégorie générique
  other: {
    id: 'other',
    name: 'Autre',
    name_en: 'Other',
    category: 'other',
    images: {
      primary: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/b9d0w2sg_image.png',
      thumbnail: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/b9d0w2sg_image.png',
      full: 'https://customer-assets.emergentagent.com/job_huntiq-fusion-2/artifacts/b9d0w2sg_image.png'
    },
    color: '#808080',
    colorVar: 'var(--bionic-gray-medium)'
  }
};

// Catégories de gibier
export const SPECIES_CATEGORIES = {
  big_game: {
    id: 'big_game',
    name: 'Gros gibier',
    name_en: 'Big Game',
    species: ['deer', 'moose', 'bear', 'boar']
  },
  small_game: {
    id: 'small_game',
    name: 'Petit gibier',
    name_en: 'Small Game',
    species: ['turkey', 'hare', 'coyote']
  },
  waterfowl: {
    id: 'waterfowl',
    name: 'Sauvagine',
    name_en: 'Waterfowl',
    species: ['duck', 'goose']
  }
};

/**
 * Obtenir les informations complètes d'une espèce
 * @param {string} speciesId - Identifiant de l'espèce
 * @returns {object|null} Informations de l'espèce ou null
 */
export const getSpeciesInfo = (speciesId) => {
  if (!speciesId) return null;
  const normalizedId = speciesId.toLowerCase().replace(/\s+/g, '_');
  return SPECIES_IMAGES[normalizedId] || SPECIES_IMAGES.other;
};

/**
 * Obtenir l'URL de l'image principale d'une espèce
 * @param {string} speciesId - Identifiant de l'espèce
 * @param {string} size - 'thumbnail' | 'primary' | 'full'
 * @returns {string} URL de l'image
 */
export const getSpeciesImage = (speciesId, size = 'primary') => {
  const species = getSpeciesInfo(speciesId);
  return species?.images?.[size] || SPECIES_IMAGES.other.images[size];
};

/**
 * Obtenir le nom localisé d'une espèce
 * @param {string} speciesId - Identifiant de l'espèce
 * @param {string} lang - 'fr' | 'en'
 * @returns {string} Nom de l'espèce
 */
export const getSpeciesName = (speciesId, lang = 'fr') => {
  const species = getSpeciesInfo(speciesId);
  if (!species) return speciesId;
  return lang === 'en' ? species.name_en : species.name;
};

/**
 * Obtenir la couleur associée à une espèce
 * @param {string} speciesId - Identifiant de l'espèce
 * @returns {string} Couleur hex
 */
export const getSpeciesColor = (speciesId) => {
  const species = getSpeciesInfo(speciesId);
  return species?.color || '#808080';
};

/**
 * Obtenir toutes les espèces d'une catégorie
 * @param {string} categoryId - Identifiant de la catégorie
 * @returns {array} Liste des espèces
 */
export const getSpeciesByCategory = (categoryId) => {
  const category = SPECIES_CATEGORIES[categoryId];
  if (!category) return [];
  return category.species.map(id => SPECIES_IMAGES[id]).filter(Boolean);
};

/**
 * Liste complète des espèces pour les sélecteurs
 */
export const SPECIES_LIST = Object.values(SPECIES_IMAGES)
  .filter(s => !['chevreuil', 'ours', 'caribou', 'rabbit', 'wild_boar'].includes(s.id))
  .map(species => ({
    value: species.id,
    label: species.name,
    label_en: species.name_en,
    image: species.images.thumbnail,
    category: species.category,
    color: species.color
  }));

export default {
  SPECIES_IMAGES,
  SPECIES_CATEGORIES,
  SPECIES_LIST,
  getSpeciesInfo,
  getSpeciesImage,
  getSpeciesName,
  getSpeciesColor,
  getSpeciesByCategory
};
