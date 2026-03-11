/**
 * NutritionAnalyzer - Main nutrition analysis component
 */
import React, { useState, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { NutritionService } from '../NutritionService';
import { NutritionScore } from './NutritionScore';
import { FlaskConical, Microscope, Lightbulb, Loader2 } from 'lucide-react';

export const NutritionAnalyzer = ({ productId, productName, onAnalysisComplete }) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = useCallback(async () => {
    if (!productId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await NutritionService.analyzeProduct(productId);
      setAnalysis(result);
      onAnalysisComplete?.(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [productId, onAnalysisComplete]);

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center gap-2">
          <FlaskConical className="h-6 w-6 text-emerald-400" />
          Analyse Nutritionnelle
        </CardTitle>
      </CardHeader>
      <CardContent>
        {productName && (
          <p className="text-slate-400 text-sm mb-4">
            Produit: <span className="text-white font-medium">{productName}</span>
          </p>
        )}

        {!analysis ? (
          <Button
            onClick={handleAnalyze}
            disabled={loading || !productId}
            className="w-full bg-emerald-600 hover:bg-emerald-500"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Analyse en cours...
              </>
            ) : (
              <>
                <Microscope className="h-4 w-4 mr-2" />
                Analyser la composition
              </>
            )}
          </Button>
        ) : (
          <div className="space-y-4">
            <NutritionScore score={analysis.score} />
            
            {analysis.nutrients && (
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(analysis.nutrients).map(([nutrient, value]) => (
                  <div 
                    key={nutrient}
                    className="bg-slate-700/50 rounded-lg p-2 text-center"
                  >
                    <div className="text-xs text-slate-400 capitalize">
                      {nutrient.replace(/_/g, ' ')}
                    </div>
                    <div className="text-lg font-bold text-emerald-400">
                      {typeof value === 'number' ? value.toFixed(1) : value}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {analysis.recommendations && (
              <div className="mt-4 p-3 bg-blue-900/30 rounded-lg border border-blue-700">
                <h4 className="text-blue-400 font-medium text-sm mb-2 flex items-center gap-2">
                  <Lightbulb className="h-4 w-4" /> Recommandations
                </h4>
                <p className="text-slate-300 text-sm">
                  {analysis.recommendations}
                </p>
              </div>
            )}

            <Button
              variant="outline"
              size="sm"
              onClick={() => setAnalysis(null)}
              className="w-full mt-2"
            >
              Nouvelle analyse
            </Button>
          </div>
        )}

        {error && (
          <div className="mt-3 p-3 bg-red-900/30 rounded-lg border border-red-700">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default NutritionAnalyzer;
