/**
 * MODULE GROUPE - Exports centralisés
 * BIONIC Design System compliant
 * Version: 1.5.0 - Phase 6
 * 
 * Fonctionnalités collaboratives pour les sorties de chasse en équipe.
 */

// Components - Phase 1
export { GroupeTab } from './components/GroupeTab';
export { GroupePanel } from './components/GroupePanel';

// Components - Phase 3
export { MembersTracker } from './components/MembersTracker';

// Components - Phase 3.5
export { GroupChat } from './components/GroupChat';

// Components - Phase 4
export { SafetyStatus, SafetyStatusBadge } from './components/SafetyStatus';
export { ShootingZones, ShootingZone } from './components/ShootingZones';

// Components - Phase 5
export { SmartAlerts, AlertItem, AlertTypeBadge, SeverityBadge } from './components/SmartAlerts';

// Components - Phase 6
export { SessionHeatmap } from './components/SessionHeatmap';

// Hooks - Phase 3
export { useGroupeTracking, TRACKING_STATUS } from './hooks/useGroupeTracking';

// Hooks - Phase 3.5
export { useGroupeChat, MESSAGE_TYPES, ALERT_TYPES as CHAT_ALERT_TYPES, QUICK_MESSAGES } from './hooks/useGroupeChat';

// Hooks - Phase 4
export { useGroupeSafety, SAFETY_STATUS, SHOOTING_ZONE_TYPES } from './hooks/useGroupeSafety';

// Hooks - Phase 5
export { useGroupeAlerts, ALERT_TYPES, ALERT_SEVERITY } from './hooks/useGroupeAlerts';

// Services (Phase 7+)
// export { GroupeService } from './services/GroupeService';
