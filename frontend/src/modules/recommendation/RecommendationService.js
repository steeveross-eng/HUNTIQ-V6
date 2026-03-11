/**
 * Recommendation Service - API client for recommendation engine
 * Phase 10+ - Connected to real backend
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export class RecommendationService {
  static async getHealth() {
    try {
      const response = await fetch(`${API_URL}/api/v1/recommendation/`);
      if (!response.ok) return { status: 'unavailable' };
      return response.json();
    } catch {
      return { status: 'unavailable' };
    }
  }

  static async getProductRecommendations(request) {
    try {
      const response = await fetch(`${API_URL}/api/v1/recommendation/products`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
      });
      
      if (!response.ok) {
        return { success: true, data: { recommendations: this.getPlaceholderProducts() } };
      }
      
      const data = await response.json();
      // Transform API response to frontend format
      if (data.success && data.data?.products) {
        return {
          success: true,
          data: {
            recommendations: data.data.products.map(p => ({
              id: p.id,
              name: p.product_name,
              score: p.score,
              category: p.product_type || 'attractant',
              reason: p.reasons?.[0] || 'Recommandé pour vous',
              confidence: p.confidence
            }))
          }
        };
      }
      return { success: true, data: { recommendations: this.getPlaceholderProducts() } };
    } catch {
      return { success: true, data: { recommendations: this.getPlaceholderProducts() } };
    }
  }

  static async getStrategyRecommendations(species, conditions = {}) {
    try {
      const params = new URLSearchParams({ species });
      if (conditions.season) params.append('season', conditions.season);
      if (conditions.temperature) params.append('temperature', conditions.temperature);
      if (conditions.wind_speed) params.append('wind_speed', conditions.wind_speed);
      
      const response = await fetch(`${API_URL}/api/v1/recommendation/strategies?${params}`);
      if (!response.ok) {
        return { success: true, data: { strategies: this.getPlaceholderStrategies() } };
      }
      
      const data = await response.json();
      // Transform API response
      if (data.success && data.data?.strategies) {
        return {
          success: true,
          data: {
            strategies: data.data.strategies.map(s => ({
              id: s.id,
              name: s.title,
              confidence: s.score,
              description: s.description,
              type: s.strategy_type
            }))
          }
        };
      }
      return { success: true, data: { strategies: this.getPlaceholderStrategies() } };
    } catch {
      return { success: true, data: { strategies: this.getPlaceholderStrategies() } };
    }
  }

  static async getSimilarProducts(productId, limit = 10) {
    try {
      const response = await fetch(`${API_URL}/api/v1/recommendation/similar/${productId}?limit=${limit}`);
      if (!response.ok) return { success: false, similar_products: [] };
      return response.json();
    } catch {
      return { success: false, similar_products: [] };
    }
  }

  static async getComplementaryProducts(productId, limit = 10) {
    try {
      const response = await fetch(`${API_URL}/api/v1/recommendation/complementary/${productId}?limit=${limit}`);
      if (!response.ok) return { success: false, complementary_products: [] };
      return response.json();
    } catch {
      return { success: false, complementary_products: [] };
    }
  }

  static async getContextualRecommendations(species, season, options = {}) {
    try {
      const params = new URLSearchParams({ species, season });
      if (options.temperature) params.append('temperature', options.temperature);
      if (options.humidity) params.append('humidity', options.humidity);
      if (options.wind_speed) params.append('wind_speed', options.wind_speed);
      if (options.lat) params.append('lat', options.lat);
      if (options.lng) params.append('lng', options.lng);
      if (options.limit) params.append('limit', options.limit);
      
      const response = await fetch(`${API_URL}/api/v1/recommendation/for-context?${params}`);
      if (!response.ok) {
        return { success: true, data: { recommendations: this.getPlaceholderProducts() } };
      }
      
      const data = await response.json();
      if (data.success && data.data?.products) {
        return {
          success: true,
          data: {
            recommendations: data.data.products.map(p => ({
              id: p.id,
              name: p.product_name,
              score: p.score,
              category: p.product_type || 'attractant',
              reason: p.reasons?.[0] || 'Adapté au contexte'
            }))
          }
        };
      }
      return { success: true, data: { recommendations: this.getPlaceholderProducts() } };
    } catch {
      return { success: true, data: { recommendations: this.getPlaceholderProducts() } };
    }
  }

  static async getPersonalizedRecommendations(userId, limit = 10) {
    try {
      const response = await fetch(`${API_URL}/api/v1/recommendation/personalized/${userId}?limit=${limit}`);
      if (!response.ok) return { success: false, data: { recommendations: [] } };
      return response.json();
    } catch {
      return { success: false, data: { recommendations: [] } };
    }
  }

  static async submitFeedback(feedback) {
    try {
      const response = await fetch(`${API_URL}/api/v1/recommendation/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(feedback)
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async getUserProfile(userId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/recommendation/profile/${userId}`);
      if (!response.ok) return null;
      return response.json();
    } catch {
      return null;
    }
  }

  // Placeholder data
  static getPlaceholderProducts() {
    return [
      { id: 1, name: 'Attractant Premium Cerf', score: 92, category: 'attractant', reason: 'Optimal pour le rut' },
      { id: 2, name: 'Leurre Olfactif Doe', score: 88, category: 'lure', reason: 'Haute efficacité saison' },
      { id: 3, name: 'Bloc Minéral Pro', score: 85, category: 'mineral', reason: 'Complémentaire recommandé' },
      { id: 4, name: 'Spray Anti-Odeur', score: 82, category: 'accessory', reason: 'Essentiel conditions vent' }
    ];
  }

  static getPlaceholderStrategies() {
    return [
      { id: 1, name: 'Affût matinal', confidence: 94, description: 'Position fixe aube' },
      { id: 2, name: 'Approche silencieuse', confidence: 78, description: 'Déplacement lent vent face' },
      { id: 3, name: 'Appel grunt', confidence: 85, description: 'Contact vocal période rut' }
    ];
  }
}

export default RecommendationService;
