/**
 * SidePanelZones.jsx — Panneau latéral onglet "carte" (zones, corridors, cible, diagnostics)
 * Extrait de MonTerritoireBionicPage.jsx (IM1 Refactorisation)
 */
import React, { useState } from 'react';
import { Target, X, Trash2, AlertTriangle, ChevronDown, ChevronUp, Droplets, Building, TreePine, Scissors, CloudRain, Wind, Sun, Thermometer } from 'lucide-react';
import CorridorStatsPanel from '@/components/territoire/CorridorStatsPanel';
import EcologicalPanel from '@/components/territoire/EcologicalPanel';

const REJECTION_LABELS = {
  'p0_v6_water': 'Hydrographie',
  'p0_v6_water_after_trim': 'Hydrographie (post-trim)',
  'p0_v6_urban': 'Zone urbaine',
  'p0_v6_urban_after_trim': 'Zone urbaine (post-trim)',
  'p0_v6_roads': 'Routes',
  'p0_v6_roads_after_trim': 'Routes (post-trim)',
  'p0_v6_infrastructure': 'Infrastructure',
  'p0_v6_infrastructure_after_trim': 'Infrastructure (post-trim)',
  'p0_v7_water_after_trim': 'Hydrographie V7 (post-trim)',
  'p0_v7_urban_after_trim': 'Zone urbaine V7 (post-trim)',
  'p0_v7_roads_after_trim': 'Routes V7 (post-trim)',
  'p0_v7_water': 'Hydrographie V7',
  'p0_v7_urban': 'Zone urbaine V7',
  'p0_v7_roads': 'Routes V7',
  'p0_v7_water_post_trim': 'Hydrographie V7 (résiduelle)',
  'p0_v7_urban_post_trim': 'Urbain V7 (résiduel)',
  'anthropic_urban_roads_v7': 'Pression anthropique V7',
  'anthropic_major_road_v7': 'Route majeure V7',
  'anthropic_infra_roads_v7': 'Infra routière V7',
  'anthropic_urban_close_v7': 'Proximité urbaine V7',
  'anthropic_combined_v7': 'Pression combinée V7',
  'oversized_v7': 'Surface trop grande V7',
  'anthropic_urban_roads': 'Pression anthropique',
  'anthropic_urban_roads_v72': 'Pression anthropique V7',
  'anthropic_major_road': 'Route majeure',
  'anthropic_infra_roads': 'Infrastructure routière',
  'anthropic_urban_close': 'Proximité urbaine',
  'anthropic_combined': 'Pression combinée',
  'oversized': 'Surface trop grande',
  'trimmed_degenerate': 'Fragmentation',
  'fragmentation_penalty': 'Fragmentation',
};

const REJECTION_ICONS = {
  water: Droplets,
  urban: Building,
  roads: TreePine,
  anthropic: Building,
  fragmentation: Scissors,
};

const getReasonIcon = (reason) => {
  if (reason.includes('water')) return Droplets;
  if (reason.includes('urban') || reason.includes('anthropic')) return Building;
  if (reason.includes('road') || reason.includes('infra')) return TreePine;
  return AlertTriangle;
};

const getReasonColor = (reason) => {
  if (reason.includes('water')) return 'text-blue-400';
  if (reason.includes('urban') || reason.includes('anthropic')) return 'text-amber-400';
  if (reason.includes('road') || reason.includes('infra')) return 'text-orange-400';
  return 'text-red-400';
};

