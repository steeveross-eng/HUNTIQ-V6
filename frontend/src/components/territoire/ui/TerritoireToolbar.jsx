/**
 * TerritoireToolbar — Barre d'outils unifiée MON TERRITOIRE
 * ==========================================================
 * Extraite de MonTerritoireBionicPage (STEEVE-MAX refactoring P0).
 * SAISON → SPLIT → CARTE → ESPECE → OBSERVATION → INTELLIGENCE → ZONES → ALIMENTATION → etc.
 */
import React from 'react';
import {
  Crosshair, Target, MapPin, Plus, X, LocateFixed,
  BookMarked, Users, Shield, SplitSquareHorizontal,
  Map, Binoculars, Layers, Lock, Unlock, Brain, CheckCircle, Flame, Droplets,
} from 'lucide-react';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from '@/components/ui/dropdown-menu';
import { Popover, PopoverTrigger, PopoverContent } from '@/components/ui/popover';
import { Switch } from '@/components/ui/switch';
import BionicMapSelector from '@/components/maps/BionicMapSelector';
import { BiologicalSeasonSelector } from '@/components/territoire/ui/BiologicalSeasonSelector';
import { BionicScoreBadge } from '@/components/territoire/BionicScoreBadge';
import { SPECIES_LIST } from '@/core/bionic/speciesConfig';

