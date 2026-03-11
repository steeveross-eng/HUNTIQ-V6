/**
 * Orders Module - MÉTIER (Phase 9)
 * 
 * Order management UI components.
 * Integrates with /api/v1/orders backend.
 * 
 * @module orders
 * @version 1.0.0
 */

export const MODULE_NAME = 'orders';
export const MODULE_VERSION = '1.0.0';
export const MODULE_TYPE = 'business';

// Service
export { OrdersService } from './OrdersService';

// Components
export { OrderCard } from './components/OrderCard';
export { OrdersList } from './components/OrdersList';
