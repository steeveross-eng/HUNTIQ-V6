/**
 * WaypointService - API Service for Waypoint Management
 * ======================================================
 * 
 * Service pour la création et gestion des waypoints.
 * Architecture LEGO V5 - Module métier isolé.
 * 
 * @module modules/map_interaction/services
 */

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

export class WaypointService {
  /**
   * Create a new waypoint
   * @param {Object} data - Waypoint data
   * @param {number} data.lat - Latitude
   * @param {number} data.lng - Longitude
   * @param {string} data.name - Waypoint name
   * @param {string} data.timestamp - ISO timestamp
   * @param {string} data.source - Creation source
   * @param {string} data.user_id - User ID
   * @returns {Promise<Object>} Created waypoint
   */
  static async createWaypoint(data) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/waypoints/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          lat: data.lat,
          lng: data.lng,
          name: data.name || `Waypoint ${new Date().toLocaleDateString('fr-CA')}`,
          timestamp: data.timestamp || new Date().toISOString(),
          source: data.source || 'user_double_click',
          user_id: data.user_id
        }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Erreur serveur' }));
        throw new Error(error.detail || 'Erreur lors de la création du waypoint');
      }

      return await response.json();
    } catch (error) {
      console.error('WaypointService.createWaypoint error:', error);
      throw error;
    }
  }

  /**
   * Get waypoints for a user
   * @param {string} userId - User ID
   * @param {Object} options - Query options
   * @returns {Promise<Array>} List of waypoints
   */
  static async getWaypoints(userId, options = {}) {
    try {
      const params = new URLSearchParams();
      if (userId) params.append('user_id', userId);
      if (options.limit) params.append('limit', options.limit);
      if (options.source) params.append('source', options.source);

      const response = await fetch(`${API_BASE}/api/v1/waypoints?${params}`);

      if (!response.ok) {
        throw new Error('Erreur lors de la récupération des waypoints');
      }

      return await response.json();
    } catch (error) {
      console.error('WaypointService.getWaypoints error:', error);
      throw error;
    }
  }

  /**
   * Delete a waypoint
   * @param {string} waypointId - Waypoint ID
   * @returns {Promise<Object>} Deletion result
   */
  static async deleteWaypoint(waypointId) {
    try {
      const response = await fetch(`${API_BASE}/api/v1/waypoints/${waypointId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la suppression du waypoint');
      }

      return await response.json();
    } catch (error) {
      console.error('WaypointService.deleteWaypoint error:', error);
      throw error;
    }
  }
}

export default WaypointService;
