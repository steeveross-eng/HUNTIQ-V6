/**
 * OnboardingService - V5-ULTIME Monétisation
 * ==========================================
 * 
 * Service pour le parcours d'accueil.
 */

const API_BASE = process.env.REACT_APP_BACKEND_URL;

export const OnboardingService = {
  /**
   * Récupérer le statut d'onboarding
   */
  async getStatus(userId) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/onboarding/status/${userId}`);
      if (!response.ok) throw new Error('Failed to fetch onboarding status');
      return await response.json();
    } catch (error) {
      console.error('OnboardingService.getStatus error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Soumettre une étape
   */
  async submitStep(userId, step, data) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/onboarding/steps/${userId}/${step}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      if (!response.ok) throw new Error('Failed to submit step');
      return await response.json();
    } catch (error) {
      console.error('OnboardingService.submitStep error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Récupérer la configuration d'une étape
   */
  async getStepConfig(step) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/onboarding/steps/${step}`);
      if (!response.ok) throw new Error('Failed to fetch step config');
      return await response.json();
    } catch (error) {
      console.error('OnboardingService.getStepConfig error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Récupérer toutes les étapes
   */
  async getAllSteps() {
    try {
      const response = await fetch(`${API_BASE}/api/v1/onboarding/steps`);
      if (!response.ok) throw new Error('Failed to fetch steps');
      return await response.json();
    } catch (error) {
      console.error('OnboardingService.getAllSteps error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Ignorer l'onboarding
   */
  async skip(userId) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/onboarding/skip/${userId}`, {
        method: 'POST'
      });
      if (!response.ok) throw new Error('Failed to skip onboarding');
      return await response.json();
    } catch (error) {
      console.error('OnboardingService.skip error:', error);
      return { success: false, error: error.message };
    }
  }
};

export default OnboardingService;
