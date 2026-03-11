/**
 * EcoforestryLayers.jsx
 * 
 * Composant de gestion des couches écoforestières du Québec
 * Sources: MRNF (Ministère des Ressources naturelles et des Forêts)
 * 
 * FONCTIONNALITÉS :
 * 1. Carte écoforestière complète (peuplements, essences, perturbations)
 * 2. Couches LiDAR dendrométriques (hauteur, volume, surface terrière)
 * 3. Orthophotographies haute résolution
 * 4. Courbes de niveau et reliefs
 * 5. Classification du couvert forestier (résineux, feuillus, mélangés)
 * 
 * SYSTÈME DE FALLBACK :
 * - Détection automatique de la disponibilité de la carte écoforestière
 * - Fallback vers fond HD alternatif (topographique/satellite)
 * - Polling silencieux pour re-détection
 * - Remplacement dynamique sans rechargement
 * 
 * SERVICES WMS OFFICIELS DU QUÉBEC :
 * - https://geoegl.msp.gouv.qc.ca/ws/mffpecofor.fcgi (Inventaire écoforestier)
 * - https://ca.nfis.org/cubewerx/cubeserv (NFIS-QC)
 * - Forêt Ouverte (données ouvertes)
 */

import React, { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import { TileLayer, WMSTileLayer, LayersControl, useMap } from 'react-leaflet';
import L from 'leaflet';
import { 
  Layers, TreePine, Mountain, Droplets, Eye, EyeOff,
  MapPin, Info, Settings, ChevronDown, ChevronUp,
  Leaf, Trees, Thermometer, Ruler, AlertTriangle, 
  RefreshCw, Wifi, WifiOff, CheckCircle2, SatelliteDish
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

// ============================================
// SYSTÈME DE FALLBACK - CONFIGURATION
// ============================================

/**
 * États de disponibilité de la carte écoforestière
 */
export const EcoMapStatus = {
  CHECKING: 'checking',      // Vérification en cours
  AVAILABLE: 'available',    // Carte disponible
  UNAVAILABLE: 'unavailable', // Carte non disponible (fallback actif)
  ERROR: 'error',            // Erreur de chargement
  LOADING: 'loading'         // Chargement en cours
};

/**
 * Configuration du système de fallback
 */
const FALLBACK_CONFIG = {
  // Intervalle de polling pour vérifier la disponibilité (ms)
  pollingInterval: 30000, // 30 secondes
  // Timeout pour la vérification de disponibilité (ms)
  checkTimeout: 8000,
  // Nombre max de tentatives avant d'arrêter le polling
  maxRetries: 10,
  // Délai avant la première vérification (ms)
  initialDelay: 1000
};

/**
 * Fonds de carte de fallback haute résolution
 */
// Stadia Maps API Key - Required for terrain layer
const STADIA_API_KEY = '5272b858-5b8c-4140-8ad2-066343695ca3';

export const FALLBACK_BASEMAPS = {
  // Topographique haute résolution (OpenTopoMap)
  topo_hd: {
    id: 'topo_hd',
    name: 'Topographique HD',
    url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attribution: '&copy; OpenTopoMap (CC-BY-SA)',
    maxZoom: 17,
    priority: 1
  },
  // Satellite Esri World Imagery
  satellite_hd: {
    id: 'satellite_hd',
    name: 'Satellite HD',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: '&copy; Esri, Maxar, Earthstar Geographics',
    maxZoom: 19,
    priority: 2
  },
  // Terrain Stamen (bon relief) - Stadia Maps avec API Key
  terrain: {
    id: 'terrain',
    name: 'Terrain Relief',
    url: `https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png${STADIA_API_KEY ? `?api_key=${STADIA_API_KEY}` : ''}`,
    attribution: '&copy; Stadia Maps, Stamen Design',
    maxZoom: 18,
    priority: 3
  }
};

// ============================================
// CONFIGURATION DES SERVICES WMS DU QUÉBEC
// ============================================

/**
 * Services WMS officiels du gouvernement du Québec (MRNF)
 * Documentation: https://www.quebec.ca/agriculture-environnement-et-ressources-naturelles/forets/recherche-connaissances/inventaire-forestier/donnees-cartes-resultats
 * 
 * SOURCES PRINCIPALES :
 * 1. NFIS (National Forest Information System) - Accès pancanadien
 * 2. Données Québec - Carte écoforestière officielle
 * 3. Forêt Ouverte - Plateforme de données ouvertes
 */
export const QUEBEC_WMS_SERVICES = {
  // Service NFIS-QC - National Forest Information System (PRINCIPAL - FONCTIONNEL)
  nfis_qc: {
    url: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
    version: '1.3.0',
    format: 'image/png',
    layers: {
      produits_eco: 'NFIS-QC.produits_ecoforestiers',
      peuplements: 'NFIS-QC.ori_pee_ori_prov',
      depots: 'NFIS-QC.depots_surface',
      vegetation_pot: 'NFIS-QC.veg_pot',
      volumes: 'NFIS-QC.volumes_forestiers',
      feux: 'NFIS-QC.ca_feux',
      interventions: 'NFIS-QC.ca_interv_fores',
      classification_eco: 'NFIS-QC.classi_eco_terri',
      pentes: 'NFIS-QC.pentes',
      hydro: 'NFIS-QC.hydro',
      lidar_mhc: 'NFIS-QC.lidar_mhc',
      lidar_ombre: 'NFIS-QC.lidar_ombre',
      courbes_niveau: 'NFIS-QC.courbes_niveau_5m'
    }
  },
  // Service MERN - Territoire administratif (secondaire)
  mern: {
    url: 'https://servicescarto.mern.gouv.qc.ca/pes/services/Territoire/SDA_WMS/MapServer/WMSServer',
    version: '1.3.0',
    format: 'image/png',
    layers: {
      territoire: '0,1,2,3,4,5',
      hydrographie: '6,7,8',
      relief: '9,10'
    }
  },
  // Service NFIS - National Forest Information System (accès pancanadien)
  nfis: {
    url: 'https://ca.nfis.org/cubewerx/cubeserv',
    datastore: 'NFIS-QC',
    version: '1.3.0',
    layers: {
      index_carte: 'qc_5einv_index_carte_ecoforestiere',
      disponibilite: 'qc_5einv_disponibilite',
      volume_forestier: 'qc_volumeforestier',
      vegetation_potentielle: 'qc_vegetation_potentielle',
      classification_ecologique: 'qc_classification_ecologique',
      depots_surface: 'qc_depots_surface',
      interventions_sylvicoles: 'qc_interventions_sylvicoles',
      pien: 'qc_pien_inventaire'
    }
  },
  // Service alternatif - Carte écoforestière (peut nécessiter authentification)
  ecoforestry_alt: {
    url: 'https://servicescarto.mffp.gouv.qc.ca/pes/services/Inventaire/CarteEcoforestiere/MapServer/WMSServer',
    layers: {
      peuplements: '0',
      perturbations: '1'
    },
    note: 'Peut nécessiter authentification - utiliser MERN en priorité'
  }
};

/**
 * Services WMS pancanadiens (NFI - National Forest Inventory)
 */
export const CANADA_NATIONAL_SERVICES = {
  // National Forest Inventory - Managed Forests
  nfi: {
    url: 'https://ca.nfis.org/mapserver/cgi-bin/ccfm_managed_forests_eng.cgi',
    type: 'WMS',
    version: '1.1.1',
    layers: {
      managed_forests: 'managed_forests',
      forest_management: 'forest_management_classification'
    }
  },
  // SCANFI - Spatialized Canadian NFI (2020)
  scanfi: {
    url: 'https://ca.nfis.org/cubewerx/cubeserv',
    datastore: 'SCANFI',
    type: 'WMS',
    layers: {
      land_cover: 'scanfi_landcover_2020',
      canopy_height: 'scanfi_canopy_height_2020'
    }
  }
};

/**
 * Services REST du USDA Forest Service (États-Unis)
 */
export const USA_FOREST_SERVICES = {
  // Enterprise Data Warehouse (EDW)
  usfs_edw: {
    baseUrl: 'https://apps.fs.usda.gov/arcx/rest/services/EDW',
    type: 'REST',
    layers: {
      national_forests: 'EDW_ForestSystemBoundaries_01/MapServer',
      wilderness: 'EDW_WildernessAreas_01/MapServer',
      fire_perimeters: 'EDW_FireOccurrencePoint_01/MapServer',
      roads: 'EDW_RoadCore_01/MapServer',
      trails: 'EDW_TrailNFSPublish_01/MapServer'
    }
  },
  // National Land Cover Database
  nlcd: {
    url: 'https://www.mrlc.gov/geoserver/wms',
    type: 'WMS',
    layers: {
      landcover_2021: 'nlcd_2021'
    }
  }
};

/**
 * Services WMS des autres provinces canadiennes
 */
export const PROVINCIAL_SERVICES = {
  // Colombie-Britannique
  bc: {
    url: 'https://openmaps.gov.bc.ca/geo/pub/wms',
    type: 'WMS',
    layers: {
      vri: 'WHSE_FOREST_VEGETATION.VEG_COMP_LYR_R1_POLY',
      fire_current: 'WHSE_LAND_AND_NATURAL_RESOURCE.PROT_CURRENT_FIRE_POLYS_SP',
      harvest: 'WHSE_FOREST_TENURE.FTEN_HARVEST_AUTH_POLY_SVW',
      cutblocks: 'WHSE_FOREST_VEGETATION.RSLT_OPENING_SVW'
    }
  },
  // Ontario
  on: {
    url: 'https://ws.lioservices.lrc.gov.on.ca/arcgis1061a/rest/services/LIO_Open_Data',
    type: 'REST',
    layers: {
      forest_inventory: 'Forest_Resources_Inventory/MapServer',
      forest_management: 'Forest_Management_Unit/MapServer'
    }
  },
  // Nouveau-Brunswick
  nb: {
    url: 'https://geonb.snb.ca/arcgis/services/GeoNB_ENR_ForestManagement/MapServer/WMSServer',
    type: 'WMS',
    layers: {
      forest_inventory: 'Forest_Inventory',
      vegetation: 'Vegetation_Management',
      silviculture: 'Silviculture'
    }
  }
};

// ============================================
// HOOK DE GESTION DU FALLBACK
// ============================================

/**
 * Hook personnalisé pour gérer la disponibilité de la carte écoforestière
 * et le système de fallback automatique
 */
export const useEcoMapFallback = (ecoMapEnabled = false) => {
  const [status, setStatus] = useState(EcoMapStatus.CHECKING);
  // Initialiser avec le fallback par défaut pour éviter un écran noir
  const [activeFallback, setActiveFallback] = useState(FALLBACK_BASEMAPS.topo_hd);
  const [retryCount, setRetryCount] = useState(0);
  const [lastCheck, setLastCheck] = useState(null);
  const pollingRef = useRef(null);
  const checkingRef = useRef(false);
  // STABILISATION: Tracker le status courant pour le polling sans re-render
  const statusRef = useRef(status);
  const retryCountRef = useRef(retryCount);
  
  /**
   * Vérifie la disponibilité du service WMS écoforestier
   * STABILISATION: Ne déclenche pas de re-render si le status ne change pas réellement
   */
  const checkEcoMapAvailability = useCallback(async () => {
    if (checkingRef.current) return;
    checkingRef.current = true;
    
    const API_BASE = process.env.REACT_APP_BACKEND_URL || '';
    
    try {
      // STABILISATION: Ne pas set CHECKING si on est déjà CHECKING (évite flash)
      if (statusRef.current !== EcoMapStatus.CHECKING) {
        setStatus(EcoMapStatus.CHECKING);
        statusRef.current = EcoMapStatus.CHECKING;
      }
      
      const nfisUrl = QUEBEC_WMS_SERVICES.nfis_qc.url;
      const checkUrl = `${API_BASE}/api/wms-proxy/check?url=${encodeURIComponent(nfisUrl)}`;
      
      // Utiliser XMLHttpRequest pour éviter le conflit postMessage/AbortController
      const data = await new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('GET', checkUrl);
        xhr.timeout = FALLBACK_CONFIG.checkTimeout;
        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            try { resolve(JSON.parse(xhr.responseText)); } 
            catch { reject(new Error('Invalid JSON')); }
          } else {
            reject(new Error(`HTTP ${xhr.status}`));
          }
        };
        xhr.onerror = () => reject(new Error('Network error'));
        xhr.ontimeout = () => reject(new Error('Timeout'));
        xhr.send();
      });
      
      if (data.available) {
        // STABILISATION: Ne mettre à jour que si le status change réellement
        if (statusRef.current !== EcoMapStatus.AVAILABLE) {
          setStatus(EcoMapStatus.AVAILABLE);
          statusRef.current = EcoMapStatus.AVAILABLE;
          setActiveFallback(null);
          setRetryCount(0);
          retryCountRef.current = 0;
        }
        setLastCheck(new Date());
        
        // Arrêter le polling dès que disponible
        if (pollingRef.current) {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }
        
        return true;
      }
      
      throw new Error('Service unavailable');
      
    } catch (error) {
      console.log('[EcoMap Fallback] Service indisponible:', error.message);
      
      // STABILISATION: Ne mettre à jour que si le status change réellement
      if (statusRef.current !== EcoMapStatus.UNAVAILABLE) {
        setStatus(EcoMapStatus.UNAVAILABLE);
        statusRef.current = EcoMapStatus.UNAVAILABLE;
        setActiveFallback(FALLBACK_BASEMAPS.topo_hd);
      }
      retryCountRef.current += 1;
      setRetryCount(retryCountRef.current);
      setLastCheck(new Date());
      
      return false;
    } finally {
      checkingRef.current = false;
    }
  }, []);
  
  /**
   * Démarre le polling silencieux pour vérifier la disponibilité
   * STABILISATION: Utilise des refs pour éviter les closures stales
   */
  const startPolling = useCallback(() => {
    if (pollingRef.current) return;
    
    pollingRef.current = setInterval(() => {
      if (retryCountRef.current < FALLBACK_CONFIG.maxRetries && statusRef.current === EcoMapStatus.UNAVAILABLE) {
        checkEcoMapAvailability();
      } else if (retryCountRef.current >= FALLBACK_CONFIG.maxRetries) {
        // Arrêter le polling après max retries
        if (pollingRef.current) {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }
      }
    }, FALLBACK_CONFIG.pollingInterval);
  }, [checkEcoMapAvailability]);
  
  /**
   * Arrête le polling
   */
  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);
  
  /**
   * Force une vérification manuelle
   */
  const forceCheck = useCallback(() => {
    setRetryCount(0);
    checkEcoMapAvailability();
  }, [checkEcoMapAvailability]);
  
  /**
   * Change le fallback actif
   */
  const setFallbackMap = useCallback((fallbackId) => {
    const fallback = FALLBACK_BASEMAPS[fallbackId];
    if (fallback) {
      setActiveFallback(fallback);
    }
  }, []);
  
  // Effet pour vérifier la disponibilité au montage et quand ecoMap est activé
  useEffect(() => {
    if (ecoMapEnabled) {
      // Délai initial avant la première vérification
      const initialTimeout = setTimeout(() => {
        checkEcoMapAvailability().then(available => {
          if (!available) {
            startPolling();
          }
        });
      }, FALLBACK_CONFIG.initialDelay);
      
      return () => {
        clearTimeout(initialTimeout);
        stopPolling();
      };
    }
  }, [ecoMapEnabled, checkEcoMapAvailability, startPolling, stopPolling]);
  
  // Cleanup au démontage
  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);
  
  return {
    status,
    activeFallback,
    retryCount,
    lastCheck,
    isAvailable: status === EcoMapStatus.AVAILABLE,
    isChecking: status === EcoMapStatus.CHECKING,
    isUnavailable: status === EcoMapStatus.UNAVAILABLE,
    forceCheck,
    setFallbackMap,
    stopPolling,
    startPolling
  };
};

