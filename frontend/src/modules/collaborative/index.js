/**
 * Collaborative Module - Plan Maître (Phase 10)
 * 
 * Collaborative sightings and reports sharing.
 * Integrates with /api/v1/collaborative backend.
 * 
 * @module collaborative
 * @version 1.0.0
 */

export const MODULE_NAME = 'collaborative';
export const MODULE_VERSION = '1.0.0';
export const MODULE_TYPE = 'plan_maitre';

// Service
export { CollaborativeService } from './CollaborativeService';

// Components
export { SightingsFeed } from './components/SightingsFeed';
