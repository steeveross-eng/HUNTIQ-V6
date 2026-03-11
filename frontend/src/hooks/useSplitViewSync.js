/**
 * useSplitViewSync.js — Hook de synchronisation des cartes Split View
 * V8.1 Split View — Synchronise zoom + pan entre deux MapContainer Leaflet
 *
 * CONTRAT BIONIC:
 * - Deux refs map (left, right) synchronisées en temps réel
 * - Aucun effet de boucle (guard par sourceRef)
 * - Déterministe: même input → même output
 */
import { useRef, useCallback, useEffect } from 'react';

export function useSplitViewSync(enabled) {
  const leftMapRef = useRef(null);
  const rightMapRef = useRef(null);
  const syncingRef = useRef(false); // Guard anti-boucle

  // Sync right → match left
  const syncRightToLeft = useCallback(() => {
    if (syncingRef.current || !leftMapRef.current || !rightMapRef.current) return;
    syncingRef.current = true;
    try {
      const center = leftMapRef.current.getCenter();
      const zoom = leftMapRef.current.getZoom();
      rightMapRef.current.setView(center, zoom, { animate: false });
    } finally {
      syncingRef.current = false;
    }
  }, []);

  // Sync left → match right
  const syncLeftToRight = useCallback(() => {
    if (syncingRef.current || !leftMapRef.current || !rightMapRef.current) return;
    syncingRef.current = true;
    try {
      const center = rightMapRef.current.getCenter();
      const zoom = rightMapRef.current.getZoom();
      leftMapRef.current.setView(center, zoom, { animate: false });
    } finally {
      syncingRef.current = false;
    }
  }, []);

  // Attach/detach event listeners
  useEffect(() => {
    if (!enabled) return;

    const checkAndBind = () => {
      const left = leftMapRef.current;
      const right = rightMapRef.current;
      if (!left || !right) return;

      const onLeftMove = () => syncRightToLeft();
      const onRightMove = () => syncLeftToRight();

      left.on('moveend', onLeftMove);
      left.on('zoomend', onLeftMove);
      right.on('moveend', onRightMove);
      right.on('zoomend', onRightMove);

      return () => {
        left.off('moveend', onLeftMove);
        left.off('zoomend', onLeftMove);
        right.off('moveend', onRightMove);
        right.off('zoomend', onRightMove);
      };
    };

    // Retry binding because maps mount async
    const timer = setTimeout(checkAndBind, 500);
    const cleanup = checkAndBind();
    return () => {
      clearTimeout(timer);
      if (cleanup) cleanup();
    };
  }, [enabled, syncRightToLeft, syncLeftToRight]);

  return { leftMapRef, rightMapRef };
}
