/**
 * CarteBionic - Carte Interactive BIONIC V5
 * ==========================================
 * BIONIC V5 ULTIME - PHASE 6 - ACTION 5
 * 
 * RESPONSABILITÉ UNIQUE:
 * - Afficher la carte interactive avec Leaflet
 * - Intégrer les layers depuis l'API /api/v1/bionic/analyze_waypoint
 * - Contrôler la visibilité des layers via LayerControlPanel
 * - Afficher le waypoint sélectionné et les zones comportementales
 * 
 * STATUT DU MOTEUR:
 * - Version: PRÉ-CALIBRÉE / PROTOTYPE AVANCÉ
 * - Les scores sont des ESTIMATIONS (non validés scientifiquement)
 * 
 * ISOLATION:
 * - Composant de présentation avec logique d'affichage cartographique
 * - Appel API via service dédié
 * - État local pour les layers
 * 
 * Conformité: G-SEC | G-QA | G-DOC | BIONIC V5
 */

import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polygon, Polyline, Circle, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import {
  Loader2,
  RefreshCw,
  Target,
  AlertTriangle,
  Info,
  Layers,
  MapPin
} from 'lucide-react';
import { toast } from 'sonner';

import LayerControlPanel, { LAYER_FAMILIES, getDefaultVisibility } from './LayerControlPanel';
import SeasonalFactorsPanel from './SeasonalFactorsPanel';
import { BIONIC_COLORS } from '@/config/bionic-colors';

// =============================================================================
// CONSTANTS
// =============================================================================

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || '';

// Icône personnalisée pour le waypoint
const waypointIcon = L.divIcon({
  className: 'custom-waypoint-marker',
  html: `<div style="
    width: 24px;
    height: 24px;
    background: ${BIONIC_COLORS.gold.primary};
    border: 3px solid white;
    border-radius: 50%;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
  "></div>`,
  iconSize: [24, 24],
  iconAnchor: [12, 12]
});

// Icône pour les points d'attraction
const attractionIcon = (color) => L.divIcon({
  className: 'custom-attraction-marker',
  html: `<div style="
    width: 16px;
    height: 16px;
    background: ${color};
    border: 2px solid white;
    border-radius: 50%;
    box-shadow: 0 1px 4px rgba(0,0,0,0.3);
  "></div>`,
  iconSize: [16, 16],
  iconAnchor: [8, 8]
});

// =============================================================================
// API SERVICE
// =============================================================================

/**
 * Service d'appel à l'API BIONIC
 */
const bionicApiService = {
  /**
   * Analyse un waypoint via l'API
   * @param {Object} waypoint - Waypoint à analyser
   * @param {string} targetDatetime - Date/heure cible ISO
   * @param {string} species - Espèce cible
   * @param {string} analysisMode - Mode d'analyse: 'live', 'pre_rut', 'rut', 'post_rut'
   * @param {Object} options - Options additionnelles
   */
  async analyzeWaypoint(waypoint, targetDatetime, species = 'orignal', analysisMode = 'rut', options = {}) {
    const requestBody = {
      waypoint: {
        id: waypoint.id,
        name: waypoint.name,
        latitude: waypoint.latitude,
        longitude: waypoint.longitude
      },
      target_datetime: targetDatetime || new Date().toISOString(),
      species: species,
      wqs: options.wqs || {
        score: 50.0,
        success_history: 50.0,
        weather_correlation: 50.0,
        activity_history: 50.0,
        accessibility: 50.0
      },
      parameters: {
        search_radius_km: options.parameters?.search_radius_km || 3.0,
        grid_resolution: options.parameters?.grid_resolution || 10,
        region: options.parameters?.region || 'CA-QC',
        mode: analysisMode  // Mode biologique
      },
      visualization: options.visualization || {
        organic_shape: true,
        exclude_water: true,
        follow_topography: true,
        follow_vegetation: true,
        allow_overlap: true,
        fusion_mode: 'weighted',
        smoothing_factor: 0.35
      }
    };

    const response = await fetch(`${API_BASE_URL}/api/v1/bionic/analyze_waypoint`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || `API Error: ${response.status}`);
    }

    return response.json();
  }
};

// =============================================================================
// MAP CONTROLLER COMPONENT
// =============================================================================

/**
 * Composant pour contrôler la vue de la carte
 */
const MapController = ({ center, zoom }) => {
  const map = useMap();
  
  useEffect(() => {
    if (center) {
      map.setView(center, zoom || 13);
    }
  }, [center, zoom, map]);
  
  return null;
};

