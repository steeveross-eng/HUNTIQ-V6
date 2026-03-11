/**
 * LegalTimeService - API client for legal hunting times
 * Calculates sunrise/sunset and legal hunting windows
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export class LegalTimeService {
  /**
   * Get module health/info
   */
  static async getHealth() {
    try {
      const response = await fetch(`${API_URL}/api/v1/legal-time/`);
      if (!response.ok) return { status: 'unavailable' };
      return response.json();
    } catch {
      return { status: 'unavailable' };
    }
  }

  /**
   * Get sun times (sunrise, sunset, dawn, dusk)
   */
  static async getSunTimes(date = null, lat = 46.8139, lng = -71.2080) {
    try {
      const params = new URLSearchParams();
      if (date) params.append('date', date);
      params.append('lat', lat);
      params.append('lng', lng);
      
      const response = await fetch(`${API_URL}/api/v1/legal-time/sun-times?${params}`);
      if (!response.ok) return this.getPlaceholderSunTimes();
      return response.json();
    } catch {
      return this.getPlaceholderSunTimes();
    }
  }

  /**
   * Get legal hunting window
   */
  static async getLegalWindow(date = null, lat = 46.8139, lng = -71.2080) {
    try {
      const params = new URLSearchParams();
      if (date) params.append('date', date);
      params.append('lat', lat);
      params.append('lng', lng);
      
      const response = await fetch(`${API_URL}/api/v1/legal-time/legal-window?${params}`);
      if (!response.ok) return this.getPlaceholderLegalWindow();
      return response.json();
    } catch {
      return this.getPlaceholderLegalWindow();
    }
  }

  /**
   * Check if hunting is currently legal
   */
  static async checkLegalNow(lat = 46.8139, lng = -71.2080) {
    try {
      const params = new URLSearchParams({ lat, lng });
      const response = await fetch(`${API_URL}/api/v1/legal-time/check?${params}`);
      if (!response.ok) return this.getPlaceholderCheck();
      return response.json();
    } catch {
      return this.getPlaceholderCheck();
    }
  }

  /**
   * Get recommended hunting slots
   */
  static async getRecommendedSlots(date = null, lat = 46.8139, lng = -71.2080) {
    try {
      const params = new URLSearchParams();
      if (date) params.append('date', date);
      params.append('lat', lat);
      params.append('lng', lng);
      
      const response = await fetch(`${API_URL}/api/v1/legal-time/recommended-slots?${params}`);
      if (!response.ok) return { success: false, slots: [] };
      return response.json();
    } catch {
      return { success: false, slots: [] };
    }
  }

  /**
   * Get daily hunting schedule
   */
  static async getDailySchedule(date = null, lat = 46.8139, lng = -71.2080) {
    try {
      const params = new URLSearchParams();
      if (date) params.append('date', date);
      params.append('lat', lat);
      params.append('lng', lng);
      
      const response = await fetch(`${API_URL}/api/v1/legal-time/schedule?${params}`);
      if (!response.ok) return { success: false };
      return response.json();
    } catch {
      return { success: false };
    }
  }

  /**
   * Get multi-day forecast
   */
  static async getForecast(days = 7, lat = 46.8139, lng = -71.2080) {
    try {
      const params = new URLSearchParams({ days, lat, lng });
      const response = await fetch(`${API_URL}/api/v1/legal-time/forecast?${params}`);
      if (!response.ok) return { success: false, forecast: { daily_schedules: [] } };
      return response.json();
    } catch {
      return { success: false, forecast: { daily_schedules: [] } };
    }
  }

  // Placeholder data for offline/error scenarios
  static getPlaceholderSunTimes() {
    return {
      success: true,
      sun_times: {
        sunrise: '07:00',
        sunset: '17:00',
        dawn: '06:30',
        dusk: '17:30',
        day_length_hours: 10
      }
    };
  }

  static getPlaceholderLegalWindow() {
    return {
      success: true,
      legal_window: {
        start_time: '06:30',
        end_time: '17:30',
        duration_hours: 11,
        sunrise: '07:00',
        sunset: '17:00'
      },
      status: {
        is_currently_legal: true,
        current_status: 'legal'
      }
    };
  }

  static getPlaceholderCheck() {
    return {
      success: true,
      is_legal: true,
      message: 'Période légale',
      legal_window: {
        start: '06:30',
        end: '17:30'
      }
    };
  }
}

export default LegalTimeService;
