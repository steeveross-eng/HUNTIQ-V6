/**
 * GPSNavigationPanel - GPS coordinate input and analysis panel
 * Extracted from TerritoryMap.jsx for better maintainability
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { MapPin, Activity, X, Locate, Target, Loader2 } from 'lucide-react';

const GPSNavigationPanel = ({
  // GPS Flow Mode
  gpsFlowMode,
  onDeactivateGpsFlowMode,
  
  // Format
  gpsFormat,
  onGpsFormatChange,
  
  // Decimal coordinates
  gpsLatitude,
  gpsLongitude,
  onLatitudeChange,
  onLongitudeChange,
  
  // DMS coordinates
  dmsLatDeg, dmsLatMin, dmsLatSec, dmsLatDir,
  dmsLonDeg, dmsLonMin, dmsLonSec, dmsLonDir,
  onDmsLatDegChange, onDmsLatMinChange, onDmsLatSecChange, onDmsLatDirChange,
  onDmsLonDegChange, onDmsLonMinChange, onDmsLonSecChange, onDmsLonDirChange,
  
  // Actions
  onLocateMe,
  onGoToCoords,
  onAnalyzeGps,
  loading,
  locatingMe
}) => {
  return (
    <Card className={`bg-background border-border mb-4 transition-all ${gpsFlowMode ? 'border-green-500 shadow-lg shadow-green-500/20' : ''}`}>
      <CardHeader className="pb-2">
        <CardTitle className="text-white text-sm flex items-center gap-2">
          <MapPin className="h-4 w-4 text-[#f5a623]" />
          Analyse GPS
          {gpsFlowMode && (
            <Badge className="ml-auto bg-green-500/20 text-green-400 text-[9px] animate-pulse flex items-center gap-1">
              <Activity className="h-3 w-3" />
              FLUX EN DIRECT
            </Badge>
          )}
        </CardTitle>
        <CardDescription className="text-xs">
          {gpsFlowMode 
            ? '🛰️ Coordonnées mises à jour en temps réel depuis la carte'
            : 'Entrez les coordonnées pour analyser un territoire spécifique'
          }
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* GPS Flow Mode Indicator */}
        {gpsFlowMode && (
          <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-2 mb-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="relative">
                  <div className="w-2 h-2 rounded-full bg-green-500"></div>
                  <div className="absolute inset-0 w-2 h-2 rounded-full bg-green-500 animate-ping"></div>
                </div>
                <span className="text-green-400 text-xs font-medium">Mode flux dynamique actif</span>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                className="h-6 px-2 text-xs text-red-400 hover:bg-red-500/10"
                onClick={onDeactivateGpsFlowMode}
              >
                <X className="h-3 w-3 mr-1" />
                Arrêter
              </Button>
            </div>
          </div>
        )}
        
        {/* Format Selection */}
        <div>
          <Label className="text-gray-400 text-xs">Format des coordonnées</Label>
          <Select value={gpsFormat} onValueChange={onGpsFormatChange}>
            <SelectTrigger className="bg-card border-border mt-1" data-testid="gps-format-select">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="decimal">Décimal (ex: 48.2019, -68.3844)</SelectItem>
              <SelectItem value="dms">DMS (ex: 48°12'07"N 68°23'04"W)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Decimal Format Inputs */}
        {gpsFormat === 'decimal' && (
          <div className="grid grid-cols-2 gap-2">
            <div>
              <Label className={`text-xs ${gpsFlowMode ? 'text-green-400' : 'text-gray-400'}`}>Latitude</Label>
              <Input
                type="number"
                step="0.0001"
                value={gpsLatitude}
                onChange={(e) => onLatitudeChange(e.target.value)}
                className={`bg-card border-border mt-1 text-sm transition-all ${gpsFlowMode ? 'border-green-500 text-green-400 font-mono' : ''}`}
                placeholder="48.2019"
                data-testid="gps-lat-decimal"
                readOnly={gpsFlowMode}
              />
            </div>
            <div>
              <Label className="text-gray-400 text-xs">Longitude</Label>
              <Input
                type="number"
                step="0.0001"
                value={gpsLongitude}
                onChange={(e) => onLongitudeChange(e.target.value)}
                className={`bg-card border-border mt-1 text-sm transition-all ${gpsFlowMode ? 'border-green-500 text-green-400 font-mono' : ''}`}
                placeholder="-68.3844"
                data-testid="gps-lon-decimal"
                readOnly={gpsFlowMode}
              />
            </div>
          </div>
        )}

        {/* DMS Format Inputs */}
        {gpsFormat === 'dms' && (
          <div className="space-y-3">
            {/* Latitude DMS */}
            <div>
              <Label className="text-gray-400 text-xs mb-1 block">Latitude</Label>
              <div className="flex gap-1 items-center flex-wrap">
                <Input
                  type="number"
                  min="0"
                  max="90"
                  value={dmsLatDeg}
                  onChange={(e) => onDmsLatDegChange(e.target.value)}
                  className="bg-card border-border text-sm w-14 text-center"
                  placeholder="48"
                  data-testid="gps-lat-deg"
                />
                <span className="text-gray-400 text-sm font-bold">°</span>
                <Input
                  type="number"
                  min="0"
                  max="59"
                  value={dmsLatMin}
                  onChange={(e) => onDmsLatMinChange(e.target.value)}
                  className="bg-card border-border text-sm w-14 text-center"
                  placeholder="12"
                  data-testid="gps-lat-min"
                />
                <span className="text-gray-400 text-sm font-bold">'</span>
                <Input
                  type="number"
                  min="0"
                  max="59.99"
                  step="0.01"
                  value={dmsLatSec}
                  onChange={(e) => onDmsLatSecChange(e.target.value)}
                  className="bg-card border-border text-sm w-14 text-center"
                  placeholder="07"
                  data-testid="gps-lat-sec"
                />
                <span className="text-gray-400 text-sm font-bold">"</span>
                <Select value={dmsLatDir} onValueChange={onDmsLatDirChange}>
                  <SelectTrigger className="bg-card border-border w-14" data-testid="gps-lat-dir">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="N">N</SelectItem>
                    <SelectItem value="S">S</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            {/* Longitude DMS */}
            <div>
              <Label className="text-gray-400 text-xs mb-1 block">Longitude</Label>
              <div className="flex gap-1 items-center flex-wrap">
                <Input
                  type="number"
                  min="0"
                  max="180"
                  value={dmsLonDeg}
                  onChange={(e) => onDmsLonDegChange(e.target.value)}
                  className="bg-card border-border text-sm w-14 text-center"
                  placeholder="68"
                  data-testid="gps-lon-deg"
                />
                <span className="text-gray-400 text-sm font-bold">°</span>
                <Input
                  type="number"
                  min="0"
                  max="59"
                  value={dmsLonMin}
                  onChange={(e) => onDmsLonMinChange(e.target.value)}
                  className="bg-card border-border text-sm w-14 text-center"
                  placeholder="23"
                  data-testid="gps-lon-min"
                />
                <span className="text-gray-400 text-sm font-bold">'</span>
                <Input
                  type="number"
                  min="0"
                  max="59.99"
                  step="0.01"
                  value={dmsLonSec}
                  onChange={(e) => onDmsLonSecChange(e.target.value)}
                  className="bg-card border-border text-sm w-14 text-center"
                  placeholder="04"
                  data-testid="gps-lon-sec"
                />
                <span className="text-gray-400 text-sm font-bold">"</span>
                <Select value={dmsLonDir} onValueChange={onDmsLonDirChange}>
                  <SelectTrigger className="bg-card border-border w-14" data-testid="gps-lon-dir">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="W">W</SelectItem>
                    <SelectItem value="E">E</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2 pt-2">
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={onLocateMe}
            disabled={locatingMe}
          >
            {locatingMe ? (
              <Loader2 className="h-3 w-3 mr-1 animate-spin" />
            ) : (
              <Locate className="h-3 w-3 mr-1" />
            )}
            Ma position
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={onGoToCoords}
            disabled={!gpsLatitude || !gpsLongitude}
          >
            <Target className="h-3 w-3 mr-1" />
            Aller
          </Button>
        </div>

        <Button
          onClick={onAnalyzeGps}
          disabled={loading || (!gpsLatitude || !gpsLongitude)}
          className="w-full bg-[#f5a623] hover:bg-[#d4891c] text-black"
          size="sm"
        >
          {loading ? (
            <><Loader2 className="h-3 w-3 mr-1 animate-spin" /> Analyse...</>
          ) : (
            <><Target className="h-3 w-3 mr-1" /> Analyser ce point GPS</>
          )}
        </Button>
      </CardContent>
    </Card>
  );
};

export default GPSNavigationPanel;