/**
 * Composant pour initialiser les panes de layers avec z-index distincts
 * Garantit la superposabilité sans conflit visuel (P0.2 BIONIC V5)
 */
const LayerPanesInitializer = () => {
  const map = useMap();
  
  useEffect(() => {
    if (!map) return;
    
    // Configuration des z-index pour chaque famille de layers
    // Ordre de bas en haut: terrain -> vegetation -> behavioral -> attraction -> hunt_planning
    const paneConfig = {
      // Terrain Analysis (niveau le plus bas - fond de carte analytique)
      'terrain-pane': { zIndex: 400 },
      // Vegetation Analysis
      'vegetation-pane': { zIndex: 410 },
      // Behavioral Zones (zones comportementales - niveau intermédiaire)
      'behavioral-bedding-pane': { zIndex: 420 },
      'behavioral-feeding-pane': { zIndex: 425 },
      'behavioral-rut-pane': { zIndex: 430 },
      'behavioral-pressure-pane': { zIndex: 435 },
      'behavioral-corridors-pane': { zIndex: 440 },
      // Attraction Points (points d'intérêt)
      'attraction-pane': { zIndex: 450 },
      'thermal-pane': { zIndex: 455 },
      // Hunt Planning (niveau le plus haut - éléments tactiques)
      'hunt-planning-pane': { zIndex: 460 },
      // Markers always on top
      'markers-pane': { zIndex: 500 }
    };
    
    // Créer les panes si ils n'existent pas
    Object.entries(paneConfig).forEach(([paneName, config]) => {
      if (!map.getPane(paneName)) {
        const pane = map.createPane(paneName);
        pane.style.zIndex = config.zIndex;
        pane.style.pointerEvents = 'auto';
      }
    });
    
    console.log('[BIONIC] Layer panes initialized for superposition');
  }, [map]);
  
  return null;
};

// =============================================================================
// LAYER RENDERERS
// =============================================================================

/**
 * Rendu des zones comportementales (Polygones)
 * Utilise les panes BIONIC pour garantir la superposabilité (P0.2)
 */
const BehavioralZonesRenderer = ({ zones, isVisible, type, pane = 'behavioral-bedding-pane' }) => {
  if (!isVisible || !zones || zones.length === 0) return null;
  
  return (
    <>
      {zones.map((zone) => {
        if (!zone.geometry || zone.geometry.type !== 'Polygon') return null;
        
        // Convertir les coordonnées [lng, lat] en [lat, lng] pour Leaflet
        const positions = zone.geometry.coordinates[0]?.map(coord => [coord[1], coord[0]]) || [];
        
        if (positions.length < 3) return null;
        
        return (
          <Polygon
            key={zone.zone_id}
            positions={positions}
            pane={pane}
            pathOptions={{
              fillColor: zone.rendering?.fill_color || BIONIC_COLORS.blue.primary,
              fillOpacity: zone.rendering?.fill_opacity || 0.3,
              color: zone.rendering?.stroke_color || BIONIC_COLORS.blue.primary,
              weight: zone.rendering?.stroke_width || 2
            }}
          >
            <Popup>
              <div className="p-2">
                <h4 className="font-semibold text-sm">{type}</h4>
                <p className="text-xs text-gray-600">ID: {zone.zone_id}</p>
                {zone.properties?.score && (
                  <p className="text-xs">Score: {zone.properties.score}</p>
                )}
                {zone.properties?.behavior && (
                  <p className="text-xs text-gray-500">{zone.properties.behavior}</p>
                )}
                {zone.properties?.pipeline && (
                  <Badge variant="outline" className="text-xs mt-1 bg-green-50">
                    {zone.properties.pipeline}
                  </Badge>
                )}
                {zone.organic && (
                  <Badge variant="outline" className="text-xs mt-1">Organic</Badge>
                )}
              </div>
            </Popup>
          </Polygon>
        );
      })}
    </>
  );
};

/**
 * Rendu des corridors de mouvement (LineStrings) - Legacy
 */
const CorridorsRenderer = ({ corridors, isVisible }) => {
  if (!isVisible || !corridors || corridors.length === 0) return null;
  
  return (
    <>
      {corridors.map((corridor) => {
        if (!corridor.geometry || corridor.geometry.type !== 'LineString') return null;
        
        const positions = corridor.geometry.coordinates?.map(coord => [coord[1], coord[0]]) || [];
        
        if (positions.length < 2) return null;
        
        return (
          <Polyline
            key={corridor.corridor_id}
            positions={positions}
            pathOptions={{
              color: corridor.rendering?.stroke_color || BIONIC_COLORS.gold.primary,
              weight: corridor.rendering?.stroke_width || 3,
              dashArray: corridor.rendering?.dash_array || '5,5'
            }}
          >
            <Popup>
              <div className="p-2">
                <h4 className="font-semibold text-sm">Corridor de Mouvement</h4>
                <p className="text-xs text-gray-600">ID: {corridor.corridor_id}</p>
                {corridor.properties?.score && (
                  <p className="text-xs">Score: {corridor.properties.score}</p>
                )}
                {corridor.properties?.flow_direction && (
                  <p className="text-xs">Direction: {corridor.properties.flow_direction}</p>
                )}
              </div>
            </Popup>
          </Polyline>
        );
      })}
    </>
  );
};

