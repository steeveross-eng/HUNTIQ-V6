/**
 * ScoringUIService - V5-ULTIME
 * ============================
 */

const API_BASE = process.env.REACT_APP_BACKEND_URL;

export class ScoringUIService {
  static async getOverview() {
    try {
      const response = await fetch(`${API_BASE}/api/v1/scoring/overview`);
      return response.json();
    } catch (error) {
      console.error('Scoring API error:', error);
      return null;
    }
  }

  static async getProductScore(productId) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/scoring/product/${productId}`);
      return response.json();
    } catch (error) {
      return null;
    }
  }

  static async getWeatherImpact(lat, lng) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/scoring/weather-impact?lat=${lat}&lng=${lng}`);
      return response.json();
    } catch (error) {
      return null;
    }
  }

  static async compareProducts(productIds) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/scoring/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_ids: productIds })
      });
      return response.json();
    } catch (error) {
      return null;
    }
  }
}

export default ScoringUIService;
