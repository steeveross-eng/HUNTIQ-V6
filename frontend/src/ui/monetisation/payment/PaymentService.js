/**
 * PaymentService - V5-ULTIME Monétisation
 * ========================================
 * 
 * Service isolé pour l'intégration Stripe.
 * Aucun import croisé avec d'autres modules.
 */

const API_BASE = process.env.REACT_APP_BACKEND_URL;

export const PaymentService = {
  /**
   * Récupérer les packages disponibles
   */
  async getPackages() {
    try {
      const response = await fetch(`${API_BASE}/api/v1/payments/packages`);
      if (!response.ok) throw new Error('Failed to fetch packages');
      return await response.json();
    } catch (error) {
      console.error('PaymentService.getPackages error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Créer une session de checkout Stripe
   */
  async createCheckoutSession(packageId, userId) {
    try {
      const originUrl = window.location.origin;
      
      const response = await fetch(`${API_BASE}/api/v1/payments/checkout/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          package_id: packageId,
          user_id: userId,
          origin_url: originUrl
        })
      });
      
      if (!response.ok) throw new Error('Failed to create checkout session');
      return await response.json();
    } catch (error) {
      console.error('PaymentService.createCheckoutSession error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Vérifier le statut d'un paiement
   */
  async getCheckoutStatus(sessionId) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/payments/checkout/status/${sessionId}`);
      if (!response.ok) throw new Error('Failed to get checkout status');
      return await response.json();
    } catch (error) {
      console.error('PaymentService.getCheckoutStatus error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Récupérer l'historique des transactions
   */
  async getTransactions(userId, limit = 20) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/payments/transactions/${userId}?limit=${limit}`);
      if (!response.ok) throw new Error('Failed to fetch transactions');
      return await response.json();
    } catch (error) {
      console.error('PaymentService.getTransactions error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Polling du statut de paiement
   */
  async pollPaymentStatus(sessionId, onStatusUpdate, maxAttempts = 10) {
    let attempts = 0;
    const pollInterval = 2000;

    const poll = async () => {
      if (attempts >= maxAttempts) {
        onStatusUpdate({ status: 'timeout', message: 'Vérification expirée' });
        return;
      }

      attempts++;
      const result = await this.getCheckoutStatus(sessionId);

      if (result.success) {
        if (result.payment_status === 'paid') {
          onStatusUpdate({ status: 'success', data: result });
          return;
        } else if (result.status === 'expired') {
          onStatusUpdate({ status: 'expired', data: result });
          return;
        }
      }

      onStatusUpdate({ status: 'pending', attempt: attempts });
      setTimeout(poll, pollInterval);
    };

    poll();
  }
};

export default PaymentService;
