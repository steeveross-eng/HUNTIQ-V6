/**
 * useMapType Hook
 * Gestion centralisée du type de carte et des options
 */

import { useState, useCallback, useMemo, useEffect } from 'react';
import { 
  MAP_TYPES, 
  MAP_CONFIGS, 
  DARK_OPTIMIZED_MAPS,
  getMapConfig,
  isMapDark,
  getZoneOpacity 
} from '@/config/mapSources';

const STORAGE_KEY = 'bionic_map_preferences';

/**
 * Hook pour gérer le type de carte et ses options
 * @param {string} defaultType - Type de carte par défaut
 * @returns {Object} - État et fonctions de gestion de la carte
 */
const useMapType = (defaultType = MAP_TYPES.ECOFORESTRY) => {
  // Charger les préférences sauvegardées
  const loadSavedPreferences = () => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (e) {
      console.warn('Could not load map preferences:', e);
    }
    return null;
  };

  const savedPrefs = loadSavedPreferences();
  
  // État du type de carte
  const [mapType, setMapTypeState] = useState(
    savedPrefs?.mapType || defaultType
  );
  
  // Options de la carte
  const [mapOptions, setMapOptionsState] = useState({
    showLabels: savedPrefs?.showLabels ?? true,
    showCoordinates: savedPrefs?.showCoordinates ?? true,
    showGrid: savedPrefs?.showGrid ?? false,
    highResolution: savedPrefs?.highResolution ?? false,
    autoZoneOpacity: savedPrefs?.autoZoneOpacity ?? true
  });

  // Sauvegarder les préférences
  const savePreferences = useCallback((type, options) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        mapType: type,
        ...options
      }));
    } catch (e) {
      console.warn('Could not save map preferences:', e);
    }
  }, []);

  // Changer le type de carte
  const setMapType = useCallback((newType) => {
    if (MAP_CONFIGS[newType]) {
      setMapTypeState(newType);
      savePreferences(newType, mapOptions);
    } else {
      console.warn(`Unknown map type: ${newType}`);
    }
  }, [mapOptions, savePreferences]);

  // Mettre à jour les options
  const setMapOptions = useCallback((newOptions) => {
    setMapOptionsState(prev => {
      const updated = { ...prev, ...newOptions };
      savePreferences(mapType, updated);
      return updated;
    });
  }, [mapType, savePreferences]);

  // Toggle une option spécifique
  const toggleOption = useCallback((optionKey) => {
    setMapOptions({ [optionKey]: !mapOptions[optionKey] });
  }, [mapOptions, setMapOptions]);

  // Configuration actuelle de la carte
  const currentConfig = useMemo(() => {
    return getMapConfig(mapType);
  }, [mapType]);

  // La carte est-elle optimisée pour le mode sombre?
  const isDarkOptimized = useMemo(() => {
    return isMapDark(mapType);
  }, [mapType]);

  // Obtenir l'opacité des zones pour la carte actuelle
  const getZoneOpacityForCurrentMap = useCallback((zoneType = 'fill') => {
    if (mapOptions.autoZoneOpacity) {
      return getZoneOpacity(mapType, zoneType);
    }
    return 0.25; // Opacité par défaut
  }, [mapType, mapOptions.autoZoneOpacity]);

  // URL des tiles pour la carte actuelle
  const tileUrl = useMemo(() => {
    return currentConfig.tileUrl;
  }, [currentConfig]);

  // Attribution de la carte
  const attribution = useMemo(() => {
    return currentConfig.attribution;
  }, [currentConfig]);

  // URL des labels (si disponible)
  const labelsUrl = useMemo(() => {
    return mapOptions.showLabels ? currentConfig.labelsUrl : null;
  }, [currentConfig, mapOptions.showLabels]);

  // Layers WMS (si disponibles)
  const wmsLayers = useMemo(() => {
    return currentConfig.wmsLayers || [];
  }, [currentConfig]);

  // Infos de la carte pour l'UI
  const mapInfo = useMemo(() => ({
    id: currentConfig.id,
    name: currentConfig.name,
    shortName: currentConfig.shortName,
    description: currentConfig.description,
    icon: currentConfig.icon,
    category: currentConfig.category,
    isPremium: currentConfig.isPremium
  }), [currentConfig]);

  return {
    // État
    mapType,
    mapOptions,
    currentConfig,
    mapInfo,
    
    // Propriétés dérivées
    tileUrl,
    attribution,
    labelsUrl,
    wmsLayers,
    isDarkOptimized,
    
    // Actions
    setMapType,
    setMapOptions,
    toggleOption,
    getZoneOpacityForCurrentMap,
    
    // Constants
    MAP_TYPES,
    MAP_CONFIGS,
    DARK_OPTIMIZED_MAPS
  };
};

export default useMapType;
export { MAP_TYPES, MAP_CONFIGS };
