/**
 * Customers Service - API client for customers module
 * Phase 10+ - Connected to real backend
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export class CustomersService {
  static async getHealth() {
    try {
      const response = await fetch(`${API_URL}/api/v1/customers/`);
      if (!response.ok) return { status: 'unavailable' };
      return response.json();
    } catch {
      return { status: 'unavailable' };
    }
  }

  static async getStats() {
    try {
      const response = await fetch(`${API_URL}/api/v1/customers/stats`);
      if (!response.ok) return { total: 0, active: 0, new: 0 };
      return response.json();
    } catch {
      return { total: 0, active: 0, new: 0 };
    }
  }

  static async getCustomers() {
    try {
      const response = await fetch(`${API_URL}/api/v1/customers/`);
      if (!response.ok) return [];
      const data = await response.json();
      return Array.isArray(data) ? data : (data.customers || []);
    } catch {
      return [];
    }
  }

  static async getCustomer(customerId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/customers/${customerId}`);
      if (!response.ok) return null;
      return response.json();
    } catch {
      return null;
    }
  }

  static async getCustomerBySession(sessionId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/customers/session/${sessionId}`);
      if (!response.ok) return null;
      return response.json();
    } catch {
      return null;
    }
  }

  static async createCustomer(customerData) {
    try {
      const response = await fetch(`${API_URL}/api/v1/customers/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(customerData)
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async updateCustomer(customerId, updateData) {
    try {
      const response = await fetch(`${API_URL}/api/v1/customers/${customerId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData)
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  // Helper methods
  static getSessionId() {
    let sessionId = localStorage.getItem('customer_session_id');
    if (!sessionId) {
      sessionId = 'cust_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('customer_session_id', sessionId);
    }
    return sessionId;
  }

  static formatCustomerStatus(status) {
    const statuses = {
      'new': 'Nouveau',
      'active': 'Actif',
      'inactive': 'Inactif',
      'vip': 'VIP'
    };
    return statuses[status] || status;
  }

  static getStatusColor(status) {
    const colors = {
      'new': 'blue',
      'active': 'emerald',
      'inactive': 'slate',
      'vip': 'amber'
    };
    return colors[status] || 'slate';
  }
}

export default CustomersService;