// =============================================================================
// NIVEAU 4 — CORRIDORS RENDERER (Styles Officiels)
// =============================================================================

/**
 * NORMES GRAPHIQUES OFFICIELLES — CORRIDORS (NIVEAU 4)
 */
const CORRIDOR_STYLES = {
  primary: {
    color: '#FF8A00',      // Orange
    weight: 4,
    opacity: 1.0,
    dashArray: null        // Continu
  },
  secondary: {
    color: '#FFC04D',      // Jaune-orangé
    weight: 3,
    opacity: 1.0,
    dashArray: '12,6'      // Pointillé long
  },
  seasonal: {
    color: '#4DA6FF',      // Bleu
    weight: 3,
    opacity: 1.0,
    dashArray: '6,4'       // Pointillé court
  },
  thermal: {
    color: '#FF4D4D',      // Rouge
    weight: 5,
    opacity: 0.6,          // Semi-transparent
    dashArray: null        // Continu
  },
  risk: {
    color: '#CC0000',      // Rouge foncé
    weight: 6,
    opacity: 1.0,
    dashArray: null,       // Continu
    haloColor: '#FFCCCC',  // Halo rose pâle
    haloOpacity: 0.4,
    haloWeight: 12
  }
};

/**
 * Obtenir le badge de qualité pour un corridor
 */
const getCorridorQualityBadge = (quality) => {
  const badges = {
    excellent: { label: 'Excellent', color: '#00A676' },
    good: { label: 'Bon', color: '#C9A86A' },
    moderate: { label: 'Modéré', color: '#1E3A8A' },
    poor: { label: 'Faible', color: '#C26A2E' },
    blocked: { label: 'Bloqué', color: '#B91C1C' }
  };
  return badges[quality] || badges.moderate;
};

/**
 * Rendu des corridors NIVEAU 4 avec styles officiels
 */
