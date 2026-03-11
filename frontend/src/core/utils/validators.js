/**
 * validators - Core Utils
 * ========================
 * Common validation utilities.
 * Architecture LEGO V5 - Core Utils (no business logic)
 * 
 * @module core/utils
 */

/**
 * Validate email format
 * @param {string} email - Email to validate
 */
export const isValidEmail = (email) => {
  if (!email) return false;
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
};

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {object} - Validation result with score and messages
 */
export const validatePassword = (password) => {
  const result = {
    isValid: false,
    score: 0,
    messages: []
  };

  if (!password) {
    result.messages.push('Le mot de passe est requis');
    return result;
  }

  // Length check
  if (password.length >= 8) {
    result.score += 1;
  } else {
    result.messages.push('Minimum 8 caractères');
  }

  // Uppercase check
  if (/[A-Z]/.test(password)) {
    result.score += 1;
  } else {
    result.messages.push('Au moins une majuscule');
  }

  // Lowercase check
  if (/[a-z]/.test(password)) {
    result.score += 1;
  } else {
    result.messages.push('Au moins une minuscule');
  }

  // Number check
  if (/\d/.test(password)) {
    result.score += 1;
  } else {
    result.messages.push('Au moins un chiffre');
  }

  // Special character check
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    result.score += 1;
  } else {
    result.messages.push('Au moins un caractère spécial');
  }

  result.isValid = result.score >= 4;
  return result;
};

/**
 * Validate phone number (Canadian format)
 * @param {string} phone - Phone number to validate
 */
export const isValidPhone = (phone) => {
  if (!phone) return false;
  // Remove all non-digit characters
  const digits = phone.replace(/\D/g, '');
  // Canadian phone numbers are 10 or 11 digits (with country code)
  return digits.length === 10 || (digits.length === 11 && digits.startsWith('1'));
};

/**
 * Validate postal code (Canadian format)
 * @param {string} postalCode - Postal code to validate
 */
export const isValidPostalCode = (postalCode) => {
  if (!postalCode) return false;
  const regex = /^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$/;
  return regex.test(postalCode);
};

/**
 * Validate URL format
 * @param {string} url - URL to validate
 */
export const isValidUrl = (url) => {
  if (!url) return false;
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

/**
 * Validate that a value is not empty
 * @param {any} value - Value to check
 */
export const isNotEmpty = (value) => {
  if (value === null || value === undefined) return false;
  if (typeof value === 'string') return value.trim().length > 0;
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === 'object') return Object.keys(value).length > 0;
  return true;
};

/**
 * Validate number range
 * @param {number} value - Value to check
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 */
export const isInRange = (value, min, max) => {
  if (typeof value !== 'number' || isNaN(value)) return false;
  return value >= min && value <= max;
};

/**
 * Validate coordinates (lat/lng)
 * @param {number} lat - Latitude
 * @param {number} lng - Longitude
 */
export const isValidCoordinates = (lat, lng) => {
  return isInRange(lat, -90, 90) && isInRange(lng, -180, 180);
};

/**
 * Sanitize string (remove XSS vectors)
 * @param {string} input - String to sanitize
 */
export const sanitizeString = (input) => {
  if (!input) return '';
  return input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;');
};
