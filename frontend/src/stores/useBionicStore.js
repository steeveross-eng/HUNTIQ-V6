/**
 * Zustand Store — État global BIONIC
 * ====================================
 * Synchronisation carte ↔ intelligence (bi-directionnelle).
 * Source de vérité pour: espèce, mois, localisation, registry.
 */
import { create } from 'zustand';

const API = process.env.REACT_APP_BACKEND_URL;

const useBionicStore = create((set, get) => ({
  // ── État partagé carte ↔ intelligence ──
  species: 'CHEVREUIL',
  month: new Date().getMonth() + 1,
  location: null, // { lat, lng }

  // ── Registry ──
  registry: null,
  registryLoading: false,

  // ── Intelligence data ──
  summary: null,
  forecast: null,
  plan: null,
  solunar: null,
  guidePro: null,
  loading: false,
  intelligenceWeather: null,

  // ── Actions ──
  setSpecies: (species) => set({ species }),
  setMonth: (month) => set({ month }),
  setLocation: (location) => set({ location }),

  fetchRegistry: async () => {
    if (get().registry) return;
    set({ registryLoading: true });
    try {
      const res = await fetch(`${API}/api/v3/engines/registry`);
      const data = await res.json();
      set({ registry: data, registryLoading: false });
    } catch {
      set({ registryLoading: false });
    }
  },

  fetchSummary: async () => {
    const { location, species, month } = get();
    if (!location) return;
    set({ loading: true });
    try {
      const params = new URLSearchParams({ lat: location.lat, lng: location.lng, species, month });
      const res = await fetch(`${API}/api/v3/intelligence/summary?${params}`);
      set({ summary: await res.json(), loading: false });
    } catch {
      set({ loading: false });
    }
  },

  fetchForecast: async () => {
    const { location, species } = get();
    if (!location) return;
    set({ loading: true });
    try {
      const params = new URLSearchParams({ lat: location.lat, lng: location.lng, species });
      const res = await fetch(`${API}/api/v3/intelligence/forecast?${params}`);
      set({ forecast: await res.json(), loading: false });
    } catch {
      set({ loading: false });
    }
  },

  fetchPlan: async () => {
    const { location, species, month } = get();
    if (!location) return;
    set({ loading: true });
    try {
      const params = new URLSearchParams({ lat: location.lat, lng: location.lng, species, month });
      const res = await fetch(`${API}/api/v3/intelligence/plan?${params}`);
      set({ plan: await res.json(), loading: false });
    } catch {
      set({ loading: false });
    }
  },

  fetchSolunar: async (date) => {
    const { location } = get();
    if (!location) return;
    try {
      const params = new URLSearchParams({ lat: location.lat, lng: location.lng });
      if (date) params.set('date', date);
      const res = await fetch(`${API}/api/v3/intelligence/solunar?${params}`);
      set({ solunar: await res.json() });
    } catch { /* silent */ }
  },

  fetchGuidePro: async (date) => {
    const { location, species, month } = get();
    if (!location) return;
    try {
      const params = new URLSearchParams({ lat: location.lat, lng: location.lng, species, month });
      if (date) params.set('date', date);
      const res = await fetch(`${API}/api/v3/intelligence/guide-pro?${params}`);
      const data = await res.json();
      set({ guidePro: data });
      if (data.weather_official) {
        set({ intelligenceWeather: data.weather_official });
      }
    } catch { /* silent */ }
  },

  setIntelligenceWeather: (weather) => set({ intelligenceWeather: weather }),

  fetchAll: async () => {
    const state = get();
    if (!state.location) return;
    await Promise.all([state.fetchSummary(), state.fetchForecast(), state.fetchPlan()]);
  },
}));

export default useBionicStore;
