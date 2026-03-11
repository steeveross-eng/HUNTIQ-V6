/**
 * UI Territoire - V5-ULTIME
 * =========================
 * 
 * Module UI pour la gestion du territoire.
 * Structure modulaire stricte LEGO.
 */

export { default as TerritoireDashboard } from './TerritoireDashboard';
export { default as TerritoireMap } from './TerritoireMap';
export { default as TerritoireStats } from './TerritoireStats';

export const ZONE_TYPES = {
  HUNTING: 'hunting',
  FEEDING: 'feeding',
  RESTING: 'resting',
  TRANSIT: 'transit',
};
