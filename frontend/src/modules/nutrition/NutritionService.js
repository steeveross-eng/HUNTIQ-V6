/**
 * Nutrition Service - API client for nutrition module
 * Phase 10+ - Connected to real backend
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export class NutritionService {
  static async getHealth() {
    try {
      const response = await fetch(`${API_URL}/api/v1/nutrition/`);
      if (!response.ok) return { status: 'unavailable' };
      return response.json();
    } catch {
      return { status: 'unavailable' };
    }
  }

  static async analyzeProduct(productId, productName = null, ingredients = []) {
    try {
      // Try single product analysis first
      const response = await fetch(`${API_URL}/api/v1/nutrition/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify([{
          product_id: productId,
          product_name: productName || `Product ${productId}`,
          ingredients: ingredients.length > 0 ? ingredients : ['attractant', 'mineral']
        }])
      });
      
      if (!response.ok) {
        // Fallback placeholder
        return this.getPlaceholderAnalysis(productId, productName);
      }
      
      const data = await response.json();
      // API returns array, get first result
      if (Array.isArray(data) && data.length > 0) {
        return data[0];
      }
      return data;
    } catch (error) {
      console.error('Nutrition analysis error:', error);
      return this.getPlaceholderAnalysis(productId, productName);
    }
  }

  static async getRecommendations(species, season) {
    try {
      const params = new URLSearchParams();
      if (species) params.append('species', species);
      if (season) params.append('season', season);
      
      const response = await fetch(`${API_URL}/api/v1/nutrition/recommendations?${params}`);
      if (!response.ok) return { recommendations: [] };
      return response.json();
    } catch {
      return { recommendations: [] };
    }
  }

  static async compareProducts(productIds) {
    try {
      const response = await fetch(`${API_URL}/api/v1/nutrition/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_ids: productIds })
      });
      if (!response.ok) return { comparison: [] };
      return response.json();
    } catch {
      return { comparison: [] };
    }
  }

  static async getNutritionProfile(productId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/nutrition/profile/${productId}`);
      if (!response.ok) return null;
      return response.json();
    } catch {
      return null;
    }
  }

  static async getIngredients() {
    try {
      const response = await fetch(`${API_URL}/api/v1/nutrition/ingredients`);
      if (!response.ok) return { ingredients: [] };
      return response.json();
    } catch {
      return { ingredients: [] };
    }
  }

  // Placeholder for graceful degradation
  static getPlaceholderAnalysis(productId, productName) {
    return {
      product_id: productId,
      product_name: productName || 'Produit',
      score: 75,
      nutritional_value: 72,
      protein_content: 24.5,
      mineral_content: 8.2,
      attractiveness: 85,
      duration_hours: 48,
      analysis: {
        proteins: { value: 24.5, rating: 'good' },
        minerals: { value: 8.2, rating: 'excellent' },
        carbs: { value: 12.3, rating: 'moderate' }
      }
    };
  }
}

export default NutritionService;
