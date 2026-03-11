/**
 * formatters - Core Utils
 * ========================
 * Common formatting utilities.
 * Architecture LEGO V5 - Core Utils (no business logic)
 * 
 * @module core/utils
 */

/**
 * Format a number with thousands separator
 * @param {number} num - Number to format
 * @param {string} locale - Locale for formatting (default: fr-CA)
 */
export const formatNumber = (num, locale = 'fr-CA') => {
  if (num === null || num === undefined) return '-';
  return new Intl.NumberFormat(locale).format(num);
};

/**
 * Format currency
 * @param {number} amount - Amount to format
 * @param {string} currency - Currency code (default: CAD)
 * @param {string} locale - Locale for formatting (default: fr-CA)
 */
export const formatCurrency = (amount, currency = 'CAD', locale = 'fr-CA') => {
  if (amount === null || amount === undefined) return '-';
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
};

/**
 * Format percentage
 * @param {number} value - Value to format (0-100 or 0-1)
 * @param {boolean} isDecimal - Whether value is decimal (0-1)
 */
export const formatPercent = (value, isDecimal = false) => {
  if (value === null || value === undefined) return '-';
  const percent = isDecimal ? value * 100 : value;
  return `${percent.toFixed(1)}%`;
};

/**
 * Format date
 * @param {string|Date} date - Date to format
 * @param {object} options - Intl.DateTimeFormat options
 */
export const formatDate = (date, options = {}) => {
  if (!date) return '-';
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...options
  };
  
  return new Intl.DateTimeFormat('fr-CA', defaultOptions).format(dateObj);
};

/**
 * Format date with time
 * @param {string|Date} date - Date to format
 */
export const formatDateTime = (date) => {
  return formatDate(date, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * Format relative time (time ago)
 * @param {string|Date} date - Date to format
 */
export const formatTimeAgo = (date) => {
  if (!date) return '-';
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const seconds = Math.floor((now - dateObj) / 1000);
  
  if (seconds < 60) return 'À l\'instant';
  if (seconds < 3600) return `Il y a ${Math.floor(seconds / 60)} min`;
  if (seconds < 86400) return `Il y a ${Math.floor(seconds / 3600)} h`;
  if (seconds < 604800) return `Il y a ${Math.floor(seconds / 86400)} j`;
  if (seconds < 2592000) return `Il y a ${Math.floor(seconds / 604800)} sem`;
  
  return formatDate(dateObj);
};

/**
 * Format file size
 * @param {number} bytes - Size in bytes
 */
export const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 B';
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${units[i]}`;
};

/**
 * Format duration
 * @param {number} seconds - Duration in seconds
 */
export const formatDuration = (seconds) => {
  if (!seconds || seconds === 0) return '0s';
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  }
  return `${secs}s`;
};

/**
 * Truncate text with ellipsis
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 */
export const truncateText = (text, maxLength = 100) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
};

/**
 * Capitalize first letter
 * @param {string} text - Text to capitalize
 */
export const capitalize = (text) => {
  if (!text) return '';
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
};

/**
 * Slugify text
 * @param {string} text - Text to slugify
 */
export const slugify = (text) => {
  if (!text) return '';
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
};
