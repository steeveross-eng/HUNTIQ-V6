/**
 * Live Heading View Module - V5-ULTIME PHASE 6
 * ============================================
 * 
 * Module d'immersion pour la navigation de chasse.
 * Structure modulaire stricte LEGO - Composant parent isolé.
 * 
 * Features:
 * - GPS-based travelling view
 * - Forward cone (30-60°)
 * - Direction line
 * - Wind overlay (real-time)
 * - POI markers
 * - Alerts overlay
 * - Compass widget
 * 
 * @module live_heading_view
 * @version 2.0.0 (V5-ULTIME)
 */

export const MODULE_NAME = 'live_heading_view';
export const MODULE_VERSION = '2.0.0';
export const MODULE_TYPE = 'special';
export const MODULE_PHASE = 'P6';

// Component exports - Structure LEGO
export { LiveHeadingView } from './components/LiveHeadingView';
export { CompassWidget } from './components/CompassWidget';
export { ForwardCone } from './components/ForwardCone';
export { WindIndicator } from './components/WindIndicator';
export { POIMarker } from './components/POIMarker';
export { AlertToast } from './components/AlertToast';
export { SessionControls } from './components/SessionControls';
export { SessionStats } from './components/SessionStats';

// Default export for module registration
export { LiveHeadingView as default } from './components/LiveHeadingView';
