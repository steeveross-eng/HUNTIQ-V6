/**
 * MODULE F — BIONIC Zone Service V2
 * Frontend Renderer — 100% Backend-Driven
 *
 * RÈGLE ABSOLUE:
 * - Aucune génération de zones côté client
 * - Aucun calcul de scoring
 * - Aucun traitement de données
 * - Backend = seule source de vérité
 * - Backend fetch ses propres exclusions Overpass
 *
 * Ce service:
 * 1. Fetch les zones organiques BIONIC depuis le backend pipeline V2
 * 2. Retourne les zones prêtes pour Leaflet
 */

const API_BASE = process.env.REACT_APP_BACKEND_URL;

// ============================================
// BIONIC V5 300% — ISOLATION STRUCTURELLE/DYNAMIQUE
// ============================================

/**
 * Couches STRUCTURELLES — calculées une seule fois, verrouillées (State Locking)
 * Aucun recalcul par zoom/pan/toggle dynamique
 */
export const STRUCTURAL_LAYER_IDS = new Set([
  'habitats', 'rut', 'repos', 'alimentation', 'corridors',
  'salines', 'affuts', 'trajets', 'peuplements', 'hydro',
  'pentes', 'orientation', 'ensoleillement', 'altitude', 'ndvi'
]);

/**
 * Couches DYNAMIQUES — recalculées en temps réel
 * Isolées dans leur propre pipeline
 */
export const DYNAMIC_LAYER_IDS = new Set([
  'conditions', 'exclusions', 'dynamic', 'meteo', 'pression', 'stress_thermique'
]);

// ============================================
// LAYER DEFINITIONS (affichage uniquement)
// ============================================
export const LAYER_TYPES = [
  { id: 'habitats',       label: 'Habitat optimal',        color: '#10B981', category: 'environmental', priority: 1 },
  { id: 'rut',            label: 'Zone de rut',            color: '#FF4D6D', category: 'behavioral',    priority: 2 },
  { id: 'repos',          label: 'Zone de repos',          color: '#8B5CF6', category: 'behavioral',    priority: 3 },
  { id: 'alimentation',   label: "Zone d'alimentation",    color: '#22C55E', category: 'behavioral',    priority: 4 },
  { id: 'corridors',      label: 'Corridor faunique',      color: '#06B6D4', category: 'behavioral',    priority: 5 },
  { id: 'peuplements',    label: 'Peuplements forestiers',  color: '#15803D', category: 'environmental', priority: 6 },
  { id: 'ndvi',           label: 'NDVI / Densité végétale',color: '#66BB6A', category: 'environmental', priority: 7 },
  { id: 'hydro',          label: 'Hydrographie',           color: '#3B82F6', category: 'environmental', priority: 8 },
  { id: 'pentes',         label: 'Pentes',                 color: '#FF7043', category: 'environmental', priority: 9 },
  { id: 'orientation',    label: 'Orientation',            color: '#2196F3', category: 'environmental', priority: 10 },
  { id: 'ensoleillement', label: 'Ensoleillement',         color: '#FCD34D', category: 'environmental', priority: 11 },
  { id: 'salines',        label: 'Saline potentielle',     color: '#FFFF00', category: 'strategic',     priority: 12 },
  { id: 'affuts',         label: 'Affût potentiel',        color: '#F5A623', category: 'strategic',     priority: 13 },
  { id: 'trajets',        label: 'Trajets de chasse',      color: '#FF9800', category: 'strategic',     priority: 14 },
  { id: 'altitude',       label: 'Altitude relative',      color: '#78909C', category: 'environmental', priority: 15 },
];

const SPECIES_LAYERS = {
  moose:       ['habitats', 'rut', 'repos', 'alimentation', 'corridors', 'hydro', 'salines', 'peuplements', 'pentes', 'affuts', 'trajets'],
  deer:        ['habitats', 'rut', 'repos', 'alimentation', 'corridors', 'affuts', 'peuplements', 'ensoleillement', 'trajets', 'salines'],
  bear:        ['habitats', 'repos', 'alimentation', 'corridors', 'hydro', 'peuplements', 'ndvi', 'pentes', 'trajets'],
  wild_turkey: ['habitats', 'alimentation', 'repos', 'affuts', 'peuplements', 'ensoleillement', 'ndvi', 'trajets'],
  elk:         ['habitats', 'rut', 'repos', 'alimentation', 'corridors', 'peuplements', 'pentes', 'altitude', 'trajets', 'affuts'],
};

