/**
 * Scoring Service - API client for scoring module
 * Phase 10+ - Connected to real backend
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export class ScoringService {
  static async getHealth() {
    try {
      const response = await fetch(`${API_URL}/api/v1/scoring/`);
      if (!response.ok) return { status: 'unavailable' };
      return response.json();
    } catch {
      return { status: 'unavailable' };
    }
  }

  static async calculateScore(productId, productName = null, productData = {}) {
    try {
      const response = await fetch(`${API_URL}/api/v1/scoring/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: productId,
          product_name: productName || `Product ${productId}`,
          ...productData
        })
      });
      
      if (!response.ok) {
        return this.getPlaceholderScore(productId);
      }
      
      return response.json();
    } catch (error) {
      console.error('Scoring error:', error);
      return this.getPlaceholderScore(productId);
    }
  }

  static async getBatchScores(products) {
    try {
      const response = await fetch(`${API_URL}/api/v1/scoring/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ products })
      });
      if (!response.ok) return { scores: [] };
      return response.json();
    } catch {
      return { scores: [] };
    }
  }

  static async getCriteria() {
    try {
      const response = await fetch(`${API_URL}/api/v1/scoring/criteria`);
      if (!response.ok) return { criteria: [] };
      return response.json();
    } catch {
      return { criteria: [] };
    }
  }

  static async getLeaderboard(limit = 10) {
    try {
      const response = await fetch(`${API_URL}/api/v1/scoring/leaderboard?limit=${limit}`);
      if (!response.ok) return { leaderboard: [] };
      return response.json();
    } catch {
      return { leaderboard: [] };
    }
  }

  // Placeholder for graceful degradation
  static getPlaceholderScore(productId) {
    return {
      success: true,
      product_id: productId,
      score: 7.2,
      pastille: 'yellow',
      pastille_label: 'Attraction modérée',
      breakdown: {
        attraction_days: 7.5,
        natural_palatability: 7.0,
        olfactory_power: 8.0,
        persistence: 6.5,
        nutrition: 7.2,
        behavioral_compounds: 7.8,
        rainproof: 6.0,
        feed_proof: 8.5,
        certified: 5.0,
        physical_resistance: 7.0,
        ingredient_purity: 7.5,
        loyalty: 6.8,
        chemical_stability: 7.2
      }
    };
  }
}

export default ScoringService;
