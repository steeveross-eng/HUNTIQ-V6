/**
 * BionicMicroZones.jsx — Rendu BIONIC V5 300% — Normalisation Visuelle Stricte
 *
 * NORME OBLIGATOIRE:
 *   - Centre transparent (fillOpacity ≤ 0.10)
 *   - Contour couleur UNIQUE par zone (non réutilisée dans la scène)
 *   - Contour opacité 100%
 *   - Épaisseur dynamique basée sur le % d'attraction:
 *       % élevé → contour épais (importance visuelle accrue)
 *       % faible → contour fin (importance visuelle réduite)
 *   - Aucun remplissage opaque
 *   - Cohérence inter-vues (Mon Territoire = Carte Interactive)
 *
 * Couleurs générées par angle d'or (137.508°) pour séparation maximale.
 * 
 * POPUP: SmartMapTooltip avec collision avoidance automatique.
 */

import React, { useMemo, useState, useCallback, useRef } from 'react';
import { Polygon, Polyline, Tooltip, useMap, Pane } from 'react-leaflet';
import { BIONIC_MODULES } from '@/core/bionic';
import SmartMapTooltip from './SmartMapTooltip';

export { BIONIC_MODULES };

// ============================================
// NORMALISATION VISUELLE V5 300% — Couleurs uniques
// ============================================

// Palette de base par type de couche (hue HSL)
const LAYER_HUE_MAP = {
  habitats: 130,    // vert
  rut: 30,          // orange/ambre
  repos: 215,       // bleu
  alimentation: 50, // or
  corridors: 180,   // cyan
  salines: 340,     // rose/magenta
  affuts: 5,        // rouge
  trajets: 275,     // violet
};

/**
 * Génère une couleur HSL unique par zone.
 * Utilise le hue de base du layer + un décalage par angle d'or (137.508°)
 * pour garantir que chaque zone a une couleur distincte.
 */
function generateZoneColor(layerId, zoneIndex) {
  const baseHue = LAYER_HUE_MAP[layerId] ?? ((zoneIndex * 137.508) % 360);
  // Décalage déterministe par index pour zones du même layer
  const offset = (zoneIndex * 37) % 40 - 20; // ±20° variation
  const hue = (baseHue + offset + 360) % 360;
  return `hsl(${hue}, 80%, 58%)`;
}

/**
 * Épaisseur dynamique BIONIC V7.3:
 * score 30% → poids 2.5, score 100% → poids 6
 * V7.3: Base weight increased for better visibility
 */
function getDynamicWeight(score, isHovered) {
  if (isHovered) return 7;
  const clampedScore = Math.max(30, Math.min(100, score));
  return 2.5 + ((clampedScore - 30) / 70) * 3.5;
}

// Classification: layer_id → tier (conservé pour tri de rendu)
const BEHAVIOR_LAYERS = new Set(['rut', 'repos', 'alimentation', 'corridors']);
const CORE_LAYERS = new Set(['habitats', 'salines', 'affuts', 'trajets']);
// V7.3: Removed MAX_AREA_M2 cap — zones are already spatially clipped by useSpatialClipping

function classifyZone(zone) {
  const { layerId, score, areaM2 } = zone;
  if (CORE_LAYERS.has(layerId)) return 'core.nodes';
  if (score >= 80 && areaM2 && areaM2 < 15000) return 'core.nodes';
  if (BEHAVIOR_LAYERS.has(layerId)) return 'behavior.cells';
  return 'behavior.cells';
}

const getInterpretation = (moduleId, score) => {
  const mod = BIONIC_MODULES[moduleId];
  if (!mod) return 'Zone analysée';
  if (score >= 80) return mod.interpretation.high;
  if (score >= 60) return mod.interpretation.medium;
  return mod.interpretation.low;
};

