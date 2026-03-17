/**
 * BionicCorridorsV10Layer.jsx — Couche corridors fauniques BIONIC
 * Norme CORRIDOR-V1/V10 officielle
 *
 * Palette normative obligatoire:
 *   CRITIQUE  #CC0000 (4m)  — rayé
 *   MAJEUR    #FF0000 (6m)
 *   FORT      #FF8C00 (11m)
 *   MODERE    #FFD700 (17m)
 *   FAIBLE    #BFBFBF (26m)
 *
 * Lissage contrôlé, continuité visible, aucune rupture.
 * Filtrage dynamique par espèce.
 */
import { useEffect, useRef, useCallback, useState } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const CORRIDOR_PALETTE = {
  CRITIQUE: { color: '#CC0000', weight: 6, dashArray: '10,4', label: 'Critique' },
  MAJEUR:   { color: '#FF0000', weight: 5, dashArray: null,   label: 'Majeur' },
  FORT:     { color: '#FF8C00', weight: 4, dashArray: null,   label: 'Fort' },
  MODERE:   { color: '#FFD700', weight: 3, dashArray: null,   label: 'Modéré' },
  FAIBLE:   { color: '#BFBFBF', weight: 2, dashArray: null,   label: 'Faible' },
};

const ZONE_COLORS = {
  alimentation: '#4CAF50',
  repos: '#2196F3',
  rut: '#FF5722',
  eau: '#00BCD4',
};

const SPECIES_MAP = {
  orignal: 'ORIGNAL',
  chevreuil: 'CERF',
  ours_noir: 'OURS',
  dindon_sauvage: 'DINDON',
  wapiti: 'WAPITI',
  tous: 'CERF',
};

const BionicCorridorsV10Layer = ({
  center,
  species = 'cerf',
  month = 10,
  enabled = true,
  opacity = 0.85,
}) => {
  const map = useMap();
  const layerGroupRef = useRef(null);
  const abortRef = useRef(null);
  const [loading, setLoading] = useState(false);

  const clearLayers = useCallback(() => {
    if (layerGroupRef.current) {
      map.removeLayer(layerGroupRef.current);
      layerGroupRef.current = null;
    }
  }, [map]);

  const fetchAndRender = useCallback(async () => {
    if (!center || !enabled) {
      clearLayers();
      return;
    }

    if (abortRef.current) abortRef.current.abort();
    abortRef.current = new AbortController();

    const sp = SPECIES_MAP[species] || 'CERF';
    const apiUrl = process.env.REACT_APP_BACKEND_URL;

    setLoading(true);
    try {
      const res = await fetch(`${apiUrl}/api/v10/corridors/analyze-full`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          center_lat: center.lat,
          center_lng: center.lng,
          species: sp,
          month,
        }),
        signal: abortRef.current.signal,
      });

      if (!res.ok) return;
      const data = await res.json();

      clearLayers();

      const group = L.layerGroup();
      const features = data.geojson?.features || [];

      // Trier: FAIBLE en bas, CRITIQUE en haut (z-order)
      const levelOrder = { FAIBLE: 0, MODERE: 1, FORT: 2, MAJEUR: 3, CRITIQUE: 4 };
      const corridorFeatures = features
        .filter(f => f.geometry.type === 'LineString')
        .sort((a, b) => (levelOrder[a.properties.niveau] || 0) - (levelOrder[b.properties.niveau] || 0));

      const zoneFeatures = features.filter(f => f.geometry.type === 'Point');

      // Rendu des corridors
      corridorFeatures.forEach(feature => {
        const coords = feature.geometry.coordinates.map(c => [c[1], c[0]]);
        if (coords.length < 2) return;

        const props = feature.properties;
        const palette = CORRIDOR_PALETTE[props.niveau] || CORRIDOR_PALETTE.FORT;

        // Lissage: simplifier pour lisibilité
        const smoothed = smoothPath(coords);

        // Ligne de fond (glow)
        const glowLine = L.polyline(smoothed, {
          color: palette.color,
          weight: palette.weight + 3,
          opacity: opacity * 0.25,
          lineCap: 'round',
          lineJoin: 'round',
          interactive: false,
        });
        group.addLayer(glowLine);

        // Ligne principale
        const mainLine = L.polyline(smoothed, {
          color: palette.color,
          weight: palette.weight,
          opacity: opacity,
          lineCap: 'round',
          lineJoin: 'round',
          dashArray: palette.dashArray,
        });

        mainLine.bindTooltip(
          `<div style="font-size:12px;font-weight:600;color:${palette.color}">
            ${palette.label} (${props.score}/100)
          </div>
          <div style="font-size:11px;color:#555">
            ${props.from_type} → ${props.to_type}<br/>
            Largeur: ${props.largeur_m}m
          </div>`,
          { sticky: true, opacity: 0.95 }
        );

        mainLine.on('mouseover', function() { this.setStyle({ weight: palette.weight + 2, opacity: 1 }); });
        mainLine.on('mouseout', function() { this.setStyle({ weight: palette.weight, opacity: opacity }); });

        group.addLayer(mainLine);
      });

      // Rendu des zones écologiques
      zoneFeatures.forEach(feature => {
        const [lng, lat] = feature.geometry.coordinates;
        const props = feature.properties;
        const zoneColor = ZONE_COLORS[props.zone_type] || '#9E9E9E';

        const circle = L.circleMarker([lat, lng], {
          radius: 4,
          fillColor: zoneColor,
          color: '#fff',
          weight: 1.5,
          fillOpacity: 0.8,
          opacity: 0.9,
        });

        circle.bindTooltip(
          `<div style="font-size:11px;font-weight:600;color:${zoneColor}">
            ${props.zone_type.charAt(0).toUpperCase() + props.zone_type.slice(1)}
          </div>`,
          { sticky: true }
        );

        group.addLayer(circle);
      });

      group.addTo(map);
      layerGroupRef.current = group;
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.error('[CORRIDORS-V10] Erreur:', err);
      }
    } finally {
      setLoading(false);
    }
  }, [center, species, month, enabled, opacity, map, clearLayers]);

  useEffect(() => {
    fetchAndRender();
    return () => {
      if (abortRef.current) abortRef.current.abort();
      clearLayers();
    };
  }, [fetchAndRender]);

  useEffect(() => {
    if (!enabled) clearLayers();
  }, [enabled, clearLayers]);

  return loading ? (
    <div
      data-testid="corridors-v10-loading"
      style={{
        position: 'absolute', top: 12, right: 12, zIndex: 1000,
        background: 'rgba(0,0,0,0.7)', color: '#FF8C00',
        padding: '4px 10px', borderRadius: 6, fontSize: 11, fontWeight: 600,
      }}
    >
      Corridors V10...
    </div>
  ) : null;
};

/**
 * Lissage de chemin: Douglas-Peucker simplifié + interpolation
 * Réduit le bruit des chemins A* cellule-par-cellule
 */
function smoothPath(coords) {
  if (coords.length <= 3) return coords;

  // Sous-échantillonnage adaptatif: garder 1 point sur N
  const step = Math.max(1, Math.floor(coords.length / 60));
  const sampled = [];
  for (let i = 0; i < coords.length; i += step) {
    sampled.push(coords[i]);
  }
  // Toujours inclure le dernier point
  if (sampled[sampled.length - 1] !== coords[coords.length - 1]) {
    sampled.push(coords[coords.length - 1]);
  }

  return sampled;
}

export default BionicCorridorsV10Layer;
export { CORRIDOR_PALETTE };
