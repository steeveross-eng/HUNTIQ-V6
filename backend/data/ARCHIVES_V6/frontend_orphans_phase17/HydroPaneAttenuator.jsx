/**
 * HydroPaneAttenuator.jsx
 * 
 * BIONIC V5 300% — Processeur canvas pour couche hydrographique
 * 
 * RÔLE :
 *   Transforme les tuiles NFIS-QC.hydro en ne conservant QUE les tracés
 *   linéaires (rivières, ruisseaux) et en éliminant les zones remplies
 *   (lacs, plans d'eau) qui dominent visuellement les zones BIONIC.
 * 
 * TECHNIQUE :
 *   1. Accède au pane bionicHydroPane
 *   2. Rend les tuiles hydro invisibles (opacity 0)
 *   3. Superpose un L.GridLayer canvas qui charge les mêmes tuiles,
 *      applique une érosion morphologique pour extraire les contours,
 *      et affiche uniquement les lignes fines
 * 
 * CONTRAINTES :
 *   - NE modifie PAS HydrographyOverlayLayer.jsx
 *   - Composant ISOLÉ, CONFINÉ et RÉVERSIBLE
 *   - Auto-nettoyé au démontage
 */

import { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

const HYDRO_PANE = 'bionicHydroPane';
const EDGE_PANE = 'bionicHydroEdgePane';
const EDGE_PANE_Z = 351;

/**
 * Morphological edge extraction on ImageData
 * Keeps only pixels adjacent to transparent pixels (boundary detection)
 */
function extractEdges(imgData, width, height, thickness) {
  const src = imgData.data;
  const out = new Uint8ClampedArray(src.length);
  const t = thickness;

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const idx = (y * width + x) * 4;
      const a = src[idx + 3];
      if (a < 50) continue; // transparent pixel, skip

      // Check if any neighbor within radius t is transparent
      let isEdge = false;
      for (let dy = -t; dy <= t && !isEdge; dy++) {
        for (let dx = -t; dx <= t && !isEdge; dx++) {
          if (dx === 0 && dy === 0) continue;
          const nx = x + dx, ny = y + dy;
          if (nx < 0 || nx >= width || ny < 0 || ny >= height) {
            isEdge = true; // tile border = edge
          } else {
            const nIdx = (ny * width + nx) * 4;
            if (src[nIdx + 3] < 50) isEdge = true;
          }
        }
      }

      if (isEdge) {
        out[idx]     = 30;   // R - subtle dark blue
        out[idx + 1] = 100;  // G
        out[idx + 2] = 180;  // B
        out[idx + 3] = 160;  // A - semi-transparent
      }
    }
  }
  return new ImageData(out, width, height);
}

const HydroPaneAttenuator = () => {
  const map = useMap();
  const layerRef = useRef(null);

  useEffect(() => {
    // 1. Hide original hydro tiles (they still load for data, just invisible)
    const hydroPane = map.getPane(HYDRO_PANE);
    if (hydroPane) {
      hydroPane.style.opacity = '0';
    }

    // 2. Create edge pane
    if (!map.getPane(EDGE_PANE)) {
      map.createPane(EDGE_PANE);
      const ep = map.getPane(EDGE_PANE);
      ep.style.zIndex = EDGE_PANE_Z;
      ep.style.pointerEvents = 'none';
    }

    // 3. Create custom GridLayer that loads hydro tiles and extracts edges
    const API_BASE = process.env.REACT_APP_BACKEND_URL || '';
    const proxyUrl = `${API_BASE}/api/wms-proxy/tile`;

    const EdgeLayer = L.GridLayer.extend({
      createTile(coords, done) {
        const tile = document.createElement('canvas');
        const size = this.getTileSize();
        tile.width = size.x;
        tile.height = size.y;

        const nwPoint = coords.scaleBy(size);
        const sePoint = nwPoint.add(size);
        const nw = map.options.crs.pointToLatLng(nwPoint, coords.z);
        const se = map.options.crs.pointToLatLng(sePoint, coords.z);

        // Project to EPSG:3857
        const nwM = L.CRS.EPSG3857.project(nw);
        const seM = L.CRS.EPSG3857.project(se);
        const bbox = `${nwM.x},${seM.y},${seM.x},${nwM.y}`;

        const params = new URLSearchParams({
          service: 'WMS',
          request: 'GetMap',
          layers: 'NFIS-QC.hydro',
          format: 'image/png',
          transparent: 'true',
          version: '1.1.1',
          url: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
          width: size.x,
          height: size.y,
          srs: 'EPSG:3857',
          bbox: bbox,
        });

        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => {
          const ctx = tile.getContext('2d');
          ctx.drawImage(img, 0, 0);
          try {
            const imgData = ctx.getImageData(0, 0, size.x, size.y);
            const edges = extractEdges(imgData, size.x, size.y, 2);
            ctx.clearRect(0, 0, size.x, size.y);
            ctx.putImageData(edges, 0, 0);
          } catch (e) {
            // CORS or security error — render original at low opacity
            ctx.clearRect(0, 0, size.x, size.y);
            ctx.globalAlpha = 0.15;
            ctx.drawImage(img, 0, 0);
          }
          done(null, tile);
        };
        img.onerror = () => done(null, tile);
        img.src = `${proxyUrl}?${params.toString()}`;

        return tile;
      }
    });

    const edgeLayer = new EdgeLayer({
      pane: EDGE_PANE,
      tileSize: 256,
      keepBuffer: 4,
      updateWhenZooming: false,
      updateWhenIdle: true,
    });

    edgeLayer.addTo(map);
    layerRef.current = edgeLayer;

    return () => {
      // Cleanup: restore original hydro pane, remove edge layer
      const hp = map.getPane(HYDRO_PANE);
      if (hp) {
        hp.style.opacity = '';
      }
      if (layerRef.current) {
        map.removeLayer(layerRef.current);
        layerRef.current = null;
      }
    };
  }, [map]);

  return null;
};

export default HydroPaneAttenuator;
