/**
 * RealEstateService - Frontend service for real estate API
 * Phase 11-15: Module Immobilier
 */

const API = process.env.REACT_APP_BACKEND_URL;

export class RealEstateService {
  /**
   * Import a new property
   */
  static async importProperty(propertyData) {
    const response = await fetch(`${API}/api/realestate/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(propertyData)
    });
    return response.json();
  }

  /**
   * Get list of properties with filters
   */
  static async getProperties(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const response = await fetch(`${API}/api/realestate/list?${queryString}`);
    return response.json();
  }

  /**
   * Get single property by ID
   */
  static async getProperty(propertyId) {
    const response = await fetch(`${API}/api/realestate/${propertyId}`);
    return response.json();
  }

  /**
   * Get nearby properties
   */
  static async getNearbyProperties(lat, lng, radiusKm = 10, limit = 20) {
    const params = new URLSearchParams({
      lat: lat.toString(),
      lng: lng.toString(),
      radius_km: radiusKm.toString(),
      limit: limit.toString()
    });
    const response = await fetch(`${API}/api/realestate/nearby?${params}`);
    return response.json();
  }
}

export default RealEstateService;
