/**
 * UpsellService - V5-ULTIME Monétisation
 * =======================================
 * 
 * Service pour les popups de vente incitative.
 */

const API_BASE = process.env.REACT_APP_BACKEND_URL;

export const UpsellService = {
  /**
   * Déclencher un upsell
   */
  async triggerUpsell(userId, triggerType, context = {}) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/upsell/trigger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          trigger_type: triggerType,
          context
        })
      });
      if (!response.ok) throw new Error('Failed to trigger upsell');
      return await response.json();
    } catch (error) {
      console.error('UpsellService.triggerUpsell error:', error);
      return { success: false, upsell: null };
    }
  },

  /**
   * Enregistrer un clic
   */
  async recordClick(userId, campaignName) {
    try {
      const response = await fetch(
        `${API_BASE}/api/v1/upsell/campaigns/click?user_id=${userId}&campaign_name=${campaignName}`,
        { method: 'POST' }
      );
      return await response.json();
    } catch (error) {
      console.error('UpsellService.recordClick error:', error);
      return { success: false };
    }
  },

  /**
   * Ignorer une campagne
   */
  async dismissCampaign(userId, campaignName) {
    try {
      const response = await fetch(
        `${API_BASE}/api/v1/upsell/campaigns/dismiss?user_id=${userId}&campaign_name=${campaignName}`,
        { method: 'POST' }
      );
      return await response.json();
    } catch (error) {
      console.error('UpsellService.dismissCampaign error:', error);
      return { success: false };
    }
  },

  /**
   * Récupérer les analytics
   */
  async getAnalytics(days = 30) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/upsell/analytics?days=${days}`);
      if (!response.ok) throw new Error('Failed to fetch analytics');
      return await response.json();
    } catch (error) {
      console.error('UpsellService.getAnalytics error:', error);
      return { success: false };
    }
  }
};

export default UpsellService;
