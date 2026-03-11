/**
 * Tutorial Data - Phase 11
 * 
 * Tutorial definitions for all contexts.
 */

import { TUTORIAL_CONTEXTS, TRIGGER_CONDITIONS, TOOLTIP_POSITIONS } from '../constants';

// ============================================
// TUTORIAL IDS
// ============================================

export const TUTORIAL_IDS = {
  // Dashboard
  DASHBOARD_INTRO: 'dashboard_intro',
  DASHBOARD_SCORE: 'dashboard_score',
  DASHBOARD_WEATHER: 'dashboard_weather',
  
  // Map
  MAP_INTRO: 'map_intro',
  MAP_LAYERS: 'map_layers',
  MAP_WAYPOINTS: 'map_waypoints',
  
  // Territory
  TERRITORY_INTRO: 'territory_intro',
  TERRITORY_ZONES: 'territory_zones',
  TERRITORY_ANALYSIS: 'territory_analysis',
  
  // Analytics
  ANALYTICS_INTRO: 'analytics_intro',
  
  // Plan Maître
  PLAN_MAITRE_INTRO: 'plan_maitre_intro',
  
  // Global
  NAVIGATION_INTRO: 'navigation_intro',
  FIRST_STEPS: 'first_steps'
};

// ============================================
// TUTORIALS DEFINITIONS
// ============================================

