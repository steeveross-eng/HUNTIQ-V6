/**
 * api - Core Utils
 * =================
 * API helper utilities.
 * Architecture LEGO V5 - Core Utils (no business logic)
 * 
 * @module core/utils
 */

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

/**
 * Generic API request helper
 * @param {string} endpoint - API endpoint
 * @param {object} options - Fetch options
 */
export const apiRequest = async (endpoint, options = {}) => {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  // Add auth token if available
  const token = localStorage.getItem('auth_token');
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    headers: {
      ...defaultHeaders,
      ...options.headers
    },
    ...options
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ 
      detail: `HTTP ${response.status}: ${response.statusText}` 
    }));
    throw new Error(error.detail || error.message || 'Erreur serveur');
  }

  // Handle empty responses
  const text = await response.text();
  return text ? JSON.parse(text) : null;
};

/**
 * GET request
 * @param {string} endpoint - API endpoint
 * @param {object} params - Query parameters
 */
export const apiGet = async (endpoint, params = {}) => {
  const url = new URL(endpoint, API_BASE);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      url.searchParams.append(key, value);
    }
  });
  
  return apiRequest(url.pathname + url.search, { method: 'GET' });
};

/**
 * POST request
 * @param {string} endpoint - API endpoint
 * @param {object} data - Request body
 */
export const apiPost = async (endpoint, data = {}) => {
  return apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(data)
  });
};

/**
 * PUT request
 * @param {string} endpoint - API endpoint
 * @param {object} data - Request body
 */
export const apiPut = async (endpoint, data = {}) => {
  return apiRequest(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data)
  });
};

/**
 * DELETE request
 * @param {string} endpoint - API endpoint
 */
export const apiDelete = async (endpoint) => {
  return apiRequest(endpoint, { method: 'DELETE' });
};

/**
 * Upload file
 * @param {string} endpoint - API endpoint
 * @param {File} file - File to upload
 * @param {object} additionalData - Additional form data
 */
export const apiUpload = async (endpoint, file, additionalData = {}) => {
  const formData = new FormData();
  formData.append('file', file);
  
  Object.entries(additionalData).forEach(([key, value]) => {
    formData.append(key, value);
  });

  const token = localStorage.getItem('auth_token');
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    headers,
    body: formData
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(error.detail || 'Erreur lors du téléversement');
  }

  return response.json();
};

export default {
  request: apiRequest,
  get: apiGet,
  post: apiPost,
  put: apiPut,
  delete: apiDelete,
  upload: apiUpload
};
