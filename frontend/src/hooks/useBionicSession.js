/**
 * useBionicSession Hook — BIONIC V8 + BCE-MAX x4.1
 * Persistance complète de la session utilisateur.
 * 
 * Restaure automatiquement:
 * - Position (lat, lng, zoom)
 * - Type de gibier (espèce sélectionnée)
 * - Couches actives
 * - Waypoint sélectionné
 * - Contexte complet de la session précédente
 * 
 * BCE-MAX x4.1 COMPLIANCE:
 * - Aucune perte de contexte
 * - Restauration automatique au chargement
 * - Persistance immédiate des changements
 */

import { useState, useCallback, useMemo, useEffect, useRef } from 'react';

// Clé de stockage pour la session complète
const FULL_SESSION_KEY = 'bionic_full_session_v8';

/**
 * Structure de la session BIONIC
 * @typedef {Object} BionicSession
 * @property {Object} position - { lat, lng, zoom }
 * @property {string} species - Espèce sélectionnée (orignal, chevreuil, ours_noir)
 * @property {Object} layers - État des couches {layerId: boolean}
 * @property {Object} selectedWaypoint - Waypoint sélectionné
 * @property {Array} waypoints - Liste des waypoints
 * @property {string} season - Saison biologique
 * @property {number} timestamp - Timestamp de sauvegarde
 */

/**
 * Charge la session complète depuis localStorage
 * @returns {BionicSession|null}
 */
function loadFullSession() {
  try {
    const saved = localStorage.getItem(FULL_SESSION_KEY);
    if (saved) {
      const session = JSON.parse(saved);
      // Vérifier validité (max 30 jours)
      const maxAge = 30 * 24 * 60 * 60 * 1000;
      if (session.timestamp && Date.now() - session.timestamp < maxAge) {
        console.log('[BCE-MAX x4.1] Session complète restaurée:', {
          position: session.position,
          species: session.species,
          layersCount: session.layers ? Object.keys(session.layers).filter(k => session.layers[k]).length : 0,
          waypoint: session.selectedWaypoint?.name,
        });
        return session;
      }
    }
  } catch (e) {
    console.warn('[BCE-MAX x4.1] Erreur chargement session:', e);
  }
  return null;
}

/**
 * Sauvegarde la session complète
 * @param {BionicSession} session
 */
function saveFullSession(session) {
  try {
    localStorage.setItem(FULL_SESSION_KEY, JSON.stringify({
      ...session,
      timestamp: Date.now(),
      version: 'bce_max_4.1',
    }));
  } catch (e) {
    console.warn('[BCE-MAX x4.1] Erreur sauvegarde session:', e);
  }
}

/**
 * Hook de gestion de session BIONIC complète
 */
const useBionicSession = () => {
  // Charger la session précédente au montage
  const previousSession = useMemo(() => loadFullSession(), []);
  const isInitializedRef = useRef(false);
  
  // État de la session courante
  const [session, setSession] = useState(() => ({
    position: previousSession?.position || { lat: 46.8, lng: -71.2, zoom: 13 },
    species: previousSession?.species || 'orignal',
    layers: previousSession?.layers || {},
    selectedWaypoint: previousSession?.selectedWaypoint || null,
    waypoints: previousSession?.waypoints || [],
    season: previousSession?.season || 'automne',
    timestamp: previousSession?.timestamp || Date.now(),
  }));
  
  // Sauvegarder automatiquement quand la session change
  useEffect(() => {
    if (isInitializedRef.current) {
      saveFullSession(session);
    } else {
      isInitializedRef.current = true;
    }
  }, [session]);
  
  /**
   * Met à jour la position de la carte
   */
  const updatePosition = useCallback((lat, lng, zoom) => {
    setSession(prev => ({
      ...prev,
      position: { lat, lng, zoom },
    }));
  }, []);
  
  /**
   * Met à jour l'espèce sélectionnée
   */
  const updateSpecies = useCallback((species) => {
    setSession(prev => ({
      ...prev,
      species,
    }));
  }, []);
  
  /**
   * Met à jour les couches visibles
   */
  const updateLayers = useCallback((layers) => {
    setSession(prev => ({
      ...prev,
      layers,
    }));
  }, []);
  
  /**
   * Met à jour le waypoint sélectionné
   */
  const updateSelectedWaypoint = useCallback((waypoint) => {
    setSession(prev => ({
      ...prev,
      selectedWaypoint: waypoint,
    }));
  }, []);
  
  /**
   * Met à jour la liste des waypoints
   */
  const updateWaypoints = useCallback((waypoints) => {
    setSession(prev => ({
      ...prev,
      waypoints,
    }));
  }, []);
  
  /**
   * Met à jour la saison
   */
  const updateSeason = useCallback((season) => {
    setSession(prev => ({
      ...prev,
      season,
    }));
  }, []);
  
  /**
   * Réinitialise la session
   */
  const resetSession = useCallback(() => {
    const newSession = {
      position: { lat: 46.8, lng: -71.2, zoom: 13 },
      species: 'orignal',
      layers: {},
      selectedWaypoint: null,
      waypoints: [],
      season: 'automne',
      timestamp: Date.now(),
    };
    setSession(newSession);
    saveFullSession(newSession);
  }, []);
  
  /**
   * Vérifie si une session précédente existe
   */
  const hasPreviousSession = useMemo(() => !!previousSession, [previousSession]);
  
  /**
   * Restaure explicitement la session précédente
   */
  const restorePreviousSession = useCallback(() => {
    const prev = loadFullSession();
    if (prev) {
      setSession(prev);
      return true;
    }
    return false;
  }, []);
  
  return {
    // Session courante
    session,
    
    // Accesseurs rapides
    position: session.position,
    species: session.species,
    layers: session.layers,
    selectedWaypoint: session.selectedWaypoint,
    waypoints: session.waypoints,
    season: session.season,
    
    // Actions
    updatePosition,
    updateSpecies,
    updateLayers,
    updateSelectedWaypoint,
    updateWaypoints,
    updateSeason,
    resetSession,
    restorePreviousSession,
    
    // État
    hasPreviousSession,
    previousSession,
  };
};

export default useBionicSession;
export { loadFullSession, saveFullSession };
