/**
 * Cart Service - API client for cart module
 * Phase 10+ - Connected to real backend
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export class CartService {
  static async getHealth() {
    try {
      const response = await fetch(`${API_URL}/api/v1/cart/`);
      if (!response.ok) return { status: 'unavailable' };
      return response.json();
    } catch {
      return { status: 'unavailable' };
    }
  }

  static async getStats() {
    try {
      const response = await fetch(`${API_URL}/api/v1/cart/stats`);
      if (!response.ok) return { total_carts: 0, active_carts: 0 };
      return response.json();
    } catch {
      return { total_carts: 0, active_carts: 0 };
    }
  }

  static async getCart(sessionId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/cart/session/${sessionId}`);
      if (!response.ok) return { items: [], total: 0 };
      const data = await response.json();
      return {
        items: data.items || [],
        total: data.total || 0,
        session_id: sessionId
      };
    } catch {
      return { items: [], total: 0 };
    }
  }

  static async addItem(sessionId, productId, quantity = 1) {
    try {
      const response = await fetch(`${API_URL}/api/v1/cart/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, product_id: productId, quantity })
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async updateItem(itemId, quantity) {
    try {
      const response = await fetch(`${API_URL}/api/v1/cart/${itemId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity })
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async removeItem(itemId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/cart/${itemId}`, {
        method: 'DELETE'
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async clearCart(sessionId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/cart/session/${sessionId}/clear`, {
        method: 'DELETE'
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  // Helper methods
  static getSessionId() {
    let sessionId = localStorage.getItem('cart_session_id');
    if (!sessionId) {
      sessionId = 'cart_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('cart_session_id', sessionId);
    }
    return sessionId;
  }

  static calculateTotal(items) {
    return items.reduce((total, item) => {
      const price = item.product?.price || item.price || 0;
      return total + (price * item.quantity);
    }, 0);
  }

  static getItemCount(items) {
    return items.reduce((count, item) => count + item.quantity, 0);
  }
}

export default CartService;