export function TerritoireToolbar({
  // State
  activeTab, setActiveTab, splitViewEnabled, toggleSplitView,
  selectedBiologicalSeason, setSelectedBiologicalSeason,
  selectedSpecies, setSelectedSpecies,
  // Map type
  mapType, mapOptions, setMapOptions, cartePopoverOpen, setCartePopoverOpen, handleMapTypeChangeAndClose,
  // Layers
  showZonesLayer, setShowZonesLayer, showCorridorsLayer, setShowCorridorsLayer,
  showPointsLayer, setShowPointsLayer, zoneSubFilters, toggleZoneSub,
  corridorSubFilters, toggleCorridorSub, pointSubFilters, togglePointSub,
  showWindFlow, setShowWindFlow, windMode, setWindMode,
  showExclusionOverlay, setShowExclusionOverlay,
  showHeatmapV10, setShowHeatmapV10, heatmapV10Data,
  heatmapIncludeCorridors, setHeatmapIncludeCorridors,
  // Alimentation
  showAlimentationV2, setShowAlimentationV2, showSalines, setShowSalines,
  nSalinesMax, setNSalinesMax, showNutritionPanel, setShowNutritionPanel,
  alimentationV2Data,
  // Points chauds
  pointsChaudsMode, setPointsChaudsMode, pointsChaudsFilter, setPointsChaudsFilter,
  // Seuil
  minPercentageFilter, setMinPercentageFilter,
  // Curseur
  showCursorBionic, setShowCursorBionic,
  // Admin
  adminArchitecteMode, setAdminArchitecteMode, privacyMode, setPrivacyMode,
  // Counters
  activeWaypoints, savedPlaces,
  // Score badge
  selectedWaypointForZones,
}) {
  return (
    <nav className="flex-shrink-0 h-[44px] bg-[#0d0d14] border-b border-[#1a1a2e] px-4 flex items-center relative z-40" data-testid="bionic-tabs">
      <div className="flex items-center gap-0.5 bg-black/60 backdrop-blur-sm rounded-lg border border-gray-700/40 p-1">
        {/* 1. SAISON */}
        {!splitViewEnabled && (
          <>
            <BiologicalSeasonSelector selectedSeason={selectedBiologicalSeason} onSeasonChange={setSelectedBiologicalSeason} />
            <div className="w-px h-5 bg-gray-700/50 mx-0.5" />
          </>
        )}

        {/* 2. SPLIT */}
        <button onClick={toggleSplitView} className={`h-8 px-2.5 flex items-center gap-1.5 rounded-md text-[11px] font-bold uppercase tracking-wider transition-all duration-150 flex-shrink-0 ${splitViewEnabled ? 'bg-[#3CB371]/15 text-[#3CB371]' : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'}`} data-testid="split-view-toggle" title="Comparer deux saisons">
          <SplitSquareHorizontal className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">Split</span>
        </button>
        <div className="w-px h-5 bg-gray-700/50 mx-0.5" />

        {/* 3. CARTE */}
        <Popover open={cartePopoverOpen} onOpenChange={setCartePopoverOpen}>
          <PopoverTrigger asChild>
            <button className="h-8 px-2.5 flex items-center gap-1.5 rounded-md text-[11px] font-bold uppercase tracking-wider text-[#f5a623] hover:bg-white/5 transition-all" data-testid="toolbar-carte-btn" title="Fond de Carte">
              <Map className="h-3.5 w-3.5" /><span className="hidden sm:inline">Carte</span>
            </button>
          </PopoverTrigger>
          <PopoverContent align="start" sideOffset={8} className="w-80 bg-gray-950/95 backdrop-blur-md border-gray-700/60 p-3 shadow-xl shadow-black/40">
            <BionicMapSelector currentMapType={mapType} onMapTypeChange={handleMapTypeChangeAndClose} mapOptions={mapOptions} onOptionsChange={setMapOptions} variant="panel" showOptions={true} />
          </PopoverContent>
        </Popover>
        <div className="w-px h-5 bg-gray-700/50 mx-0.5" />

        {/* 3b. ESPECE */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="h-8 px-2.5 flex items-center gap-1.5 rounded-md text-[11px] font-bold uppercase tracking-wider text-amber-400 hover:bg-white/5 transition-all" data-testid="toolbar-species-btn" title="Espece cible">
              <Target className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">{SPECIES_LIST.find(s => s.id === selectedSpecies)?.name || 'Espece'}</span>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="bg-gray-950 border-gray-700/60 shadow-xl" side="bottom" align="start">
            {SPECIES_LIST.map(sp => (
              <DropdownMenuItem key={sp.id} onClick={() => setSelectedSpecies(sp.id)} className={`cursor-pointer ${selectedSpecies === sp.id ? 'text-amber-400 bg-amber-500/10' : 'text-white hover:bg-white/10'}`} data-testid={`species-quick-${sp.id}`}>
                <div className="w-2.5 h-2.5 rounded-full mr-2 flex-shrink-0" style={{ backgroundColor: sp.color }} />
                {sp.name}
                {selectedSpecies === sp.id && <CheckCircle className="h-3 w-3 ml-auto text-amber-400" />}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
        <div className="w-px h-5 bg-gray-700/50 mx-0.5" />

        {/* 4. OBSERVATION */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className={`h-8 px-2.5 flex items-center gap-1.5 rounded-md text-[11px] font-bold uppercase tracking-wider transition-all ${['waypoints','lieux','groupe','exclusions'].includes(activeTab) ? 'bg-white/10 text-white' : 'text-[#FF9800] hover:bg-white/5'}`} data-testid="toolbar-observation-btn" title="Observation">
              <Binoculars className="h-3.5 w-3.5" /><span className="hidden sm:inline">Observation</span>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="bg-gray-950 border-gray-700/60 shadow-xl" side="bottom" align="start">
            <DropdownMenuItem onClick={() => setActiveTab(prev => prev === 'waypoints' ? 'carte' : 'waypoints')} className="text-white hover:bg-white/10 cursor-pointer" data-testid="obs-waypoints-item">
              <MapPin className="h-4 w-4 mr-2 text-[#FF9800]" /> Waypoints
              {activeWaypoints.length > 0 && <span className="ml-auto text-[9px] bg-[#3CB371] text-black rounded-full px-1.5 py-0.5 font-bold">{activeWaypoints.length}</span>}
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setActiveTab(prev => prev === 'lieux' ? 'carte' : 'lieux')} className="text-white hover:bg-white/10 cursor-pointer" data-testid="obs-lieux-item">
              <BookMarked className="h-4 w-4 mr-2 text-[#3b82f6]" /> Lieux
              {savedPlaces.length > 0 && <span className="ml-auto text-[9px] bg-[#3b82f6] text-white rounded-full px-1.5 py-0.5 font-bold">{savedPlaces.length}</span>}
            </DropdownMenuItem>
            <DropdownMenuSeparator className="bg-gray-700/50" />
            <DropdownMenuItem onClick={() => setActiveTab(prev => prev === 'groupe' ? 'carte' : 'groupe')} className="text-white hover:bg-white/10 cursor-pointer" data-testid="obs-groupe-item">
              <Users className="h-4 w-4 mr-2 text-[#f5a623]" /> Groupe
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setActiveTab(prev => prev === 'exclusions' ? 'carte' : 'exclusions')} className="text-white hover:bg-white/10 cursor-pointer" data-testid="obs-exclusions-item">
              <Shield className="h-4 w-4 mr-2 text-[#06b6d4]" /> Exclusions
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
        <div className="w-px h-5 bg-gray-700/50 mx-0.5" />

        {/* 5. INTELLIGENCE — terrain premium palette, Brain icon officiel */}
        <button onClick={() => setActiveTab(prev => prev === 'intelligence' ? 'carte' : 'intelligence')} className={`h-8 px-2.5 flex items-center gap-1.5 rounded-md text-[11px] font-bold uppercase tracking-wider transition-all ${activeTab === 'intelligence' ? 'bg-[#4A7A2E]/15 text-[#4A7A2E]' : 'text-[#A8885E] hover:bg-white/5'}`} data-testid="toolbar-intelligence-btn" title="Intelligence — Tableau central">
          <Brain className="h-3.5 w-3.5" /><span className="hidden sm:inline">Intelligence</span>
        </button>
        <div className="w-px h-5 bg-gray-700/50 mx-0.5" />

        {/* 7. LOCK — ADMIN ONLY */}
        {adminArchitecteMode && (
          <>
            <button onClick={() => setPrivacyMode(!privacyMode)} className={`h-8 w-8 flex items-center justify-center rounded-md transition-all ${privacyMode ? 'bg-red-500/15 text-red-400' : 'text-green-500 hover:bg-white/5'}`} data-testid="toolbar-lock-btn">
              {privacyMode ? <Lock className="h-3.5 w-3.5" /> : <Unlock className="h-3.5 w-3.5" />}
            </button>
            <div className="w-px h-5 bg-gray-700/50 mx-0.5" />
          </>
        )}

        {/* 8a. ZONES */}
        <Popover>
          <PopoverTrigger asChild>
            <button className="h-8 px-2 flex items-center gap-1.5 rounded-md text-[10px] font-bold uppercase tracking-wider hover:bg-white/5 transition-all" data-testid="toolbar-zones-btn" title="Controle des couches">
              <Layers className="h-3.5 w-3.5 text-emerald-400" /><span className="text-emerald-400 hidden sm:inline">Zones</span>
            </button>
          </PopoverTrigger>
          <PopoverContent align="end" sideOffset={8} className="w-64 bg-gray-950/95 backdrop-blur-md border-gray-700/60 p-3 shadow-xl shadow-black/40 max-h-[70vh] overflow-y-auto">
            <div className="space-y-2">
              {adminArchitecteMode && <div className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">Couches STEEVE-MAX</div>}
              {/* ZONES */}
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5"><span className="text-xs text-emerald-400 font-medium">Zones</span></div>
                  <Switch checked={showZonesLayer} onCheckedChange={setShowZonesLayer} className="scale-[0.6] data-[state=checked]:bg-emerald-500" data-testid="toggle-zones-layer" />
                </div>
                {showZonesLayer && (
                  <div className="ml-3 pl-2 border-l border-emerald-800/40 space-y-0.5">
                    {[{k:'alimentation',label:'Alimentation',color:'text-green-400'},{k:'repos',label:'Repos',color:'text-blue-400'},{k:'rut',label:'Rut',color:'text-orange-400'},{k:'habitat',label:'Habitat',color:'text-cyan-400'},{k:'affuts',label:'Affuts',color:'text-red-400'},{k:'trajets',label:'Trajets',color:'text-yellow-400'},{k:'multiEngines',label:'Multi-Engines',color:'text-emerald-300'}].map(item => (
                      <button key={item.k} onClick={() => toggleZoneSub(item.k)} className={`w-full flex items-center gap-1.5 px-1.5 py-0.5 rounded text-[10px] transition-all ${zoneSubFilters[item.k] ? `${item.color} bg-white/5` : 'text-gray-600 hover:text-gray-400'}`} data-testid={`zone-sub-${item.k}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${zoneSubFilters[item.k] ? 'bg-current' : 'bg-gray-700'}`} />{item.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <div className="h-px bg-gray-700/30" />
              {/* CORRIDORS */}
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-cyan-400 font-medium">Corridors</span>
                  <Switch checked={showCorridorsLayer} onCheckedChange={setShowCorridorsLayer} className="scale-[0.6] data-[state=checked]:bg-cyan-500" data-testid="toggle-corridors-layer" />
                </div>
                {showCorridorsLayer && (
                  <div className="ml-3 pl-2 border-l border-cyan-800/40 space-y-0.5">
                    {[{k:'normaux',label:'Normaux',color:'text-gray-300'},{k:'intenses',label:'Intenses',color:'text-orange-400'},{k:'extreme',label:'EXTREME',color:'text-red-400'},{k:'saisonniers',label:'Saisonniers',color:'text-cyan-300'}].map(item => (
                      <button key={item.k} onClick={() => toggleCorridorSub(item.k)} className={`w-full flex items-center gap-1.5 px-1.5 py-0.5 rounded text-[10px] transition-all ${corridorSubFilters[item.k] ? `${item.color} bg-white/5` : 'text-gray-600 hover:text-gray-400'}`} data-testid={`corridor-sub-${item.k}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${corridorSubFilters[item.k] ? 'bg-current' : 'bg-gray-700'}`} />{item.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <div className="h-px bg-gray-700/30" />
              {/* POINTS */}
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-400 font-medium">Points</span>
                  <Switch checked={showPointsLayer} onCheckedChange={setShowPointsLayer} className="scale-[0.6] data-[state=checked]:bg-gray-500" data-testid="toggle-points-layer" />
                </div>
                {showPointsLayer && (
                  <div className="ml-3 pl-2 border-l border-gray-700/40 space-y-0.5">
                    {[{k:'alimentation',label:'Alimentation',color:'text-green-400'},{k:'rut',label:'Rut',color:'text-orange-400'},{k:'repos',label:'Repos',color:'text-blue-400'},{k:'trajets',label:'Trajets',color:'text-yellow-400'},{k:'affuts',label:'Affuts',color:'text-red-400'},{k:'habitat',label:'Habitat',color:'text-cyan-400'},{k:'centroides',label:'Centroides',color:'text-white'},{k:'individuels',label:'Individuels',color:'text-gray-300'}].map(item => (
                      <button key={item.k} onClick={() => togglePointSub(item.k)} className={`w-full flex items-center gap-1.5 px-1.5 py-0.5 rounded text-[10px] transition-all ${pointSubFilters[item.k] ? `${item.color} bg-white/5` : 'text-gray-600 hover:text-gray-400'}`} data-testid={`point-sub-${item.k}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${pointSubFilters[item.k] ? 'bg-current' : 'bg-gray-700'}`} />{item.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <div className="h-px bg-gray-700/30" />
              {/* OVERLAYS */}
              <div className="space-y-1">
                <div className="text-[9px] font-bold uppercase tracking-wider text-gray-500">Overlays</div>
                <button onClick={() => setShowWindFlow(!showWindFlow)} className={`w-full flex items-center gap-1.5 px-1.5 py-0.5 rounded text-[10px] transition-all ${showWindFlow ? 'text-cyan-400 bg-white/5' : 'text-gray-600 hover:text-gray-400'}`} data-testid="layer-toggle-wind-flow">
                  <span className={`w-1.5 h-1.5 rounded-full ${showWindFlow ? 'bg-cyan-400' : 'bg-gray-700'}`} />Vent directionnel
                </button>
                {showWindFlow && (
                  <div className="flex gap-1 ml-4">
                    <button onClick={() => setWindMode('arrows')} className={`px-2 py-0.5 rounded text-[9px] transition-all ${windMode === 'arrows' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'bg-gray-900/50 text-gray-500'}`} data-testid="wind-mode-arrows">Minimaliste</button>
                    <button onClick={() => setWindMode('particles')} className={`px-2 py-0.5 rounded text-[9px] transition-all ${windMode === 'particles' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' : 'bg-gray-900/50 text-gray-500'}`} data-testid="wind-mode-particles">Particules</button>
                  </div>
                )}
                <button onClick={() => setShowExclusionOverlay(!showExclusionOverlay)} className={`w-full flex items-center gap-1.5 px-1.5 py-0.5 rounded text-[10px] transition-all ${showExclusionOverlay ? 'text-red-400 bg-white/5' : 'text-gray-600 hover:text-gray-400'}`} data-testid="layer-toggle-exclusion-overlay">
                  <span className={`w-1.5 h-1.5 rounded-full ${showExclusionOverlay ? 'bg-red-400' : 'bg-gray-700'}`} />Exclusions
                </button>
                <button onClick={() => setShowHeatmapV10(!showHeatmapV10)} className={`w-full flex items-center gap-1.5 px-1.5 py-0.5 rounded text-[10px] transition-all ${showHeatmapV10 ? 'text-orange-400 bg-white/5' : 'text-gray-600 hover:text-gray-400'}`} data-testid="layer-toggle-heatmap-v10">
                  <span className={`w-1.5 h-1.5 rounded-full ${showHeatmapV10 ? 'bg-orange-400' : 'bg-gray-700'}`} />Heatmap V10
                  {heatmapV10Data && <span className="ml-auto text-[8px] text-gray-500">{heatmapV10Data.score_avg}/100</span>}
                </button>
                {showHeatmapV10 && (
                  <div className="ml-3 pl-2 border-l border-orange-800/30 space-y-1 pt-0.5">
                    <button onClick={() => setHeatmapIncludeCorridors(!heatmapIncludeCorridors)} className={`w-full flex items-center gap-1.5 px-1.5 py-0.5 rounded text-[9px] transition-all ${heatmapIncludeCorridors ? 'text-cyan-400 bg-white/5' : 'text-gray-600 hover:text-gray-400'}`} data-testid="heatmap-toggle-corridors">
                      <span className={`w-1.5 h-1.5 rounded-full ${heatmapIncludeCorridors ? 'bg-cyan-400' : 'bg-gray-700'}`} />Corridors V10
                    </button>
                  </div>
                )}
              </div>
            </div>
          </PopoverContent>
        </Popover>
        <div className="w-px h-5 bg-gray-700/50 mx-0.5" />

        {/* 8a2. ALIMENTATION */}
        <Popover>
          <PopoverTrigger asChild>
            <button className={`h-8 px-2.5 flex items-center gap-1.5 rounded-md text-[10px] font-bold uppercase tracking-wider transition-all ${showAlimentationV2 ? 'bg-yellow-500/15 text-yellow-400' : 'text-gray-400 hover:bg-white/5'}`} data-testid="toolbar-alimentation-btn" title="Sites d'alimentation V2">
              <Droplets className="h-3.5 w-3.5" /><span className="hidden sm:inline">Alimentation</span>
              {showAlimentationV2 && alimentationV2Data && !alimentationV2Data.salines_disabled && (
                <span className="ml-0.5 text-[9px] bg-yellow-500/25 text-yellow-300 rounded px-1 py-px font-bold" data-testid="alimentation-badge">{alimentationV2Data.n_salines}</span>
              )}
            </button>
          </PopoverTrigger>
          <PopoverContent align="end" sideOffset={8} className="w-72 bg-gray-950/95 backdrop-blur-md border-gray-700/60 p-3 shadow-xl shadow-black/40">
            <div className="space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Alimentation V2</span>
                <Switch checked={showAlimentationV2} onCheckedChange={setShowAlimentationV2} className="scale-[0.6] data-[state=checked]:bg-yellow-500" data-testid="toggle-alimentation-v2-master" />
              </div>
              <div className="space-y-1.5 pt-1 border-t border-gray-700/40">
                <div className="flex items-center justify-between">
                  <span className={`text-xs font-medium ${alimentationV2Data?.salines_disabled ? 'text-gray-600' : 'text-yellow-400'}`}>Salines</span>
                  <Switch checked={showSalines && !alimentationV2Data?.salines_disabled} onCheckedChange={setShowSalines} disabled={!!alimentationV2Data?.salines_disabled} className="scale-[0.6] data-[state=checked]:bg-yellow-500 disabled:opacity-30" data-testid="toggle-salines" />
                </div>
                {alimentationV2Data?.salines_disabled && alimentationV2Data?.salines_message && (
                  <div className="px-2 py-1.5 bg-amber-900/20 border border-amber-700/30 rounded text-[10px] text-amber-300/80 leading-relaxed" data-testid="salines-disabled-message">{alimentationV2Data.salines_message}</div>
                )}
                {!alimentationV2Data?.salines_disabled && (
                  <div className="space-y-1" data-testid="salines-count-selector">
                    <div className="text-[9px] text-gray-500 uppercase font-bold">Nombre de salines</div>
                    <div className="flex gap-1">
                      {[1,2,3,4].map(n => (
                        <button key={n} onClick={() => setNSalinesMax(n)} className={`flex-1 h-7 rounded text-xs font-bold transition-all ${nSalinesMax === n ? 'bg-yellow-500/30 text-yellow-300 border border-yellow-500/50' : 'bg-gray-800/60 text-gray-500 border border-gray-700/30 hover:text-gray-300'}`} data-testid={`salines-count-${n}`}>{n}</button>
                      ))}
                    </div>
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <span className="text-xs text-amber-300 font-medium">Recommandations</span>
                  <Switch checked={showNutritionPanel} onCheckedChange={setShowNutritionPanel} className="scale-[0.6] data-[state=checked]:bg-amber-500" data-testid="toggle-nutrition-panel" />
                </div>
              </div>
              {alimentationV2Data && (
                <div className="pt-2 border-t border-gray-700/50 space-y-1">
                  <div className="text-[9px] text-gray-500 uppercase font-bold">Resume zone</div>
                  <div className="text-xs text-white">Score: <span className="text-yellow-400 font-bold">{alimentationV2Data.score_global}/100</span></div>
                  {!alimentationV2Data.salines_disabled && <div className="text-xs text-gray-400">Salines: <span className="text-yellow-300">{alimentationV2Data.n_salines}/{alimentationV2Data.n_candidates} candidats</span></div>}
                  <div className="text-xs text-gray-400">Espece: <span className="text-yellow-300">{alimentationV2Data.species_nom}</span></div>
                </div>
              )}
            </div>
          </PopoverContent>
        </Popover>
        <div className="w-px h-5 bg-gray-700/50 mx-0.5" />

        {/* 8a3. POINTS CHAUDS */}
        <Popover>
          <PopoverTrigger asChild>
            <button className={`h-8 px-2 flex items-center gap-1.5 rounded-md text-[10px] font-bold uppercase tracking-wider hover:bg-white/5 transition-all ${pointsChaudsMode ? 'bg-orange-500/15 text-orange-400' : 'text-gray-400'}`} data-testid="toolbar-points-chauds-btn">
              <Flame className="h-3.5 w-3.5" /><span className="hidden sm:inline">Points chauds</span>
            </button>
          </PopoverTrigger>
          <PopoverContent align="end" sideOffset={8} className="w-56 bg-gray-950/95 backdrop-blur-md border-gray-700/60 p-3 shadow-xl shadow-black/40">
            <div className="space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Points chauds</span>
                <Switch checked={pointsChaudsMode} onCheckedChange={(v) => { setPointsChaudsMode(v); if (v) setShowPointsLayer(true); }} className="scale-[0.6] data-[state=checked]:bg-orange-500" data-testid="toggle-points-chauds-mode" />
              </div>
              {pointsChaudsMode && (
                <div className="space-y-1.5 pt-1 border-t border-gray-700/40">
                  {[{key:'tous',label:'Tous les points',color:'text-white'},{key:'alimentation',label:'Alimentation',color:'text-green-400'},{key:'rut',label:'Rut',color:'text-orange-400'},{key:'repos',label:'Repos',color:'text-blue-400'},{key:'trajets',label:'Trajets',color:'text-yellow-400'},{key:'affuts',label:'Affuts',color:'text-red-400'},{key:'habitat',label:'Habitat',color:'text-teal-400'}].map(item => (
                    <button key={item.key} onClick={() => setPointsChaudsFilter(item.key)} className={`w-full text-left px-2 py-1 rounded text-xs font-medium transition-all ${pointsChaudsFilter === item.key ? `${item.color} bg-white/10` : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'}`} data-testid={`points-chauds-filter-${item.key}`}>{item.label}</button>
                  ))}
                </div>
              )}
            </div>
          </PopoverContent>
        </Popover>

        {/* 8b. SEUIL */}
        <Popover>
          <PopoverTrigger asChild>
            <button className="h-8 px-2 flex items-center gap-1.5 rounded-md text-[10px] font-bold uppercase tracking-wider hover:bg-white/5 transition-all" data-testid="toolbar-seuil-btn">
              <span className="text-gray-400">Seuil</span><span className="text-[#f5a623] font-bold">{minPercentageFilter}%</span>
            </button>
          </PopoverTrigger>
          <PopoverContent align="end" sideOffset={8} className="w-56 bg-gray-950/95 backdrop-blur-md border-gray-700/60 p-3 shadow-xl shadow-black/40">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-300 font-medium">Seuil minimum</span>
                <span className="text-xs font-bold text-[#f5a623]">{minPercentageFilter}%</span>
              </div>
              <input type="range" min="10" max="80" step="5" value={minPercentageFilter} onChange={(e) => setMinPercentageFilter(parseInt(e.target.value))} className="w-full h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-[#f5a623]" data-testid="min-percentage-slider" />
            </div>
          </PopoverContent>
        </Popover>
        <div className="w-px h-5 bg-gray-700/50 mx-0.5" />

        {/* 8c. CURSEUR BIONIC — terrain premium */}
        <div className="h-8 px-2 flex items-center gap-1.5 rounded-md" data-testid="toolbar-curseur-bionic">
          <span className="text-[10px] font-bold uppercase tracking-wider text-[#A8885E] hidden sm:inline">Curseur</span>
          <Switch checked={showCursorBionic} onCheckedChange={setShowCursorBionic} className="scale-[0.6] data-[state=checked]:bg-[#4A7A2E]" data-testid="toggle-curseur-bionic" />
        </div>

        {/* SCORE BADGE */}
        <div className="w-px h-5 bg-gray-700/50 mx-0.5" />
        <BionicScoreBadge center={selectedWaypointForZones ? { lat: selectedWaypointForZones.lat || selectedWaypointForZones.latitude, lng: selectedWaypointForZones.lng || selectedWaypointForZones.longitude } : null} species={selectedSpecies} month={new Date().getMonth() + 1} compact />

        {/* ADMIN ARCHITECTE */}
        <div className="w-px h-5 bg-gray-700/50 mx-0.5" />
        <button className={`h-7 w-7 flex items-center justify-center rounded transition-all ${adminArchitecteMode ? 'bg-purple-500/20 text-purple-400' : 'text-gray-700 hover:text-gray-500'}`} data-testid="admin-architecte-btn" onClick={() => {
          if (adminArchitecteMode) { setAdminArchitecteMode(false); } else { const pwd = window.prompt('Mot de passe administrateur:'); if (pwd === 'Saturn5858*') setAdminArchitecteMode(true); }
        }}>
          <Shield className="h-3 w-3" />
        </button>
      </div>
    </nav>
  );
}
