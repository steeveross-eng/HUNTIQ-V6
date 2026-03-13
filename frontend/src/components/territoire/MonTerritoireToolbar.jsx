/**
 * MonTerritoireToolbar — Barre d'outils horizontale compacte BIONIC V5 300%
 * Remplace la sidebar accordéon gauche.
 * Chaque groupe de contrôles est accessible via une icône + Popover.
 * Non-régression : toutes les fonctionnalités de l'ancienne sidebar sont préservées.
 */
import React from 'react';
import {
  Map, Binoculars, Layers, Target, Activity, Lock, Unlock,
  BarChart3, CheckCircle, RefreshCw, SplitSquareHorizontal,
  Baby, Footprints, Thermometer, Clock, Plus, Edit2, Crosshair, X,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/popover';
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import BionicMapSelector from '@/components/maps/BionicMapSelector';

const ToolbarButton = ({ icon: Icon, label, color, badge, children, align = 'start', width = 'w-72' }) => (
  <Popover>
    <PopoverTrigger asChild>
      <button
        className="relative h-8 w-8 flex items-center justify-center rounded-md hover:bg-white/10 transition-colors"
        title={label}
        data-testid={`toolbar-btn-${label.toLowerCase().replace(/\s+/g, '-')}`}
      >
        <Icon className="h-4 w-4" style={{ color }} />
        {badge !== undefined && badge !== null && (
          <span className="absolute -top-0.5 -right-0.5 min-w-[14px] h-[14px] rounded-full bg-[#f5a623] text-black text-[8px] font-bold flex items-center justify-center leading-none px-0.5">
            {badge}
          </span>
        )}
      </button>
    </PopoverTrigger>
    <PopoverContent
      align={align}
      sideOffset={8}
      className={`${width} bg-gray-950/95 backdrop-blur-md border-gray-700/60 p-0 shadow-xl shadow-black/40`}
    >
      <div className="px-3 py-2 border-b border-gray-800 flex items-center gap-2">
        <Icon className="h-3.5 w-3.5" style={{ color }} />
        <span className="text-xs font-semibold text-white">{label}</span>
      </div>
      <div className="p-3 max-h-[70vh] overflow-y-auto">
        {children}
      </div>
    </PopoverContent>
  </Popover>
);

const Sep = () => <div className="w-px h-5 bg-gray-700/50 mx-0.5" />;

const MonTerritoireToolbar = ({
  // Fond de Carte
  mapType, setMapType, mapOptions, setMapOptions,
  // Espèce
  selectedSpecies, setSelectedSpecies, speciesList,
  isLoadingExclusions, bionicStats, onNavigateComparison,
  // Couches BIONIC
  layersVisible, toggleLayer, showAllLayers, hideAllLayers, activeCount, allLayers,
  // Affichage Zones
  visibleZonesCount, bionicZonesCount, showCorridors, setShowCorridors,
  showCorridorsV1, setShowCorridorsV1, temporalHourMT, setTemporalHourMT,
  minPercentageFilter, setMinPercentageFilter,
  // Confidentialité
  privacyMode, setPrivacyMode,
  // Statistiques
  activeWaypointsCount, currentZoom, displayScore,
  // Curseur BIONIC
  showCursorBionic, setShowCursorBionic,
  // Couche d'exclusion overlay
  showExclusionOverlay, setShowExclusionOverlay,
  // Classification toggles
  classificationToggles, onClassificationToggle,
  // Loading state
  isLoadingZones,
  // Waypoint creation
  mapClickMode, setMapClickMode, setShowAddWaypointDialog,
}) => {
  return (
    <div
      className="flex items-center gap-0.5 bg-black/85 backdrop-blur-sm rounded-lg border border-gray-700/50 p-1"
      data-testid="toolbar-horizontal"
    >
      {/* 1. FOND DE CARTE */}
      <ToolbarButton icon={Map} label="Fond de Carte" color="#f5a623" width="w-80">
        <BionicMapSelector
          currentMapType={mapType}
          onMapTypeChange={setMapType}
          mapOptions={mapOptions}
          onOptionsChange={setMapOptions}
          variant="panel"
          showOptions={true}
        />
      </ToolbarButton>

      <Sep />

      {/* 2. ESPÈCE CIBLE */}
      <ToolbarButton icon={Binoculars} label="Espèce cible" color="#f59e0b">
        <div className="space-y-1">
          {speciesList.map(sp => (
            <button
              key={sp.id}
              onClick={() => setSelectedSpecies(sp.id)}
              data-testid={`species-btn-${sp.id}`}
              className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-xs transition-all ${
                selectedSpecies === sp.id
                  ? 'bg-amber-500/20 text-white border border-amber-500/40'
                  : 'bg-gray-900/50 text-gray-400 hover:bg-gray-800/50'
              }`}
            >
              <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: sp.color }} />
              <span className="flex-1 text-left">{sp.name}</span>
              {selectedSpecies === sp.id && <CheckCircle className="h-3 w-3 text-amber-400" />}
            </button>
          ))}
        </div>
        {isLoadingExclusions && (
          <div className="mt-2 flex items-center gap-2 text-[10px] text-gray-500">
            <RefreshCw className="h-3 w-3 animate-spin" />
            Chargement exclusions terrain...
          </div>
        )}
        {bionicStats.rejected > 0 && (
          <div className="mt-2 p-2 rounded-lg bg-red-500/10 border border-red-500/20">
            <p className="text-[10px] text-red-400">
              {bionicStats.rejected} zones rejetées (terrain interdit)
            </p>
          </div>
        )}
        <button
          onClick={onNavigateComparison}
          className="mt-3 w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-[#f5a623]/10 border border-[#f5a623]/30 text-[#f5a623] hover:bg-[#f5a623]/20 transition-colors text-xs font-medium"
          data-testid="comparison-species-btn"
        >
          <SplitSquareHorizontal className="h-3.5 w-3.5" />
          Comparaison Espèces
        </button>
      </ToolbarButton>

      {/* 3. COUCHES BIONIC */}
      <ToolbarButton icon={Layers} label="Couches BIONIC" color="#10b981" badge={activeCount}>
        <div className="flex gap-1 mb-3">
          <Button size="sm" variant="outline" onClick={showAllLayers} className="flex-1 text-xs h-7 border-gray-700 hover:bg-emerald-600/20 hover:text-emerald-400">
            Tout
          </Button>
          <Button size="sm" variant="outline" onClick={hideAllLayers} className="flex-1 text-xs h-7 border-gray-700 hover:bg-red-600/20 hover:text-red-400">
            Aucun
          </Button>
        </div>
        <div className="space-y-1 max-h-48 overflow-y-auto">
          {allLayers.map(layer => (
            <button
              key={layer.id}
              onClick={() => toggleLayer(layer.id)}
              className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-xs transition-all ${
                layersVisible[layer.id]
                  ? 'bg-[#f5a623]/10 text-white border border-[#f5a623]/30'
                  : 'bg-gray-900/50 text-gray-400 hover:bg-gray-800/50'
              }`}
              data-testid={`layer-toggle-${layer.id}`}
            >
              <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: layersVisible[layer.id] ? layer.color : '#4b5563' }} />
              <span className="flex-1 text-left truncate">{layer.name}</span>
              {layersVisible[layer.id] && <CheckCircle className="h-3 w-3 text-[#f5a623]" />}
            </button>
          ))}
        </div>
        {/* Toggle Exclusion Overlay */}
        <div className="mt-3 pt-3 border-t border-gray-700/50">
          <button
            onClick={() => setShowExclusionOverlay(!showExclusionOverlay)}
            className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-xs transition-all ${
              showExclusionOverlay
                ? 'bg-red-500/10 text-white border border-red-500/30'
                : 'bg-gray-900/50 text-gray-400 hover:bg-gray-800/50'
            }`}
            data-testid="layer-toggle-exclusion-overlay"
          >
            <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: showExclusionOverlay ? '#F44336' : '#4b5563' }} />
            <span className="flex-1 text-left">Zones d'exclusion (overlay)</span>
            {showExclusionOverlay && <CheckCircle className="h-3 w-3 text-red-400" />}
          </button>
        </div>
      </ToolbarButton>

      {/* 4. CLASSIFICATION V5 — TOGGLES FONCTIONNELS */}
      <ToolbarButton icon={Layers} label="Classification" color="#14b8a6" width="w-80">
        <div className="space-y-3">
          {/* STRUCTURE (statique) */}
          <div className="space-y-1">
            <div className="flex items-center gap-1.5 mb-1">
              <div className="w-2 h-2 rounded-sm bg-gray-400" />
              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Structure</span>
              <span className="text-[9px] text-gray-600 ml-auto">statique</span>
            </div>
            {[
              { key: 'relief', label: 'Relief / Altitude', color: '#FF7043' },
              { key: 'hydro', label: 'Hydrographie', color: '#3B82F6' },
              { key: 'foret', label: 'Type de foret', color: '#66BB6A' },
              { key: 'anthropique', label: 'Zones anthropiques', color: '#EF5350' },
            ].map(item => (
              <div key={item.key} className="flex items-center justify-between gap-2 px-2 py-1 rounded text-[10px] bg-gray-900/30" data-testid={`classification-toggle-${item.key}`}>
                <div className="flex items-center gap-2 min-w-0">
                  <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }} />
                  <span className={classificationToggles?.[item.key] ? 'text-gray-300' : 'text-gray-600 line-through'}>{item.label}</span>
                </div>
                <Switch
                  checked={classificationToggles?.[item.key] ?? true}
                  onCheckedChange={() => onClassificationToggle(item.key)}
                  className="scale-[0.6] data-[state=checked]:bg-slate-400 flex-shrink-0"
                />
              </div>
            ))}
          </div>

          {/* FONCTIONNEL (semi-statique) */}
          <div className="space-y-1">
            <div className="flex items-center gap-1.5 mb-1">
              <div className="w-2 h-2 rounded-sm bg-green-500" />
              <span className="text-[10px] font-bold text-green-400 uppercase tracking-wider">Fonctionnel</span>
              <span className="text-[9px] text-gray-600 ml-auto">semi-statique</span>
            </div>
            {[
              { key: 'dominantes', label: 'Zones dominantes (alimentation, repos, rut)', color: '#f5a623' },
              { key: 'corridorsReels', label: 'Corridors réels', color: '#4CAF50', desc: '--- lignes continues' },
            ].map(item => (
              <div key={item.key} className="flex items-center justify-between gap-2 px-2 py-1 rounded text-[10px] bg-green-900/10 border border-green-900/20" data-testid={`classification-toggle-${item.key}`}>
                <div className="flex items-center gap-2 min-w-0">
                  <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }} />
                  <div>
                    <div className={classificationToggles?.[item.key] ? 'text-green-200/70' : 'text-gray-600 line-through'}>{item.label}</div>
                    {item.desc && <div className="text-[9px] text-gray-500">{item.desc}</div>}
                  </div>
                </div>
                <Switch
                  checked={classificationToggles?.[item.key] ?? true}
                  onCheckedChange={() => onClassificationToggle(item.key)}
                  className="scale-[0.6] data-[state=checked]:bg-green-500"
                />
              </div>
            ))}
          </div>

          {/* CONDITIONS (dynamique) */}
          <div className="space-y-1">
            <div className="flex items-center gap-1.5 mb-1">
              <div className="w-2 h-2 rounded-sm bg-orange-500" />
              <span className="text-[10px] font-bold text-orange-400 uppercase tracking-wider">Conditions</span>
              <span className="text-[9px] text-gray-600 ml-auto">dynamique</span>
            </div>
            {[
              { key: 'meteo', label: 'Vent, Météo, Thermique', color: '#00BCD4' },
              { key: 'pression', label: 'Pression humaine', color: '#E91E63' },
              { key: 'corridorsEstimes', label: 'Corridors estimés', color: '#FF9800', desc: '--- lignes pointillées' },
            ].map(item => (
              <div key={item.key} className="flex items-center justify-between gap-2 px-2 py-1 rounded text-[10px] bg-orange-900/10 border border-orange-900/20" data-testid={`classification-toggle-${item.key}`}>
                <div className="flex items-center gap-2 min-w-0">
                  <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }} />
                  <div>
                    <div className={classificationToggles?.[item.key] ? 'text-orange-200/70' : 'text-gray-600 line-through'}>{item.label}</div>
                    {item.desc && <div className="text-[9px] text-gray-500">{item.desc}</div>}
                  </div>
                </div>
                <Switch
                  checked={classificationToggles?.[item.key] ?? true}
                  onCheckedChange={() => onClassificationToggle(item.key)}
                  className="scale-[0.6] data-[state=checked]:bg-orange-500"
                />
              </div>
            ))}
          </div>

          {/* INSTANTANÉ (temps réel) */}
          <div className="space-y-1">
            <div className="flex items-center gap-1.5 mb-1">
              <div className="w-2 h-2 rounded-sm bg-blue-500" />
              <span className="text-[10px] font-bold text-blue-400 uppercase tracking-wider">Instantané</span>
              <span className="text-[9px] text-gray-600 ml-auto">temps réel</span>
            </div>
            {[
              { key: 'scoreHabitat', label: 'Score habitat (0-100%)', color: '#3b82f6' },
              { key: 'curseurBionic', label: 'Curseur BIONIC', color: '#8B5CF6' },
              { key: 'waypoints', label: 'Waypoints / Observations', color: '#f5a623' },
            ].map(item => (
              <div key={item.key} className="flex items-center justify-between gap-2 px-2 py-1 rounded text-[10px] bg-blue-900/10 border border-blue-900/20" data-testid={`classification-toggle-${item.key}`}>
                <div className="flex items-center gap-2 min-w-0">
                  <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }} />
                  <span className={classificationToggles?.[item.key] ? 'text-blue-200/70' : 'text-gray-600 line-through'}>{item.label}</span>
                </div>
                <Switch
                  checked={classificationToggles?.[item.key] ?? true}
                  onCheckedChange={() => onClassificationToggle(item.key)}
                  className="scale-[0.6] data-[state=checked]:bg-blue-500"
                />
              </div>
            ))}
          </div>

          <div className="p-2 rounded-lg border border-teal-500/20 bg-teal-900/10">
            <p className="text-[9px] text-gray-400">
              <span className="font-medium text-teal-400">NORME V5 300%</span> — Les toggles agissent sur le rendu uniquement. Les zones structurelles restent figées en mémoire. Aucun recalcul déclenché.
            </p>
          </div>
        </div>
      </ToolbarButton>

      <Sep />

      {/* 5. AFFICHAGE ZONES */}
      <ToolbarButton icon={Target} label="Affichage Zones" color="#06b6d4" badge={isLoadingZones ? '...' : visibleZonesCount}>
        <div className="space-y-3 bg-gray-900/50 rounded-lg p-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-300">Zones organiques</span>
            <span className="text-xs font-semibold text-cyan-400">{bionicZonesCount}</span>
          </div>
          {bionicStats.avgArea > 0 && (
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-300">Superficie moy.</span>
              <span className="text-xs font-semibold text-emerald-400">~{bionicStats.avgArea?.toLocaleString('fr-FR')} m2</span>
            </div>
          )}
          {bionicStats.rejected > 0 && (
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-300">Rejetées (terrain)</span>
              <span className="text-xs font-semibold text-red-400">{bionicStats.rejected}</span>
            </div>
          )}
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-300">Corridors</span>
            <Switch
              checked={showCorridors}
              onCheckedChange={setShowCorridors}
              className="scale-75 data-[state=checked]:bg-cyan-500"
            />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-300">Déplacements V1</span>
            <Switch
              checked={showCorridorsV1}
              onCheckedChange={setShowCorridorsV1}
              className="scale-75 data-[state=checked]:bg-teal-500"
              data-testid="toggle-corridors-v1"
            />
          </div>
          {showCorridorsV1 && (
            <div className="space-y-1 bg-gray-900/30 rounded-lg p-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-orange-400 font-medium">Scène temporelle</span>
                <span className="text-[10px] text-gray-500">{temporalHourMT !== null ? `${temporalHourMT}h` : 'Auto'}</span>
              </div>
              <input
                type="range"
                min="-1"
                max="23"
                value={temporalHourMT !== null ? temporalHourMT : -1}
                onChange={(e) => {
                  const v = parseInt(e.target.value);
                  setTemporalHourMT(v === -1 ? null : v);
                }}
                className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-orange-400"
                data-testid="temporal-hour-mt"
              />
              <div className="flex justify-between text-[8px] text-gray-600">
                <span>Auto</span><span>6h</span><span>12h</span><span>18h</span><span>23h</span>
              </div>
            </div>
          )}
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-300">Seuil minimum</span>
              <span className="text-xs font-semibold text-[#f5a623]">{minPercentageFilter}%</span>
            </div>
            <input
              type="range"
              min="10"
              max="80"
              step="5"
              value={minPercentageFilter}
              onChange={(e) => setMinPercentageFilter(parseInt(e.target.value))}
              className="w-full h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-[#f5a623]"
              data-testid="min-percentage-slider"
            />
          </div>
          {/* Curseur BIONIC toggle */}
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-300">Curseur BIONIC</span>
            <Switch
              checked={showCursorBionic}
              onCheckedChange={setShowCursorBionic}
              className="scale-75 data-[state=checked]:bg-violet-500"
            />
          </div>
        </div>
      </ToolbarButton>

      {/* 6. FACTEURS SAISONNIERS */}
      <ToolbarButton icon={Activity} label="Facteurs Saisonniers" color="#ec4899">
        <div className="space-y-2">
          <div className="flex items-center gap-2 p-2 rounded-lg bg-gray-900/50" data-testid="seasonal-c1-calving">
            <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#EC489920' }}>
              <Baby className="h-3.5 w-3.5 text-pink-400" />
            </div>
            <div className="flex-1 min-w-0">
              <span className="text-[10px] font-mono text-gray-500">C.1</span>
              <span className="text-xs text-gray-300 ml-1.5">Mise bas</span>
              <p className="text-[9px] text-gray-500">Zones de velage et comportement maternel</p>
            </div>
            <div className="w-2 h-2 rounded-full bg-gray-600" title="Intégré au modèle" />
          </div>
          <div className="flex items-center gap-2 p-2 rounded-lg bg-gray-900/50" data-testid="seasonal-c2-dispersal">
            <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#8B5CF620' }}>
              <Footprints className="h-3.5 w-3.5 text-violet-400" />
            </div>
            <div className="flex-1 min-w-0">
              <span className="text-[10px] font-mono text-gray-500">C.2</span>
              <span className="text-xs text-gray-300 ml-1.5">Dispersion juvénile</span>
              <p className="text-[9px] text-gray-500">Mouvements erratiques des jeunes</p>
            </div>
            <div className="w-2 h-2 rounded-full bg-gray-600" title="Intégré au modèle" />
          </div>
          <div className="flex items-center gap-2 p-2 rounded-lg bg-gray-900/50" data-testid="seasonal-c3-thermal">
            <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#EF444420' }}>
              <Thermometer className="h-3.5 w-3.5 text-red-400" />
            </div>
            <div className="flex-1 min-w-0">
              <span className="text-[10px] font-mono text-gray-500">C.3</span>
              <span className="text-xs text-gray-300 ml-1.5">Stress thermique</span>
              <p className="text-[9px] text-gray-500">Impact température sur le comportement</p>
            </div>
            <div className="w-2 h-2 rounded-full bg-gray-600" title="Intégré au modèle" />
          </div>
          <div className="flex items-center gap-2 p-2 rounded-lg bg-gray-900/50" data-testid="seasonal-c4-pressure">
            <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#F59E0B20' }}>
              <Target className="h-3.5 w-3.5 text-amber-400" />
            </div>
            <div className="flex-1 min-w-0">
              <span className="text-[10px] font-mono text-gray-500">C.4</span>
              <span className="text-xs text-gray-300 ml-1.5">Pression de chasse</span>
              <p className="text-[9px] text-gray-500">Données terrain réelles intégrées</p>
            </div>
            <div className="w-2 h-2 rounded-full bg-gray-600" title="Intégré au modèle" />
          </div>
          <div className="mt-2 p-2 rounded-lg border border-pink-500/20" style={{ backgroundColor: '#EC489910' }}>
            <p className="text-[9px] text-gray-400">
              <span className="font-medium text-pink-400">PHASE C</span> — Les 4 facteurs saisonniers influencent automatiquement le Score BIONIC via le Knowledge Layer.
            </p>
          </div>
        </div>
      </ToolbarButton>

      <Sep />

      {/* 7. CONFIDENTIALITÉ */}
      <ToolbarButton
        icon={privacyMode ? Lock : Unlock}
        label="Confidentialité"
        color={privacyMode ? '#ef4444' : '#22c55e'}
        width="w-56"
      >
        <div className="bg-gray-900/50 rounded-lg p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-300">Mode privé</span>
            <Switch
              checked={privacyMode}
              onCheckedChange={setPrivacyMode}
              className="scale-90 data-[state=checked]:bg-red-500"
            />
          </div>
          <p className="text-[10px] text-gray-500">
            {privacyMode ? 'Données personnelles masquées sur la carte' : 'Waypoints et lieux visibles sur la carte'}
          </p>
        </div>
      </ToolbarButton>

      {/* 8. STATISTIQUES */}
      <ToolbarButton icon={BarChart3} label="Statistiques" color="#a855f7" width="w-56">
        <div className="grid grid-cols-2 gap-2">
          <div className="bg-gray-900/50 rounded-lg p-2 text-center">
            <div className="text-lg font-bold text-[#f5a623]">{visibleZonesCount}</div>
            <div className="text-[10px] text-gray-400">Zones visibles</div>
          </div>
          <div className="bg-gray-900/50 rounded-lg p-2 text-center">
            <div className="text-lg font-bold text-white">{activeWaypointsCount}</div>
            <div className="text-[10px] text-gray-400">Waypoints actifs</div>
          </div>
          <div className="bg-gray-900/50 rounded-lg p-2 text-center">
            <div className="text-3xl font-bold text-emerald-400">{displayScore ?? '—'}</div>
            <div className="text-[10px] text-gray-400">Score Global</div>
          </div>
          <div className="bg-gray-900/50 rounded-lg p-2 text-center">
            <div className="text-lg font-bold text-cyan-400">{currentZoom}</div>
            <div className="text-[10px] text-gray-400">Niveau Zoom</div>
          </div>
        </div>
      </ToolbarButton>
    </div>
  );
};

export default MonTerritoireToolbar;
