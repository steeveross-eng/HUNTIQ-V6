/**
 * WaypointUnifiedPanel.jsx — Panneau latéral unifié BIONIC V5 300%
 *
 * Source de vérité unique pour toutes les interactions waypoint.
 * Panneau latéral unifié — source de vérité unique pour les waypoints.
 *
 * Logique contextuelle:
 *   - Aucun waypoint → état neutre + CTA
 *   - Un waypoint sélectionné → détails complets + actions
 *   - Plusieurs waypoints → liste + sélection
 *
 * Aucune duplication d'actions entre carte et panneau.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  MapPin, Target, Trash2, Share2, ChevronRight, ChevronLeft,
  Zap, Clock, Thermometer, TreePine, Eye, EyeOff, Navigation,
  Layers, Search, AlertTriangle, Camera, FileDown, FileText,
  GitCompareArrows, CheckSquare, Square
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const WaypointUnifiedPanel = ({
  waypoints = [],
  activeWaypoints = [],
  selectedWaypoint,
  onSelectWaypoint,
  onDeselectWaypoint,
  onDeleteWaypoint,
  onToggleActive,
  onAnalyze,
  onShare,
  onCenterMap,
  userPosition,
  watchingPosition,
  onStartWatching,
  onStopWatching,
  layersVisible = {},
  dynamicScores,
  currentMapCenter,
  PLACE_TYPES = [],
  // BIONIC V5 300%: Snapshot Territoire
  onGenerateSnapshot,
  isGeneratingSnapshot = false,
  snapshotData = null,
  // V8.3.A: Compare multi-waypoints
  compareSelection = [],
  onToggleCompare,
  onLaunchCompare,
}) => {
  const [panelExpanded, setPanelExpanded] = useState(true);
  const [localDynamicScores, setLocalDynamicScores] = useState(null);
  const [compareMode, setCompareMode] = useState(false);

  // Fetch dynamic scores for selected waypoint
  useEffect(() => {
    if (!selectedWaypoint) { setLocalDynamicScores(null); return; }
    let cancelled = false;
    const fetchScores = async () => {
      try {
        const resp = await fetch(`${API_BASE}/api/v1/bionic/dynamic/scores`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            lat: selectedWaypoint.lat,
            lng: selectedWaypoint.lng,
            species: 'moose',
          }),
        });
        if (resp.ok && !cancelled) {
          const data = await resp.json();
          if (data.success) setLocalDynamicScores(data);
        }
      } catch { /* non-bloquant */ }
    };
    fetchScores();
    return () => { cancelled = true; };
  }, [selectedWaypoint]);

  const getTypeInfo = useCallback((wp) => {
    return PLACE_TYPES.find(t => t.id === wp?.type) || { name: 'Waypoint', color: '#f5a623' };
  }, [PLACE_TYPES]);

  const activeLayers = Object.entries(layersVisible).filter(([, v]) => v).map(([k]) => k);

  return (
    <div className="flex h-full" data-testid="waypoint-unified-panel">
      {/* Liste + sélection */}
      <div className={`${panelExpanded ? 'w-80' : 'w-12'} bg-gray-900/95 border-r border-gray-800 flex flex-col transition-all duration-300`}>
        {/* Header avec toggle */}
        <div className="p-3 border-b border-gray-800 flex items-center gap-2">
          <button
            onClick={() => setPanelExpanded(!panelExpanded)}
            className="p-1.5 rounded-lg hover:bg-gray-800 transition-colors"
            data-testid="waypoint-panel-toggle"
          >
            {panelExpanded ? <ChevronLeft className="h-4 w-4 text-gray-400" /> : <ChevronRight className="h-4 w-4 text-gray-400" />}
          </button>
          {panelExpanded && (
            <div className="flex items-center justify-between flex-1">
              <h2 className="text-white font-semibold flex items-center gap-2 text-sm">
                <MapPin className="h-4 w-4 text-[#f5a623]" />
                Waypoints
              </h2>
              <Badge className="bg-[#f5a623]/20 text-[#f5a623] text-[10px]">
                {activeWaypoints.length}/{waypoints.length}
              </Badge>
            </div>
          )}
        </div>

        {panelExpanded && (
          <>
            {/* Position GPS */}
            <div className="px-3 py-2 border-b border-gray-800/50">
              <div className="bg-blue-900/20 rounded-lg p-2.5 border border-blue-500/20">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-pulse" />
                    <span className="text-blue-400 text-xs font-medium">GPS</span>
                  </div>
                  <Switch
                    checked={watchingPosition}
                    onCheckedChange={(checked) => checked ? onStartWatching?.() : onStopWatching?.()}
                    className="data-[state=checked]:bg-blue-500 scale-75"
                    data-testid="gps-toggle"
                  />
                </div>
                {userPosition && (
                  <div className="text-[10px] text-gray-500 mt-1">
                    {userPosition.lat.toFixed(5)}, {userPosition.lng.toFixed(5)}
                  </div>
                )}
              </div>
            </div>

            {/* V8.3.A: Bouton mode comparaison */}
            {waypoints.length >= 2 && (
              <div className="px-3 py-2 border-b border-gray-800/50">
                <button
                  onClick={() => setCompareMode(!compareMode)}
                  className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                    compareMode
                      ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30'
                      : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800/70 hover:text-gray-300 border border-gray-700/30'
                  }`}
                  data-testid="compare-mode-toggle"
                >
                  <GitCompareArrows className="h-3.5 w-3.5" />
                  {compareMode ? 'Mode comparaison actif' : 'Comparer des waypoints'}
                </button>
                {compareMode && compareSelection.length > 0 && (
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-[9px] text-gray-500">{compareSelection.length}/3 sélectionnés</span>
                    <button
                      onClick={onLaunchCompare}
                      disabled={compareSelection.length < 2}
                      className={`ml-auto px-3 py-1.5 rounded-md text-[10px] font-bold uppercase tracking-wider transition-all ${
                        compareSelection.length >= 2
                          ? 'bg-cyan-500 text-black hover:bg-cyan-400'
                          : 'bg-gray-800 text-gray-600 cursor-not-allowed'
                      }`}
                      data-testid="compare-launch-btn"
                    >
                      Comparer
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Liste des waypoints */}
            <div className="flex-1 overflow-y-auto p-3 space-y-1.5" data-testid="waypoint-list">
              {waypoints.length === 0 ? (
                <div className="text-center text-gray-500 py-12" data-testid="waypoint-empty-state">
                  <Navigation className="h-10 w-10 mx-auto mb-3 opacity-20" />
                  <p className="text-sm">Aucun waypoint</p>
                  <p className="text-[10px] mt-1 text-gray-600">
                    Cliquez sur la carte ou utilisez "Enregistrer un Waypoint"
                  </p>
                </div>
              ) : (
                waypoints.map(wp => {
                  const typeInfo = getTypeInfo(wp);
                  const isSelected = selectedWaypoint?.id === wp.id;
                  const isCompareChecked = compareSelection.some(w => w.id === wp.id);
                  const isCompareDisabled = !isCompareChecked && compareSelection.length >= 3;
                  return (
                    <div key={wp.id} className="flex items-center gap-1.5">
                      {/* V8.3.A: Checkbox comparaison */}
                      {compareMode && (
                        <button
                          onClick={(e) => { e.stopPropagation(); if (!isCompareDisabled) onToggleCompare?.(wp); }}
                          className={`flex-shrink-0 p-0.5 rounded transition-colors ${
                            isCompareDisabled ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer hover:bg-gray-800/50'
                          }`}
                          data-testid={`compare-checkbox-${wp.id}`}
                        >
                          {isCompareChecked ? (
                            <CheckSquare className="h-4 w-4 text-cyan-400" />
                          ) : (
                            <Square className="h-4 w-4 text-gray-600" />
                          )}
                        </button>
                      )}
                      <button
                        onClick={() => isSelected ? onDeselectWaypoint?.() : onSelectWaypoint?.(wp)}
                        className={`flex-1 text-left rounded-lg p-2.5 border transition-all duration-200 ${
                          isSelected
                            ? 'bg-[#f5a623]/10 border-[#f5a623]/50 ring-1 ring-[#f5a623]/30'
                            : wp.active
                              ? 'bg-gray-800/40 border-gray-700/50 hover:bg-gray-800/70'
                              : 'bg-gray-900/40 border-gray-800/30 opacity-50 hover:opacity-70'
                        }`}
                        data-testid={`waypoint-item-${wp.id}`}
                      >
                        <div className="flex items-center gap-2.5">
                          <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                            style={{ backgroundColor: `${typeInfo.color || '#f5a623'}15`, border: `1px solid ${typeInfo.color || '#f5a623'}30` }}>
                            <MapPin className="h-4 w-4" style={{ color: typeInfo.color || '#f5a623' }} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="text-white text-xs font-medium truncate">{wp.name}</div>
                            <div className="text-[10px] text-gray-500 font-mono mt-0.5">
                              {wp.lat.toFixed(4)}, {wp.lng.toFixed(4)}
                            </div>
                          </div>
                          {isSelected && (
                            <Target className="h-4 w-4 text-[#f5a623] flex-shrink-0" />
                          )}
                        </div>
                      </button>
                    </div>
                  );
                })
              )}
            </div>
          </>
        )}
      </div>

      {/* Panneau de détails — contextuel */}
      <div className="flex-1 bg-black overflow-y-auto" data-testid="waypoint-detail-panel">
        {!selectedWaypoint ? (
          /* État neutre — aucun waypoint sélectionné */
          <div className="flex items-center justify-center h-full" data-testid="waypoint-neutral-state">
            <div className="text-center max-w-xs">
              <div className="w-16 h-16 rounded-2xl bg-[#f5a623]/10 flex items-center justify-center mx-auto mb-4">
                <Search className="h-8 w-8 text-[#f5a623]/40" />
              </div>
              <p className="text-gray-400 text-sm">Sélectionnez un waypoint</p>
              <p className="text-gray-600 text-[10px] mt-2">
                Cliquez sur un waypoint dans la liste ou sur la carte pour afficher ses détails, l'analyser et gérer ses exclusions.
              </p>
            </div>
          </div>
        ) : (
          /* Waypoint sélectionné — détails complets */
          <div className="p-5 space-y-4" data-testid="waypoint-detail-content">
            {/* En-tête */}
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <div className="w-12 h-12 rounded-xl flex items-center justify-center"
                  style={{ backgroundColor: `${getTypeInfo(selectedWaypoint).color || '#f5a623'}15`, border: `1px solid ${getTypeInfo(selectedWaypoint).color || '#f5a623'}30` }}>
                  <MapPin className="h-6 w-6" style={{ color: getTypeInfo(selectedWaypoint).color || '#f5a623' }} />
                </div>
                <div>
                  <h3 className="text-white font-bold text-lg" data-testid="waypoint-detail-name">
                    {selectedWaypoint.name}
                  </h3>
                  <div className="text-xs text-gray-500 mt-0.5">
                    {getTypeInfo(selectedWaypoint).name || 'Waypoint'}
                  </div>
                </div>
              </div>
              <Badge className={`text-[10px] ${selectedWaypoint.active ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>
                {selectedWaypoint.active ? 'Actif' : 'Inactif'}
              </Badge>
            </div>

            {/* Coordonnées */}
            <div className="bg-gray-900/80 rounded-lg p-3 border border-gray-800" data-testid="waypoint-detail-coords">
              <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Coordonnées</div>
              <div className="text-sm text-white font-mono">
                {selectedWaypoint.lat.toFixed(6)}, {selectedWaypoint.lng.toFixed(6)}
              </div>
            </div>

            {/* Actions principales */}
            <div className="grid grid-cols-2 gap-2" data-testid="waypoint-detail-actions">
              <Button
                onClick={() => onAnalyze?.(selectedWaypoint)}
                className="bg-[#f5a623]/20 text-[#f5a623] hover:bg-[#f5a623]/30 border border-[#f5a623]/30 h-9 text-xs"
                data-testid="waypoint-btn-analyze"
              >
                <Target className="h-3.5 w-3.5 mr-1.5" />
                Analyser
              </Button>
              <Button
                onClick={() => onCenterMap?.(selectedWaypoint)}
                className="bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 border border-blue-500/30 h-9 text-xs"
                data-testid="waypoint-btn-center"
              >
                <Navigation className="h-3.5 w-3.5 mr-1.5" />
                Centrer
              </Button>
              <Button
                onClick={() => onShare?.(selectedWaypoint)}
                className="bg-purple-500/20 text-purple-400 hover:bg-purple-500/30 border border-purple-500/30 h-9 text-xs"
                data-testid="waypoint-btn-share"
              >
                <Share2 className="h-3.5 w-3.5 mr-1.5" />
                Partager
              </Button>
              <Button
                onClick={() => { onDeleteWaypoint?.(selectedWaypoint.id); }}
                className="bg-red-500/20 text-red-400 hover:bg-red-500/30 border border-red-500/30 h-9 text-xs"
                data-testid="waypoint-btn-delete"
              >
                <Trash2 className="h-3.5 w-3.5 mr-1.5" />
                Effacer
              </Button>
            </div>

            {/* Toggle actif/inactif */}
            <div className="flex items-center justify-between bg-gray-900/80 rounded-lg p-3 border border-gray-800">
              <span className="text-xs text-gray-400">Waypoint actif</span>
              <Switch
                checked={selectedWaypoint.active}
                onCheckedChange={() => onToggleActive?.(selectedWaypoint.id)}
                className="data-[state=checked]:bg-[#f5a623]"
                data-testid="waypoint-toggle-active"
              />
            </div>

            {/* Exclusions dynamiques — temps réel */}
            <div className="bg-purple-900/30 rounded-lg p-3 border border-purple-500/30" data-testid="waypoint-dynamic-scores">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Zap className="h-3.5 w-3.5 text-purple-400" />
                  <span className="text-xs font-semibold text-purple-400">Exclusions dynamiques</span>
                </div>
                <Badge className="bg-purple-500/20 text-purple-300 text-[9px]">LIVE</Badge>
              </div>
              {localDynamicScores ? (
                <div className="space-y-1.5">
                  <div className="flex justify-between text-[10px]">
                    <span className="text-gray-400">Score composite</span>
                    <span className="text-purple-300 font-bold">{localDynamicScores.score}/100</span>
                  </div>
                  <div className="flex justify-between text-[10px]">
                    <span className="text-gray-400">Risque</span>
                    <span className={localDynamicScores.risk_level === 'elevated' ? 'text-orange-400' : localDynamicScores.risk_level === 'critical' ? 'text-red-400' : 'text-green-400'}>
                      {localDynamicScores.risk_level?.toUpperCase()}
                    </span>
                  </div>
                  {localDynamicScores.factors?.temporal && (
                    <div className="flex items-center gap-2 text-[10px]">
                      <Clock className="h-3 w-3 text-blue-400" />
                      <span className="text-gray-400 flex-1">Temporel</span>
                      <span className="text-blue-300">{Math.round(localDynamicScores.factors.temporal.activity_level * 100)}%</span>
                    </div>
                  )}
                  {localDynamicScores.factors?.hunting_pressure && (
                    <div className="flex items-center gap-2 text-[10px]">
                      <Target className="h-3 w-3 text-red-400" />
                      <span className="text-gray-400 flex-1">Pression chasse</span>
                      <span className={localDynamicScores.factors.hunting_pressure.hunting_season ? 'text-red-400' : 'text-green-400'}>
                        {localDynamicScores.factors.hunting_pressure.hunting_season ? 'SAISON' : 'Hors saison'}
                      </span>
                    </div>
                  )}
                  {localDynamicScores.factors?.seasonal_context && (
                    <div className="flex items-center gap-2 text-[10px]">
                      <TreePine className="h-3 w-3 text-emerald-400" />
                      <span className="text-gray-400 flex-1">Saison</span>
                      <span className="text-emerald-300 capitalize">{localDynamicScores.factors.seasonal_context.season}</span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-[10px] text-gray-500">Chargement...</div>
              )}
            </div>

            {/* Couches activées */}
            <div className="bg-gray-900/80 rounded-lg p-3 border border-gray-800" data-testid="waypoint-active-layers">
              <div className="flex items-center gap-2 mb-2">
                <Layers className="h-3.5 w-3.5 text-teal-400" />
                <span className="text-xs font-semibold text-teal-400">Couches activées</span>
              </div>
              {activeLayers.length > 0 ? (
                <div className="flex flex-wrap gap-1.5">
                  {activeLayers.map(l => (
                    <Badge key={l} className="bg-teal-500/10 text-teal-300 text-[9px] border border-teal-500/20">
                      {l}
                    </Badge>
                  ))}
                </div>
              ) : (
                <div className="text-[10px] text-gray-500">Aucune couche active</div>
              )}
            </div>

            {/* BIONIC V5 300%: Snapshot Territoire — Export PDF/JSON */}
            <div className="bg-[#f5a623]/10 rounded-lg p-3 border border-[#f5a623]/20" data-testid="waypoint-snapshot-section">
              <div className="flex items-center gap-2 mb-2">
                <Camera className="h-3.5 w-3.5 text-[#f5a623]" />
                <span className="text-xs font-semibold text-[#f5a623]">Snapshot Territoire</span>
                <Badge className="bg-[#f5a623]/20 text-[#f5a623] text-[9px] ml-auto">1km x 1km</Badge>
              </div>
              <p className="text-[10px] text-gray-500 mb-2">
                Fige l'état complet du territoire dans le carré d'analyse.
              </p>
              <div className="grid grid-cols-2 gap-1.5">
                <Button
                  onClick={() => onGenerateSnapshot?.('json')}
                  disabled={isGeneratingSnapshot}
                  className="bg-[#f5a623]/20 text-[#f5a623] hover:bg-[#f5a623]/30 border border-[#f5a623]/30 h-8 text-[10px]"
                  data-testid="snapshot-btn-json"
                >
                  <FileText className="h-3 w-3 mr-1" />
                  {isGeneratingSnapshot ? '...' : 'Export JSON'}
                </Button>
                <Button
                  onClick={() => onGenerateSnapshot?.('pdf')}
                  disabled={isGeneratingSnapshot}
                  className="bg-[#f5a623]/20 text-[#f5a623] hover:bg-[#f5a623]/30 border border-[#f5a623]/30 h-8 text-[10px]"
                  data-testid="snapshot-btn-pdf"
                >
                  <FileDown className="h-3 w-3 mr-1" />
                  {isGeneratingSnapshot ? '...' : 'Export PDF'}
                </Button>
              </div>
              {snapshotData && (
                <div className="mt-2 text-[9px] text-green-400">
                  Dernier snapshot: {new Date(snapshotData.timestamp).toLocaleString('fr-CA')}
                </div>
              )}
            </div>

            {/* Sections futures — Placeholders */}
            <div className="space-y-2 opacity-40">
              <div className="bg-gray-900/50 rounded-lg p-3 border border-gray-800/50">
                <div className="text-[10px] text-gray-600 uppercase tracking-wider">Historique (V2)</div>
              </div>
              <div className="bg-gray-900/50 rounded-lg p-3 border border-gray-800/50">
                <div className="text-[10px] text-gray-600 uppercase tracking-wider">Notes terrain (V2)</div>
              </div>
              <div className="bg-gray-900/50 rounded-lg p-3 border border-gray-800/50">
                <div className="text-[10px] text-gray-600 uppercase tracking-wider">Photos (V2)</div>
              </div>
              <div className="bg-gray-900/50 rounded-lg p-3 border border-gray-800/50">
                <div className="text-[10px] text-gray-600 uppercase tracking-wider">Mode Équipe (V2)</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WaypointUnifiedPanel;
