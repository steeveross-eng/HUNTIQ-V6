/**
 * HydrographyOverlayLayer.jsx
 * 
 * BIONIC V5 300% — Couche hydrographique ISOLÉE
 * Overlay indépendant pour rivières et zones d'eau (NFIS-QC.hydro)
 * 
 * HIÉRARCHIE DE RENDU GARANTIE :
 *   1. Couches scientifiques (NDVI, pente, etc.)  → tilePane     (z=200)
 *   2. Hydrographie (cette couche)                 → hydroPane    (z=350)
 *   3. Zones BIONIC                                → overlayPane  (z=400)
 * 
 * CONTRAINTES RESPECTÉES :
 * - Composant ISOLÉ, CONFINÉ et RÉVERSIBLE
 * - Aucune modification aux composants stables existants
 * - Utilise un pane Leaflet dédié pour contrôle z-index absolu
 * - Opacité contrôlée, continuité du tracé, style stable
 */

import React, { useState, useMemo, useEffect, useRef } from 'react';
import { WMSTileLayer, useMap } from 'react-leaflet';

const HYDRO_PANE_NAME = 'bionicHydroPane';
const HYDRO_PANE_ZINDEX = 350;

const HYDRO_WMS_CONFIG = {
  serviceUrl: 'https://ca.nfis.org/cubewerx/cubeserv?DATASTORE=NFIS-QC',
  layer: 'NFIS-QC.hydro',
  format: 'image/png',
};

/**
 * Sous-composant utilitaire : crée le pane Leaflet dédié une seule fois
 */
const HydroPaneCreator = () => {
  const map = useMap();

  useEffect(() => {
    if (!map.getPane(HYDRO_PANE_NAME)) {
      map.createPane(HYDRO_PANE_NAME);
      const pane = map.getPane(HYDRO_PANE_NAME);
      pane.style.zIndex = HYDRO_PANE_ZINDEX;
      pane.style.pointerEvents = 'none';
    }
  }, [map]);

  return null;
};

/**
 * Couche hydrographique overlay
 * @param {boolean} enabled - Visibilité contrôlée par classificationToggles.hydro
 * @param {number}  opacity - Opacité (0-1), défaut 0.75
 */
const HydrographyOverlayLayer = React.memo(({ enabled = true, opacity = 0.75 }) => {
  const API_BASE = process.env.REACT_APP_BACKEND_URL || '';
  const [tilesReady, setTilesReady] = useState(false);
  const loadCountRef = useRef(0);

  const proxyUrl = useMemo(() => `${API_BASE}/api/wms-proxy/tile`, [API_BASE]);

  const wmsParams = useMemo(() => ({
    url: HYDRO_WMS_CONFIG.serviceUrl,
    layers: HYDRO_WMS_CONFIG.layer,
    format: HYDRO_WMS_CONFIG.format,
    transparent: 'true'
  }), []);

  const tileEvents = useMemo(() => ({
    loading: () => {
      loadCountRef.current += 1;
      setTilesReady(false);
    },
    load: () => {
      loadCountRef.current = Math.max(0, loadCountRef.current - 1);
      if (loadCountRef.current === 0) setTilesReady(true);
    },
    tileerror: () => {
      loadCountRef.current = Math.max(0, loadCountRef.current - 1);
      if (loadCountRef.current === 0) setTilesReady(true);
    }
  }), []);

  if (!enabled) return null;

  return (
    <>
      <HydroPaneCreator />
      <WMSTileLayer
        url={proxyUrl}
        params={wmsParams}
        pane={HYDRO_PANE_NAME}
        uppercase={false}
        format="image/png"
        transparent={true}
        opacity={tilesReady ? opacity : 0}
        keepBuffer={8}
        updateWhenZooming={false}
        updateWhenIdle={true}
        className="hydro-overlay-layer"
        eventHandlers={tileEvents}
        data-testid="hydro-overlay-layer"
      />
    </>
  );
});

export default HydrographyOverlayLayer;
