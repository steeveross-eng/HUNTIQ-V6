/**
 * Core Utils - BIONIC™ V5
 * ========================
 * 
 * Barrel export for all core utilities.
 * These are generic, reusable functions with NO business logic.
 * 
 * @module core/utils
 */

// Formatters
export {
  formatNumber,
  formatCurrency,
  formatPercent,
  formatDate,
  formatDateTime,
  formatTimeAgo,
  formatFileSize,
  formatDuration,
  truncateText,
  capitalize,
  slugify
} from './formatters';

// Validators
export {
  isValidEmail,
  validatePassword,
  isValidPhone,
  isValidPostalCode,
  isValidUrl,
  isNotEmpty,
  isInRange,
  isValidCoordinates,
  sanitizeString
} from './validators';

// API helpers
export {
  apiRequest,
  apiGet,
  apiPost,
  apiPut,
  apiDelete,
  apiUpload
} from './api';

// Default export for api
export { default as api } from './api';
