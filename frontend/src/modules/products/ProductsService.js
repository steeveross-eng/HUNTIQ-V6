/**
 * Products Service - API client for products module
 * Phase 10+ - Connected to real backend
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export class ProductsService {
  static async getHealth() {
    try {
      const response = await fetch(`${API_URL}/api/v1/products/`);
      if (!response.ok) return { status: 'unavailable' };
      return response.json();
    } catch {
      return { status: 'unavailable' };
    }
  }

  static async getStats() {
    try {
      const response = await fetch(`${API_URL}/api/v1/products/stats`);
      if (!response.ok) return { total: 0, categories: [] };
      return response.json();
    } catch {
      return { total: 0, categories: [] };
    }
  }

  static async getProducts(options = {}) {
    try {
      const params = new URLSearchParams();
      if (options.category) params.append('category', options.category);
      if (options.animal_type) params.append('animal_type', options.animal_type);
      if (options.season) params.append('season', options.season);
      if (options.sale_mode) params.append('sale_mode', options.sale_mode);
      if (options.limit) params.append('limit', options.limit);
      
      const response = await fetch(`${API_URL}/api/v1/products/?${params}`);
      if (!response.ok) return [];
      return response.json();
    } catch {
      return [];
    }
  }

  static async getTopProducts(limit = 5) {
    try {
      const response = await fetch(`${API_URL}/api/v1/products/top?limit=${limit}`);
      if (!response.ok) return [];
      const data = await response.json();
      // Ensure we return an array
      return Array.isArray(data) ? data : (data.products || []);
    } catch {
      return [];
    }
  }

  static async getFilterOptions() {
    try {
      const response = await fetch(`${API_URL}/api/v1/products/filters/options`);
      if (!response.ok) return { categories: [], animal_types: [], seasons: [] };
      return response.json();
    } catch {
      return { categories: [], animal_types: [], seasons: [] };
    }
  }

  static async getProduct(productId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/products/${productId}`);
      if (!response.ok) return null;
      return response.json();
    } catch {
      return null;
    }
  }

  static async createProduct(productData) {
    try {
      const response = await fetch(`${API_URL}/api/v1/products/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(productData)
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async updateProduct(productId, updateData) {
    try {
      const response = await fetch(`${API_URL}/api/v1/products/${productId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData)
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async deleteProduct(productId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/products/${productId}`, {
        method: 'DELETE'
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async searchProducts(searchRequest) {
    try {
      const response = await fetch(`${API_URL}/api/v1/products/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(searchRequest)
      });
      if (!response.ok) return { results: [] };
      return response.json();
    } catch {
      return { results: [] };
    }
  }

  static async trackAnalyze(productId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/products/${productId}/track/analyze`, {
        method: 'POST'
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async trackCompare(productId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/products/${productId}/track/compare`, {
        method: 'POST'
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async trackClick(productId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/products/${productId}/track/click`, {
        method: 'POST'
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }
}

export default ProductsService;
