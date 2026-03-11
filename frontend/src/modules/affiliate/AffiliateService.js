/**
 * Affiliate Service - API client for affiliate module
 * Phase 10+ - Connected to real backend
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export class AffiliateService {
  static async getHealth() {
    try {
      const response = await fetch(`${API_URL}/api/v1/affiliate/`);
      if (!response.ok) return { status: 'unavailable' };
      return response.json();
    } catch {
      return { status: 'unavailable' };
    }
  }

  static async getStats() {
    try {
      const response = await fetch(`${API_URL}/api/v1/affiliate/stats`);
      if (!response.ok) {
        return { total_clicks: 0, total_sales: 0, total_commission: 0, conversion_rate: 0 };
      }
      return response.json();
    } catch {
      return { total_clicks: 0, total_sales: 0, total_commission: 0, conversion_rate: 0 };
    }
  }

  static async recordClick(productId, sessionId) {
    try {
      const params = new URLSearchParams({ product_id: productId, session_id: sessionId });
      const response = await fetch(`${API_URL}/api/v1/affiliate/click?${params}`, {
        method: 'POST'
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to record click');
      }
      return response.json();
    } catch (error) {
      throw error;
    }
  }

  static async getClicks(limit = 500) {
    try {
      const response = await fetch(`${API_URL}/api/v1/affiliate/clicks?limit=${limit}`);
      if (!response.ok) return [];
      return response.json();
    } catch {
      return [];
    }
  }

  static async confirmSale(clickId, commissionAmount) {
    try {
      const response = await fetch(`${API_URL}/api/v1/affiliate/confirm/${clickId}?commission_amount=${commissionAmount}`, {
        method: 'POST'
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  // Helper methods
  static getSessionId() {
    let sessionId = localStorage.getItem('affiliate_session_id');
    if (!sessionId) {
      sessionId = 'aff_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('affiliate_session_id', sessionId);
    }
    return sessionId;
  }

  static async trackAndRedirect(productId, affiliateUrl) {
    const sessionId = this.getSessionId();
    try {
      const result = await this.recordClick(productId, sessionId);
      if (result.success && result.redirect_url) {
        window.open(result.redirect_url, '_blank');
      } else if (affiliateUrl) {
        window.open(affiliateUrl, '_blank');
      }
      return result;
    } catch (error) {
      // Fallback to direct URL on error
      if (affiliateUrl) {
        window.open(affiliateUrl, '_blank');
      }
      throw error;
    }
  }
}

export default AffiliateService;
