/**
 * SplitViewContainer.jsx — Conteneur Split View BIONIC™ V8.1
 *
 * Affiche deux cartes synchronisées côte-à-côte pour comparer
 * les saisons biologiques. Chaque côté a son propre sélecteur de saison.
 *
 * Architecture:
 * - SplitViewContainer (orchestrateur)
 *   ├── SeasonMapPane (gauche) — saison A
 *   └── SeasonMapPane (droite) — saison B
 *
 * NORME BIONIC: Déterministe, modulaire, zéro code mort
 */
import React, { useState, useEffect, useRef, useCallback, useLayoutEffect } from 'react';
import { MapContainer, useMap } from 'react-leaflet';
import { MapContent } from '@/components/territoire/map/MapContent';
import { BiologicalSeasonSelector } from '@/components/territoire/ui/BiologicalSeasonSelector';
import { getBiologicalSeason } from '@/config/biologicalSeasons';
import EcoforestryLayers from '@/components/territoire/EcoforestryLayers';
import { MapRefCapture, ZoomHandler, MapResizer } from '@/components/territoire/map/MapHelpers';
import BionicLegend from '@/components/territoire/BionicLegend';

// Capture la ref map pour sync
const MapRefBinder = ({ mapRefTarget }) => {
  const map = useMap();
  useLayoutEffect(() => { mapRefTarget.current = map; }, [map, mapRefTarget]);
  return null;
};

// Label de saison avec couleur
const SeasonLabel = ({ seasonId, side }) => {
  const season = getBiologicalSeason(seasonId);
  return (
    <div className={`absolute top-3 ${side === 'left' ? 'left-3' : 'right-3'} z-[1000] flex items-center gap-2`}>
      <div
        className="px-3 py-1.5 rounded-lg text-[11px] font-semibold backdrop-blur-sm border"
        style={{
          backgroundColor: `${season.color}20`,
          borderColor: `${season.color}40`,
          color: season.color,
        }}
        data-testid={`split-label-${side}`}
      >
        {season.label}
      </div>
    </div>
  );
};

