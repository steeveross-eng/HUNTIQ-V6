/**
 * PredictiveWidget - Hunting success prediction display
 * Phase 10 - Plan Maître Modules
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Button } from '../../../components/ui/button';
import { PredictiveService } from '../PredictiveService';
import { Sparkles, Lightbulb, Loader2, TrendingUp, TrendingDown, ArrowRight } from 'lucide-react';

export const PredictiveWidget = ({ 
  species = 'deer',
  coordinates = null,
  weather = null,
  compact = false
}) => {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadPrediction = useCallback(async () => {
    setLoading(true);
    try {
      const result = await PredictiveService.predictHuntingSuccess({
        species,
        lat: coordinates?.lat,
        lng: coordinates?.lng,
        weather
      });
      
      if (result.success && result.prediction) {
        setPrediction(result.prediction);
      } else {
        setPrediction(PredictiveService.getPlaceholderPrediction());
      }
    } catch (error) {
      console.error('Prediction error:', error);
      setPrediction(PredictiveService.getPlaceholderPrediction());
    } finally {
      setLoading(false);
    }
  }, [species, coordinates, weather]);

  useEffect(() => {
    loadPrediction();
  }, [loadPrediction]);

  const getProbabilityColor = (prob) => {
    if (prob >= 80) return '#10b981';
    if (prob >= 60) return '#22c55e';
    if (prob >= 40) return '#f59e0b';
    return '#ef4444';
  };

  const getImpactIcon = (impact) => {
    const icons = {
      very_positive: TrendingUp,
      positive: TrendingUp,
      neutral: ArrowRight,
      negative: TrendingDown,
      very_negative: TrendingDown
    };
    return icons[impact] || ArrowRight;
  };

  const getImpactColor = (impact) => {
    const colors = {
      very_positive: 'text-emerald-400',
      positive: 'text-green-400',
      neutral: 'text-slate-400',
      negative: 'text-orange-400',
      very_negative: 'text-red-400'
    };
    return colors[impact] || 'text-slate-400';
  };

  if (compact && prediction) {
    return (
      <div className="bg-gradient-to-r from-blue-900/30 to-slate-900 rounded-lg p-4 border border-blue-700/50">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-xs">Probabilité de succès</p>
            <p 
              className="text-2xl font-bold"
              style={{ color: getProbabilityColor(prediction.success_probability) }}
            >
              {prediction.success_probability}%
            </p>
          </div>
          <div className="text-right">
            <Badge className="bg-blue-900/50 text-blue-400">
              {Math.round(prediction.confidence * 100)}% confiance
            </Badge>
          </div>
        </div>
      </div>
    );
  }

  return (
    <Card className="bg-gradient-to-br from-blue-900/20 to-slate-900 border-blue-700/50">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-blue-400" />
            Prédiction de Succès
          </span>
          <Badge className="bg-blue-900/50 text-blue-400">
            Predictive Engine
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-6">
            <Loader2 className="h-8 w-8 animate-spin text-blue-400 mx-auto" />
            <p className="text-slate-400 text-sm mt-2">Analyse prédictive...</p>
          </div>
        ) : prediction ? (
          <div className="space-y-4">
            {/* Main Score */}
            <div className="text-center py-4 bg-slate-800/50 rounded-lg">
              <p className="text-slate-400 text-sm mb-2">Probabilité de succès</p>
              <p 
                className="text-5xl font-bold"
                style={{ color: getProbabilityColor(prediction.success_probability) }}
              >
                {prediction.success_probability}%
              </p>
              <Badge className="mt-2 bg-slate-700 text-slate-300">
                Confiance: {Math.round(prediction.confidence * 100)}%
              </Badge>
            </div>

            {/* Factors */}
            <div>
              <p className="text-slate-400 text-sm mb-2">Facteurs d'influence</p>
              <div className="space-y-2">
                {prediction.factors?.slice(0, 5).map((factor, index) => {
                  const ImpactIcon = getImpactIcon(factor.impact);
                  return (
                    <div key={index} className="flex items-center justify-between text-sm">
                      <span className="text-slate-300">{factor.name}</span>
                      <span className="flex items-center gap-2">
                        <ImpactIcon className={`h-4 w-4 ${getImpactColor(factor.impact)}`} />
                        <Badge 
                          className="text-xs"
                          style={{ 
                            backgroundColor: `${getProbabilityColor(factor.score)}20`,
                            color: getProbabilityColor(factor.score)
                          }}
                        >
                          {factor.score}
                        </Badge>
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Optimal Times */}
            {prediction.optimal_times && (
              <div>
                <p className="text-slate-400 text-sm mb-2">Périodes optimales</p>
                <div className="grid grid-cols-3 gap-2">
                  {prediction.optimal_times.map((time, index) => (
                    <div 
                      key={index}
                      className="bg-slate-800/50 rounded-lg p-2 text-center"
                    >
                      <div className="text-xs text-slate-400">{time.period}</div>
                      <div className="text-white text-sm font-medium">{time.time}</div>
                      <Badge 
                        className="text-xs mt-1"
                        style={{ 
                          backgroundColor: `${getProbabilityColor(time.score)}20`,
                          color: getProbabilityColor(time.score)
                        }}
                      >
                        {time.score}%
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendation */}
            {prediction.recommendation && (
              <div className="bg-emerald-900/20 border border-emerald-700/50 rounded-lg p-3">
                <p className="text-emerald-400 text-sm flex items-center gap-2">
                  <Lightbulb className="h-4 w-4" />
                  {prediction.recommendation}
                </p>
              </div>
            )}

            <Button 
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              onClick={loadPrediction}
            >
              Actualiser la prédiction
            </Button>
          </div>
        ) : (
          <div className="text-center py-8">
            <Sparkles className="h-10 w-10 text-blue-400 mx-auto" />
            <p className="text-slate-400 mt-2">Aucune prédiction disponible</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PredictiveWidget;
