/**
 * Onboarding Constants - Phase 10
 * 
 * Configuration constants for onboarding flow.
 */

// ============================================
// ONBOARDING STEPS
// ============================================

export const ONBOARDING_STEPS = {
  WELCOME: 'welcome',
  TERRITORY: 'territory',
  EXPERIENCE: 'experience',
  OBJECTIVES: 'objectives',
  COMPLETE: 'complete'
};

export const STEP_ORDER = [
  ONBOARDING_STEPS.WELCOME,
  ONBOARDING_STEPS.TERRITORY,
  ONBOARDING_STEPS.EXPERIENCE,
  ONBOARDING_STEPS.OBJECTIVES,
  ONBOARDING_STEPS.COMPLETE
];

// ============================================
// EXPERIENCE LEVELS
// ============================================

export const EXPERIENCE_LEVELS = [
  {
    id: 'beginner',
    label: 'Débutant',
    labelKey: 'onboarding_exp_beginner',
    description: 'Nouvelle expérience de chasse',
    descriptionKey: 'onboarding_exp_beginner_desc',
    icon: 'Sprout',
    years: '0-2 ans'
  },
  {
    id: 'intermediate',
    label: 'Intermédiaire',
    labelKey: 'onboarding_exp_intermediate',
    description: 'Quelques saisons d\'expérience',
    descriptionKey: 'onboarding_exp_intermediate_desc',
    icon: 'TreeDeciduous',
    years: '3-5 ans'
  },
  {
    id: 'advanced',
    label: 'Avancé',
    labelKey: 'onboarding_exp_advanced',
    description: 'Chasseur expérimenté',
    descriptionKey: 'onboarding_exp_advanced_desc',
    icon: 'TreePine',
    years: '6-10 ans'
  },
  {
    id: 'expert',
    label: 'Expert',
    labelKey: 'onboarding_exp_expert',
    description: 'Maître chasseur',
    descriptionKey: 'onboarding_exp_expert_desc',
    icon: 'Mountain',
    years: '10+ ans'
  }
];

// ============================================
// HUNTING OBJECTIVES
// ============================================

export const HUNTING_OBJECTIVES = [
  {
    id: 'trophy',
    label: 'Chasse au trophée',
    labelKey: 'onboarding_obj_trophy',
    description: 'Cibler les mâles matures',
    descriptionKey: 'onboarding_obj_trophy_desc',
    icon: 'Trophy'
  },
  {
    id: 'meat',
    label: 'Chasse alimentaire',
    labelKey: 'onboarding_obj_meat',
    description: 'Récolter de la viande de qualité',
    descriptionKey: 'onboarding_obj_meat_desc',
    icon: 'Beef'
  },
  {
    id: 'sport',
    label: 'Chasse sportive',
    labelKey: 'onboarding_obj_sport',
    description: 'L\'expérience et le défi',
    descriptionKey: 'onboarding_obj_sport_desc',
    icon: 'Target'
  },
  {
    id: 'management',
    label: 'Gestion du territoire',
    labelKey: 'onboarding_obj_management',
    description: 'Équilibrer les populations',
    descriptionKey: 'onboarding_obj_management_desc',
    icon: 'TreePine'
  },
  {
    id: 'learning',
    label: 'Apprentissage',
    labelKey: 'onboarding_obj_learning',
    description: 'Développer mes compétences',
    descriptionKey: 'onboarding_obj_learning_desc',
    icon: 'GraduationCap'
  }
];

// ============================================
// TERRITORY TYPES
// ============================================

export const TERRITORY_TYPES = [
  {
    id: 'private',
    label: 'Terrain privé',
    labelKey: 'onboarding_terr_private',
    description: 'Propriété personnelle ou louée',
    descriptionKey: 'onboarding_terr_private_desc',
    icon: 'Home'
  },
  {
    id: 'zec',
    label: 'ZEC',
    labelKey: 'onboarding_terr_zec',
    description: 'Zone d\'exploitation contrôlée',
    descriptionKey: 'onboarding_terr_zec_desc',
    icon: 'Map'
  },
  {
    id: 'pourvoirie',
    label: 'Pourvoirie',
    labelKey: 'onboarding_terr_pourvoirie',
    description: 'Territoire de pourvoirie',
    descriptionKey: 'onboarding_terr_pourvoirie_desc',
    icon: 'Building2'
  },
  {
    id: 'public',
    label: 'Terres publiques',
    labelKey: 'onboarding_terr_public',
    description: 'Forêt publique québécoise',
    descriptionKey: 'onboarding_terr_public_desc',
    icon: 'Trees'
  },
  {
    id: 'mixed',
    label: 'Mixte',
    labelKey: 'onboarding_terr_mixed',
    description: 'Combinaison de territoires',
    descriptionKey: 'onboarding_terr_mixed_desc',
    icon: 'Layers'
  }
];

// ============================================
// GAME SPECIES (Quebec)
// ============================================

export const GAME_SPECIES = [
  { id: 'whitetail', label: 'Cerf de Virginie', icon: 'deer' },
  { id: 'moose', label: 'Orignal', icon: 'moose' },
  { id: 'black_bear', label: 'Ours noir', icon: 'bear' },
  { id: 'wild_turkey', label: 'Dindon sauvage', icon: 'turkey' },
  { id: 'small_game', label: 'Petit gibier', icon: 'rabbit' },
  { id: 'waterfowl', label: 'Sauvagine', icon: 'duck' }
];

// ============================================
// STORAGE KEYS
// ============================================

export const STORAGE_KEYS = {
  ONBOARDING_COMPLETE: 'huntiq_onboarding_complete',
  USER_PROFILE: 'huntiq_user_profile',
  ONBOARDING_STEP: 'huntiq_onboarding_step'
};
