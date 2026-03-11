/**
 * DiagnosticExclusionsPanel — Onglet Diagnostic Exclusions
 * BIONIC V5 300% — Migration du panneau d'analyse droit
 * 
 * Contenu migré:
 * - ZoneInfoPanel (détails zone survolée/sélectionnée)
 * - Mode Libre (indicateur sans waypoints)
 * - Exclusion Terrain V5 (sources Overpass, indicateurs)
 * - SeasonalConditionsWidget
 * - AlertsPanel + FavoritesList
 * - Score Global + Scores par catégorie
 *
 * Prépare l'intégration future ExclusionsSpatiales.v2
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Layers, Waves, CheckCircle, RefreshCw, Target,
  AlertTriangle, Shield, Activity, Zap, Clock, Thermometer, TreePine
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import ZoneInfoPanel from '@/components/territoire/ZoneInfoPanel';
import SeasonalConditionsWidget from '@/components/territoire/SeasonalConditionsWidget';
import { AlertsPanel, FavoritesList } from '@/components/territoire/ZoneFavorites';
import { SCORE_CATEGORIES } from '@/core/bionic';

const API_BASE = process.env.REACT_APP_BACKEND_URL;

const DiagnosticExclusionsPanel = ({
  hoveredZone,
  selectedZone,
  onClearZone,
  activeWaypoints,
  visibleZonesCount,
  isLoadingExclusions,
  terrainExclusions,
  currentMapCenter,
  alerts,
  unreadAlertCount,
  markAlertRead,
  markAllAlertsRead,
  checkOptimalConditions,
  favoritesLoading,
  favorites,
  removeFavorite,
  updateAlertSettings,
  getZoneConditions,
  displayScore,
  categoryScores,
  bionicStats,
}) => {
  // Fetch des scores dynamiques
  const [dynamicScores, setDynamicScores] = useState(null);
  const [loadingDynamic, setLoadingDynamic] = useState(false);

  const fetchDynamicScores = useCallback(async () => {
    if (!currentMapCenter?.lat) return;
    setLoadingDynamic(true);
    try {
      const resp = await fetch(`${API_BASE}/api/v1/bionic/dynamic/scores`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lat: currentMapCenter.lat,
          lng: currentMapCenter.lng,
          species: 'moose',
        }),
      });
      if (resp.ok) {
        const data = await resp.json();
        if (data.success) setDynamicScores(data);
      }
    } catch { /* non-bloquant */ }
    setLoadingDynamic(false);
  }, [currentMapCenter]);

  useEffect(() => {
    fetchDynamicScores();
    const interval = setInterval(fetchDynamicScores, 120000); // Refresh toutes les 2 min
    return () => clearInterval(interval);
  }, [fetchDynamicScores]);

  return (
    <div className="h-full overflow-y-auto bg-black" data-testid="diagnostic-exclusions-panel">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-black/95 backdrop-blur-sm border-b border-gray-800 px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-cyan-500/20 flex items-center justify-center">
            <Shield className="h-4 w-4 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white">Diagnostic Exclusions</h2>
            <p className="text-[10px] text-gray-500">ExclusionsSpatiales.v1 — Backend source de vérité</p>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-4">
        {/* Grille principale: 2 colonnes */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

          {/* COLONNE 1: Diagnostic Zones */}
          <div className="space-y-4">
            {/* Zone Info Panel */}
            <div className="bg-gray-900/80 rounded-lg border border-gray-800 p-4" data-testid="diag-zone-info">
              <div className="flex items-center gap-2 mb-3">
                <Target className="h-4 w-4 text-[#f5a623]" />
                <span className="text-xs font-semibold text-white uppercase tracking-wider">Zone sélectionnée</span>
              </div>
              <ZoneInfoPanel
                zone={hoveredZone || selectedZone}
                onClear={onClearZone}
              />
              {!(hoveredZone || selectedZone) && (
                <p className="text-[10px] text-gray-500 mt-2">
                  Survolez ou cliquez une zone sur la carte pour voir ses détails ici.
                </p>
              )}
            </div>

            {/* Mode Libre */}
            {(!activeWaypoints || activeWaypoints.length === 0) && (
              <div className="bg-emerald-900/30 rounded-lg p-4 border border-emerald-500/30" data-testid="diag-mode-libre">
                <div className="flex items-center gap-2 mb-2">
                  <Layers className="h-4 w-4 text-emerald-400" />
                  <span className="text-xs font-medium text-emerald-400">Mode Libre actif</span>
                </div>
                <p className="text-[10px] text-gray-400 leading-relaxed">
                  Les couches BIONIC couvrent toute la zone visible. Ajoutez des waypoints pour concentrer l'analyse.
                </p>
                <p className="text-[10px] text-emerald-300/70 mt-2">
                  {visibleZonesCount} zone{visibleZonesCount !== 1 ? 's' : ''} affichée{visibleZonesCount !== 1 ? 's' : ''}
                </p>
              </div>
            )}

            {/* Exclusion Terrain V5 */}
            <div className="bg-cyan-900/40 rounded-lg p-4 border border-cyan-500/40" data-testid="diag-exclusion-terrain">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Waves className="h-4 w-4 text-cyan-400" />
                  <span className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">Exclusion Terrain V5</span>
                </div>
                <Badge className="bg-cyan-500/20 text-cyan-300 text-[9px] px-1.5">
                  PERMANENT
                </Badge>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="text-gray-400">Module</span>
                  <span className="text-cyan-300 font-mono">ExclusionsSpatiales.v1</span>
                </div>
                <div className="flex items-center justify-between text-[10px]">
                  <span className="text-gray-400">Sources</span>
                  <span className="text-cyan-300">OSM / Overpass API</span>
                </div>
                <div className="flex items-center justify-between text-[10px]">
                  <span className="text-gray-400">Types d'exclusion</span>
                  <span className="text-cyan-300">water, urban, roads, infrastructure</span>
                </div>
                <div className="flex items-center justify-between text-[10px]">
                  <span className="text-gray-400">Retry</span>
                  <span className="text-cyan-300">3x avec délai exponentiel</span>
                </div>
                {isLoadingExclusions ? (
                  <div className="flex items-center gap-2 text-[10px] text-cyan-300 mt-1">
                    <RefreshCw className="h-3 w-3 animate-spin" />
                    Analyse terrain en cours...
                  </div>
                ) : terrainExclusions.length > 0 ? (
                  <div className="flex items-center justify-between text-[10px] mt-1">
                    <span className="text-gray-400">Zones exclues</span>
                    <span className="text-orange-400">{terrainExclusions.length} entités</span>
                  </div>
                ) : (
                  <div className="text-[10px] text-green-400 flex items-center gap-1 mt-1">
                    <CheckCircle className="h-3 w-3" />
                    Exclusion active — Pipeline opérationnel
                  </div>
                )}
              </div>
            </div>

            {/* Conditions Saisonnières */}
            <div className="bg-gray-900/80 rounded-lg border border-gray-800 p-4" data-testid="diag-seasonal">
              <SeasonalConditionsWidget
                lat={currentMapCenter?.lat}
                lng={currentMapCenter?.lng}
              />
            </div>
          </div>

          {/* COLONNE 2: Scores & Alertes */}
          <div className="space-y-4">
            {/* Score Global */}
            <div className="bg-[#f5a623]/10 rounded-lg p-4 border border-[#f5a623]/30" data-testid="diag-score-global">
              <div className="text-[10px] text-gray-400 uppercase tracking-wider mb-1">Score Global Territoire</div>
              <div className="flex items-baseline gap-2">
                <span className="text-5xl font-bold text-white">{displayScore ?? '—'}</span>
                <span className="text-gray-500 text-2xl">/100</span>
              </div>
              {bionicStats?.total !== undefined && (
                <div className="text-[10px] text-gray-500 mt-2">
                  {bionicStats.total} zones analysées
                  {bionicStats.error && <span className="text-red-400 ml-2">Erreur pipeline</span>}
                </div>
              )}
            </div>

            {/* Scores par catégorie */}
            <div className="bg-gray-900/80 rounded-lg border border-gray-800 p-4" data-testid="diag-category-scores">
              <div className="flex items-center gap-2 mb-3">
                <Activity className="h-4 w-4 text-[#f5a623]" />
                <span className="text-xs font-semibold text-white uppercase tracking-wider">Scores par catégorie</span>
              </div>
              <div className="space-y-2">
                {SCORE_CATEGORIES.map((cat) => {
                  const score = categoryScores[cat.id] || 0;
                  return (
                    <div key={cat.id} className="bg-gray-800/50 rounded p-2">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs text-gray-300">{cat.icon} {cat.name}</span>
                        <span className="text-xs font-bold text-white">{score}%</span>
                      </div>
                      <div className="h-1.5 bg-gray-700 rounded-full">
                        <div
                          className="h-full bg-[#f5a623] rounded-full transition-all"
                          style={{ width: `${score}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Exclusions Dynamiques — BIONIC V5 300% */}
            <div className="bg-purple-900/30 rounded-lg p-4 border border-purple-500/30" data-testid="diag-dynamic-scores">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-purple-400" />
                  <span className="text-xs font-semibold text-purple-400 uppercase tracking-wider">Exclusions Dynamiques</span>
                </div>
                <Badge className="bg-purple-500/20 text-purple-300 text-[9px] px-1.5">
                  TEMPS RÉEL
                </Badge>
              </div>
              {loadingDynamic ? (
                <div className="flex items-center gap-2 text-[10px] text-purple-300">
                  <RefreshCw className="h-3 w-3 animate-spin" />
                  Calcul des facteurs dynamiques...
                </div>
              ) : dynamicScores ? (
                <div className="space-y-2">
                  {/* Score composite */}
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="text-gray-400">Score composite</span>
                    <span className="text-purple-300 font-bold">{dynamicScores.score}/100</span>
                  </div>
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="text-gray-400">Risque</span>
                    <span className={`font-mono ${dynamicScores.risk_level === 'elevated' ? 'text-orange-400' : dynamicScores.risk_level === 'critical' ? 'text-red-400' : 'text-green-400'}`}>
                      {dynamicScores.risk_level.toUpperCase()}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="text-gray-400">Facteurs actifs</span>
                    <span className="text-purple-300">{dynamicScores.active_factors}/{dynamicScores.total_factors}</span>
                  </div>

                  {/* Facteurs individuels */}
                  <div className="mt-2 pt-2 border-t border-purple-500/20 space-y-1.5">
                    {dynamicScores.factors?.temporal && (
                      <div className="flex items-center gap-2 text-[10px]">
                        <Clock className="h-3 w-3 text-blue-400" />
                        <span className="text-gray-400 flex-1">Temporel (h{dynamicScores.factors.temporal.hour})</span>
                        <span className="text-blue-300">{(dynamicScores.factors.temporal.activity_level * 100 / 100).toFixed(0)}%</span>
                      </div>
                    )}
                    {dynamicScores.factors?.thermal_stress && (
                      <div className="flex items-center gap-2 text-[10px]">
                        <Thermometer className="h-3 w-3 text-orange-400" />
                        <span className="text-gray-400 flex-1">Stress thermique</span>
                        <span className={dynamicScores.factors.thermal_stress.active ? 'text-orange-400' : 'text-green-400'}>
                          {dynamicScores.factors.thermal_stress.active ? 'ACTIF' : 'Inactif'}
                        </span>
                      </div>
                    )}
                    {dynamicScores.factors?.hunting_pressure && (
                      <div className="flex items-center gap-2 text-[10px]">
                        <Target className="h-3 w-3 text-red-400" />
                        <span className="text-gray-400 flex-1">Pression chasse</span>
                        <span className={dynamicScores.factors.hunting_pressure.hunting_season ? 'text-red-400' : 'text-green-400'}>
                          {dynamicScores.factors.hunting_pressure.hunting_season ? 'SAISON' : 'Hors saison'}
                        </span>
                      </div>
                    )}
                    {dynamicScores.factors?.seasonal_context && (
                      <div className="flex items-center gap-2 text-[10px]">
                        <TreePine className="h-3 w-3 text-emerald-400" />
                        <span className="text-gray-400 flex-1">Saison</span>
                        <span className="text-emerald-300 capitalize">{dynamicScores.factors.seasonal_context.season}</span>
                      </div>
                    )}
                    {dynamicScores.factors?.calving && dynamicScores.factors.calving.active && (
                      <div className="flex items-center gap-2 text-[10px]">
                        <AlertTriangle className="h-3 w-3 text-yellow-400" />
                        <span className="text-gray-400 flex-1">Mise bas</span>
                        <span className="text-yellow-400">ACTIF</span>
                      </div>
                    )}
                  </div>

                  {/* Recommandations */}
                  {dynamicScores.recommendations?.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-purple-500/20">
                      {dynamicScores.recommendations.map((rec, i) => (
                        <div key={i} className="text-[10px] text-purple-300/80 flex items-start gap-1 mt-1">
                          <AlertTriangle className="h-3 w-3 flex-shrink-0 mt-0.5" />
                          <span>{rec}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-[10px] text-gray-500">
                  Aucune donnée dynamique disponible
                </div>
              )}
            </div>

            {/* Alertes conditions optimales */}
            <div className="bg-gray-900/80 rounded-lg border border-gray-800 p-4" data-testid="diag-alerts">
              <AlertsPanel
                alerts={alerts}
                unreadCount={unreadAlertCount}
                onMarkRead={markAlertRead}
                onMarkAllRead={markAllAlertsRead}
                onRefresh={checkOptimalConditions}
                loading={favoritesLoading}
              />
            </div>

            {/* Zones favorites */}
            <div className="bg-gray-900/80 rounded-lg border border-gray-800 p-4" data-testid="diag-favorites">
              <FavoritesList
                favorites={favorites}
                onRemove={removeFavorite}
                onUpdateAlerts={updateAlertSettings}
                onViewConditions={getZoneConditions}
              />
            </div>
          </div>
        </div>

        {/* Footer — Prêt pour ExclusionsSpatiales.v2 */}
        <div className="border-t border-gray-800 pt-4 mt-4">
          <div className="flex items-center gap-2 text-[10px] text-gray-600">
            <AlertTriangle className="h-3 w-3" />
            <span>ExclusionsSpatiales.v1 figé — V2 en préparation (exclusions dynamiques)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiagnosticExclusionsPanel;
