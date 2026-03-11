/**
 * TripService - Frontend service for hunting trip management
 * Phase P4+ - Real Data Logging
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

class TripServiceClass {
  constructor() {
    this.baseUrl = `${API_URL}/api/v1/trips`;
  }

  /**
   * Get auth headers
   */
  getHeaders() {
    const token = localStorage.getItem('auth_token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  /**
   * Create a new hunting trip
   */
  async createTrip(tripData) {
    try {
      const response = await fetch(`${this.baseUrl}/create`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(tripData)
      });
      return await response.json();
    } catch (error) {
      console.error('[TripService] Create trip error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Start a hunting trip
   */
  async startTrip(tripId, weatherData = {}) {
    try {
      const response = await fetch(`${this.baseUrl}/start`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({
          trip_id: tripId,
          ...weatherData
        })
      });
      return await response.json();
    } catch (error) {
      console.error('[TripService] Start trip error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * End a hunting trip
   */
  async endTrip(tripId, success = false, notes = '') {
    try {
      const response = await fetch(`${this.baseUrl}/end`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({
          trip_id: tripId,
          success,
          notes
        })
      });
      return await response.json();
    } catch (error) {
      console.error('[TripService] End trip error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Get trip details
   */
  async getTrip(tripId) {
    try {
      const response = await fetch(`${this.baseUrl}/${tripId}`, {
        headers: this.getHeaders()
      });
      return await response.json();
    } catch (error) {
      console.error('[TripService] Get trip error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * List all trips
   */
  async listTrips(status = null, limit = 50) {
    try {
      const params = new URLSearchParams();
      if (status) params.append('status', status);
      params.append('limit', limit);

      const response = await fetch(`${this.baseUrl}/list?${params}`, {
        headers: this.getHeaders()
      });
      return await response.json();
    } catch (error) {
      console.error('[TripService] List trips error:', error);
      return [];
    }
  }

  /**
   * Get active trip
   */
  async getActiveTrip() {
    try {
      const response = await fetch(`${this.baseUrl}/active`, {
        headers: this.getHeaders()
      });
      return await response.json();
    } catch (error) {
      console.error('[TripService] Get active trip error:', error);
      return { active: false, trip: null };
    }
  }

  /**
   * Log an observation
   */
  async logObservation(observationData) {
    try {
      const response = await fetch(`${this.baseUrl}/observations`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(observationData)
      });
      return await response.json();
    } catch (error) {
      console.error('[TripService] Log observation error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * List observations
   */
  async listObservations(tripId = null, waypointId = null, species = null, limit = 100) {
    try {
      const params = new URLSearchParams();
      if (tripId) params.append('trip_id', tripId);
      if (waypointId) params.append('waypoint_id', waypointId);
      if (species) params.append('species', species);
      params.append('limit', limit);

      const response = await fetch(`${this.baseUrl}/observations/list?${params}`, {
        headers: this.getHeaders()
      });
      return await response.json();
    } catch (error) {
      console.error('[TripService] List observations error:', error);
      return [];
    }
  }

  /**
   * Log a waypoint visit
   */
  async logVisit(visitData) {
    try {
      const response = await fetch(`${this.baseUrl}/visits`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(visitData)
      });
      return await response.json();
    } catch (error) {
      console.error('[TripService] Log visit error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * End a waypoint visit
   */
  async endVisit(visitId, success = false, notes = '') {
    try {
      const params = new URLSearchParams();
      params.append('success', success);
      if (notes) params.append('notes', notes);

      const response = await fetch(`${this.baseUrl}/visits/${visitId}/end?${params}`, {
        method: 'POST',
        headers: this.getHeaders()
      });
      return await response.json();
    } catch (error) {
      console.error('[TripService] End visit error:', error);
      return { success: false, error: error.message };
    }
  }

  /**
   * List waypoint visits
   */
  async listVisits(waypointId = null, limit = 50) {
    try {
      const params = new URLSearchParams();
      if (waypointId) params.append('waypoint_id', waypointId);
      params.append('limit', limit);

      const response = await fetch(`${this.baseUrl}/visits/list?${params}`, {
        headers: this.getHeaders()
      });
      return await response.json();
    } catch (error) {
      console.error('[TripService] List visits error:', error);
      return [];
    }
  }

  /**
   * Get user statistics
   */
  async getStatistics() {
    try {
      const response = await fetch(`${this.baseUrl}/statistics`, {
        headers: this.getHeaders()
      });
      return await response.json();
    } catch (error) {
      console.error('[TripService] Get statistics error:', error);
      return { success: false, statistics: null };
    }
  }

  /**
   * Get waypoint statistics
   */
  async getWaypointStatistics(waypointId) {
    try {
      const response = await fetch(`${this.baseUrl}/statistics/waypoint/${waypointId}`, {
        headers: this.getHeaders()
      });
      return await response.json();
    } catch (error) {
      console.error('[TripService] Get waypoint statistics error:', error);
      return { success: false, statistics: null };
    }
  }
}

// Export singleton instance
export const TripService = new TripServiceClass();
export default TripService;
