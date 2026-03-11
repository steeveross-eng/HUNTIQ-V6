/**
 * HabitatAnalysis - Ecoforestry habitat analysis display
 * Phase 10 - Plan Maître Modules
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { EcoforestryService } from '../EcoforestryService';
import { TreePine, Loader2, Leaf, Trees, Droplets, Mountain } from 'lucide-react';

const HABITAT_ICONS = {
  food: Leaf,
  cover: Trees,
  water: Droplets,
  terrain: Mountain
};

const HABITAT_LABELS = {
  food: 'Nourriture',
  cover: 'Couvert',
  water: 'Eau',
  terrain: 'Terrain'
};

export const HabitatAnalysis = ({ 
  coordinates = null,
  species = 'deer'
}) => {
  const [forestData, setForestData] = useState(null);
  const [habitatScore, setHabitatScore] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      if (coordinates) {
        const forestResult = await EcoforestryService.getForestData(
          coordinates.lat, 
          coordinates.lng, 
          5
        );
        const habitatResult = await EcoforestryService.getHabitatAnalysis(
          coordinates.lat,
          coordinates.lng,
          species
        );

        if (forestResult.success && forestResult.data) {
          setForestData(forestResult.data);
        } else {
          setForestData(EcoforestryService.getPlaceholderForestData());
        }

        if (habitatResult.success && habitatResult.analysis) {
          setHabitatScore(habitatResult.analysis);
        } else {
          setHabitatScore(EcoforestryService.getPlaceholderHabitatScore());
        }
      } else {
        setForestData(EcoforestryService.getPlaceholderForestData());
        setHabitatScore(EcoforestryService.getPlaceholderHabitatScore());
      }
    } catch (error) {
      console.error('Habitat analysis error:', error);
      setForestData(EcoforestryService.getPlaceholderForestData());
      setHabitatScore(EcoforestryService.getPlaceholderHabitatScore());
    } finally {
      setLoading(false);
    }
  }, [coordinates, species]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#22c55e';
    if (score >= 40) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <Card className="bg-gradient-to-br from-green-900/20 to-slate-900 border-green-700/50">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center justify-between">
          <span className="flex items-center gap-2">
            <TreePine className="h-6 w-6 text-green-400" />
            Analyse Habitat
          </span>
          <Badge className="bg-green-900/50 text-green-400">
            Ecoforestry
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-6">
            <Loader2 className="h-8 w-8 animate-spin text-green-400 mx-auto" />
            <p className="text-slate-400 text-sm mt-2">Analyse en cours...</p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Overall Score */}
            {habitatScore && (
              <div className="text-center py-4 bg-slate-800/50 rounded-lg">
                <p className="text-slate-400 text-sm mb-2">Score Habitat Global</p>
                <p 
                  className="text-4xl font-bold"
                  style={{ color: getScoreColor(habitatScore.overall) }}
                >
                  {habitatScore.overall}
                </p>
              </div>
            )}

            {/* Score Breakdown */}
            {habitatScore && (
              <div className="grid grid-cols-2 gap-2">
                {['food', 'cover', 'water', 'terrain'].map(key => {
                  const IconComponent = HABITAT_ICONS[key];
                  return (
                    <div key={key} className="bg-slate-800/50 rounded-lg p-3">
                      <div className="flex items-center gap-2 mb-1">
                        <IconComponent className="h-4 w-4 text-slate-400" />
                        <span className="text-slate-400 text-xs">{HABITAT_LABELS[key]}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                          <div 
                            className="h-full rounded-full"
                            style={{ 
                              width: `${habitatScore[key]}%`,
                              backgroundColor: getScoreColor(habitatScore[key])
                            }}
                          />
                        </div>
                        <span 
                          className="text-sm font-medium"
                          style={{ color: getScoreColor(habitatScore[key]) }}
                        >
                          {habitatScore[key]}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Forest Info */}
            {forestData && (
              <div className="bg-slate-800/50 rounded-lg p-3">
                <p className="text-slate-400 text-xs mb-2">Caractéristiques forestières</p>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Type</span>
                    <span className="text-white">{forestData.forest_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Classe d'âge</span>
                    <span className="text-white">{forestData.age_class}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Couvert</span>
                    <span className="text-white">{forestData.canopy_cover}%</span>
                  </div>
                  {forestData.water_proximity && (
                    <div className="flex justify-between">
                      <span className="text-slate-400">Eau</span>
                      <span className="text-emerald-400">{forestData.water_proximity}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Dominant Species */}
            {forestData?.dominant_species && (
              <div>
                <p className="text-slate-400 text-xs mb-2">Espèces dominantes</p>
                <div className="flex flex-wrap gap-1">
                  {forestData.dominant_species.map((sp, i) => (
                    <Badge key={i} className="bg-green-900/30 text-green-400 text-xs">
                      {sp}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            <Button 
              className="w-full bg-green-600 hover:bg-green-700 text-white"
              onClick={loadData}
            >
              Actualiser l'analyse
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default HabitatAnalysis;
