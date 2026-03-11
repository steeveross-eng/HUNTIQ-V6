/**
 * biologicalSeasons.js — Saisons biologiques BIONIC™
 * V8.1 — Modèle comportemental saisonnier
 *
 * 5 saisons biologiques basées sur le cycle de vie du gibier québécois.
 * Chaque saison modifie les poids des couches d'analyse et l'apparence visuelle.
 */

export const BIOLOGICAL_SEASONS = [
  {
    id: 'pre_rut',
    label: 'Pré-rut',
    shortLabel: 'Pré-rut',
    description: 'Marquage territorial, frottage, augmentation des déplacements',
    months: [9],           // Septembre
    dateRange: '1 sept — 30 sept',
    color: '#F59E0B',      // Ambre
    bgColor: 'bg-amber-500/15',
    borderColor: 'border-amber-500/30',
    textColor: 'text-amber-400',
    icon: 'activity',
    // Poids relatifs des couches (multiplicateur 0.0 → 2.0)
    layerWeights: {
      habitats: 1.2,
      rut: 1.5,         // Début d'activité rut
      repos: 0.8,       // Moins de repos
      alimentation: 1.3, // Accumulation énergie
      corridors: 1.6,   // Déplacements accrus
      salines: 1.4,     // Salines très fréquentées
      affuts: 1.2,
      hydro: 1.0,
      peuplements: 1.0,
    },
    // Ajustement visuel
    visual: { saturation: 1.1, brightness: 1.0, opacity: 0.85 },
  },
  {
    id: 'rut',
    label: 'Rut',
    shortLabel: 'Rut',
    description: 'Période de reproduction, activité maximale, déplacements erratiques',
    months: [10],          // Octobre
    dateRange: '1 oct — 31 oct',
    color: '#EF4444',      // Rouge
    bgColor: 'bg-red-500/15',
    borderColor: 'border-red-500/30',
    textColor: 'text-red-400',
    icon: 'flame',
    layerWeights: {
      habitats: 1.0,
      rut: 2.0,          // Maximum absolu
      repos: 0.5,        // Repos minimal
      alimentation: 0.7, // Alimentation réduite
      corridors: 1.8,    // Corridors très actifs
      salines: 0.8,
      affuts: 1.5,       // Affûts stratégiques
      hydro: 0.9,
      peuplements: 1.0,
    },
    visual: { saturation: 1.3, brightness: 1.05, opacity: 0.9 },
  },
  {
    id: 'post_rut',
    label: 'Post-rut',
    shortLabel: 'Post-rut',
    description: 'Récupération, alimentation intensive, préparation hivernale',
    months: [11],          // Novembre
    dateRange: '1 nov — 30 nov',
    color: '#8B5CF6',      // Violet
    bgColor: 'bg-violet-500/15',
    borderColor: 'border-violet-500/30',
    textColor: 'text-violet-400',
    icon: 'moon',
    layerWeights: {
      habitats: 1.3,
      rut: 0.3,          // Quasi terminé
      repos: 1.5,        // Repos très important
      alimentation: 1.8, // Alimentation maximale
      corridors: 1.0,
      salines: 0.6,
      affuts: 1.0,
      hydro: 1.0,
      peuplements: 1.2,
    },
    visual: { saturation: 0.9, brightness: 0.95, opacity: 0.8 },
  },
  {
    id: 'winter',
    label: 'Hiver',
    shortLabel: 'Hiver',
    description: 'Survie, ravages, alimentation de subsistance, mobilité réduite',
    months: [12, 1, 2],   // Décembre-Février
    dateRange: '1 déc — 28 fév',
    color: '#06B6D4',      // Cyan
    bgColor: 'bg-cyan-500/15',
    borderColor: 'border-cyan-500/30',
    textColor: 'text-cyan-400',
    icon: 'snowflake',
    layerWeights: {
      habitats: 1.5,      // Ravages très importants
      rut: 0.0,           // Aucun rut
      repos: 1.8,         // Repos maximal (conservation énergie)
      alimentation: 1.6,  // Alimentation critique
      corridors: 0.5,     // Mobilité très réduite
      salines: 0.3,
      affuts: 0.5,
      hydro: 0.8,
      peuplements: 1.4,   // Conifères = couvert thermique
    },
    visual: { saturation: 0.7, brightness: 0.9, opacity: 0.75 },
  },
  {
    id: 'spring',
    label: 'Printemps',
    shortLabel: 'Print.',
    description: 'Reprise d\'activité, alimentation verte, dispersion des jeunes',
    months: [3, 4, 5, 6, 7, 8], // Mars-Août
    dateRange: '1 mars — 31 août',
    color: '#22C55E',      // Vert
    bgColor: 'bg-green-500/15',
    borderColor: 'border-green-500/30',
    textColor: 'text-green-400',
    icon: 'sprout',
    layerWeights: {
      habitats: 1.0,
      rut: 0.1,
      repos: 1.0,
      alimentation: 1.5,  // Végétation nouvelle
      corridors: 1.2,     // Dispersion
      salines: 1.3,       // Salines reprennent
      affuts: 0.8,
      hydro: 1.2,         // Points d'eau importants
      peuplements: 1.0,
    },
    visual: { saturation: 1.0, brightness: 1.0, opacity: 0.85 },
  },
];

/**
 * Détecte la saison biologique actuelle basée sur le mois courant
 */
export function getCurrentBiologicalSeason() {
  const month = new Date().getMonth() + 1; // 1-12
  return BIOLOGICAL_SEASONS.find(s => s.months.includes(month)) || BIOLOGICAL_SEASONS[4]; // fallback spring
}

/**
 * Retourne une saison par son ID
 */
export function getBiologicalSeason(id) {
  return BIOLOGICAL_SEASONS.find(s => s.id === id) || getCurrentBiologicalSeason();
}

/**
 * Mappe une saison biologique vers la saison calendaire backend
 */
export function mapToBackendSeason(biologicalSeasonId) {
  const map = {
    pre_rut: 'autumn',
    rut: 'autumn',
    post_rut: 'autumn',
    winter: 'winter',
    spring: 'spring',
  };
  return map[biologicalSeasonId] || 'autumn';
}
