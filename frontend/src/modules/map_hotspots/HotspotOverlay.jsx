/**
 * HotspotOverlay - Overlay des hotspots BIONIC sur Leaflet
 * PHASE P1-HOTSPOTS
 * 
 * Specifications visuelles BIONIC V5 (NON NEGOCIABLES):
 * - Contours ultra-fins (1-2px)
 * - Centre 100% transparent (fill_opacity = 0)
 * - Formes naturelles (Chaikin smoothing)
 * - ZERO glow, shadow, halo
 * 
 * Composant Leaflet: Affiche hotspots, zones et corridors comme GeoJSON
 */
import React, { useEffect, useState } from 'react';
import { GeoJSON, useMap } from 'react-leaflet';

const API_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * Style pour les hotspots (Polygon)
 * CONFORME AU CONTRAT: fill_opacity tres faible pour permettre de voir la carte
 */
const getHotspotStyle = (feature) => {
  const style = feature.properties?.style || {};
  return {
    color: style.stroke_color || '#FFD700',
    weight: Math.max(style.stroke_width || 1.5, 2),  // Minimum 2px pour visibilite
    opacity: 1,
    fillColor: style.stroke_color || '#FFD700',
    fillOpacity: 0.08,  // Tres leger fill pour rendre visible sur la carte
    dashArray: null
  };
};

/**
 * Style pour les zones comportementales (Polygon)
 */
const getZoneStyle = (feature) => {
  const style = feature.properties?.style || {};
  return {
    color: style.stroke_color || '#4CAF50',
    weight: Math.max(style.stroke_width || 1.5, 2),  // Minimum 2px
    opacity: 0.9,
    fillColor: style.stroke_color || '#4CAF50',
    fillOpacity: 0.1,  // Leger fill pour visibilite
    dashArray: style.stroke_dasharray !== 'none' ? style.stroke_dasharray : null
  };
};

/**
 * Style pour les corridors (LineString)
 */
const getCorridorStyle = (feature) => {
  const style = feature.properties?.style || {};
  return {
    color: style.stroke_color || '#8BC34A',
    weight: style.stroke_width || 2,
    opacity: 0.85,
    dashArray: style.stroke_dasharray !== 'none' ? style.stroke_dasharray : null
  };
};

/**
 * Popup pour hotspot
 */
const onEachHotspotFeature = (feature, layer) => {
  if (feature.properties) {
    const props = feature.properties;
    const metadata = props.metadata || {};
    const timeValidity = props.time_validity || {};
    
    layer.bindPopup(`
      <div style="min-width: 200px; font-family: system-ui, sans-serif;">
        <div style="font-weight: 600; font-size: 14px; color: ${props.style?.stroke_color || '#FFD700'}; margin-bottom: 8px;">
          ${getHotspotLabel(props.type)}
        </div>
        <div style="font-size: 12px; color: #666; line-height: 1.5;">
          <div><strong>Score:</strong> ${props.score}/100</div>
          <div><strong>Confiance:</strong> ${Math.round((props.confidence || 0) * 100)}%</div>
          <div><strong>Especes:</strong> ${(props.species || []).join(', ')}</div>
          ${timeValidity.optimal_hours?.length ? 
            `<div><strong>Heures optimales:</strong> ${timeValidity.optimal_hours.join('h, ')}h</div>` : ''}
          <div style="margin-top: 6px; font-size: 11px; color: #888;">
            Facteur: ${metadata.source_factor || 'N/A'} (${metadata.factor_score || 0}/100)
          </div>
        </div>
      </div>
    `);
    
    layer.on('mouseover', () => {
      layer.setStyle({ weight: 3, opacity: 1 });
    });
    layer.on('mouseout', () => {
      layer.setStyle({ weight: props.style?.stroke_width || 1.5, opacity: 0.9 });
    });
  }
};

/**
 * Popup pour zone
 */
const onEachZoneFeature = (feature, layer) => {
  if (feature.properties) {
    const props = feature.properties;
    const context = props.behavior_context || {};
    
    layer.bindPopup(`
      <div style="min-width: 180px; font-family: system-ui, sans-serif;">
        <div style="font-weight: 600; font-size: 14px; color: ${props.style?.stroke_color || '#4CAF50'}; margin-bottom: 8px;">
          Zone: ${getZoneLabel(props.type)}
        </div>
        <div style="font-size: 12px; color: #666; line-height: 1.5;">
          <div><strong>Activite:</strong> ${context.primary_activity || 'N/A'}</div>
          <div><strong>Periode:</strong> ${(context.time_of_day || []).join(', ')}</div>
          ${props.overlap_zones?.length ? 
            `<div><strong>Chevauche:</strong> ${props.overlap_zones.length} zone(s)</div>` : ''}
        </div>
      </div>
    `);
    
    layer.on('mouseover', () => {
      layer.setStyle({ weight: 3 });
    });
    layer.on('mouseout', () => {
      layer.setStyle({ weight: props.style?.stroke_width || 1.5 });
    });
  }
};

