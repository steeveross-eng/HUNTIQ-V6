/**
 * Admin Module Components
 * =======================
 * Barrel export for admin panel components.
 * Architecture LEGO V5 - Business Module
 * 
 * @module modules/admin/components
 */

// Content management
export { default as ContentDepot } from './ContentDepot';
export { default as CategoriesManager } from './CategoriesManager';
export { default as PromptManager } from './PromptManager';

// System management
export { default as BackupManager } from './BackupManager';
export { default as MaintenanceControl } from './MaintenanceControl';
export { default as SiteAccessControl } from './SiteAccessControl';
export { default as FeatureControlsAdmin } from './FeatureControlsAdmin';

// Marketing & Branding
export { default as BrandIdentityAdmin } from './BrandIdentityAdmin';
export { default as MarketingAIAdmin } from './MarketingAIAdmin';
export { default as EmailAdmin } from './EmailAdmin';

// Products & Pricing
export { default as ProductDiscoveryAdmin } from './ProductDiscoveryAdmin';
export { default as LandsPricingAdmin } from './LandsPricingAdmin';
export { default as AutoCategorizeButton } from './AutoCategorizeButton';

// Hotspots
export { default as AdminHotspotsPanel } from './AdminHotspotsPanel';
