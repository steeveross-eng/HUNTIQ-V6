/**
 * GuidedRoutePanel.jsx — Guided Route Details Sidebar Panel
 * 
 * Displays route statistics, highest probability zone, waypoint list,
 * and footer actions (hide/clear). 
 * 
 * Phase 2 extraction from TerritoryMap.jsx
 * @module territory/GuidedRoutePanel
 */

import React from 'react';
import { Navigation, ArrowRight, X, EyeOff, Trash2 } from 'lucide-react';
import { Button } from '../ui/button';

const GuidedRoutePanel = ({
  route,
  show,
  selectedAnalysisSpecies,
  onClose,
  onClear,
  onNavigateToPoint,
}) => {
  if (!route || !show) return null;

  return (
    <div
      className="absolute top-4 left-4 z-[700] bg-black/95 backdrop-blur-sm rounded-xl shadow-2xl border border-green-500/30 w-[340px] max-h-[70vh] overflow-hidden"
      style={{ marginLeft: '0' }}
      data-testid="guided-route-panel"
    >
      {/* Header */}
      <div className="p-3 bg-gradient-to-r from-green-600/20 to-emerald-600/20 border-b border-green-500/30">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-green-500/20 rounded-lg">
              <Navigation className="h-5 w-5 text-green-400" />
            </div>
            <div>
              <h3 className="text-white font-bold text-sm">Parcours Guide</h3>
              <p className="text-green-400 text-[10px] font-medium">{selectedAnalysisSpecies.toUpperCase()}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-gray-400 hover:text-white"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="p-2 grid grid-cols-3 gap-2 border-b border-gray-800">
        <div className="text-center p-1.5 bg-gray-900 rounded-lg">
          <div className="text-green-400 text-lg font-bold">{route.total_distance_km}</div>
          <div className="text-gray-500 text-[9px]">km</div>
        </div>
        <div className="text-center p-1.5 bg-gray-900 rounded-lg">
          <div className="text-yellow-400 text-lg font-bold">{route.estimated_time_hours}h</div>
          <div className="text-gray-500 text-[9px]">estimation</div>
        </div>
        <div className="text-center p-1.5 bg-gray-900 rounded-lg">
          <div className="text-blue-400 text-lg font-bold">{Math.round(route.average_probability)}%</div>
          <div className="text-gray-500 text-[9px]">prob. moy.</div>
        </div>
      </div>

      {/* Highest Probability Zone */}
      {route.highest_probability_zone && (
        <div className="p-2 bg-gradient-to-r from-green-500/5 to-transparent border-b border-gray-800">
          <div className="text-[9px] text-gray-500 uppercase tracking-wider mb-1">Meilleure zone</div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-green-500/20 flex items-center justify-center">
              <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
            </div>
            <div className="flex-1">
              <div className="text-white text-sm font-medium">{route.highest_probability_zone.name}</div>
            </div>
            <div className="text-right">
              <div className="text-green-400 text-xl font-bold">{route.highest_probability_zone.probability}%</div>
            </div>
          </div>
          {route.highest_probability_zone.factors?.length > 0 && (
            <div className="mt-1.5 flex flex-wrap gap-1">
              {route.highest_probability_zone.factors.slice(0, 3).map((factor, idx) => (
                <span key={idx} className="text-[9px] bg-green-500/20 text-green-300 px-1.5 py-0.5 rounded">
                  {factor}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Route Points List */}
      <div className="p-2 max-h-[calc(70vh-240px)] overflow-y-auto">
        <div className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">
          Itineraire ({route.waypoint_order.length} points)
        </div>
        <div className="space-y-1">
          {route.waypoint_order.map((point, idx) => (
            <button
              key={point.id}
              onClick={() => onNavigateToPoint(point)}
              className="w-full p-2 bg-card/50 hover:bg-card rounded-lg border border-border/50 hover:border-green-500/30 transition-all text-left group"
              data-testid={`guided-route-point-${idx}`}
            >
              <div className="flex items-center gap-2">
                <div
                  className="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
                  style={{ backgroundColor: point.color }}
                >
                  {idx + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-white text-sm font-medium truncate">{point.name}</div>
                  <div className="text-gray-500 text-[10px]">
                    {point.lat.toFixed(4)}, {point.lng.toFixed(4)}
                  </div>
                </div>
                <div
                  className="px-2 py-1 rounded-lg text-white text-xs font-bold"
                  style={{ backgroundColor: point.color }}
                >
                  {point.probability}%
                </div>
              </div>
              {idx < route.segments.length && (
                <div className="mt-1.5 flex items-center gap-2 text-[10px] text-gray-500">
                  <ArrowRight className="h-3 w-3" />
                  <span>{route.segments[idx].distance_km} km vers suivant</span>
                  {route.segments[idx].probability_level === 'high' && (
                    <span className="text-green-400">Zone favorable</span>
                  )}
                </div>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="p-2 border-t border-green-500/20 bg-black/50">
        <p className="text-[10px] text-gray-400 mb-2 text-center">{route.summary}</p>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            className="flex-1 text-xs"
            onClick={onClose}
          >
            <EyeOff className="h-3 w-3 mr-1" />
            Masquer
          </Button>
          <Button
            size="sm"
            className="flex-1 bg-red-500/80 hover:bg-red-600 text-white text-xs"
            onClick={onClear}
          >
            <Trash2 className="h-3 w-3 mr-1" />
            Effacer
          </Button>
        </div>
      </div>
    </div>
  );
};

export default GuidedRoutePanel;
