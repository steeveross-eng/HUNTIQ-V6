/**
 * Orders Service - API client for orders module
 * Phase 10+ - Connected to real backend
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export class OrdersService {
  static async getHealth() {
    try {
      const response = await fetch(`${API_URL}/api/v1/orders/`);
      if (!response.ok) return { status: 'unavailable' };
      return response.json();
    } catch {
      return { status: 'unavailable' };
    }
  }

  static async getStats() {
    try {
      const response = await fetch(`${API_URL}/api/v1/orders/stats`);
      if (!response.ok) return { total: 0, pending: 0, revenue: 0 };
      return response.json();
    } catch {
      return { total: 0, pending: 0, revenue: 0 };
    }
  }

  static async getOrders(options = {}) {
    try {
      const params = new URLSearchParams();
      if (options.status) params.append('status', options.status);
      if (options.sale_mode) params.append('sale_mode', options.sale_mode);
      if (options.limit) params.append('limit', options.limit);
      
      const response = await fetch(`${API_URL}/api/v1/orders/?${params}`);
      if (!response.ok) return [];
      const data = await response.json();
      return Array.isArray(data) ? data : (data.orders || []);
    } catch {
      return [];
    }
  }

  static async getOrder(orderId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/orders/${orderId}`);
      if (!response.ok) return null;
      return response.json();
    } catch {
      return null;
    }
  }

  static async createOrder(orderData) {
    try {
      const response = await fetch(`${API_URL}/api/v1/orders/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderData)
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Order creation failed');
      }
      return response.json();
    } catch (error) {
      throw error;
    }
  }

  static async updateOrderStatus(orderId, status, notes = '') {
    try {
      const response = await fetch(`${API_URL}/api/v1/orders/${orderId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status, notes })
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async cancelOrder(orderId, reason, refund_requested = false) {
    try {
      const response = await fetch(`${API_URL}/api/v1/orders/${orderId}/cancel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason, refund_requested })
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  // Commissions
  static async getCommissions(options = {}) {
    try {
      const params = new URLSearchParams();
      if (options.status) params.append('status', options.status);
      if (options.commission_type) params.append('commission_type', options.commission_type);
      if (options.limit) params.append('limit', options.limit);
      
      const response = await fetch(`${API_URL}/api/v1/orders/commissions/?${params}`);
      if (!response.ok) return [];
      return response.json();
    } catch {
      return [];
    }
  }

  static async markCommissionPaid(commissionId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/orders/commissions/${commissionId}/pay`, {
        method: 'PUT'
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }
}

export default OrdersService;
