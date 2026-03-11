/**
 * TutorialService - V5-ULTIME Monétisation
 * =========================================
 * 
 * Service pour les tutoriels dynamiques.
 */

const API_BASE = process.env.REACT_APP_BACKEND_URL;

export const TutorialService = {
  /**
   * Lister les tutoriels
   */
  async listTutorials(type = null, feature = null, tier = 'free') {
    try {
      const params = new URLSearchParams({ tier });
      if (type) params.append('type', type);
      if (feature) params.append('feature', feature);

      const response = await fetch(`${API_BASE}/api/v1/tutorials/list?${params}`);
      if (!response.ok) throw new Error('Failed to fetch tutorials');
      return await response.json();
    } catch (error) {
      console.error('TutorialService.listTutorials error:', error);
      return { success: false, tutorials: [] };
    }
  },

  /**
   * Récupérer un tutoriel spécifique
   */
  async getTutorial(tutorialId) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/tutorials/${tutorialId}`);
      if (!response.ok) throw new Error('Failed to fetch tutorial');
      return await response.json();
    } catch (error) {
      console.error('TutorialService.getTutorial error:', error);
      return { success: false };
    }
  },

  /**
   * Récupérer la progression utilisateur
   */
  async getProgress(userId) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/tutorials/progress/${userId}`);
      if (!response.ok) throw new Error('Failed to fetch progress');
      return await response.json();
    } catch (error) {
      console.error('TutorialService.getProgress error:', error);
      return { success: false };
    }
  },

  /**
   * Mettre à jour la progression
   */
  async updateProgress(userId, tutorialId, stepCompleted = null, completed = false) {
    try {
      const params = new URLSearchParams();
      if (stepCompleted !== null) params.append('step_completed', stepCompleted);
      if (completed) params.append('completed', 'true');

      const response = await fetch(
        `${API_BASE}/api/v1/tutorials/progress/${userId}/${tutorialId}?${params}`,
        { method: 'POST' }
      );
      if (!response.ok) throw new Error('Failed to update progress');
      return await response.json();
    } catch (error) {
      console.error('TutorialService.updateProgress error:', error);
      return { success: false };
    }
  },

  /**
   * Ignorer un tutoriel
   */
  async skipTutorial(userId, tutorialId) {
    try {
      const response = await fetch(
        `${API_BASE}/api/v1/tutorials/skip/${userId}/${tutorialId}`,
        { method: 'POST' }
      );
      if (!response.ok) throw new Error('Failed to skip tutorial');
      return await response.json();
    } catch (error) {
      console.error('TutorialService.skipTutorial error:', error);
      return { success: false };
    }
  },

  /**
   * Récupérer un tutoriel contextuel
   */
  async getContextualTutorial(feature, userId = null) {
    try {
      const params = userId ? `?user_id=${userId}` : '';
      const response = await fetch(`${API_BASE}/api/v1/tutorials/contextual/${feature}${params}`);
      if (!response.ok) throw new Error('Failed to fetch contextual tutorial');
      return await response.json();
    } catch (error) {
      console.error('TutorialService.getContextualTutorial error:', error);
      return { success: false, tutorial: null };
    }
  },

  /**
   * Récupérer le tip du jour
   */
  async getDailyTip() {
    try {
      const response = await fetch(`${API_BASE}/api/v1/tutorials/tip/daily`);
      if (!response.ok) throw new Error('Failed to fetch daily tip');
      return await response.json();
    } catch (error) {
      console.error('TutorialService.getDailyTip error:', error);
      return { success: false, tip: null };
    }
  }
};

export default TutorialService;
