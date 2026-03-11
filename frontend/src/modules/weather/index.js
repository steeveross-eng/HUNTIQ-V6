/**
 * Weather Module - CORE (Phase 8)
 * 
 * Provides weather display and forecast components.
 * Integrates with /api/v1/weather backend.
 * 
 * @module weather
 * @version 1.1.0
 */

export const MODULE_NAME = 'weather';
export const MODULE_VERSION = '1.1.0';
export const MODULE_TYPE = 'core';

// Service
export { WeatherService } from './WeatherService';

// Components
export { WeatherWidget } from './components/WeatherWidget';
export { WeatherForecast } from './components/WeatherForecast';
export { WindRose } from './components/WindRose';
export { HuntingConditions } from './components/HuntingConditions';

// Advanced Weather Widget (v1.1.0 - OpenWeatherMap integration)
export { default as AdvancedWeatherWidget } from './components/AdvancedWeatherWidget';
