/**
 * useGeolocation.js — Hook de géolocalisation pour Mon Territoire BIONIC
 * Extrait de MonTerritoireBionicPage.jsx (IM1 Refactorisation)
 */
import { useState, useCallback, useRef } from 'react';
import { toast } from 'sonner';

export function useGeolocation(mapRef) {
  const [userPosition, setUserPosition] = useState(null);
  const [watchingPosition, setWatchingPosition] = useState(false);
  const watchIdRef = useRef(null);

  const startWatchingPosition = useCallback(() => {
    if (!navigator.geolocation) {
      toast.error('Géolocalisation non supportée');
      return;
    }
    setWatchingPosition(true);
    watchIdRef.current = navigator.geolocation.watchPosition(
      (position) => {
        const { latitude, longitude, accuracy } = position.coords;
        setUserPosition({ lat: latitude, lng: longitude, accuracy });
        toast.success('Position mise à jour', { description: `Précision: ${Math.round(accuracy)}m` });
      },
      (error) => {
        toast.error('Erreur de géolocalisation', { description: error.message });
        setWatchingPosition(false);
      },
      { enableHighAccuracy: true, maximumAge: 10000, timeout: 10000 }
    );
  }, []);

  const stopWatchingPosition = useCallback(() => {
    if (watchIdRef.current) {
      navigator.geolocation.clearWatch(watchIdRef.current);
      watchIdRef.current = null;
    }
    setWatchingPosition(false);
  }, []);

  const centerOnUser = useCallback(() => {
    if (userPosition) {
      if (mapRef.current) mapRef.current.setView([userPosition.lat, userPosition.lng], 14);
    } else {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setUserPosition({ lat: latitude, lng: longitude });
          if (mapRef.current) mapRef.current.setView([latitude, longitude], 14);
          toast.success('Centré sur votre position');
        },
        () => toast.error('Impossible d\'obtenir votre position')
      );
    }
  }, [userPosition, mapRef]);

  return { userPosition, setUserPosition, watchingPosition, startWatchingPosition, stopWatchingPosition, centerOnUser };
}