/**
 * Fonds de carte disponibles pour "Mon Territoire BIONIC™"
 * Note: "Sombre (BIONIC)" et "OpenStreetMap" ont été retirés
 * BIONIC Design System Compliant - Lucide icons via iconName property
 */
export const BASE_MAPS = {
  satellite: {
    id: 'satellite',
    name: 'Satellite',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: '&copy; Esri, Maxar, Earthstar Geographics',
    iconName: 'satellite',
    isDark: false
  },
  satellite_hd: {
    id: 'satellite_hd',
    name: 'Satellite HD',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: '&copy; Esri, Maxar, Earthstar Geographics',
    iconName: 'satellite-dish',
    isDark: false
  },
  // IQHO - Hydro + Relief + Ombrage
  iqho: {
    id: 'iqho',
    name: 'IQHO',
    url: `https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png?api_key=${STADIA_API_KEY}`,
    attribution: '© Stadia Maps | © Stamen Design | © OpenStreetMap',
    iconName: 'droplet',
    isDark: true
  },
  // Écoforestière - Base OSM + WMS NFIS-QC
  ecoforestry: {
    id: 'ecoforestry',
    name: 'Écoforestière',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '© NFIS/MRNF Québec | © OpenStreetMap',
    iconName: 'tree-pine',
    isDark: false,
    type: 'wms',
    wmsUrl: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
    layers: 'NFIS-QC.produits_ecoforestiers'
  },
  // Bathymétrie
  bathymetry: {
    id: 'bathymetry',
    name: 'Bathymétrie',
    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    attribution: '© BIONIC™ | © OpenStreetMap | © CARTO',
    iconName: 'waves',
    isDark: true
  },
  // Chemins Forestiers
  'forest-roads': {
    id: 'forest-roads',
    name: 'Chemins Forestiers',
    url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attribution: '© OpenTopoMap',
    iconName: 'route',
    isDark: false
  }
};

