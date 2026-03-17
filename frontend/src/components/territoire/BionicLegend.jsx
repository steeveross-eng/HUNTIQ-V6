/**
 * BionicLegend.jsx — Legende Mon Territoire VERSION 3X
 * Norme Steeve-MAX + BCE-4X
 *
 * 3 blocs normatifs:
 *   A. Zones ecologiques (V1)
 *   B. Corridors normatifs (CORRIDOR-V1/V10)
 *   C. Facteurs environnementaux (V9/V10)
 *
 * Hierarchie: Zones > Corridors > Facteurs
 * Chaque item cliquable (toggle) + tooltip
 * Compteurs dynamiques par niveau et espece
 * Prepare pour HABITAT-V1, RUT-V1, AFFUTS-V1, TRAJETS-V1
 */
import { useState, useCallback, useMemo } from 'react';
import {
  ChevronRight, ChevronDown,
  Trees, Navigation, Layers,
  Eye, EyeOff,
} from 'lucide-react';

/* ═══ A. ZONES ECOLOGIQUES ═══ */
const ZONE_ITEMS = [
  { id: 'habitat',      label: 'Habitat optimal',     color: '#2E7D32', tooltip: 'Zone de couvert et refuge principal' },
  { id: 'rut',          label: 'Zone de rut',          color: '#FF5722', tooltip: 'Zone de reproduction saisonniere' },
  { id: 'repos',        label: 'Zone de repos',        color: '#1976D2', tooltip: 'Zone de repos thermique et securitaire' },
  { id: 'alimentation', label: 'Alimentation',         color: '#F9A825', tooltip: 'Zone de nourriture (ALIMENTATION-V1)' },
  { id: 'humides',      label: 'Zones humides',        color: '#00ACC1', tooltip: 'Milieux humides, marecages, tourbières' },
  { id: 'foret',        label: 'Forets matures',       color: '#1B5E20', tooltip: 'Forets matures, mosaiques, regeneration' },
];

/* ═══ B. CORRIDORS NORMATIFS ═══ */
const CORRIDOR_ITEMS = [
  { id: 'CRITIQUE', label: 'Critique',  color: '#CC0000', largeur: 4,  dash: true,  weight: 6, tooltip: 'Axe critique / ultra-frequent (4m)' },
  { id: 'MAJEUR',   label: 'Majeur',    color: '#FF0000', largeur: 6,  dash: false, weight: 5, tooltip: 'Corridor majeur / prioritaire (6m)' },
  { id: 'FORT',     label: 'Fort',      color: '#FF8C00', largeur: 11, dash: false, weight: 4, tooltip: 'Corridor fort / frequent (11m)' },
  { id: 'MODERE',   label: 'Modere',    color: '#FFD700', largeur: 17, dash: false, weight: 3, tooltip: 'Corridor modere / secondaire (17m)' },
  { id: 'FAIBLE',   label: 'Faible',    color: '#BFBFBF', largeur: 26, dash: false, weight: 2, tooltip: 'Corridor faible / opportuniste (26m)' },
];

/* ═══ C. FACTEURS ENVIRONNEMENTAUX ═══ */
const FACTOR_ITEMS = [
  { id: 'ndvi',          label: 'NDVI',               color: '#66BB6A', tooltip: 'Indice de vegetation normalise' },
  { id: 'pentes',        label: 'Pentes',             color: '#8D6E63', tooltip: 'Relief et micro-pente du terrain' },
  { id: 'orientation',   label: 'Orientation',        color: '#AB47BC', tooltip: 'Exposition solaire des versants' },
  { id: 'ensoleillement',label: 'Ensoleillement',     color: '#FFA726', tooltip: 'Heures de soleil direct' },
  { id: 'altitude',      label: 'Altitude relative',  color: '#78909C', tooltip: 'Elevation par rapport au terrain environnant' },
  { id: 'pression',      label: 'Pression humaine',   color: '#EF5350', tooltip: 'Routes, sentiers, batiments, perturbations' },
  { id: 'hydrologie',    label: 'Hydrologie',         color: '#29B6F6', tooltip: 'Cours d\'eau, bassins versants, suintements' },
];

