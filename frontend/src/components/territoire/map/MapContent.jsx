/**
 * MapContent.jsx — Contenu de la carte Leaflet BIONIC
 * Extrait de MonTerritoireBionicPage.jsx (IM1.2 Refactorisation)
 *
 * Rendu de tous les layers, markers et interactions de la carte.
 */
import React from 'react';
import { Marker, Popup, Circle, Rectangle } from 'react-leaflet';
import EcoforestryLayers from '@/components/territoire/EcoforestryLayers';
import { MapRefCapture, ZoomHandler, MapResizer, MapClickHandler, createCustomIcon } from '@/components/territoire/map/MapHelpers';
import HydrographyOverlayLayer from '@/components/territoire/HydrographyOverlayLayer';
import ExclusionOverlayLayer from '@/components/territoire/ExclusionOverlayLayer';
import WindFlowLayer from '@/components/territoire/WindFlowLayer';
import StructureContrastLayer from '@/components/territoire/StructureContrastLayer';
// BCE-4X-UI-003: BionicMicroZones (V9) SUPPRIME DEFINITIVEMENT — Zones rendues par BionicCorridorsV10Layer
import { ShootingZones } from '@/modules/groupe';
import CursorBionicLayer from '@/components/territoire/CursorBionicLayer';
import BionicAntiDoublesGuard from '@/components/territoire/BionicAntiDoublesGuard';
import { BionicZone2kmLayer } from '@/components/territoire/BionicZone2km';
import HuntingPathLayer from '@/components/territoire/HuntingPathLayer';
import { MapInteractionLayer } from '@/modules/map_interaction';
import { BIONIC_MODULES } from '@/core/bionic';
import { PLACE_TYPES } from '@/config/placeTypes';
import BionicCorridorsV10Layer from '@/components/territoire/BionicCorridorsV10Layer';
import AlimentationV2Layer from '@/components/territoire/AlimentationV2Layer';
import ConsolidatedHeatmapLayer from '@/components/territoire/ConsolidatedHeatmapLayer';

