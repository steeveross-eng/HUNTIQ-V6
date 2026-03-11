/**
 * UI Météo - V5-ULTIME
 * ====================
 * 
 * Module UI pour les données météorologiques.
 * Structure modulaire stricte LEGO.
 */

export { default as MeteoDashboard } from './MeteoDashboard';
export { default as MeteoCard } from './MeteoCard';
export { default as MeteoForecast } from './MeteoForecast';

export const METEO_CONDITIONS = {
  IDEAL: 'ideal',
  FAVORABLE: 'favorable',
  NEUTRAL: 'neutral',
  UNFAVORABLE: 'unfavorable',
};
