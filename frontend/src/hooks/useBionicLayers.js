/**
 * useBionicLayers Hook
 * Gère l'état des couches BIONIC (on/off)
 */

import { useState, useCallback, useMemo } from 'react';
import { BIONIC_LAYERS } from '@/core/bionic';

const useBionicLayers = (initialState = {}) => {
  // État initial : couches ESSENTIELLES activées, reste désactivé
  // P0 FIX: Seules les couches essentielles activées par défaut
  // Corridors désactivé pour éviter zones rouges dans le fleuve
  const ESSENTIAL_LAYERS = ['habitats', 'alimentation', 'repos'];
  const defaultState = useMemo(() => {
    const state = {};
    BIONIC_LAYERS.forEach(layer => {
      state[layer.id] = initialState[layer.id] ?? ESSENTIAL_LAYERS.includes(layer.id);
    });
    return state;
  }, []);
  
  const [layersVisible, setLayersVisible] = useState(defaultState);
  
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
   * Active toutes les couches
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
    
    // Vérification
    isLayerVisible: (layerId) => layersVisible[layerId] ?? false
  };
};

export default useBionicLayers;
