/**
 * useTerritoireEffects — Effects et logique zone/snapshot extraits
 * =================================================================
 * Extrait de MonTerritoireBionicPage (STEEVE-MAX refactoring P0).
 * Contient: zone toast notifications, amenagement engine, snapshot export.
 */
import { useState, useEffect, useCallback, useMemo } from 'react';
import { toast } from 'sonner';

/**
 * Zone toast notifications pour erreurs/warnings de generation.
 */
export function useZoneToasts(zeroZonesReason, isLoadingZones, bionicZonesData) {
  useEffect(() => {
    if (!zeroZonesReason || isLoadingZones) return;
    if (zeroZonesReason === 'timeout') {
      toast.error('Delai d\'analyse depasse (30s)', {
        description: 'Le serveur n\'a pas repondu a temps. Veuillez reessayer avec un secteur plus petit.',
        duration: 8000,
      });
    } else if (zeroZonesReason === 'overpass_unavailable') {
      toast.warning('Service de cartographie temporairement indisponible', {
        description: 'Les donnees d\'exclusion n\'ont pas pu etre recuperees. Reessayez dans quelques instants.',
        duration: 6000,
      });
    } else if (zeroZonesReason === 'all_filtered_by_exclusions') {
      toast.info('Aucune zone generee dans ce secteur', {
        description: 'Toutes les zones candidates ont ete exclues par les filtres anthropiques (routes, batiments, infrastructures).',
        duration: 5000,
      });
    } else if (zeroZonesReason === 'backend_error') {
      toast.error('Erreur de calcul des zones', {
        description: 'Une erreur est survenue lors de l\'analyse. Veuillez reessayer.',
        duration: 5000,
      });
    }
  }, [zeroZonesReason, isLoadingZones]);

  useEffect(() => {
    const stats = bionicZonesData?.stats || {};
    if (stats.t4_mismatch) {
      console.error(`[T4-COHERENCE] Backend t4_zone_count=${stats.t4_backend_count}, frontend parsed=${stats.total}`);
      toast.warning('Incoherence de donnees detectee', {
        description: `Le backend a genere ${stats.t4_backend_count} zones mais ${stats.total} ont ete rendues.`,
        duration: 8000,
      });
    }
  }, [bionicZonesData?.stats]);
}

/**
 * Amenagement Engine — fetch hunting path + amenagement report.
 */
export function useAmenagementEngine(bionicZones, selectedWaypointForZones, bionicZonesData) {
  const [huntingPathData, setHuntingPathData] = useState(null);
  const [amenagementReport, setAmenagementReport] = useState(null);
  const [showHuntingPath, setShowHuntingPath] = useState(true);

  useEffect(() => {
    if (!bionicZones.length || !selectedWaypointForZones) return;
    const corridors = bionicZonesData?.corridors || [];
    const wp = selectedWaypointForZones;
    const wpc = { lat: wp.lat || wp.latitude, lng: wp.lng || wp.longitude };
    const API = process.env.REACT_APP_BACKEND_URL;
    const zoneFeatures = bionicZones.map(z => ({
      geometry: z.geometry || { type: 'Polygon', coordinates: z.coordinates ? [z.coordinates] : [] },
      properties: { layer_id: z.layerId, score: z.score, label: z.label },
    }));
    fetch(`${API}/api/v1/bionic/amenagement-report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ zones: zoneFeatures, corridors, waypoint_center: wpc }),
    })
      .then(r => r.json())
      .then(data => {
        if (data.success) { setHuntingPathData(data.hunting_path); setAmenagementReport(data.amenagement_report); }
      })
      .catch(() => {});
  }, [bionicZones.length, selectedWaypointForZones, bionicZonesData?.corridors]);

  return { huntingPathData, amenagementReport, showHuntingPath, setShowHuntingPath };
}

/**
 * Snapshot export (JSON + PDF).
 */
export function useSnapshotExport(selectedWaypointForZones, generateSnapshot, selectedSpecies, layersVisible, temporalHourMT, currentZoom) {
  const handleGenerateSnapshot = useCallback(async (format) => {
    if (!selectedWaypointForZones) return;
    const snap = await generateSnapshot(selectedSpecies, layersVisible, {
      hour: temporalHourMT, zoom: currentZoom, timestamp: new Date().toISOString(),
    });
    if (!snap) return;
    if (format === 'json') {
      const blob = new Blob([JSON.stringify(snap, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href = url; a.download = `${snap.snapshot_id || 'snapshot'}.json`; a.click();
      URL.revokeObjectURL(url);
    } else if (format === 'pdf') {
      try {
        const { jsPDF } = await import('jspdf');
        const doc = new jsPDF('landscape', 'mm', 'a4');
        const mapEl = document.querySelector('.leaflet-container');
        if (mapEl) {
          const html2canvas = (await import('html2canvas')).default;
          const canvas = await html2canvas(mapEl, { useCORS: true, scale: 1, logging: false });
          doc.addImage(canvas.toDataURL('image/jpeg', 0.8), 'JPEG', 10, 10, 180, 120);
        }
        const y0 = 135;
        doc.setFontSize(14); doc.text(`Snapshot Territoire — BIONIC V5 300%`, 10, y0);
        doc.setFontSize(9);
        doc.text(`Waypoint: ${snap.waypoint?.name || 'N/A'}`, 10, y0 + 7);
        doc.text(`Coords: ${snap.waypoint?.lat?.toFixed(6)}, ${snap.waypoint?.lng?.toFixed(6)}`, 10, y0 + 12);
        doc.text(`Espece: ${snap.species} | Saison: ${snap.season}`, 10, y0 + 17);
        doc.text(`Perimetre: 1km x 1km | Zones: ${snap.structural_zones?.length || 0}`, 10, y0 + 22);
        doc.text(`Date: ${new Date(snap.timestamp).toLocaleString('fr-CA')}`, 10, y0 + 27);
        doc.text(`ID: ${snap.snapshot_id}`, 10, y0 + 32);
        if (snap.zone_summary) {
          let yOff = y0 + 40; doc.setFontSize(10); doc.text('Resume par couche:', 10, yOff); yOff += 5; doc.setFontSize(8);
          Object.entries(snap.zone_summary).forEach(([lid, info]) => { doc.text(`  ${lid}: ${info.count} zones, score moyen ${info.avg_score}`, 10, yOff); yOff += 4; });
        }
        doc.save(`${snap.snapshot_id || 'snapshot'}.pdf`);
      } catch (err) { console.error('[Snapshot PDF] Error:', err); }
    }
  }, [selectedWaypointForZones, generateSnapshot, selectedSpecies, layersVisible, temporalHourMT, currentZoom]);

  return handleGenerateSnapshot;
}

/**
 * Category scores derivation.
 */
export function useCategoryScores(scores, currentMapCenter) {
  return useMemo(() => {
    if (scores?.breakdown) return scores.breakdown;
    const baseSeed = Math.abs(Math.round(currentMapCenter.lat * 100 + currentMapCenter.lng * 50));
    return {
      habitat: 75 + (baseSeed % 15),
      rut: 68 + ((baseSeed + 1) % 20),
      salines: 60 + ((baseSeed + 2) % 25),
      affuts: 80 + ((baseSeed + 3) % 15),
      trajets: 65 + ((baseSeed + 4) % 20),
      peuplements: 70 + ((baseSeed + 5) % 15),
    };
  }, [scores?.breakdown, currentMapCenter.lat, currentMapCenter.lng]);
}
