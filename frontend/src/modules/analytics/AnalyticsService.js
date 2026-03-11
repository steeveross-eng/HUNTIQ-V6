/**
 * Analytics Service - API client for analytics endpoints
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export const AnalyticsService = {
  /**
   * Get complete dashboard data
   */
  async getDashboard(timeRange = 'all') {
    try {
      const response = await fetch(`${API_URL}/api/v1/analytics/dashboard?time_range=${timeRange}`);
      if (!response.ok) throw new Error('Failed to fetch dashboard');
      return await response.json();
    } catch (error) {
      console.error('Analytics dashboard error:', error);
      return this.getFallbackDashboard();
    }
  },

  /**
   * Get overview statistics
   */
  async getOverview(timeRange = 'all') {
    try {
      const response = await fetch(`${API_URL}/api/v1/analytics/overview?time_range=${timeRange}`);
      if (!response.ok) throw new Error('Failed to fetch overview');
      return await response.json();
    } catch (error) {
      console.error('Analytics overview error:', error);
      return null;
    }
  },

  /**
   * Get species breakdown
   */
  async getSpeciesBreakdown(timeRange = 'all') {
    try {
      const response = await fetch(`${API_URL}/api/v1/analytics/species?time_range=${timeRange}`);
      if (!response.ok) throw new Error('Failed to fetch species');
      return await response.json();
    } catch (error) {
      console.error('Analytics species error:', error);
      return [];
    }
  },

  /**
   * Get weather analysis
   */
  async getWeatherAnalysis() {
    try {
      const response = await fetch(`${API_URL}/api/v1/analytics/weather`);
      if (!response.ok) throw new Error('Failed to fetch weather analysis');
      return await response.json();
    } catch (error) {
      console.error('Analytics weather error:', error);
      return [];
    }
  },

  /**
   * Get optimal times analysis
   */
  async getOptimalTimes() {
    try {
      const response = await fetch(`${API_URL}/api/v1/analytics/optimal-times`);
      if (!response.ok) throw new Error('Failed to fetch optimal times');
      return await response.json();
    } catch (error) {
      console.error('Analytics times error:', error);
      return [];
    }
  },

  /**
   * Get monthly trends
   */
  async getMonthlyTrends(months = 12) {
    try {
      const response = await fetch(`${API_URL}/api/v1/analytics/trends?months=${months}`);
      if (!response.ok) throw new Error('Failed to fetch trends');
      return await response.json();
    } catch (error) {
      console.error('Analytics trends error:', error);
      return [];
    }
  },

  /**
   * Get hunting trips list
   */
  async getTrips(timeRange = 'all', species = null, limit = 50) {
    try {
      let url = `${API_URL}/api/v1/analytics/trips?time_range=${timeRange}&limit=${limit}`;
      if (species) url += `&species=${species}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch trips');
      return await response.json();
    } catch (error) {
      console.error('Analytics trips error:', error);
      return [];
    }
  },

  /**
   * Create a new hunting trip
   */
  async createTrip(tripData) {
    try {
      const response = await fetch(`${API_URL}/api/v1/analytics/trips`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(tripData)
      });
      if (!response.ok) throw new Error('Failed to create trip');
      return await response.json();
    } catch (error) {
      console.error('Create trip error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Delete a hunting trip
   */
  async deleteTrip(tripId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/analytics/trips/${tripId}`, {
        method: 'DELETE'
      });
      if (!response.ok) throw new Error('Failed to delete trip');
      return await response.json();
    } catch (error) {
      console.error('Delete trip error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Seed demo data
   */
  async seedDemoData() {
    try {
      const response = await fetch(`${API_URL}/api/v1/analytics/seed`, {
        method: 'POST'
      });
      if (!response.ok) throw new Error('Failed to seed data');
      return await response.json();
    } catch (error) {
      console.error('Seed data error:', error);
      return { success: false, error: error.message };
    }
  },

  /**
   * Fallback dashboard data
   */
  getFallbackDashboard() {
    return {
      overview: {
        total_trips: 0,
        successful_trips: 0,
        success_rate: 0,
        total_hours: 0,
        total_observations: 0,
        avg_trip_duration: 0,
        most_active_species: null,
        best_success_species: null
      },
      species_breakdown: [],
      weather_analysis: [],
      optimal_times: [],
      monthly_trends: [],
      recent_trips: []
    };
  }
};

export default AnalyticsService;