const MapContentInner = React.memo(({
  // Eco layers
  activeEcoLayers,
  ecoLayerOpacities,
  ecoMapStatus,
  activeFallback,
  // Map refs & handlers
  mapRef,
  handleZoomChange,
  handleMapMove,
  handleBoundsChange,
  mapClickMode,
  handleMapClickForWaypoint,
  // Classification & toggles
  classificationToggles,
  showExclusionOverlay,
  showWindFlow,
  windMode,
  showCorridorsV1,
  showCorridors,
  showCursorBionic,
  isPrivateDataVisible,
  privacyMode,
  // Zones & corridors
  bionicZones,
  bionicZonesData,
  minPercentageFilter,
  selectedSpecies,
  temporalHourMT,
  layersVisible,
  // Waypoints & places
  selectedWaypointForZones,
  bboxBounds,
  activeWaypoints,
  savedPlaces,
  selectWaypointAsTarget,
  setContextMenuMT,
  // Favorites
  isZoneFavorite,
  addFavorite,
  getFavoriteId,
  removeFavorite,
  // Zone click
  setSelectedZone,
  setHoveredZone,
  // User
  userPosition,
  userId,
  syncToBackend,
  // Groupe
  groupMembersPositions,
  isGroupeTrackingActive,
  // STEVE-MAX: Hunting Path
  huntingPathData,
  showHuntingPath,
  // CORRIDORS-V10
  onCorridorDataLoaded,
  // ALIMENTATION-V2
  showAlimentationV2,
  showSalines,
  nSalinesMax,
  onAlimentationDataLoaded,
  // HEATMAP V10 consolidée
  showHeatmapV10,
  onHeatmapDataLoaded,
  heatmapIncludeCorridors,
  // STEEVE-MAX UX: Contrôles couches et points chauds
  showZonesLayer,
  showCorridorsLayer,
  showPointsLayer,
  pointsChaudsMode,
  pointsChaudsFilter,
  zoneSubFilters,
  corridorSubFilters,
  pointSubFilters,
  // STABILITÉ V2: Centre memoizé
  waypointCenter,
}) => (
  <>
    <EcoforestryLayers
      activeLayers={activeEcoLayers}
      layerOpacities={ecoLayerOpacities}
      baseMapId={activeEcoLayers.baseMap}
      fallbackStatus={ecoMapStatus}
      activeFallback={activeFallback}
    />
    <MapRefCapture mapRefProp={mapRef} />
    <MapResizer />
    <ZoomHandler onZoomChange={handleZoomChange} onMapMove={handleMapMove} onBoundsChange={handleBoundsChange} />
    {mapClickMode && <MapClickHandler onMapClick={handleMapClickForWaypoint} enabled={true} />}

    <HydrographyOverlayLayer enabled={false} opacity={0.25} />

    <ExclusionOverlayLayer enabled={showExclusionOverlay && classificationToggles.pression} />
    {showWindFlow && <WindFlowLayer mode={windMode || 'arrows'} />}
    <StructureContrastLayer enabled={classificationToggles.anthropique} />
    {/* BCE-4X: Zones V9 (BionicMicroZones) SUPPRIMEES — Zones V10 rendues par BionicCorridorsV10Layer */}
    {/* STEVE-MAX: MovementCorridorsLayer PURGE DEFINITIVE — BCE-4X-UI-003 */}

    {/* STEVE-MAX P3: Hunting Path Layer — z-index 700 (above corridors) */}
    {showHuntingPath && huntingPathData && (
      <HuntingPathLayer huntingPath={huntingPathData} />
    )}

    {/* BIONIC Zone 2 km² — Carré unique centré sur le waypoint actif */}
    {selectedWaypointForZones && (
      <BionicZone2kmLayer 
        waypoints={activeWaypoints}
        selectedWaypoint={selectedWaypointForZones}
        showForAll={false}
        opacity={0.7}
      />
    )}

    {/* P0 FIX: BBox Rectangle hidden by default — only show when Curseur BIONIC is active */}
    {selectedWaypointForZones && bboxBounds && showCursorBionic && (
      <Rectangle
        bounds={bboxBounds}
        pathOptions={{ color: '#FF9800', fillColor: 'transparent', fillOpacity: 0, weight: 2, dashArray: '8, 4' }}
        data-testid="analysis-bbox-overlay"
      />
    )}
    {selectedWaypointForZones && (
      <Circle center={[selectedWaypointForZones.lat, selectedWaypointForZones.lng]} radius={30} pathOptions={{ color: '#FF9800', fillColor: 'transparent', fillOpacity: 0, weight: 2 }} />
    )}

    <ShootingZones zones={[]} currentUserId={userId} dangerAlerts={[]} members={[]} onZoneClick={null} showOwnZone={true} showOtherZones={true} showDangerIndicators={true} />

    {/* SCORE CONSOLIDÉ V10: Data-only (100% transparent, zero rendu graphique) */}
    {selectedWaypointForZones && showHeatmapV10 && waypointCenter && (
      <ConsolidatedHeatmapLayer
        center={waypointCenter}
        species={selectedSpecies}
        month={new Date().getMonth() + 1}
        enabled={showHeatmapV10}
        onDataLoaded={onHeatmapDataLoaded}
        includeCorridors={heatmapIncludeCorridors}
      />
    )}

    {/* CORRIDORS-V10: Couche corridors fauniques — palette normative (SEULE couche active) */}
    {selectedWaypointForZones && showCorridors && waypointCenter && (
      <BionicCorridorsV10Layer
        center={waypointCenter}
        species={selectedSpecies}
        month={new Date().getMonth() + 1}
        enabled={showCorridors}
        opacity={0.55}
        minPercentage={minPercentageFilter}
        onDataLoaded={onCorridorDataLoaded}
        showZones={showZonesLayer !== false}
        showCorridorsLayer={showCorridorsLayer !== false}
        showPoints={showPointsLayer !== false}
        pointsChaudsMode={pointsChaudsMode || false}
        pointsChaudsFilter={pointsChaudsFilter || 'tous'}
        zoneSubFilters={zoneSubFilters}
        corridorSubFilters={corridorSubFilters}
        pointSubFilters={pointSubFilters}
      />
    )}

    {/* ALIMENTATION-V2: Salines optimales dans la zone 2km×2km */}
    {selectedWaypointForZones && showAlimentationV2 && waypointCenter && (
      <AlimentationV2Layer
        center={waypointCenter}
        species={selectedSpecies}
        month={new Date().getMonth() + 1}
        enabled={showAlimentationV2}
        showSalines={showSalines}
        maxSalines={nSalinesMax}
        onDataLoaded={onAlimentationDataLoaded}
      />
    )}

    {userPosition && (
      <Marker position={[userPosition.lat, userPosition.lng]} icon={createCustomIcon('#3b82f6', 'user')}>
        <Popup><div className="text-center font-bold">Ma position</div></Popup>
      </Marker>
    )}
    {showCursorBionic && classificationToggles.curseurBionic && (
      <CursorBionicLayer species={selectedSpecies} onQuickAddWaypoint={null} />
    )}
    {isPrivateDataVisible && classificationToggles.waypoints && activeWaypoints.map(wp => (
      <Marker
        key={wp.id}
        position={[wp.lat, wp.lng]}
        icon={createCustomIcon(selectedWaypointForZones?.id === wp.id ? '#3CB371' : '#FF9800', 'waypoint')}
        eventHandlers={{
          click: () => selectWaypointAsTarget(wp),
          contextmenu: (e) => {
            e.originalEvent.preventDefault();
            setContextMenuMT({ position: { x: e.originalEvent.clientX, y: e.originalEvent.clientY }, waypoint: { ...wp } });
          }
        }}
      />
    ))}
    {isPrivateDataVisible && classificationToggles.waypoints && savedPlaces.map(place => (
      <Marker key={place.id} position={[place.lat, place.lng]} icon={createCustomIcon(PLACE_TYPES.find(t => t.id === place.type)?.color || '#6b7280', 'place')}>
        <Popup><div className="text-center"><div className="font-bold">{place.name}</div><div className="text-xs">{PLACE_TYPES.find(t => t.id === place.type)?.name}</div></div></Popup>
      </Marker>
    ))}
    {privacyMode && <div className="bionic-private-overlay" />}
    <MapInteractionLayer showCoordinates={true} enableWaypointCreation={!mapClickMode} showHint={!mapClickMode} onWaypointCreated={(waypoint) => { if (syncToBackend) syncToBackend(); }} userId={userId || 'anonymous'} />
    <BionicAntiDoublesGuard zones={bionicZones} onZoneClick={setSelectedZone} />
  </>
));

MapContentInner.displayName = 'MapContent';
export const MapContent = MapContentInner;