const SPECIES_LABELS = {
  tous: 'Toutes especes',
  orignal: 'Orignal',
  chevreuil: 'Cerf de Virginie',
  ours_noir: 'Ours noir',
  dindon_sauvage: 'Dindon sauvage',
  wapiti: 'Wapiti',
};

/* ═══ COMPOSANT PRINCIPAL ═══ */
export default function BionicLegend({
  pipelineState,
  zoneCount = 0,
  corridorCount = 0,
  windDeg = 225,
  corridorData = null,
  selectedSpecies = 'tous',
  showCorridors = true,
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [expandedBlocks, setExpandedBlocks] = useState({ zones: true, corridors: true, factors: false });
  const [hiddenItems, setHiddenItems] = useState({});

  const toggleBlock = useCallback((block) => {
    setExpandedBlocks(p => ({ ...p, [block]: !p[block] }));
  }, []);

  const toggleItem = useCallback((id) => {
    setHiddenItems(p => ({ ...p, [id]: !p[id] }));
  }, []);

  const dist = useMemo(() => {
    if (!corridorData?.niveauDistribution) return {};
    return corridorData.niveauDistribution;
  }, [corridorData]);

  const totalCorr = corridorData?.totalCorridors || corridorCount;
  const speciesLabel = SPECIES_LABELS[selectedSpecies] || 'Toutes especes';

  return (
    <div
      data-testid="bionic-legend"
      className="absolute bottom-14 left-2 z-[1000] select-none"
      style={{ pointerEvents: 'auto' }}
      onMouseDown={(e) => e.stopPropagation()}
      onClick={(e) => e.stopPropagation()}
      onDoubleClick={(e) => e.stopPropagation()}
    >
      {/* ═══ COLLAPSED ═══ */}
      {!isOpen && (
        <button
          data-testid="bionic-legend-toggle"
          onClick={() => setIsOpen(true)}
          className="flex items-center gap-1.5 px-3 py-2 bg-[#0c0c14]/95 border border-gray-700/50 rounded-lg shadow-xl hover:border-gray-600/70 transition-all backdrop-blur-sm"
        >
          <Layers className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-[10px] font-bold text-gray-200 tracking-wide">LEGENDE</span>
          <span className="text-[9px] text-gray-500 ml-0.5">{zoneCount}z {totalCorr}c</span>
          <ChevronRight className="w-3 h-3 text-gray-500" />
        </button>
      )}

      {/* ═══ EXPANDED: 3 BLOCS NORMATIFS ═══ */}
      {isOpen && (
        <div
          data-testid="bionic-legend-expanded"
          className="bg-[#0c0c14]/95 border border-gray-700/50 rounded-lg shadow-2xl backdrop-blur-sm"
          style={{ width: 248, maxHeight: 440, overflowY: 'auto' }}
        >
          {/* Header */}
          <button
            data-testid="bionic-legend-toggle"
            onClick={() => setIsOpen(false)}
            className="w-full flex items-center justify-between px-3 py-2 hover:bg-white/5 transition-colors rounded-t-lg border-b border-gray-800/60"
          >
            <div className="flex items-center gap-2">
              <Layers className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-[10px] font-bold tracking-wider text-gray-100">LEGENDE BIONIC</span>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-gray-500" />
          </button>

          {/* Species tag */}
          <div className="px-3 py-1.5 border-b border-gray-800/40">
            <span className="text-[9px] font-semibold text-cyan-400/80 tracking-wide uppercase" data-testid="legend-species-label">{speciesLabel}</span>
          </div>

          {/* ═══ BLOC A: ZONES ECOLOGIQUES ═══ */}
          <LegendBlock
            id="zones"
            title="Zones ecologiques"
            icon={<Trees className="w-3 h-3" />}
            color="text-emerald-400"
            expanded={expandedBlocks.zones}
            onToggle={() => toggleBlock('zones')}
            badge={zoneCount}
          >
            {ZONE_ITEMS.map(item => (
              <LegendItem
                key={item.id}
                item={item}
                hidden={hiddenItems[item.id]}
                onToggle={() => toggleItem(item.id)}
                renderSwatch={() => (
                  <div className="w-3.5 h-2.5 rounded-[2px] flex-shrink-0 border" style={{ borderColor: item.color, backgroundColor: `${item.color}30` }} />
                )}
              />
            ))}
          </LegendBlock>

          {/* ═══ BLOC B: CORRIDORS NORMATIFS ═══ */}
          <LegendBlock
            id="corridors"
            title="Corridors V10"
            icon={<Navigation className="w-3 h-3" />}
            color="text-red-400"
            expanded={expandedBlocks.corridors}
            onToggle={() => toggleBlock('corridors')}
            badge={totalCorr}
            active={showCorridors}
          >
            {CORRIDOR_ITEMS.map(item => {
              const count = dist[item.id]?.count || 0;
              return (
                <LegendItem
                  key={item.id}
                  item={item}
                  hidden={hiddenItems[item.id]}
                  onToggle={() => toggleItem(item.id)}
                  count={showCorridors ? count : null}
                  renderSwatch={() => (
                    <svg width="18" height="6" className="flex-shrink-0">
                      <line x1="0" y1="3" x2="18" y2="3"
                        stroke={item.color}
                        strokeWidth={Math.min(item.weight, 5)}
                        strokeDasharray={item.dash ? '4,2' : 'none'}
                        strokeLinecap="round"
                      />
                    </svg>
                  )}
                />
              );
            })}
          </LegendBlock>

          {/* ═══ BLOC C: FACTEURS ENVIRONNEMENTAUX ═══ */}
          <LegendBlock
            id="factors"
            title="Facteurs"
            icon={<Layers className="w-3 h-3" />}
            color="text-gray-400"
            expanded={expandedBlocks.factors}
            onToggle={() => toggleBlock('factors')}
          >
            {FACTOR_ITEMS.map(item => (
              <LegendItem
                key={item.id}
                item={item}
                hidden={hiddenItems[item.id]}
                onToggle={() => toggleItem(item.id)}
                renderSwatch={() => (
                  <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }} />
                )}
              />
            ))}
          </LegendBlock>

          {/* Footer: norme */}
          <div className="px-3 py-1.5 border-t border-gray-800/40 flex items-center justify-between">
            <span className="text-[8px] text-gray-600 tracking-wide">BCE-4X + Steeve-MAX</span>
            <span className="text-[8px] text-gray-600">V10</span>
          </div>
        </div>
      )}
    </div>
  );
}

