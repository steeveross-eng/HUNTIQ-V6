/**
 * Map Interaction Module - Barrel Export
 * =======================================
 * 
 * Module d'interaction cartographique universel.
 * Architecture LEGO V5 - Module métier isolé.
 * 
 * @module modules/map_interaction
 */

// Components
export { MapInteractionLayer } from './components/MapInteractionLayer';
export { default as MapInteractionLayerDefault } from './components/MapInteractionLayer';

// Services
export { WaypointService } from './services/WaypointService';

// Hooks
export { useMapInteraction } from './hooks/useMapInteraction';
