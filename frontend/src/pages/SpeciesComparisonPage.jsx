/**
 * SpeciesComparisonPage.jsx
 * Mode "Comparaison Espèces" — Split-screen BIONIC V5
 *
 * Pipeline strict:
 *  - 2 appels API indépendants (1 par espèce)
 *  - 2 GeoJSON indépendants
 *  - 2 cartes synchronisées (zoom + center)
 *  - Aucun lien transversal entre espèces
 */

import React, { useState, useEffect, useRef, useCallback } from "react";
import { MapContainer, TileLayer, Polygon, Tooltip, useMap, useMapEvents } from "react-leaflet";
import { useNavigate } from "react-router-dom";
import { generateBionicZonesV5 } from "@/services/BionicZoneService";
import useBionicLayers from "@/hooks/useBionicLayers";
import { SPECIES_LIST } from "@/core/bionic/speciesConfig";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Loader2, SplitSquareHorizontal } from "lucide-react";

const DEFAULT_CENTER = [46.85, -71.25];
const DEFAULT_ZOOM = 13;

// Map synchronizer: syncs one map's view to another
const MapSync = ({ syncRef, isMaster }) => {
  const map = useMap();

  useEffect(() => {
    if (isMaster) syncRef.current = map;
  }, [map, syncRef, isMaster]);

  useMapEvents({
    moveend: () => {
      if (isMaster && syncRef.current) {
        const center = map.getCenter();
        const zoom = map.getZoom();
        window.dispatchEvent(new CustomEvent("bionic-sync", { detail: { center, zoom } }));
      }
    },
  });

  useEffect(() => {
    if (!isMaster) {
      const handler = (e) => {
        map.setView(e.detail.center, e.detail.zoom, { animate: false });
      };
      window.addEventListener("bionic-sync", handler);
      return () => window.removeEventListener("bionic-sync", handler);
    }
  }, [map, isMaster]);

  return null;
};

// Invalidate map size after mount to fix tile loading in split-screen layout
const MapResizer = () => {
  const map = useMap();
  useEffect(() => {
    const timers = [
      setTimeout(() => map.invalidateSize(), 100),
      setTimeout(() => map.invalidateSize(), 500),
      setTimeout(() => map.invalidateSize(), 1500),
    ];
    const container = map.getContainer();
    let rafId = null;
    const observer = new ResizeObserver(() => {
      if (rafId) cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(() => {
        if (map && map.getContainer()) map.invalidateSize({ animate: false });
        rafId = null;
      });
    });
    observer.observe(container);
    return () => {
      timers.forEach(clearTimeout);
      if (rafId) cancelAnimationFrame(rafId);
      observer.disconnect();
    };
  }, [map]);
  return null;
};

// Zone renderer for one species
const SpeciesZoneLayer = ({ zones }) => {
  if (!zones || zones.length === 0) return null;
  return (
    <>
      {zones.map((zone) => (
        <Polygon
          key={zone.id}
          positions={zone.positions}
          pathOptions={{
            color: zone.color,
            weight: 4,
            opacity: 0.95,
            fillColor: zone.color,
            fillOpacity: 0.0,
          }}
        >
          <Tooltip direction="top" opacity={0.9}>
            <div className="text-xs">
              <div className="font-bold">{zone.label}</div>
              <div>Score: {zone.score}/100</div>
              <div>Aire: {zone.areaM2?.toLocaleString("fr-FR")} m²</div>
            </div>
          </Tooltip>
        </Polygon>
      ))}
    </>
  );
};

// Bounds capture — defined outside ComparisonPane to avoid re-creation
const MapBoundsCapture = ({ onBoundsChange }) => {
  const map = useMap();
  const initRef = useRef(false);

  useMapEvents({
    moveend: () => {
      const b = map.getBounds();
      onBoundsChange({
        south: b.getSouth(), west: b.getWest(),
        north: b.getNorth(), east: b.getEast(),
      }, map.getZoom());
    },
  });

  useEffect(() => {
    if (initRef.current) return;
    initRef.current = true;
    const timer = setTimeout(() => {
      const b = map.getBounds();
      onBoundsChange({
        south: b.getSouth(), west: b.getWest(),
        north: b.getNorth(), east: b.getEast(),
      }, map.getZoom());
    }, 500);
    return () => clearTimeout(timer);
  }, [map, onBoundsChange]);

  return null;
};

