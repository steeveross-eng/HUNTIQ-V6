/**
 * Territory Service - API client for territory management
 * Phase 10+ - Connected to real backend
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export class TerritoryService {
  static async getHealth() {
    try {
      const response = await fetch(`${API_URL}/api/v1/territory/`);
      if (!response.ok) return { status: 'unavailable' };
      return response.json();
    } catch {
      return { status: 'unavailable' };
    }
  }

  static async getTerritories(type = null) {
    try {
      let url = `${API_URL}/api/v1/territory/list`;
      if (type) url += `?type=${type}`;
      
      const response = await fetch(url);
      if (!response.ok) {
        return { territories: this.getPlaceholderTerritories() };
      }
      
      const data = await response.json();
      // If empty, use placeholders
      if (data.success && data.territories?.length > 0) {
        return data;
      }
      return { territories: this.getPlaceholderTerritories() };
    } catch {
      return { territories: this.getPlaceholderTerritories() };
    }
  }

  static async getTerritory(territoryId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/territory/${territoryId}`);
      if (!response.ok) return null;
      return response.json();
    } catch {
      return null;
    }
  }

  static async searchBySpecies(species) {
    try {
      const response = await fetch(`${API_URL}/api/v1/territory/search/species/${species}`);
      if (!response.ok) return { territories: [] };
      return response.json();
    } catch {
      return { territories: [] };
    }
  }

  static async getLandRentals(options = {}) {
    try {
      const params = new URLSearchParams();
      if (options.type) params.append('type', options.type);
      if (options.available !== undefined) params.append('available', options.available);
      
      const response = await fetch(`${API_URL}/api/v1/territory/rentals?${params}`);
      if (!response.ok) return { rentals: [] };
      return response.json();
    } catch {
      return { rentals: [] };
    }
  }

  static async getAccessPermits(territoryId) {
    try {
      const response = await fetch(`${API_URL}/api/v1/territory/${territoryId}/permits`);
      if (!response.ok) return { permits: [] };
      return response.json();
    } catch {
      return { permits: [] };
    }
  }

  // Placeholder territories
  static getPlaceholderTerritories() {
    return [
      { 
        id: 'zec-1', 
        name: 'ZEC Batiscan-Neilson', 
        type: 'zec', 
        region: 'Mauricie',
        species: ['deer', 'moose', 'bear'],
        area_km2: 1245,
        available: true
      },
      { 
        id: 'pourv-1', 
        name: 'Pourvoirie du Lac Blanc', 
        type: 'pourvoirie', 
        region: 'Laurentides',
        species: ['deer', 'bear', 'turkey'],
        area_km2: 320,
        available: true
      },
      { 
        id: 'private-1', 
        name: 'Terre Privée Beauce', 
        type: 'private', 
        region: 'Chaudière-Appalaches',
        species: ['deer', 'turkey'],
        area_km2: 85,
        available: false
      }
    ];
  }

  static getTerritoryTypeInfo(type) {
    const types = {
      zec: { label: 'ZEC', iconName: 'Tent', color: 'emerald' },
      pourvoirie: { label: 'Pourvoirie', iconName: 'Home', color: 'blue' },
      public: { label: 'Terre publique', iconName: 'TreePine', color: 'green' },
      reserve: { label: 'Réserve faunique', iconName: 'Shield', color: 'amber' },
      private: { label: 'Terre privée', iconName: 'Lock', color: 'purple' }
    };
    return types[type] || { label: type, iconName: 'MapPin', color: 'slate' };
  }
}

export default TerritoryService;