/**
 * Couches écoforestières disponibles
 * BIONIC Design System Compliant - Lucide icons via iconName property
 */
export const ECOFORESTRY_LAYERS = {
  peuplements: {
    id: 'peuplements',
    name: 'Peuplements forestiers',
    description: 'Types de peuplements et structure (min. 4 ha)',
    iconName: 'tree-pine',
    color: '#00CC00',
    wmsUrl: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
    wmsLayer: 'NFIS-QC.ori_pee_ori_prov',
    defaultOpacity: 0.6,
    legend: [
      { color: '#006400', label: 'Résineux (>75% ST)' },
      { color: '#228B22', label: 'Mélangés à résineux' },
      { color: '#90EE90', label: 'Mélangés à feuillus' },
      { color: '#FFD700', label: 'Feuillus (>75% ST)' }
    ]
  },
  essences: {
    id: 'essences',
    name: 'Essences principales (AIPF)',
    description: 'Groupements d\'essences et proportions',
    iconName: 'leaf',
    color: '#FF9900',
    wmsUrl: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
    wmsLayer: 'NFIS-QC.veg_pot',
    defaultOpacity: 0.5,
    legend: [
      { color: '#006400', label: 'Épinette noire (EPN)' },
      { color: '#228B22', label: 'Sapin baumier (SAB)' },
      { color: '#8B4513', label: 'Bouleau jaune (BOJ)' },
      { color: '#DAA520', label: 'Érable à sucre (ERS)' },
      { color: '#2E8B57', label: 'Pin gris (PIG)' }
    ]
  },
  perturbations: {
    id: 'perturbations',
    name: 'Perturbations récentes',
    description: 'Feux, coupes, chablis (min. 0,1 ha)',
    iconName: 'flame',
    color: '#FF4444',
    wmsUrl: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
    wmsLayer: 'NFIS-QC.ca_feux',
    defaultOpacity: 0.7,
    legend: [
      { color: '#FF0000', label: 'Feu récent' },
      { color: '#FF8C00', label: 'Coupe totale (CT)' },
      { color: '#FFD700', label: 'Coupe partielle (CP)' },
      { color: '#800080', label: 'Chablis (CHT/CHP)' }
    ]
  },
  densite: {
    id: 'densite',
    name: 'Densité du couvert',
    description: 'Pourcentage de couverture forestière',
    iconName: 'bar-chart-3',
    color: '#00CCFF',
    wmsUrl: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
    wmsLayer: 'NFIS-QC.depots_surface',
    defaultOpacity: 0.5,
    legend: [
      { color: '#006400', label: 'A - Dense (>80%)' },
      { color: '#228B22', label: 'B - Moyennement dense (60-80%)' },
      { color: '#90EE90', label: 'C - Claire (40-60%)' },
      { color: '#F0E68C', label: 'D - Très claire (25-40%)' }
    ]
  },
  hauteur: {
    id: 'hauteur',
    name: 'Hauteur des peuplements',
    description: 'Classes de hauteur dominante',
    iconName: 'ruler',
    color: '#9900FF',
    wmsUrl: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
    wmsLayer: 'NFIS-QC.volumes_forestiers',
    defaultOpacity: 0.5,
    legend: [
      { color: '#800080', label: '1 - >22m (très haute)' },
      { color: '#9932CC', label: '2 - 17-22m (haute)' },
      { color: '#BA55D3', label: '3 - 12-17m (moyenne)' },
      { color: '#DDA0DD', label: '4 - 7-12m (basse)' },
      { color: '#E6E6FA', label: '5 - <7m (très basse)' }
    ]
  },
  lidar_chm: {
    id: 'lidar_chm',
    name: 'LiDAR - Hauteur canopée',
    description: 'Modèle de hauteur de canopée (CHM)',
    iconName: 'satellite-dish',
    color: '#00FF00',
    wmsUrl: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
    wmsLayer: 'NFIS-QC.lidar_mhc',
    defaultOpacity: 0.6,
    isLidar: true,
    legend: [
      { color: '#FFFF00', label: '<5m' },
      { color: '#90EE90', label: '5-10m' },
      { color: '#00FF00', label: '10-20m' },
      { color: '#006400', label: '>20m' }
    ]
  },
  lidar_volume: {
    id: 'lidar_volume',
    name: 'LiDAR - Volume utilisable',
    description: 'Volume marchand par essence (m3/ha)',
    iconName: 'box',
    color: '#FF6600',
    wmsUrl: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
    wmsLayer: 'NFIS-QC.vmb_ha_tot',
    defaultOpacity: 0.6,
    isLidar: true,
    legend: [
      { color: '#FFF8DC', label: '<50 m³/ha' },
      { color: '#FFD700', label: '50-100 m³/ha' },
      { color: '#FF8C00', label: '100-200 m³/ha' },
      { color: '#FF4500', label: '>200 m³/ha' }
    ]
  },
  lidar_st: {
    id: 'lidar_st',
    name: 'LiDAR - Surface terrière',
    description: 'Surface terrière par unité (m2/ha)',
    iconName: 'target',
    color: '#0066FF',
    wmsUrl: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
    wmsLayer: 'NFIS-QC.lidar_ombre',
    defaultOpacity: 0.6,
    isLidar: true,
    legend: [
      { color: '#E0FFFF', label: '<15 m²/ha' },
      { color: '#87CEEB', label: '15-25 m²/ha' },
      { color: '#4169E1', label: '25-35 m²/ha' },
      { color: '#00008B', label: '>35 m²/ha' }
    ]
  },
  courbes_niveau: {
    id: 'courbes_niveau',
    name: 'Courbes de niveau',
    description: 'Relief, pentes et micro-reliefs',
    iconName: 'mountain',
    color: '#996633',
    wmsUrl: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
    wmsLayer: 'NFIS-QC.courbes_niveau_5m',
    defaultOpacity: 0.7,
    legend: [
      { color: '#8B4513', label: 'Courbes majeures (10m)' },
      { color: '#CD853F', label: 'Courbes mineures (2m)' }
    ]
  }
};

