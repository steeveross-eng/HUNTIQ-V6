/**
 * Strategy Module - CORE (Phase 8)
 * 
 * Provides hunting strategy components.
 * Integrates with /api/v1/strategy backend.
 * 
 * @module strategy
 * @version 1.0.0
 */

export const MODULE_NAME = 'strategy';
export const MODULE_VERSION = '1.0.0';
export const MODULE_TYPE = 'core';

// Service
export { StrategyService } from './StrategyService';

// Components
export { StrategyPanel } from './components/StrategyPanel';
export { StrategyCard } from './components/StrategyCard';
export { StrategyTimeline } from './components/StrategyTimeline';