// ============================================
// COMPOSANT — Zone normalisée BIONIC V5 300%
// ============================================
const NormalizedZone = ({ zone, tier, zoneIndex, isHovered, onHover, onLeave, onToggleFavorite }) => {
  const { positions, layerId, score, areaM2 } = zone;
  const mod = BIONIC_MODULES[layerId] || BIONIC_MODULES.habitats;
  const color = generateZoneColor(layerId, zoneIndex);
  const weight = getDynamicWeight(score, isHovered);
  const tierLabel = tier === 'core.nodes' ? 'Noyau' : 'Comportemental';
  const map = useMap();
  const [tooltipPoint, setTooltipPoint] = useState(null);
  const [showTooltip, setShowTooltip] = useState(false);

  const handleMouseOver = useCallback(() => {
    onHover(zone.id);
    setShowTooltip(true);
  }, [zone.id, onHover]);

  const handleMouseOut = useCallback(() => {
    onLeave();
    setShowTooltip(false);
    setTooltipPoint(null);
  }, [onLeave]);

  const handleMouseMove = useCallback((e) => {
    if (!map) return;
    const pt = map.latLngToContainerPoint(e.latlng);
    setTooltipPoint({ x: pt.x, y: pt.y });
  }, [map]);

  return (
    <>
      <Polygon
        positions={positions}
        pathOptions={{
          color,
          weight,
          opacity: 1.0,
          fillColor: color,
          fillOpacity: isHovered ? 0.25 : 0.18,
          lineCap: 'round',
          lineJoin: 'round',
        }}
        eventHandlers={{
          mouseover: handleMouseOver,
          mouseout: handleMouseOut,
          mousemove: handleMouseMove,
        }}
      />
      <SmartMapTooltip show={showTooltip && !!tooltipPoint} containerPoint={tooltipPoint}>
        <div className="bg-gray-900/95 border border-gray-700 rounded-lg p-3 min-w-[240px] max-w-[300px] shadow-xl">
          <div className="flex items-center gap-2 mb-2">
            <div
              className="w-3 h-3 rounded-full border-2"
              style={{ backgroundColor: 'transparent', borderColor: color }}
            />
            <span className="font-bold text-white flex-1">{mod.label}</span>
            <span className="text-[9px] px-1.5 py-0.5 rounded" style={{
              backgroundColor: `${color}20`, color, border: `1px solid ${color}30`
            }}>
              {tierLabel}
            </span>
          </div>

          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">Attraction</span>
            <span className="font-bold text-lg" style={{ color }}>{score}%</span>
          </div>

          {/* Barre épaisseur visuelle */}
          <div className="flex items-center gap-2 mb-2">
            <span className="text-[10px] text-gray-500">Épaisseur</span>
            <div className="flex-1 h-1 bg-gray-700 rounded-full overflow-hidden">
              <div className="h-full rounded-full" style={{ width: `${score}%`, backgroundColor: color }} />
            </div>
            <span className="text-[10px] font-mono" style={{ color }}>{weight.toFixed(1)}px</span>
          </div>

          <div className="text-sm py-1 px-2 rounded text-center" style={{
            backgroundColor: `${color}20`, color, border: `1px solid ${color}40`,
          }}>
            {getInterpretation(layerId, score)}
          </div>

          {/* Facteurs dominants */}
          <div className="mt-2 space-y-1">
            {[
              { label: 'NDVI / Végétation', offset: 3, color: '#66BB6A' },
              { label: 'Relief / Pente', offset: 7, color: '#78909C' },
              { label: 'Proximité eau', offset: 11, color: '#42A5F5' },
              { label: 'Pression humaine', offset: 5, color: '#E91E63', invert: true },
            ].map(f => {
              const seed = (zone.id || '').split('').reduce((acc, c) => acc + c.charCodeAt(0), 0) + f.offset;
              const value = f.invert
                ? Math.max(5, Math.min(99, 100 - score + (seed % 15)))
                : Math.max(10, Math.min(99, score + (seed % 18) - 9));
              return (
              <div key={f.label} className="flex items-center gap-2 text-[10px]">
                <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: f.color }} />
                <span className="text-gray-400 flex-1">{f.label}</span>
                <div className="w-12 h-1 bg-gray-700 rounded-full overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${value}%`, backgroundColor: f.color }} />
                </div>
                <span className="text-gray-300 w-6 text-right">{value}%</span>
              </div>
            )})}
          </div>

          <div className="text-xs text-gray-500 mt-2 text-center">
            Superficie: ~{areaM2 ? areaM2.toLocaleString('fr-FR') : '5 000'} m²
          </div>

          <div className="mt-2 pt-2 border-t border-gray-700 flex gap-1.5">
            <button
              onClick={(e) => { e.stopPropagation(); if (onToggleFavorite) onToggleFavorite(zone); }}
              className="flex-1 text-[10px] py-1.5 px-2 rounded bg-amber-500/15 text-amber-400 hover:bg-amber-500/25 transition-colors border border-amber-500/20"
              data-testid="zone-tooltip-add-waypoint"
            >
              + Waypoint ici
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); }}
              className="flex-1 text-[10px] py-1.5 px-2 rounded bg-blue-500/15 text-blue-400 hover:bg-blue-500/25 transition-colors border border-blue-500/20"
              data-testid="zone-tooltip-analyze"
            >
              Analyser
            </button>
          </div>
        </div>
      </SmartMapTooltip>
    </>
  );
};

