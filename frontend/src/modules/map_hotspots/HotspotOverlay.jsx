/**
 * HotspotOverlay - Overlay des hotspots BIONIC sur Leaflet
 * PHASE P1-HOTSPOTS V3 — REFONTE ON/OFF INDIVIDUELS
 * 
 * Specifications visuelles BIONIC V5 (NON NEGOCIABLES):
 * - Contours ultra-fins (1-2px)
 * - Centre 100% transparent (fill_opacity = 0)
 * - Formes naturelles (Chaikin smoothing)
 * - ZERO glow, shadow, halo
 * - Boutons ON/OFF individuels par hotspot
 * 
 * Composant Leaflet: Affiche hotspots, zones et corridors comme GeoJSON
 */
import React, { useEffect, useState, useCallback, useMemo } from 'react';
import { GeoJSON, useMap } from 'react-leaflet';
import { Eye, EyeOff, X } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * Style pour les hotspots (Polygon)
 * CONFORME AU CONTRAT: contours fins et visibles, fill tres leger
 */
const getHotspotStyle = (feature, isDisabled = false) => {
  const style = feature.properties?.style || {};
  return {
    color: isDisabled ? '#666' : (style.stroke_color || '#FFD700'),
    weight: Math.max(style.stroke_width || 1.5, 2),
    opacity: isDisabled ? 0.3 : 0.9,
    fillColor: isDisabled ? '#666' : (style.stroke_color || '#FFD700'),
    fillOpacity: 0.0,
    dashArray: isDisabled ? '5,5' : null
  };
};

/**
 * Style pour les zones comportementales (Polygon)
 */
