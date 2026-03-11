/**
 * Predictive Module - Plan Maître (Phase 10)
 * 
 * Predictive analytics for hunting success.
 * Integrates with /api/v1/predictive backend.
 * 
 * @module predictive
 * @version 1.0.0
 */

export const MODULE_NAME = 'predictive';
export const MODULE_VERSION = '1.0.0';
export const MODULE_TYPE = 'plan_maitre';

// Service
export { PredictiveService } from './PredictiveService';

// Components
export { PredictiveWidget } from './components/PredictiveWidget';