/* ═══ SOUS-COMPOSANTS ═══ */

function LegendBlock({ id, title, icon, color, expanded, onToggle, children, badge = null, active = true }) {
  return (
    <div className="border-b border-gray-800/40 last:border-b-0" data-testid={`legend-block-${id}`}>
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-2 px-3 py-1.5 hover:bg-white/5 transition-colors"
        data-testid={`legend-block-toggle-${id}`}
      >
        <span className={color}>{icon}</span>
        <span className="text-[9px] font-bold uppercase tracking-wider text-gray-300 flex-1 text-left">{title}</span>
        {badge != null && (
          <span className={`text-[9px] font-mono px-1 rounded ${active ? 'text-gray-400 bg-gray-800/50' : 'text-gray-600 bg-gray-900/50'}`}>
            {badge}
          </span>
        )}
        <ChevronDown className={`w-3 h-3 text-gray-600 transition-transform ${expanded ? '' : '-rotate-90'}`} />
      </button>
      {expanded && (
        <div className="px-3 pb-2 space-y-0.5">
          {children}
        </div>
      )}
    </div>
  );
}

function LegendItem({ item, hidden, onToggle, renderSwatch, count = null }) {
  return (
    <button
      onClick={onToggle}
      className={`w-full flex items-center gap-2 py-[3px] px-1 rounded hover:bg-white/5 transition-all group ${hidden ? 'opacity-40' : ''}`}
      title={item.tooltip}
      data-testid={`legend-item-${item.id}`}
    >
      {renderSwatch()}
      <span className="text-[10px] text-gray-300 flex-1 text-left leading-tight">{item.label}</span>
      {count != null && (
        <span className="text-[9px] font-mono text-gray-500 tabular-nums">{count}</span>
      )}
      {hidden ? (
        <EyeOff className="w-3 h-3 text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity" />
      ) : (
        <Eye className="w-3 h-3 text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity" />
      )}
    </button>
  );
}
