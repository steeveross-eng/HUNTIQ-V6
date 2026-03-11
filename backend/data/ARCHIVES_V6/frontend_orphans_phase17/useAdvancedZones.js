/**
 * useAdvancedZones Hook
 * 
 * Gestion des 14 types de zones avancées BIONIC
 * - Chargement des zones depuis l'API ou données locales
 * - Filtrage par visibilité
 * - Calcul de l'opacité adaptative
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { ZONE_CONFIG, getAdaptiveOpacity } from '@/components/maps/BionicAdvancedZones';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

/**
 * Hook pour gérer les zones avancées
 * 
 * @param {object} options
 * @param {array} options.bounds - Limites de la carte [sw, ne]
 * @param {string} options.territoryId - ID du territoire
 * @param {boolean} options.autoLoad - Charger automatiquement les zones
 */
const useAdvancedZones = ({
  bounds = null,
  territoryId = null,
  autoLoad = true
} = {}) => {
  // État des zones
  const [zones, setZones] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Visibilité par type de zone
  const [visibility, setVisibility] = useState({
    // Comportementales
    rut: true,
    repos: true,
    alimentation: true,
    corridor: true,
    // Environnementales
    habitat: true,
    soleil: false,
    pente: false,
    hydro: true,
    foret: false,
    thermique: false,
    // Stratégiques
    affut: true,
    hotspot: true,
    pression: false,
    acces: false
  });
  
  // Opacité globale (0-100)
  const [globalOpacity, setGlobalOpacity] = useState(75);
  
  // Filtre de score minimum
  const [minScore, setMinScore] = useState(50);
  
  // Charger les zones depuis l'API
  const loadZones = useCallback(async () => {
    if (!territoryId && !bounds) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      let url = `${API_BASE}/api/territory/zones`;
      const params = new URLSearchParams();
      
      if (territoryId) {
        params.append('territory_id', territoryId);
      }
      
      if (bounds) {
        params.append('sw_lat', bounds[0][0]);
        params.append('sw_lng', bounds[0][1]);
        params.append('ne_lat', bounds[1][0]);
        params.append('ne_lng', bounds[1][1]);
      }
      
      if (minScore > 0) {
        params.append('min_score', minScore);
      }
      
      const response = await fetch(`${url}?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error('Erreur lors du chargement des zones');
      }
      
      const data = await response.json();
      setZones(data.zones || []);
      
    } catch (err) {
      console.warn('Zone loading error:', err);
      setError(err.message);
      
      // Utiliser des zones de démonstration si l'API échoue
      setZones(generateDemoZones(bounds));
    } finally {
      setIsLoading(false);
    }
  }, [territoryId, bounds, minScore]);
  
  // Charger automatiquement au montage
  useEffect(() => {
    if (autoLoad) {
      loadZones();
    }
  }, [autoLoad, loadZones]);
  
  // Toggle la visibilité d'un type de zone
  const toggleZoneVisibility = useCallback((zoneType) => {
    setVisibility(prev => ({
      ...prev,
      [zoneType]: !prev[zoneType]
    }));
  }, []);
  
  // Activer toutes les zones
  const showAllZones = useCallback(() => {
    setVisibility(prev => 
      Object.keys(prev).reduce((acc, key) => ({ ...acc, [key]: true }), {})
    );
  }, []);
  
  // Masquer toutes les zones
  const hideAllZones = useCallback(() => {
    setVisibility(prev => 
      Object.keys(prev).reduce((acc, key) => ({ ...acc, [key]: false }), {})
    );
  }, []);
  
  // Activer uniquement les zones d'une catégorie
  const showCategoryOnly = useCallback((category) => {
    setVisibility(prev => {
      const newVisibility = { ...prev };
      Object.keys(ZONE_CONFIG).forEach(zoneType => {
        const config = ZONE_CONFIG[zoneType];
        newVisibility[zoneType] = config.category === category;
      });
      return newVisibility;
    });
  }, []);
  
  // Presets de visibilité
  const applyPreset = useCallback((presetName) => {
    const presets = {
      chasse: {
        rut: true, repos: true, alimentation: true, corridor: true,
        habitat: true, affut: true, hotspot: true,
        soleil: false, pente: false, hydro: false, foret: false,
        thermique: false, pression: false, acces: false
      },
      analyse: {
        rut: true, repos: true, alimentation: true, corridor: true,
        habitat: true, soleil: true, pente: true, hydro: true, foret: true,
        thermique: true, affut: true, hotspot: true, pression: true, acces: true
      },
      minimal: {
        rut: false, repos: false, alimentation: false, corridor: false,
        habitat: true, soleil: false, pente: false, hydro: false, foret: false,
        thermique: false, affut: true, hotspot: true, pression: false, acces: false
      }
    };
    
    if (presets[presetName]) {
      setVisibility(presets[presetName]);
    }
  }, []);
  
  // Zones filtrées par visibilité
  const visibleZones = useMemo(() => {
    return zones.filter(zone => {
      const zoneType = zone.type || zone.zoneType;
      return visibility[zoneType] === true;
    });
  }, [zones, visibility]);
  
  // Compteurs par catégorie
  const zoneCounts = useMemo(() => {
    const counts = {
      behavioral: 0,
      environmental: 0,
      strategic: 0,
      total: zones.length,
      visible: visibleZones.length
    };
    
    zones.forEach(zone => {
      const zoneType = zone.type || zone.zoneType;
      const config = ZONE_CONFIG[zoneType];
      if (config) {
        counts[config.category]++;
      }
    });
    
    return counts;
  }, [zones, visibleZones]);
  
  // Ajouter une zone localement (avant sync avec backend)
  const addZone = useCallback((zone) => {
    setZones(prev => [...prev, { ...zone, id: zone.id || `local-${Date.now()}` }]);
  }, []);
  
  // Supprimer une zone localement
  const removeZone = useCallback((zoneId) => {
    setZones(prev => prev.filter(z => z.id !== zoneId));
  }, []);
  
  // Mettre à jour une zone localement
  const updateZone = useCallback((zoneId, updates) => {
    setZones(prev => prev.map(z => 
      z.id === zoneId ? { ...z, ...updates } : z
    ));
  }, []);
  
  return {
    // État
    zones,
    visibleZones,
    visibility,
    globalOpacity,
    minScore,
    isLoading,
    error,
    zoneCounts,
    
    // Actions
    loadZones,
    toggleZoneVisibility,
    showAllZones,
    hideAllZones,
    showCategoryOnly,
    applyPreset,
    setGlobalOpacity,
    setMinScore,
    addZone,
    removeZone,
    updateZone,
    
    // Configuration
    ZONE_CONFIG
  };
};

/**
 * Générer des zones de démonstration
 * Utilisé si l'API n'est pas disponible
 */
const generateDemoZones = (bounds) => {
  if (!bounds) return [];
  
  const [[swLat, swLng], [neLat, neLng]] = bounds;
  const centerLat = (swLat + neLat) / 2;
  const centerLng = (swLng + neLng) / 2;
  
  // Générer quelques zones de démo
  return [
    {
      id: 'demo-hotspot-1',
      type: 'hotspot',
      geometry: 'circle',
      center: [centerLat + 0.01, centerLng - 0.02],
      radius: 200,
      score: 92,
      confirmed: true
    },
    {
      id: 'demo-rut-1',
      type: 'rut',
      geometry: 'polygon',
      coordinates: [
        [centerLat + 0.015, centerLng + 0.01],
        [centerLat + 0.02, centerLng + 0.015],
        [centerLat + 0.018, centerLng + 0.025],
        [centerLat + 0.012, centerLng + 0.022],
        [centerLat + 0.015, centerLng + 0.01]
      ],
      score: 85
    },
    {
      id: 'demo-alimentation-1',
      type: 'alimentation',
      geometry: 'polygon',
      coordinates: [
        [centerLat - 0.01, centerLng - 0.01],
        [centerLat - 0.005, centerLng - 0.005],
        [centerLat - 0.008, centerLng + 0.005],
        [centerLat - 0.015, centerLng + 0.002],
        [centerLat - 0.01, centerLng - 0.01]
      ],
      score: 78
    },
    {
      id: 'demo-corridor-1',
      type: 'corridor',
      geometry: 'corridor',
      coordinates: [
        [centerLat - 0.02, centerLng + 0.02],
        [centerLat - 0.01, centerLng + 0.015],
        [centerLat, centerLng + 0.01],
        [centerLat + 0.01, centerLng + 0.008]
      ],
      width: 80,
      score: 72
    },
    {
      id: 'demo-affut-1',
      type: 'affut',
      geometry: 'circle',
      center: [centerLat + 0.005, centerLng - 0.015],
      radius: 50,
      score: 88
    },
    {
      id: 'demo-habitat-1',
      type: 'habitat',
      geometry: 'polygon',
      coordinates: [
        [centerLat - 0.025, centerLng - 0.02],
        [centerLat - 0.018, centerLng - 0.015],
        [centerLat - 0.02, centerLng - 0.008],
        [centerLat - 0.028, centerLng - 0.012],
        [centerLat - 0.025, centerLng - 0.02]
      ],
      score: 81
    }
  ];
};

export default useAdvancedZones;