const Niveau4CorridorsRenderer = ({ corridors, visibility }) => {
  if (!corridors?.features || corridors.features.length === 0) return null;
  
  // Filtrer par type de corridor selon la visibilité
  const renderCorridor = (feature, index) => {
    const { geometry, properties } = feature;
    
    if (!geometry || geometry.type !== 'LineString') return null;
    
    const corridorType = properties?.corridor_type || 'primary';
    
    // Vérifier la visibilité pour ce type
    const isTypeVisible = visibility?.[corridorType] !== false;
    if (!isTypeVisible) return null;
    
    // Coordonnées [lng, lat] -> [lat, lng] pour Leaflet
    const positions = geometry.coordinates?.map(coord => [coord[1], coord[0]]) || [];
    if (positions.length < 2) return null;
    
    // Obtenir le style officiel ou utiliser le rendering de l'API
    const rendering = properties?.rendering || {};
    const defaultStyle = CORRIDOR_STYLES[corridorType] || CORRIDOR_STYLES.primary;
    
    const style = {
      color: rendering.stroke_color || defaultStyle.color,
      weight: rendering.stroke_width || defaultStyle.weight,
      opacity: rendering.stroke_opacity || defaultStyle.opacity,
      dashArray: rendering.dash_array || defaultStyle.dashArray,
      lineCap: rendering.line_cap || 'round',
      lineJoin: rendering.line_join || 'round'
    };
    
    const qualityBadge = getCorridorQualityBadge(properties?.quality);
    
    return (
      <React.Fragment key={properties?.corridor_id || `corridor-${index}`}>
        {/* Halo pour corridors à risque */}
        {corridorType === 'risk' && (
          <Polyline
            positions={positions}
            pathOptions={{
              color: rendering.halo_color || CORRIDOR_STYLES.risk.haloColor,
              weight: rendering.halo_weight || CORRIDOR_STYLES.risk.haloWeight,
              opacity: rendering.halo_opacity || CORRIDOR_STYLES.risk.haloOpacity,
              lineCap: 'round',
              lineJoin: 'round'
            }}
          />
        )}
        
        {/* Corridor principal */}
        <Polyline
          positions={positions}
          pathOptions={style}
        >
          <Popup>
            <div className="p-3 min-w-[220px]">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-bold text-sm">{properties?.name || 'Corridor'}</h4>
                <span 
                  className="px-2 py-0.5 rounded text-xs font-medium text-white"
                  style={{ backgroundColor: qualityBadge.color }}
                >
                  {qualityBadge.label}
                </span>
              </div>
              
              <p className="text-xs text-gray-600 mb-2">{properties?.description}</p>
              
              <div className="grid grid-cols-2 gap-2 text-xs border-t pt-2">
                <div>
                  <span className="text-gray-500">Type:</span>
                  <span className="ml-1 font-medium capitalize">{corridorType}</span>
                </div>
                <div>
                  <span className="text-gray-500">Score:</span>
                  <span className="ml-1 font-medium">{properties?.composite_score?.toFixed(1)}</span>
                </div>
                <div>
                  <span className="text-gray-500">Longueur:</span>
                  <span className="ml-1 font-medium">{(properties?.total_length_m / 1000)?.toFixed(2)} km</span>
                </div>
                <div>
                  <span className="text-gray-500">Priorité:</span>
                  <span className="ml-1 font-medium capitalize">{properties?.priority}</span>
                </div>
              </div>
              
              {/* Facteurs d'influence */}
              {properties?.factors && (
                <div className="mt-2 pt-2 border-t">
                  <p className="text-xs text-gray-500 mb-1">Facteurs d'influence:</p>
                  <div className="flex flex-wrap gap-1">
                    {Object.entries(properties.factors).map(([key, value]) => (
                      <span 
                        key={key}
                        className="px-1.5 py-0.5 rounded text-[10px] bg-gray-100"
                        title={`${key}: ${value}`}
                      >
                        {key.substring(0, 3)}: {value?.toFixed(0)}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Avertissement pour corridors à risque */}
              {corridorType === 'risk' && (
                <div className="mt-2 p-2 bg-red-50 rounded text-xs text-red-700 flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" />
                  <span>Zone à éviter - Pression humaine détectée</span>
                </div>
              )}
              
              {/* Saisons actives */}
              {properties?.active_seasons?.length > 0 && (
                <div className="mt-2 text-xs text-gray-500">
                  Saisons: {properties.active_seasons.join(', ')}
                </div>
              )}
            </div>
          </Popup>
        </Polyline>
      </React.Fragment>
    );
  };
  
  return <>{corridors.features.map(renderCorridor)}</>;
};

/**
 * Rendu des points d'attraction
 */
const AttractionPointsRenderer = ({ points, isVisible, type, color }) => {
  if (!isVisible || !points || points.length === 0) return null;
  
  return (
    <>
      {points.map((point) => {
        if (!point.coordinates) return null;
        
        const position = [point.coordinates.lat, point.coordinates.lng];
        
        return (
          <Marker
            key={point.point_id}
            position={position}
            icon={attractionIcon(color)}
          >
            <Popup>
              <div className="p-2">
                <h4 className="font-semibold text-sm">{type}</h4>
                <p className="text-xs text-gray-600">ID: {point.point_id}</p>
                {point.score && (
                  <p className="text-xs">Score: {point.score}</p>
                )}
                {point.type && (
                  <p className="text-xs">Type: {point.type}</p>
                )}
                {point.distance_m && (
                  <p className="text-xs">Distance: {point.distance_m}m</p>
                )}
              </div>
            </Popup>
          </Marker>
        );
      })}
    </>
  );
};

/**
 * Rendu des refuges thermiques
 */
const ThermalRefugesRenderer = ({ refuges, isVisible }) => {
  if (!isVisible || !refuges || refuges.length === 0) return null;
  
  return (
    <>
      {refuges.map((refuge) => {
        if (!refuge.geometry || refuge.geometry.type !== 'Polygon') return null;
        
        const positions = refuge.geometry.coordinates[0]?.map(coord => [coord[1], coord[0]]) || [];
        
        if (positions.length < 3) return null;
        
        return (
          <Polygon
            key={refuge.zone_id}
            positions={positions}
            pathOptions={{
              fillColor: '#00BCD4',
              fillOpacity: 0.25,
              color: '#00BCD4',
              weight: 1.5
            }}
          >
            <Popup>
              <div className="p-2">
                <h4 className="font-semibold text-sm">Refuge Thermique</h4>
                <p className="text-xs text-gray-600">ID: {refuge.zone_id}</p>
                {refuge.temperature_delta && (
                  <p className="text-xs">Delta T°: {refuge.temperature_delta}°C</p>
                )}
              </div>
            </Popup>
          </Polygon>
        );
      })}
    </>
  );
};

/**
 * Rendu des routes optimales
 */
const OptimalRoutesRenderer = ({ routes, isVisible }) => {
  if (!isVisible || !routes || routes.length === 0) return null;
  
  return (
    <>
      {routes.map((route) => {
        if (!route.geometry || route.geometry.type !== 'LineString') return null;
        
        const positions = route.geometry.coordinates?.map(coord => [coord[1], coord[0]]) || [];
        
        if (positions.length < 2) return null;
        
        return (
          <Polyline
            key={route.route_id}
            positions={positions}
            pathOptions={{
              color: '#E91E63',
              weight: 3,
              opacity: 0.8
            }}
          >
            <Popup>
              <div className="p-2">
                <h4 className="font-semibold text-sm">Route Optimale</h4>
                <p className="text-xs text-gray-600">ID: {route.route_id}</p>
                <p className="text-xs">Distance: {route.distance_m}m</p>
                <p className="text-xs">Difficulté: {route.difficulty}</p>
                <p className="text-xs">Discrétion: {Math.round(route.stealth_score * 100)}%</p>
              </div>
            </Popup>
          </Polyline>
        );
      })}
    </>
  );
};

/**
 * Rendu des positions d'affût
 */
const StandPositionsRenderer = ({ positions, isVisible }) => {
  if (!isVisible || !positions || positions.length === 0) return null;
  
  return (
    <>
      {positions.map((pos) => {
        if (!pos.coordinates) return null;
        
        const position = [pos.coordinates.lat, pos.coordinates.lng];
        
        return (
          <Marker
            key={pos.position_id}
            position={position}
            icon={attractionIcon('#F44336')}
          >
            <Popup>
              <div className="p-2">
                <h4 className="font-semibold text-sm">Position d'Affût</h4>
                <p className="text-xs text-gray-600">ID: {pos.position_id}</p>
                <p className="text-xs">Type: {pos.type}</p>
                <p className="text-xs">Score: {pos.score}</p>
              </div>
            </Popup>
          </Marker>
        );
      })}
    </>
  );
};

/**
 * Rendu des sentiers
 */
const TrailsRenderer = ({ trails, isVisible }) => {
  if (!isVisible || !trails || trails.length === 0) return null;
  
  return (
    <>
      {trails.map((trail) => {
        if (!trail.geometry || trail.geometry.type !== 'LineString') return null;
        
        const positions = trail.geometry.coordinates?.map(coord => [coord[1], coord[0]]) || [];
        
        if (positions.length < 2) return null;
        
        return (
          <Polyline
            key={trail.trail_id}
            positions={positions}
            pathOptions={{
              color: '#795548',
              weight: 2,
              dashArray: '3,6'
            }}
          >
            <Popup>
              <div className="p-2">
                <h4 className="font-semibold text-sm">Sentier</h4>
                <p className="text-xs text-gray-600">ID: {trail.trail_id}</p>
                <p className="text-xs">Type: {trail.type}</p>
                <p className="text-xs">Condition: {trail.condition}</p>
              </div>
            </Popup>
          </Polyline>
        );
      })}
    </>
  );
};

// =============================================================================
// ANALYSIS INFO PANEL
// =============================================================================

const AnalysisInfoPanel = ({ analysisData, isLoading }) => {
  if (isLoading) {
    return (
      <div className="p-4 flex items-center justify-center">
        <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
        <span className="ml-2 text-sm text-gray-400">Analyse en cours...</span>
      </div>
    );
  }
  
  if (!analysisData) {
    return (
      <div className="p-4 text-center">
        <Info className="w-8 h-8 mx-auto text-gray-500 mb-2" />
        <p className="text-sm text-gray-400">Aucune analyse chargée</p>
        <p className="text-xs text-gray-500 mt-1">Sélectionnez un waypoint pour analyser</p>
      </div>
    );
  }
  
  const { scores, legal_status, metadata } = analysisData;
  
  return (
    <div className="p-4 space-y-3">
      {/* Score principal */}
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-400">Score BIONIC</span>
        <div className="flex items-center gap-2">
          <span 
            className="text-2xl font-bold"
            style={{ color: scores?.category?.color || BIONIC_COLORS.gold.primary }}
          >
            {scores?.score_bionic_final?.toFixed(1) || '—'}
          </span>
          <Badge 
            variant="outline"
            style={{ 
              borderColor: scores?.category?.color,
              color: scores?.category?.color 
            }}
          >
            {scores?.category?.label || scores?.level}
          </Badge>
        </div>
      </div>
      
      <Separator style={{ backgroundColor: BIONIC_COLORS.gray[700] }} />
      
      {/* Statut légal */}
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-400">Statut Légal</span>
        <Badge 
          variant={legal_status?.is_legal_period ? 'default' : 'destructive'}
          className="text-xs"
        >
          {legal_status?.legal_badge || 'N/A'}
        </Badge>
      </div>
      
      {/* Heures légales */}
      {legal_status && (
        <div className="text-xs text-gray-500">
          Heures légales: {legal_status.legal_start} - {legal_status.legal_end}
        </div>
      )}
      
      <Separator style={{ backgroundColor: BIONIC_COLORS.gray[700] }} />
      
      {/* Métadonnées */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>Temps de calcul</span>
        <span>{metadata?.processing_time_ms || '—'}ms</span>
      </div>
      
      {/* Avertissement pré-calibration */}
      <div 
        className="p-2 rounded-lg flex items-start gap-2"
        style={{ backgroundColor: `${BIONIC_COLORS.gold.primary}15` }}
      >
        <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: BIONIC_COLORS.gold.primary }} />
        <p className="text-[10px] text-gray-400">
          <span className="font-medium" style={{ color: BIONIC_COLORS.gold.primary }}>Version pré-calibrée.</span>
          {' '}Les scores sont des estimations indicatives, non validées scientifiquement.
        </p>
      </div>
      
      {/* PHASE C — Facteurs Saisonniers */}
      <Separator style={{ backgroundColor: BIONIC_COLORS.gray[700] }} />
      <SeasonalFactorsPanel analysisData={analysisData} compact={true} />
    </div>
  );
};

// =============================================================================
// MAIN COMPONENT
// =============================================================================

/**
 * CarteBionic
 * 
 * Carte interactive BIONIC V5 avec intégration des layers depuis l'API.
 * 
 * @param {Object} waypoint - Waypoint sélectionné à analyser
 * @param {string} species - Espèce cible (défaut: orignal)
 * @param {Date} targetDatetime - Date/heure cible de l'analyse
 * @param {string} analysisMode - Mode d'analyse: 'live', 'pre_rut', 'rut', 'post_rut'
 * @param {boolean} showLayerControl - Afficher le panneau de contrôle des layers
 * @param {boolean} autoAnalyze - Lancer l'analyse automatiquement au montage
 * @param {Function} onAnalysisComplete - Callback après analyse
 * @param {Function} onAnalysisModeChange - Callback lors du changement de mode
 * @param {string} className - Classes CSS additionnelles
 */
const CarteBionic = ({
  waypoint,
  species = 'orignal',
  targetDatetime = null,
  analysisMode = 'rut',
  showLayerControl = true,
  autoAnalyze = true,
  onAnalysisComplete = null,
  onAnalysisModeChange = null,
  className = ''
}) => {
  // États
  const [analysisData, setAnalysisData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [layerVisibility, setLayerVisibility] = useState(getDefaultVisibility);
  const [internalMode, setInternalMode] = useState(analysisMode);
  
  // Ref pour éviter les doubles appels
  const analysisInProgress = useRef(false);
  
  // Synchroniser le mode interne avec le mode externe
  const currentMode = onAnalysisModeChange ? analysisMode : internalMode;
  const setCurrentMode = onAnalysisModeChange || setInternalMode;
  
  // Centre de la carte
  const mapCenter = useMemo(() => {
    if (waypoint?.latitude && waypoint?.longitude) {
      return [waypoint.latitude, waypoint.longitude];
    }
    return [46.8139, -71.2080]; // Québec par défaut
  }, [waypoint]);
  
  // Fonction d'analyse - utilise le mode d'analyse actuel
  const runAnalysis = useCallback(async (modeOverride = null) => {
    if (!waypoint || analysisInProgress.current) return;
    
    const effectiveMode = modeOverride || currentMode;
    
    analysisInProgress.current = true;
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await bionicApiService.analyzeWaypoint(
        waypoint,
        targetDatetime || new Date().toISOString(),
        species,
        effectiveMode  // Mode d'analyse passé à l'API
      );
      
      setAnalysisData(result);
      
      if (onAnalysisComplete) {
        onAnalysisComplete(result);
      }
      
      const modeLabels = {
        'live': 'LIVE',
        'pre_rut': 'PRÉ-RUT',
        'rut': 'RUT',
        'post_rut': 'POST-RUT'
      };
      
      toast.success(`Analyse ${modeLabels[effectiveMode] || effectiveMode}: Score ${result.scores?.score_bionic_final?.toFixed(1)}/100`);
      
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message);
      toast.error(`Erreur d'analyse: ${err.message}`);
    } finally {
      setIsLoading(false);
      analysisInProgress.current = false;
    }
  }, [waypoint, targetDatetime, species, currentMode, onAnalysisComplete]);
  
  // Auto-analyse au montage ou changement de waypoint
  useEffect(() => {
    if (autoAnalyze && waypoint) {
      runAnalysis();
    }
  }, [waypoint?.id, autoAnalyze]); // eslint-disable-line react-hooks/exhaustive-deps
  
  // Relancer l'analyse quand le mode change (prop externe)
  useEffect(() => {
    // Ne relancer que si on a déjà des données et que le mode externe change
    if (onAnalysisModeChange && waypoint && analysisData) {
      runAnalysis(analysisMode);
    }
  }, [analysisMode]); // eslint-disable-line react-hooks/exhaustive-deps
  
  // Handler pour le changement de mode depuis LayerControlPanel
  const handleInternalModeChange = useCallback((newMode) => {
    setCurrentMode(newMode);
    // Relancer l'analyse avec le nouveau mode
    runAnalysis(newMode);
  }, [setCurrentMode, runAnalysis]);
  
  // Extraire les layers de l'analyse
  const layers = analysisData?.layers;
  
  // Vérifier la visibilité d'une sous-layer
  const isSubLayerVisible = useCallback((familyId, sublayerId) => {
    const family = layerVisibility[familyId];
    if (!family?.visible) return false;
    return family.sublayers?.[sublayerId] ?? true;
  }, [layerVisibility]);
  
  return (
    <div className={`flex gap-4 ${className}`} data-testid="carte-bionic">
      {/* Carte principale */}
      <div className="flex-1 relative">
        <Card 
          className="border-0 overflow-hidden h-[600px]"
          style={{ backgroundColor: BIONIC_COLORS.black.elevated }}
        >
          <CardHeader className="pb-2 absolute top-0 left-0 right-0 z-[1000] bg-gradient-to-b from-black/80 to-transparent">
            <CardTitle className="flex items-center justify-between text-white text-base">
              <div className="flex items-center gap-2">
                <Layers className="w-5 h-5" style={{ color: BIONIC_COLORS.gold.primary }} />
                Carte BIONIC V5
                {analysisData && (
                  <Badge variant="outline" className="text-xs ml-2">
                    {analysisData.analysis_id}
                  </Badge>
                )}
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={runAnalysis}
                disabled={isLoading || !waypoint}
                className="h-8"
              >
                <RefreshCw className={`w-4 h-4 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
                {isLoading ? 'Analyse...' : 'Actualiser'}
              </Button>
            </CardTitle>
          </CardHeader>
          
          <MapContainer
            center={mapCenter}
            zoom={13}
            style={{ height: '100%', width: '100%' }}
            className="z-0"
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            
            {/* Initialisation des panes pour superposabilité (P0.2) */}
            <LayerPanesInitializer />
            
            <MapController center={mapCenter} zoom={13} />
            
            {/* Waypoint principal */}
            {waypoint && (
              <Marker position={mapCenter} icon={waypointIcon}>
                <Popup>
                  <div className="p-2">
                    <h4 className="font-semibold">{waypoint.name}</h4>
                    <p className="text-xs text-gray-600">ID: {waypoint.id}</p>
                    <p className="text-xs">{waypoint.latitude.toFixed(5)}, {waypoint.longitude.toFixed(5)}</p>
                  </div>
                </Popup>
              </Marker>
            )}
            
            {/* ==================== BEHAVIORAL ZONES ==================== */}
            
            {/* Zones de repos */}
            <BehavioralZonesRenderer
              zones={layers?.behavioral_zones?.bedding_zones}
              isVisible={isSubLayerVisible('behavioral_zones', 'bedding_zones')}
              type="Zone de Repos"
              pane="behavioral-bedding-pane"
            />
            
            {/* Zones d'alimentation */}
            <BehavioralZonesRenderer
              zones={layers?.behavioral_zones?.feeding_zones}
              isVisible={isSubLayerVisible('behavioral_zones', 'feeding_zones')}
              type="Zone d'Alimentation"
              pane="behavioral-feeding-pane"
            />
            
            {/* Zones de rut */}
            <BehavioralZonesRenderer
              zones={layers?.behavioral_zones?.rut_zones}
              isVisible={isSubLayerVisible('behavioral_zones', 'rut_zones')}
              type="Zone de Rut"
              pane="behavioral-rut-pane"
            />
            
            {/* Corridors de mouvement */}
            <CorridorsRenderer
              corridors={layers?.behavioral_zones?.movement_corridors}
              isVisible={isSubLayerVisible('behavioral_zones', 'movement_corridors')}
            />
            
            {/* Zones d'évitement pression */}
            <BehavioralZonesRenderer
              zones={layers?.behavioral_zones?.pressure_avoidance}
              isVisible={isSubLayerVisible('behavioral_zones', 'pressure_avoidance')}
              type="Zone d'Évitement"
              pane="behavioral-pressure-pane"
            />
            
            {/* ==================== ATTRACTION POINTS ==================== */}
            
            {/* Salines */}
            <AttractionPointsRenderer
              points={layers?.attraction_points?.salines}
              isVisible={isSubLayerVisible('attraction_points', 'salines')}
              type="Saline"
              color="#FFC107"
            />
            
            {/* Sources d'eau */}
            <AttractionPointsRenderer
              points={layers?.attraction_points?.water_sources}
              isVisible={isSubLayerVisible('attraction_points', 'water_sources')}
              type="Source d'Eau"
              color="#2196F3"
            />
            
            {/* Refuges thermiques */}
            <ThermalRefugesRenderer
              refuges={layers?.attraction_points?.thermal_refuges}
              isVisible={isSubLayerVisible('attraction_points', 'thermal_refuges')}
            />
            
            {/* Affûts potentiels */}
            <AttractionPointsRenderer
              points={layers?.attraction_points?.affuts_potentiels}
              isVisible={isSubLayerVisible('attraction_points', 'affuts_potentiels')}
              type="Affût Potentiel"
              color="#FF9800"
            />
            
            {/* ==================== HUNT PLANNING ==================== */}
            
            {/* Routes optimales */}
            <OptimalRoutesRenderer
              routes={layers?.hunt_planning?.optimal_routes}
              isVisible={isSubLayerVisible('hunt_planning', 'optimal_routes')}
            />
            
            {/* Positions d'affût */}
            <StandPositionsRenderer
              positions={layers?.hunt_planning?.stand_positions}
              isVisible={isSubLayerVisible('hunt_planning', 'stand_positions')}
            />
            
            {/* Sentiers */}
            <TrailsRenderer
              trails={layers?.hunt_planning?.trails}
              isVisible={isSubLayerVisible('hunt_planning', 'trails')}
            />
            
            {/* ==================== CORRIDORS NIVEAU 4 ==================== */}
            
            {/* Corridors de déplacement (NIVEAU 4 - Habitat & Corridors) */}
            <Niveau4CorridorsRenderer
              corridors={analysisData?.corridors}
              visibility={{
                primary: isSubLayerVisible('corridors', 'primary'),
                secondary: isSubLayerVisible('corridors', 'secondary'),
                seasonal: isSubLayerVisible('corridors', 'seasonal'),
                thermal: isSubLayerVisible('corridors', 'thermal'),
                risk: isSubLayerVisible('corridors', 'risk')
              }}
            />
            
          </MapContainer>
          
          {/* Overlay d'erreur */}
          {error && (
            <div 
              className="absolute inset-0 flex items-center justify-center bg-black/70 z-[1001]"
            >
              <div className="text-center p-6">
                <AlertTriangle className="w-12 h-12 mx-auto text-red-500 mb-4" />
                <h3 className="text-white font-semibold mb-2">Erreur d'analyse</h3>
                <p className="text-gray-400 text-sm mb-4">{error}</p>
                <Button onClick={runAnalysis} variant="outline">
                  Réessayer
                </Button>
              </div>
            </div>
          )}
        </Card>
      </div>
      
      {/* Panneau latéral */}
      {showLayerControl && (
        <div className="w-80 space-y-4">
          {/* Info analyse */}
          <Card 
            className="border-0"
            style={{ backgroundColor: BIONIC_COLORS.black.elevated }}
          >
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-white text-base">
                <Target className="w-5 h-5" style={{ color: BIONIC_COLORS.gold.primary }} />
                Analyse
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <AnalysisInfoPanel 
                analysisData={analysisData} 
                isLoading={isLoading} 
              />
            </CardContent>
          </Card>
          
          {/* Contrôle des layers */}
          <LayerControlPanel
            layerVisibility={layerVisibility}
            onLayerVisibilityChange={setLayerVisibility}
            analysisMode={currentMode}
            onAnalysisModeChange={handleInternalModeChange}
            compact={true}
            showQuickActions={true}
            defaultAllOpen={false}
          />
        </div>
      )}
    </div>
  );
};

// =============================================================================
// EXPORTS
// =============================================================================

export default CarteBionic;

export { bionicApiService };
