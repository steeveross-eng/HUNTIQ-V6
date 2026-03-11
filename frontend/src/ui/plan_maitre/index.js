/**
 * UI Plan Maître - V5-ULTIME (Phase 9)
 * =====================================
 * 
 * Module UI complet pour le Plan Maître.
 * Structure modulaire stricte LEGO.
 * 
 * Intégrations backend:
 * - rules_engine
 * - strategy_master_engine
 */

export { default as PlanMaitreDashboard } from './PlanMaitreDashboard';
export { default as PlanMaitreTimeline } from './PlanMaitreTimeline';
export { default as PlanMaitreRules } from './PlanMaitreRules';
export { default as PlanMaitreStrategyView } from './PlanMaitreStrategyView';
export { default as PlanMaitreStats } from './PlanMaitreStats';

export const PLAN_PHASES = {
  PREPARATION: 'preparation',
  RECONNAISSANCE: 'reconnaissance',
  INSTALLATION: 'installation',
  EXECUTION: 'execution',
  REVIEW: 'review',
};

export const STRATEGY_TYPES = {
  APPROACH: 'approach',
  AMBUSH: 'ambush',
  TRACKING: 'tracking',
  CALL: 'call',
  MIXED: 'mixed',
};
