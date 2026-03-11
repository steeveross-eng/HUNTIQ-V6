/**
 * BIONIC TACTICAL Design System
 * Central export file for all design system components and utilities
 * 
 * Usage:
 *   import { BionicButton, BionicCard, theme } from '@/design-system';
 */

// Theme
export { default as theme, colors, typography, spacing, borderRadius, shadows, transitions, zIndex, cssVariables } from './theme';

// Components
export { BionicButton } from './components/BionicButton';
export { BionicCard, BionicCardHeader, BionicCardTitle, BionicCardContent, BionicCardFooter } from './components/BionicCard';
export { BionicNavBar, BionicNavItem, BionicNavDropdownItem, BionicTabs } from './components/BionicNavigation';
export { BionicLayerPanel, LAYER_GROUPS, ZONE_COLORS, ZONE_ICONS } from './components/BionicLayerPanel';
export { BionicDataValue, BionicCoordinates, BionicScore, BionicStatus, BionicStatsGrid } from './components/BionicDataDisplay';

// Re-export all as default object for convenience
import theme from './theme';
import { BionicButton } from './components/BionicButton';
import { BionicCard, BionicCardHeader, BionicCardTitle, BionicCardContent, BionicCardFooter } from './components/BionicCard';
import { BionicNavBar, BionicNavItem, BionicNavDropdownItem, BionicTabs } from './components/BionicNavigation';
import { BionicLayerPanel, LAYER_GROUPS, ZONE_COLORS, ZONE_ICONS } from './components/BionicLayerPanel';
import { BionicDataValue, BionicCoordinates, BionicScore, BionicStatus, BionicStatsGrid } from './components/BionicDataDisplay';

export default {
  theme,
  components: {
    BionicButton,
    BionicCard,
    BionicCardHeader,
    BionicCardTitle,
    BionicCardContent,
    BionicCardFooter,
    BionicNavBar,
    BionicNavItem,
    BionicNavDropdownItem,
    BionicTabs,
    BionicLayerPanel,
    BionicDataValue,
    BionicCoordinates,
    BionicScore,
    BionicStatus,
    BionicStatsGrid,
  },
  config: {
    LAYER_GROUPS,
    ZONE_COLORS,
    ZONE_ICONS,
  },
};