export const TUTORIALS = {
  // ==========================================
  // DASHBOARD TUTORIALS
  // ==========================================
  [TUTORIAL_IDS.DASHBOARD_INTRO]: {
    id: TUTORIAL_IDS.DASHBOARD_INTRO,
    title: 'Bienvenue sur votre Dashboard',
    context: TUTORIAL_CONTEXTS.DASHBOARD,
    trigger: TRIGGER_CONDITIONS.ON_FIRST_VISIT,
    priority: 1,
    steps: [
      {
        id: 'welcome',
        title: 'Votre tableau de bord BIONIC',
        content: 'Ce dashboard centralise toutes les informations importantes pour optimiser vos sessions de chasse.',
        target: '[data-testid="dashboard-container"]',
        position: TOOLTIP_POSITIONS.CENTER,
        spotlight: false
      },
      {
        id: 'score',
        title: 'Score BIONIC',
        content: 'Ce score évalue les conditions actuelles de chasse. Plus il est élevé, meilleures sont les conditions.',
        target: '[data-testid="bionic-score"]',
        position: TOOLTIP_POSITIONS.BOTTOM,
        spotlight: true
      },
      {
        id: 'weather',
        title: 'Météo en temps réel',
        content: 'Consultez les conditions météo actuelles et les prévisions pour planifier vos sorties.',
        target: '[data-testid="weather-widget"]',
        position: TOOLTIP_POSITIONS.LEFT,
        spotlight: true
      },
      {
        id: 'actions',
        title: 'Actions rapides',
        content: 'Accédez rapidement aux fonctionnalités principales depuis cette section.',
        target: '[data-testid="quick-actions"]',
        position: TOOLTIP_POSITIONS.TOP,
        spotlight: true
      }
    ]
  },

  // ==========================================
  // MAP TUTORIALS
  // ==========================================
  [TUTORIAL_IDS.MAP_INTRO]: {
    id: TUTORIAL_IDS.MAP_INTRO,
    title: 'Découvrez la carte interactive',
    context: TUTORIAL_CONTEXTS.MAP,
    trigger: TRIGGER_CONDITIONS.ON_FIRST_VISIT,
    priority: 1,
    steps: [
      {
        id: 'welcome',
        title: 'Carte interactive BIONIC',
        content: 'Cette carte vous permet de visualiser et analyser votre territoire de chasse.',
        target: '[data-testid="map-container"]',
        position: TOOLTIP_POSITIONS.CENTER,
        spotlight: false
      },
      {
        id: 'layers',
        title: 'Couches de données',
        content: 'Activez différentes couches pour afficher les zones forestières, les points d\'eau, et plus encore.',
        target: '[data-testid="layers-panel"]',
        position: TOOLTIP_POSITIONS.LEFT,
        spotlight: true
      },
      {
        id: 'controls',
        title: 'Contrôles de la carte',
        content: 'Utilisez ces contrôles pour zoomer, changer de vue et naviguer sur la carte.',
        target: '[data-testid="map-controls"]',
        position: TOOLTIP_POSITIONS.RIGHT,
        spotlight: true
      }
    ]
  },

  [TUTORIAL_IDS.MAP_WAYPOINTS]: {
    id: TUTORIAL_IDS.MAP_WAYPOINTS,
    title: 'Gérer vos waypoints',
    context: TUTORIAL_CONTEXTS.MAP,
    trigger: TRIGGER_CONDITIONS.MANUAL,
    priority: 2,
    steps: [
      {
        id: 'add',
        title: 'Ajouter un waypoint',
        content: 'Cliquez sur la carte pour ajouter un nouveau point d\'intérêt.',
        target: '[data-testid="add-waypoint-btn"]',
        position: TOOLTIP_POSITIONS.BOTTOM,
        spotlight: true
      },
      {
        id: 'edit',
        title: 'Modifier un waypoint',
        content: 'Cliquez sur un waypoint existant pour le modifier ou le supprimer.',
        target: '[data-testid="waypoint-marker"]',
        position: TOOLTIP_POSITIONS.TOP,
        spotlight: true
      }
    ]
  },

  // ==========================================
  // TERRITORY TUTORIALS
  // ==========================================
  [TUTORIAL_IDS.TERRITORY_INTRO]: {
    id: TUTORIAL_IDS.TERRITORY_INTRO,
    title: 'Analysez votre territoire',
    context: TUTORIAL_CONTEXTS.TERRITORY,
    trigger: TRIGGER_CONDITIONS.ON_FIRST_VISIT,
    priority: 1,
    steps: [
      {
        id: 'welcome',
        title: 'Mon Territoire BIONIC',
        content: 'Cette vue combine carte, météo et analyse pour vous aider à optimiser vos sessions.',
        target: '[data-testid="territory-container"]',
        position: TOOLTIP_POSITIONS.CENTER,
        spotlight: false
      },
      {
        id: 'score-panel',
        title: 'Panneau de score',
        content: 'Ce panneau affiche le score BIONIC calculé selon les conditions actuelles.',
        target: '[data-testid="score-panel"]',
        position: TOOLTIP_POSITIONS.LEFT,
        spotlight: true
      },
      {
        id: 'layers-panel',
        title: 'Couches disponibles',
        content: 'Activez les couches WMS pour visualiser les données écoforestières du MFFP.',
        target: '[data-testid="layers-toggle"]',
        position: TOOLTIP_POSITIONS.RIGHT,
        spotlight: true
      }
    ]
  },

  // ==========================================
  // ANALYTICS TUTORIALS
  // ==========================================
  [TUTORIAL_IDS.ANALYTICS_INTRO]: {
    id: TUTORIAL_IDS.ANALYTICS_INTRO,
    title: 'Vos statistiques de chasse',
    context: TUTORIAL_CONTEXTS.ANALYTICS,
    trigger: TRIGGER_CONDITIONS.ON_FIRST_VISIT,
    priority: 1,
    steps: [
      {
        id: 'welcome',
        title: 'Analytics BIONIC',
        content: 'Suivez vos statistiques et analysez vos performances de chasse.',
        target: '[data-testid="analytics-dashboard"]',
        position: TOOLTIP_POSITIONS.CENTER,
        spotlight: false
      },
      {
        id: 'charts',
        title: 'Graphiques',
        content: 'Visualisez vos données sous forme de graphiques interactifs.',
        target: '[data-testid="analytics-charts"]',
        position: TOOLTIP_POSITIONS.BOTTOM,
        spotlight: true
      }
    ]
  },

  // ==========================================
  // PLAN MAÎTRE TUTORIALS
  // ==========================================
  [TUTORIAL_IDS.PLAN_MAITRE_INTRO]: {
    id: TUTORIAL_IDS.PLAN_MAITRE_INTRO,
    title: 'Votre Plan Maître',
    context: TUTORIAL_CONTEXTS.PLAN_MAITRE,
    trigger: TRIGGER_CONDITIONS.ON_FIRST_VISIT,
    priority: 1,
    steps: [
      {
        id: 'welcome',
        title: 'Plan Maître BIONIC',
        content: 'Le Plan Maître combine toutes les données pour vous proposer une stratégie optimale.',
        target: '[data-testid="plan-maitre-container"]',
        position: TOOLTIP_POSITIONS.CENTER,
        spotlight: false
      },
      {
        id: 'recommendations',
        title: 'Recommandations',
        content: 'Consultez les recommandations personnalisées basées sur votre profil et les conditions.',
        target: '[data-testid="recommendations-panel"]',
        position: TOOLTIP_POSITIONS.LEFT,
        spotlight: true
      }
    ]
  },

  // ==========================================
  // GLOBAL TUTORIALS
  // ==========================================
  [TUTORIAL_IDS.NAVIGATION_INTRO]: {
    id: TUTORIAL_IDS.NAVIGATION_INTRO,
    title: 'Navigation BIONIC',
    context: TUTORIAL_CONTEXTS.GLOBAL,
    trigger: TRIGGER_CONDITIONS.ON_ONBOARDING_COMPLETE,
    priority: 0,
    steps: [
      {
        id: 'menu',
        title: 'Menu principal',
        content: 'Utilisez ce menu pour naviguer entre les différentes sections de BIONIC.',
        target: '[data-testid="nav-intelligence"]',
        position: TOOLTIP_POSITIONS.BOTTOM,
        spotlight: true
      },
      {
        id: 'intelligence',
        title: 'Intelligence',
        content: 'Accédez aux Analytics, Prévisions et Plan Maître depuis ce menu.',
        target: '[data-testid="nav-intelligence"]',
        position: TOOLTIP_POSITIONS.BOTTOM,
        spotlight: true
      },
      {
        id: 'carte',
        title: 'Carte & Territoire',
        content: 'Visualisez et analysez votre territoire de chasse.',
        target: '[data-testid="nav-carte"]',
        position: TOOLTIP_POSITIONS.BOTTOM,
        spotlight: true
      }
    ]
  },

  [TUTORIAL_IDS.FIRST_STEPS]: {
    id: TUTORIAL_IDS.FIRST_STEPS,
    title: 'Premiers pas avec BIONIC',
    context: TUTORIAL_CONTEXTS.GLOBAL,
    trigger: TRIGGER_CONDITIONS.ON_ONBOARDING_COMPLETE,
    priority: 0,
    steps: [
      {
        id: 'step1',
        title: 'Étape 1: Explorez le Dashboard',
        content: 'Commencez par explorer votre tableau de bord pour voir les conditions actuelles.',
        target: '[data-testid="nav-dashboard"]',
        position: TOOLTIP_POSITIONS.BOTTOM,
        spotlight: true,
        action: { type: 'navigate', path: '/dashboard' }
      },
      {
        id: 'step2',
        title: 'Étape 2: Consultez votre territoire',
        content: 'Visualisez votre territoire sur la carte interactive.',
        target: '[data-testid="nav-carte"]',
        position: TOOLTIP_POSITIONS.BOTTOM,
        spotlight: true
      },
      {
        id: 'step3',
        title: 'Étape 3: Planifiez votre sortie',
        content: 'Utilisez le Plan Maître pour optimiser votre prochaine session.',
        target: '[data-testid="nav-intelligence"]',
        position: TOOLTIP_POSITIONS.BOTTOM,
        spotlight: true
      }
    ]
  }
};