// One half of the split screen
const ComparisonPane = ({ speciesId, isMaster, syncRef, layersVisible }) => {
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(false);
  const boundsRef = useRef(null);
  const zoomRef = useRef(DEFAULT_ZOOM);
  const [fetchTrigger, setFetchTrigger] = useState(0);
  const speciesInfo = SPECIES_LIST.find((s) => s.id === speciesId) || { name: speciesId, color: "#f5a623" };

  const handleBoundsChange = useCallback((newBounds, newZoom) => {
    boundsRef.current = newBounds;
    zoomRef.current = newZoom;
    setFetchTrigger(prev => prev + 1);
  }, []);

  useEffect(() => {
    if (!boundsRef.current) return;
    let cancelled = false;
    setLoading(true);

    const load = async () => {
      try {
        const result = await generateBionicZonesV5(boundsRef.current, zoomRef.current, layersVisible, speciesId);
        if (!cancelled) setZones(result.zones || []);
      } catch (e) {
        console.warn("[Comparison] Error:", e);
        if (!cancelled) setZones([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    load();
    return () => { cancelled = true; };
  }, [fetchTrigger, speciesId, layersVisible]);

  return (
    <div className="relative flex-1 h-full" data-testid={`comparison-pane-${speciesId}`}>
      {/* Species label */}
      <div className="absolute top-3 left-14 z-[1000] flex items-center gap-2">
        <Badge
          className="px-3 py-1.5 text-xs font-bold shadow-xl border-2"
          style={{
            backgroundColor: "#111",
            borderColor: speciesInfo.color,
            color: speciesInfo.color,
          }}
          data-testid={`species-badge-${speciesId}`}
        >
          <div className="w-2.5 h-2.5 rounded-full mr-1.5" style={{ backgroundColor: speciesInfo.color }} />
          {speciesInfo.name}
        </Badge>
        {loading && <Loader2 className="h-4 w-4 animate-spin text-[#f5a623]" data-testid={`loading-${speciesId}`} />}
        {!loading && (
          <Badge className="bg-black/80 text-white text-[10px] border border-white/20" data-testid={`zone-count-${speciesId}`}>{zones.length} zones</Badge>
        )}
      </div>

      <MapContainer
        center={DEFAULT_CENTER}
        zoom={DEFAULT_ZOOM}
        className="h-full w-full"
        zoomControl={isMaster}
        attributionControl={false}
      >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <MapSync syncRef={syncRef} isMaster={isMaster} />
        <MapResizer />
        <MapBoundsCapture onBoundsChange={handleBoundsChange} />
        <SpeciesZoneLayer zones={zones} />
      </MapContainer>
    </div>
  );
};

export default function SpeciesComparisonPage() {
  const navigate = useNavigate();
  const syncRef = useRef(null);
  const { layersVisible } = useBionicLayers();

  const [speciesLeft, setSpeciesLeft] = useState("orignal");
  const [speciesRight, setSpeciesRight] = useState("chevreuil");

  const speciesOptions = SPECIES_LIST.filter((s) => s.id !== "tous");

  return (
    <div className="fixed inset-0 bg-[#0a0f1a] flex flex-col pt-16" data-testid="species-comparison-page">
      {/* Header */}
      <div className="flex-shrink-0 bg-black/95 border-b border-[#f5a623]/20 px-4 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="sm" onClick={() => navigate("/territoire")} className="text-gray-300 hover:text-white h-8 px-2" data-testid="back-btn">
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div className="h-5 w-px bg-[#f5a623]/30" />
            <SplitSquareHorizontal className="h-5 w-5 text-[#f5a623]" />
            <div>
              <h1 className="text-sm font-bold text-white" data-testid="comparison-title">Comparaison Espèces</h1>
              <p className="text-[10px] text-gray-400">Pipeline backend V2 — Zones organiques indépendantes</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={speciesLeft}
              onChange={(e) => setSpeciesLeft(e.target.value)}
              className="bg-gray-900 border border-gray-700 text-white text-xs rounded px-2 py-1 h-8"
              data-testid="species-select-left"
            >
              {speciesOptions.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>

            <span className="text-[#f5a623] text-xs font-bold tracking-wider">VS</span>

            <select
              value={speciesRight}
              onChange={(e) => setSpeciesRight(e.target.value)}
              className="bg-gray-900 border border-gray-700 text-white text-xs rounded px-2 py-1 h-8"
              data-testid="species-select-right"
            >
              {speciesOptions.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Split screen maps */}
      <div className="flex-1 flex overflow-hidden min-h-0">
        <ComparisonPane speciesId={speciesLeft} isMaster={true} syncRef={syncRef} layersVisible={layersVisible} />
        <div className="w-1 bg-[#f5a623]/60 flex-shrink-0" />
        <ComparisonPane speciesId={speciesRight} isMaster={false} syncRef={syncRef} layersVisible={layersVisible} />
      </div>
    </div>
  );
}
