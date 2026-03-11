/**
 * AnalysisResultsPanel - Display territory and GPS analysis results
 * Extracted from TerritoryMap.jsx for better maintainability
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  TrendingUp, 
  TreePine, 
  Droplets, 
  Mountain, 
  Activity, 
  X,
  Target,
  MapPin
} from 'lucide-react';
import { SpeciesIcon } from '@/components/bionic/SpeciesIcon';

// Species configuration for display - BIONIC Design System Compliant
const SPECIES_DISPLAY = {
  orignal: { species: 'moose', label: 'Orignal', color: 'text-amber-500' },
  chevreuil: { species: 'deer', label: 'Chevreuil', color: 'text-orange-500' },
  ours: { species: 'bear', label: 'Ours', color: 'text-gray-500' }
};

const AnalysisResultsPanel = ({ 
  territoryAnalysis, 
  gpsAnalysis, 
  onClearTerritory, 
  onClearGps 
}) => {
  if (!territoryAnalysis && !gpsAnalysis) return null;

  return (
    <Card className="bg-background border-border mb-4">
      <CardHeader className="pb-2">
        <CardTitle className="text-white text-sm flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-[#f5a623]" />
          Résultats d'Analyse
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Territory Analysis Results */}
        {territoryAnalysis && (
          <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Badge className="bg-green-500/20 text-green-400 text-xs">
                  {territoryAnalysis.type?.toUpperCase()}
                </Badge>
                <span className="text-white text-sm font-medium">
                  {territoryAnalysis.name || territoryAnalysis.zone}
                </span>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                className="h-6 px-2 text-red-400"
                onClick={onClearTerritory}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
            
            {/* Probability scores */}
            {territoryAnalysis.probability && (
              <div className="space-y-2 mt-3">
                <p className="text-gray-400 text-xs">Probabilités de présence :</p>
                {Object.entries(territoryAnalysis.probability).map(([species, prob]) => {
                  const speciesInfo = SPECIES_DISPLAY[species];
                  if (!speciesInfo) return null;
                  const percentage = Math.round(prob * 100);
                  return (
                    <div key={species} className="flex items-center gap-2">
                      <SpeciesIcon species={speciesInfo.species} size="xs" />
                      <span className="text-gray-300 text-xs flex-1">{speciesInfo.label}</span>
                      <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div 
                          className={`h-full bg-gradient-to-r from-green-500 to-green-400 transition-all`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                      <span className={`text-xs font-medium ${speciesInfo.color}`}>
                        {percentage}%
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
            
            {/* Territory characteristics */}
            {territoryAnalysis.characteristics && (
              <div className="grid grid-cols-3 gap-2 mt-3">
                <div className="bg-background rounded p-2 text-center">
                  <TreePine className="h-4 w-4 text-green-500 mx-auto mb-1" />
                  <p className="text-[10px] text-gray-400">Forêt</p>
                  <p className="text-xs text-white font-medium">
                    {territoryAnalysis.characteristics.forest || 'N/A'}%
                  </p>
                </div>
                <div className="bg-background rounded p-2 text-center">
                  <Droplets className="h-4 w-4 text-blue-500 mx-auto mb-1" />
                  <p className="text-[10px] text-gray-400">Eau</p>
                  <p className="text-xs text-white font-medium">
                    {territoryAnalysis.characteristics.water || 'N/A'}%
                  </p>
                </div>
                <div className="bg-background rounded p-2 text-center">
                  <Mountain className="h-4 w-4 text-gray-500 mx-auto mb-1" />
                  <p className="text-[10px] text-gray-400">Élévation</p>
                  <p className="text-xs text-white font-medium">
                    {territoryAnalysis.characteristics.elevation || 'N/A'}m
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* GPS Analysis Results */}
        {gpsAnalysis && (
          <div className="bg-[#f5a623]/10 border border-[#f5a623]/30 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Target className="h-4 w-4 text-[#f5a623]" />
                <span className="text-white text-sm font-medium">
                  Point GPS analysé
                </span>
              </div>
              <Button 
                variant="ghost" 
                size="sm" 
                className="h-6 px-2 text-red-400"
                onClick={onClearGps}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
            
            <div className="text-xs text-gray-400 mb-2 flex items-center gap-1">
              <MapPin className="h-3 w-3" /> {gpsAnalysis.lat?.toFixed(4)}, {gpsAnalysis.lng?.toFixed(4)}
            </div>
            
            {/* GPS Point Analysis */}
            {gpsAnalysis.analysis && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 text-xs">Score habitat</span>
                  <Badge className={`text-xs ${
                    gpsAnalysis.analysis.habitatScore > 70 ? 'bg-green-500/20 text-green-400' :
                    gpsAnalysis.analysis.habitatScore > 40 ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {gpsAnalysis.analysis.habitatScore || 0}/100
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 text-xs">Activité récente</span>
                  <Badge className="bg-blue-500/20 text-blue-400 text-xs">
                    <Activity className="h-3 w-3 mr-1" />
                    {gpsAnalysis.analysis.recentActivity || 'Modérée'}
                  </Badge>
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default AnalysisResultsPanel;
