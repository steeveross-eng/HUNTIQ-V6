/**
 * Nutrition Module - CORE (Phase 8)
 * 
 * Provides nutrition analysis UI components.
 * Integrates with /api/v1/nutrition backend.
 * 
 * @module nutrition
 * @version 1.0.0
 */

export const MODULE_NAME = 'nutrition';
export const MODULE_VERSION = '1.0.0';
export const MODULE_TYPE = 'core';

// Service
export { NutritionService } from './NutritionService';

// Components
export { NutritionAnalyzer } from './components/NutritionAnalyzer';
export { NutritionCard } from './components/NutritionCard';
export { NutritionScore } from './components/NutritionScore';
