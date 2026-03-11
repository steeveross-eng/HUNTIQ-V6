/**
 * User Module - MÉTIER (Phase 9)
 * 
 * User management and authentication UI components.
 * Integrates with /api/v1/user backend.
 * 
 * @module user
 * @version 1.0.0
 */

export const MODULE_NAME = 'user';
export const MODULE_VERSION = '1.0.0';
export const MODULE_TYPE = 'business';

// Service
export { UserService } from './UserService';

// Components
export { UserProfile } from './components/UserProfile';
export { UserActivity } from './components/UserActivity';