const RejectionDiagnosticsPanel = ({ diagnostics }) => {
  const [expanded, setExpanded] = useState(false);
  if (!diagnostics || diagnostics.total_rejected === 0) return null;

  const byReason = diagnostics.by_reason || {};
  const byLayer = diagnostics.by_layer || {};

  return (
    <div className="bg-[#111118] rounded-lg border border-amber-500/20 overflow-hidden" data-testid="rejection-diagnostics-panel">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-3 hover:bg-white/5 transition-colors"
        data-testid="rejection-diagnostics-toggle"
      >
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />
          <span className="text-[10px] text-amber-400 uppercase tracking-wider font-medium">
            Diagnostics
          </span>
          <span className="text-[10px] text-amber-400/60">
            {diagnostics.total_rejected} rejet{diagnostics.total_rejected > 1 ? 's' : ''}
          </span>
        </div>
        {expanded ? (
          <ChevronUp className="h-3 w-3 text-amber-400/60" />
        ) : (
          <ChevronDown className="h-3 w-3 text-amber-400/60" />
        )}
      </button>

      {expanded && (
        <div className="px-3 pb-3 space-y-3">
          {/* By Reason */}
          <div>
            <div className="text-[9px] text-gray-500 uppercase tracking-wider mb-1.5">Par raison</div>
            <div className="space-y-1">
              {Object.entries(byReason)
                .sort((a, b) => b[1] - a[1])
                .map(([reason, count]) => {
                  const Icon = getReasonIcon(reason);
                  const colorClass = getReasonColor(reason);
                  const label = REJECTION_LABELS[reason] || reason.replace(/_/g, ' ');
                  return (
                    <div key={reason} className="flex items-center gap-2 text-[10px]">
                      <Icon className={`h-3 w-3 ${colorClass} flex-shrink-0`} />
                      <span className="text-gray-300 flex-1 truncate">{label}</span>
                      <span className={`font-mono ${colorClass}`}>{count}</span>
                    </div>
                  );
                })}
            </div>
          </div>

          {/* By Layer */}
          <div>
            <div className="text-[9px] text-gray-500 uppercase tracking-wider mb-1.5">Par couche</div>
            <div className="space-y-1">
              {Object.entries(byLayer)
                .sort((a, b) => b[1].count - a[1].count)
                .map(([layer, info]) => (
                  <div key={layer} className="flex items-center gap-2 text-[10px]">
                    <span className="text-gray-400 flex-1 truncate capitalize">{layer}</span>
                    <span className="font-mono text-gray-500">{info.count}</span>
                  </div>
                ))}
            </div>
          </div>

          {/* Legend */}
          <div className="border-t border-gray-800 pt-2">
            <div className="text-[8px] text-gray-600 leading-relaxed">
              Les zones candidates ont été rejetées par le moteur d'exclusion BIONIC V7.
              Causes principales : superposition eau/urbain/routes au-delà du seuil (5%).
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const BADGE_ICONS = {
  favorable: Sun,
  wind_alert: Wind,
  heavy_rain: CloudRain,
};

const INFLUENCE_LABELS = {
  repos: 'Repos',
  alimentation: 'Alimentation',
  corridors: 'Corridors',
  rut: 'Rut',
  habitats: 'Habitats',
};

const WeatherInfluencePanel = ({ weatherMetadata, zones }) => {
  if (!weatherMetadata?.applied) return null;

  const snap = weatherMetadata.snapshot || {};
  const influence = weatherMetadata.influence_multipliers || {};
  const badges = weatherMetadata.badges || [];
  const globalMult = weatherMetadata.global_multiplier || 1.0;

  return (
    <div className="bg-[#111118] rounded-lg border border-[#1a1a2e] overflow-hidden" data-testid="weather-influence-panel">
      <div className="p-3">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-1.5">
            <Thermometer className="h-3.5 w-3.5 text-blue-400" />
            <span className="text-[10px] text-gray-400 uppercase tracking-wider font-medium">Impact Météo</span>
          </div>
          <span className="text-[10px] text-gray-500">
            {snap.temperature_c != null ? `${Math.round(snap.temperature_c)}°C` : '--'}
            {snap.wind_speed_kmh != null ? ` / ${Math.round(snap.wind_speed_kmh)}km/h` : ''}
          </span>
        </div>

        {/* Badges */}
        {badges.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-2" data-testid="weather-badges">
            {badges.map((badge, i) => {
              const Icon = BADGE_ICONS[badge.type] || Sun;
              return (
                <span
                  key={i}
                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-semibold"
                  style={{ backgroundColor: `${badge.color}20`, color: badge.color, border: `1px solid ${badge.color}40` }}
                  data-testid={`weather-badge-${badge.type}`}
                >
                  <Icon className="h-2.5 w-2.5" />
                  {badge.label}
                </span>
              );
            })}
          </div>
        )}

        {/* Global multiplier */}
        <div className="flex items-center gap-2 mb-2">
          <span className="text-[9px] text-gray-500">Global</span>
          <div className="flex-1 h-1.5 bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${Math.min(100, (globalMult / 1.3) * 100)}%`,
                backgroundColor: globalMult > 1.05 ? '#22c55e' : globalMult < 0.95 ? '#ef4444' : '#6b7280',
              }}
            />
          </div>
          <span className={`text-[10px] font-mono font-bold ${globalMult > 1.05 ? 'text-green-400' : globalMult < 0.95 ? 'text-red-400' : 'text-gray-400'}`}>
            x{globalMult.toFixed(2)}
          </span>
        </div>

        {/* Per-category multipliers */}
        <div className="space-y-1">
          {Object.entries(influence).map(([cat, mult]) => (
            <div key={cat} className="flex items-center gap-2">
              <span className="text-[8px] text-gray-500 w-16 truncate">{INFLUENCE_LABELS[cat] || cat}</span>
              <div className="flex-1 h-1 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${Math.min(100, (mult / 1.3) * 100)}%`,
                    backgroundColor: mult > 1.05 ? '#22c55e' : mult < 0.95 ? '#ef4444' : '#4b5563',
                  }}
                />
              </div>
              <span className={`text-[8px] font-mono ${mult > 1.05 ? 'text-green-400' : mult < 0.95 ? 'text-red-400' : 'text-gray-500'}`}>
                {mult > 1.0 ? '+' : ''}{((mult - 1) * 100).toFixed(0)}%
              </span>
            </div>
          ))}
        </div>

        {/* Condition detail */}
        {snap.condition_detail && (
          <div className="mt-2 text-[8px] text-gray-600 italic">{snap.condition_detail}</div>
        )}
        <div className="mt-1 text-[7px] text-gray-700">MAJ auto. 30 min {snap.from_cache ? '(cache)' : '(live)'}</div>
      </div>
    </div>
  );
};

