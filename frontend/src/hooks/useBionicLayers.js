/**
 * useBionicLayers Hook — BIONIC V8 + BCE-MAX x4.1
 * Gère l'état des couches BIONIC avec persistance de session complète.
 * 
 * BCE-MAX x4.1 COMPLIANCE:
 * - Aucune couche ne peut disparaître
 * - Restauration automatique de la session précédente
 * - Toutes les couches actives sont persistées
 */

import { useState, useCallback, useMemo, useEffect } from 'react';
import { BIONIC_LAYERS } from '@/core/bionic';

// Clé de stockage pour la persistance de session
const SESSION_STORAGE_KEY = 'bionic_session_v8';

/**
 * Charge la session précédente depuis localStorage
 */
function loadPreviousSession() {
  try {
    const saved = localStorage.getItem(SESSION_STORAGE_KEY);
    if (saved) {
      const session = JSON.parse(saved);
      // Vérifier que la session est valide (moins de 7 jours)
      const maxAge = 7 * 24 * 60 * 60 * 1000;
      if (session.timestamp && Date.now() - session.timestamp < maxAge) {
        console.log('[BCE-MAX] Session précédente restaurée:', session);
        return session;
      }
    }
  } catch (e) {
    console.warn('[BCE-MAX] Erreur chargement session:', e);
  }
  return null;
}

/**
 * Sauvegarde la session courante dans localStorage
 */
function saveSession(session) {
  try {
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify({
      ...session,
      timestamp: Date.now(),
    }));
  } catch (e) {
    console.warn('[BCE-MAX] Erreur sauvegarde session:', e);
  }
}

const useBionicLayers = (initialState = {}) => {
  // Charger la session précédente
  const previousSession = useMemo(() => loadPreviousSession(), []);
  
  // TOUTES les couches BIONIC disponibles - BCE-MAX x4.1
  const ALL_LAYER_IDS = useMemo(() => BIONIC_LAYERS.map(l => l.id), []);
  
  // État initial : restaurer session OU activer TOUTES les couches essentielles
  const defaultState = useMemo(() => {
    const state = {};
    
    // Si session précédente existe, restaurer exactement
    if (previousSession?.layers) {
      BIONIC_LAYERS.forEach(layer => {
        state[layer.id] = previousSession.layers[layer.id] ?? true;
      });
      console.log('[BCE-MAX] Couches restaurées depuis session:', Object.keys(state).filter(k => state[k]).length);
      return state;
    }
    
    // Sinon, utiliser initialState ou activer toutes les couches essentielles
    // BCE-MAX x4.1: TOUTES les couches écologiques activées par défaut
    const ESSENTIAL_LAYERS = [
      'habitats', 'alimentation', 'repos', 'rut', 
      'trajets', 'corridors', 'ensoleillement', 'peuplements',
      'salines', 'affuts', 'pentes', 'orientation', 'altitude'
    ];
    
    BIONIC_LAYERS.forEach(layer => {
      // Priorité: initialState > session > essential
      state[layer.id] = initialState[layer.id] ?? ESSENTIAL_LAYERS.includes(layer.id);
    });
    
    return state;
  }, [previousSession, initialState]);
  
  const [layersVisible, setLayersVisible] = useState(defaultState);
  
  // Sauvegarder automatiquement quand les couches changent
  useEffect(() => {
    const activeCount = Object.values(layersVisible).filter(Boolean).length;
    if (activeCount > 0) {
      saveSession({
        layers: layersVisible,
        activeCount,
        version: 'bce_max_4.1',
      });
    }
  }, [layersVisible]);
  
  /**
   * Toggle une couche spécifique
   */
  const toggleLayer = useCallback((layerId) => {
    setLayersVisible(prev => ({
      ...prev,
      [layerId]: !prev[layerId]
    }));
  }, []);
  
  /**
   * Définit la visibilité d'une couche
   */
  const setLayerVisibility = useCallback((layerId, visible) => {
    setLayersVisible(prev => ({
      ...prev,
      [layerId]: visible
    }));
  }, []);
  
  /**
   * Active toutes les couches — BCE-MAX x4.1
   */
  const showAllLayers = useCallback(() => {
    const allVisible = {};
    BIONIC_LAYERS.forEach(layer => {
      allVisible[layer.id] = true;
    });
    setLayersVisible(allVisible);
  }, []);
  
  /**
   * Désactive toutes les couches
   */
  const hideAllLayers = useCallback(() => {
    const allHidden = {};
    BIONIC_LAYERS.forEach(layer => {
      allHidden[layer.id] = false;
    });
    setLayersVisible(allHidden);
  }, []);
  
  /**
   * Active un groupe de couches
   */
  const showLayerGroup = useCallback((groupIds) => {
    setLayersVisible(prev => {
      const newState = { ...prev };
      groupIds.forEach(id => {
        newState[id] = true;
      });
      return newState;
    });
  }, []);
  
  /**
   * Réinitialise aux valeurs par défaut
   */
  const resetLayers = useCallback(() => {
    setLayersVisible(defaultState);
  }, [defaultState]);
  
  /**
   * Restaure la session précédente — BCE-MAX x4.1
   */
  const restoreSession = useCallback(() => {
    const session = loadPreviousSession();
    if (session?.layers) {
      setLayersVisible(session.layers);
      return true;
    }
    return false;
  }, []);
  
  /**
   * Obtient les couches visibles
   */
  const visibleLayers = useMemo(() => {
    return BIONIC_LAYERS.filter(layer => layersVisible[layer.id]);
  }, [layersVisible]);
  
  /**
   * Compte des couches actives
   */
  const activeCount = useMemo(() => {
    return Object.values(layersVisible).filter(Boolean).length;
  }, [layersVisible]);
  
  return {
    // État
    layersVisible,
    visibleLayers,
    activeCount,
    
    // Liste complète des couches
    allLayers: BIONIC_LAYERS,
    
    // Actions
    toggleLayer,
    setLayerVisibility,
    showAllLayers,
    hideAllLayers,
    showLayerGroup,
    resetLayers,
    restoreSession,
    
    // Vérification
    isLayerVisible: (layerId) => layersVisible[layerId] ?? false,
    
    // BCE-MAX x4.1
    hasPreviousSession: !!previousSession,
  };
};

export default useBionicLayers;
