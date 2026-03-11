/**
 * LayersPanel - Map layers selection panel
 * Extracted from TerritoryMap.jsx for better maintainability
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Layers, Map, Trees, Droplets, Mountain, Route, Flame, MapPin, Camera, Footprints } from 'lucide-react';

// Base layer configurations
export const BASE_LAYERS = {
  carte: {
    name: 'Carte Standard',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '© OpenStreetMap contributors'
  },
  satellite: {
    name: 'Satellite',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: '© Esri, Maxar, Earthstar Geographics'
  },
  topo: {
    name: 'Topographique',
    url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attribution: '© OpenTopoMap'
  },
  terrain: {
    name: 'Terrain',
    url: 'https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg',
    attribution: '© Stamen Design'
  }
};

const LayersPanel = ({
  selectedBaseLayer,
  onBaseLayerChange,
  showHeatmap,
  onToggleHeatmap,
  showEvents,
  onToggleEvents,
  showCameras,
  onToggleCameras,
  showForestTrails,
  onToggleForestTrails,
  showForestLayer,
  onToggleForestLayer,
  showWaterLayer,
  onToggleWaterLayer,
  showReliefLayer,
  onToggleReliefLayer,
  showRoadsLayer,
  onToggleRoadsLayer,
  onClose
}) => {
  return (
    <Card className="bg-card border-border w-72">
      <CardHeader className="pb-2">
        <CardTitle className="text-white text-sm flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Layers className="h-4 w-4 text-[#f5a623]" />
            Couches de carte
          </span>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-white"
          >
            ×
          </button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Base Layer Selection */}
        <div>
          <Label className="text-xs text-gray-400 mb-2 block">Fond de carte</Label>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(BASE_LAYERS).map(([key, layer]) => (
              <button
                key={key}
                onClick={() => onBaseLayerChange(key)}
                className={`p-2 rounded-lg border text-xs transition-colors ${
                  selectedBaseLayer === key
                    ? 'border-[#f5a623] bg-[#f5a623]/10 text-[#f5a623]'
                    : 'border-border text-gray-400 hover:border-gray-600'
                }`}
              >
                <Map className="h-4 w-4 mx-auto mb-1" />
                {layer.name}
              </button>
            ))}
          </div>
        </div>

        {/* Data Layers */}
        <div>
          <Label className="text-xs text-gray-400 mb-2 block">Données</Label>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-white flex items-center gap-2">
                <Flame className="h-4 w-4 text-red-500" /> Carte de chaleur
              </span>
              <Switch
                checked={showHeatmap}
                onCheckedChange={onToggleHeatmap}
                className="data-[state=checked]:bg-[#f5a623]"
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-white flex items-center gap-2">
                <MapPin className="h-4 w-4 text-[#f5a623]" /> Événements
              </span>
              <Switch
                checked={showEvents}
                onCheckedChange={onToggleEvents}
                className="data-[state=checked]:bg-[#f5a623]"
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-white flex items-center gap-2">
                <Camera className="h-4 w-4 text-pink-500" /> Caméras
              </span>
              <Switch
                checked={showCameras}
                onCheckedChange={onToggleCameras}
                className="data-[state=checked]:bg-[#f5a623]"
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-white flex items-center gap-2">
                <Footprints className="h-4 w-4 text-emerald-500" /> Sentiers forestiers
              </span>
              <Switch
                checked={showForestTrails}
                onCheckedChange={onToggleForestTrails}
                className="data-[state=checked]:bg-[#f5a623]"
              />
            </div>
          </div>
        </div>

        {/* Environmental Layers */}
        <div>
          <Label className="text-xs text-gray-400 mb-2 block">Environnement</Label>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-white flex items-center gap-2">
                <Trees className="h-4 w-4 text-green-500" /> Forêts
              </span>
              <Switch
                checked={showForestLayer}
                onCheckedChange={onToggleForestLayer}
                className="data-[state=checked]:bg-green-500"
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-white flex items-center gap-2">
                <Droplets className="h-4 w-4 text-blue-500" /> Plans d'eau
              </span>
              <Switch
                checked={showWaterLayer}
                onCheckedChange={onToggleWaterLayer}
                className="data-[state=checked]:bg-blue-500"
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-white flex items-center gap-2">
                <Mountain className="h-4 w-4 text-amber-500" /> Relief
              </span>
              <Switch
                checked={showReliefLayer}
                onCheckedChange={onToggleReliefLayer}
                className="data-[state=checked]:bg-amber-500"
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-white flex items-center gap-2">
                <Route className="h-4 w-4 text-gray-400" /> Routes
              </span>
              <Switch
                checked={showRoadsLayer}
                onCheckedChange={onToggleRoadsLayer}
                className="data-[state=checked]:bg-gray-500"
              />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default LayersPanel;