export const SidePanelZones = React.memo(({
  currentZoom,
  isLoadingZones,
  pipelineState,
  zoneSource,
  visibleZonesCount,
  reloadZones,
  activeWaypoints,
  corridors,
  selectedWaypointForZones,
  clearWaypointTarget,
  handleDeleteWaypoint,
  handleGenerateSnapshot,
  rejectionDiagnostics,
  weatherMetadata,
  zones,
  species,
}) => (
  <div className="p-4 space-y-4" data-testid="panel-zones">
    {/* Zoom */}
    <div className="bg-[#111118] rounded-lg p-3 border border-[#1a1a2e]">
      <div className="text-[10px] text-gray-500 uppercase tracking-wider">Zoom</div>
      <div className="text-2xl font-bold text-white">{currentZoom}</div>
    </div>
    {/* Compteur zones */}
    <div className="bg-[#111118] rounded-lg p-3 border border-[#1a1a2e]" data-testid="zones-counter-panel">
      <div className="text-[10px] text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
        Zones
        {pipelineState === 'refreshing' && (
          <span className="text-[8px] text-amber-400 animate-pulse" data-testid="zones-refreshing-badge">Mise à jour...</span>
        )}
      </div>
      {isLoadingZones && visibleZonesCount === 0 ? (
        <div className="flex items-center gap-1 py-1">
          <div className="w-1.5 h-1.5 rounded-full bg-[#3CB371] animate-pulse" />
          <div className="w-1.5 h-1.5 rounded-full bg-[#3CB371] animate-pulse" style={{ animationDelay: '0.3s' }} />
          <div className="w-1.5 h-1.5 rounded-full bg-[#3CB371] animate-pulse" style={{ animationDelay: '0.6s' }} />
        </div>
      ) : (
        <div className="text-2xl font-bold text-[#3CB371]">{visibleZonesCount}</div>
      )}
      <div className="text-[10px] mt-1">
        {isLoadingZones ? (
          <span className="text-gray-400">Calcul en cours...</span>
        ) : zoneSource === 'backend' ? (
          <span className="text-green-400">V7 {weatherMetadata?.applied ? '+ Météo' : ''}</span>
        ) : zoneSource === 'cache' ? (
          <span className="text-cyan-400">Cache V7</span>
        ) : (
          <span className="text-gray-600">En attente</span>
        )}
      </div>
      {!isLoadingZones && visibleZonesCount === 0 && activeWaypoints.length > 0 && (
        <button onClick={reloadZones} className="mt-2 w-full text-[10px] px-2 py-1 rounded-lg bg-[#3CB371]/15 text-[#3CB371] hover:bg-[#3CB371]/25 transition-colors" data-testid="reload-zones-btn">
          Recharger zones
        </button>
      )}
      <div className="text-[8px] text-gray-600 mt-1" data-testid="pipeline-version">Pipeline V7 + Météo V8.2.1</div>
    </div>
    {/* Rejection Diagnostics Panel */}
    {!isLoadingZones && visibleZonesCount === 0 && rejectionDiagnostics && (
      <RejectionDiagnosticsPanel diagnostics={rejectionDiagnostics} />
    )}
    {/* V8.2.1: Weather Influence Panel */}
    <WeatherInfluencePanel weatherMetadata={weatherMetadata} zones={zones} />
    {/* Corridor Stats V7.1 */}
    <CorridorStatsPanel corridors={corridors} />
    {/* Ecologie V8 — Panneau dynamique */}
    <EcologicalPanel corridors={corridors} species={species} />
    {/* Waypoint cible */}
    {selectedWaypointForZones && (
      <div className="bg-[#3CB371]/10 rounded-lg p-3 border border-[#3CB371]/30">
        <div className="text-[10px] text-[#3CB371] uppercase tracking-wider flex items-center gap-1">
          <Target className="h-3 w-3" /> Cible
        </div>
        <div className="text-sm font-medium text-white truncate mt-1">{selectedWaypointForZones.name}</div>
        <div className="text-[10px] text-gray-500 mt-0.5">{selectedWaypointForZones.lat?.toFixed(4)}, {selectedWaypointForZones.lng?.toFixed(4)}</div>
        <div className="text-[10px] text-gray-600 mt-1 italic">Actions via le bouton Waypoint</div>
      </div>
    )}
    {/* Snapshot */}
    {selectedWaypointForZones && (
      <div className="flex gap-2">
        <button onClick={() => handleGenerateSnapshot('json')} className="flex-1 text-[10px] px-2 py-1.5 rounded-lg bg-[#111118] border border-[#1a1a2e] text-gray-400 hover:text-white hover:border-gray-600 transition-colors">Export JSON</button>
        <button onClick={() => handleGenerateSnapshot('pdf')} className="flex-1 text-[10px] px-2 py-1.5 rounded-lg bg-[#111118] border border-[#1a1a2e] text-gray-400 hover:text-white hover:border-gray-600 transition-colors">Export PDF</button>
      </div>
    )}
  </div>
));