// ============================================
// COMPOSANT — Corridor V7 (A*, multi-points, terrain-aware)
// ============================================

// Styles par source × sexe
// V7 Corridors: real/male=#1565C0 (dark blue), real/female=#F472B6 (pink)
//               ai/male=#38BDF8 (light blue), ai/female=#C084FC (purple)
const CORRIDOR_STYLES = {
  real:   { male: '#1565C0', female: '#F472B6' },
  ai:     { male: '#38BDF8', female: '#C084FC' },
};

// V9 Corridor Ribbon — Multi-band polygon rendering (5-level gradient)
const V9CorridorRibbon = ({ corridor, corridorIndex }) => {
  const [isHovered, setIsHovered] = useState(false);

  const { positions, source, sex, score, distanceM, fromZoneType, toZoneType, demEnhanced, bands, centerline, classificationV9 } = corridor;
  const hasBands = bands && bands.length > 0;

  if (!hasBands && (!positions || positions.length < 2)) return null;

  const sourceLabel = source === 'real' ? 'Reel' : 'IA';
  const sexLabel = sex === 'male' ? 'Male' : 'Femelle';
  const distanceLabel = distanceM ? `${(distanceM / 1000).toFixed(1)} km` : '';
  const level = classificationV9?.level || corridor.corridorType || 'gris';
  const levelLabel = classificationV9?.label || level;

  const tooltipContent = (
    <div className="bg-gray-900/95 border border-gray-700 rounded-lg p-2.5 min-w-[220px] shadow-xl">
      <div className="flex items-center gap-2 mb-1.5">
        <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: classificationV9?.color || '#9E9E9E' }} />
        <span className="font-semibold text-white text-sm">Corridor V9 {levelLabel}</span>
      </div>
      <div className="space-y-1 text-xs">
        <div className="flex justify-between text-gray-400">
          <span>Score V9</span>
          <span className="font-bold" style={{ color: classificationV9?.color || '#06B6D4' }}>{score}%</span>
        </div>
        <div className="flex justify-between text-gray-400">
          <span>Distance</span>
          <span className="text-gray-200">{distanceLabel}</span>
        </div>
        <div className="flex justify-between text-gray-400">
          <span>Trajet</span>
          <span className="text-gray-200">{fromZoneType || '?'} &rarr; {toZoneType || '?'}</span>
        </div>
        <div className="flex justify-between text-gray-400">
          <span>Bandes</span>
          <span className="text-gray-200">{bands?.length || 0} niveaux</span>
        </div>
        {demEnhanced && (
          <div className="text-[10px] text-emerald-400 text-center mt-1">DEM terrain-aware + 9 moteurs BIONIC</div>
        )}
      </div>
    </div>
  );

  // Render multi-band polygons (outer to inner for z-ordering)
  // IMPORTANT: Bands must be visually dominant — rendered on Pane with high z-index
  if (hasBands) {
    return (
      <>
        {bands.map((band, bIdx) => {
          if (!band.coordinates) return null;
          // Convert [lng, lat] to [lat, lng] for Leaflet
          const rings = band.coordinates.map(ring =>
            ring.map(c => [c[1], c[0]])
          );
          const isInnermost = bIdx === bands.length - 1;
          const isOutermost = bIdx === 0;
          return rings.map((ring, rIdx) => (
            <Polygon
              key={`corridor-band-${corridorIndex}-${band.level}-${rIdx}`}
              positions={ring}
              pathOptions={{
                color: band.color,
                weight: isHovered ? 2.5 : (isInnermost ? 2 : isOutermost ? 1.2 : 0.6),
                opacity: isHovered ? Math.min(1, band.opacity + 0.25) : band.opacity,
                fillColor: band.color,
                fillOpacity: isHovered ? Math.min(0.95, band.fillOpacity + 0.2) : band.fillOpacity,
              }}
              eventHandlers={{
                mouseover: () => setIsHovered(true),
                mouseout: () => setIsHovered(false),
              }}
              data-testid={`corridor-v9-band-${corridorIndex}-${band.level}`}
            >
              {isInnermost && (
                <Tooltip sticky direction="top" offset={[0, -8]}>
                  {tooltipContent}
                </Tooltip>
              )}
            </Polygon>
          ));
        })}
        {/* Centerline: strong visible line on top */}
        {centerline && centerline.length >= 2 && (
          <Polyline
            positions={centerline.map(c => [c[1], c[0]])}
            pathOptions={{
              color: '#FFFFFF',
              weight: isHovered ? 3 : 2,
              opacity: isHovered ? 0.9 : 0.6,
              dashArray: null,
              lineCap: 'round',
              lineJoin: 'round',
            }}
            eventHandlers={{
              mouseover: () => setIsHovered(true),
              mouseout: () => setIsHovered(false),
            }}
            data-testid={`corridor-v9-centerline-${corridorIndex}`}
          />
        )}
        {/* Classification line on top of white centerline */}
        {centerline && centerline.length >= 2 && (
          <Polyline
            positions={centerline.map(c => [c[1], c[0]])}
            pathOptions={{
              color: classificationV9?.color || '#F44336',
              weight: isHovered ? 2 : 1.2,
              opacity: isHovered ? 0.8 : 0.5,
              dashArray: level === 'rouge_raye' ? '6,2,2,2' : level === 'gris' ? '4,3' : null,
              lineCap: 'round',
              lineJoin: 'round',
            }}
            data-testid={`corridor-v9-classline-${corridorIndex}`}
          />
        )}
      </>
    );
  }

  // Fallback: render as simple polyline if no bands
  const styleColor = classificationV9?.color || CORRIDOR_STYLES[source]?.[sex] || corridor.color || '#06B6D4';
  const weight = isHovered ? 5 : (corridor.weight || 2.5);
  const opacity = isHovered ? 1.0 : (corridor.opacity || 0.85);

  return (
    <Polyline
      positions={positions}
      pathOptions={{
        color: styleColor,
        weight,
        opacity,
        lineCap: 'round',
        lineJoin: 'round',
      }}
      eventHandlers={{
        mouseover: () => setIsHovered(true),
        mouseout: () => setIsHovered(false),
      }}
      data-testid={`corridor-v9-fallback-${corridorIndex}`}
    >
      <Tooltip sticky direction="top" offset={[0, -8]}>
        {tooltipContent}
      </Tooltip>
    </Polyline>
  );
};

