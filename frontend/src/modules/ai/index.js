/**
 * AI Module - CORE (Phase 8)
 * 
 * Provides AI analysis interface components.
 * Integrates with /api/v1/ai backend.
 * 
 * @module ai
 * @version 1.0.0
 */

export const MODULE_NAME = 'ai';
export const MODULE_VERSION = '1.0.0';
export const MODULE_TYPE = 'core';

// Service
export { AIService } from './AIService';

// Components
export { AIAnalyzer } from './components/AIAnalyzer';
export { AIChat } from './components/AIChat';
export { AIInsights } from './components/AIInsights';