/**
 * Popup pour corridor
 */
const onEachCorridorFeature = (feature, layer) => {
  if (feature.properties) {
    const props = feature.properties;
    const movement = props.movement_context || {};
    
    layer.bindPopup(`
      <div style="min-width: 180px; font-family: system-ui, sans-serif;">
        <div style="font-weight: 600; font-size: 14px; color: ${props.style?.stroke_color || '#8BC34A'}; margin-bottom: 8px;">
          Corridor: ${getCorridorLabel(props.type)}
        </div>
        <div style="font-size: 12px; color: #666; line-height: 1.5;">
          <div><strong>Direction:</strong> ${movement.direction || 'bidirectional'}</div>
          <div><strong>Frequence:</strong> ${movement.frequency || 'daily'}</div>
          <div><strong>Probabilite:</strong> ${Math.round((props.usage_probability || 0) * 100)}%</div>
          <div><strong>Largeur:</strong> ~${props.width_meters || 50}m</div>
          ${movement.peak_hours?.length ? 
            `<div><strong>Heures pic:</strong> ${movement.peak_hours.join('h, ')}h</div>` : ''}
        </div>
      </div>
    `);
    
    layer.on('mouseover', () => {
      layer.setStyle({ weight: 4 });
    });
    layer.on('mouseout', () => {
      layer.setStyle({ weight: props.style?.stroke_width || 2 });
    });
  }
};

// Labels traduits
const getHotspotLabel = (type) => {
  const labels = {
    activity_peak: "Pic d'activite",
    feeding_zone: "Zone d'alimentation",
    rut_zone: "Zone de rut",
    thermal_refuge: "Refuge thermique",
    water_source: "Point d'eau",
    predation_risk: "Risque predation",
    snow_impact: "Impact neige",
    human_avoidance: "Evitement humain",
    mineral_site: "Site mineral",
    composite_optimal: "Zone optimale"
  };
  return labels[type] || type;
};

const getZoneLabel = (type) => {
  const labels = {
    feeding: "Alimentation",
    bedding: "Repos",
    rut_arena: "Arene de rut",
    thermal_cover: "Couvert thermique",
    water_access: "Acces eau",
    predation_zone: "Zone predation",
    yarding_zone: "Ravage hivernal"
  };
  return labels[type] || type;
};

const getCorridorLabel = (type) => {
  const labels = {
    movement: "Deplacement",
    avoidance: "Evitement",
    preferred: "Route preferee",
    feeding_transit: "Transit alimentation"
  };
  return labels[type] || type;
};

/**
 * Convertit les donnees API en GeoJSON FeatureCollection
 */
const toGeoJSONCollection = (items) => {
  return {
    type: 'FeatureCollection',
    features: items.map(item => ({
      type: 'Feature',
      geometry: item.geometry,
      properties: {
        id: item.id,
        type: item.type,
        score: item.score,
        confidence: item.confidence,
        time_validity: item.time_validity,
        species: item.species,
        style: item.style,
        metadata: item.metadata,
        behavior_context: item.behavior_context,
        overlap_zones: item.overlap_zones,
        movement_context: item.movement_context,
        width_meters: item.width_meters,
        usage_probability: item.usage_probability
      }
    }))
  };
};

/**
 * Composant principal HotspotOverlay
 */
