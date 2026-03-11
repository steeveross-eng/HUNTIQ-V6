/**
 * Suppliers Service - API client for suppliers module
 * Phase 10+ - Connected to real backend
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export class SuppliersService {
  static async getHealth() {
    try {
      const response = await fetch(`${API_URL}/api/v1/suppliers/`);
      if (!response.ok) return { status: 'unavailable' };
      return response.json();
    } catch {
      return { status: 'unavailable' };
    }
  }

  static async getStats() {
    try {
      const response = await fetch(`${API_URL}/api/v1/suppliers/stats`);
      if (!response.ok) return { total: 0, active: 0 };
      return response.json();
    } catch {
      return { total: 0, active: 0 };
    }
  }

  static async getSuppliers(isActive = null) {
    try {
      let url = `${API_URL}/api/v1/suppliers/`;
      if (isActive !== null) {
        url += `?is_active=${isActive}`;
      }
      const response = await fetch(url);
      if (!response.ok) return [];
      const data = await response.json();
      return Array.isArray(data) ? data : (data.suppliers || []);
    } catch {
      return [];
    }
  }

  static async getSupplier(supplierId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/suppliers/${supplierId}`);
      if (!response.ok) return null;
      return response.json();
    } catch {
      return null;
    }
  }

  static async createSupplier(supplierData) {
    try {
      const response = await fetch(`${API_URL}/api/v1/suppliers/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(supplierData)
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async updateSupplier(supplierId, updateData) {
    try {
      const response = await fetch(`${API_URL}/api/v1/suppliers/${supplierId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData)
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async deleteSupplier(supplierId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/suppliers/${supplierId}`, {
        method: 'DELETE'
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  // Helper methods
  static formatSupplierType(type) {
    const types = {
      'manufacturer': 'Fabricant',
      'distributor': 'Distributeur',
      'retailer': 'Détaillant',
      'dropshipper': 'Dropshipper'
    };
    return types[type] || type;
  }

  static getSupplierStatusColor(isActive) {
    return isActive ? 'emerald' : 'red';
  }
}

export default SuppliersService;
