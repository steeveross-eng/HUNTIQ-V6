/**
 * Recommendation Module - Plan Maître (Phase 10)
 * 
 * Intelligent product and strategy recommendations.
 * Integrates with /api/v1/recommendation backend.
 * 
 * @module recommendation
 * @version 1.0.0
 */

export const MODULE_NAME = 'recommendation';
export const MODULE_VERSION = '1.0.0';
export const MODULE_TYPE = 'plan_maitre';

// Service
export { RecommendationService } from './RecommendationService';

// Components
export { RecommendationPanel } from './components/RecommendationPanel';
export { SimilarProducts } from './components/SimilarProducts';
