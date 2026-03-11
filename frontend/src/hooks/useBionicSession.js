/**
 * useBionicSession Hook — BCE-MAX x4.1 — SOURCE DE VERITE UNIQUE
 * 
 * ANTI-REGRESSION: Ce hook est la SEULE source de persistance de session.
 * Aucun autre hook, aucun autre composant ne doit utiliser localStorage
 * pour la persistance de session BIONIC.
 * 
 * Restaure automatiquement:
 * - Position (lat, lng, zoom)
 * - Espece selectionnee
 * - Toutes les couches actives
 * - Waypoint selectionne (ID)
 * - Classification toggles
 * - Saison biologique
 * - Onglet actif
 * - Options visuelles (corridors, vent, exclusions)
 */

import { useState, useCallback, useMemo, useEffect, useRef } from 'react';

const SESSION_KEY = 'bionic_session_bce_max_v4';
const MAX_AGE_MS = 30 * 24 * 60 * 60 * 1000; // 30 jours

/**
 * Charge la session complete depuis localStorage
 */
function loadSession() {
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    if (!raw) return null;
    const session = JSON.parse(raw);
    if (!session || typeof session !== 'object') return null;
    if (session.timestamp && Date.now() - session.timestamp > MAX_AGE_MS) return null;
    // Validation basique
    if (session.position) {
      if (session.position.lat < -90 || session.position.lat > 90) return null;
      if (session.position.lng < -180 || session.position.lng > 180) return null;
      session.position.zoom = Math.max(3, Math.min(18, session.position.zoom || 13));
    }
    console.log('[BCE-MAX x4.1] Session restauree:', {
      position: session.position,
      species: session.species,
      layersCount: session.layers ? Object.keys(session.layers).filter(k => session.layers[k]).length : 0,
      waypointId: session.waypointId,
    });
    return session;
  } catch (e) {
    console.warn('[BCE-MAX x4.1] Erreur chargement session:', e);
    return null;
  }
}

/**
 * Sauvegarde la session dans localStorage
 */
function saveSession(session) {
  try {
    localStorage.setItem(SESSION_KEY, JSON.stringify({
      ...session,
      timestamp: Date.now(),
      version: 'bce_max_4.1',
    }));
  } catch (e) {
    console.warn('[BCE-MAX x4.1] Erreur sauvegarde:', e);
  }
}

/**
 * Hook principal — source de verite unique pour la session BIONIC
 */
const useBionicSession = () => {
  const previousSession = useMemo(() => loadSession(), []);
  const isInitRef = useRef(false);
  const saveTimerRef = useRef(null);

  const [session, setSession] = useState(() => ({
    position: previousSession?.position || { lat: 46.8139, lng: -71.2080, zoom: 13 },
    species: previousSession?.species || 'tous',
    layers: previousSession?.layers || null, // null = use defaults
    waypointId: previousSession?.waypointId || null,
    biologicalSeason: previousSession?.biologicalSeason || null,
    activeTab: previousSession?.activeTab || 'carte',
    classificationToggles: previousSession?.classificationToggles || null,
    showCorridorsV1: previousSession?.showCorridorsV1 ?? false,
    showExclusionOverlay: previousSession?.showExclusionOverlay ?? false,
    showWindFlow: previousSession?.showWindFlow ?? false,
    windMode: previousSession?.windMode || 'arrows',
    timestamp: previousSession?.timestamp || Date.now(),
  }));

  // Sauvegarde debounced (300ms) quand la session change
  useEffect(() => {
    if (!isInitRef.current) {
      isInitRef.current = true;
      return;
    }
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(() => {
      saveSession(session);
    }, 300);
    return () => { if (saveTimerRef.current) clearTimeout(saveTimerRef.current); };
  }, [session]);

  const updatePosition = useCallback((lat, lng, zoom) => {
    setSession(prev => ({ ...prev, position: { lat, lng, zoom } }));
  }, []);

  const updateSpecies = useCallback((species) => {
    setSession(prev => ({ ...prev, species }));
  }, []);

  const updateLayers = useCallback((layers) => {
    setSession(prev => ({ ...prev, layers }));
  }, []);

  const updateWaypointId = useCallback((waypointId) => {
    setSession(prev => ({ ...prev, waypointId }));
  }, []);

  const updateBiologicalSeason = useCallback((biologicalSeason) => {
    setSession(prev => ({ ...prev, biologicalSeason }));
  }, []);

  const updateActiveTab = useCallback((activeTab) => {
    setSession(prev => ({ ...prev, activeTab }));
  }, []);

  const updateClassificationToggles = useCallback((classificationToggles) => {
    setSession(prev => ({ ...prev, classificationToggles }));
  }, []);

  const updateVisualOptions = useCallback((opts) => {
    setSession(prev => ({ ...prev, ...opts }));
  }, []);

  const hasPreviousSession = useMemo(() => !!previousSession, [previousSession]);

  return {
    session,
    // Accesseurs rapides
    position: session.position,
    species: session.species,
    layers: session.layers,
    waypointId: session.waypointId,
    biologicalSeason: session.biologicalSeason,
    activeTab: session.activeTab,
    classificationToggles: session.classificationToggles,
    showCorridorsV1: session.showCorridorsV1,
    showExclusionOverlay: session.showExclusionOverlay,
    showWindFlow: session.showWindFlow,
    windMode: session.windMode,
    // Actions
    updatePosition,
    updateSpecies,
    updateLayers,
    updateWaypointId,
    updateBiologicalSeason,
    updateActiveTab,
    updateClassificationToggles,
    updateVisualOptions,
    // Etat
    hasPreviousSession,
    previousSession,
  };
};

export default useBionicSession;
