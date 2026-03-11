/**
 * Scoring Module - CORE (Phase 8)
 * 
 * Provides score visualization components.
 * Integrates with /api/v1/scoring backend.
 * 
 * @module scoring
 * @version 1.0.0
 */

export const MODULE_NAME = 'scoring';
export const MODULE_VERSION = '1.0.0';
export const MODULE_TYPE = 'core';

// Service
export { ScoringService } from './ScoringService';

// Components
export { ScoreDisplay } from './components/ScoreDisplay';
export { ScoreGauge } from './components/ScoreGauge';
export { ScoreBreakdown } from './components/ScoreBreakdown';
export { ScoreCompare } from './components/ScoreCompare';
