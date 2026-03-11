/**
 * FreemiumService - V5-ULTIME Monétisation
 * =========================================
 * 
 * Service pour la gestion freemium et quotas.
 */

const API_BASE = process.env.REACT_APP_BACKEND_URL;

export const FreemiumService = {
  /**
   * Récupérer l'abonnement utilisateur
   */
  async getSubscription(userId) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/freemium/subscription/${userId}`);
      if (!response.ok) throw new Error('Failed to fetch subscription');
      return await response.json();
    } catch (error) {
      console.error('FreemiumService.getSubscription error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Vérifier l'accès à une fonctionnalité
   */
  async checkAccess(userId, feature) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/freemium/check-access`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, feature })
      });
      if (!response.ok) throw new Error('Failed to check access');
      return await response.json();
    } catch (error) {
      console.error('FreemiumService.checkAccess error:', error);
      return { success: false, can_access: false, error: error.message };
    }
  },

  /**
   * Récupérer l'utilisation d'un quota
   */
  async getQuota(userId, feature) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/freemium/quota/${userId}/${feature}`);
      if (!response.ok) throw new Error('Failed to fetch quota');
      return await response.json();
    } catch (error) {
      console.error('FreemiumService.getQuota error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Incrémenter un quota
   */
  async incrementQuota(userId, feature, amount = 1) {
    try {
      const response = await fetch(
        `${API_BASE}/api/v1/freemium/quota/${userId}/${feature}/increment?amount=${amount}`,
        { method: 'POST' }
      );
      if (!response.ok) throw new Error('Failed to increment quota');
      return await response.json();
    } catch (error) {
      console.error('FreemiumService.incrementQuota error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Récupérer la comparaison des tiers
   */
  async compareTiers() {
    try {
      const response = await fetch(`${API_BASE}/api/v1/freemium/tiers/compare`);
      if (!response.ok) throw new Error('Failed to compare tiers');
      return await response.json();
    } catch (error) {
      console.error('FreemiumService.compareTiers error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Récupérer les tarifs
   */
  async getPricing() {
    try {
      const response = await fetch(`${API_BASE}/api/v1/freemium/pricing`);
      if (!response.ok) throw new Error('Failed to fetch pricing');
      return await response.json();
    } catch (error) {
      console.error('FreemiumService.getPricing error:', error);
      return { success: false, error: error.message };
    }
  }
};

export default FreemiumService;
