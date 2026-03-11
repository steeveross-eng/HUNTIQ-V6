/**
 * WildlifeTracker - Species tracking and activity display
 * BIONIC Design System compliant - No emojis
 * Phase 10 - Plan Maître Modules
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Loader2, Sunrise, Sunset } from 'lucide-react';
import { WildlifeService } from '../WildlifeService';
import { SpeciesIcon } from '../../../components/bionic/SpeciesIcon';
import { getSpeciesInfo } from '../../../config/speciesImages';

export const WildlifeTracker = ({ 
  species = 'deer',
  coordinates = null,
  showPrediction = true
}) => {
  const [speciesInfo, setSpeciesInfo] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      // Get species info
      const infoResult = await WildlifeService.getSpeciesInfo(species);
      if (infoResult?.success) {
        setSpeciesInfo(infoResult.species);
      } else {
        // Placeholder - using centralized species config
        const placeholders = WildlifeService.getPlaceholderSpecies();
        const found = placeholders.find(s => s.id === species);
        const speciesData = getSpeciesInfo(species);
        setSpeciesInfo(found || { 
          id: species, 
          name: speciesData?.name || species.charAt(0).toUpperCase() + species.slice(1),
          category: 'big_game'
        });
      }

      // Get activity prediction
      if (showPrediction && coordinates) {
        const predResult = await WildlifeService.predictActivity(species, {
          lat: coordinates.lat,
          lng: coordinates.lng
        });
        if (predResult?.success) {
          setPrediction(predResult.prediction);
        } else {
          setPrediction({
            activity_level: 'moderate',
            score: 65,
            peak_hours: ['06:00-08:00', '17:00-19:00'],
            confidence: 0.78
          });
        }
      }
    } catch (error) {
      console.error('Wildlife tracker error:', error);
    } finally {
      setLoading(false);
    }
  }, [species, coordinates, showPrediction]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const getActivityColor = (level) => {
    const colors = {
      very_high: '#10b981',
      high: '#22c55e',
      moderate: '#f59e0b',
      low: '#f97316',
      very_low: '#ef4444'
    };
    return colors[level] || '#64748b';
  };

  return (
    <Card className="bg-gradient-to-br from-green-900/20 to-slate-900 border-green-700/50">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center justify-between">
          <span className="flex items-center gap-2">
            <SpeciesIcon species={species} size="lg" rounded />
            Suivi {speciesInfo?.name || species}
          </span>
          <Badge className="bg-green-900/50 text-green-400">
            Wildlife Engine
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-6">
            <Loader2 className="w-8 h-8 animate-spin text-green-400 mx-auto" />
            <p className="text-slate-400 text-sm mt-2">Chargement...</p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Activity Level */}
            {prediction && (
              <div className="bg-slate-800/50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-slate-300 text-sm">Niveau d'activité</span>
                  <Badge 
                    style={{ 
                      backgroundColor: `${getActivityColor(prediction.activity_level)}20`,
                      color: getActivityColor(prediction.activity_level)
                    }}
                  >
                    {prediction.activity_level?.replace('_', ' ') || 'N/A'}
                  </Badge>
                </div>
                
                {/* Score Bar */}
                <div className="mb-3">
                  <div className="flex justify-between text-xs text-slate-400 mb-1">
                    <span>Score d'activité</span>
                    <span>{prediction.score || 0}%</span>
                  </div>
                  <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div 
                      className="h-full rounded-full transition-all"
                      style={{ 
                        width: `${prediction.score || 0}%`,
                        backgroundColor: getActivityColor(prediction.activity_level)
                      }}
                    />
                  </div>
                </div>

                {/* Peak Hours */}
                {prediction.peak_hours && (
                  <div>
                    <span className="text-slate-400 text-xs">Heures de pointe</span>
                    <div className="flex gap-2 mt-1">
                      {prediction.peak_hours.map((hour, i) => (
                        <Badge key={i} className="bg-slate-700 text-slate-300">
                          {hour}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Species Quick Info */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-slate-800/50 rounded-lg p-3 text-center">
                <Sunrise className="h-6 w-6 text-amber-400 mx-auto mb-1" />
                <div className="text-xs text-slate-400">Aube</div>
                <div className="text-emerald-400 font-medium">Actif</div>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-3 text-center">
                <Sunset className="h-6 w-6 text-orange-400 mx-auto mb-1" />
                <div className="text-xs text-slate-400">Crépuscule</div>
                <div className="text-emerald-400 font-medium">Très actif</div>
              </div>
            </div>

            <Button 
              className="w-full bg-green-600 hover:bg-green-700 text-white"
              onClick={loadData}
            >
              Actualiser la prédiction
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default WildlifeTracker;