/**
 * TILE LOCKING SYSTEM — BIONIC V5 300%
 * 
 * Mécanisme de verrouillage des tuiles WMS :
 * - Aucune tuile visible tant que 100% du viewport n'est pas prêt
 * - Transition fluide opacity 0→target une fois chargé
 * - Cache persistant : keepBuffer=8 pour conserver les tuiles hors viewport
 * - Aucun rechargement lors du zoom/pan (updateWhenZooming=false)
 */
const TILE_LOCK_CONFIG = {
  keepBuffer: 8,           // Tuiles conservées hors viewport
  updateWhenZooming: false, // Pas de rechargement pendant le zoom
  updateWhenIdle: true,     // Rechargement uniquement au repos
  fadeInDuration: 300,      // Durée de la transition (ms)
};

/**
 * Composant pour une couche WMS individuelle avec Tile Locking
 * Utilise le proxy backend pour contourner les restrictions CORS
 */
const EcoforestryWMSLayer = React.memo(({ layer, opacity, visible }) => {
  const API_BASE = process.env.REACT_APP_BACKEND_URL || '';
  const [tilesReady, setTilesReady] = useState(false);
  const loadingCountRef = useRef(0);
  
  // Memoize l'URL et les layers pour éviter les re-créations d'objets
  const wmsUrl = layer.wmsUrl || QUEBEC_WMS_SERVICES.nfis_qc.url;
  const wmsLayers = layer.wmsLayer || 'NFIS-QC.produits_ecoforestiers';
  
  // STABILISATION: Memoize params — identité d'objet stable
  const wmsParams = useMemo(() => ({
    url: wmsUrl,
    layers: wmsLayers,
    format: 'image/png',
    transparent: 'true'
  }), [wmsUrl, wmsLayers]);
  
  // TILE LOCKING: Event handlers pour le suivi du chargement
  const tileEvents = useMemo(() => ({
    loading: () => {
      loadingCountRef.current += 1;
      setTilesReady(false);
    },
    load: () => {
      loadingCountRef.current = Math.max(0, loadingCountRef.current - 1);
      if (loadingCountRef.current === 0) {
        setTilesReady(true);
      }
    },
    tileerror: () => {
      loadingCountRef.current = Math.max(0, loadingCountRef.current - 1);
      if (loadingCountRef.current === 0) {
        setTilesReady(true);
      }
    }
  }), []);
  
  if (!visible) return null;
  
  return (
    <WMSTileLayer
      url={`${API_BASE}/api/wms-proxy/tile`}
      params={wmsParams}
      uppercase={false}
      format="image/png"
      transparent={true}
      opacity={tilesReady ? opacity : 0}
      keepBuffer={TILE_LOCK_CONFIG.keepBuffer}
      updateWhenZooming={TILE_LOCK_CONFIG.updateWhenZooming}
      updateWhenIdle={TILE_LOCK_CONFIG.updateWhenIdle}
      className="ecoforestry-tile-locked"
      eventHandlers={tileEvents}
    />
  );
});

