/**
 * useSplitViewZones.js — Hook pour charger les zones de la carte droite (Split View)
 * V8.1 — Charge les zones avec une saison biologique différente
 *
 * CONTRAT BIONIC:
 * - Appel backend uniquement quand split view est actif ET saison droite ≠ gauche
 * - Cache IndexedDB séparé (clé inclut la saison)
 * - Nettoyage à la désactivation du split view
 */
import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { generateWaypointZonesV5, LAYER_TYPES } from '@/services/BionicZoneService';

export function useSplitViewZones({
  enabled,
  selectedWaypointForZones,
  activeWaypoints,
  selectedSpecies,
  currentZoom,
  biologicalSeason,
}) {
  const [zonesData, setZonesData] = useState({ zones: [], corridors: [], stats: {} });
  const [isLoading, setIsLoading] = useState(false);
  const cancelRef = useRef(false);

  // V8.2 PERF: Stable cache key to prevent spurious re-fetches
  const splitCacheKey = useMemo(() => {
    if (!enabled || !biologicalSeason) return null;
    const wp = selectedWaypointForZones;
    if (wp) return `split_${wp.lat?.toFixed(4)}_${wp.lng?.toFixed(4)}_${selectedSpecies}_${biologicalSeason}`;
    if (activeWaypoints.length > 0) {
      return `split_multi_${activeWaypoints.map(w => `${(w.lat||w.latitude)?.toFixed(4)}_${(w.lng||w.longitude)?.toFixed(4)}`).join('|')}_${selectedSpecies}_${biologicalSeason}`;
    }
    return null;
  }, [enabled, selectedWaypointForZones, activeWaypoints, selectedSpecies, biologicalSeason]);

  useEffect(() => {
    if (!splitCacheKey) {
      setZonesData({ zones: [], corridors: [], stats: {} });
      return;
    }

    let cancelled = false;

    const loadZones = async () => {
      const waypointsToAnalyze = selectedWaypointForZones
        ? [selectedWaypointForZones]
        : activeWaypoints.filter(w => w.active !== false);

      if (waypointsToAnalyze.length === 0) return;

      setIsLoading(true);
      try {
        const zoom = Math.max(currentZoom, 14);
        const allLayers = {};
        LAYER_TYPES.forEach(lt => { allLayers[lt.id] = true; });
        const allZones = [];
        const allCorridors = [];

        for (const wp of waypointsToAnalyze) {
          if (cancelled) break;
          const result = await generateWaypointZonesV5(wp, zoom, allLayers, selectedSpecies, biologicalSeason);
          if (result?.zones) allZones.push(...result.zones);
          if (result?.corridors) allCorridors.push(...result.corridors);
        }

        if (!cancelled) {
          setZonesData({ zones: allZones, corridors: allCorridors, stats: { total: allZones.length } });
        }
      } catch (err) {
        console.error('[SplitView] Zone loading error:', err);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    loadZones();
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [splitCacheKey]);

  return { zonesData, isLoading };
}
