/**
 * useTerritoryAutoLoad.js — Auto-chargement territoire BIONIC V8
 * 
 * Charge automatiquement au chargement de MON TERRITOIRE:
 * - Zones écologiques pertinentes
 * - Corridors 10X
 * - Stopovers
 * - Couches V7 nécessaires
 * - Selon la dernière recherche utilisateur
 * 
 * VERSION: 8.0.0 — Auto-load territoire complet
 */

import { useState, useEffect, useCallback, useRef } from 'react';

const STORAGE_KEY = 'bionic_territory_last_search';
const BCE_STORAGE_KEY = 'bionic_bce_last_report';

/**
 * Hook pour l'auto-chargement du territoire
 */
export function useTerritoryAutoLoad({
  enabled = true,
  onLoadComplete,
  onBCEValidation,
}) {
  const [isLoading, setIsLoading] = useState(false);
  const [loadedData, setLoadedData] = useState(null);
  const [bceReport, setBceReport] = useState(null);
  const [error, setError] = useState(null);
  const hasLoadedRef = useRef(false);
  
  // Charger la dernière recherche sauvegardée
  const getLastSearch = useCallback(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  }, []);
  
  // Sauvegarder la recherche courante
  const saveSearch = useCallback((searchData) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        ...searchData,
        timestamp: new Date().toISOString(),
      }));
    } catch (e) {
      console.warn('Failed to save search:', e);
    }
  }, []);
  
  // Charger les zones écologiques
  const loadEcologicalZones = useCallback(async (species, bbox) => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
    try {
      const response = await fetch(
        `${backendUrl}/api/v1/ecological/species/${species}/zones`
      );
      if (response.ok) {
        return await response.json();
      }
    } catch (e) {
      console.warn('Failed to load ecological zones:', e);
    }
    return null;
  }, []);
  
  // Charger les corridors
  const loadCorridors = useCallback(async (bbox, species) => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
    try {
      const response = await fetch(
        `${backendUrl}/api/v1/bionic/movement-corridors?` +
        `species=${species || 'orignal'}&` +
        `min_lat=${bbox?.minLat || 45.5}&max_lat=${bbox?.maxLat || 46.0}&` +
        `min_lng=${bbox?.minLng || -73.5}&max_lng=${bbox?.maxLng || -73.0}`
      );
      if (response.ok) {
        return await response.json();
      }
    } catch (e) {
      console.warn('Failed to load corridors:', e);
    }
    return null;
  }, []);
  
  // Charger le résumé des corridors
  const loadCorridorsSummary = useCallback(async () => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
    try {
      const response = await fetch(`${backendUrl}/api/v1/ecological/corridors/summary`);
      if (response.ok) {
        return await response.json();
      }
    } catch (e) {
      console.warn('Failed to load corridors summary:', e);
    }
    return {
      summary: { total_corridors: 0, macro_corridors: 0, biological_corridors: 0, conservation_corridors: 0 },
      by_species: {}
    };
  }, []);
  
  // Exécuter la validation BCE
  const runBCEValidation = useCallback(async (data) => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
    try {
      const response = await fetch(`${backendUrl}/api/v1/ecological/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          species: data.species || 'orignal',
          zone_type: data.zone_type || 'alimentation',
          season: data.season || 'automne',
          ndvi: data.ndvi || 0.6,
          slope: data.slope || 10,
          distance_to_water: data.distance_to_water || 500,
          human_pressure: data.human_pressure || 0.2,
        }),
      });
      
      if (response.ok) {
        const report = await response.json();
        setBceReport(report);
        
        // Sauvegarder le rapport BCE
        try {
          localStorage.setItem(BCE_STORAGE_KEY, JSON.stringify(report));
        } catch {}
        
        if (onBCEValidation) {
          onBCEValidation(report);
        }
        
        return report;
      }
    } catch (e) {
      console.warn('BCE validation failed:', e);
    }
    return null;
  }, [onBCEValidation]);
  
  // Auto-load principal
  const autoLoad = useCallback(async () => {
    if (!enabled || hasLoadedRef.current) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const lastSearch = getLastSearch();
      const species = lastSearch?.species || 'orignal';
      const bbox = lastSearch?.bbox || {
        minLat: 45.5, maxLat: 46.0,
        minLng: -73.5, maxLng: -73.0
      };
      
      // Charger en parallèle
      const [zones, corridors, summary] = await Promise.all([
        loadEcologicalZones(species, bbox),
        loadCorridors(bbox, species),
        loadCorridorsSummary(),
      ]);
      
      const data = {
        species,
        bbox,
        zones,
        corridors,
        corridorsSummary: summary,
        loadedAt: new Date().toISOString(),
      };
      
      setLoadedData(data);
      hasLoadedRef.current = true;
      
      // Exécuter validation BCE automatiquement
      await runBCEValidation({
        species,
        zone_type: 'alimentation',
        season: getCurrentSeason(),
      });
      
      if (onLoadComplete) {
        onLoadComplete(data);
      }
      
    } catch (e) {
      console.error('Auto-load failed:', e);
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  }, [enabled, getLastSearch, loadEcologicalZones, loadCorridors, loadCorridorsSummary, runBCEValidation, onLoadComplete]);
  
  // Déclencher l'auto-load au montage
  useEffect(() => {
    autoLoad();
  }, [autoLoad]);
  
  // Recharger manuellement
  const reload = useCallback(() => {
    hasLoadedRef.current = false;
    autoLoad();
  }, [autoLoad]);
  
  return {
    isLoading,
    loadedData,
    bceReport,
    error,
    reload,
    saveSearch,
  };
}

/**
 * Détermine la saison courante
 */
function getCurrentSeason() {
  const month = new Date().getMonth();
  if (month >= 2 && month <= 4) return 'printemps';
  if (month >= 5 && month <= 7) return 'ete';
  if (month >= 8 && month <= 10) return 'automne';
  return 'hiver';
}

/**
 * Hook pour le statut BCE
 */
export function useBCEStatus() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchStatus = async () => {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      try {
        const response = await fetch(`${backendUrl}/api/bce/status`);
        if (response.ok) {
          const data = await response.json();
          setStatus(data);
        }
      } catch (e) {
        console.warn('Failed to fetch BCE status:', e);
      } finally {
        setLoading(false);
      }
    };
    
    fetchStatus();
    
    // Polling toutes les 30 secondes
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);
  
  return { status, loading };
}

export default useTerritoryAutoLoad;