/**
 * Composant de notification de fallback (non intrusif)
 * Affiche un message discret quand la carte écoforestière n'est pas disponible
 */
export const EcoMapFallbackNotification = ({ 
  status, 
  activeFallback, 
  retryCount, 
  onForceCheck,
  onChangeFallback 
}) => {
  // Utiliser un état dérivé pour dismissed basé sur le status
  const [dismissed, setDismissed] = useState(false);
  
  // Reset dismissed quand le status change vers AVAILABLE (sans useEffect)
  const effectiveDismissed = dismissed && status !== EcoMapStatus.AVAILABLE;
  
  if (effectiveDismissed || status === EcoMapStatus.AVAILABLE) return null;
  
  const isChecking = status === EcoMapStatus.CHECKING;
  const isUnavailable = status === EcoMapStatus.UNAVAILABLE;
  
  return (
    <div className={`
      absolute top-16 left-1/2 -translate-x-1/2 z-[1001]
      bg-gray-900/95 backdrop-blur-sm rounded-lg border shadow-xl
      transition-all duration-300 max-w-md
      ${isUnavailable ? 'border-amber-500/50' : 'border-blue-500/50'}
    `}>
      <div className="p-3">
        <div className="flex items-start gap-3">
          {/* Icône de statut */}
          <div className={`
            p-2 rounded-full
            ${isChecking ? 'bg-blue-500/20' : 'bg-amber-500/20'}
          `}>
            {isChecking ? (
              <RefreshCw className="h-4 w-4 text-blue-400 animate-spin" />
            ) : (
              <AlertTriangle className="h-4 w-4 text-amber-400" />
            )}
          </div>
          
          {/* Contenu */}
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-white">
                {isChecking ? 'Vérification...' : 'Carte écoforestière indisponible'}
              </span>
              {isUnavailable && (
                <Badge className="bg-amber-500/20 text-amber-400 text-[9px]">Fallback</Badge>
              )}
            </div>
            
            {isUnavailable && (
              <>
                <p className="text-xs text-gray-400 mt-1">
                  Fond alternatif activé : <span className="text-white">{activeFallback?.name || 'Topographique HD'}</span>
                </p>
                <p className="text-[10px] text-gray-500 mt-1">
                  Toutes les couches d&apos;analyse restent actives. Vérification auto en cours...
                </p>
                
                {/* Actions */}
                <div className="flex items-center gap-2 mt-2">
                  <button
                    onClick={onForceCheck}
                    className="text-[10px] text-blue-400 hover:text-blue-300 flex items-center gap-1"
                  >
                    <RefreshCw className="h-3 w-3" />
                    Réessayer
                  </button>
                  <span className="text-gray-600">•</span>
                  <button
                    onClick={() => setDismissed(true)}
                    className="text-[10px] text-gray-400 hover:text-gray-300"
                  >
                    Masquer
                  </button>
                  {retryCount > 0 && (
                    <>
                      <span className="text-gray-600">•</span>
                      <span className="text-[10px] text-gray-500">
                        Tentatives: {retryCount}/{FALLBACK_CONFIG.maxRetries}
                      </span>
                    </>
                  )}
                </div>
              </>
            )}
          </div>
          
          {/* Indicateur de connexion */}
          <div className="flex flex-col items-center">
            {isUnavailable ? (
              <WifiOff className="h-4 w-4 text-amber-400" />
            ) : (
              <Wifi className="h-4 w-4 text-blue-400" />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Composant de statut de la carte écoforestière (petit badge)
 */
export const EcoMapStatusBadge = ({ status, onClick }) => {
  const getStatusConfig = () => {
    switch (status) {
      case EcoMapStatus.AVAILABLE:
        return { icon: CheckCircle2, color: 'text-green-400', bg: 'bg-green-500/20', label: 'Connecté' };
      case EcoMapStatus.CHECKING:
        return { icon: RefreshCw, color: 'text-blue-400', bg: 'bg-blue-500/20', label: 'Vérification...', animate: true };
      case EcoMapStatus.UNAVAILABLE:
        return { icon: AlertTriangle, color: 'text-amber-400', bg: 'bg-amber-500/20', label: 'Fallback' };
      case EcoMapStatus.ERROR:
        return { icon: WifiOff, color: 'text-red-400', bg: 'bg-red-500/20', label: 'Erreur' };
      default:
        return { icon: Wifi, color: 'text-gray-400', bg: 'bg-gray-500/20', label: 'Inconnu' };
    }
  };
  
  const config = getStatusConfig();
  const Icon = config.icon;
  
  return (
    <button
      onClick={onClick}
      className={`
        flex items-center gap-1.5 px-2 py-1 rounded-md
        ${config.bg} border border-gray-700/50
        hover:bg-gray-800/50 transition-colors
      `}
      title={`État carte écoforestière: ${config.label}`}
    >
      <Icon className={`h-3 w-3 ${config.color} ${config.animate ? 'animate-spin' : ''}`} />
      <span className={`text-[10px] ${config.color}`}>{config.label}</span>
    </button>
  );
};

/**
 * Composant de contrôle des couches écoforestières
 */
export const EcoforestryLayerControl = ({ 
  activeLayers, 
  onToggleLayer, 
  layerOpacities, 
  onOpacityChange,
  expanded = false,
  onToggleExpand,
  // Props du système de fallback
  fallbackStatus,
  activeFallback,
  retryCount,
  onForceCheck,
  onChangeFallback
}) => {
  const [showLegend, setShowLegend] = useState(false);
  const [activeSection, setActiveSection] = useState('base');
  
  const lidarLayers = Object.values(ECOFORESTRY_LAYERS).filter(l => l.isLidar);
  const standardLayers = Object.values(ECOFORESTRY_LAYERS).filter(l => !l.isLidar);
  
  // Détecter si le mode écoforestier est activé
  const isEcoMapSelected = activeLayers.baseMap === 'ecoforestry';
  const showFallbackWarning = false; // Désactivé: WMS NFIS-QC est directement intégré
  
  return (
    <div className="bg-gray-900/95 backdrop-blur-sm border border-gray-700 rounded-lg shadow-xl overflow-hidden">
      {/* Header avec statut */}
      <div 
        className="flex items-center justify-between p-3 cursor-pointer hover:bg-gray-800/50 transition-colors"
        onClick={onToggleExpand}
      >
        <div className="flex items-center gap-2">
          <Layers className="h-4 w-4 text-[#f5a623]" />
          <span className="text-sm font-medium text-white">Carte Écoforestière</span>
          {fallbackStatus && isEcoMapSelected && (
            <EcoMapStatusBadge status={fallbackStatus} onClick={(e) => { e.stopPropagation(); onForceCheck?.(); }} />
          )}
          {!isEcoMapSelected && (
            <Badge className="bg-green-600/20 text-green-400 text-[9px]">Québec</Badge>
          )}
        </div>
        {expanded ? (
          <ChevronUp className="h-4 w-4 text-gray-400" />
        ) : (
          <ChevronDown className="h-4 w-4 text-gray-400" />
        )}
      </div>
      
      {/* Bandeau de fallback (si actif) */}
      {expanded && showFallbackWarning && (
        <div className="px-3 py-2 bg-amber-900/20 border-b border-amber-500/30">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-3 w-3 text-amber-400" />
            <span className="text-[10px] text-amber-300">
              Fond alternatif : <strong>{activeFallback?.name || 'Topographique HD'}</strong>
            </span>
            <button 
              onClick={onForceCheck}
              className="ml-auto text-[10px] text-blue-400 hover:text-blue-300 flex items-center gap-1"
            >
              <RefreshCw className="h-3 w-3" /> Réessayer
            </button>
          </div>
          <p className="text-[9px] text-gray-500 mt-1">
            Les couches d&apos;analyse, zones et interactions sont préservées.
          </p>
        </div>
      )}
      
      {expanded && (
        <div className="border-t border-gray-700 max-h-[400px] overflow-y-auto">
          {/* Tabs */}
          <div className="flex border-b border-gray-700">
            <button
              className={`flex-1 px-3 py-2 text-xs font-medium transition-colors ${activeSection === 'base' ? 'text-[#f5a623] border-b-2 border-[#f5a623]' : 'text-gray-400 hover:text-white'}`}
              onClick={() => setActiveSection('base')}
            >
              Fonds
            </button>
            <button
              className={`flex-1 px-3 py-2 text-xs font-medium transition-colors ${activeSection === 'ecoforestry' ? 'text-[#f5a623] border-b-2 border-[#f5a623]' : 'text-gray-400 hover:text-white'}`}
              onClick={() => setActiveSection('ecoforestry')}
            >
              Écoforestier
            </button>
            <button
              className={`flex-1 px-3 py-2 text-xs font-medium transition-colors ${activeSection === 'lidar' ? 'text-[#f5a623] border-b-2 border-[#f5a623]' : 'text-gray-400 hover:text-white'}`}
              onClick={() => setActiveSection('lidar')}
            >
              LiDAR
            </button>
          </div>
          
          {/* Base Maps Section */}
          {activeSection === 'base' && (
            <div className="p-3 space-y-2">
              <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Fond de carte</div>
              {Object.values(BASE_MAPS).map(baseMap => (
                <div 
                  key={baseMap.id}
                  className={`flex items-center justify-between p-2 rounded-lg cursor-pointer transition-colors ${activeLayers.baseMap === baseMap.id ? 'bg-[#f5a623]/20 border border-[#f5a623]/50' : 'hover:bg-gray-800/50'}`}
                  onClick={() => onToggleLayer('baseMap', baseMap.id)}
                >
                  <div className="flex items-center gap-2">
                    <span>{baseMap.icon}</span>
                    <span className="text-sm text-white">{baseMap.name}</span>
                  </div>
                  {activeLayers.baseMap === baseMap.id && (
                    <Badge className="bg-[#f5a623] text-black text-[9px]">Actif</Badge>
                  )}
                </div>
              ))}
            </div>
          )}
          
          {/* Ecoforestry Layers Section */}
          {activeSection === 'ecoforestry' && (
            <div className="p-3 space-y-3">
              <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Couches écoforestières</div>
              {standardLayers.map(layer => (
                <LayerItem
                  key={layer.id}
                  layer={layer}
                  isActive={activeLayers[layer.id]}
                  opacity={layerOpacities[layer.id] || layer.defaultOpacity}
                  onToggle={() => onToggleLayer(layer.id)}
                  onOpacityChange={(val) => onOpacityChange(layer.id, val)}
                  showLegend={showLegend}
                />
              ))}
            </div>
          )}
          
          {/* LiDAR Layers Section */}
          {activeSection === 'lidar' && (
            <div className="p-3 space-y-3">
              <div className="flex items-center justify-between mb-2">
                <div className="text-[10px] text-gray-500 uppercase tracking-wider">Couches LiDAR dendrométriques</div>
                <Badge className="bg-purple-600/20 text-purple-400 text-[9px]">Haute résolution</Badge>
              </div>
              <div className="bg-purple-900/20 border border-purple-700/30 rounded p-2 mb-3">
                <p className="text-[10px] text-purple-300 flex items-center gap-1">
                  <SatelliteDish className="h-3 w-3" /> Données LiDAR aéroporté - Résolution 0,8 ha - Précision ±5-10m
                </p>
              </div>
              {lidarLayers.map(layer => (
                <LayerItem
                  key={layer.id}
                  layer={layer}
                  isActive={activeLayers[layer.id]}
                  opacity={layerOpacities[layer.id] || layer.defaultOpacity}
                  onToggle={() => onToggleLayer(layer.id)}
                  onOpacityChange={(val) => onOpacityChange(layer.id, val)}
                  showLegend={showLegend}
                />
              ))}
            </div>
          )}
          
          {/* Footer */}
          <div className="border-t border-gray-700 p-2 flex items-center justify-between">
            <button
              className="text-[10px] text-gray-400 hover:text-white flex items-center gap-1"
              onClick={() => setShowLegend(!showLegend)}
            >
              <Info className="h-3 w-3" />
              {showLegend ? 'Masquer légendes' : 'Afficher légendes'}
            </button>
            <span className="text-[9px] text-gray-600">Source: MRNF Québec</span>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Composant pour un item de couche avec toggle et slider d'opacité
 */
const LayerItem = ({ layer, isActive, opacity, onToggle, onOpacityChange, showLegend }) => {
  return (
    <div className={`rounded-lg transition-colors ${isActive ? 'bg-gray-800/50' : ''}`}>
      <div className="flex items-center justify-between p-2">
        <div className="flex items-center gap-2 flex-1">
          <span className="text-base">{layer.icon}</span>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="text-sm text-white">{layer.name}</span>
              {layer.isLidar && (
                <Badge className="bg-purple-600/20 text-purple-400 text-[8px]">LiDAR</Badge>
              )}
            </div>
            <p className="text-[10px] text-gray-500 line-clamp-1">{layer.description}</p>
          </div>
        </div>
        <Switch
          checked={isActive}
          onCheckedChange={onToggle}
          className="data-[state=checked]:bg-[#f5a623]"
        />
      </div>
      
      {/* Opacity Slider */}
      {isActive && (
        <div className="px-2 pb-2">
          <div className="flex items-center gap-2">
            <Eye className="h-3 w-3 text-gray-500" />
            <Slider
              value={[opacity * 100]}
              onValueChange={([val]) => onOpacityChange(val / 100)}
              max={100}
              min={10}
              step={5}
              className="flex-1"
            />
            <span className="text-[10px] text-gray-500 w-8">{Math.round(opacity * 100)}%</span>
          </div>
        </div>
      )}
      
      {/* Legend */}
      {isActive && showLegend && layer.legend && (
        <div className="px-2 pb-2">
          <div className="bg-gray-900/50 rounded p-2 space-y-1">
            {layer.legend.map((item, idx) => (
              <div key={idx} className="flex items-center gap-2">
                <div 
                  className="w-3 h-3 rounded-sm border border-gray-600"
                  style={{ backgroundColor: item.color }}
                />
                <span className="text-[9px] text-gray-400">{item.label}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Composant principal qui rend les couches sur la carte
 * AVEC SYSTÈME DE FALLBACK AUTOMATIQUE
 */
const EcoforestryLayers = React.memo(({ 
  activeLayers = {}, 
  layerOpacities = {},
  baseMapId = 'dark',
  // Props du système de fallback (non utilisés dans le rendu, préservés pour compatibilité)
  fallbackStatus,
  activeFallback
}) => {
  const baseMap = BASE_MAPS[baseMapId] || BASE_MAPS.dark;
  const isEcoMapSelected = baseMapId === 'ecoforestry';
  
  // Déterminer le fond de carte effectif à utiliser
  const effectiveBaseMap = baseMap;
  const shouldRenderWMS = isEcoMapSelected || baseMap.type === 'wms';
  
  const API_BASE = process.env.REACT_APP_BACKEND_URL || '';
  
  // TILE LOCKING: Suivi du chargement de l'overlay WMS principal
  const [overlayReady, setOverlayReady] = useState(false);
  const overlayLoadCountRef = useRef(0);
  
  // STABILISATION: Memoize les params WMS de l'overlay principal
  const overlayWmsUrl = baseMap.wmsUrl || QUEBEC_WMS_SERVICES.nfis_qc.url;
  const overlayWmsLayers = baseMap.layers || 'NFIS-QC.produits_ecoforestiers';
  const overlayParams = useMemo(() => ({
    url: overlayWmsUrl,
    layers: overlayWmsLayers,
    format: 'image/png',
    transparent: 'true'
  }), [overlayWmsUrl, overlayWmsLayers]);
  
  // STABILISATION: Memoize l'URL du proxy
  const proxyUrl = useMemo(() => `${API_BASE}/api/wms-proxy/tile`, [API_BASE]);
  
  // TILE LOCKING: Event handlers pour l'overlay WMS principal
  const overlayTileEvents = useMemo(() => ({
    loading: () => {
      overlayLoadCountRef.current += 1;
      setOverlayReady(false);
    },
    load: () => {
      overlayLoadCountRef.current = Math.max(0, overlayLoadCountRef.current - 1);
      if (overlayLoadCountRef.current === 0) {
        setOverlayReady(true);
      }
    },
    tileerror: () => {
      overlayLoadCountRef.current = Math.max(0, overlayLoadCountRef.current - 1);
      if (overlayLoadCountRef.current === 0) {
        setOverlayReady(true);
      }
    }
  }), []);
  
  // Reset tile ready state quand on change de baseMap
  useEffect(() => {
    setOverlayReady(false);
    overlayLoadCountRef.current = 0;
  }, [baseMapId]);
  
  return (
    <>
      {/* Base Map Layer - toujours un TileLayer comme fond de sécurité */}
      <TileLayer
        url={effectiveBaseMap.url}
        attribution={effectiveBaseMap.attribution}
        maxZoom={effectiveBaseMap.maxZoom || 18}
        keepBuffer={TILE_LOCK_CONFIG.keepBuffer}
      />
      
      {/* WMS Overlay avec TILE LOCKING — opacity 0 tant que pas 100% chargé */}
      {shouldRenderWMS && (
        <WMSTileLayer
          url={proxyUrl}
          params={overlayParams}
          uppercase={false}
          format="image/png"
          transparent={true}
          opacity={overlayReady ? 0.7 : 0}
          keepBuffer={TILE_LOCK_CONFIG.keepBuffer}
          updateWhenZooming={TILE_LOCK_CONFIG.updateWhenZooming}
          updateWhenIdle={TILE_LOCK_CONFIG.updateWhenIdle}
          className="ecoforestry-tile-locked"
          eventHandlers={overlayTileEvents}
        />
      )}
      
      {/* Ecoforestry WMS Layers — indépendants du paramètre layers=… */}
      {isEcoMapSelected && Object.entries(ECOFORESTRY_LAYERS).map(([id, layer]) => (
        <EcoforestryWMSLayer
          key={id}
          layer={layer}
          opacity={layerOpacities[id] || layer.defaultOpacity}
          visible={activeLayers[id] === true}
        />
      ))}
    </>
  );
});

export default EcoforestryLayers;
export { EcoforestryWMSLayer, LayerItem };
