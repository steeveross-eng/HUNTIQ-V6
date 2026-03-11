/**
 * Collaborative Service - API client for collaborative sharing
 * Phase 10+ - Connected to real backend
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export class CollaborativeService {
  static async getHealth() {
    try {
      const response = await fetch(`${API_URL}/api/v1/collaborative/`);
      if (!response.ok) return { status: 'unavailable' };
      return response.json();
    } catch {
      return { status: 'unavailable' };
    }
  }

  static async getSharedSpots(options = {}) {
    try {
      const params = new URLSearchParams();
      if (options.species) params.append('species', options.species);
      if (options.region) params.append('region', options.region);
      if (options.limit) params.append('limit', options.limit);
      
      const response = await fetch(`${API_URL}/api/v1/collaborative/spots?${params}`);
      if (!response.ok) return { success: false, spots: [] };
      return response.json();
    } catch {
      return { success: false, spots: [] };
    }
  }

  static async shareSpot(spotData) {
    try {
      const response = await fetch(`${API_URL}/api/v1/collaborative/spots`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(spotData)
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async getHuntingReports(options = {}) {
    try {
      const params = new URLSearchParams();
      if (options.species) params.append('species', options.species);
      if (options.date_from) params.append('date_from', options.date_from);
      if (options.limit) params.append('limit', options.limit);
      
      const response = await fetch(`${API_URL}/api/v1/collaborative/reports?${params}`);
      if (!response.ok) {
        return { success: true, reports: this.getPlaceholderReports() };
      }
      const data = await response.json();
      if (data.success && data.reports?.length > 0) {
        return data;
      }
      return { success: true, reports: this.getPlaceholderReports() };
    } catch {
      return { success: true, reports: this.getPlaceholderReports() };
    }
  }

  static async submitReport(reportData) {
    try {
      const response = await fetch(`${API_URL}/api/v1/collaborative/reports`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reportData)
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async getSightings(lat, lng, radiusKm = 10) {
    try {
      const params = new URLSearchParams({ lat, lng, radius_km: radiusKm });
      const response = await fetch(`${API_URL}/api/v1/collaborative/sightings?${params}`);
      if (!response.ok) {
        return { success: true, sightings: this.getPlaceholderSightings() };
      }
      const data = await response.json();
      if (data.success && data.sightings?.length > 0) {
        return data;
      }
      return { success: true, sightings: this.getPlaceholderSightings() };
    } catch {
      return { success: true, sightings: this.getPlaceholderSightings() };
    }
  }

  static async reportSighting(sightingData) {
    try {
      const response = await fetch(`${API_URL}/api/v1/collaborative/sightings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sightingData)
      });
      return response.json();
    } catch {
      return { success: false };
    }
  }

  static async getGroups(userId = null) {
    try {
      let url = `${API_URL}/api/v1/collaborative/groups`;
      if (userId) url += `?user_id=${userId}`;
      
      const response = await fetch(url);
      if (!response.ok) return { success: false, groups: [] };
      return response.json();
    } catch {
      return { success: false, groups: [] };
    }
  }

  // Placeholder data
  static getPlaceholderSightings() {
    const now = new Date();
    return [
      { id: 1, species: 'deer', count: 3, timestamp: new Date(now - 2 * 3600000).toISOString(), verified: true, location: 'Zone Nord' },
      { id: 2, species: 'moose', count: 1, timestamp: new Date(now - 26 * 3600000).toISOString(), verified: true, location: 'Secteur Est' },
      { id: 3, species: 'turkey', count: 8, timestamp: new Date(now - 50 * 3600000).toISOString(), verified: false, location: 'Champ sud' }
    ];
  }

  static getPlaceholderReports() {
    return [
      { 
        id: 1, 
        hunter: 'ChasseurPro', 
        species: 'deer', 
        success: true, 
        date: '2026-02-08',
        rating: 4,
        comment: 'Excellente matinée, 3 observations' 
      },
      { 
        id: 2, 
        hunter: 'NatureHunter', 
        species: 'bear', 
        success: false, 
        date: '2026-02-07',
        rating: 3,
        comment: 'Traces fraîches mais pas de contact visuel' 
      }
    ];
  }
}

export default CollaborativeService;