export const getSpeciesLayers = (speciesId) => {
  if (!speciesId || speciesId === 'tous') return null;
  return SPECIES_LAYERS[speciesId] || null;
};

// ============================================
// ORGANIC ZONES — 100% BACKEND
// ============================================

let _zoneCache = { key: null, data: null };

/**
 * Fetch les zones organiques depuis le backend pipeline V2.
 * Backend gère TOUT: rasterisation, Marching Squares, Chaikin, exclusion Overpass, scoring.
 *
 * @param {Object} bounds      { north, south, east, west }
 * @param {number} zoom        Niveau de zoom
 * @param {Object} layersVisible { habitats: true, rut: false, ... }
 * @param {string} speciesId   'moose', 'deer', etc.
 * @returns {Object} { zones: [], stats: {} }
 */
export const generateBionicZonesV5 = async (bounds, zoom, layersVisible, speciesId = 'tous', waypointCenter = null, biologicalSeason = null) => {
  if (!bounds) return { zones: [], corridors: [], stats: { total: 0 } };

  const speciesLayers = getSpeciesLayers(speciesId);
  const activeLayers = LAYER_TYPES
    .filter(lt => layersVisible[lt.id])
    .filter(lt => !speciesLayers || speciesLayers.includes(lt.id))
    .map(lt => lt.id);

  if (activeLayers.length === 0) return { zones: [], corridors: [], stats: { total: 0 } };

  const cacheKey = `${bounds.south.toFixed(4)}_${bounds.west.toFixed(4)}_${bounds.north.toFixed(4)}_${bounds.east.toFixed(4)}_${speciesId}_${activeLayers.join(',')}_${biologicalSeason || 'auto'}`;
  if (_zoneCache.key === cacheKey && _zoneCache.data) return _zoneCache.data;

  const speciesMap = { orignal: 'moose', chevreuil: 'deer', ours: 'bear', dindon: 'wild_turkey', wapiti: 'elk' };
  const backendSpecies = speciesMap[speciesId] || speciesId || 'moose';

  const resolution = zoom >= 16 ? 100 : zoom >= 14 ? 80 : 60;
  const maxPerLayer = zoom >= 16 ? 12 : zoom >= 14 ? 10 : 8;

  try {
    const requestBody = {
        bounds: { north: bounds.north, south: bounds.south, east: bounds.east, west: bounds.west },
        species: backendSpecies === 'tous' ? 'moose' : backendSpecies,
        layers: activeLayers,
        resolution,
        max_zones_per_layer: maxPerLayer,
        include_scoring: true,
      };
      if (waypointCenter) {
        requestBody.waypoint_center = {
          lat: waypointCenter.lat || waypointCenter.latitude,
          lng: waypointCenter.lng || waypointCenter.longitude,
        };
      }
      if (biologicalSeason) {
        requestBody.biological_season = biologicalSeason;
      }

    const resp = await fetch(`${API_BASE}/api/v1/bionic/organic-zones`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    });

    if (!resp.ok) {
      console.error('[BIONIC V5] Organic zones API error:', resp.status);
      return { zones: [], corridors: [], stats: { total: 0, error: true } };
    }

    const geojson = await resp.json();

    const zones = (geojson.features || []).map((feature, idx) => {
      const props = feature.properties || {};
      const coords = feature.geometry?.coordinates?.[0] || [];
      const positions = coords.map(c => [c[1], c[0]]);

      return {
        id: feature.id || `organic-${idx}`,
        layerId: props.layer_id,
        positions,
        color: props.style?.stroke_color || '#999',
        score: props.score || 0,
        label: props.label || '',
        category: props.category || '',
        center: [props.centroid_lat || 0, props.centroid_lng || 0],
        areaM2: Math.round(props.area_m2 || 0),
        compactness: props.compactness || 0,
        vertices: props.vertices || 0,
        zoom,
        priority: LAYER_TYPES.findIndex(lt => lt.id === props.layer_id) + 1,
        // V8.2.1: Weather influence data
        weatherMultiplier: props.weather_multiplier || null,
        weatherGlobal: props.weather_global || null,
        scorePreWeather: props.score_pre_weather || null,
        weatherBadges: props.weather_badges || [],
      };
    });

    // V9 Corridors — Multi-band ribbon polygons with 5-level gradient
    const corridors = (geojson.corridors || []).map((corridor) => {
      const props = corridor.properties || {};
      const coords = corridor.geometry?.coordinates || [];
      const positions = coords.map(c => [c[1], c[0]]);
      const style = props.style || {};
      const scoring = props.scoring || {};

      // V9: Extract polygon bands and smoothed centerline
      const bands = props.bands || [];
      const centerline = props.centerline || null;

      return {
        id: corridor.id || `corridor-${props.from_zone_id}-${props.to_zone_id}`,
        positions,
        color: style.color || '#06B6D4',
        weight: style.width || 2.5,
        opacity: style.opacity || 0.85,
        dashArray: style.dasharray === 'none' ? null : style.dasharray,
        source: props.source,
        sex: props.sex,
        confidence: props.confidence,
        corridorType: props.corridor_type,
        classificationV9: props.classification_v9 || null,
        fromZoneType: props.from_zone_type,
        toZoneType: props.to_zone_type,
        distanceM: props.distance_m,
        pathfinding: props.pathfinding || 'unknown',
        score: scoring.score || 0,
        subscores: scoring.subscores || {},
        justification: scoring.justification || [],
        demEnhanced: props.dem_enhanced || false,
        inPerimeter: props.in_perimeter || false,
        certainty: props.certainty || 0,
        enginesEvaluated: props.engines_evaluated || 0,
        v9Pipeline: props.v9_pipeline || false,
        continuityValid: props.continuity_valid,
        scores10x: props.scores_10x || null,
        // V9: Band data for multi-layer polygon rendering
        bands,
        centerline,
        hasBands: bands.length > 0,
        bandCount: props.band_count || bands.length,
      };
    });

    const result = {
      zones,
      corridors,
      stats: {
        total: zones.length,
        corridors_total: corridors.length,
        corridors_real: corridors.filter(c => c.source === 'real').length,
        corridors_ai: corridors.filter(c => c.source === 'ai').length,
        ...(geojson.stats || {}),
      },
      rejection_diagnostics: geojson.rejection_diagnostics || null,
      // V8.2.1: Weather influence metadata
      weather_metadata: geojson.weather_metadata || null,
    };

    // T4 COHERENCE: Validate backend zone count matches parsed zones
    const backendT4Count = geojson.stats?.t4_zone_count;
    const backendFeatureCount = (geojson.features || []).length;
    if (backendT4Count !== undefined && backendT4Count !== zones.length) {
      console.warn(
        `[T4-COHERENCE] MISMATCH: backend t4_zone_count=${backendT4Count}, ` +
        `geojson.features=${backendFeatureCount}, parsed zones=${zones.length}`
      );
      result.stats.t4_mismatch = true;
      result.stats.t4_backend_count = backendT4Count;
    }

    _zoneCache = { key: cacheKey, data: result };
    return result;

  } catch (err) {
    console.error('[BIONIC V5] Organic zones fetch error:', err);
    return { zones: [], corridors: [], stats: { total: 0, error: true } };
  }
};

export const generateWaypointZonesV5 = async (waypoint, zoom, layersVisible, speciesId = 'tous', biologicalSeason = null) => {
  const radius = 0.015;
  const lat = waypoint.lat || waypoint.latitude;
  const lng = waypoint.lng || waypoint.longitude;
  const bounds = {
    south: lat - radius,
    north: lat + radius,
    west: lng - radius,
    east: lng + radius,
  };
  const waypointCenter = { lat, lng };
  return generateBionicZonesV5(bounds, Math.max(zoom, 14), layersVisible, speciesId, waypointCenter, biologicalSeason);
};

// Legacy exports — kept for backward compatibility (no-op, scoring is backend-only)
export const fetchTerrainExclusions = async () => [];
export const ZONE_LIMITS = { TARGET_AREA_M2: 6500, MIN_AREA_M2: 4500, MAX_AREA_M2: 10000 };
export const calculateZoneScore = () => 0;
export const calculatePolygonAreaM2 = () => 0;
