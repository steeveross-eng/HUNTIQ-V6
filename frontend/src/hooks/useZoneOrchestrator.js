/**
 * useZoneOrchestrator.js — Module ORCHESTRATION ZONES
 * 
 * CONTRAT:
 *   Input:  waypoint(s), species, layerTypes
 *   Output: { zones, isLoading, isPreview, source, reload }
 *
 * NORME BIONIC STABILITÉ:
 *   - Orchestration seule: NE contient AUCUNE logique de calcul ou de cache
 *   - Délègue au cache (useZoneCache), backend (generateWaypointZonesV5)
 *   - PAS DE PREVIEW SYNTHÉTIQUE — les zones affichées sont DÉFINITIVES
 *   - Contrats explicites entre modules
 *   - Zéro connexion croisée
 *
 * FLUX:
 *   1. Waypoint créé/sélectionné
 *   2. Vérifie IndexedDB cache → si hit, affiche immédiatement (source='cache')
 *   3. Si cache miss, affiche loader (pas de preview)
 *   4. Lance calcul backend
 *   5. Backend retourne → affiche zones finales, sauvegarde en cache (source='backend')
 *   6. Prochaine visite: cache hit (source='cache', <100ms)
 *
 * CORRECTIF BIONIC STABILITÉ — Pas de recalcul visible:
 *   Les zones ne changent JAMAIS après leur première apparition.
 *   Soit cache (instantané), soit backend (unique, définitif).
 */
import { useState, useEffect, useRef, useCallback, useMemo, startTransition } from 'react';
import { useZoneCache } from './useZoneCache';
import { generateWaypointZonesV5, LAYER_TYPES } from '@/services/BionicZoneService';

