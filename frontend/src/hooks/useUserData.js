/**
 * useUserData - Hook pour la gestion des waypoints et lieux avec synchronisation backend
 * 
 * Fonctionnalités :
 * - CRUD waypoints et lieux via API backend
 * - Fallback localStorage pour mode hors ligne
 * - Synchronisation automatique au login
 * - Cache local pour performances
 */

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { toast } from 'sonner';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

// Helper pour les requêtes API
const apiRequest = async (endpoint, options = {}) => {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Erreur réseau' }));
    throw new Error(error.detail || 'Erreur serveur');
  }
  
  return response.json();
};

// Clés localStorage
const LOCAL_WAYPOINTS_KEY = 'bionic_waypoints';
const LOCAL_PLACES_KEY = 'bionic_places';
const SYNC_STATUS_KEY = 'bionic_sync_status';

/**
 * Hook principal pour les données utilisateur
 */
export const useUserData = (userId, options = {}) => {
  const { 
    autoSync = true,        // Synchroniser automatiquement au montage
    offlineMode = false,    // Mode hors ligne forcé
    onSyncComplete = null   // Callback après sync
  } = options;

  // États
  const [waypoints, setWaypoints] = useState([]);
  const [places, setPlaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [lastSync, setLastSync] = useState(null);
  
  const isMounted = useRef(true);

  // Détecter connexion/déconnexion
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Charger depuis localStorage
  const loadFromLocalStorage = useCallback(() => {
    try {
      const savedWaypoints = localStorage.getItem(LOCAL_WAYPOINTS_KEY);
      const savedPlaces = localStorage.getItem(LOCAL_PLACES_KEY);
      
      return {
        waypoints: savedWaypoints ? JSON.parse(savedWaypoints) : [],
        places: savedPlaces ? JSON.parse(savedPlaces) : []
      };
    } catch (e) {
      console.error('Error loading from localStorage:', e);
      return { waypoints: [], places: [] };
    }
  }, []);

  // Sauvegarder dans localStorage
  const saveToLocalStorage = useCallback((newWaypoints, newPlaces) => {
    try {
      if (newWaypoints !== undefined) {
        localStorage.setItem(LOCAL_WAYPOINTS_KEY, JSON.stringify(newWaypoints));
      }
      if (newPlaces !== undefined) {
        localStorage.setItem(LOCAL_PLACES_KEY, JSON.stringify(newPlaces));
      }
    } catch (e) {
      console.error('Error saving to localStorage:', e);
    }
  }, []);

  // Charger les données depuis le backend
  const fetchFromBackend = useCallback(async () => {
    if (!userId || offlineMode || !isOnline) return null;
    
    try {
      const [waypointsData, placesData] = await Promise.all([
        apiRequest(`/api/user-data/waypoints/${userId}`),
        apiRequest(`/api/user-data/places/${userId}`)
      ]);
      
      return { waypoints: waypointsData, places: placesData };
    } catch (e) {
      console.error('Error fetching from backend:', e);
      return null;
    }
  }, [userId, offlineMode, isOnline]);

  // Synchroniser localStorage vers backend
  const syncToBackend = useCallback(async () => {
    if (!userId || offlineMode || !isOnline) {
      toast.info('Mode hors ligne - Données sauvegardées localement');
      return false;
    }
    
    setSyncing(true);
    try {
      const localData = loadFromLocalStorage();
      
      // Sync vers backend
      const result = await apiRequest(`/api/user-data/sync/${userId}`, {
        method: 'POST',
        body: JSON.stringify({
          waypoints: localData.waypoints,
          places: localData.places
        })
      });
      
      // Recharger les données du backend après sync
      const backendData = await fetchFromBackend();
      if (backendData && isMounted.current) {
        setWaypoints(backendData.waypoints);
        setPlaces(backendData.places);
        saveToLocalStorage(backendData.waypoints, backendData.places);
      }
      
      setLastSync(new Date().toISOString());
      localStorage.setItem(SYNC_STATUS_KEY, JSON.stringify({
        lastSync: new Date().toISOString(),
        userId
      }));
      
      if (result.waypoints_synced > 0 || result.places_synced > 0) {
        toast.success('Données synchronisées', {
          description: result.message
        });
      }
      
      if (onSyncComplete) onSyncComplete(result);
      return true;
    } catch (e) {
      console.error('Sync error:', e);
      toast.error('Erreur de synchronisation', {
        description: 'Les données restent sauvegardées localement'
      });
      return false;
    } finally {
      if (isMounted.current) setSyncing(false);
    }
  }, [userId, offlineMode, isOnline, loadFromLocalStorage, fetchFromBackend, saveToLocalStorage, onSyncComplete]);

  // Charger les données au montage
  useEffect(() => {
    isMounted.current = true;
    
    const loadData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // D'abord charger depuis localStorage pour affichage immédiat
        const localData = loadFromLocalStorage();
        if (isMounted.current) {
          setWaypoints(localData.waypoints);
          setPlaces(localData.places);
        }
        
        // Si online et userId, charger depuis backend
        if (userId && isOnline && !offlineMode) {
          const backendData = await fetchFromBackend();
          
          if (backendData && isMounted.current) {
            // Fusionner les données (priorité au backend)
            const mergedWaypoints = backendData.waypoints.length > 0 
              ? backendData.waypoints 
              : localData.waypoints;
            const mergedPlaces = backendData.places.length > 0 
              ? backendData.places 
              : localData.places;
            
            setWaypoints(mergedWaypoints);
            setPlaces(mergedPlaces);
            saveToLocalStorage(mergedWaypoints, mergedPlaces);
            
            // Si données locales mais pas de backend, sync
            if (autoSync && backendData.waypoints.length === 0 && localData.waypoints.length > 0) {
              await syncToBackend();
            }
          }
        }
      } catch (e) {
        console.error('Error loading data:', e);
        if (isMounted.current) setError(e.message);
      } finally {
        if (isMounted.current) setLoading(false);
      }
    };
    
    loadData();
    
    return () => {
      isMounted.current = false;
    };
  }, [userId, isOnline, offlineMode, autoSync]); // eslint-disable-line

  // =============================================
  // WAYPOINTS CRUD
  // =============================================

  const addWaypoint = useCallback(async (waypointData) => {
    const tempId = `temp-${Date.now()}`;
    const now = new Date().toISOString();
    
    const newWaypoint = {
      id: tempId,
      user_id: userId || 'local',
      name: waypointData.name || 'Nouveau waypoint',
      lat: parseFloat(waypointData.lat) || 0,
      lng: parseFloat(waypointData.lng) || 0,
      type: waypointData.type || 'autre',
      active: waypointData.active !== undefined ? waypointData.active : true,
      notes: waypointData.notes || null,
      created_at: now
    };
    
    // Mise à jour optimiste
    setWaypoints(prev => {
      const updated = [...prev, newWaypoint];
      saveToLocalStorage(updated, undefined);
      return updated;
    });
    
    // Sync avec backend si possible
    if (userId && isOnline && !offlineMode) {
      try {
        const result = await apiRequest(`/api/user-data/waypoints/${userId}`, {
          method: 'POST',
          body: JSON.stringify(waypointData)
        });
        
        // Remplacer le waypoint temporaire par celui du backend
        setWaypoints(prev => {
          const updated = prev.map(wp => wp.id === tempId ? result : wp);
          saveToLocalStorage(updated, undefined);
          return updated;
        });
        
        toast.success('Waypoint créé et synchronisé');
        return result;
      } catch (e) {
        console.error('Error creating waypoint on backend:', e);
        toast.warning('Waypoint créé localement', {
          description: 'Sera synchronisé plus tard'
        });
      }
    } else {
      toast.success('Waypoint créé localement');
    }
    
    return newWaypoint;
  }, [userId, isOnline, offlineMode, saveToLocalStorage]);

  const updateWaypoint = useCallback(async (waypointId, updates) => {
    // Mise à jour optimiste
    setWaypoints(prev => {
      const updated = prev.map(wp => 
        wp.id === waypointId 
          ? { ...wp, ...updates, updated_at: new Date().toISOString() }
          : wp
      );
      saveToLocalStorage(updated, undefined);
      return updated;
    });
    
    // Sync avec backend
    if (userId && isOnline && !offlineMode && !waypointId.startsWith('temp-')) {
      try {
        const result = await apiRequest(`/api/user-data/waypoints/${userId}/${waypointId}`, {
          method: 'PUT',
          body: JSON.stringify(updates)
        });
        
        setWaypoints(prev => {
          const updated = prev.map(wp => wp.id === waypointId ? result : wp);
          saveToLocalStorage(updated, undefined);
          return updated;
        });
      } catch (e) {
        console.error('Error updating waypoint:', e);
      }
    }
  }, [userId, isOnline, offlineMode, saveToLocalStorage]);

  const deleteWaypoint = useCallback(async (waypointId) => {
    // Mise à jour optimiste
    setWaypoints(prev => {
      const updated = prev.filter(wp => wp.id !== waypointId);
      saveToLocalStorage(updated, undefined);
      return updated;
    });
    
    // Sync avec backend
    if (userId && isOnline && !offlineMode && !waypointId.startsWith('temp-')) {
      try {
        await apiRequest(`/api/user-data/waypoints/${userId}/${waypointId}`, {
          method: 'DELETE'
        });
        toast.success('Waypoint supprimé');
      } catch (e) {
        console.error('Error deleting waypoint:', e);
      }
    } else {
      toast.success('Waypoint supprimé localement');
    }
  }, [userId, isOnline, offlineMode, saveToLocalStorage]);

  const toggleWaypointActive = useCallback(async (waypointId) => {
    const waypoint = waypoints.find(wp => wp.id === waypointId);
    if (!waypoint) return;
    
    await updateWaypoint(waypointId, { active: !waypoint.active });
  }, [waypoints, updateWaypoint]);

  // =============================================
  // PLACES CRUD
  // =============================================

  const addPlace = useCallback(async (placeData) => {
    const tempId = `temp-${Date.now()}`;
    const now = new Date().toISOString();
    
    const newPlace = {
      id: tempId,
      user_id: userId || 'local',
      name: placeData.name,
      lat: parseFloat(placeData.lat) || 0,
      lng: parseFloat(placeData.lng) || 0,
      type: placeData.type || 'autre',
      notes: placeData.notes || null,
      address: placeData.address || null,
      phone: placeData.phone || null,
      website: placeData.website || null,
      created_at: now
    };
    
    // Mise à jour optimiste
    setPlaces(prev => {
      const updated = [...prev, newPlace];
      saveToLocalStorage(undefined, updated);
      return updated;
    });
    
    // Sync avec backend
    if (userId && isOnline && !offlineMode) {
      try {
        const result = await apiRequest(`/api/user-data/places/${userId}`, {
          method: 'POST',
          body: JSON.stringify(placeData)
        });
        
        setPlaces(prev => {
          const updated = prev.map(p => p.id === tempId ? result : p);
          saveToLocalStorage(undefined, updated);
          return updated;
        });
        
        toast.success('Lieu enregistré et synchronisé');
        return result;
      } catch (e) {
        console.error('Error creating place on backend:', e);
        toast.warning('Lieu enregistré localement', {
          description: 'Sera synchronisé plus tard'
        });
      }
    } else {
      toast.success('Lieu enregistré localement');
    }
    
    return newPlace;
  }, [userId, isOnline, offlineMode, saveToLocalStorage]);

  const updatePlace = useCallback(async (placeId, updates) => {
    setPlaces(prev => {
      const updated = prev.map(p => 
        p.id === placeId 
          ? { ...p, ...updates, updated_at: new Date().toISOString() }
          : p
      );
      saveToLocalStorage(undefined, updated);
      return updated;
    });
    
    if (userId && isOnline && !offlineMode && !placeId.startsWith('temp-')) {
      try {
        const result = await apiRequest(`/api/user-data/places/${userId}/${placeId}`, {
          method: 'PUT',
          body: JSON.stringify(updates)
        });
        
        setPlaces(prev => {
          const updated = prev.map(p => p.id === placeId ? result : p);
          saveToLocalStorage(undefined, updated);
          return updated;
        });
      } catch (e) {
        console.error('Error updating place:', e);
      }
    }
  }, [userId, isOnline, offlineMode, saveToLocalStorage]);

  const deletePlace = useCallback(async (placeId) => {
    setPlaces(prev => {
      const updated = prev.filter(p => p.id !== placeId);
      saveToLocalStorage(undefined, updated);
      return updated;
    });
    
    if (userId && isOnline && !offlineMode && !placeId.startsWith('temp-')) {
      try {
        await apiRequest(`/api/user-data/places/${userId}/${placeId}`, {
          method: 'DELETE'
        });
        toast.success('Lieu supprimé');
      } catch (e) {
        console.error('Error deleting place:', e);
      }
    } else {
      toast.success('Lieu supprimé localement');
    }
  }, [userId, isOnline, offlineMode, saveToLocalStorage]);

  // =============================================
  // COMPUTED VALUES (mémorisés pour éviter les re-renders)
  // =============================================

  const activeWaypoints = useMemo(() => {
    return waypoints.filter(wp => wp.active);
  }, [waypoints]);
  
  const stats = useMemo(() => ({
    totalWaypoints: waypoints.length,
    activeWaypoints: activeWaypoints.length,
    totalPlaces: places.length,
    isOnline,
    lastSync
  }), [waypoints.length, activeWaypoints.length, places.length, isOnline, lastSync]);

  return {
    // Data
    waypoints,
    places,
    activeWaypoints,
    stats,
    
    // States
    loading,
    syncing,
    error,
    isOnline,
    lastSync,
    
    // Waypoint actions
    addWaypoint,
    updateWaypoint,
    deleteWaypoint,
    toggleWaypointActive,
    
    // Place actions
    addPlace,
    updatePlace,
    deletePlace,
    
    // Sync actions
    syncToBackend,
    refresh: fetchFromBackend
  };
};

export default useUserData;
