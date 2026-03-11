/**
 * AIAnalyzer - AI-powered product analysis component
 * BIONIC Design System compliant - No emojis
 */
import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { AIService } from '../AIService';
import { CheckCircle, AlertTriangle, Bot, Sparkles, FileText, Loader2 } from 'lucide-react';

export const AIAnalyzer = ({ 
  productId, 
  productName,
  onAnalysisComplete 
}) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!productId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await AIService.analyzeProduct(productId);
      setAnalysis(result);
      onAnalysisComplete?.(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="bg-gradient-to-br from-purple-900/30 to-slate-900 border-purple-700/50">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center gap-2">
          <Bot className="h-6 w-6 text-purple-400" />
          Analyse IA Bionic™
        </CardTitle>
      </CardHeader>
      <CardContent>
        {productName && (
          <p className="text-slate-400 text-sm mb-4">
            Analyse de: <span className="text-purple-300 font-medium">{productName}</span>
          </p>
        )}

        {!analysis ? (
          <Button
            onClick={handleAnalyze}
            disabled={loading || !productId}
            className="w-full bg-purple-600 hover:bg-purple-500"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Analyse en cours...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-2" />
                Lancer l'analyse IA
              </>
            )}
          </Button>
        ) : (
          <div className="space-y-4">
            {/* Score */}
            {analysis.score !== undefined && (
              <div className="text-center p-4 bg-purple-900/30 rounded-lg">
                <div className="text-4xl font-bold text-purple-400">
                  {analysis.score}/100
                </div>
                <div className="text-sm text-purple-300 mt-1">
                  Score IA
                </div>
              </div>
            )}

            {/* Summary */}
            {analysis.summary && (
              <div className="p-3 bg-slate-800/50 rounded-lg">
                <h4 className="text-purple-400 font-medium text-sm mb-2 flex items-center gap-2">
                  <FileText className="h-4 w-4" /> Résumé
                </h4>
                <p className="text-slate-300 text-sm">
                  {analysis.summary}
                </p>
              </div>
            )}

            {/* Strengths */}
            {analysis.strengths?.length > 0 && (
              <div className="p-3 bg-emerald-900/20 rounded-lg border border-emerald-700/50">
                <h4 className="text-emerald-400 font-medium text-sm mb-2 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" /> Points forts
                </h4>
                <ul className="space-y-1">
                  {analysis.strengths.map((s, i) => (
                    <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                      <span className="text-emerald-400">•</span>
                      {s}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Weaknesses */}
            {analysis.weaknesses?.length > 0 && (
              <div className="p-3 bg-amber-900/20 rounded-lg border border-amber-700/50">
                <h4 className="text-amber-400 font-medium text-sm mb-2 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4" /> Points d'attention
                </h4>
                <ul className="space-y-1">
                  {analysis.weaknesses.map((w, i) => (
                    <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                      <span className="text-amber-400">•</span>
                      {w}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <Button
              variant="outline"
              size="sm"
              onClick={() => setAnalysis(null)}
              className="w-full mt-2 border-purple-700 text-purple-300"
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

export default AIAnalyzer;