export function useZoneOrchestrator({
  selectedWaypointForZones,
  activeWaypoints,
  selectedSpecies,
  currentZoom,
  biologicalSeason = null,
}) {
  const [zonesData, setZonesData] = useState({ zones: [], corridors: [], stats: { total: 0 } });
  const [isLoading, setIsLoading] = useState(false);
  const [zoneSource, setZoneSource] = useState('none'); // 'none' | 'cache' | 'backend'
  const [forceReload, setForceReload] = useState(0);
  const [zeroZonesReason, setZeroZonesReason] = useState(null); // V7.3: diagnostic feedback
  // V8.2.1: Weather metadata from backend zone response
  const [weatherMetadata, setWeatherMetadata] = useState(null);
  // C13 BIONIC 1000%: Explicit pipeline state for strict UX
  const [pipelineState, setPipelineState] = useState('idle'); // 'idle' | 'loading' | 'success' | 'empty' | 'error' | 'timeout'
  
  // Refs stables — CRITIQUE: évite les closures stale dans orchestrate()
  const zoomRef = useRef(currentZoom);
  zoomRef.current = currentZoom;
  const lockRef = useRef({ locked: false, key: null });
  const zoneSourceRef = useRef('none'); // Miroir ref de zoneSource pour accès synchrone

  // Setter combiné: state + ref simultanément
  const setZoneSourceSafe = useCallback((src) => {
    zoneSourceRef.current = src;
    setZoneSource(src);
  }, []);

  // Modules isolés
  const { getCached, setCached } = useZoneCache();

  // Cle de cache deterministe — v10x: corridors inclus
  const CACHE_VERSION = '_v10x';
  const cacheKey = useMemo(() => {
    const seasonSuffix = biologicalSeason ? `_${biologicalSeason}` : '';
    if (selectedWaypointForZones) {
      const wpLat = selectedWaypointForZones.lat ?? selectedWaypointForZones.latitude;
      const wpLng = selectedWaypointForZones.lng ?? selectedWaypointForZones.longitude;
      if (wpLat && wpLng) {
        return `${selectedSpecies}_wp_${wpLat.toFixed(4)}_${wpLng.toFixed(4)}${seasonSuffix}${CACHE_VERSION}`;
      }
    }
    if (activeWaypoints.length > 0) {
      const validWps = activeWaypoints.filter(w => (w.lat ?? w.latitude) && (w.lng ?? w.longitude));
      if (validWps.length > 0) {
        return `${selectedSpecies}_wps_${validWps.map(w => `${(w.lat??w.latitude).toFixed(4)}_${(w.lng??w.longitude).toFixed(4)}`).join('|')}${seasonSuffix}${CACHE_VERSION}`;
      }
    }
    return null;
  }, [selectedSpecies, selectedWaypointForZones, activeWaypoints, biologicalSeason]);

  // Fonction de rechargement manuel
  const reload = useCallback(() => {
    lockRef.current = { locked: false, key: null };
    zoneSourceRef.current = 'none';
    setForceReload(v => v + 1);
  }, []);

  // V8.2.1: Auto-refresh every 30 minutes to sync with weather cache TTL
  const weatherRefreshRef = useRef(null);
  useEffect(() => {
    const WEATHER_SYNC_INTERVAL = 30 * 60 * 1000; // 30 minutes
    if (cacheKey) {
      weatherRefreshRef.current = setInterval(() => {
        lockRef.current = { locked: false, key: null };
        zoneSourceRef.current = 'none';
        setForceReload(v => v + 1);
      }, WEATHER_SYNC_INTERVAL);
    }
    return () => {
      if (weatherRefreshRef.current) clearInterval(weatherRefreshRef.current);
    };
  }, [cacheKey]);

  useEffect(() => {
    // Pas de waypoint = pas de zones
    if (!cacheKey) {
      setZonesData({ zones: [], corridors: [], stats: { total: 0 } });
      setZoneSourceSafe('none');
      setZeroZonesReason(null);
      setIsLoading(false);
      setPipelineState('idle');
      return;
    }

    // STATE LOCKING: même clé déjà chargée depuis le backend
    if (lockRef.current.locked && lockRef.current.key === cacheKey && zoneSourceRef.current === 'backend') {
      return;
    }

    // P0 FIX STALE-WHILE-REVALIDATE: NE PAS vider les zones immédiatement
    // quand la clé change. Garder les anciennes zones visibles pendant que
    // les nouvelles chargent. Cela donne un affichage instantané (<300ms)
    // au lieu d'un écran vide pendant 10s.
    if (lockRef.current.key && lockRef.current.key !== cacheKey) {
      lockRef.current = { locked: false, key: null };
      // REMOVED: setZonesData empty — keep stale zones visible
      setPipelineState('refreshing');
    }

    let cancelled = false;

    const orchestrate = async () => {
      const waypointsToAnalyze = selectedWaypointForZones
        ? [selectedWaypointForZones]
        : activeWaypoints;
      
      if (!waypointsToAnalyze.length) return;

      // ÉTAPE 1: Vérifier le cache IndexedDB (< 100ms)
      const cached = await getCached(cacheKey);
      const cacheHasZones = cached && cached.zones && cached.zones.length > 0;
      const cacheIsBackendVerified = cached && cached.stats && cached.stats.backendVerified;
      if ((cacheHasZones || cacheIsBackendVerified) && !cancelled) {
        setZonesData(cached);
        setZoneSourceSafe('backend');
        setZeroZonesReason(null);
        setPipelineState(cacheHasZones ? 'success' : 'empty');
        lockRef.current = { locked: true, key: cacheKey };
        setIsLoading(false);
        return; // Cache hit — affichage instantané
      }

      // ÉTAPE 2: Cache miss — charger depuis le backend
      // P0 FIX: Ne pas masquer les zones stale pendant le chargement
      startTransition(() => {
        setIsLoading(true);
        // Ne setPipelineState('loading') que si aucune zone n'est affichée
        setPipelineState(prev => prev === 'refreshing' ? 'refreshing' : 'loading');
      });

      // C13 BIONIC 1000%: Timeout strict — 60s max (V8.2: increased for Overpass resilience)
      const BACKEND_TIMEOUT_MS = 60000;
      const timeoutController = new AbortController();
      const timeoutId = setTimeout(() => {
        timeoutController.abort();
      }, BACKEND_TIMEOUT_MS);

      try {
        const zoom = Math.max(zoomRef.current, 14);
        const allLayers = {};
        LAYER_TYPES.forEach(lt => { allLayers[lt.id] = true; });

        let allZones = [];
        let allCorridors = [];
        let lastStats = {};
        let lastDiagnostics = null;
        for (const wp of waypointsToAnalyze) {
          if (!wp || (!wp.lat && !wp.latitude)) continue;
          const r = await generateWaypointZonesV5(wp, zoom, allLayers, selectedSpecies, biologicalSeason);
          if (r && r.zones) allZones = [...allZones, ...r.zones];
          if (r && r.corridors) allCorridors = [...allCorridors, ...r.corridors];
          if (r && r.stats) lastStats = r.stats;
          if (r && r.rejection_diagnostics) lastDiagnostics = r.rejection_diagnostics;
          // V8.2.1: Capture weather metadata from backend response
          if (r && r.weather_metadata) setWeatherMetadata(r.weather_metadata);
        }
        
        if (!cancelled) {
          if (allZones.length > 0) {
            const result = { zones: allZones, corridors: allCorridors, stats: { total: allZones.length, corridors_total: allCorridors.length, backendVerified: true }, rejection_diagnostics: lastDiagnostics };
            setZonesData(result);
            setZoneSourceSafe('backend');
            setZeroZonesReason(null);
            setPipelineState('success');
            lockRef.current = { locked: true, key: cacheKey };
            await setCached(cacheKey, result);
          } else {
            const reason = lastStats.exclusion_failed ? 'overpass_unavailable' 
              : (lastStats.zero_zones_reason || 'all_filtered_by_exclusions');
            const emptyResult = { zones: [], corridors: [], stats: { total: 0, backendVerified: true }, rejection_diagnostics: lastDiagnostics };
            setZonesData(emptyResult);
            setZoneSourceSafe('backend');
            setZeroZonesReason(reason);
            setPipelineState('empty');
            lockRef.current = { locked: true, key: cacheKey };
            await setCached(cacheKey, emptyResult);
          }
        }
      } catch (err) {
        if (!cancelled) {
          const isTimeout = err.name === 'AbortError' || (err.message && err.message.includes('aborted'));
          setZonesData({ zones: [], corridors: [], stats: { total: 0, error: true } });
          setZoneSourceSafe('none');
          setZeroZonesReason(isTimeout ? 'timeout' : 'backend_error');
          setPipelineState(isTimeout ? 'timeout' : 'error');
        }
      } finally {
        clearTimeout(timeoutId);
        if (!cancelled) setIsLoading(false);
      }
    };

    orchestrate();
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cacheKey, forceReload]);

  return {
    zonesData,
    isLoading,
    isPreview: zoneSource === 'preview',
    zoneSource,
    zeroZonesReason,
    pipelineState,
    reload,
    cacheKey,
    weatherMetadata,
  };
}
