/**
 * useBionicLayers Hook — BCE-MAX x4.1
 * Gere l'etat des couches BIONIC.
 * 
 * IMPORTANT: Ce hook ne fait AUCUNE persistance localStorage.
 * La persistance est geree EXCLUSIVEMENT par useBionicSession.
 * Ce hook accepte un initialState (depuis la session) et gere le toggle.
 */

import { useState, useCallback, useMemo } from 'react';
import { BIONIC_LAYERS } from '@/core/bionic';

// Couches essentielles activees par defaut quand aucune session n'existe
// ALIMENTATION-V2: Sites permanents SUPPRIMÉS définitivement
// 'alimentation' et 'salines' retirés — contrôlés exclusivement par ALIMENTATION-V2
const ESSENTIAL_LAYERS = [
  'habitats', 'repos', 'rut',
  'trajets', 'corridors', 'ensoleillement', 'peuplements',
  'affuts', 'pentes', 'orientation', 'altitude'
];

// Couches interdites (STEEVE-MAX: anciens sites V1 éliminés — ALIMENTATION-V2 seul contrôle)
const BANNED_LAYERS = new Set(['alimentation', 'salines', 'alimentation_sec']);

const useBionicLayers = (initialState = null) => {
  // Etat initial: session restauree OU toutes les couches essentielles
  const defaultState = useMemo(() => {
    const state = {};
    
    // Si initialState fourni par la session, l'utiliser exactement
    if (initialState && typeof initialState === 'object' && Object.keys(initialState).length > 0) {
      BIONIC_LAYERS.forEach(layer => {
        // ALIMENTATION-V2: Forcer alimentation/salines à false
        state[layer.id] = BANNED_LAYERS.has(layer.id) ? false : (initialState[layer.id] ?? true);
      });
      console.log('[BCE-MAX] Couches restaurees depuis session:', Object.keys(state).filter(k => state[k]).length);
      return state;
    }

    // Sinon, activer TOUTES les couches essentielles par defaut
    BIONIC_LAYERS.forEach(layer => {
      state[layer.id] = ESSENTIAL_LAYERS.includes(layer.id);
    });
    console.log('[BCE-MAX] Couches par defaut:', Object.keys(state).filter(k => state[k]).length);
    return state;
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
  // Note: intentionnellement [] car initialState est lu une seule fois au mount

  const [layersVisible, setLayersVisible] = useState(defaultState);

  const toggleLayer = useCallback((layerId) => {
    setLayersVisible(prev => ({ ...prev, [layerId]: !prev[layerId] }));
  }, []);

  const setLayerVisibility = useCallback((layerId, visible) => {
    setLayersVisible(prev => ({ ...prev, [layerId]: visible }));
  }, []);

  const showAllLayers = useCallback(() => {
    const allVisible = {};
    BIONIC_LAYERS.forEach(layer => { allVisible[layer.id] = true; });
    setLayersVisible(allVisible);
  }, []);

  const hideAllLayers = useCallback(() => {
    const allHidden = {};
    BIONIC_LAYERS.forEach(layer => { allHidden[layer.id] = false; });
    setLayersVisible(allHidden);
  }, []);

  const showLayerGroup = useCallback((groupIds) => {
    setLayersVisible(prev => {
      const newState = { ...prev };
      groupIds.forEach(id => { newState[id] = true; });
      return newState;
    });
  }, []);

  const resetLayers = useCallback(() => {
    setLayersVisible(defaultState);
  }, [defaultState]);

  const visibleLayers = useMemo(() => {
    return BIONIC_LAYERS.filter(layer => layersVisible[layer.id]);
  }, [layersVisible]);

  const activeCount = useMemo(() => {
    return Object.values(layersVisible).filter(Boolean).length;
  }, [layersVisible]);

  return {
    layersVisible,
    visibleLayers,
    activeCount,
    allLayers: BIONIC_LAYERS,
    toggleLayer,
    setLayerVisibility,
    showAllLayers,
    hideAllLayers,
    showLayerGroup,
    resetLayers,
    isLayerVisible: (layerId) => layersVisible[layerId] ?? false,
  };
};

export default useBionicLayers;