const getZoneStyle = (feature) => {
  const style = feature.properties?.style || {};
  return {
    color: style.stroke_color || '#4CAF50',
    weight: Math.max(style.stroke_width || 1.5, 2),
    opacity: 0.8,
    fillColor: style.stroke_color || '#4CAF50',
    fillOpacity: 0.0,
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

// Labels traduits
const getHotspotLabel = (type) => {
  const labels = {
    activity_peak: "Pic d'activité",
    feeding_zone: "Zone d'alimentation",
    rut_zone: "Zone de rut",
    thermal_refuge: "Refuge thermique",
    water_source: "Point d'eau",
    predation_risk: "Risque prédation",
    snow_impact: "Impact neige",
    human_avoidance: "Évitement humain",
    mineral_site: "Site minéral",
    composite_optimal: "Zone optimale"
  };
  return labels[type] || type;
};

const getZoneLabel = (type) => {
  const labels = {
    feeding: "Alimentation",
    bedding: "Repos",
    rut_arena: "Arène de rut",
    thermal_cover: "Couvert thermique",
    water_access: "Accès eau",
    predation_zone: "Zone prédation",
    yarding_zone: "Ravage hivernal"
  };
  return labels[type] || type;
};

const getCorridorLabel = (type) => {
  const labels = {
    movement: "Déplacement",
    avoidance: "Évitement",
    preferred: "Route préférée",
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
 * Panneau de contrôle ON/OFF individuel pour les hotspots
 */
const HotspotTogglePanel = ({ 
  hotspots, 
  disabledHotspots, 
  onToggle, 
  onToggleAll,
  isOpen,
  onClose 
}) => {
  if (!isOpen || !hotspots?.features?.length) return null;

  const enabledCount = hotspots.features.filter(f => !disabledHotspots.has(f.properties.id)).length;
  const totalCount = hotspots.features.length;

  return (
    <div 
      className="absolute left-4 top-20 z-[1000] w-64 bg-slate-900/95 backdrop-blur-sm border border-slate-700/60 rounded-xl shadow-xl overflow-hidden"
      data-testid="hotspot-toggle-panel"
    >
      {/* Header */}
      <div className="px-3 py-2 bg-gradient-to-r from-amber-600/20 to-slate-800/50 border-b border-slate-700/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Eye className="h-4 w-4 text-amber-400" />
          <span className="font-semibold text-white text-sm">Hotspots ON/OFF</span>
          <span className="text-xs text-slate-400">({enabledCount}/{totalCount})</span>
        </div>
        <button
          onClick={onClose}
          className="h-6 w-6 flex items-center justify-center text-slate-400 hover:text-white rounded"
          data-testid="close-toggle-panel"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Toggle All */}
      <div className="px-3 py-2 border-b border-slate-800 flex items-center justify-between">
        <span className="text-xs text-slate-400">Tous les hotspots</span>
        <div className="flex gap-1">
          <button
            onClick={() => onToggleAll(true)}
            className="px-2 py-1 text-xs bg-emerald-600/30 text-emerald-300 rounded hover:bg-emerald-600/50 transition-colors"
            data-testid="enable-all-hotspots"
          >
            Tout ON
          </button>
          <button
            onClick={() => onToggleAll(false)}
            className="px-2 py-1 text-xs bg-red-600/30 text-red-300 rounded hover:bg-red-600/50 transition-colors"
            data-testid="disable-all-hotspots"
          >
            Tout OFF
          </button>
        </div>
      </div>
      
      {/* Liste des hotspots */}
      <div className="max-h-[50vh] overflow-y-auto">
        {hotspots.features.map((feature) => {
          const props = feature.properties;
          const isDisabled = disabledHotspots.has(props.id);
          const color = props.style?.stroke_color || '#FFD700';
          
          return (
            <div
              key={props.id}
              className={`px-3 py-2 border-b border-slate-800/50 flex items-center justify-between hover:bg-slate-800/30 transition-colors ${
                isDisabled ? 'opacity-50' : ''
              }`}
              data-testid={`hotspot-item-${props.id}`}
            >
              <div className="flex items-center gap-2 flex-1 min-w-0">
                <div 
                  className="w-3 h-3 rounded-full flex-shrink-0 border-2"
                  style={{ 
                    borderColor: isDisabled ? '#666' : color,
                    backgroundColor: 'transparent'
                  }}
                />
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-white truncate">
                    {getHotspotLabel(props.type)}
                  </div>
                  <div className="text-[10px] text-slate-500">
                    Score: {props.score} | {props.id.slice(-6)}
                  </div>
                </div>
              </div>
              
              <button
                onClick={() => onToggle(props.id)}
                className={`p-1.5 rounded transition-colors ${
                  isDisabled 
                    ? 'bg-slate-700/50 text-slate-500 hover:bg-slate-700'
                    : 'bg-amber-600/30 text-amber-300 hover:bg-amber-600/50'
                }`}
                data-testid={`toggle-hotspot-${props.id}`}
                title={isDisabled ? 'Activer ce hotspot' : 'Désactiver ce hotspot'}
              >
                {isDisabled ? (
                  <EyeOff className="h-3.5 w-3.5" />
                ) : (
                  <Eye className="h-3.5 w-3.5" />
                )}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
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
  minScoreThreshold = 50,
  timeRange = '24h',
  showTogglePanel = false,
  onTogglePanelClose = () => {},
  onHotspotsLoaded = () => {}  // Callback quand les hotspots sont chargés
}) => {
  const map = useMap();
  const [hotspots, setHotspots] = useState(null);
  const [zones, setZones] = useState(null);
  const [corridors, setCorridors] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // État des hotspots désactivés (IDs)
  const [disabledHotspots, setDisabledHotspots] = useState(new Set());

  // Toggle individuel d'un hotspot
  const toggleHotspot = useCallback((hotspotId) => {
    setDisabledHotspots(prev => {
      const next = new Set(prev);
      if (next.has(hotspotId)) {
        next.delete(hotspotId);
      } else {
        next.add(hotspotId);
      }
      return next;
    });
  }, []);

  // Toggle tous les hotspots
  const toggleAllHotspots = useCallback((enable) => {
    if (enable) {
      setDisabledHotspots(new Set());
    } else if (hotspots?.features) {
      setDisabledHotspots(new Set(hotspots.features.map(f => f.properties.id)));
    }
  }, [hotspots]);

  // Filtrer les hotspots visibles
  const visibleHotspots = useMemo(() => {
    if (!hotspots?.features) return null;
    
    const filteredFeatures = hotspots.features.filter(
      f => !disabledHotspots.has(f.properties.id)
    );
    
    if (filteredFeatures.length === 0) return null;
    
    return {
      type: 'FeatureCollection',
      features: filteredFeatures
    };
  }, [hotspots, disabledHotspots]);

  // Popup avec bouton ON/OFF intégré
  const onEachHotspotFeature = useCallback((feature, layer) => {
    if (feature.properties) {
      const props = feature.properties;
      const metadata = props.metadata || {};
      const timeValidity = props.time_validity || {};
      const isDisabled = disabledHotspots.has(props.id);
      
      layer.bindPopup(`
        <div style="min-width: 220px; font-family: system-ui, sans-serif;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
            <div style="font-weight: 600; font-size: 14px; color: ${props.style?.stroke_color || '#FFD700'};">
              ${getHotspotLabel(props.type)}
            </div>
            <button 
              onclick="window.toggleHotspot('${props.id}')"
              style="
                padding: 4px 8px;
                font-size: 11px;
                border-radius: 4px;
                border: none;
                cursor: pointer;
                background: ${isDisabled ? '#4a5568' : '#d69e2e'};
                color: white;
              "
              data-testid="popup-toggle-${props.id}"
            >
              ${isDisabled ? 'OFF' : 'ON'}
            </button>
          </div>
          <div style="font-size: 12px; color: #666; line-height: 1.5;">
            <div><strong>ID:</strong> ${props.id}</div>
            <div><strong>Score:</strong> ${props.score}/100</div>
            <div><strong>Confiance:</strong> ${Math.round((props.confidence || 0) * 100)}%</div>
            <div><strong>Espèces:</strong> ${(props.species || []).join(', ')}</div>
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
        const style = getHotspotStyle(feature, isDisabled);
        layer.setStyle(style);
      });
    }
  }, [disabledHotspots]);

  // Exposer la fonction de toggle globalement pour les popups
  useEffect(() => {
    window.toggleHotspot = (id) => {
      toggleHotspot(id);
      // Fermer le popup après toggle
      map?.closePopup();
    };
    return () => {
      delete window.toggleHotspot;
    };
  }, [toggleHotspot, map]);

  // Popup pour zone
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
            <div><strong>Activité:</strong> ${context.primary_activity || 'N/A'}</div>
            <div><strong>Période:</strong> ${(context.time_of_day || []).join(', ')}</div>
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

  // Popup pour corridor
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
            <div><strong>Fréquence:</strong> ${movement.frequency || 'daily'}</div>
            <div><strong>Probabilité:</strong> ${Math.round((props.usage_probability || 0) * 100)}%</div>
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
          // Reset disabled set when new hotspots are loaded
          setDisabledHotspots(new Set());
          // Notifier le parent du nombre de hotspots
          onHotspotsLoaded(hotspotsData.hotspots.length);
        } else {
          setHotspots(null);
          onHotspotsLoaded(0);
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
  const hotspotsKey = visibleHotspots 
    ? `hotspots-${visibleHotspots.features.length}-${disabledHotspots.size}-${Date.now()}` 
    : 'hotspots-empty';
  const zonesKey = zones ? `zones-${zones.features.length}-${Date.now()}` : 'zones-empty';
  const corridorsKey = corridors ? `corridors-${corridors.features.length}-${Date.now()}` : 'corridors-empty';
  
  // Log de debug pour le rendu
  console.log('[HotspotOverlay] Render state:', {
    hotspots: hotspots?.features?.length || 0,
    visibleHotspots: visibleHotspots?.features?.length || 0,
    disabledCount: disabledHotspots.size,
    zones: zones?.features?.length || 0,
    corridors: corridors?.features?.length || 0,
    showHotspots,
    showZones,
    showCorridors
  });

  return (
    <>
      {/* Panneau de contrôle ON/OFF individuel */}
      <HotspotTogglePanel
        hotspots={hotspots}
        disabledHotspots={disabledHotspots}
        onToggle={toggleHotspot}
        onToggleAll={toggleAllHotspots}
        isOpen={showTogglePanel}
        onClose={onTogglePanelClose}
      />
      
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
      
      {/* Hotspots au dessus (seulement les visibles) */}
      {showHotspots && visibleHotspots && visibleHotspots.features.length > 0 && (
        <GeoJSON 
          key={hotspotsKey}
          data={visibleHotspots}
          style={(feature) => getHotspotStyle(feature, false)}
          onEachFeature={onEachHotspotFeature}
        />
      )}
    </>
  );
};

export default HotspotOverlay;
