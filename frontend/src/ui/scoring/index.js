/**
 * UI Scoring - V5-ULTIME
 * ======================
 * 
 * Module UI pour le système de scoring.
 * Structure modulaire stricte LEGO.
 */

// Exports du module
export { default as ScoringDashboard } from './ScoringDashboard';
export { default as ScoringCard } from './ScoringCard';
export { default as ScoringGauge } from './ScoringGauge';
export { default as ScoringRadar } from './ScoringRadar';

// Service du module
export { ScoringUIService } from './ScoringUIService';

// Types et constantes
export const SCORING_CATEGORIES = {
  NUTRITION: 'nutrition',
  ATTRACTIVITY: 'attractivity',
  WEATHER_IMPACT: 'weather_impact',
  TERRAIN: 'terrain',
  TIMING: 'timing',
};

export const SCORING_THRESHOLDS = {
  EXCELLENT: 85,
  GOOD: 70,
  AVERAGE: 50,
  POOR: 30,
};