export const SplitViewContainer = React.memo(({
  // Map shared props
  mapCenter,
  mapZoom,
  mapRef: primaryMapRef,
  activeEcoLayers,
  ecoLayerOpacities,
  ecoMapStatus,
  activeFallback,
  classificationToggles,
  showExclusionOverlay,
  showCorridorsV1,
  showCorridors,
  showCursorBionic,
  isPrivateDataVisible,
  privacyMode,
  minPercentageFilter,
  selectedSpecies,
  temporalHourMT,
  layersVisible,
  selectedWaypointForZones,
  bboxBounds,
  activeWaypoints,
  savedPlaces,
  selectWaypointAsTarget,
  setContextMenuMT,
  isZoneFavorite,
  addFavorite,
  getFavoriteId,
  removeFavorite,
  setSelectedZone,
  setHoveredZone,
  userPosition,
  userId,
  syncToBackend,
  groupMembersPositions,
  isGroupeTrackingActive,
  handleZoomChange,
  handleMapMove,
  handleBoundsChange,
  mapClickMode,
  handleMapClickForWaypoint,
  // Season props
  leftSeason,
  rightSeason,
  onLeftSeasonChange,
  onRightSeasonChange,
  // Zone data per season
  leftZonesData,
  rightZonesData,
  // Legend
  pipelineState,
}) => {
  const leftMapRef = useRef(null);
  const rightMapRef = useRef(null);
  const syncingRef = useRef(false);

  // Sync maps
  const syncRight = useCallback(() => {
    if (syncingRef.current || !leftMapRef.current || !rightMapRef.current) return;
    syncingRef.current = true;
    const c = leftMapRef.current.getCenter();
    const z = leftMapRef.current.getZoom();
    rightMapRef.current.setView(c, z, { animate: false });
    setTimeout(() => { syncingRef.current = false; }, 50);
  }, []);

  const syncLeft = useCallback(() => {
    if (syncingRef.current || !leftMapRef.current || !rightMapRef.current) return;
    syncingRef.current = true;
    const c = rightMapRef.current.getCenter();
    const z = rightMapRef.current.getZoom();
    leftMapRef.current.setView(c, z, { animate: false });
    setTimeout(() => { syncingRef.current = false; }, 50);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      const l = leftMapRef.current;
      const r = rightMapRef.current;
      if (!l || !r) return;
      l.on('moveend', syncRight);
      l.on('zoomend', syncRight);
      r.on('moveend', syncLeft);
      r.on('zoomend', syncLeft);
      clearInterval(interval);
    }, 300);
    return () => {
      clearInterval(interval);
      if (leftMapRef.current) {
        leftMapRef.current.off('moveend', syncRight);
        leftMapRef.current.off('zoomend', syncRight);
      }
      if (rightMapRef.current) {
        rightMapRef.current.off('moveend', syncLeft);
        rightMapRef.current.off('zoomend', syncLeft);
      }
    };
  }, [syncRight, syncLeft]);

  // Bind primary map ref to left
  useEffect(() => {
    if (leftMapRef.current) {
      primaryMapRef.current = leftMapRef.current;
    }
  });

  const sharedMapContentProps = {
    activeEcoLayers, ecoLayerOpacities, ecoMapStatus, activeFallback,
    classificationToggles, showExclusionOverlay, showCorridorsV1, showCorridors,
    showCursorBionic: false, // Disable cursor in split
    isPrivateDataVisible, privacyMode,
    minPercentageFilter, selectedSpecies, temporalHourMT, layersVisible,
    selectedWaypointForZones, bboxBounds, activeWaypoints, savedPlaces,
    selectWaypointAsTarget, setContextMenuMT,
    isZoneFavorite, addFavorite, getFavoriteId, removeFavorite,
    setSelectedZone, setHoveredZone,
    userPosition, userId, syncToBackend,
    groupMembersPositions, isGroupeTrackingActive,
    mapClickMode: false, handleMapClickForWaypoint: () => {},
  };

  return (
    <div className="absolute inset-0 flex" data-testid="split-view-container">
      {/* LEFT MAP */}
      <div className="flex-1 relative border-r border-[#1a1a2e]">
        <SeasonLabel seasonId={leftSeason} side="left" />
        <div className="absolute bottom-3 left-3 z-[1000]">
          <BiologicalSeasonSelector
            selectedSeason={leftSeason}
            onSeasonChange={onLeftSeasonChange}
            compact={true}
          />
        </div>
        <MapContainer
          center={mapCenter}
          zoom={mapZoom}
          className="absolute inset-0 w-full h-full"
          zoomControl={false}
          style={{ background: '#0a0a0f' }}
        >
          <MapRefBinder mapRefTarget={leftMapRef} />
          <MapResizer />
          <ZoomHandler onZoomChange={handleZoomChange} onMapMove={handleMapMove} onBoundsChange={handleBoundsChange} />
          <MapContent
            {...sharedMapContentProps}
            mapRef={leftMapRef}
            handleZoomChange={handleZoomChange}
            handleMapMove={handleMapMove}
            handleBoundsChange={handleBoundsChange}
            bionicZones={leftZonesData.zones || []}
            bionicZonesData={leftZonesData}
          />
        </MapContainer>
      </div>

      {/* DIVIDER */}
      <div className="w-px bg-[#3CB371]/40 z-[1001] relative">
        <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 bg-[#3CB371] text-black text-[9px] font-bold px-1.5 py-0.5 rounded-full z-10">
          VS
        </div>
      </div>

      {/* RIGHT MAP */}
      <div className="flex-1 relative">
        <SeasonLabel seasonId={rightSeason} side="right" />
        <div className="absolute bottom-3 right-3 z-[1000]">
          <BiologicalSeasonSelector
            selectedSeason={rightSeason}
            onSeasonChange={onRightSeasonChange}
            compact={true}
          />
        </div>
        <MapContainer
          center={mapCenter}
          zoom={mapZoom}
          className="absolute inset-0 w-full h-full"
          zoomControl={false}
          style={{ background: '#0a0a0f' }}
        >
          <MapRefBinder mapRefTarget={rightMapRef} />
          <MapResizer />
          <MapContent
            {...sharedMapContentProps}
            mapRef={rightMapRef}
            handleZoomChange={() => {}}
            handleMapMove={() => {}}
            handleBoundsChange={() => {}}
            bionicZones={rightZonesData.zones || []}
            bionicZonesData={rightZonesData}
          />
        </MapContainer>
      </div>
    </div>
  );
});

SplitViewContainer.displayName = 'SplitViewContainer';
