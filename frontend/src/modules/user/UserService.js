/**
 * User Service - API client for user module
 * Phase 9 - Business Modules
 */

const API_URL = process.env.REACT_APP_BACKEND_URL;

export class UserService {
  static async getHealth() {
    const response = await fetch(`${API_URL}/api/v1/user/`);
    return response.json();
  }

  static async register(userData) {
    const response = await fetch(`${API_URL}/api/v1/user/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }
    return response.json();
  }

  static async login(email, password) {
    const response = await fetch(`${API_URL}/api/v1/user/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }
    return response.json();
  }

  static async logout(token) {
    const response = await fetch(`${API_URL}/api/v1/user/logout`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  }

  static async getCurrentUser(token) {
    const response = await fetch(`${API_URL}/api/v1/user/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!response.ok) return null;
    return response.json();
  }

  static async updateCurrentUser(token, updateData) {
    const response = await fetch(`${API_URL}/api/v1/user/me`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(updateData)
    });
    return response.json();
  }

  static async getProfile(userId) {
    const response = await fetch(`${API_URL}/api/v1/user/profile/${userId}`);
    if (!response.ok) return null;
    return response.json();
  }

  static async updateProfile(token, profileData) {
    const response = await fetch(`${API_URL}/api/v1/user/profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(profileData)
    });
    return response.json();
  }

  static async getPreferences(token) {
    const response = await fetch(`${API_URL}/api/v1/user/preferences`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!response.ok) return null;
    return response.json();
  }

  static async updatePreferences(token, prefsData) {
    const response = await fetch(`${API_URL}/api/v1/user/preferences`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(prefsData)
    });
    return response.json();
  }

  static async getActivity(token, limit = 50) {
    const response = await fetch(`${API_URL}/api/v1/user/activity?limit=${limit}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!response.ok) return { activity: [] };
    return response.json();
  }

  static async getRoles() {
    const response = await fetch(`${API_URL}/api/v1/user/roles`);
    return response.json();
  }

  // Admin endpoints
  static async adminListUsers(token, skip = 0, limit = 50, role = null) {
    const params = new URLSearchParams({ skip, limit });
    if (role) params.append('role', role);
    
    const response = await fetch(`${API_URL}/api/v1/user/admin/list?${params}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  }

  static async adminUpdateRole(token, userId, newRole) {
    const response = await fetch(`${API_URL}/api/v1/user/admin/${userId}/role?new_role=${newRole}`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  }

  static async adminSuspendUser(token, userId, reason = '') {
    const response = await fetch(`${API_URL}/api/v1/user/admin/${userId}/suspend?reason=${encodeURIComponent(reason)}`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  }
}

export default UserService;
