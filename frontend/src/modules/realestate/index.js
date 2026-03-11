/**
 * BIONIC™ Real Estate Module - Frontend
 * ======================================
 * Phase 11-15: Module Immobilier
 * 
 * "La plateforme qui révèle la valeur géospatiale d'un terrain"
 */

// Components
export { default as RealEstatePanel } from './components/RealEstatePanel';
export { default as PropertyCard } from './components/PropertyCard';
export { default as PropertyGallery } from './components/PropertyGallery';
export { default as PropertySourceBadge } from './components/PropertySourceBadge';

// Opportunity Components
export { default as OpportunityList } from './components/OpportunityList';
export { default as OpportunityCard } from './components/OpportunityCard';
export { default as OpportunityFilters } from './components/OpportunityFilters';

// Marketplace Components
export { default as MarketplacePanel } from './components/MarketplacePanel';
export { default as MarketplaceCreateForm } from './components/MarketplaceCreateForm';
export { default as MarketplaceCard } from './components/MarketplaceCard';

// Services
export { RealEstateService } from './services/RealEstateService';
export { OpportunityService } from './services/OpportunityService';

// Hooks
export { useProperties } from './hooks/useProperties';
export { useOpportunities } from './hooks/useOpportunities';

// Constants
export const MODULE_VERSION = '0.1.0';
export const MODULE_PHASE = '11-15';
