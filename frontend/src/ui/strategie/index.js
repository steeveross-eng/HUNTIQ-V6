/**
 * UI Stratégie - V5-ULTIME
 * ========================
 * 
 * Module UI pour les stratégies de chasse.
 * Structure modulaire stricte LEGO.
 */

export { default as StrategieDashboard } from './StrategieDashboard';
export { default as StrategieCard } from './StrategieCard';
export { default as StrategieTimeline } from './StrategieTimeline';

export const STRATEGY_TYPES = {
  APPROACH: 'approach',
  AMBUSH: 'ambush',
  TRACKING: 'tracking',
  CALL: 'call',
};
