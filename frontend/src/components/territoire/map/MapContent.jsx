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
import BionicMicroZones from '@/components/territoire/BionicMicroZones';
// STEVE-MAX: MovementCorridorsLayer SUPPRIME DEFINITIVEMENT — BCE-4X-UI-003
import { ShootingZones, SessionHeatmap } from '@/modules/groupe';
import CursorBionicLayer from '@/components/territoire/CursorBionicLayer';
import BionicAntiDoublesGuard from '@/components/territoire/BionicAntiDoublesGuard';
import { BionicZone2kmLayer } from '@/components/territoire/BionicZone2km';
import HuntingPathLayer from '@/components/territoire/HuntingPathLayer';
import { MapInteractionLayer } from '@/modules/map_interaction';
import { BIONIC_MODULES } from '@/core/bionic';
import { PLACE_TYPES } from '@/config/placeTypes';

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
    <BionicMicroZones
      zones={bionicZones}
      corridors={bionicZonesData.corridors || []}
      minPercentage={minPercentageFilter}
      showCorridors={showCorridors && classificationToggles.corridorsEstimes}
      onZoneClick={setSelectedZone}
      onZoneHover={setHoveredZone}
      isZoneFavorite={isZoneFavorite}
      onAddFavorite={async (zone) => {
        const name = prompt(`Nom pour cette zone ${BIONIC_MODULES[zone.layerId]?.label || zone.layerId} (${zone.score}%) ?`, `Zone ${BIONIC_MODULES[zone.layerId]?.label}`);
        if (name) {
          await addFavorite({
            name,
            module_id: zone.layerId,
            location: { lat: zone.center[0], lng: zone.center[1], radius_meters: 40 },
            notes: null,
            alert_enabled: true,
            alert_days_before: 3
          });
        }
      }}
      onRemoveFavorite={(zone) => {
        const favId = getFavoriteId(zone);
        if (favId) removeFavorite(favId);
      }}
    />
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
        pathOptions={{ color: '#FF9800', fillColor: '#FF9800', fillOpacity: 0.04, weight: 2, dashArray: '8, 4' }}
        data-testid="analysis-bbox-overlay"
      />
    )}
    {selectedWaypointForZones && (
      <Circle center={[selectedWaypointForZones.lat, selectedWaypointForZones.lng]} radius={30} pathOptions={{ color: '#FF9800', fillColor: '#FF9800', fillOpacity: 0.5, weight: 2 }} />
    )}

    <ShootingZones zones={[]} currentUserId={userId} dangerAlerts={[]} members={[]} onZoneClick={null} showOwnZone={true} showOtherZones={true} showDangerIndicators={true} />
    <SessionHeatmap membersWithPositions={groupMembersPositions} isActive={isGroupeTrackingActive} />

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
