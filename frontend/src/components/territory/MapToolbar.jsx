/**
 * MapToolbar - Map tools (pin, route, measure)
 * Extracted from TerritoryMap.jsx for better maintainability
 */

import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { MapPin, Route, Ruler, Layers, Navigation, Upload, Download, Play, Square, Trash2 } from 'lucide-react';

const MapToolbar = ({
  activeTool,
  onToolChange,
  onToggleLayers,
  onUpload,
  onExport,
  isTracking,
  onStartTracking,
  onStopTracking,
  routePoints,
  measurePoints,
  totalDistance,
  onClearRoute,
  onClearMeasure,
  uploading
}) => {
  return (
    <div className="absolute top-4 left-4 z-[1000] flex flex-col gap-2">
      <TooltipProvider>
        {/* Main Tools */}
        <div className="bg-card border border-border rounded-lg p-1 flex flex-col gap-1">
          {/* Pin Tool */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                size="icon"
                variant={activeTool === 'pin' ? 'default' : 'ghost'}
                className={activeTool === 'pin' ? 'bg-[#f5a623] text-black' : 'text-white'}
                onClick={() => onToolChange(activeTool === 'pin' ? null : 'pin')}
              >
                <MapPin className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">
              <p>Ajouter un waypoint</p>
            </TooltipContent>
          </Tooltip>

          {/* Route Tool */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                size="icon"
                variant={activeTool === 'route' ? 'default' : 'ghost'}
                className={activeTool === 'route' ? 'bg-blue-500 text-white' : 'text-white'}
                onClick={() => onToolChange(activeTool === 'route' ? null : 'route')}
              >
                <Route className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">
              <p>Tracer un itinéraire</p>
              {routePoints.length > 0 && (
                <p className="text-xs text-gray-400">{routePoints.length} points</p>
              )}
            </TooltipContent>
          </Tooltip>

          {/* Measure Tool */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                size="icon"
                variant={activeTool === 'measure' ? 'default' : 'ghost'}
                className={activeTool === 'measure' ? 'bg-green-500 text-white' : 'text-white'}
                onClick={() => onToolChange(activeTool === 'measure' ? null : 'measure')}
              >
                <Ruler className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">
              <p>Mesurer une distance</p>
              {measurePoints.length > 1 && totalDistance && (
                <p className="text-xs text-gray-400">{totalDistance}</p>
              )}
            </TooltipContent>
          </Tooltip>

          {/* Layers */}
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                size="icon"
                variant="ghost"
                className="text-white"
                onClick={onToggleLayers}
              >
                <Layers className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">
              <p>Couches de carte</p>
            </TooltipContent>
          </Tooltip>
        </div>

        {/* GPS Tracking */}
        <div className="bg-card border border-border rounded-lg p-1 flex flex-col gap-1">
          {!isTracking ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  size="icon"
                  variant="ghost"
                  className="text-green-400 hover:bg-green-500/20"
                  onClick={onStartTracking}
                >
                  <Play className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>Démarrer le suivi GPS</p>
              </TooltipContent>
            </Tooltip>
          ) : (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  size="icon"
                  variant="ghost"
                  className="text-red-400 hover:bg-red-500/20 animate-pulse"
                  onClick={onStopTracking}
                >
                  <Square className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right">
                <p>Arrêter le suivi</p>
              </TooltipContent>
            </Tooltip>
          )}

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                size="icon"
                variant="ghost"
                className="text-white"
                onClick={onExport}
              >
                <Download className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">
              <p>Exporter GPX</p>
            </TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                size="icon"
                variant="ghost"
                className="text-white"
                onClick={onUpload}
                disabled={uploading}
              >
                <Upload className={`h-4 w-4 ${uploading ? 'animate-spin' : ''}`} />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="right">
              <p>Importer GPX</p>
            </TooltipContent>
          </Tooltip>
        </div>

        {/* Clear buttons when tools active */}
        {(routePoints.length > 0 || measurePoints.length > 0) && (
          <div className="bg-card border border-border rounded-lg p-1">
            {routePoints.length > 0 && (
              <Button
                size="sm"
                variant="ghost"
                className="text-red-400 hover:bg-red-500/20 w-full justify-start"
                onClick={onClearRoute}
              >
                <Trash2 className="h-3 w-3 mr-1" />
                Effacer route
              </Button>
            )}
            {measurePoints.length > 0 && (
              <Button
                size="sm"
                variant="ghost"
                className="text-red-400 hover:bg-red-500/20 w-full justify-start"
                onClick={onClearMeasure}
              >
                <Trash2 className="h-3 w-3 mr-1" />
                Effacer mesure
              </Button>
            )}
          </div>
        )}
      </TooltipProvider>
    </div>
  );
};

export default MapToolbar;
