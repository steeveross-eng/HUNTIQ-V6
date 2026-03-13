/**
 * bionicModules.js — Source de vérité pour les modules BIONIC
 * 
 * Définit les 15 modules d'analyse + modules legacy et stratégiques.
 * Ce fichier est la référence unique pour les couleurs, catégories
 * et interprétations des zones BIONIC.
 * 
 * CONFORME: BIONIC V5 PHASE F — Structure modulaire
 * ALIGNÉ: Correspondance 1:1 avec BIONIC_LAYERS (core/bionic/index.js)
 */

// ============================================
// MODULES BIONIC — 15 COUCHES PRINCIPALES
// IDs alignés avec BIONIC_LAYERS (core/bionic/index.js)
// ============================================

export const BIONIC_MODULES = {
  // --- ZONES COMPORTEMENTALES (4) ---
  rut: { 
    color: '#FF4D6D', label: 'Zone de rut', iconName: 'heart',
    category: 'behavioral',
    interpretation: { high: 'Activité intense', medium: 'Zone de reproduction', low: 'Passage occasionnel' }
  },
  repos: { 
    color: '#8B5CF6', label: 'Zone de repos', iconName: 'moon',
    category: 'behavioral',
    interpretation: { high: 'Remise principale', medium: 'Zone de couche', low: 'Repos temporaire' }
  },
  alimentation: { 
    color: '#22C55E', label: 'Zone d\'alimentation', iconName: 'leaf',
    category: 'behavioral',
    interpretation: { high: 'Gagnage optimal', medium: 'Zone de nourrissage', low: 'Ressource limitée' }
  },
  corridors: { 
    color: '#06B6D4', label: 'Corridor faunique', iconName: 'route',
    category: 'behavioral',
    interpretation: { high: 'Passage principal', medium: 'Route fréquente', low: 'Itinéraire secondaire' }
  },

  // --- ZONES ENVIRONNEMENTALES (7) ---
  habitats: { 
    color: '#10B981', label: 'Habitat optimal', iconName: 'trees',
    category: 'environmental',
    interpretation: { high: 'Zone de refuge idéale', medium: 'Habitat favorable', low: 'Habitat secondaire' }
  },
  ensoleillement: {
    color: '#FCD34D', label: 'Ensoleillement', iconName: 'sun',
    category: 'environmental',
    interpretation: { high: 'Exposition maximale', medium: 'Mi-ombre', low: 'Zone ombragée' }
  },
  orientation: {
    color: '#2196F3', label: 'Orientation', iconName: 'compass',
    category: 'environmental',
    interpretation: { high: 'Orientation sud idéale', medium: 'Orientation mixte', low: 'Orientation nord' }
  },
  hydro: { 
    color: '#3B82F6', label: 'Hydrographie', iconName: 'droplet',
    category: 'environmental',
    interpretation: { high: 'Point d\'eau vital', medium: 'Zone humide', low: 'Proximité eau' }
  },
  peuplements: {
    color: '#15803D', label: 'Peuplements forestiers', iconName: 'tree-pine',
    category: 'environmental',
    interpretation: { high: 'Peuplement mature', medium: 'Forêt mixte', low: 'Régénération' }
  },
  ndvi: {
    color: '#66BB6A', label: 'NDVI / Densité végétale', iconName: 'sprout',
    category: 'environmental',
    interpretation: { high: 'Végétation très dense', medium: 'Couvert moyen', low: 'Végétation clairsemée' }
  },
  pentes: {
    color: '#FF7043', label: 'Pentes', iconName: 'mountain',
    category: 'environmental',
    interpretation: { high: 'Pente abrupte', medium: 'Pente modérée', low: 'Terrain plat' }
  },

  // --- ZONES STRATÉGIQUES (3) ---
  salines: { 
    color: '#FFFF00', label: 'Saline potentielle', iconName: 'sparkles',
    category: 'strategic',
    interpretation: { high: 'Saline active', medium: 'Zone minérale', low: 'Présence possible' }
  },
  affuts: { 
    color: '#F5A623', label: 'Affût potentiel', iconName: 'target',
    category: 'strategic',
    interpretation: { high: 'Position stratégique', medium: 'Bon potentiel', low: 'Point d\'observation' }
  },
  trajets: {
    color: '#ff9800', label: 'Trajets de chasse', iconName: 'route',
    category: 'strategic',
    interpretation: { high: 'Trajet principal', medium: 'Route fréquente', low: 'Passage secondaire' }
  },

  // --- COMPLÉMENT: altitude (15e couche) ---
  altitude: {
    color: '#78909c', label: 'Altitude relative', iconName: 'bar-chart',
    category: 'environmental',
    interpretation: { high: 'Point culminant', medium: 'Altitude moyenne', low: 'Vallée / bas-fond' }
  },

  // ============================================
  // MODULES INTERNES (non-sidebar, usage par services)
  // ============================================
  soleil: { 
    color: '#FCD34D', label: 'Ensoleillement', iconName: 'sun',
    category: 'environmental',
    interpretation: { high: 'Exposition maximale', medium: 'Mi-ombre', low: 'Zone ombragée' }
  },
  pente: { 
    color: '#A78BFA', label: 'Orientation/Pentes', iconName: 'mountain',
    category: 'environmental',
    interpretation: { high: 'Pente abrupte', medium: 'Pente modérée', low: 'Terrain plat' }
  },
  foret: { 
    color: '#15803D', label: 'Couvert forestier', iconName: 'tree-pine',
    category: 'environmental',
    interpretation: { high: 'Forêt dense', medium: 'Couvert mixte', low: 'Clairière' }
  },
  thermique: { 
    color: '#EF4444', label: 'Zone thermique', iconName: 'thermometer',
    category: 'environmental',
    interpretation: { high: 'Zone de chaleur', medium: 'Température modérée', low: 'Zone fraîche' }
  },
  hotspot: { 
    color: '#FF6B6B', label: 'Point chaud', iconName: 'flame',
    category: 'strategic',
    interpretation: { high: 'Activité très élevée', medium: 'Zone active', low: 'Activité modérée' }
  },
  pression: { 
    color: '#F97316', label: 'Zone de pression', iconName: 'alert-triangle',
    category: 'strategic',
    interpretation: { high: 'Pression forte', medium: 'Pression modérée', low: 'Zone tranquille' }
  },
  acces: { 
    color: '#8B5CF6', label: 'Point d\'accès', iconName: 'footprints',
    category: 'strategic',
    interpretation: { high: 'Accès principal', medium: 'Accès secondaire', low: 'Accès difficile' }
  },
  fraicheur: { 
    color: '#00CCFF', label: 'Zone de fraîcheur', iconName: 'droplet',
    category: 'environmental',
    interpretation: { high: 'Point d\'eau vital', medium: 'Zone humide', low: 'Fraîcheur relative' }
  },
  transition: { 
    color: '#9CA3AF', label: 'Zone tampon', iconName: 'move-horizontal',
    category: 'strategic',
    interpretation: { high: 'Transition clé', medium: 'Zone intermédiaire', low: 'Bordure de territoire' }
  }
};
