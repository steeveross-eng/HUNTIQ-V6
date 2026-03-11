/**
 * Ecoforestry Module - Plan Maître (Phase 10)
 * 
 * Ecoforestry data layers and habitat analysis.
 * Integrates with /api/v1/ecoforestry backend.
 * 
 * @module ecoforestry
 * @version 1.0.0
 */

export const MODULE_NAME = 'ecoforestry';
export const MODULE_VERSION = '1.0.0';
export const MODULE_TYPE = 'plan_maitre';

// Service
export { EcoforestryService } from './EcoforestryService';

// Components
export { HabitatAnalysis } from './components/HabitatAnalysis';
