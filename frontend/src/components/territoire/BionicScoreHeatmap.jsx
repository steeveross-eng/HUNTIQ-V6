/**
 * BionicScoreHeatmap — Heatmap écologique officiel BIONIC
 * Couche principale unique basée sur le score consolidé
 * Palette: bleu (faible) → vert (modéré) → jaune (bon) → rouge (optimal)
 * Conforme BCE-4X + Steeve-MAX
 */
import { useEffect, useRef, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';

const HEATMAP_GRADIENT = {
  0.0:  '#1E3A5F',  // Bleu profond - faible
  0.15: '#2563EB',  // Bleu - faible+
  0.30: '#16A34A',  // Vert - modéré
  0.45: '#22C55E',  // Vert clair - modéré+
  0.60: '#EAB308',  // Jaune - bon
  0.75: '#F59E0B',  // Ambre - bon+
  0.85: '#EF4444',  // Rouge - optimal
  1.0:  '#DC2626',  // Rouge vif - optimal+
};

export const BionicScoreHeatmap = ({
  center,
  species = 'cerf',
  month = 10,
  enabled = true,
  opacity = 0.55,
}) => {
  const map = useMap();
  const layerRef = useRef(null);
  const abortRef = useRef(null);

  const fetchHeatmap = useCallback(async () => {
    if (!center || !enabled) return;

    // Annuler la requête précédente
    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();

    const speciesMap = {
      orignal: 'ORIGNAL', chevreuil: 'CERF', ours_noir: 'OURS',
      dindon_sauvage: 'DINDON', wapiti: 'WAPITI', tous: 'CERF',
    };
    const sp = speciesMap[species] || 'CERF';
    const apiUrl = process.env.REACT_APP_BACKEND_URL;

    try {
      const res = await fetch(
        `${apiUrl}/api/v1/score-consolide/heatmap?lat=${center.lat}&lng=${center.lng}&species=${sp}&month=${month}&grid_size=20`,
        { signal: abortRef.current.signal }
      );
      if (!res.ok) return;
      const data = await res.json();

      // Nettoyer ancien layer
      if (layerRef.current) {
        map.removeLayer(layerRef.current);
        layerRef.current = null;
      }

      // Convertir les points en format heatmap [lat, lng, intensity]
      const heatData = data.points.map(p => [
        p.lat, p.lng, p.score / 100.0
      ]);

      if (heatData.length === 0) return;

      const heatLayer = L.heatLayer(heatData, {
        radius: 35,
        blur: 25,
        maxZoom: 17,
        max: 1.0,
        minOpacity: opacity * 0.3,
        gradient: HEATMAP_GRADIENT,
      });

      heatLayer.addTo(map);
      layerRef.current = heatLayer;

    } catch (e) {
      if (e.name !== 'AbortError') {
        console.error('[BionicScoreHeatmap] Error:', e);
      }
    }
  }, [center, species, month, enabled, map, opacity]);

  useEffect(() => {
    if (enabled && center) {
      fetchHeatmap();
    } else if (layerRef.current) {
      map.removeLayer(layerRef.current);
      layerRef.current = null;
    }

    return () => {
      if (layerRef.current) {
        try { map.removeLayer(layerRef.current); } catch (e) {}
        layerRef.current = null;
      }
      if (abortRef.current) abortRef.current.abort();
    };
  }, [enabled, center, species, month, fetchHeatmap, map]);

  return null;
};