// ============================================
// TUTORIAL TRIGGERS
// ============================================

export const TUTORIAL_TRIGGERS = {
  [TUTORIAL_CONTEXTS.DASHBOARD]: [TUTORIAL_IDS.DASHBOARD_INTRO],
  [TUTORIAL_CONTEXTS.MAP]: [TUTORIAL_IDS.MAP_INTRO],
  [TUTORIAL_CONTEXTS.TERRITORY]: [TUTORIAL_IDS.TERRITORY_INTRO],
  [TUTORIAL_CONTEXTS.ANALYTICS]: [TUTORIAL_IDS.ANALYTICS_INTRO],
  [TUTORIAL_CONTEXTS.PLAN_MAITRE]: [TUTORIAL_IDS.PLAN_MAITRE_INTRO],
  [TUTORIAL_CONTEXTS.GLOBAL]: [TUTORIAL_IDS.NAVIGATION_INTRO, TUTORIAL_IDS.FIRST_STEPS]
};

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Get tutorial by ID
 */
export function getTutorialById(id) {
  return TUTORIALS[id] || null;
}

/**
 * Get tutorials by context
 */
export function getTutorialsByContext(context) {
  return Object.values(TUTORIALS).filter(t => t.context === context);
}

/**
 * Get all tutorial IDs
 */
export function getAllTutorialIds() {
  return Object.keys(TUTORIALS);
}

export default TUTORIALS;
