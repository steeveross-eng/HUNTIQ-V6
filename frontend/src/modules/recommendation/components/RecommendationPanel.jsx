/**
 * RecommendationPanel - Product/Strategy recommendation display
 * BIONIC Design System compliant - No emojis
 * Phase 10 - Plan Maître Modules
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Badge } from '../../../components/ui/badge';
import { Target, Package, Loader2 } from 'lucide-react';
import { RecommendationService } from '../RecommendationService';

export const RecommendationPanel = ({ 
  species = 'deer',
  season = 'rut',
  userId = null,
  onSelectProduct
}) => {
  const [recommendations, setRecommendations] = useState([]);
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('products');

  const loadRecommendations = useCallback(async () => {
    setLoading(true);
    try {
      // Get contextual recommendations
      const result = await RecommendationService.getContextualRecommendations(
        species, season, { limit: 6 }
      );
      
      if (result.success && result.data?.recommendations) {
        setRecommendations(result.data.recommendations);
      } else {
        // Use placeholder data
        setRecommendations([
          { id: 1, name: 'Attractant Premium Cerf', score: 92, category: 'attractant', reason: 'Optimal pour le rut' },
          { id: 2, name: 'Leurre Olfactif Doe', score: 88, category: 'lure', reason: 'Haute efficacité saison' },
          { id: 3, name: 'Bloc Minéral Pro', score: 85, category: 'mineral', reason: 'Complémentaire recommandé' },
          { id: 4, name: 'Spray Anti-Odeur', score: 82, category: 'accessory', reason: 'Essentiel conditions vent' }
        ]);
      }

      // Get strategy recommendations
      const stratResult = await RecommendationService.getStrategyRecommendations(species, { season });
      if (stratResult.success && stratResult.data?.strategies) {
        setStrategies(stratResult.data.strategies);
      } else {
        setStrategies([
          { id: 1, name: 'Affût matinal', confidence: 94, description: 'Position fixe aube' },
          { id: 2, name: 'Approche silencieuse', confidence: 78, description: 'Déplacement lent vent face' },
          { id: 3, name: 'Appel grunt', confidence: 85, description: 'Contact vocal période rut' }
        ]);
      }
    } catch (error) {
      console.error('Recommendation load error:', error);
    } finally {
      setLoading(false);
    }
  }, [species, season]);

  useEffect(() => {
    loadRecommendations();
  }, [loadRecommendations]);

  const getScoreColor = (score) => {
    if (score >= 90) return '#10b981';
    if (score >= 75) return '#22c55e';
    if (score >= 60) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <Card className="bg-gradient-to-br from-amber-900/20 to-slate-900 border-amber-700/50">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-white flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Target className="w-6 h-6 text-amber-400" />
            Recommandations IA
          </span>
          <Badge className="bg-amber-900/50 text-amber-400">
            {species} • {season}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Tab Switcher */}
        <div className="flex gap-2 mb-4">
          <Button
            size="sm"
            variant={activeTab === 'products' ? 'default' : 'outline'}
            className={activeTab === 'products' ? 'bg-[#f5a623] text-black' : 'border-slate-600'}
            onClick={() => setActiveTab('products')}
          >
            <Package className="w-4 h-4 mr-1" /> Produits
          </Button>
          <Button
            size="sm"
            variant={activeTab === 'strategies' ? 'default' : 'outline'}
            className={activeTab === 'strategies' ? 'bg-[#f5a623] text-black' : 'border-slate-600'}
            onClick={() => setActiveTab('strategies')}
          >
            <Target className="w-4 h-4 mr-1" /> Stratégies
          </Button>
        </div>

        {loading ? (
          <div className="text-center py-8">
            <Loader2 className="w-8 h-8 animate-spin text-amber-400 mx-auto" />
            <p className="text-slate-400 text-sm mt-2">Analyse en cours...</p>
          </div>
        ) : activeTab === 'products' ? (
          <div className="space-y-3">
            {recommendations.map((rec, index) => (
              <div 
                key={rec.id || index}
                className="flex items-center gap-3 bg-slate-800/50 rounded-lg p-3 hover:bg-slate-700/50 cursor-pointer transition-colors"
                onClick={() => onSelectProduct?.(rec)}
              >
                <div 
                  className="w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold"
                  style={{ backgroundColor: `${getScoreColor(rec.score)}20`, color: getScoreColor(rec.score) }}
                >
                  {rec.score}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-white font-medium text-sm truncate">{rec.name}</p>
                  <p className="text-slate-400 text-xs">{rec.reason}</p>
                </div>
                <Badge className="bg-slate-700 text-slate-300 text-xs">
                  {rec.category}
                </Badge>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {strategies.map((strat, index) => (
              <div 
                key={strat.id || index}
                className="bg-slate-800/50 rounded-lg p-3"
              >
                <div className="flex items-center justify-between mb-1">
                  <p className="text-white font-medium text-sm">{strat.name}</p>
                  <Badge 
                    style={{ 
                      backgroundColor: `${getScoreColor(strat.confidence)}20`, 
                      color: getScoreColor(strat.confidence) 
                    }}
                  >
                    {strat.confidence}%
                  </Badge>
                </div>
                <p className="text-slate-400 text-xs">{strat.description}</p>
              </div>
            ))}
          </div>
        )}

        <Button 
          className="w-full mt-4 bg-amber-600 hover:bg-amber-700 text-white"
          onClick={loadRecommendations}
        >
          Actualiser les recommandations
        </Button>
      </CardContent>
    </Card>
  );
};

export default RecommendationPanel;
