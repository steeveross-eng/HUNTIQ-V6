/**
 * Behavioral Module - Plan Maître (Phase 10)
 * 
 * Behavioral data layers and activity patterns.
 * Integrates with /api/v1/behavioral backend.
 * 
 * @module behavioral
 * @version 1.0.0
 */

export const MODULE_NAME = 'behavioral';
export const MODULE_VERSION = '1.0.0';
export const MODULE_TYPE = 'plan_maitre';

// Service
export { BehavioralService } from './BehavioralService';

// Components
export { ActivityChart } from './components/ActivityChart';