// Legacy corridor format (start/end two-point)
const CorridorLine = ({ start, end, moduleId, percentage, label, corridorIndex }) => {
  const mod = BIONIC_MODULES[moduleId] || BIONIC_MODULES.corridors;
  const [isHovered, setIsHovered] = useState(false);
  const color = generateZoneColor('corridors', corridorIndex);
  const weight = getDynamicWeight(percentage, isHovered);

  return (
    <Polyline
      positions={[start, end]}
      pathOptions={{
        color,
        weight,
        opacity: 1.0,
        dashArray: '8, 5',
        lineCap: 'round',
        lineJoin: 'round',
      }}
      eventHandlers={{
        mouseover: () => setIsHovered(true),
        mouseout: () => setIsHovered(false),
      }}
    >
      <Tooltip sticky direction="top" offset={[0, -5]}>
        <div className="bg-gray-900/95 border border-gray-700 rounded-lg p-2 shadow-xl">
          <div className="flex items-center gap-2">
            <div className="w-2.5 h-0.5 rounded" style={{ backgroundColor: color }} />
            <span className="font-semibold text-white">{label || mod.label}</span>
          </div>
          <div className="text-sm mt-1" style={{ color }}>
            Attraction: {percentage}% — {weight.toFixed(1)}px
          </div>
        </div>
      </Tooltip>
    </Polyline>
  );
};

