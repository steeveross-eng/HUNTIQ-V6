/**
 * WaypointScoringService - API client for WQS and Success Forecast
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export const WaypointScoringService = {
  /**
   * Get WQS for all waypoints
   */
  async getAllWQS() {
    try {
      const response = await fetch(`${API_URL}/api/v1/waypoint-scoring/wqs`);
      if (!response.ok) throw new Error('Failed to fetch WQS');
      return await response.json();
    } catch (error) {
      console.error('WQS error:', error);
      return [];
    }
  },

  /**
   * Get WQS for a specific waypoint
   */
  async getWaypointWQS(waypointId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/waypoint-scoring/wqs/${waypointId}`);
      if (!response.ok) throw new Error('Failed to fetch WQS');
      return await response.json();
    } catch (error) {
      console.error('WQS error:', error);
      return null;
    }
  },

  /**
   * Get heatmap data
   */
  async getHeatmapData() {
    try {
      const response = await fetch(`${API_URL}/api/v1/waypoint-scoring/heatmap`);
      if (!response.ok) throw new Error('Failed to fetch heatmap');
      return await response.json();
    } catch (error) {
      console.error('Heatmap error:', error);
      return [];
    }
  },

  /**
   * Get success forecast
   */
  async getSuccessForecast(params = {}) {
    try {
      const { species = 'deer', weather, hour, temperature } = params;
      let url = `${API_URL}/api/v1/waypoint-scoring/forecast/quick?species=${species}`;
      if (weather) url += `&weather=${encodeURIComponent(weather)}`;
      if (hour !== undefined) url += `&hour=${hour}`;
      if (temperature !== undefined) url += `&temperature=${temperature}`;
      
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch forecast');
      return await response.json();
    } catch (error) {
      console.error('Forecast error:', error);
      return null;
    }
  },

  /**
   * Get AI recommendations
   */
  async getRecommendations(species = 'deer', weather = null) {
    try {
      let url = `${API_URL}/api/v1/waypoint-scoring/recommendations?species=${species}`;
      if (weather) url += `&weather=${encodeURIComponent(weather)}`;
      
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch recommendations');
      return await response.json();
    } catch (error) {
      console.error('Recommendations error:', error);
      return [];
    }
  },

  /**
   * Get waypoint ranking
   */
  async getRanking(species = null, weather = null) {
    try {
      let url = `${API_URL}/api/v1/waypoint-scoring/ranking`;
      const params = [];
      if (species) params.push(`species=${species}`);
      if (weather) params.push(`weather=${encodeURIComponent(weather)}`);
      if (params.length) url += '?' + params.join('&');
      
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch ranking');
      return await response.json();
    } catch (error) {
      console.error('Ranking error:', error);
      return { rankings: [] };
    }
  },

  /**
   * Seed demo data
   */
  async seedDemoData() {
    try {
      const response = await fetch(`${API_URL}/api/v1/waypoint-scoring/seed-visits`, {
        method: 'POST'
      });
      if (!response.ok) throw new Error('Failed to seed data');
      return await response.json();
    } catch (error) {
      console.error('Seed error:', error);
      return { success: false };
    }
  }
};

export default WaypointScoringService;
