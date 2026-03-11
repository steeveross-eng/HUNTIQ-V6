/**
 * Strategy Service - API client for strategy module
 * Phase 10+ - Connected to real backend
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export class StrategyService {
  static async getHealth() {
    try {
      const response = await fetch(`${API_URL}/api/v1/strategy/`);
      if (!response.ok) return { status: 'unavailable' };
      return response.json();
    } catch {
      return { status: 'unavailable' };
    }
  }

  static async getStrategies(species, season, weather = null) {
    try {
      const params = new URLSearchParams({ species });
      if (season) params.append('season', season);
      if (weather) params.append('weather', weather);
      
      const response = await fetch(`${API_URL}/api/v1/strategy/?${params}`);
      if (!response.ok) {
        return this.getPlaceholderStrategies(species, season);
      }
      return response.json();
    } catch {
      return this.getPlaceholderStrategies(species, season);
    }
  }

  static async generateStrategy(request) {
    try {
      const response = await fetch(`${API_URL}/api/v1/strategy/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
      });
      
      if (!response.ok) {
        return this.getPlaceholderGeneratedStrategy(request);
      }
      return response.json();
    } catch {
      return this.getPlaceholderGeneratedStrategy(request);
    }
  }

  static async getStandPlacements(lat, lng, species, wind_direction) {
    try {
      const params = new URLSearchParams({ lat, lng, species, wind_direction });
      const response = await fetch(`${API_URL}/api/v1/strategy/stands?${params}`);
      if (!response.ok) return { placements: [] };
      return response.json();
    } catch {
      return { placements: [] };
    }
  }

  static async getTimingRecommendations(species, date) {
    try {
      const params = new URLSearchParams({ species, date });
      const response = await fetch(`${API_URL}/api/v1/strategy/timing?${params}`);
      if (!response.ok) return { timings: [] };
      return response.json();
    } catch {
      return { timings: [] };
    }
  }

  // Placeholder for graceful degradation
  static getPlaceholderStrategies(species, season) {
    return {
      species,
      season,
      strategies: [
        {
          id: 1,
          name: 'Affût matinal',
          type: 'stand_hunting',
          confidence: 92,
          description: 'Position fixe en hauteur près des corridors de déplacement',
          timing: '05:30 - 09:00',
          equipment: ['Mirador', 'Appeau grunt', 'Attractant'],
          tips: ['Arrivez 45min avant l\'aube', 'Restez immobile', 'Vent de face']
        },
        {
          id: 2,
          name: 'Rattling agressif',
          type: 'calling',
          confidence: 78,
          description: 'Simulation de combat entre mâles pour attirer les dominants',
          timing: '08:00 - 10:00',
          equipment: ['Rattling antlers', 'Grunt call'],
          tips: ['Commencez doucement', 'Augmentez l\'intensité', 'Patience 20min']
        },
        {
          id: 3,
          name: 'Approche furtive',
          type: 'stalking',
          confidence: 65,
          description: 'Déplacement lent vers les zones d\'alimentation',
          timing: '15:00 - 17:00',
          equipment: ['Vêtements silencieux', 'Jumelles'],
          tips: ['Vent favorable obligatoire', '3 pas puis stop', 'Observer avant d\'avancer']
        }
      ]
    };
  }

  static getPlaceholderGeneratedStrategy(request) {
    return {
      success: true,
      strategy: {
        title: `Stratégie optimisée - ${request.species || 'Cerf'}`,
        summary: 'Stratégie personnalisée basée sur les conditions actuelles',
        phases: [
          { time: '05:30', action: 'Installation', details: 'Mise en place silencieuse' },
          { time: '06:00', action: 'Observation', details: 'Premiers mouvements attendus' },
          { time: '08:00', action: 'Appel', details: 'Grunt call discret' },
          { time: '11:00', action: 'Pause', details: 'Repos et collation' },
          { time: '16:00', action: 'Session soir', details: 'Reprise active' }
        ],
        success_probability: 75
      }
    };
  }
}

export default StrategyService;
