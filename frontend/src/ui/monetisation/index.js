/**
 * Monetisation Module - V5-ULTIME
 * ================================
 * 
 * Point d'entrée global du module de monétisation.
 * Regroupe: Payment, Freemium, Upsell, Onboarding, Tutorial
 */

// Payment
export { PaymentDashboard, PricingCard, PaymentService } from './payment';

// Freemium
export { FreemiumService, QuotaIndicator, FreemiumGate } from './freemium';

// Upsell
export { UpsellService, UpsellPopup, useUpsell } from './upsell';

// Onboarding
export { OnboardingService, OnboardingWizard } from './onboarding';

// Tutorial
export { TutorialService, TutorialOverlay, DailyTip } from './tutorial';