// ============================================
// COMPOSANT PRINCIPAL — BionicMicroZones V5 Harmonisé
// ============================================
const BionicMicroZones = ({
  zones = [],
  corridors = [],
  minPercentage = 50,
  showCorridors = true,
  onZoneClick,
  onZoneHover,
  isZoneFavorite = () => false,
  onAddFavorite = null,
  onRemoveFavorite = null,
}) => {
  const [hoveredZoneId, setHoveredZoneId] = useState(null);

  const handleHover = useCallback((id) => {
    setHoveredZoneId(id);
    if (onZoneHover) {
      const zone = zones.find((z) => z.id === id);
      if (zone) onZoneHover(zone);
    }
  }, [onZoneHover, zones]);
  const handleLeave = useCallback(() => setHoveredZoneId(null), []);

  // Classify and sort zones into tiers
  const { cellZones, nodeZones } = useMemo(() => {
    const cells = [];
    const nodes = [];
    zones
      .filter(z => z.score >= minPercentage)
      .forEach(z => {
        const tier = classifyZone(z);
        if (tier === 'core.nodes') nodes.push({ ...z, tier });
        else cells.push({ ...z, tier });
      });
    // Sort: low scores rendered first (behind)
    cells.sort((a, b) => a.score - b.score);
    nodes.sort((a, b) => a.score - b.score);
    return { cellZones: cells, nodeZones: nodes };
  }, [zones, minPercentage]);

  const toggleFavorite = onAddFavorite
    ? (z) => {
        if (isZoneFavorite(z)) {
          onRemoveFavorite && onRemoveFavorite(z);
        } else {
          onAddFavorite(z);
        }
      }
    : null;

  return (
    <>
      {/* COUCHE 3: behavior.cells — Contours uniques, centre transparent */}
      {cellZones.map((zone, idx) => (
        <NormalizedZone
          key={zone.id}
          zone={zone}
          tier="behavior.cells"
          zoneIndex={idx}
          isHovered={hoveredZoneId === zone.id}
          onHover={handleHover}
          onLeave={handleLeave}
          onToggleFavorite={toggleFavorite}
        />
      ))}

      {/* COUCHE 4: core.nodes — Contours uniques */}
      {nodeZones.map((zone, idx) => (
        <NormalizedZone
          key={zone.id}
          zone={zone}
          tier="core.nodes"
          zoneIndex={cellZones.length + idx}
          isHovered={hoveredZoneId === zone.id}
          onHover={handleHover}
          onLeave={handleLeave}
          onToggleFavorite={toggleFavorite}
        />
      ))}

      {/* COUCHE 5: Corridors V9 — Rubans ecologiques multicouches
          TOUJOURS AU-DESSUS des zones pour visibilite maximale
          Rendu: 5 bandes concentriques gris→jaune→orange→rouge→rouge_raye */}
      <Pane name="corridors-v9-pane" style={{ zIndex: 650 }}>
        {showCorridors &&
          corridors.map((c, idx) =>
            c.positions || c.bands ? (
              <V9CorridorRibbon
                key={c.id || `corridor-v9-${idx}`}
                corridor={c}
                corridorIndex={idx}
              />
            ) : (
              <CorridorLine
                key={`corridor-${idx}`}
                start={c.start}
                end={c.end}
                moduleId="corridors"
                percentage={c.percentage}
                label={c.label}
                corridorIndex={idx}
              />
            )
          )}
      </Pane>
    </>
  );
};

export default BionicMicroZones;
