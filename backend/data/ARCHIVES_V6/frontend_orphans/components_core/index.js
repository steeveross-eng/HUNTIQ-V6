/**
 * V5-ULTIME Frontend Architecture
 * ================================
 * 
 * STRUCTURE MODULAIRE STRICTE (LEGO)
 * 
 * Règles:
 * 1. Un module = un dossier = une page = un composant parent
 * 2. Aucun composant partagé hors /components/core
 * 3. Aucun import croisé entre modules
 * 4. Aucun helper global
 * 5. Navigation modulaire obligatoire
 * 
 * Structure:
 * /src
 * ├── components/
 * │   └── core/          # Composants réutilisables SEULS autorisés
 * ├── ui/
 * │   ├── core/          # UI Core (base)
 * │   ├── metier/        # UI Métier (business)
 * │   ├── plan_maitre/   # UI Plan Maître (Phase 9)
 * │   ├── scoring/       # UI Scoring
 * │   ├── meteo/         # UI Météo
 * │   ├── strategie/     # UI Stratégie
 * │   └── territoire/    # UI Territoire
 * ├── data_layers/
 * │   ├── ecoforestry/   # Couche données écoforestières
 * │   ├── behavioral/    # Couche données comportementales
 * │   ├── simulation/    # Couche données simulation
 * │   ├── layers_3d/     # Couche données 3D
 * │   └── advanced_geospatial/ # Couche géospatiale avancée
 * ├── modules/           # Modules métier isolés
 * └── pages/             # Pages principales
 */

// Core exports
export { default as CoreNavigation } from './CoreNavigation';
export { default as CoreLayout } from './CoreLayout';
export { default as CoreButton } from './CoreButton';
export { default as CoreCard } from './CoreCard';
export { default as CoreLoader } from './CoreLoader';
export { default as CoreError } from './CoreError';
export { default as CoreModal } from './CoreModal';

// Module registry
export { MODULE_ROUTES } from './CoreNavigation';
