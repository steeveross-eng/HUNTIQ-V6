/**
 * Wildlife Module - Plan Maître (Phase 10)
 * 
 * Wildlife behavior tracking and prediction.
 * Integrates with /api/v1/wildlife backend.
 * 
 * @module wildlife
 * @version 1.0.0
 */

export const MODULE_NAME = 'wildlife';
export const MODULE_VERSION = '1.0.0';
export const MODULE_TYPE = 'plan_maitre';

// Service
export { WildlifeService } from './WildlifeService';

// Components
export { WildlifeTracker } from './components/WildlifeTracker';
export { SpeciesSelector } from './components/SpeciesSelector';
