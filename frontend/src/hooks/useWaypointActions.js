/**
 * useWaypointActions.js — Logique CRUD Waypoints & Lieux
 * Extrait de MonTerritoireBionicPage.jsx (IM1.2 Refactorisation)
 *
 * Gère:
 * - Sélection/désélection du waypoint cible
 * - Création (dialog + click carte), suppression
 * - Création/édition/suppression de lieux
 * - Mode click carte
 * - Partage waypoint
 */
import { useState, useCallback, useRef } from 'react';
import { toast } from 'sonner';

const LAST_WAYPOINT_KEY = 'bionic_last_active_waypoint_id';

export function useWaypointActions({
  mapRef,
  mapCenter,
  addWaypoint,
  deleteWaypoint,
  addPlace,
  updatePlace,
  userPosition,
}) {
  // reloadZones est fourni après l'init de l'orchestrateur via bindReloadZones
  const reloadZonesRef = useRef(() => {});
  const bindReloadZones = useCallback((fn) => { reloadZonesRef.current = fn; }, []);
  // State waypoints
  const [selectedWaypointForZones, setSelectedWaypointForZones] = useState(null);
  const [mapClickMode, setMapClickMode] = useState(false);
  const [showAddWaypointDialog, setShowAddWaypointDialog] = useState(false);
  const [newWaypoint, setNewWaypoint] = useState({ name: '', type: 'autre', lat: '', lng: '' });

  // State lieux
  const [showAddPlaceDialog, setShowAddPlaceDialog] = useState(false);
  const [newPlace, setNewPlace] = useState({ name: '', type: 'autre', lat: '', lng: '', notes: '' });
  const [editingPlace, setEditingPlace] = useState(null);

  // State partage
  const [showShareDialog, setShowShareDialog] = useState(false);
  const [waypointToShare, setWaypointToShare] = useState(null);

  // Sélectionner un waypoint comme cible
  const selectWaypointAsTarget = useCallback((waypoint) => {
    setSelectedWaypointForZones(waypoint);
    if (waypoint?.id) localStorage.setItem(LAST_WAYPOINT_KEY, waypoint.id);
    toast.success(`Waypoint actif: ${waypoint.name}`, {
      description: 'Zones BIONIC en cours de chargement'
    });
  }, []);

  // Effacer la cible waypoint — C12 reset complet
  const clearWaypointTarget = useCallback(() => {
    setSelectedWaypointForZones(null);
    localStorage.removeItem(LAST_WAYPOINT_KEY);
    reloadZonesRef.current();
    toast.info('Cible désactivée — zones et corridors nettoyés');
  }, []);

  // Supprimer un waypoint — C12 nettoyage total
  const handleDeleteWaypoint = useCallback((id) => {
    if (selectedWaypointForZones?.id === id) {
      setSelectedWaypointForZones(null);
      localStorage.removeItem(LAST_WAYPOINT_KEY);
    }
    deleteWaypoint(id);
    reloadZonesRef.current();
    toast.info('Waypoint supprimé — zones et corridors nettoyés');
  }, [selectedWaypointForZones, deleteWaypoint]);

  // Ajouter un waypoint (API directe)
  const handleAddWaypoint = useCallback((data) => {
    addWaypoint({
      name: data.name || 'Nouveau waypoint',
      lat: parseFloat(data.lat) || mapCenter[0],
      lng: parseFloat(data.lng) || mapCenter[1],
      type: data.type || 'autre',
      active: true
    });
  }, [mapCenter, addWaypoint]);

  // Ajouter un waypoint depuis le dialog
  const handleAddWaypointFromDialog = useCallback(() => {
    if (!newWaypoint.name) {
      toast.error('Veuillez entrer un nom');
      return;
    }
    const wpLat = parseFloat(newWaypoint.lat) || mapCenter[0];
    const wpLng = parseFloat(newWaypoint.lng) || mapCenter[1];
    const wpData = { name: newWaypoint.name, lat: wpLat, lng: wpLng, type: newWaypoint.type || 'autre', active: true };
    addWaypoint(wpData);
    setSelectedWaypointForZones({ ...wpData, id: `temp-${Date.now()}` });
    localStorage.setItem(LAST_WAYPOINT_KEY, `temp-${Date.now()}`);
    if (mapRef.current) mapRef.current.setView([wpLat, wpLng], 14);
    setNewWaypoint({ name: '', type: 'autre', lat: '', lng: '' });
    setShowAddWaypointDialog(false);
    toast.success('Waypoint créé — zones en cours de génération');
  }, [newWaypoint, mapCenter, addWaypoint, mapRef]);

  // Click carte → pré-remplir coords et ouvrir dialog
  const handleMapClickForWaypoint = useCallback((lat, lng) => {
    setNewWaypoint(prev => ({ ...prev, lat: lat.toFixed(6), lng: lng.toFixed(6) }));
    setShowAddWaypointDialog(true);
    setMapClickMode(false);
    toast.info('Coordonnées capturées !', { description: `Lat: ${lat.toFixed(4)}, Lng: ${lng.toFixed(4)}` });
  }, []);

  // Utiliser position GPS pour nouveau waypoint
  const useCurrentPositionForNewWaypoint = useCallback(() => {
    if (userPosition) {
      setNewWaypoint(prev => ({ ...prev, lat: userPosition.lat.toFixed(6), lng: userPosition.lng.toFixed(6) }));
    } else {
      navigator.geolocation.getCurrentPosition(
        (pos) => setNewWaypoint(prev => ({ ...prev, lat: pos.coords.latitude.toFixed(6), lng: pos.coords.longitude.toFixed(6) })),
        () => toast.error('Impossible d\'obtenir votre position')
      );
    }
  }, [userPosition]);

  // Utiliser position GPS pour nouveau lieu
  const useCurrentPositionForNewPlace = useCallback(() => {
    if (userPosition) {
      setNewPlace(prev => ({ ...prev, lat: userPosition.lat.toFixed(6), lng: userPosition.lng.toFixed(6) }));
    } else {
      navigator.geolocation.getCurrentPosition(
        (pos) => setNewPlace(prev => ({ ...prev, lat: pos.coords.latitude.toFixed(6), lng: pos.coords.longitude.toFixed(6) })),
        () => toast.error('Impossible d\'obtenir votre position')
      );
    }
  }, [userPosition]);

  // Ajouter un lieu
  const handleAddPlace = useCallback(() => {
    if (!newPlace.name) { toast.error('Veuillez entrer un nom'); return; }
    addPlace({
      name: newPlace.name,
      lat: parseFloat(newPlace.lat) || mapCenter[0],
      lng: parseFloat(newPlace.lng) || mapCenter[1],
      type: newPlace.type,
      notes: newPlace.notes
    });
    setNewPlace({ name: '', type: 'autre', lat: '', lng: '', notes: '' });
    setShowAddPlaceDialog(false);
  }, [newPlace, mapCenter, addPlace]);

  // Modifier un lieu
  const handleUpdatePlace = useCallback(() => {
    if (!editingPlace) return;
    updatePlace(editingPlace.id, { name: editingPlace.name, type: editingPlace.type, notes: editingPlace.notes });
    setEditingPlace(null);
  }, [editingPlace, updatePlace]);

  // Partage
  const openShareDialog = useCallback((waypoint) => {
    setWaypointToShare(waypoint);
    setShowShareDialog(true);
  }, []);

  return {
    // Waypoint state
    selectedWaypointForZones, setSelectedWaypointForZones,
    mapClickMode, setMapClickMode,
    showAddWaypointDialog, setShowAddWaypointDialog,
    newWaypoint, setNewWaypoint,
    // Place state
    showAddPlaceDialog, setShowAddPlaceDialog,
    newPlace, setNewPlace,
    editingPlace, setEditingPlace,
    // Share state
    showShareDialog, setShowShareDialog,
    waypointToShare, setWaypointToShare,
    // Actions
    selectWaypointAsTarget,
    clearWaypointTarget,
    handleDeleteWaypoint,
    handleAddWaypoint,
    handleAddWaypointFromDialog,
    handleMapClickForWaypoint,
    useCurrentPositionForNewWaypoint,
    useCurrentPositionForNewPlace,
    handleAddPlace,
    handleUpdatePlace,
    openShareDialog,
    // Late-binding
    bindReloadZones,
  };
}
