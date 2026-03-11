/**
 * Territory Module - Plan Maître (Phase 10)
 * 
 * Territory and land management.
 * Integrates with /api/v1/territory backend.
 * 
 * @module territory
 * @version 1.0.0
 */

export const MODULE_NAME = 'territory';
export const MODULE_VERSION = '1.0.0';
export const MODULE_TYPE = 'plan_maitre';

// Service
export { TerritoryService } from './TerritoryService';

// Components
export { TerritoryCard } from './components/TerritoryCard';
export { TerritoryList } from './components/TerritoryList';
export { WaypointManager } from './components/WaypointManager';
export { WaypointMap } from './components/WaypointMap';
