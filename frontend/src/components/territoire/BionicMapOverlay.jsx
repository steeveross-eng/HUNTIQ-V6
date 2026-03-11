/**
 * BionicMapOverlay.jsx — Overlay BIONIC V5 pour Carte Interactive
 *
 * Backend = seule source de vérité. Aucune génération côté client.
 * Le backend fetch ses propres exclusions Overpass.
 */

import React, { useState, useEffect } from 'react';
import { useMap, useMapEvents } from 'react-leaflet';
import BionicMicroZones from '@/components/territoire/BionicMicroZones';
import { generateBionicZonesV5 } from '@/services/BionicZoneService';

const BionicMapOverlay = ({
  selectedSpecies = 'tous',
  layersVisible = {},
  minPercentage = 30,
  showCorridors = true,
  onStatsUpdate = null,
}) => {
  const map = useMap();
  const [currentBounds, setCurrentBounds] = useState(null);
  const [currentZoom, setCurrentZoom] = useState(map.getZoom());
  const [bionicData, setBionicData] = useState({ zones: [], corridors: [], stats: { total: 0 } });

  useEffect(() => {
    const b = map.getBounds();
    setCurrentBounds({
      south: b.getSouth(), west: b.getWest(),
      north: b.getNorth(), east: b.getEast(),
    });
    setCurrentZoom(map.getZoom());
  }, [map]);

  useMapEvents({
    moveend: () => {
      const b = map.getBounds();
      setCurrentBounds({
        south: b.getSouth(), west: b.getWest(),
        north: b.getNorth(), east: b.getEast(),
      });
      setCurrentZoom(map.getZoom());
    },
    zoomend: () => setCurrentZoom(map.getZoom()),
  });

  useEffect(() => {
    if (!currentBounds) return;
    let cancelled = false;

    const loadZones = async () => {
      try {
        const result = await generateBionicZonesV5(
          currentBounds, currentZoom, layersVisible, selectedSpecies,
        );
        if (!cancelled && result) setBionicData(result);
      } catch (err) {
        console.warn('[BIONIC V5] Overlay zone fetch error:', err);
        if (!cancelled) setBionicData({ zones: [], corridors: [], stats: { total: 0, error: true } });
      }
    };

    loadZones();
    return () => { cancelled = true; };
  }, [currentBounds, currentZoom, layersVisible, selectedSpecies]);

  useEffect(() => {
    if (onStatsUpdate) onStatsUpdate(bionicData.stats);
  }, [bionicData.stats, onStatsUpdate]);

  return (
    <BionicMicroZones
      zones={bionicData.zones}
      corridors={bionicData.corridors || []}
      minPercentage={minPercentage}
      showCorridors={showCorridors}
    />
  );
};

export default BionicMapOverlay;