export const HotspotOverlay = ({ 
  showHotspots = true,
  showZones = false,
  showCorridors = false,
  species = ['moose'],
  hotspotTypes = ['activity_peak', 'feeding_zone', 'rut_zone'],
  zoneTypes = ['feeding', 'bedding', 'water_access'],
  corridorTypes = ['movement', 'preferred', 'feeding_transit'],
  minScoreThreshold = 70,
  timeRange = '24h'
}) => {
  const map = useMap();
  const [hotspots, setHotspots] = useState(null);
  const [zones, setZones] = useState(null);
  const [corridors, setCorridors] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Charger les donnees quand les bounds changent
  useEffect(() => {
    const fetchData = async () => {
      if (!map) {
        console.log('[HotspotOverlay] Map not ready');
        return;
      }
      
      console.log('[HotspotOverlay] Fetching data...', { showHotspots, showZones, showCorridors });
      
      const bounds = map.getBounds();
      const boundsData = {
        north: bounds.getNorth(),
        south: bounds.getSouth(),
        east: bounds.getEast(),
        west: bounds.getWest()
      };
      
      console.log('[HotspotOverlay] Bounds:', boundsData);
      
      setLoading(true);
      setError(null);
      
      try {
        const requests = [];
        
        // Hotspots
        if (showHotspots) {
          console.log('[HotspotOverlay] Fetching hotspots...');
          requests.push(
            fetch(`${API_URL}/api/v1/bionic/map/hotspots`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                bounds: boundsData,
                species,
                time_range: timeRange,
                hotspot_types: hotspotTypes,
                min_score_threshold: minScoreThreshold
              })
            }).then(r => r.json())
          );
        } else {
          requests.push(Promise.resolve(null));
        }
        
        // Zones
        if (showZones) {
          requests.push(
            fetch(`${API_URL}/api/v1/bionic/map/zones`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                bounds: boundsData,
                species: species[0] || 'moose',
                zone_types: zoneTypes,
                include_overlaps: true
              })
            }).then(r => r.json())
          );
        } else {
          requests.push(Promise.resolve(null));
        }
        
        // Corridors
        if (showCorridors) {
          requests.push(
            fetch(`${API_URL}/api/v1/bionic/map/corridors`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                bounds: boundsData,
                species: species[0] || 'moose',
                corridor_types: corridorTypes,
                connect_zones: true
              })
            }).then(r => r.json())
          );
        } else {
          requests.push(Promise.resolve(null));
        }
        
        const [hotspotsData, zonesData, corridorsData] = await Promise.all(requests);
        
        console.log('[HotspotOverlay] Responses:', { 
          hotspots: hotspotsData?.hotspots?.length, 
          zones: zonesData?.zones?.length,
          corridors: corridorsData?.corridors?.length 
        });
        
        if (hotspotsData?.success && hotspotsData.hotspots?.length) {
          setHotspots(toGeoJSONCollection(hotspotsData.hotspots));
        } else {
          setHotspots(null);
        }
        
        if (zonesData?.success && zonesData.zones?.length) {
          setZones(toGeoJSONCollection(zonesData.zones));
        } else {
          setZones(null);
        }
        
        if (corridorsData?.success && corridorsData.corridors?.length) {
          setCorridors(toGeoJSONCollection(corridorsData.corridors));
        } else {
          setCorridors(null);
        }
        
      } catch (err) {
        console.error('[HotspotOverlay] Fetch error:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    // Execute immediatement au montage
    fetchData();
    
    // Recharger quand la carte bouge
    const onMoveEnd = () => {
      fetchData();
    };
    
    map.on('moveend', onMoveEnd);
    
    return () => {
      map.off('moveend', onMoveEnd);
    };
  }, [map, showHotspots, showZones, showCorridors, species, hotspotTypes, zoneTypes, corridorTypes, minScoreThreshold, timeRange]);

  // Generer des keys uniques pour forcer le refresh
  const hotspotsKey = hotspots ? `hotspots-${hotspots.features.length}-${Date.now()}` : 'hotspots-empty';
  const zonesKey = zones ? `zones-${zones.features.length}-${Date.now()}` : 'zones-empty';
  const corridorsKey = corridors ? `corridors-${corridors.features.length}-${Date.now()}` : 'corridors-empty';
  
  // Log de debug pour le rendu
  console.log('[HotspotOverlay] Render state:', {
    hotspots: hotspots?.features?.length || 0,
    zones: zones?.features?.length || 0,
    corridors: corridors?.features?.length || 0,
    showHotspots,
    showZones,
    showCorridors
  });

  return (
    <>
      {/* Corridors en premier (en dessous) */}
      {showCorridors && corridors && corridors.features.length > 0 && (
        <GeoJSON 
          key={corridorsKey}
          data={corridors}
          style={getCorridorStyle}
          onEachFeature={onEachCorridorFeature}
        />
      )}
      
      {/* Zones ensuite */}
      {showZones && zones && zones.features.length > 0 && (
        <GeoJSON 
          key={zonesKey}
          data={zones}
          style={getZoneStyle}
          onEachFeature={onEachZoneFeature}
        />
      )}
      
      {/* Hotspots au dessus */}
      {showHotspots && hotspots && hotspots.features.length > 0 && (
        <GeoJSON 
          key={hotspotsKey}
          data={hotspots}
          style={getHotspotStyle}
          onEachFeature={onEachHotspotFeature}
        />
      )}
    </>
  );
};

export default HotspotOverlay;
