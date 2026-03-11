/**
 * Territory Components Index
 * Re-exports all territory map sub-components
 * 
 * BLOC 3 Refactoring: Added constants and MapHelpers exports
 */

// Sub-components
export { default as MapControls, dmsToDecimal, decimalToDms, SCALE_TO_ZOOM } from './MapControls';
export { default as LayersPanel, BASE_LAYERS } from './LayersPanel';
export { default as MapToolbar } from './MapToolbar';
export { default as WaypointPanel, WAYPOINT_TYPES } from './WaypointPanel';
export { default as TerritoryFilter, TERRITORY_TYPES } from './TerritoryFilter';
export { default as SpeciesFilter, SPECIES_CONFIG, TIME_WINDOWS } from './SpeciesFilter';
export { default as TerritoryHeader } from './TerritoryHeader';
export { default as GPSNavigationPanel } from './GPSNavigationPanel';
export { default as AnalysisResultsPanel } from './AnalysisResultsPanel';
export { generateGPX, downloadGPX, parseGPX } from './gpxUtils';

// BLOC 3: Extracted constants and helpers
export * from './constants';
export { 
  createCustomIcon,
  HeatmapLayer,
  MapCenterController,
  MapClickHandler,
  ZoomSyncComponent,
  dmsToDecimal as convertDmsToDecimal,
  decimalToDms as convertDecimalToDms
} from './MapHelpers';
