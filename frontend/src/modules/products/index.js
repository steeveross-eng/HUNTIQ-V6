/**
 * Products Module - MÉTIER (Phase 9)
 * 
 * Product management UI components.
 * Integrates with /api/v1/products backend.
 * 
 * @module products
 * @version 1.0.0
 */

export const MODULE_NAME = 'products';
export const MODULE_VERSION = '1.0.0';
export const MODULE_TYPE = 'business';

// Service
export { ProductsService } from './ProductsService';

// Components
export { ProductCard } from './components/ProductCard';
export { ProductGrid } from './components/ProductGrid';
